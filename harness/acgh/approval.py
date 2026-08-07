"""Shared validation for attributable human approvals."""
from __future__ import annotations

import datetime as _dt

_PLACEHOLDERS = {
    "", "tbd", "todo", "unassigned", "placeholder", "changeme",
    "none", "n/a", "요청자", "담당자", "approver", "rationale",
}


def _is_placeholder(value) -> bool:
    if not isinstance(value, str):
        return True
    stripped = value.strip()
    if stripped.lower() in _PLACEHOLDERS:
        return True
    return "<" in stripped and ">" in stripped


def _valid_rfc3339(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = _dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_approval_metadata(approval: dict) -> tuple[str, ...]:
    """Return every missing/placeholder human approval field."""
    if not isinstance(approval, dict):
        return ("approval must be a mapping",)
    reasons: list[str] = []
    if _is_placeholder(approval.get("approver")):
        reasons.append("approver is placeholder/empty — real sign-off required")
    if _is_placeholder(approval.get("rationale")):
        reasons.append("rationale is placeholder/empty")
    if not _valid_rfc3339(approval.get("approved_at")):
        reasons.append("approved_at not RFC3339 (e.g. 2026-08-07T23:00:00Z)")
    return tuple(reasons)
