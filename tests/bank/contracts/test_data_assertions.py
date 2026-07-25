"""CONTRACT-DATA-ASSERTIONS live projection implementation."""

from _runtime_contract import ApiClient, encoded, required_env


def test_failed_assertion_projection():
    client = ApiClient.from_env()
    fqn = required_env("BANK_FAILED_ASSERTION_FQN")
    test_case = client.get(
        "/v1/dataQuality/testCases/name/"
        f"{encoded(fqn)}?fields=owners,testCaseResult,testDefinition,testSuite"
    )

    result = test_case.get("testCaseResult") or {}
    assert result.get("testCaseStatus") == "Failed"
    assert test_case.get("owners"), "failed assertion must expose an owner"
    entity_link = test_case.get("entityLink", "")
    assert "<#E::table::" in entity_link
    assert (
        "::columns::" in entity_link
        or test_case.get("testDefinition", {}).get("id")
    )
