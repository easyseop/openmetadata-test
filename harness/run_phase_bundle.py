#!/usr/bin/env python3
"""Execute candidate selection, preflight, and phase bundles as real CLI steps."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import yaml

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


def _atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp.write_text(blob, encoding="utf-8")
    os.replace(tmp, path)


def _write_conflict_evidence(path: Path, payload: dict, validate) -> None:
    """Write one collector artifact without clobbering or exposing partial data."""
    import datetime
    import socket

    path.parent.mkdir(parents=True, exist_ok=True)
    reservation = path.with_name(f".{path.name}.lock")
    try:
        reservation_fd = os.open(
            str(reservation), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644
        )
    except FileExistsError as exc:
        raise PhaseCLIError(
            f"다른 수집 작업이 증거 경로를 사용 중입니다: {path}; lock={reservation}"
        ) from exc
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    try:
        metadata = json.dumps({
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "output": str(path),
        }, ensure_ascii=False, sort_keys=True).encode("utf-8")
        os.write(reservation_fd, metadata)
        os.fsync(reservation_fd)
        if path.exists():
            raise PhaseCLIError(f"기존 conflict evidence를 덮어쓰지 않습니다: {path}")
        blob = yaml.safe_dump(payload, allow_unicode=True, sort_keys=True).encode("utf-8")
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            os.write(fd, blob)
            os.fsync(fd)
        finally:
            os.close(fd)
        validate(tmp)
        os.replace(str(tmp), str(path))
    finally:
        tmp.unlink(missing_ok=True)
        os.close(reservation_fd)
        reservation.unlink(missing_ok=True)


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
    premerge_parser.add_argument("--run-id", required=True)
    premerge_parser.add_argument("--output", required=True, type=Path)

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
            "prep-official": prep_official_command,
            "collect-conflict-evidence": collect_conflict_evidence_command,
            "preflight": preflight_command,
            "premerge": premerge_command,
            "postmerge": postmerge_command,
            "status": status_command,
        }[args.command](args)
    except (
        PhaseCLIError, phase.PhaseError, candidate.CandidateLockError,
        gitprim.GitPrimitiveError, OSError, ValueError,
    ) as exc:
        print(json.dumps({"status": "analysis_error", "reason": str(exc)}, ensure_ascii=False))
        return verdict.EXIT_CODE[verdict.ANALYSIS_ERROR]


if __name__ == "__main__":
    raise SystemExit(main())
