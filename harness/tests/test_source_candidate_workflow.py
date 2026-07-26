"""Supply-chain and lock checks for the source-candidate CI workflow."""

import re
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _ROOT / ".github" / "workflows" / "source-candidate.yml"
_EVIDENCE = (
    _ROOT
    / "harness"
    / "registrations"
    / "kb-openmetadata"
    / "source-candidate-evidence.yaml"
)


def _load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_source_candidate_workflow_is_read_only_and_candidate_locked():
    workflow = _load(_WORKFLOW)
    evidence = _load(_EVIDENCE)

    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["env"]["PRODUCT_REPOSITORY"] == evidence["repository"]
    assert workflow["env"]["PRODUCT_BRANCH"] == evidence["branch"]
    assert (
        workflow["env"]["PRODUCT_SHA"]
        == evidence["candidate"]["commit_sha"]
    )


def test_source_candidate_workflow_pins_actions_and_runs_all_source_gates():
    workflow = _load(_WORKFLOW)
    steps = workflow["jobs"]["governance"]["steps"]
    action_uses = [step["uses"] for step in steps if "uses" in step]

    assert action_uses
    assert all(
        re.fullmatch(r"[a-z0-9_-]+/[a-z0-9_-]+@[0-9a-f]{40}", item)
        for item in action_uses
    )
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "pytest harness/tests tests/bank/contracts -ra" in commands
    assert "run_source_candidate_gates.py" in commands
    assert "run_source_patch_kills.py" in commands
    assert '--run-id "${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"' in commands
    assert "--filter=blob:none" in commands
    assert "rev-parse HEAD" in commands

    upload = next(
        step
        for step in steps
        if step.get("name") == "Preserve source patch-kill evidence"
    )
    assert (
        upload["uses"]
        == "actions/upload-artifact@"
        "ea165f8d65b6e75b540449e92b4886f43607fa02"
    )
    assert upload["if"] == "always()"
    assert upload["with"]["if-no-files-found"] == "error"
    assert upload["with"]["retention-days"] == "90"
    assert upload["with"]["overwrite"] == "false"
    assert upload["with"]["include-hidden-files"] == "false"
