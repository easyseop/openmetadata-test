#!/usr/bin/env python3
"""Run one T61 deployed-counterfactual negative-control experiment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--customization-id", required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--deployment-evidence-digest", required=True)
    parser.add_argument("--target-environment", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", default="local-runtime-patch-kill")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    return parser.parse_args()


def _experiment(plan: dict, customization_id: str) -> dict:
    matches = [
        item
        for item in plan["experiments"]
        if item["customization_id"] == customization_id
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"runtime patch-kill experiment not found: {customization_id}"
        )
    return matches[0]


def _assert_clean(root: Path, gitprim) -> None:
    status = gitprim.git(
        str(root), "status", "--porcelain", "--untracked-files=all"
    )
    if status.strip():
        raise RuntimeError("governance worktree is not clean")


def main() -> int:
    args = parse_args()
    harness = args.harness.resolve(strict=True)
    root = harness.parent
    registration = args.registration.resolve(strict=True)
    repo = args.repo.resolve(strict=True)
    sys.path.insert(0, str(harness))

    from acgh import binding
    from acgh import contracts
    from acgh import gitprim
    from acgh import patchkill
    from acgh import pytest_runs
    from acgh import result_io
    from acgh import vendor_rebuild
    from acgh import verdict

    _assert_clean(root, gitprim)
    plan_path = registration / "runtime-patch-kill-plan.yaml"
    plan = patchkill.load_runtime_plan(plan_path)
    experiment = _experiment(plan, args.customization_id)
    source_plan = patchkill.load_plan(registration / "patch-kill-plan.yaml")
    runtime_ids = {
        item["customization_id"] for item in plan["experiments"]
    }
    pending_ids = {
        item["customization_id"] for item in source_plan["pending"]
    }
    if runtime_ids != pending_ids:
        raise RuntimeError(
            "runtime experiments must exactly close source-plan pending IDs"
        )

    registry, manifests, inventory = vendor_rebuild.load_registration_bundle(
        registration
    )
    del inventory
    catalog_path = registration / "contracts.yaml"
    catalog = contracts.load_catalog(catalog_path)
    entry = registry.by_id().get(args.customization_id)
    if (
        entry is None
        or entry.status != "active"
        or entry.criticality not in {"high", "critical"}
    ):
        raise RuntimeError(
            f"{args.customization_id}: not an active high/critical customization"
        )
    required = contracts.effective_tests(
        manifests[args.customization_id], catalog
    )
    if experiment["required_test"] not in required:
        raise RuntimeError(
            f"{args.customization_id}: selector is not contract-bound"
        )

    candidate_sha = binding.pin(str(repo), "HEAD")
    if candidate_sha != plan["candidate"]["commit_sha"]:
        raise RuntimeError(
            "stale runtime patch-kill plan: candidate HEAD does not match"
        )
    without_sha = experiment["without_patch_sha"]
    if not gitprim.object_exists(str(repo), without_sha):
        raise RuntimeError("without-patch source commit is missing")
    if not gitprim.is_ancestor(str(repo), without_sha, candidate_sha):
        raise RuntimeError("without-patch source is not a candidate ancestor")
    commits = gitprim.commits(str(repo), without_sha, candidate_sha)
    if not any(
        args.customization_id in commit.customization_ids
        for commit in commits
    ):
        raise RuntimeError(
            "no matching customization commit follows the counterfactual"
        )

    governance_sha = binding.pin(str(root), "HEAD")
    tree_sha = gitprim.git(
        str(repo), "rev-parse", f"{without_sha}^{{tree}}"
    ).strip()
    selectors = [
        experiment["required_test"],
        *experiment["probes"],
    ]
    suite_digest = pytest_runs.suite_digest(
        root,
        selectors,
        metadata_paths=[plan_path, catalog_path],
    )
    inputs = patchkill.runtime_result_inputs(
        plan,
        experiment,
        candidate_sha=candidate_sha,
        counterfactual_tree_sha=tree_sha,
        governance_sha=governance_sha,
        counterfactual_artifact_digest=args.artifact_digest,
        deployment_evidence_digest=args.deployment_evidence_digest,
        target_environment=args.target_environment,
        suite_digest=suite_digest,
    )
    gates = patchkill.runtime_patch_kill(
        root,
        customization_id=args.customization_id,
        required_test=experiment["required_test"],
        probes=experiment["probes"],
        target_repeats=experiment["target_repeats"],
        timeout_seconds=args.timeout_seconds,
    )
    result = verdict.build_result(
        list(gates),
        inputs,
        governance_sha,
        run_id=args.run_id,
        observational={
            "probe_phases": 2,
            "target_executions": experiment["target_repeats"],
        },
    )
    result_io.write_result(result, args.output)
    summary = {
        "customization_id": args.customization_id,
        "counterfactual_source_sha": without_sha,
        "governance_sha": governance_sha,
        "result_digest": result["result_digest"],
        "suite_digest": suite_digest,
        "verdict": result["canonical_payload"]["verdict"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return result["expected_exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
