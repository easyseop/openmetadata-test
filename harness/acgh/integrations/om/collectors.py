"""OpenMetadata facts injected into the product-neutral planning core."""

from __future__ import annotations

import re
import os
import subprocess
from pathlib import Path

import yaml

from acgh import gitprim
from acgh.integrations.om.config import CUSTOMIZATION_ID_PATTERN, registration_relative_path
from acgh.integrations.om.doc_sources import collect_document_snapshots, verify_document_snapshots
from acgh.plancore.errors import PlanControlError

_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _version_relation(base: str | None, target: str | None) -> str:
    if base is None or target is None:
        return "not_applicable"
    left = _VERSION.fullmatch(base)
    right = _VERSION.fullmatch(target)
    if left is None or right is None:
        raise PlanControlError(
            "VERSION_FORMAT_INVALID",
            "versions must use major.minor.patch",
            details={"base": base, "target": target},
        )
    a = tuple(int(value) for value in left.groups())
    b = tuple(int(value) for value in right.groups())
    if a == b:
        return "equal"
    if b < a:
        return "reversed"
    if a[:2] == b[:2] and b[2] == a[2] + 1:
        return "adjacent"
    if a[0] == b[0] and b[1] == a[1] + 1 and b[2] == 0:
        return "adjacent"
    return "non_adjacent"


def _registration_metadata(path: Path | None) -> dict:
    if path is None or not path.is_dir():
        return {
            "ids": [],
            "contract_ids": [],
            "test_ids": [],
            "shared_owners": {},
            "source_provenance": {},
        }
    registry = path / "customization-registry.yaml"
    if not registry.is_file():
        return {
            "ids": [],
            "contract_ids": [],
            "test_ids": [],
            "shared_owners": {},
            "source_provenance": {},
        }
    data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
    candidates = data.get("customizations") or data.get("entries") or []
    result: list[str] = []
    if isinstance(candidates, list):
        for item in candidates:
            if isinstance(item, dict):
                value = item.get("id") or item.get("customization_id")
                if isinstance(value, str):
                    result.append(value)
    elif isinstance(candidates, dict):
        result.extend(str(value) for value in candidates)
    contracts_path = path / "contracts.yaml"
    contract_ids: list[str] = []
    test_ids: list[str] = []
    if contracts_path.is_file():
        contracts_data = yaml.safe_load(contracts_path.read_text(encoding="utf-8")) or {}
        for contract in contracts_data.get("contracts") or []:
            if not isinstance(contract, dict):
                continue
            if isinstance(contract.get("id"), str):
                contract_ids.append(contract["id"])
            test_ids.extend(
                value
                for value in contract.get("required_tests") or []
                if isinstance(value, str)
            )
    shared_path = path / "shared-path-owners.yaml"
    shared_owners = {}
    if shared_path.is_file():
        loaded = yaml.safe_load(shared_path.read_text(encoding="utf-8")) or {}
        if isinstance(loaded, dict):
            shared_owners = loaded
    return {
        "ids": result,
        "contract_ids": sorted(set(contract_ids)),
        "test_ids": sorted(set(test_ids)),
        "shared_owners": shared_owners,
        # Historical source SHAs explain how the registration was created. They
        # are intentionally facts, not active candidate locks or block rules.
        "source_provenance": data.get("source")
        if isinstance(data.get("source"), dict)
        else {},
    }


def _materialized_objects(
    repo: str,
    left: str,
    right: str,
    paths: list[str],
) -> list[dict[str, str]]:
    left_entries = gitprim.tree_entries(repo, left)
    right_entries = gitprim.tree_entries(repo, right)
    records: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    environment = os.environ.copy()
    environment["GIT_NO_LAZY_FETCH"] = "1"
    for path in sorted(paths):
        for side, entries in (("base", left_entries), ("target", right_entries)):
            entry = entries.get(path)
            if entry is None or entry.object_type != "blob":
                continue
            probe = subprocess.run(
                ["git", "-C", repo, "cat-file", "-e", entry.object_id],
                env=environment,
                capture_output=True,
                check=False,
            )
            item = {"path": path, "side": side, "object_id": entry.object_id}
            if probe.returncode:
                missing.append(item)
            else:
                records.append(item)
    if missing:
        raise PlanControlError(
            "SOURCE_BLOBS_UNAVAILABLE",
            "required source blobs are not available locally",
            details={"missing_objects": missing},
        )
    return records


class OpenMetadataPlanAdapter:
    """Product-specific request checks and fact collectors."""

    name = "openmetadata"

    def resolve_registration_path(self, request: dict, checker_repo: Path) -> Path | None:
        configured = request.get("registration_path")
        if configured:
            path = Path(configured)
            return path if path.is_absolute() else checker_repo / path
        product_version = request.get("product_version")
        if product_version:
            return checker_repo / registration_relative_path(product_version)
        return None

    def validate_request(self, request: dict) -> dict:
        mode = request["mode"]
        if request.get("customization_id") and not CUSTOMIZATION_ID_PATTERN.fullmatch(
            request["customization_id"]
        ):
            raise PlanControlError(
                "CUSTOMIZATION_ID_INVALID",
                "customization id does not match the configured product policy",
            )
        relation = _version_relation(
            (request.get("versions") or {}).get("base"),
            (request.get("versions") or {}).get("target"),
        )
        if mode == "upgrade" and relation != "adjacent":
            raise PlanControlError(
                "UPGRADE_RELATION_UNSUPPORTED",
                "the first implementation accepts adjacent upgrades only",
                details={"version_relation": relation},
            )
        if mode == "upgrade" and not request.get("deployment_method"):
            raise PlanControlError(
                "DEPLOYMENT_METHOD_REQUIRED",
                "deployment method is required for every upgrade run",
            )
        if mode == "upgrade":
            method = request["deployment_method"]
            covered = any(
                method in (document.get("deployment_methods") or [])
                or "all" in (document.get("deployment_methods") or [])
                for document in request.get("official_documents") or []
            )
            if not covered:
                raise PlanControlError(
                    "DEPLOYMENT_DOCUMENT_MISSING",
                    "official documents do not cover the selected deployment method",
                    details={"deployment_method": method},
                )
        return {"version_relation": relation}

    def catalog_paths(self, checker_repo: Path) -> list[Path]:
        return [
            checker_repo / "harness" / "acgh" / "plancore",
            checker_repo / "harness" / "acgh" / "integrations" / "om",
        ]

    def collect_documents(self, request: dict, run_dir: Path) -> dict:
        return collect_document_snapshots(request, run_dir)

    def verify_documents(self, run_dir: Path, recorded: dict) -> None:
        verify_document_snapshots(run_dir, recorded)

    def collect_facts(
        self,
        request: dict,
        locked_refs: dict[str, str],
        registration_path: Path | None,
        document_sources: dict,
    ) -> list[dict]:
        repo = request["repositories"]["product"]
        mode = request["mode"]
        values: list[tuple[str, str, object]] = []
        for role in sorted(locked_refs):
            commit = locked_refs[role]
            tree = gitprim.git(repo, "rev-parse", f"{commit}^{{tree}}").strip()
            values.append(
                (
                    f"ref-{role}",
                    "ref_identity",
                    {"role": role, "commit_sha": commit, "tree_sha": tree},
                )
            )

        if mode == "initial":
            commits = gitprim.commits(repo, locked_refs["official"], locked_refs["current_custom"])
            values.append(
                (
                    "customization-commits",
                    "commit_inventory",
                    [
                        {
                            "sha": item.sha,
                            "subject": item.subject,
                            "customization_ids": item.customization_ids,
                            "changed_paths": gitprim.changed_paths(repo, item.sha),
                        }
                        for item in commits
                    ],
                )
            )
            net_paths = gitprim.net_changed_paths(
                repo, locked_refs["official"], locked_refs["current_custom"]
            )
            values.append(
                (
                    "net-custom-paths",
                    "changed_paths",
                    net_paths,
                )
            )
            values.append(
                (
                    "net-custom-source-objects",
                    "source_objects",
                    _materialized_objects(
                        repo,
                        locked_refs["official"],
                        locked_refs["current_custom"],
                        net_paths,
                    ),
                )
            )
        elif mode == "change" and request["change_path"] == "post_change_reconcile":
            change_paths = gitprim.net_changed_paths(
                repo, locked_refs["custom_baseline"], locked_refs["candidate"]
            )
            values.append(
                (
                    "observed-change-paths",
                    "changed_paths",
                    change_paths,
                )
            )
            values.append(
                (
                    "observed-change-source-objects",
                    "source_objects",
                    _materialized_objects(
                        repo,
                        locked_refs["custom_baseline"],
                        locked_refs["candidate"],
                        change_paths,
                    ),
                )
            )
        elif mode == "upgrade":
            upgrade_paths = gitprim.net_changed_paths(
                repo, locked_refs["official_base"], locked_refs["official_target"]
            )
            values.append(
                (
                    "official-upgrade-paths",
                    "changed_paths",
                    upgrade_paths,
                )
            )
            values.append(
                (
                    "official-upgrade-source-objects",
                    "source_objects",
                    _materialized_objects(
                        repo,
                        locked_refs["official_base"],
                        locked_refs["official_target"],
                        upgrade_paths,
                    ),
                )
            )
            values.append(
                (
                    "official-documents",
                    "official_document_snapshots",
                    document_sources.get("documents", []),
                )
            )

        registration = _registration_metadata(registration_path)
        registry_ids = registration["ids"]
        values.append(("registered-customizations", "registered_ids", registry_ids))
        values.append(
            (
                "duplicate-registered-customizations",
                "duplicate_ids",
                sorted({value for value in registry_ids if registry_ids.count(value) > 1}),
            )
        )
        values.append(
            ("registered-contracts", "registered_contracts", registration["contract_ids"])
        )
        values.append(("registered-tests", "registered_tests", registration["test_ids"]))
        values.append(("shared-path-owners", "shared_path_owners", registration["shared_owners"]))
        values.append(
            (
                "registration-source-provenance",
                "provenance",
                registration["source_provenance"],
            )
        )
        values.append(
            (
                "owner-status",
                "human_input_status",
                {
                    "owner": request.get("owner"),
                    "unresolved": not bool(request.get("owner")),
                },
            )
        )
        return [
            {
                "fact_id": fact_id,
                "kind": kind,
                "value": value,
                "evidence_ref": "",
            }
            for fact_id, kind, value in values
        ]

    def validate_proposal(
        self,
        request: dict,
        proposal_documents: list[dict],
        discovered_facts: dict,
    ) -> list[str]:
        issues: list[str] = []
        fact_values = {
            item["fact_id"]: item["value"]
            for item in discovered_facts.get("canonical_payload", {}).get("items", [])
        }
        duplicates = fact_values.get("duplicate-registered-customizations") or []
        if duplicates:
            issues.append(f"duplicate registered customization ids: {duplicates}")
        registered_ids = set(fact_values.get("registered-customizations") or [])
        if request.get("mode") == "feature" and request.get("customization_id") in registered_ids:
            issues.append("feature customization id already exists in the registry")
        if request.get("mode") == "change" and request.get("customization_id") not in registered_ids:
            issues.append("change customization id is not registered")

        all_questions: list[object] = []
        blocked = False
        proposal_owners: list[object] = []
        required_test_claims: list[object] = []
        observed_claims_without_refs = False
        unresolved = False
        for document in proposal_documents:
            if document.get("next_step_blocked") is True:
                blocked = True
            questions = document.get("questions") or document.get("unresolved_questions") or []
            if isinstance(questions, list):
                all_questions.extend(questions)
                unresolved = unresolved or any(
                    "owner" in str(question).lower() or "담당" in str(question)
                    for question in questions
                )
            if "owner" in document:
                proposal_owners.append(document["owner"])
            for decision in document.get("decisions") or []:
                if not isinstance(decision, dict):
                    continue
                if decision.get("decision_source") == "observed" and not decision.get("evidence_refs"):
                    observed_claims_without_refs = True
                required_test_claims.extend(decision.get("required_tests") or [])
        if not request.get("owner") and (not unresolved or not blocked):
            issues.append(
                "owner is unresolved; proposal must include an owner question and next_step_blocked=true"
            )
        if not request.get("owner") and any(value not in (None, "", "unresolved") for value in proposal_owners):
            issues.append("proposal filled an owner that was not supplied by a human")
        if observed_claims_without_refs:
            issues.append("observed decisions require machine evidence refs")

        registered_tests = set(fact_values.get("registered-tests") or [])
        for claim in required_test_claims:
            if isinstance(claim, dict):
                test_id = claim.get("id")
                status = claim.get("status")
            else:
                test_id = claim
                status = "existing"
            if status == "existing" and test_id not in registered_tests:
                issues.append(f"test claimed as existing is not registered: {test_id}")
            if isinstance(claim, dict) and claim.get("required") is True and claim.get("result") in {"skip", "skipped", "not_run"}:
                issues.append(f"required test was not executed: {test_id}")

        commit_inventory = fact_values.get("customization-commits") or []
        ambiguous = [
            item for item in commit_inventory if len(item.get("customization_ids") or []) != 1
        ]
        if ambiguous:
            rendered_questions = " ".join(str(value) for value in all_questions)
            if not blocked or not all(
                item.get("sha", "")[:12] in rendered_questions
                or "ID" in rendered_questions
                for item in ambiguous
            ):
                issues.append("ambiguous commit ids require unresolved questions and a STOP")

        changed_paths = set(
            fact_values.get("observed-change-paths")
            or fact_values.get("official-upgrade-paths")
            or []
        )
        shared_owners = fact_values.get("shared-path-owners") or {}
        declared_shared: dict[str, set[str]] = {}
        for document in proposal_documents:
            impacts = document.get("shared_impact") or document.get("shared_impacts") or []
            if isinstance(impacts, list):
                for impact in impacts:
                    if not isinstance(impact, dict) or not isinstance(impact.get("path"), str):
                        continue
                    ids = impact.get("customization_ids") or impact.get("owner_ids") or []
                    declared_shared[impact["path"]] = {str(value) for value in ids}
        for path in sorted(changed_paths & set(shared_owners)):
            expected = {str(value) for value in shared_owners[path]}
            if declared_shared.get(path) != expected:
                issues.append(
                    f"shared path owners are incomplete for {path}: expected {sorted(expected)}"
                )

        findings: list[dict] = []
        checklist_refs: set[str] = set()
        crosscheck_relations: list[str] = []
        pointer_movement = False
        has_shared_delta = False
        for document in proposal_documents:
            for finding in document.get("findings") or []:
                if isinstance(finding, dict):
                    findings.append(finding)
            for item in document.get("operations") or document.get("checklist") or []:
                if isinstance(item, dict):
                    reference = item.get("finding_id") or item.get("source_finding")
                    if isinstance(reference, str):
                        checklist_refs.add(reference)
            for item in document.get("crosschecks") or []:
                if isinstance(item, dict) and isinstance(item.get("relation"), str):
                    crosscheck_relations.append(item["relation"])
            pointer_movement = pointer_movement or bool(document.get("pointer_movements"))
            has_shared_delta = has_shared_delta or "shared_code_definitions_delta" in document
        for finding in findings:
            if finding.get("category") in {"db_migration", "reindex", "configuration"}:
                if finding.get("id") not in checklist_refs:
                    issues.append(
                        f"operational finding is missing from checklist: {finding.get('id')}"
                    )
        allowed_relations = {
            "documented_and_observed",
            "documented_not_located",
            "code_change_not_documented",
            "documented_contradicts_observed",
            "not_applicable",
        }
        for relation in crosscheck_relations:
            if relation not in allowed_relations:
                issues.append(f"unsupported document/code relation: {relation}")
        if pointer_movement and not has_shared_delta:
            issues.append(
                "pointer movement requires a shared code definition delta instead of a feature-loss claim"
            )
        return issues
