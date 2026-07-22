"""T15 — result writer + CI adapter (SRS 부칙 A-1).

Closes the result contract at the CI boundary. Two halves:

WRITE (부칙 A-1.2) — ``write_result`` persists an acgh-result atomically:
serialize to a temp file in the same directory, schema-validate, self-verify
that ``result_digest`` recomputes from ``canonical_payload``, fsync, then
``os.replace`` into place. A reader can therefore never observe a half-written
or internally inconsistent result.

INTERPRET (부칙 A-1.1/A-1.6) — ``interpret_result`` is what the CI wrapper runs
AFTER capturing the harness's actual exit code (never short-circuited by
``set -e``). It trusts neither the exit code nor the file blindly: a missing,
corrupt, schema-invalid, digest-mismatched, stale (inputs != current
candidate/policy), or exit-disagreeing result all collapse to a synthetic
``analysis_error`` — the fail-closed decision (P0-4).

ATTESTATION (부칙 A-1.4) — human approvals live in SEPARATE artifacts and are
bound to a specific result digest + candidate SHA + policy digest, so any
change to candidate or policy auto-invalidates them.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "acgh-result.schema.json"


class ResultIOError(ValueError):
    """Raised on write-time (producer) errors — never on interpret."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def _schema_errors(data: dict) -> list[str]:
    errs = sorted(
        _schema_validator().iter_errors(data),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    loc = lambda e: "/".join(str(p) for p in e.absolute_path) or "<root>"
    return [f"{loc(e)}: {e.message}" for e in errs]


# --- write -----------------------------------------------------------------
def write_result(result: dict, out_path) -> str:
    """Validate, self-verify, and atomically write ``result``. Returns path.

    The producer must hand a well-formed result (from verdict.build_result);
    a producer bug raises ResultIOError rather than emitting a bad artifact.
    """
    errs = _schema_errors(result)
    if errs:
        raise ResultIOError("result schema invalid: " + "; ".join(errs))
    recomputed = verdict.canonical_digest(result["canonical_payload"])
    if recomputed != result["result_digest"]:
        raise ResultIOError(
            f"result_digest self-check failed: {result['result_digest']} "
            f"!= recomputed {recomputed}"
        )
    if result["expected_exit_code"] != verdict.to_exit_code(
        result["canonical_payload"]["verdict"]
    ):
        raise ResultIOError("expected_exit_code disagrees with verdict")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(f".{out.name}.tmp.{os.getpid()}")
    blob = yaml.safe_dump(result, sort_keys=True, allow_unicode=True)
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, blob.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(str(tmp), str(out))  # atomic on POSIX
    return str(out)


# --- interpret (CI adapter) ------------------------------------------------
@dataclass(frozen=True)
class Decision:
    verdict: str
    exit_code: int
    reason: str
    synthetic: bool  # True => we fabricated analysis_error, did not trust file


def _analysis_error(reason: str) -> Decision:
    return Decision(
        verdict.ANALYSIS_ERROR,
        verdict.to_exit_code(verdict.ANALYSIS_ERROR),
        reason,
        synthetic=True,
    )


def interpret_result(
    path,
    actual_exit: int | None,
    expected_inputs: dict | None = None,
    *,
    harness_version: str | None = None,
) -> Decision:
    """Reconcile a result file with the CI reality; fail closed on any doubt.

    ``expected_inputs`` is the repository-qualified input set the CI is actually
    running against (current candidate/policy). ``actual_exit`` is the exit code
    the harness process really returned. Any inconsistency -> analysis_error.
    """
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _analysis_error("result file missing")
    except OSError as e:
        return _analysis_error(f"result file unreadable: {e}")

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return _analysis_error("result file corrupt (YAML parse failed)")
    if not isinstance(data, dict):
        return _analysis_error("result file is not a mapping")

    errs = _schema_errors(data)
    if errs:
        return _analysis_error("result schema invalid: " + "; ".join(errs))

    payload = data["canonical_payload"]
    if verdict.canonical_digest(payload) != data["result_digest"]:
        return _analysis_error("result_digest mismatch (tampered or corrupt)")

    recorded = payload["verdict"]
    expected_exit = data["expected_exit_code"]
    if verdict.to_exit_code(recorded) != expected_exit:
        return _analysis_error(
            f"recorded verdict {recorded!r} inconsistent with "
            f"expected_exit_code {expected_exit}"
        )

    if harness_version is not None and payload["harness_version"] != harness_version:
        return _analysis_error(
            f"harness_version mismatch: {payload['harness_version']!r} "
            f"!= {harness_version!r}"
        )

    if expected_inputs is not None and payload["inputs"] != expected_inputs:
        # Result was produced against a different candidate/policy (부칙 A-1.1).
        return _analysis_error("stale result: inputs != current candidate/policy")

    if actual_exit is not None and actual_exit != expected_exit:
        # Trust neither side — the two disagree (부칙 A-1.1/A-1.6).
        return _analysis_error(
            f"exit/result mismatch: actual exit {actual_exit} "
            f"!= expected {expected_exit}"
        )

    return Decision(recorded, expected_exit, "consistent", synthetic=False)


# --- attestation invalidation (부칙 A-1.4) ---------------------------------
def attestation_is_valid(
    attestation: dict,
    *,
    result_digest: str,
    candidate_sha: str,
    policy_digest: str,
    now: str | None = None,
) -> bool:
    """True iff a human attestation still binds the current judgment.

    An approval/break-glass attestation names the exact ``result_digest``,
    ``candidate_sha`` and ``policy_digest`` it was granted for. If any of those
    changed, the attestation is automatically void (부칙 A-1.4). break-glass may
    also carry ``expires_at`` (ISO-8601); a provided ``now`` past it voids it.
    """
    if attestation.get("target_result_digest") != result_digest:
        return False
    if attestation.get("candidate_sha") != candidate_sha:
        return False
    if attestation.get("policy_digest") != policy_digest:
        return False
    expires = attestation.get("expires_at")
    if expires is not None and now is not None and now >= expires:
        return False
    return True
