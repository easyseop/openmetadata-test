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
import re
import tempfile
from collections import defaultdict
from datetime import datetime
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
_RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class InitialRegistrationError(ValueError):
    """Initial registration inputs cannot produce a trustworthy proposal."""


class ApprovalValidationError(InitialRegistrationError):
    """An approval file identifies exactly what the operator must correct."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        field: str,
        message_ko: str,
        next_action: str,
        current_value: object | None = None,
        issues: list[dict[str, object]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.field = field
        self.message_ko = message_ko
        self.next_action = next_action
        self.current_value = current_value
        self.issues = issues or []

    def as_result(self) -> dict[str, object]:
        result: dict[str, object] = {
            "status": "ANALYSIS_ERROR",
            "code": self.code,
            "field": self.field,
            "message": str(self),
            "message_ko": self.message_ko,
            "next_action": self.next_action,
        }
        if self.current_value is not None:
            result["current_value"] = self.current_value
        if self.issues:
            result["issues"] = self.issues
        return result


class BlockedInitialRegistrationError(InitialRegistrationError):
    """A valid proposal is intentionally blocked until its inputs are fixed."""


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
    return customizations, contract_map


def _input_blocking_findings(
    customizations: dict[str, dict],
    contract_map: dict[str, dict],
) -> list[dict]:
    """Find incomplete human inputs that must block approval and apply."""
    findings: list[dict] = []

    def add(code: str, customization_id: str, message: str, next_action: str) -> None:
        findings.append(
            {
                "finding_id": f"BLOCK-{len(findings) + 1:04d}",
                "code": code,
                "customization_id": customization_id,
                "message": message,
                "next_action": next_action,
            }
        )

    known_ids = set(customizations)
    dependency_graph: dict[str, list[str]] = {}
    for customization_id, item in sorted(customizations.items()):
        owner = str(item.get("owner", "")).strip()
        if (
            not owner
            or owner == "UNASSIGNED"
            or item.get("owner_status") != "assigned"
        ):
            add(
                "OWNER_NOT_ASSIGNED",
                customization_id,
                f"{customization_id}의 운영 담당자가 지정되지 않았습니다.",
                (
                    "initial-registration-input.yaml에서 owner를 실제 담당자로 "
                    "바꾸고 owner_status를 assigned로 설정합니다."
                ),
            )

        if not item.get("required_changed_paths", []):
            add(
                "REQUIRED_PATHS_MISSING",
                customization_id,
                f"{customization_id}의 필수 변경 경로가 비어 있습니다.",
                (
                    "initial-registration-input.yaml의 required_changed_paths에 "
                    "기능 유지에 반드시 필요한 실제 코드 경로를 작성합니다."
                ),
            )

        contract_ids = item.get("contracts", [])
        if not contract_ids:
            add(
                "CONTRACT_MISSING",
                customization_id,
                f"{customization_id}에 연결된 Contract가 없습니다.",
                (
                    "initial-registration-input.yaml에 업무 정상 조건과 필수 test를 "
                    "담은 Contract를 작성하고 해당 ID와 연결합니다."
                ),
            )
        for contract_id in contract_ids:
            contract = contract_map.get(contract_id)
            if contract is None:
                continue
            invariant = str(contract.get("invariant", "")).strip()
            required_tests = contract.get("required_tests", [])
            incomplete = (
                not invariant
                or invariant.startswith("TODO:")
                or not required_tests
                or any(
                    str(value).strip().startswith("TODO:")
                    for value in required_tests
                )
            )
            if incomplete:
                add(
                    "CONTRACT_INCOMPLETE",
                    customization_id,
                    f"{contract_id}에 미작성 정상 조건 또는 필수 test가 있습니다.",
                    (
                        "initial-registration-input.yaml에서 Contract의 invariant와 "
                        "required_tests를 실제 값으로 작성합니다."
                    ),
                )

        dependencies = list(dict.fromkeys(item.get("depends_on", [])))
        dependency_graph[customization_id] = dependencies
        for dependency in dependencies:
            if dependency not in known_ids:
                add(
                    "UNKNOWN_DEPENDENCY",
                    customization_id,
                    f"{customization_id}가 등록되지 않은 {dependency}에 의존합니다.",
                    (
                        "depends_on에서 잘못된 ID를 제거하거나 선행 BANK-OM ID를 "
                        "같은 최초 등록 입력에 추가합니다."
                    ),
                )
            elif dependency == customization_id:
                add(
                    "SELF_DEPENDENCY",
                    customization_id,
                    f"{customization_id}가 자기 자신을 depends_on으로 지정했습니다.",
                    "depends_on에서 자기 자신의 BANK-OM ID를 제거합니다.",
                )

    state = {customization_id: 0 for customization_id in known_ids}
    stack: list[str] = []
    cycle_reported = False

    def visit(customization_id: str) -> None:
        nonlocal cycle_reported
        if cycle_reported:
            return
        state[customization_id] = 1
        stack.append(customization_id)
        for dependency in dependency_graph.get(customization_id, []):
            if dependency not in state or dependency == customization_id:
                continue
            if state[dependency] == 0:
                visit(dependency)
            elif state[dependency] == 1:
                start = stack.index(dependency)
                cycle = stack[start:] + [dependency]
                add(
                    "DEPENDENCY_CYCLE",
                    customization_id,
                    f"depends_on 순환 관계가 있습니다: {' -> '.join(cycle)}",
                    "순환이 없어지도록 depends_on 관계를 수정합니다.",
                )
                cycle_reported = True
                break
        stack.pop()
        state[customization_id] = 2

    for customization_id in sorted(known_ids):
        if state[customization_id] == 0:
            visit(customization_id)

    return findings


def build_input_template(
    repo: Path,
    *,
    official_ref: str,
    custom_ref: str,
    repository: str,
    upstream_repository: str,
    upstream_tag: str,
) -> dict:
    """Create a reviewable business-input draft from the BANK-OM commit series.

    Git can discover IDs, subjects, and touched paths.  It cannot decide the
    final owner, criticality, required-path subset, or business Contract, so
    those values remain explicit review placeholders in the generated YAML.
    """
    repo = repo.resolve(strict=True)
    official_sha = gitprim.resolve_commit(str(repo), official_ref)
    custom_sha = gitprim.resolve_commit(str(repo), custom_ref)
    discovered: dict[str, dict[str, object]] = {}

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
        if not customization_id.startswith("BANK-OM-"):
            raise InitialRegistrationError(
                f"{commit.sha}: invalid Customization-ID {customization_id}"
            )
        item = discovered.setdefault(
            customization_id,
            {"subjects": [], "paths": set()},
        )
        item["subjects"].append(commit.subject)
        item["paths"].update(gitprim.changed_paths(str(repo), commit.sha))

    if not discovered:
        raise InitialRegistrationError("official..custom range has no BANK-OM commits")

    customizations: list[dict] = []
    contracts: list[dict] = []
    for customization_id in sorted(discovered):
        item = discovered[customization_id]
        contract_id = f"CONTRACT-{customization_id.removeprefix('BANK-OM-')}-DRAFT"
        subjects = list(dict.fromkeys(item["subjects"]))
        customizations.append(
            {
                "customization_id": customization_id,
                "title": subjects[-1] if subjects else f"{customization_id} title TODO",
                "owner": "UNASSIGNED",
                "owner_status": "pending",
                "criticality": "medium",
                "kind": "core-patch",
                "provenance": "source-snapshot",
                "required_changed_paths": sorted(item["paths"]),
                "contracts": [contract_id],
                "series_allowed": len(item["subjects"]) > 1,
            }
        )
        contracts.append(
            {
                "id": contract_id,
                "title": f"{customization_id} Contract TODO",
                "invariant": "TODO: 이 기능이 정상이라고 판단할 업무 동작을 작성합니다.",
                "required_tests": [
                    "TODO: 위 업무 동작을 확인하는 실제 test 경로를 작성합니다."
                ],
                "customization_ids": [customization_id],
            }
        )

    return {
        "schema_version": 1,
        "source": {
            "repository": repository,
            "upstream_repository": upstream_repository,
            "upstream_tag": upstream_tag,
            "limitations": [
                "자동 생성 초안입니다. 제목·담당자·중요도·필수 경로·Contract를 승인 전에 검토합니다.",
                "required_changed_paths는 해당 ID commit이 수정한 전체 경로입니다. 실제 필수 경로만 남깁니다.",
                "Contract의 TODO 문장을 실제 정상 조건과 test 경로로 바꿉니다.",
            ],
            "unregistered_findings": [],
            "use_shared_code_definitions": True,
        },
        "customizations": customizations,
        "contracts": contracts,
    }


def write_input_template(path: Path, template: dict) -> bool:
    """Write a new input template without overwriting human edits.

    Returns True when the file is created and False when it already exists.
    """
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_yaml_bytes(template))
    return True


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
    customizations, contract_map = _metadata_maps(metadata)
    blocking_findings = _input_blocking_findings(customizations, contract_map)
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
        "status": "BLOCKED" if blocking_findings else "REVIEW_REQUIRED",
        "apply_ready": not blocking_findings,
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
        "input_summary": [
            {
                "customization_id": customization_id,
                "owner": item["owner"],
                "owner_status": item["owner_status"],
                "criticality": item["criticality"],
                "depends_on": sorted(set(item.get("depends_on", []))),
            }
            for customization_id, item in sorted(customizations.items())
        ],
        "blocking_findings": blocking_findings,
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
    summary = [
        "# 최초 등록 생성 제안",
        "",
        f"- 상태: `{proposal['status']}`",
        f"- 반영 가능: `{'yes' if proposal['apply_ready'] else 'no'}`",
        f"- 버전: `{proposal['inputs']['product_version']}`",
        f"- BANK-OM ID: {proposal['facts']['customization_count']}개",
        f"- commit: {proposal['facts']['commit_count']}개",
        f"- 변경 경로: {proposal['facts']['changed_path_count']}개",
        f"- 공용 경로: {proposal['facts']['shared_path_count']}개",
        f"- 제안 digest: `{digest}`",
        "",
        "## 담당자·중요도·의존 관계",
        "",
        "| BANK-OM ID | 담당자 | 담당자 상태 | 중요도 | depends_on |",
        "|---|---|---|---|---|",
    ]
    for item in proposal["input_summary"]:
        dependencies = ", ".join(item["depends_on"]) or "없음"
        summary.append(
            f"| {item['customization_id']} | {item['owner']} | "
            f"{item['owner_status']} | {item['criticality']} | {dependencies} |"
        )
    if proposal.get("blocking_findings"):
        summary.extend(
            [
                "",
                "## 반드시 수정할 항목",
                "",
                "아래 항목을 수정하고 새 실행 ID로 bootstrap-plan을 다시 실행합니다.",
                "",
            ]
        )
        for finding in proposal["blocking_findings"]:
            summary.extend(
                [
                    f"- **{finding['customization_id']} · {finding['code']}**: "
                    f"{finding['message']}",
                    f"  - 다음 조치: {finding['next_action']}",
                ]
            )
    summary.extend(["", "활성 등록 폴더는 아직 수정하지 않았습니다."])
    (output / "summary.md").write_text(
        "\n".join(summary) + "\n",
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
    if not proposal["apply_ready"] or proposal["status"] == "BLOCKED":
        raise BlockedInitialRegistrationError(
            "blocked initial registration proposal cannot create an approval template"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_yaml_bytes(approval_template(proposal)))


def _approval_field_action(field: str) -> str:
    if field == "approved_by":
        return "approved_by에 실제 승인자 이름이나 조직 식별값을 입력합니다."
    if field == "approved_at":
        return (
            "approved_at에 RFC 3339 형식의 승인 시각을 입력합니다. "
            "예: 2026-08-06T10:30:00-07:00"
        )
    if field.endswith(".reason"):
        return "reason에 제안 내용을 확인하고 승인한 근거를 입력합니다."
    if field.startswith("decisions"):
        return "proposal의 모든 REVIEW 항목에 대한 승인 결정을 decisions에 작성합니다."
    if field == "proposal_digest":
        return "proposal에서 생성된 proposal_digest를 임의로 바꾸지 말고 그대로 사용합니다."
    return f"registration-approval.yaml의 {field} 값을 형식에 맞게 수정합니다."


def _approval_schema_issue(error: jsonschema.ValidationError) -> dict[str, object]:
    field = ".".join(str(part) for part in error.absolute_path) or "<root>"
    code = f"APPROVAL_{str(error.validator).upper()}_INVALID"
    current_value: object | None = error.instance
    if not isinstance(current_value, (str, int, float, bool, type(None))):
        current_value = None

    if error.validator == "required":
        missing = sorted(set(error.validator_value) - set(error.instance))
        missing_field = missing[0] if missing else field
        field = missing_field if field == "<root>" else f"{field}.{missing_field}"
        message_ko = f"승인서에 필수 항목 `{field}`이(가) 없습니다."
        current_value = None
    elif error.validator == "format" and error.validator_value == "date-time":
        message_ko = f"`{field}`가 RFC 3339 날짜·시간 형식이 아닙니다."
    elif error.validator == "minLength":
        message_ko = f"`{field}`에 빈 값을 사용할 수 없습니다."
    elif error.validator == "const":
        message_ko = f"`{field}`는 `{error.validator_value}` 값이어야 합니다."
    elif error.validator == "pattern":
        message_ko = f"`{field}`가 허용된 문자열 형식과 다릅니다."
    elif error.validator == "additionalProperties":
        message_ko = f"`{field}`에 허용되지 않은 항목이 있습니다."
    else:
        message_ko = f"`{field}` 값이 승인서 형식과 다릅니다."

    issue: dict[str, object] = {
        "code": code,
        "field": field,
        "message": error.message,
        "message_ko": message_ko,
        "next_action": _approval_field_action(field),
    }
    if current_value is not None:
        issue["current_value"] = current_value
    return issue


def _is_rfc3339_time(value: object) -> bool:
    if not isinstance(value, str) or not _RFC3339_PATTERN.fullmatch(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _load_approval(path: Path) -> dict:
    approval = _load_yaml(path, "initial registration approval")
    issues: list[dict[str, object]] = []
    placeholder_checks = (
        (
            approval.get("approved_by"),
            "REPLACE_WITH_APPROVER_ID",
            "APPROVAL_APPROVER_PLACEHOLDER",
            "approved_by",
            "승인자 항목이 아직 기본 자리표시자입니다.",
        ),
        (
            approval.get("approved_at"),
            "REPLACE_WITH_RFC3339_TIME",
            "APPROVAL_TIME_PLACEHOLDER",
            "approved_at",
            "승인 시각 항목이 아직 기본 자리표시자입니다.",
        ),
    )
    for value, placeholder, code, field, message_ko in placeholder_checks:
        if value == placeholder:
            issues.append(
                {
                    "code": code,
                    "field": field,
                    "current_value": value,
                    "message": f"approval still contains placeholder: {field}",
                    "message_ko": message_ko,
                    "next_action": _approval_field_action(field),
                }
            )

    decisions = approval.get("decisions")
    if isinstance(decisions, list):
        for index, item in enumerate(decisions):
            if isinstance(item, dict) and item.get("reason") == "REPLACE_WITH_REVIEW_REASON":
                field = f"decisions[{index}].reason"
                issues.append(
                    {
                        "code": "APPROVAL_REASON_PLACEHOLDER",
                        "field": field,
                        "current_value": item["reason"],
                        "message": f"approval still contains placeholder: {field}",
                        "message_ko": "승인 근거 항목이 아직 기본 자리표시자입니다.",
                        "next_action": _approval_field_action(field),
                    }
                )

    errors = sorted(
        _validator(_APPROVAL_SCHEMA).iter_errors(approval),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    issue_fields = {str(issue["field"]) for issue in issues}
    for error in errors:
        issue = _approval_schema_issue(error)
        if str(issue["field"]) not in issue_fields:
            issues.append(issue)
            issue_fields.add(str(issue["field"]))
    approved_at = approval.get("approved_at")
    if (
        isinstance(approved_at, str)
        and approved_at != "REPLACE_WITH_RFC3339_TIME"
        and not _is_rfc3339_time(approved_at)
        and "approved_at" not in issue_fields
    ):
        issues.append(
            {
                "code": "APPROVAL_TIME_INVALID",
                "field": "approved_at",
                "current_value": approved_at,
                "message": "approved_at is not an RFC 3339 timestamp",
                "message_ko": "`approved_at`가 RFC 3339 날짜·시간 형식이 아닙니다.",
                "next_action": _approval_field_action("approved_at"),
            }
        )
        issue_fields.add("approved_at")
    if issues:
        first = issues[0]
        raise ApprovalValidationError(
            f"initial registration approval contains {len(issues)} invalid fields",
            code="APPROVAL_INPUT_INVALID",
            field=str(first["field"]),
            message_ko=f"승인서에 수정해야 할 항목이 {len(issues)}개 있습니다.",
            next_action="issues의 각 필드와 수정 방법을 확인해 registration-approval.yaml을 수정합니다.",
            issues=issues,
        )
    return approval


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
    if not proposal["apply_ready"] or proposal["status"] == "BLOCKED":
        raise BlockedInitialRegistrationError(
            "blocked initial registration proposal cannot be applied"
        )
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
        missing = sorted(expected_findings - actual_findings)
        unexpected = sorted(actual_findings - expected_findings)
        raise ApprovalValidationError(
            "approval decisions do not cover the proposal review items",
            code="APPROVAL_DECISION_COVERAGE_MISMATCH",
            field="decisions[].finding_id",
            message_ko="승인서의 검토 항목과 proposal의 검토 항목이 일치하지 않습니다.",
            next_action=(
                "proposal에서 새 승인 양식을 다시 생성하고, "
                "finding_id를 임의로 추가·삭제하지 않습니다. "
                f"누락={missing}, 예상 밖={unexpected}"
            ),
        )

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
