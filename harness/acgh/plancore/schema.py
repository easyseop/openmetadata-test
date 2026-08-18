"""Schema loading and canonical payload helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path

import jsonschema
import yaml

from acgh.verdict import canonical_digest
from acgh.plancore.errors import PlanControlError

SCHEMA_DIR = Path(__file__).parent / "schema"


def schema_path(name: str) -> Path:
    return SCHEMA_DIR / f"plan-{name}.schema.json"


def load_schema(name: str) -> dict:
    path = schema_path(name)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanControlError(
            "SCHEMA_UNAVAILABLE",
            f"cannot load schema {name!r}: {exc}",
            details={"schema": str(path)},
        ) from exc


def validate(name: str, data: object) -> None:
    schema = load_schema(name)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    errors = sorted(
        validator_cls(schema).iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if not errors:
        return
    rendered = []
    for error in errors:
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        rendered.append({"field": location, "message": error.message})
    raise PlanControlError(
        "SCHEMA_INVALID",
        f"{name} does not match its schema",
        details={"issues": rendered},
    )


def read_data(path: str | Path) -> dict:
    source = Path(path)
    try:
        if source.suffix == ".json":
            value = json.loads(source.read_text(encoding="utf-8"))
        else:
            value = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise PlanControlError(
            "INPUT_UNREADABLE",
            f"cannot read {source}: {exc}",
            details={"path": str(source)},
        ) from exc
    if not isinstance(value, dict):
        raise PlanControlError(
            "INPUT_NOT_MAPPING",
            f"expected a mapping in {source}",
            details={"path": str(source)},
        )
    return value


def canonical_payload_digest(data: dict) -> str:
    payload = data.get("canonical_payload")
    if not isinstance(payload, dict):
        raise PlanControlError(
            "CANONICAL_PAYLOAD_MISSING",
            "canonical_payload must be a mapping",
        )
    return canonical_digest(payload)


def atomic_write(path: str | Path, data: dict) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.suffix == ".json":
        rendered = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    else:
        rendered = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    temporary = destination.with_name(f".{destination.name}.tmp.{os.getpid()}")
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        0o644,
    )
    try:
        os.write(descriptor, rendered.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, destination)
    return destination
