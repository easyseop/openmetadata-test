"""T61 — patch-kill test (SRS P0-7 · C-4).

A required test only proves a customization *survives* if removing the patch
makes that test FAIL. patch-kill checks exactly that: run the test against a tree
that does NOT contain the patch and require a failure.

- test fails without the patch -> PROVEN (the test genuinely defends it) -> pass.
- test passes without the patch -> SHELL (it asserts nothing about the patch;
  a green "껍데기" that would keep passing even if the customization vanished)
  -> block.
- test cannot be run (missing binary, timeout) -> INCONCLUSIVE -> analysis_error.

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
_SCHEMA_PATH = Path(__file__).parent / "schema" / "patch-kill-plan.schema.json"

_VERDICT = {
    PROVEN: verdict.PASS,
    SHELL: verdict.BLOCK,
    INCONCLUSIVE: verdict.ANALYSIS_ERROR,
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


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
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
            return PatchKillResult(INCONCLUSIVE, f"test timed out after {timeout}s")
        except OSError as e:
            return PatchKillResult(INCONCLUSIVE, f"test could not be executed: {e}")

        if proc.returncode == 1:
            return PatchKillResult(PROVEN, f"test failed without patch (rc={proc.returncode})")
        if proc.returncode != 0:
            return PatchKillResult(
                INCONCLUSIVE,
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
                INCONCLUSIVE, f"pytest evidence is not trustworthy: {exc}"
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
