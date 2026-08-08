"""candidate binding + activation + malformed-input distinction — C26, C29, C30, C49.

Reuses the existing acgh.candidate binding (assert_candidate_binding) and
candidate_select activation; the bundle only orchestrates.
"""
from __future__ import annotations

import os
import subprocess

import pytest
import yaml

from acgh import candidate as C
from acgh import candidate_select as cs
from acgh import phase as P
from acgh import verdict
from acgh import zones as Z


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
    return str(r), c1, c2


# ---- C29 : commit exists but tree SHA mismatch -> binding fails ----
def test_c29_tree_mismatch_binding_fails(repo):
    r, c1, c2 = repo
    good = C.build_candidate_lock(r, c2, upstream_repository="om", upstream_base_sha=c1,
                                  upstream_target_sha=c1, candidate_repository="c",
                                  artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree")
    # corrupt the tree SHA while keeping the (valid) commit SHA
    bad = C.CandidateLock(
        schema_version=2, integration_strategy=C.VENDOR_MERGE, upstream=good.upstream,
        candidate=C.CandidateIdentity(repository="c", commit_sha=c2, tree_sha="f" * 40,
                                      artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree"),
    )
    with pytest.raises(C.CandidateLockError):
        C.assert_candidate_binding(r, bad)


# ---- C30 : build-artifact digest mismatch -> runtime binding forbidden ----
def test_c30_artifact_digest_mismatch_forbidden(repo):
    r, c1, c2 = repo
    tree = _git(r, "rev-parse", f"{c2}^{{tree}}").strip()
    lock = C.CandidateLock(
        schema_version=2, integration_strategy=C.VENDOR_MERGE,
        upstream=C.UpstreamLock(repository="om", base_sha=c1, target_sha=c1),
        candidate=C.CandidateIdentity(repository="c", commit_sha=c2, tree_sha=tree,
                                      artifact_digest="sha256:" + "a" * 64,
                                      artifact_kind="build-artifact"),
    )
    with pytest.raises(C.CandidateLockError):
        C.assert_candidate_binding(r, lock, artifact_digest="sha256:" + "b" * 64)
    # correct digest binds fine
    C.assert_candidate_binding(r, lock, artifact_digest="sha256:" + "a" * 64)


# ---- C26 : after run A, activating lock B -> the next selection uses B ----
def test_c26_next_run_uses_newly_activated_lock(tmp_path):
    reg = tmp_path
    locks = reg / "candidate-locks"
    locks.mkdir()

    def _lock(name, commit):
        data = {"schema_version": 2, "integration_strategy": "vendor-merge",
                "upstream": {"repository": "om", "base_sha": "a" * 40, "target_sha": "c" * 40},
                "candidate": {"repository": "c", "commit_sha": commit, "tree_sha": "d" * 40,
                              "artifact_digest": "sha256:" + "0" * 64, "artifact_kind": "source-tree"}}
        (locks / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
        d = C.load_candidate_lock(locks / f"{name}.yaml").digest()
        (locks / f"{name}.approval.yaml").write_text(yaml.safe_dump(
            {"candidate_lock_digest": d, "approver": "데이터시스템부",
             "approved_at": "2026-08-07T23:00:00Z", "rationale": "ok"}), encoding="utf-8")
        return d

    dA = _lock("A", "1" * 40)
    dB = _lock("B", "2" * 40)

    (locks / "active-candidate.yaml").write_text(yaml.safe_dump(
        {"schema_version": 1, "candidate_lock_digest": dA}), encoding="utf-8")
    assert cs.select_active_candidate(reg).lock.candidate.commit_sha == "1" * 40

    # activate B for the next run
    (locks / "active-candidate.yaml").write_text(yaml.safe_dump(
        {"schema_version": 1, "candidate_lock_digest": dB}), encoding="utf-8")
    assert cs.select_active_candidate(reg).lock.candidate.commit_sha == "2" * 40


# ---- C49 : malformed change-intent -> analysis_error (failed), NOT skipped ----
def test_c49_malformed_change_intent_is_failed(repo, tmp_path):
    r, c1, c2 = repo
    lock = C.build_candidate_lock(r, c2, upstream_repository="om", upstream_base_sha=c1,
                                  upstream_target_sha=c1, candidate_repository="c",
                                  artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree")
    bad = tmp_path / "change-intent.yaml"
    bad.write_text("allowed: [oops\n", encoding="utf-8")  # broken YAML
    zones = Z.Zones({lvl: Z.L.make_spec([]) for lvl in Z._ZONE_ORDER})
    specs = P.build_postmerge_catalog(r, lock, {}, zones=zones,
                                      change_intent_path=str(bad), conflict_rate=0.0)
    ex = next(e for e in [P.execute_gate(s) for s in specs] if e.name == "sensitive-zones")
    assert ex.execution_status == P.FAILED
    assert ex.verdict == verdict.ANALYSIS_ERROR


# ---- C49 companion : MISSING change-intent is skipped, not failed ----
def test_missing_change_intent_is_skipped_not_failed(repo, tmp_path):
    r, c1, c2 = repo
    lock = C.build_candidate_lock(r, c2, upstream_repository="om", upstream_base_sha=c1,
                                  upstream_target_sha=c1, candidate_repository="c",
                                  artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree")
    zones = Z.Zones({lvl: Z.L.make_spec([]) for lvl in Z._ZONE_ORDER})
    specs = P.build_postmerge_catalog(r, lock, {}, zones=zones,
                                      change_intent_path=str(tmp_path / "nope.yaml"), conflict_rate=0.0)
    ex = next(e for e in [P.execute_gate(s) for s in specs] if e.name == "sensitive-zones")
    assert ex.execution_status == P.SKIPPED_MISSING_INPUT
