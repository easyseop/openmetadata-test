"""T94 — signed, checksum-complete air-gap transfer verification.

The payload digest is computed before signing.  Internal verification checks
that digest, every transferred byte, the expected release lock, and an
organization-supplied offline signature verifier.  If the verifier is absent
or crashes, the result is ``analysis_error`` rather than an unsigned pass.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "airgap-manifest.schema.json"


class AirgapError(ValueError):
    """Air-gap manifest is malformed or unsafe."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def _safe_relative(value: str, field: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "." in path.parts
        or str(path) != value
    ):
        raise AirgapError(f"{field}: path must be normalized and relative")
    return path


def validate_airgap_manifest(data: dict) -> dict:
    if not isinstance(data, dict):
        raise AirgapError("air-gap manifest is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise AirgapError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )
    paths = []
    for item in data["payload"]["files"]:
        paths.append(str(_safe_relative(item["path"], "files.path")))
    if len(paths) != len(set(paths)):
        raise AirgapError("duplicate transferred file path")
    signature_path = str(
        _safe_relative(data["signature"]["path"], "signature.path")
    )
    if signature_path in set(paths):
        raise AirgapError("signature file cannot be part of signed payload files")
    return data


def load_airgap_manifest(path) -> dict:
    return validate_airgap_manifest(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def payload_digest(payload: dict) -> str:
    return verdict.canonical_digest(payload)


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def build_airgap_manifest(
    root,
    *,
    release_lock_digest: str,
    source_commit_sha: str,
    files,
    signature_algorithm: str,
    key_identity: str,
    signature_path: str,
) -> dict:
    """Inventory existing transfer files; signing is performed outside."""
    base = Path(root)
    inventory = []
    for item in files:
        relative = _safe_relative(item["path"], "files.path")
        path = base.joinpath(*relative.parts)
        inventory.append({
            "type": item["type"],
            "path": str(relative),
            "size": path.stat().st_size,
            "sha256": _file_digest(path),
        })
    inventory.sort(key=lambda item: item["path"])
    payload = {
        "release_lock_digest": release_lock_digest,
        "source_commit_sha": source_commit_sha,
        "files": inventory,
    }
    return validate_airgap_manifest({
        "schema_version": 1,
        "payload": payload,
        "signed_payload_digest": payload_digest(payload),
        "signature": {
            "algorithm": signature_algorithm,
            "key_identity": key_identity,
            "path": signature_path,
        },
    })


def verify_airgap_bundle(
    root,
    manifest,
    *,
    expected_release_lock_digest: str,
    signature_verifier=None,
    name: str = "airgap-integrity",
) -> verdict.GateResult:
    """Verify transfer inventory plus an injected offline signature verifier."""
    try:
        item = validate_airgap_manifest(manifest)
    except AirgapError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"invalid air-gap manifest: {exc}",)
        )
    payload = item["payload"]
    if payload["release_lock_digest"] != expected_release_lock_digest:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            ("stale air-gap bundle: release-lock digest mismatch",),
        )
    computed_payload = payload_digest(payload)
    if computed_payload != item["signed_payload_digest"]:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            ("signed payload digest mismatch",),
        )

    base = Path(root)
    mismatches = []
    for expected in payload["files"]:
        relative = PurePosixPath(expected["path"])
        path = base.joinpath(*relative.parts)
        if not path.is_file():
            mismatches.append(f"file missing: {expected['path']}")
            continue
        if path.stat().st_size != expected["size"]:
            mismatches.append(f"file size mismatch: {expected['path']}")
            continue
        if _file_digest(path) != expected["sha256"]:
            mismatches.append(f"file digest mismatch: {expected['path']}")
    signature = item["signature"]
    signature_path = base.joinpath(*PurePosixPath(signature["path"]).parts)
    if not signature_path.is_file():
        mismatches.append(f"signature file missing: {signature['path']}")
    if mismatches:
        return verdict.GateResult(name, verdict.BLOCK, tuple(mismatches))
    if signature_verifier is None:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            ("offline signature verifier unavailable",),
        )
    try:
        signature_ok = signature_verifier(
            item["signed_payload_digest"],
            signature_path,
            signature["key_identity"],
            signature["algorithm"],
        )
    except Exception as exc:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            (f"signature verifier failed: {type(exc).__name__}: {exc}",),
        )
    if signature_ok is not True:
        return verdict.GateResult(
            name, verdict.BLOCK, ("offline signature verification failed",)
        )
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"release_lock_digest={payload['release_lock_digest']}",
            f"files_verified={len(payload['files'])}",
            f"signature={signature['algorithm']}:{signature['key_identity']}",
        ),
    )
