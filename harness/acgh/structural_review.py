"""Deterministic structural-upgrade review and relocation diagnostics.

This module deliberately separates two jobs:

* canonical review classification uses rename detection disabled and can affect
  gate evidence; and
* rename/token diagnostics only propose paths for human review and never turn a
  missing shared-code definition into PASS.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath

import yaml

from acgh import gitprim
from acgh import layout as layout_module
from acgh import shared_code
from acgh import verdict


NEITHER_PARENT_CHANGED = "NEITHER_PARENT_CHANGED"
TARGET_ONLY = "TARGET_ONLY"
CUSTOM_ONLY = "CUSTOM_ONLY"
BOTH_CHANGED_PARENTS_AGREE = "BOTH_CHANGED_PARENTS_AGREE"
BOTH_CHANGED_PARENTS_DIVERGE = "BOTH_CHANGED_PARENTS_DIVERGE"

EQUALS_BOTH_PARENTS = "EQUALS_BOTH_PARENTS"
EQUALS_TARGET = "EQUALS_TARGET"
EQUALS_CUSTOM = "EQUALS_CUSTOM"
DIFFERS_FROM_BOTH = "DIFFERS_FROM_BOTH"

CUSTOM_LOSS_SUSPECT = "CUSTOM_LOSS_SUSPECT"
OFFICIAL_LOSS_SUSPECT = "OFFICIAL_LOSS_SUSPECT"
REVERTED_TO_MERGE_BASE = "REVERTED_TO_MERGE_BASE"


class StructuralReviewError(ValueError):
    """Structural review inputs cannot produce trustworthy evidence."""


@dataclass(frozen=True)
class PathFinding:
    path: str
    change_origin: str
    result_relation: str
    risk_flags: tuple[str, ...]
    diagnostic_flags: tuple[str, ...]
    related_customization_ids: tuple[str, ...]
    statuses: dict[str, str | None]
    states: dict[str, str | None]


def _state(entry: gitprim.TreeEntry | None) -> str | None:
    if entry is None:
        return None
    return f"{entry.mode}:{entry.object_type}:{entry.object_id}"


def _origin(base, target, custom) -> str:
    target_changed = target != base
    custom_changed = custom != base
    if not target_changed and not custom_changed:
        return NEITHER_PARENT_CHANGED
    if target_changed and not custom_changed:
        return TARGET_ONLY
    if custom_changed and not target_changed:
        return CUSTOM_ONLY
    return (
        BOTH_CHANGED_PARENTS_AGREE
        if target == custom
        else BOTH_CHANGED_PARENTS_DIVERGE
    )


def _relation(target, custom, candidate) -> str:
    if candidate == target == custom:
        return EQUALS_BOTH_PARENTS
    if candidate == target:
        return EQUALS_TARGET
    if candidate == custom:
        return EQUALS_CUSTOM
    return DIFFERS_FROM_BOTH


def _manifest_specs(manifests_by_id: dict[str, dict]):
    specs = {}
    for customization_id, manifest in manifests_by_id.items():
        patterns = set(manifest.get("upgrade_watch", {}).get("paths", []))
        patterns.update(manifest.get("implementation", {}).get("changed_paths", []))
        if patterns:
            specs[customization_id] = layout_module.make_spec(sorted(patterns))
    return specs


def _diagnostic_payload(repo, base, head, label, threshold):
    warnings: list[str] = []
    try:
        report = gitprim.diagnostic_rename_report(
            repo, base, head, threshold=threshold
        )
        findings = report.findings
        warnings.extend(report.warnings)
        degraded = report.degraded
        timeout_seconds = report.timeout_seconds
        config = list(report.config)
    except gitprim.GitPrimitiveError as exc:
        findings = ()
        warnings.append(str(exc))
        degraded = True
        timeout_seconds = 30.0
        config = ["diff.renameLimit=0"]
    try:
        version = gitprim.git_version()
    except gitprim.GitPrimitiveError as exc:
        version = "unknown"
        warnings.append(str(exc))
        degraded = True
    try:
        binary_paths = list(gitprim.binary_changed_paths(repo, base, head))
    except gitprim.GitPrimitiveError as exc:
        binary_paths = []
        warnings.append(str(exc))
        degraded = True
    return {
        "comparison": label,
        "policy": f"diagnostic(-M -C, threshold={threshold}%)",
        "git_version": version,
        "degraded": degraded,
        "warnings": warnings,
        "timeout_seconds": timeout_seconds,
        "config": config,
        "binary_paths": binary_paths,
        "findings": [asdict(item) for item in findings],
    }


def _canonical_projection(payload: dict) -> dict:
    """Return only decision-bearing fields covered by ``review_digest``."""
    if payload.get("schema_version") != 2:
        raise StructuralReviewError("structural review schema_version must be 2")
    raw_findings = payload.get("findings")
    if not isinstance(raw_findings, list):
        raise StructuralReviewError("structural review findings must be a list")
    canonical_findings = []
    required = (
        "path", "change_origin", "result_relation", "risk_flags",
        "related_customization_ids", "statuses", "states",
    )
    for finding in raw_findings:
        if not isinstance(finding, dict) or any(key not in finding for key in required):
            raise StructuralReviewError("structural review finding is incomplete")
        canonical_findings.append({key: finding[key] for key in required})
    required_top = ("refs", "canonical_policy", "review_surface_paths")
    if any(key not in payload for key in required_top):
        raise StructuralReviewError("structural review canonical fields are incomplete")
    return {
        "schema_version": 2,
        "refs": payload["refs"],
        "canonical_policy": payload["canonical_policy"],
        "review_surface_paths": payload["review_surface_paths"],
        "findings": canonical_findings,
    }


def _diagnostic_projection(payload: dict) -> dict:
    """Bind stored diagnostics to themselves without rerunning them."""
    return {
        "rename_diagnostics": payload.get("rename_diagnostics", []),
        "path_diagnostic_flags": [
            {
                "path": finding.get("path"),
                "diagnostic_flags": finding.get("diagnostic_flags", []),
            }
            for finding in payload.get("findings", [])
        ],
    }


def build_review(
    repo: str,
    merge_base_sha: str,
    target_sha: str,
    custom_head_sha: str,
    candidate_sha: str,
    manifests_by_id: dict[str, dict],
    *,
    zones=None,
    diagnostic_threshold: int = 50,
    include_diagnostics: bool = True,
) -> dict:
    """Build the complete three-set review surface and its orthogonal axes."""
    refs = {
        "merge_base": merge_base_sha,
        "target": target_sha,
        "custom_head": custom_head_sha,
        "candidate": candidate_sha,
    }
    trees = {name: gitprim.tree_entries(repo, ref) for name, ref in refs.items()}
    comparisons = {
        "base_to_target": gitprim.net_changes(repo, merge_base_sha, target_sha),
        "base_to_custom": gitprim.net_changes(repo, merge_base_sha, custom_head_sha),
        "base_to_candidate": gitprim.net_changes(repo, merge_base_sha, candidate_sha),
    }
    status_maps = {
        name: {item.path: item.status for item in changes}
        for name, changes in comparisons.items()
    }
    review_paths = sorted(
        {
            item.path
            for changes in comparisons.values()
            for item in changes
        },
        key=lambda path: path.encode("utf-8"),
    )
    specs = _manifest_specs(manifests_by_id)
    diagnostics = (
        [
            _diagnostic_payload(
                repo, merge_base_sha, ref, name, diagnostic_threshold
            )
            for name, ref in (
                ("merge_base_to_target", target_sha),
                ("merge_base_to_custom", custom_head_sha),
                ("merge_base_to_candidate", candidate_sha),
            )
        ]
        if include_diagnostics
        else []
    )
    rename_paths = {
        path
        for packet in diagnostics
        for item in packet["findings"]
        for path in (item["old_path"], item["new_path"])
    }
    binary_paths = {
        path
        for packet in diagnostics
        for path in packet.get("binary_paths", [])
    }

    findings: list[PathFinding] = []
    for path in review_paths:
        base = _state(trees["merge_base"].get(path))
        target = _state(trees["target"].get(path))
        custom = _state(trees["custom_head"].get(path))
        candidate = _state(trees["candidate"].get(path))
        origin = _origin(base, target, custom)
        relation = _relation(target, custom, candidate)
        related_ids = tuple(sorted(
            customization_id
            for customization_id, spec in specs.items()
            if spec.match_file(path)
        ))
        flags: set[str] = set()
        diagnostic_flags: set[str] = set()
        if base is None and candidate is not None:
            flags.add("PATH_ADDED")
        if base is not None and candidate is None:
            flags.add("PATH_DELETED")
        if path in rename_paths:
            diagnostic_flags.add("POSSIBLE_RENAME")
        if path in binary_paths:
            diagnostic_flags.add("BINARY")
        if related_ids:
            flags.add("MANIFEST_WATCHED")
        if zones is not None:
            zone = zones.zone_of(path)
            if zone is not None:
                flags.add(zone.upper())
        if custom != base and candidate == target and target != custom:
            flags.add(CUSTOM_LOSS_SUSPECT)
        if target != base and candidate == custom and target != custom:
            flags.add(OFFICIAL_LOSS_SUSPECT)
        if target != base and custom != base and candidate == base:
            flags.update({
                CUSTOM_LOSS_SUSPECT,
                OFFICIAL_LOSS_SUSPECT,
                REVERTED_TO_MERGE_BASE,
            })
        findings.append(PathFinding(
            path=path,
            change_origin=origin,
            result_relation=relation,
            risk_flags=tuple(sorted(flags)),
            diagnostic_flags=tuple(sorted(diagnostic_flags)),
            related_customization_ids=related_ids,
            statuses={
                name: status_maps[name].get(path)
                for name in sorted(status_maps)
            },
            states={name: value for name, value in (
                ("merge_base", base),
                ("target", target),
                ("custom_head", custom),
                ("candidate", candidate),
            )},
        ))

    payload = {
        "schema_version": 2,
        "refs": refs,
        "canonical_policy": "rename_detection=disabled (--no-renames)",
        "review_surface_paths": review_paths,
        "findings": [
            {
                "path": item.path,
                "change_origin": item.change_origin,
                "result_relation": item.result_relation,
                "risk_flags": list(item.risk_flags),
                "diagnostic_flags": list(item.diagnostic_flags),
                "related_customization_ids": list(item.related_customization_ids),
                "statuses": item.statuses,
                "states": item.states,
            }
            for item in findings
        ],
        "rename_diagnostics": diagnostics,
    }
    payload["diagnostics_digest"] = verdict.canonical_digest(
        _diagnostic_projection(payload)
    )
    payload["review_digest"] = verdict.canonical_digest(
        _canonical_projection(payload)
    )
    return payload


def verify_review(repo: str, payload: dict, manifests_by_id: dict[str, dict], *, zones=None) -> None:
    """Recompute structural evidence; any omission or extra path is an error."""
    if not isinstance(payload, dict):
        raise StructuralReviewError("structural review evidence must be a mapping")
    refs = payload.get("refs")
    if not isinstance(refs, dict):
        raise StructuralReviewError("structural review evidence has no refs mapping")
    required = ("merge_base", "target", "custom_head", "candidate")
    if any(not isinstance(refs.get(name), str) for name in required):
        raise StructuralReviewError("structural review evidence has incomplete refs")
    expected_review_digest = verdict.canonical_digest(_canonical_projection(payload))
    if payload.get("review_digest") != expected_review_digest:
        raise StructuralReviewError("structural review canonical digest mismatch")
    expected_diagnostics_digest = verdict.canonical_digest(
        _diagnostic_projection(payload)
    )
    if payload.get("diagnostics_digest") != expected_diagnostics_digest:
        raise StructuralReviewError("structural review diagnostics digest mismatch")
    recomputed = build_review(
        repo,
        refs["merge_base"],
        refs["target"],
        refs["custom_head"],
        refs["candidate"],
        manifests_by_id,
        zones=zones,
        include_diagnostics=False,
    )
    if _canonical_projection(payload) != _canonical_projection(recomputed):
        raise StructuralReviewError(
            "structural review canonical evidence differs from deterministic recomputation"
        )


def _path_context(path: str) -> str:
    lowered = path.lower()
    name = PurePosixPath(path).name.lower()
    if any(part in lowered for part in ("/test/", "/tests/", "/__tests__/")):
        return "test"
    if ".test." in name or ".spec." in name or name.endswith(".snap"):
        return "test"
    if any(part in lowered for part in ("/generated/", "/dist/", "/build/", "/target/")):
        return "generated"
    return "source"


def _definition_digest(definition: shared_code.Definition) -> str:
    return verdict.canonical_digest({
        "path": definition.path,
        "customization_id": definition.customization_id,
        "assertions": list(definition.assertions),
    })


def _suffix_group(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix in {".ts", ".tsx"}:
        return "typescript"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    return suffix


_WEAK_CODE_TOKENS = {
    "break", "case", "const", "default", "else", "export", "from",
    "function", "if", "import", "let", "new", "return", "switch", "var",
}


def _meaningful_tokens(assertions: tuple[dict, ...], suffix: str) -> set[str]:
    result: set[str] = set()
    for assertion in assertions:
        if assertion["matcher"] != "code_fragment":
            continue
        for token in shared_code._code_tokens(assertion["fragment"], suffix):
            if token.startswith("STRING:"):
                if len(token) >= 10:
                    result.add(token)
            elif (
                any(character.isalnum() for character in token)
                and len(token) >= 3
                and token.lower() not in _WEAK_CODE_TOKENS
            ):
                result.add(token)
    return result


def find_relocations(
    repo: str,
    candidate_sha: str,
    catalog: shared_code.Catalog,
    review_surface_paths: list[str] | tuple[str, ...],
) -> dict:
    """Find relocation candidates but never promote a candidate automatically."""
    tree = gitprim.tree_entries(repo, candidate_sha)
    searchable = sorted(
        set(review_surface_paths) & set(tree),
        key=lambda path: path.encode("utf-8"),
    )
    paths_by_suffix: dict[str, list[str]] = {}
    for path in searchable:
        paths_by_suffix.setdefault(_suffix_group(path), []).append(path)
    raw_cache: dict[str, bytes] = {}
    text_cache: dict[str, str] = {}
    token_cache: dict[str, tuple[str, ...]] = {}
    json_cache: dict[str, object] = {}
    yaml_cache: dict[str, object] = {}

    def raw_for(path: str) -> bytes:
        if path not in raw_cache:
            raw_cache[path] = gitprim.blob_bytes(repo, candidate_sha, path)
        return raw_cache[path]

    def text_for(path: str) -> str:
        if path not in text_cache:
            text_cache[path] = raw_for(path).decode("utf-8")
        return text_cache[path]

    def assertion_matches(path: str, assertion: dict) -> bool:
        suffix = PurePosixPath(path).suffix.lower()
        try:
            matcher = assertion["matcher"]
            if matcher == "code_fragment":
                if path not in token_cache:
                    token_cache[path] = shared_code._code_tokens(text_for(path), suffix)
                fragment = shared_code._code_tokens(assertion["fragment"], suffix)
                actual = shared_code._subsequence_count(token_cache[path], fragment)
                return actual == assertion.get("occurrences", 1)
            if matcher == "json_value":
                if path not in json_cache:
                    json_cache[path] = json.loads(text_for(path))
                return shared_code._pointer_value(
                    json_cache[path], assertion["pointer"]
                ) == assertion["expected"]
            if path not in yaml_cache:
                yaml_cache[path] = yaml.safe_load(text_for(path))
            return shared_code._pointer_value(
                yaml_cache[path], assertion["pointer"]
            ) == assertion["expected"]
        except (
            gitprim.GitPrimitiveError,
            UnicodeError,
            ValueError,
            TypeError,
            KeyError,
            yaml.YAMLError,
        ):
            return False

    def matches(path: str, definition: shared_code.Definition) -> bool:
        return all(assertion_matches(path, item) for item in definition.assertions)

    findings = []
    for definition in catalog.definitions:
        old_error = None
        if definition.path in tree and matches(definition.path, definition):
            continue
        try:
            old_text = text_for(definition.path)
            old_error = "; ".join(shared_code._check_definition(old_text, definition))
        except (
            gitprim.GitPrimitiveError,
            UnicodeError,
            ValueError,
            TypeError,
            yaml.YAMLError,
        ) as exc:
            old_error = str(exc)

        suffix = PurePosixPath(definition.path).suffix.lower()
        group = _suffix_group(definition.path)
        definition_tokens = _meaningful_tokens(definition.assertions, suffix)
        candidates = []
        for path in paths_by_suffix.get(group, []):
            if path == definition.path:
                continue
            exact_matches = sum(
                assertion_matches(path, assertion)
                for assertion in definition.assertions
            )
            candidate_tokens = set(token_cache.get(path, ()))
            if group == "typescript" and path not in token_cache:
                try:
                    token_cache[path] = shared_code._code_tokens(
                        text_for(path), PurePosixPath(path).suffix.lower()
                    )
                    candidate_tokens = set(token_cache[path])
                except (gitprim.GitPrimitiveError, UnicodeError):
                    candidate_tokens = set()
            overlap = sorted(definition_tokens & candidate_tokens)
            exact_definition = exact_matches == len(definition.assertions)
            symbol_candidate = (
                bool(definition_tokens)
                and len(overlap) >= 2
                and len(overlap) / len(definition_tokens) >= 0.30
            )
            if not exact_definition and exact_matches == 0 and not symbol_candidate:
                continue
            raw = raw_for(path)
            context = _path_context(path)
            strength = (
                "exact_definition"
                if exact_definition
                else "partial_assertion"
                if exact_matches
                else "symbol_overlap"
            )
            candidates.append({
                "path": path,
                "blob_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "context": context,
                "eligible_for_migration": context == "source",
                "evidence_strength": strength,
                "matched_assertion_count": exact_matches,
                "assertion_count": len(definition.assertions),
                "symbol_overlap_count": len(overlap),
                "symbol_token_count": len(definition_tokens),
                "matched_symbols": overlap,
            })
        strength_order = {
            "exact_definition": 0,
            "partial_assertion": 1,
            "symbol_overlap": 2,
        }
        candidates.sort(key=lambda item: (
            strength_order[item["evidence_strength"]],
            -item["matched_assertion_count"],
            -item["symbol_overlap_count"],
            item["path"].encode("utf-8"),
        ))
        eligible = [item for item in candidates if item["eligible_for_migration"]]
        finding_verdict = verdict.APPROVAL if eligible else verdict.BLOCK
        findings.append({
            "customization_id": definition.customization_id,
            "definition_id": f"{definition.customization_id}:{definition.path}",
            "old_definition_digest": _definition_digest(definition),
            "old_path": definition.path,
            "old_path_result": old_error,
            "verdict": finding_verdict,
            "candidate_count": len(candidates),
            "eligible_candidate_count": len(eligible),
            "candidates": candidates,
        })
    overall = verdict.aggregate([item["verdict"] for item in findings]) if findings else verdict.PASS
    return {
        "schema_version": 1,
        "candidate_sha": candidate_sha,
        "verdict": overall,
        "finding_count": len(findings),
        "findings": findings,
        "rule": (
            "candidate discovery is diagnostic only; human approval and a versioned "
            "definition migration are required before PASS"
        ),
    }


def to_gate_result(review: dict, relocation: dict) -> verdict.GateResult:
    """Require review for loss suspects and block unresolved shared definitions."""
    if not isinstance(review, dict) or not isinstance(relocation, dict):
        return verdict.GateResult(
            "structural-review",
            verdict.ANALYSIS_ERROR,
            ("structural or relocation evidence is missing",),
        )
    priority = []
    for finding in review.get("findings", []):
        flags = set(finding.get("risk_flags", []))
        selected = sorted(flags & {CUSTOM_LOSS_SUSPECT, OFFICIAL_LOSS_SUSPECT})
        if selected:
            priority.append(
                f"{finding.get('path')}: {','.join(selected)} "
                f"({finding.get('change_origin')} + {finding.get('result_relation')})"
            )
    relocation_verdict = relocation.get("verdict")
    reasons = list(priority)
    if relocation_verdict == verdict.BLOCK:
        reasons.append(
            f"shared definition relocation unresolved: findings={relocation.get('finding_count', 0)}"
        )
        result = verdict.BLOCK
    elif relocation_verdict == verdict.APPROVAL:
        reasons.append(
            "shared definition relocation candidates require human approval and versioned migration"
        )
        result = verdict.APPROVAL
    elif relocation_verdict not in {verdict.PASS, None}:
        return verdict.GateResult(
            "structural-review",
            verdict.ANALYSIS_ERROR,
            (f"unknown relocation verdict: {relocation_verdict!r}",),
        )
    else:
        result = verdict.APPROVAL if priority else verdict.PASS
    return verdict.GateResult("structural-review", result, tuple(reasons))


def gate_detail(review: dict, relocation: dict) -> dict:
    """Compact gate detail; the full classifications remain in conflict evidence."""
    counts: dict[str, int] = {}
    loss_suspects = []
    deleted = []
    for finding in review.get("findings", []):
        origin = finding.get("change_origin")
        counts[origin] = counts.get(origin, 0) + 1
        flags = set(finding.get("risk_flags", []))
        if flags & {CUSTOM_LOSS_SUSPECT, OFFICIAL_LOSS_SUSPECT}:
            loss_suspects.append(finding.get("path"))
        if "PATH_DELETED" in flags:
            deleted.append(finding.get("path"))
    return {
        "review_digest": review.get("review_digest"),
        "review_surface_path_count": len(review.get("review_surface_paths", [])),
        "change_origin_counts": dict(sorted(counts.items())),
        "loss_suspect_paths": sorted(set(loss_suspects)),
        "deleted_paths": sorted(set(deleted)),
        "relocation_verdict": relocation.get("verdict"),
        "relocation_finding_count": relocation.get("finding_count", 0),
        "full_detail_location": "conflict evidence structural_review/relocation_review",
    }
