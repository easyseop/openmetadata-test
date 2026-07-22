"""T21 maintainer-resolve mode tests, on real OM auth source.

The test plays the maintainer: on a conflict it writes the resolved file and
`git add`s it, then continues — exercising the real cherry-pick --continue +
trailer-stamping path.
"""
import subprocess
from collections import namedtuple

import pytest

from acgh import gitprim as G
from acgh import patchlock as P
from acgh import resolve as RS


def _run(repo, *args, **kw):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, **kw)


def _replace_line0(content, new):
    lines = content.split("\n")
    lines[0] = new
    return "\n".join(lines)


def _replace_last(content, new):
    lines = content.split("\n")
    idx = len(lines) - 2 if lines and lines[-1] == "" else len(lines) - 1
    lines[idx] = new
    return "\n".join(lines)


Scenario = namedtuple("Scenario", "repo path bank up_clean up_conflict")
_BANK0 = "// BANK-OM-001 SSO hook"


@pytest.fixture()
def scenario(tmp_path, om_auth_content, om_auth_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "main")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")

    def write(c):
        fp = repo / om_auth_path
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(c)

    def commit(msg):
        _run(repo, "add", "-A")
        _run(repo, "commit", "-m", msg)
        return G.git(str(repo), "rev-parse", "HEAD").strip()

    def branch(base, name):
        _run(repo, "checkout", "-q", "-b", name, base)

    write(om_auth_content)
    base = commit("upstream base (real OM 1.12.13)")
    branch(base, "bank")
    write(_replace_line0(om_auth_content, _BANK0))
    bank = commit("bank hook\n\nCustomization-ID: BANK-OM-001")
    branch(base, "up_clean")
    write(_replace_last(om_auth_content, "// upstream 1.13 note"))
    up_clean = commit("upstream edits last line")
    branch(base, "up_conflict")
    write(_replace_line0(om_auth_content, "// upstream refactor first line"))
    up_conflict = commit("upstream edits first line")
    _run(repo, "checkout", "-q", "main")
    return Scenario(repo, om_auth_path, bank, up_clean, up_conflict)


def _plan(bank_sha):
    return [RS.PlanEntry(sha=bank_sha, customization_id="BANK-OM-001",
                         revision=1, source_commits=(bank_sha,),
                         application_record_id="APP-1")]


def _msg(repo, sha):
    return G.git(str(repo), "show", "-s", "--format=%B", sha)


def test_clean_apply_stamps_lineage_same_revision(scenario, tmp_path):
    s = RS.start_resolve(str(scenario.repo), scenario.up_clean,
                         _plan(scenario.bank), str(tmp_path / "wt"))
    assert s.done and s.paused is None
    assert len(s.applied_commits) == 1
    msg = _msg(scenario.repo, s.applied_commits[0])
    assert f"Source-Commit: {scenario.bank}" in msg
    assert "Patch-Revision: 1" in msg          # unchanged on clean port
    assert "Application-Record-ID: APP-1" in msg
    assert "Customization-ID: BANK-OM-001" in msg
    assert "Resolution-Record-ID" not in msg
    RS.finish(s)


def test_conflict_pauses_then_resolves_with_bumped_revision(scenario, tmp_path):
    wt = tmp_path / "wt"
    s = RS.start_resolve(str(scenario.repo), scenario.up_conflict,
                         _plan(scenario.bank), str(wt))
    # Paused at the conflict, worktree kept for the human.
    assert s.paused is not None
    assert scenario.path in s.paused.conflicted_paths
    assert not s.done

    # Play the maintainer: resolve the file and stage it.
    (wt / scenario.path).write_text(
        "// BANK-OM-001 SSO hook (kept over upstream refactor)\n"
    )
    _run(wt, "add", scenario.path)

    RS.resolve_continue(s, resolution_record_id="RES-1")
    assert s.done
    assert len(s.applied_commits) == 1
    msg = _msg(scenario.repo, s.applied_commits[0])
    assert "Patch-Revision: 2" in msg           # bumped on resolution
    assert "Resolution-Record-ID: RES-1" in msg
    assert f"Source-Commit: {scenario.bank}" in msg

    lock = P.parse_source_lock({
        "schema_version": 1,
        "source_release_sha": "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7",
        "patch_series": [{"id": "BANK-OM-001", "revision": 2,
                          "source_commits": [scenario.bank]}],
    })
    app = RS.finish(s, source_lock=lock)
    assert app.parent_lock_digest == lock.digest()
    assert app.resolution_record_ids == ("RES-1",)
    assert len(app.applied_commits) == 1


def test_abort_cleans_worktree(scenario, tmp_path):
    wt = tmp_path / "wt"
    s = RS.start_resolve(str(scenario.repo), scenario.up_conflict,
                         _plan(scenario.bank), str(wt))
    assert s.paused is not None
    RS.abort_resolve(s)
    listing = G.git(str(scenario.repo), "worktree", "list", "--porcelain")
    assert str(wt) not in listing
    assert G.git(str(scenario.repo), "status", "--porcelain").strip() == ""
