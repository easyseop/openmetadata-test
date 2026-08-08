"""Phase bundling — active candidate selection.

Reuses ``acgh.candidate`` (CandidateLock schema v1/v2, digest, binding). This
module only decides *which approved lock is the active baseline* via an explicit
``active-candidate.yaml`` pointer. It never auto-picks "most recent approved".

Layout under ``<registration>/candidate-locks/``::

    <name>.yaml            # a CandidateLock (schema v1 or v2)
    <name>.approval.yaml   # approver/approved_at/rationale + candidate_lock_digest
    active-candidate.yaml  # candidate_lock_digest of the chosen lock

Outcomes (status):
    selected        — one approved lock matches the active pointer
    analysis_error  — no active pointer / no locks / corrupt lock (verdict=analysis_error)
    blocked         — active points to a missing/unapproved lock (phase must not start)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from acgh import candidate as candidate_mod
from acgh.approval import _is_placeholder, validate_approval_metadata

SELECTED = "selected"
ANALYSIS_ERROR = "analysis_error"
BLOCKED = "blocked"

@dataclass(frozen=True)
class ActiveCandidateSelection:
    status: str
    reasons: tuple[str, ...] = ()
    lock: candidate_mod.CandidateLock | None = None
    lock_digest: str | None = None
    lock_path: str | None = None
    provenance: tuple[dict, ...] = field(default_factory=tuple)


def _load_locks(locks_dir: Path):
    found: dict[str, tuple[Path, candidate_mod.CandidateLock]] = {}
    errors: list[tuple[Path, Exception]] = []
    if not locks_dir.is_dir():
        return found, errors
    for path in sorted(locks_dir.glob("*.yaml")):
        if path.name == "active-candidate.yaml" or path.name.endswith(".approval.yaml"):
            continue
        try:
            lock = candidate_mod.load_candidate_lock(path)
        except Exception as exc:  # noqa: BLE001 - CandidateLockError, yaml, etc.
            errors.append((path, exc))
            continue
        found[lock.digest()] = (path, lock)
    return found, errors


def _provenance(found, active_digest):
    return tuple(
        {
            "lock_path": str(path),
            "commit_sha": lock.candidate.commit_sha,
            "tree_sha": lock.candidate.tree_sha,
            "digest": digest,
        }
        for digest, (path, lock) in sorted(found.items())
        if digest != active_digest
    )


def select_active_candidate(registration_dir) -> ActiveCandidateSelection:
    locks_dir = Path(registration_dir) / "candidate-locks"
    active_path = locks_dir / "active-candidate.yaml"
    found, parse_errors = _load_locks(locks_dir)

    if not active_path.is_file():
        return ActiveCandidateSelection(
            ANALYSIS_ERROR,
            reasons=(f"no active-candidate pointer: {active_path}",),
            provenance=_provenance(found, None),
        )
    if not found and not parse_errors:
        return ActiveCandidateSelection(
            ANALYSIS_ERROR,
            reasons=(f"no candidate locks under {locks_dir}",),
        )

    try:
        active = yaml.safe_load(active_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return ActiveCandidateSelection(
            ANALYSIS_ERROR, reasons=(f"active-candidate.yaml malformed: {exc}",)
        )
    active_digest = active.get("candidate_lock_digest") if isinstance(active, dict) else None
    if not active_digest:
        return ActiveCandidateSelection(
            ANALYSIS_ERROR,
            reasons=("active-candidate.yaml missing candidate_lock_digest",),
        )

    provenance = _provenance(found, active_digest)

    if active_digest not in found:
        if parse_errors:
            details = "; ".join(f"{p.name}: {exc}" for p, exc in parse_errors)
            return ActiveCandidateSelection(
                ANALYSIS_ERROR,
                reasons=(f"corrupt candidate lock(s): {details}",),
                provenance=provenance,
            )
        available = ", ".join(sorted(found)) or "(none)"
        return ActiveCandidateSelection(
            BLOCKED,
            reasons=(
                "active candidate_lock_digest not found among locks",
                f"active={active_digest}",
                f"available=[{available}]",
            ),
            provenance=provenance,
        )

    lock_path, lock = found[active_digest]
    lock_digest = lock.digest()
    approval_path = lock_path.parent / (lock_path.stem + ".approval.yaml")
    common = dict(lock=lock, lock_digest=lock_digest, lock_path=str(lock_path), provenance=provenance)

    if not approval_path.is_file():
        return ActiveCandidateSelection(
            BLOCKED,
            reasons=(
                "active points to an unapproved lock (no approval file)",
                f"expected {approval_path.name}",
            ),
            **common,
        )
    try:
        approval = yaml.safe_load(approval_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        return ActiveCandidateSelection(
            ANALYSIS_ERROR, reasons=(f"approval malformed: {exc}",), **common
        )

    reasons: list[str] = []
    if approval.get("candidate_lock_digest") != lock_digest:
        reasons.append(
            f"approval digest mismatch: {approval.get('candidate_lock_digest')} != {lock_digest}"
        )
    reasons.extend(validate_approval_metadata(approval))

    if reasons:
        return ActiveCandidateSelection(BLOCKED, reasons=tuple(reasons), **common)
    return ActiveCandidateSelection(SELECTED, **common)


def select_approved_candidate(registration_dir, lock_digest: str) -> ActiveCandidateSelection:
    """Select one explicitly named approved lock without changing the active pointer."""
    locks_dir = Path(registration_dir) / "candidate-locks"
    found, parse_errors = _load_locks(locks_dir)
    if lock_digest not in found:
        details = "; ".join(f"{p.name}: {exc}" for p, exc in parse_errors)
        reason = f"approved baseline lock digest not found: {lock_digest}"
        if details:
            reason += f"; corrupt lock(s): {details}"
        return ActiveCandidateSelection(ANALYSIS_ERROR, reasons=(reason,))
    lock_path, lock = found[lock_digest]
    approval_path = lock_path.with_name(lock_path.stem + ".approval.yaml")
    common = dict(
        lock=lock,
        lock_digest=lock_digest,
        lock_path=str(lock_path),
        provenance=_provenance(found, lock_digest),
    )
    if not approval_path.is_file():
        return ActiveCandidateSelection(
            BLOCKED,
            reasons=(f"approved baseline has no approval file: {approval_path}",),
            **common,
        )
    try:
        approval = yaml.safe_load(approval_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        return ActiveCandidateSelection(
            ANALYSIS_ERROR, reasons=(f"baseline approval unreadable: {exc}",), **common
        )
    reasons = list(validate_approval_metadata(approval))
    if approval.get("candidate_lock_digest") != lock_digest:
        reasons.append("baseline approval digest does not match its Candidate lock")
    if reasons:
        return ActiveCandidateSelection(BLOCKED, reasons=tuple(reasons), **common)
    return ActiveCandidateSelection(SELECTED, **common)
