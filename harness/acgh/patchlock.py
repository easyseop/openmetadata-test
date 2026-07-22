"""T11 — patch-lock data structures, digest, and lineage/order checks.

Reifies the two-lock model from SRS 부칙 A-2:

- ``patch_source_lock`` — IMMUTABLE during a run. Fixed SHAs only; never a
  "latest branch" lookup (부칙 A-2.1/A-2.4). Its canonical digest is the stable
  identity that the result contract binds to (``patch_source_lock_digest``).
- ``candidate_application_lock`` — the RESULT of a run: which commits were
  actually applied, on top of which parent lock, with which resolution records.
  After promotion, an application lock becomes the next upgrade's source lock.

This module never mutates a source lock. It validates structure (JSON Schema),
computes the canonical digest (reusing verdict.canonical_digest so the whole
harness hashes judgments identically), and enforces the lock's ordering
invariants: unique IDs, dependency references resolve, no cycles, and the
series list is already a valid topological order — dependencies appear before
their dependents (부칙 A-3.7). Source-object reachability preflight
(``git cat-file -e``) is provided for T30/T31 to call before reapply
(부칙 A-2.4); missing objects are analysis_error, never auto-substituted.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

from acgh import gitprim
from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "patch-source-lock.schema.json"


class PatchLockError(ValueError):
    """Patch-lock fails structural or ordering validation (fail-closed)."""


@dataclass(frozen=True)
class SeriesEntry:
    id: str
    revision: int
    source_commits: tuple[str, ...]
    depends_on: tuple[str, ...] = ()


@dataclass(frozen=True)
class PatchSourceLock:
    source_release_sha: str
    patch_series: tuple[SeriesEntry, ...]
    source_release_tag: str | None = None

    def canonical(self) -> dict:
        """Digest-relevant projection (order preserved; nothing observational)."""
        return {
            "schema_version": 1,
            "source_release_tag": self.source_release_tag,
            "source_release_sha": self.source_release_sha,
            "patch_series": [
                {
                    "id": e.id,
                    "revision": e.revision,
                    "source_commits": list(e.source_commits),
                    "depends_on": list(e.depends_on),
                }
                for e in self.patch_series
            ],
        }

    def digest(self) -> str:
        return verdict.canonical_digest(self.canonical())

    def lineage_map(self) -> dict[str, list[str]]:
        """Explicit id -> source commit SHAs mapping (부칙 A-2.2 정본 lineage)."""
        return {e.id: list(e.source_commits) for e in self.patch_series}


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def load_source_lock(path) -> PatchSourceLock:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return parse_source_lock(data)


def parse_source_lock(data: dict) -> PatchSourceLock:
    """Validate structure + ordering, return an immutable PatchSourceLock."""
    if not isinstance(data, dict):
        raise PatchLockError("patch-lock is not a mapping")
    errs = sorted(
        _schema_validator().iter_errors(data),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    if errs:
        loc = lambda e: "/".join(str(p) for p in e.absolute_path) or "<root>"
        raise PatchLockError(
            "schema: " + "; ".join(f"{loc(e)}: {e.message}" for e in errs)
        )
    entries = tuple(
        SeriesEntry(
            id=e["id"],
            revision=e["revision"],
            source_commits=tuple(e["source_commits"]),
            depends_on=tuple(e.get("depends_on", [])),
        )
        for e in data["patch_series"]
    )
    lock = PatchSourceLock(
        source_release_sha=data["source_release_sha"],
        patch_series=entries,
        source_release_tag=data.get("source_release_tag"),
    )
    _validate_order(lock)
    return lock


def _validate_order(lock: PatchSourceLock) -> None:
    """Unique IDs, resolvable deps, no cycles, deps-before-dependents order."""
    ids = [e.id for e in lock.patch_series]
    if len(set(ids)) != len(ids):
        raise PatchLockError("duplicate customization_id in patch_series")
    known = set(ids)
    seen: set[str] = set()
    for e in lock.patch_series:
        for dep in e.depends_on:
            if dep not in known:
                raise PatchLockError(
                    f"{e.id} depends_on unknown id {dep!r}"
                )
            if dep == e.id:
                raise PatchLockError(f"{e.id} depends on itself")
            # The series list IS the application order (부칙 A-3.7): a dependency
            # must already have appeared, which also rules out cycles.
            if dep not in seen:
                raise PatchLockError(
                    f"{e.id} lists dependency {dep!r} that does not precede it "
                    f"(series order must be topological)"
                )
        seen.add(e.id)


def verify_source_objects(repo: str, lock: PatchSourceLock) -> list[str]:
    """Preflight (부칙 A-2.4): return source SHAs not reachable in ``repo``.

    Empty list = all present. A non-empty result must be treated as
    analysis_error by the caller (T30/T31), never auto-substituted with a
    "latest" commit.
    """
    missing = []
    for e in lock.patch_series:
        for sha in e.source_commits:
            if not gitprim.object_exists(repo, sha):
                missing.append(sha)
    return missing


@dataclass(frozen=True)
class CandidateApplicationLock:
    parent_lock_digest: str
    applied_commits: tuple[str, ...]
    resolution_record_ids: tuple[str, ...] = ()

    def canonical(self) -> dict:
        return {
            "schema_version": 1,
            "parent_lock_digest": self.parent_lock_digest,
            "applied_commits": list(self.applied_commits),
            "resolution_record_ids": list(self.resolution_record_ids),
        }

    def digest(self) -> str:
        return verdict.canonical_digest(self.canonical())


def build_application_lock(
    source_lock: PatchSourceLock,
    applied_commits,
    resolution_record_ids=(),
) -> CandidateApplicationLock:
    """Build the run-result lock, binding it to the source lock's digest.

    ``parent_lock_digest`` pins the exact source lock this application was
    derived from, so promotion can later verify the chain (부칙 A-2.1).
    """
    return CandidateApplicationLock(
        parent_lock_digest=source_lock.digest(),
        applied_commits=tuple(applied_commits),
        resolution_record_ids=tuple(resolution_record_ids),
    )
