"""T24 — integration strategy and immutable candidate lock.

The candidate lock is the source of truth for one upgrade evaluation:

- the default integration strategy is ``vendor-merge``;
- the official upstream base and target are pinned to full commit SHAs;
- the candidate is pinned to commit SHA, tree SHA, and artifact digest;
- ``patch-replay`` additionally binds the patch source lock it replays.

The strategy belongs to the upgrade run, not to every customization manifest.
Keeping it here avoids contradictory per-feature strategy declarations.
T25 will consume this lock to prove upstream ancestry; T26 will consume it to
evaluate customization survival.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import binding
from acgh import gitprim
from acgh import verdict

VENDOR_MERGE = "vendor-merge"
PATCH_REPLAY = "patch-replay"
INTEGRATION_STRATEGIES = (VENDOR_MERGE, PATCH_REPLAY)

_SCHEMA_PATH = Path(__file__).parent / "schema" / "candidate-lock.schema.json"


class CandidateLockError(ValueError):
    """Candidate lock is malformed or does not match the repository."""


@dataclass(frozen=True)
class UpstreamLock:
    repository: str
    base_sha: str
    target_sha: str
    base_tag: str | None = None
    target_tag: str | None = None


@dataclass(frozen=True)
class CandidateIdentity:
    repository: str
    commit_sha: str
    tree_sha: str
    artifact_digest: str


@dataclass(frozen=True)
class CandidateLock:
    integration_strategy: str
    upstream: UpstreamLock
    candidate: CandidateIdentity
    patch_source_lock_digest: str | None = None

    def canonical(self) -> dict:
        """Return the complete judgment-relevant representation."""
        upstream = {
            "repository": self.upstream.repository,
            "base_sha": self.upstream.base_sha,
            "target_sha": self.upstream.target_sha,
        }
        if self.upstream.base_tag is not None:
            upstream["base_tag"] = self.upstream.base_tag
        if self.upstream.target_tag is not None:
            upstream["target_tag"] = self.upstream.target_tag
        data = {
            "schema_version": 1,
            "integration_strategy": self.integration_strategy,
            "upstream": upstream,
            "candidate": {
                "repository": self.candidate.repository,
                "commit_sha": self.candidate.commit_sha,
                "tree_sha": self.candidate.tree_sha,
                "artifact_digest": self.candidate.artifact_digest,
            },
        }
        if self.patch_source_lock_digest is not None:
            data["patch_source_lock_digest"] = self.patch_source_lock_digest
        return data

    def digest(self) -> str:
        return verdict.canonical_digest(self.canonical())

    def result_inputs(self, *, verifier_catalog_digest: str) -> dict:
        """Build the exact input block embedded in an ACGH result."""
        return binding.build_candidate_inputs(
            self, verifier_catalog_digest=verifier_catalog_digest
        )


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def load_candidate_lock(path) -> CandidateLock:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return parse_candidate_lock(data)


def parse_candidate_lock(data: dict) -> CandidateLock:
    """Validate and normalize a lock; omitted strategy defaults to vendor merge."""
    if not isinstance(data, dict):
        raise CandidateLockError("candidate-lock is not a mapping")

    normalized = copy.deepcopy(data)
    normalized.setdefault("integration_strategy", VENDOR_MERGE)
    errs = sorted(
        _schema_validator().iter_errors(normalized),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    if errs:
        loc = lambda e: "/".join(str(p) for p in e.absolute_path) or "<root>"
        raise CandidateLockError(
            "schema: " + "; ".join(f"{loc(e)}: {e.message}" for e in errs)
        )

    upstream = normalized["upstream"]
    candidate = normalized["candidate"]
    return CandidateLock(
        integration_strategy=normalized["integration_strategy"],
        upstream=UpstreamLock(
            repository=upstream["repository"],
            base_sha=upstream["base_sha"],
            target_sha=upstream["target_sha"],
            base_tag=upstream.get("base_tag"),
            target_tag=upstream.get("target_tag"),
        ),
        candidate=CandidateIdentity(
            repository=candidate["repository"],
            commit_sha=candidate["commit_sha"],
            tree_sha=candidate["tree_sha"],
            artifact_digest=candidate["artifact_digest"],
        ),
        patch_source_lock_digest=normalized.get("patch_source_lock_digest"),
    )


def build_candidate_lock(
    repo: str,
    candidate_ref: str,
    *,
    upstream_repository: str,
    upstream_base_sha: str,
    upstream_target_sha: str,
    candidate_repository: str,
    artifact_digest: str,
    integration_strategy: str = VENDOR_MERGE,
    upstream_base_tag: str | None = None,
    upstream_target_tag: str | None = None,
    patch_source_lock_digest: str | None = None,
) -> CandidateLock:
    """Resolve a candidate ref once and construct a fully pinned lock."""
    commit_sha = binding.pin(repo, candidate_ref)
    tree_sha = gitprim.git(repo, "rev-parse", f"{commit_sha}^{{tree}}").strip()
    data = {
        "schema_version": 1,
        "integration_strategy": integration_strategy,
        "upstream": {
            "repository": upstream_repository,
            "base_sha": upstream_base_sha,
            "target_sha": upstream_target_sha,
        },
        "candidate": {
            "repository": candidate_repository,
            "commit_sha": commit_sha,
            "tree_sha": tree_sha,
            "artifact_digest": artifact_digest,
        },
    }
    if upstream_base_tag is not None:
        data["upstream"]["base_tag"] = upstream_base_tag
    if upstream_target_tag is not None:
        data["upstream"]["target_tag"] = upstream_target_tag
    if patch_source_lock_digest is not None:
        data["patch_source_lock_digest"] = patch_source_lock_digest
    return parse_candidate_lock(data)


def assert_candidate_binding(
    repo: str,
    lock: CandidateLock,
    *,
    artifact_digest: str | None = None,
) -> None:
    """Fail if the local candidate or supplied artifact differs from the lock."""
    try:
        actual_commit = binding.pin(repo, lock.candidate.commit_sha)
        actual_tree = gitprim.git(
            repo, "rev-parse", f"{actual_commit}^{{tree}}"
        ).strip()
    except (binding.BindingError, OSError) as exc:
        raise CandidateLockError(
            f"candidate commit is unavailable: {lock.candidate.commit_sha}"
        ) from exc

    if actual_commit != lock.candidate.commit_sha:
        raise CandidateLockError(
            f"candidate commit mismatch: {actual_commit} != "
            f"{lock.candidate.commit_sha}"
        )
    if actual_tree != lock.candidate.tree_sha:
        raise CandidateLockError(
            f"candidate tree mismatch: {actual_tree} != {lock.candidate.tree_sha}"
        )
    if (
        artifact_digest is not None
        and artifact_digest != lock.candidate.artifact_digest
    ):
        raise CandidateLockError(
            f"artifact digest mismatch: {artifact_digest} != "
            f"{lock.candidate.artifact_digest}"
        )
