#!/usr/bin/env python3
"""Create reusable mock database metadata through the OpenMetadata API.

This does not connect to the named database engines.  It registers catalog
metadata in OpenMetadata and waits until every example table is searchable.
Running the command again reuses entities with the same fully-qualified names.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ENGINES = (
    ("oracle", "Oracle", "Oracle"),
    ("tibero", "Tibero", "Tibero"),
    ("sybase", "Sybase", "Sybase"),
    ("db2", "Db2", "DB2"),
    ("postgres", "Postgres", "PostgreSQL"),
)

TABLES = (
    {
        "name": "customer",
        "displayName": "고객",
        "description": "화면 및 검색 확인용 고객 목 메타데이터입니다.",
        "columns": [
            ("customer_id", "고객 ID", "BIGINT", "bigint", "PRIMARY_KEY"),
            ("customer_name", "고객명", "STRING", "varchar(100)", "NOT_NULL"),
            ("created_at", "등록 시각", "TIMESTAMP", "timestamp", "NULL"),
        ],
    },
    {
        "name": "account_transaction",
        "displayName": "계좌 거래",
        "description": "화면 및 검색 확인용 계좌 거래 목 메타데이터입니다.",
        "columns": [
            ("transaction_id", "거래 ID", "BIGINT", "bigint", "PRIMARY_KEY"),
            ("customer_id", "고객 ID", "BIGINT", "bigint", "NOT_NULL"),
            ("amount", "거래 금액", "DECIMAL", "decimal(18,2)", "NOT_NULL"),
            ("transaction_at", "거래 시각", "TIMESTAMP", "timestamp", "NOT_NULL"),
        ],
    },
)


class ApiError(RuntimeError):
    """An OpenMetadata API call failed."""


def api_call(
    base_api: str,
    method: str,
    endpoint: str,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        base_api.rstrip("/") + endpoint,
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ApiError(f"{method} {endpoint}: HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(f"{method} {endpoint}: OpenMetadata 연결 실패: {exc}") from exc


def login(base_api: str, email: str, password: str) -> str:
    result = api_call(
        base_api,
        "POST",
        "/auth/login",
        payload={
            "email": email,
            "password": base64.b64encode(password.encode("utf-8")).decode("ascii"),
        },
    )
    token = result.get("accessToken")
    if not token:
        raise ApiError("로그인 응답에 accessToken이 없습니다.")
    return str(token)


def by_name_endpoint(collection: str, fqn: str, fields: str = "") -> str:
    suffix = f"?fields={fields}" if fields else ""
    return f"/{collection}/name/{urllib.parse.quote(fqn, safe='')}{suffix}"


def get_or_create(
    base_api: str,
    token: str,
    collection: str,
    fqn: str,
    payload: dict[str, Any],
    fields: str = "",
) -> tuple[dict[str, Any], str]:
    try:
        entity = api_call(
            base_api,
            "GET",
            by_name_endpoint(collection, fqn, fields),
            token,
        )
        return entity, "existing"
    except ApiError as exc:
        if "HTTP 404" not in str(exc):
            raise
    return api_call(base_api, "POST", f"/{collection}", token, payload), "created"


def columns_for(table: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for position, (name, display_name, data_type, display_type, constraint) in enumerate(
        table["columns"], start=1
    ):
        column: dict[str, Any] = {
            "name": name,
            "displayName": display_name,
            "dataType": data_type,
            "dataTypeDisplay": display_type,
            "ordinalPosition": position,
        }
        if constraint != "NULL":
            column["constraint"] = constraint
        result.append(column)
    return result


def wait_for_search(
    base_api: str,
    token: str,
    table_ids: set[str],
    timeout_seconds: int,
) -> set[str]:
    deadline = time.monotonic() + timeout_seconds
    found: set[str] = set()
    while time.monotonic() < deadline:
        result = api_call(
            base_api,
            "GET",
            "/search/query?index=table_search_index&q=%2A&from=0&size=100",
            token,
        )
        hits = result.get("hits", {}).get("hits", [])
        found = {
            str(hit.get("_source", {}).get("id"))
            for hit in hits
            if str(hit.get("_source", {}).get("id")) in table_ids
        }
        if found == table_ids:
            return found
        time.sleep(2)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="5종 DB의 목 메타데이터를 OpenMetadata API로 등록합니다."
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENMETADATA_BASE_URL", "http://127.0.0.1:8585/api/v1"),
        help="OpenMetadata API 주소",
    )
    parser.add_argument(
        "--email",
        default=os.getenv("OPENMETADATA_EMAIL", "admin@open-metadata.org"),
        help="로그인 이메일",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("OPENMETADATA_PASSWORD", "admin"),
        help="로그인 비밀번호(환경 변수 OPENMETADATA_PASSWORD 사용 권장)",
    )
    parser.add_argument(
        "--prefix",
        default="bank_mock",
        help="생성할 서비스 이름의 접두어",
    )
    parser.add_argument("--output", type=Path, help="비밀정보를 제외한 JSON 결과 파일")
    parser.add_argument("--search-timeout", type=int, default=60)
    args = parser.parse_args()

    token = login(args.base_url, args.email, args.password)
    admin = api_call(args.base_url, "GET", "/users/name/admin", token)
    owner = {"id": admin["id"], "type": "user"}
    records: list[dict[str, Any]] = []
    table_ids: set[str] = set()
    test_case_count = 0

    for key, service_type, label in ENGINES:
        service_name = f"{args.prefix}_{key}"
        database_name = f"{key}_bank"
        schema_name = "banking"
        service, service_state = get_or_create(
            args.base_url,
            token,
            "services/databaseServices",
            service_name,
            {
                "name": service_name,
                "displayName": f"{label} 목 데이터",
                "description": f"실제 {label} 연결 없이 화면과 검색을 검증하는 목 서비스입니다.",
                "serviceType": service_type,
                "owners": [owner],
            },
        )
        database_fqn = f"{service_name}.{database_name}"
        database, database_state = get_or_create(
            args.base_url,
            token,
            "databases",
            database_fqn,
            {
                "name": database_name,
                "displayName": f"{label} 은행 DB",
                "description": f"{label} 예시 데이터베이스입니다.",
                "service": service["fullyQualifiedName"],
                "owners": [owner],
            },
        )
        schema_fqn = f"{database_fqn}.{schema_name}"
        schema, schema_state = get_or_create(
            args.base_url,
            token,
            "databaseSchemas",
            schema_fqn,
            {
                "name": schema_name,
                "displayName": "은행 업무 스키마",
                "description": f"{label} 은행 업무 목 스키마입니다.",
                "database": database["fullyQualifiedName"],
                "owners": [owner],
            },
        )
        table_records = []
        quality_records = []
        for table_spec in TABLES:
            table_fqn = f"{schema_fqn}.{table_spec['name']}"
            table, table_state = get_or_create(
                args.base_url,
                token,
                "tables",
                table_fqn,
                {
                    "name": table_spec["name"],
                    "displayName": table_spec["displayName"],
                    "description": table_spec["description"],
                    "databaseSchema": schema["fullyQualifiedName"],
                    "owners": [owner],
                    "columns": columns_for(table_spec),
                },
                fields="columns,owners",
            )
            table_ids.add(str(table["id"]))
            table_records.append(
                {
                    "name": table["name"],
                    "fullyQualifiedName": table["fullyQualifiedName"],
                    "id": table["id"],
                    "state": table_state,
                    "column_count": len(table.get("columns", table_spec["columns"])),
                    "ui": (
                        args.base_url.removesuffix("/api/v1")
                        + "/table/"
                        + table["fullyQualifiedName"]
                    ),
                    "data_quality_ui": (
                        args.base_url.removesuffix("/api/v1")
                        + "/table/"
                        + table["fullyQualifiedName"]
                        + "/profiler/data-quality"
                    ),
                }
            )
            column_name = (
                "customer_id"
                if table_spec["name"] == "customer"
                else "transaction_id"
            )
            expected_status = (
                "Success" if table_spec["name"] == "customer" else "Failed"
            )
            test_name = (
                "mock_customer_id_not_null_pass"
                if expected_status == "Success"
                else "mock_transaction_id_not_null_fail"
            )
            test_fqn = f"{table_fqn}.{column_name}.{test_name}"
            test_case, test_state = get_or_create(
                args.base_url,
                token,
                "dataQuality/testCases",
                test_fqn,
                {
                    "name": test_name,
                    "displayName": (
                        "[목] 고객 ID NULL 없음 - 정상"
                        if expected_status == "Success"
                        else "[목] 거래 ID NULL 발견 - 실패"
                    ),
                    "description": (
                        "실제 DB 실행 결과가 아닌 데이터 품질 화면 확인용 목 결과입니다."
                    ),
                    "testDefinition": "columnValuesToBeNotNull",
                    "entityLink": (
                        f"<#E::table::{table_fqn}::columns::{column_name}>"
                    ),
                    "owners": [owner],
                    "parameterValues": [],
                },
                fields="owners,testCaseResult,testDefinition,testSuite",
            )
            current_status = (test_case.get("testCaseResult") or {}).get(
                "testCaseStatus"
            )
            if current_status != expected_status:
                passed = expected_status == "Success"
                api_call(
                    args.base_url,
                    "POST",
                    "/dataQuality/testCases/testCaseResults/"
                    + urllib.parse.quote(test_case["fullyQualifiedName"], safe=""),
                    token,
                    {
                        "timestamp": int(time.time() * 1000),
                        "testCaseStatus": expected_status,
                        "result": (
                            "Intentional mock success for the Data Quality screen."
                            if passed
                            else "Intentional mock failure for the Data Quality screen."
                        ),
                        "testResultValue": [],
                        "passedRows": 1 if passed else 0,
                        "failedRows": 0 if passed else 1,
                    },
                )
            test_case_count += 1
            quality_records.append(
                {
                    "fullyQualifiedName": test_case["fullyQualifiedName"],
                    "state": test_state,
                    "result": expected_status,
                    "mock": True,
                }
            )
        records.append(
            {
                "engine": label,
                "serviceType": service_type,
                "service": service["fullyQualifiedName"],
                "service_state": service_state,
                "database": database["fullyQualifiedName"],
                "database_state": database_state,
                "schema": schema["fullyQualifiedName"],
                "schema_state": schema_state,
                "tables": table_records,
                "data_quality_tests": quality_records,
            }
        )

    indexed = wait_for_search(args.base_url, token, table_ids, args.search_timeout)
    result = {
        "status": "PASS" if indexed == table_ids else "SEARCH_TIMEOUT",
        "base_url": args.base_url,
        "summary": {
            "database_services": len(records),
            "databases": len(records),
            "schemas": len(records),
            "tables": len(table_ids),
            "indexed_tables": len(indexed),
            "data_quality_tests": test_case_count,
        },
        "services": records,
        "ui": args.base_url.removesuffix("/api/v1") + "/settings/services/databases",
        "data_quality_ui": (
            args.base_url.removesuffix("/api/v1") + "/data-quality/test-cases"
        ),
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
