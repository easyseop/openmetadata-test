"""CONTRACT-BANK-COLUMN-VIEW API and rendered projection implementation."""

import os

import pytest

from _browser_contract import browser_storage_state, sync_playwright_or_fail
from _runtime_contract import ApiClient, encoded, required_env


def _extended_column():
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
    return column


def test_extended_column_projection():
    column = _extended_column()
    assert isinstance(column.get("ordinalPosition"), int)
    assert column.get("constraint") is not None
    extension = column.get("extension") or {}
    for key in ("attributeName", "instanceName", "infoType"):
        assert key in extension, f"missing bank column extension: {key}"


def test_extended_column_rendered_row():
    """Match the API extension values to the customized schema table row."""
    page_url = os.environ.get("BANK_COLUMN_UI_URL")
    if not page_url:
        pytest.skip("BANK_COLUMN_UI_URL is required for the browser contract")

    column = _extended_column()
    extension = column.get("extension") or {}
    expected = []
    for key in ("attributeName", "instanceName", "infoType"):
        value = extension.get(key)
        assert value, f"bank column extension must be non-empty: {key}"
        expected.append(str(value))

    sync_playwright = sync_playwright_or_fail()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=browser_storage_state())
        page = context.new_page()
        page.goto(page_url, wait_until="domcontentloaded")
        table = page.get_by_test_id("entity-table")
        table.wait_for(state="visible")
        row = (
            table.get_by_role("row")
            .filter(has_text=str(column["name"]))
            .first
        )
        row.wait_for(state="visible")
        rendered = row.inner_text()
        for value in expected:
            assert value in rendered
        context.close()
        browser.close()
