"""CONTRACT-KOREAN-IME source guard and real browser composition round-trip."""

import base64
import json
import os
from pathlib import Path

import pytest


def test_hangul_composition_source_guard():
    """Keep the source wiring visible without claiming browser evidence."""
    value = os.environ.get("OPENMETADATA_PRODUCT_REPO")
    if not value:
        pytest.skip("OPENMETADATA_PRODUCT_REPO is required")
    source_path = (
        Path(value)
        / "openmetadata-ui/src/main/resources/ui/src/components/Database/"
        "SchemaEditor/SchemaEditor.tsx"
    )
    source = source_path.read_text(encoding="utf-8")

    required_fragments = (
        "const isComposingRef = useRef(false)",
        "isComposingRef.current = true",
        "isComposingRef.current = false",
        "editorInstance.current.getValue()",
        "'compositionstart'",
        "'compositionend'",
        "if (isComposingRef.current)",
    )
    for fragment in required_fragments:
        assert fragment in source
    assert source.count("if (isComposingRef.current)") >= 2


def _browser_storage_state():
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


def _replace_during_composition(wrapper, stages):
    """Drive the rendered CodeMirror through real composition DOM events."""
    wrapper.evaluate(
        """(element, values) => {
          const editor = element.CodeMirror;
          if (!editor) {
            throw new Error('CodeMirror instance is not attached to wrapper');
          }
          if (editor.getOption('readOnly')) {
            throw new Error('target SchemaEditor is read-only');
          }
          element.dispatchEvent(
            new CompositionEvent('compositionstart', {
              bubbles: true,
              data: values[0],
            })
          );
          for (const value of values) {
            editor.setValue(value);
            element.dispatchEvent(
              new CompositionEvent('compositionupdate', {
                bubbles: true,
                data: value,
              })
            );
          }
          element.dispatchEvent(
            new CompositionEvent('compositionend', {
              bubbles: true,
              data: values[values.length - 1],
            })
          );
        }""",
        stages,
    )


def test_hangul_composition_roundtrip():
    """Prove the rendered controlled editor retains composed Hangul."""
    editor_url = os.environ.get("BANK_IME_EDITOR_URL")
    if not editor_url:
        pytest.skip(
            "BANK_IME_EDITOR_URL is required for the browser IME contract"
        )

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.fail(
            "Playwright is required when BANK_IME_EDITOR_URL is configured"
        )

    try:
        editor_index = int(os.environ.get("BANK_IME_EDITOR_INDEX", "0"))
    except ValueError:
        pytest.fail("BANK_IME_EDITOR_INDEX must be an integer")
    if editor_index < 0:
        pytest.fail("BANK_IME_EDITOR_INDEX must be zero or greater")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=_browser_storage_state())
        page = context.new_page()
        page.goto(editor_url, wait_until="domcontentloaded")
        container = page.get_by_test_id("code-mirror-container").nth(
            editor_index
        )
        container.wait_for(state="visible")
        wrapper = container.locator(".CodeMirror").first
        wrapper.wait_for(state="visible")

        wrapper.evaluate("(element) => element.CodeMirror.setValue('')")
        _replace_during_composition(wrapper, ["ㅎ", "하", "한"])
        _replace_during_composition(wrapper, ["한ㄱ", "한그", "한글"])
        page.wait_for_timeout(250)

        actual = wrapper.evaluate(
            "(element) => element.CodeMirror.getValue()"
        )
        assert actual == "한글"
        context.close()
        browser.close()
