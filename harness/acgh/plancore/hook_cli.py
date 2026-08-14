"""Claude Code hook adapter for the product-neutral plan controls.

This module is installable infrastructure, not an installed project hook.  It
uses only hook event data plus an external runtime-state directory; installation
under a project's control directory is a later, separately approved step.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from acgh.plancore.errors import PlanControlError
from acgh.plancore.hook_policy import decide_pre_tool_use, stop_is_allowed
from acgh.plancore.markers import create_session_marker, session_marker_path


def _required(payload: dict, name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str) or not value:
        raise PlanControlError(
            "HOOK_INPUT_INVALID",
            f"hook input is missing {name}",
            details={"field": name},
        )
    return value


def _marker(payload: dict, state_root: str | Path) -> Path:
    return session_marker_path(
        state_root,
        _required(payload, "cwd"),
        _required(payload, "session_id"),
    )


def _deny(event: str, reason: str) -> dict:
    if event == "PreToolUse":
        return {
            "hookSpecificOutput": {
                "hookEventName": event,
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    return {"decision": "block", "reason": reason}


def handle_event(payload: dict, state_root: str | Path) -> dict | None:
    """Return the hook protocol decision, or ``None`` for no decision."""
    event = _required(payload, "hook_event_name")
    marker = _marker(payload, state_root)

    if event == "UserPromptSubmit":
        prompt = payload.get("prompt")
        if not isinstance(prompt, str) or not prompt.lstrip().startswith(
            ("/om-plan", "/om-resume")
        ):
            return None
        if marker.exists():
            return _deny(event, "this session already has an active planning run")
        create_session_marker(
            state_root,
            _required(payload, "cwd"),
            _required(payload, "session_id"),
        )
        return None

    if not marker.exists():
        return None

    if event == "PreToolUse":
        tool_name = _required(payload, "tool_name")
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            return _deny(event, "tool_input is missing or invalid")
        target = tool_input.get("file_path")
        command = tool_input.get("command")
        decision = decide_pre_tool_use(
            session_marker=marker,
            tool_name=tool_name,
            target_path=target if isinstance(target, str) else None,
            command=command if isinstance(command, str) else None,
        )
        if decision.allowed:
            return None
        return _deny(event, decision.reason)

    if event == "Stop":
        decision = stop_is_allowed(marker)
        if decision.allowed:
            return None
        suffix = ""
        if payload.get("stop_hook_active") is True:
            suffix = "; validation is still incomplete—do not synthesize a pass"
        return _deny(event, decision.reason + suffix)

    return None


def main() -> int:
    state_root = os.environ.get("OM_PLAN_HOOK_STATE_ROOT")
    if not state_root:
        print("OM_PLAN_HOOK_STATE_ROOT is required", file=sys.stderr)
        return 2
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise PlanControlError("HOOK_INPUT_INVALID", "hook input must be an object")
        output = handle_event(payload, state_root)
        if output is not None:
            print(json.dumps(output, ensure_ascii=False))
        return 0
    except (json.JSONDecodeError, PlanControlError) as exc:
        message = exc.message if isinstance(exc, PlanControlError) else str(exc)
        print(message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
