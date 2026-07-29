"""T29 — customization registry loader and cross-reference validator."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = (
    Path(__file__).parent / "schema" / "customization-registry.schema.json"
)


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class RegistryEntry:
    customization_id: str
    title: str
    owner: str
    owner_status: str
    status: str
    criticality: str
    manifest: str
    contracts: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class Registry:
    source: dict
    entries: tuple[RegistryEntry, ...]

    def active_ids(self) -> tuple[str, ...]:
        return tuple(
            entry.customization_id
            for entry in self.entries
            if entry.status == "active"
        )

    def source_snapshot_ids(self) -> tuple[str, ...]:
        """Active IDs imported from the pinned source snapshot.

        Candidate hardening can introduce a separately registered follow-up
        without pretending that it existed in the original root snapshot.
        """
        return tuple(
            entry.customization_id
            for entry in self.entries
            if entry.status == "active"
            and entry.provenance == "source-snapshot"
        )

    def by_id(self) -> dict[str, RegistryEntry]:
        return {entry.customization_id: entry for entry in self.entries}


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def parse_registry(data: dict) -> Registry:
    if not isinstance(data, dict):
        raise RegistryError("customization registry is not a mapping")
    errs = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errs:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise RegistryError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errs)
        )

    entries = tuple(
        RegistryEntry(
            customization_id=item["customization_id"],
            title=item["title"],
            owner=item["owner"],
            owner_status=item["owner_status"],
            status=item["status"],
            criticality=item["criticality"],
            manifest=item["manifest"],
            contracts=tuple(item["contracts"]),
            provenance=item["provenance"],
        )
        for item in data["entries"]
    )
    ids = [entry.customization_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise RegistryError("duplicate customization_id in registry")
    manifests = [entry.manifest for entry in entries]
    if len(manifests) != len(set(manifests)):
        raise RegistryError("one manifest is assigned to multiple registry entries")
    findings = [
        item["path"] for item in data["source"]["unregistered_findings"]
    ]
    if len(findings) != len(set(findings)):
        raise RegistryError("duplicate unregistered finding path")
    return Registry(source=dict(data["source"]), entries=entries)


def load_registry(path) -> Registry:
    return parse_registry(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def validate_references(
    registry: Registry,
    manifests_by_id: dict,
    contract_catalog,
) -> None:
    """Ensure registry, manifests, and contract catalog form one closed graph."""
    errors = []
    for entry in registry.entries:
        manifest = manifests_by_id.get(entry.customization_id)
        if manifest is None:
            errors.append(f"{entry.customization_id}: manifest not loaded")
            continue
        if manifest.get("customization_id") != entry.customization_id:
            errors.append(
                f"{entry.customization_id}: manifest customization_id mismatch"
            )
        if manifest.get("status", "active") != entry.status:
            errors.append(
                f"{entry.customization_id}: registry/manifest status mismatch"
            )
        manifest_contracts = set(
            manifest.get("assurance", {}).get("contracts", [])
        )
        if manifest_contracts != set(entry.contracts):
            errors.append(
                f"{entry.customization_id}: registry/manifest contract mismatch"
            )
        for contract_id in entry.contracts:
            contract = contract_catalog.get(contract_id)
            if contract is None:
                errors.append(
                    f"{entry.customization_id}: unknown contract {contract_id}"
                )
            elif entry.customization_id not in contract.customization_ids:
                errors.append(
                    f"{entry.customization_id}: {contract_id} lacks reverse binding"
                )
    if errors:
        raise RegistryError("; ".join(errors))


def check_registry_readiness(
    registry: Registry,
    *,
    name: str = "customization-registry-readiness",
) -> verdict.GateResult:
    """Block a release while inventory, ownership, or lineage is unresolved."""
    reasons = []
    if not registry.source["ancestry_preserved"]:
        reasons.append("source snapshot does not preserve upstream ancestry")
    for item in registry.source["unregistered_findings"]:
        if item["disposition"] in {"block", "remove", "register"}:
            reasons.append(
                f"unregistered {item['classification']} path "
                f"{item['path']}: disposition={item['disposition']}"
            )
    for entry in registry.entries:
        if entry.owner_status != "assigned":
            reasons.append(
                f"{entry.customization_id}: owner is not assigned"
            )
    if reasons:
        return verdict.GateResult(name, verdict.BLOCK, tuple(reasons))
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"registered_customizations={len(registry.entries)}",
            "ancestry, inventory, and ownership are resolved",
        ),
    )
