"""T42 — impact analysis for case D (SRS §7, 부칙 A-3.6).

T93 says WHICH customizations are affected by an upstream upgrade. T42 turns
each raw watch-hit into a review surface: the changed watched paths plus the
manifest's declared dependency / configuration / contract context, so a reviewer
sees not just "something changed" but "what our customization leaned on".

Crucially, T42 has NO verdict authority. It emits advisory Impact-Memos in the
evidence card's ``llm_suggestions`` shape (which the schema forbids from
carrying a verdict, §7). The gate verdict stays whatever T93 produced
(approval); the memo can inform the human review, never decide it.
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh.upgrade_watch import WatchFinding


@dataclass(frozen=True)
class ImpactItem:
    customization_id: str
    changed_watch_paths: tuple[str, ...]
    configuration_keys: tuple[str, ...]
    dependencies: tuple[str, ...]
    contracts: tuple[str, ...]


def build_impact_surface(findings, manifests_by_id) -> list[ImpactItem]:
    """Map each T93 finding to its full declared review context."""
    items: list[ImpactItem] = []
    for f in findings:
        m = manifests_by_id.get(f.customization_id, {})
        watch = m.get("upgrade_watch", {})
        assurance = m.get("assurance", {})
        items.append(ImpactItem(
            customization_id=f.customization_id,
            changed_watch_paths=tuple(f.changed_watch_paths),
            configuration_keys=tuple(watch.get("configuration_keys", [])),
            dependencies=tuple(watch.get("dependencies", [])),
            contracts=tuple(assurance.get("contracts", [])),
        ))
    return items


def to_llm_suggestions(items: list[ImpactItem], gate: str = "upgrade-watch") -> list[dict]:
    """Advisory Impact-Memos for the evidence card. No verdict field (§7)."""
    out: list[dict] = []
    for it in items:
        ctx = []
        if it.dependencies:
            ctx.append(f"deps={list(it.dependencies)}")
        if it.configuration_keys:
            ctx.append(f"config={list(it.configuration_keys)}")
        if it.contracts:
            ctx.append(f"contracts={list(it.contracts)}")
        memo = (
            f"upstream A->B changed {len(it.changed_watch_paths)} watched "
            f"path(s) for {it.customization_id} (e.g. {it.changed_watch_paths[0]}). "
            f"Review whether the depended-on behavior still holds"
            + (f"; {'; '.join(ctx)}" if ctx else "")
            + "."
        )
        out.append({"gate": gate, "memo": memo, "severity_hint": "medium"})
    return out


def review_packet(items: list[ImpactItem]) -> dict:
    """A compact machine-readable summary of the impact surface."""
    return {
        "impacted_count": len(items),
        "impacted": [
            {
                "customization_id": it.customization_id,
                "changed_watch_paths": list(it.changed_watch_paths),
                "configuration_keys": list(it.configuration_keys),
                "dependencies": list(it.dependencies),
                "contracts": list(it.contracts),
            }
            for it in items
        ],
    }
