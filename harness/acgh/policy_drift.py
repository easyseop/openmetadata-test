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


def stale_patterns(repo, ref, patterns) -> list[str]:
    """Policy globs that match zero paths in ``ref``'s tree (empty guns)."""
    files = gitprim.list_tree_recursive(repo, ref)
    stale = []
    for pat in patterns:
        spec = L.make_spec([pat])
        if not any(spec.match_file(f) for f in files):
            stale.append(pat)
    return stale


def unclassified_toplevel_modules(repo, ref, layout: L.Layout) -> list[str]:
    """New top-level directories the ownership map cannot classify."""
    out = []
    for d in gitprim.list_tree(repo, ref, dirs_only=True):
        if layout.classify(f"{d}/_probe") == L.UNKNOWN:
            out.append(d)
    return out


def check_policy_drift(repo, ref, patterns, layout: L.Layout) -> verdict.GateResult:
    stale = stale_patterns(repo, ref, patterns)
    unclassified = unclassified_toplevel_modules(repo, ref, layout)
    reasons = tuple(f"{STALE_PATTERN}: {p} matches 0 paths in {ref}" for p in stale) \
        + tuple(f"{UNCLASSIFIED_MODULE}: {d}" for d in unclassified)
    if unclassified:
        v = verdict.ANALYSIS_ERROR   # fail-closed: map can't judge this zone yet
    elif stale:
        v = verdict.APPROVAL         # policy must be refreshed before trust
    else:
        v = verdict.PASS
    return verdict.GateResult("policy-drift", v, reasons)
