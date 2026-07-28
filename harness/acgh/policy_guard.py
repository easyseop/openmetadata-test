"""T70 — policy self-protection (SRS P0-9 · §정책).

Blocks the self-weakening bypass: a candidate that relaxes the gates/policies
must not be judged by its OWN relaxed policy. If a candidate changes a
policy-defining file, the evaluation must load the BASE (pre-change) policy; a
run that judged such a candidate with the candidate's new policy is a bypass and
is blocked.

Deterministic, no upstream needed — it reasons purely over which paths the
candidate touched, using the shared T05 glob grammar.
"""
from __future__ import annotations

from acgh import layout as L
from acgh import verdict

# Paths whose change must be judged by the OLD policy (weakening-sensitive).
DEFAULT_POLICY_GLOBS = (
    "policies/**",
    ".bank/**",
    "docs/bank/**",
    ".github/workflows/**",
    "harness/acgh/**",
    "harness/policies/**",
    "harness/registrations/**",
    "harness/tests/**",
    "docs/02-설계/**",
    "docs/03-기술참조/**",
    "docs/04-진행/**",
    "STATUS.md",
    "CLAUDE.md",
)


def touched_policy_paths(changed_paths, policy_globs=DEFAULT_POLICY_GLOBS) -> list[str]:
    spec = L.make_spec(list(policy_globs))
    return [p for p in changed_paths if spec.match_file(L.normalize_path(p))]


def evaluation_policy_ref(base_ref, candidate_ref, changed_paths,
                          policy_globs=DEFAULT_POLICY_GLOBS):
    """The ref whose policy MUST be used to judge this candidate.

    base_ref if the candidate touches any policy path (so it cannot approve its
    own relaxation); otherwise candidate_ref.
    """
    return base_ref if touched_policy_paths(changed_paths, policy_globs) else candidate_ref


def check_self_approval(changed_paths, used_policy_ref, base_ref, *,
                        policy_globs=DEFAULT_POLICY_GLOBS,
                        name="policy-self-protection") -> verdict.GateResult:
    """Verify a policy-changing candidate was judged by the base policy."""
    touched = touched_policy_paths(changed_paths, policy_globs)
    if not touched:
        return verdict.GateResult(name, verdict.PASS, ("no policy change",))
    if used_policy_ref != base_ref:
        return verdict.GateResult(
            name, verdict.BLOCK,
            (f"policy changed ({touched[0]}) but evaluated with "
             f"{used_policy_ref!r}, not base {base_ref!r} — self-weakening bypass",),
        )
    return verdict.GateResult(
        name, verdict.APPROVAL,
        (f"policy change judged against base policy; "
         f"{len(touched)} policy path(s) touched — needs approval",),
    )
