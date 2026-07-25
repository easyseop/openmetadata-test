"""T90 upgrade orchestration result-contract tests."""
import copy

from acgh import candidate as C
from acgh import testruns as T
from acgh import upgrade_run as U
from acgh import verdict as V

_ARTIFACT = "sha256:" + "a" * 64


def _candidate():
    return C.parse_candidate_lock({
        "schema_version": 1,
        "integration_strategy": "vendor-merge",
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_sha": "b" * 40,
            "target_sha": "c" * 40,
        },
        "candidate": {
            "repository": "bank/vendor",
            "commit_sha": "d" * 40,
            "tree_sha": "e" * 40,
            "artifact_digest": _ARTIFACT,
        },
    })


def _tests():
    return T.parse_test_run_set({
        "schema_version": 1,
        "candidate": {
            "commit_sha": "d" * 40,
            "artifact_digest": _ARTIFACT,
        },
        "harness_version": "1.0",
        "suite_version": "suite-1",
        "runs": [{"test_id": "x", "attempt": 1, "outcome": "pass"}],
    })


def _run():
    return {
        "schema_version": 1,
        "candidate": {
            "commit_sha": "d" * 40,
            "artifact_digest": _ARTIFACT,
        },
        "test_run_set_digest": _tests().digest(),
        "old_version": "1.13.1",
        "new_version": "1.14.0",
        "environment_digest": "sha256:" + "f" * 64,
        "stages": [
            {
                "name": stage,
                "outcome": "pass",
                "evidence_digest": "sha256:" + format(index, "064x"),
            }
            for index, stage in enumerate(U.REQUIRED_STAGES, 1)
        ],
    }


def _check(data):
    return U.check_upgrade_run(
        data, candidate_lock=_candidate(), test_run_set=_tests()
    )


def test_all_migration_differential_and_rollback_stages_pass():
    result = _check(_run())
    assert result.verdict == V.PASS
    assert f"stages_passed={len(U.REQUIRED_STAGES)}" in result.reasons


def test_missing_or_skipped_stage_blocks():
    run = _run()
    run["stages"] = run["stages"][:-1]
    result = _check(run)
    assert result.verdict == V.BLOCK
    assert "rollback-drill" in result.reasons[0]
    run = _run()
    run["stages"][1]["outcome"] = "skipped"
    assert _check(run).verdict == V.BLOCK


def test_candidate_artifact_and_test_set_are_bound():
    run = _run()
    run["candidate"]["commit_sha"] = "0" * 40
    assert _check(run).verdict == V.ANALYSIS_ERROR
    run = _run()
    run["test_run_set_digest"] = "sha256:" + "0" * 64
    assert _check(run).verdict == V.ANALYSIS_ERROR


def test_duplicate_stage_is_malformed_evidence():
    run = _run()
    run["stages"].append(copy.deepcopy(run["stages"][0]))
    assert _check(run).verdict == V.ANALYSIS_ERROR


def test_digest_is_independent_of_stage_serialization_order():
    run = _run()
    reversed_run = copy.deepcopy(run)
    reversed_run["stages"].reverse()
    assert U.upgrade_run_digest(run) == U.upgrade_run_digest(reversed_run)
