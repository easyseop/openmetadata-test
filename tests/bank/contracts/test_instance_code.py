"""CONTRACT-INSTANCE-CODE live CRUD and search implementation."""

from __future__ import annotations

import uuid

from _runtime_contract import ApiClient, encoded, wait_for


def test_crud_search_roundtrip():
    client = ApiClient.from_env()
    suffix = uuid.uuid4().hex[:12]
    name = f"contract_instance_code_{suffix}"
    payload = {
        "name": name,
        "codeGroup": "CONTRACT",
        "codeValue": suffix,
        "codeName": "before",
        "active": True,
    }
    created = client.post("/v1/instanceCodes", payload)
    entity_id = created["id"]
    try:
        fetched = client.get(f"/v1/instanceCodes/{entity_id}")
        assert fetched["codeGroup"] == payload["codeGroup"]
        assert fetched["codeValue"] == payload["codeValue"]

        updated_payload = dict(payload, codeName="after")
        updated = client.put("/v1/instanceCodes", updated_payload)
        assert updated["id"] == entity_id
        assert updated["codeName"] == "after"

        def search_hit():
            result = client.get(
                "/v1/search/query"
                f"?index=instance_code_search_index&q={encoded(name)}"
            )
            hits = result.get("hits", {}).get("hits", [])
            return next(
                (
                    hit
                    for hit in hits
                    if hit.get("_source", {}).get("id") == entity_id
                ),
                None,
            )

        hit = wait_for(search_hit)
        assert hit["_source"]["codeGroup"] == payload["codeGroup"]
        assert hit["_source"]["codeValue"] == payload["codeValue"]
    finally:
        client.delete(
            f"/v1/instanceCodes/{entity_id}?hardDelete=true&recursive=true"
        )
