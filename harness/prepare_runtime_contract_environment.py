#!/usr/bin/env python3
"""Create the local fixtures and private environment file for runtime Contracts."""

from __future__ import annotations

import argparse
import base64
import json
import os
import shlex
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright


def call(
    base_api: str,
    method: str,
    endpoint: str,
    token: str | None = None,
    payload: dict | None = None,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        base_api + endpoint, data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"{method} {endpoint}: HTTP {exc.code}: {body}"
        ) from exc


def login(base_api: str, email: str, password: str) -> str:
    result = call(
        base_api,
        "POST",
        "/auth/login",
        payload={
            "email": email,
            "password": base64.b64encode(password.encode()).decode(),
        },
    )
    token = result.get("accessToken")
    if not token:
        raise RuntimeError("로그인 응답에 accessToken이 없습니다.")
    return token


def get_or_create(
    base_api: str,
    token: str,
    get_endpoint: str,
    post_endpoint: str,
    payload: dict,
) -> dict:
    try:
        return call(base_api, "GET", get_endpoint, token)
    except RuntimeError as exc:
        if "HTTP 404" not in str(exc):
            raise
    return call(base_api, "POST", post_endpoint, token, payload)


def prepare_fixtures(base_api: str, token: str) -> dict[str, str]:
    admin = call(base_api, "GET", "/users/name/admin", token)
    owner = {"id": admin["id"], "type": "user"}
    service = get_or_create(
        base_api,
        token,
        "/services/databaseServices/name/bank_contract_runtime",
        "/services/databaseServices",
        {
            "name": "bank_contract_runtime",
            "displayName": "BANK Contract Runtime",
            "description": "Local fixture service for BANK-OM runtime contracts.",
            "serviceType": "Mysql",
            "owners": [owner],
        },
    )
    database = get_or_create(
        base_api,
        token,
        "/databases/name/bank_contract_runtime.bank_contract_db",
        "/databases",
        {
            "name": "bank_contract_db",
            "displayName": "BANK Contract DB",
            "service": service["fullyQualifiedName"],
            "owners": [owner],
        },
    )
    schema = get_or_create(
        base_api,
        token,
        "/databaseSchemas/name/bank_contract_runtime.bank_contract_db.bank_contract_schema",
        "/databaseSchemas",
        {
            "name": "bank_contract_schema",
            "displayName": "BANK Contract Schema",
            "database": database["fullyQualifiedName"],
            "owners": [owner],
        },
    )
    table = get_or_create(
        base_api,
        token,
        "/tables/name/bank_contract_runtime.bank_contract_db.bank_contract_schema.bank_contract_table?fields=columns",
        "/tables",
        {
            "name": "bank_contract_table",
            "displayName": "BANK Contract Table",
            "description": "Local fixture table for BANK-OM runtime contracts.",
            "databaseSchema": schema["fullyQualifiedName"],
            "owners": [owner],
            "columns": [
                {
                    "name": "bank_contract_column",
                    "displayName": "BANK Contract Column",
                    "dataType": "STRING",
                    "dataTypeDisplay": "varchar(255)",
                    "dataLength": 255,
                    "constraint": "NOT_NULL",
                    "ordinalPosition": 1,
                    "extension": {
                        "attributeName": "contractAttribute",
                        "instanceName": "contractInstance",
                        "infoType": "contractInfo",
                    },
                }
            ],
        },
    )
    query = get_or_create(
        base_api,
        token,
        "/queries/name/bank_contract_runtime.bank_contract_query",
        "/queries",
        {
            "name": "bank_contract_query",
            "displayName": "BANK Contract Query",
            "description": "Local QueryReport runtime fixture.",
            "query": "SELECT bank_contract_column FROM bank_contract_table",
            "query_type": "SELECT",
            "service": service["fullyQualifiedName"],
            "owners": [owner],
        },
    )

    table_fqn = table["fullyQualifiedName"]
    column_name = "bank_contract_column"
    test_case_name = "bank_contract_column_not_null"
    test_case_fqn = f"{table_fqn}.{column_name}.{test_case_name}"
    encoded_fqn = urllib.parse.quote(test_case_fqn, safe="")
    test_case = get_or_create(
        base_api,
        token,
        f"/dataQuality/testCases/name/{encoded_fqn}?fields=owners,testCaseResult,testDefinition,testSuite",
        "/dataQuality/testCases",
        {
            "name": test_case_name,
            "displayName": "BANK Contract Failed Assertion",
            "description": "Local failed assertion fixture for BANK-OM runtime contracts.",
            "testDefinition": "columnValuesToBeNotNull",
            "entityLink": f"<#E::table::{table_fqn}::columns::{column_name}>",
            "owners": [owner],
            "parameterValues": [],
        },
    )
    test_case_fqn = test_case["fullyQualifiedName"]
    current = call(
        base_api,
        "GET",
        "/dataQuality/testCases/name/"
        + urllib.parse.quote(test_case_fqn, safe="")
        + "?fields=owners,testCaseResult,testDefinition,testSuite",
        token,
    )
    if (current.get("testCaseResult") or {}).get("testCaseStatus") != "Failed":
        call(
            base_api,
            "POST",
            "/dataQuality/testCases/testCaseResults/"
            + urllib.parse.quote(test_case_fqn, safe=""),
            token,
            {
                "timestamp": int(time.time() * 1000),
                "testCaseStatus": "Failed",
                "result": "Intentional local failure for BANK-OM runtime contract.",
                "testResultValue": [],
                "passedRows": 0,
                "failedRows": 1,
            },
        )
    return {
        "BANK_CONTRACT_QUERY_ID": query["id"],
        "BANK_FAILED_ASSERTION_FQN": test_case_fqn,
        "BANK_COLUMN_TABLE_FQN": table_fqn,
        "BANK_COLUMN_NAME": column_name,
    }


def browser_state(base_url: str, email: str, password: str) -> dict:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(f"{base_url}/signin", wait_until="domcontentloaded")
        page.locator('input[type="text"]').fill(email)
        page.locator('input[type="password"]').fill(password)
        page.locator('button[type="submit"]').click()
        page.wait_for_url(f"{base_url}/my-data", timeout=30_000)
        state = context.storage_state(indexed_db=True)
        context.close()
        browser.close()
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8585")
    parser.add_argument("--product-repo", type=Path, required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    email = os.environ["OM_LOCAL_ADMIN_EMAIL"]
    password = os.environ["OM_LOCAL_ADMIN_PASSWORD"]
    base_url = args.base_url.rstrip("/")
    base_api = f"{base_url}/api/v1"
    token = login(base_api, email, password)
    fixtures = prepare_fixtures(base_api, token)
    state = browser_state(base_url, email, password)
    state_b64 = base64.b64encode(
        json.dumps(state, separators=(",", ":")).encode()
    ).decode()
    values = {
        "OPENMETADATA_BASE_URL": f"{base_url}/api",
        "OPENMETADATA_AUTH_TOKEN": token,
        "OPENMETADATA_PRODUCT_REPO": str(args.product_repo.resolve(strict=True)),
        **fixtures,
        "BANK_IME_EDITOR_URL": f"{base_url}/metrics/add-metric",
        "BANK_DATA_ASSERTIONS_URL": f"{base_url}/data_assertions",
        "BANK_COLUMN_UI_URL": f"{base_url}/table/{fixtures['BANK_COLUMN_TABLE_FQN']}",
        "BANK_BROWSER_STORAGE_STATE_B64": state_b64,
        "DEPLOYED_ARTIFACT_DIGEST": args.artifact_digest,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(
            f"export {key}={shlex.quote(value)}" for key, value in values.items()
        )
        + "\n",
        encoding="utf-8",
    )
    args.output.chmod(0o600)
    print(
        json.dumps(
            {
                "status": "ready",
                "output": str(args.output),
                "field_count": len(values),
                "secret_values_printed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
