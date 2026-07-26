#!/usr/bin/env python3
"""Run T61 source-capable negative controls for the locked vendor candidate."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", default="local-source-patch-kill")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    harness = args.harness.resolve()
    root = harness.parent
    registration = args.registration.resolve()
    repo = args.repo.resolve()
    sys.path.insert(0, str(harness))

    from acgh import contracts
    from acgh import gitprim
    from acgh import patchkill
    from acgh import result_io
    from acgh import vendor_rebuild
    from acgh import verdict

    plan_path = registration / "patch-kill-plan.yaml"
    plan = patchkill.load_plan(plan_path)
    registry, manifests, inventory = vendor_rebuild.load_registration_bundle(
        registration
    )
    del inventory
    catalog = contracts.load_catalog(registration / "contracts.yaml")

    candidate_sha = gitprim.git(str(repo), "rev-parse", "HEAD").strip()
    if candidate_sha != plan["candidate"]["commit_sha"]:
        raise RuntimeError(
            "stale patch-kill plan: candidate HEAD does not match plan"
        )
    governance_sha = gitprim.git(str(root), "rev-parse", "HEAD").strip()
    by_id = registry.by_id()
    high_ids = {
        entry.customization_id
        for entry in registry.entries
        if entry.status == "active"
        and entry.criticality in {"high", "critical"}
    }
    covered_ids = {
        item["customization_id"]
        for item in [*plan["experiments"], *plan["pending"]]
    }
    if covered_ids != high_ids:
        raise RuntimeError(
            "patch-kill plan must classify every active high/critical ID"
        )

    gates = []
    experiment_inputs = []
    with tempfile.TemporaryDirectory(prefix="acgh-t61-worktrees-") as temp:
        for index, experiment in enumerate(plan["experiments"], start=1):
            customization_id = experiment["customization_id"]
            entry = by_id[customization_id]
            if entry.criticality not in {"high", "critical"}:
                raise RuntimeError(
                    f"{customization_id}: source patch-kill is not high/critical"
                )
            required = contracts.effective_tests(
                manifests[customization_id], catalog
            )
            selector = experiment["required_test"]
            if selector not in required:
                raise RuntimeError(
                    f"{customization_id}: patch-kill selector is not contract-bound"
                )
            without_sha = experiment["without_patch_sha"]
            if not gitprim.object_exists(str(repo), without_sha):
                raise RuntimeError(
                    f"{customization_id}: without-patch commit is missing"
                )
            if not gitprim.is_ancestor(str(repo), without_sha, candidate_sha):
                raise RuntimeError(
                    f"{customization_id}: without-patch commit is not an ancestor"
                )
            commits = gitprim.commits(str(repo), without_sha, candidate_sha)
            if not any(
                customization_id in commit.customization_ids
                for commit in commits
            ):
                raise RuntimeError(
                    f"{customization_id}: no matching patch follows negative control"
                )
            result = patchkill.patch_kill_pytest(
                str(repo),
                without_sha,
                root,
                selector,
                str(Path(temp) / f"experiment-{index}"),
                timeout=args.timeout_seconds,
            )
            gates.append(
                result.to_gate_result(
                    f"source-patch-kill:{customization_id}"
                )
            )
            experiment_inputs.append(
                {
                    "customization_id": customization_id,
                    "without_patch_sha": without_sha,
                    "required_test": selector,
                    "method": experiment["method"],
                }
            )

    pending_ids = sorted(item["customization_id"] for item in plan["pending"])
    inputs = {
        "scope": plan["scope"],
        "repositories": {
            "candidate": {
                "repository": plan["candidate"]["repository"],
                "sha": candidate_sha,
            },
            "governance": {"repository": "easyseop/openmetadata-test", "sha": governance_sha},
        },
        "patch_kill_plan_digest": patchkill.plan_digest(plan),
        "experiments": experiment_inputs,
        "pending_high_critical_ids": pending_ids,
    }
    result = verdict.build_result(
        gates,
        inputs,
        governance_sha,
        run_id=args.run_id,
        observational={
            "source_experiments": len(experiment_inputs),
            "pending_runtime_experiments": len(pending_ids),
        },
    )
    result_io.write_result(result, args.output)
    summary = {
        "scope": plan["scope"],
        "candidate_sha": candidate_sha,
        "governance_sha": governance_sha,
        "verdict": result["canonical_payload"]["verdict"],
        "result_digest": result["result_digest"],
        "source_experiments": len(experiment_inputs),
        "pending_runtime_experiments": pending_ids,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return result["expected_exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
