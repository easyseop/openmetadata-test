#!/usr/bin/env python3
"""Run the shared source-candidate gate command.

The implementation remains at its original path for compatibility with the
existing KB registration documents. New registrations can use this neutral
entry point instead of referring to another product-registration directory.
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    implementation = (
        Path(__file__).parent
        / "registrations"
        / "kb-openmetadata"
        / "run_source_candidate_gates.py"
    )
    runpy.run_path(str(implementation), run_name="__main__")
