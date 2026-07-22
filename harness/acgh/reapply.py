"""T20 — reapply, CI-detect mode (SRS P0-2, 부칙 A-2.6).

Answers the pipeline's first question after an upstream upgrade: *does the
customization stack still apply cleanly on the new upstream?* — without ever
touching the caller's working tree.

Mechanism: add a throwaway detached ``git worktree`` at the target upstream ref,
cherry-pick the patch-lock's source commits in order there, classify each
outcome, then destroy the worktree. The caller's tree is never modified, so this
is safe to run in CI on every push.

Outcome classification is the A-2.6 taxonomy — a non-zero cherry-pick is NOT
uniformly "conflict":
- ``applied``                 — clean.
- ``content_conflict``        — real merge conflict; conflicted paths reported.
- ``redundant_or_empty``      — change already present; NOT auto-dropped, routed
                                to retirement (T92).
- ``missing_source_object``   — source SHA not reachable (부칙 A-2.4); never
                                substituted with "latest".
- ``invalid_source_commit``   — SHA is not a commit object.
- ``skipped_due_to_dependency`` — a prior commit in the stack blocked.
- ``internal_error``          — unexpected git failure.

Verdict (reusing the verdict engine): any missing/invalid/internal ->
analysis_error; else any conflict/redundant -> block; else pass.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from acgh import gitprim
from acgh import verdict

APPLIED = "applied"
CONTENT_CONFLICT = "content_conflict"
REDUNDANT_OR_EMPTY = "redundant_or_empty"
MISSING_SOURCE_OBJECT = "missing_source_object"
INVALID_SOURCE_COMMIT = "invalid_source_commit"
SKIPPED_DUE_TO_DEPENDENCY = "skipped_due_to_dependency"
INTERNAL_ERROR = "internal_error"

_ANALYSIS_ERROR = frozenset(
    {MISSING_SOURCE_OBJECT, INVALID_SOURCE_COMMIT, INTERNAL_ERROR}
)
_BLOCK = frozenset({CONTENT_CONFLICT, REDUNDANT_OR_EMPTY})


class ReapplyError(RuntimeError):
    """Unrecoverable harness-side failure (e.g. worktree setup)."""


@dataclass(frozen=True)
class CommitResult:
    sha: str
    status: str
    conflicted_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReapplyReport:
    target_ref: str
    results: tuple[CommitResult, ...]

    def verdict(self) -> str:
        statuses = {r.status for r in self.results}
        if statuses & _ANALYSIS_ERROR:
            return verdict.ANALYSIS_ERROR
        if statuses & _BLOCK:
            return verdict.BLOCK
        return verdict.PASS

    def to_gate_result(self, name: str = "reapply-detect") -> verdict.GateResult:
        reasons = tuple(
            f"{r.status}: {r.sha[:12]}"
            + (f" [{', '.join(r.conflicted_paths)}]" if r.conflicted_paths else "")
            for r in self.results
        )
        return verdict.GateResult(name, self.verdict(), reasons)


def _wt(worktree: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", worktree, *gitprim._STABLE_CONFIG, *args],
        text=True,
        capture_output=True,
    )


def reapply_detect(
    repo: str,
    target_ref: str,
    source_commits,
    worktree_dir: str,
) -> ReapplyReport:
    """Cherry-pick ``source_commits`` (in order) onto ``target_ref`` in a
    throwaway worktree; report per-commit status. The worktree is always removed.

    ``worktree_dir`` must not already exist. ``repo`` and the caller's tree are
    left untouched.
    """
    add = _wt(repo, "worktree", "add", "--detach", worktree_dir, target_ref)
    if add.returncode != 0:
        raise ReapplyError(f"worktree add failed: {add.stderr.strip()}")

    results: list[CommitResult] = []
    try:
        blocked = False
        for sha in source_commits:
            if blocked:
                results.append(CommitResult(sha, SKIPPED_DUE_TO_DEPENDENCY))
                continue
            if not gitprim.object_exists(repo, sha):
                results.append(CommitResult(sha, MISSING_SOURCE_OBJECT))
                blocked = True
                continue

            res = _wt(worktree_dir, "cherry-pick", sha)
            if res.returncode == 0:
                results.append(CommitResult(sha, APPLIED))
                continue

            # Non-zero: classify, then reset the worktree for the next commit.
            unmerged = _wt(
                worktree_dir, "diff", "--name-only", "--diff-filter=U", "-z"
            ).stdout
            conflicted = tuple(p for p in unmerged.split("\x00") if p)
            _wt(worktree_dir, "cherry-pick", "--abort")

            if conflicted:
                results.append(
                    CommitResult(sha, CONTENT_CONFLICT, conflicted_paths=conflicted)
                )
                blocked = True  # downstream of a conflict can't be trusted
            elif "empty" in (res.stderr + res.stdout).lower():
                # Change already present upstream; do not auto-drop (A-2.6).
                results.append(CommitResult(sha, REDUNDANT_OR_EMPTY))
            else:
                results.append(CommitResult(sha, INTERNAL_ERROR))
                blocked = True
    finally:
        _wt(repo, "worktree", "remove", "--force", worktree_dir)
        _wt(repo, "worktree", "prune")

    return ReapplyReport(target_ref=target_ref, results=tuple(results))
