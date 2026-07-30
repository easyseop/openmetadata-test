"""T10 — customization manifest schema + semantic validator.

Two layers, because JSON Schema alone cannot express the invariants that matter
(부칙 A-3.2/3.3):

1. STRUCTURE — ``manifest.schema.json`` (JSON Schema 2020-12). Notably
   ``additionalProperties: false`` forbids a ``verification.command`` field, so
   arbitrary shell can never enter through the manifest (P0-8); verification is
   declarative only (T50).
2. SEMANTICS — code rules this module enforces:
   - schema v2 uses one literal ``changed_paths`` list for the current-version
     implementation scope.
   - schema v1 ``allowed_changed_paths`` plus ``candidate_additional_paths``
     remain read-compatible while historical registrations are migrated.
   - ``required_changed_paths`` are literal and covered by the current scope.
   - ``kind: core-patch`` must declare at least one required path.
   - each required path's ownership (via T05 layout) matches ``kind``.
   - ``assurance.contracts`` / ``assurance.direct_tests`` are unique & disjoint.
   - across a manifest set, ``customization_id`` is unique.

The manifest owns POLICY (paths, watch, assurance, series-allowed); it never
owns per-release SHAs or series order — those live in the patch-lock (T11,
부칙 A-3.4).
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from acgh import layout as L

_SCHEMA_PATH = Path(__file__).parent / "schema" / "manifest.schema.json"

# kind -> the ownership zone its changed paths must fall in.
_KIND_ROLE = {
    "core-patch": L.UPSTREAM,
    "extension": L.EXTENSION,
    "governance": L.GOVERNANCE,
}


class ManifestError(ValueError):
    """Manifest fails structural or semantic validation (fail-closed)."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def validate_manifest(data: dict, layout: L.Layout) -> dict:
    """Validate one manifest dict; return it unchanged, or raise ManifestError."""
    errs = sorted(
        _schema_validator().iter_errors(data),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    if errs:
        loc = lambda e: "/".join(str(p) for p in e.absolute_path) or "<root>"
        raise ManifestError(
            "schema: " + "; ".join(f"{loc(e)}: {e.message}" for e in errs)
        )
    _semantic(data, layout)
    return data


def load_manifest(path, layout: L.Layout) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestError(f"manifest is not a mapping: {path}")
    return validate_manifest(data, layout)


def declared_changed_paths(data: dict) -> list[str]:
    """Return the current-version implementation scope for any schema version."""
    implementation = data.get("implementation", {})
    if data.get("schema_version") == 2:
        return list(implementation.get("changed_paths", []))
    return [
        *implementation.get("allowed_changed_paths", []),
        *implementation.get("candidate_additional_paths", []),
    ]


def _semantic(data: dict, layout: L.Layout) -> None:
    kind = data["kind"]
    role = _KIND_ROLE[kind]
    impl = data["implementation"]
    schema_version = data["schema_version"]
    required = impl.get("required_changed_paths", [])

    if schema_version == 2:
        legacy = sorted(
            set(impl) & {"allowed_changed_paths", "candidate_additional_paths"}
        )
        if legacy:
            raise ManifestError(
                f"schema v2 cannot use legacy path fields: {legacy}"
            )
        raw_scope = impl.get("changed_paths")
        if not raw_scope:
            raise ManifestError(
                "schema v2 implementation.changed_paths must be non-empty"
            )
        try:
            current = [L.ensure_literal(path) for path in raw_scope]
        except L.LayoutError as e:
            raise ManifestError(f"changed_paths: {e}") from e
        if len(current) != len(set(current)):
            raise ManifestError("changed_paths has duplicate entries")
    else:
        if "changed_paths" in impl:
            raise ManifestError(
                "schema v1 cannot use changed_paths; migrate to schema v2"
            )
        allowed = impl.get("allowed_changed_paths")
        if not allowed:
            raise ManifestError(
                "schema v1 implementation.allowed_changed_paths must be non-empty"
            )
        # Legacy allowed patterns remain supported for historical registrations.
        try:
            allowed_spec = L.make_spec(allowed)
        except L.LayoutError as e:
            raise ManifestError(f"allowed_changed_paths: {e}") from e
        try:
            additional = [
                L.ensure_literal(path)
                for path in impl.get("candidate_additional_paths", [])
            ]
        except L.LayoutError as e:
            raise ManifestError(f"candidate_additional_paths: {e}") from e
        if len(additional) != len(set(additional)):
            raise ManifestError("candidate_additional_paths has duplicate entries")
        overlap = {
            path for path in additional
            if allowed_spec.match_file(path)
        }
        if overlap:
            raise ManifestError(
                "candidate_additional_paths overlaps source allowed scope: "
                f"{sorted(overlap)}"
            )
        current = [*allowed, *additional]

    try:
        current_spec = L.make_spec(current)
    except L.LayoutError as e:
        raise ManifestError(
            f"current implementation scope is invalid: {e}"
        ) from e

    # core-patch must pin down at least one file it is required to change.
    if kind == "core-patch" and not required:
        raise ManifestError(
            "core-patch must declare at least one required_changed_paths entry"
        )

    for raw in required:
        # literal + normalized (부칙 A-3.2)
        try:
            lit = L.ensure_literal(raw)
        except L.LayoutError as e:
            raise ManifestError(f"required_changed_paths: {e}") from e
        # required ⊆ current changed scope
        if not current_spec.match_file(lit):
            raise ManifestError(
                f"required path not covered by current changed scope: {lit!r}"
            )
        # ownership must match kind
        owner = layout.classify(lit)
        if owner != role:
            raise ManifestError(
                f"required path {lit!r} is owned by {owner!r}, "
                f"but kind {kind!r} requires {role!r}"
            )
    if schema_version == 2:
        for lit in current:
            owner = layout.classify(lit)
            if owner != role:
                raise ManifestError(
                    f"changed path {lit!r} is owned by {owner!r}, "
                    f"but kind {kind!r} requires {role!r}"
                )
    else:
        for lit in additional:
            owner = layout.classify(lit)
            if owner != role:
                raise ManifestError(
                    f"candidate additional path {lit!r} is owned by {owner!r}, "
                    f"but kind {kind!r} requires {role!r}"
                )

    _check_assurance(data.get("assurance", {}))


def _check_assurance(assurance: dict) -> None:
    contracts = assurance.get("contracts", [])
    direct = assurance.get("direct_tests", [])
    for name, items in (("contracts", contracts), ("direct_tests", direct)):
        if len(set(items)) != len(items):
            raise ManifestError(f"assurance.{name} has duplicate entries")
    overlap = set(contracts) & set(direct)
    if overlap:
        # A test declared both as a contract reference and a direct test is the
        # "중복 선언 불일치" case (부칙 A-3.3) — block, don't silently union.
        raise ManifestError(
            f"assurance.contracts and direct_tests overlap: {sorted(overlap)}"
        )


def validate_manifest_set(manifests, layout: L.Layout) -> list[dict]:
    """Validate many manifests and enforce global uniqueness of IDs.

    ``manifests`` is an iterable of (label, dict). Duplicate customization_id
    across the set is a hard error (build_plan T10 code rule).
    """
    seen: dict[str, str] = {}
    out = []
    for label, data in manifests:
        try:
            validate_manifest(data, layout)
        except ManifestError as e:
            raise ManifestError(f"{label}: {e}") from e
        cid = data["customization_id"]
        if cid in seen:
            raise ManifestError(
                f"duplicate customization_id {cid!r} in {label} and {seen[cid]}"
            )
        seen[cid] = label
        out.append(data)
    return out
