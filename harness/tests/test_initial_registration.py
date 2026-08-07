from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from acgh import initial_registration as I


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo: Path, files: dict[str, str], message: str) -> str:
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


@pytest.fixture()
def initial_case(tmp_path: Path):
    repo = tmp_path / "product"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "commit.gpgsign", "false")
    base = _commit(
        repo,
        {
            "core/a.txt": "official-a\n",
            "core/b.txt": "official-b\n",
            "core/shared.txt": "official-shared\n",
        },
        "official",
    )
    _git(repo, "branch", "official")
    _commit(
        repo,
        {
            "core/a.txt": "bank-a\n",
            "core/shared.txt": "bank-a-shared\n",
        },
        "feature A\n\nCustomization-ID: BANK-OM-001",
    )
    _commit(
        repo,
        {
            "core/b.txt": "bank-b\n",
            "core/shared.txt": "bank-a-and-b-shared\n",
        },
        "feature B\n\nCustomization-ID: BANK-OM-002",
    )
    custom = _git(repo, "rev-parse", "HEAD")
    _git(repo, "branch", "custom")

    registration = tmp_path / "registration"
    registration.mkdir()
    _dump(
        registration / "repository-layout.yaml",
        {
            "schema_version": 1,
            "upstream_base_sha": base,
            "path_grammar": {
                "name": "gitignore-pathspec",
                "version": 1,
                "root_relative": True,
                "separator": "/",
                "case_sensitive": True,
                "unicode_normalization": "NFC",
                "negation_allowed": False,
                "symlink_policy": "reject",
                "submodule_policy": "reject",
                "lfs_policy": "reject",
            },
            "upstream_owned_roots": ["core/**"],
            "bank_governance_roots": [".bank/**"],
            "platform_extension_roots": ["bank-extensions/**"],
            "unknown_path_policy": "analysis_error",
        },
    )
    _dump(registration / "sensitive-zones.yaml", {"schema_version": 1, "zones": []})

    metadata = tmp_path / "initial-input.yaml"
    _dump(
        metadata,
        {
            "schema_version": 1,
            "source": {
                "repository": "example/product",
                "upstream_repository": "vendor/product",
                "upstream_tag": "42.7-release",
                "limitations": [],
                "unregistered_findings": [],
            },
            "customizations": [
                {
                    "customization_id": "BANK-OM-001",
                    "title": "Feature A",
                    "owner": "team-a",
                    "owner_status": "assigned",
                    "criticality": "high",
                    "kind": "core-patch",
                    "provenance": "source-snapshot",
                    "required_changed_paths": ["core/a.txt"],
                    "contracts": ["CONTRACT-A"],
                    "series_allowed": False,
                },
                {
                    "customization_id": "BANK-OM-002",
                    "title": "Feature B",
                    "owner": "team-b",
                    "owner_status": "assigned",
                    "criticality": "medium",
                    "kind": "core-patch",
                    "provenance": "source-snapshot",
                    "required_changed_paths": ["core/b.txt"],
                    "contracts": ["CONTRACT-B"],
                    "series_allowed": False,
                },
            ],
            "contracts": [
                {
                    "id": "CONTRACT-A",
                    "title": "A works",
                    "invariant": "A remains available.",
                    "required_tests": ["tests/test_a.py::test_a"],
                    "customization_ids": ["BANK-OM-001"],
                },
                {
                    "id": "CONTRACT-B",
                    "title": "B works",
                    "invariant": "B remains available.",
                    "required_tests": ["tests/test_b.py::test_b"],
                    "customization_ids": ["BANK-OM-002"],
                },
            ],
        },
    )
    return repo, registration, metadata, base, custom


def _approved(proposal: dict) -> dict:
    return {
        "schema_version": 1,
        "proposal_digest": I.proposal_digest(proposal),
        "approved_by": "owner@example.com",
        "approved_at": "2026-08-06T12:00:00-07:00",
        "decisions": [
            {
                "finding_id": "REVIEW-0001",
                "decision": "accept_proposal",
                "reason": "Reviewed generated paths, ownership, and contracts.",
            }
        ],
    }


def test_version_independent_plan_derives_all_initial_files(initial_case, tmp_path):
    repo, registration, metadata, base, custom = initial_case
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )

    assert proposal["status"] == "REVIEW_REQUIRED"
    assert proposal["inputs"]["product_version"] == "42.7"
    assert proposal["inputs"]["official_sha"] == base
    assert proposal["inputs"]["custom_sha"] == custom
    assert proposal["facts"] == {
        "customization_count": 2,
        "commit_count": 2,
        "changed_path_count": 3,
        "shared_path_count": 1,
        "commits_by_id": proposal["facts"]["commits_by_id"],
    }
    assert set(generated) == {
        "customization-registry.yaml",
        "contracts.yaml",
        "source-diff-paths.txt",
        "source-snapshot-path-owners.yaml",
        "shared-path-owners.yaml",
        "manifests/BANK-OM-001.yaml",
        "manifests/BANK-OM-002.yaml",
    }
    owners = yaml.safe_load(generated["shared-path-owners.yaml"])
    assert owners == {"core/shared.txt": ["BANK-OM-001", "BANK-OM-002"]}
    assert not (registration / "customization-registry.yaml").exists()

    output = tmp_path / "proposal"
    I.write_plan(output, proposal, generated)
    assert (output / "proposed-registration/contracts.yaml").is_file()


def test_plan_blocks_unassigned_owner_and_explains_recovery(initial_case, tmp_path):
    repo, registration, metadata, _, _ = initial_case
    value = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    value["customizations"][0]["owner"] = "UNASSIGNED"
    value["customizations"][0]["owner_status"] = "pending"
    _dump(metadata, value)

    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )

    assert proposal["status"] == "BLOCKED"
    assert proposal["apply_ready"] is False
    assert proposal["blocking_findings"][0]["code"] == "OWNER_NOT_ASSIGNED"
    assert proposal["blocking_findings"][0]["customization_id"] == "BANK-OM-001"

    output = tmp_path / "blocked-proposal"
    I.write_plan(output, proposal, generated)
    summary = (output / "summary.md").read_text(encoding="utf-8")
    assert "반영 가능: `no`" in summary
    assert "BANK-OM-001 · OWNER_NOT_ASSIGNED" in summary
    assert "owner_status를 assigned로 설정" in summary

    with pytest.raises(I.InitialRegistrationError, match="cannot create"):
        I.write_approval_template(
            output / "proposal.yaml",
            tmp_path / "approval.yaml",
        )


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (
            lambda value: value["contracts"][0].update(
                invariant="TODO: write invariant"
            ),
            "CONTRACT_INCOMPLETE",
        ),
        (
            lambda value: value["customizations"][0].update(
                depends_on=["BANK-OM-999"]
            ),
            "UNKNOWN_DEPENDENCY",
        ),
        (
            lambda value: value["customizations"][0].update(
                depends_on=["BANK-OM-001"]
            ),
            "SELF_DEPENDENCY",
        ),
    ],
)
def test_plan_blocks_incomplete_required_input(
    initial_case,
    mutate,
    expected_code,
):
    repo, registration, metadata, _, _ = initial_case
    value = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    mutate(value)
    _dump(metadata, value)

    proposal, _ = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )

    assert proposal["status"] == "BLOCKED"
    assert proposal["apply_ready"] is False
    assert expected_code in {
        finding["code"] for finding in proposal["blocking_findings"]
    }


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["customizations"][0].update(
            required_changed_paths=[]
        ),
        lambda value: value["customizations"][0].update(contracts=[]),
    ],
)
def test_plan_rejects_structurally_missing_required_input(initial_case, mutate):
    repo, registration, metadata, _, _ = initial_case
    value = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    mutate(value)
    _dump(metadata, value)

    with pytest.raises(I.InitialRegistrationError):
        I.build_plan(
            repo,
            registration,
            metadata,
            official_ref="official",
            custom_ref="custom",
            product_version="42.7",
        )


def test_plan_blocks_dependency_cycle(initial_case):
    repo, registration, metadata, _, _ = initial_case
    value = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    value["customizations"][0]["depends_on"] = ["BANK-OM-002"]
    value["customizations"][1]["depends_on"] = ["BANK-OM-001"]
    _dump(metadata, value)

    proposal, _ = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )

    assert "DEPENDENCY_CYCLE" in {
        finding["code"] for finding in proposal["blocking_findings"]
    }


def test_apply_rejects_blocked_initial_registration(initial_case, tmp_path):
    repo, registration, metadata, _, _ = initial_case
    value = yaml.safe_load(metadata.read_text(encoding="utf-8"))
    value["customizations"][0]["owner"] = "UNASSIGNED"
    value["customizations"][0]["owner_status"] = "pending"
    _dump(metadata, value)
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )
    output = tmp_path / "blocked-proposal"
    I.write_plan(output, proposal, generated)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approved(proposal))

    with pytest.raises(I.InitialRegistrationError, match="cannot be applied"):
        I.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )


def test_input_template_discovers_ids_paths_and_never_overwrites(initial_case, tmp_path):
    repo, _, _, _, _ = initial_case
    template = I.build_input_template(
        repo,
        official_ref="official",
        custom_ref="custom",
        repository="example/product",
        upstream_repository="vendor/product",
        upstream_tag="42.7-release",
    )

    assert [item["customization_id"] for item in template["customizations"]] == [
        "BANK-OM-001",
        "BANK-OM-002",
    ]
    assert template["customizations"][0]["owner"] == "UNASSIGNED"
    assert template["customizations"][0]["required_changed_paths"] == [
        "core/a.txt",
        "core/shared.txt",
    ]
    assert template["contracts"][0]["required_tests"][0].startswith("TODO:")

    output = tmp_path / "inputs" / "initial-registration-input.yaml"
    assert I.write_input_template(output, template) is True
    first = output.read_text(encoding="utf-8")
    output.write_text(first + "# human edit\n", encoding="utf-8")
    assert I.write_input_template(output, template) is False
    assert output.read_text(encoding="utf-8").endswith("# human edit\n")


def test_approved_apply_writes_one_complete_initial_bundle(initial_case, tmp_path):
    repo, registration, metadata, _, _ = initial_case
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )
    output = tmp_path / "proposal"
    I.write_plan(output, proposal, generated)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approved(proposal))

    result = I.apply_plan(
        repo,
        registration,
        proposal_path=output / "proposal.yaml",
        approval_path=approval,
    )

    assert result["status"] == "APPLIED"
    assert (registration / "customization-registry.yaml").is_file()
    assert (registration / "contracts.yaml").is_file()
    assert (registration / "manifests/BANK-OM-001.yaml").is_file()
    registry = yaml.safe_load(
        (registration / "customization-registry.yaml").read_text()
    )
    assert registry["source"]["upstream_tag"] == "42.7-release"
    assert registry["source"]["changed_path_count"] == 3


@pytest.mark.parametrize(
    ("complete_before", "expected_code", "expected_field"),
    [
        (0, "APPROVAL_APPROVER_PLACEHOLDER", "approved_by"),
        (1, "APPROVAL_TIME_PLACEHOLDER", "approved_at"),
        (2, "APPROVAL_REASON_PLACEHOLDER", "decisions[0].reason"),
    ],
)
def test_apply_identifies_each_approval_placeholder_in_korean(
    initial_case,
    tmp_path,
    complete_before,
    expected_code,
    expected_field,
):
    repo, registration, metadata, _, _ = initial_case
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )
    output = tmp_path / "proposal"
    I.write_plan(output, proposal, generated)
    approval_value = I.approval_template(proposal)
    if complete_before >= 1:
        approval_value["approved_by"] = "data-platform-team"
    if complete_before >= 2:
        approval_value["approved_at"] = "2026-08-06T12:00:00-07:00"
    approval = tmp_path / "approval.yaml"
    _dump(approval, approval_value)

    with pytest.raises(I.ApprovalValidationError) as caught:
        I.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )

    result = caught.value.as_result()
    assert result["code"] == "APPROVAL_INPUT_INVALID"
    issue = next(item for item in result["issues"] if item["code"] == expected_code)
    assert issue["field"] == expected_field
    assert result["message_ko"]
    assert result["next_action"]


def test_apply_reports_all_approval_schema_issues_with_fields(initial_case, tmp_path):
    repo, registration, metadata, _, _ = initial_case
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )
    output = tmp_path / "proposal"
    I.write_plan(output, proposal, generated)
    approval_value = _approved(proposal)
    approval_value["approved_at"] = "2026/08/06 noon"
    approval_value["approved_by"] = ""
    approval = tmp_path / "approval.yaml"
    _dump(approval, approval_value)

    with pytest.raises(I.ApprovalValidationError) as caught:
        I.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )

    result = caught.value.as_result()
    assert result["code"] == "APPROVAL_INPUT_INVALID"
    assert {issue["field"] for issue in result["issues"]} == {
        "approved_at",
        "approved_by",
    }
    assert all(issue["message_ko"] for issue in result["issues"])
    assert all(issue["next_action"] for issue in result["issues"])


def test_apply_reports_missing_and_unexpected_review_decisions(initial_case, tmp_path):
    repo, registration, metadata, _, _ = initial_case
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )
    output = tmp_path / "proposal"
    I.write_plan(output, proposal, generated)
    approval_value = _approved(proposal)
    approval_value["decisions"] = []
    approval = tmp_path / "approval.yaml"
    _dump(approval, approval_value)

    with pytest.raises(I.ApprovalValidationError) as caught:
        I.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )

    result = caught.value.as_result()
    assert result["code"] == "APPROVAL_DECISION_COVERAGE_MISMATCH"
    assert result["field"] == "decisions[].finding_id"
    assert "REVIEW-0001" in result["next_action"]


def test_apply_blocks_when_human_input_changes(initial_case, tmp_path):
    repo, registration, metadata, _, _ = initial_case
    proposal, generated = I.build_plan(
        repo,
        registration,
        metadata,
        official_ref="official",
        custom_ref="custom",
        product_version="42.7",
    )
    output = tmp_path / "proposal"
    I.write_plan(output, proposal, generated)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approved(proposal))
    metadata.write_text(metadata.read_text() + "\n", encoding="utf-8")

    with pytest.raises(
        I.StaleInitialRegistrationError,
        match="input changed",
    ):
        I.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )


def test_plan_blocks_commit_without_customization_id(initial_case):
    repo, registration, metadata, _, _ = initial_case
    _git(repo, "checkout", "-q", "custom")
    _commit(repo, {"core/extra.txt": "extra\n"}, "missing trailer")

    with pytest.raises(I.InitialRegistrationError, match="exactly one"):
        I.build_plan(
            repo,
            registration,
            metadata,
            official_ref="official",
            custom_ref="custom",
            product_version="42.7",
        )
