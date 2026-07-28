#!/usr/bin/env python3
"""Validate the isolated phase-four upgrade rehearsal matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(args.harness))
    from acgh import rehearsal
    from acgh import verdict

    try:
        plan = rehearsal.load_plan(args.matrix)
        result = rehearsal.inspect_plan(args.repo, plan)
    except rehearsal.RehearsalPlanError as exc:
        result = {
            "schema_version": 1,
            "verdict": verdict.ANALYSIS_ERROR,
            "errors": [str(exc)],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return verdict.to_exit_code(result["verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
