"""T71 — deterministic gate routing by change type.

Fast lanes reduce operational cost without turning into bypasses.  Every lane
has an explicit, reviewable minimum gate set; mixed changes receive the union
of their lanes, and a core patch expands to the complete integration-strategy
plan from T28.
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh import routing
from acgh import verdict

LANES = {
    "config": (
        "manifest-validation",
        "configuration-render",
        "declarative-verifiers",
        "smoke-tests",
        "test-candidate-binding",
        "verdict-integrity",
    ),
    "deployment": (
        "manifest-validation",
        "deployment-render",
        "declarative-verifiers",
        "smoke-tests",
        "test-candidate-binding",
        "verdict-integrity",
    ),
    "extension": (
        "manifest-validation",
        "extension-inclusion",
        "sdk-contract",
        "import-test",
        "integration-test",
        "test-candidate-binding",
        "verdict-integrity",
    ),
    "governance": (
        "policy-base-evaluation",
        "policy-simulation",
        "two-person-approval",
        "verdict-integrity",
    ),
}
CHANGE_TYPES = tuple(LANES) + ("core-patch",)


@dataclass(frozen=True)
class FastLanePlan:
    change_types: tuple[str, ...]
    required_gates: tuple[str, ...]


def _normalize(change_types) -> tuple[str, ...]:
    if isinstance(change_types, str):
        values = (change_types,)
    else:
        values = tuple(change_types)
    if not values:
        raise ValueError("at least one change type is required")
    unknown = sorted(set(values) - set(CHANGE_TYPES))
    if unknown:
        raise ValueError(f"unsupported change type(s): {unknown}")
    return tuple(sorted(set(values)))


def build_fast_lane(change_types, *, candidate_lock=None) -> FastLanePlan:
    """Build the minimum required gate union for one or more change types."""
    types = _normalize(change_types)
    required: list[str] = []

    def add(gates):
        for gate in gates:
            if gate not in required:
                required.append(gate)

    for change_type in types:
        if change_type == "core-patch":
            if candidate_lock is None:
                raise ValueError("core-patch fast lane requires candidate_lock")
            add(routing.build_gate_plan(candidate_lock).required_gates)
        else:
            add(LANES[change_type])
    return FastLanePlan(types, tuple(required))


def check_fast_lane(
    change_types,
    available_gates,
    *,
    candidate_lock=None,
    name: str = "fast-lane-routing",
) -> verdict.GateResult:
    """Fail closed if a configured lane omits any of its declared gates."""
    try:
        plan = build_fast_lane(change_types, candidate_lock=candidate_lock)
    except (ValueError, TypeError) as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"analysis_error: {exc}",)
        )
    available = set(available_gates)
    missing = [
        gate for gate in plan.required_gates if gate not in available
    ]
    if missing:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"required lane gate unavailable: {gate}" for gate in missing),
        )
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            "change_types=" + ",".join(plan.change_types),
            "required_gates=" + ",".join(plan.required_gates),
        ),
    )
