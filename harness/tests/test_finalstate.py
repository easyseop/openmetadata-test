"""T32 final-state invariant tests, on real OM auth source."""
import subprocess
from collections import namedtuple

import pytest

from acgh import finalstate as F
from acgh import gitprim as G
from acgh import verdict as V


def _run(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


Scen = namedtuple("Scen", "repo up_clean bank_add bank_revert dep_a dep_b")


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

    lines = om_auth_content.split("\n")
    write(om_auth_content)
    base = commit("upstream base")

    # up_clean: divergent target (edits last line) so bank picks apply cleanly.
    branch(base, "up_clean")
    edited = list(lines)
    idx = len(edited) - 2 if edited and edited[-1] == "" else len(edited) - 1
    edited[idx] = "// upstream 1.13"
    write("\n".join(edited))
    up_clean = commit("upstream last line")

    # bank_add then bank_revert on top of base: net-zero pair for one ID.
    branch(base, "bankwork")
    added = list(lines)
    added[0] = "// BANK-OM-001 hook"
    write("\n".join(added))
    bank_add = commit("add hook\n\nCustomization-ID: BANK-OM-001")
    write(om_auth_content)  # revert to base content
    bank_revert = commit("revert hook\n\nCustomization-ID: BANK-OM-001")

    # dependency pair: dep_a inserts an anchor line, dep_b edits that same line.
    branch(base, "depwork")
    a = list(lines)
    a[0] = "// ANCHOR from BANK-OM-002"
    write("\n".join(a))
    dep_a = commit("anchor\n\nCustomization-ID: BANK-OM-002")
    b = list(lines)
    b[0] = "// ANCHOR edited by BANK-OM-003"
    write("\n".join(b))
    dep_b = commit("edit anchor\n\nCustomization-ID: BANK-OM-003")

    _run(repo, "checkout", "-q", "main")
    return Scen(repo, up_clean, bank_add, bank_revert, dep_a, dep_b)


def test_contributing_id_passes(scen, tmp_path):
    status = F.id_net_contribution(
        str(scen.repo), scen.up_clean,
        full_source_commits=[scen.bank_add],
        id_source_commits=[scen.bank_add],
        worktree_full=str(tmp_path / "wf"),
        worktree_without=str(tmp_path / "ww"),
    )
    assert status == F.CONTRIBUTES
    assert F.contribution_verdict(status) == V.PASS


def test_net_zero_id_is_inert_block(scen, tmp_path):
    # ID BANK-OM-001 = add + revert. Dropping both leaves the same tree.
    status = F.id_net_contribution(
        str(scen.repo), scen.up_clean,
        full_source_commits=[scen.bank_add, scen.bank_revert],
        id_source_commits=[scen.bank_add, scen.bank_revert],
        worktree_full=str(tmp_path / "wf"),
        worktree_without=str(tmp_path / "ww"),
    )
    assert status == F.INERT
    assert F.contribution_verdict(status) == V.BLOCK


def test_dropping_depended_on_id_is_inconclusive(scen, tmp_path):
    # Drop dep_a (the anchor); dep_b edits that anchor line -> replay fails.
    status = F.id_net_contribution(
        str(scen.repo), scen.up_clean,
        full_source_commits=[scen.dep_a, scen.dep_b],
        id_source_commits=[scen.dep_a],
        worktree_full=str(tmp_path / "wf"),
        worktree_without=str(tmp_path / "ww"),
    )
    assert status == F.INCONCLUSIVE
    assert F.contribution_verdict(status) == V.ANALYSIS_ERROR


def test_candidate_reproducible_wrapper(scen, tmp_path):
    # Build a candidate = up_clean + bank_add, then verify reproducibility.
    _run(scen.repo, "checkout", "-q", "-b", "cand", scen.up_clean)
    _run(scen.repo, "cherry-pick", scen.bank_add)
    _run(scen.repo, "checkout", "-q", "main")
    r = F.candidate_reproducible(str(scen.repo), scen.up_clean, [scen.bank_add],
                                 "cand", str(tmp_path / "wt"))
    assert r.equal and r.verdict() == V.PASS


def test_stale_attestations_on_candidate_change():
    att = [{"target_result_digest": "sha256:" + "a" * 64,
            "candidate_sha": "d" * 40, "policy_digest": "sha256:" + "e" * 64}]
    fresh = F.stale_attestations(
        att, result_digest="sha256:" + "a" * 64, candidate_sha="d" * 40,
        policy_digest="sha256:" + "e" * 64)
    assert fresh == []
    stale = F.stale_attestations(
        att, result_digest="sha256:" + "a" * 64, candidate_sha="NEW" + "d" * 37,
        policy_digest="sha256:" + "e" * 64)
    assert len(stale) == 1
