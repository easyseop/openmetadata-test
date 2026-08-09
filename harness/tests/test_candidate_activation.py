"""Candidate lock preparation, approval and activation (public CLI).

The three commands stay separate on purpose: the tool may place and verify a
lock, only a human may approve it, and activation re-verifies instead of
trusting what it was handed. These tests pin that boundary, the non-overwrite
guarantees around hand-made files, and the registration binding rules.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from acgh import candidate
from acgh import candidate_select
from harness import run_phase_bundle


def _git(repo, *args, env=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True, env=env,
    ).stdout.strip()


ARTIFACT_DIGEST = "sha256:" + "a" * 64


def _fixture(tmp_path, *, artifact_kind="build-artifact", repository="bank/product"):
    repo = tmp_path / "product"
    repo.mkdir()
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    _git(repo, "init", "-q")
    (repo / "svc").mkdir()
    (repo / "svc/a.java").write_text("class A {}\n", encoding="utf-8")
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-qm", "official", env=env)
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "svc/a.java").write_text("class A { int bank; }\n", encoding="utf-8")
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-qm", "bank\n\nCustomization-ID: BANK-OM-001", env=env)
    custom = _git(repo, "rev-parse", "HEAD")

    registration = tmp_path / "registration"
    registration.mkdir()
    (registration / "customization-registry.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "source": {
            "repository": repository,
            "upstream_repository": "vendor/product",
            "upstream_tag": "1.0.0-release",
            "upstream_sha": base,
        },
    }), encoding="utf-8")

    lock = candidate.build_candidate_lock(
        str(repo), custom,
        upstream_repository="vendor/product",
        upstream_base_sha=base,
        upstream_target_sha=base,
        candidate_repository="bank/product",
        artifact_digest=ARTIFACT_DIGEST,
        artifact_kind=artifact_kind,
    )
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    source_lock = evidence / "candidate-lock.yaml"
    source_lock.write_text(
        yaml.safe_dump(lock.canonical(), allow_unicode=True, sort_keys=True),
        encoding="utf-8",
    )
    source_result = evidence / "acgh-result.yaml"
    source_result.write_text(yaml.safe_dump(_result_payload(lock)), encoding="utf-8")
    return SimpleNamespace(
        repo=repo, registration=registration, base=base, custom=custom,
        lock=lock, source_lock=source_lock, source_result=source_result,
        locks_dir=registration / "candidate-locks",
    )


def _result_payload(lock, **override):
    inputs = {
        "repositories": {
            "candidate": {
                "repository": lock.candidate.repository,
                "sha": lock.candidate.commit_sha,
                "tree_sha": lock.candidate.tree_sha,
            },
            "upstream_base": {"repository": lock.upstream.repository, "sha": lock.upstream.base_sha},
            "upstream_target": {"repository": lock.upstream.repository, "sha": lock.upstream.target_sha},
        },
        "artifact_digest": lock.candidate.artifact_digest,
        "artifact_kind": lock.candidate.artifact_kind,
        "candidate_lock_digest": lock.digest(),
        "integration_strategy": lock.integration_strategy,
    }
    inputs.update(override.pop("inputs", {}))
    payload = {
        "schema_version": 1,
        "canonical_payload": {
            "verdict": override.pop("verdict", "pass"),
            "gates": [{"name": "contract", "verdict": "pass", "reasons": []}],
            "inputs": inputs,
            "harness_version": "sha256:" + "b" * 64,
        },
        "result_digest": "sha256:" + "c" * 64,
    }
    payload.update(override)
    return payload


def _prepare(fx, name="baseline", **extra):
    args = SimpleNamespace(
        registration=fx.registration,
        source_lock=fx.source_lock,
        source_result=fx.source_result,
        name=name,
        allow_repository_mismatch=extra.pop("allow_repository_mismatch", False),
    )
    return run_phase_bundle.candidate_prepare_command(args)


def _template(fx, tmp_path, name="baseline", *, output=None, **values):
    args = SimpleNamespace(
        registration=fx.registration,
        lock_name=name,
        approver=values.pop("approver", None),
        approved_at=values.pop("approved_at", None),
        rationale=values.pop("rationale", None),
        output=str(output or (tmp_path / "approval.yaml")),
    )
    return run_phase_bundle.candidate_approval_template_command(args)


def _activate(fx, approval, name="baseline", **extra):
    args = SimpleNamespace(
        registration=fx.registration,
        lock_name=name,
        approval=approval,
        replace_active=extra.pop("replace_active", False),
        allow_repository_mismatch=extra.pop("allow_repository_mismatch", False),
        record=extra.pop("record", None),
    )
    return run_phase_bundle.candidate_activate_command(args)


def _human_approval(path, lock_digest, **override):
    payload = {
        "candidate_lock_digest": lock_digest,
        "approver": override.pop("approver", "데이터시스템부"),
        "approved_at": override.pop("approved_at", "2026-08-09T12:00:00+09:00"),
        "rationale": override.pop("rationale", "1.13.1 기준선을 사전검사에 사용 승인"),
        "approval_confirmed": override.pop("approval_confirmed", True),
    }
    payload.update(override)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


def _last_json(capsys):
    for line in reversed(capsys.readouterr().out.splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise AssertionError("no JSON document on stdout")


# ---- normal flow -----------------------------------------------------------
def test_prepare_approve_activate_makes_candidate_select_succeed(tmp_path, capsys):
    fx = _fixture(tmp_path)
    assert _prepare(fx) == 0
    prepared = _last_json(capsys)
    assert prepared["status"] == "prepared"
    assert prepared["approved"] is False
    assert "--artifact-digest" in prepared["artifact_kind_notice"]

    approval_form = tmp_path / "approval.yaml"
    assert _template(fx, tmp_path, output=approval_form) == 0
    form = yaml.safe_load(approval_form.read_text(encoding="utf-8"))
    assert form["approval_confirmed"] is False
    assert form["candidate_lock_digest"] == fx.lock.digest()

    _human_approval(approval_form, fx.lock.digest())
    assert _activate(fx, approval_form) == 0
    activated = _last_json(capsys)
    assert activated["activated"] is True
    assert activated["pointer_status"] == "activated"
    assert "조직 권한" in activated["authority_notice"]

    selection = candidate_select.select_active_candidate(fx.registration)
    assert selection.status == candidate_select.SELECTED
    assert selection.lock_digest == fx.lock.digest()
    # the approver's file is stored byte-for-byte so git review sees what was signed
    stored = fx.locks_dir / "baseline.approval.yaml"
    assert stored.read_bytes() == approval_form.read_bytes()


def test_preparing_the_same_lock_twice_is_idempotent(tmp_path, capsys):
    fx = _fixture(tmp_path)
    assert _prepare(fx) == 0
    capsys.readouterr()
    assert _prepare(fx) == 0
    assert _last_json(capsys)["status"] == "already_prepared"


def test_template_to_stdout_emits_pure_yaml(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx)
    capsys.readouterr()
    assert _template(fx, tmp_path, output="-") == 0
    document = yaml.safe_load(capsys.readouterr().out)
    assert document["approval_confirmed"] is False
    assert document["approver"] == ""


# ---- the tool must never complete an approval on its own -------------------
def test_flag_generated_approval_alone_cannot_activate(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx)
    form = tmp_path / "flags.yaml"
    assert _template(
        fx, tmp_path, output=form,
        approver="데이터시스템부",
        approved_at="2026-08-09T12:00:00+09:00",
        rationale="자동 생성 값",
    ) == 0
    generated = yaml.safe_load(form.read_text(encoding="utf-8"))
    assert generated["provenance"]["values_source"] == "cli-flags"
    assert generated["approval_confirmed"] is False

    capsys.readouterr()
    assert _activate(fx, form) == 1
    blocked = _last_json(capsys)
    assert blocked["status"] == "blocked"
    assert "비대화형" in blocked["reason"]
    assert not (fx.locks_dir / "active-candidate.yaml").exists()


def test_partial_approval_flags_report_missing_fields_without_stdin(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx)
    capsys.readouterr()
    assert _template(fx, tmp_path, approver="데이터시스템부") == 2
    payload = _last_json(capsys)
    assert payload["status"] == "input_required"
    assert payload["missing_fields"] == ["approved_at", "rationale"]


def test_template_command_runs_without_stdin(tmp_path):
    """A heredoc/CI run must not block on input() or die with EOFError."""
    fx = _fixture(tmp_path)
    _prepare(fx)
    output = tmp_path / "no-stdin.yaml"
    runner = Path(run_phase_bundle.__file__)
    completed = subprocess.run(
        [
            sys.executable, str(runner),
            "candidate-approval-template",
            "--registration", str(fx.registration),
            "--lock-name", "baseline",
            "--output", str(output),
        ],
        stdin=subprocess.DEVNULL, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(runner.parent)},
    )
    assert completed.returncode == 0, completed.stderr
    assert "EOFError" not in completed.stderr
    assert output.is_file()


# ---- approval content counterexamples --------------------------------------
@pytest.mark.parametrize("override, expected", [
    ({"approver": ""}, "approver"),
    ({"approver": "TBD"}, "approver"),
    ({"rationale": "  "}, "rationale"),
    ({"approved_at": "2026-08-09T12:00:00"}, "RFC3339"),
])
def test_incomplete_approval_blocks_activation(tmp_path, capsys, override, expected):
    fx = _fixture(tmp_path)
    _prepare(fx)
    form = _human_approval(tmp_path / "a.yaml", fx.lock.digest(), **override)
    capsys.readouterr()
    assert _activate(fx, form) == 1
    assert expected in _last_json(capsys)["reason"]
    assert not (fx.locks_dir / "active-candidate.yaml").exists()


def test_tampered_approval_digest_blocks_activation(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx)
    form = _human_approval(tmp_path / "a.yaml", "sha256:" + "0" * 64)
    capsys.readouterr()
    assert _activate(fx, form) == 1
    assert "candidate_lock_digest" in _last_json(capsys)["reason"]


def test_unconfirmed_hand_written_approval_blocks_activation(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx)
    form = _human_approval(tmp_path / "a.yaml", fx.lock.digest(), approval_confirmed=False)
    capsys.readouterr()
    assert _activate(fx, form) == 1
    assert "approval_confirmed" in _last_json(capsys)["reason"]


# ---- lock name and source-result counterexamples ---------------------------
@pytest.mark.parametrize("name", [
    "../escape", "/absolute", "active-candidate", "baseline.approval",
    "baseline.yaml", "a/b", "..", "",
])
def test_unsafe_lock_names_are_rejected(tmp_path, name):
    fx = _fixture(tmp_path)
    with pytest.raises(run_phase_bundle.PhaseCLIError):
        _prepare(fx, name=name)
    assert not fx.locks_dir.exists()


def test_non_pass_source_result_blocks_preparation(tmp_path):
    fx = _fixture(tmp_path)
    fx.source_result.write_text(
        yaml.safe_dump(_result_payload(fx.lock, verdict="approval")), encoding="utf-8"
    )
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="pass가 아닙니다"):
        _prepare(fx)
    assert not fx.locks_dir.exists()


@pytest.mark.parametrize("field, value, expected", [
    ("candidate_lock_digest", "sha256:" + "0" * 64, "Candidate lock digest"),
    ("artifact_digest", "sha256:" + "0" * 64, "artifact digest"),
    ("artifact_kind", "source-tree", "artifact kind"),
])
def test_source_result_that_names_another_candidate_blocks(tmp_path, field, value, expected):
    fx = _fixture(tmp_path)
    fx.source_result.write_text(
        yaml.safe_dump(_result_payload(fx.lock, inputs={field: value})), encoding="utf-8"
    )
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match=expected):
        _prepare(fx)


def test_source_result_with_another_candidate_commit_blocks(tmp_path):
    fx = _fixture(tmp_path)
    payload = _result_payload(fx.lock)
    payload["canonical_payload"]["inputs"]["repositories"]["candidate"]["sha"] = "0" * 40
    fx.source_result.write_text(yaml.safe_dump(payload), encoding="utf-8")
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="candidate commit"):
        _prepare(fx)


# ---- registration binding (P1-3) -------------------------------------------
def test_lock_from_another_baseline_is_blocked(tmp_path):
    fx = _fixture(tmp_path)
    registry = fx.registration / "customization-registry.yaml"
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    data["source"]["upstream_sha"] = "9" * 40
    registry.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="upstream base"):
        _prepare(fx)
    assert not fx.locks_dir.exists()


def test_repository_difference_needs_explicit_acknowledgement(tmp_path, capsys):
    fx = _fixture(tmp_path, repository="bank/moved-elsewhere")
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="allow-repository-mismatch"):
        _prepare(fx)
    assert _prepare(fx, allow_repository_mismatch=True) == 0
    payload = _last_json(capsys)
    assert payload["status"] == "prepared"
    assert any("저장소가 다릅니다" in note for note in payload["notes"])


# ---- non-overwrite guarantees ----------------------------------------------
def test_a_different_lock_under_the_same_name_is_never_overwritten(tmp_path):
    fx = _fixture(tmp_path)
    _prepare(fx)
    original = (fx.locks_dir / "baseline.yaml").read_bytes()
    other = candidate.build_candidate_lock(
        str(fx.repo), fx.base,
        upstream_repository="vendor/product",
        upstream_base_sha=fx.base, upstream_target_sha=fx.base,
        candidate_repository="bank/product",
        artifact_digest="sha256:" + "d" * 64, artifact_kind="build-artifact",
    )
    fx.source_lock.write_text(
        yaml.safe_dump(other.canonical(), allow_unicode=True, sort_keys=True), encoding="utf-8"
    )
    fx.source_result.write_text(yaml.safe_dump(_result_payload(other)), encoding="utf-8")
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="덮어쓰지 않습니다"):
        _prepare(fx)
    assert (fx.locks_dir / "baseline.yaml").read_bytes() == original


def test_a_different_stored_approval_is_never_overwritten(tmp_path):
    fx = _fixture(tmp_path)
    _prepare(fx)
    first = _human_approval(tmp_path / "first.yaml", fx.lock.digest())
    assert _activate(fx, first) == 0
    stored = (fx.locks_dir / "baseline.approval.yaml").read_bytes()
    second = _human_approval(
        tmp_path / "second.yaml", fx.lock.digest(), rationale="다른 사유로 재승인"
    )
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="덮어쓰지 않습니다"):
        _activate(fx, second)
    assert (fx.locks_dir / "baseline.approval.yaml").read_bytes() == stored


def test_activating_another_candidate_requires_replace_active(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx, name="first")
    assert _activate(fx, _human_approval(tmp_path / "a.yaml", fx.lock.digest()), name="first") == 0
    previous = fx.lock.digest()

    other = candidate.build_candidate_lock(
        str(fx.repo), fx.base,
        upstream_repository="vendor/product",
        upstream_base_sha=fx.base, upstream_target_sha=fx.base,
        candidate_repository="bank/product",
        artifact_digest="sha256:" + "e" * 64, artifact_kind="build-artifact",
    )
    fx.source_lock.write_text(
        yaml.safe_dump(other.canonical(), allow_unicode=True, sort_keys=True), encoding="utf-8"
    )
    fx.source_result.write_text(yaml.safe_dump(_result_payload(other)), encoding="utf-8")
    _prepare(fx, name="second")
    approval = _human_approval(tmp_path / "b.yaml", other.digest())

    capsys.readouterr()
    assert _activate(fx, approval, name="second") == 1
    assert "--replace-active" in _last_json(capsys)["reason"]
    pointer = yaml.safe_load((fx.locks_dir / "active-candidate.yaml").read_text(encoding="utf-8"))
    assert pointer["candidate_lock_digest"] == previous

    assert _activate(fx, approval, name="second", replace_active=True) == 0
    replaced = _last_json(capsys)
    assert replaced["pointer_status"] == "replaced"
    assert replaced["previous_candidate_lock_digest"] == previous
    assert "재사용할 수 없으며" in replaced["replacement_notice"]


def test_activation_is_idempotent_for_the_same_candidate(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _prepare(fx)
    approval = _human_approval(tmp_path / "a.yaml", fx.lock.digest())
    assert _activate(fx, approval) == 0
    capsys.readouterr()
    assert _activate(fx, approval) == 0
    payload = _last_json(capsys)
    assert payload["pointer_status"] == "already_active"
    assert payload["approval_status"] == "already_stored"


def test_a_reserved_path_stops_a_concurrent_activation(tmp_path):
    fx = _fixture(tmp_path)
    _prepare(fx)
    reservation = fx.locks_dir / ".baseline.approval.yaml.lock"
    reservation.write_text('{"pid": 4242}', encoding="utf-8")
    approval = _human_approval(tmp_path / "a.yaml", fx.lock.digest())
    with pytest.raises(run_phase_bundle.PhaseCLIError, match="사용 중"):
        _activate(fx, approval)
    assert not (fx.locks_dir / "baseline.approval.yaml").exists()
    assert not (fx.locks_dir / "active-candidate.yaml").exists()


def test_a_failed_write_leaves_no_partial_file(tmp_path, monkeypatch):
    fx = _fixture(tmp_path)
    real_replace = os.replace

    def explode(src, dst):
        if str(dst).endswith("baseline.yaml"):
            raise OSError("simulated failure")
        return real_replace(src, dst)

    monkeypatch.setattr(run_phase_bundle.os, "replace", explode)
    with pytest.raises(OSError, match="simulated failure"):
        _prepare(fx)
    assert not (fx.locks_dir / "baseline.yaml").exists()
    assert list(fx.locks_dir.glob(".*")) == []


# ---- read-only verification of hand-made files (P1-1) ----------------------
def _hand_made_bundle(fx):
    """Recreate the pre-CLI layout: files written by hand, no provenance."""
    fx.locks_dir.mkdir(parents=True, exist_ok=True)
    (fx.locks_dir / "baseline.yaml").write_text(
        yaml.safe_dump(fx.lock.canonical(), allow_unicode=True, sort_keys=True),
        encoding="utf-8",
    )
    (fx.locks_dir / "baseline.approval.yaml").write_text(yaml.safe_dump({
        "candidate_lock_digest": fx.lock.digest(),
        "approver": "데이터시스템부",
        "approved_at": "2026-08-09T03:00:11+09:00",
        "rationale": "수동으로 복구한 승인",
    }, allow_unicode=True), encoding="utf-8")
    (fx.locks_dir / "active-candidate.yaml").write_text(
        yaml.safe_dump({"candidate_lock_digest": fx.lock.digest()}), encoding="utf-8"
    )


def test_verify_reports_hand_made_files_as_usable_without_touching_them(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _hand_made_bundle(fx)
    before = {p.name: p.read_bytes() for p in fx.locks_dir.iterdir()}

    args = SimpleNamespace(registration=fx.registration, source_lock=fx.source_lock)
    assert run_phase_bundle.candidate_verify_command(args) == 0
    report = _last_json(capsys)
    assert report["status"] == "consistent"
    assert report["selectable"] is True
    entry = report["locks"][0]
    assert entry["is_active"] is True
    assert entry["matches_source_lock"] is True
    assert entry["approval"]["cli_generated"] is False
    assert any("수동으로 만든 승인 파일" in note for note in report["notes"])
    assert {p.name: p.read_bytes() for p in fx.locks_dir.iterdir()} == before


def test_verify_reports_a_lock_that_does_not_match_the_source(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _hand_made_bundle(fx)
    other = candidate.build_candidate_lock(
        str(fx.repo), fx.base,
        upstream_repository="vendor/product",
        upstream_base_sha=fx.base, upstream_target_sha=fx.base,
        candidate_repository="bank/product",
        artifact_digest="sha256:" + "f" * 64, artifact_kind="build-artifact",
    )
    fx.source_lock.write_text(
        yaml.safe_dump(other.canonical(), allow_unicode=True, sort_keys=True), encoding="utf-8"
    )
    args = SimpleNamespace(registration=fx.registration, source_lock=fx.source_lock)
    assert run_phase_bundle.candidate_verify_command(args) == 0
    assert _last_json(capsys)["locks"][0]["matches_source_lock"] is False


def test_verify_flags_an_active_pointer_without_approval(tmp_path, capsys):
    fx = _fixture(tmp_path)
    _hand_made_bundle(fx)
    (fx.locks_dir / "baseline.approval.yaml").unlink()
    args = SimpleNamespace(registration=fx.registration, source_lock=None)
    assert run_phase_bundle.candidate_verify_command(args) == 3
    report = _last_json(capsys)
    assert report["selectable"] is False
    assert any("승인 파일이 없습니다" in problem for problem in report["problems"])


def test_hand_made_files_block_prepare_and_activate_with_guidance(tmp_path, capsys):
    """The CLI must not silently take over files a human already placed."""
    fx = _fixture(tmp_path)
    _hand_made_bundle(fx)
    before = {p.name: p.read_bytes() for p in fx.locks_dir.iterdir()}

    # same content -> reported as already prepared, still not overwritten
    assert _prepare(fx) == 0
    assert _last_json(capsys)["status"] == "already_prepared"

    form = _human_approval(tmp_path / "new.yaml", fx.lock.digest())
    with pytest.raises(run_phase_bundle.CandidatePolicyBlock, match="candidate-verify"):
        _activate(fx, form)
    assert {p.name: p.read_bytes() for p in fx.locks_dir.iterdir()} == before


# ---- public workflow surface -----------------------------------------------
def test_om_workflow_exposes_the_candidate_preparation_commands(monkeypatch):
    from harness import om_workflow

    commands = {
        "candidate-verify": ["--version", "1.13.1"],
        "candidate-prepare": [
            "--version", "1.13.1", "--source-lock", "/work/lock.yaml",
            "--source-result", "/work/result.yaml", "--name", "baseline",
        ],
        "candidate-approval-template": ["--version", "1.13.1", "--lock-name", "baseline"],
        "candidate-activate": [
            "--version", "1.13.1", "--lock-name", "baseline",
            "--approval", "/work/approval.yaml",
        ],
    }
    for command, arguments in commands.items():
        monkeypatch.setattr(sys, "argv", ["om_workflow.py", command, *arguments])
        parsed = om_workflow.parse_args()
        assert parsed.command == command
        assert parsed.version == "1.13.1"
        # --version selects the registration bundle; the clearer spelling works too
        alias = ["--registration-version" if item == "--version" else item for item in arguments]
        monkeypatch.setattr(sys, "argv", ["om_workflow.py", command, *alias])
        assert om_workflow.parse_args().version == "1.13.1"


def test_human_activation_block_names_the_missing_human_step(capsys):
    from harness import om_workflow

    om_workflow._print_human_phase("candidate-activate", {
        "status": "blocked",
        "process_exit_code": 1,
        "reason": "비대화형으로 생성한 승인 값만으로는 활성화할 수 없습니다.",
        "activated": False,
        "candidate_lock_digest": "sha256:" + "1" * 64,
    })
    out = capsys.readouterr().out
    assert "[준비 3/3]" in out
    assert "비대화형" in out
    assert "candidate-activate를 다시 실행" in out


def test_human_verify_output_reports_manual_files(capsys):
    from harness import om_workflow

    om_workflow._print_human_phase("candidate-verify", {
        "status": "consistent",
        "process_exit_code": 0,
        "selectable": True,
        "selection_status": "selected",
        "active_candidate_lock_digest": "sha256:" + "2" * 64,
        "locks": [{
            "name": "baseline",
            "candidate_lock_digest": "sha256:" + "2" * 64,
            "is_active": True,
            "matches_source_lock": True,
            "approval": {"cli_generated": False, "digest_matches": True},
        }],
        "problems": [],
        "notes": ["baseline.approval.yaml: CLI 이전에 수동으로 만든 승인 파일입니다."],
    })
    out = capsys.readouterr().out
    assert "[점검]" in out
    assert "수동 작성" in out
    assert "commit해 이력을 남기세요" in out


# ---- artifact kind consequence (P2) ----------------------------------------
def test_source_tree_lock_states_its_source_only_limit(tmp_path, capsys):
    fx = _fixture(tmp_path, artifact_kind="source-tree")
    assert _prepare(fx) == 0
    notice = _last_json(capsys)["artifact_kind_notice"]
    assert "source-only" in notice
    assert "build-artifact lock이 따로 필요" in notice
