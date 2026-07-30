#!/usr/bin/env python3
"""Run the shared T41/T43/T93-policy upgrade-risk command."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    implementation = (
        Path(__file__).parent
        / "registrations"
        / "kb-openmetadata"
        / "run_upgrade_risk_gates.py"
    )
    runpy.run_path(str(implementation), run_name="__main__")
