"""T22 — clean-room replay (SRS P0-5 · C-5, 부칙 A-3.8).

Proves a candidate is exactly reproducible from its locked sources: replay the
patch-lock onto the target upstream in a throwaway worktree and compare the
resulting *tree* to the candidate's tree. If they match, nothing was
hand-edited into the candidate outside the registered patches — the strongest
"survival" evidence short of running tests.

Tree comparison, not commit comparison: git trees are content-addressed, so the
replayed tree hash is independent of commit metadata (author/committer/date).
Same target + same sources always yield the same tree hash — determinism is
free. Scope is the TRACKED source tree only (부칙 A-3.8); build artifacts / image
layers are T91's concern.

Verdict:
- replay could not be produced (missing source, conflict) -> analysis_error
  (inconclusive, route to review — 부칙 A-3.7).
- tree mismatch -> block, with the differing paths reported.
- tree match -> pass.
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh import gitprim
from acgh import reapply
from acgh import verdict


@dataclass(frozen=True)
class ReplayResult:
    target_ref: str
    candidate_ref: str
    replay_tree: str
    candidate_tree: str
    apply_ok: bool
    differing_paths: tuple[str, ...] = ()

    @property
    def equal(self) -> bool:
        return self.apply_ok and self.replay_tree == self.candidate_tree

    def verdict(self) -> str:
        if not self.apply_ok:
            return verdict.ANALYSIS_ERROR
        return verdict.PASS if self.equal else verdict.BLOCK

    def to_gate_result(self, name: str = "clean-room-replay") -> verdict.GateResult:
        if not self.apply_ok:
            reasons = ("replay could not be produced (missing source or conflict)",)
        elif self.equal:
            reasons = (f"tree match: {self.replay_tree}",)
        else:
            reasons = (f"tree mismatch; differing: {', '.join(self.differing_paths)}",)
        return verdict.GateResult(name, self.verdict(), reasons)


def replay_tree(repo: str, target_ref: str, source_commits, worktree_dir: str):
    """Replay ``source_commits`` onto ``target_ref`` in a throwaway worktree and
    return the resulting tree hash, or None if replay could not be produced
    (missing source object or conflict). The worktree is always torn down."""
    add = reapply._wt(repo, "worktree", "add", "--detach", worktree_dir, target_ref)
    if add.returncode != 0:
        raise reapply.ReapplyError(f"worktree add failed: {add.stderr.strip()}")
    tree = None
    try:
        ok = True
        for sha in source_commits:
            if not gitprim.object_exists(repo, sha):
                ok = False
                break
            r = reapply._wt(worktree_dir, "cherry-pick", sha)
            if r.returncode != 0:
                reapply._wt(worktree_dir, "cherry-pick", "--abort")
                ok = False
                break
        if ok:
            tree = reapply._wt(
                worktree_dir, "rev-parse", "HEAD^{tree}"
            ).stdout.strip()
    finally:
        reapply._wt(repo, "worktree", "remove", "--force", worktree_dir)
        reapply._wt(repo, "worktree", "prune")
    return tree


def replay_and_compare(
    repo: str,
    target_ref: str,
    source_commits,
    candidate_ref: str,
    worktree_dir: str,
) -> ReplayResult:
    """Replay ``source_commits`` onto ``target_ref`` in a clean worktree and
    compare the resulting tree to ``candidate_ref``'s tree."""
    candidate_tree = reapply._wt(
        repo, "rev-parse", f"{candidate_ref}^{{tree}}"
    ).stdout.strip()

    tree = replay_tree(repo, target_ref, source_commits, worktree_dir)
    apply_ok = tree is not None
    replay_tree_hash = tree or ""

    differing: tuple[str, ...] = ()
    if apply_ok and replay_tree_hash != candidate_tree:
        out = reapply._wt(
            repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z",
            candidate_tree, replay_tree_hash,
        ).stdout
        differing = tuple(p for p in out.split("\x00") if p)

    return ReplayResult(
        target_ref=target_ref,
        candidate_ref=candidate_ref,
        replay_tree=replay_tree_hash,
        candidate_tree=candidate_tree,
        apply_ok=apply_ok,
        differing_paths=differing,
    )
