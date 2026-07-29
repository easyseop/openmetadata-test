#!/usr/bin/env python3
"""Plan and safely apply BANK-OM registration preparation changes."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from acgh.registration_prep import (
    ApplyLockError,
    PreparationError,
    StaleProposalError,
    approval_template,
    apply_plan,
    build_plan,
    load_proposal,
    write_plan,
)

EXIT_CODES = {
    "READY": 0,
    "BLOCKED": 1,
    "REVIEW_REQUIRED": 2,
    "ANALYSIS_ERROR": 3,
    "APPLIED": 0,
}


def _json(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _metadata(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PreparationError("new-ID input must be a mapping keyed by BANK-OM ID")
    return data


def _plan(args: argparse.Namespace) -> int:
    proposal = build_plan(
        args.repo,
        args.registration,
        patch_ref=args.patch_ref,
        custom_ref=args.custom_ref,
        product_version=args.product_version,
        new_id_metadata=_metadata(args.new_id_input),
    )
    digest = write_plan(
        args.output,
        proposal,
        registration=args.registration,
    )
    result = {
        "status": proposal["status"],
        "proposal_digest": digest,
        "output": str(args.output.absolute()),
        "change_count": len(proposal["changes"]),
        "review_count": len(proposal["review_required"]),
        "blocked_count": len(proposal["blocked"]),
        "analysis_error_count": len(proposal["analysis_errors"]),
    }
    _json(result)
    return EXIT_CODES[proposal["status"]]


def _approval_template(args: argparse.Namespace) -> int:
    if args.output.exists():
        raise PreparationError(f"approval template already exists: {args.output}")
    proposal = load_proposal(args.proposal)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(
            approval_template(proposal),
            allow_unicode=True,
            sort_keys=False,
            width=1000,
        ),
        encoding="utf-8",
    )
    _json({"status": "TEMPLATE_WRITTEN", "output": str(args.output.absolute())})
    return 0


def _apply(args: argparse.Namespace) -> int:
    result = apply_plan(
        args.repo,
        args.registration,
        proposal_path=args.proposal,
        approval_path=args.approval,
    )
    if args.result is not None:
        if args.result.exists():
            raise PreparationError(f"apply result already exists: {args.result}")
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    _json(result)
    return EXIT_CODES[result["status"]]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Git facts and BANK-OM policy inputs are separated into an immutable "
            "proposal and a digest-bound approval."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="analyze without changing registration")
    plan.add_argument("--repo", required=True, type=Path)
    plan.add_argument("--registration", required=True, type=Path)
    plan.add_argument("--patch-ref", required=True)
    plan.add_argument("--custom-ref", required=True)
    plan.add_argument("--product-version", required=True)
    plan.add_argument("--output", required=True, type=Path)
    plan.add_argument("--new-id-input", type=Path)
    plan.set_defaults(handler=_plan)

    template = subparsers.add_parser(
        "approval-template", help="create an unapproved template for one proposal"
    )
    template.add_argument("--proposal", required=True, type=Path)
    template.add_argument("--output", required=True, type=Path)
    template.set_defaults(handler=_approval_template)

    apply = subparsers.add_parser(
        "apply", help="apply one unchanged proposal with an exact approval"
    )
    apply.add_argument("--repo", required=True, type=Path)
    apply.add_argument("--registration", required=True, type=Path)
    apply.add_argument("--proposal", required=True, type=Path)
    apply.add_argument("--approval", required=True, type=Path)
    apply.add_argument("--result", type=Path)
    apply.set_defaults(handler=_apply)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return args.handler(args)
    except StaleProposalError as exc:
        _json({"status": "BLOCKED", "code": "STALE_PROPOSAL", "message": str(exc)})
        return 1
    except ApplyLockError as exc:
        _json({"status": "BLOCKED", "code": "APPLY_LOCKED", "message": str(exc)})
        return 1
    except (PreparationError, OSError, yaml.YAMLError) as exc:
        _json({"status": "ANALYSIS_ERROR", "message": str(exc)})
        return 3


if __name__ == "__main__":
    sys.exit(main())
