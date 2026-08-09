"""T42 — upgrade_watch (SRS case D, REQ-GZ / 부칙 A-3.6).

Case D is the dangerous quiet one: the upstream upgrade produces NO textual
conflict in our patches, yet a file/symbol/config we DEPEND on changed
underneath us. Registration and reapply both pass; the customization silently
rots.

This gate flags it. Each manifest declares ``upgrade_watch.paths`` — the
upstream files its customization leans on. We intersect those globs with the
NET diff of the actual upstream upgrade (UPSTREAM_A -> UPSTREAM_B). Any hit ->
approval: no automatic block (the change may be benign), but a human/LLM must
review before promotion. That review is where the Impact-Memo (T42/§7, advisory
only) attaches.

Glob grammar is the shared T05 grammar (layout.make_spec).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from acgh import gitprim
from acgh import layout as L
from acgh import verdict


@dataclass(frozen=True)
class WatchFinding:
    customization_id: str
    changed_watch_paths: tuple[str, ...]
    changed_configuration_keys: tuple[str, ...] = ()
    changed_dependencies: tuple[str, ...] = ()
    changed_watch_path_statuses: tuple[tuple[str, str], ...] = ()
    comparison: str = "range(ancestor)"


_CONFIG_SUFFIXES = {
    ".yaml", ".yml", ".json", ".toml", ".conf", ".properties",
}
_DEPENDENCY_FILES = {
    "pom.xml", "package.json", "yarn.lock", "package-lock.json",
    "pnpm-lock.yaml", "pyproject.toml", "poetry.lock", "requirements.txt",
    "build.gradle", "build.gradle.kts", "gradle.lockfile",
}


def _changed_diff(repo: str, base_ref: str, head_ref: str, path: str) -> str:
    return gitprim.git(
        repo, "diff", "--unified=0", base_ref, head_ref, "--", path
    )


def _configuration_hits(repo, base_ref, head_ref, net, keys) -> tuple[str, ...]:
    candidates = [
        path for path in net
        if PurePosixPath(path).suffix.lower() in _CONFIG_SUFFIXES
    ]
    diffs = {
        path: _changed_diff(repo, base_ref, head_ref, path)
        for path in candidates
    }
    hits = []
    for key in keys:
        tokens = tuple(part for part in key.split(".") if part)
        if tokens and any(all(token in diff for token in tokens)
                          for diff in diffs.values()):
            hits.append(key)
    return tuple(sorted(set(hits)))


def _dependency_hits(repo, base_ref, head_ref, net, dependencies) -> tuple[str, ...]:
    candidates = [
        path for path in net
        if PurePosixPath(path).name in _DEPENDENCY_FILES
        or PurePosixPath(path).name.startswith("requirements")
    ]
    diffs = {
        path: _changed_diff(repo, base_ref, head_ref, path)
        for path in candidates
    }
    return tuple(sorted({
        dependency
        for dependency in dependencies
        if any(dependency in diff for diff in diffs.values())
    }))


def evaluate_upgrade_watch(repo, base_ref, head_ref, manifests_by_id) -> list[WatchFinding]:
    """Return one finding per customization whose watched paths changed A->B."""
    changes = gitprim.net_changes(repo, base_ref, head_ref)
    net = {L.normalize_path(item.path) for item in changes}
    status_by_path = {L.normalize_path(item.path): item.status for item in changes}
    comparison = (
        "range(ancestor)"
        if gitprim.is_ancestor(repo, base_ref, head_ref)
        else "two_tree(non_ancestor)"
    )
    findings: list[WatchFinding] = []
    for cid in sorted(manifests_by_id):
        watch = manifests_by_id[cid].get("upgrade_watch", {})
        paths = watch.get("paths", [])
        spec = L.make_spec(paths)
        path_hits = tuple(sorted(p for p in net if spec.match_file(p)))
        config_hits = _configuration_hits(
            repo, base_ref, head_ref, net,
            watch.get("configuration_keys", []),
        )
        dependency_hits = _dependency_hits(
            repo, base_ref, head_ref, net,
            watch.get("dependencies", []),
        )
        if path_hits or config_hits or dependency_hits:
            findings.append(WatchFinding(
                cid,
                path_hits,
                config_hits,
                dependency_hits,
                tuple((status_by_path[path], path) for path in path_hits),
                comparison,
            ))
    return findings


def finding_payload(finding: WatchFinding) -> dict:
    """Render the full path-level evidence instead of one lossy example."""
    changes = [
        {"status": status, "path": path}
        for status, path in finding.changed_watch_path_statuses
    ]
    return {
        "customization_id": finding.customization_id,
        "comparison": finding.comparison,
        "changed_watch_paths": changes,
        "deleted_paths": [item["path"] for item in changes if item["status"] == "D"],
        "added_paths": [item["path"] for item in changes if item["status"] == "A"],
        "modified_paths": [item["path"] for item in changes if item["status"] == "M"],
        "changed_configuration_keys": list(finding.changed_configuration_keys),
        "changed_dependencies": list(finding.changed_dependencies),
    }


def review_packet(findings: list[WatchFinding]) -> dict:
    """Canonical, complete A/M/D detail for Phase evidence and human review."""
    payloads = [finding_payload(finding) for finding in findings]
    deleted = sorted({
        path
        for payload in payloads
        for path in payload["deleted_paths"]
    }, key=lambda path: path.encode("utf-8"))
    return {
        "finding_count": len(payloads),
        "deleted_paths": deleted,
        "findings": payloads,
    }


def to_gate_result(findings: list[WatchFinding],
                   name: str = "upgrade-watch") -> verdict.GateResult:
    if not findings:
        return verdict.GateResult(name, verdict.PASS, ())
    reasons = []
    for finding in findings:
        parts = []
        payload = finding_payload(finding)
        if payload["deleted_paths"]:
            parts.append(f"deleted_paths={payload['deleted_paths']}")
        if finding.changed_watch_paths:
            parts.append(
                f"paths={len(finding.changed_watch_paths)} "
                f"(full A/M/D detail in Phase gate detail)"
            )
        if finding.changed_configuration_keys:
            parts.append(
                f"configuration_keys={list(finding.changed_configuration_keys)}"
            )
        if finding.changed_dependencies:
            parts.append(f"dependencies={list(finding.changed_dependencies)}")
        reasons.append(
            f"{finding.customization_id}: {finding.comparison} changed "
            + ", ".join(parts)
        )
    return verdict.GateResult(name, verdict.APPROVAL, tuple(reasons))
