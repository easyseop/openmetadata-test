"""Versioned shared-code definition migration with human approval binding.

Old registrations are immutable.  A migration creates a new registration only
after every missing definition is either relocated to a verified Candidate path
or positively proven to be provided by the official target.
"""
from __future__ import annotations

import copy
import datetime as datetime_module
import hashlib
import json
import os
import shutil
from pathlib import Path

import yaml

from acgh import binding
from acgh import gitprim
from acgh import layout as layout_module
from acgh import manifest as manifest_module
from acgh import shared_code
from acgh import structural_review
from acgh import verdict
from acgh import zones as zones_module


RELOCATED = "relocated"
ABSORBED = "absorbed_by_upstream"


class MigrationError(ValueError):
    """A definition migration is incomplete, stale, or untrusted."""


def _file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping(path: Path, label: str) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise MigrationError(f"cannot load {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MigrationError(f"{label} must be a mapping")
    return payload


def _tree_sha(repo: str, commit_sha: str) -> str:
    value = gitprim.git(repo, "rev-parse", f"{commit_sha}^{{tree}}").strip()
    if len(value) != 40:
        raise MigrationError(f"candidate tree is not a full SHA: {value!r}")
    return value


def _definition_id(definition: shared_code.Definition) -> str:
    return f"{definition.customization_id}:{definition.path}"


def _definition_digest(definition: shared_code.Definition) -> str:
    return verdict.canonical_digest({
        "path": definition.path,
        "customization_id": definition.customization_id,
        "assertions": list(definition.assertions),
    })


def _functional_evidence(
    path: Path,
    *,
    expected_sha: str,
    expected_role: str,
) -> dict:
    payload = _mapping(path, "functional test evidence")
    required = {
        "evidence_kind": "functional_test",
        "subject_sha": expected_sha,
        "subject_role": expected_role,
        "verdict": "pass",
    }
    for field, expected in required.items():
        if payload.get(field) != expected:
            raise MigrationError(
                f"functional evidence {field} must be {expected!r}, "
                f"got {payload.get(field)!r}"
            )
    if payload.get("absence_only") is True:
        raise MigrationError(
            "absence-only evidence cannot prove that the official target provides behavior"
        )
    for field in ("test_id", "asserts_behavior", "command"):
        if not payload.get(field):
            raise MigrationError(f"functional evidence requires {field}")
    return {
        "path": str(path),
        "digest": _file_digest(path),
        "test_id": payload["test_id"],
        "asserts_behavior": payload["asserts_behavior"],
        "subject_sha": expected_sha,
        "subject_role": expected_role,
        "verdict": "pass",
    }


def _catalog_and_owners(registration: Path):
    catalog_path = registration / "shared-code-definitions.yaml"
    owners_path = registration / "shared-path-owners.yaml"
    catalog = shared_code.load_catalog(catalog_path)
    owners = _mapping(owners_path, "shared path owners")
    shared_code.validate_coverage(catalog, owners)
    return catalog_path, owners_path, catalog, owners


def build_proposal(
    *,
    repo: str,
    source_registration: Path,
    source_version: str,
    target_version: str,
    candidate_ref: str,
    upstream_target_ref: str,
    structural_evidence: dict,
    decisions: dict,
    harness_commit: str,
    harness_digest: str,
) -> dict:
    """Create a Candidate-bound proposal; no approval is inferred."""
    if source_version == target_version:
        raise MigrationError("target registration version must differ from source version")
    candidate_sha = binding.pin(repo, candidate_ref)
    target_sha = binding.pin(repo, upstream_target_ref)
    candidate_tree = _tree_sha(repo, candidate_sha)
    catalog_path, owners_path, catalog, _owners = _catalog_and_owners(
        source_registration
    )
    if not isinstance(decisions, dict):
        raise MigrationError("migration decisions must be a mapping")
    relocation = structural_evidence.get("relocation_review")
    review = structural_evidence.get("structural_review")
    if not isinstance(relocation, dict) or not isinstance(review, dict):
        raise MigrationError(
            "structural evidence requires relocation_review and structural_review"
        )
    if relocation.get("candidate_sha") != candidate_sha:
        raise MigrationError("relocation review candidate differs from requested Candidate")
    refs = review.get("refs", {})
    if refs.get("candidate") != candidate_sha or refs.get("target") != target_sha:
        raise MigrationError("structural review refs differ from migration inputs")
    findings = {
        item.get("definition_id"): item
        for item in relocation.get("findings", [])
        if isinstance(item, dict) and isinstance(item.get("definition_id"), str)
    }
    layout = layout_module.load_layout(source_registration / "repository-layout.yaml")
    manifests = {}
    for path in sorted((source_registration / "manifests").glob("BANK-OM-*.yaml")):
        manifest = manifest_module.load_manifest(path, layout)
        manifests[manifest["customization_id"]] = manifest
    zones = zones_module.load_zones(source_registration / "sensitive-zones.yaml")
    try:
        structural_review.verify_review(repo, review, manifests, zones=zones)
    except structural_review.StructuralReviewError as exc:
        raise MigrationError(str(exc)) from exc
    recomputed_relocation = structural_review.find_relocations(
        repo, candidate_sha, catalog, review["review_surface_paths"]
    )
    recomputed_relocation["applicable"] = True
    if relocation != recomputed_relocation:
        raise MigrationError(
            "relocation review differs from Candidate-bound deterministic recomputation"
        )
    if set(decisions) != set(findings):
        raise MigrationError(
            "every missing definition needs exactly one decision: "
            f"missing={sorted(set(findings) - set(decisions))}, "
            f"extra={sorted(set(decisions) - set(findings))}"
        )
    if not findings:
        raise MigrationError("there are no missing shared definitions to migrate")
    definitions = {_definition_id(item): item for item in catalog.definitions}
    items = []
    for definition_id in sorted(findings):
        finding = findings[definition_id]
        decision = decisions[definition_id]
        if not isinstance(decision, dict):
            raise MigrationError(f"decision {definition_id} must be a mapping")
        definition = definitions.get(definition_id)
        if definition is None:
            raise MigrationError(f"unknown old definition: {definition_id}")
        old_digest = _definition_digest(definition)
        if finding.get("old_definition_digest") != old_digest:
            raise MigrationError(f"stale relocation finding: {definition_id}")
        disposition = decision.get("disposition")
        evidence_path = Path(str(decision.get("functional_evidence", "")))
        if disposition == RELOCATED:
            new_path = decision.get("proposed_new_path")
            eligible = {
                item.get("path"): item
                for item in finding.get("candidates", [])
                if item.get("eligible_for_migration") is True
            }
            if new_path not in eligible:
                raise MigrationError(
                    f"{definition_id}: proposed path is not an eligible relocation candidate"
                )
            evidence = _functional_evidence(
                evidence_path,
                expected_sha=candidate_sha,
                expected_role="candidate",
            )
            candidate_evidence = eligible[new_path]
            proposed_assertions = decision.get("proposed_assertions")
            if candidate_evidence.get("evidence_strength") != "exact_definition":
                if not isinstance(proposed_assertions, list) or not proposed_assertions:
                    raise MigrationError(
                        f"{definition_id}: a partial or symbol relocation requires "
                        "proposed_assertions for the refactored Candidate path"
                    )
            elif proposed_assertions is None:
                proposed_assertions = list(definition.assertions)
            try:
                parsed_proposal = shared_code.parse_catalog({
                    "schema_version": 1,
                    "definitions": [{
                        "path": new_path,
                        "customization_id": definition.customization_id,
                        "assertions": proposed_assertions,
                    }],
                })
            except shared_code.SharedCodeError as exc:
                raise MigrationError(
                    f"{definition_id}: proposed assertions are invalid: {exc}"
                ) from exc
            proposed_definition = parsed_proposal.definitions[0]
            proposed = shared_code.Definition(
                path=new_path,
                customization_id=definition.customization_id,
                assertions=proposed_definition.assertions,
            )
            try:
                text = gitprim.blob_bytes(repo, candidate_sha, new_path).decode("utf-8")
                failures = shared_code._check_definition(text, proposed)
            except (gitprim.GitPrimitiveError, UnicodeError, ValueError) as exc:
                raise MigrationError(
                    f"{definition_id}: cannot verify proposed definition: {exc}"
                ) from exc
            if failures:
                raise MigrationError(
                    f"{definition_id}: proposed definition fails Candidate: {failures}"
                )
            items.append({
                "definition_id": definition_id,
                "customization_id": definition.customization_id,
                "disposition": RELOCATED,
                "supersedes": {
                    "definition_id": definition_id,
                    "definition_digest": old_digest,
                },
                "old_path": definition.path,
                "proposed_new_path": new_path,
                "candidate_blob_digest": candidate_evidence["blob_digest"],
                "candidate_evidence_strength": candidate_evidence["evidence_strength"],
                "assertions": list(proposed_definition.assertions),
                "functional_evidence": evidence,
            })
        elif disposition == ABSORBED:
            evidence = _functional_evidence(
                evidence_path,
                expected_sha=target_sha,
                expected_role="official_target",
            )
            items.append({
                "definition_id": definition_id,
                "customization_id": definition.customization_id,
                "disposition": ABSORBED,
                "supersedes": {
                    "definition_id": definition_id,
                    "definition_digest": old_digest,
                },
                "old_path": definition.path,
                "functional_evidence": evidence,
            })
        else:
            raise MigrationError(
                f"{definition_id}: disposition must be {RELOCATED!r} or {ABSORBED!r}"
            )

    proposal = {
        "schema_version": 1,
        "source_registration_version": source_version,
        "target_registration_version": target_version,
        "source_registration": str(source_registration),
        "candidate": {"commit_sha": candidate_sha, "tree_sha": candidate_tree},
        "upstream_target_sha": target_sha,
        "old_catalog_digest": _file_digest(catalog_path),
        "old_owners_digest": _file_digest(owners_path),
        "structural_review_digest": review.get("review_digest"),
        "harness_commit": harness_commit,
        "harness_digest": harness_digest,
        "items": items,
    }
    proposal["proposal_digest"] = verdict.canonical_digest(proposal)
    return proposal


def approval_template(proposal: dict) -> dict:
    digest = verify_proposal_digest(proposal)
    return {
        "schema_version": 1,
        "proposal_digest": digest,
        "approval_confirmed": False,
        "approver": "",
        "approved_at": "",
        "rationale": "",
        "approval_source": "",
    }


def verify_proposal_digest(proposal: dict) -> str:
    if not isinstance(proposal, dict):
        raise MigrationError("proposal must be a mapping")
    stored = proposal.get("proposal_digest")
    unsigned = {key: value for key, value in proposal.items() if key != "proposal_digest"}
    actual = verdict.canonical_digest(unsigned)
    if stored != actual:
        raise MigrationError(
            f"proposal digest mismatch: stored={stored}, recomputed={actual}"
        )
    return actual


def _verify_approval(approval: dict, proposal_digest: str) -> str:
    if approval.get("proposal_digest") != proposal_digest:
        raise MigrationError("approval is not bound to this proposal digest")
    if approval.get("approval_confirmed") is not True:
        raise MigrationError("approval_confirmed must be true after human review")
    for field in ("approver", "approved_at", "rationale", "approval_source"):
        if not isinstance(approval.get(field), str) or not approval[field].strip():
            raise MigrationError(f"approval requires {field}")
    try:
        approved_at = datetime_module.datetime.fromisoformat(
            approval["approved_at"].replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise MigrationError("approved_at must be an ISO-8601 timestamp") from exc
    if approved_at.tzinfo is None:
        raise MigrationError("approved_at must include a timezone")
    return verdict.canonical_digest(approval)


def _rewrite_registration(
    catalog: shared_code.Catalog,
    owners: dict,
    proposal: dict,
) -> tuple[dict, dict]:
    definitions = {
        _definition_id(item): {
            "path": item.path,
            "customization_id": item.customization_id,
            "assertions": list(item.assertions),
        }
        for item in catalog.definitions
    }
    updated_owners = copy.deepcopy(owners)
    for item in proposal["items"]:
        definition_id = item["definition_id"]
        old = definitions.pop(definition_id, None)
        if old is None:
            raise MigrationError(f"proposal old definition is no longer present: {definition_id}")
        old_path = item["old_path"]
        customization_id = item["customization_id"]
        current = list(updated_owners.get(old_path, []))
        if customization_id not in current:
            raise MigrationError(f"owners no longer contains {definition_id}")
        current.remove(customization_id)
        if current:
            updated_owners[old_path] = current
        else:
            updated_owners.pop(old_path, None)
        if item["disposition"] == RELOCATED:
            new_path = item["proposed_new_path"]
            new_definition_id = f"{customization_id}:{new_path}"
            if new_definition_id in definitions:
                raise MigrationError(f"relocated definition already exists: {new_definition_id}")
            definitions[new_definition_id] = {
                "path": new_path,
                "customization_id": customization_id,
                "assertions": item["assertions"],
            }
            updated_owners.setdefault(new_path, [])
            if customization_id not in updated_owners[new_path]:
                updated_owners[new_path].append(customization_id)
                updated_owners[new_path].sort()
    new_catalog = {
        "schema_version": 1,
        "definitions": sorted(
            definitions.values(),
            key=lambda item: (item["path"], item["customization_id"]),
        ),
    }
    parsed = shared_code.parse_catalog(new_catalog)
    shared_code.validate_coverage(parsed, updated_owners)
    return new_catalog, dict(sorted(updated_owners.items()))


def apply_proposal(
    *,
    repo: str,
    source_registration: Path,
    target_registration: Path,
    proposal: dict,
    approval: dict,
    harness_commit: str,
    harness_digest: str,
) -> dict:
    """Create a new registration atomically; never alter the source version."""
    digest = verify_proposal_digest(proposal)
    approval_digest = _verify_approval(approval, digest)
    if target_registration.exists():
        raise MigrationError(f"target registration already exists: {target_registration}")
    if source_registration.resolve() == target_registration.resolve():
        raise MigrationError("source registration cannot be overwritten in place")
    if proposal.get("harness_commit") != harness_commit:
        raise MigrationError("proposal harness_commit differs from the running verifier")
    if proposal.get("harness_digest") != harness_digest:
        raise MigrationError("proposal harness_digest differs from the running verifier")
    candidate_sha = binding.pin(repo, proposal["candidate"]["commit_sha"])
    if _tree_sha(repo, candidate_sha) != proposal["candidate"]["tree_sha"]:
        raise MigrationError("Candidate tree changed after proposal creation")
    catalog_path, owners_path, catalog, owners = _catalog_and_owners(source_registration)
    if _file_digest(catalog_path) != proposal.get("old_catalog_digest"):
        raise MigrationError("old shared-code definitions changed after proposal creation")
    if _file_digest(owners_path) != proposal.get("old_owners_digest"):
        raise MigrationError("old shared path owners changed after proposal creation")
    for item in proposal["items"]:
        evidence = item["functional_evidence"]
        evidence_path = Path(evidence["path"])
        if _file_digest(evidence_path) != evidence["digest"]:
            raise MigrationError(
                f"functional evidence changed: {item['definition_id']}"
            )
        expected_sha = (
            candidate_sha if item["disposition"] == RELOCATED
            else proposal["upstream_target_sha"]
        )
        expected_role = (
            "candidate" if item["disposition"] == RELOCATED
            else "official_target"
        )
        _functional_evidence(
            evidence_path, expected_sha=expected_sha, expected_role=expected_role
        )
    new_catalog, new_owners = _rewrite_registration(catalog, owners, proposal)
    parsed = shared_code.parse_catalog(new_catalog)
    check = shared_code.check_shared_code_definitions(
        repo, candidate_sha, parsed, new_owners
    )
    if check.verdict != verdict.PASS:
        raise MigrationError(
            "new shared-code definitions do not pass Candidate verification: "
            + "; ".join(check.reasons)
        )

    target_registration.parent.mkdir(parents=True, exist_ok=True)
    temp = target_registration.with_name(
        f".{target_registration.name}.tmp.{os.getpid()}"
    )
    if temp.exists():
        raise MigrationError(f"temporary registration path already exists: {temp}")
    try:
        shutil.copytree(
            source_registration,
            temp,
            ignore=shutil.ignore_patterns("candidate-locks"),
        )
        (temp / "candidate-locks").mkdir()
        (temp / "shared-code-definitions.yaml").write_text(
            yaml.safe_dump(new_catalog, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        (temp / "shared-path-owners.yaml").write_text(
            yaml.safe_dump(new_owners, allow_unicode=True, sort_keys=True),
            encoding="utf-8",
        )
        record = {
            "schema_version": 1,
            "source_registration_version": proposal["source_registration_version"],
            "target_registration_version": proposal["target_registration_version"],
            "proposal_digest": digest,
            "approval_digest": approval_digest,
            "candidate": proposal["candidate"],
            "upstream_target_sha": proposal["upstream_target_sha"],
            "items": [
                {
                    "definition_id": item["definition_id"],
                    "disposition": item["disposition"],
                    "supersedes": item["supersedes"],
                }
                for item in proposal["items"]
            ],
            "registration_state": "definition-migration-draft",
            "next_required_checks": [
                "rebuild version-specific registry and Manifest inputs",
                "run registration validation",
                "prepare and approve a new Candidate lock",
                "rerun shared-code and direct functional tests",
            ],
        }
        (temp / "shared-code-migration-record.yaml").write_text(
            yaml.safe_dump(record, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        os.replace(temp, target_registration)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return {
        "status": "created",
        "target_registration": str(target_registration),
        "proposal_digest": digest,
        "approval_digest": approval_digest,
        "candidate_sha": candidate_sha,
        "shared_definition_count": len(new_catalog["definitions"]),
        "shared_owner_pair_count": sum(len(value) for value in new_owners.values()),
        "registration_state": "definition-migration-draft",
        "next_action": (
            "새 버전 registry·Manifest를 재생성하고 등록 검사를 통과한 뒤에만 "
            "Candidate lock을 준비·승인하십시오."
        ),
    }
