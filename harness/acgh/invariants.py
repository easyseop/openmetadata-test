"""T30 + T31 — registration-completeness invariants (SRS P0-5).

This is the gate that makes "every core change is registered" mechanically
true, at two granularities:

T30 (commit unit) — every commit that touches an upstream-owned path must be
exactly one registered customization: exactly one Customization-ID, not a
merge, not empty, and not mixing upstream with governance changes. The critical
case is an ID-less commit that edits upstream code — the P0-5 root cause — which
is caught here, per commit, because gitprim never collapses commit boundaries.

T31 (ID unit) — across the whole candidate: an ID used by several commits must
be an authorized, contiguous series; declared dependencies must not form a
cycle; retired IDs may never be reused; and every ID on a commit must have a
manifest.

Verdict mapping (reusing the verdict engine, P0-3/P0-4):
- an unknown-ownership path -> analysis_error (fail-closed, unknown_path_policy).
- any other violation -> block.
- none -> pass.
"""
from __future__ import annotations

from dataclasses import dataclass

from acgh import gitprim
from acgh import layout as L
from acgh import verdict

# --- T30 commit-unit violation codes ---------------------------------------
MERGE_COMMIT = "merge_commit"
EMPTY_COMMIT = "empty_commit"
CORE_CHANGE_WITHOUT_ID = "core_change_without_id"
MULTIPLE_IDS = "multiple_ids"
CORE_GOVERNANCE_MIXED = "core_governance_mixed"
GOVERNANCE_TOUCHES_CORE = "governance_touches_core"
UNKNOWN_PATH = "unknown_path"  # -> analysis_error

# --- T31 ID-unit violation codes -------------------------------------------
UNREGISTERED_ID = "unregistered_id"
UNAUTHORIZED_SERIES = "unauthorized_series"
NON_CONTIGUOUS_SERIES = "non_contiguous_series"
DEPENDENCY_CYCLE = "dependency_cycle"
RETIRED_ID_REUSED = "retired_id_reused"

# Codes that mean "verification could not be trusted" rather than "rejected".
_ANALYSIS_ERROR_CODES = frozenset({UNKNOWN_PATH})


@dataclass(frozen=True)
class Violation:
    sha: str  # commit sha, or "" for whole-candidate (T31) findings
    code: str
    detail: str


def violations_to_verdict(violations: list[Violation]) -> str:
    if any(v.code in _ANALYSIS_ERROR_CODES for v in violations):
        return verdict.ANALYSIS_ERROR
    if violations:
        return verdict.BLOCK
    return verdict.PASS


def to_gate_result(name: str, violations: list[Violation]) -> verdict.GateResult:
    reasons = tuple(f"{v.code}: {v.sha[:12] or '-'} {v.detail}" for v in violations)
    return verdict.GateResult(name, violations_to_verdict(violations), reasons)


# --- T30 --------------------------------------------------------------------
def check_commit(commit: gitprim.Commit, changed: list[str], layout: L.Layout) -> list[Violation]:
    """Invariants for a single commit given its changed paths."""
    v: list[Violation] = []
    if commit.is_merge:
        # Merges are disallowed in the patch stack; classifying a merge's diff
        # is ambiguous, so we flag and stop here.
        return [Violation(commit.sha, MERGE_COMMIT, f"{len(commit.parents)} parents")]
    if not changed:
        return [Violation(commit.sha, EMPTY_COMMIT, "no file changes")]

    roles: dict[str, list[str]] = {}
    for p in changed:
        roles.setdefault(layout.classify(p), []).append(p)

    if L.UNKNOWN in roles:
        v.append(Violation(commit.sha, UNKNOWN_PATH, roles[L.UNKNOWN][0]))

    touches_upstream = L.UPSTREAM in roles
    touches_gov = L.GOVERNANCE in roles

    if touches_upstream and touches_gov:
        v.append(Violation(commit.sha, CORE_GOVERNANCE_MIXED,
                           "commit changes both upstream and governance paths"))
    if commit.change_type == "governance" and touches_upstream:
        v.append(Violation(commit.sha, GOVERNANCE_TOUCHES_CORE,
                           "Change-Type: governance but touches upstream path"))

    if touches_upstream:
        n = len(commit.customization_ids)
        if n == 0:
            v.append(Violation(commit.sha, CORE_CHANGE_WITHOUT_ID,
                               f"upstream path changed with no Customization-ID "
                               f"(e.g. {roles[L.UPSTREAM][0]})"))
        elif n > 1:
            v.append(Violation(commit.sha, MULTIPLE_IDS,
                               ",".join(commit.customization_ids)))
    return v


def check_commit_invariants(repo: str, base: str, head: str, layout: L.Layout) -> list[Violation]:
    out: list[Violation] = []
    for c in gitprim.commits(repo, base, head):
        changed = [] if c.is_merge else gitprim.changed_paths(repo, c.sha)
        out.extend(check_commit(c, changed, layout))
    return out


# --- T31 --------------------------------------------------------------------
def check_id_invariants(
    commits: list[gitprim.Commit],
    manifests_by_id: dict,
    retired_ids=frozenset(),
) -> list[Violation]:
    """Whole-candidate ID-level invariants.

    ``commits`` are in application order (oldest first). ``manifests_by_id`` maps
    Customization-ID -> validated manifest dict. Only single-ID commits are
    grouped here; 0/>1-ID commits are T30's concern.
    """
    v: list[Violation] = []
    retired = frozenset(retired_ids)

    # positions of each id across the ordered commit list (single-ID commits).
    positions: dict[str, list[int]] = {}
    for i, c in enumerate(commits):
        if len(c.customization_ids) == 1:
            positions.setdefault(c.customization_ids[0], []).append(i)

    for cid, idx in positions.items():
        if cid in retired:
            v.append(Violation(commits[idx[0]].sha, RETIRED_ID_REUSED, cid))
        manifest = manifests_by_id.get(cid)
        if manifest is None:
            v.append(Violation(commits[idx[0]].sha, UNREGISTERED_ID,
                               f"{cid} has no manifest"))
            continue
        if len(idx) > 1:
            series = manifest.get("series", {})
            if not series.get("allowed", False):
                v.append(Violation(commits[idx[0]].sha, UNAUTHORIZED_SERIES,
                                   f"{cid} spans {len(idx)} commits but series not allowed"))
            # contiguous == occupies a run with no other ID interleaved (A-3.7).
            if idx != list(range(idx[0], idx[-1] + 1)):
                v.append(Violation(commits[idx[0]].sha, NON_CONTIGUOUS_SERIES,
                                   f"{cid} commits are interleaved with other IDs"))

    v.extend(_dependency_cycles(manifests_by_id, set(positions)))
    return v


def _dependency_cycles(manifests_by_id: dict, present: set) -> list[Violation]:
    """Detect cycles in series.depends_on among present IDs (DFS)."""
    graph = {
        cid: [d for d in m.get("series", {}).get("depends_on", []) if d in present]
        for cid, m in manifests_by_id.items()
        if cid in present
    }
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    found: list[str] = []

    def dfs(n: str, stack: list[str]) -> bool:
        color[n] = GREY
        for nxt in graph.get(n, []):
            if color.get(nxt, BLACK) == GREY:
                found.append(" -> ".join(stack + [nxt]))
                return True
            if color.get(nxt, BLACK) == WHITE and dfs(nxt, stack + [nxt]):
                return True
        color[n] = BLACK
        return False

    for n in sorted(graph):
        if color[n] == WHITE and dfs(n, [n]):
            break
    return [Violation("", DEPENDENCY_CYCLE, c) for c in found]
