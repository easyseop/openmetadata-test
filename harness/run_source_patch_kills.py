#!/usr/bin/env python3
"""Run the shared T61 source patch-kill command."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    implementation = (
        Path(__file__).parent
        / "registrations"
        / "kb-openmetadata"
        / "run_source_patch_kills.py"
    )
    runpy.run_path(str(implementation), run_name="__main__")
