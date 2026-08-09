"""T93 upgrade_watch tests against the REAL OM 1.12.13 -> 1.13.0 upgrade diff.

This is the most authentic case-D test we can write: real upstream churn.
"""
from acgh import upgrade_watch as UW
from acgh import verdict as V
import subprocess

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


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _commit(repo, message):
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def test_configuration_key_and_dependency_changes_are_detected(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    (tmp_path / "conf.yaml").write_text("auth:\n  provider: basic\n")
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"1"}}')
    base = _commit(tmp_path, "base")
    (tmp_path / "conf.yaml").write_text("auth:\n  provider: saml\n")
    (tmp_path / "package.json").write_text('{"dependencies":{"react":"2"}}')
    head = _commit(tmp_path, "upgrade")
    manifests = {
        "BANK-OM-001": {
            "upgrade_watch": {
                "paths": [],
                "configuration_keys": ["auth.provider"],
                "dependencies": ["react"],
            }
        }
    }

    findings = UW.evaluate_upgrade_watch(
        str(tmp_path), base, head, manifests
    )
    assert findings[0].changed_watch_paths == ()
    assert findings[0].changed_configuration_keys == ("auth.provider",)
    assert findings[0].changed_dependencies == ("react",)
    result = UW.to_gate_result(findings)
    assert result.verdict == V.APPROVAL
    assert "configuration_keys" in result.reasons[0]
    assert "dependencies" in result.reasons[0]


def test_deleted_watch_path_is_explicit_and_non_ancestor_comparison_is_labeled(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    (tmp_path / "watched.ts").write_text("export const bank = 1;\n")
    base = _commit(tmp_path, "base")

    _git(tmp_path, "switch", "--orphan", "new-release")
    for path in tmp_path.iterdir():
        if path.name != ".git" and path.is_file():
            path.unlink()
    (tmp_path / "other.ts").write_text("export const upstream = 2;\n")
    head = _commit(tmp_path, "unrelated release")

    findings = UW.evaluate_upgrade_watch(
        str(tmp_path), base, head, _m("BANK-OM-004", ["watched.ts"])
    )
    assert findings[0].comparison == "two_tree(non_ancestor)"
    packet = UW.review_packet(findings)
    assert packet["deleted_paths"] == ["watched.ts"]
    assert packet["findings"][0]["changed_watch_paths"] == [
        {"status": "D", "path": "watched.ts"}
    ]
    result = UW.to_gate_result(findings)
    assert "deleted_paths=['watched.ts']" in result.reasons[0]
