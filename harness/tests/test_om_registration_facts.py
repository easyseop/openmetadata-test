from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from acgh.integrations.om.collectors import OpenMetadataPlanAdapter
from acgh.integrations.om.collectors import _registration_metadata
from acgh.plancore.errors import PlanControlError
from acgh.verdict import canonical_digest


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _product_repo(path: Path) -> tuple[Path, str]:
    path.mkdir()
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "facts@example.invalid")
    _git(path, "config", "user.name", "Facts Test")
    (path / "base.txt").write_text("base\n", encoding="utf-8")
    _git(path, "add", "base.txt")
    _git(path, "commit", "-q", "-m", "base")
    return path, _git(path, "rev-parse", "HEAD")


def _write_registration(root: Path, *, reverse: bool = False) -> Path:
    manifests = root / "manifests"
    manifests.mkdir(parents=True)
    entries = [
        {
            "customization_id": "BANK-OM-001",
            "contracts": ["CONTRACT-A"],
            "manifest": "manifests/BANK-OM-001.yaml",
        },
        {
            "customization_id": "BANK-OM-002",
            "contracts": ["CONTRACT-B"],
            "manifest": "manifests/BANK-OM-002.yaml",
        },
    ]
    contract_rows = [
        {
            "id": "CONTRACT-A",
            "required_tests": ["tests/contracts_a.py::test_roundtrip"],
            "customization_ids": ["BANK-OM-001"],
        },
        {
            "id": "CONTRACT-B",
            "required_tests": ["tests/contracts_b.py::test_roundtrip"],
            "customization_ids": ["BANK-OM-002"],
        },
    ]
    manifest_rows = {
        "BANK-OM-001": {
            "customization_id": "BANK-OM-001",
            "implementation": {
                "changed_paths": ["product/shared.py", "product/a.py"],
                "required_changed_paths": ["product/a.py"],
            },
            "assurance": {
                "contracts": ["CONTRACT-A"],
                "direct_tests": ["tests/direct_a.py::test_guard"],
            },
        },
        "BANK-OM-002": {
            "customization_id": "BANK-OM-002",
            "implementation": {
                "changed_paths": ["product/b.py", "product/shared.py"],
                "required_changed_paths": ["product/b.py"],
            },
            "assurance": {
                "contracts": ["CONTRACT-B"],
                "direct_tests": [],
            },
        },
    }
    if reverse:
        entries.reverse()
        contract_rows.reverse()
        for manifest in manifest_rows.values():
            manifest["implementation"]["changed_paths"].reverse()
            manifest["implementation"]["required_changed_paths"].reverse()
            manifest["assurance"]["contracts"].reverse()
            manifest["assurance"]["direct_tests"].reverse()

    (root / "customization-registry.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "entries": entries}, sort_keys=False),
        encoding="utf-8",
    )
    (root / "contracts.yaml").write_text(
        yaml.safe_dump(
            {"schema_version": 1, "contracts": contract_rows}, sort_keys=False
        ),
        encoding="utf-8",
    )
    (root / "shared-path-owners.yaml").write_text(
        yaml.safe_dump(
            {"product/shared.py": ["BANK-OM-001", "BANK-OM-002"]},
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    for customization_id, manifest in manifest_rows.items():
        (manifests / f"{customization_id}.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
        )
    return root


def _fact_values(registration: Path, product: Path, head: str) -> dict[str, object]:
    facts = OpenMetadataPlanAdapter().collect_facts(
        {"mode": "feature", "repositories": {"product": str(product)}},
        {"custom_baseline": head},
        registration,
        {},
    )
    return {fact["fact_id"]: fact["value"] for fact in facts}


def test_a4_relations_preserve_per_id_paths_contracts_and_tests(tmp_path: Path):
    registration = _write_registration(tmp_path / "registration")
    product, head = _product_repo(tmp_path / "product")
    facts = _fact_values(registration, product, head)

    assert facts["customization-relations"] == [
        {
            "customization_id": "BANK-OM-001",
            "changed_paths": ["product/a.py", "product/shared.py"],
            "required_changed_paths": ["product/a.py"],
            "contracts": ["CONTRACT-A"],
            "tests": [
                "tests/contracts_a.py::test_roundtrip",
            ],
        },
        {
            "customization_id": "BANK-OM-002",
            "changed_paths": ["product/b.py", "product/shared.py"],
            "required_changed_paths": ["product/b.py"],
            "contracts": ["CONTRACT-B"],
            "tests": ["tests/contracts_b.py::test_roundtrip"],
        },
    ]
    assert facts["contract-tests"] == {
        "CONTRACT-A": ["tests/contracts_a.py::test_roundtrip"],
        "CONTRACT-B": ["tests/contracts_b.py::test_roundtrip"],
    }
    assert facts["id-contract-consistency"] == {
        "consistent": True,
        "divergences": [],
    }

    assert facts["registered-customizations"] == ["BANK-OM-001", "BANK-OM-002"]
    assert facts["registered-customization-paths"] == [
        "product/a.py",
        "product/b.py",
        "product/shared.py",
    ]
    assert facts["registered-contracts"] == ["CONTRACT-A", "CONTRACT-B"]
    assert facts["registered-tests"] == [
        "tests/contracts_a.py::test_roundtrip",
        "tests/contracts_b.py::test_roundtrip",
    ]
    assert "tests/direct_a.py::test_guard" not in {
        test_id
        for relation in facts["customization-relations"]
        for test_id in relation["tests"]
    }
    registered_tests = set(facts["registered-tests"])
    assert all(
        set(relation["tests"]) <= registered_tests
        for relation in facts["customization-relations"]
    )
    assert facts["shared-path-owners"] == {
        "product/shared.py": ["BANK-OM-001", "BANK-OM-002"]
    }


def test_a4_new_facts_have_the_required_ids_and_kinds(tmp_path: Path):
    registration = _write_registration(tmp_path / "registration")
    product, head = _product_repo(tmp_path / "product")
    facts = OpenMetadataPlanAdapter().collect_facts(
        {"mode": "feature", "repositories": {"product": str(product)}},
        {"custom_baseline": head},
        registration,
        {},
    )
    by_id = {fact["fact_id"]: fact for fact in facts}

    assert by_id["customization-relations"]["kind"] == "customization_relations"
    assert by_id["contract-tests"]["kind"] == "contract_tests"
    assert by_id["id-contract-consistency"]["kind"] == "id_contract_consistency"


def test_a4_relation_fact_digest_ignores_source_order(tmp_path: Path):
    first = _write_registration(tmp_path / "first")
    second = _write_registration(tmp_path / "second", reverse=True)
    product, head = _product_repo(tmp_path / "product")
    fact_ids = {
        "customization-relations",
        "contract-tests",
        "id-contract-consistency",
    }

    first_facts = OpenMetadataPlanAdapter().collect_facts(
        {"mode": "feature", "repositories": {"product": str(product)}},
        {"custom_baseline": head},
        first,
        {},
    )
    second_facts = OpenMetadataPlanAdapter().collect_facts(
        {"mode": "feature", "repositories": {"product": str(product)}},
        {"custom_baseline": head},
        second,
        {},
    )
    first_new = [fact for fact in first_facts if fact["fact_id"] in fact_ids]
    second_new = [fact for fact in second_facts if fact["fact_id"] in fact_ids]

    assert canonical_digest(first_new) == canonical_digest(second_new)


@pytest.mark.parametrize(
    "source",
    [
        "registry",
        "manifest.assurance.contracts",
        "contracts.yaml.customization_ids",
    ],
)
def test_a4_consistency_reports_each_single_source_divergence(
    tmp_path: Path, source: str
):
    registration = _write_registration(tmp_path / "registration")
    if source == "registry":
        path = registration / "customization-registry.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["entries"][0]["contracts"] = ["CONTRACT-B"]
    elif source == "manifest.assurance.contracts":
        path = registration / "manifests" / "BANK-OM-001.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["assurance"]["contracts"] = ["CONTRACT-B"]
    else:
        path = registration / "contracts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["contracts"][0]["customization_ids"] = ["BANK-OM-002"]
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    consistency = _registration_metadata(registration)["id_contract_consistency"]

    assert consistency["consistent"] is False
    if source == "registry":
        assert {
            divergence["source"] for divergence in consistency["divergences"]
        } == {
            "manifest.assurance.contracts",
            "contracts.yaml.customization_ids",
        }
    else:
        assert any(
            divergence["source"] == source
            for divergence in consistency["divergences"]
        )


@pytest.mark.parametrize("failure", ["missing", "escape"])
def test_a4_invalid_manifest_path_keeps_existing_error_code(
    tmp_path: Path, failure: str
):
    registration = _write_registration(tmp_path / "registration")
    registry_path = registration / "customization-registry.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if failure == "missing":
        (registration / registry["entries"][0]["manifest"]).unlink()
    else:
        registry["entries"][0]["manifest"] = "../outside.yaml"
        registry_path.write_text(
            yaml.safe_dump(registry, sort_keys=False), encoding="utf-8"
        )

    with pytest.raises(PlanControlError) as caught:
        _registration_metadata(registration)

    assert caught.value.code == "REGISTRATION_MANIFEST_PATH_INVALID"
