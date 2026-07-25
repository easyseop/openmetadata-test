"""CONTRACT-BANK-COLUMN-VIEW live metadata projection implementation."""

from _runtime_contract import ApiClient, encoded, required_env


def test_extended_column_projection():
    client = ApiClient.from_env()
    table_fqn = required_env("BANK_COLUMN_TABLE_FQN")
    column_name = required_env("BANK_COLUMN_NAME")
    table = client.get(
        f"/v1/tables/name/{encoded(table_fqn)}?fields=columns"
    )
    column = next(
        (
            item
            for item in table.get("columns", [])
            if item.get("name") == column_name
        ),
        None,
    )

    assert column is not None, f"column not found: {column_name}"
    assert isinstance(column.get("ordinalPosition"), int)
    assert column.get("constraint") is not None
    extension = column.get("extension") or {}
    for key in ("attributeName", "instanceName", "infoType"):
        assert key in extension, f"missing bank column extension: {key}"
