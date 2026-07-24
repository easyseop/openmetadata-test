"""T25 — vendor ancestry and approved-upstream-target gate.

For a ``vendor-merge`` run, Git must prove all of the following from the exact
T24 candidate lock:

1. base, target, and candidate commit objects exist locally;
2. the candidate commit/tree still matches the lock;
3. official base and target have a common history;
4. both the locked base lineage and the approved target are ancestors of the
   candidate.

Known-but-invalid topology is ``block``. Missing objects, a stale lock, a Git
query failure, or running this mode-specific gate for ``patch-replay`` is
``analysis_error``. This distinction is fail-closed: absence of evidence can
never be presented as a normal policy violation or an approval.
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh import candidate as C
from acgh import gitprim
from acgh import verdict


@dataclass(frozen=True)
class AncestryEvidence:
    base_target_merge_base: str | None
    base_in_candidate: bool
    target_in_candidate: bool


class AncestryAnalysisError(RuntimeError):
    """The repository did not contain enough trustworthy evidence."""


def inspect_vendor_ancestry(repo: str, lock: C.CandidateLock) -> AncestryEvidence:
    """Collect deterministic ancestry evidence or raise analysis error."""
    if lock.integration_strategy != C.VENDOR_MERGE:
        raise AncestryAnalysisError(
            "vendor-ancestry gate requires integration_strategy=vendor-merge"
        )

    commits = {
        "upstream base": lock.upstream.base_sha,
        "upstream target": lock.upstream.target_sha,
        "candidate": lock.candidate.commit_sha,
    }
    missing = [
        f"{label} {sha}" for label, sha in commits.items()
        if not gitprim.object_exists(repo, sha)
    ]
    if missing:
        raise AncestryAnalysisError(
            "required commit object missing: " + "; ".join(missing)
        )

    try:
        C.assert_candidate_binding(repo, lock)
        common = gitprim.merge_base(
            repo, lock.upstream.base_sha, lock.upstream.target_sha
        )
        base_in_candidate = gitprim.is_ancestor(
            repo, lock.upstream.base_sha, lock.candidate.commit_sha
        )
        target_in_candidate = gitprim.is_ancestor(
            repo, lock.upstream.target_sha, lock.candidate.commit_sha
        )
    except (C.CandidateLockError, gitprim.GitPrimitiveError) as exc:
        raise AncestryAnalysisError(str(exc)) from exc

    return AncestryEvidence(
        base_target_merge_base=common,
        base_in_candidate=base_in_candidate,
        target_in_candidate=target_in_candidate,
    )


def to_gate_result(
    lock: C.CandidateLock,
    evidence: AncestryEvidence,
    *,
    name: str = "vendor-ancestry",
) -> verdict.GateResult:
    """Convert evidence into a deterministic pass/block gate result."""
    violations = []
    if evidence.base_target_merge_base is None:
        violations.append("upstream base and target have no common ancestor")
    if not evidence.base_in_candidate:
        violations.append("candidate does not contain locked upstream base")
    if not evidence.target_in_candidate:
        violations.append("candidate does not contain approved upstream target")

    if violations:
        return verdict.GateResult(name, verdict.BLOCK, tuple(violations))

    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"candidate={lock.candidate.commit_sha}",
            f"approved_target={lock.upstream.target_sha}",
            f"base_target_merge_base={evidence.base_target_merge_base}",
            f"candidate_lock_digest={lock.digest()}",
        ),
    )


def check_vendor_ancestry(
    repo: str,
    lock: C.CandidateLock,
    *,
    name: str = "vendor-ancestry",
) -> verdict.GateResult:
    """Run the complete T25 gate and fail closed on analysis errors."""
    try:
        evidence = inspect_vendor_ancestry(repo, lock)
    except AncestryAnalysisError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"analysis_error: {exc}",)
        )
    return to_gate_result(lock, evidence, name=name)
