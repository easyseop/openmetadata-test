"""T29 real kb_openmetadata registration integrity tests."""
from pathlib import Path

import yaml

from acgh import contracts
from acgh import layout
from acgh import manifest
from acgh import registry
from acgh import verdict

_HARNESS = Path(__file__).parents[1]
_REGISTRATION = _HARNESS / "registrations" / "kb-openmetadata"


def _load_all():
    layout_policy = layout.load_layout(
        _HARNESS / "policies" / "repository-layout.yaml"
    )
    reg = registry.load_registry(
        _REGISTRATION / "customization-registry.yaml"
    )
    catalog = contracts.load_catalog(_REGISTRATION / "contracts.yaml")
    loaded = []
    for entry in reg.entries:
        path = _REGISTRATION / entry.manifest
        loaded.append((str(path), yaml.safe_load(path.read_text(encoding="utf-8"))))
    validated = manifest.validate_manifest_set(loaded, layout_policy)
    return reg, catalog, {
        item["customization_id"]: item for item in validated
    }


def test_nine_real_customizations_form_closed_registry():
    reg, catalog, manifests = _load_all()
    assert reg.active_ids() == tuple(
        f"BANK-OM-{number:03d}" for number in range(1, 10)
    )
    assert len(catalog.ids()) == 7
    assert reg.source_snapshot_ids() == tuple(
        f"BANK-OM-{number:03d}" for number in range(1, 8)
    )
    assert reg.by_id()["BANK-OM-008"].provenance == "candidate-follow-up"
    assert reg.by_id()["BANK-OM-009"].provenance == "candidate-follow-up"
    registry.validate_references(reg, manifests, catalog)


def test_registration_pins_reproducible_source_comparison():
    reg, _, _ = _load_all()
    assert reg.source["snapshot_sha"] == (
        "2c2347043235aa2a4ecba4729774c770fcee5d67"
    )
    assert reg.source["upstream_sha"] == (
        "afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9"
    )
    assert reg.source["changed_path_count"] == 113
    assert reg.source["ancestry_preserved"] is False


def test_every_registration_has_required_path_and_contract():
    reg, catalog, manifests = _load_all()
    for customization_id in reg.active_ids():
        item = manifests[customization_id]
        assert item["implementation"]["required_changed_paths"]
        assert contracts.effective_tests(item, catalog)


def test_every_source_diff_path_is_registered_or_explicitly_blocked():
    reg, _, manifests = _load_all()
    inventory_path = _REGISTRATION / reg.source["diff_inventory"]
    paths = [
        line.strip()
        for line in inventory_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(paths) == reg.source["changed_path_count"] == 113
    assert len(paths) == len(set(paths))

    findings = {
        item["path"]: item for item in reg.source["unregistered_findings"]
    }
    assert set(findings) == {
        ".claude/settings.json",
        "docker/development/docker-compose.yml",
    }
    assert all(item["disposition"] == "block" for item in findings.values())

    specs = {
        customization_id: layout.make_spec(
            item["implementation"]["allowed_changed_paths"]
        )
        for customization_id, item in manifests.items()
    }
    uncovered = {
        path for path in paths
        if not any(spec.match_file(path) for spec in specs.values())
    }
    assert uncovered == set(findings)


def test_real_snapshot_readiness_is_honestly_blocked():
    reg, _, _ = _load_all()
    result = registry.check_registry_readiness(reg)
    assert result.verdict == verdict.BLOCK
    assert "does not preserve upstream ancestry" in result.reasons[0]
    assert any(".claude/settings.json" in reason for reason in result.reasons)
    assert any("docker/development/docker-compose.yml" in reason for reason in result.reasons)
    assert sum("owner is not assigned" in reason for reason in result.reasons) == 9
