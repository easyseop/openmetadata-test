"""Shared helpers for authenticated browser runtime contracts."""

import base64
import json
import os

import pytest


def browser_storage_state():
    """Decode the optional Playwright storage state supplied by CI."""
    encoded = os.environ.get("BANK_BROWSER_STORAGE_STATE_B64")
    if not encoded:
        return None
    try:
        raw = base64.b64decode(encoded, validate=True)
        state = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        pytest.fail(f"BANK_BROWSER_STORAGE_STATE_B64 is invalid: {exc}")
    if not isinstance(state, dict):
        pytest.fail("BANK_BROWSER_STORAGE_STATE_B64 must decode to a JSON object")
    return state


def sync_playwright_or_fail():
    """Load Playwright only for configured live browser contracts."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.fail("Playwright is required for configured browser contracts")
    return sync_playwright
