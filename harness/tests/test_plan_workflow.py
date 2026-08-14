from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from acgh.integrations.om import OpenMetadataPlanAdapter
from acgh.integrations.om.doc_sources import collect_document_snapshots, verify_document_snapshots
from acgh.plancore.errors import PlanControlError
from acgh.plancore.hook_policy import decide_pre_tool_use
from acgh.plancore.hook_cli import handle_event
from acgh.plancore.markers import (
    bind_run,
    cleanup_pair,
    create_session_marker,
    session_marker_path,
)
from acgh.plancore.preflight import run_preflight
from acgh.plancore.preflight import collect_state
from acgh.plancore.rerun import retry_decision
from acgh.plancore.schema import read_data, validate
from acgh.plancore.validate import run_validation


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _init_repo(path: Path, files: dict[str, str]) -> Path:
    path.mkdir()
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "plan-test@example.invalid")
    _git(path, "config", "user.name", "Plan Test")
    for name, content in files.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    _git(path, "add", "-A")
    _git(path, "commit", "-q", "-m", "initial")
    return path


def _add_commit(repo: Path, name: str, content: str, customization_id: str) -> str:
    target = repo / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(repo, "add", name)
    _git(
        repo,
        "commit",
        "-q",
        "-m",
        f"change {name}",
        "-m",
        f"Customization-ID: {customization_id}",
    )
    return _git(repo, "rev-parse", "HEAD")


def _repos(tmp_path: Path) -> tuple[Path, Path, str, str]:
    product = _init_repo(tmp_path / "product", {"base.txt": "base\n"})
    official = _git(product, "rev-parse", "HEAD")
    custom = _add_commit(product, "feature.txt", "custom\n", "BANK-OM-001")
    checker = _init_repo(
        tmp_path / "checker",
        {
            "harness/acgh/plancore/catalog.txt": "core\n",
            "harness/acgh/integrations/om/catalog.txt": "adapter\n",
        },
    )
    return product, checker, official, custom


def _initial_request(
    tmp_path: Path,
    product: Path,
    checker: Path,
    official: str,
    custom: str,
    *,
    owner: str | None = "data-team",
) -> Path:
    request = {
        "schema_version": 1,
        "run_id": "initial-01",
        "mode": "initial",
        "repositories": {"product": str(product), "checker": str(checker)},
        "repository_ids": {"product": "product-repo", "checker": "checker-repo"},
        "refs": {"official": official, "current_custom": custom},
        "product_version": "1.0.0",
        "owner": owner,
    }
    path = tmp_path / "request.yaml"
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


def _preflight(tmp_path: Path, *, owner: str | None = "data-team"):
    product, checker, official, custom = _repos(tmp_path)
    request = _initial_request(
        tmp_path, product, checker, official, custom, owner=owner
    )
    state_root = tmp_path / "state"
    marker = create_session_marker(state_root, checker, "session-a")
    run_dir = checker / "evidence" / "om-plan-initial-01"
    result = run_preflight(
        request,
        run_dir,
        OpenMetadataPlanAdapter(),
        session_marker=marker,
    )
    return product, checker, request, state_root, marker, run_dir, result


def _install_registration(
    checker: Path,
    *,
    duplicate: bool = False,
    shared_path: str | None = None,
    snapshot_sha: str | None = None,
) -> Path:
    root = checker / "registration"
    root.mkdir()
    ids = ["BANK-OM-001", "BANK-OM-001" if duplicate else "BANK-OM-002"]
    registry = {
        "schema_version": 1,
        "source": {"snapshot_sha": snapshot_sha} if snapshot_sha else {},
        "entries": [
            {"customization_id": value, "contracts": [f"CONTRACT-{index}"]}
            for index, value in enumerate(ids, start=1)
        ],
    }
    contracts = {
        "schema_version": 1,
        "contracts": [
            {
                "id": "CONTRACT-1",
                "required_tests": ["tests/contracts.py::test_one"],
                "customization_ids": ["BANK-OM-001"],
            }
        ],
    }
    (root / "customization-registry.yaml").write_text(
        yaml.safe_dump(registry), encoding="utf-8"
    )
    (root / "contracts.yaml").write_text(
        yaml.safe_dump(contracts), encoding="utf-8"
    )
    shared = {shared_path: ["BANK-OM-001", "BANK-OM-002"]} if shared_path else {}
    (root / "shared-path-owners.yaml").write_text(
        yaml.safe_dump(shared), encoding="utf-8"
    )
    _git(checker, "add", "registration")
    _git(checker, "commit", "-q", "-m", "add registration")
    return root


def _feature_or_change_request(
    tmp_path: Path,
    product: Path,
    checker: Path,
    baseline: str,
    registration: Path,
    *,
    mode: str = "feature",
    candidate: str | None = None,
    customization_id: str = "BANK-OM-001",
) -> Path:
    request = {
        "schema_version": 1,
        "run_id": f"{mode}-01",
        "mode": mode,
        "repositories": {"product": str(product), "checker": str(checker)},
        "repository_ids": {"product": "product-repo", "checker": "checker-repo"},
        "refs": {"custom_baseline": baseline},
        "registration_path": str(registration),
        "customization_id": customization_id,
        "requirement": "preserve behavior",
        "owner": "data-team",
    }
    if mode == "change":
        request["change_path"] = (
            "post_change_reconcile" if candidate else "pre_plan"
        )
        if candidate:
            request["refs"]["candidate"] = candidate
    path = tmp_path / f"{mode}-request.yaml"
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


def _run_requested_preflight(
    tmp_path: Path,
    checker: Path,
    request: Path,
    *,
    session_id: str = "session-a",
):
    state_root = tmp_path / "state"
    marker = create_session_marker(state_root, checker, session_id)
    request_data = read_data(request)
    run_dir = checker / "evidence" / f"om-plan-{request_data['run_id']}"
    result = run_preflight(
        request,
        run_dir,
        OpenMetadataPlanAdapter(),
        session_marker=marker,
    )
    return state_root, marker, run_dir, result


def _upgrade_request(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    product = _init_repo(tmp_path / "product", {"base.txt": "base\n"})
    base = _git(product, "rev-parse", "HEAD")
    target = _add_commit(product, "official.txt", "official target\n", "BANK-OM-900")
    _git(product, "checkout", "-q", "-b", "custom-baseline", base)
    custom = _add_commit(product, "custom.txt", "custom baseline\n", "BANK-OM-001")
    checker = _init_repo(
        tmp_path / "checker",
        {
            "harness/acgh/plancore/catalog.txt": "core\n",
            "harness/acgh/integrations/om/catalog.txt": "adapter\n",
        },
    )
    registration = _install_registration(checker)
    document = tmp_path / "release-1.0.1.html"
    document.write_text("official release 1.0.1 container", encoding="utf-8")
    request = {
        "schema_version": 1,
        "run_id": "upgrade-01",
        "mode": "upgrade",
        "hop_policy": "adjacent_only",
        "repositories": {"product": str(product), "checker": str(checker)},
        "repository_ids": {"product": "product-repo", "checker": "checker-repo"},
        "refs": {
            "official_base": base,
            "official_target": target,
            "custom_baseline": custom,
        },
        "versions": {"base": "1.0.0", "target": "1.0.1"},
        "deployment_method": "container",
        "official_documents": [
            {
                "source": str(document),
                "version_token": "1.0.1",
                "deployment_methods": ["container"],
            }
        ],
        "registration_path": str(registration),
        "owner": "data-team",
    }
    request_path = tmp_path / "upgrade-request.yaml"
    request_path.write_text(
        yaml.safe_dump(request, sort_keys=False), encoding="utf-8"
    )
    return product, checker, request_path, registration


def _proposal_from_first_fact(run_dir: Path, *, owner_unresolved: bool = False) -> None:
    facts = read_data(run_dir / "discovered-facts.json")
    item = facts["canonical_payload"]["items"][0]
    proposal = {
        "decisions": [
            {
                "subject": "retain customization",
                "decision": "keep",
                "decision_source": "proposed",
                "evidence_refs": [
                    {"ref": item["evidence_ref"], "expected": item["value"]}
                ],
                "affected_customization_ids": ["BANK-OM-001"],
                "required_follow_up": "human review",
            }
        ]
    }
    if owner_unresolved:
        proposal["questions"] = ["담당 owner를 지정하세요"]
        proposal["next_step_blocked"] = True
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def test_c01_unknown_mode_is_rejected():
    request = {
        "schema_version": 1,
        "run_id": "x",
        "mode": "unknown",
        "repositories": {"product": "p", "checker": "c"},
        "refs": {},
    }
    with pytest.raises(PlanControlError) as caught:
        validate("run-request", request)
    assert caught.value.code == "SCHEMA_INVALID"


def test_c02_missing_ref_reports_all_missing_roles_and_next_action(tmp_path: Path):
    product, checker, _, _ = _repos(tmp_path)
    request = _initial_request(
        tmp_path,
        product,
        checker,
        "missing-official",
        "missing-custom",
    )
    marker = create_session_marker(tmp_path / "state", checker, "a")
    run_dir = checker / "evidence" / "missing-refs"
    with pytest.raises(PlanControlError) as caught:
        run_preflight(
            request,
            run_dir,
            OpenMetadataPlanAdapter(),
            session_marker=marker,
        )
    assert caught.value.code == "REFS_UNAVAILABLE"
    missing = caught.value.details["missing_refs"]
    assert {item["role"] for item in missing} == {"official", "current_custom"}
    assert "next_action" in caught.value.details


def test_c04_missing_source_blob_reports_exact_path_and_object(tmp_path: Path):
    product, checker, official, custom = _repos(tmp_path)
    object_id = _git(product, "rev-parse", f"{custom}:feature.txt")
    object_path = product / ".git" / "objects" / object_id[:2] / object_id[2:]
    assert object_path.is_file()
    object_path.unlink()
    request = _initial_request(tmp_path, product, checker, official, custom)
    marker = create_session_marker(tmp_path / "state", checker, "a")
    with pytest.raises(PlanControlError) as caught:
        run_preflight(
            request,
            checker / "evidence" / "missing-blob",
            OpenMetadataPlanAdapter(),
            session_marker=marker,
        )
    assert caught.value.code == "SOURCE_BLOBS_UNAVAILABLE"
    assert any(
        item["path"] == "feature.txt" and item["object_id"] == object_id
        for item in caught.value.details["missing_objects"]
    )


@pytest.mark.parametrize("run_id", ["../escape", "a/b", "x\nnext", ""])
def test_c37_invalid_run_id_is_rejected(run_id: str):
    request = {
        "schema_version": 1,
        "run_id": run_id,
        "mode": "initial",
        "repositories": {"product": "p", "checker": "c"},
        "refs": {"official": "x", "current_custom": "y"},
    }
    with pytest.raises(PlanControlError):
        validate("run-request", request)


def test_c39_preflight_creates_run_marker_only_after_machine_files(tmp_path: Path):
    *_, marker, run_dir, result = _preflight(tmp_path)
    assert result["status"] == "ready_for_proposal"
    assert (run_dir / "run-request.yaml").is_file()
    assert (run_dir / "input-lock.yaml").is_file()
    assert (run_dir / "discovered-facts.json").is_file()
    assert (run_dir / ".plan-active").is_file()
    assert marker.is_file()


def test_c05_dirty_worktree_fails_without_cleaning_and_cleans_session(tmp_path: Path):
    product, checker, official, custom = _repos(tmp_path)
    (product / "untracked.txt").write_text("keep me", encoding="utf-8")
    request = _initial_request(tmp_path, product, checker, official, custom)
    marker = create_session_marker(tmp_path / "state", checker, "session-a")
    run_dir = checker / "evidence" / "dirty-run"
    with pytest.raises(PlanControlError) as caught:
        run_preflight(
            request,
            run_dir,
            OpenMetadataPlanAdapter(),
            session_marker=marker,
        )
    assert caught.value.code == "WORKTREE_DIRTY"
    assert (product / "untracked.txt").is_file()
    assert not marker.exists()
    assert not (run_dir / ".plan-active").exists()
    error = json.loads((run_dir / "preflight-result.json").read_text())
    assert error["status"] == "analysis_error"


def test_c06_missing_registration_stops_change_without_guessing(tmp_path: Path):
    product, checker, _, custom = _repos(tmp_path)
    request = _feature_or_change_request(
        tmp_path,
        product,
        checker,
        custom,
        checker / "missing-registration",
        mode="change",
    )
    marker = create_session_marker(tmp_path / "state", checker, "a")
    with pytest.raises(PlanControlError) as caught:
        run_preflight(
            request,
            checker / "evidence" / "missing",
            OpenMetadataPlanAdapter(),
            session_marker=marker,
        )
    assert caught.value.code == "ACTIVE_REGISTRATION_MISSING"


def test_c07_schema_error_reports_field_location():
    bad = {
        "schema_version": 1,
        "run_id": "change-01",
        "mode": "change",
        "repositories": {"product": "p", "checker": "c"},
        "refs": {"custom_baseline": "x"},
    }
    with pytest.raises(PlanControlError) as caught:
        validate("run-request", bad)
    issues = caught.value.details["issues"]
    assert any("change_path" in issue["message"] for issue in issues)


def test_c08_duplicate_registered_id_blocks_proposal(tmp_path: Path):
    product, checker, _, custom = _repos(tmp_path)
    registration = _install_registration(checker, duplicate=True)
    request = _feature_or_change_request(
        tmp_path, product, checker, custom, registration
    )
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    _proposal_from_first_fact(run_dir)
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"
    attempt = read_data(run_dir / result["attempts"][-1])
    assert any("duplicate" in reason for reason in attempt["reasons"])


def test_c09_idless_commit_is_collected_as_unassigned_fact(tmp_path: Path):
    product, checker, official, _ = _repos(tmp_path)
    (product / "idless.txt").write_text("idless\n", encoding="utf-8")
    _git(product, "add", "idless.txt")
    _git(product, "commit", "-q", "-m", "idless change")
    custom = _git(product, "rev-parse", "HEAD")
    request = _initial_request(tmp_path, product, checker, official, custom)
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    facts = read_data(run_dir / "discovered-facts.json")
    inventory = next(
        item["value"]
        for item in facts["canonical_payload"]["items"]
        if item["fact_id"] == "customization-commits"
    )
    assert any(item["customization_ids"] == [] for item in inventory)


def test_c10_multi_id_commit_cannot_be_silently_assigned(tmp_path: Path):
    product, checker, official, _ = _repos(tmp_path)
    (product / "multi.txt").write_text("multi\n", encoding="utf-8")
    _git(product, "add", "multi.txt")
    _git(
        product,
        "commit",
        "-q",
        "-m",
        "multi id",
        "-m",
        "Customization-ID: BANK-OM-001\nCustomization-ID: BANK-OM-002",
    )
    custom = _git(product, "rev-parse", "HEAD")
    request = _initial_request(tmp_path, product, checker, official, custom)
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    _proposal_from_first_fact(run_dir)
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"


def test_c12_unregistered_test_cannot_be_claimed_as_existing(tmp_path: Path):
    product, checker, _, custom = _repos(tmp_path)
    registration = _install_registration(checker)
    request = _feature_or_change_request(
        tmp_path, product, checker, custom, registration, customization_id="BANK-OM-003"
    )
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    _proposal_from_first_fact(run_dir)
    proposal = read_data(run_dir / "proposal" / "plan.yaml")
    proposal["decisions"][0]["required_tests"] = [
        {"id": "tests/missing.py::test_fake", "status": "existing"}
    ]
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"


def test_c13_observed_claim_without_machine_evidence_is_blocked(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path)
    proposal = {
        "decisions": [
            {
                "subject": "claim",
                "decision": "present",
                "decision_source": "observed",
                "evidence_refs": [],
                "affected_customization_ids": [],
                "required_follow_up": "none",
            }
        ]
    }
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "block"


def test_c17_required_test_skip_is_not_a_pass(tmp_path: Path):
    product, checker, _, custom = _repos(tmp_path)
    registration = _install_registration(checker)
    request = _feature_or_change_request(
        tmp_path, product, checker, custom, registration, customization_id="BANK-OM-003"
    )
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    _proposal_from_first_fact(run_dir)
    proposal = read_data(run_dir / "proposal" / "plan.yaml")
    proposal["decisions"][0]["required_tests"] = [
        {
            "id": "tests/contracts.py::test_one",
            "status": "existing",
            "required": True,
            "result": "skipped",
        }
    ]
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "block"


def test_c18_c45_observational_time_and_key_order_do_not_change_digest(tmp_path: Path):
    product, checker, official, custom = _repos(tmp_path)
    request_path = _initial_request(tmp_path, product, checker, official, custom)
    request = read_data(request_path)
    first_lock, first_facts, _ = collect_state(
        request, OpenMetadataPlanAdapter(), run_dir=tmp_path / "one", collect_documents=False
    )
    second_lock, second_facts, _ = collect_state(
        dict(reversed(list(request.items()))),
        OpenMetadataPlanAdapter(),
        run_dir=tmp_path / "two",
        collect_documents=False,
    )
    assert first_lock["input_lock_digest"] == second_lock["input_lock_digest"]
    assert first_facts["discovered_facts_digest"] == second_facts["discovered_facts_digest"]


def test_c11_shared_path_requires_every_registered_owner(tmp_path: Path):
    product, checker, _, baseline = _repos(tmp_path)
    (product / "shared.txt").write_text("shared\n", encoding="utf-8")
    _git(product, "add", "shared.txt")
    _git(product, "commit", "-q", "-m", "shared baseline")
    baseline = _git(product, "rev-parse", "HEAD")
    candidate = _add_commit(product, "shared.txt", "changed\n", "BANK-OM-001")
    registration = _install_registration(checker, shared_path="shared.txt")
    request = _feature_or_change_request(
        tmp_path,
        product,
        checker,
        baseline,
        registration,
        mode="change",
        candidate=candidate,
    )
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    _proposal_from_first_fact(run_dir)
    proposal = read_data(run_dir / "proposal" / "plan.yaml")
    proposal["shared_impact"] = [
        {"path": "shared.txt", "customization_ids": ["BANK-OM-001"]}
    ]
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"
    attempt = read_data(run_dir / result["attempts"][-1])
    assert any("shared path owners" in reason for reason in attempt["reasons"])


def test_c20_historical_provenance_sha_is_not_an_active_lock(tmp_path: Path):
    product, checker, official, baseline = _repos(tmp_path)
    registration = _install_registration(checker, snapshot_sha=official)
    request = _feature_or_change_request(
        tmp_path,
        product,
        checker,
        baseline,
        registration,
        mode="change",
    )
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    facts = read_data(run_dir / "discovered-facts.json")
    values = {
        item["fact_id"]: item["value"]
        for item in facts["canonical_payload"]["items"]
    }
    assert values["registration-source-provenance"]["snapshot_sha"] == official
    assert values["ref-custom_baseline"]["commit_sha"] == baseline
    assert official != baseline
    _proposal_from_first_fact(run_dir)
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "approval"


def test_c19_one_character_change_breaks_stored_digest(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    path = run_dir / "input-lock.yaml"
    data = read_data(path)
    data["canonical_payload"]["run_id"] += "x"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "analysis_error"


def test_c15_hook_and_final_scan_block_outside_proposal_write(tmp_path: Path):
    product, _, _, _, marker, run_dir, _ = _preflight(tmp_path)
    decision = decide_pre_tool_use(
        session_marker=marker,
        tool_name="Write",
        target_path=product / "changed.txt",
    )
    assert not decision.allowed
    _proposal_from_first_fact(run_dir)
    (product / "changed.txt").write_text("forbidden", encoding="utf-8")
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "analysis_error"


def test_c21_upgrade_without_official_documents_is_rejected():
    request = {
        "mode": "upgrade",
        "deployment_method": "container",
        "versions": {"base": "1.13.1", "target": "1.13.2"},
        "official_documents": [],
    }
    with pytest.raises(PlanControlError) as caught:
        OpenMetadataPlanAdapter().validate_request(request)
    assert caught.value.code == "DEPLOYMENT_DOCUMENT_MISSING"


def test_c22_c29_wrong_document_version_token_is_rejected(tmp_path: Path):
    source = tmp_path / "release.html"
    source.write_text("release 1.13.1", encoding="utf-8")
    request = {
        "mode": "upgrade",
        "official_documents": [
            {"source": str(source), "version_token": "1.13.2"}
        ],
    }
    with pytest.raises(PlanControlError) as caught:
        collect_document_snapshots(request, tmp_path / "run")
    assert caught.value.code == "OFFICIAL_DOCUMENT_VERSION_MISMATCH"


def test_c23_deployment_specific_document_is_required():
    request = {
        "mode": "upgrade",
        "deployment_method": "container",
        "versions": {"base": "1.13.1", "target": "1.13.2"},
        "official_documents": [
            {
                "source": "release.html",
                "version_token": "1.13.2",
                "deployment_methods": ["cluster"],
            }
        ],
    }
    with pytest.raises(PlanControlError) as caught:
        OpenMetadataPlanAdapter().validate_request(request)
    assert caught.value.code == "DEPLOYMENT_DOCUMENT_MISSING"


def test_c24_operational_finding_must_reach_checklist(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    proposal = read_data(run_dir / "proposal" / "plan.yaml")
    proposal["findings"] = [{"id": "F-1", "category": "db_migration"}]
    proposal["operations"] = []
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"


@pytest.mark.parametrize(
    "relation",
    [
        "documented_not_located",
        "code_change_not_documented",
        "documented_contradicts_observed",
    ],
)
def test_c25_c26_c36_explicit_doc_code_relations_are_preserved(
    tmp_path: Path, relation: str
):
    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    proposal = read_data(run_dir / "proposal" / "plan.yaml")
    proposal["crosschecks"] = [{"subject": "X", "relation": relation}]
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "approval"


def test_c27_network_or_source_failure_cannot_be_replaced_from_memory(tmp_path: Path):
    request = {
        "mode": "upgrade",
        "official_documents": [
            {"source": str(tmp_path / "missing.html"), "version_token": "1.13.2"}
        ],
    }
    with pytest.raises(PlanControlError) as caught:
        collect_document_snapshots(request, tmp_path / "run")
    assert caught.value.code == "OFFICIAL_DOCUMENT_UNAVAILABLE"


def test_c33_c43_forged_facts_fail_recollection_even_without_hook(tmp_path: Path):
    from acgh.verdict import canonical_digest

    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    path = run_dir / "discovered-facts.json"
    data = read_data(path)
    data["canonical_payload"]["items"][0]["value"] = {"forged": True}
    data["item_digests"] = {
        item["fact_id"]: canonical_digest(item)
        for item in data["canonical_payload"]["items"]
    }
    data["discovered_facts_digest"] = canonical_digest(data["canonical_payload"])
    path.write_text(json.dumps(data), encoding="utf-8")
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "analysis_error"


def test_c38_registration_change_is_stale_and_requires_new_plan(tmp_path: Path):
    product, checker, _, baseline = _repos(tmp_path)
    registration = _install_registration(checker)
    request = _feature_or_change_request(
        tmp_path, product, checker, baseline, registration, customization_id="BANK-OM-003"
    )
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request)
    _proposal_from_first_fact(run_dir)
    registry = registration / "customization-registry.yaml"
    registry.write_text(registry.read_text() + "# changed\n", encoding="utf-8")
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "analysis_error"
    attempt = read_data(run_dir / result["attempts"][-1])
    assert attempt["registration_stale"] is True


def test_c40_pointer_movement_requires_definition_delta(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    proposal = read_data(run_dir / "proposal" / "plan.yaml")
    proposal["pointer_movements"] = [{"from": "/oneOf/1", "to": "/oneOf/2"}]
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"


def test_c41_session_marker_without_run_marker_blocks_product_write(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    marker = create_session_marker(tmp_path / "state", project, "a")
    decision = decide_pre_tool_use(
        session_marker=marker,
        tool_name="Write",
        target_path=tmp_path / "product" / "file.txt",
    )
    assert not decision.allowed
    assert "preflight" in decision.reason


def test_c42_successful_validation_cleans_both_markers(tmp_path: Path):
    *_, marker, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    run_validation(run_dir, OpenMetadataPlanAdapter())
    assert not marker.exists()
    assert not (run_dir / ".plan-active").exists()


def test_r03_facts_cannot_change_between_proposal_attempts(tmp_path: Path):
    _, checker, _, state_root, _, run_dir, _ = _preflight(tmp_path)
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump({"decisions": [{}]}), encoding="utf-8"
    )
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "block"
    marker = create_session_marker(state_root, checker, "session-b")
    bind_run(marker, run_dir)
    facts_path = run_dir / "discovered-facts.json"
    facts = read_data(facts_path)
    facts["canonical_payload"]["items"][0]["value"] = "changed"
    facts_path.write_text(json.dumps(facts), encoding="utf-8")
    _proposal_from_first_fact(run_dir)
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "analysis_error"


def test_r06_same_url_with_changed_bytes_cannot_reuse_snapshot(tmp_path: Path):
    source = tmp_path / "release.html"
    source.write_text("release 1.13.2 first", encoding="utf-8")
    request = {
        "mode": "upgrade",
        "official_documents": [
            {"source": str(source), "version_token": "1.13.2"}
        ],
    }
    run = tmp_path / "run"
    recorded = collect_document_snapshots(request, run)
    snapshot = run / recorded["documents"][0]["snapshot_path"]
    snapshot.write_text("release 1.13.2 second", encoding="utf-8")
    with pytest.raises(PlanControlError) as caught:
        verify_document_snapshots(run, recorded)
    assert caught.value.code == "OFFICIAL_DOCUMENT_DIGEST_MISMATCH"


def test_c03_branch_move_does_not_change_pinned_validation_input(tmp_path: Path):
    product, _, _, _, _, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    _add_commit(product, "later.txt", "later\n", "BANK-OM-002")
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "approval"


def test_c31_tampered_facts_are_rejected_by_recollection(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    path = run_dir / "discovered-facts.json"
    data = json.loads(path.read_text())
    data["canonical_payload"]["items"][0]["value"] = "forged"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "analysis_error"
    attempt = read_data(run_dir / result["attempts"][-1])
    assert any("digest" in reason or "facts" in reason for reason in attempt["reasons"])


def test_c32_missing_evidence_pointer_is_rejected(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path)
    proposal = {
        "decisions": [
            {
                "subject": "x",
                "decision": "y",
                "decision_source": "proposed",
                "evidence_refs": ["discovered-facts.json#/missing"],
                "affected_customization_ids": [],
                "required_follow_up": "review",
            }
        ]
    }
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump(proposal), encoding="utf-8"
    )
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "analysis_error"
    attempt = read_data(run_dir / result["attempts"][-1])
    assert attempt["evidence_ref_errors"]


def test_c34_unknown_owner_requires_question_and_stop(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path, owner=None)
    _proposal_from_first_fact(run_dir, owner_unresolved=True)
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "approval"
    assert "owner" in result["next_action"]


def test_c34_unknown_owner_without_question_is_blocked(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path, owner=None)
    _proposal_from_first_fact(run_dir)
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"


def test_c14_llm_cannot_fill_an_owner_that_human_did_not_supply(tmp_path: Path):
    *_, run_dir, _ = _preflight(tmp_path, owner=None)
    _proposal_from_first_fact(run_dir, owner_unresolved=True)
    proposal_path = run_dir / "proposal" / "plan.yaml"
    proposal = read_data(proposal_path)
    proposal["owner"] = "LLM-GUESSED-OWNER"
    proposal_path.write_text(
        yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    result = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert result["verdict"] == "block"
    attempt = read_data(run_dir / result["attempts"][-1])
    assert any("owner" in reason for reason in attempt["reasons"])


def test_r04_validation_attempts_are_append_only_for_proposal_fix(tmp_path: Path):
    _, checker, _, state_root, _, run_dir, _ = _preflight(tmp_path)
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump({"decisions": [{}]}), encoding="utf-8"
    )
    first = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert first["verdict"] == "block"
    first_attempt = (run_dir / first["attempts"][0]).read_bytes()

    marker = create_session_marker(state_root, checker, "session-b")
    bind_run(marker, run_dir)
    _proposal_from_first_fact(run_dir)
    second = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert second["verdict"] == "approval"
    assert len(second["attempts"]) == 2
    assert (run_dir / second["attempts"][0]).read_bytes() == first_attempt


def test_r07_completed_run_cannot_be_revalidated(tmp_path: Path):
    _, checker, _, state_root, _, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "approval"
    marker = create_session_marker(state_root, checker, "session-b")
    bind_run(marker, run_dir)
    with pytest.raises(PlanControlError) as caught:
        run_validation(run_dir, OpenMetadataPlanAdapter())
    assert caught.value.code == "COMPLETED_RUN_READ_ONLY"


def test_c41_concurrent_cleanup_does_not_remove_other_session(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    state = tmp_path / "state"
    marker_a = create_session_marker(state, project, "a")
    marker_b = create_session_marker(state, project, "b")
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    run_a.mkdir()
    run_b.mkdir()
    pair_a = bind_run(marker_a, run_a)
    bind_run(marker_b, run_b)
    cleanup_pair(pair_a)
    assert not marker_a.exists()
    assert marker_b.exists()
    assert (run_b / ".plan-active").exists()


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m x",
        "git -C /tmp/repo reset --hard",
        "git worktree add /tmp/x branch",
        "git fetch origin",
        "python harness/om_workflow.py plan-validate --run-dir x && git push",
    ],
)
def test_c16_c30_hook_blocks_git_mutations_and_compound_bypass(
    tmp_path: Path, command: str
):
    project = tmp_path / "project"
    project.mkdir()
    marker = create_session_marker(tmp_path / "state", project, "a")
    decision = decide_pre_tool_use(
        session_marker=marker,
        tool_name="Bash",
        command=command,
    )
    assert not decision.allowed


def test_c42_hook_allows_only_current_proposal_directory(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    marker = create_session_marker(tmp_path / "state", project, "a")
    run = tmp_path / "run"
    run.mkdir()
    (run / "proposal").mkdir()
    bind_run(marker, run)
    allowed = decide_pre_tool_use(
        session_marker=marker,
        tool_name="Write",
        target_path=run / "proposal" / "plan.yaml",
    )
    denied = decide_pre_tool_use(
        session_marker=marker,
        tool_name="Write",
        target_path=run / "input-lock.yaml",
    )
    assert allowed.allowed
    assert not denied.allowed


def test_hook_adapter_uses_event_session_and_cwd_for_markers(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    state = tmp_path / "state"
    base = {
        "session_id": "claude-session-a",
        "cwd": str(project),
    }
    assert handle_event(
        {
            **base,
            "hook_event_name": "UserPromptSubmit",
            "prompt": "/om-plan initial",
        },
        state,
    ) is None
    marker = session_marker_path(state, project, "claude-session-a")
    assert marker.is_file()
    denied = handle_event(
        {
            **base,
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(project / "product.txt")},
        },
        state,
    )
    assert denied["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_stop_hook_does_not_turn_recursive_block_into_pass(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    state = tmp_path / "state"
    create_session_marker(state, project, "claude-session-a")
    result = handle_event(
        {
            "session_id": "claude-session-a",
            "cwd": str(project),
            "hook_event_name": "Stop",
            "stop_hook_active": True,
        },
        state,
    )
    assert result["decision"] == "block"
    assert "do not synthesize a pass" in result["reason"]


def test_c28_official_document_snapshot_uses_exact_bytes(tmp_path: Path):
    source = tmp_path / "release.html"
    raw = b"release 1.2.1\r\n\x00raw-bytes"
    source.write_bytes(raw)
    run = tmp_path / "run"
    request = {
        "mode": "upgrade",
        "official_documents": [
            {"source": str(source), "version_token": "1.2.1"}
        ],
    }
    result = collect_document_snapshots(request, run)
    snapshot = run / result["documents"][0]["snapshot_path"]
    assert snapshot.read_bytes() == raw
    verify_document_snapshots(run, result)
    snapshot.write_bytes(raw + b"changed")
    with pytest.raises(PlanControlError) as caught:
        verify_document_snapshots(run, result)
    assert caught.value.code == "OFFICIAL_DOCUMENT_DIGEST_MISMATCH"


@pytest.mark.parametrize(
    ("base", "target", "expected"),
    [
        ("1.13.1", "1.13.1", "equal"),
        ("1.13.2", "1.13.1", "reversed"),
        ("1.13.1", "1.13.3", "non_adjacent"),
    ],
)
def test_c35_non_adjacent_equal_and_reversed_upgrades_stop(
    base: str, target: str, expected: str
):
    request = {
        "mode": "upgrade",
        "deployment_method": "container",
        "versions": {"base": base, "target": target},
    }
    with pytest.raises(PlanControlError) as caught:
        OpenMetadataPlanAdapter().validate_request(request)
    assert caught.value.code == "UPGRADE_RELATION_UNSUPPORTED"
    assert caught.value.details["version_relation"] == expected


def test_c46_locked_sha_change_alters_digest_and_fails_validation(tmp_path: Path):
    from acgh.verdict import canonical_digest

    *_, run_dir, _ = _preflight(tmp_path)
    _proposal_from_first_fact(run_dir)
    path = run_dir / "input-lock.yaml"
    data = read_data(path)
    before = data["input_lock_digest"]
    product = Path(data["observational_metadata"]["repository_paths"]["product"])
    official = _git(product, "rev-list", "--max-parents=0", "HEAD")
    canonical = data["canonical_payload"]
    canonical["repositories"]["product"]["commit_shas"]["current_custom"] = official
    canonical["repositories"]["product"]["tree_shas"]["current_custom"] = _git(
        product, "rev-parse", f"{official}^{{tree}}"
    )
    data["input_lock_digest"] = canonical_digest(canonical)
    assert data["input_lock_digest"] != before
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "analysis_error"


def test_c46_deployment_method_change_fails_the_locked_request(tmp_path: Path):
    _, checker, request_path, _ = _upgrade_request(tmp_path)
    _, _, run_dir, _ = _run_requested_preflight(tmp_path, checker, request_path)
    _proposal_from_first_fact(run_dir)
    request = read_data(run_dir / "run-request.yaml")
    request["deployment_method"] = "cluster"
    (run_dir / "run-request.yaml").write_text(
        yaml.safe_dump(request, sort_keys=False), encoding="utf-8"
    )
    assert run_validation(run_dir, OpenMetadataPlanAdapter())["verdict"] == "analysis_error"


@pytest.mark.parametrize(
    ("stage", "new_run", "proposal_only"),
    [
        ("preflight", True, False),
        ("fact_collection", True, False),
        ("proposal_validation", False, True),
        ("fact_recalculation", True, False),
        ("completed", True, False),
    ],
)
def test_r01_r07_retry_table(stage: str, new_run: bool, proposal_only: bool):
    decision = retry_decision(stage)
    assert decision.new_run_required is new_run
    assert decision.proposal_only is proposal_only


def test_r01_failed_preflight_directory_cannot_be_resumed(tmp_path: Path):
    product, checker, official, custom = _repos(tmp_path)
    request = _initial_request(tmp_path, product, checker, official, custom)
    (product / "dirty.txt").write_text("dirty", encoding="utf-8")
    state = tmp_path / "state"
    marker = create_session_marker(state, checker, "first")
    run_dir = checker / "evidence" / "failed-preflight"
    with pytest.raises(PlanControlError) as first:
        run_preflight(request, run_dir, OpenMetadataPlanAdapter(), session_marker=marker)
    assert first.value.code == "WORKTREE_DIRTY"
    assert (run_dir / "preflight-result.json").is_file()
    (product / "dirty.txt").unlink()
    second_marker = create_session_marker(state, checker, "second")
    with pytest.raises(PlanControlError) as second:
        run_preflight(
            request,
            run_dir,
            OpenMetadataPlanAdapter(),
            session_marker=second_marker,
        )
    assert second.value.code == "RUN_DIRECTORY_EXISTS"


def test_r02_failed_fact_collection_cannot_be_manually_completed(tmp_path: Path):
    product, checker, official, custom = _repos(tmp_path)
    request = _initial_request(tmp_path, product, checker, official, custom)
    object_id = _git(product, "rev-parse", f"{custom}:feature.txt")
    object_path = product / ".git" / "objects" / object_id[:2] / object_id[2:]
    object_path.unlink()
    state = tmp_path / "state"
    marker = create_session_marker(state, checker, "first")
    run_dir = checker / "evidence" / "failed-facts"
    with pytest.raises(PlanControlError) as first:
        run_preflight(request, run_dir, OpenMetadataPlanAdapter(), session_marker=marker)
    assert first.value.code == "SOURCE_BLOBS_UNAVAILABLE"
    (run_dir / "discovered-facts.json").write_text("{}\n", encoding="utf-8")
    second_marker = create_session_marker(state, checker, "second")
    with pytest.raises(PlanControlError) as second:
        run_preflight(
            request,
            run_dir,
            OpenMetadataPlanAdapter(),
            session_marker=second_marker,
        )
    assert second.value.code == "RUN_DIRECTORY_EXISTS"


def test_r05_revalidation_appends_and_never_overwrites_attempt(tmp_path: Path):
    _, checker, _, state_root, _, run_dir, _ = _preflight(tmp_path)
    (run_dir / "proposal" / "plan.yaml").write_text(
        yaml.safe_dump({"decisions": [{}]}), encoding="utf-8"
    )
    first = run_validation(run_dir, OpenMetadataPlanAdapter())
    first_path = run_dir / first["attempts"][0]
    first_bytes = first_path.read_bytes()
    marker = create_session_marker(state_root, checker, "second")
    bind_run(marker, run_dir)
    _proposal_from_first_fact(run_dir)
    second = run_validation(run_dir, OpenMetadataPlanAdapter())
    assert second["attempts"] == [
        "validation-attempts/attempt-0001.json",
        "validation-attempts/attempt-0002.json",
    ]
    assert first_path.read_bytes() == first_bytes
