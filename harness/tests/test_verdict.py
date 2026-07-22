"""T13 verdict engine tests. Includes the P0-3 mutation guard."""
import pytest

from acgh import verdict as V


def test_exit_code_mapping():
    assert V.to_exit_code(V.PASS) == 0
    assert V.to_exit_code(V.BLOCK) == 1
    assert V.to_exit_code(V.APPROVAL) == 2
    assert V.to_exit_code(V.ANALYSIS_ERROR) == 3


def test_aggregate_prefers_more_severe():
    assert V.aggregate([V.PASS, V.APPROVAL]) == V.APPROVAL
    assert V.aggregate([V.PASS, V.PASS]) == V.PASS


def test_block_beats_approval_P0_3():
    # THE key invariant: block must NOT be downgraded to approval.
    # Mutation guard: if aggregation used EXIT_CODE (approval=2 > block=1),
    # this would return "approval" and fail.
    assert V.aggregate([V.BLOCK, V.APPROVAL]) == V.BLOCK
    assert V.aggregate([V.APPROVAL, V.BLOCK, V.PASS]) == V.BLOCK


def test_analysis_error_is_most_severe():
    assert V.aggregate([V.BLOCK, V.ANALYSIS_ERROR]) == V.ANALYSIS_ERROR
    assert V.aggregate([V.APPROVAL, V.ANALYSIS_ERROR]) == V.ANALYSIS_ERROR


def test_empty_input_fails_closed_P0_4():
    # Nothing judged -> must not report pass.
    assert V.aggregate([]) == V.ANALYSIS_ERROR


def test_invalid_verdict_raises():
    with pytest.raises(V.InvalidVerdict):
        V.aggregate(["ok"])
    with pytest.raises(V.InvalidVerdict):
        V.to_exit_code("fail")


def test_canonical_digest_is_stable_and_key_order_independent():
    a = {"verdict": "block", "gates": [{"name": "x", "verdict": "block"}]}
    b = {"gates": [{"verdict": "block", "name": "x"}], "verdict": "block"}
    assert V.canonical_digest(a) == V.canonical_digest(b)


def test_result_digest_excludes_observational_metadata():
    gates = [V.GateResult("reapply", V.BLOCK, ("BANK-OM-001 conflict",))]
    inputs = {"repositories": {"upstream": {"sha": "e6c6650"}}}
    r1 = V.build_result(gates, inputs, "0.0.1", run_id="run-1",
                        observational={"duration_ms": 12})
    r2 = V.build_result(gates, inputs, "0.0.1", run_id="run-2",
                        observational={"duration_ms": 999})
    # Different run/duration, same judgment -> identical digest.
    assert r1["result_digest"] == r2["result_digest"]
    assert r1["canonical_payload"]["verdict"] == "block"
    assert r1["expected_exit_code"] == 1


def test_gate_result_rejects_bad_verdict():
    with pytest.raises(V.InvalidVerdict):
        V.GateResult("g", "maybe")
