"""T72 — bounded, auditable break-glass authorization.

A break-glass record never rewrites an ``acgh-result`` and never converts its
machine verdict to pass.  This module only checks whether a separately stored
exception is valid for one exact result, candidate, policy, gate, and time.
Integrity gates remain non-waivable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = (
    Path(__file__).parent / "schema" / "break-glass-attestation.schema.json"
)
NON_WAIVABLE_GATES = frozenset({
    "candidate-lock",
    "test-candidate-binding",
    "verdict-integrity",
    "artifact-digest",
    "release-digest",
})


class BreakGlassError(ValueError):
    """Break-glass evidence is malformed or semantically unsafe."""


@dataclass(frozen=True)
class BreakGlassAttestation:
    attestation_id: str
    ticket: str
    requested_by: str
    approvers: tuple[str, ...]
    target_result_digest: str
    candidate_sha: str
    policy_digest: str
    allowed_gates: tuple[str, ...]
    requested_at: datetime
    expires_at: datetime
    post_validation_due_at: datetime
    reason: str
    status: str
    closed_at: datetime | None = None
    normal_rerun_result_digest: str | None = None


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def _time(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise BreakGlassError(f"{field}: invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise BreakGlassError(f"{field}: timezone is required")
    return parsed.astimezone(timezone.utc)


def parse_break_glass(data: dict) -> BreakGlassAttestation:
    if not isinstance(data, dict):
        raise BreakGlassError("break-glass attestation is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise BreakGlassError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )

    requested_at = _time(data["requested_at"], "requested_at")
    expires_at = _time(data["expires_at"], "expires_at")
    post_due = _time(data["post_validation_due_at"], "post_validation_due_at")
    if expires_at <= requested_at:
        raise BreakGlassError("expires_at must be after requested_at")
    if post_due < expires_at:
        raise BreakGlassError(
            "post_validation_due_at must be at or after expires_at"
        )
    if data["requested_by"] in data["approvers"]:
        raise BreakGlassError("requester cannot count as an approver")
    forbidden = sorted(set(data["allowed_gates"]) & NON_WAIVABLE_GATES)
    if forbidden:
        raise BreakGlassError(
            f"non-waivable gates requested: {forbidden}"
        )

    closed_at = None
    if data.get("closed_at") is not None:
        closed_at = _time(data["closed_at"], "closed_at")
        if closed_at < requested_at:
            raise BreakGlassError("closed_at cannot precede requested_at")
    return BreakGlassAttestation(
        attestation_id=data["attestation_id"],
        ticket=data["ticket"],
        requested_by=data["requested_by"],
        approvers=tuple(data["approvers"]),
        target_result_digest=data["target_result_digest"],
        candidate_sha=data["candidate_sha"],
        policy_digest=data["policy_digest"],
        allowed_gates=tuple(data["allowed_gates"]),
        requested_at=requested_at,
        expires_at=expires_at,
        post_validation_due_at=post_due,
        reason=data["reason"],
        status=data["status"],
        closed_at=closed_at,
        normal_rerun_result_digest=data.get("normal_rerun_result_digest"),
    )


def load_break_glass(path) -> BreakGlassAttestation:
    return parse_break_glass(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def check_break_glass(
    data,
    *,
    requested_gate: str,
    result_digest: str,
    candidate_sha: str,
    policy_digest: str,
    now: datetime,
    name: str = "break-glass-authorization",
) -> verdict.GateResult:
    """Validate one exception; PASS means the exception record is valid only."""
    try:
        attestation = (
            data
            if isinstance(data, BreakGlassAttestation)
            else parse_break_glass(data)
        )
    except BreakGlassError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"invalid attestation: {exc}",)
        )

    if now.tzinfo is None or now.utcoffset() is None:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            ("current time must be timezone-aware",),
        )
    now_utc = now.astimezone(timezone.utc)
    stale = []
    if attestation.target_result_digest != result_digest:
        stale.append("result digest")
    if attestation.candidate_sha != candidate_sha:
        stale.append("candidate SHA")
    if attestation.policy_digest != policy_digest:
        stale.append("policy digest")
    if stale:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"stale break-glass: {item} mismatch" for item in stale),
        )
    if requested_gate in NON_WAIVABLE_GATES:
        return verdict.GateResult(
            name, verdict.BLOCK, (f"gate is non-waivable: {requested_gate}",)
        )
    if requested_gate not in attestation.allowed_gates:
        return verdict.GateResult(
            name,
            verdict.BLOCK,
            (f"gate not authorized by attestation: {requested_gate}",),
        )
    if attestation.status != "active":
        return verdict.GateResult(
            name, verdict.BLOCK, ("attestation is already closed",)
        )
    if now_utc >= attestation.expires_at:
        return verdict.GateResult(
            name, verdict.BLOCK, ("attestation expired",)
        )
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"authorized gate={requested_gate}",
            f"ticket={attestation.ticket}",
            f"approvers={len(attestation.approvers)}",
            "machine verdict remains unchanged",
        ),
    )


def break_glass_statistics(records, *, now: datetime) -> dict[str, int]:
    """Aggregate auditable exception counts without changing any verdict."""
    stats = {"active": 0, "expired": 0, "closed": 0, "invalid": 0}
    if now.tzinfo is None or now.utcoffset() is None:
        raise BreakGlassError("statistics time must be timezone-aware")
    now_utc = now.astimezone(timezone.utc)
    for record in records:
        try:
            item = (
                record
                if isinstance(record, BreakGlassAttestation)
                else parse_break_glass(record)
            )
        except BreakGlassError:
            stats["invalid"] += 1
            continue
        if item.status == "closed":
            stats["closed"] += 1
        elif now_utc >= item.expires_at:
            stats["expired"] += 1
        else:
            stats["active"] += 1
    return stats
