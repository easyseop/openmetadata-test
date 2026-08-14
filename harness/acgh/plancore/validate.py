"""Recompute plan inputs and validate proposal evidence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import yaml

from acgh.verdict import ANALYSIS_ERROR, APPROVAL, BLOCK, canonical_digest
from acgh.plancore.errors import PlanControlError
from acgh.plancore.markers import cleanup_pair, pair_from_run
from acgh.plancore.paths import directory_digest, list_dirty_paths
from acgh.plancore.preflight import collect_state
from acgh.plancore.schema import (
    atomic_write,
    canonical_payload_digest,
    read_data,
    validate,
)


class ValidationAdapter(Protocol):
    name: str

    def verify_documents(self, run_dir: Path, recorded: dict) -> None: ...
    def validate_proposal(
        self,
        request: dict,
        proposal_documents: list[dict],
        discovered_facts: dict,
    ) -> list[str]: ...


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _load_proposal_documents(proposal_dir: Path) -> list[tuple[Path, dict]]:
    if not proposal_dir.is_dir():
        raise PlanControlError("PROPOSAL_MISSING", "proposal directory is missing")
    documents: list[tuple[Path, dict]] = []
    for path in sorted(proposal_dir.rglob("*")):
        if path.is_symlink():
            raise PlanControlError(
                "PROPOSAL_SYMLINK",
                "proposal must not contain symlinks",
                details={"path": str(path)},
            )
        if not path.is_file() or path.suffix not in {".yaml", ".yml", ".json"}:
            continue
        value = read_data(path)
        documents.append((path, value))
    if not documents:
        raise PlanControlError(
            "PROPOSAL_EMPTY",
            "proposal must contain at least one YAML or JSON document",
        )
    return documents


def _decode_pointer(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise PlanControlError(
            "EVIDENCE_POINTER_INVALID",
            f"JSON pointer must start with '/': {pointer}",
        )
    return [token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")]


def _dereference(value: object, pointer: str) -> object:
    current = value
    for token in _decode_pointer(pointer):
        if isinstance(current, list):
            try:
                index = int(token)
                current = current[index]
            except (ValueError, IndexError) as exc:
                raise PlanControlError(
                    "EVIDENCE_POINTER_NOT_FOUND",
                    f"list pointer token does not exist: {token}",
                ) from exc
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise PlanControlError(
                "EVIDENCE_POINTER_NOT_FOUND",
                f"pointer token does not exist: {token}",
            )
    return current


def _parse_ref(run_dir: Path, reference: str) -> tuple[Path, str]:
    file_name, separator, pointer = reference.partition("#")
    if not separator:
        raise PlanControlError(
            "EVIDENCE_REF_INVALID",
            f"evidence ref requires file#pointer: {reference}",
        )
    path = (run_dir / file_name).resolve()
    try:
        path.relative_to(run_dir)
    except ValueError as exc:
        raise PlanControlError(
            "EVIDENCE_REF_OUTSIDE_RUN",
            f"evidence ref escapes run directory: {reference}",
        ) from exc
    if path.parts[: len((run_dir / "proposal").parts)] == (run_dir / "proposal").parts:
        raise PlanControlError(
            "EVIDENCE_REF_SELF_REFERENCE",
            "proposal files cannot be used as machine evidence",
        )
    return path, pointer


def _walk_evidence_refs(value: object) -> list[object]:
    found: list[object] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidence_refs":
                if not isinstance(child, list):
                    raise PlanControlError(
                        "EVIDENCE_REFS_INVALID",
                        "evidence_refs must be a list",
                    )
                found.extend(child)
            else:
                found.extend(_walk_evidence_refs(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk_evidence_refs(child))
    return found


def _validate_refs(run_dir: Path, documents: list[tuple[Path, dict]]) -> list[str]:
    errors: list[str] = []
    cache: dict[Path, dict] = {}
    for _, document in documents:
        for item in _walk_evidence_refs(document):
            if isinstance(item, str):
                reference = item
                expected = None
                has_expected = False
            elif isinstance(item, dict) and isinstance(item.get("ref"), str):
                reference = item["ref"]
                has_expected = "expected" in item
                expected = item.get("expected")
            else:
                errors.append(f"unsupported evidence ref: {item!r}")
                continue
            try:
                path, pointer = _parse_ref(run_dir, reference)
                if path not in cache:
                    cache[path] = read_data(path)
                actual = _dereference(cache[path], pointer)
                if has_expected and actual != expected:
                    errors.append(
                        f"{reference}: expected {expected!r}, found {actual!r}"
                    )
            except PlanControlError as exc:
                errors.append(f"{reference}: {exc.message}")
    return errors


def _validate_required_decision_fields(documents: list[tuple[Path, dict]]) -> list[str]:
    required = {
        "subject",
        "decision",
        "decision_source",
        "evidence_refs",
        "affected_customization_ids",
        "required_follow_up",
    }
    issues: list[str] = []
    for path, document in documents:
        decisions = document.get("decisions")
        if decisions is None:
            continue
        if not isinstance(decisions, list):
            issues.append(f"{path.name}: decisions must be a list")
            continue
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                issues.append(f"{path.name}: decisions[{index}] must be a mapping")
                continue
            missing = sorted(required - set(decision))
            if missing:
                issues.append(
                    f"{path.name}: decisions[{index}] missing {', '.join(missing)}"
                )
            if decision.get("decision_source") not in {
                "proposed",
                "human_input",
                "observed",
            }:
                issues.append(
                    f"{path.name}: decisions[{index}].decision_source is invalid"
                )
    return issues


def _verify_self_digests(input_lock: dict, facts: dict) -> list[str]:
    issues: list[str] = []
    if canonical_payload_digest(input_lock) != input_lock.get("input_lock_digest"):
        issues.append("stored input_lock_digest does not match canonical_payload")
    if canonical_payload_digest(facts) != facts.get("discovered_facts_digest"):
        issues.append("stored discovered_facts_digest does not match canonical_payload")
    expected_items = {
        item["fact_id"]: canonical_digest(item)
        for item in facts.get("canonical_payload", {}).get("items", [])
    }
    if expected_items != facts.get("item_digests"):
        issues.append("stored item_digests do not match discovered facts")
    return issues


def _allowed_run_dirty_paths(repo: Path, run_dir: Path) -> set[str]:
    try:
        relative = run_dir.relative_to(repo).as_posix()
    except ValueError:
        return set()
    components = relative.split("/")
    return {"/".join(components[:index]) for index in range(1, len(components) + 1)}


def _dirty_paths(request: dict, run_dir: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for name, raw in request["repositories"].items():
        repo = Path(raw).resolve()
        dirty = list_dirty_paths(repo)
        allowed = _allowed_run_dirty_paths(repo, run_dir) if name == "checker" else set()
        result[name] = [
            path
            for path in dirty
            if not any(
                path == prefix
                or path.rstrip("/") == prefix.rstrip("/")
                or prefix.startswith(path.rstrip("/") + "/")
                or path.startswith(prefix.rstrip("/") + "/")
                for prefix in allowed
            )
        ]
    return result


def _next_attempt(attempt_dir: Path) -> tuple[int, str, Path]:
    existing = sorted(attempt_dir.glob("attempt-*.json"))
    ordinal = len(existing) + 1
    attempt_id = f"attempt-{ordinal:04d}"
    path = attempt_dir / f"{attempt_id}.json"
    if path.exists():
        raise PlanControlError(
            "ATTEMPT_APPEND_ONLY_VIOLATION",
            "validation attempt path already exists",
        )
    return ordinal, attempt_id, path


def _write_attempt_and_summary(
    run_dir: Path,
    request: dict,
    *,
    verdict: str,
    reasons: list[str],
    registration_stale: bool,
    binding: dict,
    evidence_ref_errors: list[str],
    dirty_paths: dict[str, list[str]],
) -> dict:
    attempt_dir = run_dir / "validation-attempts"
    attempt_dir.mkdir(exist_ok=True)
    ordinal, attempt_id, attempt_path = _next_attempt(attempt_dir)
    attempt = {
        "schema_version": 1,
        "attempt_id": attempt_id,
        "ordinal": ordinal,
        "verdict": verdict,
        "reasons": reasons,
        "registration_stale": registration_stale,
        "plan_binding": binding,
        "evidence_ref_errors": evidence_ref_errors,
        "dirty_paths": dirty_paths,
        "observational_metadata": {"validated_at": _utc_now()},
    }
    validate("validation-attempt", attempt)
    atomic_write(attempt_path, attempt)
    attempts = [
        f"validation-attempts/{path.name}"
        for path in sorted(attempt_dir.glob("attempt-*.json"))
    ]
    if verdict == APPROVAL:
        next_action = "review the proposal; implementation remains a separate decision"
        if not request.get("owner"):
            next_action = "assign the unresolved owner before implementation"
    else:
        next_action = "fix the reported proposal issue or start a new run as required"
    result = {
        "schema_version": 1,
        "run_id": request["run_id"],
        "latest_attempt": attempt_id,
        "attempts": attempts,
        "verdict": verdict,
        "plan_binding": binding,
        "next_action": next_action,
    }
    validate("result", result)
    atomic_write(run_dir / "validation-result.json", result)
    return result


def _run_validation_active(run_dir: str | Path, adapter: ValidationAdapter) -> dict:
    root = Path(run_dir).resolve()
    existing_result = root / "validation-result.json"
    if existing_result.is_file():
        previous = read_data(existing_result)
        if previous.get("verdict") == APPROVAL:
            raise PlanControlError(
                "COMPLETED_RUN_READ_ONLY",
                "a completed run cannot be revalidated or overwritten",
            )
    pair = pair_from_run(root)
    request = read_data(root / "run-request.yaml")
    stored_lock = read_data(root / "input-lock.yaml")
    stored_facts = read_data(root / "discovered-facts.json")
    validate("run-request", request)
    validate("input-lock", stored_lock)
    validate("discovered-facts", stored_facts)
    documents = _load_proposal_documents(root / "proposal")
    proposal_digest = directory_digest(root / "proposal")
    input_lock_digest = stored_lock["input_lock_digest"]
    facts_digest = stored_facts["discovered_facts_digest"]
    binding = {
        "proposal_digest": proposal_digest,
        "input_lock_digest": input_lock_digest,
        "discovered_facts_digest": facts_digest,
        "plan_digest": canonical_digest(
            {
                "proposal_digest": proposal_digest,
                "input_lock_digest": input_lock_digest,
                "discovered_facts_digest": facts_digest,
            }
        ),
    }
    reasons = _verify_self_digests(stored_lock, stored_facts)
    evidence_errors = _validate_refs(root, documents)
    decision_issues = _validate_required_decision_fields(documents)
    proposal_values = [document for _, document in documents]
    policy_issues = adapter.validate_proposal(
        request,
        proposal_values,
        stored_facts,
    )
    dirty = _dirty_paths(request, root)
    registration_stale = False
    try:
        source_path = root / "official-doc-sources.yaml"
        if source_path.is_file():
            adapter.verify_documents(root, read_data(source_path))
        recomputed_lock, recomputed_facts, _ = collect_state(
            request,
            adapter,
            run_dir=root,
            collect_documents=False,
            locked_refs_override=stored_lock["canonical_payload"]["repositories"]["product"]["commit_shas"],
        )
        stored_registration = stored_lock["canonical_payload"]["registration"]
        current_registration = recomputed_lock["canonical_payload"]["registration"]
        registration_stale = stored_registration != current_registration
        if registration_stale:
            reasons.append("active registration changed after preflight")
        stored_without_registration = dict(stored_lock["canonical_payload"])
        current_without_registration = dict(recomputed_lock["canonical_payload"])
        stored_without_registration.pop("registration", None)
        current_without_registration.pop("registration", None)
        if stored_without_registration != current_without_registration:
            reasons.append("recomputed input lock does not match the stored lock")
        if stored_facts["canonical_payload"] != recomputed_facts["canonical_payload"]:
            reasons.append("recomputed discovered facts do not match stored facts")
    except PlanControlError as exc:
        reasons.append(f"{exc.code}: {exc.message}")
    if any(dirty.values()):
        reasons.append("unreported repository changes remain outside the current run")

    if reasons or evidence_errors:
        final_verdict = ANALYSIS_ERROR
    elif decision_issues or policy_issues:
        final_verdict = BLOCK
        reasons.extend(decision_issues)
        reasons.extend(policy_issues)
    else:
        final_verdict = APPROVAL
    result = _write_attempt_and_summary(
        root,
        request,
        verdict=final_verdict,
        reasons=reasons,
        registration_stale=registration_stale,
        binding=binding,
        evidence_ref_errors=evidence_errors,
        dirty_paths=dirty,
    )
    cleanup_pair(pair)
    return result


def _failure_binding(root: Path) -> tuple[dict, dict]:
    request = {"run_id": root.name}
    try:
        request = read_data(root / "run-request.yaml")
    except PlanControlError:
        pass
    try:
        input_lock = read_data(root / "input-lock.yaml")
        input_digest = input_lock.get("input_lock_digest") or canonical_digest(input_lock)
    except PlanControlError:
        input_digest = canonical_digest({"state": "input-lock-unreadable"})
    try:
        facts = read_data(root / "discovered-facts.json")
        facts_digest = facts.get("discovered_facts_digest") or canonical_digest(facts)
    except PlanControlError:
        facts_digest = canonical_digest({"state": "facts-unreadable"})
    try:
        proposal_digest = directory_digest(root / "proposal")
    except PlanControlError:
        proposal_digest = canonical_digest({"state": "proposal-unreadable"})
    binding = {
        "proposal_digest": proposal_digest,
        "input_lock_digest": input_digest,
        "discovered_facts_digest": facts_digest,
        "plan_digest": canonical_digest(
            {
                "proposal_digest": proposal_digest,
                "input_lock_digest": input_digest,
                "discovered_facts_digest": facts_digest,
            }
        ),
    }
    return request, binding


def run_validation(run_dir: str | Path, adapter: ValidationAdapter) -> dict:
    """Validate and always close the current marker pair on a completed attempt."""
    root = Path(run_dir).resolve()
    pair = pair_from_run(root)
    try:
        return _run_validation_active(root, adapter)
    except PlanControlError as exc:
        if exc.code == "COMPLETED_RUN_READ_ONLY":
            cleanup_pair(pair)
            raise
        request, binding = _failure_binding(root)
        result = _write_attempt_and_summary(
            root,
            request,
            verdict=ANALYSIS_ERROR,
            reasons=[f"{exc.code}: {exc.message}"],
            registration_stale=False,
            binding=binding,
            evidence_ref_errors=[],
            dirty_paths={},
        )
        cleanup_pair(pair)
        return result
