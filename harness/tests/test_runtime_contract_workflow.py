"""Supply-chain and fail-closed checks for the runtime contract workflow."""
import re
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _ROOT / ".github" / "workflows" / "runtime-contracts.yml"


def _load():
    return yaml.load(
        _WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader
    )


def test_runtime_workflow_is_manual_read_only_and_candidate_locked():
    workflow = _load()
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert (
        workflow["env"]["PRODUCT_SHA"]
        == "b80d24d83124435733d5af05d56515b3a855330e"
    )
    job = workflow["jobs"]["contracts"]
    assert job["environment"] == "openmetadata-runtime"
    assert "continue-on-error" not in _WORKFLOW.read_text(encoding="utf-8")


def test_runtime_workflow_requires_identity_and_live_inputs():
    workflow = _load()
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert {
        "artifact_digest",
        "base_url",
        "ime_editor_url",
        "data_assertions_url",
        "bank_column_ui_url",
    }.issubset(inputs)
    assert all(inputs[name]["required"] == "true" for name in inputs)

    steps = workflow["jobs"]["contracts"]["steps"]
    action_uses = [step["uses"] for step in steps if "uses" in step]
    assert action_uses
    assert all(
        re.fullmatch(r"[a-z0-9_-]+/[a-z0-9_-]+@[0-9a-f]{40}", item)
        for item in action_uses
    )
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "run_runtime_contracts.py" in commands
    assert "--artifact-digest" in commands
    assert "${{ inputs.artifact_digest }}" not in commands
    assert "playwright install --with-deps chromium" in commands
    assert "GITHUB_STEP_SUMMARY" in commands
    assert "actual_exit=$?" in commands
    assert "interpret_runtime_result.py" in commands
    assert "--actual-exit" in commands
    assert '--run-id "${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"' in commands

    upload = next(
        step for step in steps if step.get("name") == "Preserve runtime evidence"
    )
    assert (
        upload["uses"]
        == "actions/upload-artifact@"
        "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
    )
    assert upload["if"] == "always()"
    assert upload["with"]["if-no-files-found"] == "error"
    assert upload["with"]["retention-days"] == "90"
    assert upload["with"]["overwrite"] == "false"
    assert upload["with"]["include-hidden-files"] == "false"
    assert "runtime-evidence/*.yaml" in upload["with"]["path"]
