"""T62/T24 — evaluation-time SHA and candidate-lock binding.

Closes the time-gap between a gate evaluating a candidate and that candidate
being promoted: bind every input to a resolved 40-hex commit SHA, never to a
moving reference (a branch, HEAD, or a mutable tag). A branch is resolved to a
SHA ONCE, here, and only the SHA travels downstream — so "what the gate judged"
and "what gets promoted" are provably the same object.

Produces the repository-qualified ``inputs`` block that verdict.build_result
embeds and result_io.interpret_result stale-checks against (부칙 A-1.5):
``{repositories: {name: {sha}}, patch_source_lock_digest, verifier_catalog_digest}``.

``build_repository_inputs`` remains the patch-replay input builder.
``build_candidate_inputs`` is the strategy-neutral T24 path: it derives all
judgment inputs from one immutable candidate lock.
"""
from __future__ import annotations

import re
import subprocess

from acgh import gitprim

_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class BindingError(ValueError):
    pass


def pin(repo: str, ref: str) -> str:
    """Resolve ``ref`` to a concrete commit SHA now, and verify it exists.

    Accepts any commit-ish (branch, tag, SHA) but returns the pinned SHA; the
    caller stores the SHA, never the ref, so later movement of the ref is
    irrelevant.
    """
    p = subprocess.run(
        ["git", "-C", repo, *gitprim._STABLE_CONFIG,
         "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        text=True, capture_output=True,
    )
    sha = p.stdout.strip()
    if p.returncode != 0 or not _FULL_SHA.match(sha):
        raise BindingError(f"cannot resolve {ref!r} to a commit SHA")
    return sha


def pin_all(repo: str, refs: dict) -> dict:
    """Pin a mapping of name -> ref to name -> SHA."""
    return {name: pin(repo, ref) for name, ref in refs.items()}


def build_repository_inputs(
    repository_shas: dict,
    *,
    patch_source_lock_digest: str,
    verifier_catalog_digest: str,
) -> dict:
    """Assemble the repository-qualified inputs block; reject anything unpinned.

    ``repository_shas`` maps a role name (upstream/core/platform/policy/...) to a
    full 40-hex SHA. A value that is not a full SHA (e.g. a branch name or an
    abbreviation) is rejected — dynamic references never enter the record.
    """
    if not repository_shas:
        raise BindingError("at least one repository SHA is required")
    for name, sha in repository_shas.items():
        if not isinstance(sha, str) or not _FULL_SHA.match(sha):
            raise BindingError(f"{name}: not a full 40-hex SHA: {sha!r}")
    if not _DIGEST.match(patch_source_lock_digest or ""):
        raise BindingError(f"bad patch_source_lock_digest: {patch_source_lock_digest!r}")
    if not _DIGEST.match(verifier_catalog_digest or ""):
        raise BindingError(f"bad verifier_catalog_digest: {verifier_catalog_digest!r}")
    return {
        "repositories": {
            name: {"sha": repository_shas[name]} for name in sorted(repository_shas)
        },
        "patch_source_lock_digest": patch_source_lock_digest,
        "verifier_catalog_digest": verifier_catalog_digest,
    }


def assert_lock_binding(inputs: dict, source_lock) -> None:
    """Verify the inputs' patch_source_lock_digest matches the actual lock."""
    got = inputs.get("patch_source_lock_digest")
    want = source_lock.digest()
    if got != want:
        raise BindingError(
            f"inputs patch_source_lock_digest {got} != lock digest {want}"
        )


def build_candidate_inputs(candidate_lock, *, verifier_catalog_digest: str) -> dict:
    """Build result inputs from one immutable T24 candidate lock.

    Callers do not pass candidate SHAs separately: deriving them from the lock
    prevents a result from accidentally binding a different commit or artifact.
    """
    if not _DIGEST.match(verifier_catalog_digest or ""):
        raise BindingError(
            f"bad verifier_catalog_digest: {verifier_catalog_digest!r}"
        )

    upstream = candidate_lock.upstream
    candidate = candidate_lock.candidate
    result = {
        "integration_strategy": candidate_lock.integration_strategy,
        "repositories": {
            "upstream_base": {
                "repository": upstream.repository,
                "sha": upstream.base_sha,
            },
            "upstream_target": {
                "repository": upstream.repository,
                "sha": upstream.target_sha,
            },
            "candidate": {
                "repository": candidate.repository,
                "sha": candidate.commit_sha,
                "tree_sha": candidate.tree_sha,
            },
        },
        "artifact_digest": candidate.artifact_digest,
        "candidate_lock_digest": candidate_lock.digest(),
        "verifier_catalog_digest": verifier_catalog_digest,
    }
    if candidate_lock.patch_source_lock_digest is not None:
        result["patch_source_lock_digest"] = (
            candidate_lock.patch_source_lock_digest
        )
    return result
