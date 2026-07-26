"""T61 — patch-kill test (SRS P0-7 · C-4).

A required test only proves a customization *survives* if removing the patch
makes that test FAIL. patch-kill checks exactly that: run the test against a tree
that does NOT contain the patch and require a failure.

- test fails without the patch -> PROVEN (the test genuinely defends it) -> pass.
- test passes without the patch -> SHELL (it asserts nothing about the patch;
  a green "껍데기" that would keep passing even if the customization vanished)
  -> block.
- required test skips/errors -> INCONCLUSIVE -> analysis_error.
- harness cannot run (missing binary, timeout, internal exit) -> INFRA_ERROR
  -> analysis_error.

The caller supplies the without-patch ref (e.g. base upstream, or the candidate
with this one ID's commits removed via clean-room replay). This mechanism is
agnostic to how that tree was produced.

SANDBOX: this executes a test command, so in production it MUST run in the
sandboxed runner (부칙 A-3.5) — network off, read-only root, resource/time limits.
Here it runs with a timeout only; callers are responsible for isolation.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import pytest_runs
from acgh import reapply
from acgh import verdict

PROVEN = "proven"
SHELL = "shell_test"
INCONCLUSIVE = "inconclusive"
INFRA_ERROR = "infra_error"
_SCHEMA_PATH = Path(__file__).parent / "schema" / "patch-kill-plan.schema.json"
_RUNTIME_SCHEMA_PATH = (
    Path(__file__).parent / "schema" / "runtime-patch-kill-plan.schema.json"
)
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

_VERDICT = {
    PROVEN: verdict.PASS,
    SHELL: verdict.BLOCK,
    INCONCLUSIVE: verdict.ANALYSIS_ERROR,
    INFRA_ERROR: verdict.ANALYSIS_ERROR,
}


class PatchKillPlanError(ValueError):
    """A source patch-kill plan is malformed or semantically ambiguous."""


@dataclass(frozen=True)
class PatchKillResult:
    status: str
    detail: str

    def verdict(self) -> str:
        return _VERDICT[self.status]

    def to_gate_result(self, name: str = "patch-kill") -> verdict.GateResult:
        return verdict.GateResult(name, self.verdict(), (f"{self.status}: {self.detail}",))


def _schema_validator(
    path: Path = _SCHEMA_PATH,
) -> jsonschema.protocols.Validator:
    schema = json.loads(path.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def parse_plan(data: dict) -> dict:
    """Validate a source-negative-control plan and return it unchanged."""
    if not isinstance(data, dict):
        raise PatchKillPlanError("patch-kill plan is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise PatchKillPlanError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )

    experiments = [
        item["customization_id"] for item in data["experiments"]
    ]
    pending = [item["customization_id"] for item in data["pending"]]
    covered = experiments + pending
    if len(covered) != len(set(covered)):
        raise PatchKillPlanError(
            "customization IDs must be unique across experiments and pending"
        )
    selectors = [item["required_test"] for item in data["experiments"]]
    if len(selectors) != len(set(selectors)):
        raise PatchKillPlanError(
            "each source experiment must use a distinct required test"
        )
    return data


def load_plan(path) -> dict:
    return parse_plan(yaml.safe_load(Path(path).read_text(encoding="utf-8")))


def plan_digest(plan: dict) -> str:
    parse_plan(plan)
    return verdict.canonical_digest(plan)


def parse_runtime_plan(data: dict) -> dict:
    """Validate the deployed-counterfactual plan and its unique bindings."""
    if not isinstance(data, dict):
        raise PatchKillPlanError("runtime patch-kill plan is not a mapping")
    errors = sorted(
        _schema_validator(_RUNTIME_SCHEMA_PATH).iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise PatchKillPlanError(
            "runtime schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )
    ids = [item["customization_id"] for item in data["experiments"]]
    if len(ids) != len(set(ids)):
        raise PatchKillPlanError(
            "runtime experiment customization IDs must be unique"
        )
    selectors = [item["required_test"] for item in data["experiments"]]
    if len(selectors) != len(set(selectors)):
        raise PatchKillPlanError(
            "each runtime experiment must use a distinct required test"
        )
    return data


def load_runtime_plan(path) -> dict:
    return parse_runtime_plan(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def runtime_plan_digest(plan: dict) -> str:
    parse_runtime_plan(plan)
    return verdict.canonical_digest(plan)


def runtime_patch_kill(
    root,
    *,
    customization_id: str,
    required_test: str,
    probes: list[str],
    target_repeats: int = 2,
    timeout_seconds: int = 300,
    environment: dict[str, str] | None = None,
) -> tuple[verdict.GateResult, ...]:
    """Run health probes around repeated deployed-counterfactual failures.

    A target failure is accepted only when every independent probe passes both
    before and after the target selector. The target selector must fail on
    every repetition. A passing target is a shell test; skip/error/harness
    failures are never patch-kill proof.
    """
    if not probes:
        raise PatchKillPlanError("runtime patch-kill probes cannot be empty")
    if target_repeats < 2:
        raise PatchKillPlanError(
            "runtime patch-kill target must run at least twice"
        )

    def run(selector: str) -> str:
        try:
            return pytest_runs.run_selector(
                root,
                selector,
                timeout_seconds=timeout_seconds,
                environment=environment,
            )
        except pytest_runs.PytestRunError as exc:
            return f"{INFRA_ERROR}:{exc}"

    def probe_gate(phase: str) -> verdict.GateResult:
        outcomes = [(selector, run(selector)) for selector in probes]
        reasons = tuple(
            f"{selector}={outcome}" for selector, outcome in outcomes
        )
        probe_verdict = (
            verdict.PASS
            if all(outcome == "pass" for _, outcome in outcomes)
            else verdict.ANALYSIS_ERROR
        )
        return verdict.GateResult(
            f"runtime-patch-kill:{customization_id}:{phase}",
            probe_verdict,
            reasons,
        )

    preflight = probe_gate("preflight")
    target_outcomes = [run(required_test) for _ in range(target_repeats)]
    if all(outcome == "fail" for outcome in target_outcomes):
        target_verdict = verdict.PASS
        target_status = PROVEN
    elif any(outcome == "pass" for outcome in target_outcomes):
        target_verdict = verdict.BLOCK
        target_status = SHELL
    else:
        target_verdict = verdict.ANALYSIS_ERROR
        target_status = INCONCLUSIVE
    target = verdict.GateResult(
        f"runtime-patch-kill:{customization_id}:negative-control",
        target_verdict,
        (
            f"status={target_status}",
            f"required_test={required_test}",
            "outcomes=" + ",".join(target_outcomes),
        ),
    )
    postflight = probe_gate("postflight")
    return preflight, target, postflight


def runtime_result_inputs(
    plan: dict,
    experiment: dict,
    *,
    candidate_sha: str,
    counterfactual_tree_sha: str,
    governance_sha: str,
    counterfactual_artifact_digest: str,
    deployment_evidence_digest: str,
    target_environment: str,
    suite_digest: str,
) -> dict:
    """Build the canonical non-secret input binding for a runtime experiment."""
    parse_runtime_plan(plan)
    for label, value in {
        "candidate_sha": candidate_sha,
        "counterfactual_tree_sha": counterfactual_tree_sha,
        "governance_sha": governance_sha,
    }.items():
        if not _FULL_SHA.fullmatch(value or ""):
            raise PatchKillPlanError(f"{label} is not a full commit/tree SHA")
    for label, value in {
        "counterfactual_artifact_digest": counterfactual_artifact_digest,
        "deployment_evidence_digest": deployment_evidence_digest,
        "suite_digest": suite_digest,
    }.items():
        if not _DIGEST.fullmatch(value or ""):
            raise PatchKillPlanError(f"{label} is not a sha256 digest")
    if not target_environment.strip():
        raise PatchKillPlanError("target_environment cannot be empty")
    return {
        "scope": plan["scope"],
        "repositories": {
            "candidate": {
                "repository": plan["candidate"]["repository"],
                "sha": candidate_sha,
            },
            "counterfactual": {
                "repository": plan["candidate"]["repository"],
                "sha": experiment["without_patch_sha"],
                "tree_sha": counterfactual_tree_sha,
            },
            "governance": {
                "repository": "easyseop/openmetadata-test",
                "sha": governance_sha,
            },
        },
        "runtime_patch_kill_plan_digest": runtime_plan_digest(plan),
        "customization_id": experiment["customization_id"],
        "required_test": experiment["required_test"],
        "probes": list(experiment["probes"]),
        "target_repeats": experiment["target_repeats"],
        "suite_digest": suite_digest,
        "counterfactual_artifact_digest": counterfactual_artifact_digest,
        "deployment_evidence_digest": deployment_evidence_digest,
        "target_environment": target_environment,
    }


def patch_kill(
    repo: str,
    ref_without_patch: str,
    test_cmd,
    worktree_dir: str,
    *,
    timeout: int = 120,
    environment: dict[str, str] | None = None,
) -> PatchKillResult:
    """Run ``test_cmd`` in a worktree at ``ref_without_patch``; require failure."""
    add = reapply._wt(repo, "worktree", "add", "--detach", worktree_dir, ref_without_patch)
    if add.returncode != 0:
        raise reapply.ReapplyError(f"worktree add failed: {add.stderr.strip()}")
    try:
        try:
            proc = subprocess.run(
                list(test_cmd), cwd=worktree_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, **(environment or {})},
            )
        except subprocess.TimeoutExpired:
            return PatchKillResult(INFRA_ERROR, f"test timed out after {timeout}s")
        except OSError as e:
            return PatchKillResult(INFRA_ERROR, f"test could not be executed: {e}")

        if proc.returncode == 1:
            return PatchKillResult(PROVEN, f"test failed without patch (rc={proc.returncode})")
        if proc.returncode != 0:
            return PatchKillResult(
                INFRA_ERROR,
                f"test harness exited unexpectedly (rc={proc.returncode})",
            )
        return PatchKillResult(
            SHELL, "test PASSED without the patch — does not prove survival"
        )
    finally:
        reapply._wt(repo, "worktree", "remove", "--force", worktree_dir)
        reapply._wt(repo, "worktree", "prune")


def patch_kill_pytest(
    repo: str,
    ref_without_patch: str,
    suite_root,
    selector: str,
    worktree_dir: str,
    *,
    timeout: int = 120,
) -> PatchKillResult:
    """Run one pytest selector against a source tree without the patch.

    JUnit and the real pytest exit are reconciled by ``pytest_runs``. Only an
    assertion failure proves the negative control. Collection/internal errors,
    skips, and timeouts remain inconclusive and can never become pass.
    """
    add = reapply._wt(
        repo, "worktree", "add", "--detach", worktree_dir, ref_without_patch
    )
    if add.returncode != 0:
        raise reapply.ReapplyError(f"worktree add failed: {add.stderr.strip()}")
    try:
        try:
            outcome = pytest_runs.run_selector(
                suite_root,
                selector,
                timeout_seconds=timeout,
                environment={
                    "OPENMETADATA_PRODUCT_REPO": str(
                        Path(worktree_dir).resolve()
                    )
                },
            )
        except pytest_runs.PytestRunError as exc:
            return PatchKillResult(
                INFRA_ERROR, f"pytest evidence is not trustworthy: {exc}"
            )
        if outcome == "fail":
            return PatchKillResult(
                PROVEN, "required test failed without the patch"
            )
        if outcome == "pass":
            return PatchKillResult(
                SHELL,
                "required test PASSED without the patch — does not prove survival",
            )
        return PatchKillResult(
            INCONCLUSIVE,
            f"required test outcome cannot prove patch survival: {outcome}",
        )
    finally:
        reapply._wt(repo, "worktree", "remove", "--force", worktree_dir)
        reapply._wt(repo, "worktree", "prune")
