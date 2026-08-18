"""CONTRACT-SYBASE-CONNECTOR implementation."""

from _connector_contract import assert_connection_schema_roundtrip


def test_connection_schema_roundtrip():
    assert_connection_schema_roundtrip(
        connector="Sybase",
        schema_stem="sybase",
        type_definition="sybaseType",
        scheme_definition="sybaseScheme",
        scheme="sybase+pyodbc",
        required={"type"},
    )
