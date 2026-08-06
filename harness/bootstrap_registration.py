#!/usr/bin/env python3
"""Create and apply a version-independent initial registration proposal."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from acgh.initial_registration import (
    InitialRegistrationError,
    StaleInitialRegistrationError,
    apply_plan,
    build_plan,
    write_approval_template,
    write_plan,
)
from acgh.gitprim import GitPrimitiveError


EXIT_CODES = {
    "PROPOSAL_WRITTEN": 2,
    "TEMPLATE_WRITTEN": 0,
    "APPLIED": 0,
    "BLOCKED": 1,
    "ANALYSIS_ERROR": 3,
}


def _print(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Git에서 commit·경로를 계산하고 사람이 작성한 업무 입력과 합쳐 "
            "버전에 관계없는 최초 등록 제안을 만듭니다."
        )
    )
    commands = parser.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan", help="활성 등록 폴더를 수정하지 않고 제안 생성")
    plan.add_argument("--repo", required=True, type=Path)
    plan.add_argument("--registration", required=True, type=Path)
    plan.add_argument("--official-ref", required=True)
    plan.add_argument("--custom-ref", required=True)
    plan.add_argument("--product-version", required=True)
    plan.add_argument("--input", required=True, type=Path)
    plan.add_argument("--output", required=True, type=Path)

    template = commands.add_parser(
        "approval-template", help="최초 등록 제안의 승인 양식 생성"
    )
    template.add_argument("--proposal", required=True, type=Path)
    template.add_argument("--output", required=True, type=Path)

    apply = commands.add_parser("apply", help="승인한 최초 등록 제안을 반영")
    apply.add_argument("--repo", required=True, type=Path)
    apply.add_argument("--registration", required=True, type=Path)
    apply.add_argument("--proposal", required=True, type=Path)
    apply.add_argument("--approval", required=True, type=Path)
    apply.add_argument("--result", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "plan":
            proposal, generated = build_plan(
                args.repo,
                args.registration,
                args.input,
                official_ref=args.official_ref,
                custom_ref=args.custom_ref,
                product_version=args.product_version,
            )
            digest = write_plan(args.output, proposal, generated)
            _print(
                {
                    "status": "PROPOSAL_WRITTEN",
                    "proposal": str(args.output / "proposal.yaml"),
                    "proposal_digest": digest,
                    **proposal["facts"],
                }
            )
            return EXIT_CODES["PROPOSAL_WRITTEN"]

        if args.command == "approval-template":
            write_approval_template(args.proposal, args.output)
            _print({"status": "TEMPLATE_WRITTEN", "approval": str(args.output)})
            return EXIT_CODES["TEMPLATE_WRITTEN"]

        result = apply_plan(
            args.repo,
            args.registration,
            proposal_path=args.proposal,
            approval_path=args.approval,
        )
        if args.result.exists():
            raise InitialRegistrationError(
                f"apply result already exists: {args.result}"
            )
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _print(result)
        return EXIT_CODES["APPLIED"]
    except StaleInitialRegistrationError as exc:
        _print({"status": "BLOCKED", "code": "STALE_PROPOSAL", "message": str(exc)})
        return EXIT_CODES["BLOCKED"]
    except (InitialRegistrationError, GitPrimitiveError, OSError, yaml.YAMLError) as exc:
        _print({"status": "ANALYSIS_ERROR", "message": str(exc)})
        return EXIT_CODES["ANALYSIS_ERROR"]


if __name__ == "__main__":
    sys.exit(main())
