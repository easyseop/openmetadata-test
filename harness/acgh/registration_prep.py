"""Safe preparation of versioned BANK-OM registration inputs.

The preparation workflow has two deliberately separate phases:

* ``plan`` pins Git refs, calculates facts, and writes a proposal outside the
  registration directory.
* ``apply`` accepts only that exact proposal digest, rechecks every pinned
  input, and atomically writes the approved generated files.

Git-derived facts are automated. Business decisions such as required paths,
contracts, ownership, and whether a bank-only path belongs in an upstream
watch list are never inferred.
"""
from __future__ import annotations

import copy
import datetime
import difflib
import hashlib
import json
import os
import socket
import tempfile
from collections import defaultdict
from pathlib import Path

import jsonschema
import yaml

from acgh import contracts
from acgh import gitprim
from acgh import layout as layout_module
from acgh import manifest as manifest_module
from acgh import registry as registry_module
from acgh import verdict

_SCHEMA_ROOT = Path(__file__).parent / "schema"
_REGISTRATION_INPUTS = (
    "customization-registry.yaml",
    "contracts.yaml",
    "repository-layout.yaml",
    "sensitive-zones.yaml",
    "source-diff-paths.txt",
    "source-snapshot-path-owners.yaml",
    "shared-path-owners.yaml",
)
# Policy inputs prep never reads itself, but the later gates do: the approver
# judged the proposal under these rules, so a change must invalidate it.
_OPTIONAL_REGISTRATION_INPUTS = frozenset(
    {"sensitive-zones.yaml", "source-diff-paths.txt"}
)


def _utc_now() -> str:
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )
_LFS_PREFIX = b"version https://git-lfs.github.com/spec/v1\n"


class PreparationError(ValueError):
    """A proposal or approval is structurally unsafe."""


class PolicyRefusal(PreparationError):
    """A rule was evaluated and the input was rejected.

    Distinct from the base error, which means the input could not be read or
    trusted well enough to judge. A refusal is a BLOCKED outcome the operator
    fixes in the approval or the proposal; it is not an ANALYSIS_ERROR.
    """


class StaleProposalError(PreparationError):
    """The repository or registration changed after proposal creation."""


class ApplyLockError(PreparationError):
    """Another apply owns the registration-directory lock."""


def _validator(name: str) -> jsonschema.protocols.Validator:
    schema = json.loads((_SCHEMA_ROOT / name).read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema, format_checker=jsonschema.FormatChecker())


def _validate(data: dict, schema_name: str, label: str) -> dict:
    errors = sorted(
        _validator(schema_name).iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        def location(error):
            return "/".join(str(part) for part in error.absolute_path) or "<root>"

        raise PreparationError(
            f"{label}: "
            + "; ".join(
                f"{location(error)}: {error.message}" for error in errors
            )
        )
    return data


def _load_yaml(path: Path, label: str) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise PreparationError(f"cannot read {label}: {exc}") from exc
    if not isinstance(data, dict):
        raise PreparationError(f"{label} is not a mapping")
    return data


def _yaml_bytes(data: dict) -> bytes:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    ).encode("utf-8")


def proposal_digest(proposal: dict) -> str:
    return verdict.canonical_digest(
        _validate(
            copy.deepcopy(proposal),
            "registration-proposal.schema.json",
            "proposal",
        )
    )


def registration_state_digest(registration: Path) -> str:
    """Digest only human/policy inputs that must remain stable until apply."""
    payload: dict[str, str | None] = {}
    paths = [registration / name for name in _REGISTRATION_INPUTS]
    paths.extend(sorted((registration / "manifests").glob("BANK-OM-*.yaml")))
    for path in paths:
        relative = path.relative_to(registration).as_posix()
        if not path.exists() and relative in _OPTIONAL_REGISTRATION_INPUTS:
            # Recorded as absent rather than skipped, so a policy file that
            # appears between plan and apply also invalidates the approval.
            payload[relative] = None
            continue
        if not path.is_file() or path.is_symlink():
            raise PreparationError(
                f"registration input is missing or not a regular file: {path}"
            )
        payload[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return verdict.canonical_digest(payload)


def _load_registration(registration: Path):
    layout = layout_module.load_layout(registration / "repository-layout.yaml")
    registry_data = _load_yaml(
        registration / "customization-registry.yaml", "customization registry"
    )
    registry = registry_module.parse_registry(registry_data)
    catalog = contracts.load_catalog(registration / "contracts.yaml")

    manifests: dict[str, dict] = {}
    for path in sorted((registration / "manifests").glob("BANK-OM-*.yaml")):
        data = manifest_module.load_manifest(path, layout)
        customization_id = data["customization_id"]
        if customization_id in manifests:
            raise PreparationError(
                f"duplicate manifest customization ID: {customization_id}"
            )
        manifests[customization_id] = data
    registry_module.validate_references(registry, manifests, catalog)
    return layout, registry_data, registry, catalog, manifests


def _finding(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def _review(
    items: list[dict],
    code: str,
    question: str,
    *,
    customization_id: str | None = None,
    path: str | None = None,
    paths: list[str] | None = None,
) -> None:
    item = {
        "finding_id": f"REVIEW-{len(items) + 1:04d}",
        "code": code,
        "question": question,
    }
    if customization_id is not None:
        item["customization_id"] = customization_id
    if path is not None:
        item["path"] = path
    if paths is not None:
        item["paths"] = paths
    items.append(item)


def _new_manifest(
    customization_id: str,
    changed_paths: list[str],
    metadata: dict,
    patch_paths: set[str],
) -> dict:
    required = sorted(set(metadata.get("required_changed_paths", [])))
    dependencies = sorted(set(metadata.get("watch_dependencies", [])))
    return {
        "schema_version": 2,
        "customization_id": customization_id,
        "status": "active",
        "kind": metadata["kind"],
        "title": metadata["title"],
        "implementation": {
            "changed_paths": changed_paths,
            "required_changed_paths": required,
        },
        "upgrade_watch": {
            "paths": sorted(
                (set(changed_paths) & patch_paths) | set(dependencies)
            )
        },
        "assurance": {
            "contracts": sorted(set(metadata["contracts"])),
            "direct_tests": sorted(set(metadata.get("direct_tests", []))),
        },
        "series": {
            "allowed": bool(metadata.get("series_allowed", False)),
            "depends_on": sorted(set(metadata.get("depends_on", []))),
        },
    }


def _new_registry_entry(customization_id: str, metadata: dict) -> dict:
    return {
        "customization_id": customization_id,
        "title": metadata["title"],
        "owner": metadata["owner"],
        "owner_status": metadata["owner_status"],
        "status": "active",
        "criticality": metadata["criticality"],
        "manifest": f"manifests/{customization_id}.yaml",
        "contracts": sorted(set(metadata["contracts"])),
        "provenance": metadata["provenance"],
    }


def _validate_new_metadata(
    customization_id: str,
    metadata,
    catalog: contracts.Catalog,
) -> list[str]:
    if not isinstance(metadata, dict):
        return ["new-ID input must be a mapping"]
    required = {
        "title",
        "owner",
        "owner_status",
        "criticality",
        "kind",
        "provenance",
        "required_changed_paths",
        "contracts",
    }
    missing = sorted(required - set(metadata))
    errors = (
        [f"missing new-ID fields: {missing}"] if missing else []
    )
    if metadata.get("owner_status") not in {"assigned", "pending"}:
        errors.append("owner_status must be assigned or pending")
    if metadata.get("criticality") not in {"low", "medium", "high", "critical"}:
        errors.append("criticality is invalid")
    if metadata.get("kind") not in {"core-patch", "extension", "governance"}:
        errors.append("kind is invalid")
    if metadata.get("provenance") != "candidate-follow-up":
        errors.append("new IDs must use provenance candidate-follow-up")
    list_fields = (
        "required_changed_paths",
        "contracts",
        "direct_tests",
        "watch_dependencies",
        "depends_on",
    )
    for field in list_fields:
        value = metadata.get(field, [])
        if not isinstance(value, list) or any(
            not isinstance(item, str) or not item for item in value
        ):
            errors.append(f"{field} must be a list of non-empty strings")
        elif len(value) != len(set(value)):
            errors.append(f"{field} must not contain duplicates")
    if "series_allowed" in metadata and not isinstance(
        metadata["series_allowed"], bool
    ):
        errors.append("series_allowed must be a boolean")
    contracts_value = metadata.get("contracts", [])
    if not isinstance(contracts_value, list):
        contracts_value = []
    for contract_id in contracts_value:
        if not isinstance(contract_id, str):
            continue
        contract = catalog.get(contract_id)
        if contract is None:
            errors.append(f"unknown contract: {contract_id}")
        elif customization_id not in contract.customization_ids:
            errors.append(
                f"{contract_id} lacks reverse binding to {customization_id}"
            )
    return errors


def _check_path_modes(
    repo: str,
    custom_sha: str,
    paths: set[str],
    blocked: list[dict],
    analysis_errors: list[dict],
    reviews: list[dict],
) -> set[str]:
    """Judge each touched path at custom HEAD; return the ones no longer there."""
    removed: set[str] = set()
    try:
        entries = gitprim.tree_entries(repo, custom_sha)
    except (OSError, gitprim.GitPrimitiveError) as exc:
        analysis_errors.append(_finding("TREE_READ_FAILED", str(exc)))
        return removed
    for path in sorted(paths):
        entry = entries.get(path)
        if entry is None:
            # The series removed the file, or renamed away from it. That is a
            # legitimate change, so ask rather than dead-end the operator; a
            # required path that disappears is caught separately against the
            # net diff.
            _review(
                reviews,
                "REMOVED_PATH_DECISION",
                "이 경로는 해당 BANK-OM commit이 바꿨지만 custom 최종 상태에는 "
                "없습니다. 삭제·이름 변경이 의도한 것인지, changed_paths에 계속 "
                "남길지 담당자가 확인해야 합니다.",
                path=path,
            )
            removed.add(path)
            continue
        if entry.mode == "120000":
            blocked.append(_finding("SYMLINK_PATH", f"{path}: symlink is unsupported"))
            continue
        if entry.mode == "160000" or entry.object_type == "commit":
            blocked.append(
                _finding("SUBMODULE_PATH", f"{path}: submodule is unsupported")
            )
            continue
        try:
            if gitprim.blob_bytes(repo, custom_sha, path).startswith(_LFS_PREFIX):
                blocked.append(
                    _finding("LFS_POINTER_PATH", f"{path}: Git LFS is unsupported")
                )
        except gitprim.GitPrimitiveError as exc:
            analysis_errors.append(_finding("BLOB_READ_FAILED", str(exc)))
    return removed


def build_plan(
    repo: Path,
    registration: Path,
    *,
    patch_ref: str,
    custom_ref: str,
    product_version: str,
    new_id_metadata: dict[str, dict] | None = None,
) -> dict:
    """Build one deterministic proposal without writing registration files."""
    repo = repo.resolve(strict=True)
    registration = registration.resolve(strict=True)
    blocked: list[dict] = []
    analysis_errors: list[dict] = []
    reviews: list[dict] = []
    changes: list[dict] = []
    new_id_metadata = new_id_metadata or {}

    try:
        layout, registry_data, registry, catalog, manifests = _load_registration(
            registration
        )
    except (
        OSError,
        UnicodeError,
        yaml.YAMLError,
        contracts.ContractError,
        layout_module.LayoutError,
        manifest_module.ManifestError,
        registry_module.RegistryError,
    ) as exc:
        raise PreparationError(f"cannot load registration policy: {exc}") from exc
    try:
        patch_sha = gitprim.resolve_commit(str(repo), patch_ref)
        custom_sha = gitprim.resolve_commit(str(repo), custom_ref)
        merge_base = gitprim.merge_base(str(repo), patch_sha, custom_sha)
        dirty = gitprim.worktree_is_dirty(str(repo))
    except (OSError, gitprim.GitPrimitiveError) as exc:
        raise PreparationError(f"cannot pin Git inputs: {exc}") from exc

    if dirty:
        blocked.append(
            _finding(
                "DIRTY_WORKTREE",
                "product repository has committed or untracked worktree changes",
            )
        )
    if merge_base != patch_sha:
        analysis_errors.append(
            _finding(
                "UNRELATED_OR_NONLINEAR_RANGE",
                f"patch {patch_sha} is not the merge base of custom {custom_sha}",
            )
        )
    for label, sha in (
        ("registry source snapshot", registry.source["snapshot_sha"]),
        ("registry upstream", registry.source["upstream_sha"]),
    ):
        if not gitprim.object_exists(str(repo), sha):
            blocked.append(
                _finding(
                    "REGISTRATION_GIT_OBJECT_MISSING",
                    f"{label} commit is unavailable in product repository: {sha}",
                )
            )

    commits = (
        gitprim.commits(str(repo), patch_sha, custom_sha)
        if not analysis_errors
        else []
    )
    if not commits and not analysis_errors:
        analysis_errors.append(
            _finding("EMPTY_CUSTOM_RANGE", "patch..custom contains no commits")
        )

    layout_by_path: dict[str, str] = {}
    commit_records: dict[str, list[dict]] = defaultdict(list)
    changed_by_id: dict[str, set[str]] = defaultdict(set)
    sequence: list[str] = []
    for commit in commits:
        paths = sorted(set(gitprim.changed_paths(str(repo), commit.sha)))
        if commit.is_merge:
            blocked.append(
                _finding("MERGE_COMMIT", f"{commit.sha}: merge commit is not allowed")
            )
        if not paths:
            blocked.append(
                _finding("EMPTY_COMMIT", f"{commit.sha}: commit changes no paths")
            )
        roles: set[str] = set()
        for path in paths:
            try:
                normalized = layout_module.ensure_literal(path)
                role = layout.classify(normalized)
            except layout_module.LayoutError as exc:
                analysis_errors.append(_finding("INVALID_PATH", str(exc)))
                continue
            layout_by_path[normalized] = role
            roles.add(role)
            if role == layout_module.UNKNOWN:
                analysis_errors.append(
                    _finding("UNKNOWN_PATH", f"{path}: no repository owner")
                )
        if len(roles - {layout_module.UNKNOWN}) > 1:
            blocked.append(
                _finding(
                    "MIXED_OWNERSHIP_COMMIT",
                    f"{commit.sha}: commit mixes ownership roles {sorted(roles)}",
                )
            )
        if (
            commit.change_type == "governance"
            and roles - {layout_module.GOVERNANCE, layout_module.UNKNOWN}
        ):
            blocked.append(
                _finding(
                    "GOVERNANCE_COMMIT_SCOPE",
                    f"{commit.sha}: governance commit changes non-governance "
                    f"roles {sorted(roles)}",
                )
            )
        if len(commit.customization_ids) != 1:
            blocked.append(
                _finding(
                    "CUSTOMIZATION_ID_CARDINALITY",
                    f"{commit.sha}: expected one Customization-ID, "
                    f"got {commit.customization_ids}",
                )
            )
            continue
        customization_id = commit.customization_ids[0]
        sequence.append(customization_id)
        commit_records[customization_id].append(
            {
                "sha": commit.sha,
                "subject": commit.subject,
                "changed_paths": paths,
            }
        )
        changed_by_id[customization_id].update(paths)

    for customization_id in sorted(set(sequence)):
        positions = [
            index for index, value in enumerate(sequence) if value == customization_id
        ]
        if positions and positions != list(range(positions[0], positions[-1] + 1)):
            blocked.append(
                _finding(
                    "NONCONTIGUOUS_SERIES",
                    f"{customization_id}: commits are interrupted by another ID",
                )
            )

    all_touched = set().union(*changed_by_id.values()) if changed_by_id else set()
    removed_at_head = _check_path_modes(
        str(repo), custom_sha, all_touched, blocked, analysis_errors, reviews
    )

    net_paths = sorted(
        set(gitprim.net_changed_paths(str(repo), patch_sha, custom_sha))
        if not analysis_errors
        else set()
    )
    owned_paths = set().union(*changed_by_id.values()) if changed_by_id else set()
    for path in sorted(set(net_paths) - owned_paths):
        blocked.append(
            _finding(
                "UNOWNED_NET_CHANGE",
                f"{path}: final patch..custom change has no BANK-OM commit owner",
            )
        )
    for unused_id in sorted(set(new_id_metadata) - set(changed_by_id)):
        blocked.append(
            _finding(
                "UNUSED_NEW_CUSTOMIZATION_INPUT",
                f"{unused_id}: new-ID input has no commit in patch..custom",
            )
        )

    patch_paths = set(gitprim.list_tree_recursive(str(repo), patch_sha))
    registry_entries = registry.by_id()
    registry_after = copy.deepcopy(registry_data)
    registry_changed = False
    proposed_manifests = copy.deepcopy(manifests)

    for customization_id in sorted(changed_by_id):
        actual = sorted(changed_by_id[customization_id])
        entry = registry_entries.get(customization_id)
        manifest = manifests.get(customization_id)
        action = "update_existing"

        if (entry is None) != (manifest is None):
            blocked.append(
                _finding(
                    "PARTIAL_CUSTOMIZATION_REGISTRATION",
                    f"{customization_id}: registry entry and manifest must either "
                    "both exist or both be absent",
                )
            )
            continue
        if entry is None and manifest is None:
            metadata = new_id_metadata.get(customization_id)
            if metadata is None:
                _review(
                    reviews,
                    "NEW_CUSTOMIZATION_INPUT",
                    "새 BANK-OM의 제목·담당자·중요도·필수 경로·Contract를 "
                    "new-ID 입력 파일에 작성해야 합니다.",
                    customization_id=customization_id,
                )
                continue
            metadata_errors = _validate_new_metadata(
                customization_id, metadata, catalog
            )
            if metadata_errors:
                blocked.extend(
                    _finding(
                        "INVALID_NEW_CUSTOMIZATION",
                        f"{customization_id}: {message}",
                    )
                    for message in metadata_errors
                )
                continue
            manifest = _new_manifest(
                customization_id, actual, metadata, patch_paths
            )
            registry_after["entries"].append(
                _new_registry_entry(customization_id, metadata)
            )
            registry_changed = True
            action = "create_new"
            _review(
                reviews,
                "NEW_CUSTOMIZATION_APPROVAL",
                "신규 BANK-OM의 업무 범위·담당자·필수 경로·Contract를 "
                "독립적으로 확인해야 합니다.",
                customization_id=customization_id,
            )
        elif entry.status != "active":
            blocked.append(
                _finding(
                    "RETIRED_ID_REUSED",
                    f"{customization_id}: non-active ID appears in custom commits",
                )
            )
            continue

        series_allowed = manifest.get("series", {}).get("allowed", False)
        if len(commit_records[customization_id]) > 1 and not series_allowed:
            blocked.append(
                _finding(
                    "SERIES_NOT_ALLOWED",
                    f"{customization_id}: multiple commits require series.allowed",
                )
            )

        before_changed = set(manifest_module.declared_changed_paths(manifest))
        schema_migrated = manifest.get("schema_version") != 2
        required = set(
            manifest.get("implementation", {}).get(
                "required_changed_paths", []
            )
        )
        missing_required = sorted(required - set(actual))
        if missing_required:
            blocked.append(
                _finding(
                    "REQUIRED_PATH_REMOVED",
                    f"{customization_id}: required paths not changed by its series: "
                    f"{missing_required}",
                )
            )
        # touched != net. A file edited then reverted is touched but nets out,
        # and T40's lower bound reads the net diff — so prep must judge the
        # same way or it hands READY to a candidate the gate will block.
        reverted_required = sorted(required & set(actual) - set(net_paths))
        if reverted_required:
            blocked.append(
                _finding(
                    "REQUIRED_PATH_REVERTED",
                    f"{customization_id}: required paths are changed by its series "
                    f"but absent from the final patch..custom diff: "
                    f"{reverted_required}",
                )
            )
        for path in sorted(
            set(actual) - set(net_paths) - required - removed_at_head
        ):
            _review(
                reviews,
                "REVERTED_PATH_DECISION",
                "이 경로는 해당 BANK-OM commit이 바꿨지만 공식 코드와 최종 결과가 "
                "같아 최종 diff에는 없습니다. 되돌린 것이 의도한 결과인지 "
                "담당자가 확인해야 합니다.",
                customization_id=customization_id,
                path=path,
            )
        after_manifest = copy.deepcopy(manifest)
        after_manifest["schema_version"] = 2
        after_manifest["implementation"].pop("allowed_changed_paths", None)
        after_manifest["implementation"].pop("candidate_additional_paths", None)
        after_manifest["implementation"]["changed_paths"] = actual
        existing_watch = set(
            after_manifest.get("upgrade_watch", {}).get("paths", [])
        )
        automatic_watch = set(actual) & patch_paths
        after_manifest.setdefault("upgrade_watch", {})["paths"] = sorted(
            existing_watch | automatic_watch
        )

        for path in sorted(set(actual) - before_changed):
            _review(
                reviews,
                "REQUIRED_PATH_DECISION",
                "새 변경 파일이 빠질 때 기능이 소실되는지 판단하고 "
                "required_changed_paths 추가 여부를 확인해야 합니다.",
                customization_id=customization_id,
                path=path,
            )
        bank_only_watch = sorted(existing_watch - patch_paths)
        if bank_only_watch:
            _review(
                reviews,
                "BANK_ONLY_WATCH_DECISION",
                f"공식 patch에 없는 기존 watch 경로 {len(bank_only_watch)}개를 "
                "보존할지 행내 changed_paths만으로 관리할지 담당자가 "
                "한 번에 확인해야 합니다.",
                customization_id=customization_id,
                paths=bank_only_watch,
            )

        try:
            manifest_module.validate_manifest(after_manifest, layout)
        except manifest_module.ManifestError as exc:
            blocked.append(
                _finding(
                    "PROPOSED_MANIFEST_INVALID",
                    f"{customization_id}: {exc}",
                )
            )
            continue
        proposed_manifests[customization_id] = after_manifest
        added = sorted(set(actual) - before_changed)
        removed = sorted(before_changed - set(actual))
        added_watch = sorted(automatic_watch - existing_watch)
        if (
            action == "create_new"
            or schema_migrated
            or added
            or removed
            or added_watch
        ):
            changes.append(
                {
                    "customization_id": customization_id,
                    "action": action,
                    "manifest_path": f"manifests/{customization_id}.yaml",
                    "added_changed_paths": added,
                    "removed_changed_paths": removed,
                    "added_watch_paths": added_watch,
                    "after_manifest": after_manifest,
                }
            )

    try:
        proposed_registry = registry_module.parse_registry(registry_after)
        registry_module.validate_references(
            proposed_registry,
            proposed_manifests,
            catalog,
        )
    except registry_module.RegistryError as exc:
        blocked.append(
            _finding(
                "PROPOSED_REGISTRATION_INVALID",
                str(exc),
            )
        )

    source_owners = _load_yaml(
        registration / "source-snapshot-path-owners.yaml",
        "source snapshot path owners",
    )
    for path, owners in source_owners.items():
        if not isinstance(owners, list):
            analysis_errors.append(
                _finding("INVALID_SOURCE_OWNER_MAP", f"{path}: owners must be a list")
            )
            continue
        for customization_id in owners:
            if path not in changed_by_id.get(customization_id, set()):
                blocked.append(
                    _finding(
                        "SOURCE_OWNER_SCOPE_LOST",
                        f"{customization_id}: source-owned path missing from current "
                        f"series: {path}",
                    )
                )
    expected_shared = {
        path: sorted(set(owners))
        for path, owners in source_owners.items()
        if isinstance(owners, list) and len(set(owners)) > 1
    }
    actual_shared = _load_yaml(
        registration / "shared-path-owners.yaml", "shared path owners"
    )
    normalized_shared = {
        path: sorted(set(owners))
        for path, owners in actual_shared.items()
        if isinstance(owners, list)
    }
    if normalized_shared != expected_shared:
        analysis_errors.append(
            _finding(
                "SHARED_OWNER_MAP_MISMATCH",
                "shared-path-owners.yaml does not equal multi-owner source paths",
            )
        )

    inventory = {
        "schema_version": 1,
        "product_version": product_version,
        "range": {
            "patch_ref": patch_ref,
            "patch_sha": patch_sha,
            "custom_ref": custom_ref,
            "custom_head_sha": custom_sha,
        },
        "customizations": {
            customization_id: {
                "commits": commit_records[customization_id],
                "latest_commit_sha": commit_records[customization_id][-1]["sha"],
                "changed_paths": sorted(changed_by_id[customization_id]),
            }
            for customization_id in sorted(commit_records)
        },
        "net_changed_paths": net_paths,
    }
    _validate(inventory, "commit-inventory.schema.json", "commit inventory")

    if analysis_errors:
        status = "ANALYSIS_ERROR"
    elif blocked:
        status = "BLOCKED"
    elif reviews:
        status = "REVIEW_REQUIRED"
    else:
        status = "READY"
    apply_ready = not analysis_errors and not blocked and all(
        customization_id in manifests or customization_id in new_id_metadata
        for customization_id in changed_by_id
    )
    proposal = {
        "schema_version": 1,
        "status": status,
        "apply_ready": apply_ready,
        "inputs": {
            "repository": registry.source["repository"],
            "registration": registration.name,
            "patch_ref": patch_ref,
            "patch_sha": patch_sha,
            "custom_ref": custom_ref,
            "custom_head_sha": custom_sha,
            "registration_state_digest": registration_state_digest(registration),
        },
        "generated": {
            "commit_inventory": inventory,
            "current_diff_paths": net_paths,
        },
        "changes": changes,
        "registry_after": registry_after if registry_changed else None,
        "review_required": reviews,
        "blocked": blocked,
        "analysis_errors": analysis_errors,
    }
    return _validate(
        proposal, "registration-proposal.schema.json", "registration proposal"
    )


def write_plan(output: Path, proposal: dict, *, registration: Path) -> str:
    """Write a new immutable proposal directory; never overwrite one."""
    registration = registration.resolve(strict=True)
    output = output.resolve(strict=False)
    try:
        output.relative_to(registration)
    except ValueError:
        pass
    else:
        raise PolicyRefusal(
            "proposal output must be outside the registration directory"
        )
    if output.exists():
        raise PolicyRefusal(f"proposal output already exists: {output}")
    output.mkdir(parents=True)
    digest = proposal_digest(proposal)
    (output / "commit-inventory.yaml").write_bytes(
        _yaml_bytes(proposal["generated"]["commit_inventory"])
    )
    paths = proposal["generated"]["current_diff_paths"]
    (output / "current-diff-paths.txt").write_text(
        "".join(f"{path}\n" for path in paths),
        encoding="utf-8",
    )
    (output / "proposal.yaml").write_bytes(_yaml_bytes(proposal))
    (output / "proposal-digest.txt").write_text(digest + "\n", encoding="utf-8")
    (output / "review-required.yaml").write_bytes(
        _yaml_bytes(
            {
                "schema_version": 1,
                "proposal_digest": digest,
                "status": proposal["status"],
                "items": proposal["review_required"],
            }
        )
    )
    proposed = output / "proposed-registration"
    proposed.mkdir()
    for change in proposal["changes"]:
        target = proposed / change["manifest_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_yaml_bytes(change["after_manifest"]))
    if proposal.get("registry_after") is not None:
        (proposed / "customization-registry.yaml").write_bytes(
            _yaml_bytes(proposal["registry_after"])
        )
    (output / "diff.patch").write_text(
        _proposal_diff(registration, proposal),
        encoding="utf-8",
    )
    (output / "summary.md").write_text(_summary(proposal, digest), encoding="utf-8")
    return digest


def _proposal_diff(registration: Path, proposal: dict) -> str:
    chunks: list[str] = []
    changes = {
        change["manifest_path"]: _yaml_bytes(change["after_manifest"]).decode("utf-8")
        for change in proposal["changes"]
    }
    if proposal.get("registry_after") is not None:
        changes["customization-registry.yaml"] = _yaml_bytes(
            proposal["registry_after"]
        ).decode("utf-8")
    for relative in sorted(changes):
        target = _safe_target(registration, relative)
        before = target.read_text(encoding="utf-8").splitlines(keepends=True)
        after = changes[relative].splitlines(keepends=True)
        chunks.extend(
            difflib.unified_diff(
                before,
                after,
                fromfile=f"a/{relative}",
                tofile=f"b/{relative}",
            )
        )
    return "".join(chunks)


def _summary(proposal: dict, digest: str) -> str:
    lines = [
        "# 등록자료 준비 제안 요약",
        "",
        f"- 상태: `{proposal['status']}`",
        f"- 승인 조건 충족 후 적용 가능한 구조: "
        f"`{'yes' if proposal['apply_ready'] else 'no'}`",
        f"- patch SHA: `{proposal['inputs']['patch_sha']}`",
        f"- custom SHA: `{proposal['inputs']['custom_head_sha']}`",
        f"- 제안 digest: `{digest}`",
        f"- 자동 변경: {len(proposal['changes'])}건",
        f"- 사람 판단: {len(proposal['review_required'])}건",
        f"- 차단: {len(proposal['blocked'])}건",
        f"- 분석 오류: {len(proposal['analysis_errors'])}건",
        "",
        "이 제안은 실제 등록 폴더를 수정하지 않았습니다.",
        "REVIEW_REQUIRED 항목은 담당자가 승인서에 같은 finding ID와 사유를 "
        "기록해야 합니다.",
        "",
    ]
    return "\n".join(lines)


def approval_template(proposal: dict) -> dict:
    digest = proposal_digest(proposal)
    return {
        "schema_version": 1,
        "proposal_digest": digest,
        "approved_by": "REPLACE_WITH_APPROVER_ID",
        "approved_at": "REPLACE_WITH_RFC3339_TIME",
        "decisions": [
            {
                "finding_id": item["finding_id"],
                "decision": "accept_proposal",
                "reason": "REPLACE_WITH_REVIEW_REASON",
            }
            for item in proposal["review_required"]
        ],
    }


def load_proposal(path: Path) -> dict:
    return _validate(
        _load_yaml(path, "registration proposal"),
        "registration-proposal.schema.json",
        "registration proposal",
    )


def _load_approval(path: Path) -> dict:
    return _validate(
        _load_yaml(path, "registration approval"),
        "registration-approval.schema.json",
        "registration approval",
    )


def _safe_target(registration: Path, relative: str) -> Path:
    allowed = {
        "commit-inventory.yaml",
        "current-diff-paths.txt",
        "customization-registry.yaml",
    }
    if relative not in allowed and not (
        relative.startswith("manifests/BANK-OM-") and relative.endswith(".yaml")
    ):
        raise PolicyRefusal(f"proposal targets forbidden path: {relative}")
    target = registration / relative
    if target.is_symlink() or target.parent.is_symlink():
        raise PolicyRefusal(f"proposal target uses a symlink: {relative}")
    target.resolve(strict=False).relative_to(registration.resolve(strict=True))
    return target


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def observed_git_facts(repo: str, patch_sha: str, custom_sha: str) -> dict:
    """Recompute the Git-derived facts of a pinned range.

    Deliberately independent of :func:`build_plan`'s judgment loop: apply must
    be able to reject a proposal that was edited after ``plan`` produced it, so
    it recomputes the facts rather than trusting the file.
    """
    commits_by_id: dict[str, list[dict]] = defaultdict(list)
    changed_by_id: dict[str, set[str]] = defaultdict(set)
    for commit in gitprim.commits(repo, patch_sha, custom_sha):
        if len(commit.customization_ids) != 1:
            continue  # 0/many IDs never reach a proposal change
        customization_id = commit.customization_ids[0]
        paths = sorted(set(gitprim.changed_paths(repo, commit.sha)))
        commits_by_id[customization_id].append(
            {"sha": commit.sha, "subject": commit.subject, "changed_paths": paths}
        )
        changed_by_id[customization_id].update(paths)
    return {
        "customizations": {
            customization_id: {
                "commits": commits_by_id[customization_id],
                "latest_commit_sha": commits_by_id[customization_id][-1]["sha"],
                "changed_paths": sorted(changed_by_id[customization_id]),
            }
            for customization_id in sorted(commits_by_id)
        },
        "net_changed_paths": sorted(
            set(gitprim.net_changed_paths(repo, patch_sha, custom_sha))
        ),
    }


def _assert_proposal_is_derivable(
    repo: Path, registration: Path, proposal: dict
) -> None:
    """Reject a proposal that ``plan`` could not have produced.

    The proposal digest only binds proposal to approval; it says nothing about
    where the proposal came from. Without this check a hand-edited
    ``proposal.yaml`` plus a regenerated approval writes arbitrary manifests
    into the registration directory.
    """
    inputs = proposal["inputs"]
    facts = observed_git_facts(
        str(repo), inputs["patch_sha"], inputs["custom_head_sha"]
    )
    inventory = proposal["generated"]["commit_inventory"]
    if inventory.get("customizations") != facts["customizations"]:
        raise StaleProposalError(
            "commit inventory does not match the pinned Git range"
        )
    if list(proposal["generated"]["current_diff_paths"]) != facts["net_changed_paths"]:
        raise StaleProposalError(
            "current diff paths do not match the pinned Git range"
        )
    if inventory.get("range", {}).get("patch_sha") != inputs["patch_sha"] or (
        inventory.get("range", {}).get("custom_head_sha")
        != inputs["custom_head_sha"]
    ):
        raise StaleProposalError("commit inventory range does not match inputs")

    layout, _registry_data, registry, catalog, manifests = _load_registration(
        registration
    )
    proposed = dict(manifests)
    for change in proposal["changes"]:
        customization_id = change["customization_id"]
        after = change["after_manifest"]
        if change["manifest_path"] != f"manifests/{customization_id}.yaml":
            raise PolicyRefusal(
                f"{customization_id}: manifest path does not match its ID"
            )
        if after.get("customization_id") != customization_id:
            raise PolicyRefusal(
                f"{customization_id}: after_manifest declares a different ID"
            )
        observed = facts["customizations"].get(customization_id, {}).get(
            "changed_paths", []
        )
        if list(after.get("implementation", {}).get("changed_paths", [])) != observed:
            raise StaleProposalError(
                f"{customization_id}: after_manifest changed_paths do not equal "
                "the paths its commits actually changed"
            )
        try:
            manifest_module.validate_manifest(after, layout)
        except manifest_module.ManifestError as exc:
            raise PolicyRefusal(
                f"{customization_id}: proposed manifest is invalid: {exc}"
            ) from exc
        proposed[customization_id] = after

    proposed_registry = registry
    if proposal.get("registry_after") is not None:
        proposed_registry = registry_module.parse_registry(
            proposal["registry_after"]
        )
    try:
        registry_module.validate_references(proposed_registry, proposed, catalog)
    except registry_module.RegistryError as exc:
        raise PolicyRefusal(
            f"proposed registration state is inconsistent: {exc}"
        ) from exc


def apply_plan(
    repo: Path,
    registration: Path,
    *,
    proposal_path: Path,
    approval_path: Path,
) -> dict:
    """Apply an explicitly approved, unchanged proposal with rollback."""
    repo = repo.resolve(strict=True)
    registration = registration.resolve(strict=True)
    proposal = load_proposal(proposal_path)
    approval = _load_approval(approval_path)
    digest = proposal_digest(proposal)
    if not proposal["apply_ready"] or proposal["status"] in {
        "BLOCKED",
        "ANALYSIS_ERROR",
    }:
        raise PolicyRefusal(
            f"proposal status {proposal['status']} is not applicable"
        )
    if approval["proposal_digest"] != digest:
        raise StaleProposalError("approval digest does not match proposal")
    review_ids = {item["finding_id"] for item in proposal["review_required"]}
    decision_ids = [item["finding_id"] for item in approval["decisions"]]
    if len(decision_ids) != len(set(decision_ids)):
        raise PolicyRefusal("approval has duplicate finding decisions")
    if set(decision_ids) != review_ids:
        raise PolicyRefusal(
            "approval decisions do not exactly cover review-required findings"
        )
    if approval["approved_by"] == "REPLACE_WITH_APPROVER_ID":
        raise PolicyRefusal("approval still contains placeholder approver")
    if not approval["approved_by"].strip():
        raise PolicyRefusal("approval approver is blank")
    if any(
        item["reason"] == "REPLACE_WITH_REVIEW_REASON"
        or not item["reason"].strip()
        for item in approval["decisions"]
    ):
        raise PolicyRefusal("approval contains a placeholder or blank reason")

    if gitprim.worktree_is_dirty(str(repo)):
        raise StaleProposalError("product repository worktree is dirty")
    inputs = proposal["inputs"]
    if gitprim.resolve_commit(str(repo), inputs["patch_ref"]) != inputs["patch_sha"]:
        raise StaleProposalError("patch ref moved after proposal creation")
    if (
        gitprim.resolve_commit(str(repo), inputs["custom_ref"])
        != inputs["custom_head_sha"]
    ):
        raise StaleProposalError("custom ref moved after proposal creation")
    if registration_state_digest(registration) != inputs["registration_state_digest"]:
        raise StaleProposalError("registration inputs changed after proposal creation")
    _assert_proposal_is_derivable(repo, registration, proposal)

    writes: dict[str, bytes] = {
        "commit-inventory.yaml": _yaml_bytes(
            proposal["generated"]["commit_inventory"]
        ),
        "current-diff-paths.txt": "".join(
            f"{path}\n" for path in proposal["generated"]["current_diff_paths"]
        ).encode("utf-8"),
    }
    for change in proposal["changes"]:
        writes[change["manifest_path"]] = _yaml_bytes(change["after_manifest"])
    if proposal.get("registry_after") is not None:
        registry_module.parse_registry(proposal["registry_after"])
        writes["customization-registry.yaml"] = _yaml_bytes(
            proposal["registry_after"]
        )

    targets = {
        relative: _safe_target(registration, relative)
        for relative in sorted(writes)
    }
    lock_path = registration / ".registration-apply.lock"
    try:
        lock_descriptor = os.open(
            lock_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except FileExistsError as exc:
        raise ApplyLockError(
            f"registration apply lock exists: {lock_path}. Read it to identify "
            "the owning run before removing it."
        ) from exc
    try:
        with os.fdopen(lock_descriptor, "w", encoding="utf-8") as lock:
            # A killed process cannot clean this up, so record who to ask.
            lock.write(
                _yaml_bytes(
                    {
                        "proposal_digest": digest,
                        "pid": os.getpid(),
                        "host": socket.gethostname(),
                        "started_at": _utc_now(),
                        "registration": registration.name,
                    }
                ).decode("utf-8")
            )
            lock.flush()
            os.fsync(lock.fileno())
        # Read the current bytes only once the lock is held, so a rollback
        # cannot restore content another writer replaced in the meantime.
        originals = {
            relative: target.read_bytes() if target.exists() else None
            for relative, target in targets.items()
        }
        if gitprim.worktree_is_dirty(str(repo)):
            raise StaleProposalError(
                "product repository changed before apply lock was acquired"
            )
        if (
            gitprim.resolve_commit(str(repo), inputs["patch_ref"])
            != inputs["patch_sha"]
            or gitprim.resolve_commit(str(repo), inputs["custom_ref"])
            != inputs["custom_head_sha"]
        ):
            raise StaleProposalError(
                "a pinned Git ref changed before apply lock was acquired"
            )
        if (
            registration_state_digest(registration)
            != inputs["registration_state_digest"]
        ):
            raise StaleProposalError(
                "registration inputs changed before apply lock was acquired"
            )
        written: list[str] = []
        try:
            for relative, target in targets.items():
                _atomic_write(target, writes[relative])
                written.append(relative)
        except BaseException:
            for relative in reversed(written):
                original = originals[relative]
                target = targets[relative]
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    _atomic_write(target, original)
            raise
    finally:
        lock_path.unlink(missing_ok=True)

    return {
        "schema_version": 1,
        "status": "APPLIED",
        "proposal_digest": digest,
        "approved_by": approval["approved_by"],
        "patch_sha": inputs["patch_sha"],
        "custom_head_sha": inputs["custom_head_sha"],
        "written_files": sorted(writes),
    }
