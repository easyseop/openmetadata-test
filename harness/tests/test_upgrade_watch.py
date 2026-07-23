"""T93 upgrade_watch tests against the REAL OM 1.12.13 -> 1.13.0 upgrade diff.

This is the most authentic case-D test we can write: real upstream churn.
"""
from acgh import upgrade_watch as UW
from acgh import verdict as V

# Verified against the mirror: unchanged A->B / changed A->B.
_UNCHANGED = ("openmetadata-service/src/main/java/org/openmetadata/service/"
              "security/AuthLoginServlet.java")
_CHANGED_DIR = "openmetadata-service/src/main/java/org/openmetadata/service/security/**"
_CHANGED_CONF = "conf/**"


def _m(cid, watch_paths):
    return {cid: {"customization_id": cid, "kind": "core-patch",
                  "upgrade_watch": {"paths": watch_paths}}}


def test_watched_upstream_change_triggers_approval(om_mirror):
    findings = UW.evaluate_upgrade_watch(
        str(om_mirror), "UPSTREAM_A", "UPSTREAM_B",
        _m("BANK-OM-001", [_CHANGED_DIR]))
    assert len(findings) == 1
    assert findings[0].customization_id == "BANK-OM-001"
    assert findings[0].changed_watch_paths  # real changed security files
    assert UW.to_gate_result(findings).verdict == V.APPROVAL


def test_unchanged_watched_path_passes(om_mirror):
    findings = UW.evaluate_upgrade_watch(
        str(om_mirror), "UPSTREAM_A", "UPSTREAM_B",
        _m("BANK-OM-001", [_UNCHANGED]))
    assert findings == []
    assert UW.to_gate_result(findings).verdict == V.PASS


def test_conf_change_triggers_approval(om_mirror):
    # conf/openmetadata.yaml really changed A->B.
    findings = UW.evaluate_upgrade_watch(
        str(om_mirror), "UPSTREAM_A", "UPSTREAM_B",
        _m("BANK-OM-002", [_CHANGED_CONF]))
    assert findings and "conf/" in findings[0].changed_watch_paths[0]
    assert UW.to_gate_result(findings).verdict == V.APPROVAL


def test_only_watching_manifests_are_considered(om_mirror):
    manifests = {
        "BANK-OM-001": {"customization_id": "BANK-OM-001", "kind": "core-patch",
                        "upgrade_watch": {"paths": [_UNCHANGED]}},
        "BANK-OM-002": {"customization_id": "BANK-OM-002", "kind": "core-patch"},
        "BANK-OM-003": {"customization_id": "BANK-OM-003", "kind": "core-patch",
                        "upgrade_watch": {"paths": [_CHANGED_CONF]}},
    }
    findings = UW.evaluate_upgrade_watch(
        str(om_mirror), "UPSTREAM_A", "UPSTREAM_B", manifests)
    # Only 003 (watching a changed path) fires; 001 unchanged, 002 no watch.
    assert [f.customization_id for f in findings] == ["BANK-OM-003"]
