"""Static and runtime checks for the installed Claude Code wiring."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from collections import namedtuple
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".claude" / "settings.json"
SHELL_WRAPPER = ROOT / ".claude" / "hooks" / "run_om_plan_hook.sh"
PYTHON_WRAPPER = ROOT / ".claude" / "hooks" / "run_om_plan_hook.py"


def test_settings_wires_all_required_events_and_denies_mutations():
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    assert set(settings["hooks"]) == {
        "UserPromptSubmit",
        "UserPromptExpansion",
        "PreToolUse",
        "Stop",
    }
    assert settings["hooks"]["UserPromptExpansion"][0]["matcher"] == (
        "^(om-plan|om-resume)$"
    )
    commands = [
        hook["command"]
        for groups in settings["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]
    assert commands
    assert all("run_om_plan_hook.sh" in command for command in commands)
    denied = "\n".join(settings["permissions"]["deny"])
    for operation in ("apply", "git push", "git tag", "docker push"):
        assert operation in denied


def test_shell_wrapper_has_valid_posix_syntax():
    subprocess.run(["sh", "-n", str(SHELL_WRAPPER)], check=True)


def test_python_wrapper_reports_old_interpreter_before_importing_harness():
    spec = importlib.util.spec_from_file_location("om_plan_hook_wrapper", PYTHON_WRAPPER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    Version = namedtuple("Version", "major minor")
    original = module.sys.version_info
    try:
        module.sys.version_info = Version(3, 9)
        assert module._runtime_error() == (
            "om-plan hook requires Python 3.11 or newer; "
            "current interpreter is 3.9"
        )
    finally:
        module.sys.version_info = original


def test_independent_review_agent_is_read_only_and_separate():
    source = (
        ROOT / ".claude" / "agents" / "om-plan-official-doc-reviewer.md"
    ).read_text(encoding="utf-8")
    assert "tools: Read, Glob, Grep" in source
    assert "independent_agent" in source
    assert "Do not modify any file" in source
