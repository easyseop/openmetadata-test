"""T27 — structured vendor-merge conflict resolution evidence.

The conflict set is captured from Git's unmerged index before resolution. The
final evidence binds every captured path, its base/ours/theirs blob identities,
the chosen resolution, the resolved candidate blob, rationale, resolver, and
separate approval ids to the immutable candidate lock.

The machine gate never treats a resolver's prose as proof. Missing records or a
resolved blob that does not match the candidate are ``block``; a stale lock or
malformed evidence is ``analysis_error``; complete records without an approval
remain ``approval``; fully approved evidence is ``pass``.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import jsonschema

from acgh import candidate as C
from acgh import gitprim
from acgh import layout as L
from acgh import verdict

_SCHEMA_PATH = (
    Path(__file__).parent / "schema" / "merge-conflict-evidence.schema.json"
)


class ConflictEvidenceError(ValueError):
    """Conflict evidence is malformed or cannot be bound to the candidate."""


@dataclass(frozen=True)
class CapturedConflict:
    path: str
    base_blob_sha: str | None
    ours_blob_sha: str | None
    theirs_blob_sha: str | None


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def capture_unmerged(repo: str) -> list[CapturedConflict]:
    """Capture Git index stages 1/2/3 for every currently conflicted path."""
    proc = subprocess.run(
        ["git", "-C", repo, *gitprim._STABLE_CONFIG, "ls-files", "-u", "-z"],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise ConflictEvidenceError(
            f"git ls-files -u failed: {proc.stderr.strip() or proc.returncode}"
        )

    staged: dict[str, dict[int, str]] = {}
    for record in (item for item in proc.stdout.split("\x00") if item):
        try:
            metadata, raw_path = record.split("\t", 1)
            _mode, blob_sha, stage_text = metadata.split()
            stage = int(stage_text)
            path = L.normalize_path(raw_path)
        except (ValueError, L.LayoutError) as exc:
            raise ConflictEvidenceError(
                f"cannot parse unmerged index record: {record!r}"
            ) from exc
        staged.setdefault(path, {})[stage] = blob_sha

    return [
        CapturedConflict(
            path=path,
            base_blob_sha=stages.get(1),
            ours_blob_sha=stages.get(2),
            theirs_blob_sha=stages.get(3),
        )
        for path, stages in sorted(staged.items())
    ]


def _candidate_blob(repo: str, candidate_sha: str, path: str) -> str | None:
    out = gitprim.git(repo, "ls-tree", candidate_sha, "--", path)
    if not out.strip():
        return None
    metadata, listed_path = out.rstrip("\n").split("\t", 1)
    if listed_path != path:
        raise ConflictEvidenceError(
            f"candidate tree returned unexpected path {listed_path!r}"
        )
    _mode, object_type, blob_sha = metadata.split()
    if object_type != "blob":
        raise ConflictEvidenceError(
            f"candidate object for {path!r} is {object_type}, not blob"
        )
    return blob_sha


def build_conflict_evidence(
    repo: str,
    lock: C.CandidateLock,
    *,
    merge_base_sha: str,
    captured: list[CapturedConflict],
    decisions: dict[str, dict],
) -> dict:
    """Finalize captured conflicts against the exact candidate tree."""
    if lock.integration_strategy != C.VENDOR_MERGE:
        raise ConflictEvidenceError(
            "merge-conflict evidence requires vendor-merge strategy"
        )
    try:
        C.assert_candidate_binding(repo, lock)
    except C.CandidateLockError as exc:
        raise ConflictEvidenceError(str(exc)) from exc

    captured_paths = {item.path for item in captured}
    if len(captured_paths) != len(captured):
        raise ConflictEvidenceError("captured conflict paths are not unique")
    extra = sorted(set(decisions) - captured_paths)
    if extra:
        raise ConflictEvidenceError(
            f"decisions contain paths not captured as conflicts: {extra}"
        )

    records = []
    for item in captured:
        decision = decisions.get(item.path)
        if decision is None:
            raise ConflictEvidenceError(
                f"missing resolution decision for {item.path}"
            )
        resolution = decision.get("resolution")
        resolved_blob = _candidate_blob(
            repo, lock.candidate.commit_sha, item.path
        )
        if resolution == "deleted":
            if resolved_blob is not None:
                raise ConflictEvidenceError(
                    f"{item.path}: resolution says deleted but candidate has blob"
                )
        elif resolved_blob is None:
            raise ConflictEvidenceError(
                f"{item.path}: resolved path is absent from candidate"
            )

        records.append(
            {
                "path": item.path,
                "base_blob_sha": item.base_blob_sha,
                "ours_blob_sha": item.ours_blob_sha,
                "theirs_blob_sha": item.theirs_blob_sha,
                "resolution": resolution,
                "resolution_blob_sha": resolved_blob,
                "rationale": decision.get("rationale", ""),
                "resolved_by": decision.get("resolved_by", ""),
                "approval_ids": list(decision.get("approval_ids", [])),
            }
        )

    evidence = {
        "schema_version": 1,
        "candidate_lock_digest": lock.digest(),
        "candidate_sha": lock.candidate.commit_sha,
        "upstream_target_sha": lock.upstream.target_sha,
        "merge_base_sha": merge_base_sha,
        "captured_conflict_count": len(captured),
        "conflicts": records,
    }
    validate_conflict_evidence(evidence)
    return evidence


def validate_conflict_evidence(evidence: dict) -> dict:
    errs = sorted(
        _schema_validator().iter_errors(evidence),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errs:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise ConflictEvidenceError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errs)
        )
    paths = [item["path"] for item in evidence["conflicts"]]
    if len(paths) != len(set(paths)):
        raise ConflictEvidenceError("conflict paths are not unique")
    return evidence


def check_conflict_evidence(
    evidence: dict,
    *,
    expected_candidate_lock_digest: str,
    name: str = "merge-conflict-evidence",
) -> verdict.GateResult:
    """Validate T27 evidence and surface missing approval separately."""
    try:
        validate_conflict_evidence(evidence)
    except ConflictEvidenceError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"analysis_error: {exc}",)
        )
    if evidence["candidate_lock_digest"] != expected_candidate_lock_digest:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            ("analysis_error: conflict evidence is stale for candidate lock",),
        )
    if evidence["captured_conflict_count"] != len(evidence["conflicts"]):
        return verdict.GateResult(
            name,
            verdict.BLOCK,
            (
                "captured conflict count does not match resolution record count",
            ),
        )

    unapproved = [
        item["path"] for item in evidence["conflicts"]
        if not item["approval_ids"]
    ]
    if unapproved:
        return verdict.GateResult(
            name,
            verdict.APPROVAL,
            tuple(f"resolution approval required: {path}" for path in unapproved),
        )

    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"conflicts={len(evidence['conflicts'])}",
            f"candidate={evidence['candidate_sha']}",
        ),
    )
