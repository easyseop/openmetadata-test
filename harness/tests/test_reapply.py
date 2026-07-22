"""T20 reapply CI-detect-mode tests, using REAL OpenMetadata auth source as the
common ancestor. Scenarios (case B/C/redundant) are constructed by editing that
real file so cherry-pick conflict detection is exercised on genuine content.
"""
import subprocess
from collections import namedtuple

import pytest

from acgh import gitprim as G
from acgh import reapply as RA
from acgh import verdict as V


def _run(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


def _replace_line0(content, new):
    lines = content.split("\n")
    lines[0] = new
    return "\n".join(lines)


def _replace_last(content, new):
    lines = content.split("\n")
    idx = len(lines) - 2 if lines and lines[-1] == "" else len(lines) - 1
    lines[idx] = new
    return "\n".join(lines)


Scenario = namedtuple("Scenario", "repo path base bank upstream_clean "
                                  "upstream_conflict upstream_redundant")

_BANK_LINE0 = "// BANK-OM-001 SSO login hook — bank customization"


@pytest.fixture()
def scenario(tmp_path, om_auth_content, om_auth_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "main")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")

    def write(content):
        fp = repo / om_auth_path
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)

    def commit(msg):
        _run(repo, "add", "-A")
        _run(repo, "commit", "-m", msg)
        return G.git(str(repo), "rev-parse", "HEAD").strip()

    def branch_from(base_sha, name):
        _run(repo, "checkout", "-q", "-b", name, base_sha)

    # common ancestor = real 1.12.13 auth file
    write(om_auth_content)
    base = commit("upstream base (real OM 1.12.13)")

    branch_from(base, "bank")
    write(_replace_line0(om_auth_content, _BANK_LINE0))
    bank = commit("bank hook\n\nCustomization-ID: BANK-OM-001")

    branch_from(base, "up_clean")  # edits a far-away line -> no conflict
    write(_replace_last(om_auth_content, "// upstream 1.13 note"))
    up_clean = commit("upstream edits last line")

    branch_from(base, "up_conflict")  # edits the SAME line as bank -> conflict
    write(_replace_line0(om_auth_content, "// upstream refactor of first line"))
    up_conflict = commit("upstream edits first line")

    branch_from(base, "up_redundant")  # already contains bank's exact change
    write(_replace_line0(om_auth_content, _BANK_LINE0))
    up_redundant = commit("upstream already has the bank change")

    _run(repo, "checkout", "-q", "main")
    return Scenario(repo, om_auth_path, base, bank, up_clean, up_conflict, up_redundant)


def test_clean_apply_on_divergent_upstream(scenario, tmp_path):
    rep = RA.reapply_detect(str(scenario.repo), scenario.upstream_clean,
                            [scenario.bank], str(tmp_path / "wt"))
    assert [r.status for r in rep.results] == [RA.APPLIED]
    assert rep.verdict() == V.PASS
    assert rep.to_gate_result().verdict == V.PASS


def test_conflict_detected_and_reported(scenario, tmp_path):
    rep = RA.reapply_detect(str(scenario.repo), scenario.upstream_conflict,
                            [scenario.bank], str(tmp_path / "wt"))
    assert rep.results[0].status == RA.CONTENT_CONFLICT
    assert scenario.path in rep.results[0].conflicted_paths
    assert rep.verdict() == V.BLOCK


def test_redundant_change_not_auto_dropped(scenario, tmp_path):
    rep = RA.reapply_detect(str(scenario.repo), scenario.upstream_redundant,
                            [scenario.bank], str(tmp_path / "wt"))
    assert rep.results[0].status == RA.REDUNDANT_OR_EMPTY
    assert rep.verdict() == V.BLOCK  # routed to retirement, not silently dropped


def test_missing_source_object_is_analysis_error(scenario, tmp_path):
    rep = RA.reapply_detect(str(scenario.repo), scenario.upstream_clean,
                            ["0" * 40], str(tmp_path / "wt"))
    assert rep.results[0].status == RA.MISSING_SOURCE_OBJECT
    assert rep.verdict() == V.ANALYSIS_ERROR


def test_conflict_blocks_downstream_as_skipped(scenario, tmp_path):
    # A second (valid) commit after a conflicting one must be skipped, not tried.
    rep = RA.reapply_detect(str(scenario.repo), scenario.upstream_conflict,
                            [scenario.bank, scenario.base], str(tmp_path / "wt"))
    assert rep.results[0].status == RA.CONTENT_CONFLICT
    assert rep.results[1].status == RA.SKIPPED_DUE_TO_DEPENDENCY


def test_worktree_removed_and_main_tree_clean(scenario, tmp_path):
    wt = tmp_path / "wt"
    RA.reapply_detect(str(scenario.repo), scenario.upstream_conflict,
                      [scenario.bank], str(wt))
    # No leftover worktree registered, and the caller's tree is clean.
    listing = G.git(str(scenario.repo), "worktree", "list", "--porcelain")
    assert str(wt) not in listing
    status = G.git(str(scenario.repo), "status", "--porcelain")
    assert status.strip() == ""
    assert not wt.exists()
