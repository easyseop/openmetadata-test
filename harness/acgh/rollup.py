"""Phase bundling — L7 three-tier output (설계 §10).

All three views are RENDERED from the ONE system JSON produced by
``phase.PhaseResult.to_system_json()`` — never recomputed independently. If any
view disagreed with the system JSON on a verdict or a count, that is a bug the
tests must catch (C14, C94-C100).

- manager summary: counts (정상/검토/미실행/차단), ``확인 수/전체 수`` over the
  required+applicable gates, and the next action. Reasons are summarized to
  counts; the full text lives in the practitioner detail.
- practitioner detail: per-gate verdict / SHAs / IDs / paths / missing input /
  rerun hint, with every reason preserved.
- system JSON: the input itself (all inputs, digests, SHAs, reasons, approval).
"""
from __future__ import annotations

from acgh import phase as P
from acgh import verdict

# manager-facing buckets
NORMAL = "normal"      # 정상  — executed & pass
REVIEW = "review"      # 검토  — executed & approval
BLOCKED = "blocked"    # 차단  — executed & block/analysis_error, OR failed
NOT_RUN = "not_run"    # 미실행 — skipped_missing_input / blocked_by_preflight / not_applicable

_MANAGER_SUMMARY_LIMIT = 160  # 관리자 요약 reason 미리보기 길이 (C114)


def _bucket(gate: dict) -> str:
    status = gate["execution_status"]
    if status == P.EXECUTED:
        v = gate["verdict"]
        if v == verdict.PASS:
            return NORMAL
        if v == verdict.APPROVAL:
            return REVIEW
        return BLOCKED  # block / analysis_error
    if status == P.FAILED:
        return BLOCKED
    return NOT_RUN  # skipped_missing_input / blocked_by_preflight / not_applicable


def _counted_gates(system_json: dict) -> list[dict]:
    """Gates that count toward 확인 수/전체 수: required + applicable, non-advisory."""
    return [
        g for g in system_json["gates"]
        if g.get("required") and g.get("applicable") and not g.get("advisory")
    ]


def manager_summary(system_json: dict) -> dict:
    counts = {NORMAL: 0, REVIEW: 0, BLOCKED: 0, NOT_RUN: 0}
    for g in system_json["gates"]:
        if g.get("advisory"):
            continue  # advisory gates are informational; not in the manager tally
        counts[_bucket(g)] += 1

    # 확인 수/전체 수: prefer an explicit target rollup (C95/C97), else count the
    # required+applicable gates.
    target_rollup = system_json.get("target_rollup")
    if target_rollup is not None:
        total = target_rollup["total"]
        checked = target_rollup["checked"]
    else:
        counted = _counted_gates(system_json)
        total = len(counted)
        checked = sum(1 for g in counted if g["execution_status"] == P.EXECUTED)

    phase_status = system_json["phase_status"]
    overall = system_json["overall_verdict"]
    if phase_status == P.INCOMPLETE:
        next_action = (
            "필수 검사 미완료. 미실행 검사의 누락 입력을 채운 뒤 다시 실행하세요. "
            "완료 전 통과로 확정 금지."
        )
    elif (
        overall == verdict.PASS
        and system_json.get("phase") == P.POSTMERGE
        and system_json.get("inputs", {}).get("verification_scope") == "source-only"
    ):
        next_action = (
            "소스 검사는 통과했습니다. 승인된 build-artifact Candidate lock과 "
            "Runtime Contract 결과가 없으므로 운영 배포를 승인하지 마세요."
        )
    elif overall == verdict.PASS:
        next_action = "모든 필수 검사 통과. 다음 단계로 진행할 수 있습니다."
    elif overall == verdict.APPROVAL:
        next_action = "검토 대상이 있습니다. 담당자 승인 후 진행하세요."
    elif overall == verdict.BLOCK:
        next_action = "차단 사유가 있습니다. 원인을 해결한 뒤 다시 실행하세요."
    else:
        next_action = "분석 오류가 있습니다. 검사 실패 로그를 확인하고 재실행하세요."

    checked_over_total = "검사 대상 없음" if total == 0 else f"{checked}/{total}"

    return {
        "phase": system_json["phase"],
        "overall_verdict": overall,
        "phase_status": phase_status,
        "result_digest": system_json.get("result_digest"),
        "verification_scope": system_json.get("inputs", {}).get("verification_scope"),
        "counts": counts,
        "checked": checked,
        "total": total,
        "checked_over_total": checked_over_total,
        "next_action": next_action,
        # 관리자 요약은 사유 건수만, 원문은 실무자 상세로 (C99/C114)
        "reason_counts": {
            g["name"]: len(g["reasons"]) for g in system_json["gates"] if g["reasons"]
        },
        "reason_previews": {
            g["name"]: _preview(g["reasons"][0])
            for g in system_json["gates"]
            if g["reasons"]
        },
    }


def _preview(text: str) -> str:
    text = " ".join(str(text).split())
    if len(text) <= _MANAGER_SUMMARY_LIMIT:
        return text
    return text[: _MANAGER_SUMMARY_LIMIT - 1] + "…"


def practitioner_detail(system_json: dict) -> dict:
    inputs = system_json.get("inputs", {})
    gates = []
    for g in system_json["gates"]:
        rerun = None
        if g["execution_status"] in (P.SKIPPED_MISSING_INPUT, P.FAILED, P.BLOCKED_BY_PREFLIGHT):
            rerun = _rerun_hint(system_json, g)
        gates.append(
            {
                "name": g["name"],
                "verdict": g["verdict"],
                "execution_status": g["execution_status"],
                "target_count": g.get("target_count"),
                "reasons": list(g["reasons"]),          # full, never truncated
                "evidence": list(g.get("evidence", [])),
                "rerun": rerun,
            }
        )
    return {
        "phase": system_json["phase"],
        "overall_verdict": system_json["overall_verdict"],
        "phase_status": system_json["phase_status"],
        "inputs": inputs,
        "result_digest": system_json.get("result_digest"),
        "gates": gates,
    }


def _rerun_hint(system_json: dict, gate: dict) -> str:
    if gate["execution_status"] == P.SKIPPED_MISSING_INPUT:
        return f"{gate['name']}: 누락 입력을 제공한 뒤 재실행하세요."
    if gate["execution_status"] == P.BLOCKED_BY_PREFLIGHT:
        return f"{gate['name']}: preflight 차단을 해결한 뒤 phase를 다시 시작하세요."
    return f"{gate['name']}: 실패 로그를 확인하고 원인 수정 후 재실행하세요."


def render_all(system_json: dict) -> dict:
    """Render the three tiers together for convenience/testing."""
    return {
        "manager": manager_summary(system_json),
        "practitioner": practitioner_detail(system_json),
        "system": system_json,
    }


def check_output_invariants(rendered: dict) -> tuple[str, ...]:
    """Return invariant violations across the three tiers (empty tuple = ok, C94/C100).

    All three views derive from one system JSON, so a disagreement in verdict or
    count is a rendering bug that must fail a test.
    """
    problems: list[str] = []
    m, d, s = rendered["manager"], rendered["practitioner"], rendered["system"]
    if not (m["overall_verdict"] == d["overall_verdict"] == s["overall_verdict"]):
        problems.append(
            f"overall_verdict disagreement: manager={m['overall_verdict']} "
            f"practitioner={d['overall_verdict']} system={s['overall_verdict']}"
        )
    if not (m["phase_status"] == d["phase_status"] == s["phase_status"]):
        problems.append("phase_status disagreement across tiers")
    if not (m.get("result_digest") == d.get("result_digest") == s.get("result_digest")):
        problems.append("result_digest disagreement across tiers")
    # counts must reconcile with the number of gates in the system JSON
    non_advisory = [g for g in s["gates"] if not g.get("advisory")]
    if sum(m["counts"].values()) != len(non_advisory):
        problems.append("manager counts do not sum to the non-advisory gate count")
    return tuple(problems)


def target_rollup(unique_paths, path_id_pairs) -> dict:
    """Distinguish unique path count from (path, ID) combination count (C98)."""
    return {
        "unique_path_count": len(set(unique_paths)),
        "path_id_combination_count": len(set(path_id_pairs)),
    }
