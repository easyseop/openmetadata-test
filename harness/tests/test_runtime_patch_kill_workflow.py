"""Supply-chain and fail-closed checks for runtime patch-kill CI."""

import re
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _ROOT / ".github" / "workflows" / "runtime-patch-kill.yml"


def _load():
    return yaml.load(
        _WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader
    )


def test_workflow_is_manual_read_only_and_separately_approved():
    workflow = _load()
    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "false"
    assert (
        workflow["env"]["PRODUCT_SHA"]
        == "849ae756cd238f218b5e3a6c795a392305cb32ee"
    )
    job = workflow["jobs"]["negative-control"]
    assert job["environment"] == "openmetadata-runtime-patch-kill"
    assert "continue-on-error" not in _WORKFLOW.read_text(encoding="utf-8")


def test_workflow_requires_identity_inputs_and_preserves_evidence():
    workflow = _load()
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    required = {
        "customization_id",
        "counterfactual_artifact_digest",
        "deployment_evidence_digest",
        "target_environment",
        "base_url",
    }
    assert all(inputs[name]["required"] == "true" for name in required)
    assert inputs["customization_id"]["options"] == [
        "BANK-OM-001",
        "BANK-OM-002",
        "BANK-OM-003",
    ]

    steps = workflow["jobs"]["negative-control"]["steps"]
    action_uses = [step["uses"] for step in steps if "uses" in step]
    assert action_uses
    assert all(
        re.fullmatch(r"[a-z0-9_-]+/[a-z0-9_-]+@[0-9a-f]{40}", item)
        for item in action_uses
    )
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "run_runtime_patch_kill.py" in commands
    assert "interpret_runtime_patch_kill_result.py" in commands
    assert "actual_exit=$?" in commands
    assert "playwright install --with-deps chromium" in commands
    assert "--deployment-evidence-digest" in commands
    assert "--target-environment" in commands
    assert "${{ inputs.counterfactual_artifact_digest }}" not in commands

    upload = next(
        step
        for step in steps
        if step.get("name") == "Preserve runtime patch-kill evidence"
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
