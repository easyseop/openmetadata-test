"""Security-boundary tests for the protected /om-plan CI wiring."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from acgh.plancore.schema import read_data
from acgh.integrations.om import OpenMetadataPlanAdapter
from acgh.plancore.markers import create_session_marker
from acgh.plancore.preflight import run_preflight
from ci import om_plan_ci as CI


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "om-plan-ci.yml"
DIGEST = "sha256:" + "a" * 64


def _git(repo: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _product_repo(path: Path) -> tuple[Path, str, str]:
    path.mkdir()
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    (path / "base.txt").write_text("base\n", encoding="utf-8")
    _git(path, "add", "base.txt")
    _git(path, "commit", "-q", "-m", "base")
    official = _git(path, "rev-parse", "HEAD")
    (path / "custom.txt").write_text("custom\n", encoding="utf-8")
    _git(path, "add", "custom.txt")
    _git(
        path,
        "commit",
        "-q",
        "-m",
        "custom",
        "-m",
        "Customization-ID: BANK-OM-001",
    )
    custom = _git(path, "rev-parse", "HEAD")
    return path, official, custom


def _workflow() -> dict:
    return yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_ci_workflow_keeps_expected_digest_out_of_untrusted_proposal_job():
    workflow = _workflow()
    assert workflow["permissions"] == {"actions": "none", "contents": "read"}
    assert set(workflow["jobs"]) == {
        "preflight",
        "intent-review",
        "untrusted-proposal",
        "validate",
    }

    preflight = workflow["jobs"]["preflight"]
    proposal = workflow["jobs"]["untrusted-proposal"]
    validate = workflow["jobs"]["validate"]
    review = workflow["jobs"]["intent-review"]

    assert preflight["outputs"]["input_lock_digest"] == (
        "${{ steps.capture.outputs.input_lock_digest }}"
    )
    assert review["needs"] == "preflight"
    assert review["environment"] == {
        "deployment": "false",
        "name": "om-plan-intent-review",
    }
    assert proposal["needs"] == "intent-review"
    assert "preflight" not in json.dumps(proposal, sort_keys=True)
    assert "input_lock_digest" not in json.dumps(proposal, sort_keys=True)
    assert proposal["permissions"] == {"actions": "none", "contents": "read"}

    assert set(validate["needs"]) == {
        "preflight",
        "intent-review",
        "untrusted-proposal",
    }
    validate_text = json.dumps(validate, sort_keys=True)
    assert "needs.preflight.outputs.input_lock_digest" in validate_text
    assert "validation-result.json" not in validate_text
    assert "om_plan_ci.py validate" in validate_text
    assert validate["permissions"] == {"actions": "read", "contents": "read"}


def test_ci_workflow_uses_default_branch_and_pinned_actions_only():
    workflow = _workflow()
    expected_guard = (
        "github.ref == format('refs/heads/{0}', "
        "github.event.repository.default_branch)"
    )
    for job in workflow["jobs"].values():
        assert expected_guard in job["if"]

    action_uses = []
    for job in workflow["jobs"].values():
        action_uses.extend(
            step["uses"] for step in job.get("steps", []) if "uses" in step
        )
    assert action_uses
    assert all(
        len(value.rsplit("@", 1)[1]) == 40
        and all(character in "0123456789abcdef" for character in value.rsplit("@", 1)[1])
        for value in action_uses
    )


def test_prepare_request_rebinds_only_ci_paths(tmp_path: Path):
    request_root = tmp_path / "request-source"
    checker = tmp_path / "checker"
    product = tmp_path / "product"
    request_root.mkdir()
    checker.mkdir()
    product.mkdir()
    (request_root / "release.html").write_text("release", encoding="utf-8")
    source = request_root / "request.yaml"
    source.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "run_id": "upgrade-ci-01",
                "mode": "upgrade",
                "repositories": {"product": "/old/product", "checker": "/old/checker"},
                "refs": {
                    "official_base": "1" * 40,
                    "official_target": "2" * 40,
                    "custom_baseline": "3" * 40,
                },
                "versions": {"base": "1.0.0", "target": "1.0.1"},
                "hop_policy": "adjacent_only",
                "deployment_method": "container",
                "registration_path": "harness/registrations/example",
                "official_documents": [
                    {"source": "release.html", "version_token": "1.0.1"}
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    output = tmp_path / "prepared.yaml"

    CI.prepare_request(source, output, product, checker)

    prepared = read_data(output)
    assert prepared["repositories"] == {
        "product": str(product.resolve()),
        "checker": str(checker.resolve()),
    }
    assert prepared["registration_path"] == str(
        (checker / "harness/registrations/example").resolve()
    )
    assert prepared["official_documents"][0]["source"] == str(
        (request_root / "release.html").resolve()
    )


def test_package_proposal_accepts_data_only_and_rejects_symlink(tmp_path: Path):
    source = tmp_path / "source"
    output = tmp_path / "output"
    source.mkdir()
    (source / "plan.yaml").write_text("findings: []\n", encoding="utf-8")
    CI.package_proposal(source, output)
    assert (output / "plan.yaml").read_text(encoding="utf-8") == "findings: []\n"

    linked = tmp_path / "linked"
    linked.mkdir()
    (tmp_path / "outside.yaml").write_text("note: outside\n", encoding="utf-8")
    (linked / "escape.yaml").symlink_to(tmp_path / "outside.yaml")
    with pytest.raises(CI.PlanCIError, match="symlink"):
        CI.package_proposal(linked, tmp_path / "rejected")


def test_package_proposal_allows_only_an_existing_empty_output(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "plan.yaml").write_text("findings: []\n", encoding="utf-8")
    empty = tmp_path / "empty"
    empty.mkdir()
    CI.package_proposal(source, empty)
    assert (empty / "plan.yaml").is_file()

    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "old.yaml").write_text("old: true\n", encoding="utf-8")
    with pytest.raises(CI.PlanCIError, match="not empty"):
        CI.package_proposal(source, occupied)


def test_capture_preflight_writes_ci_output_and_human_summary(tmp_path: Path):
    source = tmp_path / "preflight.json"
    output = tmp_path / "github-output"
    summary = tmp_path / "summary"
    receipt = tmp_path / "receipt"
    source.write_text(
        json.dumps(
            {
                "status": "ready_for_proposal",
                "input_lock_digest": DIGEST,
                "intent_review_required": True,
                "intent_summary": {
                    "mode": "upgrade",
                    "refs": {
                        "official_target": {
                            "requested": "target",
                            "pinned_commit_sha": "1" * 40,
                        }
                    },
                },
                "operator_action": "review and retain digest",
            }
        ),
        encoding="utf-8",
    )

    CI.capture_preflight(source, output, summary, receipt)

    assert output.read_text(encoding="utf-8") == f"input_lock_digest={DIGEST}\n"
    assert receipt.read_text(encoding="utf-8") == f"{DIGEST}\n"
    summary_text = summary.read_text(encoding="utf-8")
    assert "official_target" in summary_text
    assert "사람이 확인" in summary_text


def test_restore_run_rebinds_relocated_trusted_artifact(tmp_path: Path):
    run_dir = tmp_path / "relocated-run"
    run_dir.mkdir()
    (run_dir / ".plan-active").write_text("old marker", encoding="utf-8")
    state_root = tmp_path / "state"
    project_root = tmp_path / "checker"
    project_root.mkdir()

    pair = CI.restore_run(run_dir, state_root, project_root, "ci-validate-1")

    assert pair.run_marker == run_dir / ".plan-active"
    assert pair.run_marker.is_file()
    assert pair.session_marker.is_file()


def test_rebind_run_request_changes_only_excluded_runtime_paths(tmp_path: Path):
    old_checker = tmp_path / "old-checker"
    run_dir = tmp_path / "run"
    new_checker = tmp_path / "new-checker"
    new_product = tmp_path / "new-product"
    run_dir.mkdir()
    new_checker.mkdir()
    new_product.mkdir()
    request = {
        "schema_version": 1,
        "run_id": "upgrade-01",
        "mode": "upgrade",
        "repositories": {
            "product": str(tmp_path / "old-product"),
            "checker": str(old_checker),
        },
        "registration_path": str(old_checker / "harness/registrations/example"),
        "refs": {
            "official_base": "1" * 40,
            "official_target": "2" * 40,
            "custom_baseline": "3" * 40,
        },
        "official_documents": [
            {"source": "/old/request/release.html", "version_token": "1.0.1"}
        ],
    }
    (run_dir / "run-request.yaml").write_text(
        yaml.safe_dump(request, sort_keys=False), encoding="utf-8"
    )

    rebound = CI.rebind_run_request(run_dir, new_product, new_checker)

    assert rebound["repositories"] == {
        "product": str(new_product.resolve()),
        "checker": str(new_checker.resolve()),
    }
    assert rebound["registration_path"] == str(
        (new_checker / "harness/registrations/example").resolve()
    )
    assert rebound["refs"] == request["refs"]
    assert rebound["official_documents"] == request["official_documents"]


@pytest.mark.parametrize(
    ("verdict", "review_state", "exit_code"),
    [
        ("pass", "not_ready", 0),
        ("block", "not_ready", 1),
        ("approval", "review_ready", 2),
        ("analysis_error", "not_ready", 3),
    ],
)
def test_fresh_validate_returns_exact_cli_exit_and_records_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    verdict: str,
    review_state: str,
    exit_code: int,
):
    checker = tmp_path / "checker"
    run_dir = tmp_path / "run"
    checker.mkdir()
    run_dir.mkdir()
    captured = tmp_path / "fresh.json"
    summary = tmp_path / "summary"
    result = {"verdict": verdict, "review_state": review_state}

    def fake_run(command, **kwargs):
        assert "plan-validate" in command
        assert command[-1] == DIGEST
        assert kwargs["cwd"] == checker.resolve()
        return subprocess.CompletedProcess(
            command,
            exit_code,
            stdout=json.dumps(result),
            stderr="",
        )

    monkeypatch.setattr(CI.subprocess, "run", fake_run)
    actual = CI.run_fresh_validation(checker, run_dir, DIGEST, captured, summary)

    assert actual == exit_code
    assert json.loads(captured.read_text(encoding="utf-8")) == result
    assert verdict in summary.read_text(encoding="utf-8")


def test_fresh_validate_fails_closed_on_exit_result_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    checker = tmp_path / "checker"
    run_dir = tmp_path / "run"
    checker.mkdir()
    run_dir.mkdir()

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"verdict": "approval", "review_state": "review_ready"}),
            stderr="",
        )

    monkeypatch.setattr(CI.subprocess, "run", fake_run)
    with pytest.raises(CI.PlanCIError, match="exit code"):
        CI.run_fresh_validation(
            checker,
            run_dir,
            DIGEST,
            tmp_path / "fresh.json",
            tmp_path / "summary",
        )


def test_ci_wrapper_never_consumes_stored_validation_result():
    source = (ROOT / "harness" / "ci" / "om_plan_ci.py").read_text(
        encoding="utf-8"
    )
    assert "validation-result.json" not in source


def test_workflow_does_not_dirty_checker_with_editable_install():
    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    assert 'pip install --disable-pip-version-check -e "checker/harness' not in workflow_text
    assert "--no-checkout" not in workflow_text
    assert "rebind-run-request" in workflow_text

    workflow = _workflow()
    for job_name in ("preflight", "untrusted-proposal", "validate"):
        assert workflow["jobs"][job_name]["env"]["PYTHONPATH"] == (
            "${{ github.workspace }}/checker/harness"
        )


def test_cross_runner_fresh_validation_uses_ci_digest_and_recomputed_sources(
    tmp_path: Path,
):
    product, official, custom = _product_repo(tmp_path / "product-a")
    checker = tmp_path / "checker-a"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(checker)],
        check=True,
    )
    request = tmp_path / "request.yaml"
    request.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "run_id": "ci-integration-01",
                "mode": "initial",
                "repositories": {
                    "product": str(product),
                    "checker": str(checker),
                },
                "repository_ids": {
                    "product": "product-repo",
                    "checker": "checker-repo",
                },
                "refs": {"official": official, "current_custom": custom},
                "product_version": "1.0.0",
                "owner": "data-team",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    original_run = tmp_path / "original-run"
    marker = create_session_marker(tmp_path / "state-a", checker, "preflight")
    preflight = run_preflight(
        request,
        original_run,
        OpenMetadataPlanAdapter(),
        session_marker=marker,
    )
    relocated = tmp_path / "relocated-run"
    shutil.copytree(original_run, relocated)

    facts = read_data(original_run / "discovered-facts.json")
    item = facts["canonical_payload"]["items"][0]
    proposal_source = tmp_path / "proposal-source"
    proposal_source.mkdir()
    (proposal_source / "plan.yaml").write_text(
        yaml.safe_dump(
            {
                "decisions": [
                    {
                        "subject": "retain customization",
                        "decision": "keep",
                        "decision_source": "proposed",
                        "evidence_refs": [
                            {
                                "ref": item["evidence_ref"],
                                "expected": item["value"],
                            }
                        ],
                        "affected_customization_ids": ["BANK-OM-001"],
                        "required_follow_up": "human review",
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    CI.package_proposal(proposal_source, relocated / "proposal")

    product_b = tmp_path / "product-b"
    checker_b = tmp_path / "checker-b"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(product), str(product_b)],
        check=True,
    )
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(checker), str(checker_b)],
        check=True,
    )
    CI.rebind_run_request(relocated, product_b, checker_b)
    CI.restore_run(
        relocated,
        tmp_path / "state-b",
        checker_b,
        "ci-validate",
    )

    exit_code = CI.run_fresh_validation(
        checker_b,
        relocated,
        preflight["input_lock_digest"],
        tmp_path / "fresh.json",
        tmp_path / "summary",
    )

    assert exit_code == 2
    assert json.loads((tmp_path / "fresh.json").read_text(encoding="utf-8"))[
        "review_state"
    ] == "review_ready"
