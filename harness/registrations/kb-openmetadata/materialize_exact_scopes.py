#!/usr/bin/env python3
"""Materialize exact per-ID source scopes from the pinned snapshot inventory.

The source snapshot is already pinned by ``customization-registry.yaml`` and
``source-diff-paths.txt``.  Older manifests used glob patterns to assign those
paths to BANK-OM IDs.  This tool converts that one-time classification into
literal file lists and then verifies that the manifests stay exact.

It deliberately updates only source-snapshot IDs.  Candidate follow-up IDs
already have commit-derived literal scopes.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from acgh import layout
from acgh import vendor_rebuild


def _load_shared_owners(path: Path) -> dict[str, list[str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("shared-path-owners.yaml must be a mapping")
    return data


def _resolved_scopes(
    plan: vendor_rebuild.ReconstructionPlan,
    shared_owners: dict[str, list[str]],
) -> dict[str, tuple[str, ...]]:
    owners_by_path: dict[str, tuple[str, ...]] = {
        path: (customization_id,)
        for path, customization_id in plan.unique_assignments
    }
    candidates = dict(plan.shared_candidates)
    if set(shared_owners) != set(candidates):
        raise ValueError(
            "shared owner map does not match ambiguous source paths: "
            f"missing={sorted(set(candidates) - set(shared_owners))}, "
            f"extra={sorted(set(shared_owners) - set(candidates))}"
        )
    for path, candidate_ids in candidates.items():
        owners = tuple(sorted(set(shared_owners[path])))
        if not owners or not set(owners).issubset(candidate_ids):
            raise ValueError(
                f"invalid shared owners for {path}: owners={owners}, "
                f"candidates={candidate_ids}"
            )
        owners_by_path[path] = owners

    scopes: dict[str, list[str]] = {
        customization_id: [] for customization_id in plan.active_ids
    }
    for path, owners in owners_by_path.items():
        for customization_id in owners:
            scopes[customization_id].append(path)
    return {
        customization_id: tuple(sorted(paths))
        for customization_id, paths in scopes.items()
    }


def _write_manifests(
    root: Path,
    registry,
    scopes: dict[str, tuple[str, ...]],
) -> None:
    entries = {entry.customization_id: entry for entry in registry.entries}
    for customization_id, paths in scopes.items():
        manifest_path = root / entries[customization_id].manifest
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        data["implementation"]["allowed_changed_paths"] = list(paths)
        manifest_path.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def _prune_single_owner_lines(
    path: Path,
    shared_owners: dict[str, list[str]],
) -> None:
    single_owner_paths = {
        source_path
        for source_path, owners in shared_owners.items()
        if len(set(owners)) == 1
    }
    kept = []
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("#") or not line.strip():
            kept.append(line)
            continue
        source_path = line.split(":", 1)[0]
        if source_path not in single_owner_paths:
            kept.append(line)
    path.write_text("".join(kept), encoding="utf-8")


def _check_literal_exact(
    manifests: dict[str, dict],
    scopes: dict[str, tuple[str, ...]],
) -> list[str]:
    errors: list[str] = []
    for customization_id, expected in scopes.items():
        raw = manifests[customization_id]["implementation"][
            "allowed_changed_paths"
        ]
        actual: list[str] = []
        for entry in raw:
            try:
                actual.append(layout.ensure_literal(entry))
            except layout.LayoutError as exc:
                errors.append(f"{customization_id}: non-literal scope {entry!r}: {exc}")
        if tuple(sorted(actual)) != expected:
            errors.append(
                f"{customization_id}: exact scope mismatch "
                f"missing={sorted(set(expected) - set(actual))}, "
                f"extra={sorted(set(actual) - set(expected))}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="replace source-snapshot manifest globs with resolved literal paths",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    registry, manifests, inventory = vendor_rebuild.load_registration_bundle(root)
    plan = vendor_rebuild.build_reconstruction_plan(
        registry, manifests, inventory
    )
    owner_path = root / "shared-path-owners.yaml"
    shared_owners = _load_shared_owners(owner_path)
    scopes = _resolved_scopes(plan, shared_owners)

    if args.write:
        _write_manifests(root, registry, scopes)
        _prune_single_owner_lines(owner_path, shared_owners)
        registry, manifests, inventory = vendor_rebuild.load_registration_bundle(
            root
        )
        plan = vendor_rebuild.build_reconstruction_plan(
            registry, manifests, inventory
        )
        shared_owners = _load_shared_owners(owner_path)
        scopes = _resolved_scopes(plan, shared_owners)

    errors = _check_literal_exact(manifests, scopes)
    for customization_id, paths in scopes.items():
        print(f"{customization_id}: {len(paths)} exact source path(s)")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("exact source scopes: verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
