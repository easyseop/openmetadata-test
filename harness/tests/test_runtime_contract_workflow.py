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
        == "38bccf90779a8afe4a4f0e9313e11706f6d940d4"
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
