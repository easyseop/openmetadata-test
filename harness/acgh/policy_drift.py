"""T93 — sensitive/watch policy-staleness drift (SRS §10.5 · C-2).

Distinct from T42 (which asks "did a watched file CHANGE A->B?"). T93 asks
whether our POLICY itself has gone stale against the new upstream: a sensitive
or watch glob that matched real files in the old version but matches NOTHING in
the new one is an "empty gun" — it will keep reporting pass while guarding
thin air, because an upstream refactor moved the code out from under it. And a
new top-level module the ownership map has never heard of must not be silently
treated as unowned.

Checks against the NEW upstream tree:
- stale_patterns: each policy glob must match >= 1 path -> else approval
  (someone must update the policy before trusting it).
- unclassified top-level modules: a new top-level directory that classifies to
  UNKNOWN -> analysis_error (fail-closed; the ownership map must be extended
  before it can judge changes there).
"""
from __future__ import annotations

from acgh import gitprim
from acgh import layout as L
from acgh import verdict

STALE_PATTERN = "stale_pattern"
UNCLASSIFIED_MODULE = "unclassified_toplevel_module"
OBSERVED_OUTSIDE_SCOPE = "observed_path_outside_exact_scope"
DECLARED_BUT_UNOBSERVED = "declared_path_not_observed"
NON_LITERAL_SCOPE = "non_literal_exact_scope"


def stale_patterns(repo, ref, patterns) -> list[str]:
    """Policy globs that match zero paths in ``ref``'s tree (empty guns)."""
    files = gitprim.list_tree_recursive(repo, ref)
    stale = []
    for pat in patterns:
        spec = L.make_spec([pat])
        if not any(spec.match_file(f) for f in files):
            stale.append(pat)
    return stale


def unclassified_toplevel_modules(
    repo, ref, layout: L.Layout, baseline_ref=None
) -> list[str]:
    """Top-level directories added after baseline that remain unclassified."""
    baseline = baseline_ref or layout.upstream_base_sha
    previous = set(gitprim.list_tree(repo, baseline, dirs_only=True))
    out = []
    current = set(gitprim.list_tree(repo, ref, dirs_only=True))
    for d in sorted(current - previous):
        if layout.classify(f"{d}/_probe") == L.UNKNOWN:
            out.append(d)
    return out


def check_policy_drift(
    repo, ref, patterns, layout: L.Layout, *, baseline_ref=None
) -> verdict.GateResult:
    stale = stale_patterns(repo, ref, patterns)
    unclassified = unclassified_toplevel_modules(
        repo, ref, layout, baseline_ref=baseline_ref
    )
    reasons = tuple(f"{STALE_PATTERN}: {p} matches 0 paths in {ref}" for p in stale) \
        + tuple(f"{UNCLASSIFIED_MODULE}: {d}" for d in unclassified)
    if unclassified:
        v = verdict.ANALYSIS_ERROR   # fail-closed: map can't judge this zone yet
    elif stale:
        v = verdict.APPROVAL         # policy must be refreshed before trust
    else:
        v = verdict.PASS
    return verdict.GateResult("policy-drift", v, reasons)


def check_exact_scope_history(
    repo: str,
    base_ref: str,
    head_ref: str,
    manifests_by_id: dict[str, dict],
) -> verdict.GateResult:
    """Compare every ID's declared exact scope with its observed commit history.

    An observed path outside the declaration is a block (omission).  A declared
    path never touched by that ID is approval (the scope is broader/stale and
    must be justified or reduced).  Non-literal declarations are
    analysis_error because exact equality cannot be evaluated.
    """
    observed: dict[str, set[str]] = {}
    for commit in gitprim.commits(repo, base_ref, head_ref):
        if len(commit.customization_ids) != 1:
            continue  # T30 owns missing/multiple IDs.
        customization_id = commit.customization_ids[0]
        observed.setdefault(customization_id, set()).update(
            L.normalize_path(path)
            for path in gitprim.changed_paths(repo, commit.sha)
        )

    analysis: list[str] = []
    blocks: list[str] = []
    approvals: list[str] = []
    for customization_id in sorted(set(observed) | set(manifests_by_id)):
        manifest = manifests_by_id.get(customization_id)
        if manifest is None:
            continue  # T31 owns unregistered IDs.
        declared = set()
        implementation = manifest.get("implementation", {})
        for raw in [
            *implementation.get("allowed_changed_paths", []),
            *implementation.get("candidate_additional_paths", []),
        ]:
            try:
                declared.add(L.ensure_literal(raw))
            except L.LayoutError as exc:
                analysis.append(
                    f"{customization_id} {NON_LITERAL_SCOPE}: {raw}: {exc}"
                )
        observed_paths = observed.get(customization_id, set())
        missing = sorted(observed_paths - declared)
        extra = sorted(declared - observed_paths)
        if missing:
            blocks.append(
                f"{customization_id} {OBSERVED_OUTSIDE_SCOPE}: {missing}"
            )
        if extra:
            approvals.append(
                f"{customization_id} {DECLARED_BUT_UNOBSERVED}: {extra}"
            )
    if analysis:
        state = verdict.ANALYSIS_ERROR
    elif blocks:
        state = verdict.BLOCK
    elif approvals:
        state = verdict.APPROVAL
    else:
        state = verdict.PASS
    reasons = tuple(analysis + blocks + approvals)
    if not reasons:
        reasons = ("declared exact scopes equal observed per-ID history",)
    return verdict.GateResult("exact-scope-history", state, reasons)
