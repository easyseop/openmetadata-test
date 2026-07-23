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

import subprocess
from dataclasses import dataclass

from acgh import reapply
from acgh import verdict

PROVEN = "proven"
SHELL = "shell_test"
INCONCLUSIVE = "inconclusive"

_VERDICT = {
    PROVEN: verdict.PASS,
    SHELL: verdict.BLOCK,
    INCONCLUSIVE: verdict.ANALYSIS_ERROR,
}


@dataclass(frozen=True)
class PatchKillResult:
    status: str
    detail: str

    def verdict(self) -> str:
        return _VERDICT[self.status]

    def to_gate_result(self, name: str = "patch-kill") -> verdict.GateResult:
        return verdict.GateResult(name, self.verdict(), (f"{self.status}: {self.detail}",))


def patch_kill(
    repo: str,
    ref_without_patch: str,
    test_cmd,
    worktree_dir: str,
    *,
    timeout: int = 120,
) -> PatchKillResult:
    """Run ``test_cmd`` in a worktree at ``ref_without_patch``; require failure."""
    add = reapply._wt(repo, "worktree", "add", "--detach", worktree_dir, ref_without_patch)
    if add.returncode != 0:
        raise reapply.ReapplyError(f"worktree add failed: {add.stderr.strip()}")
    try:
        try:
            proc = subprocess.run(
                list(test_cmd), cwd=worktree_dir,
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return PatchKillResult(INCONCLUSIVE, f"test timed out after {timeout}s")
        except OSError as e:
            return PatchKillResult(INCONCLUSIVE, f"test could not be executed: {e}")

        if proc.returncode != 0:
            return PatchKillResult(PROVEN, f"test failed without patch (rc={proc.returncode})")
        return PatchKillResult(
            SHELL, "test PASSED without the patch — does not prove survival"
        )
    finally:
        reapply._wt(repo, "worktree", "remove", "--force", worktree_dir)
        reapply._wt(repo, "worktree", "prune")
