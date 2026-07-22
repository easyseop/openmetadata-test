"""T22 clean-room replay tests, on real OM auth source."""
import subprocess
from collections import namedtuple

import pytest

from acgh import gitprim as G
from acgh import replay as RP
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


Scen = namedtuple("Scen", "repo path bank up_clean candidate candidate_tampered")


@pytest.fixture()
def scen(tmp_path, om_auth_content, om_auth_path):
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
    write(_replace_line0(om_auth_content, "// BANK-OM-001 hook"))
    bank = commit("bank hook\n\nCustomization-ID: BANK-OM-001")
    branch(base, "up_clean")
    write(_replace_last(om_auth_content, "// upstream 1.13 note"))
    up_clean = commit("upstream edits last line")

    # Official candidate = up_clean + bank (cherry-pick), reproducible from lock.
    branch(up_clean, "candidate")
    _run(repo, "cherry-pick", bank)
    candidate = G.git(str(repo), "rev-parse", "HEAD").strip()

    # Tampered candidate = candidate + a hand edit NOT in any patch.
    branch(candidate, "candidate_tampered")
    write(_replace_line0(
        _replace_last(om_auth_content, "// upstream 1.13 note"),
        "// BANK-OM-001 hook + sneaky uncrolled edit"))
    candidate_tampered = commit("sneaky edit outside the patch stack")

    _run(repo, "checkout", "-q", "main")
    return Scen(repo, om_auth_path, bank, up_clean, candidate, candidate_tampered)


def test_replay_reproduces_candidate(scen, tmp_path):
    r = RP.replay_and_compare(str(scen.repo), scen.up_clean, [scen.bank],
                              scen.candidate, str(tmp_path / "wt"))
    assert r.apply_ok and r.equal
    assert r.verdict() == V.PASS
    assert r.replay_tree == r.candidate_tree


def test_replay_is_deterministic_three_runs(scen, tmp_path):
    trees = set()
    for i in range(3):
        r = RP.replay_and_compare(str(scen.repo), scen.up_clean, [scen.bank],
                                  scen.candidate, str(tmp_path / f"wt{i}"))
        trees.add(r.replay_tree)
    assert len(trees) == 1  # content-addressed -> identical every time


def test_tampered_candidate_blocks_and_reports_path(scen, tmp_path):
    r = RP.replay_and_compare(str(scen.repo), scen.up_clean, [scen.bank],
                              scen.candidate_tampered, str(tmp_path / "wt"))
    assert not r.equal
    assert r.verdict() == V.BLOCK
    assert scen.path in r.differing_paths


def test_missing_source_is_inconclusive(scen, tmp_path):
    r = RP.replay_and_compare(str(scen.repo), scen.up_clean, ["0" * 40],
                              scen.candidate, str(tmp_path / "wt"))
    assert not r.apply_ok
    assert r.verdict() == V.ANALYSIS_ERROR
