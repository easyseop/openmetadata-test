#!/usr/bin/env python3
"""Run OM_TEMP preparation and checks with version-based path discovery.

Operators provide the product-code repository and product version.  This
front-end resolves the registration directory and its policy files, then calls
the existing implementation commands with the full argument list.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml

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
REGISTRATIONS = HARNESS / "registrations"


class WorkflowInputError(RuntimeError):
    """The requested workflow cannot start with the supplied inputs."""


def timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


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


def registration_for(version: str) -> Path:
    registration = REGISTRATIONS / f"om-temp-{version}"
    if not registration.is_dir():
        raise WorkflowInputError(
            f"등록 폴더가 없습니다: {registration}\n"
            f"--version 값과 harness/registrations/om-temp-<버전> 폴더를 확인하세요."
        )
    return registration


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise WorkflowInputError(f"{label} 파일이 없습니다: {path}")
    return path


def registry_source(registration: Path) -> dict:
    path = require_file(
        registration / "customization-registry.yaml",
        "Registry",
    )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    source = data.get("source")
    if not isinstance(source, dict):
        raise WorkflowInputError(f"Registry source 항목이 없습니다: {path}")
    return source


def common_paths(version: str) -> dict[str, Path]:
    registration = registration_for(version)
    return {
        "registration": registration,
        "layout": require_file(
            registration / "repository-layout.yaml",
            "코드 경로 분류표",
        ),
        "zones": require_file(
            registration / "sensitive-zones.yaml",
            "중요 경로 정책",
        ),
    }


def registration_validator(registration: Path) -> Path:
    """Return the version-local validator or the shared generic validator."""
    local = registration / "validate_registration_bundle.py"
    if local.is_file():
        return local
    return require_file(
        REGISTRATIONS / "om-temp-1.13.0" / "validate_registration_bundle.py",
        "공용 등록자료 검사기",
    )


def python_command(script: Path, *arguments: object) -> list[str]:
    return [sys.executable, str(script), *(str(value) for value in arguments)]


def print_selection(paths: dict[str, object]) -> None:
    print("자동으로 선택한 입력")
    for label, value in paths.items():
        print(f"- {label}: {value}")
    sys.stdout.flush()


def run(command: list[str]) -> int:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(HARNESS)
    completed = subprocess.run(command, cwd=PROJECT, env=environment, check=False)
    return completed.returncode


def run_to_file(command: list[str], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(HARNESS)
    completed = subprocess.run(
        command,
        cwd=PROJECT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.stdout:
        output.write_text(completed.stdout, encoding="utf-8")
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    return completed.returncode


def add_repo_version(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--version", required=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "제품 코드 저장소 경로와 버전만 입력하면 등록 폴더와 정책 파일을 "
            "자동으로 찾아 준비·검사 명령을 실행합니다."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="계획 실행 또는 기존 등록 변경안 생성")
    plan_actions = plan.add_subparsers(dest="plan_action")
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

    plan.add_argument("--repo", type=Path)
    plan.add_argument("--version")
    plan.add_argument("--fork-ref")
    plan.add_argument("--custom-ref")
    plan.add_argument("--new-id-input", type=Path)
    plan.add_argument("--output", type=Path)

    template = subparsers.add_parser(
        "approval-template",
        help="plan 결과에서 빈 승인 양식 생성",
    )
    template.add_argument("--proposal", required=True, type=Path)
    template.add_argument("--output", type=Path)

    apply = subparsers.add_parser("apply", help="승인된 등록 변경안 반영")
    add_repo_version(apply)
    apply.add_argument("--proposal", required=True, type=Path)
    apply.add_argument("--approval", required=True, type=Path)
    apply.add_argument("--result", type=Path)

    bootstrap = subparsers.add_parser(
        "bootstrap",
        help="과거 버전 전용 초기 등록 묶음 재생성(호환용 특수 작업)",
    )
    add_repo_version(bootstrap)
    bootstrap.add_argument(
        "--confirm-replace-registration",
        action="store_true",
        help="기존 등록 파일을 다시 만들겠다는 명시적 확인",
    )

    bootstrap_input = subparsers.add_parser(
        "bootstrap-input-template",
        help="BANK-OM commit 이력에서 최초 등록 업무 입력 양식 생성",
    )
    add_repo_version(bootstrap_input)
    bootstrap_input.add_argument("--official-ref", required=True)
    bootstrap_input.add_argument("--custom-ref", required=True)
    bootstrap_input.add_argument("--repository", required=True)
    bootstrap_input.add_argument("--upstream-repository", required=True)
    bootstrap_input.add_argument("--upstream-tag", required=True)
    bootstrap_input.add_argument("--output", required=True, type=Path)

    bootstrap_plan = subparsers.add_parser(
        "bootstrap-plan",
        help="버전과 무관한 최초 등록 제안 생성",
    )
    add_repo_version(bootstrap_plan)
    bootstrap_plan.add_argument("--official-ref", required=True)
    bootstrap_plan.add_argument("--custom-ref", required=True)
    bootstrap_plan.add_argument("--input", required=True, type=Path)
    bootstrap_plan.add_argument("--output", required=True, type=Path)

    bootstrap_template = subparsers.add_parser(
        "bootstrap-approval-template",
        help="최초 등록 제안의 승인 양식 생성",
    )
    bootstrap_template.add_argument("--proposal", required=True, type=Path)
    bootstrap_template.add_argument("--output", required=True, type=Path)

    bootstrap_apply = subparsers.add_parser(
        "bootstrap-apply",
        help="승인한 최초 등록 제안을 활성 등록 폴더에 반영",
    )
    add_repo_version(bootstrap_apply)
    bootstrap_apply.add_argument("--proposal", required=True, type=Path)
    bootstrap_apply.add_argument("--approval", required=True, type=Path)
    bootstrap_apply.add_argument("--result", required=True, type=Path)

    validate = subparsers.add_parser("validate", help="등록자료 5종 검사")
    add_repo_version(validate)
    validate.add_argument("--output", type=Path)

    source = subparsers.add_parser("source", help="T25·T26 등 소스 검사 실행")
    add_repo_version(source)
    source.add_argument("--output", type=Path)

    watch = subparsers.add_parser(
        "watch",
        help="새 공식 버전이 watch 경로를 바꿨는지 병합 전에 검사",
    )
    add_repo_version(watch)
    watch.add_argument("--target", required=True, help="새 공식 버전 commit 또는 tag")
    watch.add_argument("--base", help="생략하면 Registry source.upstream_sha 사용")
    watch.add_argument("--output", type=Path)

    risk = subparsers.add_parser("risk", help="업그레이드 위험 검사")
    add_repo_version(risk)
    risk.add_argument("--target", required=True, help="새 공식 버전 commit 또는 tag")
    risk.add_argument("--base", help="생략하면 Registry source.upstream_sha 사용")
    risk.add_argument("--candidate", help="생략하면 제품 코드 저장소 HEAD 사용")
    risk.add_argument("--conflict-rate", required=True, type=float)
    risk.add_argument("--output", type=Path)

    runtime = subparsers.add_parser("runtime", help="Contract test 실행 자료 생성")
    add_repo_version(runtime)
    artifact = runtime.add_mutually_exclusive_group(required=True)
    artifact.add_argument("--artifact", type=Path, help="digest를 계산할 배포 파일")
    artifact.add_argument("--artifact-digest")
    runtime.add_argument("--output-dir", type=Path)
    runtime.add_argument("--run-id")

    patch_kill = subparsers.add_parser(
        "patch-kill",
        help="BANK-OM 제거 후 필수 test 실패 확인",
    )
    add_repo_version(patch_kill)
    patch_kill.add_argument("--output", type=Path)
    patch_kill.add_argument("--run-id")

    typecheck = subparsers.add_parser(
        "typecheck",
        help="공식 코드와 커스텀 코드의 UI typecheck 결과 비교",
    )
    typecheck.add_argument("--upstream-log", required=True, type=Path)
    typecheck.add_argument("--candidate-log", required=True, type=Path)
    typecheck.add_argument("--upstream-exit", required=True, type=int)
    typecheck.add_argument("--candidate-exit", required=True, type=int)
    typecheck.add_argument("--output", type=Path)

    resolve_json = subparsers.add_parser(
        "resolve-json",
        help="겹치지 않는 JSON 충돌만 자동 병합",
    )
    resolve_json.add_argument("--repo", required=True, type=Path)

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


def plan_command(args: argparse.Namespace) -> tuple[list[str], dict[str, object]]:
    if args.repo is None or not args.version:
        raise WorkflowInputError(
            "기존 등록 변경안 생성에는 --repo와 --version이 필요합니다. "
            "새 /om-plan 실행은 'plan start <요청.yaml>'을 사용하세요."
        )
    paths = common_paths(args.version)
    output = args.output or (
        HARNESS
        / "preparation-plans"
        / f"om-temp-{args.version}-{timestamp()}"
    )
    fork_ref = args.fork_ref or f"origin/fork/om-{args.version}"
    custom_ref = args.custom_ref or f"origin/custom/om-{args.version}"
    command = python_command(
        HARNESS / "prepare_registration.py",
        "plan",
        "--repo",
        args.repo,
        "--registration",
        paths["registration"],
        "--patch-ref",
        fork_ref,
        "--custom-ref",
        custom_ref,
        "--product-version",
        args.version,
        "--output",
        output,
    )
    if args.new_id_input:
        command.extend(["--new-id-input", str(args.new_id_input)])
    return command, {
        "등록 폴더": paths["registration"],
        "OpenMetadata 포크 브랜치": fork_ref,
        "커스텀 브랜치": custom_ref,
        "결과 폴더": output,
    }


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
        print(json.dumps({"status": "protected", "session_marker": str(marker)}, ensure_ascii=False, indent=2))
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

    if args.command == "plan":
        command, selected = plan_command(args)
        print_selection(selected)
        return run(command)

    if args.command == "approval-template":
        output = args.output or args.proposal.parent / "registration-approval.yaml"
        print_selection({"제안 파일": args.proposal, "빈 승인 양식": output})
        return run(
            python_command(
                HARNESS / "prepare_registration.py",
                "approval-template",
                "--proposal",
                args.proposal,
                "--output",
                output,
            )
        )

    if args.command == "apply":
        paths = common_paths(args.version)
        result = args.result or args.approval.parent / "registration-apply-result.json"
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "승인한 제안": args.proposal,
                "승인서": args.approval,
                "적용 결과": result,
            }
        )
        return run(
            python_command(
                HARNESS / "prepare_registration.py",
                "apply",
                "--repo",
                args.repo,
                "--registration",
                paths["registration"],
                "--proposal",
                args.proposal,
                "--approval",
                args.approval,
                "--result",
                result,
            )
        )

    if args.command == "bootstrap":
        paths = common_paths(args.version)
        if not args.confirm_replace_registration:
            raise WorkflowInputError(
                "bootstrap은 기존 등록 파일을 다시 만드는 특수 작업입니다.\n"
                "일반 후속 commit에는 plan을 사용하세요. 정말 다시 만들려면 "
                "--confirm-replace-registration을 추가하세요."
            )
        generator = require_file(
            paths["registration"] / "generate_registration_bundle.py",
            "초기 등록 묶음 생성기",
        )
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "초기 등록 생성기": generator,
                "주의": "기존 등록 파일을 다시 생성",
            }
        )
        return run(
            python_command(
                generator,
                "--repo",
                args.repo,
                "--output-dir",
                paths["registration"],
            )
        )

    if args.command == "bootstrap-input-template":
        print_selection(
            {
                "공식 OpenMetadata 브랜치": args.official_ref,
                "커스터마이징 브랜치": args.custom_ref,
                "최초 등록 업무 입력 양식": args.output,
            }
        )
        return run(
            python_command(
                HARNESS / "bootstrap_registration.py",
                "input-template",
                "--repo",
                args.repo,
                "--official-ref",
                args.official_ref,
                "--custom-ref",
                args.custom_ref,
                "--repository",
                args.repository,
                "--upstream-repository",
                args.upstream_repository,
                "--upstream-tag",
                args.upstream_tag,
                "--output",
                args.output,
            )
        )

    if args.command == "bootstrap-plan":
        paths = common_paths(args.version)
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "공식 OpenMetadata 브랜치": args.official_ref,
                "커스터마이징 브랜치": args.custom_ref,
                "사람이 작성한 업무 입력": args.input,
                "최초 등록 제안": args.output,
            }
        )
        return run(
            python_command(
                HARNESS / "bootstrap_registration.py",
                "plan",
                "--repo",
                args.repo,
                "--registration",
                paths["registration"],
                "--official-ref",
                args.official_ref,
                "--custom-ref",
                args.custom_ref,
                "--product-version",
                args.version,
                "--input",
                args.input,
                "--output",
                args.output,
            )
        )

    if args.command == "bootstrap-approval-template":
        print_selection({"최초 등록 제안": args.proposal, "승인 양식": args.output})
        return run(
            python_command(
                HARNESS / "bootstrap_registration.py",
                "approval-template",
                "--proposal",
                args.proposal,
                "--output",
                args.output,
            )
        )

    if args.command == "bootstrap-apply":
        paths = common_paths(args.version)
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "승인한 최초 등록 제안": args.proposal,
                "승인서": args.approval,
                "반영 결과": args.result,
            }
        )
        return run(
            python_command(
                HARNESS / "bootstrap_registration.py",
                "apply",
                "--repo",
                args.repo,
                "--registration",
                paths["registration"],
                "--proposal",
                args.proposal,
                "--approval",
                args.approval,
                "--result",
                args.result,
            )
        )

    if args.command == "validate":
        paths = common_paths(args.version)
        output = args.output or paths["registration"] / "registration-validation-results.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        # The validator is registration-directory agnostic. Older
        # registrations keep the executable copy under om-temp-1.13.0; pass
        # the selected registration and layout explicitly below.
        validator = registration_validator(paths["registration"])
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "코드 경로 분류표": paths["layout"],
                "등록자료 검사기": validator,
                "결과 파일": output,
            }
        )
        return run(
            python_command(
                validator,
                "--repo",
                args.repo,
                "--registration",
                paths["registration"],
                "--layout",
                paths["layout"],
                "--output",
                output,
            )
        )

    if args.command == "source":
        paths = common_paths(args.version)
        output = args.output or paths["registration"] / "source-gate-results.json"
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "코드 경로 분류표": paths["layout"],
                "중요 경로 정책": paths["zones"],
                "결과 파일": output,
            }
        )
        return run(
            python_command(
                HARNESS / "run_source_candidate_gates.py",
                "--repo",
                args.repo,
                "--harness",
                HARNESS,
                "--registration",
                paths["registration"],
                "--layout",
                paths["layout"],
                "--sensitive-zones",
                paths["zones"],
                "--output",
                output,
            )
        )

    if args.command == "watch":
        paths = common_paths(args.version)
        base = args.base or registry_source(paths["registration"]).get("upstream_sha")
        if not base:
            raise WorkflowInputError(
                "Registry source.upstream_sha가 없어 --base를 직접 입력해야 합니다."
            )
        output = args.output or paths["registration"] / "upgrade-watch-results.json"
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "비교 전 공식 commit": base,
                "비교할 새 공식 commit": args.target,
                "결과 파일": output,
            }
        )
        return run(
            python_command(
                HARNESS / "run_upgrade_watch.py",
                "--repo",
                args.repo,
                "--harness",
                HARNESS,
                "--registration",
                paths["registration"],
                "--upstream-base",
                base,
                "--upstream-target",
                args.target,
                "--output",
                output,
            )
        )

    if args.command == "risk":
        paths = common_paths(args.version)
        source = registry_source(paths["registration"])
        base = args.base or source.get("upstream_sha")
        if not base:
            raise WorkflowInputError(
                "Registry source.upstream_sha가 없어 --base를 직접 입력해야 합니다."
            )
        candidate = args.candidate
        if not candidate:
            candidate = subprocess.run(
                ["git", "-C", str(args.repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        change_intent = require_file(
            paths["registration"] / "change-intent.yaml",
            "변경 의도",
        )
        debt_policy = require_file(
            HARNESS / "policies" / "debt-thresholds.yaml",
            "유지 부담 정책",
        )
        output = args.output or paths["registration"] / "upgrade-risk-results.json"
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "코드 경로 분류표": paths["layout"],
                "중요 경로 정책": paths["zones"],
                "유지 부담 정책": debt_policy,
                "변경 의도": change_intent,
                "검사할 커스텀 commit": candidate,
                "결과 파일": output,
            }
        )
        command = python_command(
            HARNESS / "run_upgrade_risk_gates.py",
            "--repo",
            args.repo,
            "--harness",
            HARNESS,
            "--registration",
            paths["registration"],
            "--layout",
            paths["layout"],
            "--sensitive-zones",
            paths["zones"],
            "--debt-policy",
            debt_policy,
            "--change-intent",
            change_intent,
            "--upstream-base",
            base,
            "--upstream-target",
            args.target,
            "--candidate",
            candidate,
            "--conflict-rate",
            args.conflict_rate,
        )
        return run_to_file(command, output)

    if args.command == "runtime":
        paths = common_paths(args.version)
        run_id = args.run_id or f"runtime-contract-{timestamp()}"
        output_dir = args.output_dir or PROJECT / "evidence" / run_id
        if args.artifact:
            require_file(args.artifact, "배포 파일")
            digest = "sha256:" + hashlib.sha256(args.artifact.read_bytes()).hexdigest()
        else:
            digest = args.artifact_digest
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "배포 파일 확인값": digest,
                "실행 ID": run_id,
                "증거 폴더": output_dir,
            }
        )
        return run(
            python_command(
                HARNESS / "run_runtime_contracts.py",
                "--repo",
                args.repo,
                "--harness",
                HARNESS,
                "--registration",
                paths["registration"],
                "--artifact-digest",
                digest,
                "--output-dir",
                output_dir,
                "--run-id",
                run_id,
            )
        )

    if args.command == "patch-kill":
        paths = common_paths(args.version)
        plan = require_file(
            paths["registration"] / "patch-kill-plan.yaml",
            "BANK-OM 제거 test 계획",
        )
        run_id = args.run_id or f"source-patch-kill-{timestamp()}"
        output = args.output or PROJECT / "evidence" / run_id / "result.yaml"
        print_selection(
            {
                "등록 폴더": paths["registration"],
                "제거 test 계획": plan,
                "실행 ID": run_id,
                "결과 파일": output,
            }
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        return run(
            python_command(
                HARNESS / "run_source_patch_kills.py",
                "--repo",
                args.repo,
                "--harness",
                HARNESS,
                "--registration",
                paths["registration"],
                "--output",
                output,
                "--run-id",
                run_id,
            )
        )

    if args.command == "typecheck":
        require_file(args.upstream_log, "공식 코드 typecheck 로그")
        require_file(args.candidate_log, "커스텀 코드 typecheck 로그")
        output = args.output or PROJECT / "evidence" / "typecheck-comparison.json"
        print_selection(
            {
                "공식 코드 로그": args.upstream_log,
                "커스텀 코드 로그": args.candidate_log,
                "결과 파일": output,
            }
        )
        return run_to_file(
            python_command(
                HARNESS / "compare_ui_typecheck.py",
                "--harness",
                HARNESS,
                "--upstream-log",
                args.upstream_log,
                "--candidate-log",
                args.candidate_log,
                "--upstream-exit",
                args.upstream_exit,
                "--candidate-exit",
                args.candidate_exit,
            ),
            output,
        )

    if args.command == "resolve-json":
        print_selection({"충돌이 발생한 제품 코드 저장소": args.repo})
        return run(
            python_command(
                HARNESS / "tools" / "resolve_nonoverlapping_json_conflicts.py",
                "--repo",
                args.repo,
            )
        )

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
