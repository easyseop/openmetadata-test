#!/usr/bin/env python3
"""Create and apply a version-independent initial registration proposal."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from acgh.initial_registration import (
    ApprovalValidationError,
    BlockedInitialRegistrationError,
    InitialRegistrationError,
    StaleInitialRegistrationError,
    apply_plan,
    build_input_template,
    build_plan,
    write_input_template,
    write_approval_template,
    write_plan,
)
from acgh.gitprim import GitPrimitiveError


EXIT_CODES = {
    "INPUT_TEMPLATE_WRITTEN": 0,
    "INPUT_TEMPLATE_EXISTS": 0,
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

    input_template = commands.add_parser(
        "input-template", help="Git commit 이력에서 최초 등록 업무 입력 양식 생성"
    )
    input_template.add_argument("--repo", required=True, type=Path)
    input_template.add_argument("--official-ref", required=True)
    input_template.add_argument("--custom-ref", required=True)
    input_template.add_argument("--repository", required=True)
    input_template.add_argument("--upstream-repository", required=True)
    input_template.add_argument("--upstream-tag", required=True)
    input_template.add_argument("--output", required=True, type=Path)

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
        if args.command == "input-template":
            template = build_input_template(
                args.repo,
                official_ref=args.official_ref,
                custom_ref=args.custom_ref,
                repository=args.repository,
                upstream_repository=args.upstream_repository,
                upstream_tag=args.upstream_tag,
            )
            created = write_input_template(args.output, template)
            status = (
                "INPUT_TEMPLATE_WRITTEN" if created else "INPUT_TEMPLATE_EXISTS"
            )
            _print(
                {
                    "status": status,
                    "input": str(args.output),
                    "customization_count": len(template["customizations"]),
                    "contract_count": len(template["contracts"]),
                }
            )
            return EXIT_CODES[status]

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
            facts = proposal["facts"]
            status = "BLOCKED" if not proposal["apply_ready"] else "PROPOSAL_WRITTEN"
            _print(
                {
                    "status": status,
                    "proposal": str(args.output / "proposal.yaml"),
                    "summary": str(args.output / "summary.md"),
                    "proposed_registration": str(
                        args.output / "proposed-registration"
                    ),
                    "proposal_digest": digest,
                    "customization_count": facts["customization_count"],
                    "commit_count": facts["commit_count"],
                    "changed_path_count": facts["changed_path_count"],
                    "shared_path_count": facts["shared_path_count"],
                    "blocking_findings": proposal.get("blocking_findings", []),
                    "next_action": (
                        "summary.md의 반드시 수정할 항목을 고치고 새 실행 ID로 "
                        "bootstrap-plan을 다시 실행합니다."
                        if status == "BLOCKED"
                        else "summary.md와 proposed-registration을 검토합니다."
                    ),
                }
            )
            return EXIT_CODES[status]

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
    except ApprovalValidationError as exc:
        result = exc.as_result()
        if getattr(args, "command", None) == "apply":
            result["file"] = str(args.approval)
        _print(result)
        return EXIT_CODES["ANALYSIS_ERROR"]
    except BlockedInitialRegistrationError as exc:
        _print(
            {
                "status": "BLOCKED",
                "code": "PROPOSAL_NOT_APPLY_READY",
                "message": str(exc),
            }
        )
        return EXIT_CODES["BLOCKED"]
    except StaleInitialRegistrationError as exc:
        _print({"status": "BLOCKED", "code": "STALE_PROPOSAL", "message": str(exc)})
        return EXIT_CODES["BLOCKED"]
    except (InitialRegistrationError, GitPrimitiveError, OSError, yaml.YAMLError) as exc:
        _print({"status": "ANALYSIS_ERROR", "message": str(exc)})
        return EXIT_CODES["ANALYSIS_ERROR"]


if __name__ == "__main__":
    sys.exit(main())
