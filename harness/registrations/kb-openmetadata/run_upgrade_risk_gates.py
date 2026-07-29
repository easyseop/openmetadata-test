#!/usr/bin/env python3
"""Run second-stage upgrade risk gates and emit one review packet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath

import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--sensitive-zones", type=Path, required=True)
    parser.add_argument("--debt-policy", type=Path, required=True)
    parser.add_argument("--change-intent", type=Path, required=True)
    parser.add_argument("--upstream-base", required=True)
    parser.add_argument("--upstream-target", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--conflict-rate", type=float, required=True)
    return parser.parse_args()


def _gate(result):
    return {
        "name": result.name,
        "verdict": result.verdict,
        "reasons": list(result.reasons),
    }


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(args.harness))
    from acgh import debt
    from acgh import gitprim
    from acgh import impact
    from acgh import layout
    from acgh import manifest as manifest_module
    from acgh import policy_drift
    from acgh import structdiff
    from acgh import upgrade_watch
    from acgh import vendor_rebuild
    from acgh import verdict
    from acgh import watch_suggest
    from acgh import zones

    registry, manifests, _inventory = vendor_rebuild.load_registration_bundle(
        args.registration
    )
    active = {
        customization_id: manifests[customization_id]
        for customization_id in registry.active_ids()
    }
    change_intent = yaml.safe_load(
        args.change_intent.read_text(encoding="utf-8")
    )
    if change_intent.get("allowed_from_active_manifests") is True:
        change_intent = {
            "allowed": manifest_module.declared_scope(
                manifests,
                registry.active_ids(),
            ),
            "forbidden": change_intent.get("forbidden", []),
        }
    findings = upgrade_watch.evaluate_upgrade_watch(
        args.repo, args.upstream_base, args.upstream_target, active
    )
    t42 = upgrade_watch.to_gate_result(findings)
    impact_items = impact.build_impact_surface(findings, active)
    suggestions = watch_suggest.suggest_watch_paths(
        args.repo,
        args.upstream_base,
        args.upstream_target,
        args.candidate,
        active,
    )
    candidate_changes = gitprim.net_changed_paths(
        args.repo, args.upstream_target, args.candidate
    )
    t41 = zones.check_sensitive_zones(
        candidate_changes,
        zones.load_zones(args.sensitive_zones),
        change_intent,
    )
    metrics = debt.collect_metrics(
        args.repo,
        args.upstream_target,
        args.candidate,
        active,
        conflict_rate=args.conflict_rate,
    )
    t43 = debt.evaluate_debt(
        metrics, debt.load_thresholds(args.debt_policy)
    )
    watch_patterns = sorted({
        pattern
        for manifest in active.values()
        for pattern in manifest.get("upgrade_watch", {}).get("paths", [])
    })
    t93_policy = policy_drift.check_policy_drift(
        args.repo,
        args.upstream_target,
        watch_patterns,
        layout.load_layout(args.layout),
        baseline_ref=args.upstream_base,
    )
    t93_scope = policy_drift.check_exact_scope_history(
        args.repo, args.upstream_target, args.candidate, active
    )

    structured = []
    for finding in findings:
        for path in finding.changed_watch_paths:
            if PurePosixPath(path).suffix.lower() not in {
                ".json", ".yaml", ".yml",
            }:
                continue
            try:
                diff = structdiff.diff_file(
                    args.repo, args.upstream_base, args.upstream_target, path
                )
                structured.append({
                    "customization_id": finding.customization_id,
                    "path": path,
                    "summary": diff.summary(),
                    "added": list(diff.added),
                    "removed": list(diff.removed),
                    "type_changed": list(diff.type_changed),
                    "scalar_changed": list(diff.scalar_changed),
                    "list_changed": list(diff.list_changed),
                })
            except Exception as exc:
                structured.append({
                    "customization_id": finding.customization_id,
                    "path": path,
                    "analysis_error": type(exc).__name__,
                })

    gates = [t42, t41, t43, t93_policy, t93_scope]
    output = {
        "upstream": {
            "base": args.upstream_base,
            "target": args.upstream_target,
        },
        "candidate": args.candidate,
        "gates": [_gate(result) for result in gates],
        "debt_metrics": metrics,
        "impact_review": impact.review_packet(impact_items),
        "watch_suggestions": watch_suggest.review_packet(suggestions),
        "structured_diffs": structured,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    states = {result.verdict for result in gates}
    if verdict.ANALYSIS_ERROR in states or verdict.BLOCK in states:
        return 1
    return 2 if verdict.APPROVAL in states else 0


if __name__ == "__main__":
    raise SystemExit(main())
