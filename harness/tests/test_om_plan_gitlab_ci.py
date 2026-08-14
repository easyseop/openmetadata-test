"""Security-boundary tests for the GitLab /om-plan wiring."""

from __future__ import annotations

import importlib.util
import json
import os
import py_compile
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / ".gitlab-ci.yml"
CACHE_CLEANER = ROOT / "harness" / "ci" / "prepare_trusted_checker.sh"


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _pipeline() -> tuple[dict, dict]:
    documents = list(yaml.safe_load_all(PIPELINE.read_text(encoding="utf-8")))
    assert len(documents) == 2
    return documents[0], documents[1]


def test_gitlab_pipeline_uses_fixed_inputs_and_protected_manual_entrypoint():
    header, pipeline = _pipeline()
    inputs = header["spec"]["inputs"]

    assert set(inputs) == {
        "request-ref",
        "request-path",
        "product-project",
        "proposal-ref",
        "proposal-path",
    }
    assert inputs["request-ref"]["regex"] == "^[0-9a-f]{40}$"
    assert inputs["proposal-ref"]["regex"] == "^[0-9a-f]{40}$"
    assert pipeline["workflow"]["rules"] == [
        {"if": '$CI_PIPELINE_SOURCE == "web"', "when": "always"},
        {"when": "never"},
    ]
    assert pipeline["variables"]["GIT_STRATEGY"] == "clone"
    assert pipeline["variables"]["GIT_DEPTH"] == "0"

    trusted_rule = json.dumps(
        pipeline[".om-plan-protected-job"]["rules"], sort_keys=True
    )
    assert pipeline[".om-plan-protected-job"]["tags"] == [
        "om-plan-protected"
    ]
    assert "CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH" in trusted_rule
    assert 'CI_COMMIT_REF_PROTECTED == \\"true\\"' in trusted_rule

    reject = pipeline["reject_untrusted_context"]
    reject_text = json.dumps(reject, sort_keys=True)
    assert "CI_COMMIT_BRANCH != $CI_DEFAULT_BRANCH" in reject_text
    assert 'CI_COMMIT_REF_PROTECTED != \\"true\\"' in reject_text
    assert "exit 3" in reject_text


def test_gitlab_proposal_cannot_inherit_preflight_artifacts_or_digest():
    _, pipeline = _pipeline()
    proposal = pipeline["om_plan_package_proposal"]
    validate = pipeline["om_plan_validate"]

    assert proposal["dependencies"] == []
    proposal_text = json.dumps(proposal, sort_keys=True)
    assert "preflight" not in proposal_text
    assert "digest" not in proposal_text
    assert "expected" not in proposal_text
    assert "OM_PLAN_REQUEST_REF" not in proposal_text
    assert "OM_PLAN_PRODUCT_PROJECT" not in proposal_text
    proposal_script = proposal["script"][0]
    assert proposal_script.index("unset CI_JOB_TOKEN") < proposal_script.index(
        "package-proposal"
    )

    assert validate["needs"] == [
        {"job": "om_plan_preflight", "artifacts": True},
        {"job": "om_plan_intent_review", "artifacts": False},
        {"job": "om_plan_package_proposal", "artifacts": True},
    ]
    pipeline_text = PIPELINE.read_text(encoding="utf-8")
    assert "artifacts:\n    reports:\n      dotenv:" not in pipeline_text


def test_gitlab_review_is_blocking_and_fresh_exit_semantics_are_preserved():
    _, pipeline = _pipeline()
    review = pipeline["om_plan_intent_review"]
    validate = pipeline["om_plan_validate"]

    assert review["environment"] == {
        "name": "om-plan-intent-review",
        "action": "start",
    }
    assert review["when"] == "manual"
    assert review["allow_failure"] is False
    assert review["dependencies"] == ["om_plan_preflight"]
    assert "intent-summary.md" in json.dumps(review, sort_keys=True)

    validate_text = json.dumps(validate, sort_keys=True)
    assert validate["allow_failure"] is False
    assert "expected-input-lock-digest.txt" in validate_text
    assert "om_plan_ci.py validate" in validate_text
    assert "fresh-validation/stdout.json" in validate_text
    assert "validation-result.json" not in validate_text
    assert "exit 0" not in validate_text
    assert "exit_codes" not in validate_text
    validate_script = validate["script"][0]
    assert validate_script.index("unset product_url CI_JOB_TOKEN") < (
        validate_script.index("package-proposal")
    )


def test_gitlab_jobs_clean_bytecode_before_starting_python():
    _, pipeline = _pipeline()
    before_script = pipeline[".om-plan-python-job"]["before_script"]

    assert before_script[0] == (
        'sh harness/ci/prepare_trusted_checker.sh "$CI_PROJECT_DIR"'
    )
    assert before_script[1] == 'test "${GIT_STRATEGY:-}" = "clone"'
    assert before_script[2] == "export PYTHONDONTWRITEBYTECODE=1"
    assert "python3 -m venv" in before_script[5]
    assert pipeline["variables"]["PYTHONDONTWRITEBYTECODE"] == "1"
    for job_name in (
        "om_plan_preflight",
        "om_plan_package_proposal",
        "om_plan_validate",
    ):
        assert pipeline[job_name]["extends"] == ".om-plan-python-job"


def test_cache_cleaner_neutralizes_timestamp_valid_crafted_pyc(tmp_path: Path):
    checker = tmp_path / "checker"
    harness = checker / "harness"
    harness.mkdir(parents=True)
    _git(checker, "init", "-q")
    _git(checker, "config", "user.email", "test@example.com")
    _git(checker, "config", "user.name", "Test")

    source = harness / "fixture.py"
    benign = "VALUE = 'benign'\n"
    malicious = "VALUE = 'PWNED!'\n"
    assert len(benign.encode()) == len(malicious.encode())
    source.write_text(benign, encoding="utf-8")
    _git(checker, "add", "harness/fixture.py")
    _git(checker, "commit", "-q", "-m", "trusted source")

    fixed_time = 1_700_000_000
    source.write_text(malicious, encoding="utf-8")
    os.utime(source, (fixed_time, fixed_time))
    cache = Path(importlib.util.cache_from_source(str(source)))
    cache.parent.mkdir()
    py_compile.compile(str(source), cfile=str(cache), doraise=True)
    source.write_text(benign, encoding="utf-8")
    os.utime(source, (fixed_time, fixed_time))

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(harness)
    environment.pop("PYTHONDONTWRITEBYTECODE", None)
    poisoned = subprocess.run(
        [sys.executable, "-c", "import fixture; print(fixture.VALUE)"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    assert poisoned.stdout.strip() == "PWNED!"

    subprocess.run(
        ["sh", str(CACHE_CLEANER), str(checker)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert not cache.parent.exists()
    assert _git(checker, "status", "--short") == ""

    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    cleaned = subprocess.run(
        [sys.executable, "-c", "import fixture; print(fixture.VALUE)"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )
    assert cleaned.stdout.strip() == "benign"
    assert not cache.parent.exists()
