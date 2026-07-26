"""T61 patch-kill tests on a real OM auth file (base = without the bank patch)."""
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from acgh import gitprim as G
from acgh import patchkill as PK
from acgh import result_io as RIO
from acgh import verdict as V


def _run(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path, om_auth_content, om_auth_path):
    r = tmp_path / "repo"
    r.mkdir()
    _run(r, "init", "-q", "-b", "main")
    _run(r, "config", "user.email", "t@example.com")
    _run(r, "config", "user.name", "t")
    _run(r, "config", "commit.gpgsign", "false")
    # base = real OM auth file WITHOUT the bank marker (i.e. patch removed).
    fp = r / om_auth_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(om_auth_content)
    _run(r, "add", "-A")
    _run(r, "commit", "-m", "base without patch")
    return r


def _marker_test(auth_path):
    # exits 0 iff the bank marker is present -> without the patch it exits 1.
    return [sys.executable, "-c",
            f"import sys,pathlib;"
            f"sys.exit(0 if 'BANK-OM-001' in pathlib.Path({auth_path!r}).read_text() "
            f"else 1)"]


def test_proven_when_test_fails_without_patch(repo, tmp_path, om_auth_path):
    r = PK.patch_kill(str(repo), "main", _marker_test(om_auth_path),
                      str(tmp_path / "wt"))
    assert r.status == PK.PROVEN
    assert r.verdict() == V.PASS


def test_shell_test_blocks(repo, tmp_path):
    # A test that always passes proves nothing about the patch.
    always_ok = [sys.executable, "-c", "import sys; sys.exit(0)"]
    r = PK.patch_kill(str(repo), "main", always_ok, str(tmp_path / "wt"))
    assert r.status == PK.SHELL
    assert r.verdict() == V.BLOCK


def test_unrunnable_test_is_infrastructure_error(repo, tmp_path):
    r = PK.patch_kill(str(repo), "main", ["__no_such_binary_xyz__"],
                      str(tmp_path / "wt"))
    assert r.status == PK.INFRA_ERROR
    assert r.verdict() == V.ANALYSIS_ERROR


def test_unexpected_harness_exit_is_infrastructure_error(repo, tmp_path):
    internal_error = [sys.executable, "-c", "import sys; sys.exit(3)"]
    r = PK.patch_kill(
        str(repo), "main", internal_error, str(tmp_path / "wt")
    )
    assert r.status == PK.INFRA_ERROR
    assert r.verdict() == V.ANALYSIS_ERROR


def test_pytest_negative_control_requires_an_assertion_failure(
    repo, tmp_path, om_auth_path
):
    suite = tmp_path / "suite"
    suite.mkdir()
    selector = suite / "test_negative.py"
    selector.write_text(
        "import os\n"
        "from pathlib import Path\n\n"
        "def test_patch_marker():\n"
        "    root = Path(os.environ['OPENMETADATA_PRODUCT_REPO'])\n"
        f"    assert 'BANK-OM-001' in (root / {om_auth_path!r}).read_text()\n\n"
        "def test_environment_missing():\n"
        "    import pytest\n"
        "    pytest.skip('counterfactual runtime is unavailable')\n",
        encoding="utf-8",
    )
    result = PK.patch_kill_pytest(
        str(repo),
        "main",
        suite,
        "test_negative.py::test_patch_marker",
        str(tmp_path / "wt"),
    )
    assert result.status == PK.PROVEN
    assert result.verdict() == V.PASS
    skipped = PK.patch_kill_pytest(
        str(repo),
        "main",
        suite,
        "test_negative.py::test_environment_missing",
        str(tmp_path / "wt-skipped"),
    )
    assert skipped.status == PK.INCONCLUSIVE
    assert skipped.verdict() == V.ANALYSIS_ERROR


def test_patch_kill_plan_rejects_duplicate_scope_classification():
    plan_path = (
        Path(__file__).parents[1]
        / "registrations"
        / "kb-openmetadata"
        / "patch-kill-plan.yaml"
    )
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    assert PK.parse_plan(plan) == plan
    duplicate = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    duplicate["pending"].append(
        {
            "customization_id": "BANK-OM-006",
            "reason": "This deliberately duplicates a source experiment for validation.",
        }
    )
    with pytest.raises(PK.PatchKillPlanError, match="unique"):
        PK.parse_plan(duplicate)


def test_registered_source_patch_kill_evidence_is_self_consistent():
    registration = (
        Path(__file__).parents[1] / "registrations" / "kb-openmetadata"
    )
    evidence_path = registration / "source-patch-kill-evidence.yaml"
    evidence = yaml.safe_load(evidence_path.read_text(encoding="utf-8"))
    plan = PK.load_plan(registration / "patch-kill-plan.yaml")
    payload = evidence["canonical_payload"]

    assert payload["inputs"]["patch_kill_plan_digest"] == PK.plan_digest(plan)
    assert payload["inputs"]["pending_high_critical_ids"] == [
        "BANK-OM-001",
        "BANK-OM-002",
        "BANK-OM-003",
    ]
    assert [gate["verdict"] for gate in payload["gates"]] == [
        V.PASS,
        V.PASS,
    ]
    decision = RIO.interpret_result(
        evidence_path,
        actual_exit=0,
        expected_inputs=payload["inputs"],
        harness_version=payload["harness_version"],
    )
    assert decision.verdict == V.PASS
    assert decision.synthetic is False


def test_worktree_cleaned_after_run(repo, tmp_path):
    wt = tmp_path / "wt"
    PK.patch_kill(str(repo), "main", [sys.executable, "-c", "0"], str(wt))
    listing = G.git(str(repo), "worktree", "list", "--porcelain")
    assert str(wt) not in listing
    assert not wt.exists()
