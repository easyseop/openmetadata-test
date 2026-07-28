"""T41 — sensitive-zone + change-intent gate (SRS REQ-GZ-01/02, 보완책 2).

Two independent judgments per changed file, combined by severity:

- ZONE (where): a changed path matching a ``frozen`` zone -> block, a
  ``protected`` zone -> approval, a ``watched`` zone -> pass (noted). Zones use
  the same gitignore-pathspec grammar as T05.
- INTENT (was it declared): the change-intent declares ``allowed`` and
  ``forbidden`` path sets. A changed file in ``forbidden`` -> block; outside a
  non-empty ``allowed`` -> approval (scope escape). A MISSING intent is
  fail-closed -> analysis_error: we do not approve a change nobody scoped.

The gate verdict is the severity-rank aggregate of every file's judgment
(reusing the verdict engine), so frozen/forbidden dominate.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from acgh import layout as L
from acgh import verdict

FROZEN = "frozen"
PROTECTED = "protected"
WATCHED = "watched"

_ZONE_VERDICT = {
    FROZEN: verdict.BLOCK,
    PROTECTED: verdict.APPROVAL,
    WATCHED: verdict.PASS,
}
# Most-sensitive zone wins when a path matches several.
_ZONE_ORDER = [FROZEN, PROTECTED, WATCHED]


@dataclass(frozen=True)
class Finding:
    path: str
    verdict: str
    reason: str


class Zones:
    def __init__(self, specs: dict):
        self._specs = specs  # level -> PathSpec

    def zone_of(self, path: str):
        s = L.normalize_path(path)
        for level in _ZONE_ORDER:
            spec = self._specs.get(level)
            if spec is not None and spec.match_file(s):
                return level
        return None


def load_zones(path) -> Zones:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    zdefs = data.get("zones", {})
    return Zones({lvl: L.make_spec(zdefs.get(lvl, [])) for lvl in _ZONE_ORDER})


def check_sensitive_zones(changed_paths, zones: Zones, change_intent) -> verdict.GateResult:
    """Judge changed paths against zones + change-intent.

    ``change_intent`` is a dict {"allowed": [...globs], "forbidden": [...globs]}
    or None. None => fail-closed (analysis_error).
    """
    if change_intent is None:
        return verdict.GateResult(
            "sensitive-zones", verdict.ANALYSIS_ERROR,
            ("change-intent 부재 — fail-closed",),
        )
    if not isinstance(change_intent, dict):
        return verdict.GateResult(
            "sensitive-zones", verdict.ANALYSIS_ERROR,
            ("change-intent must be a mapping",),
        )
    raw_allowed = change_intent.get("allowed")
    if not isinstance(raw_allowed, list) or not raw_allowed:
        return verdict.GateResult(
            "sensitive-zones", verdict.ANALYSIS_ERROR,
            ("change-intent.allowed is empty — no approved change scope",),
        )
    raw_forbidden = change_intent.get("forbidden", [])
    if not isinstance(raw_forbidden, list):
        return verdict.GateResult(
            "sensitive-zones", verdict.ANALYSIS_ERROR,
            ("change-intent.forbidden must be a list",),
        )
    try:
        allowed = L.make_spec(raw_allowed)
        forbidden = L.make_spec(raw_forbidden)
    except L.LayoutError as exc:
        return verdict.GateResult(
            "sensitive-zones", verdict.ANALYSIS_ERROR,
            (f"invalid change-intent path policy: {exc}",),
        )

    findings: list[Finding] = []
    for p in sorted(set(changed_paths)):
        s = L.normalize_path(p)
        # zone judgment
        zone = zones.zone_of(s)
        if zone is not None:
            reason = (
                "zone=watched visibility_only"
                if zone == WATCHED else f"zone={zone}"
            )
            findings.append(Finding(s, _ZONE_VERDICT[zone], reason))
        # intent judgment
        if forbidden.match_file(s):
            findings.append(Finding(s, verdict.BLOCK, "in change-intent forbidden"))
        elif not allowed.match_file(s):
            findings.append(Finding(
                s, verdict.APPROVAL,
                "outside change-intent allowed — explicit owner review required",
            ))

    v = verdict.aggregate([f.verdict for f in findings]) if findings else verdict.PASS
    reasons = tuple(f"{f.path}: {f.reason} -> {f.verdict}" for f in findings)
    return verdict.GateResult("sensitive-zones", v, reasons)
