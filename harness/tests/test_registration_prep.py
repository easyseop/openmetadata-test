"""Fail-closed registration preparation tests."""
from __future__ import annotations

import copy
import subprocess
from pathlib import Path

import pytest
import yaml

from acgh import registration_prep as P
from prepare_registration import main as cli_main


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo: Path, path: str, content: str, message: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


def _registration(root: Path, base: str, head: str) -> Path:
    registration = root / "registration"
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
    _dump(
        registration / "contracts.yaml",
        {
            "schema_version": 1,
            "contracts": [
                {
                    "id": "CONTRACT-A",
                    "title": "A remains available",
                    "required_tests": ["tests/test_a.py::test_a"],
                    "customization_ids": ["BANK-OM-001"],
                }
            ],
        },
    )
    _dump(
        registration / "customization-registry.yaml",
        {
            "schema_version": 1,
            "source": {
                "repository": "example/product",
                "snapshot_sha": head,
                "upstream_repository": "vendor/product",
                "upstream_tag": "1.0.0",
                "upstream_sha": base,
                "changed_path_count": 1,
                "ancestry_preserved": True,
                "diff_inventory": "source-diff-paths.txt",
                "unregistered_findings": [],
                "limitations": [],
            },
            "entries": [
                {
                    "customization_id": "BANK-OM-001",
                    "title": "Feature A",
                    "owner": "team-a",
                    "owner_status": "assigned",
                    "status": "active",
                    "criticality": "high",
                    "manifest": "manifests/BANK-OM-001.yaml",
                    "contracts": ["CONTRACT-A"],
                    "provenance": "source-snapshot",
                }
            ],
        },
    )
    _dump(
        registration / "manifests/BANK-OM-001.yaml",
        {
            "schema_version": 2,
            "customization_id": "BANK-OM-001",
            "status": "active",
            "kind": "core-patch",
            "title": "Feature A",
            "implementation": {
                "changed_paths": ["core/a.txt"],
                "required_changed_paths": ["core/a.txt"],
            },
            "upgrade_watch": {"paths": ["core/a.txt"]},
            "assurance": {"contracts": ["CONTRACT-A"], "direct_tests": []},
            "series": {"allowed": False, "depends_on": []},
        },
    )
    _dump(
        registration / "source-snapshot-path-owners.yaml",
        {"core/a.txt": ["BANK-OM-001"]},
    )
    _dump(registration / "shared-path-owners.yaml", {})
    return registration


@pytest.fixture()
def prepared(tmp_path):
    repo = tmp_path / "product"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "commit.gpgsign", "false")
    base = _commit(repo, "core/a.txt", "vendor\n", "vendor")
    _git(repo, "branch", "patch")
    head = _commit(
        repo,
        "core/a.txt",
        "bank\n",
        "bank feature\n\nCustomization-ID: BANK-OM-001",
    )
    _git(repo, "branch", "custom")
    registration = _registration(tmp_path, base, head)
    return repo, registration, base, head


def _plan(prepared, **kwargs):
    repo, registration, _, _ = prepared
    return P.build_plan(
        repo,
        registration,
        patch_ref=kwargs.pop("patch_ref", "patch"),
        custom_ref=kwargs.pop("custom_ref", "custom"),
        product_version="1.0.0",
        **kwargs,
    )


def _approve(proposal: dict) -> dict:
    return {
        "schema_version": 1,
        "proposal_digest": P.proposal_digest(proposal),
        "approved_by": "reviewer@example.com",
        "approved_at": "2026-07-30T12:00:00+09:00",
        "decisions": [
            {
                "finding_id": finding["finding_id"],
                "decision": "accept_proposal",
                "reason": "business owner reviewed this exact proposal",
            }
            for finding in proposal["review_required"]
        ],
    }


def test_clean_exact_scope_is_ready_and_plan_is_read_only(prepared, tmp_path):
    _, registration, _, _ = prepared
    before = (registration / "manifests/BANK-OM-001.yaml").read_bytes()
    proposal = _plan(prepared)

    assert proposal["status"] == "READY"
    assert proposal["apply_ready"] is True
    assert proposal["changes"] == []
    assert (registration / "commit-inventory.yaml").exists() is False
    assert (registration / "manifests/BANK-OM-001.yaml").read_bytes() == before

    output = tmp_path / "proposal"
    digest = P.write_plan(output, proposal, registration=registration)
    assert (output / "proposal.yaml").is_file()
    assert (output / "commit-inventory.yaml").is_file()
    assert (output / "diff.patch").read_text() == ""
    assert (output / "proposal-digest.txt").read_text().strip() == digest
    with pytest.raises(P.PreparationError, match="already exists"):
        P.write_plan(output, proposal, registration=registration)
    with pytest.raises(P.PreparationError, match="outside"):
        P.write_plan(
            registration / "unsafe-proposal",
            proposal,
            registration=registration,
        )


def test_followup_path_requires_human_decision_then_applies_atomically(
    prepared, tmp_path
):
    repo, registration, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _commit(
        repo,
        "core/b.txt",
        "followup\n",
        "followup\n\nCustomization-ID: BANK-OM-001",
    )
    manifest_path = registration / "manifests/BANK-OM-001.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["series"]["allowed"] = True
    _dump(manifest_path, manifest)

    proposal = _plan(prepared)
    assert proposal["status"] == "REVIEW_REQUIRED"
    assert proposal["apply_ready"] is True
    assert {item["code"] for item in proposal["review_required"]} == {
        "REQUIRED_PATH_DECISION"
    }
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approve(proposal))

    result = P.apply_plan(
        repo,
        registration,
        proposal_path=output / "proposal.yaml",
        approval_path=approval,
    )
    assert result["status"] == "APPLIED"
    assert result["written_files"] == [
        "commit-inventory.yaml",
        "current-diff-paths.txt",
        "manifests/BANK-OM-001.yaml",
    ]
    applied = yaml.safe_load(manifest_path.read_text())
    assert applied["implementation"]["changed_paths"] == [
        "core/a.txt",
        "core/b.txt",
    ]
    assert applied["implementation"]["required_changed_paths"] == ["core/a.txt"]
    assert applied["upgrade_watch"]["paths"] == ["core/a.txt"]


def test_apply_accepts_an_unquoted_yaml_timestamp(prepared, tmp_path):
    """`approval-template` emits an unquoted placeholder for `approved_at`.

    Replacing it in place leaves a bare RFC3339 scalar, which YAML parses into
    a datetime rather than a string. That is the approver's normal editing
    path, so it must not be refused over quoting.
    """
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)

    template = P.approval_template(proposal)
    assert template["approved_at"] == "REPLACE_WITH_RFC3339_TIME"

    approval = tmp_path / "approval.yaml"
    approval.write_text(
        yaml.safe_dump(template, allow_unicode=True, sort_keys=False).replace(
            "REPLACE_WITH_APPROVER_ID", "reviewer@example.com"
        )
        .replace("REPLACE_WITH_RFC3339_TIME", "2026-07-30T12:00:00+09:00")
        .replace("REPLACE_WITH_REVIEW_REASON", "business owner reviewed this"),
        encoding="utf-8",
    )
    assert "approved_at: 2026-07-30T12:00:00+09:00" in approval.read_text()

    result = P.apply_plan(
        repo,
        registration,
        proposal_path=output / "proposal.yaml",
        approval_path=approval,
    )
    assert result["status"] == "APPLIED"
    assert result["approved_by"] == "reviewer@example.com"


@pytest.mark.parametrize(
    "approved_at",
    [
        "언젠가",
        "2026-07-30",
        "2026-07-30T12:00:00",
        "30/07/2026 12:00",
        "",
    ],
)
def test_apply_refuses_an_unreadable_approved_at(prepared, tmp_path, approved_at):
    """The schema's `format: date-time` is inert without an optional package.

    Normalizing a YAML datetime must not become a way in for anything else,
    and a timestamp with no UTC offset does not pin a moment.
    """
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)

    approval_data = _approve(proposal)
    approval_data["approved_at"] = approved_at
    approval = tmp_path / "approval.yaml"
    _dump(approval, approval_data)

    with pytest.raises(P.PreparationError):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )
    assert (registration / "commit-inventory.yaml").exists() is False


@pytest.mark.parametrize("approved_at", ["2026-07-30T03:00:00Z", "2026-07-30T12:00:00+09:00"])
def test_apply_accepts_both_rfc3339_offset_forms(prepared, tmp_path, approved_at):
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)

    approval_data = _approve(proposal)
    approval_data["approved_at"] = approved_at
    approval = tmp_path / "approval.yaml"
    _dump(approval, approval_data)

    result = P.apply_plan(
        repo,
        registration,
        proposal_path=output / "proposal.yaml",
        approval_path=approval,
    )
    assert result["status"] == "APPLIED"


def test_idless_commit_blocks(prepared):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _commit(repo, "core/no-id.txt", "oops\n", "missing trailer")

    proposal = _plan(prepared)
    assert proposal["status"] == "BLOCKED"
    assert "CUSTOMIZATION_ID_CARDINALITY" in {
        item["code"] for item in proposal["blocked"]
    }


@pytest.mark.parametrize(
    ("path", "content", "expected"),
    [
        (
            "core/lfs.bin",
            "version https://git-lfs.github.com/spec/v1\n"
            "oid sha256:" + "0" * 64 + "\nsize 1\n",
            "LFS_POINTER_PATH",
        ),
    ],
)
def test_unsupported_blob_modes_block(prepared, path, content, expected):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _commit(
        repo,
        path,
        content,
        "unsupported\n\nCustomization-ID: BANK-OM-001",
    )
    proposal = _plan(prepared)
    assert expected in {item["code"] for item in proposal["blocked"]}


def test_symlink_blocks(prepared):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    (repo / "core/link.txt").symlink_to("a.txt")
    _git(repo, "add", "core/link.txt")
    _git(
        repo,
        "commit",
        "-m",
        "link\n\nCustomization-ID: BANK-OM-001",
    )

    proposal = _plan(prepared)
    assert "SYMLINK_PATH" in {item["code"] for item in proposal["blocked"]}


def test_new_id_without_policy_input_cannot_apply(prepared):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _commit(
        repo,
        "core/new.txt",
        "new\n",
        "new customization\n\nCustomization-ID: BANK-OM-099",
    )

    proposal = _plan(prepared)
    assert proposal["status"] == "REVIEW_REQUIRED"
    assert proposal["apply_ready"] is False
    assert proposal["review_required"][0]["code"] == "NEW_CUSTOMIZATION_INPUT"


def test_malformed_and_unused_new_id_input_blocks_without_traceback(prepared):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _commit(
        repo,
        "core/new.txt",
        "new\n",
        "new customization\n\nCustomization-ID: BANK-OM-099",
    )
    proposal = _plan(
        prepared,
        new_id_metadata={
            "BANK-OM-099": [],
            "BANK-OM-100": {"title": "unused"},
        },
    )
    codes = {item["code"] for item in proposal["blocked"]}
    assert "INVALID_NEW_CUSTOMIZATION" in codes
    assert "UNUSED_NEW_CUSTOMIZATION_INPUT" in codes


def test_partial_registry_manifest_pair_blocks(prepared):
    _, registration, _, _ = prepared
    (registration / "manifests/BANK-OM-001.yaml").unlink()
    with pytest.raises(P.PreparationError, match="cannot load registration"):
        _plan(prepared)


def test_multiple_ids_and_mixed_ownership_block(prepared):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    (repo / ".bank").mkdir()
    (repo / "core/mixed.txt").write_text("core\n")
    (repo / ".bank/mixed.yaml").write_text("bank: true\n")
    _git(repo, "add", "-A")
    _git(
        repo,
        "commit",
        "-m",
        "mixed\n\nCustomization-ID: BANK-OM-001\n"
        "Customization-ID: BANK-OM-002",
    )

    proposal = _plan(prepared)
    codes = {item["code"] for item in proposal["blocked"]}
    assert "CUSTOMIZATION_ID_CARDINALITY" in codes
    assert "MIXED_OWNERSHIP_COMMIT" in codes


def test_unknown_path_is_analysis_error(prepared):
    repo, _, _, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _commit(
        repo,
        "misc/unknown.txt",
        "unknown\n",
        "unknown\n\nCustomization-ID: BANK-OM-001",
    )
    proposal = _plan(prepared)
    assert proposal["status"] == "ANALYSIS_ERROR"
    assert "UNKNOWN_PATH" in {
        item["code"] for item in proposal["analysis_errors"]
    }


def test_submodule_entry_blocks(prepared):
    repo, _, base, _ = prepared
    _git(repo, "checkout", "-q", "custom")
    _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{base},core/sub")
    _git(
        repo,
        "commit",
        "-m",
        "gitlink\n\nCustomization-ID: BANK-OM-001",
    )
    proposal = _plan(prepared)
    assert "SUBMODULE_PATH" in {item["code"] for item in proposal["blocked"]}


def test_source_owner_and_shared_maps_fail_closed(prepared):
    _, registration, _, _ = prepared
    _dump(
        registration / "source-snapshot-path-owners.yaml",
        {
            "core/a.txt": ["BANK-OM-001"],
            "core/missing.txt": ["BANK-OM-001"],
        },
    )
    proposal = _plan(prepared)
    assert "SOURCE_OWNER_SCOPE_LOST" in {
        item["code"] for item in proposal["blocked"]
    }

    _dump(
        registration / "shared-path-owners.yaml",
        {"core/a.txt": ["BANK-OM-001", "BANK-OM-002"]},
    )
    proposal = _plan(prepared)
    assert "SHARED_OWNER_MAP_MISMATCH" in {
        item["code"] for item in proposal["analysis_errors"]
    }


def test_unrelated_ref_is_analysis_error(prepared):
    repo, _, _, _ = prepared
    tree = _git(repo, "rev-parse", "patch^{tree}")
    unrelated = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", tree],
        check=True,
        input="unrelated\n",
        capture_output=True,
        text=True,
    ).stdout.strip()
    _git(repo, "branch", "unrelated", unrelated)
    proposal = _plan(prepared, custom_ref="unrelated")
    assert proposal["status"] == "ANALYSIS_ERROR"
    assert "UNRELATED_OR_NONLINEAR_RANGE" in {
        item["code"] for item in proposal["analysis_errors"]
    }


def test_bank_only_watch_questions_are_grouped(prepared):
    _, registration, _, _ = prepared
    manifest_path = registration / "manifests/BANK-OM-001.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["upgrade_watch"]["paths"].extend(
        ["core/bank-only-a.txt", "core/bank-only-b.txt"]
    )
    _dump(manifest_path, manifest)
    proposal = _plan(prepared)
    findings = [
        item
        for item in proposal["review_required"]
        if item["code"] == "BANK_ONLY_WATCH_DECISION"
    ]
    assert len(findings) == 1
    assert findings[0]["paths"] == [
        "core/bank-only-a.txt",
        "core/bank-only-b.txt",
    ]


def test_dirty_worktree_blocks(prepared):
    repo, _, _, _ = prepared
    (repo / "local.tmp").write_text("dirty\n")
    proposal = _plan(prepared)
    assert proposal["status"] == "BLOCKED"
    assert "DIRTY_WORKTREE" in {item["code"] for item in proposal["blocked"]}


def test_stale_registration_and_lock_reject_apply(prepared, tmp_path):
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approve(proposal))

    contracts = yaml.safe_load((registration / "contracts.yaml").read_text())
    contracts["contracts"][0]["title"] = "changed after planning"
    _dump(registration / "contracts.yaml", contracts)
    with pytest.raises(P.StaleProposalError, match="registration inputs changed"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )

    contracts["contracts"][0]["title"] = "A remains available"
    _dump(registration / "contracts.yaml", contracts)
    (registration / ".registration-apply.lock").write_text("held\n")
    with pytest.raises(P.ApplyLockError):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )


def test_digest_and_decision_set_are_exact(prepared, tmp_path):
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)
    approval_data = _approve(proposal)
    approval_data["proposal_digest"] = "sha256:" + "0" * 64
    approval = tmp_path / "approval.yaml"
    _dump(approval, approval_data)

    with pytest.raises(P.StaleProposalError, match="digest"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )


def test_moved_ref_rejects_apply(prepared, tmp_path):
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approve(proposal))
    _git(repo, "checkout", "-q", "custom")
    _commit(
        repo,
        "core/later.txt",
        "later\n",
        "later\n\nCustomization-ID: BANK-OM-001",
    )

    with pytest.raises(P.StaleProposalError, match="custom ref moved"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )


def test_apply_failure_rolls_back_and_removes_lock(
    prepared, tmp_path, monkeypatch
):
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / "proposal"
    P.write_plan(output, proposal, registration=registration)
    approval = tmp_path / "approval.yaml"
    _dump(approval, _approve(proposal))
    real_atomic_write = P._atomic_write
    calls = 0

    def fail_second_write(path, content):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected write failure")
        real_atomic_write(path, content)

    monkeypatch.setattr(P, "_atomic_write", fail_second_write)
    with pytest.raises(OSError, match="injected"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=approval,
        )

    assert (registration / "commit-inventory.yaml").exists() is False
    assert (registration / "current-diff-paths.txt").exists() is False
    assert (registration / ".registration-apply.lock").exists() is False


def test_cli_emits_structured_analysis_error_for_bad_ref(
    prepared, tmp_path, capsys
):
    repo, registration, _, _ = prepared
    exit_code = cli_main(
        [
            "plan",
            "--repo",
            str(repo),
            "--registration",
            str(registration),
            "--patch-ref",
            "missing-ref",
            "--custom-ref",
            "custom",
            "--product-version",
            "1.0.0",
            "--output",
            str(tmp_path / "not-created"),
        ]
    )
    output = capsys.readouterr().out
    assert exit_code == 3
    assert '"status": "ANALYSIS_ERROR"' in output
    assert "Traceback" not in output


def _applied_pair(prepared, tmp_path, name="proposal"):
    """A plan plus its matching approval, ready for apply."""
    repo, registration, _, _ = prepared
    proposal = _plan(prepared)
    output = tmp_path / name
    P.write_plan(output, proposal, registration=registration)
    return repo, registration, output, proposal


def _write(path, value):
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def test_apply_rejects_a_hand_edited_after_manifest(prepared, tmp_path):
    """The digest binds proposal to approval; it must not stand in for origin."""
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    before = (registration / "manifests/BANK-OM-001.yaml").read_bytes()

    tampered = dict(proposal)
    tampered["changes"] = [
        {
            "customization_id": "BANK-OM-001",
            "action": "update_existing",
            "manifest_path": "manifests/BANK-OM-001.yaml",
            "added_changed_paths": [],
            "removed_changed_paths": [],
            "added_watch_paths": [],
            "after_manifest": {
                "schema_version": 2,
                "customization_id": "BANK-OM-001",
                "status": "active",
                "kind": "core-patch",
                "title": "Feature A",
                # A glob would make T40's upper bound unbounded, and dropping
                # required_changed_paths removes its lower bound entirely.
                "implementation": {
                    "changed_paths": ["core/**"],
                    "required_changed_paths": [],
                },
                "upgrade_watch": {"paths": []},
                "assurance": {"contracts": ["CONTRACT-A"], "direct_tests": []},
                "series": {"allowed": False, "depends_on": []},
            },
        }
    ]
    _write(output / "proposal.yaml", tampered)
    # The documented approval-template step recomputes the digest for free.
    _write(output / "approval.yaml", _approve(tampered))

    with pytest.raises(P.StaleProposalError, match="changed_paths do not equal"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=output / "approval.yaml",
        )
    assert (registration / "manifests/BANK-OM-001.yaml").read_bytes() == before


def test_apply_rejects_a_tampered_commit_inventory(prepared, tmp_path):
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    tampered = copy.deepcopy(proposal)
    inventory = tampered["generated"]["commit_inventory"]["customizations"]
    inventory["BANK-OM-001"]["changed_paths"] = ["core/a.txt", "core/ghost.txt"]
    _write(output / "proposal.yaml", tampered)
    _write(output / "approval.yaml", _approve(tampered))

    with pytest.raises(P.StaleProposalError, match="commit inventory"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=output / "approval.yaml",
        )
    assert (registration / "commit-inventory.yaml").exists() is False


def test_apply_rejects_a_proposal_that_breaks_contract_binding(prepared, tmp_path):
    """changed_paths may be honest while the rest of the manifest is not."""
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    tampered = copy.deepcopy(proposal)
    manifest = yaml.safe_load(
        (registration / "manifests/BANK-OM-001.yaml").read_text(encoding="utf-8")
    )
    manifest["assurance"]["contracts"] = []
    tampered["changes"] = [
        {
            "customization_id": "BANK-OM-001",
            "action": "update_existing",
            "manifest_path": "manifests/BANK-OM-001.yaml",
            "added_changed_paths": [],
            "removed_changed_paths": [],
            "added_watch_paths": [],
            "after_manifest": manifest,
        }
    ]
    _write(output / "proposal.yaml", tampered)
    _write(output / "approval.yaml", _approve(tampered))

    with pytest.raises(P.PreparationError, match="inconsistent"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=output / "approval.yaml",
        )


def test_apply_still_accepts_the_unmodified_proposal(prepared, tmp_path):
    """The new derivation check must not reject a genuine plan output."""
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    _write(output / "approval.yaml", _approve(proposal))

    result = P.apply_plan(
        repo,
        registration,
        proposal_path=output / "proposal.yaml",
        approval_path=output / "approval.yaml",
    )

    assert result["status"] == "APPLIED"
    assert "commit-inventory.yaml" in result["written_files"]
    assert (registration / "commit-inventory.yaml").is_file()


def test_policy_refusal_reports_blocked_not_analysis_error(
    prepared, tmp_path, capsys
):
    """A rule that said no is BLOCKED; ANALYSIS_ERROR means we could not judge."""
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    cli_main(
        [
            "approval-template",
            "--proposal", str(output / "proposal.yaml"),
            "--output", str(output / "approval.yaml"),
        ]
    )
    capsys.readouterr()

    exit_code = cli_main(
        [
            "apply",
            "--repo", str(repo),
            "--registration", str(registration),
            "--proposal", str(output / "proposal.yaml"),
            "--approval", str(output / "approval.yaml"),
        ]
    )

    printed = capsys.readouterr().out
    assert exit_code == 1
    assert '"status": "BLOCKED"' in printed
    assert '"code": "POLICY_REFUSED"' in printed
    assert "placeholder approver" in printed
    assert "ANALYSIS_ERROR" not in printed


def _enable_series(registration: Path) -> None:
    path = registration / "manifests/BANK-OM-001.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["series"]["allowed"] = True
    _dump(path, manifest)


def test_reverted_required_path_blocks_and_matches_drift(prepared):
    """prep must not hand READY to a candidate T40's lower bound rejects."""
    from acgh import drift, layout as layout_module

    repo, registration, _, _ = prepared
    _enable_series(registration)
    _git(repo, "checkout", "-q", "custom")
    _commit(repo, "core/a.txt", "vendor\n", "revert\n\nCustomization-ID: BANK-OM-001")

    proposal = _plan(prepared)
    assert proposal["status"] == "BLOCKED"
    assert [f["code"] for f in proposal["blocked"]] == ["REQUIRED_PATH_REVERTED"]

    # The gate that runs later must reach the same conclusion.
    manifests = {
        "BANK-OM-001": yaml.safe_load(
            (registration / "manifests/BANK-OM-001.yaml").read_text(encoding="utf-8")
        )
    }
    violations = drift.check_drift(
        str(repo),
        "patch",
        "custom",
        manifests,
        layout_module.load_layout(registration / "repository-layout.yaml"),
    )
    assert [v.code for v in violations] == [drift.REQUIRED_NET_MISSING]


def test_reverted_optional_path_is_a_question_not_a_block(prepared):
    repo, registration, _, _ = prepared
    _enable_series(registration)
    _git(repo, "checkout", "-q", "custom")
    _commit(repo, "core/b.txt", "extra\n", "add b\n\nCustomization-ID: BANK-OM-001")
    _commit(repo, "core/b.txt", "", "blank b\n\nCustomization-ID: BANK-OM-001")
    (repo / "core/b.txt").write_text("")

    proposal = _plan(prepared)
    assert proposal["blocked"] == []
    assert proposal["status"] == "REVIEW_REQUIRED"


@pytest.mark.parametrize("operation", ["delete", "rename"])
def test_removed_path_is_a_question_not_a_dead_end(prepared, operation):
    """A legitimate delete or rename must leave the operator a next action."""
    repo, registration, _, _ = prepared
    _enable_series(registration)
    _git(repo, "checkout", "-q", "custom")
    if operation == "delete":
        _commit(repo, "core/b.txt", "x\n", "add b\n\nCustomization-ID: BANK-OM-001")
        (repo / "core/b.txt").unlink()
        _git(repo, "add", "-A")
        _git(repo, "commit", "-m", "delete b\n\nCustomization-ID: BANK-OM-001")
    else:
        _git(repo, "mv", "core/a.txt", "core/renamed.txt")
        _git(repo, "commit", "-m", "rename\n\nCustomization-ID: BANK-OM-001")

    proposal = _plan(prepared)

    assert proposal["blocked"] == []
    assert proposal["status"] == "REVIEW_REQUIRED"
    codes = [item["code"] for item in proposal["review_required"]]
    assert "REMOVED_PATH_DECISION" in codes
    # One question per removed path, not one per detection rule.
    assert codes.count("REMOVED_PATH_DECISION") == 1


def test_stale_lock_identifies_its_owner(prepared, tmp_path, monkeypatch):
    """A killed apply cannot clean up, so the lock must say who to ask."""
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    _write(output / "approval.yaml", _approve(proposal))

    captured: dict[str, bytes] = {}
    real_write = P._atomic_write

    def capture_then_fail(path, content):
        captured["lock"] = (registration / ".registration-apply.lock").read_bytes()
        raise OSError("disk full")

    monkeypatch.setattr(P, "_atomic_write", capture_then_fail)
    with pytest.raises(OSError):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=output / "approval.yaml",
        )
    monkeypatch.setattr(P, "_atomic_write", real_write)

    owner = yaml.safe_load(captured["lock"].decode("utf-8"))
    assert owner["proposal_digest"] == P.proposal_digest(proposal)
    assert owner["pid"] and owner["host"] and owner["started_at"]
    assert owner["registration"] == registration.name
    # The failure path still releases the lock.
    assert (registration / ".registration-apply.lock").exists() is False


def test_sensitive_zone_policy_change_invalidates_the_approval(prepared, tmp_path):
    """The approver judged under a policy; changing it must not be silent."""
    repo, registration, output, proposal = _applied_pair(prepared, tmp_path)
    _write(output / "approval.yaml", _approve(proposal))

    _dump(registration / "sensitive-zones.yaml", {"zones": {"frozen": ["core/**"]}})

    with pytest.raises(P.StaleProposalError, match="registration inputs changed"):
        P.apply_plan(
            repo,
            registration,
            proposal_path=output / "proposal.yaml",
            approval_path=output / "approval.yaml",
        )
