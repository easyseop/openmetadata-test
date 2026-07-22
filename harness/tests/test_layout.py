"""T05 layout / shared path-grammar tests."""
from pathlib import Path

import pytest

from acgh import layout as L

_LAYOUT = Path(__file__).resolve().parents[1] / "policies" / "repository-layout.yaml"


def load():
    return L.load_layout(_LAYOUT)


def test_normalize_rejects_absolute_and_dotdot():
    assert L.normalize_path("a/b/c.java") == "a/b/c.java"
    for bad in ["/abs/x", "a/../b", "./a", "a/", "a\\b", ""]:
        with pytest.raises(L.LayoutError):
            L.normalize_path(bad)


def test_normalize_is_nfc():
    # 'é' composed (U+00E9) vs decomposed (e + U+0301) must normalize equal.
    composed = "dir/é.txt"
    decomposed = "dir/é.txt"
    assert L.normalize_path(composed) == L.normalize_path(decomposed)


def test_ensure_literal_rejects_glob():
    assert L.ensure_literal("a/b/File.java") == "a/b/File.java"
    for glob in ["a/**", "a/*.java", "a/f?.java", "a/[ab].java"]:
        with pytest.raises(L.LayoutError):
            L.ensure_literal(glob)


def test_classify_real_om_roots():
    lay = load()
    assert lay.classify(
        "openmetadata-service/src/main/java/org/openmetadata/service/security/"
        "AuthLoginServlet.java"
    ) == L.UPSTREAM
    assert lay.classify(".bank/policy/x.yaml") == L.GOVERNANCE
    assert lay.classify("bank-extensions/foo/Bar.java") == L.EXTENSION
    # A path under no owned root is unknown -> caller fails closed.
    assert lay.classify("some-new-toplevel/x") == L.UNKNOWN


def test_layout_binds_to_upstream_sha():
    lay = load()
    assert lay.upstream_base_sha == "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7"
    assert lay.unknown_policy == "analysis_error"


def test_negation_pattern_rejected():
    with pytest.raises(L.LayoutError):
        L.make_spec(["a/**", "!a/skip/**"])


def test_ambiguous_ownership_fails_closed():
    lay = L.Layout(
        upstream_base_sha="0" * 40,
        upstream_roots=["shared/**"],
        governance_roots=["shared/**"],
        extension_roots=[],
        unknown_policy="analysis_error",
    )
    with pytest.raises(L.LayoutError):
        lay.classify("shared/x.txt")
