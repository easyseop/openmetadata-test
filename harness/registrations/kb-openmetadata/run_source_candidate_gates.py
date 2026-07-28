#!/usr/bin/env python3
"""Run source-candidate gates for the rebuilt vendor branch.

The source artifact digest binds the candidate Git tree identity.  Release
image/package digests remain a later build-and-promotion concern.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--sensitive-zones", type=Path, required=True)
    return parser.parse_args()


def gate_json(result) -> dict:
    return {
        "name": result.name,
        "verdict": result.verdict,
        "reasons": list(result.reasons),
    }


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(args.harness))

    from acgh import ancestry
    from acgh import candidate
    from acgh import contracts
    from acgh import drift
    from acgh import gitprim
    from acgh import invariants
    from acgh import layout
    from acgh import policy_drift
    from acgh import survival
    from acgh import vendor_rebuild
    from acgh import zones

    registry, manifests, inventory = vendor_rebuild.load_registration_bundle(
        args.registration
    )
    del inventory
    head = gitprim.git(args.repo, "rev-parse", "HEAD").strip()
    tree = gitprim.git(args.repo, "rev-parse", "HEAD^{tree}").strip()
    target = registry.source["upstream_sha"]
    source_identity = f"git-tree:{tree}".encode()
    source_digest = "sha256:" + hashlib.sha256(source_identity).hexdigest()
    lock = candidate.build_candidate_lock(
        args.repo,
        head,
        upstream_repository=registry.source["upstream_repository"],
        upstream_base_sha=target,
        upstream_target_sha=target,
        candidate_repository="easyseop/OpenMetadata",
        artifact_digest=source_digest,
        upstream_base_tag=registry.source["upstream_tag"],
        upstream_target_tag=registry.source["upstream_tag"],
    )

    t25 = ancestry.check_vendor_ancestry(args.repo, lock)
    catalog = contracts.load_catalog(args.registration / "contracts.yaml")
    t26 = survival.check_customization_survival(
        args.repo,
        lock,
        manifests,
        catalog,
        active_ids=registry.active_ids(),
    )
    t60_i = contracts.check_required_test_implementations(
        args.registration.parents[2],
        catalog,
    )
    repository_layout = layout.load_layout(args.layout)
    t30_violations = invariants.check_commit_invariants(
        args.repo, target, head, repository_layout
    )
    t30 = invariants.to_gate_result("commit-invariants", t30_violations)
    commits = gitprim.commits(args.repo, target, head)
    t31_violations = invariants.check_id_invariants(commits, manifests)
    t31 = invariants.to_gate_result("id-invariants", t31_violations)
    t40_violations = drift.check_drift(
        args.repo, target, head, manifests, repository_layout
    )
    t40 = drift.to_gate_result(t40_violations)
    current_scope = sorted({
        path
        for customization_id in registry.active_ids()
        for path in [
            *manifests[customization_id]["implementation"].get(
                "allowed_changed_paths", []
            ),
            *manifests[customization_id]["implementation"].get(
                "candidate_additional_paths", []
            ),
        ]
    })
    t41 = zones.check_sensitive_zones(
        gitprim.net_changed_paths(args.repo, target, head),
        zones.load_zones(args.sensitive_zones),
        {"allowed": current_scope, "forbidden": []},
    )
    t93 = policy_drift.check_exact_scope_history(
        args.repo, target, head, manifests
    )
    gates = [t25, t26, t60_i, t30, t31, t40, t41, t93]
    output = {
        "candidate_lock": lock.canonical(),
        "candidate_lock_digest": lock.digest(),
        "artifact_note": (
            "artifact_digest binds the source Git tree identity; binary/image "
            "release artifacts are not built yet"
        ),
        "gates": [gate_json(result) for result in gates],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all(result.verdict == "pass" for result in gates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
