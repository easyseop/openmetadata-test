"""T51/T52 — structured diff provider (evidence, SRS 계층 2 / REQ-EV).

An EVIDENCE provider, not a gate: it extracts the *structural facts* of how a
document changed between two upstream versions — which keys were added/removed,
which types changed — so a human/LLM review (and the T42 impact memo) has a
deterministic basis instead of eyeballing a raw text diff. It renders no verdict
(계층 2 boundary): facts only, judgment elsewhere.

Docker-free: works entirely from the fixed mirror (`git show ref:path`), so it
covers a large part of case D (a JSON Schema / API contract we depend on gained
or changed a field) without booting the OM stack.

MVP scope: object-key presence and scalar/container type changes. Element-wise
list diffing is intentionally omitted (noisy); a changed list type still surfaces
as a type change.
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

    @property
    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.type_changed)

    def summary(self) -> str:
        return (f"+{len(self.added)} -{len(self.removed)} "
                f"~{len(self.type_changed)} (added/removed/type-changed)")


def _walk(old, new, prefix, added, removed, changed) -> None:
    if isinstance(old, dict) and isinstance(new, dict):
        for k in new:
            path = f"{prefix}/{k}"
            if k not in old:
                added.append(path)
            else:
                _walk(old[k], new[k], path, added, removed, changed)
        for k in old:
            if k not in new:
                removed.append(f"{prefix}/{k}")
        return
    to, tn = _typename(old), _typename(new)
    if to != tn:
        changed.append((prefix or "/", to, tn))


def structural_diff(old, new) -> StructDiff:
    added: list[str] = []
    removed: list[str] = []
    changed: list[tuple[str, str, str]] = []
    _walk(old, new, "", added, removed, changed)
    return StructDiff(
        tuple(sorted(added)),
        tuple(sorted(removed)),
        tuple(sorted(changed)),
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
