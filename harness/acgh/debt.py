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

from pathlib import Path

import yaml

from acgh import gitprim
from acgh import layout as L
from acgh import verdict

# metric -> {soft, hard}. Tunable per team; these are conservative defaults.
DEFAULT_THRESHOLDS = {
    "core_patch_count": {"soft": 20, "hard": 40},
    "changed_lines": {"soft": 2000, "hard": 5000},
    "conflict_rate": {"soft": 0.15, "hard": 0.35},   # fraction of reapplies that conflict
    "hotspot_overlap": {"soft": 3, "hard": 6},        # patches touching one hot file
}


class DebtPolicyError(ValueError):
    """Debt threshold policy or measured input is not trustworthy."""


def _validate_thresholds(thresholds: dict) -> dict:
    if not isinstance(thresholds, dict) or not thresholds:
        raise DebtPolicyError("debt thresholds must be a non-empty mapping")
    normalized = {}
    for metric, raw in thresholds.items():
        if metric not in DEFAULT_THRESHOLDS:
            raise DebtPolicyError(f"unknown debt threshold metric: {metric}")
        if not isinstance(raw, dict) or set(raw) != {"soft", "hard"}:
            raise DebtPolicyError(
                f"{metric} threshold must contain exactly soft and hard"
            )
        soft, hard = raw["soft"], raw["hard"]
        if not isinstance(soft, (int, float)) or not isinstance(hard, (int, float)):
            raise DebtPolicyError(f"{metric} thresholds must be numeric")
        if soft < 0 or hard <= soft:
            raise DebtPolicyError(
                f"{metric} requires 0 <= soft < hard"
            )
        normalized[metric] = {"soft": soft, "hard": hard}
    return normalized


def load_thresholds(path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise DebtPolicyError("debt policy schema_version must be 1")
    return _validate_thresholds(data.get("thresholds"))


def collect_metrics(
    repo: str,
    base_ref: str,
    head_ref: str,
    manifests_by_id: dict[str, dict],
    *,
    conflict_rate: float,
) -> dict:
    """Measure deterministic debt inputs from the candidate and manifests."""
    if not isinstance(conflict_rate, (int, float)) or not 0 <= conflict_rate <= 1:
        raise DebtPolicyError("conflict_rate must be between 0 and 1")
    numstat = gitprim.git(repo, "diff", "--numstat", base_ref, head_ref)
    changed_lines = 0
    for line in numstat.splitlines():
        added, deleted, _path = line.split("\t", 2)
        if added == "-" or deleted == "-":
            continue  # binary file: no line metric
        changed_lines += int(added) + int(deleted)

    active_core = {
        customization_id: manifest
        for customization_id, manifest in manifests_by_id.items()
        if manifest.get("status", "active") == "active"
        and manifest.get("kind") == "core-patch"
    }
    owners: dict[str, set[str]] = {}
    for customization_id, manifest in active_core.items():
        implementation = manifest.get("implementation", {})
        for raw in [
            *implementation.get("allowed_changed_paths", []),
            *implementation.get("candidate_additional_paths", []),
        ]:
            path = L.ensure_literal(raw)
            owners.setdefault(path, set()).add(customization_id)
    return {
        "core_patch_count": len(active_core),
        "changed_lines": changed_lines,
        "conflict_rate": float(conflict_rate),
        "hotspot_overlap": max((len(ids) for ids in owners.values()), default=0),
    }


def evaluate_debt(metrics: dict, thresholds=DEFAULT_THRESHOLDS,
                  name: str = "debt") -> verdict.GateResult:
    try:
        checked_thresholds = _validate_thresholds(thresholds)
    except DebtPolicyError as exc:
        return verdict.GateResult(name, verdict.ANALYSIS_ERROR, (str(exc),))
    unknown = sorted(set(metrics) - set(checked_thresholds))
    if unknown:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (f"unknown debt metrics: {unknown}",),
        )
    hard: list[str] = []
    soft: list[str] = []
    for metric, value in metrics.items():
        if not isinstance(value, (int, float)):
            return verdict.GateResult(
                name, verdict.ANALYSIS_ERROR,
                (f"{metric} value must be numeric",),
            )
        th = checked_thresholds[metric]
        if value > th["hard"]:
            hard.append(f"{metric}={value} > hard {th['hard']}")
        elif value > th["soft"]:
            soft.append(f"{metric}={value} > soft {th['soft']}")
    if hard:
        return verdict.GateResult(name, verdict.BLOCK, tuple(hard + soft))
    if soft:
        return verdict.GateResult(name, verdict.APPROVAL, tuple(soft))
    return verdict.GateResult(name, verdict.PASS, ("within debt budget",))
