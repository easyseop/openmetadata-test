"""T24 candidate-lock and integration-strategy tests."""
import copy
import subprocess

import pytest

from acgh import candidate as C
from acgh import result_io as R
from acgh import verdict as V

_BASE = "a" * 40
_TARGET = "b" * 40
_COMMIT = "c" * 40
_TREE = "d" * 40
_ARTIFACT = "sha256:" + "e" * 64
_CATALOG = "sha256:" + "f" * 64
_PATCH_LOCK = "sha256:" + "1" * 64


def _lock_dict():
    return {
        "schema_version": 1,
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_tag": "1.12.3-release",
            "base_sha": _BASE,
            "target_tag": "1.13.1-release",
            "target_sha": _TARGET,
        },
        "candidate": {
            "repository": "bank/kb_openmetadata",
            "commit_sha": _COMMIT,
            "tree_sha": _TREE,
            "artifact_digest": _ARTIFACT,
        },
    }


def _run(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")
    (repo / "f").write_text("candidate\n")
    _run(repo, "add", "f")
    _run(repo, "commit", "-m", "candidate")
    return repo


def test_missing_strategy_defaults_to_vendor_merge():
    lock = C.parse_candidate_lock(_lock_dict())
    assert lock.integration_strategy == C.VENDOR_MERGE
    assert lock.canonical()["integration_strategy"] == C.VENDOR_MERGE


def test_invalid_strategy_rejected():
    data = _lock_dict()
    data["integration_strategy"] = "rebase"
    with pytest.raises(C.CandidateLockError, match="schema"):
        C.parse_candidate_lock(data)


def test_patch_replay_requires_patch_source_lock_digest():
    data = _lock_dict()
    data["integration_strategy"] = C.PATCH_REPLAY
    with pytest.raises(C.CandidateLockError, match="patch_source_lock_digest"):
        C.parse_candidate_lock(data)
    data["patch_source_lock_digest"] = _PATCH_LOCK
    assert C.parse_candidate_lock(data).patch_source_lock_digest == _PATCH_LOCK


def test_bad_sha_and_unknown_fields_rejected():
    data = _lock_dict()
    data["candidate"]["commit_sha"] = "main"
    with pytest.raises(C.CandidateLockError, match="schema"):
        C.parse_candidate_lock(data)
    data = _lock_dict()
    data["candidate"]["moving_branch"] = "main"
    with pytest.raises(C.CandidateLockError, match="schema"):
        C.parse_candidate_lock(data)


def test_digest_is_stable_but_changes_with_artifact():
    first = _lock_dict()
    reordered = {
        "candidate": copy.deepcopy(first["candidate"]),
        "upstream": copy.deepcopy(first["upstream"]),
        "schema_version": 1,
    }
    assert C.parse_candidate_lock(first).digest() == C.parse_candidate_lock(
        reordered
    ).digest()
    changed = copy.deepcopy(first)
    changed["candidate"]["artifact_digest"] = "sha256:" + "0" * 64
    assert C.parse_candidate_lock(first).digest() != C.parse_candidate_lock(
        changed
    ).digest()


def test_build_lock_pins_real_commit_and_tree(tmp_path):
    repo = _repo(tmp_path)
    lock = C.build_candidate_lock(
        str(repo),
        "HEAD",
        upstream_repository="open-metadata/OpenMetadata",
        upstream_base_sha=_BASE,
        upstream_target_sha=_TARGET,
        candidate_repository="bank/kb_openmetadata",
        artifact_digest=_ARTIFACT,
        artifact_kind=C.SOURCE_TREE,
    )
    assert lock.candidate.commit_sha == _run(repo, "rev-parse", "HEAD")
    assert lock.candidate.tree_sha == _run(repo, "rev-parse", "HEAD^{tree}")
    C.assert_candidate_binding(str(repo), lock, artifact_digest=_ARTIFACT)


def test_binding_detects_tree_and_artifact_mismatch(tmp_path):
    repo = _repo(tmp_path)
    lock = C.build_candidate_lock(
        str(repo),
        "HEAD",
        upstream_repository="open-metadata/OpenMetadata",
        upstream_base_sha=_BASE,
        upstream_target_sha=_TARGET,
        candidate_repository="bank/kb_openmetadata",
        artifact_digest=_ARTIFACT,
        artifact_kind=C.BUILD_ARTIFACT,
    )
    bad_data = lock.canonical()
    bad_data["candidate"]["tree_sha"] = "0" * 40
    with pytest.raises(C.CandidateLockError, match="tree mismatch"):
        C.assert_candidate_binding(str(repo), C.parse_candidate_lock(bad_data))
    with pytest.raises(C.CandidateLockError, match="requires"):
        C.assert_candidate_binding(str(repo), lock)
    with pytest.raises(C.CandidateLockError, match="artifact digest mismatch"):
        C.assert_candidate_binding(
            str(repo), lock, artifact_digest="sha256:" + "0" * 64
        )


def test_result_inputs_are_derived_from_candidate_lock():
    lock = C.parse_candidate_lock(_lock_dict())
    inputs = lock.result_inputs(verifier_catalog_digest=_CATALOG)
    assert inputs["integration_strategy"] == C.VENDOR_MERGE
    assert inputs["repositories"]["candidate"] == {
        "repository": "bank/kb_openmetadata",
        "sha": _COMMIT,
        "tree_sha": _TREE,
    }
    assert inputs["artifact_digest"] == _ARTIFACT
    assert inputs["candidate_lock_digest"] == lock.digest()
    assert "patch_source_lock_digest" not in inputs


def test_schema_v2_requires_explicit_artifact_kind():
    data = _lock_dict()
    data["schema_version"] = 2
    with pytest.raises(C.CandidateLockError, match="artifact_kind"):
        C.parse_candidate_lock(data)
    data["candidate"]["artifact_kind"] = C.SOURCE_TREE
    lock = C.parse_candidate_lock(data)
    assert lock.candidate.artifact_kind == C.SOURCE_TREE
    assert lock.canonical()["candidate"]["artifact_kind"] == C.SOURCE_TREE


def test_changed_candidate_lock_invalidates_prior_result(tmp_path):
    lock = C.parse_candidate_lock(_lock_dict())
    inputs = lock.result_inputs(verifier_catalog_digest=_CATALOG)
    result = V.build_result(
        [V.GateResult("candidate-lock", V.PASS, ())],
        inputs,
        "0.0.1",
        run_id="t24",
    )
    out = tmp_path / "acgh-result.yaml"
    R.write_result(result, out)
    assert R.interpret_result(
        out, actual_exit=0, expected_inputs=inputs
    ).verdict == V.PASS

    changed = _lock_dict()
    changed["candidate"]["artifact_digest"] = "sha256:" + "0" * 64
    changed_inputs = C.parse_candidate_lock(changed).result_inputs(
        verifier_catalog_digest=_CATALOG
    )
    decision = R.interpret_result(
        out, actual_exit=0, expected_inputs=changed_inputs
    )
    assert decision.verdict == V.ANALYSIS_ERROR
    assert "stale" in decision.reason
