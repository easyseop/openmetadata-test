"""Session-scoped and run-scoped marker lifetime."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from acgh.plancore.errors import PlanControlError
from acgh.plancore.schema import atomic_write

_SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True)
class MarkerPair:
    session_marker: Path
    run_marker: Path
    session_id: str
    project_key: str


def project_key(project_root: str | Path) -> str:
    value = str(Path(project_root).resolve()).encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:24]


def session_marker_path(
    state_root: str | Path,
    project_root: str | Path,
    session_id: str,
) -> Path:
    if not _SESSION_ID.fullmatch(session_id):
        raise PlanControlError(
            "SESSION_ID_INVALID",
            "session id contains unsupported characters",
            details={"session_id": session_id},
        )
    return Path(state_root).resolve() / project_key(project_root) / f"{session_id}.active"


def create_session_marker(
    state_root: str | Path,
    project_root: str | Path,
    session_id: str,
) -> Path:
    marker = session_marker_path(state_root, project_root, session_id)
    if marker.exists():
        raise PlanControlError(
            "SESSION_ALREADY_ACTIVE",
            "this session already has an active plan",
            details={"marker": str(marker)},
        )
    atomic_write(
        marker,
        {
            "schema_version": 1,
            "session_id": session_id,
            "project_key": project_key(project_root),
            "run_dir": None,
        },
    )
    return marker


def load_session_marker(marker: str | Path) -> dict:
    source = Path(marker)
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PlanControlError(
            "SESSION_MARKER_INVALID",
            f"cannot read session marker: {exc}",
            details={"marker": str(source)},
        ) from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise PlanControlError(
            "SESSION_MARKER_INVALID",
            "session marker has an unsupported format",
            details={"marker": str(source)},
        )
    return data


def bind_run(marker: str | Path, run_dir: str | Path) -> MarkerPair:
    source = Path(marker).resolve()
    session = load_session_marker(source)
    if session.get("run_dir") not in (None, str(Path(run_dir).resolve())):
        raise PlanControlError(
            "SESSION_BOUND_TO_OTHER_RUN",
            "session marker is already bound to another run",
            details={"run_dir": session.get("run_dir")},
        )
    run = Path(run_dir).resolve()
    run_marker = run / ".plan-active"
    if run_marker.exists():
        raise PlanControlError(
            "RUN_ALREADY_ACTIVE",
            "run marker already exists",
            details={"run_marker": str(run_marker)},
        )
    session["run_dir"] = str(run)
    atomic_write(source, session)
    atomic_write(
        run_marker,
        {
            "schema_version": 1,
            "session_id": session["session_id"],
            "project_key": session["project_key"],
            "session_marker": str(source),
            "run_dir": str(run),
            "proposal_dir": str(run / "proposal"),
        },
    )
    return MarkerPair(
        session_marker=source,
        run_marker=run_marker,
        session_id=session["session_id"],
        project_key=session["project_key"],
    )


def pair_from_run(run_dir: str | Path) -> MarkerPair:
    marker = Path(run_dir).resolve() / ".plan-active"
    try:
        data = yaml.safe_load(marker.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PlanControlError(
            "RUN_MARKER_INVALID",
            f"cannot read run marker: {exc}",
            details={"run_marker": str(marker)},
        ) from exc
    required = {"session_marker", "session_id", "project_key", "run_dir"}
    if not isinstance(data, dict) or not required.issubset(data):
        raise PlanControlError(
            "RUN_MARKER_INVALID",
            "run marker is missing required fields",
            details={"run_marker": str(marker)},
        )
    if Path(data["run_dir"]).resolve() != Path(run_dir).resolve():
        raise PlanControlError(
            "RUN_MARKER_MISMATCH",
            "run marker points to a different run directory",
        )
    return MarkerPair(
        session_marker=Path(data["session_marker"]).resolve(),
        run_marker=marker,
        session_id=data["session_id"],
        project_key=data["project_key"],
    )


def cleanup_pair(pair: MarkerPair) -> None:
    if pair.run_marker.exists():
        current = pair_from_run(pair.run_marker.parent)
        if current.session_id != pair.session_id:
            raise PlanControlError(
                "MARKER_OWNERSHIP_MISMATCH",
                "refusing to clean another session's run marker",
            )
        pair.run_marker.unlink()
    if pair.session_marker.exists():
        session = load_session_marker(pair.session_marker)
        if session.get("session_id") != pair.session_id:
            raise PlanControlError(
                "MARKER_OWNERSHIP_MISMATCH",
                "refusing to clean another session's marker",
            )
        pair.session_marker.unlink()


def cleanup_unbound_session(marker: str | Path) -> None:
    """Remove only an unbound marker owned by the marker's recorded session."""
    source = Path(marker).resolve()
    if not source.exists():
        return
    session = load_session_marker(source)
    if session.get("run_dir") is not None:
        raise PlanControlError(
            "SESSION_ALREADY_BOUND",
            "refusing to clean a session marker that is bound to a run",
        )
    source.unlink()
