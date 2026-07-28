"""Phase-four isolated upgrade rehearsal plan tests."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from acgh import rehearsal as R
from acgh import verdict as V


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    path = tmp_path / "product"
    path.mkdir()
    _git(path, "init")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    shas = []
    for index in range(4):
        (path / "state.txt").write_text(f"{index}\n", encoding="utf-8")
        _git(path, "add", "state.txt")
        _git(path, "commit", "-m", f"version {index}")
        shas.append(_git(path, "rev-parse", "HEAD"))
        _git(path, "tag", f"v{index}")
    return path, shas


def _plan(path: Path, shas):
    data = {
        "schema_version": 1,
        "mode": "synthetic-backtest",
        "historical_claim": "not-production-history",
        "source_reference": {
            "commit_sha": shas[-1],
            "evidence_file": "source-evidence.yaml",
        },
        "execution": {
            "isolation": "disposable-worktree",
            "product_branch_mutation": False,
            "persistent_candidate_branch": False,
            "branch_prefix": "codex/upgrade-rehearsal",
            "result_directory": "results/upgrade-rehearsals",
        },
        "stages": [
            "identify-refs",
            "upstream-diff",
            "bank-diff",
            "prepare-disposable-upgrade-branch",
            "reapply-detect",
            "source-gates",
            "upgrade-risk-gates",
            "result-labels",
        ],
        "runs": [
            {
                "id": f"r{index + 1}",
                "order": index + 1,
                "upstream_base": {"tag": f"v{index}", "sha": shas[index]},
                "upstream_target": {
                    "tag": f"v{index + 1}",
                    "sha": shas[index + 1],
                },
                "expected_git_relation": "ancestor",
                "result_file": f"results/upgrade-rehearsals/{index + 1}.json",
            }
            for index in range(3)
        ],
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return data


def test_three_contiguous_runs_are_refs_ready(repo, tmp_path):
    product, shas = repo
    plan_path = tmp_path / "matrix.yaml"
    _plan(plan_path, shas)
    result = R.inspect_plan(str(product), R.load_plan(plan_path))
    assert result["verdict"] == V.PASS
    assert [item["status"] for item in result["runs"]] == [
        "refs-ready",
        "refs-ready",
        "refs-ready",
    ]
    assert result["product_branch_mutation"] is False
    assert result["persistent_candidate_branch"] is False
    assert all(
        "temporary_upgrade_branch" in item for item in result["runs"]
    )


def test_noncontiguous_chain_is_rejected(repo, tmp_path):
    _product, shas = repo
    plan_path = tmp_path / "matrix.yaml"
    data = _plan(plan_path, shas)
    data["runs"][1]["upstream_base"] = {
        "tag": "other",
        "sha": "0" * 40,
    }
    plan_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(R.RehearsalPlanError, match="not contiguous"):
        R.load_plan(plan_path)


def test_tag_sha_mismatch_is_analysis_error(repo, tmp_path):
    product, shas = repo
    plan_path = tmp_path / "matrix.yaml"
    data = _plan(plan_path, shas)
    data["runs"][0]["upstream_base"]["sha"] = shas[1]
    plan_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    result = R.inspect_plan(str(product), R.load_plan(plan_path))
    assert result["verdict"] == V.ANALYSIS_ERROR
    assert "pinned SHA" in result["errors"][0]


def test_historical_claim_and_isolation_are_mandatory(repo, tmp_path):
    _product, shas = repo
    plan_path = tmp_path / "matrix.yaml"
    data = _plan(plan_path, shas)
    data["historical_claim"] = "real-production-history"
    plan_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    with pytest.raises(R.RehearsalPlanError, match="historical_claim"):
        R.load_plan(plan_path)
