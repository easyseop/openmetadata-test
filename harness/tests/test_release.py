"""T91 identical-digest release promotion tests."""
import copy

import pytest

from acgh import candidate as C
from acgh import release as R
from acgh import testruns as T
from acgh import verdict as V

_ARTIFACT = "sha256:" + "a" * 64
_HELM = "sha256:" + "b" * 64
_POLICY = "sha256:" + "c" * 64
_CATALOG = "sha256:" + "d" * 64


def _candidate():
    return C.parse_candidate_lock({
        "schema_version": 1,
        "integration_strategy": "vendor-merge",
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_sha": "1" * 40,
            "target_sha": "2" * 40,
        },
        "candidate": {
            "repository": "bank/vendor",
            "commit_sha": "3" * 40,
            "tree_sha": "4" * 40,
            "artifact_digest": _ARTIFACT,
        },
    })


def _tests():
    return T.parse_test_run_set({
        "schema_version": 1,
        "candidate": {
            "commit_sha": "3" * 40,
            "artifact_digest": _ARTIFACT,
        },
        "harness_version": "1.0",
        "suite_version": "suite-9",
        "runs": [{"test_id": "contract-x", "attempt": 1, "outcome": "pass"}],
    })


def _result(state=V.PASS):
    lock = _candidate()
    inputs = lock.result_inputs(verifier_catalog_digest=_CATALOG)
    inputs["policy_digest"] = _POLICY
    inputs["repositories"]["core"] = {"sha": "5" * 40}
    inputs["repositories"]["platform"] = {"sha": "6" * 40}
    return V.build_result(
        [V.GateResult("all", state, ())],
        inputs,
        "1.0",
        run_id="release",
    )


def _release(state=V.PASS, approvals=()):
    return R.build_release_lock(
        _candidate(),
        _result(state),
        _tests(),
        core_sha="5" * 40,
        platform_sha="6" * 40,
        policy_digest=_POLICY,
        verifier_catalog_digest=_CATALOG,
        images={"openmetadata": _ARTIFACT},
        helm_digest=_HELM,
        approval_ids=approvals,
        source_environment="validated",
        target_environment="production",
    )


def _check(lock=None, **changes):
    args = {
        "candidate_lock": _candidate(),
        "result": _result(),
        "test_run_set": _tests(),
        "observed_candidate_sha": "3" * 40,
        "observed_images": {"openmetadata": _ARTIFACT},
        "observed_helm_digest": _HELM,
        "rebuilt": False,
    }
    args.update(changes)
    return R.check_promotion(lock or _release(), **args)


def test_exact_existing_artifacts_promote():
    result = _check()
    assert result.verdict == V.PASS
    assert "promote-existing" in result.reasons[1]


def test_rebuild_or_observed_digest_difference_blocks():
    assert _check(rebuilt=True).verdict == V.BLOCK
    assert _check(
        observed_images={"openmetadata": "sha256:" + "0" * 64}
    ).verdict == V.BLOCK
    assert _check(observed_helm_digest="sha256:" + "0" * 64).verdict == V.BLOCK


def test_changed_candidate_result_or_tests_make_lock_stale():
    changed_candidate = _candidate().canonical()
    changed_candidate["candidate"]["commit_sha"] = "0" * 40
    candidate = C.parse_candidate_lock(changed_candidate)
    assert _check(candidate_lock=candidate).verdict == V.ANALYSIS_ERROR

    changed_tests = _tests().canonical()
    changed_tests["runs"].append(
        {"test_id": "contract-y", "attempt": 1, "outcome": "pass"}
    )
    assert _check(
        test_run_set=T.parse_test_run_set(changed_tests)
    ).verdict == V.ANALYSIS_ERROR


def test_block_and_analysis_error_results_cannot_build_release():
    with pytest.raises(R.ReleaseError, match="not promotable"):
        _release(V.BLOCK)
    with pytest.raises(R.ReleaseError, match="not promotable"):
        _release(V.ANALYSIS_ERROR)


def test_approval_result_requires_approval_identifier():
    with pytest.raises(R.ReleaseError, match="schema"):
        _release(V.APPROVAL)
    lock = _release(V.APPROVAL, approvals=["APR-9"])
    assert lock["approval_ids"] == ["APR-9"]


def test_candidate_artifact_must_be_in_image_set():
    with pytest.raises(R.ReleaseError, match="artifact_digest"):
        R.build_release_lock(
            _candidate(),
            _result(),
            _tests(),
            core_sha="5" * 40,
            platform_sha="6" * 40,
            policy_digest=_POLICY,
            verifier_catalog_digest=_CATALOG,
            images={"other": "sha256:" + "0" * 64},
            helm_digest=_HELM,
            source_environment="validated",
            target_environment="production",
        )


def test_lock_rejects_mutable_promotion_method():
    lock = copy.deepcopy(_release())
    lock["promotion"]["method"] = "rebuild"
    with pytest.raises(R.ReleaseError, match="schema"):
        R.validate_release_lock(lock)


def test_source_result_must_bind_policy_catalog_core_platform_and_harness():
    result = _result()
    result["canonical_payload"]["inputs"]["policy_digest"] = (
        "sha256:" + "0" * 64
    )
    result["result_digest"] = V.canonical_digest(result["canonical_payload"])
    with pytest.raises(R.ReleaseError, match="policy"):
        R.build_release_lock(
            _candidate(),
            result,
            _tests(),
            core_sha="5" * 40,
            platform_sha="6" * 40,
            policy_digest=_POLICY,
            verifier_catalog_digest=_CATALOG,
            images={"openmetadata": _ARTIFACT},
            helm_digest=_HELM,
            source_environment="validated",
            target_environment="production",
        )
