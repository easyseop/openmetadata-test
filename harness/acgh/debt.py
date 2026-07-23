"""T43 — customization debt gate (SRS §부채).

Core modifications tend to accumulate; past some point the fork is no longer
upgradable. This gate measures debt and forces conscious acceptance before it
compounds silently:

- a metric over its SOFT threshold -> approval (someone must accept the debt,
  e.g. via an ADR),
- over its HARD threshold -> block (stop and reduce before the next upgrade),
- within budget -> pass.

Metrics are quantitative signals only (computed upstream); this gate never
judges an individual patch's correctness.
"""
from __future__ import annotations

from acgh import verdict

# metric -> {soft, hard}. Tunable per team; these are conservative defaults.
DEFAULT_THRESHOLDS = {
    "core_patch_count": {"soft": 20, "hard": 40},
    "changed_lines": {"soft": 2000, "hard": 5000},
    "conflict_rate": {"soft": 0.15, "hard": 0.35},   # fraction of reapplies that conflict
    "hotspot_overlap": {"soft": 3, "hard": 6},        # patches touching one hot file
}


def evaluate_debt(metrics: dict, thresholds=DEFAULT_THRESHOLDS,
                  name: str = "debt") -> verdict.GateResult:
    hard: list[str] = []
    soft: list[str] = []
    for metric, value in metrics.items():
        th = thresholds.get(metric)
        if th is None:
            continue  # unknown metric — not this gate's concern
        if value > th["hard"]:
            hard.append(f"{metric}={value} > hard {th['hard']}")
        elif value > th["soft"]:
            soft.append(f"{metric}={value} > soft {th['soft']}")
    if hard:
        return verdict.GateResult(name, verdict.BLOCK, tuple(hard + soft))
    if soft:
        return verdict.GateResult(name, verdict.APPROVAL, tuple(soft))
    return verdict.GateResult(name, verdict.PASS, ("within debt budget",))
