"""T62 — bind required test execution to one immutable candidate.

The contract catalog says *which* tests must exist.  This module proves that
those tests actually ran against the candidate commit and artifact recorded in
the candidate lock.  It also preserves retry history instead of flattening a
fail-then-pass sequence into an ordinary pass.

Trust boundary:

* malformed or stale result metadata -> ``analysis_error``;
* missing, skipped, failed, or errored required tests -> ``block``;
* critical/high fail-then-pass -> ``approval`` (flaky evidence is retained);
* clean required runs -> ``pass``.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import contracts
from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "test-run-set.schema.json"
_CRITICALITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class TestRunError(ValueError):
    """A test-run set is malformed or internally inconsistent."""


@dataclass(frozen=True)
class TestAttempt:
    test_id: str
    attempt: int
    outcome: str


@dataclass(frozen=True)
class TestRunSet:
    candidate_sha: str
    artifact_digest: str
    harness_version: str
    suite_version: str
    runs: tuple[TestAttempt, ...]

    def canonical(self) -> dict:
        return {
            "schema_version": 1,
            "candidate": {
                "commit_sha": self.candidate_sha,
                "artifact_digest": self.artifact_digest,
            },
            "harness_version": self.harness_version,
            "suite_version": self.suite_version,
            "runs": [
                {
                    "test_id": run.test_id,
                    "attempt": run.attempt,
                    "outcome": run.outcome,
                }
                for run in sorted(
                    self.runs, key=lambda item: (item.test_id, item.attempt)
                )
            ],
        }

    def digest(self) -> str:
        return verdict.canonical_digest(self.canonical())


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def parse_test_run_set(data: dict) -> TestRunSet:
    if not isinstance(data, dict):
        raise TestRunError("test-run set is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise TestRunError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )

    runs = tuple(
        TestAttempt(item["test_id"], item["attempt"], item["outcome"])
        for item in data["runs"]
    )
    grouped: dict[str, list[int]] = {}
    for run in runs:
        grouped.setdefault(run.test_id, []).append(run.attempt)
    for test_id, attempts in grouped.items():
        if len(attempts) != len(set(attempts)):
            raise TestRunError(f"{test_id}: duplicate attempt number")
        ordered = sorted(attempts)
        if ordered != list(range(1, len(ordered) + 1)):
            raise TestRunError(
                f"{test_id}: attempts must be contiguous starting at 1"
            )

    return TestRunSet(
        candidate_sha=data["candidate"]["commit_sha"],
        artifact_digest=data["candidate"]["artifact_digest"],
        harness_version=data["harness_version"],
        suite_version=data["suite_version"],
        runs=runs,
    )


def load_test_run_set(path) -> TestRunSet:
    return parse_test_run_set(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def write_test_run_set(run_set: TestRunSet, path) -> str:
    """Schema-validate and atomically persist the canonical T62 run set."""
    data = run_set.canonical()
    # Reparse before writing so producer bugs cannot emit invalid evidence.
    parse_test_run_set(data)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp.{os.getpid()}")
    blob = yaml.safe_dump(data, sort_keys=True, allow_unicode=True)
    descriptor = os.open(
        str(temporary), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644
    )
    try:
        os.write(descriptor, blob.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(str(temporary), str(output))
    return str(output)


def _required_tests(manifests, catalog, criticality_by_id):
    required: dict[str, str] = {}
    for manifest in manifests:
        customization_id = manifest["customization_id"]
        criticality = criticality_by_id.get(customization_id)
        if criticality not in _CRITICALITY_RANK:
            raise TestRunError(
                f"{customization_id}: missing or invalid criticality"
            )
        try:
            test_ids = contracts.effective_tests(manifest, catalog)
        except contracts.ContractError as exc:
            raise TestRunError(str(exc)) from exc
        if not test_ids:
            raise TestRunError(
                f"{customization_id}: active customization has no effective tests"
            )
        for test_id in test_ids:
            current = required.get(test_id)
            if (
                current is None
                or _CRITICALITY_RANK[criticality] > _CRITICALITY_RANK[current]
            ):
                required[test_id] = criticality
    return required


def check_test_runs(
    manifests,
    catalog,
    run_set: TestRunSet,
    candidate_lock,
    *,
    criticality_by_id: dict[str, str],
    expected_harness_version: str,
    expected_suite_version: str,
    name: str = "test-candidate-binding",
) -> verdict.GateResult:
    """Judge required test execution without hiding retries or stale inputs."""
    reasons: list[str] = []
    stale: list[str] = []
    if run_set.candidate_sha != candidate_lock.candidate.commit_sha:
        stale.append("candidate commit SHA")
    if run_set.artifact_digest != candidate_lock.candidate.artifact_digest:
        stale.append("candidate artifact digest")
    if run_set.harness_version != expected_harness_version:
        stale.append("harness version")
    if run_set.suite_version != expected_suite_version:
        stale.append("suite version")
    if stale:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"stale test result: {field} mismatch" for field in stale),
        )

    try:
        required = _required_tests(manifests, catalog, criticality_by_id)
    except TestRunError as exc:
        return verdict.GateResult(
            name, verdict.BLOCK, (str(exc),)
        )

    grouped: dict[str, list[TestAttempt]] = {}
    for run in run_set.runs:
        grouped.setdefault(run.test_id, []).append(run)

    missing = sorted(set(required) - set(grouped))
    reasons.extend(f"required test missing: {test_id}" for test_id in missing)
    blocking = bool(missing)
    approval = False

    for test_id in sorted(required):
        attempts = sorted(grouped.get(test_id, []), key=lambda item: item.attempt)
        if not attempts:
            continue
        outcomes = [attempt.outcome for attempt in attempts]
        final = outcomes[-1]
        if final != "pass":
            blocking = True
            reasons.append(f"required test {test_id}: final outcome={final}")
            continue
        prior_failures = [
            outcome for outcome in outcomes[:-1] if outcome in {"fail", "error"}
        ]
        if prior_failures:
            flaky_reason = (
                f"flaky retry-pass: {test_id} "
                f"(attempts={','.join(outcomes)}, "
                f"criticality={required[test_id]})"
            )
            reasons.append(flaky_reason)
            if required[test_id] in {"high", "critical"}:
                approval = True
        else:
            reasons.append(f"required test passed: {test_id}")

    if blocking:
        state = verdict.BLOCK
    elif approval:
        state = verdict.APPROVAL
    else:
        state = verdict.PASS
    reasons.append(f"test_run_set_digest={run_set.digest()}")
    return verdict.GateResult(name, state, tuple(reasons))
