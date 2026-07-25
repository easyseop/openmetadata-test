"""T92 explicit retirement transition tests."""
import copy

import pytest

from acgh import registry as G
from acgh import retirement as R
from acgh import verdict as V

_CANDIDATE = "a" * 40
_TEST_DIGEST = "sha256:" + "b" * 64


def _registry_data():
    return {
        "schema_version": 1,
        "source": {
            "repository": "bank/vendor",
            "snapshot_sha": "c" * 40,
            "upstream_repository": "open-metadata/OpenMetadata",
            "upstream_tag": "1.13.1-release",
            "upstream_sha": "d" * 40,
            "changed_path_count": 1,
            "ancestry_preserved": True,
            "diff_inventory": "source-diff-paths.txt",
            "unregistered_findings": [],
            "limitations": [],
        },
        "entries": [{
            "customization_id": "BANK-OM-001",
            "title": "x",
            "owner": "team-x",
            "owner_status": "assigned",
            "status": "active",
            "criticality": "high",
            "manifest": "manifests/BANK-OM-001.yaml",
            "contracts": ["CONTRACT-X"],
        }],
    }


def _manifest():
    return {
        "schema_version": 1,
        "customization_id": "BANK-OM-001",
        "status": "active",
        "kind": "core-patch",
        "implementation": {"allowed_changed_paths": ["core/x"]},
    }


def _record():
    return {
        "schema_version": 1,
        "customization_id": "BANK-OM-001",
        "from_status": "active",
        "to_status": "retired",
        "upstream_replacement": {
            "repository": "open-metadata/OpenMetadata",
            "commit_sha": "e" * 40,
            "reference": "official feature replaces bank patch",
        },
        "adr_path": "docs/adr/ADR-009-retire-x.md",
        "removal_candidate_sha": _CANDIDATE,
        "removal_result_digest": "sha256:" + "f" * 64,
        "contract_test_run_set_digest": _TEST_DIGEST,
        "checks": {
            "official_replacement_verified": True,
            "required_contract_tests_passed": True,
            "removal_regression_passed": True,
            "active_effect_absent": True,
        },
        "approved_by": ["owner", "platform"],
    }


def _entry():
    return G.parse_registry(_registry_data()).entries[0]


def test_verified_active_customization_can_retire():
    result = R.check_retirement(
        _record(),
        registry_entry=_entry(),
        manifest=_manifest(),
        candidate_sha=_CANDIDATE,
        test_run_set_digest=_TEST_DIGEST,
    )
    assert result.verdict == V.PASS
    assert "no empty placeholder" in result.reasons[-1]


def test_missing_replacement_or_regression_proof_is_analysis_error():
    record = _record()
    record["checks"]["official_replacement_verified"] = False
    assert R.check_retirement(
        record,
        registry_entry=_entry(),
        manifest=_manifest(),
        candidate_sha=_CANDIDATE,
        test_run_set_digest=_TEST_DIGEST,
    ).verdict == V.ANALYSIS_ERROR


def test_stale_candidate_or_test_evidence_is_analysis_error():
    result = R.check_retirement(
        _record(),
        registry_entry=_entry(),
        manifest=_manifest(),
        candidate_sha="0" * 40,
        test_run_set_digest=_TEST_DIGEST,
    )
    assert result.verdict == V.ANALYSIS_ERROR
    result = R.check_retirement(
        _record(),
        registry_entry=_entry(),
        manifest=_manifest(),
        candidate_sha=_CANDIDATE,
        test_run_set_digest="sha256:" + "0" * 64,
    )
    assert result.verdict == V.ANALYSIS_ERROR


def test_retired_or_wrong_id_state_cannot_transition_again():
    data = _registry_data()
    data["entries"][0]["status"] = "retired"
    entry = G.parse_registry(data).entries[0]
    assert R.check_retirement(
        _record(),
        registry_entry=entry,
        manifest=_manifest(),
        candidate_sha=_CANDIDATE,
        test_run_set_digest=_TEST_DIGEST,
    ).verdict == V.BLOCK

    record = _record()
    record["customization_id"] = "BANK-OM-002"
    assert R.check_retirement(
        record,
        registry_entry=_entry(),
        manifest=_manifest(),
        candidate_sha=_CANDIDATE,
        test_run_set_digest=_TEST_DIGEST,
    ).verdict == V.BLOCK


def test_apply_transition_updates_registry_and_manifest_copies():
    registry_data = _registry_data()
    manifest = _manifest()
    updated_registry, updated_manifest = R.apply_retirement_state(
        registry_data, manifest, _record()
    )
    assert updated_registry["entries"][0]["status"] == "retired"
    assert updated_manifest["status"] == "retired"
    assert registry_data["entries"][0]["status"] == "active"
    assert manifest["status"] == "active"


def test_unsafe_adr_path_and_one_person_approval_rejected():
    record = _record()
    record["adr_path"] = "../escape.md"
    with pytest.raises(R.RetirementError, match="adr_path"):
        R.validate_retirement_record(record)
    record = copy.deepcopy(_record())
    record["approved_by"] = ["owner"]
    with pytest.raises(R.RetirementError, match="schema"):
        R.validate_retirement_record(record)
