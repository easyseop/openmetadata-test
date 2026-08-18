"""Safe path and deterministic tree helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from acgh.verdict import canonical_digest
from acgh.plancore.errors import PlanControlError


def resolve_within(root: str | Path, path: str | Path, *, must_exist: bool = True) -> Path:
    base = Path(root).resolve()
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = base / candidate
    resolved = candidate.resolve(strict=must_exist)
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise PlanControlError(
            "PATH_OUTSIDE_ROOT",
            f"path is outside allowed root: {candidate}",
            details={"root": str(base), "path": str(candidate)},
        ) from exc
    return resolved


def file_digest(path: str | Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def directory_digest(path: str | Path, *, allow_absent: bool = False) -> str:
    root = Path(path)
    if not root.exists():
        if allow_absent:
            return canonical_digest({"state": "absent"})
        raise PlanControlError(
            "DIRECTORY_MISSING",
            f"directory does not exist: {root}",
            details={"path": str(root)},
        )
    if not root.is_dir():
        raise PlanControlError(
            "NOT_DIRECTORY",
            f"expected directory: {root}",
            details={"path": str(root)},
        )
    entries: list[dict[str, str]] = []
    for child in sorted(root.rglob("*")):
        if child.is_symlink():
            raise PlanControlError(
                "SYMLINK_NOT_ALLOWED",
                f"symlink is not allowed in digested directory: {child}",
                details={"path": str(child)},
            )
        relative = child.relative_to(root)
        if "__pycache__" in relative.parts or child.suffix in {".pyc", ".pyo"}:
            continue
        if child.is_file():
            entries.append(
                {
                    "path": relative.as_posix(),
                    "digest": file_digest(child),
                }
            )
    return canonical_digest({"files": entries})


def list_dirty_paths(repo: str | Path) -> list[str]:
    from acgh import gitprim

    raw = gitprim.git(str(repo), "status", "--porcelain=v1", "-z")
    return sorted(record[3:] for record in raw.split("\x00") if record)
