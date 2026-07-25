"""CONTRACT-KOREAN-IME source guard for the browser composition round-trip."""

import os
from pathlib import Path

import pytest


def test_hangul_composition_roundtrip():
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
