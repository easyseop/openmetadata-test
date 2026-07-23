"""T60 (+ T04) — contract catalog + contract↔test binding (SRS 부칙 A-3.3).

A contract is a business invariant (e.g. "userId가 같아도 tenant가 다르면 다른
사용자") plus the tests that prove it. The catalog is the single source of truth
for those invariants; a manifest only *references* contract IDs and may add
non-contract technical tests (direct_tests).

The load-bearing rule (부칙 A-3.3): effective tests = direct_tests ∪
contract-derived required_tests. A test declared BOTH as a direct test and as a
contract's required test is a duplicate-declaration inconsistency -> block (it
must be owned in exactly one place). A reference to an unknown contract -> block.

Without this, a release only checks that test IDs *exist* (계층 3 '필수 테스트
존재') but never ties them to *which business rule* they defend — so no one knows
what is actually guaranteed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "contract-catalog.schema.json"


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Contract:
    id: str
    title: str
    required_tests: tuple[str, ...]
    customization_ids: tuple[str, ...] = ()


class Catalog:
    def __init__(self, contracts):
        self._by_id: dict[str, Contract] = {}
        for c in contracts:
            if c.id in self._by_id:
                raise ContractError(f"duplicate contract id: {c.id}")
            self._by_id[c.id] = c

    def __contains__(self, cid: str) -> bool:
        return cid in self._by_id

    def get(self, cid: str) -> Contract | None:
        return self._by_id.get(cid)

    def ids(self) -> set[str]:
        return set(self._by_id)


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def parse_catalog(data: dict) -> Catalog:
    if not isinstance(data, dict):
        raise ContractError("contract catalog is not a mapping")
    errs = sorted(
        _schema_validator().iter_errors(data),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    if errs:
        loc = lambda e: "/".join(str(p) for p in e.absolute_path) or "<root>"
        raise ContractError("schema: " + "; ".join(f"{loc(e)}: {e.message}" for e in errs))
    contracts = [
        Contract(
            id=c["id"],
            title=c["title"],
            required_tests=tuple(c["required_tests"]),
            customization_ids=tuple(c.get("customization_ids", [])),
        )
        for c in data["contracts"]
    ]
    return Catalog(contracts)  # raises on duplicate ids


def load_catalog(path) -> Catalog:
    return parse_catalog(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def effective_tests(manifest: dict, catalog: Catalog) -> set[str]:
    """Resolve a manifest's assurance to its effective test set, or raise.

    direct ∪ contract-derived, after enforcing: referenced contracts exist,
    and direct/contract-derived do not overlap (부칙 A-3.3).
    """
    assurance = manifest.get("assurance", {})
    refs = list(assurance.get("contracts", []))
    direct = list(assurance.get("direct_tests", []))

    unknown = [cid for cid in refs if cid not in catalog]
    if unknown:
        raise ContractError(f"manifest references unknown contract(s): {sorted(unknown)}")

    derived: set[str] = set()
    for cid in refs:
        derived |= set(catalog.get(cid).required_tests)

    overlap = set(direct) & derived
    if overlap:
        raise ContractError(
            f"test declared both as direct and contract-derived: {sorted(overlap)}"
        )
    return set(direct) | derived


def check_binding(manifest: dict, catalog: Catalog,
                  name: str = "contract-binding") -> verdict.GateResult:
    """Gate result for one manifest's contract binding."""
    try:
        tests = effective_tests(manifest, catalog)
    except ContractError as e:
        return verdict.GateResult(name, verdict.BLOCK, (str(e),))
    return verdict.GateResult(
        name, verdict.PASS, (f"effective tests: {len(tests)}",)
    )
