"""CONTRACT-DATA-ASSERTIONS API and rendered projection implementation."""

import os
import re

import pytest

from _browser_contract import browser_storage_state, sync_playwright_or_fail
from _runtime_contract import ApiClient, encoded, required_env


def _failed_assertion():
    client = ApiClient.from_env()
    fqn = required_env("BANK_FAILED_ASSERTION_FQN")
    return client.get(
        "/v1/dataQuality/testCases/name/"
        f"{encoded(fqn)}?fields=owners,testCaseResult,testDefinition,testSuite"
    )


def test_failed_assertion_projection():
    test_case = _failed_assertion()
    result = test_case.get("testCaseResult") or {}
    assert result.get("testCaseStatus") == "Failed"
    assert test_case.get("owners"), "failed assertion must expose an owner"
    entity_link = test_case.get("entityLink", "")
    assert "<#E::table::" in entity_link
    assert (
        "::columns::" in entity_link
        or test_case.get("testDefinition", {}).get("id")
    )


def test_failed_assertion_rendered_row():
    """Match the API truth to the row rendered by the customized page."""
    page_url = os.environ.get("BANK_DATA_ASSERTIONS_URL")
    if not page_url:
        pytest.skip(
            "BANK_DATA_ASSERTIONS_URL is required for the browser contract"
        )

    test_case = _failed_assertion()
    result = test_case.get("testCaseResult") or {}
    assert result.get("testCaseStatus") == "Failed"
    owners = test_case.get("owners") or []
    assert owners, "failed assertion must expose an owner"
    owner = owners[0].get("displayName") or owners[0].get("name")
    assert owner

    entity_link = test_case.get("entityLink", "")
    match = re.fullmatch(
        r"<#E::table::(?P<table>.+?)::columns::(?P<column>.+?)>",
        entity_link,
    )
    assert match, f"column-level entityLink is required: {entity_link}"
    table_name = match.group("table").split(".")[-1]
    column_name = match.group("column").split(".")[-1]

    sync_playwright = sync_playwright_or_fail()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=browser_storage_state())
        page = context.new_page()
        page.goto(page_url, wait_until="domcontentloaded")
        row = (
            page.get_by_role("row")
            .filter(has_text=table_name)
            .filter(has_text=column_name)
            .first
        )
        row.wait_for(state="visible")
        rendered = row.inner_text()
        assert "Failed" in rendered
        assert owner in rendered
        context.close()
        browser.close()
