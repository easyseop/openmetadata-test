"""T93 — upgrade_watch (SRS case D, REQ-GZ / 부칙 A-3.6).

Case D is the dangerous quiet one: the upstream upgrade produces NO textual
conflict in our patches, yet a file/symbol/config we DEPEND on changed
underneath us. Registration and reapply both pass; the customization silently
rots.

This gate flags it. Each manifest declares ``upgrade_watch.paths`` — the
upstream files its customization leans on. We intersect those globs with the
NET diff of the actual upstream upgrade (UPSTREAM_A -> UPSTREAM_B). Any hit ->
approval: no automatic block (the change may be benign), but a human/LLM must
review before promotion. That review is where the Impact-Memo (T42/§7, advisory
only) attaches.

Glob grammar is the shared T05 grammar (layout.make_spec).
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh import gitprim
from acgh import layout as L
from acgh import verdict


@dataclass(frozen=True)
class WatchFinding:
    customization_id: str
    changed_watch_paths: tuple[str, ...]


def evaluate_upgrade_watch(repo, base_ref, head_ref, manifests_by_id) -> list[WatchFinding]:
    """Return one finding per customization whose watched paths changed A->B."""
    net = {L.normalize_path(p)
           for p in gitprim.net_changed_paths(repo, base_ref, head_ref)}
    findings: list[WatchFinding] = []
    for cid in sorted(manifests_by_id):
        paths = manifests_by_id[cid].get("upgrade_watch", {}).get("paths", [])
        if not paths:
            continue
        spec = L.make_spec(paths)
        hits = tuple(sorted(p for p in net if spec.match_file(p)))
        if hits:
            findings.append(WatchFinding(cid, hits))
    return findings


def to_gate_result(findings: list[WatchFinding],
                   name: str = "upgrade-watch") -> verdict.GateResult:
    if not findings:
        return verdict.GateResult(name, verdict.PASS, ())
    reasons = tuple(
        f"{f.customization_id}: upstream A->B changed {len(f.changed_watch_paths)} "
        f"watched path(s), e.g. {f.changed_watch_paths[0]}"
        for f in findings
    )
    return verdict.GateResult(name, verdict.APPROVAL, reasons)
