from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from acgh import shared_code
from acgh import shared_code_migration as M
from acgh import structural_review as S


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo, message):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", message)
    return _git(repo, "rev-parse", "HEAD")


def _write_functional(path, *, sha, role, test_id, absence_only=False):
    path.write_text(json.dumps({
        "schema_version": 1,
        "evidence_kind": "functional_test",
        "subject_sha": sha,
        "subject_role": role,
        "verdict": "pass",
        "test_id": test_id,
        "asserts_behavior": f"{test_id} behavior remains available",
        "command": ["pytest", "-q", test_id],
        "absence_only": absence_only,
    }), encoding="utf-8")


def _fixture(tmp_path, *, refactored=False):
    repo = tmp_path / "product"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "old.ts").write_text(
        "export const MOVED = makeValue(BANK_MODE);\n"
    )
    (repo / "absorbed.ts").write_text("export const LEGACY = 1;\n")
    base = _commit(repo, "base")

    _git(repo, "switch", "-qc", "custom", base)
    (repo / "custom.txt").write_text("bank branch\n")
    custom = _commit(repo, "custom")

    _git(repo, "switch", "-qc", "target", base)
    (repo / "old.ts").unlink()
    (repo / "absorbed.ts").unlink()
    moved_mode = "OFFICIAL_MODE" if refactored else "BANK_MODE"
    (repo / "new.ts").write_text(
        f"export const MOVED = makeValue({moved_mode});\n"
    )
    (repo / "official.ts").write_text("export const OFFICIAL_BEHAVIOR = true;\n")
    target = _commit(repo, "target")

    _git(repo, "switch", "-qc", "candidate", target)
    (repo / "candidate.txt").write_text("resolved\n")
    candidate = _commit(repo, "candidate")

    registration = tmp_path / "registration-1.0"
    (registration / "manifests").mkdir(parents=True)
    (registration / "repository-layout.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "upstream_base_sha": base,
        "path_grammar": {"negation_allowed": False},
        "upstream_owned_roots": ["**"],
        "bank_governance_roots": [],
        "platform_extension_roots": [],
        "unknown_path_policy": "analysis_error",
    }), encoding="utf-8")
    (registration / "sensitive-zones.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "zones": {},
    }), encoding="utf-8")
    (registration / "manifests/BANK-OM-004.yaml").write_text(yaml.safe_dump({
        "schema_version": 2,
        "customization_id": "BANK-OM-004",
        "status": "active",
        "kind": "core-patch",
        "title": "migration fixture",
        "implementation": {
            "changed_paths": ["old.ts", "absorbed.ts"],
            "required_changed_paths": ["old.ts", "absorbed.ts"],
        },
        "upgrade_watch": {"paths": ["old.ts", "absorbed.ts"]},
        "assurance": {"contracts": [], "direct_tests": []},
        "series": {"allowed": False, "depends_on": []},
    }), encoding="utf-8")
    catalog_payload = {
        "schema_version": 1,
        "definitions": [
            {
                "path": "old.ts",
                "customization_id": "BANK-OM-004",
                "assertions": [{
                    "id": "moved",
                    "matcher": "code_fragment",
                    "fragment": "export const MOVED = makeValue(BANK_MODE);",
                }],
            },
            {
                "path": "absorbed.ts",
                "customization_id": "BANK-OM-004",
                "assertions": [{
                    "id": "legacy",
                    "matcher": "code_fragment",
                    "fragment": "export const LEGACY = 1;",
                }],
            },
        ],
    }
    (registration / "shared-code-definitions.yaml").write_text(
        yaml.safe_dump(catalog_payload, sort_keys=False), encoding="utf-8"
    )
    (registration / "shared-path-owners.yaml").write_text(yaml.safe_dump({
        "old.ts": ["BANK-OM-004"],
        "absorbed.ts": ["BANK-OM-004"],
    }), encoding="utf-8")
    (registration / "customization-registry.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "source": {"shared_code_definitions": "shared-code-definitions.yaml"},
        "entries": [],
    }), encoding="utf-8")

    manifests = {
        "BANK-OM-004": yaml.safe_load(
            (registration / "manifests/BANK-OM-004.yaml").read_text(encoding="utf-8")
        )
    }
    review = S.build_review(str(repo), base, target, custom, candidate, manifests)
    catalog = shared_code.parse_catalog(catalog_payload)
    relocation = S.find_relocations(
        str(repo), candidate, catalog, review["review_surface_paths"]
    )
    relocation["applicable"] = True
    structural_evidence = {
        "structural_review": review,
        "relocation_review": relocation,
    }
    moved_evidence = tmp_path / "moved-test.json"
    absorbed_evidence = tmp_path / "absorbed-test.json"
    _write_functional(
        moved_evidence,
        sha=candidate,
        role="candidate",
        test_id="BANK-OM-004-MOVED",
    )
    _write_functional(
        absorbed_evidence,
        sha=target,
        role="official_target",
        test_id="BANK-OM-004-ABSORBED",
    )
    decisions = {
        "BANK-OM-004:old.ts": {
            "disposition": M.RELOCATED,
            "proposed_new_path": "new.ts",
            "functional_evidence": str(moved_evidence),
        },
        "BANK-OM-004:absorbed.ts": {
            "disposition": M.ABSORBED,
            "functional_evidence": str(absorbed_evidence),
        },
    }
    if refactored:
        decisions["BANK-OM-004:old.ts"]["proposed_assertions"] = [{
            "id": "moved-refactored",
            "matcher": "code_fragment",
            "fragment": "export const MOVED = makeValue(OFFICIAL_MODE);",
        }]
    return (
        repo, registration, base, target, candidate,
        structural_evidence, decisions, moved_evidence, absorbed_evidence,
    )


def _proposal(fixture):
    (
        repo, registration, _base, target, candidate,
        structural_evidence, decisions, _moved, _absorbed,
    ) = fixture
    return M.build_proposal(
        repo=str(repo),
        source_registration=registration,
        source_version="1.0",
        target_version="1.1",
        candidate_ref=candidate,
        upstream_target_ref=target,
        structural_evidence=structural_evidence,
        decisions=decisions,
        harness_commit="a" * 40,
        harness_digest="sha256:" + "b" * 64,
    )


def test_versioned_migration_updates_catalog_and_owners_together(tmp_path):
    fixture = _fixture(tmp_path)
    proposal = _proposal(fixture)
    template = M.approval_template(proposal)
    assert template["approval_confirmed"] is False
    template.update({
        "approval_confirmed": True,
        "approver": "데이터플랫폼 승인자",
        "approved_at": "2026-08-09T10:00:00Z",
        "rationale": "기능 test와 공식 흡수 근거 확인",
        "approval_source": "review/123",
    })
    repo, registration, *_ = fixture
    target_registration = tmp_path / "registration-1.1"
    before_catalog = (registration / "shared-code-definitions.yaml").read_bytes()
    result = M.apply_proposal(
        repo=str(repo),
        source_registration=registration,
        target_registration=target_registration,
        proposal=proposal,
        approval=template,
        harness_commit="a" * 40,
        harness_digest="sha256:" + "b" * 64,
    )

    assert result["status"] == "created"
    assert (registration / "shared-code-definitions.yaml").read_bytes() == before_catalog
    catalog = shared_code.load_catalog(target_registration / "shared-code-definitions.yaml")
    owners = yaml.safe_load(
        (target_registration / "shared-path-owners.yaml").read_text(encoding="utf-8")
    )
    assert catalog.pairs() == {("new.ts", "BANK-OM-004")}
    assert owners == {"new.ts": ["BANK-OM-004"]}
    record = yaml.safe_load(
        (target_registration / "shared-code-migration-record.yaml").read_text(encoding="utf-8")
    )
    assert {item["disposition"] for item in record["items"]} == {
        M.RELOCATED, M.ABSORBED
    }


def test_migration_rejects_unconfirmed_or_tampered_approval_and_proposal(tmp_path):
    fixture = _fixture(tmp_path)
    proposal = _proposal(fixture)
    template = M.approval_template(proposal)
    repo, registration, *_ = fixture
    with pytest.raises(M.MigrationError, match="approval_confirmed"):
        M.apply_proposal(
            repo=str(repo),
            source_registration=registration,
            target_registration=tmp_path / "target",
            proposal=proposal,
            approval=template,
            harness_commit="a" * 40,
            harness_digest="sha256:" + "b" * 64,
        )
    tampered = dict(proposal)
    tampered["target_registration_version"] = "9.9"
    with pytest.raises(M.MigrationError, match="proposal digest mismatch"):
        M.approval_template(tampered)


def test_absorbed_definition_requires_positive_official_behavior_evidence(tmp_path):
    fixture = list(_fixture(tmp_path))
    target = fixture[3]
    absorbed_evidence = fixture[8]
    _write_functional(
        absorbed_evidence,
        sha=target,
        role="official_target",
        test_id="ABSENCE-ONLY",
        absence_only=True,
    )
    with pytest.raises(M.MigrationError, match="absence-only"):
        _proposal(tuple(fixture))


def test_migration_rejects_changed_functional_evidence_and_harness(tmp_path):
    fixture = _fixture(tmp_path)
    proposal = _proposal(fixture)
    approval = M.approval_template(proposal)
    approval.update({
        "approval_confirmed": True,
        "approver": "승인자",
        "approved_at": "2026-08-09T10:00:00Z",
        "rationale": "검토",
        "approval_source": "review/1",
    })
    repo, registration, *_rest, moved_evidence, _absorbed = fixture
    with pytest.raises(M.MigrationError, match="harness_commit"):
        M.apply_proposal(
            repo=str(repo), source_registration=registration,
            target_registration=tmp_path / "wrong-harness",
            proposal=proposal, approval=approval,
            harness_commit="c" * 40,
            harness_digest="sha256:" + "b" * 64,
        )
    moved_evidence.write_text("{}", encoding="utf-8")
    with pytest.raises(M.MigrationError, match="functional evidence changed"):
        M.apply_proposal(
            repo=str(repo), source_registration=registration,
            target_registration=tmp_path / "changed-evidence",
            proposal=proposal, approval=approval,
            harness_commit="a" * 40,
            harness_digest="sha256:" + "b" * 64,
        )


def test_refactored_relocation_requires_and_binds_new_assertions(tmp_path):
    fixture = _fixture(tmp_path, refactored=True)
    proposal = _proposal(fixture)
    relocated = next(
        item for item in proposal["items"] if item["disposition"] == M.RELOCATED
    )
    assert relocated["candidate_evidence_strength"] == "symbol_overlap"
    assert relocated["assertions"][0]["id"] == "moved-refactored"

    fixture_without_assertions = list(fixture)
    fixture_without_assertions[6] = copy.deepcopy(fixture[6])
    fixture_without_assertions[6]["BANK-OM-004:old.ts"].pop("proposed_assertions")
    with pytest.raises(M.MigrationError, match="requires proposed_assertions"):
        _proposal(tuple(fixture_without_assertions))
