"""T28 — explicit integration-strategy gate routing.

The common candidate/content gates run for every strategy. Git integration
mechanics are mode-specific:

* vendor-merge: ancestry, customization survival, conflict evidence;
* patch-replay: patch lock, reapply, clean-room replay, integrator CAS.

Keeping this plan deterministic prevents the historical failure mode where a
normal vendor candidate was blocked only because it had no patch lock, or where
cherry-pick success was mistaken for a complete vendor release verdict.
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh import candidate as C
from acgh import verdict

COMMON_GATES = (
    "candidate-lock",
    "registration-invariants",
    "drift",
    "sensitive-zones",
    "policy-drift",
    "upgrade-watch",
    "declarative-verifiers",
    "contract-binding",
    "test-candidate-binding",
    "verdict-integrity",
)

VENDOR_MERGE_GATES = (
    "vendor-ancestry",
    "customization-survival",
    "merge-conflict-evidence",
)

PATCH_REPLAY_GATES = (
    "patch-lock",
    "reapply-detect",
    "clean-room-replay",
    "single-integrator-cas",
)


@dataclass(frozen=True)
class GatePlan:
    strategy: str
    common_gates: tuple[str, ...]
    mode_gates: tuple[str, ...]

    @property
    def required_gates(self) -> tuple[str, ...]:
        return self.common_gates + self.mode_gates


def build_gate_plan(lock: C.CandidateLock) -> GatePlan:
    if lock.integration_strategy == C.VENDOR_MERGE:
        mode = VENDOR_MERGE_GATES
    elif lock.integration_strategy == C.PATCH_REPLAY:
        mode = PATCH_REPLAY_GATES
    else:
        raise ValueError(
            f"unsupported integration strategy: {lock.integration_strategy!r}"
        )
    return GatePlan(lock.integration_strategy, COMMON_GATES, mode)


def check_gate_routing(
    lock: C.CandidateLock,
    available_gates,
    *,
    name: str = "integration-strategy-routing",
) -> verdict.GateResult:
    """Fail closed when the configured runner omits a required mode gate."""
    try:
        plan = build_gate_plan(lock)
    except ValueError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"analysis_error: {exc}",)
        )
    available = set(available_gates)
    missing = [gate for gate in plan.required_gates if gate not in available]
    if missing:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"required gate unavailable: {gate}" for gate in missing),
        )
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"strategy={plan.strategy}",
            "mode_gates=" + ",".join(plan.mode_gates),
        ),
    )
