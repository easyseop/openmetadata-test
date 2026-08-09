"""T42-A — deterministic upgrade-watch candidate suggestions.

This is a suggestion provider, not a verdict gate. During an upstream upgrade it
looks only at files that actually changed A->B, then proposes a changed file when
one of the customization's exact implementation files directly references that
file's symbol. Existing allowed/watch paths are excluded. A code owner must
review and accept a proposal before it enters a manifest — nothing here edits a
manifest or approves a path.

Why an index instead of a search (2026-08-09): the original implementation
searched every customization file again for every changed upstream path, i.e.
``changed x custom-files`` regex passes over cached blobs. On the real
1.13.1->1.13.2 range (1,702 changed paths, 112 distinct customization files, a
4.9MB shared i18n bundle among them) that is ~320k full-text scans and the gate
exceeded its 300s deadline without producing a single candidate. The customization
side is now tokenized exactly once into ``symbol -> paths``, so the changed side
is a dictionary lookup. Structured data (JSON/YAML/...) is deliberately not a code
reference source: a basename appearing in a translation string is not an import.
``upgrade-watch`` still reports those files changing — excluding them here only
removes them as *evidence of a code reference*, never from the watch itself.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from acgh import gitprim
from acgh import layout as L
from acgh import manifest as M
from acgh import verdict

# Reference evidence comes from code only; these carry data, not imports.
STRUCTURED_SUFFIXES = frozenset({
    ".json", ".yaml", ".yml", ".xml", ".svg", ".md", ".txt", ".csv",
    ".properties", ".po", ".pot", ".lock", ".sum", ".html", ".htm", ".sql",
})
BINARY_SUFFIXES = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".woff", ".woff2",
    ".ttf", ".otf", ".eot", ".zip", ".jar", ".war", ".class", ".so", ".dylib",
    ".dll", ".pdf", ".gz", ".tgz", ".bin", ".pyc",
})
_C_FAMILY = frozenset({
    ".java", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".kt",
    ".kts", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".scss", ".less", ".css",
})
_HASH_FAMILY = frozenset({".py", ".sh", ".bash", ".rb", ".pl", ".tf", ".cfg", ".ini"})

_IDENTIFIER = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_TRIVIAL_SYMBOLS = frozenset({"index", "__init__", "package", "main", "types"})
_MIN_SYMBOL_LENGTH = 4
_CAMEL_WORD = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+")
# Words that name a role rather than a subject: two files sharing only these are
# not evidence that one replaced the other.
_GENERIC_WORDS = frozenset({
    "util", "utils", "pure", "helper", "helpers", "service", "services",
    "component", "components", "constant", "constants", "type", "types",
    "index", "base", "common", "test", "tests", "spec", "mock", "mocks",
    "model", "models", "config", "class", "impl", "api", "page", "view",
})

# Stages are reported verbatim when a deadline stops the run, so an operator
# knows which work was finished and which was not.
STAGE_CHANGED = "changed-paths"
STAGE_INDEX = "customization-index"
STAGE_MATCH = "changed-path-matching"
STAGE_DELETED = "deleted-watch-paths"
STAGE_DONE = "complete"


class WatchSuggestTimeout(RuntimeError):
    """The deadline elapsed; the caller receives a partial, clearly-marked report."""


@dataclass(frozen=True)
class WatchSuggestion:
    customization_id: str
    suggested_path: str
    referenced_from: tuple[str, ...]
    reason: str = "changed upstream file is directly referenced by customization code"

    def to_json(self) -> dict:
        return {
            "customization_id": self.customization_id,
            "suggested_path": self.suggested_path,
            "referenced_from": list(self.referenced_from),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class DeletedWatchFinding:
    """An existing watch path that the official target no longer contains.

    Reported even when no move candidate is found: the deletion itself is what a
    code owner must decide about, and hiding it because the tool cannot guess the
    replacement is how BANK-OM-004's EntityUtils.tsx split went unnoticed.
    """
    customization_id: str
    watch_path: str
    change_type: str = "deleted"
    candidates: tuple[str, ...] = ()
    candidate_reason: str = "same directory or referenced by this customization"
    authority: str = "code-owner-review-required"

    def to_json(self) -> dict:
        return {
            "customization_id": self.customization_id,
            "watch_path": self.watch_path,
            "change_type": self.change_type,
            "candidates": list(self.candidates),
            "candidate_count": len(self.candidates),
            "candidate_reason": self.candidate_reason,
            "authority": self.authority,
        }


@dataclass(frozen=True)
class SuggestReport:
    complete: bool
    stage: str
    suggestions: tuple[WatchSuggestion, ...] = ()
    deleted_watch: tuple[DeletedWatchFinding, ...] = ()
    counts: dict = field(default_factory=dict)
    excluded: dict = field(default_factory=dict)
    inputs: dict = field(default_factory=dict)
    telemetry: dict = field(default_factory=dict)

    def packet(self) -> dict:
        """Judgment-only payload. Never carries elapsed time or cache state."""
        return review_packet(self)


def _suffix(path: str) -> str:
    return PurePosixPath(path).suffix.lower()


def _symbol(path: str) -> str | None:
    name = PurePosixPath(path).name
    stem = name.split(".", 1)[0]
    if stem in _TRIVIAL_SYMBOLS or len(stem) < _MIN_SYMBOL_LENGTH:
        return None
    return stem


def _is_binary(blob: bytes) -> bool:
    return b"\x00" in blob[:8000]


def _words(stem: str) -> frozenset[str]:
    return frozenset(word.lower() for word in _CAMEL_WORD.findall(stem))


def _ambiguous_symbols(tree_paths) -> frozenset[str]:
    """Stems that name files in more than one directory identify nothing.

    ``metadata.py`` exists under a dozen ingestion sources, so the token
    ``metadata`` appearing in a customization file says nothing about which of
    them is referenced — on the real 1.13.2 range these generic stems produced
    614 suggestions, almost all noise. A stem that is reused across directories
    is therefore not usable evidence; ``Foo.ts`` beside its own ``Foo.test.ts``
    stays usable because both live in one place.
    """
    directories: dict[str, set[str]] = {}
    for path in tree_paths:
        symbol = _symbol(path)
        if symbol is None:
            continue
        directories.setdefault(symbol, set()).add(str(PurePosixPath(path).parent))
    return frozenset(
        symbol for symbol, dirs in directories.items() if len(dirs) > 1
    )


def _strip_comments(text: str, suffix: str) -> str:
    """Drop comments while keeping string literals.

    Import targets live inside strings (``from './EntityUtils'``), so stripping
    quotes would lose real references; a basename mentioned only in a comment is
    not a reference, so comments must go. The scanner tracks quote state so a
    ``//`` inside a URL string is not mistaken for a comment.
    """
    if suffix in _C_FAMILY:
        line_marks, block = ("//",), ("/*", "*/")
    elif suffix in _HASH_FAMILY:
        line_marks, block = ("#",), None
    else:
        return text

    out: list[str] = []
    index, length, quote = 0, len(text), ""
    while index < length:
        char = text[index]
        if quote:
            out.append(char)
            if char == "\\" and index + 1 < length:
                out.append(text[index + 1])
                index += 2
                continue
            if char == quote:
                quote = ""
            index += 1
            continue
        if char in "\"'`":
            quote = char
            out.append(char)
            index += 1
            continue
        if block and text.startswith(block[0], index):
            end = text.find(block[1], index + len(block[0]))
            index = length if end < 0 else end + len(block[1])
            out.append(" ")
            continue
        if any(text.startswith(mark, index) for mark in line_marks):
            end = text.find("\n", index)
            index = length if end < 0 else end
            out.append(" ")
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _tokens(blob: bytes, suffix: str) -> set[str]:
    text = blob.decode("utf-8", errors="replace")
    return set(_IDENTIFIER.findall(_strip_comments(text, suffix)))


def _deadline_check(deadline: float | None, stage: str) -> None:
    if deadline is not None and time.monotonic() > deadline:
        raise WatchSuggestTimeout(stage)


def _declared_paths(manifest: dict) -> tuple[str, ...]:
    return tuple(L.ensure_literal(path) for path in M.declared_changed_paths(manifest))


def _watch_paths(manifest: dict) -> tuple[str, ...]:
    return tuple(manifest.get("upgrade_watch", {}).get("paths", []) or ())


def _build_index(
    repo: str,
    candidate_ref: str,
    manifests_by_id: dict[str, dict],
    *,
    deadline: float | None = None,
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, int]]:
    """Tokenize every distinct customization file once.

    Returns ``symbol -> paths``, ``path -> customization ids`` and the exclusion
    tally, so the changed side becomes a dictionary lookup instead of a scan.
    """
    owners: dict[str, set[str]] = {}
    for customization_id in sorted(manifests_by_id):
        for path in _declared_paths(manifests_by_id[customization_id]):
            owners.setdefault(path, set()).add(customization_id)

    present = set(gitprim.list_tree_recursive(repo, candidate_ref))
    excluded = {"structured": 0, "binary": 0, "missing_in_candidate": 0}
    readable: list[str] = []
    for path in sorted(owners):
        if path not in present:
            excluded["missing_in_candidate"] += 1
            continue
        if _suffix(path) in STRUCTURED_SUFFIXES:
            excluded["structured"] += 1
            continue
        if _suffix(path) in BINARY_SUFFIXES:
            excluded["binary"] += 1
            continue
        readable.append(path)

    _deadline_check(deadline, STAGE_INDEX)
    blobs = gitprim.blob_batch(repo, candidate_ref, readable)
    symbols: dict[str, set[str]] = {}
    indexed = 0
    for position, path in enumerate(readable):
        if position % 32 == 0:
            _deadline_check(deadline, STAGE_INDEX)
        blob = blobs.get(path)
        if blob is None:
            excluded["missing_in_candidate"] += 1
            continue
        if _is_binary(blob):
            excluded["binary"] += 1
            continue
        indexed += 1
        for token in _tokens(blob, _suffix(path)):
            symbols.setdefault(token, set()).add(path)
    excluded["indexed"] = indexed
    return symbols, owners, excluded


def _match_changed(
    changed: tuple[str, ...],
    manifests_by_id: dict[str, dict],
    symbols: dict[str, set[str]],
    owners: dict[str, set[str]],
    ambiguous: frozenset[str],
    *,
    deadline: float | None = None,
) -> tuple[list[WatchSuggestion], dict[str, int]]:
    allowed_by_id = {
        customization_id: set(_declared_paths(manifest))
        for customization_id, manifest in manifests_by_id.items()
    }
    watched_by_id = {
        customization_id: L.make_spec(_watch_paths(manifest))
        for customization_id, manifest in manifests_by_id.items()
    }
    skipped = {
        "structured": 0, "binary": 0, "no_symbol": 0,
        "ambiguous_symbol": 0, "unreferenced": 0,
    }
    found: dict[tuple[str, str], set[str]] = {}
    for position, changed_path in enumerate(changed):
        if position % 128 == 0:
            _deadline_check(deadline, STAGE_MATCH)
        suffix = _suffix(changed_path)
        if suffix in STRUCTURED_SUFFIXES:
            skipped["structured"] += 1
            continue
        if suffix in BINARY_SUFFIXES:
            skipped["binary"] += 1
            continue
        symbol = _symbol(changed_path)
        if symbol is None:
            skipped["no_symbol"] += 1
            continue
        if symbol in ambiguous:
            skipped["ambiguous_symbol"] += 1
            continue
        referencing = symbols.get(symbol)
        if not referencing:
            skipped["unreferenced"] += 1
            continue
        for source_path in referencing:
            for customization_id in owners.get(source_path, ()):
                if changed_path in allowed_by_id.get(customization_id, ()):
                    continue
                if watched_by_id[customization_id].match_file(changed_path):
                    continue
                found.setdefault((customization_id, changed_path), set()).add(source_path)
    suggestions = [
        WatchSuggestion(customization_id, changed_path, tuple(sorted(refs)))
        for (customization_id, changed_path), refs in sorted(found.items())
    ]
    return suggestions, skipped


def _deleted_watch_findings(
    repo: str,
    upstream_base: str,
    upstream_target: str,
    changed: tuple[str, ...],
    manifests_by_id: dict[str, dict],
    suggestions: list[WatchSuggestion],
    *,
    target_tree=None,
    deadline: float | None = None,
) -> list[DeletedWatchFinding]:
    """Report watch paths the official target dropped, with move candidates."""
    base_tree = set(gitprim.list_tree_recursive(repo, upstream_base))
    if target_tree is None:
        target_tree = gitprim.list_tree_recursive(repo, upstream_target)
    target_tree = set(target_tree)
    added = tuple(sorted(path for path in changed if path not in base_tree))
    by_id: dict[str, set[str]] = {}
    for item in suggestions:
        by_id.setdefault(item.customization_id, set()).add(item.suggested_path)

    findings: list[DeletedWatchFinding] = []
    for customization_id in sorted(manifests_by_id):
        _deadline_check(deadline, STAGE_DELETED)
        for raw in sorted(_watch_paths(manifests_by_id[customization_id])):
            try:
                watch_path = L.ensure_literal(raw)
            except Exception:  # noqa: BLE001 - a glob watch has no single file to lose
                continue
            if watch_path in target_tree or watch_path not in base_tree:
                continue
            directory = str(PurePosixPath(watch_path).parent)
            subject = _words(_symbol(watch_path) or "") - _GENERIC_WORDS
            # Every new file in the directory is not a move candidate; one that
            # shares the deleted file's subject word (EntityUtils -> Entity*Utils)
            # or that this customization actually references, is.
            candidates = sorted({
                path for path in added
                if str(PurePosixPath(path).parent) == directory
                and _suffix(path) not in STRUCTURED_SUFFIXES | BINARY_SUFFIXES
                and subject & (_words(_symbol(path) or "") - _GENERIC_WORDS)
            } | {
                path for path in by_id.get(customization_id, set()) if path in added
            })
            findings.append(DeletedWatchFinding(
                customization_id, watch_path, candidates=tuple(candidates)
            ))
    return findings


def _cache_inputs(
    upstream_base: str,
    upstream_target: str,
    candidate_ref: str,
    manifests_by_id: dict[str, dict],
    harness_version: str | None,
) -> dict:
    return {
        "upstream_base": upstream_base,
        "upstream_target": upstream_target,
        "candidate_ref": candidate_ref,
        "manifests_digest": verdict.canonical_digest({
            customization_id: {
                "declared": sorted(_declared_paths(manifest)),
                "watch": sorted(_watch_paths(manifest)),
            }
            for customization_id, manifest in sorted(manifests_by_id.items())
        }),
        "harness_version": harness_version,
        "analyzer_version": ANALYZER_VERSION,
    }


ANALYZER_VERSION = 2


def analyze(
    repo: str,
    upstream_base: str,
    upstream_target: str,
    candidate_ref: str,
    manifests_by_id: dict[str, dict],
    *,
    timeout_seconds: float | None = None,
    cache_dir=None,
    harness_version: str | None = None,
) -> SuggestReport:
    """Produce candidates, deletions and counts, or a clearly partial report.

    A deadline never turns into a quiet "no candidates": the report is returned
    with ``complete=False`` and the stage that was running, and callers must
    surface that as analysis_error rather than a pass.
    """
    started = time.monotonic()
    deadline = None if timeout_seconds is None else started + float(timeout_seconds)
    inputs = _cache_inputs(
        upstream_base, upstream_target, candidate_ref, manifests_by_id, harness_version
    )
    cache_key = verdict.canonical_digest(inputs)
    cached = _read_cache(cache_dir, cache_key)
    if cached is not None:
        return _report_from_packet(
            cached, inputs, cache_key,
            telemetry={
                "cache": "hit",
                "cache_key": cache_key,
                "elapsed_seconds": round(time.monotonic() - started, 3),
            },
        )

    stage = STAGE_CHANGED
    try:
        changed = tuple(sorted({
            L.normalize_path(path)
            for path in gitprim.net_changed_paths(repo, upstream_base, upstream_target)
        }))
        _deadline_check(deadline, stage)

        stage = STAGE_INDEX
        symbols, owners, excluded = _build_index(
            repo, candidate_ref, manifests_by_id, deadline=deadline
        )

        stage = STAGE_MATCH
        target_tree = tuple(gitprim.list_tree_recursive(repo, upstream_target))
        ambiguous = _ambiguous_symbols(target_tree)
        suggestions, skipped = _match_changed(
            changed, manifests_by_id, symbols, owners, ambiguous, deadline=deadline
        )

        stage = STAGE_DELETED
        deleted = _deleted_watch_findings(
            repo, upstream_base, upstream_target, changed,
            manifests_by_id, suggestions, target_tree=target_tree, deadline=deadline,
        )
    except WatchSuggestTimeout as exc:
        return SuggestReport(
            complete=False,
            stage=str(exc),
            inputs=inputs,
            counts={"changed_paths": len(changed) if stage != STAGE_CHANGED else 0},
            telemetry={
                "cache": "miss",
                "cache_key": cache_key,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "timeout_seconds": timeout_seconds,
            },
        )

    report = SuggestReport(
        complete=True,
        stage=STAGE_DONE,
        suggestions=tuple(suggestions),
        deleted_watch=tuple(deleted),
        counts={
            "changed_paths": len(changed),
            "indexed_customization_files": excluded.get("indexed", 0),
            "suggestions": len(suggestions),
            "deleted_watch_paths": len(deleted),
        },
        excluded={
            "customization_structured": excluded["structured"],
            "customization_binary": excluded["binary"],
            "customization_missing_in_candidate": excluded["missing_in_candidate"],
            "changed_structured": skipped["structured"],
            "changed_binary": skipped["binary"],
            "changed_without_symbol": skipped["no_symbol"],
            "changed_ambiguous_symbol": skipped["ambiguous_symbol"],
            "changed_unreferenced": skipped["unreferenced"],
        },
        inputs=inputs,
        telemetry={
            "cache": "miss",
            "cache_key": cache_key,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "timeout_seconds": timeout_seconds,
        },
    )
    _write_cache(cache_dir, cache_key, report)
    return report


def _cache_path(cache_dir, cache_key: str):
    if cache_dir is None:
        return None
    return Path(cache_dir) / f"watch-suggest-{cache_key.split(':', 1)[-1]}.json"


def _read_cache(cache_dir, cache_key: str) -> dict | None:
    path = _cache_path(cache_dir, cache_key)
    if path is None or not path.is_file():
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    # The key already covers every judgment input; a stored key that disagrees
    # means the file was moved or edited, so recompute instead of trusting it.
    if stored.get("cache_key") != cache_key:
        return None
    return stored.get("packet")


def _write_cache(cache_dir, cache_key: str, report: SuggestReport) -> None:
    path = _cache_path(cache_dir, cache_key)
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"cache_key": cache_key, "packet": report.packet()},
                ensure_ascii=False, sort_keys=True, indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        return  # a cache that cannot be written must not fail the analysis


def _report_from_packet(packet: dict, inputs: dict, cache_key: str, *, telemetry: dict):
    suggestions = tuple(
        WatchSuggestion(
            item["customization_id"], item["suggested_path"],
            tuple(item["referenced_from"]), item.get("reason", WatchSuggestion.reason),
        )
        for item in packet.get("suggestions", [])
    )
    deleted = tuple(
        DeletedWatchFinding(
            item["customization_id"], item["watch_path"],
            item.get("change_type", "deleted"), tuple(item.get("candidates", [])),
        )
        for item in packet.get("deleted_watch_paths", [])
    )
    return SuggestReport(
        complete=packet.get("complete", True),
        stage=packet.get("stage", STAGE_DONE),
        suggestions=suggestions,
        deleted_watch=deleted,
        counts=packet.get("counts", {}),
        excluded=packet.get("excluded", {}),
        inputs=inputs,
        telemetry=telemetry,
    )


def suggest_watch_paths(
    repo: str,
    upstream_base: str,
    upstream_target: str,
    candidate_ref: str,
    manifests_by_id: dict[str, dict],
    **options,
) -> list[WatchSuggestion]:
    """Backwards-compatible entry point returning suggestions only."""
    return list(analyze(
        repo, upstream_base, upstream_target, candidate_ref, manifests_by_id, **options
    ).suggestions)


def review_packet(suggestions) -> dict:
    """Deterministic review payload; accepts a report or a suggestion list.

    Everything here is a function of the pinned inputs, so the same inputs
    produce the same document whether or not a cache was used. Elapsed time and
    cache state stay in ``SuggestReport.telemetry`` and out of this payload.
    """
    if isinstance(suggestions, SuggestReport):
        report = suggestions
    else:
        items = tuple(suggestions)
        report = SuggestReport(
            complete=True, stage=STAGE_DONE, suggestions=items,
            counts={"suggestions": len(items)},
        )
    return {
        "complete": report.complete,
        "stage": report.stage,
        "authority": "code-owner-review-required",
        "suggestion_count": len(report.suggestions),
        "suggestions": [item.to_json() for item in report.suggestions],
        "deleted_watch_path_count": len(report.deleted_watch),
        "deleted_watch_paths": [item.to_json() for item in report.deleted_watch],
        "counts": dict(sorted(report.counts.items())),
        "excluded": dict(sorted(report.excluded.items())),
        "inputs": dict(sorted(report.inputs.items())),
    }
