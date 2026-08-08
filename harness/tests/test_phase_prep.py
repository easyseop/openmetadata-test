"""prep-official + candidate pinning — C13, C18, C19, C79-C82.

Creating a local official branch from an upstream tag must fail closed when the
tag is missing, pin annotated/lightweight tags to their commit, and never
overwrite an existing branch that points elsewhere.
"""
from __future__ import annotations

import os
import subprocess

import pytest

from acgh import binding
from acgh import candidate as C
from acgh import phase as P


def _git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, env=env).stdout


def _env():
    return {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "r"
    r.mkdir()
    env = _env()
    _git(r, "init", "-q")
    (r / "a.txt").write_text("1\n", encoding="utf-8")
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "c1", env=env)
    c1 = _git(r, "rev-parse", "HEAD").strip()
    (r / "a.txt").write_text("2\n", encoding="utf-8")
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "c2", env=env)
    c2 = _git(r, "rev-parse", "HEAD").strip()
    return str(r), c1, c2, env


# ---- C18 : target tag exists -> branch created, tree matches ----
def test_c18_tag_exists_creates_branch(repo):
    r, c1, c2, env = repo
    _git(r, "tag", "1.13.2-release", c2, env=env)
    ob = P.prepare_official_branch(r, "1.13.2-release", "official/target")
    assert ob.created
    assert ob.commit_sha == c2
    assert binding.pin(r, "official/target") == c2
    assert ob.tree_sha == _git(r, "rev-parse", f"{c2}^{{tree}}").strip()


# ---- C19 : target tag missing -> STOP, branch not created ----
def test_c19_tag_missing_stops(repo):
    r, c1, c2, env = repo
    with pytest.raises(P.PhaseError):
        P.prepare_official_branch(r, "9.9.9-release", "official/target")
    assert P.subprocess_pin(r, "official/target") is None


# ---- C80 : annotated tag -> pins to commit, not the tag object ----
def test_c80_annotated_tag_pins_commit(repo):
    r, c1, c2, env = repo
    _git(r, "tag", "-a", "annot", "-m", "annotated", c2, env=env)
    ob = P.prepare_official_branch(r, "annot", "official/annot")
    assert ob.commit_sha == c2  # commit, not the tag object SHA


# ---- C79 : lightweight tag -> pins to commit ----
def test_c79_lightweight_tag_pins_commit(repo):
    r, c1, c2, env = repo
    _git(r, "tag", "light", c1, env=env)
    ob = P.prepare_official_branch(r, "light", "official/light")
    assert ob.commit_sha == c1


# ---- C81 : existing branch at a different commit -> no overwrite ----
def test_c81_existing_branch_mismatch_no_overwrite(repo):
    r, c1, c2, env = repo
    _git(r, "branch", "official/target", c1, env=env)
    _git(r, "tag", "1.13.2-release", c2, env=env)
    with pytest.raises(P.PhaseError):
        P.prepare_official_branch(r, "1.13.2-release", "official/target")
    assert binding.pin(r, "official/target") == c1  # unchanged


# ---- C82 : existing correct branch -> idempotent success ----
def test_c82_existing_correct_branch_idempotent(repo):
    r, c1, c2, env = repo
    _git(r, "tag", "1.13.2-release", c2, env=env)
    _git(r, "branch", "official/target", c2, env=env)
    ob = P.prepare_official_branch(r, "1.13.2-release", "official/target")
    assert not ob.created
    assert ob.commit_sha == c2


# ---- C13 : once pinned, a moving branch does not change the run's SHA ----
def test_c13_pinned_sha_survives_branch_move(repo):
    r, c1, c2, env = repo
    _git(r, "branch", "candidate", c2, env=env)
    lock = C.build_candidate_lock(
        r, "candidate", upstream_repository="om", upstream_base_sha=c1,
        upstream_target_sha=c1, candidate_repository="c",
        artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree",
    )
    assert lock.candidate.commit_sha == c2
    # move the branch after pinning
    _git(r, "branch", "-f", "candidate", c1, env=env)
    # the lock still names the originally pinned commit/tree
    assert lock.candidate.commit_sha == c2
    assert lock.candidate.tree_sha == _git(r, "rev-parse", f"{c2}^{{tree}}").strip()
