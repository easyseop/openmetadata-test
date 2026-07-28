"""T93 policy-staleness tests against the fixed upstream A→B mirror.

The test compares the two pinned trees and checks only top-level directories
that are genuinely new in B. Directories already present in A are not policy
drift merely because the ownership layout does not classify them.
"""
import subprocess
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
    assert unclassified == [".devcontainer", "skills"]


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
    r = PD.check_policy_drift(
        str(om_mirror),
        "UPSTREAM_B",
        ["nonexistent-module/**"],
        wide,
        baseline_ref="UPSTREAM_A",
    )
    assert r.verdict == V.APPROVAL


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _commit(repo, message, customization_id=None):
    _git(repo, "add", ".")
    args = ["commit", "-m", message]
    if customization_id:
        args += ["-m", f"Customization-ID: {customization_id}"]
    _git(repo, *args)
    return _git(repo, "rev-parse", "HEAD")


def _history_repo(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    (tmp_path / "a.txt").write_text("a\n")
    (tmp_path / "b.txt").write_text("b\n")
    base = _commit(tmp_path, "base")
    (tmp_path / "a.txt").write_text("a2\n")
    head = _commit(tmp_path, "custom", "BANK-OM-001")
    return base, head


def test_exact_scope_history_passes_on_exact_equality(tmp_path):
    base, head = _history_repo(tmp_path)
    manifests = {
        "BANK-OM-001": {
            "implementation": {"allowed_changed_paths": ["a.txt"]}
        }
    }
    result = PD.check_exact_scope_history(
        str(tmp_path), base, head, manifests
    )
    assert result.verdict == V.PASS


def test_exact_scope_history_blocks_omission(tmp_path):
    base, head = _history_repo(tmp_path)
    manifests = {
        "BANK-OM-001": {
            "implementation": {"allowed_changed_paths": ["b.txt"]}
        }
    }
    result = PD.check_exact_scope_history(
        str(tmp_path), base, head, manifests
    )
    assert result.verdict == V.BLOCK
    assert any("observed_path_outside_exact_scope" in r for r in result.reasons)


def test_exact_scope_history_flags_overbroad_declaration(tmp_path):
    base, head = _history_repo(tmp_path)
    manifests = {
        "BANK-OM-001": {
            "implementation": {
                "allowed_changed_paths": ["a.txt", "b.txt"]
            }
        }
    }
    result = PD.check_exact_scope_history(
        str(tmp_path), base, head, manifests
    )
    assert result.verdict == V.APPROVAL
    assert any("declared_path_not_observed" in r for r in result.reasons)


def test_exact_scope_history_flags_registered_id_with_no_commit(tmp_path):
    base, head = _history_repo(tmp_path)
    manifests = {
        "BANK-OM-001": {
            "implementation": {"allowed_changed_paths": ["a.txt"]}
        },
        "BANK-OM-002": {
            "implementation": {"allowed_changed_paths": ["b.txt"]}
        },
    }
    result = PD.check_exact_scope_history(
        str(tmp_path), base, head, manifests
    )
    assert result.verdict == V.APPROVAL
    assert any(
        "BANK-OM-002 declared_path_not_observed" in reason
        for reason in result.reasons
    )
