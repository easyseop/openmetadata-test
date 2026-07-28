"""T42-A — deterministic upgrade-watch candidate suggestions.

This is a suggestion provider, not a verdict gate.  During an upstream
upgrade it looks only at files that actually changed A->B, then proposes a
changed file when one of the customization's exact implementation files
directly references that file's symbol/basename.  Existing allowed/watch paths
are excluded.  A code owner must review and accept a proposal before it enters
the manifest.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from acgh import gitprim
from acgh import layout as L


@dataclass(frozen=True)
class WatchSuggestion:
    customization_id: str
    suggested_path: str
    referenced_from: tuple[str, ...]
    reason: str = "changed upstream file is directly referenced by customization code"


def _symbol(path: str) -> str | None:
    name = PurePosixPath(path).name
    stem = name.split(".", 1)[0]
    if stem in {"index", "__init__", "package"} or len(stem) < 4:
        return None
    return stem


def _blob(repo: str, ref: str, path: str) -> str:
    try:
        return gitprim.git(repo, "show", f"{ref}:{path}")
    except Exception:
        return ""


def suggest_watch_paths(
    repo: str,
    upstream_base: str,
    upstream_target: str,
    candidate_ref: str,
    manifests_by_id: dict[str, dict],
) -> list[WatchSuggestion]:
    changed = tuple(sorted({
        L.normalize_path(path)
        for path in gitprim.net_changed_paths(repo, upstream_base, upstream_target)
    }))
    candidate_files = set(gitprim.list_tree_recursive(repo, candidate_ref))
    content_cache: dict[str, str] = {}
    suggestions: list[WatchSuggestion] = []

    for customization_id in sorted(manifests_by_id):
        manifest = manifests_by_id[customization_id]
        implementation = manifest.get("implementation", {})
        allowed = tuple(
            L.ensure_literal(path)
            for path in [
                *implementation.get("allowed_changed_paths", []),
                *implementation.get("candidate_additional_paths", []),
            ]
        )
        watched = L.make_spec(
            manifest.get("upgrade_watch", {}).get("paths", [])
        )
        for changed_path in changed:
            if changed_path in allowed or watched.match_file(changed_path):
                continue
            symbol = _symbol(changed_path)
            if symbol is None:
                continue
            pattern = re.compile(rf"(?<![A-Za-z0-9_$]){re.escape(symbol)}"
                                 r"(?![A-Za-z0-9_$])")
            refs = []
            for source_path in allowed:
                if source_path not in candidate_files:
                    continue
                if source_path not in content_cache:
                    content_cache[source_path] = _blob(
                        repo, candidate_ref, source_path
                    )
                if pattern.search(content_cache[source_path]):
                    refs.append(source_path)
            if refs:
                suggestions.append(WatchSuggestion(
                    customization_id,
                    changed_path,
                    tuple(sorted(refs)),
                ))
    return suggestions


def review_packet(suggestions: list[WatchSuggestion]) -> dict:
    return {
        "suggestion_count": len(suggestions),
        "authority": "code-owner-review-required",
        "suggestions": [
            {
                "customization_id": item.customization_id,
                "suggested_path": item.suggested_path,
                "referenced_from": list(item.referenced_from),
                "reason": item.reason,
            }
            for item in suggestions
        ],
    }
