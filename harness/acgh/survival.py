"""T26 — vendor-merge customization survival gate.

This gate answers the vendor-mode question that replay cannot answer:
"after the approved upstream target was merged, does every registered active
customization still have its required source state and business contracts?"

For every active BANK-OM id it proves, from the exact T24 candidate lock:

* a validated manifest exists;
* every required path exists in the candidate tree;
* every required path is still different from the approved upstream target;
* at least one contract is declared and exists in the contract catalog;
* the catalog binds that contract back to the same customization id; and
* the contract resolves to at least one required test.

Missing or stale Git evidence is ``analysis_error``. A trustworthy observation
that a required state/contract is absent is ``block``. This module deliberately
does not claim the tests passed; T14/T60/T62 and runtime gates own that layer.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from acgh import candidate as C
from acgh import contracts
from acgh import gitprim
from acgh import layout as L
from acgh import verdict


@dataclass(frozen=True)
class SurvivalFinding:
    customization_id: str
    code: str
    detail: str


@dataclass(frozen=True)
class CustomizationSurvival:
    customization_id: str
    required_paths: int
    contracts: int
    effective_tests: int


class SurvivalAnalysisError(RuntimeError):
    """The locked candidate could not be inspected deterministically."""


def inspect_survival(
    repo: str,
    lock: C.CandidateLock,
    manifests_by_id: dict,
    catalog: contracts.Catalog,
    *,
    active_ids=None,
) -> tuple[list[CustomizationSurvival], list[SurvivalFinding]]:
    """Inspect required source/contract state for all active customizations."""
    if lock.integration_strategy != C.VENDOR_MERGE:
        raise SurvivalAnalysisError(
            "customization-survival requires integration_strategy=vendor-merge"
        )

    required_objects = {
        "upstream target": lock.upstream.target_sha,
        "candidate": lock.candidate.commit_sha,
    }
    missing = [
        f"{label} {sha}"
        for label, sha in required_objects.items()
        if not gitprim.object_exists(repo, sha)
    ]
    if missing:
        raise SurvivalAnalysisError(
            "required commit object missing: " + "; ".join(missing)
        )

    try:
        C.assert_candidate_binding(repo, lock)
        candidate_paths = set(
            gitprim.list_tree_recursive(repo, lock.candidate.commit_sha)
        )
        changed_from_target = {
            L.normalize_path(path)
            for path in gitprim.net_changed_paths(
                repo, lock.upstream.target_sha, lock.candidate.commit_sha
            )
        }
    except (
        C.CandidateLockError,
        gitprim.GitPrimitiveError,
        subprocess.CalledProcessError,
        OSError,
    ) as exc:
        raise SurvivalAnalysisError(str(exc)) from exc

    ids = sorted(set(active_ids if active_ids is not None else manifests_by_id))
    if not ids:
        raise SurvivalAnalysisError("active customization set is empty")

    survived: list[CustomizationSurvival] = []
    findings: list[SurvivalFinding] = []
    for customization_id in ids:
        manifest = manifests_by_id.get(customization_id)
        if manifest is None:
            findings.append(
                SurvivalFinding(
                    customization_id,
                    "manifest_missing",
                    "active customization has no manifest",
                )
            )
            continue

        required_paths = [
            L.normalize_path(path)
            for path in manifest.get("implementation", {}).get(
                "required_changed_paths", []
            )
        ]
        if not required_paths:
            findings.append(
                SurvivalFinding(
                    customization_id,
                    "required_state_empty",
                    "manifest declares no required_changed_paths",
                )
            )
        for path in required_paths:
            if path not in candidate_paths:
                findings.append(
                    SurvivalFinding(
                        customization_id,
                        "required_path_missing",
                        path,
                    )
                )
            elif path not in changed_from_target:
                findings.append(
                    SurvivalFinding(
                        customization_id,
                        "required_state_not_distinct",
                        f"{path} is identical to approved upstream target",
                    )
                )

        contract_ids = list(manifest.get("assurance", {}).get("contracts", []))
        if not contract_ids:
            findings.append(
                SurvivalFinding(
                    customization_id,
                    "contract_missing",
                    "active customization declares no business contract",
                )
            )

        effective: set[str] = set()
        try:
            effective = contracts.effective_tests(manifest, catalog)
        except contracts.ContractError as exc:
            findings.append(
                SurvivalFinding(
                    customization_id,
                    "contract_invalid",
                    str(exc),
                )
            )

        for contract_id in contract_ids:
            contract = catalog.get(contract_id)
            if contract is None:
                continue
            if customization_id not in contract.customization_ids:
                findings.append(
                    SurvivalFinding(
                        customization_id,
                        "contract_reverse_binding_missing",
                        f"{contract_id} does not list {customization_id}",
                    )
                )
        if contract_ids and not effective:
            findings.append(
                SurvivalFinding(
                    customization_id,
                    "required_tests_empty",
                    "declared contracts resolve to no tests",
                )
            )

        if not any(f.customization_id == customization_id for f in findings):
            survived.append(
                CustomizationSurvival(
                    customization_id=customization_id,
                    required_paths=len(required_paths),
                    contracts=len(contract_ids),
                    effective_tests=len(effective),
                )
            )

    return survived, findings


def check_customization_survival(
    repo: str,
    lock: C.CandidateLock,
    manifests_by_id: dict,
    catalog: contracts.Catalog,
    *,
    active_ids=None,
    name: str = "customization-survival",
) -> verdict.GateResult:
    """Run T26 and return a fail-closed gate result."""
    try:
        survived, findings = inspect_survival(
            repo,
            lock,
            manifests_by_id,
            catalog,
            active_ids=active_ids,
        )
    except SurvivalAnalysisError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"analysis_error: {exc}",)
        )

    if findings:
        return verdict.GateResult(
            name,
            verdict.BLOCK,
            tuple(
                f"{item.customization_id} {item.code}: {item.detail}"
                for item in findings
            ),
        )

    return verdict.GateResult(
        name,
        verdict.PASS,
        tuple(
            f"{item.customization_id}: required_paths={item.required_paths}, "
            f"contracts={item.contracts}, effective_tests={item.effective_tests}"
            for item in survived
        ),
    )
