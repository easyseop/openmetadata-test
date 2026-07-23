"""T32 — final-state invariants (SRS P0-5, 부칙 A-3.7).

Moves the bar from "registered" toward "survives": a customization that is
present but contributes nothing to the final tree is dead weight, and a
candidate that cannot be reproduced from its sources cannot be trusted.

Checks:
- id_net_contribution — counterfactual replay (부칙 A-3.7 (b)): replay the full
  stack vs the stack with one ID's commits removed. Same tree => that ID is
  INERT (net-effect-zero / effectively reverted) -> route to retirement/ADR. A
  replay that cannot be produced (dropping the ID breaks a dependent) is
  INCONCLUSIVE -> review, not a silent pass.
- candidate_reproducible — candidate HEAD tree == replayed tree (delegates to
  T22 clean-room replay).
- stale_attestations — when the candidate/policy/result changes, prior human
  approvals are void (reuses result_io.attestation_is_valid): the ones that no
  longer bind must be re-collected.
"""
from __future__ import annotations

from acgh import replay
from acgh import result_io
from acgh import verdict

CONTRIBUTES = "contributes"
INERT = "inert"
INCONCLUSIVE = "inconclusive"

_CONTRIB_VERDICT = {
    CONTRIBUTES: verdict.PASS,
    INERT: verdict.BLOCK,          # net-effect-zero -> retirement (부칙 A-2.6)
    INCONCLUSIVE: verdict.ANALYSIS_ERROR,
}


def id_net_contribution(
    repo, target_ref, full_source_commits, id_source_commits,
    worktree_full, worktree_without,
) -> str:
    """Return CONTRIBUTES / INERT / INCONCLUSIVE for one ID via counterfactual."""
    tree_full = replay.replay_tree(repo, target_ref, full_source_commits, worktree_full)
    if tree_full is None:
        return INCONCLUSIVE
    drop = set(id_source_commits)
    without = [c for c in full_source_commits if c not in drop]
    tree_without = replay.replay_tree(repo, target_ref, without, worktree_without)
    if tree_without is None:
        return INCONCLUSIVE
    return CONTRIBUTES if tree_full != tree_without else INERT


def contribution_verdict(status: str) -> str:
    return _CONTRIB_VERDICT[status]


def candidate_reproducible(
    repo, target_ref, source_commits, candidate_ref, worktree_dir
) -> replay.ReplayResult:
    """Candidate HEAD tree must equal the replayed tree (T22 reuse)."""
    return replay.replay_and_compare(
        repo, target_ref, source_commits, candidate_ref, worktree_dir
    )


def stale_attestations(
    attestations, *, result_digest, candidate_sha, policy_digest, now=None
):
    """Return the attestations that no longer bind the current judgment."""
    return [
        a for a in attestations
        if not result_io.attestation_is_valid(
            a, result_digest=result_digest, candidate_sha=candidate_sha,
            policy_digest=policy_digest, now=now,
        )
    ]
