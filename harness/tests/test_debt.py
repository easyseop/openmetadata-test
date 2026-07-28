"""T43 debt-gate tests (pure threshold logic — synthetic)."""
import subprocess
from pathlib import Path

from acgh import debt as D
from acgh import verdict as V


def test_within_budget_passes():
    r = D.evaluate_debt({"core_patch_count": 10, "changed_lines": 500,
                         "conflict_rate": 0.05, "hotspot_overlap": 1})
    assert r.verdict == V.PASS


def test_over_soft_is_approval():
    r = D.evaluate_debt({"core_patch_count": 25})  # >20 soft, <40 hard
    assert r.verdict == V.APPROVAL
    assert any("soft" in x for x in r.reasons)


def test_over_hard_is_block():
    r = D.evaluate_debt({"conflict_rate": 0.5})  # >0.35 hard
    assert r.verdict == V.BLOCK
    assert any("hard" in x for x in r.reasons)


def test_hard_dominates_soft():
    r = D.evaluate_debt({"core_patch_count": 25, "changed_lines": 9000})
    assert r.verdict == V.BLOCK  # changed_lines over hard wins


def test_unknown_metric_fails_closed():
    r = D.evaluate_debt({"made_up_metric": 999999})
    assert r.verdict == V.ANALYSIS_ERROR


def test_policy_loads_from_versioned_yaml():
    path = Path(__file__).resolve().parents[1] / "policies" / "debt-thresholds.yaml"
    policy = D.load_thresholds(path)
    assert policy["core_patch_count"] == {"soft": 14, "hard": 19}


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _commit(repo, message):
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def test_collect_metrics_from_candidate_and_exact_manifests(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    (tmp_path / "shared.txt").write_text("a\n")
    base = _commit(tmp_path, "base")
    (tmp_path / "shared.txt").write_text("a\nb\n")
    head = _commit(tmp_path, "head")
    manifests = {
        "BANK-OM-001": {
            "status": "active", "kind": "core-patch",
            "implementation": {"allowed_changed_paths": ["shared.txt"]},
        },
        "BANK-OM-002": {
            "status": "active", "kind": "core-patch",
            "implementation": {"allowed_changed_paths": ["shared.txt"]},
        },
    }
    metrics = D.collect_metrics(
        str(tmp_path), base, head, manifests, conflict_rate=0.25
    )
    assert metrics == {
        "core_patch_count": 2,
        "changed_lines": 1,
        "conflict_rate": 0.25,
        "hotspot_overlap": 2,
    }
