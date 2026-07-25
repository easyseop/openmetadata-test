"""T90 — executor-neutral upgrade test orchestration contract.

Docker/Kubernetes jobs may perform the work, but they cannot choose which
stages count.  This module defines the complete required stage set and binds
the resulting evidence to the same candidate artifact and T62 test-run set.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "upgrade-test-run.schema.json"
REQUIRED_STAGES = (
    "restore-production-snapshot",
    "migration",
    "row-reconciliation",
    "reindex",
    "ingestion",
    "differential-authentication",
    "differential-authorization",
    "differential-api",
    "differential-relations",
    "differential-search",
    "differential-ingestion",
    "rollback-drill",
)


class UpgradeRunError(ValueError):
    """Upgrade test result is structurally invalid."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def validate_upgrade_run(data: dict) -> dict:
    if not isinstance(data, dict):
        raise UpgradeRunError("upgrade test run is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise UpgradeRunError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )
    names = [stage["name"] for stage in data["stages"]]
    if len(names) != len(set(names)):
        raise UpgradeRunError("duplicate upgrade test stage")
    return data


def load_upgrade_run(path) -> dict:
    return validate_upgrade_run(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def upgrade_run_digest(data: dict) -> str:
    item = validate_upgrade_run(data)
    canonical = dict(item)
    canonical["stages"] = sorted(
        item["stages"], key=lambda stage: stage["name"]
    )
    return verdict.canonical_digest(canonical)


def check_upgrade_run(
    data,
    *,
    candidate_lock,
    test_run_set,
    name: str = "upgrade-test-orchestration",
) -> verdict.GateResult:
    try:
        run = validate_upgrade_run(data)
    except UpgradeRunError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"invalid upgrade evidence: {exc}",)
        )

    stale = []
    if run["candidate"]["commit_sha"] != candidate_lock.candidate.commit_sha:
        stale.append("candidate SHA")
    if (
        run["candidate"]["artifact_digest"]
        != candidate_lock.candidate.artifact_digest
    ):
        stale.append("candidate artifact")
    if run["test_run_set_digest"] != test_run_set.digest():
        stale.append("test run set")
    if stale:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"stale upgrade run: {field} mismatch" for field in stale),
        )

    by_name = {stage["name"]: stage for stage in run["stages"]}
    missing = [stage for stage in REQUIRED_STAGES if stage not in by_name]
    reasons = [f"required upgrade stage missing: {stage}" for stage in missing]
    failed = []
    for stage in REQUIRED_STAGES:
        if stage in by_name and by_name[stage]["outcome"] != "pass":
            outcome = by_name[stage]["outcome"]
            failed.append(stage)
            reasons.append(f"upgrade stage {stage}: outcome={outcome}")
    if missing or failed:
        return verdict.GateResult(name, verdict.BLOCK, tuple(reasons))
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"old={run['old_version']}",
            f"new={run['new_version']}",
            f"stages_passed={len(REQUIRED_STAGES)}",
            f"upgrade_run_digest={upgrade_run_digest(run)}",
        ),
    )
