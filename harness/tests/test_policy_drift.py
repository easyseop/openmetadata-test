"""T93 policy-staleness tests against the REAL 1.13.0 tree.

The layout is pinned to 1.12.13, and 1.13.0 really adds new top-level modules
(openmetadata-mcp, etc.), so this exercises a genuine policy-drift finding.
"""
from pathlib import Path

from acgh import layout as L
from acgh import policy_drift as PD
from acgh import verdict as V

_LAYOUT = Path(__file__).resolve().parents[1] / "policies" / "repository-layout.yaml"
_SECDIR = "openmetadata-service/src/main/java/org/openmetadata/service/security/**"


def layout():
    return L.load_layout(_LAYOUT)


def test_live_pattern_is_not_stale(om_mirror):
    stale = PD.stale_patterns(str(om_mirror), "UPSTREAM_B", [_SECDIR])
    assert stale == []  # security dir still exists in 1.13.0


def test_empty_gun_pattern_detected(om_mirror):
    stale = PD.stale_patterns(str(om_mirror), "UPSTREAM_B",
                              ["nonexistent-module/**", _SECDIR])
    assert stale == ["nonexistent-module/**"]


def test_new_toplevel_modules_are_unclassified(om_mirror):
    unclassified = PD.unclassified_toplevel_modules(
        str(om_mirror), "UPSTREAM_B", layout())
    # 1.13.0 adds modules the 1.12.13-pinned layout has never seen.
    assert "openmetadata-mcp" in unclassified


def test_check_policy_drift_fails_closed_on_new_module(om_mirror):
    r = PD.check_policy_drift(str(om_mirror), "UPSTREAM_B", [_SECDIR], layout())
    # A new unclassified module dominates -> analysis_error (fail-closed).
    assert r.verdict == V.ANALYSIS_ERROR
    assert any("unclassified_toplevel_module" in x for x in r.reasons)


def test_stale_pattern_only_is_approval(om_mirror):
    # Force no unclassified finding by using a layout that owns everything,
    # so only the stale-pattern path is exercised.
    wide = L.Layout(
        upstream_base_sha="0" * 40,
        upstream_roots=["**"], governance_roots=[], extension_roots=[],
        unknown_policy="analysis_error",
    )
    r = PD.check_policy_drift(str(om_mirror), "UPSTREAM_B",
                             ["nonexistent-module/**"], wide)
    assert r.verdict == V.APPROVAL
