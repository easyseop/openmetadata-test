#!/usr/bin/env python3
"""Run the self-contained /om-plan preparation and validation commands."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import uuid

if sys.version_info < (3, 11):
    print(
        "om_workflow.py requires Python 3.11 or newer; "
        f"current interpreter is {sys.version_info.major}.{sys.version_info.minor}",
        file=sys.stderr,
    )
    raise SystemExit(2)

from datetime import UTC, datetime
from pathlib import Path

from acgh.integrations.om import OpenMetadataPlanAdapter
from acgh.plancore.errors import PlanControlError
from acgh.plancore.markers import create_session_marker, session_marker_path
from acgh.plancore.markers import (
    load_session_marker,
    pair_from_run,
    project_key,
    record_trusted_input_lock_digest,
    trusted_input_lock_digest,
)
from acgh.plancore.preflight import run_preflight
from acgh.plancore.resume import resume_proposal_run
from acgh.plancore.schema import read_data, validate as validate_schema
from acgh.plancore.validate import run_validation
from acgh.verdict import to_exit_code


HARNESS = Path(__file__).resolve().parent
PROJECT = HARNESS.parent


class WorkflowInputError(RuntimeError):
    """The requested workflow cannot start with the supplied inputs."""


def plan_timestamp() -> str:
    """Return a UTC timestamp precise enough for local run allocation."""
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")


def _new_plan_session_id() -> str:
    return f"local-{uuid.uuid4().hex}"


def default_plan_state_root(project_root: str | Path) -> Path:
    """Keep local plan state in Git metadata so it never dirties the checker."""
    configured = os.environ.get("OM_PLAN_HOOK_STATE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    project = Path(project_root).resolve()
    completed = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--git-path", "om-plan-state"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise WorkflowInputError(
            "기본 plan state 경로를 찾지 못했습니다. "
            "Git 저장소에서 실행하거나 --state-root를 지정하세요."
        )
    candidate = Path(completed.stdout.strip())
    if not candidate.is_absolute():
        candidate = project / candidate
    return candidate.resolve()


def default_plan_evidence_root(project_root: str | Path) -> Path:
    """Keep generated runs in Git metadata so repeated starts stay clean."""
    project = Path(project_root).resolve()
    completed = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "--git-path", "om-plan-evidence"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        raise WorkflowInputError(
            "기본 plan evidence 경로를 찾지 못했습니다. "
            "Git 저장소에서 실행하거나 --evidence-root를 지정하세요."
        )
    candidate = Path(completed.stdout.strip())
    if not candidate.is_absolute():
        candidate = project / candidate
    return candidate.resolve()


def allocate_plan_run_dir(
    evidence_root: str | Path,
    mode: str,
    *,
    timestamp_value: str | None = None,
) -> Path:
    """Select a new path without ever reusing an existing run directory."""
    stamp = timestamp_value or plan_timestamp()
    base = Path(evidence_root).resolve() / f"om-plan-{mode}-{stamp}"
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = base.with_name(f"{base.name}-{suffix:02d}")
        suffix += 1
    return candidate


def _create_or_reuse_session_marker(
    state_root: str | Path,
    project_root: str | Path,
    session_id: str | None,
) -> tuple[str, Path]:
    if session_id:
        marker = session_marker_path(state_root, project_root, session_id)
        if marker.exists():
            session = load_session_marker(marker)
            if session.get("run_dir") is not None:
                raise PlanControlError(
                    "SESSION_ALREADY_BOUND",
                    "the requested session is already bound to a plan run",
                    details={"run_dir": session.get("run_dir")},
                )
            return session_id, marker
        return session_id, create_session_marker(
            state_root,
            project_root,
            session_id,
        )

    for _ in range(32):
        generated = _new_plan_session_id()
        try:
            marker = create_session_marker(state_root, project_root, generated)
        except PlanControlError as exc:
            if exc.code == "SESSION_ALREADY_ACTIVE":
                continue
            raise
        return generated, marker
    raise PlanControlError(
        "SESSION_ID_ALLOCATION_FAILED",
        "could not allocate a unique automatic session id",
    )


def select_plan_session_id(
    explicit_session_id: str | None,
) -> str | None:
    """Prefer an explicit identity, then one supplied by a trusted adapter."""
    if explicit_session_id:
        return explicit_session_id
    return os.environ.get("OM_PLAN_SESSION_ID") or None


def incomplete_plan_runs(
    state_root: str | Path,
    project_root: str | Path,
) -> list[dict[str, str]]:
    """Return marker-verified active runs for the requested checker project."""
    directory = Path(state_root).resolve() / project_key(project_root)
    if not directory.is_dir():
        return []
    active: list[dict[str, str]] = []
    for marker in sorted(directory.glob("*.active")):
        session = load_session_marker(marker)
        run_dir = session.get("run_dir")
        if run_dir is None:
            continue
        pair = pair_from_run(run_dir)
        if pair.session_marker != marker.resolve():
            raise PlanControlError(
                "MARKER_OWNERSHIP_MISMATCH",
                "run marker points to a different session marker",
                details={"marker": str(marker), "run_dir": str(run_dir)},
            )
        active.append(
            {
                "run_dir": str(Path(run_dir).resolve()),
                "session_id": pair.session_id,
            }
        )
    return active


def select_incomplete_plan_run(
    state_root: str | Path,
    project_root: str | Path,
) -> Path:
    active = incomplete_plan_runs(state_root, project_root)
    if not active:
        raise PlanControlError(
            "PLAN_RUN_NOT_FOUND",
            "no incomplete plan run was found",
            details={"state_root": str(Path(state_root).resolve())},
        )
    if len(active) != 1:
        raise PlanControlError(
            "PLAN_RUN_AMBIGUOUS",
            "multiple incomplete plan runs require an explicit run directory",
            details={"runs": active},
        )
    return Path(active[0]["run_dir"])


def start_plan_run(args: argparse.Namespace) -> dict:
    request = read_data(args.request)
    validate_schema("run-request", request)
    project_root = Path(args.project_root).resolve()
    state_root = (
        Path(args.state_root).resolve()
        if args.state_root is not None
        else default_plan_state_root(project_root)
    )
    if args.run_dir is not None:
        run_dir = Path(args.run_dir).resolve()
    else:
        evidence_root = (
            Path(args.evidence_root).resolve()
            if args.evidence_root is not None
            else default_plan_evidence_root(project_root)
        )
        run_dir = allocate_plan_run_dir(evidence_root, request["mode"])
    session_id_hint = select_plan_session_id(
        args.session_id,
    )
    session_id, marker = _create_or_reuse_session_marker(
        state_root,
        project_root,
        session_id_hint,
    )
    result = run_preflight(
        args.request,
        run_dir,
        OpenMetadataPlanAdapter(),
        session_marker=marker,
    )
    record_trusted_input_lock_digest(marker, result["input_lock_digest"])
    command = " ".join(
        shlex.quote(value)
        for value in (
            sys.executable,
            str(Path(__file__).resolve()),
            "plan",
            "check",
            str(run_dir),
        )
    )
    return {
        **result,
        "run_dir": str(run_dir),
        "state_root": str(state_root),
        "session_id": session_id,
        "next_command": command,
    }


def check_plan_run(args: argparse.Namespace) -> dict:
    project_root = Path(args.project_root).resolve()
    if args.run_dir is not None:
        run_dir = Path(args.run_dir).resolve()
    else:
        state_root = (
            Path(args.state_root).resolve()
            if args.state_root is not None
            else default_plan_state_root(project_root)
        )
        run_dir = select_incomplete_plan_run(state_root, project_root)
    pair = pair_from_run(run_dir)
    supplied_digest = args.expected_input_lock_digest
    try:
        recorded_digest = trusted_input_lock_digest(pair.session_marker)
    except PlanControlError as exc:
        if exc.code != "TRUSTED_INPUT_LOCK_DIGEST_MISSING" or supplied_digest is None:
            raise
        recorded_digest = supplied_digest
    if supplied_digest is not None:
        if supplied_digest != recorded_digest:
            raise PlanControlError(
                "TRUSTED_INPUT_LOCK_DIGEST_MISMATCH",
                "the supplied digest differs from the digest retained at plan start",
                details={"recorded": recorded_digest, "supplied": supplied_digest},
            )
    return run_validation(
        run_dir,
        OpenMetadataPlanAdapter(),
        expected_input_lock_digest=supplied_digest or recorded_digest,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "/om-plan 요청의 입력 고정·사실 수집·제안 검증·제안 재검증을 "
            "실행합니다."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="새 계획을 시작하거나 현재 계획을 검증")
    plan_actions = plan.add_subparsers(dest="plan_action", required=True)
    plan_start = plan_actions.add_parser(
        "start",
        help="요청 파일로 새 /om-plan run 시작",
    )
    plan_start.add_argument("request", type=Path)
    run_location = plan_start.add_mutually_exclusive_group()
    run_location.add_argument("--run-dir", type=Path)
    run_location.add_argument("--evidence-root", type=Path)
    plan_start.add_argument("--state-root", type=Path)
    plan_start.add_argument("--session-id")
    plan_start.add_argument("--project-root", type=Path, default=PROJECT)

    plan_check = plan_actions.add_parser(
        "check",
        help="현재 또는 지정한 /om-plan run 검증",
    )
    plan_check.add_argument("run_dir", nargs="?", type=Path)
    plan_check.add_argument("--state-root", type=Path)
    plan_check.add_argument("--project-root", type=Path, default=PROJECT)
    plan_check.add_argument("--expected-input-lock-digest")

    plan_session = subparsers.add_parser(
        "plan-session-start",
        help="Hook에서 /om-plan 세션 보호 marker 생성",
    )
    plan_session.add_argument("--state-root", required=True, type=Path)
    plan_session.add_argument("--session-id", required=True)
    plan_session.add_argument("--project-root", type=Path, default=PROJECT)

    plan_preflight = subparsers.add_parser(
        "plan-preflight",
        help="/om-plan 입력 고정과 기계 사실 수집",
    )
    plan_preflight.add_argument("--request", required=True, type=Path)
    plan_preflight.add_argument("--run-dir", required=True, type=Path)
    plan_preflight.add_argument("--state-root", required=True, type=Path)
    plan_preflight.add_argument("--session-id", required=True)
    plan_preflight.add_argument("--project-root", type=Path, default=PROJECT)

    plan_validate = subparsers.add_parser(
        "plan-validate",
        help="/om-plan 사실 재계산과 proposal 검증",
    )
    plan_validate.add_argument("--run-dir", required=True, type=Path)
    plan_validate.add_argument(
        "--expected-input-lock-digest",
        help=(
            "사람 또는 보호된 CI가 preflight 직후 보관한 input-lock digest; "
            "누락·형식 오류·불일치는 analysis_error"
        ),
    )

    plan_resume = subparsers.add_parser(
        "plan-resume",
        help="proposal 검증 block run을 사실 변경 없이 다시 연결",
    )
    plan_resume.add_argument("--run-dir", required=True, type=Path)
    plan_resume.add_argument("--state-root", required=True, type=Path)
    plan_resume.add_argument("--session-id", required=True)
    plan_resume.add_argument("--project-root", type=Path, default=PROJECT)

    return parser.parse_args()


def dispatch(args: argparse.Namespace) -> int:
    if args.command == "plan" and args.plan_action == "start":
        result = start_plan_run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "plan" and args.plan_action == "check":
        result = check_plan_run(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return to_exit_code(result["verdict"])

    if args.command == "plan-session-start":
        marker = create_session_marker(
            args.state_root,
            args.project_root,
            args.session_id,
        )
        print(
            json.dumps(
                {"status": "protected", "session_marker": str(marker)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "plan-preflight":
        marker = session_marker_path(
            args.state_root,
            args.project_root,
            args.session_id,
        )
        result = run_preflight(
            args.request,
            args.run_dir,
            OpenMetadataPlanAdapter(),
            session_marker=marker,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "plan-validate":
        result = run_validation(
            args.run_dir,
            OpenMetadataPlanAdapter(),
            expected_input_lock_digest=args.expected_input_lock_digest,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return to_exit_code(result["verdict"])

    if args.command == "plan-resume":
        marker = session_marker_path(
            args.state_root,
            args.project_root,
            args.session_id,
        )

        def verify_documents(run_dir: Path) -> None:
            source = run_dir / "official-doc-sources.yaml"
            if source.is_file():
                OpenMetadataPlanAdapter().verify_documents(run_dir, read_data(source))

        result = resume_proposal_run(
            args.run_dir,
            marker,
            verify_external_inputs=verify_documents,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    raise WorkflowInputError(f"지원하지 않는 작업입니다: {args.command}")


def main() -> int:
    try:
        return dispatch(parse_args())
    except WorkflowInputError as exc:
        print(f"입력 확인 필요\n{exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"Git 명령을 실행하지 못했습니다: {exc}", file=sys.stderr)
        return 2
    except PlanControlError as exc:
        print(
            json.dumps(
                {"status": "analysis_error", **exc.as_dict()},
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
