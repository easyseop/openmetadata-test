"""Candidate-vs-upstream TypeScript diagnostic baseline comparison.

The comparator uses a path + TypeScript error-code multiset for blocking
candidate regressions and a second path + code + message multiset for review
visibility. An unchanged non-zero coarse baseline remains ``approval`` rather
than ``pass``; message substitutions are surfaced without pretending the broad
typecheck is green.
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter

from acgh import verdict

_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_DIAGNOSTIC = re.compile(
    r"^(?P<path>[^(\r\n]+)\(\d+,\d+\): "
    r"error (?P<code>TS\d+): (?P<message>.+)$"
)
_ERROR_MARKER = re.compile(r"error TS\d+:")
_TRUSTED_EXITS = frozenset({0, 2})


def _diagnostics(
    text: str,
) -> tuple[
    Counter[tuple[str, str]],
    Counter[tuple[str, str, str]],
    int,
]:
    cleaned = _ANSI.sub("", text).replace("\r", "")
    found: Counter[tuple[str, str]] = Counter()
    messages: Counter[tuple[str, str, str]] = Counter()
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
        code = match.group("code")
        found[(path, code)] += 1
        messages[(path, code, match.group("message"))] += 1
    return found, messages, malformed


def fingerprint(diagnostics: Counter[tuple[str, str]]) -> str:
    expanded = [
        f"{path}|{code}"
        for (path, code), count in sorted(diagnostics.items())
        for _ in range(count)
    ]
    payload = ("\n".join(expanded) + ("\n" if expanded else "")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def message_fingerprint(
    diagnostics: Counter[tuple[str, str, str]],
) -> str:
    expanded = [
        f"{path}|{code}|{message}"
        for (path, code, message), count in sorted(diagnostics.items())
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

    upstream, upstream_messages, upstream_malformed = _diagnostics(upstream_log)
    candidate, candidate_messages, candidate_malformed = _diagnostics(
        candidate_log
    )
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
    new_messages = candidate_messages - upstream_messages
    removed_messages = upstream_messages - candidate_messages
    new_message_count = sum(new_messages.values())
    removed_message_count = sum(removed_messages.values())
    reasons = (
        f"upstream_diagnostics={upstream_count}",
        f"candidate_diagnostics={candidate_count}",
        f"new_diagnostics={new_count}",
        f"removed_diagnostics={removed_count}",
        f"upstream_fingerprint={fingerprint(upstream)}",
        f"candidate_fingerprint={fingerprint(candidate)}",
        f"new_message_variants={new_message_count}",
        f"removed_message_variants={removed_message_count}",
        (
            "upstream_message_fingerprint="
            f"{message_fingerprint(upstream_messages)}"
        ),
        (
            "candidate_message_fingerprint="
            f"{message_fingerprint(candidate_messages)}"
        ),
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
