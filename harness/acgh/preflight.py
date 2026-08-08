"""Phase bundling — L2 preflight (batch input verification).

The preflight NEVER stops at the first problem. It collects every input issue
and returns them together so an operator can fix them in one pass (설계 §7).

Two classes of problem (설계 §7):
- ``blocking`` — base/target/candidate objects, active-baseline approval,
  candidate ancestry/consistency, missing repository policy files, partial-clone
  blobs. Any blocking problem forbids the phase from starting.
- per-gate ``optional`` — a missing input that only disables ONE gate
  (change-intent -> T41, conflict-rate/debt-thresholds -> T43). The phase may
  still start; the affected gate becomes ``skipped_missing_input`` in L3.

The module reuses ``acgh.gitprim`` for object/blob probing and never
reimplements gate judgment. ``registry.source.snapshot_sha`` and any past
proposal/evidence SHAs are PROVENANCE only: they are recorded but excluded from
the active-source consistency comparison (C6/C34).

Covers C4-C8, C34, C46-C51, C76-C78, C101, C105.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from acgh import gitprim

# check statuses
OK = "ok"
MISSING = "missing"
UNREACHABLE = "unreachable"      # ref/object not resolvable / not present
INVALID = "invalid"             # present but out of contract (bad value/syntax)
INCONSISTENT = "inconsistent"   # active sources disagree on a pinned SHA
BLOB_MISSING = "blob_missing"   # blobless clone lacks a required blob


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    blocking: bool
    detail: str = ""
    value: str | None = None
    required_for: tuple[str, ...] = ()      # gate names disabled by an optional miss
    next_action: str = ""

    @property
    def ok(self) -> bool:
        return self.status == OK


@dataclass(frozen=True)
class PreflightReport:
    checks: tuple[Check, ...] = ()

    @property
    def blocking_problems(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if c.blocking and not c.ok)

    @property
    def ready(self) -> bool:
        """True iff no blocking problem is present (optional misses are allowed)."""
        return not self.blocking_problems

    def optional_missing(self) -> tuple[Check, ...]:
        return tuple(c for c in self.checks if not c.blocking and not c.ok)

    def disabled_gates(self) -> frozenset[str]:
        """Gate names that must become skipped_missing_input in L3."""
        gates: set[str] = set()
        for c in self.optional_missing():
            gates.update(c.required_for)
        return frozenset(gates)

    def to_json(self) -> dict:
        return {
            "ready": self.ready,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "blocking": c.blocking,
                    **({"value": c.value} if c.value is not None else {}),
                    **({"detail": c.detail} if c.detail else {}),
                    **({"required_for": list(c.required_for)} if c.required_for else {}),
                    **({"next_action": c.next_action} if c.next_action else {}),
                }
                for c in self.checks
            ],
            "blocking_problems": [c.name for c in self.blocking_problems],
            "disabled_gates": sorted(self.disabled_gates()),
        }


# --- individual probes ------------------------------------------------------
def check_commit_object(repo: str, label: str, sha: str | None, *, blocking: bool = True) -> Check:
    """A required commit object must resolve and be present locally (C8/C78)."""
    if not sha:
        return Check(label, MISSING, blocking, detail=f"{label} ref/sha not provided")
    try:
        present = gitprim.object_exists(repo, sha)
    except Exception as exc:  # noqa: BLE001 - never let preflight itself crash
        return Check(label, UNREACHABLE, blocking, detail=f"probe failed: {exc}", value=sha)
    if not present:
        return Check(
            label,
            UNREACHABLE,
            blocking,
            detail=f"commit object not present locally: {sha}",
            value=sha,
            next_action=f"git -C {repo} fetch <remote> {sha}",
        )
    return Check(label, OK, blocking, value=sha)


def check_blob_access(repo: str, ref: str, path: str, *, blocking: bool = True) -> Check:
    """A blobless partial clone may lack a needed blob (C76). Give fetch guidance."""
    name = f"blob:{path}"
    try:
        gitprim.blob_bytes(repo, ref, path)
    except gitprim.GitPrimitiveError as exc:
        return Check(
            name,
            BLOB_MISSING,
            blocking,
            detail=f"cannot read {ref}:{path}: {exc}",
            value=f"{ref}:{path}",
            next_action=(
                f"git -C {repo} fetch --filter=blob:none <remote> {ref} "
                f"&& git -C {repo} cat-file blob {ref}:{path}"
            ),
        )
    return Check(name, OK, blocking, value=f"{ref}:{path}")


def check_file_present(name: str, path, *, blocking: bool, required_for=()) -> Check:
    """A required policy/registration file (blocking) or per-gate input (optional)."""
    p = Path(path) if path is not None else None
    if p is None or not p.is_file():
        return Check(
            name,
            MISSING,
            blocking,
            detail=f"file not found: {path}",
            value=str(path) if path is not None else None,
            required_for=tuple(required_for),
        )
    return Check(name, OK, blocking, value=str(p), required_for=tuple(required_for))


def check_conflict_rate(value, *, required_for=("debt",)) -> Check:
    """conflict-rate is a per-gate (T43) optional input.

    Absent -> missing (T43 skipped, C47/C101, never assumed 0).
    Present but out of [0,1] / NaN / Inf -> invalid (C50/C51).
    """
    name = "conflict_rate"
    if value is None:
        return Check(name, MISSING, blocking=False, detail="not provided", required_for=tuple(required_for))
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return Check(name, INVALID, blocking=False, detail=f"not numeric: {value!r}", value=str(value), required_for=tuple(required_for))
    if math.isnan(value) or math.isinf(value):
        return Check(name, INVALID, blocking=False, detail=f"NaN/Inf not allowed: {value!r}", value=str(value), required_for=tuple(required_for))
    if not 0.0 <= float(value) <= 1.0:
        return Check(name, INVALID, blocking=False, detail=f"out of [0,1]: {value!r}", value=str(value), required_for=tuple(required_for))
    return Check(name, OK, blocking=False, value=str(value), required_for=tuple(required_for))


def check_active_source_consistency(active_sources, provenance=()) -> tuple[Check, ...]:
    """All ACTIVE sources must pin the same candidate commit SHA (C4/C5).

    ``active_sources`` is an iterable of ``(name, sha)``. ``provenance`` is an
    iterable of ``(name, sha)`` recorded but EXCLUDED from the equality test:
    past snapshot/proposal/evidence SHAs are expected to differ (C6/C34).
    """
    active = list(active_sources)
    checks: list[Check] = []
    shas = {sha for _n, sha in active}
    consistent = len(shas) <= 1
    if consistent:
        checks.append(
            Check(
                "candidate_consistency",
                OK,
                blocking=True,
                detail=f"all active sources pin {next(iter(shas), '(none)')}",
                value=next(iter(shas), None),
            )
        )
    else:
        detail = "; ".join(f"{name}={sha}" for name, sha in active)
        checks.append(
            Check(
                "candidate_consistency",
                INCONSISTENT,
                blocking=True,
                detail=f"active sources disagree: {detail}",
            )
        )
    # provenance recorded, never blocking
    for name, sha in provenance:
        checks.append(
            Check(f"provenance:{name}", OK, blocking=False, detail="provenance only (excluded from consistency)", value=sha)
        )
    return tuple(checks)


# --- orchestration ----------------------------------------------------------
def run_preflight(
    repo: str,
    *,
    refs: dict | None = None,               # label -> sha, all blocking commit objects
    required_files: dict | None = None,     # name -> path, blocking repo/policy files
    optional_inputs: dict | None = None,    # name -> {"path"|"value", "required_for": [...]}
    conflict_rate=...,                       # sentinel: only checked if provided
    active_sources=None,                     # list[(name, sha)]
    provenance=(),                           # list[(name, sha)]
    required_blobs=(),                       # list[(ref, path)]
) -> PreflightReport:
    """Batch every check and report ALL problems at once (설계 §7)."""
    checks: list[Check] = []

    for label, sha in (refs or {}).items():
        checks.append(check_commit_object(repo, label, sha))

    for ref, path in required_blobs:
        checks.append(check_blob_access(repo, ref, path))

    for name, path in (required_files or {}).items():
        checks.append(check_file_present(name, path, blocking=True))

    for name, spec in (optional_inputs or {}).items():
        required_for = spec.get("required_for", ())
        if "path" in spec:
            checks.append(check_file_present(name, spec["path"], blocking=False, required_for=required_for))
        elif "value" in spec:
            # generic optional value presence
            if spec["value"] is None:
                checks.append(Check(name, MISSING, blocking=False, required_for=tuple(required_for)))
            else:
                checks.append(Check(name, OK, blocking=False, value=str(spec["value"]), required_for=tuple(required_for)))

    if conflict_rate is not ...:
        checks.append(check_conflict_rate(conflict_rate))

    if active_sources is not None:
        checks.extend(check_active_source_consistency(active_sources, provenance))

    return PreflightReport(tuple(checks))
