from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from acgh.plancore.errors import PlanControlError
from acgh.plancore.markers import bind_run, create_session_marker
from acgh.plancore.markers import record_trusted_input_lock_digest
from harness import om_workflow


def _request_file(path: Path, checker: Path) -> Path:
    request = {
        "schema_version": 1,
        "run_id": "cli-start",
        "mode": "initial",
        "repositories": {"product": str(path), "checker": str(checker)},
        "refs": {"official": "official", "current_custom": "custom"},
        "product_version": "1.0.0",
        "owner": "data-team",
    }
    source = path / "request.yaml"
    source.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return source


def test_plan_start_cli_accepts_simple_and_override_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "om_workflow.py",
            "plan",
            "start",
            "/work/request.yaml",
            "--run-dir",
            "/work/run",
            "--state-root",
            "/work/state",
            "--session-id",
            "operator-a",
            "--project-root",
            "/work/checker",
        ],
    )

    args = om_workflow.parse_args()

    assert args.command == "plan"
    assert args.plan_action == "start"
    assert args.request == Path("/work/request.yaml")
    assert args.run_dir == Path("/work/run")
    assert args.state_root == Path("/work/state")
    assert args.session_id == "operator-a"


@pytest.mark.parametrize(
    "removed_command",
    [
        "apply",
        "bootstrap",
        "risk",
        "runtime",
        "source",
        "watch",
        "patch-kill",
        "typecheck",
        "resolve-json",
    ],
)
def test_clean_export_rejects_removed_dangling_commands(
    monkeypatch: pytest.MonkeyPatch,
    removed_command: str,
) -> None:
    monkeypatch.setattr(sys, "argv", ["om_workflow.py", removed_command])

    with pytest.raises(SystemExit) as caught:
        om_workflow.parse_args()

    assert caught.value.code == 2


def test_plan_requires_an_executable_subcommand(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["om_workflow.py", "plan"])

    with pytest.raises(SystemExit) as caught:
        om_workflow.parse_args()

    assert caught.value.code == 2


def test_start_allocator_never_reuses_existing_run(tmp_path: Path) -> None:
    existing = tmp_path / "om-plan-initial-fixed"
    existing.mkdir()

    selected = om_workflow.allocate_plan_run_dir(
        tmp_path,
        "initial",
        timestamp_value="fixed",
    )

    assert selected == tmp_path / "om-plan-initial-fixed-01"
    assert selected != existing
    assert not selected.exists()


def test_automatic_session_id_retries_a_collision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    create_session_marker(state, project, "collision")
    identifiers = iter(["collision", "fresh-session"])
    monkeypatch.setattr(
        om_workflow,
        "_new_plan_session_id",
        lambda: next(identifiers),
    )

    session_id, marker = om_workflow._create_or_reuse_session_marker(
        state,
        project,
        None,
    )

    assert session_id == "fresh-session"
    assert marker.is_file()


def test_plan_start_uses_session_id_supplied_by_trusted_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    marker = create_session_marker(state, project, "claude-session-a")
    monkeypatch.setenv("OM_PLAN_SESSION_ID", "claude-session-a")

    selected = om_workflow.select_plan_session_id(None)

    assert selected == "claude-session-a"
    session_id, selected_marker = om_workflow._create_or_reuse_session_marker(
        state,
        project,
        selected,
    )
    assert session_id == "claude-session-a"
    assert selected_marker == marker


def test_plan_check_stops_when_multiple_runs_are_active(tmp_path: Path) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    for session_id in ("one", "two"):
        marker = create_session_marker(state, project, session_id)
        run = tmp_path / f"run-{session_id}"
        run.mkdir()
        bind_run(marker, run)

    with pytest.raises(PlanControlError) as caught:
        om_workflow.select_incomplete_plan_run(state, project)

    assert caught.value.code == "PLAN_RUN_AMBIGUOUS"
    assert [item["session_id"] for item in caught.value.details["runs"]] == [
        "one",
        "two",
    ]


def test_plan_check_selects_the_only_active_run(tmp_path: Path) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    marker = create_session_marker(state, project, "only")
    run = tmp_path / "run-only"
    run.mkdir()
    bind_run(marker, run)

    selected = om_workflow.select_incomplete_plan_run(state, project)

    assert selected == run


def test_plan_start_explicit_overrides_call_existing_preflight_unchanged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    checker = tmp_path / "checker"
    checker.mkdir()
    request = _request_file(tmp_path, checker)
    run_dir = tmp_path / "run"
    state = tmp_path / "state"
    captured: dict[str, object] = {}
    digest = "sha256:" + "a" * 64

    def fake_preflight(request_path, destination, adapter, *, session_marker):
        captured.update(
            request=Path(request_path),
            run_dir=Path(destination),
            adapter=type(adapter),
            session_marker=Path(session_marker),
        )
        Path(destination).mkdir()
        bind_run(session_marker, destination)
        return {
            "status": "ready_for_proposal",
            "run_dir": str(Path(destination).resolve()),
            "input_lock_digest": digest,
            "session_id": "operator-a",
        }

    monkeypatch.setattr(om_workflow, "run_preflight", fake_preflight)
    args = SimpleNamespace(
        request=request,
        run_dir=run_dir,
        evidence_root=None,
        state_root=state,
        session_id="operator-a",
        project_root=checker,
    )

    result = om_workflow.start_plan_run(args)

    assert captured["request"] == request
    assert captured["run_dir"] == run_dir
    assert captured["adapter"] is om_workflow.OpenMetadataPlanAdapter
    assert result["status"] == "ready_for_proposal"
    assert result["input_lock_digest"] == digest
    assert result["run_dir"] == str(run_dir)
    assert " plan check " in result["next_command"]


def test_plan_check_uses_digest_retained_at_start(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    run = tmp_path / "run"
    run.mkdir()
    marker = create_session_marker(state, project, "one")
    bind_run(marker, run)
    digest = "sha256:" + "b" * 64
    record_trusted_input_lock_digest(marker, digest)
    captured: dict[str, object] = {}

    def fake_validation(run_dir, adapter, *, expected_input_lock_digest):
        captured.update(
            run_dir=Path(run_dir),
            adapter=type(adapter),
            digest=expected_input_lock_digest,
        )
        return {"verdict": "approval"}

    monkeypatch.setattr(om_workflow, "run_validation", fake_validation)
    args = SimpleNamespace(
        run_dir=run,
        state_root=None,
        project_root=project,
        expected_input_lock_digest=None,
    )

    result = om_workflow.check_plan_run(args)

    assert result == {"verdict": "approval"}
    assert captured == {
        "run_dir": run,
        "adapter": om_workflow.OpenMetadataPlanAdapter,
        "digest": digest,
    }


def test_plan_check_rejects_digest_override_that_changes_trusted_value(
    tmp_path: Path,
) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    run = tmp_path / "run"
    run.mkdir()
    marker = create_session_marker(state, project, "one")
    bind_run(marker, run)
    record_trusted_input_lock_digest(marker, "sha256:" + "b" * 64)
    args = SimpleNamespace(
        run_dir=run,
        state_root=None,
        project_root=project,
        expected_input_lock_digest="sha256:" + "c" * 64,
    )

    with pytest.raises(PlanControlError) as caught:
        om_workflow.check_plan_run(args)

    assert caught.value.code == "TRUSTED_INPUT_LOCK_DIGEST_MISMATCH"


def test_plan_check_accepts_external_digest_for_legacy_explicit_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "checker"
    project.mkdir()
    state = tmp_path / "state"
    run = tmp_path / "run"
    run.mkdir()
    marker = create_session_marker(state, project, "legacy")
    bind_run(marker, run)
    supplied = "sha256:" + "d" * 64
    captured: dict[str, object] = {}

    def fake_validation(run_dir, adapter, *, expected_input_lock_digest):
        captured["digest"] = expected_input_lock_digest
        return {"verdict": "approval"}

    monkeypatch.setattr(om_workflow, "run_validation", fake_validation)
    args = SimpleNamespace(
        run_dir=run,
        state_root=None,
        project_root=project,
        expected_input_lock_digest=supplied,
    )

    result = om_workflow.check_plan_run(args)

    assert result == {"verdict": "approval"}
    assert captured["digest"] == supplied
