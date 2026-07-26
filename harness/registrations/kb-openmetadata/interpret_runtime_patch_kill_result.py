#!/usr/bin/env python3
"""Fail-closed CI adapter for T61 runtime patch-kill evidence."""

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
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--actual-exit", type=int, required=True)
    return parser.parse_args()


def _experiment(plan: dict, customization_id: str) -> dict:
    return next(
        item
        for item in plan["experiments"]
        if item["customization_id"] == customization_id
    )


def main() -> int:
    args = parse_args()
    harness = args.harness.resolve(strict=True)
    root = harness.parent
    registration = args.registration.resolve(strict=True)
    repo = args.repo.resolve(strict=True)
    sys.path.insert(0, str(harness))

    from acgh import binding
    from acgh import gitprim
    from acgh import patchkill
    from acgh import pytest_runs
    from acgh import result_io
    from acgh import verdict

    try:
        plan_path = registration / "runtime-patch-kill-plan.yaml"
        catalog_path = registration / "contracts.yaml"
        plan = patchkill.load_runtime_plan(plan_path)
        experiment = _experiment(plan, args.customization_id)
        candidate_sha = binding.pin(str(repo), "HEAD")
        governance_sha = binding.pin(str(root), "HEAD")
        tree_sha = gitprim.git(
            str(repo),
            "rev-parse",
            f"{experiment['without_patch_sha']}^{{tree}}",
        ).strip()
        suite_digest = pytest_runs.suite_digest(
            root,
            [experiment["required_test"], *experiment["probes"]],
            metadata_paths=[plan_path, catalog_path],
        )
        expected_inputs = patchkill.runtime_result_inputs(
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
    except Exception as exc:
        payload = {
            "verdict": verdict.ANALYSIS_ERROR,
            "exit_code": verdict.to_exit_code(verdict.ANALYSIS_ERROR),
            "reason": f"cannot reconstruct runtime patch-kill inputs: {exc}",
            "synthetic": True,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return payload["exit_code"]

    decision = result_io.interpret_result(
        args.result,
        actual_exit=args.actual_exit,
        expected_inputs=expected_inputs,
        harness_version=governance_sha,
    )
    print(
        json.dumps(
            {
                "verdict": decision.verdict,
                "exit_code": decision.exit_code,
                "reason": decision.reason,
                "synthetic": decision.synthetic,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return decision.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
