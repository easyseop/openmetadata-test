"""T12 — deterministic git primitives.

Provides commit-boundary-safe access used by the completeness gates
(REQ-CG-01, 부칙 A-2). Key property: parsing preserves commit boundaries, so an
ID-less commit sitting between ID'd commits is returned as its own record with
an empty id list — never collapsed away by set reduction (P0-5 root cause).

All functions take an explicit repo path so tests can point at temp repos.
"""
from __future__ import annotations

import hashlib
import re
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
    "-c", "diff.renames=false",
    "-c", "merge.renames=false",
    "-c", "merge.directoryRenames=false",
]
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
RENAME_DETECTION_POLICY = "disabled"
EMPTY_MERGE_DRIVER_CONFIG_DIGEST = "sha256:" + hashlib.sha256(b"").hexdigest()


class GitPrimitiveError(RuntimeError):
    """A deterministic Git query could not produce a trustworthy answer."""


def git_version() -> str:
    proc = subprocess.run(["git", "--version"], text=True, capture_output=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise GitPrimitiveError("cannot determine Git version for audit evidence")
    return proc.stdout.strip()


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


@dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_type: str
    object_id: str
    path: str


@dataclass(frozen=True)
class NetChange:
    """One canonical tree-to-tree path change with rename detection disabled."""

    status: str
    path: str


@dataclass(frozen=True)
class DiagnosticRename:
    """A non-canonical rename/copy hint produced only for human diagnosis."""

    status: str
    score: int
    old_path: str
    new_path: str


@dataclass(frozen=True)
class MergeTreeResult:
    tree_sha: str
    conflicted_paths: tuple[str, ...]
    git_version: str
    command: tuple[str, ...]
    output_digest: str
    merge_driver_config_digest: str
    # Informational audit digest. Effective behavior is fixed by _STABLE_CONFIG,
    # while this digest may still differ when user config contains shadowed values.
    replay_config_digest: str
    rename_detection_policy: str


def git(repo: str, *args: str, check: bool = True) -> str:
    """Run a git command in repo and return stdout (text)."""
    try:
        proc = subprocess.run(
            ["git", "-C", repo, *_STABLE_CONFIG, *args],
            check=check,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "no output").strip()
        raise GitPrimitiveError(
            f"git {' '.join(args)} failed ({exc.returncode}): {detail}"
        ) from exc
    return proc.stdout


def resolve_commit(repo: str, ref: str) -> str:
    """Resolve one ref to an exact commit SHA, rejecting ambiguous output."""
    sha = git(
        repo,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{ref}^{{commit}}",
    ).strip()
    if not _FULL_SHA.match(sha):
        raise GitPrimitiveError(f"cannot resolve commit ref {ref!r}: {sha!r}")
    return sha


def worktree_is_dirty(repo: str) -> bool:
    """Return whether tracked or untracked worktree state is present."""
    return bool(git(repo, "status", "--porcelain=v1", "-z"))


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
    out = git(repo, "diff", "--no-renames", "--name-only", "-z", base, head)
    return [p for p in out.split("\x00") if p != ""]


def net_changes(repo: str, base: str, head: str) -> tuple[NetChange, ...]:
    """Return canonical A/M/D-style changes, independent of user rename config.

    Git can also report type changes and unmerged/broken pairs.  They are retained
    as their one-letter status instead of being silently folded into ``M``.
    Rename/copy statuses cannot appear because ``--no-renames`` is explicit.
    """
    out = git(repo, "diff", "--no-renames", "--name-status", "-z", base, head)
    fields = [item for item in out.split("\x00") if item]
    if len(fields) % 2:
        raise GitPrimitiveError("malformed canonical --name-status output")
    changes: list[NetChange] = []
    for index in range(0, len(fields), 2):
        status, path = fields[index:index + 2]
        code = status[:1]
        if code in {"R", "C"}:
            raise GitPrimitiveError(
                "canonical change output unexpectedly contains rename/copy status"
            )
        changes.append(NetChange(code, path))
    return tuple(sorted(changes, key=lambda item: item.path.encode("utf-8")))


def diagnostic_renames(
    repo: str,
    base: str,
    head: str,
    *,
    threshold: int = 50,
) -> tuple[DiagnosticRename, ...]:
    """Return explicit ``-M -C`` hints without affecting canonical judgments."""
    if isinstance(threshold, bool) or not isinstance(threshold, int) or not 0 < threshold <= 100:
        raise GitPrimitiveError("rename diagnostic threshold must be an integer from 1 to 100")
    option = f"{threshold}%"
    out = git(
        repo,
        "diff",
        "--name-status",
        "-z",
        f"-M{option}",
        f"-C{option}",
        "--find-copies-harder",
        base,
        head,
    )
    fields = [item for item in out.split("\x00") if item]
    findings: list[DiagnosticRename] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        code = status[:1]
        if code not in {"R", "C"}:
            if index >= len(fields):
                raise GitPrimitiveError("malformed diagnostic --name-status output")
            index += 1
            continue
        if index + 1 >= len(fields):
            raise GitPrimitiveError("malformed diagnostic rename/copy output")
        old_path, new_path = fields[index:index + 2]
        index += 2
        try:
            score = int(status[1:])
        except ValueError as exc:
            raise GitPrimitiveError(f"malformed diagnostic score: {status!r}") from exc
        findings.append(DiagnosticRename(code, score, old_path, new_path))
    return tuple(sorted(
        findings,
        key=lambda item: (
            item.old_path.encode("utf-8"), item.new_path.encode("utf-8"), item.status
        ),
    ))


def binary_changed_paths(repo: str, base: str, head: str) -> tuple[str, ...]:
    """Return paths Git reports as binary in one canonical no-rename diff."""
    proc = subprocess.run(
        [
            "git", "-C", repo, *_STABLE_CONFIG,
            "diff", "--no-renames", "--numstat", "-z", base, head,
        ],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise GitPrimitiveError(
            "binary path diff failed: "
            + proc.stderr.decode("utf-8", errors="replace").strip()
        )
    paths: list[str] = []
    for record in (item for item in proc.stdout.split(b"\x00") if item):
        parts = record.split(b"\t", 2)
        if len(parts) != 3:
            raise GitPrimitiveError("malformed --numstat output")
        added, deleted, raw_path = parts
        if added == b"-" and deleted == b"-":
            try:
                paths.append(raw_path.decode("utf-8"))
            except UnicodeDecodeError as exc:
                raise GitPrimitiveError("binary diff returned a non-UTF-8 path") from exc
    return tuple(sorted(paths, key=lambda path: path.encode("utf-8")))


def list_tree(repo: str, ref: str, *, dirs_only: bool = False) -> list[str]:
    """Top-level entries of ``ref``'s tree (NUL-safe). dirs_only -> trees only."""
    args = ["ls-tree", "--name-only", "-z"]
    if dirs_only:
        args.append("-d")
    out = git(repo, *args, ref)
    return [p for p in out.split("\x00") if p != ""]


def list_tree_recursive(repo: str, ref: str) -> list[str]:
    """All file paths under ``ref``'s tree (NUL-safe)."""
    out = git(repo, "ls-tree", "-r", "--name-only", "-z", ref)
    return [p for p in out.split("\x00") if p != ""]


def tree_entries(repo: str, ref: str) -> dict[str, TreeEntry]:
    """Return every recursive tree entry keyed by its NUL-safe path."""
    out = git(repo, "ls-tree", "-r", "-z", ref)
    entries: dict[str, TreeEntry] = {}
    for raw in (item for item in out.split("\x00") if item):
        metadata, separator, path = raw.partition("\t")
        parts = metadata.split()
        if not separator or len(parts) != 3:
            raise GitPrimitiveError(f"malformed ls-tree record: {raw!r}")
        mode, object_type, object_id = parts
        entries[path] = TreeEntry(mode, object_type, object_id, path)
    return entries


def blob_bytes(repo: str, ref: str, path: str) -> bytes:
    """Read one path from one ref without applying text decoding."""
    proc = subprocess.run(
        ["git", "-C", repo, *_STABLE_CONFIG, "show", f"{ref}:{path}"],
        check=False,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise GitPrimitiveError(
            f"cannot read {ref}:{path}: "
            f"{proc.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return proc.stdout


def object_exists(repo: str, sha: str) -> bool:
    """True if <sha>^{commit} exists and is valid (부칙 A-2.4 preflight)."""
    proc = subprocess.run(
        ["git", "-C", repo, "cat-file", "-e", f"{sha}^{{commit}}"],
        text=True,
        capture_output=True,
    )
    return proc.returncode == 0


def is_ancestor(repo: str, ancestor: str, descendant: str) -> bool:
    """Return whether ``ancestor`` is reachable from ``descendant``.

    Git uses exit 1 for the valid answer "not an ancestor". Any other failure
    means the gate could not evaluate and must become analysis_error.
    """
    proc = subprocess.run(
        [
            "git", "-C", repo, *_STABLE_CONFIG,
            "merge-base", "--is-ancestor", ancestor, descendant,
        ],
        text=True,
        capture_output=True,
    )
    if proc.returncode == 0:
        return True
    if proc.returncode == 1:
        return False
    raise GitPrimitiveError(
        f"merge-base --is-ancestor failed ({proc.returncode}): "
        f"{proc.stderr.strip() or 'no stderr'}"
    )


def merge_base(repo: str, left: str, right: str) -> str | None:
    """Return one common ancestor SHA, or ``None`` for unrelated histories."""
    proc = subprocess.run(
        ["git", "-C", repo, *_STABLE_CONFIG, "merge-base", left, right],
        text=True,
        capture_output=True,
    )
    if proc.returncode == 1 and not proc.stdout.strip():
        return None
    sha = proc.stdout.strip()
    if proc.returncode != 0 or not _FULL_SHA.match(sha):
        raise GitPrimitiveError(
            f"merge-base failed ({proc.returncode}): "
            f"{proc.stderr.strip() or sha or 'no output'}"
        )
    return sha


def _captured_config(repo: str, pattern: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", repo, *_STABLE_CONFIG, "config", "--null", "--get-regexp", pattern],
        capture_output=True,
    )
    if proc.returncode not in (0, 1):
        raise GitPrimitiveError(
            "cannot capture Git merge configuration: "
            + proc.stderr.decode("utf-8", errors="replace").strip()
        )
    return proc.stdout


def merge_tree_conflicts(
    repo: str,
    target: str,
    custom_head: str,
    *,
    allowed_merge_driver_config_digest: str = EMPTY_MERGE_DRIVER_CONFIG_DIGEST,
) -> MergeTreeResult:
    """Reproduce ort merge conflicts without changing the worktree.

    Git 2.38+ ``merge-tree --write-tree`` returns 0 for a clean merge and 1
    for a merge with conflicts. Both are valid results; every other exit code
    is an analysis failure. ``--name-only -z`` keeps path parsing NUL-safe.
    """
    driver_config = _captured_config(
        repo, r"^merge\..*\.(driver|recursive|name)$"
    )
    driver_digest = "sha256:" + hashlib.sha256(driver_config).hexdigest()
    if driver_digest != allowed_merge_driver_config_digest:
        raise GitPrimitiveError(
            "merge driver configuration is not allowed by the deterministic replay "
            f"policy: actual={driver_digest}, allowed={allowed_merge_driver_config_digest}"
        )
    replay_config = _captured_config(
        repo,
        r"^(diff\.renames|merge\.renames|merge\.directoryRenames|"
        r"merge\..*\.(driver|recursive|name))$",
    )
    command = (
        "merge-tree", "--write-tree", "--name-only", "-z", target, custom_head
    )
    proc = subprocess.run(
        ["git", "-C", repo, *_STABLE_CONFIG, *command],
        capture_output=True,
    )
    if proc.returncode not in (0, 1):
        raise GitPrimitiveError(
            f"git {' '.join(command)} failed ({proc.returncode}): "
            f"{proc.stderr.decode('utf-8', errors='replace').strip() or 'no stderr'}"
        )
    parts = proc.stdout.split(b"\x00")
    if not parts or not _FULL_SHA.match(parts[0].decode("ascii", errors="ignore")):
        raise GitPrimitiveError("merge-tree did not return a valid result tree SHA")
    tree_sha = parts[0].decode("ascii")
    try:
        section_end = parts.index(b"", 1)
    except ValueError:
        section_end = len(parts)
    try:
        paths = tuple(
            path
            for path in (raw.decode("utf-8") for raw in parts[1:section_end])
            if path
        )
    except UnicodeDecodeError as exc:
        raise GitPrimitiveError("merge-tree returned a non-UTF-8 path") from exc
    if len(paths) != len(set(paths)):
        raise GitPrimitiveError("merge-tree returned duplicate conflict paths")
    return MergeTreeResult(
        tree_sha=tree_sha,
        conflicted_paths=tuple(sorted(paths, key=lambda path: path.encode("utf-8"))),
        git_version=git_version(),
        command=command,
        output_digest="sha256:" + hashlib.sha256(proc.stdout).hexdigest(),
        merge_driver_config_digest=driver_digest,
        replay_config_digest="sha256:" + hashlib.sha256(replay_config).hexdigest(),
        rename_detection_policy=RENAME_DETECTION_POLICY,
    )
