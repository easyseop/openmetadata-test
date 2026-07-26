"""Independent health probes for deployed T61 counterfactual experiments."""

from _browser_contract import browser_storage_state, sync_playwright_or_fail
from _runtime_contract import ApiClient, encoded, required_env


def test_api_health():
    """Prove the authenticated API remains responsive."""
    result = ApiClient.from_env().get("/v1/users?limit=1")
    assert isinstance(result, dict)
    assert isinstance(result.get("data"), list)


def test_query_fixture_health():
    """Prove the fixed Query fixture exists independently of QueryReport."""
    query_id = required_env("BANK_CONTRACT_QUERY_ID")
    query = ApiClient.from_env().get(f"/v1/queries/{encoded(query_id)}")
    assert query.get("id") == query_id


def test_failed_assertion_fixture_health():
    """Prove the fixed failed assertion data remains healthy."""
    fqn = required_env("BANK_FAILED_ASSERTION_FQN")
    test_case = ApiClient.from_env().get(
        "/v1/dataQuality/testCases/name/"
        f"{encoded(fqn)}?fields=owners,testCaseResult"
    )
    assert (test_case.get("testCaseResult") or {}).get(
        "testCaseStatus"
    ) == "Failed"
    assert test_case.get("owners")


def test_authenticated_ui_health():
    """Prove a separate authenticated UI route renders a stable marker."""
    page_url = required_env("BANK_RUNTIME_UI_HEALTH_URL")
    test_id = required_env("BANK_RUNTIME_UI_HEALTH_TEST_ID")
    sync_playwright = sync_playwright_or_fail()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=browser_storage_state())
        page = context.new_page()
        page.goto(page_url, wait_until="domcontentloaded")
        page.get_by_test_id(test_id).first.wait_for(state="visible")
        context.close()
        browser.close()
