#!/usr/bin/env python3
"""Compatibility entry point for the registration preparation planner.

This file intentionally contains no BANK-OM commit SHA or business-policy
constant. New automation should call ``harness/prepare_registration.py plan``
directly; this wrapper preserves the old discoverable filename.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HARNESS = Path(__file__).resolve().parents[2]
if str(_HARNESS) not in sys.path:
    sys.path.insert(0, str(_HARNESS))

from acgh.registration_prep import build_plan, write_plan  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a read-only OM_TEMP registration proposal."
    )
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument(
        "--registration",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--patch-ref", required=True)
    parser.add_argument("--custom-ref", required=True)
    parser.add_argument("--product-version", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    proposal = build_plan(
        args.repo,
        args.registration,
        patch_ref=args.patch_ref,
        custom_ref=args.custom_ref,
        product_version=args.product_version,
    )
    digest = write_plan(
        args.output,
        proposal,
        registration=args.registration,
    )
    print(f"status={proposal['status']}")
    print(f"proposal_digest={digest}")
    print(f"output={args.output.resolve()}")
    return {
        "READY": 0,
        "BLOCKED": 1,
        "REVIEW_REQUIRED": 2,
        "ANALYSIS_ERROR": 3,
    }[proposal["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
