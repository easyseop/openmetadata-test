"""T05 operational layer — path ownership & shared glob grammar.

Loads ``repository-layout.yaml`` (the T05 정본) and exposes the ONE path
grammar every gate must reuse (SRS 부칙 A-3.1): normalization, literal-path
validation, and ownership classification. Concentrating this here is the
mechanism that makes "CG-01 / MF-01 / GZ / T93 share the same path grammar"
true rather than aspirational — a gate that imports this module cannot drift.

Grammar (fixed by repository-layout.yaml.path_grammar):
- gitignore-pathspec (python ``pathspec`` GitWildMatch), repo-root relative,
  ``/`` separator, case-sensitive, NFC-normalized, negation forbidden.
- symlink/submodule/LFS content policy is enforced elsewhere (diff-time);
  this module governs the path STRING grammar and ownership only.
"""
from __future__ import annotations

import unicodedata
from pathlib import Path

import pathspec
import yaml

# Ownership roles.
UPSTREAM = "upstream"
GOVERNANCE = "governance"
EXTENSION = "extension"
UNKNOWN = "unknown"

# Any of these in a path means it is a glob pattern, not a literal path.
_GLOB_METACHARS = frozenset("*?[]!")


class LayoutError(ValueError):
    """Layout policy or path-grammar violation. Callers treat as fail-closed."""


def normalize_path(p: str) -> str:
    """Normalize a repo-root-relative path per 부칙 A-3.1.

    NFC unicode, ``/`` separator, case preserved. Rejects absolute paths,
    backslashes, ``.``/``..``/empty segments, and trailing slashes so that two
    spellings of the same path can never classify differently.
    """
    if not isinstance(p, str) or p == "":
        raise LayoutError(f"empty or non-string path: {p!r}")
    s = unicodedata.normalize("NFC", p)
    if "\\" in s:
        raise LayoutError(f"backslash not allowed (use '/'): {p!r}")
    if s.startswith("/"):
        raise LayoutError(f"absolute path not allowed: {p!r}")
    if s.endswith("/"):
        raise LayoutError(f"trailing slash not allowed: {p!r}")
    for seg in s.split("/"):
        if seg in ("", ".", ".."):
            raise LayoutError(f"illegal path segment in {p!r}")
    return s


def ensure_literal(p: str) -> str:
    """Normalize and require a LITERAL path (no glob metachars) — 부칙 A-3.2.

    ``required_changed_paths`` entries must be literal so ownership and
    ⊆-allowed checks are decidable without ambiguity.
    """
    s = normalize_path(p)
    bad = sorted(set(s) & _GLOB_METACHARS)
    if bad:
        raise LayoutError(
            f"required path must be literal (glob metachar {bad} in {p!r})"
        )
    return s


# pathspec factory implementing gitignore semantics. Fixed by the T05 policy
# (path_grammar.name: gitignore-pathspec); pinned here so a reinstall cannot
# silently change match semantics (§8 determinism).
_PATHSPEC_FACTORY = "gitignore"


def make_spec(patterns) -> pathspec.PathSpec:
    """Build a gitignore-grammar spec, rejecting negation (MVP determinism)."""
    for pat in patterns:
        if pat.lstrip().startswith("!"):
            raise LayoutError(f"negation pattern not allowed: {pat!r}")
    return pathspec.PathSpec.from_lines(_PATHSPEC_FACTORY, list(patterns))


class Layout:
    """Ownership map + shared matcher, bound to one upstream SHA."""

    def __init__(
        self,
        upstream_base_sha: str,
        upstream_roots,
        governance_roots,
        extension_roots,
        unknown_policy: str,
    ) -> None:
        self.upstream_base_sha = upstream_base_sha
        self.unknown_policy = unknown_policy
        self._specs = {
            UPSTREAM: make_spec(upstream_roots),
            GOVERNANCE: make_spec(governance_roots),
            EXTENSION: make_spec(extension_roots),
        }

    def classify(self, path: str) -> str:
        """Return the ownership role of ``path`` (or ``UNKNOWN``).

        Ownership zones are disjoint by design; a path matching more than one
        is a layout misconfiguration and fails closed rather than picking one.
        """
        s = normalize_path(path)
        hits = [role for role, spec in self._specs.items() if spec.match_file(s)]
        if len(hits) > 1:
            raise LayoutError(f"ambiguous ownership for {path!r}: {sorted(hits)}")
        return hits[0] if hits else UNKNOWN


def load_layout(path) -> Layout:
    """Load and validate ``repository-layout.yaml`` into a :class:`Layout`."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    grammar = data.get("path_grammar", {})
    if grammar.get("negation_allowed", False):
        raise LayoutError("MVP requires path_grammar.negation_allowed: false")
    if "upstream_base_sha" not in data:
        raise LayoutError("repository-layout.yaml missing upstream_base_sha")
    return Layout(
        upstream_base_sha=data["upstream_base_sha"],
        upstream_roots=data.get("upstream_owned_roots", []),
        governance_roots=data.get("bank_governance_roots", []),
        extension_roots=data.get("platform_extension_roots", []),
        unknown_policy=data.get("unknown_path_policy", "analysis_error"),
    )
