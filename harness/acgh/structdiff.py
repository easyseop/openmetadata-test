"""T51/T52 — structured diff provider (evidence, SRS 계층 2 / REQ-EV).

An EVIDENCE provider, not a gate: it extracts the *structural facts* of how a
document changed between two upstream versions — which keys were added/removed,
which types changed — so a human/LLM review (and the T42 impact memo) has a
deterministic basis instead of eyeballing a raw text diff. It renders no verdict
(계층 2 boundary): facts only, judgment elsewhere.

Docker-free: works entirely from the fixed mirror (`git show ref:path`), so it
covers a large part of case D (a JSON Schema / API contract we depend on gained
or changed a field) without booting the OM stack.

The provider reports object-key presence, type changes, same-type scalar value
changes, and same-type list content changes.  Lists are reported at their
document path rather than element-by-element to avoid noisy or unstable index
interpretation.
"""
from __future__ import annotations

from dataclasses import dataclass

import yaml

from acgh import gitprim


def _typename(v) -> str:
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, dict):
        return "object"
    if isinstance(v, list):
        return "array"
    if isinstance(v, str):
        return "string"
    if isinstance(v, (int, float)):
        return "number"
    if v is None:
        return "null"
    return type(v).__name__


@dataclass(frozen=True)
class StructDiff:
    added: tuple[str, ...]                      # paths present in new, not old
    removed: tuple[str, ...]                    # paths present in old, not new
    type_changed: tuple[tuple[str, str, str], ...]  # (path, old_type, new_type)
    scalar_changed: tuple[str, ...]
    list_changed: tuple[str, ...]

    @property
    def is_empty(self) -> bool:
        return not (
            self.added or self.removed or self.type_changed
            or self.scalar_changed or self.list_changed
        )

    def summary(self) -> str:
        return (
            f"+{len(self.added)} -{len(self.removed)} "
            f"~type:{len(self.type_changed)} "
            f"~scalar:{len(self.scalar_changed)} "
            f"~list:{len(self.list_changed)}"
        )


def _walk(old, new, prefix, added, removed, changed, scalar, lists) -> None:
    if isinstance(old, dict) and isinstance(new, dict):
        for k in new:
            path = f"{prefix}/{k}"
            if k not in old:
                added.append(path)
            else:
                _walk(
                    old[k], new[k], path,
                    added, removed, changed, scalar, lists,
                )
        for k in old:
            if k not in new:
                removed.append(f"{prefix}/{k}")
        return
    if isinstance(old, list) and isinstance(new, list):
        if old != new:
            lists.append(prefix or "/")
        return
    to, tn = _typename(old), _typename(new)
    if to != tn:
        changed.append((prefix or "/", to, tn))
    elif old != new:
        scalar.append(prefix or "/")


def structural_diff(old, new) -> StructDiff:
    added: list[str] = []
    removed: list[str] = []
    changed: list[tuple[str, str, str]] = []
    scalar: list[str] = []
    lists: list[str] = []
    _walk(old, new, "", added, removed, changed, scalar, lists)
    return StructDiff(
        tuple(sorted(added)),
        tuple(sorted(removed)),
        tuple(sorted(changed)),
        tuple(sorted(scalar)),
        tuple(sorted(lists)),
    )


def load_doc_at(repo: str, ref: str, path: str):
    """Load and parse a JSON/YAML document at a git ref (yaml parses JSON too)."""
    return yaml.safe_load(gitprim.git(repo, "show", f"{ref}:{path}"))


def diff_file(repo: str, old_ref: str, new_ref: str, path: str) -> StructDiff:
    """Structural diff of one document between two refs."""
    return structural_diff(
        load_doc_at(repo, old_ref, path),
        load_doc_at(repo, new_ref, path),
    )
