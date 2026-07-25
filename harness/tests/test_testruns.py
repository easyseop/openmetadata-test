"""T62 candidate-bound required test result tests."""
import copy

import pytest

from acgh import candidate as C
from acgh import contracts
from acgh import testruns as T
from acgh import verdict as V

_SHA = "a" * 40
_ARTIFACT = "sha256:" + "b" * 64


def _lock():
    return C.parse_candidate_lock({
        "schema_version": 1,
        "integration_strategy": "vendor-merge",
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_sha": "c" * 40,
            "target_sha": "d" * 40,
        },
        "candidate": {
            "repository": "bank/vendor",
            "commit_sha": _SHA,
            "tree_sha": "e" * 40,
            "artifact_digest": _ARTIFACT,
        },
    })


def _catalog():
    return contracts.parse_catalog({
        "schema_version": 1,
        "contracts": [{
            "id": "CONTRACT-X",
            "title": "x",
            "required_tests": ["tests/contracts/test_x.py::test_x"],
            "customization_ids": ["BANK-OM-001"],
        }],
    })


def _manifest():
    return {
        "customization_id": "BANK-OM-001",
        "assurance": {"contracts": ["CONTRACT-X"], "direct_tests": []},
    }


def _data(outcomes=("pass",)):
    return {
        "schema_version": 1,
        "candidate": {
            "commit_sha": _SHA,
            "artifact_digest": _ARTIFACT,
        },
        "harness_version": "1.0",
        "suite_version": "suite-7",
        "runs": [
            {
                "test_id": "tests/contracts/test_x.py::test_x",
                "attempt": index,
                "outcome": outcome,
            }
            for index, outcome in enumerate(outcomes, 1)
        ],
    }


def _check(data, criticality="high"):
    return T.check_test_runs(
        [_manifest()],
        _catalog(),
        T.parse_test_run_set(data),
        _lock(),
        criticality_by_id={"BANK-OM-001": criticality},
        expected_harness_version="1.0",
        expected_suite_version="suite-7",
    )


def test_clean_required_test_passes_and_has_stable_digest():
    first = T.parse_test_run_set(_data())
    second_data = _data()
    second_data["runs"] = list(reversed(second_data["runs"]))
    second = T.parse_test_run_set(second_data)
    assert first.digest() == second.digest()
    assert _check(_data()).verdict == V.PASS


def test_candidate_or_artifact_change_invalidates_result():
    changed = _data()
    changed["candidate"]["commit_sha"] = "0" * 40
    result = _check(changed)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "candidate commit SHA" in result.reasons[0]

    changed = _data()
    changed["candidate"]["artifact_digest"] = "sha256:" + "0" * 64
    assert _check(changed).verdict == V.ANALYSIS_ERROR


def test_harness_and_suite_versions_are_bound():
    changed = _data()
    changed["harness_version"] = "old"
    assert _check(changed).verdict == V.ANALYSIS_ERROR
    changed = _data()
    changed["suite_version"] = "old"
    assert _check(changed).verdict == V.ANALYSIS_ERROR


def test_missing_skipped_and_failed_required_tests_block():
    assert _check({**_data(), "runs": []}).verdict == V.BLOCK
    assert _check(_data(("skipped",))).verdict == V.BLOCK
    assert _check(_data(("fail",))).verdict == V.BLOCK


def test_critical_retry_pass_requires_approval_and_retains_history():
    result = _check(_data(("fail", "pass")), criticality="critical")
    assert result.verdict == V.APPROVAL
    assert "flaky retry-pass" in result.reasons[0]
    assert "fail,pass" in result.reasons[0]


def test_noncritical_retry_pass_is_distinguished_but_not_blocked():
    result = _check(_data(("error", "pass")), criticality="medium")
    assert result.verdict == V.PASS
    assert "flaky retry-pass" in result.reasons[0]


def test_empty_effective_test_set_blocks():
    manifest = {
        "customization_id": "BANK-OM-001",
        "assurance": {"contracts": [], "direct_tests": []},
    }
    result = T.check_test_runs(
        [manifest],
        _catalog(),
        T.parse_test_run_set(_data()),
        _lock(),
        criticality_by_id={"BANK-OM-001": "high"},
        expected_harness_version="1.0",
        expected_suite_version="suite-7",
    )
    assert result.verdict == V.BLOCK
    assert "no effective tests" in result.reasons[0]


def test_duplicate_or_gapped_attempts_rejected():
    duplicate = _data(("fail", "pass"))
    duplicate["runs"][1]["attempt"] = 1
    with pytest.raises(T.TestRunError, match="duplicate attempt"):
        T.parse_test_run_set(duplicate)

    gap = copy.deepcopy(_data(("fail", "pass")))
    gap["runs"][1]["attempt"] = 3
    with pytest.raises(T.TestRunError, match="contiguous"):
        T.parse_test_run_set(gap)


def test_run_set_writer_is_atomic_and_round_trips(tmp_path):
    run_set = T.parse_test_run_set(_data(("fail", "pass")))
    output = tmp_path / "test-run-set.yaml"
    assert T.write_test_run_set(run_set, output) == str(output)
    assert T.load_test_run_set(output) == run_set
    assert not [path for path in tmp_path.iterdir() if ".tmp." in path.name]
