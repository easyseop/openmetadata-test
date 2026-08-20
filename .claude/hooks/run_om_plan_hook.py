#!/usr/bin/env python3
"""Runtime-checked entry point for the installed Claude Code hook."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _runtime_error() -> str | None:
    if sys.version_info < (3, 11):
        return (
            "om-plan hook requires Python 3.11 or newer; "
            f"current interpreter is {sys.version_info.major}.{sys.version_info.minor}"
        )
    missing: list[str] = []
    for module_name in ("yaml", "jsonschema", "pathspec"):
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)
    if missing:
        return "om-plan hook is missing Python dependencies: " + ", ".join(missing)
    return None


def main() -> int:
    error = _runtime_error()
    if error:
        print(error, file=sys.stderr)
        return 2

    project_dir = Path(
        os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2])
    ).resolve()
    harness_dir = project_dir / "harness"
    if not (harness_dir / "acgh" / "plancore" / "hook_cli.py").is_file():
        print(f"om-plan hook cannot find the harness under {project_dir}", file=sys.stderr)
        return 2
    sys.path.insert(0, str(harness_dir))

    os.environ.setdefault(
        "OM_PLAN_HOOK_STATE_ROOT",
        str(
            Path.home()
            / ".local"
            / "state"
            / "kb-datacatalog-upgrade-checker"
            / "om-plan"
        ),
    )
    from acgh.plancore.hook_cli import main as hook_main

    return hook_main()


if __name__ == "__main__":
    raise SystemExit(main())
