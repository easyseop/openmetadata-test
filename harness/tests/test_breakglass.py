"""T72 break-glass procedure tests."""
from datetime import datetime, timezone

import pytest

from acgh import breakglass as B
from acgh import verdict as V

_RESULT = "sha256:" + "a" * 64
_POLICY = "sha256:" + "b" * 64
_SHA = "c" * 40
_NOW = datetime(2026, 7, 25, 10, 0, tzinfo=timezone.utc)


def _record():
    return {
        "schema_version": 1,
        "attestation_id": "BG-2026-001",
        "ticket": "INC-4242",
        "requested_by": "operator",
        "approvers": ["security", "service-owner"],
        "target_result_digest": _RESULT,
        "candidate_sha": _SHA,
        "policy_digest": _POLICY,
        "allowed_gates": ["runtime-smoke"],
        "requested_at": "2026-07-25T09:00:00Z",
        "expires_at": "2026-07-25T11:00:00Z",
        "post_validation_due_at": "2026-07-26T11:00:00Z",
        "reason": "restore critical metadata access",
        "status": "active",
    }


def _check(record=None, **overrides):
    args = {
        "requested_gate": "runtime-smoke",
        "result_digest": _RESULT,
        "candidate_sha": _SHA,
        "policy_digest": _POLICY,
        "now": _NOW,
    }
    args.update(overrides)
    return B.check_break_glass(record or _record(), **args)


def test_valid_two_person_bounded_exception_passes_only_its_record():
    result = _check()
    assert result.verdict == V.PASS
    assert result.reasons[-1] == "machine verdict remains unchanged"


def test_stale_binding_is_analysis_error():
    assert _check(candidate_sha="0" * 40).verdict == V.ANALYSIS_ERROR
    assert _check(result_digest="sha256:" + "0" * 64).verdict == V.ANALYSIS_ERROR


def test_expired_closed_or_unlisted_gate_blocks():
    late = datetime(2026, 7, 25, 11, 0, tzinfo=timezone.utc)
    assert _check(now=late).verdict == V.BLOCK
    assert _check(requested_gate="migration").verdict == V.BLOCK

    closed = _record()
    closed.update({
        "status": "closed",
        "closed_at": "2026-07-25T10:30:00Z",
        "normal_rerun_result_digest": "sha256:" + "d" * 64,
    })
    assert _check(closed).verdict == V.BLOCK


def test_integrity_gates_are_never_waivable():
    record = _record()
    record["allowed_gates"] = ["candidate-lock"]
    result = _check(record, requested_gate="candidate-lock")
    assert result.verdict == V.ANALYSIS_ERROR
    with pytest.raises(B.BreakGlassError, match="non-waivable"):
        B.parse_break_glass(record)


def test_requester_cannot_approve_and_two_approvals_required():
    record = _record()
    record["approvers"] = ["operator", "security"]
    with pytest.raises(B.BreakGlassError, match="requester"):
        B.parse_break_glass(record)
    record = _record()
    record["approvers"] = ["security"]
    with pytest.raises(B.BreakGlassError, match="schema"):
        B.parse_break_glass(record)


def test_post_validation_deadline_and_timezone_are_enforced():
    record = _record()
    record["post_validation_due_at"] = "2026-07-25T10:30:00Z"
    with pytest.raises(B.BreakGlassError, match="post_validation"):
        B.parse_break_glass(record)
    record = _record()
    record["expires_at"] = "2026-07-25T11:00:00"
    with pytest.raises(B.BreakGlassError, match="timezone"):
        B.parse_break_glass(record)


def test_statistics_separate_active_expired_closed_and_invalid():
    expired = _record()
    expired["expires_at"] = "2026-07-25T09:30:00Z"
    expired["post_validation_due_at"] = "2026-07-26T09:30:00Z"
    closed = _record()
    closed.update({
        "status": "closed",
        "closed_at": "2026-07-25T09:30:00Z",
        "normal_rerun_result_digest": "sha256:" + "d" * 64,
    })
    stats = B.break_glass_statistics(
        [_record(), expired, closed, {"bad": True}], now=_NOW
    )
    assert stats == {"active": 1, "expired": 1, "closed": 1, "invalid": 1}


def test_naive_current_time_fails_closed():
    naive = datetime(2026, 7, 25, 10, 0)
    assert _check(now=naive).verdict == V.ANALYSIS_ERROR
    with pytest.raises(B.BreakGlassError, match="timezone-aware"):
        B.break_glass_statistics([_record()], now=naive)
