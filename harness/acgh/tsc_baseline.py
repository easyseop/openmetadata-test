"""Candidate-vs-upstream TypeScript diagnostic baseline comparison.

The comparator intentionally uses a conservative path + TypeScript error-code
multiset. It detects new diagnostics and increased multiplicity, while an
unchanged non-zero baseline remains ``approval`` rather than ``pass`` because
same-path/same-code substitution is still possible and the broad typecheck is
not green.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter

from acgh import verdict

_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_DIAGNOSTIC = re.compile(
    r"^(?P<path>[^(\r\n]+)\(\d+,\d+\): "
    r"error (?P<code>TS\d+): .+$"
)
_ERROR_MARKER = re.compile(r"error TS\d+:")
_TRUSTED_EXITS = frozenset({0, 2})


def _diagnostics(text: str) -> tuple[Counter[tuple[str, str]], int]:
    cleaned = _ANSI.sub("", text).replace("\r", "")
    found: Counter[tuple[str, str]] = Counter()
    malformed = 0
    for line in cleaned.splitlines():
        if not _ERROR_MARKER.search(line):
            continue
        match = _DIAGNOSTIC.fullmatch(line)
        if match is None:
            malformed += 1
            continue
        path = match.group("path")
        if path.startswith("/") or ".." in path.split("/"):
            malformed += 1
            continue
        found[(path, match.group("code"))] += 1
    return found, malformed


def fingerprint(diagnostics: Counter[tuple[str, str]]) -> str:
    expanded = [
        f"{path}|{code}"
        for (path, code), count in sorted(diagnostics.items())
        for _ in range(count)
    ]
    payload = ("\n".join(expanded) + ("\n" if expanded else "")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def compare(
    upstream_log: str,
    candidate_log: str,
    *,
    upstream_exit: int,
    candidate_exit: int,
    name: str = "ui-typecheck-baseline",
) -> verdict.GateResult:
    """Compare two complete tsc logs and return a fail-closed gate result."""
    if upstream_exit not in _TRUSTED_EXITS or candidate_exit not in _TRUSTED_EXITS:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (
                "untrusted tsc exit: "
                f"upstream={upstream_exit}, candidate={candidate_exit}",
            ),
        )

    upstream, upstream_malformed = _diagnostics(upstream_log)
    candidate, candidate_malformed = _diagnostics(candidate_log)
    if upstream_malformed or candidate_malformed:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (
                "malformed diagnostics: "
                f"upstream={upstream_malformed}, candidate={candidate_malformed}",
            ),
        )

    upstream_count = sum(upstream.values())
    candidate_count = sum(candidate.values())
    inconsistent = (
        (upstream_exit == 0) != (upstream_count == 0)
        or (candidate_exit == 0) != (candidate_count == 0)
    )
    if inconsistent:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (
                "tsc exit/diagnostic mismatch: "
                f"upstream_exit={upstream_exit}, upstream={upstream_count}, "
                f"candidate_exit={candidate_exit}, candidate={candidate_count}",
            ),
        )

    new = candidate - upstream
    removed = upstream - candidate
    new_count = sum(new.values())
    removed_count = sum(removed.values())
    reasons = (
        f"upstream_diagnostics={upstream_count}",
        f"candidate_diagnostics={candidate_count}",
        f"new_diagnostics={new_count}",
        f"removed_diagnostics={removed_count}",
        f"upstream_fingerprint={fingerprint(upstream)}",
        f"candidate_fingerprint={fingerprint(candidate)}",
    )
    if new_count:
        first = sorted(new.elements())[0]
        return verdict.GateResult(
            name,
            verdict.BLOCK,
            reasons + (f"first_new={first[0]}|{first[1]}",),
        )
    if candidate_count:
        return verdict.GateResult(
            name,
            verdict.APPROVAL,
            reasons
            + (
                "non-zero upstream baseline remains; human baseline approval "
                "or full repair is required",
            ),
        )
    return verdict.GateResult(name, verdict.PASS, reasons)
