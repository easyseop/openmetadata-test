"""T50 — declarative verifier runner (SRS P0-8, 부칙 A-3.5/3.6).

The manifest schema already makes arbitrary shell impossible (no
``verification.command`` field). This module is its positive counterpart: a
small set of DECLARATIVE, non-executing verifier types, so a customization can
assert facts about the candidate tree without the harness ever running
attacker-influenced code.

Supported (no sandbox — they read data, they do not execute it):
- ``document_query_assert`` — resolve an RFC 6901 JSON Pointer into a JSON/YAML
  file and assert it equals a literal. JSON Pointer only (no JSONPath/eval, 부칙
  A-3.6): no expressions, so nothing to sandbox.
- ``file_hash_equals`` — a file's SHA-256 equals an expected digest (this IS the
  A-3.6 artifact binding).
- ``python_module_present`` — a module file exists at a path (STATIC — no import).

Executable types (``python_import_succeeds``, scripts, containers) are refused
here with analysis_error: they require the sandboxed runner (부칙 A-3.5), which
is out of the declarative runner's scope.

Verdict mapping: assertion ran and is false -> block; could not run (missing
file, unresolvable pointer, parse error, unsupported type) -> analysis_error
(fail-closed). All file paths are candidate-root-relative and validated by the
T05 grammar, so a verifier cannot read outside the candidate tree.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml

from acgh import layout as L
from acgh import verdict

DECLARATIVE_TYPES = frozenset(
    {"document_query_assert", "file_hash_equals", "python_module_present"}
)
EXECUTABLE_TYPES = frozenset(
    {"python_import_succeeds", "allowlist_script", "container_run"}
)


class _CannotRun(Exception):
    """Verifier could not be evaluated -> analysis_error (not a failed assertion)."""


@dataclass(frozen=True)
class VerifierResult:
    type: str
    verdict: str
    reason: str


def _safe(root: str, rel: str) -> Path:
    # normalize_path rejects absolute paths and '..' -> no escape from root.
    try:
        norm = L.normalize_path(rel)
    except L.LayoutError as e:
        raise _CannotRun(f"invalid verifier path {rel!r}: {e}")
    return Path(root) / norm


def _resolve_pointer(doc, pointer: str):
    """RFC 6901 JSON Pointer. '' -> whole doc."""
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise _CannotRun(f"invalid JSON Pointer: {pointer!r}")
    cur = doc
    for raw in pointer.split("/")[1:]:
        tok = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            try:
                cur = cur[int(tok)]
            except (ValueError, IndexError):
                raise _CannotRun(f"pointer {pointer!r} not resolvable at {tok!r}")
        elif isinstance(cur, dict):
            if tok not in cur:
                raise _CannotRun(f"pointer {pointer!r} not resolvable at {tok!r}")
            cur = cur[tok]
        else:
            raise _CannotRun(f"pointer {pointer!r} descends into scalar at {tok!r}")
    return cur


def _document_query_assert(spec, root) -> VerifierResult:
    path = _safe(root, spec["file"])
    if not path.is_file():
        raise _CannotRun(f"file not found: {spec['file']}")
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        raise _CannotRun(f"could not parse {spec['file']}")
    val = _resolve_pointer(doc, spec["pointer"])
    ok = val == spec["equals"]
    return VerifierResult(
        "document_query_assert",
        verdict.PASS if ok else verdict.BLOCK,
        f"{spec['pointer']} = {val!r} (expected {spec['equals']!r})",
    )


def _file_hash_equals(spec, root) -> VerifierResult:
    path = _safe(root, spec["file"])
    if not path.is_file():
        raise _CannotRun(f"file not found: {spec['file']}")
    got = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    want = spec["sha256"]
    want = want if want.startswith("sha256:") else "sha256:" + want
    ok = got == want
    return VerifierResult(
        "file_hash_equals",
        verdict.PASS if ok else verdict.BLOCK,
        f"{got} (expected {want})",
    )


def _python_module_present(spec, root) -> VerifierResult:
    path = _safe(root, spec["module_path"])
    ok = path.is_file()
    return VerifierResult(
        "python_module_present",
        verdict.PASS if ok else verdict.BLOCK,
        f"present={ok}: {spec['module_path']}",
    )


_HANDLERS = {
    "document_query_assert": _document_query_assert,
    "file_hash_equals": _file_hash_equals,
    "python_module_present": _python_module_present,
}


def run_verifier(spec: dict, root: str) -> VerifierResult:
    t = spec.get("type")
    if t not in DECLARATIVE_TYPES:
        reason = (
            "executable verifier requires the sandboxed runner (부칙 A-3.5)"
            if t in EXECUTABLE_TYPES else f"unknown verifier type: {t!r}"
        )
        return VerifierResult(t, verdict.ANALYSIS_ERROR, reason)
    try:
        return _HANDLERS[t](spec, root)
    except _CannotRun as e:
        return VerifierResult(t, verdict.ANALYSIS_ERROR, str(e))


def run_verifiers(
    specs,
    root: str,
    name: str = "declarative-verifiers",
    *,
    require_declared: bool = False,
):
    """Run all verifiers; return (GateResult, [VerifierResult]).

    No verifiers declared -> pass (nothing to assert here; test completeness is
    a separate gate), not the aggregate's empty-set analysis_error.
    """
    specs = list(specs)
    if require_declared and not specs:
        return (
            verdict.GateResult(
                name,
                verdict.ANALYSIS_ERROR,
                ("declarative verifier set is empty but required",),
            ),
            [],
        )
    results = [run_verifier(s, root) for s in specs]
    v = verdict.aggregate([r.verdict for r in results]) if results else verdict.PASS
    reasons = tuple(f"{r.type}: {r.verdict} ({r.reason})" for r in results)
    return verdict.GateResult(name, v, reasons), results
