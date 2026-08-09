#!/usr/bin/env python3
"""Execute candidate selection, preflight, and phase bundles as real CLI steps."""
from __future__ import annotations

import argparse
import datetime
import getpass
import hashlib
import json
import math
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

import yaml

from acgh import approval as approval_module
from acgh import candidate
from acgh import candidate_select
from acgh import debt
from acgh import gitprim
from acgh import layout as layout_module
from acgh import manifest as manifest_module
from acgh import phase
from acgh import preflight
from acgh import rollup
from acgh import verdict
from acgh import zones as zones_module


class PhaseCLIError(RuntimeError):
    """The requested phase cannot produce trustworthy evidence."""


class CandidatePolicyBlock(PhaseCLIError):
    """A known-and-invalid Candidate state: report as block, not analysis_error.

    A missing approval, a digest that does not bind, or a lock that belongs to a
    different registration baseline are *answered* questions with a negative
    answer. Reporting them as analysis_error would claim the check never ran.
    """


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(blob, encoding="utf-8")
    os.replace(tmp, path)


def _now_rfc3339() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _actor() -> dict:
    """Who and where a governance artifact was produced. Recorded, never trusted."""
    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 - a nameless environment must not break a write
        user = "unknown"
    return {"user": user, "host": socket.gethostname()}


def _write_guarded(
    path: Path,
    blob: bytes,
    *,
    label: str,
    validate=None,
    allow_replace: bool = False,
) -> None:
    """Create one governance file without clobbering or exposing partial data.

    A sibling ``.<name>.lock`` is claimed with O_EXCL first, so two concurrent
    writers cannot both pass an ``exists()`` check and race to ``os.replace``.
    The payload lands in a temp file that is fsynced and validated before the
    atomic rename, so a crash never leaves a half-written artifact under the
    real name. The reservation records pid/host/time to make a stale lock
    diagnosable by a human instead of auto-deleted by the tool.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    reservation = path.with_name(f".{path.name}.lock")
    try:
        reservation_fd = os.open(
            str(reservation), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644
        )
    except FileExistsError as exc:
        raise PhaseCLIError(
            f"다른 {label} 실행이 경로를 사용 중입니다: {path}; lock={reservation}. "
            "동시 실행이 없는데 반복되면 lock 파일의 생성 시각·pid·host를 확인하고, "
            "실행 중인 프로세스가 없을 때만 제거한 뒤 다시 실행하세요."
        ) from exc
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        metadata = json.dumps({
            "pid": os.getpid(),
            **_actor(),
            "created_at": _now_rfc3339(),
            "output": str(path),
        }, ensure_ascii=False, sort_keys=True).encode("utf-8")
        os.write(reservation_fd, metadata)
        os.fsync(reservation_fd)
        if path.exists() and not allow_replace:
            raise PhaseCLIError(f"기존 {label} 파일을 덮어쓰지 않습니다: {path}")
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            os.write(fd, blob)
            os.fsync(fd)
        finally:
            os.close(fd)
        if validate is not None:
            validate(tmp)
        os.replace(str(tmp), str(path))
    finally:
        tmp.unlink(missing_ok=True)
        os.close(reservation_fd)
        reservation.unlink(missing_ok=True)


def _write_conflict_evidence(path: Path, payload: dict, validate) -> None:
    """Write one collector artifact without clobbering or exposing partial data."""
    _write_guarded(
        path,
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True).encode("utf-8"),
        label="수집 작업",
        validate=validate,
    )


def _sha256_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_mapping(path: Path, label: str) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PhaseCLIError(f"{label} 파일을 읽을 수 없습니다: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PhaseCLIError(f"{label} 파일은 mapping이어야 합니다: {path}")
    return data


def _registration_digests(registration: Path) -> dict[str, str]:
    """Bind every registration input that can affect a Phase judgment."""
    names = (
        "customization-registry.yaml",
        "contracts.yaml",
        "shared-code-definitions.yaml",
        "shared-path-owners.yaml",
        "commit-inventory.yaml",
    )
    paths = [registration / name for name in names]
    paths.extend(sorted((registration / "manifests").glob("BANK-OM-*.yaml")))
    return {
        path.relative_to(registration).as_posix(): _sha256_file(path)
        for path in paths
        if path.is_file()
    }


def _bind_official_evidence(args) -> str:
    evidence = _load_mapping(args.official_evidence, "공식 버전 준비 증거")
    commit_sha = evidence.get("commit_sha")
    if not args.target:
        raise PhaseCLIError(
            "premerge에는 --target이 필요합니다. prep-official 결과의 "
            "commit_sha 전체 값을 입력하세요."
        )
    if commit_sha != args.target:
        raise PhaseCLIError(
            "premerge target이 공식 버전 준비 증거와 다릅니다: "
            f"{args.target} != {commit_sha}"
        )
    for label in ("tag_ref", "branch"):
        ref = evidence.get(label)
        if not isinstance(ref, str) or not ref:
            raise PhaseCLIError(f"공식 버전 준비 증거에 {label} 값이 없습니다")
        phase.assert_target_matches_tag(str(args.repo), ref, commit_sha)
    return _sha256_file(args.official_evidence)


def _bind_conflict_evidence(args, lock) -> str | None:
    path = getattr(args, "conflict_evidence", None)
    supplied_rate = getattr(args, "conflict_rate", None)
    if path is None:
        if supplied_rate is not None:
            raise PhaseCLIError(
                "--conflict-rate만 직접 입력할 수 없습니다. 실제 merge 결과를 담은 "
                "--conflict-evidence 파일을 제공하세요."
            )
        return None

    evidence = _load_mapping(path, "conflict-rate 증거")
    expected = {
        "upstream_base_sha": lock.upstream.base_sha,
        "upstream_target_sha": lock.upstream.target_sha,
        "candidate_sha": lock.candidate.commit_sha,
    }
    for field, expected_value in expected.items():
        if evidence.get(field) != expected_value:
            raise PhaseCLIError(
                f"conflict-rate 증거의 {field}가 Candidate lock과 다릅니다: "
                f"{evidence.get(field)} != {expected_value}"
            )
    custom_head = evidence.get("custom_head_sha")
    baseline_digest = evidence.get("baseline_candidate_lock_digest")
    recorded_merge_base = evidence.get("merge_base_sha")
    if not isinstance(custom_head, str) or not custom_head:
        raise PhaseCLIError("conflict-rate 증거에 custom_head_sha가 필요합니다")
    if not isinstance(baseline_digest, str) or not baseline_digest:
        raise PhaseCLIError(
            "conflict-rate 증거에 baseline_candidate_lock_digest가 필요합니다"
        )
    baseline = candidate_select.select_approved_candidate(
        args.registration, baseline_digest
    )
    if baseline.status != candidate_select.SELECTED or baseline.lock is None:
        raise PhaseCLIError(
            "conflict-rate 증거의 이전 기준선 lock이 승인되지 않았습니다: "
            + "; ".join(baseline.reasons)
        )
    if baseline.lock.candidate.commit_sha != custom_head:
        raise PhaseCLIError(
            "custom_head_sha가 승인된 이전 기준선 Candidate와 다릅니다: "
            f"{custom_head} != {baseline.lock.candidate.commit_sha}"
        )
    if custom_head == lock.candidate.commit_sha:
        raise PhaseCLIError(
            "활성 lock이 아직 병합 전 기준선입니다. 새 1.13.2 Candidate lock을 "
            "승인·활성화한 뒤 conflict evidence를 수집하거나 검증하세요."
        )
    if baseline.lock.upstream.target_sha != lock.upstream.base_sha:
        raise PhaseCLIError(
            "이전 기준선 lock의 upstream target이 현재 upgrade base와 다릅니다"
        )
    if not gitprim.is_ancestor(str(args.repo), custom_head, lock.candidate.commit_sha):
        raise PhaseCLIError("custom_head_sha가 postmerge Candidate에 포함되지 않았습니다")
    actual_merge_base = gitprim.merge_base(
        str(args.repo), lock.upstream.target_sha, custom_head
    )
    if actual_merge_base != lock.upstream.base_sha:
        raise PhaseCLIError(
            "target과 custom head의 merge-base가 Candidate lock의 base와 다릅니다: "
            f"{actual_merge_base} != {lock.upstream.base_sha}"
        )
    if recorded_merge_base != actual_merge_base:
        raise PhaseCLIError(
            "conflict-rate 증거의 merge_base_sha가 실제 merge-base와 다릅니다: "
            f"{recorded_merge_base} != {actual_merge_base}"
        )
    changed = evidence.get("merge_changed_paths")
    conflicted = evidence.get("conflicted_paths")
    if not isinstance(changed, list) or not changed or not all(
        isinstance(item, str) and item for item in changed
    ):
        raise PhaseCLIError("conflict-rate 증거의 merge_changed_paths는 비어 있지 않은 경로 목록이어야 합니다")
    if not isinstance(conflicted, list) or not all(
        isinstance(item, str) and item for item in conflicted
    ):
        raise PhaseCLIError("conflict-rate 증거의 conflicted_paths는 경로 목록이어야 합니다")
    changed_set = set(changed)
    conflicted_set = set(conflicted)
    if len(changed_set) != len(changed):
        raise PhaseCLIError("conflict-rate 증거의 merge_changed_paths에 중복 경로가 있습니다")
    if len(conflicted_set) != len(conflicted):
        raise PhaseCLIError("conflict-rate 증거의 conflicted_paths에 중복 경로가 있습니다")
    outside = sorted(conflicted_set - changed_set)
    if outside:
        raise PhaseCLIError(
            "conflict-rate 증거의 충돌 경로가 merge 변경 경로에 없습니다: "
            + ", ".join(outside)
        )
    expected_changed = set(gitprim.net_changed_paths(
        str(args.repo), lock.upstream.base_sha, lock.upstream.target_sha
    )) | set(gitprim.net_changed_paths(
        str(args.repo), lock.upstream.base_sha, custom_head
    ))
    if changed_set != expected_changed:
        missing = sorted(expected_changed - changed_set)
        extra = sorted(changed_set - expected_changed)
        raise PhaseCLIError(
            "merge_changed_paths가 base 대비 target·custom head 변경 경로와 다릅니다: "
            f"missing={missing}, extra={extra}"
        )
    replay = gitprim.merge_tree_conflicts(
        str(args.repo), lock.upstream.target_sha, custom_head
    )
    if conflicted_set != set(replay.conflicted_paths):
        raise PhaseCLIError(
            "conflicted_paths가 git merge-tree 재현 결과와 다릅니다: "
            f"recorded={sorted(conflicted_set)}, replayed={list(replay.conflicted_paths)}"
        )
    measured_rate = len(conflicted_set) / len(changed_set)
    recorded_rate = evidence.get("conflict_rate")
    if recorded_rate is not None and (
        not isinstance(recorded_rate, (int, float))
        or isinstance(recorded_rate, bool)
        or not math.isfinite(float(recorded_rate))
        or not math.isclose(
            float(recorded_rate), measured_rate, rel_tol=0.0, abs_tol=1e-12
        )
    ):
        raise PhaseCLIError(
            "conflict-rate 증거의 비율이 경로 수 계산과 다릅니다: "
            f"recorded={recorded_rate}, measured={measured_rate!r} "
            f"({len(conflicted_set)}/{len(changed_set)}). "
            "반올림 값을 수정하거나 conflict_rate 필드를 생략하세요."
        )
    if supplied_rate is not None and not math.isclose(
        float(supplied_rate), measured_rate, rel_tol=0.0, abs_tol=1e-12
    ):
        raise PhaseCLIError(
            f"--conflict-rate가 증거에서 계산한 값과 다릅니다: {supplied_rate} != {measured_rate}"
        )
    args.conflict_rate = measured_rate
    args.conflict_measurement = {
        "custom_head_sha": custom_head,
        "baseline_candidate_lock_digest": baseline_digest,
        "merge_base_sha": actual_merge_base,
        "changed_path_count": len(changed_set),
        "conflicted_path_count": len(conflicted_set),
        "conflict_rate": measured_rate,
        "merge_tree": {
            "strategy": "ort (git merge-tree --write-tree default)",
            "rename_detection": replay.rename_detection_policy,
            "git_version": replay.git_version,
            "command": list(replay.command),
            "result_tree_sha": replay.tree_sha,
            "output_digest": replay.output_digest,
            "merge_driver_config_digest": replay.merge_driver_config_digest,
            "replay_config_digest": replay.replay_config_digest,
            "conflicted_paths": list(replay.conflicted_paths),
        },
    }
    return _sha256_file(path)


def collect_conflict_evidence_command(args) -> int:
    """Generate candidate-bound conflict evidence and self-check it before publish."""
    selection = _selected(args.registration)
    lock = selection.lock
    baseline = candidate_select.select_approved_candidate(
        args.registration, args.baseline_lock_digest
    )
    if baseline.status != candidate_select.SELECTED or baseline.lock is None:
        raise PhaseCLIError(
            "이전 기준선 lock이 승인되지 않았습니다: " + "; ".join(baseline.reasons)
        )
    if baseline.lock.candidate.commit_sha != args.custom_head:
        raise PhaseCLIError(
            "--custom-head가 승인된 이전 기준선 Candidate와 다릅니다: "
            f"{args.custom_head} != {baseline.lock.candidate.commit_sha}"
        )
    if args.custom_head == lock.candidate.commit_sha:
        raise PhaseCLIError(
            "활성 lock이 아직 병합 전 기준선입니다. 새 1.13.2 Candidate lock을 "
            "승인·활성화한 뒤 수집하세요."
        )
    base = lock.upstream.base_sha
    target = lock.upstream.target_sha
    merge_base_sha = gitprim.merge_base(str(args.repo), target, args.custom_head)
    changed = sorted(
        set(gitprim.net_changed_paths(str(args.repo), base, target))
        | set(gitprim.net_changed_paths(str(args.repo), base, args.custom_head)),
        key=lambda path: path.encode("utf-8"),
    )
    if not changed:
        raise PhaseCLIError("merge_changed_paths가 비어 있어 conflict-rate를 계산할 수 없습니다")
    replay = gitprim.merge_tree_conflicts(str(args.repo), target, args.custom_head)
    conflicted = list(replay.conflicted_paths)
    if not set(conflicted).issubset(changed):
        raise PhaseCLIError("merge-tree 충돌 경로가 merge 변경 경로 밖에 있습니다")
    payload = {
        "schema_version": 1,
        "upstream_base_sha": base,
        "upstream_target_sha": target,
        "candidate_sha": lock.candidate.commit_sha,
        "custom_head_sha": args.custom_head,
        "baseline_candidate_lock_digest": args.baseline_lock_digest,
        "merge_base_sha": merge_base_sha,
        "merge_changed_paths": changed,
        "conflicted_paths": conflicted,
        "collector_harness_digest": _harness_version(),
        "merge_tree": {
            "strategy": "ort (git merge-tree --write-tree default)",
            "rename_detection": replay.rename_detection_policy,
            "git_version": replay.git_version,
            "command": list(replay.command),
            "result_tree_sha": replay.tree_sha,
            "output_digest": replay.output_digest,
            "merge_driver_config_digest": replay.merge_driver_config_digest,
            "replay_config_digest": replay.replay_config_digest,
        },
    }

    def self_check(temp_path: Path) -> None:
        check_args = argparse.Namespace(
            conflict_evidence=temp_path,
            conflict_rate=None,
            registration=args.registration,
            repo=args.repo,
        )
        _bind_conflict_evidence(check_args, lock)

    _write_conflict_evidence(args.output, payload, self_check)
    print(json.dumps({
        "status": "created",
        "output": str(args.output),
        "candidate_sha": lock.candidate.commit_sha,
        "changed_path_count": len(changed),
        "conflicted_path_count": len(conflicted),
        "conflict_rate": len(conflicted) / len(changed),
        "rename_detection": replay.rename_detection_policy,
        "merge_driver_config_digest": replay.merge_driver_config_digest,
    }, ensure_ascii=False, sort_keys=True))
    return 0


def _load_manifests(registration: Path, layout) -> dict[str, dict]:
    manifests: dict[str, dict] = {}
    for path in sorted((registration / "manifests").glob("BANK-OM-*.yaml")):
        data = manifest_module.load_manifest(path, layout)
        customization_id = data["customization_id"]
        if customization_id in manifests:
            raise PhaseCLIError(f"duplicate manifest: {customization_id}")
        manifests[customization_id] = data
    if not manifests:
        raise PhaseCLIError(f"no manifests found under {registration / 'manifests'}")
    return manifests


def _selection_payload(selection) -> dict:
    return {
        "status": selection.status,
        "reasons": list(selection.reasons),
        "candidate_lock_digest": selection.lock_digest,
        "candidate_lock_path": selection.lock_path,
        "candidate_commit_sha": (
            selection.lock.candidate.commit_sha if selection.lock is not None else None
        ),
        "candidate_artifact_kind": (
            selection.lock.candidate.artifact_kind if selection.lock is not None else None
        ),
        "upstream_target_sha": (
            selection.lock.upstream.target_sha if selection.lock is not None else None
        ),
        "provenance": list(selection.provenance),
    }


def _selected(registration: Path):
    selection = candidate_select.select_active_candidate(registration)
    if selection.status != candidate_select.SELECTED or selection.lock is None:
        raise PhaseCLIError(
            f"active candidate is not selected ({selection.status}): "
            + "; ".join(selection.reasons)
        )
    return selection


def _parse_active_sources(values: list[str]) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for raw in values:
        if "=" not in raw:
            raise PhaseCLIError(f"--active-source must be NAME=SHA: {raw!r}")
        name, sha = raw.split("=", 1)
        if not name.strip() or not sha.strip():
            raise PhaseCLIError(f"--active-source must be NAME=SHA: {raw!r}")
        parsed.append((name.strip(), sha.strip()))
    return parsed


def _preflight(
    args,
    selection,
    *,
    phase_name: str,
    required_files: dict[str, Path],
    optional_inputs: dict | None = None,
) -> preflight.PreflightReport:
    lock = selection.lock
    default_base = (
        lock.upstream.target_sha if phase_name == phase.PREMERGE
        else lock.upstream.base_sha
    )
    target_ref = (
        args.target
        if phase_name == phase.PREMERGE
        else (args.target or lock.upstream.target_sha)
    )
    refs = {
        "upstream_base": args.base or default_base,
        "upstream_target": target_ref,
        "candidate": lock.candidate.commit_sha,
    }
    active_sources = [("active-candidate", lock.candidate.commit_sha)]
    active_sources.extend(_parse_active_sources(args.active_source))
    return preflight.run_preflight(
        str(args.repo),
        refs=refs,
        required_files=required_files,
        optional_inputs=optional_inputs,
        conflict_rate=getattr(args, "conflict_rate", ...),
        active_sources=active_sources,
        provenance=[
            (Path(item["lock_path"]).name, item["commit_sha"])
            for item in selection.provenance
        ],
    )


def _assert_transition_binding(args, selection, phase_name: str) -> None:
    """Reject CLI refs that contradict the approved Candidate lock."""
    lock = selection.lock
    if phase_name == phase.PREMERGE:
        if args.base is not None and args.base != lock.upstream.target_sha:
            raise PhaseCLIError(
                "premerge base must equal the active baseline's upstream target: "
                f"{args.base} != {lock.upstream.target_sha}"
            )
        return
    for label, supplied, locked in (
        ("base", args.base, lock.upstream.base_sha),
        ("target", args.target, lock.upstream.target_sha),
    ):
        if supplied is not None and supplied != locked:
            raise PhaseCLIError(
                f"postmerge {label} contradicts Candidate lock: {supplied} != {locked}"
            )


def _harness_version() -> str:
    harness = Path(__file__).resolve().parent
    files = [
        harness / "run_phase_bundle.py",
        harness / "om_workflow.py",
        harness / "registrations" / "kb-openmetadata" / "run_source_candidate_gates.py",
    ]
    files.extend(sorted((harness / "acgh").glob("*.py")))
    payload = {path.relative_to(harness).as_posix(): _sha256_file(path) for path in files}
    return verdict.canonical_digest(payload)


def _phase_inputs(
    args,
    selection,
    policy_files: dict[str, Path | None],
    *,
    specs=(),
) -> dict:
    lock = selection.lock
    return {
        "repositories": {
            "upstream": {
                "base_sha": args.base or lock.upstream.base_sha,
                "target_sha": args.target or lock.upstream.target_sha,
            },
            "candidate": {
                "commit_sha": lock.candidate.commit_sha,
                "tree_sha": lock.candidate.tree_sha,
            },
        },
        "candidate_lock_digest": selection.lock_digest,
        "candidate_artifact_kind": lock.candidate.artifact_kind,
        "verification_scope": (
            "source-impact"
            if getattr(args, "command", None) == "premerge"
            else (
                "artifact-verified"
                if getattr(args, "artifact_digest", None)
                else "source-only"
            )
        ),
        "harness_version": _harness_version(),
        "verifier_catalog_digest": phase.gate_catalog_digest(specs),
        "registration_digests": _registration_digests(args.registration),
        "policy_digests": {
            name: _sha256_file(path) for name, path in sorted(policy_files.items())
        },
        **(
            {"conflict_rate": args.conflict_rate}
            if hasattr(args, "conflict_rate") else {}
        ),
        **(
            {"conflict_measurement": args.conflict_measurement}
            if hasattr(args, "conflict_measurement") else {}
        ),
        **(
            {"runtime_artifact_digest": args.artifact_digest}
            if getattr(args, "artifact_digest", None) else {}
        ),
    }


def _command_gate(
    name: str,
    command: list[str],
    output: Path,
    collection_key: str,
    *,
    evidence_label: str | None = None,
):
    """Run an existing JSON gate command without reimplementing its judgment."""
    def run() -> phase.GateOutcome:
        if output.exists():
            raise phase.GateExecutionError(f"refusing stale/overwritten gate evidence: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        environment = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent)}
        completed = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parent.parent,
            env=environment,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        try:
            if output.is_file():
                payload = json.loads(output.read_text(encoding="utf-8"))
            else:
                payload = json.loads(completed.stdout)
                _atomic_json(output, payload)
        except (OSError, json.JSONDecodeError) as exc:
            raise phase.GateExecutionError(
                f"{name} did not produce valid JSON at {output}: {exc}; "
                f"stderr={completed.stderr[-1000:]}"
            ) from exc
        entries = payload.get(collection_key)
        if not isinstance(entries, list) or not entries:
            raise phase.GateExecutionError(f"{name} result missing non-empty {collection_key}")
        gate_results = []
        reasons: list[str] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise phase.GateExecutionError(f"{name} contains a non-mapping result")
            entry_name = entry.get("name")
            entry_verdict = entry.get("verdict")
            gate_results.append(entry_verdict)
            raw_reasons = entry.get("reasons", [])
            if isinstance(raw_reasons, list) and raw_reasons:
                reasons.extend(f"{entry_name}: {reason}" for reason in raw_reasons)
            elif entry.get("detail"):
                reasons.append(f"{entry_name}: {entry['detail']}")
        combined = verdict.aggregate(gate_results)
        expected_exit = verdict.to_exit_code(combined)
        if completed.returncode != expected_exit:
            raise phase.GateExecutionError(
                f"{name} JSON verdict={combined} expects exit {expected_exit}, "
                f"got {completed.returncode}; stderr={completed.stderr[-1000:]}"
            )
        judgment_detail = {collection_key: entries}
        for key in (
            "candidate_lock_digest", "reconstruction_plan_digest", "artifact_note",
        ):
            if key in payload:
                judgment_detail[key] = payload[key]
        return phase.GateOutcome(
            verdict.GateResult(name, combined, tuple(reasons)),
            target_count=len(entries),
            evidence=(evidence_label or output.name,),
            detail=judgment_detail,
        )

    return phase.GateSpec(name, run, required=True, timeout=310)


def _contract_gate(args, output_dir: Path):
    result_path = output_dir / "acgh-result.yaml"

    def run() -> phase.GateOutcome:
        if result_path.exists():
            raise phase.GateExecutionError(
                f"refusing stale/overwritten contract evidence: {result_path}"
            )
        command = [
            sys.executable, str(Path(__file__).resolve().parent / "run_runtime_contracts.py"),
            "--repo", str(args.repo),
            "--harness", str(Path(__file__).resolve().parent),
            "--registration", str(args.registration),
            "--artifact-digest", args.artifact_digest,
            "--output-dir", str(output_dir),
            "--run-id", args.run_id + "-contract",
        ]
        environment = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent)}
        completed = subprocess.run(
            command, cwd=Path(__file__).resolve().parent.parent, env=environment,
            capture_output=True, text=True, timeout=1800, check=False,
        )
        try:
            payload = yaml.safe_load(result_path.read_text(encoding="utf-8"))
            canonical = payload["canonical_payload"]
            combined = canonical["verdict"]
            gates = canonical["gates"]
        except (OSError, KeyError, TypeError, yaml.YAMLError) as exc:
            raise phase.GateExecutionError(
                f"contract did not produce a valid result: {exc}; stderr={completed.stderr[-1000:]}"
            ) from exc
        expected_exit = verdict.to_exit_code(combined)
        if completed.returncode != expected_exit:
            raise phase.GateExecutionError(
                f"contract JSON verdict={combined} expects exit {expected_exit}, "
                f"got {completed.returncode}"
            )
        reasons = tuple(
            f"{gate.get('name')}: {reason}"
            for gate in gates
            for reason in gate.get("reasons", [])
        )
        return phase.GateOutcome(
            verdict.GateResult("contract", combined, reasons),
            target_count=len(gates),
            evidence=("gates/contract/acgh-result.yaml",),
            detail={
                "canonical_payload": canonical,
                "result_digest": payload.get("result_digest"),
            },
        )

    return phase.GateSpec("contract", run, required=True, timeout=1810)


def _write_result(result, report, output: Path) -> int:
    enriched = phase.PhaseResult(
        phase=result.phase,
        executions=result.executions,
        overall_verdict=result.overall_verdict,
        phase_status=result.phase_status,
        exit_code=result.exit_code,
        inputs=result.inputs,
        run_id=result.run_id,
        observational={**result.observational, "preflight": report.to_json()},
    )
    system_json = enriched.to_system_json()
    rendered = rollup.render_all(system_json)
    problems = rollup.check_output_invariants(rendered)
    if problems:
        raise PhaseCLIError("three-tier output mismatch: " + "; ".join(problems))
    manager_output = output.with_name("manager-summary.json")
    practitioner_output = output.with_name("practitioner-detail.json")
    stale = [path for path in (manager_output, practitioner_output) if path.exists()]
    if stale:
        raise PhaseCLIError(
            "refusing stale/overwritten tier output: " + ", ".join(map(str, stale))
        )
    phase.write_phase_result(enriched, output)
    _atomic_json(manager_output, rendered["manager"])
    _atomic_json(practitioner_output, rendered["practitioner"])
    print(json.dumps({
        "phase": enriched.phase,
        "phase_status": enriched.phase_status,
        "overall_verdict": enriched.overall_verdict,
        "verification_scope": enriched.inputs.get("verification_scope"),
        "result_digest": enriched.result_digest(),
        "checked_over_total": rendered["manager"]["checked_over_total"],
        "counts": rendered["manager"]["counts"],
        "non_pass_gates": [
            {
                "name": gate["name"],
                "verdict": gate["verdict"],
                "execution_status": gate["execution_status"],
            }
            for gate in rendered["practitioner"]["gates"]
            if gate["verdict"] != verdict.PASS
            or gate["execution_status"] != phase.EXECUTED
        ],
        "output": str(output),
        "manager_output": str(manager_output),
        "practitioner_output": str(practitioner_output),
    }, ensure_ascii=False, sort_keys=True))
    return enriched.exit_code


def _blocked_phase_result(args, selection, report, phase_name: str, names, policy_files):
    """Persist an incomplete result without touching unavailable policy inputs."""
    advisory_names = phase.PREMERGE_ADVISORY if phase_name == phase.PREMERGE else frozenset()
    specs = [
        phase.GateSpec(
            name,
            lambda name=name: phase.GateOutcome(
                verdict.GateResult(name, verdict.ANALYSIS_ERROR)
            ),
            required=name not in advisory_names,
            advisory=name in advisory_names,
        )
        for name in names
    ]
    result = phase.run_gates(
        specs,
        phase=phase_name,
        preflight_blocked=True,
        inputs=_phase_inputs(args, selection, policy_files, specs=specs),
        run_id=args.run_id,
    )
    return _write_result(result, report, args.output)


# --- Candidate lock preparation / approval / activation ---------------------
# A Candidate lock decides *which* commit every later Phase judges, so the three
# steps stay separate on purpose: the tool may place and verify a lock, but only
# a human can approve it, and activation re-verifies rather than trusting the
# approval it was handed.
_RESERVED_LOCK_NAMES = frozenset({"active-candidate"})
_LOCK_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_APPROVAL_CONFIRMED = "approval_confirmed"
_VALUES_FROM_FLAGS = "cli-flags"
_VALUES_FROM_TEMPLATE = "template-empty"


def _validate_lock_name(name) -> str:
    """Reject any lock name that could escape or shadow a reserved file (C109)."""
    if not isinstance(name, str) or not name.strip():
        raise PhaseCLIError("lock 이름이 비어 있습니다")
    if name != name.strip():
        raise PhaseCLIError(f"lock 이름의 앞뒤 공백을 제거하세요: {name!r}")
    if "/" in name or "\\" in name or ".." in name or Path(name).is_absolute():
        raise PhaseCLIError(f"경로를 포함한 lock 이름은 사용할 수 없습니다: {name!r}")
    if not _LOCK_NAME_PATTERN.match(name):
        raise PhaseCLIError(
            "lock 이름은 영문·숫자로 시작하고 영문·숫자·점·밑줄·하이픈만 쓸 수 있습니다: "
            f"{name!r}"
        )
    if name.endswith((".yaml", ".yml")):
        raise PhaseCLIError(f"lock 이름에 확장자를 붙이지 마세요: {name!r}")
    if name.endswith(".approval"):
        raise PhaseCLIError(f"'.approval'로 끝나는 이름은 예약되어 있습니다: {name!r}")
    if name in _RESERVED_LOCK_NAMES:
        raise PhaseCLIError(f"예약된 이름입니다: {name!r}")
    return name


def _candidate_paths(registration: Path, name: str | None = None) -> dict[str, Path]:
    locks_dir = Path(registration) / "candidate-locks"
    paths = {"dir": locks_dir, "active": locks_dir / "active-candidate.yaml"}
    if name is not None:
        _validate_lock_name(name)
        paths["lock"] = locks_dir / f"{name}.yaml"
        paths["approval"] = locks_dir / f"{name}.approval.yaml"
        base = locks_dir.resolve()
        for key in ("lock", "approval"):
            if base not in paths[key].resolve().parents:
                raise PhaseCLIError(f"lock 경로가 등록 폴더를 벗어납니다: {paths[key]}")
    return paths


def _registry_source(registration: Path) -> dict:
    path = Path(registration) / "customization-registry.yaml"
    if not path.is_file():
        raise PhaseCLIError(f"등록 Registry가 없습니다: {path}")
    source = _load_mapping(path, "Registry").get("source")
    if not isinstance(source, dict):
        raise PhaseCLIError(f"Registry에 source 항목이 없습니다: {path}")
    return source


def _registration_binding(
    registration: Path, lock, *, allow_repository_mismatch: bool = False
) -> dict:
    """Bind a Candidate lock to the registration bundle that will host it.

    ``upstream_base`` must equal the bundle's official baseline: both a baseline
    lock (base == target == official) and a later upgrade candidate (base ==
    official, target == next official) satisfy it, while a lock built from a
    different baseline does not. That is a known-and-invalid state, so it blocks.

    A repository difference is reported instead of blocked: a fork can legitimately
    move (the 1.13.1 baseline was pushed to easyseop/OpenMetadata after the
    easyseop/OM_TEMP push failed) without changing what is judged. It still needs
    an explicit acknowledgement so it is never silent.
    """
    source = _registry_source(registration)
    registry_upstream = source.get("upstream_sha")
    if not isinstance(registry_upstream, str) or not registry_upstream:
        raise PhaseCLIError("Registry source.upstream_sha가 없습니다")
    if lock.upstream.base_sha != registry_upstream:
        raise CandidatePolicyBlock(
            "Candidate lock의 upstream base가 등록 묶음의 공식 기준 commit과 다릅니다: "
            f"{lock.upstream.base_sha} != {registry_upstream}. "
            "다른 등록 묶음(--version)의 lock인지 확인하세요."
        )
    registry_repository = source.get("repository")
    warnings: list[str] = []
    if registry_repository and registry_repository != lock.candidate.repository:
        message = (
            "Registry source.repository와 Candidate lock의 저장소가 다릅니다: "
            f"{registry_repository} != {lock.candidate.repository}"
        )
        if not allow_repository_mismatch:
            raise CandidatePolicyBlock(
                message
                + ". 저장소 이전이 의도된 것이면 --allow-repository-mismatch를 붙여 "
                "다시 실행하고, 아니면 Registry를 먼저 정정하세요."
            )
        warnings.append(message + " (담당자가 명시적으로 확인함)")
    return {
        "registry_upstream_sha": registry_upstream,
        "registry_repository": registry_repository,
        "lock_repository": lock.candidate.repository,
        "warnings": warnings,
    }


def _verify_source_result(lock, result_path: Path) -> dict:
    """Require the evidence that justifies this lock to name the same candidate."""
    data = _load_mapping(Path(result_path), "Candidate 근거 결과")
    canonical = data.get("canonical_payload")
    if not isinstance(canonical, dict):
        raise PhaseCLIError(f"근거 결과에 canonical_payload가 없습니다: {result_path}")
    result_verdict = canonical.get("verdict")
    if result_verdict != verdict.PASS:
        raise CandidatePolicyBlock(
            f"근거 결과의 canonical verdict가 pass가 아닙니다: {result_verdict!r}"
        )
    inputs = canonical.get("inputs")
    if not isinstance(inputs, dict):
        raise PhaseCLIError("근거 결과에 inputs가 없습니다")
    repositories = inputs.get("repositories")
    candidate_block = repositories.get("candidate") if isinstance(repositories, dict) else None
    if not isinstance(candidate_block, dict):
        raise PhaseCLIError("근거 결과 inputs.repositories.candidate가 없습니다")
    compared = {
        "candidate commit": (candidate_block.get("sha"), lock.candidate.commit_sha),
        "candidate tree": (candidate_block.get("tree_sha"), lock.candidate.tree_sha),
        "artifact digest": (inputs.get("artifact_digest"), lock.candidate.artifact_digest),
        "Candidate lock digest": (inputs.get("candidate_lock_digest"), lock.digest()),
    }
    if inputs.get("artifact_kind") is not None and lock.candidate.artifact_kind is not None:
        compared["artifact kind"] = (inputs["artifact_kind"], lock.candidate.artifact_kind)
    for label, (actual, expected) in compared.items():
        if actual != expected:
            raise CandidatePolicyBlock(
                f"근거 결과의 {label}가 Candidate lock과 다릅니다: {actual} != {expected}"
            )
    return {"result_digest": data.get("result_digest"), "verdict": result_verdict}


def _artifact_kind_notice(lock) -> str:
    """State the downstream consequence of the lock's artifact kind up front."""
    if lock.candidate.artifact_kind == candidate.BUILD_ARTIFACT:
        return (
            "build-artifact lock입니다. postmerge 실행에 --artifact-digest가 항상 필요하며 "
            "source-only 범위만으로는 실행할 수 없습니다."
        )
    return (
        "source-tree lock입니다. postmerge는 source-only 범위로 실행되며, Runtime Contract를 "
        "포함하려면 승인된 build-artifact lock이 따로 필요합니다."
    )


def _lock_blob(lock) -> bytes:
    return yaml.safe_dump(
        lock.canonical(), allow_unicode=True, sort_keys=True
    ).encode("utf-8")


def candidate_prepare_command(args) -> int:
    """Place a verified Candidate lock. Preparing is not approving."""
    source_lock = candidate.load_candidate_lock(args.source_lock)
    lock_digest = source_lock.digest()
    result_info = _verify_source_result(source_lock, args.source_result)
    binding = _registration_binding(
        args.registration,
        source_lock,
        allow_repository_mismatch=args.allow_repository_mismatch,
    )
    paths = _candidate_paths(args.registration, args.name)
    blob = _lock_blob(source_lock)

    notes = list(binding["warnings"])
    if paths["lock"].exists():
        existing = candidate.load_candidate_lock(paths["lock"])
        if existing.digest() != lock_digest:
            raise CandidatePolicyBlock(
                f"같은 이름의 다른 Candidate lock이 이미 있습니다: {paths['lock']} "
                f"(기존 {existing.digest()} != 준비할 {lock_digest}). 덮어쓰지 않습니다. "
                "다른 --name을 쓰거나, candidate-verify로 확인한 뒤 담당자가 정리하세요."
            )
        status = "already_prepared"
        if paths["lock"].read_bytes() != blob:
            notes.append(
                "기존 파일과 판정 내용(digest)은 같지만 YAML 표기가 다릅니다. "
                "판정에는 영향이 없어 그대로 두었습니다."
            )
    else:
        status = "prepared"
        _write_guarded(paths["lock"], blob, label="Candidate lock")

    payload = {
        "status": status,
        "lock_path": str(paths["lock"]),
        "candidate_commit_sha": source_lock.candidate.commit_sha,
        "candidate_tree_sha": source_lock.candidate.tree_sha,
        "candidate_artifact_kind": source_lock.candidate.artifact_kind,
        "candidate_artifact_digest": source_lock.candidate.artifact_digest,
        "candidate_lock_digest": lock_digest,
        "source_result_digest": result_info["result_digest"],
        "registration_binding": {
            k: v for k, v in binding.items() if k != "warnings"
        },
        "artifact_kind_notice": _artifact_kind_notice(source_lock),
        "approved": False,
        "notes": notes,
        "next_command": "candidate-approval-template",
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def candidate_approval_template_command(args) -> int:
    """Write the form a human fills in. This command never approves anything."""
    paths = _candidate_paths(args.registration, args.lock_name)
    if not paths["lock"].is_file():
        raise PhaseCLIError(
            f"먼저 candidate-prepare로 Candidate lock을 준비하세요: {paths['lock']}"
        )
    lock = candidate.load_candidate_lock(paths["lock"])

    supplied = {
        "approver": args.approver,
        "approved_at": args.approved_at,
        "rationale": args.rationale,
    }
    provided = {key: value for key, value in supplied.items() if value is not None}
    if provided and len(provided) != len(supplied):
        missing = sorted(set(supplied) - set(provided))
        print(json.dumps({
            "status": "input_required",
            "missing_fields": missing,
            "reason": "세 값을 모두 지정하거나, 모두 생략해 빈 양식을 만드세요.",
            "usage": (
                "candidate-approval-template --version <버전> --lock-name <이름> "
                "[--approver <표기> --approved-at <RFC3339> --rationale <사유>] "
                "--output <경로>"
            ),
        }, ensure_ascii=False, sort_keys=True))
        return 2

    template = {
        "candidate_lock_digest": lock.digest(),
        "approver": provided.get("approver", ""),
        "approved_at": provided.get("approved_at", ""),
        "rationale": provided.get("rationale", ""),
        # The template never writes True: an activatable approval always
        # requires an edit this command did not make.
        _APPROVAL_CONFIRMED: False,
        "provenance": {
            "generated_by": "candidate-approval-template",
            "generated_at": _now_rfc3339(),
            "values_source": _VALUES_FROM_FLAGS if provided else _VALUES_FROM_TEMPLATE,
            **_actor(),
        },
    }
    blob = yaml.safe_dump(template, allow_unicode=True, sort_keys=False)

    if str(args.output) == "-":
        # Pure YAML on stdout so the form can be piped or redirected as-is.
        print(blob, end="")
        return 0

    _write_guarded(Path(args.output), blob.encode("utf-8"), label="승인 양식")
    print(json.dumps({
        "status": "template_created",
        "output": str(args.output),
        "candidate_lock_digest": lock.digest(),
        "values_source": template["provenance"]["values_source"],
        "approved": False,
        "reason": (
            "승인 양식만 생성했습니다. 담당자가 내용을 검토하고 "
            f"{_APPROVAL_CONFIRMED}를 true로 바꾸기 전에는 활성화할 수 없습니다."
        ),
        "next_command": "candidate-activate",
    }, ensure_ascii=False, sort_keys=True))
    return 0


def _approval_block(reason: str, **extra) -> int:
    print(json.dumps(
        {"status": "blocked", "reason": reason, "activated": False, **extra},
        ensure_ascii=False, sort_keys=True,
    ))
    return verdict.EXIT_CODE[verdict.BLOCK]


def candidate_activate_command(args) -> int:
    """Verify a human-authored approval, then point the bundle at that lock."""
    paths = _candidate_paths(args.registration, args.lock_name)
    if not paths["lock"].is_file():
        raise PhaseCLIError(f"Candidate lock이 없습니다: {paths['lock']}")
    lock = candidate.load_candidate_lock(paths["lock"])
    lock_digest = lock.digest()
    binding = _registration_binding(
        args.registration, lock, allow_repository_mismatch=args.allow_repository_mismatch
    )

    approval_path = Path(args.approval)
    approval = _load_mapping(approval_path, "승인 파일")
    if approval.get("candidate_lock_digest") != lock_digest:
        return _approval_block(
            "승인 파일의 candidate_lock_digest가 실제 lock digest와 다릅니다: "
            f"{approval.get('candidate_lock_digest')} != {lock_digest}",
            candidate_lock_digest=lock_digest,
        )
    missing = list(approval_module.validate_approval_metadata(approval))
    if missing:
        return _approval_block(
            "승인 정보가 비어 있거나 형식이 맞지 않습니다: " + "; ".join(missing),
            candidate_lock_digest=lock_digest,
        )

    provenance = approval.get("provenance") if isinstance(approval.get("provenance"), dict) else {}
    if approval.get(_APPROVAL_CONFIRMED) is not True:
        if provenance.get("values_source") == _VALUES_FROM_FLAGS:
            reason = (
                "비대화형으로 생성한 승인 값만으로는 활성화할 수 없습니다. 담당자가 파일 내용을 "
                f"검토한 뒤 {_APPROVAL_CONFIRMED}를 true로 바꾸고 다시 실행하세요."
            )
        else:
            reason = (
                f"승인 파일의 {_APPROVAL_CONFIRMED}가 true가 아닙니다. 담당자가 직접 확인한 뒤 "
                "true로 바꾸세요."
            )
        return _approval_block(reason, candidate_lock_digest=lock_digest)

    previous_digest = None
    if paths["active"].is_file():
        previous_digest = _load_mapping(
            paths["active"], "활성 Candidate 포인터"
        ).get("candidate_lock_digest")
    replaced = False
    if previous_digest and previous_digest != lock_digest and not args.replace_active:
        return _approval_block(
            "다른 Candidate가 이미 활성 상태입니다: "
            f"현재 {previous_digest} != 활성화할 {lock_digest}. "
            "교체하려면 --replace-active를 붙이세요.",
            candidate_lock_digest=lock_digest,
            active_candidate_lock_digest=previous_digest,
        )
    replaced = bool(previous_digest and previous_digest != lock_digest)

    if paths["approval"].exists():
        if paths["approval"].read_bytes() != approval_path.read_bytes():
            raise CandidatePolicyBlock(
                f"다른 내용의 승인 파일이 이미 보관돼 있습니다: {paths['approval']}. "
                "덮어쓰지 않습니다. candidate-verify로 기존 승인을 확인한 뒤, "
                "교체가 필요하면 담당자가 기존 파일을 먼저 정리하세요."
            )
        approval_status = "already_stored"
    else:
        # Stored byte-for-byte: what git reviews must be what the approver wrote.
        _write_guarded(paths["approval"], approval_path.read_bytes(), label="승인 파일")
        approval_status = "stored"

    pointer = yaml.safe_dump(
        {"schema_version": 1, "candidate_lock_digest": lock_digest},
        allow_unicode=True, sort_keys=True,
    ).encode("utf-8")
    if previous_digest == lock_digest:
        pointer_status = "already_active"
    else:
        _write_guarded(
            paths["active"], pointer, label="활성 Candidate 포인터",
            allow_replace=bool(previous_digest),
        )
        pointer_status = "replaced" if replaced else "activated"

    selection = candidate_select.select_active_candidate(args.registration)
    if selection.status != candidate_select.SELECTED or selection.lock_digest != lock_digest:
        raise PhaseCLIError(
            "활성화 직후 self-check에 실패했습니다: "
            f"{selection.status}; " + "; ".join(selection.reasons)
        )

    record = {
        "status": "activated",
        "activated": True,
        "approval_status": approval_status,
        "pointer_status": pointer_status,
        "candidate_lock_digest": lock_digest,
        "candidate_commit_sha": lock.candidate.commit_sha,
        "candidate_artifact_kind": lock.candidate.artifact_kind,
        "previous_candidate_lock_digest": previous_digest,
        "lock_path": str(paths["lock"]),
        "approval_path": str(paths["approval"]),
        "active_pointer_path": str(paths["active"]),
        "approver": approval.get("approver"),
        "approved_at": approval.get("approved_at"),
        "approval_values_source": provenance.get("values_source"),
        "activated_at": _now_rfc3339(),
        **{f"activated_by_{k}": v for k, v in _actor().items()},
        "registration_binding": {k: v for k, v in binding.items() if k != "warnings"},
        "notes": list(binding["warnings"]),
        "authority_notice": (
            "이 도구는 승인 형식과 digest 결속만 검증합니다. 승인자의 실제 조직 권한은 "
            "보호 branch·CODEOWNERS 등 저장소 정책으로 확인해야 합니다."
        ),
        "next_command": "candidate-select",
    }
    if replaced:
        record["replacement_notice"] = (
            "활성 Candidate를 교체했습니다. 이전 Candidate로 만든 Phase 결과와 승인은 "
            "재사용할 수 없으며 해당 Phase를 처음부터 다시 실행해야 합니다."
        )
    if args.record is not None:
        _atomic_json(Path(args.record), record)
        record["record_path"] = str(args.record)
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0


def _approval_shape(approval: dict) -> dict:
    provenance = approval.get("provenance") if isinstance(approval.get("provenance"), dict) else {}
    return {
        "has_provenance": bool(provenance),
        "values_source": provenance.get("values_source"),
        "approval_confirmed": approval.get(_APPROVAL_CONFIRMED),
        "cli_generated": provenance.get("generated_by") == "candidate-approval-template",
    }


def candidate_verify_command(args) -> int:
    """Read-only: report whether placed files match what the CLI would produce.

    Hand-made locks predate these commands, so this reports rather than rewrites:
    a bundle whose files already bind the right candidate can simply be committed,
    and only a real difference needs an operator decision.
    """
    paths = _candidate_paths(args.registration)
    report = {
        "registration_path": str(args.registration),
        "candidate_locks_dir": str(paths["dir"]),
        "locks": [],
        "active_candidate_lock_digest": None,
        "problems": [],
        "notes": [],
    }
    if not paths["dir"].is_dir():
        report["problems"].append(f"candidate-locks 폴더가 없습니다: {paths['dir']}")
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return verdict.EXIT_CODE[verdict.ANALYSIS_ERROR]

    if paths["active"].is_file():
        report["active_candidate_lock_digest"] = _load_mapping(
            paths["active"], "활성 Candidate 포인터"
        ).get("candidate_lock_digest")
    else:
        report["problems"].append(f"활성 포인터가 없습니다: {paths['active']}")

    expected_digest = None
    if args.source_lock is not None:
        expected_digest = candidate.load_candidate_lock(args.source_lock).digest()
        report["source_lock_digest"] = expected_digest

    for lock_path in sorted(paths["dir"].glob("*.yaml")):
        if lock_path.name == "active-candidate.yaml" or lock_path.name.endswith(
            ".approval.yaml"
        ):
            continue
        entry = {"lock_path": str(lock_path), "name": lock_path.stem}
        try:
            lock = candidate.load_candidate_lock(lock_path)
        except Exception as exc:  # noqa: BLE001 - a corrupt lock is a finding, not a crash
            entry["error"] = f"{type(exc).__name__}: {exc}"
            report["problems"].append(f"{lock_path.name}: 읽을 수 없습니다: {exc}")
            report["locks"].append(entry)
            continue
        digest = lock.digest()
        entry.update({
            "candidate_lock_digest": digest,
            "candidate_commit_sha": lock.candidate.commit_sha,
            "candidate_artifact_kind": lock.candidate.artifact_kind,
            "is_active": digest == report["active_candidate_lock_digest"],
            "matches_cli_output": lock_path.read_bytes() == _lock_blob(lock),
        })
        if expected_digest is not None:
            entry["matches_source_lock"] = digest == expected_digest
        try:
            binding = _registration_binding(
                args.registration, lock, allow_repository_mismatch=True
            )
            entry["registration_binding"] = {
                k: v for k, v in binding.items() if k != "warnings"
            }
            entry["registration_warnings"] = binding["warnings"]
        except PhaseCLIError as exc:
            entry["registration_binding_error"] = str(exc)
            report["problems"].append(f"{lock_path.name}: {exc}")

        approval_path = lock_path.with_name(lock_path.stem + ".approval.yaml")
        entry["approval_path"] = str(approval_path)
        if not approval_path.is_file():
            entry["approval"] = None
            if entry["is_active"]:
                report["problems"].append(
                    f"{lock_path.name}: 활성 상태인데 승인 파일이 없습니다"
                )
        else:
            approval = _load_mapping(approval_path, "승인 파일")
            shape = _approval_shape(approval)
            shape["digest_matches"] = approval.get("candidate_lock_digest") == digest
            shape["metadata_problems"] = list(
                approval_module.validate_approval_metadata(approval)
            )
            entry["approval"] = shape
            if not shape["digest_matches"]:
                report["problems"].append(f"{approval_path.name}: lock digest와 다릅니다")
            if shape["metadata_problems"]:
                report["problems"].append(
                    f"{approval_path.name}: " + "; ".join(shape["metadata_problems"])
                )
            if not shape["has_provenance"]:
                report["notes"].append(
                    f"{approval_path.name}: CLI 이전에 수동으로 만든 승인 파일입니다. "
                    "판정 내용이 맞으면 그대로 commit해 정식화할 수 있고, "
                    "다시 만들려면 담당자가 기존 파일을 먼저 정리해야 합니다."
                )
            elif shape["approval_confirmed"] is not True:
                report["notes"].append(
                    f"{approval_path.name}: {_APPROVAL_CONFIRMED}가 true가 아니라 "
                    "candidate-activate로는 활성화할 수 없습니다."
                )
        report["locks"].append(entry)

    if not report["locks"]:
        report["problems"].append("Candidate lock 파일이 없습니다")

    selection = candidate_select.select_active_candidate(args.registration)
    report["selection_status"] = selection.status
    report["selection_reasons"] = list(selection.reasons)
    selectable = selection.status == candidate_select.SELECTED
    report["selectable"] = selectable
    if not selectable:
        report["problems"].extend(selection.reasons)

    if selectable and not report["problems"]:
        report["status"] = "consistent"
        exit_code = 0
    elif selectable:
        report["status"] = "blocked"
        exit_code = verdict.EXIT_CODE[verdict.BLOCK]
    else:
        report["status"] = "analysis_error"
        exit_code = verdict.EXIT_CODE[verdict.ANALYSIS_ERROR]
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return exit_code


def watch_suggest_command(args) -> int:
    """Run only the advisory watch-suggest gate, without touching Phase evidence.

    The practitioner detail used to say "재실행하세요" with no command behind it.
    This writes its own result file, so rerunning one advisory check never
    overwrites a premerge result that other gates already produced.
    """
    from acgh import watch_suggest

    selection = _selected(args.registration)
    layout = layout_module.load_layout(args.registration / "repository-layout.yaml")
    manifests = _load_manifests(args.registration, layout)
    candidate_ref = args.candidate_ref or selection.lock.candidate.commit_sha
    report = watch_suggest.analyze(
        str(args.repo), args.base, args.target, candidate_ref, manifests,
        timeout_seconds=(
            phase.validated_timeout(args.timeout) if args.timeout is not None else None
        ),
        cache_dir=args.cache_dir,
        harness_version=_harness_version(),
    )
    packet = report.packet()
    payload = {
        "status": "complete" if report.complete else "incomplete",
        "complete": report.complete,
        "stage": report.stage,
        "verdict": verdict.PASS if report.complete else verdict.ANALYSIS_ERROR,
        "candidate_lock_digest": selection.lock_digest,
        "candidate_ref": candidate_ref,
        "packet": packet,
        # Observational only: never part of a canonical judgment payload.
        "telemetry": report.telemetry,
    }
    if not report.complete:
        payload["rerun_command"] = (
            "harness/om_workflow.py watch-suggest --version <버전> --repo <제품저장소> "
            f"--base {args.base} --target {args.target} --timeout <초>"
        )
    if args.output is not None:
        _write_guarded(
            Path(args.output),
            (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(),
            label="watch-suggest 결과",
        )
        payload["output"] = str(args.output)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if report.complete else verdict.EXIT_CODE[verdict.ANALYSIS_ERROR]


def candidate_command(args) -> int:
    selection = candidate_select.select_active_candidate(args.registration)
    payload = {
        **_selection_payload(selection),
        "registration_bundle": args.registration.name,
        "registration_path": str(args.registration),
    }
    _atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    if selection.status == candidate_select.SELECTED:
        return 0
    return 1 if selection.status == candidate_select.BLOCKED else 3


def prep_official_command(args) -> int:
    prepared = phase.prepare_official_branch(str(args.repo), args.tag_ref, args.branch)
    payload = {
        "status": "created" if prepared.created else "already_correct",
        "tag_ref": args.tag_ref,
        "branch": prepared.branch,
        "commit_sha": prepared.commit_sha,
        "tree_sha": prepared.tree_sha,
    }
    _atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def preflight_command(args) -> int:
    selection = _selected(args.registration)
    _assert_transition_binding(args, selection, args.phase)
    required = {
        "repository_layout": args.registration / "repository-layout.yaml",
        "sensitive_zones": args.registration / "sensitive-zones.yaml",
    }
    optional = {}
    official_binding_error = None
    if args.phase == phase.PREMERGE:
        required["official_evidence"] = args.official_evidence
        if args.target is not None and args.official_evidence is not None:
            try:
                _bind_official_evidence(args)
            except PhaseCLIError as exc:
                official_binding_error = str(exc)
    if args.phase == phase.POSTMERGE:
        _bind_conflict_evidence(args, selection.lock)
        required["debt_thresholds"] = args.debt_policy
        optional["change_intent"] = {
            "path": args.change_intent,
            "required_for": ["sensitive-zones"],
        }
    report = _preflight(
        args, selection, phase_name=args.phase,
        required_files=required, optional_inputs=optional,
    )
    if official_binding_error:
        report = preflight.PreflightReport(report.checks + (
            preflight.Check(
                "official_binding",
                preflight.INVALID,
                blocking=True,
                detail=official_binding_error,
                next_action="prep-official 결과와 --target 전체 SHA를 다시 확인하세요.",
            ),
        ))
    _atomic_json(args.output, report.to_json())
    print(json.dumps(report.to_json(), ensure_ascii=False, sort_keys=True))
    return 0 if report.ready else 3


def premerge_command(args) -> int:
    selection = _selected(args.registration)
    _assert_transition_binding(args, selection, phase.PREMERGE)
    _bind_official_evidence(args)
    layout_path = args.registration / "repository-layout.yaml"
    zones_path = args.registration / "sensitive-zones.yaml"
    report = _preflight(
        args, selection, phase_name=phase.PREMERGE,
        required_files={"repository_layout": layout_path, "sensitive_zones": zones_path},
    )
    if not report.ready:
        return _blocked_phase_result(
            args, selection, report, phase.PREMERGE,
            ("upgrade-watch", "policy-drift", "structdiff", "watch-suggest"),
            {
                "repository_layout": layout_path,
                "sensitive_zones": zones_path,
                "official_evidence": args.official_evidence,
            },
        )
    layout = layout_module.load_layout(layout_path)
    manifests = _load_manifests(args.registration, layout)
    specs = phase.build_premerge_catalog(
        str(args.repo), args.base, args.target, manifests,
        layout=layout, candidate_ref=args.candidate_ref or selection.lock.candidate.commit_sha,
        gate_timeout=getattr(args, "gate_timeout", None),
        watch_suggest_cache_dir=getattr(args, "watch_suggest_cache", None),
        harness_version=_harness_version(),
    )
    result = phase.run_gates(
        specs,
        phase=phase.PREMERGE,
        preflight_blocked=not report.ready,
        inputs=_phase_inputs(
            args, selection,
            {
                "repository_layout": layout_path,
                "sensitive_zones": zones_path,
                "official_evidence": args.official_evidence,
            },
            specs=specs,
        ),
        run_id=args.run_id,
    )
    return _write_result(result, report, args.output)


def postmerge_command(args) -> int:
    selection = _selected(args.registration)
    _assert_transition_binding(args, selection, phase.POSTMERGE)
    lock = selection.lock
    _bind_conflict_evidence(args, lock)
    layout_path = args.registration / "repository-layout.yaml"
    zones_path = args.registration / "sensitive-zones.yaml"
    optional = {
        "change_intent": {"path": args.change_intent, "required_for": ["sensitive-zones"]},
    }
    report = _preflight(
        args, selection, phase_name=phase.POSTMERGE,
        required_files={
            "repository_layout": layout_path,
            "sensitive_zones": zones_path,
            "debt_thresholds": args.debt_policy,
        },
        optional_inputs=optional,
    )
    policy_files = {
        "repository_layout": layout_path,
        "sensitive_zones": zones_path,
        "change_intent": args.change_intent,
        "debt_thresholds": args.debt_policy,
        "conflict_evidence": args.conflict_evidence,
    }
    if not report.ready:
        names = [
            "vendor-ancestry", "sensitive-zones", "debt", "exact-scope-history",
            "validate", "source",
        ]
        if args.artifact_digest:
            names.append("contract")
        return _blocked_phase_result(
            args, selection, report, phase.POSTMERGE, names, policy_files,
        )
    if args.artifact_digest and lock.candidate.artifact_kind != candidate.BUILD_ARTIFACT:
        raise PhaseCLIError(
            "Runtime Contract를 포함한 postmerge에는 승인된 build-artifact Candidate lock이 "
            "필요합니다. source-tree lock에 --artifact-digest를 임의로 결합할 수 없습니다."
        )
    candidate.assert_candidate_binding(
        str(args.repo), lock, artifact_digest=args.artifact_digest
    )
    phase.validate_postmerge_candidate(str(args.repo), lock)
    layout = layout_module.load_layout(layout_path)
    manifests = _load_manifests(args.registration, layout)
    zones = zones_module.load_zones(zones_path)
    thresholds = debt.load_thresholds(args.debt_policy) if args.debt_policy.is_file() else None
    specs = phase.build_postmerge_catalog(
        str(args.repo), lock, manifests,
        zones=zones,
        change_intent_path=str(args.change_intent) if args.change_intent else None,
        thresholds=thresholds,
        conflict_rate=args.conflict_rate,
        upstream_base=args.base,
        upstream_target=args.target,
    )
    gate_dir = args.output.parent / "gates"
    validator = args.registration / "validate_registration_bundle.py"
    if not validator.is_file():
        validator = (
            Path(__file__).resolve().parent / "registrations" / "om-temp-1.13.0"
            / "validate_registration_bundle.py"
        )
    validation_output = gate_dir / "registration-validation-results.json"
    specs.append(_command_gate(
        "validate",
        [
            sys.executable, str(validator),
            "--repo", str(args.repo),
            "--registration", str(args.registration),
            "--layout", str(layout_path),
            "--output", str(validation_output),
        ],
        validation_output,
        "checks",
        evidence_label="gates/registration-validation-results.json",
    ))
    source_output = gate_dir / "source-gate-results.json"
    specs.append(_command_gate(
        "source",
        [
            sys.executable, str(Path(__file__).resolve().parent / "run_source_candidate_gates.py"),
            "--repo", str(args.repo),
            "--harness", str(Path(__file__).resolve().parent),
            "--registration", str(args.registration),
            "--layout", str(layout_path),
            "--sensitive-zones", str(zones_path),
            "--output", str(source_output),
        ],
        source_output,
        "gates",
        evidence_label="gates/source-gate-results.json",
    ))
    if args.artifact_digest:
        specs.append(_contract_gate(args, args.contract_output_dir or gate_dir / "contract"))
    result = phase.run_gates(
        specs,
        phase=phase.POSTMERGE,
        preflight_blocked=not report.ready,
        inputs=_phase_inputs(
            args, selection,
            policy_files,
            specs=specs,
        ),
        run_id=args.run_id,
    )
    return _write_result(result, report, args.output)


def status_command(args) -> int:
    ok, reason = phase.verify_phase_result(args.result)
    canonical_verified = ok
    data = json.loads(args.result.read_text(encoding="utf-8")) if ok else {}
    tier_status = {"manager": False, "practitioner": False}
    if ok:
        expected = rollup.render_all(data["system_json"])
        for name, filename in (
            ("manager", "manager-summary.json"),
            ("practitioner", "practitioner-detail.json"),
        ):
            path = args.result.with_name(filename)
            try:
                actual = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                ok = False
                reason = f"{filename} unreadable/corrupt: {exc}"
                break
            if actual != expected[name]:
                ok = False
                reason = (
                    f"{filename} disagrees with canonical result. 구버전 형식의 "
                    "증거라면 최신 검사기로 해당 Phase를 다시 실행하세요."
                )
                break
            tier_status[name] = True
    payload = {
        "verified": ok,
        "canonical_verified": canonical_verified,
        "reason": reason,
        "phase": data.get("canonical_payload", {}).get("phase"),
        "phase_status": data.get("canonical_payload", {}).get("phase_status"),
        "overall_verdict": data.get("canonical_payload", {}).get("overall_verdict"),
        "verification_scope": (
            data.get("canonical_payload", {}).get("inputs", {}).get("verification_scope")
        ),
        "result_digest": data.get("result_digest"),
        "tier_outputs": tier_status,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if ok else 3


def _common(
    parser: argparse.ArgumentParser,
    *,
    base_required: bool = False,
    target_required: bool = False,
) -> None:
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--registration", required=True, type=Path)
    parser.add_argument("--base", required=base_required)
    parser.add_argument("--target", required=target_required)
    parser.add_argument("--active-source", action="append", default=[])


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="OpenMetadata phase bundle runner")
    sub = parser.add_subparsers(dest="command", required=True)

    candidate_parser = sub.add_parser("candidate")
    candidate_parser.add_argument("--registration", required=True, type=Path)
    candidate_parser.add_argument("--output", required=True, type=Path)

    prepare_parser = sub.add_parser("candidate-prepare")
    prepare_parser.add_argument("--registration", required=True, type=Path)
    prepare_parser.add_argument("--source-lock", required=True, type=Path)
    prepare_parser.add_argument("--source-result", required=True, type=Path)
    prepare_parser.add_argument("--name", required=True)
    prepare_parser.add_argument("--allow-repository-mismatch", action="store_true")

    template_parser = sub.add_parser("candidate-approval-template")
    template_parser.add_argument("--registration", required=True, type=Path)
    template_parser.add_argument("--lock-name", required=True)
    template_parser.add_argument("--approver")
    template_parser.add_argument("--approved-at")
    template_parser.add_argument("--rationale")
    template_parser.add_argument("--output", required=True)

    activate_parser = sub.add_parser("candidate-activate")
    activate_parser.add_argument("--registration", required=True, type=Path)
    activate_parser.add_argument("--lock-name", required=True)
    activate_parser.add_argument("--approval", required=True, type=Path)
    activate_parser.add_argument("--replace-active", action="store_true")
    activate_parser.add_argument("--allow-repository-mismatch", action="store_true")
    activate_parser.add_argument("--record", type=Path)

    verify_parser = sub.add_parser("candidate-verify")
    verify_parser.add_argument("--registration", required=True, type=Path)
    verify_parser.add_argument("--source-lock", type=Path)

    prep_parser = sub.add_parser("prep-official")
    prep_parser.add_argument("--repo", required=True, type=Path)
    prep_parser.add_argument("--tag-ref", required=True)
    prep_parser.add_argument("--branch", required=True)
    prep_parser.add_argument("--output", required=True, type=Path)

    collect_parser = sub.add_parser("collect-conflict-evidence")
    collect_parser.add_argument("--repo", required=True, type=Path)
    collect_parser.add_argument("--registration", required=True, type=Path)
    collect_parser.add_argument("--baseline-lock-digest", required=True)
    collect_parser.add_argument("--custom-head", required=True)
    collect_parser.add_argument("--output", required=True, type=Path)

    preflight_parser = sub.add_parser("preflight")
    _common(preflight_parser)
    preflight_parser.add_argument("--phase", required=True, choices=[phase.PREMERGE, phase.POSTMERGE])
    preflight_parser.add_argument("--change-intent", type=Path)
    preflight_parser.add_argument("--debt-policy", type=Path)
    preflight_parser.add_argument("--conflict-rate", type=float, default=...)
    preflight_parser.add_argument("--conflict-evidence", type=Path)
    preflight_parser.add_argument("--official-evidence", type=Path)
    preflight_parser.add_argument("--output", required=True, type=Path)

    premerge_parser = sub.add_parser("premerge")
    _common(premerge_parser, base_required=True)
    premerge_parser.add_argument("--candidate-ref")
    premerge_parser.add_argument("--official-evidence", required=True, type=Path)
    premerge_parser.add_argument("--gate-timeout", type=float)
    premerge_parser.add_argument("--watch-suggest-cache", type=Path)
    premerge_parser.add_argument("--run-id", required=True)
    premerge_parser.add_argument("--output", required=True, type=Path)

    watch_parser = sub.add_parser("watch-suggest")
    watch_parser.add_argument("--repo", required=True, type=Path)
    watch_parser.add_argument("--registration", required=True, type=Path)
    watch_parser.add_argument("--base", required=True)
    watch_parser.add_argument("--target", required=True)
    watch_parser.add_argument("--candidate-ref")
    watch_parser.add_argument("--timeout", type=float)
    watch_parser.add_argument("--cache-dir", type=Path)
    watch_parser.add_argument("--output", type=Path)

    postmerge_parser = sub.add_parser("postmerge")
    _common(postmerge_parser)
    postmerge_parser.add_argument("--change-intent", type=Path)
    postmerge_parser.add_argument("--debt-policy", required=True, type=Path)
    postmerge_parser.add_argument("--conflict-rate", type=float)
    postmerge_parser.add_argument("--conflict-evidence", type=Path)
    postmerge_parser.add_argument("--artifact-digest")
    postmerge_parser.add_argument("--contract-output-dir", type=Path)
    postmerge_parser.add_argument("--run-id", required=True)
    postmerge_parser.add_argument("--output", required=True, type=Path)

    status_parser = sub.add_parser("status")
    status_parser.add_argument("--result", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv=None) -> int:
    try:
        args = parse_args(argv)
        if args.command in {"premerge", "postmerge"}:
            phase.evidence_path(Path.cwd(), args.run_id)
        return {
            "candidate": candidate_command,
            "candidate-prepare": candidate_prepare_command,
            "candidate-approval-template": candidate_approval_template_command,
            "candidate-activate": candidate_activate_command,
            "candidate-verify": candidate_verify_command,
            "prep-official": prep_official_command,
            "watch-suggest": watch_suggest_command,
            "collect-conflict-evidence": collect_conflict_evidence_command,
            "preflight": preflight_command,
            "premerge": premerge_command,
            "postmerge": postmerge_command,
            "status": status_command,
        }[args.command](args)
    except CandidatePolicyBlock as exc:
        # Known-and-invalid, not "could not analyze": report as block (exit 1).
        print(json.dumps({"status": "block", "reason": str(exc)}, ensure_ascii=False))
        return verdict.EXIT_CODE[verdict.BLOCK]
    except (
        PhaseCLIError, phase.PhaseError, candidate.CandidateLockError,
        gitprim.GitPrimitiveError, OSError, ValueError,
    ) as exc:
        print(json.dumps({"status": "analysis_error", "reason": str(exc)}, ensure_ascii=False))
        return verdict.EXIT_CODE[verdict.ANALYSIS_ERROR]


if __name__ == "__main__":
    raise SystemExit(main())
