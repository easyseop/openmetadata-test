"""Version-independent initial BANK-OM registration proposal and apply.

Git supplies commit SHAs and changed paths.  A reviewed YAML input supplies
business decisions such as titles, owners, required paths, and Contracts.
The planner never writes the active registration directory.  Apply accepts
only the exact approved proposal and unchanged Git/input state.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

import jsonschema
import yaml

from acgh import contracts
from acgh import gitprim
from acgh import layout as layout_module
from acgh import manifest as manifest_module
from acgh import registry as registry_module
from acgh import shared_code
from acgh import verdict


_SCHEMA_ROOT = Path(__file__).parent / "schema"
_INPUT_SCHEMA = "initial-registration-input.schema.json"
_APPROVAL_SCHEMA = "registration-approval.schema.json"
_GENERATED_ROOT_FILES = {
    "customization-registry.yaml",
    "contracts.yaml",
    "source-diff-paths.txt",
    "source-snapshot-path-owners.yaml",
    "shared-path-owners.yaml",
}


class InitialRegistrationError(ValueError):
    """Initial registration inputs cannot produce a trustworthy proposal."""


class StaleInitialRegistrationError(InitialRegistrationError):
    """A proposal input changed after human review."""


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

        raise InitialRegistrationError(
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
        raise InitialRegistrationError(f"cannot read {label}: {exc}") from exc
    if not isinstance(data, dict):
        raise InitialRegistrationError(f"{label} is not a mapping")
    return data


def _yaml_bytes(data: dict) -> bytes:
    return yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, width=1000
    ).encode("utf-8")


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _file_digest(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _registration_digest(registration: Path) -> str:
    """Bind every current registration file before initial apply."""
    payload: dict[str, str] = {}
    for path in sorted(registration.rglob("*")):
        if path.name == ".initial-registration-apply.lock":
            continue
        if path.is_symlink():
            raise InitialRegistrationError(f"registration contains symlink: {path}")
        if path.is_file():
            payload[path.relative_to(registration).as_posix()] = _file_digest(path)
    return verdict.canonical_digest(payload)


def _safe_relative(relative: str) -> str:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise InitialRegistrationError(f"unsafe generated path: {relative}")
    if relative in _GENERATED_ROOT_FILES:
        return relative
    if (
        len(path.parts) == 2
        and path.parts[0] == "manifests"
        and path.parts[1].startswith("BANK-OM-")
        and path.suffix == ".yaml"
    ):
        return relative
    raise InitialRegistrationError(f"forbidden generated path: {relative}")


def _metadata_maps(metadata: dict) -> tuple[dict[str, dict], dict[str, dict]]:
    customizations: dict[str, dict] = {}
    for item in metadata["customizations"]:
        customization_id = item["customization_id"]
        if customization_id in customizations:
            raise InitialRegistrationError(
                f"duplicate customization input: {customization_id}"
            )
        customizations[customization_id] = item

    contract_map: dict[str, dict] = {}
    for item in metadata["contracts"]:
        contract_id = item["id"]
        if contract_id in contract_map:
            raise InitialRegistrationError(f"duplicate contract input: {contract_id}")
        contract_map[contract_id] = item

    known_ids = set(customizations)
    for contract_id, item in contract_map.items():
        unknown = sorted(set(item["customization_ids"]) - known_ids)
        if unknown:
            raise InitialRegistrationError(
                f"{contract_id} references unknown customization IDs: {unknown}"
            )
    for customization_id, item in customizations.items():
        unknown_contracts = sorted(set(item["contracts"]) - set(contract_map))
        if unknown_contracts:
            raise InitialRegistrationError(
                f"{customization_id} references unknown contracts: {unknown_contracts}"
            )
        for contract_id in item["contracts"]:
            if customization_id not in contract_map[contract_id]["customization_ids"]:
                raise InitialRegistrationError(
                    f"{contract_id} does not link back to {customization_id}"
                )
        unknown_dependencies = sorted(
            set(item.get("depends_on", [])) - known_ids
        )
        if unknown_dependencies:
            raise InitialRegistrationError(
                f"{customization_id} depends on unknown IDs: {unknown_dependencies}"
            )
        if customization_id in item.get("depends_on", []):
            raise InitialRegistrationError(
                f"{customization_id} cannot depend on itself"
            )
    return customizations, contract_map


def _git_facts(
    repo: Path,
    official_sha: str,
    custom_sha: str,
    known_ids: set[str],
) -> tuple[dict[str, list[str]], dict[str, list[dict]], list[str]]:
    changed_by_id: dict[str, set[str]] = defaultdict(set)
    commits_by_id: dict[str, list[dict]] = defaultdict(list)
    for commit in gitprim.commits(str(repo), official_sha, custom_sha):
        if commit.is_merge:
            raise InitialRegistrationError(
                f"merge commit is not allowed in initial ID series: {commit.sha}"
            )
        ids = [value.strip() for value in commit.customization_ids if value.strip()]
        if len(ids) != 1:
            raise InitialRegistrationError(
                f"{commit.sha}: expected exactly one Customization-ID, got {ids}"
            )
        customization_id = ids[0]
        if customization_id not in known_ids:
            raise InitialRegistrationError(
                f"{commit.sha}: unregistered Customization-ID {customization_id}"
            )
        paths = sorted(set(gitprim.changed_paths(str(repo), commit.sha)))
        if not paths:
            raise InitialRegistrationError(
                f"{commit.sha}: customization commit has no changed paths"
            )
        changed_by_id[customization_id].update(paths)
        commits_by_id[customization_id].append(
            {"sha": commit.sha, "subject": commit.subject, "changed_paths": paths}
        )

    if not commits_by_id:
        raise InitialRegistrationError("official..custom range has no BANK-OM commits")
    unused = sorted(known_ids - set(commits_by_id))
    if unused:
        raise InitialRegistrationError(
            f"input has BANK-OM IDs with no commit: {unused}"
        )

    net_paths = sorted(
        set(gitprim.net_changed_paths(str(repo), official_sha, custom_sha))
    )
    touched_paths = set().union(*changed_by_id.values())
    reverted = sorted(touched_paths - set(net_paths))
    if reverted:
        raise InitialRegistrationError(
            f"BANK-OM paths have no final code difference: {reverted}"
        )
    unowned = sorted(set(net_paths) - touched_paths)
    if unowned:
        raise InitialRegistrationError(
            f"final custom paths have no BANK-OM commit owner: {unowned}"
        )
    return (
        {key: sorted(value) for key, value in changed_by_id.items()},
        dict(commits_by_id),
        net_paths,
    )


def _check_existing_mapping(path: Path, expected: dict, label: str) -> None:
    if not path.exists():
        return
    current = _load_yaml(path, label)
    if current != expected:
        raise InitialRegistrationError(
            f"{label} differs from Git-derived ownership: {path}"
        )


def build_plan(
    repo: Path,
    registration: Path,
    metadata_path: Path,
    *,
    official_ref: str,
    custom_ref: str,
    product_version: str,
) -> tuple[dict, dict[str, bytes]]:
    repo = repo.resolve(strict=True)
    registration = registration.resolve(strict=True)
    metadata_path = metadata_path.resolve(strict=True)
    if not product_version.strip():
        raise InitialRegistrationError("product version is blank")

    metadata = _validate(
        _load_yaml(metadata_path, "initial registration input"),
        _INPUT_SCHEMA,
        "initial registration input",
    )
    customizations, _ = _metadata_maps(metadata)
    official_sha = gitprim.resolve_commit(str(repo), official_ref)
    custom_sha = gitprim.resolve_commit(str(repo), custom_ref)
    changed_by_id, commits_by_id, net_paths = _git_facts(
        repo, official_sha, custom_sha, set(customizations)
    )

    layout_path = registration / "repository-layout.yaml"
    zones_path = registration / "sensitive-zones.yaml"
    if not layout_path.is_file() or not zones_path.is_file():
        raise InitialRegistrationError(
            "repository-layout.yaml and sensitive-zones.yaml must exist before plan"
        )
    layout = layout_module.load_layout(layout_path)
    if layout.upstream_base_sha != official_sha:
        raise InitialRegistrationError(
            "repository-layout upstream_base_sha does not match official ref"
        )

    official_paths = set(gitprim.list_tree_recursive(str(repo), official_sha))
    contracts_data = {
        "schema_version": 1,
        "contracts": copy.deepcopy(metadata["contracts"]),
    }
    catalog = contracts.parse_catalog(contracts_data)
    manifests: dict[str, dict] = {}
    entries: list[dict] = []
    owners: dict[str, list[str]] = defaultdict(list)

    for customization_id in sorted(customizations):
        item = customizations[customization_id]
        actual = changed_by_id[customization_id]
        required = sorted(set(item["required_changed_paths"]))
        missing_required = sorted(set(required) - set(actual))
        if missing_required:
            raise InitialRegistrationError(
                f"{customization_id} required paths are not changed by its commits: "
                f"{missing_required}"
            )
        series_allowed = bool(item.get("series_allowed", False))
        if len(commits_by_id[customization_id]) > 1 and not series_allowed:
            raise InitialRegistrationError(
                f"{customization_id} has multiple commits but series_allowed is false"
            )
        watch_paths = sorted(
            (set(actual) & official_paths)
            | set(item.get("watch_dependencies", []))
        )
        manifest = {
            "schema_version": 2,
            "customization_id": customization_id,
            "status": "active",
            "kind": item["kind"],
            "title": item["title"],
            "implementation": {
                "changed_paths": actual,
                "required_changed_paths": required,
            },
            "upgrade_watch": {"paths": watch_paths},
            "assurance": {
                "contracts": sorted(item["contracts"]),
                "direct_tests": sorted(item.get("direct_tests", [])),
            },
            "series": {
                "allowed": series_allowed,
                "depends_on": sorted(item.get("depends_on", [])),
            },
        }
        manifest_module.validate_manifest(manifest, layout)
        contracts.effective_tests(manifest, catalog)
        manifests[customization_id] = manifest
        entries.append(
            {
                "customization_id": customization_id,
                "title": item["title"],
                "owner": item["owner"],
                "owner_status": item["owner_status"],
                "status": "active",
                "criticality": item["criticality"],
                "manifest": f"manifests/{customization_id}.yaml",
                "contracts": sorted(item["contracts"]),
                "provenance": item["provenance"],
            }
        )
        for path in actual:
            owners[path].append(customization_id)

    owner_map = {
        path: sorted(set(values)) for path, values in sorted(owners.items())
    }
    shared_map = {
        path: values for path, values in owner_map.items() if len(values) > 1
    }
    _check_existing_mapping(
        registration / "source-snapshot-path-owners.yaml",
        owner_map,
        "source snapshot path owners",
    )
    _check_existing_mapping(
        registration / "shared-path-owners.yaml",
        shared_map,
        "shared path owners",
    )

    source_input = metadata["source"]
    source = {
        "repository": source_input["repository"],
        "snapshot_sha": custom_sha,
        "upstream_repository": source_input["upstream_repository"],
        "upstream_tag": source_input["upstream_tag"],
        "upstream_sha": official_sha,
        "changed_path_count": len(net_paths),
        "ancestry_preserved": gitprim.is_ancestor(
            str(repo), official_sha, custom_sha
        ),
        "diff_inventory": "source-diff-paths.txt",
        "unregistered_findings": copy.deepcopy(
            source_input.get("unregistered_findings", [])
        ),
        "limitations": list(source_input.get("limitations", [])),
    }
    if source_input.get("use_shared_code_definitions", False):
        definitions = registration / "shared-code-definitions.yaml"
        if not definitions.is_file():
            raise InitialRegistrationError(
                "use_shared_code_definitions is true but shared-code-definitions.yaml "
                "is missing"
            )
        shared_code.load_catalog(definitions)
        source["shared_code_definitions"] = "shared-code-definitions.yaml"

    registry_data = {
        "schema_version": 1,
        "source": source,
        "entries": entries,
    }
    registry = registry_module.parse_registry(registry_data)
    registry_module.validate_references(registry, manifests, catalog)

    generated: dict[str, bytes] = {
        "customization-registry.yaml": _yaml_bytes(registry_data),
        "contracts.yaml": _yaml_bytes(contracts_data),
        "source-diff-paths.txt": "".join(
            f"{path}\n" for path in net_paths
        ).encode("utf-8"),
        "source-snapshot-path-owners.yaml": _yaml_bytes(owner_map),
        "shared-path-owners.yaml": _yaml_bytes(shared_map),
    }
    for customization_id, manifest in manifests.items():
        generated[f"manifests/{customization_id}.yaml"] = _yaml_bytes(manifest)

    proposal = {
        "schema_version": 1,
        "status": "REVIEW_REQUIRED",
        "apply_ready": True,
        "inputs": {
            "repository": str(repo),
            "registration": str(registration),
            "metadata_path": str(metadata_path),
            "metadata_digest": _file_digest(metadata_path),
            "registration_digest": _registration_digest(registration),
            "official_ref": official_ref,
            "official_sha": official_sha,
            "custom_ref": custom_ref,
            "custom_sha": custom_sha,
            "product_version": product_version,
        },
        "facts": {
            "customization_count": len(customizations),
            "commit_count": sum(len(value) for value in commits_by_id.values()),
            "changed_path_count": len(net_paths),
            "shared_path_count": len(shared_map),
            "commits_by_id": commits_by_id,
        },
        "generated_files": {
            relative: f"sha256:{_sha256_bytes(content)}"
            for relative, content in sorted(generated.items())
        },
        "review_required": [
            {
                "finding_id": "REVIEW-0001",
                "code": "INITIAL_REGISTRATION_APPROVAL",
                "question": (
                    "생성된 Manifest·Registry·Contract와 경로 소유정보를 "
                    "최초 등록자료로 승인합니까?"
                ),
            }
        ],
    }
    return proposal, generated


def proposal_digest(proposal: dict) -> str:
    return verdict.canonical_digest(copy.deepcopy(proposal))


def write_plan(output: Path, proposal: dict, generated: dict[str, bytes]) -> str:
    output = output.resolve(strict=False)
    if output.exists():
        raise InitialRegistrationError(f"proposal output already exists: {output}")
    output.mkdir(parents=True)
    proposed = output / "proposed-registration"
    proposed.mkdir()
    for relative, content in sorted(generated.items()):
        target = proposed / _safe_relative(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    digest = proposal_digest(proposal)
    (output / "proposal.yaml").write_bytes(_yaml_bytes(proposal))
    (output / "proposal-digest.txt").write_text(digest + "\n", encoding="utf-8")
    (output / "summary.md").write_text(
        "\n".join(
            [
                "# 최초 등록 생성 제안",
                "",
                f"- 버전: `{proposal['inputs']['product_version']}`",
                f"- BANK-OM ID: {proposal['facts']['customization_count']}개",
                f"- commit: {proposal['facts']['commit_count']}개",
                f"- 변경 경로: {proposal['facts']['changed_path_count']}개",
                f"- 공용 경로: {proposal['facts']['shared_path_count']}개",
                f"- 제안 digest: `{digest}`",
                "",
                "활성 등록 폴더는 아직 수정하지 않았습니다.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return digest


def load_proposal(path: Path) -> dict:
    proposal = _load_yaml(path, "initial registration proposal")
    required = {
        "schema_version", "status", "apply_ready", "inputs", "facts",
        "generated_files", "review_required",
    }
    if proposal.get("schema_version") != 1 or not required.issubset(proposal):
        raise InitialRegistrationError("initial registration proposal is incomplete")
    for relative, digest in proposal["generated_files"].items():
        _safe_relative(relative)
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            raise InitialRegistrationError(
                f"invalid generated file digest: {relative}"
            )
    return proposal


def approval_template(proposal: dict) -> dict:
    return {
        "schema_version": 1,
        "proposal_digest": proposal_digest(proposal),
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


def write_approval_template(proposal_path: Path, output: Path) -> None:
    if output.exists():
        raise InitialRegistrationError(f"approval output already exists: {output}")
    proposal = load_proposal(proposal_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_yaml_bytes(approval_template(proposal)))


def _load_approval(path: Path) -> dict:
    return _validate(
        _load_yaml(path, "initial registration approval"),
        _APPROVAL_SCHEMA,
        "initial registration approval",
    )


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


def apply_plan(
    repo: Path,
    registration: Path,
    *,
    proposal_path: Path,
    approval_path: Path,
) -> dict:
    repo = repo.resolve(strict=True)
    registration = registration.resolve(strict=True)
    proposal_path = proposal_path.resolve(strict=True)
    proposal = load_proposal(proposal_path)
    approval = _load_approval(approval_path.resolve(strict=True))
    digest = proposal_digest(proposal)
    if approval["proposal_digest"] != digest:
        raise StaleInitialRegistrationError(
            "approval digest does not match initial registration proposal"
        )
    expected_findings = {
        item["finding_id"] for item in proposal["review_required"]
    }
    actual_findings = {item["finding_id"] for item in approval["decisions"]}
    if expected_findings != actual_findings:
        raise InitialRegistrationError(
            "approval decisions do not cover the proposal review items"
        )
    if approval["approved_by"] == "REPLACE_WITH_APPROVER_ID":
        raise InitialRegistrationError("approval still contains placeholder approver")
    if any(
        item["reason"] == "REPLACE_WITH_REVIEW_REASON"
        for item in approval["decisions"]
    ):
        raise InitialRegistrationError("approval still contains placeholder reason")

    inputs = proposal["inputs"]
    if Path(inputs["registration"]).resolve() != registration:
        raise StaleInitialRegistrationError("proposal registration path changed")
    metadata_path = Path(inputs["metadata_path"])
    try:
        metadata_path = metadata_path.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise StaleInitialRegistrationError(
            "initial registration input is missing"
        ) from exc
    if _file_digest(metadata_path) != inputs["metadata_digest"]:
        raise StaleInitialRegistrationError(
            "initial registration input changed after proposal creation"
        )
    if gitprim.resolve_commit(str(repo), inputs["official_ref"]) != inputs["official_sha"]:
        raise StaleInitialRegistrationError("official ref moved after proposal creation")
    if gitprim.resolve_commit(str(repo), inputs["custom_ref"]) != inputs["custom_sha"]:
        raise StaleInitialRegistrationError("custom ref moved after proposal creation")
    if _registration_digest(registration) != inputs["registration_digest"]:
        raise StaleInitialRegistrationError(
            "registration files changed after proposal creation"
        )

    proposed_root = proposal_path.parent / "proposed-registration"
    writes: dict[str, bytes] = {}
    for relative, expected_digest in sorted(proposal["generated_files"].items()):
        source = proposed_root / _safe_relative(relative)
        if not source.is_file() or source.is_symlink():
            raise StaleInitialRegistrationError(
                f"proposed registration file is missing: {relative}"
            )
        content = source.read_bytes()
        if f"sha256:{_sha256_bytes(content)}" != expected_digest:
            raise StaleInitialRegistrationError(
                f"proposed registration file changed: {relative}"
            )
        writes[relative] = content

    targets = {
        relative: registration / _safe_relative(relative)
        for relative in writes
    }
    for target in targets.values():
        target.resolve(strict=False).relative_to(registration)
        if target.is_symlink() or target.parent.is_symlink():
            raise InitialRegistrationError(f"target uses symlink: {target}")
    originals = {
        relative: target.read_bytes() if target.exists() else None
        for relative, target in targets.items()
    }
    lock_path = registration / ".initial-registration-apply.lock"
    try:
        lock_descriptor = os.open(
            lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
        )
    except FileExistsError as exc:
        raise InitialRegistrationError(
            f"initial registration apply lock exists: {lock_path}"
        ) from exc
    try:
        with os.fdopen(lock_descriptor, "w", encoding="utf-8") as lock:
            lock.write(digest + "\n")
            lock.flush()
            os.fsync(lock.fileno())
        for relative in sorted(writes):
            _atomic_write(targets[relative], writes[relative])
    except BaseException:
        for relative, original in originals.items():
            target = targets[relative]
            if original is None:
                try:
                    target.unlink()
                except FileNotFoundError:
                    pass
            else:
                _atomic_write(target, original)
        raise
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass

    return {
        "status": "APPLIED",
        "proposal_digest": digest,
        "approved_by": approval["approved_by"],
        "official_sha": inputs["official_sha"],
        "custom_sha": inputs["custom_sha"],
        "written_files": sorted(writes),
    }
