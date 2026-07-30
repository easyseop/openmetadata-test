#!/usr/bin/env python3
"""Run the shared T63 upstream-versus-candidate TypeScript comparison."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    implementation = (
        Path(__file__).parent
        / "registrations"
        / "kb-openmetadata"
        / "compare_ui_typecheck.py"
    )
    runpy.run_path(str(implementation), run_name="__main__")
