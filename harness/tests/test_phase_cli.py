"""End-to-end coverage for the public Phase workflow commands."""
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
from acgh import phase
from harness import om_workflow
from harness import run_phase_bundle


def _git(repo, *args, env=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


def _fixture(tmp_path):
    repo = tmp_path / "product"
    repo.mkdir()
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    _git(repo, "init", "-q")
    (repo / "svc").mkdir()
    (repo / "svc/a.java").write_text("class A {}\n", encoding="utf-8")
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-qm", "official 1.0", env=env)
    base = _git(repo, "rev-parse", "HEAD")

    _git(repo, "switch", "-qc", "custom-baseline")
    (repo / "svc/a.java").write_text("class A { int bank; }\n", encoding="utf-8")
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-qm", "bank\n\nCustomization-ID: BANK-OM-001", env=env)
    baseline = _git(repo, "rev-parse", "HEAD")

    _git(repo, "switch", "-q", "--detach", base)
    (repo / "svc/a.java").write_text("class A { int upstream; }\n", encoding="utf-8")
    _git(repo, "add", "-A", env=env)
    _git(repo, "commit", "-qm", "official 1.1", env=env)
    target = _git(repo, "rev-parse", "HEAD")

    registration = tmp_path / "registration"
    (registration / "manifests").mkdir(parents=True)
    (registration / "candidate-locks").mkdir()
    (registration / "repository-layout.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "upstream_base_sha": base,
        "path_grammar": {"negation_allowed": False},
        "upstream_owned_roots": ["svc/**"],
        "bank_governance_roots": [".bank/**"],
        "platform_extension_roots": ["extensions/**"],
        "unknown_path_policy": "analysis_error",
    }), encoding="utf-8")
    (registration / "sensitive-zones.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "zones": {}}), encoding="utf-8"
    )
    (registration / "manifests/BANK-OM-001.yaml").write_text(yaml.safe_dump({
        "schema_version": 2,
        "customization_id": "BANK-OM-001",
        "status": "active",
        "kind": "core-patch",
        "title": "synthetic",
        "implementation": {
            "changed_paths": ["svc/a.java"],
            "required_changed_paths": ["svc/a.java"],
        },
        "upgrade_watch": {"paths": ["svc/a.java"]},
        "assurance": {"contracts": [], "direct_tests": []},
        "series": {"allowed": False, "depends_on": []},
    }), encoding="utf-8")

    lock = candidate.build_candidate_lock(
        str(repo), baseline,
        upstream_repository="vendor/product",
        upstream_base_sha=base,
        upstream_target_sha=base,
        candidate_repository="bank/product",
        artifact_digest="sha256:" + "0" * 64,
        artifact_kind="source-tree",
    )
    lock_path = registration / "candidate-locks/baseline.yaml"
    lock_path.write_text(yaml.safe_dump(lock.canonical()), encoding="utf-8")
    digest = lock.digest()
    (registration / "candidate-locks/baseline.approval.yaml").write_text(
        yaml.safe_dump({
            "candidate_lock_digest": digest,
            "approver": "데이터플랫폼 승인자",
            "approved_at": "2026-08-08T00:00:00Z",
            "rationale": "합성 기준선 승인",
        }), encoding="utf-8"
    )
    (registration / "candidate-locks/active-candidate.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "candidate_lock_digest": digest}),
        encoding="utf-8",
    )
    return repo, registration, base, target


def _official_evidence(tmp_path, repo, target):
    _git(repo, "tag", "official-release", target)
    output = tmp_path / "official.json"
    assert run_phase_bundle.main([
        "prep-official",
        "--repo", str(repo),
        "--tag-ref", "official-release",
        "--branch", "official/next",
        "--output", str(output),
    ]) == 0
    return output


def test_premerge_cli_writes_verified_phase_artifact(tmp_path):
    repo, registration, base, target = _fixture(tmp_path)
    official = _official_evidence(tmp_path, repo, target)
    output = tmp_path / "evidence/result.json"
    code = run_phase_bundle.main([
        "premerge",
        "--repo", str(repo),
        "--registration", str(registration),
        "--base", base,
        "--target", target,
        "--official-evidence", str(official),
        "--run-id", "premerge-e2e",
        "--output", str(output),
    ])
    assert code == 2  # watched official change requires human approval
    assert output.is_file()
    assert phase.verify_phase_result(output) == (True, "consistent")
    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert artifact["canonical_payload"]["phase"] == phase.PREMERGE
    assert artifact["canonical_payload"]["overall_verdict"] == "approval"
    assert artifact["canonical_payload"]["inputs"]["harness_version"].startswith("sha256:")
    assert artifact["canonical_payload"]["inputs"]["verifier_catalog_digest"].startswith("sha256:")
    assert (output.parent / "manager-summary.json").is_file()
    assert (output.parent / "practitioner-detail.json").is_file()


def test_om_workflow_exposes_all_phase_commands(monkeypatch):
    commands = {
        "prep-official": [
            "--repo", "/work/product", "--tag-ref", "1.13.2-release",
            "--branch", "official/om-1.13.2",
        ],
        "candidate-select": ["--version", "1.13.1"],
        "phase-preflight": [
            "--repo", "/work/product", "--version", "1.13.1", "--phase", "premerge",
        ],
        "premerge-check": [
            "--repo", "/work/product", "--version", "1.13.1",
            "--base", "base", "--target", "target",
            "--official-evidence", "/work/official.json",
        ],
        "postmerge-check": ["--repo", "/work/product", "--version", "1.13.1"],
        "phase-status": ["--result", "/work/result.json"],
    }
    for command, arguments in commands.items():
        monkeypatch.setattr(sys, "argv", ["om_workflow.py", command, *arguments])
        assert om_workflow.parse_args().command == command


def test_postmerge_cli_rejects_target_that_contradicts_candidate_lock(tmp_path):
    repo, registration, _base, target = _fixture(tmp_path)
    output = tmp_path / "must-not-exist.json"
    code = run_phase_bundle.main([
        "postmerge",
        "--repo", str(repo),
        "--registration", str(registration),
        "--target", target,
        "--debt-policy", str(tmp_path / "policy.yaml"),
        "--run-id", "bad-target",
        "--output", str(output),
    ])
    assert code == 3
    assert not output.exists()


def test_prep_official_cli_creates_branch_at_tag_commit(tmp_path):
    repo, _registration, base, _target = _fixture(tmp_path)
    _git(repo, "tag", "official-release", base)
    output = tmp_path / "official.json"
    code = run_phase_bundle.main([
        "prep-official",
        "--repo", str(repo),
        "--tag-ref", "official-release",
        "--branch", "official/next",
        "--output", str(output),
    ])
    assert code == 0
    assert _git(repo, "rev-parse", "official/next") == base
    assert json.loads(output.read_text(encoding="utf-8"))["commit_sha"] == base


def test_existing_runner_adapter_preserves_approval_and_evidence(tmp_path):
    runner = tmp_path / "runner.py"
    runner.write_text(
        "import json\n"
        "print(json.dumps({'gates':[{'name':'inner','verdict':'approval',"
        "'reasons':['owner review']}]}))\n"
        "raise SystemExit(2)\n",
        encoding="utf-8",
    )
    output = tmp_path / "source.json"
    spec = run_phase_bundle._command_gate(
        "source", [sys.executable, str(runner)], output, "gates"
    )
    execution = phase.execute_gate(spec)
    assert execution.execution_status == phase.EXECUTED
    assert execution.verdict == "approval"
    assert execution.evidence == ("source.json",)
    assert output.is_file()


def test_premerge_preflight_block_still_writes_incomplete_evidence(tmp_path):
    repo, registration, base, target = _fixture(tmp_path)
    official = _official_evidence(tmp_path, repo, target)
    (registration / "repository-layout.yaml").unlink()
    output = tmp_path / "blocked/result.json"
    code = run_phase_bundle.main([
        "premerge",
        "--repo", str(repo),
        "--registration", str(registration),
        "--base", base,
        "--target", target,
        "--official-evidence", str(official),
        "--run-id", "blocked-preflight",
        "--output", str(output),
    ])
    assert code == 3
    assert output.is_file()
    artifact = json.loads(output.read_text(encoding="utf-8"))
    assert artifact["canonical_payload"]["phase_status"] == "incomplete"
    assert artifact["system_json"]["observational_metadata"]["preflight"]["ready"] is False


def test_premerge_rejects_target_not_bound_to_official_evidence(tmp_path):
    repo, registration, base, target = _fixture(tmp_path)
    official = _official_evidence(tmp_path, repo, target)
    data = json.loads(official.read_text(encoding="utf-8"))
    data["commit_sha"] = base
    official.write_text(json.dumps(data), encoding="utf-8")
    code = run_phase_bundle.main([
        "premerge", "--repo", str(repo), "--registration", str(registration),
        "--base", base, "--target", target,
        "--official-evidence", str(official),
        "--run-id", "wrong-official", "--output", str(tmp_path / "result.json"),
    ])
    assert code == 3


def test_source_tree_lock_rejects_runtime_artifact_digest(tmp_path):
    repo, registration, _base, _target = _fixture(tmp_path)
    output = tmp_path / "result.json"
    code = run_phase_bundle.main([
        "postmerge", "--repo", str(repo), "--registration", str(registration),
        "--debt-policy", str(Path(__file__).parents[1] / "policies/debt-thresholds.yaml"),
        "--artifact-digest", "sha256:" + "0" * 64,
        "--run-id", "source-with-runtime", "--output", str(output),
    ])
    assert code == 3
    assert not output.exists()


def test_conflict_evidence_is_candidate_bound_and_rate_is_derived(tmp_path):
    repo, registration, base, _target = _fixture(tmp_path)
    selection = run_phase_bundle._selected(registration)
    evidence = tmp_path / "conflicts.yaml"
    evidence.write_text(yaml.safe_dump({
        "upstream_base_sha": base,
        "upstream_target_sha": base,
        "candidate_sha": selection.lock.candidate.commit_sha,
        "merge_changed_paths": ["svc/a.java", "svc/b.java"],
        "conflicted_paths": ["svc/a.java"],
        "conflict_rate": 0.5,
    }), encoding="utf-8")
    args = SimpleNamespace(conflict_evidence=evidence, conflict_rate=None)
    digest = run_phase_bundle._bind_conflict_evidence(args, selection.lock)
    assert args.conflict_rate == 0.5
    assert digest.startswith("sha256:")


def test_registration_digest_changes_when_manifest_changes(tmp_path):
    _repo, registration, _base, _target = _fixture(tmp_path)
    before = run_phase_bundle._registration_digests(registration)
    manifest = registration / "manifests/BANK-OM-001.yaml"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    after = run_phase_bundle._registration_digests(registration)
    assert before != after


def test_status_rejects_tampered_manager_summary(tmp_path):
    repo, registration, base, target = _fixture(tmp_path)
    official = _official_evidence(tmp_path, repo, target)
    output = tmp_path / "evidence/result.json"
    assert run_phase_bundle.main([
        "premerge", "--repo", str(repo), "--registration", str(registration),
        "--base", base, "--target", target,
        "--official-evidence", str(official),
        "--run-id", "tamper-tier", "--output", str(output),
    ]) == 2
    manager = output.with_name("manager-summary.json")
    data = json.loads(manager.read_text(encoding="utf-8"))
    data["overall_verdict"] = "pass"
    manager.write_text(json.dumps(data), encoding="utf-8")
    assert run_phase_bundle.main(["status", "--result", str(output)]) == 3


def test_human_phase_summary_states_next_action(capsys):
    om_workflow._print_human_phase("postmerge", {
        "overall_verdict": "approval",
        "phase_status": "complete",
        "verification_scope": "source-only",
        "checked_over_total": "5/6",
        "counts": {"pass": 5, "approval": 1, "block": 0, "analysis_error": 0},
        "non_pass_gates": [{
            "name": "approval",
            "verdict": "approval",
            "execution_status": "executed",
        }],
        "result_digest": "sha256:" + "1" * 64,
        "manager_output": "manager-summary.json",
        "practitioner_output": "practitioner-detail.json",
    })
    text = capsys.readouterr().out
    assert "[5/6]" in text
    assert "담당자 검토 필요" in text
    assert "source-only" in text
    assert "5/6" in text
    assert "approval(approval)" in text
    assert "다음 행동" in text


def test_human_preflight_summary_lists_only_actionable_checks(capsys):
    om_workflow._print_human_phase("preflight", {
        "ready": False,
        "blocking_problems": ["official evidence missing"],
        "disabled_gates": ["approval"],
        "checks": [
            {"name": "candidate", "status": "ok"},
            {
                "name": "official-evidence",
                "status": "blocked",
                "next_action": "prep-official을 먼저 실행하세요.",
            },
        ],
    })
    text = capsys.readouterr().out
    assert "candidate: ok" not in text
    assert "official-evidence: blocked" in text
    assert "prep-official을 먼저 실행" in text


def test_safe_phase_output_rejects_public_cli_path_traversal():
    with pytest.raises(om_workflow.WorkflowInputError):
        om_workflow.safe_phase_output("../escape")


def test_candidate_failure_summary_gives_recovery_action(capsys):
    om_workflow._print_human_phase("candidate", {
        "status": "analysis_error",
        "reasons": ["active-candidate.yaml missing"],
        "process_exit_code": 3,
    })
    text = capsys.readouterr().out
    assert "중단" in text
    assert "active-candidate.yaml" in text
    assert "승인된 Candidate lock" in text


def test_failed_human_phase_does_not_claim_missing_evidence_exists(tmp_path, capsys):
    evidence = tmp_path / "not-created.json"
    om_workflow._print_human_phase(
        "candidate",
        {"status": "analysis_error", "reasons": ["missing"]},
        evidence=evidence,
    )
    text = capsys.readouterr().out
    assert "중단되어 생성되지 않음" in text
    assert f"증거 파일   : {evidence}" not in text
