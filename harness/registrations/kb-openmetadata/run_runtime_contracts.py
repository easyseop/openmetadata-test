#!/usr/bin/env python3
"""Execute all required bank contracts and emit candidate-bound T62 evidence."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--candidate-repository", default="easyseop/OpenMetadata"
    )
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument(
        "--run-id",
        default=os.environ.get("GITHUB_RUN_ID", f"local-{os.getpid()}"),
    )
    return parser.parse_args()


def _assert_clean(repo, *, label: str, gitprim) -> None:
    status = gitprim.git(
        repo, "status", "--porcelain", "--untracked-files=all"
    )
    if status.strip():
        raise RuntimeError(f"{label} worktree is not clean")


def _atomic_yaml(data: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp.{os.getpid()}")
    blob = yaml.safe_dump(data, sort_keys=True, allow_unicode=True)
    descriptor = os.open(
        str(temporary), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644
    )
    try:
        os.write(descriptor, blob.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(str(temporary), str(output))


def main() -> int:
    args = parse_args()
    harness = args.harness.resolve(strict=True)
    registration = args.registration.resolve(strict=True)
    root = registration.parents[2]
    repo = Path(args.repo).resolve(strict=True)
    sys.path.insert(0, str(harness))

    from acgh import binding
    from acgh import candidate
    from acgh import contracts
    from acgh import gitprim
    from acgh import pytest_runs
    from acgh import registry as registry_module
    from acgh import result_io
    from acgh import testruns
    from acgh import vendor_rebuild
    from acgh import verdict

    _assert_clean(root, label="governance", gitprim=gitprim)
    _assert_clean(repo, label="product", gitprim=gitprim)
    governance_sha = binding.pin(str(root), "HEAD")

    registry, manifests, inventory = vendor_rebuild.load_registration_bundle(
        registration
    )
    del inventory
    catalog_path = registration / "contracts.yaml"
    catalog = contracts.load_catalog(catalog_path)
    manifests_by_id = manifests
    registry_module.validate_references(registry, manifests_by_id, catalog)

    active_ids = set(registry.active_ids())
    active_manifests = [
        manifest
        for customization_id, manifest in manifests.items()
        if customization_id in active_ids
    ]
    selectors = sorted(
        {
            selector
            for manifest in active_manifests
            for selector in contracts.effective_tests(manifest, catalog)
        }
    )
    criticality_by_id = {
        entry.customization_id: entry.criticality
        for entry in registry.entries
        if entry.status == "active"
    }

    t60_i = contracts.check_required_test_implementations(root, catalog)
    if t60_i.verdict != verdict.PASS:
        raise RuntimeError(
            "required-test implementation gate is not pass: "
            + "; ".join(t60_i.reasons)
        )

    head = binding.pin(str(repo), "HEAD")
    target = registry.source["upstream_sha"]
    lock = candidate.build_candidate_lock(
        str(repo),
        head,
        upstream_repository=registry.source["upstream_repository"],
        upstream_base_sha=target,
        upstream_target_sha=target,
        candidate_repository=args.candidate_repository,
        artifact_digest=args.artifact_digest,
        upstream_base_tag=registry.source["upstream_tag"],
        upstream_target_tag=registry.source["upstream_tag"],
    )
    candidate.assert_candidate_binding(
        str(repo), lock, artifact_digest=args.artifact_digest
    )

    metadata_paths = [
        registration / "customization-registry.yaml",
        catalog_path,
        *[
            registration / entry.manifest
            for entry in registry.entries
            if entry.status == "active"
        ],
    ]
    suite_version = pytest_runs.suite_digest(
        root, selectors, metadata_paths=metadata_paths
    )
    attempts = pytest_runs.run_required_tests(
        root,
        selectors,
        retries=args.retries,
        timeout_seconds=args.timeout_seconds,
        environment={"OPENMETADATA_PRODUCT_REPO": str(repo)},
    )
    run_set = testruns.TestRunSet(
        candidate_sha=lock.candidate.commit_sha,
        artifact_digest=lock.candidate.artifact_digest,
        harness_version=governance_sha,
        suite_version=suite_version,
        runs=attempts,
    )
    t62 = testruns.check_test_runs(
        active_manifests,
        catalog,
        run_set,
        lock,
        criticality_by_id=criticality_by_id,
        expected_harness_version=governance_sha,
        expected_suite_version=suite_version,
    )

    output_dir = args.output_dir.resolve()
    _atomic_yaml(lock.canonical(), output_dir / "candidate-lock.yaml")
    testruns.write_test_run_set(run_set, output_dir / "test-run-set.yaml")
    result = verdict.build_result(
        [t60_i, t62],
        lock.result_inputs(verifier_catalog_digest=suite_version),
        governance_sha,
        run_id=args.run_id,
        observational={"test_run_set_digest": run_set.digest()},
    )
    result_io.write_result(result, output_dir / "acgh-result.yaml")

    summary = {
        "candidate_sha": lock.candidate.commit_sha,
        "artifact_digest": lock.candidate.artifact_digest,
        "harness_version": governance_sha,
        "suite_version": suite_version,
        "test_run_set_digest": run_set.digest(),
        "verdict": result["canonical_payload"]["verdict"],
        "expected_exit_code": result["expected_exit_code"],
        "outcomes": {
            outcome: sum(1 for item in attempts if item.outcome == outcome)
            for outcome in ("pass", "fail", "error", "skipped")
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return result["expected_exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
