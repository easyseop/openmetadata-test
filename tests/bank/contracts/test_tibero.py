"""CONTRACT-TIBERO-CONNECTOR implementation."""

from _connector_contract import assert_connection_schema_roundtrip


def test_connection_schema_roundtrip():
    assert_connection_schema_roundtrip(
        connector="Tibero",
        schema_stem="tibero",
        type_definition="tiberoType",
        scheme_definition="tiberoScheme",
        scheme="tibero+pyodbc",
        required={"hostPort", "username", "database"},
    )
