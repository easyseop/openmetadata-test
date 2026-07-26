#!/usr/bin/env python3
"""Compare complete upstream and candidate tsc logs without weakening failures."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--upstream-log", type=Path, required=True)
    parser.add_argument("--candidate-log", type=Path, required=True)
    parser.add_argument("--upstream-exit", type=int, required=True)
    parser.add_argument("--candidate-exit", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(args.harness.resolve(strict=True)))

    from acgh import tsc_baseline
    from acgh import verdict

    result = tsc_baseline.compare(
        args.upstream_log.read_text(encoding="utf-8"),
        args.candidate_log.read_text(encoding="utf-8"),
        upstream_exit=args.upstream_exit,
        candidate_exit=args.candidate_exit,
    )
    print(
        json.dumps(
            {
                "name": result.name,
                "verdict": result.verdict,
                "reasons": list(result.reasons),
                "exit_code": verdict.to_exit_code(result.verdict),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return verdict.to_exit_code(result.verdict)


if __name__ == "__main__":
    raise SystemExit(main())
