"""Isolated multi-version upgrade rehearsal plan validation.

This module prepares phase-four Git rehearsals without modifying the product
branch.  A plan pins every official version to a full commit SHA, requires
contiguous upgrade intervals, and marks the exercise as a synthetic backtest
rather than historical production evidence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

from acgh import gitprim
from acgh import verdict

_SHA = re.compile(r"^[0-9a-f]{40}$")
_REQUIRED_STAGES = (
    "identify-refs",
    "upstream-diff",
    "bank-diff",
    "prepare-disposable-upgrade-branch",
    "reapply-detect",
    "source-gates",
    "upgrade-risk-gates",
    "result-labels",
)


class RehearsalPlanError(ValueError):
    """The rehearsal plan is incomplete or internally inconsistent."""


@dataclass(frozen=True)
class OfficialRef:
    tag: str
    sha: str


@dataclass(frozen=True)
class RehearsalRun:
    run_id: str
    order: int
    upstream_base: OfficialRef
    upstream_target: OfficialRef
    expected_git_relation: str
    result_file: str


@dataclass(frozen=True)
class RehearsalPlan:
    source_reference_sha: str
    source_evidence: str
    branch_prefix: str
    result_directory: str
    stages: tuple[str, ...]
    runs: tuple[RehearsalRun, ...]


def _mapping(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise RehearsalPlanError(f"{label} must be a mapping")
    return value


def _text(mapping: dict, key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RehearsalPlanError(f"{label}.{key} must be a non-empty string")
    return value


def _sha(mapping: dict, key: str, label: str) -> str:
    value = _text(mapping, key, label)
    if not _SHA.fullmatch(value):
        raise RehearsalPlanError(f"{label}.{key} must be a full Git SHA")
    return value


def _relative_file(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.endswith("/"):
        raise RehearsalPlanError(f"{label} must be a relative file path")
    return value


def load_plan(path) -> RehearsalPlan:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = _mapping(raw, "plan")
    if root.get("schema_version") != 1:
        raise RehearsalPlanError("schema_version must be 1")
    if root.get("mode") != "synthetic-backtest":
        raise RehearsalPlanError("mode must be synthetic-backtest")
    if root.get("historical_claim") != "not-production-history":
        raise RehearsalPlanError(
            "historical_claim must be not-production-history"
        )

    source = _mapping(root.get("source_reference"), "source_reference")
    source_sha = _sha(source, "commit_sha", "source_reference")
    source_evidence = _relative_file(
        _text(source, "evidence_file", "source_reference"),
        "source_reference.evidence_file",
    )

    execution = _mapping(root.get("execution"), "execution")
    if execution.get("isolation") != "disposable-worktree":
        raise RehearsalPlanError(
            "execution.isolation must be disposable-worktree"
        )
    if execution.get("product_branch_mutation") is not False:
        raise RehearsalPlanError(
            "execution.product_branch_mutation must be false"
        )
    if execution.get("persistent_candidate_branch") is not False:
        raise RehearsalPlanError(
            "execution.persistent_candidate_branch must be false"
        )
    branch_prefix = _text(execution, "branch_prefix", "execution")
    result_directory = _text(execution, "result_directory", "execution")
    _relative_file(f"{result_directory}/result.json", "result_directory")

    stages = root.get("stages")
    if not isinstance(stages, list) or tuple(stages) != _REQUIRED_STAGES:
        raise RehearsalPlanError(
            "stages must contain the required phase-four sequence"
        )

    raw_runs = root.get("runs")
    if not isinstance(raw_runs, list) or not raw_runs:
        raise RehearsalPlanError("runs must be a non-empty list")
    runs = []
    ids = set()
    orders = set()
    result_files = set()
    for index, item in enumerate(raw_runs):
        run = _mapping(item, f"runs[{index}]")
        run_id = _text(run, "id", f"runs[{index}]")
        order = run.get("order")
        if not isinstance(order, int) or order < 1:
            raise RehearsalPlanError(
                f"runs[{index}].order must be a positive integer"
            )
        if run_id in ids or order in orders:
            raise RehearsalPlanError("run ids and orders must be unique")
        ids.add(run_id)
        orders.add(order)

        base = _mapping(run.get("upstream_base"), f"runs[{index}].upstream_base")
        target = _mapping(
            run.get("upstream_target"), f"runs[{index}].upstream_target"
        )
        relation = _text(run, "expected_git_relation", f"runs[{index}]")
        if relation not in {"ancestor", "divergent"}:
            raise RehearsalPlanError(
                f"runs[{index}].expected_git_relation is invalid"
            )
        result_file = _relative_file(
            _text(run, "result_file", f"runs[{index}]"),
            f"runs[{index}].result_file",
        )
        if result_file in result_files:
            raise RehearsalPlanError("result_file values must be unique")
        result_files.add(result_file)
        runs.append(
            RehearsalRun(
                run_id=run_id,
                order=order,
                upstream_base=OfficialRef(
                    _text(base, "tag", f"runs[{index}].upstream_base"),
                    _sha(base, "sha", f"runs[{index}].upstream_base"),
                ),
                upstream_target=OfficialRef(
                    _text(target, "tag", f"runs[{index}].upstream_target"),
                    _sha(target, "sha", f"runs[{index}].upstream_target"),
                ),
                expected_git_relation=relation,
                result_file=result_file,
            )
        )

    ordered = tuple(sorted(runs, key=lambda item: item.order))
    if tuple(item.order for item in ordered) != tuple(range(1, len(ordered) + 1)):
        raise RehearsalPlanError("run order must start at 1 without gaps")
    for left, right in zip(ordered, ordered[1:]):
        if left.upstream_target != right.upstream_base:
            raise RehearsalPlanError(
                f"upgrade chain is not contiguous: {left.run_id} -> {right.run_id}"
            )
    return RehearsalPlan(
        source_reference_sha=source_sha,
        source_evidence=source_evidence,
        branch_prefix=branch_prefix,
        result_directory=result_directory,
        stages=tuple(stages),
        runs=ordered,
    )


def _resolve_tag(repo: str, ref: OfficialRef) -> tuple[str | None, str | None]:
    try:
        actual = gitprim.git(
            repo, "rev-parse", "--verify", f"{ref.tag}^{{commit}}"
        ).strip()
    except Exception as exc:
        return None, f"{ref.tag}: unavailable ({type(exc).__name__})"
    if actual != ref.sha:
        return actual, f"{ref.tag}: pinned SHA {ref.sha} != actual {actual}"
    return actual, None


def inspect_plan(repo: str, plan: RehearsalPlan) -> dict:
    errors = []
    if not gitprim.object_exists(repo, plan.source_reference_sha):
        errors.append(
            f"source reference unavailable: {plan.source_reference_sha}"
        )
    runs = []
    for item in plan.runs:
        base_sha, base_error = _resolve_tag(repo, item.upstream_base)
        target_sha, target_error = _resolve_tag(repo, item.upstream_target)
        errors.extend(error for error in (base_error, target_error) if error)
        relation = None
        if base_sha and target_sha:
            try:
                relation = (
                    "ancestor"
                    if gitprim.is_ancestor(repo, base_sha, target_sha)
                    else "divergent"
                )
            except gitprim.GitPrimitiveError as exc:
                errors.append(f"{item.run_id}: {exc}")
            if relation and relation != item.expected_git_relation:
                errors.append(
                    f"{item.run_id}: expected relation "
                    f"{item.expected_git_relation}, actual {relation}"
                )
        runs.append(
            {
                "id": item.run_id,
                "order": item.order,
                "upstream_base": {
                    "tag": item.upstream_base.tag,
                    "sha": base_sha or item.upstream_base.sha,
                },
                "upstream_target": {
                    "tag": item.upstream_target.tag,
                    "sha": target_sha or item.upstream_target.sha,
                },
                "git_relation": relation or "unavailable",
                "temporary_upgrade_branch": (
                    f"{plan.branch_prefix}/{item.run_id}"
                ),
                "result_file": item.result_file,
                "status": "refs-ready" if not (base_error or target_error) else "blocked",
            }
        )
    state = verdict.ANALYSIS_ERROR if errors else verdict.PASS
    return {
        "schema_version": 1,
        "verdict": state,
        "mode": "synthetic-backtest",
        "historical_claim": "not-production-history",
        "source_reference_sha": plan.source_reference_sha,
        "product_branch_mutation": False,
        "persistent_candidate_branch": False,
        "stages": list(plan.stages),
        "runs": runs,
        "warnings": [
            "the version-adapted 1.13.0 customization code exists in OM_TEMP; manifests and gates are not connected yet",
            "results validate the branch strategy and gates, not historical production upgrades",
        ],
        "errors": errors,
    }
