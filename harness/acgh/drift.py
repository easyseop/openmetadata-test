"""T40 — implementation-scope drift (SRS P0-6, 부칙 A-3.7, CG-03).

Two-sided check with the touched/net split A-3.7 requires:

- UPPER BOUND (touched paths): every path a candidate commit touches must fall
  within its customization's ``allowed_changed_paths``.  Scope control applies
  equally to upstream, extension, and governance ownership zones.  Registration
  of the change itself — is there an ID at all — is T30's job; drift assumes a
  registered commit and checks its declared scope.

- LOWER BOUND (net paths): every ``required_changed_paths`` entry of a
  customization present in the candidate must actually appear in the NET diff
  (base->head). A required file that nets out to no change means the
  customization did not land -> block. This is why touched != net: a file edited
  then reverted is "touched" but not "net", and the lower bound catches it.

Verdict: any violation -> block; none -> pass. (Unknown-ownership paths and
missing IDs are T30/T31's fail-closed concerns, not drift's.)
"""
from __future__ import annotations

from acgh import gitprim
from acgh import layout as L
from acgh import verdict
from acgh.invariants import Violation

OUT_OF_SCOPE = "out_of_scope_change"
REQUIRED_NET_MISSING = "required_net_missing"


def check_drift(repo, base, head, manifests_by_id, layout: L.Layout) -> list[Violation]:
    violations: list[Violation] = []
    commits = gitprim.commits(repo, base, head)

    # --- upper bound: every touched path must be in-scope -------------------
    present_ids: set[str] = set()
    for c in commits:
        if len(c.customization_ids) != 1:
            continue  # 0 / many IDs are T30's concern
        cid = c.customization_ids[0]
        present_ids.add(cid)
        manifest = manifests_by_id.get(cid)
        if manifest is None:
            continue  # unregistered ID is T31's concern
        allowed = L.make_spec(manifest["implementation"]["allowed_changed_paths"])
        for p in gitprim.changed_paths(repo, c.sha):
            if not allowed.match_file(L.normalize_path(p)):
                violations.append(Violation(
                    c.sha, OUT_OF_SCOPE,
                    f"{cid}: {p} not in allowed_changed_paths"))

    # --- lower bound: required paths must be in the net diff ----------------
    net = {L.normalize_path(p) for p in gitprim.net_changed_paths(repo, base, head)}
    for cid in sorted(present_ids):
        manifest = manifests_by_id.get(cid)
        if manifest is None:
            continue
        for req in manifest["implementation"].get("required_changed_paths", []):
            if L.normalize_path(req) not in net:
                violations.append(Violation(
                    "", REQUIRED_NET_MISSING,
                    f"{cid}: required {req} not present in net diff"))
    return violations


def to_gate_result(violations: list[Violation], name: str = "drift") -> verdict.GateResult:
    v = verdict.BLOCK if violations else verdict.PASS
    reasons = tuple(f"{x.code}: {x.detail}" for x in violations)
    return verdict.GateResult(name, v, reasons)
