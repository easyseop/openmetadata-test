#!/usr/bin/env python3
"""Fail-closed preflight for the bank runtime-contract environment.

It validates presence and shape only and never prints secret values.  This
prevents an expensive browser/runtime job from turning missing environment
configuration into a misleading pytest skip.
"""
from __future__ import annotations

import base64
import json
import os
import re
from urllib.parse import urlparse


REQUIRED = (
    "OPENMETADATA_BASE_URL",
    "OPENMETADATA_AUTH_TOKEN",
    "BANK_CONTRACT_QUERY_ID",
    "BANK_FAILED_ASSERTION_FQN",
    "BANK_COLUMN_TABLE_FQN",
    "BANK_COLUMN_NAME",
    "BANK_IME_EDITOR_URL",
    "BANK_DATA_ASSERTIONS_URL",
    "BANK_COLUMN_UI_URL",
    "BANK_BROWSER_STORAGE_STATE_B64",
    "DEPLOYED_ARTIFACT_DIGEST",
)
URL_FIELDS = (
    "OPENMETADATA_BASE_URL",
    "BANK_IME_EDITOR_URL",
    "BANK_DATA_ASSERTIONS_URL",
    "BANK_COLUMN_UI_URL",
)
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def inspect_environment(env: dict[str, str]) -> dict:
    missing = sorted(name for name in REQUIRED if not env.get(name, "").strip())
    invalid = []
    for name in URL_FIELDS:
        value = env.get(name, "")
        if not value:
            continue
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            invalid.append(f"{name}: must be an absolute http(s) URL")
    digest = env.get("DEPLOYED_ARTIFACT_DIGEST", "")
    if digest and not _DIGEST.fullmatch(digest):
        invalid.append(
            "DEPLOYED_ARTIFACT_DIGEST: must be sha256 plus 64 lowercase hex"
        )
    storage = env.get("BANK_BROWSER_STORAGE_STATE_B64", "")
    if storage:
        try:
            decoded = base64.b64decode(storage, validate=True)
            document = json.loads(decoded)
            if not isinstance(document, dict):
                raise ValueError("storage state is not a JSON object")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            invalid.append(
                "BANK_BROWSER_STORAGE_STATE_B64: invalid base64 JSON storage state "
                f"({type(exc).__name__})"
            )
    return {
        "ready": not missing and not invalid,
        "missing_fields": missing,
        "invalid_fields": sorted(invalid),
        "checked_field_count": len(REQUIRED),
        "secrets_echoed": False,
    }


def main() -> int:
    report = inspect_environment(dict(os.environ))
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ready"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
