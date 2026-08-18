"""T13 — verdict engine.

Implements the 4-state verdict contract (SRS §1.4, REQ-OR-01/02, 부칙 A-1).

Design invariants (do not "simplify" away — they encode P0-3/P0-4):
- Aggregation is by SEVERITY_RANK.max(), never by exit-code max().
  With exit codes, approval(2) > block(1) would wrongly downgrade block. (P0-3)
- analysis_error is "verification did not happen" -> treated as block, never
  approvable. Empty gate set -> analysis_error (fail-closed). (P0-4)
- Exit-code order intentionally differs from severity rank.
- The result digest covers only the canonical payload; observational metadata
  (timestamps, runner id, duration) is excluded so re-runs are comparable. (부칙 A-1.3)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Iterable

# --- 4-state verdict -------------------------------------------------------
PASS = "pass"
APPROVAL = "approval"
BLOCK = "block"
ANALYSIS_ERROR = "analysis_error"

VERDICTS = (PASS, APPROVAL, BLOCK, ANALYSIS_ERROR)

# Aggregation MUST use this rank (P0-3). Higher = more severe.
SEVERITY_RANK = {PASS: 0, APPROVAL: 1, BLOCK: 2, ANALYSIS_ERROR: 3}

# Exit codes. NOTE: order deliberately differs from SEVERITY_RANK (P0-3).
EXIT_CODE = {PASS: 0, BLOCK: 1, APPROVAL: 2, ANALYSIS_ERROR: 3}


class InvalidVerdict(ValueError):
    """Raised when a verdict string is not one of VERDICTS."""


def _check(v: str) -> str:
    if v not in SEVERITY_RANK:
        raise InvalidVerdict(f"unknown verdict: {v!r} (expected one of {VERDICTS})")
    return v


def aggregate(verdicts: Iterable[str]) -> str:
    """Aggregate gate verdicts by severity rank.

    Empty input -> analysis_error: nothing was actually judged, so we must not
    report pass (fail-closed, P0-4).
    """
    vs = [_check(v) for v in verdicts]
    if not vs:
        return ANALYSIS_ERROR
    return max(vs, key=SEVERITY_RANK.__getitem__)


def to_exit_code(verdict: str) -> int:
    return EXIT_CODE[_check(verdict)]


def canonical_digest(payload: dict) -> str:
    """Deterministic digest of a payload via canonical JSON (sorted, compact)."""
    blob = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


# --- structured result -----------------------------------------------------
@dataclass(frozen=True)
class GateResult:
    name: str
    verdict: str
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _check(self.verdict)


def build_result(
    gates: list[GateResult],
    inputs: dict,
    harness_version: str,
    *,
    run_id: str,
    observational: dict | None = None,
) -> dict:
    """Build an acgh-result payload.

    inputs should be repository-qualified (부칙 A-1.5), e.g.::
        {"repositories": {"upstream": {"sha": ...}, "core": {...}, ...},
         "patch_source_lock_digest": "sha256:...",
         "verifier_catalog_digest": "sha256:..."}

    The canonical_payload is the only thing hashed into result_digest;
    observational_metadata is excluded (부칙 A-1.3).
    """
    verdict = aggregate([g.verdict for g in gates])
    canonical_payload = {
        "verdict": verdict,
        "gates": [
            {"name": g.name, "verdict": g.verdict, "reasons": list(g.reasons)}
            for g in gates
        ],
        "inputs": inputs,
        "harness_version": harness_version,
    }
    result = {
        "schema_version": 1,
        "canonical_payload": canonical_payload,
        "observational_metadata": {"run_id": run_id, **(observational or {})},
        "result_digest": canonical_digest(canonical_payload),
        "expected_exit_code": to_exit_code(verdict),
    }
    return result
