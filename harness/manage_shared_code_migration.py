#!/usr/bin/env python3
"""Public CLI for versioned shared-code definition migration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import yaml

from acgh import gitprim
from acgh import shared_code_migration as migration
import run_phase_bundle


PROJECT = Path(__file__).resolve().parents[1]


def _load(path: Path, label: str) -> dict:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise migration.MigrationError(f"cannot load {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise migration.MigrationError(f"{label} must be a mapping")
    return payload


def _write_new(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).encode("utf-8")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        raise migration.MigrationError(f"refusing to overwrite existing file: {path}") from exc
    try:
        os.write(fd, blob)
        os.fsync(fd)
    finally:
        os.close(fd)


def _harness_identity() -> tuple[str, str]:
    return (
        gitprim.resolve_commit(str(PROJECT), "HEAD"),
        run_phase_bundle._harness_version(),
    )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Create, approve, and apply versioned shared-code migrations"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    propose = sub.add_parser("propose")
    propose.add_argument("--repo", required=True)
    propose.add_argument("--source-registration", required=True, type=Path)
    propose.add_argument("--source-version", required=True)
    propose.add_argument("--target-version", required=True)
    propose.add_argument("--candidate", required=True)
    propose.add_argument("--upstream-target", required=True)
    propose.add_argument("--structural-evidence", required=True, type=Path)
    propose.add_argument("--decisions", required=True, type=Path)
    propose.add_argument("--output", required=True, type=Path)

    template = sub.add_parser("approval-template")
    template.add_argument("--proposal", required=True, type=Path)
    template.add_argument("--output", required=True, type=Path)

    apply = sub.add_parser("apply")
    apply.add_argument("--repo", required=True)
    apply.add_argument("--source-registration", required=True, type=Path)
    apply.add_argument("--target-registration", required=True, type=Path)
    apply.add_argument("--proposal", required=True, type=Path)
    apply.add_argument("--approval", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    try:
        args = parse_args(argv)
        harness_commit, harness_digest = _harness_identity()
        if args.command == "propose":
            proposal = migration.build_proposal(
                repo=args.repo,
                source_registration=args.source_registration,
                source_version=args.source_version,
                target_version=args.target_version,
                candidate_ref=args.candidate,
                upstream_target_ref=args.upstream_target,
                structural_evidence=_load(args.structural_evidence, "structural evidence"),
                decisions=_load(args.decisions, "migration decisions"),
                harness_commit=harness_commit,
                harness_digest=harness_digest,
            )
            _write_new(args.output, proposal)
            result = {
                "status": "proposal_created",
                "output": str(args.output),
                "proposal_digest": proposal["proposal_digest"],
                "item_count": len(proposal["items"]),
                "requires_human_approval": True,
            }
        elif args.command == "approval-template":
            proposal = _load(args.proposal, "migration proposal")
            template = migration.approval_template(proposal)
            _write_new(args.output, template)
            result = {
                "status": "approval_template_created",
                "output": str(args.output),
                "proposal_digest": template["proposal_digest"],
                "next_action": (
                    "담당자가 모든 항목과 기능 test 근거를 검토한 뒤 승인 파일을 "
                    "직접 작성하십시오. 도구는 조직 권한을 확인하지 않습니다."
                ),
            }
        else:
            result = migration.apply_proposal(
                repo=args.repo,
                source_registration=args.source_registration,
                target_registration=args.target_registration,
                proposal=_load(args.proposal, "migration proposal"),
                approval=_load(args.approval, "migration approval"),
                harness_commit=harness_commit,
                harness_digest=harness_digest,
            )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (migration.MigrationError, gitprim.GitPrimitiveError, OSError, ValueError) as exc:
        print(json.dumps({
            "status": "analysis_error",
            "reason": str(exc),
        }, ensure_ascii=False, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
