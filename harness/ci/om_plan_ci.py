#!/usr/bin/env python3
"""Provider-neutral CI boundary for /om-plan preflight and validation.

The planner output is treated as untrusted data.  This module never executes
files from the proposal checkout and never derives the trusted expected digest
from the proposal artifact.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

from acgh.plancore.markers import MarkerPair, bind_run, create_session_marker


_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_ALLOWED_PROPOSAL_SUFFIXES = {".json", ".yaml", ".yml"}
_EXIT_BY_VERDICT = {
    "pass": 0,
    "block": 1,
    "approval": 2,
    "analysis_error": 3,
}


class PlanCIError(RuntimeError):
    """A CI boundary is missing, malformed, or internally inconsistent."""


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _append_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(value)


def _within(root: Path, candidate: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise PlanCIError(f"{label} escapes its allowed root: {candidate}") from exc
    return resolved


def _local_source(source: str, root: Path, label: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        return source
    path = Path(source)
    if path.is_absolute():
        raise PlanCIError(
            f"{label} must be repository-relative in CI, not an absolute path"
        )
    resolved = _within(root, root / path, label)
    if not resolved.is_file() or resolved.is_symlink():
        raise PlanCIError(f"{label} is not a regular file: {resolved}")
    return str(resolved)


def prepare_request(
    source: Path,
    output: Path,
    product_repo: Path,
    checker_repo: Path,
    *,
    request_root: Path | None = None,
) -> dict:
    """Make a CI-local request copy without changing semantic plan inputs."""
    root = (request_root or source.parent).resolve()
    resolved_source = _within(root, source, "request")
    if resolved_source.is_symlink() or not resolved_source.is_file():
        raise PlanCIError(f"request is not a regular file: {resolved_source}")
    try:
        request = yaml.safe_load(resolved_source.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PlanCIError(f"cannot read request: {exc}") from exc
    if not isinstance(request, dict):
        raise PlanCIError("request must be a YAML mapping")

    request["repositories"] = {
        "product": str(product_repo.resolve()),
        "checker": str(checker_repo.resolve()),
    }
    registration = request.get("registration_path")
    if registration is not None:
        registration_path = Path(registration)
        if registration_path.is_absolute():
            raise PlanCIError(
                "registration_path must be checker-repository-relative in CI"
            )
        request["registration_path"] = str(
            _within(
                checker_repo,
                checker_repo / registration_path,
                "registration_path",
            )
        )

    documents = request.get("official_documents") or []
    if not isinstance(documents, list):
        raise PlanCIError("official_documents must be a list")
    for index, document in enumerate(documents):
        if not isinstance(document, dict) or not isinstance(
            document.get("source"), str
        ):
            raise PlanCIError(f"official_documents[{index}].source is invalid")
        document["source"] = _local_source(
            document["source"], root, f"official_documents[{index}].source"
        )

    _write_text(output, yaml.safe_dump(request, sort_keys=False, allow_unicode=True))
    return request


def capture_preflight(
    source: Path,
    github_output: Path,
    step_summary: Path,
    receipt: Path,
) -> str:
    """Capture the trusted digest in CI-owned output and show human intent."""
    try:
        result = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanCIError(f"cannot read preflight JSON: {exc}") from exc
    if not isinstance(result, dict) or result.get("status") != "ready_for_proposal":
        raise PlanCIError("preflight did not reach ready_for_proposal")
    digest = result.get("input_lock_digest")
    if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
        raise PlanCIError("preflight input_lock_digest is missing or malformed")
    if result.get("intent_review_required") is not True:
        raise PlanCIError("preflight did not require human intent review")
    intent = result.get("intent_summary")
    if not isinstance(intent, dict):
        raise PlanCIError("preflight intent_summary is missing")

    _append_text(github_output, f"input_lock_digest={digest}\n")
    _write_text(receipt, f"{digest}\n")
    _append_text(
        step_summary,
        "## /om-plan 사전 요청 확인\n\n"
        "아래 요청 내용과 고정 commit SHA를 사람이 확인해야 합니다. "
        "이 확인은 구현·배포 승인이 아닙니다.\n\n"
        "```json\n"
        f"{json.dumps(intent, ensure_ascii=False, indent=2, sort_keys=True)}\n"
        "```\n\n"
        f"- 다음 행동: {result.get('operator_action', '')}\n",
    )
    return digest


def package_proposal(
    source: Path,
    output: Path,
    *,
    source_root: Path | None = None,
) -> list[Path]:
    """Copy proposal data only; never execute or import untrusted content."""
    root = (source_root or source.parent).resolve()
    resolved_source = _within(root, source, "proposal source")
    if resolved_source.is_symlink() or not resolved_source.is_dir():
        raise PlanCIError(f"proposal source is not a regular directory: {source}")
    if output.exists():
        if output.is_symlink() or not output.is_dir():
            raise PlanCIError(f"proposal output is not a regular directory: {output}")
        if any(output.iterdir()):
            raise PlanCIError(f"proposal output is not empty: {output}")

    files: list[tuple[Path, Path]] = []
    for candidate in sorted(resolved_source.rglob("*")):
        if candidate.is_symlink():
            raise PlanCIError(f"proposal symlink is forbidden: {candidate}")
        if candidate.is_dir():
            continue
        if candidate.suffix.lower() not in _ALLOWED_PROPOSAL_SUFFIXES:
            raise PlanCIError(f"unsupported proposal file: {candidate}")
        files.append((candidate, candidate.relative_to(resolved_source)))
    if not files:
        raise PlanCIError("proposal contains no YAML or JSON files")

    output.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for candidate, relative in files:
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate, destination)
        copied.append(destination)
    return copied


def restore_run(
    run_dir: Path,
    state_root: Path,
    project_root: Path,
    session_id: str,
) -> MarkerPair:
    """Rebind a trusted preflight artifact after extraction on a fresh runner."""
    root = run_dir.resolve()
    if not root.is_dir():
        raise PlanCIError(f"trusted run directory is missing: {root}")
    marker = root / ".plan-active"
    if marker.is_symlink():
        raise PlanCIError("trusted run marker must not be a symlink")
    if marker.exists():
        marker.unlink()
    session_marker = create_session_marker(state_root, project_root, session_id)
    return bind_run(session_marker, root)


def rebind_run_request(
    run_dir: Path,
    product_repo: Path,
    checker_repo: Path,
) -> dict:
    """Rebind excluded runtime paths after moving a run to a fresh runner."""
    request_path = run_dir.resolve() / "run-request.yaml"
    try:
        request = yaml.safe_load(request_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PlanCIError(f"cannot read relocated run request: {exc}") from exc
    if not isinstance(request, dict):
        raise PlanCIError("relocated run request must be a YAML mapping")
    repositories = request.get("repositories")
    if not isinstance(repositories, dict):
        raise PlanCIError("relocated run request repositories are missing")

    old_checker = Path(str(repositories.get("checker", "")))
    registration = request.get("registration_path")
    if registration is not None:
        old_registration = Path(registration)
        if old_registration.is_absolute():
            try:
                relative = old_registration.relative_to(old_checker)
            except ValueError as exc:
                raise PlanCIError(
                    "registration_path is not inside the recorded checker repository"
                ) from exc
        else:
            relative = old_registration
        request["registration_path"] = str(
            _within(
                checker_repo,
                checker_repo / relative,
                "registration_path",
            )
        )

    request["repositories"] = {
        "product": str(product_repo.resolve()),
        "checker": str(checker_repo.resolve()),
    }
    _write_text(
        request_path,
        yaml.safe_dump(request, sort_keys=False, allow_unicode=True),
    )
    return request


def run_fresh_validation(
    checker_root: Path,
    run_dir: Path,
    expected_digest: str,
    captured_output: Path,
    step_summary: Path,
) -> int:
    """Trust only this subprocess stdout and exit code, never a stored result."""
    if not _DIGEST.fullmatch(expected_digest):
        raise PlanCIError("trusted expected digest is malformed")
    checker = checker_root.resolve()
    command = [
        sys.executable,
        str(checker / "harness" / "om_workflow.py"),
        "plan-validate",
        "--run-dir",
        str(run_dir.resolve()),
        "--expected-input-lock-digest",
        expected_digest,
    ]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(checker / "harness")
    completed = subprocess.run(
        command,
        cwd=checker,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    _write_text(captured_output, completed.stdout)
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PlanCIError("fresh validation stdout is not JSON") from exc
    if not isinstance(result, dict):
        raise PlanCIError("fresh validation stdout must be a JSON object")
    verdict = result.get("verdict")
    expected_exit = _EXIT_BY_VERDICT.get(verdict)
    if expected_exit is None or completed.returncode != expected_exit:
        raise PlanCIError(
            "fresh validation exit code does not match its stdout verdict"
        )
    expected_review_state = "review_ready" if verdict == "approval" else "not_ready"
    if result.get("review_state") != expected_review_state:
        raise PlanCIError(
            "fresh validation review_state does not match its stdout verdict"
        )

    ci_exit_code = 0 if verdict in {"pass", "approval"} else completed.returncode
    ci_status = "success-review-ready" if verdict == "approval" else (
        "success" if verdict == "pass" else "failed"
    )
    _append_text(
        step_summary,
        "## /om-plan fresh validation\n\n"
        f"- verdict: `{verdict}`\n"
        f"- review_state: `{result['review_state']}`\n"
        f"- CLI exit code: `{completed.returncode}`\n"
        f"- CI status: `{ci_status}`\n"
        f"- CI exit code: `{ci_exit_code}`\n"
        "- `approval`은 배포 승인이 아니라 계획 검토 준비 상태\n"
        "- 판정 근거: 이 job에서 방금 실행한 CLI stdout과 종료 코드\n"
        "- 주의: 저장된 결과 파일 바이트는 CI 판정 입력으로 사용하지 않음\n",
    )
    return ci_exit_code


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-request")
    prepare.add_argument("--source", required=True, type=Path)
    prepare.add_argument("--output", required=True, type=Path)
    prepare.add_argument("--product-repo", required=True, type=Path)
    prepare.add_argument("--checker-repo", required=True, type=Path)
    prepare.add_argument("--request-root", required=True, type=Path)

    capture = subparsers.add_parser("capture-preflight")
    capture.add_argument("--source", required=True, type=Path)
    capture.add_argument("--github-output", required=True, type=Path)
    capture.add_argument("--step-summary", required=True, type=Path)
    capture.add_argument("--receipt", required=True, type=Path)

    package = subparsers.add_parser("package-proposal")
    package.add_argument("--source", required=True, type=Path)
    package.add_argument("--output", required=True, type=Path)
    package.add_argument("--source-root", required=True, type=Path)

    restore = subparsers.add_parser("restore-run")
    restore.add_argument("--run-dir", required=True, type=Path)
    restore.add_argument("--state-root", required=True, type=Path)
    restore.add_argument("--project-root", required=True, type=Path)
    restore.add_argument("--session-id", required=True)

    rebind = subparsers.add_parser("rebind-run-request")
    rebind.add_argument("--run-dir", required=True, type=Path)
    rebind.add_argument("--product-repo", required=True, type=Path)
    rebind.add_argument("--checker-repo", required=True, type=Path)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--checker-root", required=True, type=Path)
    validate.add_argument("--run-dir", required=True, type=Path)
    validate.add_argument("--expected-input-lock-digest", required=True)
    validate.add_argument("--captured-output", required=True, type=Path)
    validate.add_argument("--step-summary", required=True, type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "prepare-request":
            prepare_request(
                args.source,
                args.output,
                args.product_repo,
                args.checker_repo,
                request_root=args.request_root,
            )
            return 0
        if args.command == "capture-preflight":
            capture_preflight(
                args.source,
                args.github_output,
                args.step_summary,
                args.receipt,
            )
            return 0
        if args.command == "package-proposal":
            package_proposal(
                args.source,
                args.output,
                source_root=args.source_root,
            )
            return 0
        if args.command == "restore-run":
            restore_run(
                args.run_dir,
                args.state_root,
                args.project_root,
                args.session_id,
            )
            return 0
        if args.command == "rebind-run-request":
            rebind_run_request(
                args.run_dir,
                args.product_repo,
                args.checker_repo,
            )
            return 0
        return run_fresh_validation(
            args.checker_root,
            args.run_dir,
            args.expected_input_lock_digest,
            args.captured_output,
            args.step_summary,
        )
    except PlanCIError as exc:
        print(f"[om-plan CI analysis_error] {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
