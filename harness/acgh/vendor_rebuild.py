"""T25-R — fail-closed reconstruction of an ancestry-less vendor snapshot.

T25 can prove that an already-built candidate contains an approved upstream
target.  It cannot safely turn a one-commit, unrelated source snapshot into
that candidate.  This module closes that gap without pretending that copying a
tree is enough:

* the pinned upstream and snapshot trees must reproduce the registered source
  inventory exactly;
* every product path is assigned to one manifest, or explicitly identified as
  a shared path requiring hunk-level ownership;
* unregistered findings are excluded from the reconstructed candidate;
* the candidate starts from the approved upstream target and must not merge the
  unrelated snapshot commit;
* every candidate commit has exactly one ``Customization-ID`` and may touch
  only paths assigned to that ID; and
* final JSON values equal the snapshot (formatting ignored), all other
  registered path bytes equal the snapshot, and excluded paths equal upstream.

The shared-path owner map is intentionally explicit.  Choosing the first
matching manifest would silently attribute QueryReport lines to InstanceCode
in files both features modify.  Missing or invalid ownership therefore fails
closed instead of producing an apparently clean vendor branch.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

from acgh import binding
from acgh import gitprim
from acgh import layout
from acgh import manifest as M
from acgh import registry as R
from acgh import verdict


class ReconstructionError(ValueError):
    """The registered source cannot produce a trustworthy reconstruction plan."""


@dataclass(frozen=True)
class ReconstructionPlan:
    upstream_sha: str
    snapshot_sha: str
    inventory_paths: tuple[str, ...]
    unique_assignments: tuple[tuple[str, str], ...]
    shared_candidates: tuple[tuple[str, tuple[str, ...]], ...]
    excluded_paths: tuple[str, ...]
    active_ids: tuple[str, ...]

    def canonical(self) -> dict:
        return {
            "schema_version": 1,
            "upstream_sha": self.upstream_sha,
            "snapshot_sha": self.snapshot_sha,
            "inventory_paths": list(self.inventory_paths),
            "unique_assignments": [
                {"path": path, "customization_id": customization_id}
                for path, customization_id in self.unique_assignments
            ],
            "shared_candidates": [
                {"path": path, "candidate_ids": list(candidate_ids)}
                for path, candidate_ids in self.shared_candidates
            ],
            "excluded_paths": list(self.excluded_paths),
            "active_ids": list(self.active_ids),
        }

    def digest(self) -> str:
        return verdict.canonical_digest(self.canonical())

    def assignment_candidates(self) -> dict[str, tuple[str, ...]]:
        result = {
            path: (customization_id,)
            for path, customization_id in self.unique_assignments
        }
        result.update(dict(self.shared_candidates))
        return result


def build_reconstruction_plan(
    registry: R.Registry,
    manifests_by_id: dict[str, dict],
    inventory_paths,
    source_path_owners: dict[str, tuple[str, ...]] | None = None,
) -> ReconstructionPlan:
    """Build a deterministic path plan from the registered snapshot inventory."""
    try:
        paths = tuple(sorted(layout.normalize_path(path) for path in inventory_paths))
    except layout.LayoutError as exc:
        raise ReconstructionError(f"invalid inventory path: {exc}") from exc

    if len(paths) != len(set(paths)):
        raise ReconstructionError("source diff inventory contains duplicate paths")
    expected_count = registry.source["changed_path_count"]
    if len(paths) != expected_count:
        raise ReconstructionError(
            f"source diff inventory count {len(paths)} != registered "
            f"changed_path_count {expected_count}"
        )

    active_ids = tuple(sorted(registry.source_snapshot_ids()))
    registered_ids = set(registry.by_id())
    missing = sorted(set(active_ids) - set(manifests_by_id))
    extra = sorted(set(manifests_by_id) - registered_ids)
    if missing or extra:
        raise ReconstructionError(
            f"active manifest set mismatch: missing={missing}, extra={extra}"
        )

    inventory_set = set(paths)
    if source_path_owners is not None:
        unknown_owner_paths = sorted(set(source_path_owners) - inventory_set)
        unknown_owner_ids = sorted(
            {
                owner
                for owners in source_path_owners.values()
                for owner in owners
                if owner not in active_ids
            }
        )
        if unknown_owner_paths or unknown_owner_ids:
            raise ReconstructionError(
                "source snapshot owner map mismatch: "
                f"paths_not_in_inventory={unknown_owner_paths}, "
                f"unknown_ids={unknown_owner_ids}"
            )
    exact_scopes: dict[str, frozenset[str]] = {}
    try:
        for customization_id in active_ids:
            manifest = manifests_by_id[customization_id]
            raw_scope = M.declared_changed_paths(manifest)
            literals = tuple(layout.ensure_literal(item) for item in raw_scope)
            if len(literals) != len(set(literals)):
                raise ReconstructionError(
                    f"{customization_id}: duplicate changed path"
                )
            # Schema v2 stores the current-version scope. A separately
            # generated source ownership map preserves which ID owned each
            # path at the pinned source snapshot without splitting the current
            # Manifest into first-commit and follow-up fields.
            source_literals = set(literals) & inventory_set
            if source_path_owners is not None:
                source_literals = {
                    path
                    for path, owners in source_path_owners.items()
                    if customization_id in owners
                }
                outside_current = sorted(source_literals - set(literals))
                if outside_current:
                    raise ReconstructionError(
                        f"{customization_id}: source ownership paths are absent "
                        f"from current changed_paths: {outside_current}"
                    )
            if manifest.get("schema_version", 1) == 1:
                legacy_source = manifest["implementation"].get(
                    "allowed_changed_paths", []
                )
                source_literals = {
                    layout.ensure_literal(item) for item in legacy_source
                }
                extra = sorted(source_literals - inventory_set)
                if extra:
                    raise ReconstructionError(
                        f"{customization_id}: legacy source paths are absent from "
                        f"the pinned source inventory: {extra}"
                    )
            exact_scopes[customization_id] = frozenset(source_literals)
    except (KeyError, TypeError, layout.LayoutError) as exc:
        raise ReconstructionError(
            "source-snapshot changed paths must be literal files: "
            f"{exc}"
        ) from exc

    try:
        findings = {
            layout.normalize_path(item["path"]): item
            for item in registry.source["unregistered_findings"]
        }
    except (KeyError, TypeError, layout.LayoutError) as exc:
        raise ReconstructionError(
            f"invalid unregistered finding path: {exc}"
        ) from exc
    unknown_findings = sorted(set(findings) - set(paths))
    if unknown_findings:
        raise ReconstructionError(
            f"unregistered findings absent from source inventory: {unknown_findings}"
        )

    unique: list[tuple[str, str]] = []
    shared: list[tuple[str, tuple[str, ...]]] = []
    excluded: list[str] = []
    represented_ids: set[str] = set()

    for path in paths:
        hits = tuple(
            customization_id
            for customization_id in active_ids
            if path in exact_scopes[customization_id]
        )
        if path in findings:
            if hits:
                raise ReconstructionError(
                    f"unregistered finding is also manifest-owned: {path} -> {hits}"
                )
            excluded.append(path)
            continue
        if not hits:
            raise ReconstructionError(
                f"source path is neither registered nor explicitly excluded: {path}"
            )
        represented_ids.update(hits)
        if len(hits) == 1:
            unique.append((path, hits[0]))
        else:
            shared.append((path, hits))

    missing_ids = sorted(set(active_ids) - represented_ids)
    if missing_ids:
        raise ReconstructionError(
            f"active customizations own no source path: {missing_ids}"
        )

    return ReconstructionPlan(
        upstream_sha=registry.source["upstream_sha"],
        snapshot_sha=registry.source["snapshot_sha"],
        inventory_paths=paths,
        unique_assignments=tuple(unique),
        shared_candidates=tuple(shared),
        excluded_paths=tuple(excluded),
        active_ids=active_ids,
    )


def load_source_snapshot_owners(
    registration_dir: str | Path,
) -> dict[str, tuple[str, ...]] | None:
    """Load generated ownership at the pinned source snapshot when present."""
    path = Path(registration_dir) / "source-snapshot-path-owners.yaml"
    if not path.exists():
        return None
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ReconstructionError(
                "source snapshot path owners must be a mapping"
            )
        result: dict[str, tuple[str, ...]] = {}
        for raw_path, raw_owners in raw.items():
            normalized = layout.normalize_path(raw_path)
            if normalized in result:
                raise ReconstructionError(
                    f"duplicate source snapshot path owner entry: {normalized}"
                )
            if not isinstance(raw_owners, list) or not raw_owners:
                raise ReconstructionError(
                    f"{normalized}: source snapshot owners must be a non-empty list"
                )
            owners = tuple(raw_owners)
            if len(owners) != len(set(owners)) or not all(
                isinstance(owner, str) for owner in owners
            ):
                raise ReconstructionError(
                    f"{normalized}: invalid source snapshot owner list"
                )
            result[normalized] = owners
        return result
    except (OSError, yaml.YAMLError, layout.LayoutError) as exc:
        raise ReconstructionError(
            f"cannot load source snapshot path owners: {exc}"
        ) from exc


def inspect_source_inventory(
    repo: str,
    plan: ReconstructionPlan,
    *,
    name: str = "vendor-reconstruction-source",
) -> verdict.GateResult:
    """Prove that the Git trees still match the registered source inventory."""
    missing = [
        sha
        for sha in (plan.upstream_sha, plan.snapshot_sha)
        if not gitprim.object_exists(repo, sha)
    ]
    if missing:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (f"required source commit object missing: {', '.join(missing)}",),
        )

    try:
        actual = set(
            gitprim.net_changed_paths(repo, plan.upstream_sha, plan.snapshot_sha)
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (f"cannot inspect pinned source trees: {exc}",),
        )

    expected = set(plan.inventory_paths)
    if actual != expected:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (
                "registered inventory is stale",
                f"missing_from_inventory={sorted(actual - expected)}",
                f"missing_from_git_diff={sorted(expected - actual)}",
            ),
        )
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"source_path_count={len(actual)}",
            f"reconstruction_plan_digest={plan.digest()}",
        ),
    )


def _tree_blob(repo: str, ref: str, path: str) -> bytes | None:
    listing = subprocess.run(
        [
            "git",
            "-C",
            repo,
            *gitprim._STABLE_CONFIG,
            "ls-tree",
            "-z",
            ref,
            "--",
            path,
        ],
        capture_output=True,
    )
    if listing.returncode != 0:
        raise gitprim.GitPrimitiveError(
            f"git ls-tree failed for {ref}:{path}: "
            f"{listing.stderr.decode(errors='replace').strip() or listing.returncode}"
        )
    if not listing.stdout:
        return None
    blob = subprocess.run(
        ["git", "-C", repo, "cat-file", "blob", f"{ref}:{path}"],
        capture_output=True,
    )
    if blob.returncode != 0:
        raise gitprim.GitPrimitiveError(
            f"git cat-file failed for {ref}:{path}: "
            f"{blob.stderr.decode(errors='replace').strip() or blob.returncode}"
        )
    return blob.stdout


def _path_equal(repo: str, left: str, right: str, path: str) -> bool:
    if left == right:
        return True
    if path.endswith(".json"):
        left_blob = _tree_blob(repo, left, path)
        right_blob = _tree_blob(repo, right, path)
        if left_blob is None or right_blob is None:
            return left_blob == right_blob
        try:
            left_value = json.loads(left_blob.decode("utf-8"))
            right_value = json.loads(right_blob.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise gitprim.GitPrimitiveError(
                f"JSON semantic comparison failed for {path!r}: {exc}"
            ) from exc
        return left_value == right_value

    proc = subprocess.run(
        [
            "git",
            "-C",
            repo,
            *gitprim._STABLE_CONFIG,
            "diff",
            "--quiet",
            left,
            right,
            "--",
            path,
        ],
        text=True,
        capture_output=True,
    )
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    raise gitprim.GitPrimitiveError(
        f"git diff --quiet failed for {path!r}: "
        f"{proc.stderr.strip() or proc.returncode}"
    )


def _normalize_shared_owners(
    plan: ReconstructionPlan,
    shared_path_owners: dict[str, list[str] | tuple[str, ...]] | None,
) -> tuple[dict[str, tuple[str, ...]], list[str], list[str]]:
    supplied = shared_path_owners or {}
    candidates = dict(plan.shared_candidates)
    blocking: list[str] = []
    invalid_config: list[str] = []

    extra = sorted(set(supplied) - set(candidates))
    if extra:
        invalid_config.append(
            f"ownership supplied for non-shared paths: {extra}"
        )

    normalized: dict[str, tuple[str, ...]] = {}
    for path, allowed in candidates.items():
        raw = supplied.get(path)
        if raw is None:
            blocking.append(
                f"shared path lacks hunk-level owner resolution: {path} "
                f"candidates={list(allowed)}"
            )
            continue
        if (
            not isinstance(raw, (list, tuple))
            or any(not isinstance(owner, str) for owner in raw)
        ):
            invalid_config.append(
                f"shared path owners must be a string list: {path}"
            )
            continue
        owners = tuple(sorted(set(raw)))
        if not owners:
            blocking.append(f"shared path has empty owner resolution: {path}")
        invalid = sorted(set(owners) - set(allowed))
        if invalid:
            invalid_config.append(
                f"shared path has invalid owners: {path} invalid={invalid} "
                f"candidates={list(allowed)}"
            )
        missing = sorted(set(allowed) - set(owners))
        if missing:
            invalid_config.append(
                f"shared path manifest owners are broader than the resolved "
                f"owners: {path} extra_manifest_owners={missing}"
            )
        normalized[path] = owners
    return normalized, blocking, invalid_config


def check_reconstructed_candidate(
    repo: str,
    plan: ReconstructionPlan,
    manifests_by_id: dict[str, dict],
    candidate_ref: str,
    *,
    shared_path_owners: dict[str, list[str] | tuple[str, ...]] | None = None,
    name: str = "vendor-reconstructed-candidate",
) -> verdict.GateResult:
    """Verify a manually reconstructed vendor candidate, fail closed."""
    source_result = inspect_source_inventory(repo, plan)
    if source_result.verdict != verdict.PASS:
        return verdict.GateResult(name, source_result.verdict, source_result.reasons)

    try:
        candidate_sha = binding.pin(repo, candidate_ref)
    except (binding.BindingError, OSError) as exc:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (f"cannot pin reconstructed candidate: {exc}",),
        )

    shared_owners, owner_blocks, owner_errors = _normalize_shared_owners(
        plan, shared_path_owners
    )
    if owner_errors:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, tuple(owner_errors)
        )
    if owner_blocks:
        return verdict.GateResult(name, verdict.BLOCK, tuple(owner_blocks))

    reasons: list[str] = []
    try:
        if not gitprim.is_ancestor(repo, plan.upstream_sha, candidate_sha):
            reasons.append(
                "candidate does not descend from the approved upstream target"
            )
        if gitprim.is_ancestor(repo, plan.snapshot_sha, candidate_sha):
            reasons.append(
                "candidate illegally contains the unrelated snapshot commit"
            )

        commits = gitprim.commits(repo, plan.upstream_sha, candidate_sha)
        net_paths = set(
            gitprim.net_changed_paths(repo, plan.upstream_sha, candidate_sha)
        )
    except (
        OSError,
        subprocess.SubprocessError,
        gitprim.GitPrimitiveError,
    ) as exc:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (f"cannot inspect reconstructed candidate: {exc}",),
        )

    expected_owners = {
        path: {customization_id}
        for path, customization_id in plan.unique_assignments
    }
    expected_owners.update(
        {path: set(owners) for path, owners in shared_owners.items()}
    )
    expected_paths = set(expected_owners)
    touched_by: dict[str, set[str]] = {
        path: set() for path in expected_paths
    }
    seen_ids: set[str] = set()

    for commit in commits:
        if commit.is_merge:
            reasons.append(f"{commit.sha}: merge commit is not a logical ID unit")
            continue
        if len(commit.customization_ids) != 1:
            reasons.append(
                f"{commit.sha}: expected exactly one Customization-ID, "
                f"got {commit.customization_ids}"
            )
            continue
        customization_id = commit.customization_ids[0]
        seen_ids.add(customization_id)
        manifest = manifests_by_id.get(customization_id)
        if manifest is None:
            reasons.append(
                f"{commit.sha}: unregistered Customization-ID {customization_id}"
            )
            continue
        try:
            changed = gitprim.changed_paths(repo, commit.sha)
            allowed = layout.make_spec(M.declared_changed_paths(manifest))
        except (
            KeyError,
            TypeError,
            OSError,
            subprocess.SubprocessError,
            layout.LayoutError,
        ) as exc:
            return verdict.GateResult(
                name,
                verdict.ANALYSIS_ERROR,
                (f"cannot inspect commit {commit.sha}: {exc}",),
            )
        if not changed:
            reasons.append(f"{commit.sha}: empty reconstruction commit")
        for path in changed:
            if path in plan.excluded_paths:
                reasons.append(
                    f"{commit.sha}: excluded path changed: {path}"
                )
                continue
            if path not in expected_owners:
                reasons.append(
                    f"{commit.sha}: path is outside reconstruction plan: {path}"
                )
                continue
            if not allowed.match_file(path):
                reasons.append(
                    f"{commit.sha}: {path} is outside {customization_id} manifest"
                )
            if customization_id not in expected_owners[path]:
                reasons.append(
                    f"{commit.sha}: {customization_id} is not a resolved owner "
                    f"of {path}"
                )
            touched_by[path].add(customization_id)

    if net_paths != expected_paths:
        reasons.extend(
            (
                f"candidate has unexpected net paths: "
                f"{sorted(net_paths - expected_paths)}",
                f"candidate is missing registered net paths: "
                f"{sorted(expected_paths - net_paths)}",
            )
        )

    missing_ids = sorted(set(plan.active_ids) - seen_ids)
    extra_ids = sorted(seen_ids - set(plan.active_ids))
    if missing_ids:
        reasons.append(f"candidate has no commit for active IDs: {missing_ids}")
    if extra_ids:
        reasons.append(f"candidate uses IDs outside the active plan: {extra_ids}")

    for path in sorted(expected_paths):
        if touched_by[path] != expected_owners[path]:
            reasons.append(
                f"path owner commits mismatch: {path} "
                f"actual={sorted(touched_by[path])} "
                f"expected={sorted(expected_owners[path])}"
            )
        try:
            if not _path_equal(repo, candidate_sha, plan.snapshot_sha, path):
                reasons.append(
                    f"candidate content differs from source snapshot: {path}"
                )
        except gitprim.GitPrimitiveError as exc:
            return verdict.GateResult(
                name, verdict.ANALYSIS_ERROR, (str(exc),)
            )

    for path in plan.excluded_paths:
        try:
            if not _path_equal(repo, candidate_sha, plan.upstream_sha, path):
                reasons.append(
                    f"excluded path differs from approved upstream: {path}"
                )
        except gitprim.GitPrimitiveError as exc:
            return verdict.GateResult(
                name, verdict.ANALYSIS_ERROR, (str(exc),)
            )

    if reasons:
        return verdict.GateResult(name, verdict.BLOCK, tuple(reasons))
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"candidate={candidate_sha}",
            f"approved_upstream={plan.upstream_sha}",
            f"registered_paths={len(expected_paths)}",
            f"excluded_paths={len(plan.excluded_paths)}",
            f"reconstruction_plan_digest={plan.digest()}",
        ),
    )


def load_registration_bundle(registration_dir: str | Path):
    root = Path(registration_dir)
    reg = R.load_registry(root / "customization-registry.yaml")
    manifests = {}
    for entry in reg.entries:
        path = root / entry.manifest
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        manifests[entry.customization_id] = data
    inventory = [
        line.strip()
        for line in (root / reg.source["diff_inventory"])
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    return reg, manifests, inventory


def _result_json(result: verdict.GateResult, plan: ReconstructionPlan) -> str:
    return json.dumps(
        {
            "plan": plan.canonical(),
            "plan_digest": plan.digest(),
            "gate": {
                "name": result.name,
                "verdict": result.verdict,
                "reasons": list(result.reasons),
            },
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan or verify a safe vendor reconstruction"
    )
    parser.add_argument("--repo", required=True)
    parser.add_argument("--registration", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan")
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--candidate", required=True)
    verify_parser.add_argument(
        "--shared-owners",
        help="YAML mapping of shared path to ordered Customization-ID list",
    )
    args = parser.parse_args(argv)

    try:
        reg, manifests, inventory = load_registration_bundle(args.registration)
        source_owners = load_source_snapshot_owners(args.registration)
        plan = build_reconstruction_plan(
            reg,
            manifests,
            inventory,
            source_path_owners=source_owners,
        )
    except (OSError, yaml.YAMLError, R.RegistryError, ReconstructionError) as exc:
        result = verdict.GateResult(
            "vendor-reconstruction-plan",
            verdict.ANALYSIS_ERROR,
            (str(exc),),
        )
        print(
            json.dumps(
                {
                    "gate": {
                        "name": result.name,
                        "verdict": result.verdict,
                        "reasons": list(result.reasons),
                    }
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return verdict.to_exit_code(result.verdict)

    if args.command == "plan":
        result = inspect_source_inventory(args.repo, plan)
    else:
        owners = None
        if args.shared_owners:
            try:
                owners = yaml.safe_load(
                    Path(args.shared_owners).read_text(encoding="utf-8")
                )
            except (OSError, yaml.YAMLError) as exc:
                result = verdict.GateResult(
                    "vendor-reconstructed-candidate",
                    verdict.ANALYSIS_ERROR,
                    (f"cannot load shared owner map: {exc}",),
                )
                print(_result_json(result, plan))
                return verdict.to_exit_code(result.verdict)
            if not isinstance(owners, dict):
                result = verdict.GateResult(
                    "vendor-reconstructed-candidate",
                    verdict.ANALYSIS_ERROR,
                    ("shared owner map must be a mapping",),
                )
                print(_result_json(result, plan))
                return verdict.to_exit_code(result.verdict)
        result = check_reconstructed_candidate(
            args.repo,
            plan,
            manifests,
            args.candidate,
            shared_path_owners=owners,
        )

    print(_result_json(result, plan))
    return verdict.to_exit_code(result.verdict)


if __name__ == "__main__":
    raise SystemExit(main())
