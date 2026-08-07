"""CONTRACT-QUERY-REPORT live usage-link implementation."""

from __future__ import annotations

import uuid

from _runtime_contract import ApiClient, required_env, wait_for


def test_query_usage_roundtrip():
    client = ApiClient.from_env()
    query_id = required_env("BANK_CONTRACT_QUERY_ID")
    suffix = uuid.uuid4().hex[:12]
    name = f"contract_query_report_{suffix}"
    payload = {
        "name": name,
        "displayName": "Contract Query Report",
        "reportType": "Contract",
    }
    created = client.post("/v1/queryReports", payload)
    report_id = created["id"]
    try:
        linked = client.put(
            f"/v1/queries/{query_id}/usage",
            [{"id": report_id, "type": "queryReport"}],
        )
        linked_query_id = (
            linked.get("entityId")
            or (linked.get("entity") or {}).get("id")
            or linked.get("id")
        )
        assert linked_query_id == query_id

        def usage_hit():
            result = client.get(
                "/v1/queries"
                f"?entityId={report_id}&entityType=queryReport&limit=100"
            )
            return next(
                (
                    query
                    for query in result.get("data", [])
                    if query.get("id") == query_id
                ),
                None,
            )

        assert wait_for(usage_hit)["id"] == query_id
        updated = client.put(
            "/v1/queryReports",
            dict(payload, displayName="Contract Query Report Updated"),
        )
        assert updated["id"] == report_id
        assert wait_for(usage_hit)["id"] == query_id
    finally:
        client.delete(
            f"/v1/queryReports/{report_id}?hardDelete=true&recursive=true"
        )
