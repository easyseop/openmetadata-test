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
import subprocess
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

import yaml

from acgh import phase as phase_bundle


HARNESS = Path(__file__).resolve().parent
PROJECT = HARNESS.parent
REGISTRATIONS = HARNESS / "registrations"


class WorkflowInputError(RuntimeError):
    """The requested workflow cannot start with the supplied inputs."""


def timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S-%fZ")


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


_PHASE_LABELS = {
    "candidate": (1, "활성 Candidate 확인"),
    "official": (2, "공식 버전 준비"),
    "preflight": (3, "Phase 실행 전 점검"),
    "premerge": (4, "병합 전 영향 검사"),
    "postmerge": (5, "병합 후 Candidate 검사"),
    "status": (6, "Phase 결과 재검증"),
}


def _last_json(stdout: str) -> dict | None:
    for line in reversed(stdout.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _result_label(payload: dict) -> str:
    if payload.get("status") == "analysis_error" or payload.get("verified") is False:
        return "중단 · 분석 오류"
    if "ready" in payload:
        if not payload.get("ready"):
            return "중단 · 입력 보완 필요"
        if payload.get("disabled_gates"):
            return "조건부 준비 · 일부 검사 미실행"
        return "실행 가능"
    verdict_value = payload.get("overall_verdict")
    return {
        "pass": "계속 가능 (PASS)",
        "approval": "담당자 검토 필요 (APPROVAL)",
        "block": "중단 (BLOCK)",
        "analysis_error": "중단 · 분석 오류",
    }.get(verdict_value, {
        "selected": "계속 가능",
        "created": "준비 완료",
        "already_correct": "이미 정확히 준비됨",
        "blocked": "중단 · 승인 또는 lock 확인 필요",
    }.get(payload.get("status"), "확인 필요"))


def _verdict_label(value: str | None) -> str:
    return {
        "pass": "pass (계속 가능)",
        "approval": "approval (담당자 검토 필요)",
        "block": "block (중단)",
        "analysis_error": "analysis_error (분석 오류)",
    }.get(value, value or "-")


def _display_width(value: str) -> int:
    """Approximate terminal columns without padding fields into a table."""
    return sum(
        0 if unicodedata.combining(char)
        else 2 if unicodedata.east_asian_width(char) in {"W", "F"}
        else 1
        for char in value
    )


def _wrap_display(value: str, first_width: int, continuation_width: int) -> list[str]:
    """Wrap at spaces by terminal columns; leave copyable long tokens intact."""
    lines: list[str] = []
    limit = first_width
    for paragraph in value.splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            limit = continuation_width
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if _display_width(candidate) <= limit:
                current = candidate
            else:
                lines.append(current)
                current = word
                limit = continuation_width
        lines.append(current)
        limit = continuation_width
    return lines or [""]


def _emit(label: str, value: object, *, width: int = 80) -> None:
    prefix = f"{label}: "
    lines = _wrap_display(
        str(value),
        max(20, width - _display_width(prefix)),
        max(20, width - 2),
    )
    print(prefix + lines[0])
    for line in lines[1:]:
        print("  " + line)


def _print_premerge_next_steps() -> None:
    print("다음 행동:")
    print("  1. 담당자가 premerge 결과를 승인합니다.")
    print("  2. 별도 제품 branch에서 vendor-merge Candidate를 만듭니다.")
    print("  3. 새 Candidate lock을 작성하고 담당자가 승인합니다.")
    print("  4. candidate-select를 다시 실행합니다.")
    print("  5. postmerge-check를 실행합니다.")


def _print_human_phase(stage: str, payload: dict, *, evidence: Path | None = None) -> None:
    number, title = _PHASE_LABELS[stage]
    print(f"\n[{number}/6] {title}")
    if stage == "status":
        _emit("저장된 판정", _verdict_label(payload.get("overall_verdict")))
        _emit(
            "재검증 결과",
            "canonical·관리자·실무자 결과 일치"
            if payload.get("verified")
            else "불일치 또는 읽기 오류",
        )
    else:
        _emit("결과", _result_label(payload))
    if payload.get("process_exit_code") is not None:
        _emit("종료 코드", payload["process_exit_code"])
    if payload.get("reason"):
        _emit("사유", payload["reason"])
    for reason in payload.get("reasons", []):
        _emit("사유", reason)

    if stage == "candidate":
        _emit("등록 묶음", payload.get("registration_bundle") or "-")
        _emit("Candidate", payload.get("candidate_commit_sha") or "-")
        _emit("산출물 종류", payload.get("candidate_artifact_kind") or "-")
        _emit("Lock digest", payload.get("candidate_lock_digest") or "-")
        if payload.get("status") == "selected":
            _emit("다음 행동", "공식 새 버전을 prep-official로 고정하세요.")
        else:
            _emit("다음 행동", "승인된 Candidate lock과 active-candidate.yaml을 준비한 뒤 다시 실행하세요.")
    elif stage == "official":
        _emit("공식 tag", payload.get("tag_ref") or "-")
        _emit("공식 commit", payload.get("commit_sha") or "-")
        _emit("로컬 branch", payload.get("branch") or "-")
        if payload.get("status") == "analysis_error":
            _emit("다음 행동", "공식 tag·branch·commit 결속 오류를 해결한 뒤 다시 실행하세요.")
        else:
            _emit("다음 행동", "생성된 증거 파일을 premerge-check에 전달하세요.")
    elif stage == "preflight":
        problems = payload.get("blocking_problems", [])
        disabled = payload.get("disabled_gates", [])
        _emit("차단 항목", f"{len(problems)}개")
        _emit("미실행 검사", ", ".join(disabled) if disabled else "없음")
        for check in payload.get("checks", []):
            if check.get("status") == "ok":
                continue
            name = check.get("name") or "이름 없는 점검"
            status = check.get("status") or "확인 필요"
            detail = check.get("next_action") or check.get("detail")
            print(f"- {name}: {status}")
            if detail:
                _emit("  조치", detail)
        if problems:
            _emit("다음 행동", "차단 항목을 해결한 뒤 같은 Phase를 다시 실행하세요.")
        elif disabled:
            _emit("다음 행동", "누락된 사람 입력·증거를 채우면 모든 검사를 실행할 수 있습니다.")
        else:
            _emit("다음 행동", "해당 Phase 검사를 실행하세요.")
    elif stage in {"premerge", "postmerge"}:
        _emit("완료 상태", payload.get("phase_status") or "-")
        _emit("검사 범위", payload.get("verification_scope") or "-")
        _emit("검사 완료", payload.get("checked_over_total") or "-")
        counts = payload.get("counts", {})
        if counts:
            _emit(
                "판정 요약",
                f"PASS {counts.get('pass', 0)} · "
                f"APPROVAL {counts.get('approval', 0)} · "
                f"BLOCK {counts.get('block', 0)} · "
                f"ANALYSIS_ERROR {counts.get('analysis_error', 0)}"
            )
        non_pass = payload.get("non_pass_gates", [])
        if non_pass:
            summary = ", ".join(
                f"{gate.get('name')}({gate.get('verdict')})" for gate in non_pass
            )
            _emit("확인할 검사", summary)
        _emit("결과 digest", payload.get("result_digest") or "-")
        manager_path = payload.get("manager_output")
        practitioner_path = payload.get("practitioner_output")
        if manager_path:
            _emit("관리자 요약", manager_path)
        if practitioner_path:
            _emit("실무자 상세", practitioner_path)
        if stage == "premerge" and payload.get("overall_verdict") in {"pass", "approval"}:
            _print_premerge_next_steps()
        elif payload.get("overall_verdict") == "approval":
            _emit("다음 행동", "실무자 상세의 검토 항목을 확인하고 담당자가 승인하세요.")
        elif payload.get("overall_verdict") == "pass" and stage == "postmerge":
            if payload.get("verification_scope") == "artifact-verified":
                _emit("다음 행동", "소스와 build artifact 검사가 완료됐습니다. 같은 result digest에 담당자 승인을 결속한 뒤 별도 운영 배포 절차로 진행하세요.")
            else:
                _emit("다음 행동", "소스 검사는 통과했습니다. build-artifact 검증 전에는 운영 배포를 승인하지 마세요.")
        else:
            _emit("다음 행동", "차단·분석 오류 원인을 해결한 뒤 전체 Phase를 다시 실행하세요.")
    else:
        tier = payload.get("tier_outputs", {})
        scope = payload.get("verification_scope") or "기록 없음(구버전)"
        _emit("검사 범위", scope)
        if not payload.get("verified"):
            _emit("Canonical", "확인됨" if payload.get("canonical_verified") else "불일치")
            _emit("관리자 요약", "확인됨" if tier.get("manager") else "불일치")
            _emit("실무자 상세", "확인됨" if tier.get("practitioner") else "불일치")
        if scope == "artifact-verified":
            _emit("운영 배포", "담당자 승인 결속 전에는 완료로 처리하지 마세요.")
        else:
            _emit("운영 배포", "build-artifact 검증 전 승인 금지")
        _emit("결과 digest", payload.get("result_digest") or "-")
        if payload.get("verified"):
            if scope == "artifact-verified":
                _emit("다음 행동", "같은 result digest에 담당자 승인을 결속한 뒤 별도 운영 배포 절차로 진행하세요.")
            else:
                _emit("다음 행동", "build-artifact Candidate lock과 Runtime Contract를 준비해 postmerge를 다시 실행하세요.")
        else:
            _emit("다음 행동", "canonical·관리자·실무자 결과의 불일치를 해결한 뒤 다시 확인하세요.")
    if evidence is not None:
        if evidence.is_file():
            _emit("증거 파일", evidence)
        else:
            _emit("증거 경로", f"{evidence} (중단되어 생성되지 않음)")


def run_phase_command(
    command: list[str],
    *,
    stage: str,
    output_format: str,
    evidence: Path | None = None,
) -> int:
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
    payload = _last_json(completed.stdout)
    if output_format == "json" or payload is None:
        if completed.stdout:
            print(completed.stdout, end="")
    else:
        _print_human_phase(
            stage,
            {**payload, "process_exit_code": completed.returncode},
            evidence=evidence,
        )
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    return completed.returncode


def safe_phase_output(run_id: str) -> Path:
    try:
        return phase_bundle.evidence_path(PROJECT / "evidence", run_id)
    except phase_bundle.ApprovalError as exc:
        raise WorkflowInputError(str(exc)) from exc


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
    parser.add_argument("--repo", required=True, type=Path, help="검사할 OpenMetadata 제품 Git 저장소")
    parser.add_argument(
        "--version", "--registration-version", dest="version", required=True,
        help="등록 묶음 버전, 예: 1.13.1 (1.13.2 Candidate 검사에도 같은 묶음을 사용할 수 있음)",
    )


def add_phase_output_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output-format",
        choices=("human", "json"),
        default="human",
        help="화면에는 human 요약을 표시하고, 자동화는 json을 선택합니다",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "제품 코드 저장소 경로와 버전만 입력하면 등록 폴더와 정책 파일을 "
            "자동으로 찾아 준비·검사 명령을 실행합니다."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="승인 전 등록 변경안 생성")
    add_repo_version(plan)
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

    phase_candidate = subparsers.add_parser(
        "candidate-select",
        help="승인된 활성 Candidate lock을 명시적으로 선택",
    )
    phase_candidate.add_argument(
        "--version", "--registration-version", dest="version", required=True,
        help="등록 묶음 버전, 예: 1.13.1",
    )
    phase_candidate.add_argument("--output", type=Path, help="선택 결과 JSON 경로")
    add_phase_output_format(phase_candidate)

    collect_conflict = subparsers.add_parser(
        "collect-conflict-evidence",
        help="승인된 병합 입력에서 변경·충돌 경로 증거를 자동 수집",
    )
    add_repo_version(collect_conflict)
    collect_conflict.add_argument(
        "--baseline-lock-digest", required=True,
        help="병합 전 승인된 기준선 Candidate lock의 sha256 digest",
    )
    collect_conflict.add_argument(
        "--custom-head", required=True,
        help="승인된 기준선 Candidate의 전체 commit SHA",
    )
    collect_conflict.add_argument("--output", required=True, type=Path)
    add_phase_output_format(collect_conflict)

    prep_official = subparsers.add_parser(
        "prep-official",
        help="공식 tag commit에 고정된 로컬 공식 branch 준비",
    )
    prep_official.add_argument("--repo", required=True, type=Path, help="공식 tag가 있는 제품 Git 저장소")
    prep_official.add_argument("--tag-ref", required=True, help="공식 release tag, 예: 1.13.2-release")
    prep_official.add_argument("--branch", required=True, help="tag commit에 고정할 로컬 branch")
    prep_official.add_argument("--output", type=Path, help="tag·commit 결속 증거 JSON 경로")
    add_phase_output_format(prep_official)

    phase_preflight = subparsers.add_parser(
        "phase-preflight",
        help="Phase 실행 전에 commit·정책·후보 입력을 한 번에 검사",
    )
    add_repo_version(phase_preflight)
    phase_preflight.add_argument("--phase", required=True, choices=["premerge", "postmerge"])
    phase_preflight.add_argument("--base", help="공식 이전 버전 전체 commit SHA")
    phase_preflight.add_argument("--target", help="공식 새 버전 전체 commit SHA")
    phase_preflight.add_argument(
        "--official-evidence",
        type=Path,
        help="premerge에서 prep-official이 생성한 공식 tag·commit 결속 JSON",
    )
    phase_preflight.add_argument("--change-intent", type=Path, help="담당자가 승인한 민감 경로 변경 의도 YAML")
    phase_preflight.add_argument("--debt-policy", type=Path, help="유지 부담 임계값 정책 YAML")
    phase_preflight.add_argument("--conflict-rate", type=float, help="증거와 대조할 비율; 단독 입력 불가")
    phase_preflight.add_argument(
        "--conflict-evidence",
        type=Path,
        help="실제 merge 변경·충돌 경로와 Candidate SHA를 기록한 YAML/JSON",
    )
    phase_preflight.add_argument("--active-source", action="append", default=[], help="추가 활성 후보 NAME=SHA; 여러 번 지정 가능")
    phase_preflight.add_argument("--output", type=Path, help="사전검사 결과 JSON 경로")
    add_phase_output_format(phase_preflight)

    premerge = subparsers.add_parser(
        "premerge-check",
        help="공식 새 버전을 병합하기 전 영향 검사 Phase 실행",
    )
    add_repo_version(premerge)
    premerge.add_argument("--base", required=True, help="공식 이전 버전 전체 commit SHA")
    premerge.add_argument(
        "--target",
        help="필수: 공식 새 버전 전체 commit SHA (누락 시 복구 안내와 함께 중단)",
    )
    premerge.add_argument("--candidate-ref", help="생략하면 활성 Candidate lock의 commit 사용")
    premerge.add_argument(
        "--official-evidence",
        required=True,
        type=Path,
        help="prep-official이 생성한 공식 tag·commit 결속 JSON",
    )
    premerge.add_argument("--active-source", action="append", default=[], help="추가 활성 후보 NAME=SHA; 여러 번 지정 가능")
    premerge.add_argument("--run-id", help="증거 폴더 식별자; 생략하면 안전한 시각 기반 ID 생성")
    premerge.add_argument("--output", type=Path, help="Phase canonical result JSON 경로")
    add_phase_output_format(premerge)

    postmerge = subparsers.add_parser(
        "postmerge-check",
        help="vendor-merge 후보를 만든 뒤 최종 소스 위험 검사 Phase 실행",
    )
    add_repo_version(postmerge)
    postmerge.add_argument("--base", help="생략하면 활성 Candidate lock의 공식 base SHA 사용")
    postmerge.add_argument("--target", help="생략하면 활성 Candidate lock의 공식 target SHA 사용")
    postmerge.add_argument("--change-intent", type=Path, help="담당자가 승인한 민감 경로 변경 의도 YAML")
    postmerge.add_argument("--debt-policy", type=Path, help="생략하면 기본 유지 부담 정책 사용")
    postmerge.add_argument("--conflict-rate", type=float, help="증거와 대조할 비율; 단독 입력 불가")
    postmerge.add_argument(
        "--conflict-evidence",
        type=Path,
        help="실제 merge 변경·충돌 경로와 Candidate SHA를 기록한 YAML/JSON",
    )
    postmerge.add_argument("--artifact-digest", help="build-artifact lock과 일치하는 sha256 digest")
    postmerge.add_argument("--contract-output-dir", type=Path, help="Runtime Contract 상세 증거 폴더")
    postmerge.add_argument("--active-source", action="append", default=[], help="추가 활성 후보 NAME=SHA; 여러 번 지정 가능")
    postmerge.add_argument("--run-id", help="증거 폴더 식별자; 생략하면 안전한 시각 기반 ID 생성")
    postmerge.add_argument("--output", type=Path, help="Phase canonical result JSON 경로")
    add_phase_output_format(postmerge)

    phase_status = subparsers.add_parser(
        "phase-status",
        help="저장된 Phase 결과 digest와 상태 확인",
    )
    phase_status.add_argument("--result", required=True, type=Path, help="재검증할 canonical result.json")
    add_phase_output_format(phase_status)

    return parser.parse_args()


def plan_command(args: argparse.Namespace) -> tuple[list[str], dict[str, object]]:
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
    if args.command == "prep-official":
        output = args.output or PROJECT / "evidence" / f"official-branch-{timestamp()}.json"
        return run_phase_command(
            python_command(
                HARNESS / "run_phase_bundle.py",
                "prep-official",
                "--repo", args.repo,
                "--tag-ref", args.tag_ref,
                "--branch", args.branch,
                "--output", output,
            ),
            stage="official",
            output_format=args.output_format,
            evidence=output,
        )

    if args.command == "candidate-select":
        registration = registration_for(args.version)
        output = args.output or PROJECT / "evidence" / f"phase-candidate-{args.version}.json"
        return run_phase_command(
            python_command(
                HARNESS / "run_phase_bundle.py",
                "candidate",
                "--registration", registration,
                "--output", output,
            ),
            stage="candidate",
            output_format=args.output_format,
            evidence=output,
        )

    if args.command == "collect-conflict-evidence":
        registration = registration_for(args.version)
        command = python_command(
            HARNESS / "run_phase_bundle.py",
            "collect-conflict-evidence",
            "--repo", args.repo,
            "--registration", registration,
            "--baseline-lock-digest", args.baseline_lock_digest,
            "--custom-head", args.custom_head,
            "--output", args.output,
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(HARNESS)
        completed = subprocess.run(
            command, cwd=PROJECT, env=environment, check=False,
            capture_output=True, text=True,
        )
        payload = _last_json(completed.stdout)
        if args.output_format == "json" or payload is None:
            if completed.stdout:
                print(completed.stdout, end="")
        else:
            print("\n[새 5단계] 충돌 증거 자동 수집")
            _emit("결과", _result_label(payload))
            _emit("종료 코드", completed.returncode)
            if payload.get("reason"):
                _emit("사유", payload["reason"])
            else:
                _emit("변경 경로", f"{payload.get('changed_path_count', 0)}개")
                _emit("충돌 경로", f"{payload.get('conflicted_path_count', 0)}개")
                _emit("충돌률", payload.get("conflict_rate"))
                _emit("rename 탐지", payload.get("rename_detection"))
                _emit("증거 파일", payload.get("output"))
                _emit("다음 행동", "증거 파일을 phase-preflight와 postmerge-check에 전달하세요.")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        return completed.returncode

    if args.command == "phase-preflight":
        registration = registration_for(args.version)
        output = args.output or PROJECT / "evidence" / f"{args.phase}-preflight-{timestamp()}.json"
        debt_policy = args.debt_policy
        if args.phase == "postmerge" and debt_policy is None:
            debt_policy = HARNESS / "policies" / "debt-thresholds.yaml"
        command = python_command(
            HARNESS / "run_phase_bundle.py",
            "preflight",
            "--repo", args.repo,
            "--registration", registration,
            "--phase", args.phase,
            "--output", output,
        )
        for option, value in (
            ("--base", args.base), ("--target", args.target),
            ("--official-evidence", args.official_evidence),
            ("--change-intent", args.change_intent), ("--debt-policy", debt_policy),
            ("--conflict-rate", args.conflict_rate),
            ("--conflict-evidence", args.conflict_evidence),
        ):
            if value is not None:
                command.extend([option, str(value)])
        for source in args.active_source:
            command.extend(["--active-source", source])
        return run_phase_command(
            command,
            stage="preflight",
            output_format=args.output_format,
            evidence=output,
        )

    if args.command in {"premerge-check", "postmerge-check"}:
        registration = registration_for(args.version)
        phase_name = "premerge" if args.command == "premerge-check" else "postmerge"
        run_id = args.run_id or f"{phase_name}-{timestamp()}"
        safe_default_output = safe_phase_output(run_id)
        output = args.output or safe_default_output
        command = python_command(
            HARNESS / "run_phase_bundle.py",
            phase_name,
            "--repo", args.repo,
            "--registration", registration,
            "--run-id", run_id,
            "--output", output,
        )
        for option in (
            "base", "target", "candidate_ref", "change_intent", "debt_policy",
            "conflict_rate", "conflict_evidence", "artifact_digest",
            "contract_output_dir", "official_evidence",
        ):
            value = getattr(args, option, None)
            if value is not None:
                command.extend(["--" + option.replace("_", "-"), str(value)])
        if phase_name == "postmerge" and args.debt_policy is None:
            command.extend(["--debt-policy", str(HARNESS / "policies" / "debt-thresholds.yaml")])
        for source in args.active_source:
            command.extend(["--active-source", source])
        return run_phase_command(
            command,
            stage=phase_name,
            output_format=args.output_format,
            evidence=output,
        )

    if args.command == "phase-status":
        require_file(args.result, "Phase 결과")
        return run_phase_command(
            python_command(
                HARNESS / "run_phase_bundle.py", "status", "--result", args.result,
            ),
            stage="status",
            output_format=args.output_format,
            evidence=args.result,
        )

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


if __name__ == "__main__":
    raise SystemExit(main())
