"""T12 — deterministic git primitives.

Provides commit-boundary-safe access used by the completeness gates
(REQ-CG-01, 부칙 A-2). Key property: parsing preserves commit boundaries, so an
ID-less commit sitting between ID'd commits is returned as its own record with
an empty id list — never collapsed away by set reduction (P0-5 root cause).

All functions take an explicit repo path so tests can point at temp repos.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

# Field/record separators used inside a single --format record.
_US = "\x1f"  # unit separator: between fields (sha / subject / trailers)
_RS = "\x1e"  # record separator: between multiple trailer values

# Deterministic environment: stable output regardless of user git config/locale.
_STABLE_CONFIG = [
    "-c", "core.quotepath=false",
    "-c", "i18n.logOutputEncoding=UTF-8",
    "-c", "log.showSignature=false",
]


@dataclass(frozen=True)
class Commit:
    sha: str
    subject: str
    customization_ids: list[str]
    parents: tuple[str, ...] = ()
    change_type: str | None = None

    @property
    def is_merge(self) -> bool:
        return len(self.parents) > 1


def git(repo: str, *args: str, check: bool = True) -> str:
    """Run a git command in repo and return stdout (text)."""
    proc = subprocess.run(
        ["git", "-C", repo, *_STABLE_CONFIG, *args],
        check=check,
        text=True,
        capture_output=True,
    )
    return proc.stdout


def commits(repo: str, base: str, head: str) -> list[Commit]:
    """Return commits in base..head (oldest first), one record per commit.

    Uses NUL (-z) to separate commit records so commit boundaries are never
    ambiguous, and extracts the Customization-ID trailer(s) per commit.
    """
    fmt = (
        f"%H{_US}%s{_US}%P{_US}"
        f"%(trailers:key=Customization-ID,valueonly,separator={_RS}){_US}"
        f"%(trailers:key=Change-Type,valueonly,separator={_RS})"
    )
    out = git(
        repo, "log", "--reverse", "-z", f"--format={fmt}", f"{base}..{head}"
    )
    records = [r for r in out.split("\x00") if r != ""]
    result: list[Commit] = []
    for rec in records:
        parts = rec.split(_US)
        sha = parts[0]
        subject = parts[1] if len(parts) > 1 else ""
        parents = tuple(p for p in (parts[2] if len(parts) > 2 else "").split() if p)
        id_field = parts[3] if len(parts) > 3 else ""
        ct_field = parts[4] if len(parts) > 4 else ""
        ids = [t for t in id_field.split(_RS) if t.strip() != ""]
        ct_vals = [t for t in ct_field.split(_RS) if t.strip() != ""]
        result.append(
            Commit(
                sha=sha,
                subject=subject,
                customization_ids=ids,
                parents=parents,
                change_type=ct_vals[0] if ct_vals else None,
            )
        )
    return result


def changed_paths(repo: str, sha: str) -> list[str]:
    """Files changed by a single (non-merge) commit, NUL-safe."""
    out = git(
        repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", sha
    )
    return [p for p in out.split("\x00") if p != ""]


def net_changed_paths(repo: str, base: str, head: str) -> list[str]:
    """Paths whose content differs between base and head trees (NET effect).

    Distinct from per-commit changed_paths: a file added then removed across the
    range does NOT appear here. Used for the lower-bound (required) drift check.
    """
    out = git(repo, "diff", "--name-only", "-z", base, head)
    return [p for p in out.split("\x00") if p != ""]


def object_exists(repo: str, sha: str) -> bool:
    """True if <sha>^{commit} exists and is valid (부칙 A-2.4 preflight)."""
    proc = subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"],
        text=True,
        capture_output=True,
    )
    return proc.returncode == 0
