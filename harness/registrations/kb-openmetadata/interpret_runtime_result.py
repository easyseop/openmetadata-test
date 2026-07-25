#!/usr/bin/env python3
"""Fail-closed T15 adapter for the runtime-contract GitHub Actions boundary."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--candidate-lock", type=Path, required=True)
    parser.add_argument("--test-run-set", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--actual-exit", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    harness = args.harness.resolve(strict=True)
    root = args.root.resolve(strict=True)
    sys.path.insert(0, str(harness))

    from acgh import binding
    from acgh import candidate
    from acgh import result_io
    from acgh import testruns
    from acgh import verdict

    expected_inputs = None
    harness_version = None
    try:
        lock = candidate.load_candidate_lock(args.candidate_lock)
        run_set = testruns.load_test_run_set(args.test_run_set)
        expected_inputs = lock.result_inputs(
            verifier_catalog_digest=run_set.suite_version
        )
        harness_version = binding.pin(str(root), "HEAD")
    except Exception:
        # interpret_result will convert missing/corrupt result evidence to a
        # synthetic analysis_error. If the result itself exists but its bound
        # inputs cannot be reconstructed, force the same fail-closed outcome.
        if args.result.exists():
            print(
                json.dumps(
                    {
                        "verdict": verdict.ANALYSIS_ERROR,
                        "exit_code": verdict.to_exit_code(
                            verdict.ANALYSIS_ERROR
                        ),
                        "reason": (
                            "cannot reconstruct expected runtime result inputs"
                        ),
                        "synthetic": True,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return verdict.to_exit_code(verdict.ANALYSIS_ERROR)

    decision = result_io.interpret_result(
        args.result,
        actual_exit=args.actual_exit,
        expected_inputs=expected_inputs,
        harness_version=harness_version,
    )
    print(
        json.dumps(
            {
                "verdict": decision.verdict,
                "exit_code": decision.exit_code,
                "reason": decision.reason,
                "synthetic": decision.synthetic,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return decision.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
