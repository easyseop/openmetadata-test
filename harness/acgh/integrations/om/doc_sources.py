"""Official documentation collection for OpenMetadata upgrade planning."""

from __future__ import annotations

import hashlib
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from acgh.plancore.errors import PlanControlError
from acgh.plancore.schema import atomic_write


def _snapshot_name(index: int, source: str) -> str:
    parsed = urllib.parse.urlparse(source)
    candidate = Path(parsed.path).name or f"document-{index}.bin"
    candidate = re.sub(r"[^A-Za-z0-9._-]", "-", candidate)[:80]
    return f"{index:02d}-{candidate or 'document.bin'}"


def _read_raw(source: str) -> bytes:
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in ("http", "https", "file"):
        try:
            with urllib.request.urlopen(source, timeout=30) as response:
                return response.read()
        except (OSError, urllib.error.URLError) as exc:
            raise PlanControlError(
                "OFFICIAL_DOCUMENT_UNAVAILABLE",
                f"cannot retrieve official document: {source}",
                details={"source": source, "error": str(exc)},
            ) from exc
    path = Path(source)
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PlanControlError(
            "OFFICIAL_DOCUMENT_UNAVAILABLE",
            f"cannot read official document snapshot: {source}",
            details={"source": source, "error": str(exc)},
        ) from exc


def collect_document_snapshots(request: dict, run_dir: str | Path) -> dict:
    documents = request.get("official_documents") or []
    if request.get("mode") != "upgrade":
        return {"schema_version": 1, "documents": []}
    if not documents:
        raise PlanControlError(
            "OFFICIAL_DOCUMENTS_REQUIRED",
            "upgrade mode requires at least one official document",
        )
    output_root = Path(run_dir) / "official-doc-snapshots"
    output_root.mkdir(parents=True, exist_ok=True)
    records = []
    for index, spec in enumerate(documents, start=1):
        source = spec["source"]
        version_token = spec["version_token"]
        raw = _read_raw(source)
        if version_token.encode("utf-8") not in raw:
            raise PlanControlError(
                "OFFICIAL_DOCUMENT_VERSION_MISMATCH",
                "official document does not contain the required version token",
                details={"source": source, "version_token": version_token},
            )
        name = _snapshot_name(index, source)
        snapshot = output_root / name
        snapshot.write_bytes(raw)
        records.append(
            {
                "source": source,
                "version_token": version_token,
                "snapshot_path": f"official-doc-snapshots/{name}",
                "byte_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "deployment_methods": spec.get("deployment_methods", []),
            }
        )
    result = {"schema_version": 1, "documents": records}
    atomic_write(Path(run_dir) / "official-doc-sources.yaml", result)
    return result


def verify_document_snapshots(run_dir: str | Path, recorded: dict) -> None:
    root = Path(run_dir).resolve()
    for item in recorded.get("documents", []):
        snapshot = (root / item["snapshot_path"]).resolve()
        try:
            snapshot.relative_to(root / "official-doc-snapshots")
        except ValueError as exc:
            raise PlanControlError(
                "OFFICIAL_DOCUMENT_PATH_INVALID",
                "snapshot path escapes its run directory",
                details={"snapshot_path": item.get("snapshot_path")},
            ) from exc
        try:
            raw = snapshot.read_bytes()
        except OSError as exc:
            raise PlanControlError(
                "OFFICIAL_DOCUMENT_SNAPSHOT_MISSING",
                f"cannot read snapshot: {snapshot}",
            ) from exc
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        if digest != item.get("byte_digest"):
            raise PlanControlError(
                "OFFICIAL_DOCUMENT_DIGEST_MISMATCH",
                "official document bytes no longer match the recorded digest",
                details={"snapshot_path": item.get("snapshot_path")},
            )
        token = str(item.get("version_token", "")).encode("utf-8")
        if not token or token not in raw:
            raise PlanControlError(
                "OFFICIAL_DOCUMENT_VERSION_MISMATCH",
                "snapshot no longer contains its recorded version token",
                details={"snapshot_path": item.get("snapshot_path")},
            )
