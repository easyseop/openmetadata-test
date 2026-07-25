"""T92 — explicit customization retirement instead of empty placeholders."""
from __future__ import annotations

import copy
import json
from pathlib import Path, PurePosixPath

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "retirement-record.schema.json"


class RetirementError(ValueError):
    """Retirement evidence is malformed."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def validate_retirement_record(data: dict) -> dict:
    if not isinstance(data, dict):
        raise RetirementError("retirement record is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise RetirementError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )
    adr = PurePosixPath(data["adr_path"])
    if adr.is_absolute() or ".." in adr.parts or adr.suffix.lower() != ".md":
        raise RetirementError("adr_path must be a safe relative Markdown path")
    return data


def load_retirement_record(path) -> dict:
    return validate_retirement_record(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def check_retirement(
    record,
    *,
    registry_entry,
    manifest: dict,
    candidate_sha: str,
    test_run_set_digest: str,
    name: str = "customization-retirement",
) -> verdict.GateResult:
    try:
        item = validate_retirement_record(record)
    except RetirementError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"invalid retirement evidence: {exc}",)
        )

    customization_id = item["customization_id"]
    if registry_entry.customization_id != customization_id:
        return verdict.GateResult(
            name, verdict.BLOCK, ("retirement targets a different registry ID",)
        )
    if manifest.get("customization_id") != customization_id:
        return verdict.GateResult(
            name, verdict.BLOCK, ("retirement targets a different manifest ID",)
        )
    if registry_entry.status != "active":
        return verdict.GateResult(
            name, verdict.BLOCK, ("registry entry is not active",)
        )
    if manifest.get("status", "active") != "active":
        return verdict.GateResult(
            name, verdict.BLOCK, ("manifest is not active",)
        )

    stale = []
    if item["removal_candidate_sha"] != candidate_sha:
        stale.append("removal candidate SHA")
    if item["contract_test_run_set_digest"] != test_run_set_digest:
        stale.append("contract test run set")
    if stale:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"stale retirement record: {field} mismatch" for field in stale),
        )
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"retire={customization_id}",
            "official replacement and removal regression verified",
            "active set must exclude retired ID; no empty placeholder commit",
        ),
    )


def apply_retirement_state(
    registry_data: dict,
    manifest: dict,
    record: dict,
) -> tuple[dict, dict]:
    """Return state-updated copies after a caller has passed check_retirement."""
    item = validate_retirement_record(record)
    customization_id = item["customization_id"]
    updated_registry = copy.deepcopy(registry_data)
    matches = [
        entry for entry in updated_registry.get("entries", [])
        if entry.get("customization_id") == customization_id
    ]
    if len(matches) != 1:
        raise RetirementError(
            f"registry must contain exactly one {customization_id} entry"
        )
    if matches[0].get("status") != "active":
        raise RetirementError("registry entry is not active")
    if manifest.get("customization_id") != customization_id:
        raise RetirementError("manifest customization_id mismatch")
    if manifest.get("status", "active") != "active":
        raise RetirementError("manifest is not active")
    matches[0]["status"] = "retired"
    updated_manifest = copy.deepcopy(manifest)
    updated_manifest["status"] = "retired"
    return updated_registry, updated_manifest
