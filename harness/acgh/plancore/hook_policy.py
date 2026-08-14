"""Default-deny decisions for a future command hook installation."""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from acgh.plancore.errors import PlanControlError
from acgh.plancore.markers import load_session_marker, pair_from_run

_SHELL_OPERATORS = re.compile(r"(?:&&|\|\||[;|<>`]|\$\()")
_GIT_MUTATIONS = {
    "commit",
    "push",
    "merge",
    "rebase",
    "reset",
    "clean",
    "stash",
    "tag",
    "checkout",
    "switch",
    "branch",
    "fetch",
}
_WORKTREE_MUTATIONS = {"add", "remove", "move", "prune"}


@dataclass(frozen=True)
class HookDecision:
    allowed: bool
    reason: str
    allowed_proposal_dir: str | None = None


def _within(path: str | Path, root: Path) -> bool:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _workflow_action(command: str) -> str | None:
    if _SHELL_OPERATORS.search(command):
        return None
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    for index, token in enumerate(tokens[:-1]):
        if token.endswith("om_workflow.py") and tokens[index + 1] in {
            "plan-preflight",
            "plan-validate",
        }:
            return tokens[index + 1]
    return None


def _contains_git_mutation(command: str) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return True
    for index, token in enumerate(tokens):
        if token != "git":
            continue
        remaining = tokens[index + 1 :]
        cursor = 0
        while cursor < len(remaining):
            value = remaining[cursor]
            if value == "-C" and cursor + 1 < len(remaining):
                cursor += 2
                continue
            if value.startswith("-"):
                cursor += 1
                continue
            if value in _GIT_MUTATIONS:
                return True
            if value == "worktree":
                return any(part in _WORKTREE_MUTATIONS for part in remaining[cursor + 1 :])
            break
    return False


def decide_pre_tool_use(
    *,
    session_marker: str | Path,
    tool_name: str,
    target_path: str | Path | None = None,
    command: str | None = None,
) -> HookDecision:
    session = load_session_marker(session_marker)
    run_dir_value = session.get("run_dir")
    run_pair = None
    proposal_dir = None
    if run_dir_value:
        run_pair = pair_from_run(run_dir_value)
        if run_pair.session_id != session.get("session_id"):
            raise PlanControlError(
                "MARKER_OWNERSHIP_MISMATCH",
                "session marker and run marker belong to different sessions",
            )
        proposal_dir = Path(run_dir_value).resolve() / "proposal"

    if tool_name in {"Read", "Glob", "Grep"}:
        return HookDecision(True, "read-only tool")

    if command is not None:
        if _contains_git_mutation(command):
            return HookDecision(False, "Git state mutation is blocked")
        action = _workflow_action(command)
        if run_pair is None and action == "plan-preflight":
            return HookDecision(True, "trusted preflight establishes the run")
        if run_pair is not None and action == "plan-validate":
            return HookDecision(
                True,
                "trusted validation may append results and clean markers",
                str(proposal_dir),
            )
        return HookDecision(
            False,
            "only the trusted planning workflow command is allowed while protected",
            str(proposal_dir) if proposal_dir else None,
        )

    if tool_name in {"Write", "Edit", "MultiEdit"}:
        if run_pair is None:
            return HookDecision(False, "preflight has not established a run")
        if target_path is not None and _within(target_path, proposal_dir):
            return HookDecision(True, "write is inside the current proposal directory", str(proposal_dir))
        return HookDecision(
            False,
            f"write is outside the allowed proposal directory: {proposal_dir}",
            str(proposal_dir),
        )

    return HookDecision(False, f"tool is not allowed while protected: {tool_name}")


def stop_is_allowed(session_marker: str | Path) -> HookDecision:
    session = load_session_marker(session_marker)
    run_dir = session.get("run_dir")
    if not run_dir:
        return HookDecision(False, "preflight did not establish a run")
    result = Path(run_dir) / "validation-result.json"
    if not result.is_file():
        return HookDecision(False, "validation-result.json is missing")
    return HookDecision(True, "validation result exists")
