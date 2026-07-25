"""Cross-layer source contract shared by the bank database connectors."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
from jsonschema import Draft7Validator


def _product_root() -> Path:
    value = os.environ.get("OPENMETADATA_PRODUCT_REPO")
    if not value:
        pytest.skip("OPENMETADATA_PRODUCT_REPO is not set")
    root = Path(value).resolve()
    if not (root / ".git").exists():
        pytest.fail(f"not an OpenMetadata Git checkout: {root}")
    return root


def _read(root: Path, relative: str) -> str:
    path = root / relative
    assert path.is_file(), f"missing product path: {relative}"
    return path.read_text(encoding="utf-8")


def _load(root: Path, relative: str) -> dict:
    return json.loads(_read(root, relative))


def _refs(value) -> set[str]:
    if isinstance(value, dict):
        found = {value["$ref"]} if "$ref" in value else set()
        for child in value.values():
            found.update(_refs(child))
        return found
    if isinstance(value, list):
        found: set[str] = set()
        for child in value:
            found.update(_refs(child))
        return found
    return set()


def _enum_body(source: str, enum_name: str) -> str:
    match = re.search(
        rf"export enum {re.escape(enum_name)} \{{(?P<body>.*?)\n\}}",
        source,
        re.DOTALL,
    )
    assert match, f"missing generated enum: {enum_name}"
    return match.group("body")


def assert_connection_schema_roundtrip(
    *,
    connector: str,
    schema_stem: str,
    type_definition: str,
    scheme_definition: str,
    scheme: str,
    required: set[str],
) -> None:
    root = _product_root()
    connector_rel = (
        "openmetadata-spec/src/main/resources/json/schema/entity/services/"
        f"connections/database/{schema_stem}Connection.json"
    )
    schema = _load(root, connector_rel)
    Draft7Validator.check_schema(schema)

    assert schema["title"] == f"{connector}Connection"
    assert schema["definitions"][type_definition]["enum"] == [connector]
    assert schema["definitions"][type_definition]["default"] == connector
    assert schema["definitions"][scheme_definition]["enum"] == [scheme]
    assert schema["properties"]["type"]["default"] == connector
    assert set(schema["required"]) == required

    payload = {
        "type": connector,
        "scheme": scheme,
        "username": "contract-user",
        "password": "contract-password",
        "hostPort": "db.internal:1234",
        "database": "metadata",
    }
    Draft7Validator(schema).validate(payload)
    assert json.loads(json.dumps(payload)) == payload
    invalid = dict(payload, type="WrongConnector")
    assert list(Draft7Validator(schema).iter_errors(invalid))

    service_schema = _load(
        root,
        "openmetadata-spec/src/main/resources/json/schema/entity/services/"
        "databaseService.json",
    )
    assert (
        f"./connections/database/{schema_stem}Connection.json"
        in _refs(service_schema)
    )

    create_service = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/generated/api/services/"
        "createDatabaseService.ts",
    )
    database_service = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/generated/entity/services/"
        "databaseService.ts",
    )
    service_connection = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/generated/entity/services/"
        "connections/serviceConnection.ts",
    )
    connector_generated = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/generated/entity/services/"
        f"connections/database/{schema_stem}Connection.ts",
    )
    selector = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/utils/"
        "DatabaseServiceUtils.tsx",
    )
    selector_test = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/utils/"
        "DatabaseServiceUtils.test.tsx",
    )
    icon_util = _read(
        root,
        "openmetadata-ui/src/main/resources/ui/src/utils/ServiceIconUtils.ts",
    )

    assert f"export interface {connector}Connection" in connector_generated
    for generated in (create_service, database_service):
        assert f"{connector} Database" in generated
        assert re.search(rf"\b{connector}\s*=\s*\"{connector}\"", generated)
        assert scheme in generated
    assert re.search(
        rf"\b{connector}\s*=\s*\"{connector}\"",
        _enum_body(service_connection, "ConfigType"),
    )
    assert f"case DatabaseServiceType.{connector}" in selector
    assert f"{schema_stem}Connection" in selector
    assert f"getDatabaseConfig(DatabaseServiceType.{connector})" in selector_test
    assert f"toStrictEqual({schema_stem}Connection)" in selector_test
    assert f"{schema_stem}Icon from" in icon_util
    assert f"{schema_stem}: {schema_stem}Icon" in icon_util
    assert (
        root
        / "openmetadata-ui/src/main/resources/ui/src/assets/svg/"
        f"service-icon-{schema_stem}.svg"
    ).is_file()
