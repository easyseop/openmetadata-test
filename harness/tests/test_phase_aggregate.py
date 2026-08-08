"""L4 aggregation, phase status, exit codes — C10-C12, C20, C58-C65.

Aggregation MUST use verdict.SEVERITY_RANK, never exit-code magnitude. A mutant
that aggregates by max(exit_code) is killed by C59/C65 (approval+block -> block,
though exit(approval)=2 > exit(block)=1).
"""
from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from acgh import phase as P
from acgh import verdict


def _exec(name, v, *, required=True, applicable=True, advisory=False, status=P.EXECUTED):
    return P.GateExecution(
        name=name,
        execution_status=status,
        verdict=v,
        required=required,
        applicable=applicable,
        advisory=advisory,
    )


# ---- C11 : all required gates pass ----
def test_c11_all_pass_is_pass_exit0():
    r = P.aggregate_phase([_exec("a", verdict.PASS), _exec("b", verdict.PASS)])
    assert r.overall_verdict == verdict.PASS
    assert r.phase_status == P.COMPLETE
    assert r.exit_code == 0


# ---- C12 / C58 : pass + approval -> approval, exit 2 ----
def test_c12_pass_plus_approval_is_approval_exit2():
    r = P.aggregate_phase([_exec("a", verdict.PASS), _exec("b", verdict.APPROVAL)])
    assert r.overall_verdict == verdict.APPROVAL
    assert r.exit_code == 2


# ---- C59 : approval + block -> block, exit 1 (kills exit-code-max mutant) ----
def test_c59_approval_plus_block_is_block_exit1():
    r = P.aggregate_phase([_exec("a", verdict.APPROVAL), _exec("b", verdict.BLOCK)])
    assert r.overall_verdict == verdict.BLOCK
    assert r.exit_code == 1
    # An exit-code-max implementation would wrongly pick approval (exit 2 > 1).
    assert r.overall_verdict != verdict.APPROVAL


# ---- C60 : block + analysis_error -> analysis_error, exit 3 ----
def test_c60_block_plus_analysis_error_is_analysis_error_exit3():
    r = P.aggregate_phase([_exec("a", verdict.BLOCK), _exec("b", verdict.ANALYSIS_ERROR)])
    assert r.overall_verdict == verdict.ANALYSIS_ERROR
    assert r.exit_code == 3


# ---- C10 / C62 : one required gate not executed -> incomplete/analysis_error/exit3 ----
def test_c10_required_gate_not_executed_is_incomplete_analysis_error():
    r = P.aggregate_phase([
        _exec("a", verdict.PASS),
        _exec("b", None, status=P.SKIPPED_MISSING_INPUT),
    ])
    assert r.phase_status == P.INCOMPLETE
    assert r.overall_verdict == verdict.ANALYSIS_ERROR
    assert r.exit_code == 3


def test_c62_required_missing_rest_pass_is_incomplete():
    r = P.aggregate_phase([
        _exec("a", verdict.PASS),
        _exec("b", verdict.PASS),
        _exec("c", None, status=P.BLOCKED_BY_PREFLIGHT),
    ])
    assert r.phase_status == P.INCOMPLETE
    assert r.overall_verdict == verdict.ANALYSIS_ERROR


# ---- C63 : a NON-applicable gate that didn't run must not force incomplete ----
def test_c63_non_applicable_gate_not_run_stays_complete():
    r = P.aggregate_phase([
        _exec("a", verdict.PASS),
        _exec("t41", None, applicable=False, status=P.NOT_APPLICABLE),
    ])
    assert r.phase_status == P.COMPLETE
    assert r.overall_verdict == verdict.PASS


# ---- C39 : advisory gate excluded from verdict aggregation ----
def test_advisory_gate_excluded_from_aggregation():
    r = P.aggregate_phase([
        _exec("a", verdict.PASS),
        _exec("watch-suggest", verdict.APPROVAL, required=False, advisory=True),
    ])
    assert r.overall_verdict == verdict.PASS  # advisory approval must not escalate


# ---- C20 : the four verdicts map to the existing EXIT_CODE table ----
@pytest.mark.parametrize("v,code", [
    (verdict.PASS, 0), (verdict.BLOCK, 1),
    (verdict.APPROVAL, 2), (verdict.ANALYSIS_ERROR, 3),
])
def test_c20_exit_codes_match_verdict_table(v, code):
    r = P.aggregate_phase([_exec("only", v)])
    assert r.exit_code == code == verdict.EXIT_CODE[v]


# ---- C61 : gate order does not change overall verdict (PBT) ----
_VERDICTS = st.sampled_from(verdict.VERDICTS)


@given(vs=st.lists(_VERDICTS, min_size=1, max_size=8))
def test_c61_order_independent(vs):
    import random

    execs = [_exec(f"g{i}", v) for i, v in enumerate(vs)]
    a = P.aggregate_phase(list(execs)).overall_verdict
    shuffled = list(execs)
    random.Random(1234).shuffle(shuffled)
    b = P.aggregate_phase(shuffled).overall_verdict
    assert a == b


# ---- C64 / C65 : aggregation is ALWAYS severity-rank max over executed gates ----
@given(vs=st.lists(_VERDICTS, min_size=1, max_size=8))
def test_c64_always_severity_rank(vs):
    execs = [_exec(f"g{i}", v) for i, v in enumerate(vs)]
    r = P.aggregate_phase(execs)
    expected = max(vs, key=verdict.SEVERITY_RANK.__getitem__)
    assert r.overall_verdict == expected
    # C65: exit-code-max would diverge whenever approval outranks block by code.
    exit_max = max(vs, key=lambda v: verdict.EXIT_CODE[v])
    if verdict.EXIT_CODE[exit_max] != verdict.SEVERITY_RANK[expected] and exit_max != expected:
        assert r.overall_verdict != exit_max


def test_result_digest_excludes_order_and_observational():
    a = P.aggregate_phase(
        [_exec("a", verdict.PASS), _exec("b", verdict.APPROVAL)],
        run_id="run-1",
        observational={"duration_s": 1.2, "timestamp": "2026-08-07T00:00:00Z"},
    )
    b = P.aggregate_phase(
        [_exec("b", verdict.APPROVAL), _exec("a", verdict.PASS)],
        run_id="run-2",
        observational={"duration_s": 99.0, "timestamp": "2030-01-01T00:00:00Z"},
    )
    assert a.result_digest() == b.result_digest()
