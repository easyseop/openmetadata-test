"""L7 three-tier output — C14, C94-C100.

All three tiers are rendered from the ONE system JSON; verdict and quantity must
agree across them.
"""
from __future__ import annotations

import pytest

from acgh import phase as P
from acgh import rollup as RU
from acgh import verdict


def _sys(executions, *, phase=P.POSTMERGE, **kw):
    r = P.aggregate_phase(executions, phase=phase, **kw)
    return r.to_system_json()


def _ex(name, v, *, status=P.EXECUTED, required=True, applicable=True, advisory=False, reasons=(), target_count=None):
    return P.GateExecution(name, status, v, reasons=tuple(reasons), required=required,
                           applicable=applicable, advisory=advisory, target_count=target_count)


# ---- C14 : 3-tier output agrees on verdict and quantity ----
def test_c14_three_tiers_agree():
    sysj = _sys([_ex("a", verdict.PASS), _ex("b", verdict.APPROVAL)])
    rendered = RU.render_all(sysj)
    assert RU.check_output_invariants(rendered) == ()
    assert rendered["manager"]["overall_verdict"] == verdict.APPROVAL
    assert rendered["practitioner"]["overall_verdict"] == verdict.APPROVAL
    assert rendered["system"]["overall_verdict"] == verdict.APPROVAL


# ---- C94 : manager pass but system approval -> invariant fails ----
def test_c94_manager_disagreement_detected():
    sysj = _sys([_ex("a", verdict.APPROVAL)])
    rendered = RU.render_all(sysj)
    rendered["manager"]["overall_verdict"] = verdict.PASS  # corrupt one tier
    problems = RU.check_output_invariants(rendered)
    assert any("overall_verdict disagreement" in p for p in problems)


# ---- C95 : 99/100 targets normal -> "99/100" + next action ----
def test_c95_target_checked_over_total():
    sysj = _sys([_ex("a", verdict.PASS)])
    sysj["target_rollup"] = {"checked": 99, "total": 100}
    m = RU.manager_summary(sysj)
    assert m["checked_over_total"] == "99/100"
    assert m["next_action"]


# ---- C96 : executed gates pass but a required gate not run -> not shown normal ----
def test_c96_incomplete_not_shown_as_normal():
    sysj = _sys([
        _ex("a", verdict.PASS),
        _ex("b", None, status=P.SKIPPED_MISSING_INPUT),
    ])
    m = RU.manager_summary(sysj)
    assert m["phase_status"] == P.INCOMPLETE
    assert m["overall_verdict"] != verdict.PASS  # never a clean "정상"
    assert "미완료" in m["next_action"]
    # the skipped required gate is counted as 미실행, never as 정상
    assert m["counts"][RU.NOT_RUN] >= 1
    assert m["checked"] < m["total"]


# ---- C97 : zero targets -> "검사 대상 없음", not "0/0 정상" ----
def test_c97_zero_targets_message():
    sysj = _sys([_ex("a", verdict.PASS)])
    sysj["target_rollup"] = {"checked": 0, "total": 0}
    m = RU.manager_summary(sysj)
    assert m["checked_over_total"] == "검사 대상 없음"


# ---- C98 : same path in several IDs -> unique-path vs (path,ID) combos distinct ----
def test_c98_unique_paths_vs_combinations():
    paths = ["p/a", "p/a", "p/b"]
    combos = [("p/a", "ID1"), ("p/a", "ID2"), ("p/b", "ID1")]
    tr = RU.target_rollup(paths, combos)
    assert tr["unique_path_count"] == 2
    assert tr["path_id_combination_count"] == 3


# ---- C99 : hundreds of reasons -> manager summarizes count, practitioner keeps all ----
def test_c99_manager_counts_practitioner_full():
    reasons = tuple(f"reason-{i}" for i in range(300))
    sysj = _sys([_ex("a", verdict.BLOCK, reasons=reasons)])
    m = RU.manager_summary(sysj)
    d = RU.practitioner_detail(sysj)
    assert m["reason_counts"]["a"] == 300
    assert len(d["gates"][0]["reasons"]) == 300


# ---- C114 : very long reason -> JSON keeps full text, manager preview trimmed ----
def test_c114_long_reason_preview_trimmed_full_preserved():
    long_reason = "x" * 5000
    sysj = _sys([_ex("a", verdict.BLOCK, reasons=(long_reason,))])
    m = RU.manager_summary(sysj)
    d = RU.practitioner_detail(sysj)
    assert len(m["reason_previews"]["a"]) <= RU._MANAGER_SUMMARY_LIMIT
    assert d["gates"][0]["reasons"][0] == long_reason  # full preserved


# ---- C100 : counting order change -> same numbers ----
def test_c100_count_order_independent():
    execs = [_ex("a", verdict.PASS), _ex("b", verdict.APPROVAL), _ex("c", verdict.BLOCK)]
    sysj1 = _sys(list(execs))
    sysj2 = _sys(list(reversed(execs)))
    assert RU.manager_summary(sysj1)["counts"] == RU.manager_summary(sysj2)["counts"]
    assert RU.manager_summary(sysj1)["overall_verdict"] == RU.manager_summary(sysj2)["overall_verdict"]


def test_rerun_hint_present_for_skipped():
    sysj = _sys([
        _ex("a", verdict.PASS),
        _ex("debt", None, status=P.SKIPPED_MISSING_INPUT),
    ])
    d = RU.practitioner_detail(sysj)
    debt = next(g for g in d["gates"] if g["name"] == "debt")
    assert debt["rerun"]
