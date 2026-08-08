"""L3 gate independent execution — C9, C52-C57.

A failing gate becomes execution_status=failed / verdict=analysis_error and
NEVER aborts a sibling gate; a missing OPTIONAL input becomes
skipped_missing_input / verdict=None (never confused with a program bug).
"""
from __future__ import annotations

import time

import pytest

from acgh import phase as P
from acgh import verdict


def _ok(name, v=verdict.PASS, target_count=None):
    return P.GateSpec(name, lambda: P.GateOutcome(verdict.GateResult(name, v), target_count=target_count))


# ---- C52 : python exception inside a gate ----
def test_c52_gate_exception_is_failed_analysis_error():
    def boom():
        raise RuntimeError("kaboom")

    ex = P.execute_gate(P.GateSpec("t43", boom))
    assert ex.execution_status == P.FAILED
    assert ex.verdict == verdict.ANALYSIS_ERROR
    assert any("kaboom" in r for r in ex.reasons)


# ---- C53 : timeout is failed (a TimeoutError is just an exception here) ----
def test_c53_gate_timeout_is_failed():
    def slow():
        raise TimeoutError("gate exceeded 30s")

    ex = P.execute_gate(P.GateSpec("t42", slow, timeout=30))
    assert ex.execution_status == P.FAILED
    assert ex.verdict == verdict.ANALYSIS_ERROR
    assert any("30s" in r or "Timeout" in r for r in ex.reasons)


# ---- C54 : bad JSON output -> failed, log preserved ----
def test_c54_bad_json_is_failed_not_pass():
    def bad_json():
        raise P.GateExecutionError("runner emitted non-JSON: 'Traceback...'")

    ex = P.execute_gate(P.GateSpec("t42", bad_json))
    assert ex.execution_status == P.FAILED
    assert ex.verdict == verdict.ANALYSIS_ERROR
    assert any("non-JSON" in r for r in ex.reasons)


# ---- C55 : JSON says pass but exit code disagrees ----
def test_c55_exit_vs_json_mismatch_is_analysis_error():
    def mismatch():
        raise P.GateExecutionError("verdict=pass but runner exit code was 1")

    ex = P.execute_gate(P.GateSpec("t42", mismatch))
    assert ex.execution_status == P.FAILED
    assert ex.verdict == verdict.ANALYSIS_ERROR


# ---- C9 / C47 : missing optional input -> skipped_missing_input ----
def test_c9_missing_conflict_rate_skips_only_t43():
    def needs_conflict_rate():
        raise P.MissingInput("conflict-rate not provided")

    ex = P.execute_gate(P.GateSpec("debt", needs_conflict_rate))
    assert ex.execution_status == P.SKIPPED_MISSING_INPUT
    assert ex.verdict is None


# ---- C56 : one gate fails, the other still runs; overall analysis_error ----
def test_c56_failing_gate_does_not_abort_others():
    def boom():
        raise RuntimeError("t43 broke")

    specs = [_ok("upgrade-watch", verdict.PASS), P.GateSpec("debt", boom)]
    result = P.run_gates(specs, phase=P.POSTMERGE)
    by = {e.name: e for e in result.executions}
    assert by["upgrade-watch"].execution_status == P.EXECUTED
    assert by["upgrade-watch"].verdict == verdict.PASS
    assert by["debt"].execution_status == P.FAILED
    assert result.overall_verdict == verdict.ANALYSIS_ERROR


# ---- C57 : zero runnable gates -> analysis_error, never empty pass ----
def test_c57_zero_executed_gates_is_analysis_error():
    def miss():
        raise P.MissingInput("no input")

    specs = [P.GateSpec("a", miss), P.GateSpec("b", miss)]
    result = P.run_gates(specs)
    assert all(e.execution_status == P.SKIPPED_MISSING_INPUT for e in result.executions)
    assert result.overall_verdict == verdict.ANALYSIS_ERROR
    assert result.exit_code == verdict.EXIT_CODE[verdict.ANALYSIS_ERROR]


def test_missing_input_is_never_reclassified_as_failed():
    # A bug must not hide as skipped, and a missing input must not inflate to failed.
    def miss():
        raise P.MissingInput("optional gone")

    def bug():
        raise ValueError("real bug")

    assert P.execute_gate(P.GateSpec("x", miss)).execution_status == P.SKIPPED_MISSING_INPUT
    assert P.execute_gate(P.GateSpec("y", bug)).execution_status == P.FAILED


def test_target_count_is_carried_through():
    spec = _ok("upgrade-watch", verdict.APPROVAL, target_count=1702)
    ex = P.execute_gate(spec)
    assert ex.target_count == 1702
