"""T25-R vendor reconstruction planner and candidate gate tests."""
import subprocess
from pathlib import Path

import yaml

from acgh import registry as R
from acgh import vendor_rebuild as VR
from acgh import verdict as V

_REGISTRATION = (
    Path(__file__).parents[1] / "registrations" / "kb-openmetadata"
)


def _run(repo, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _write(repo, path, content):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _commit(repo, files, message):
    for path, content in files.items():
        _write(repo, path, content)
    _run(repo, "add", "-A")
    _run(repo, "commit", "-m", message)
    return _run(repo, "rev-parse", "HEAD")


def _source(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "upstream")
    _run(repo, "config", "user.email", "test@example.com")
    _run(repo, "config", "user.name", "test")
    _run(repo, "config", "commit.gpgsign", "false")

    target = _commit(
        repo,
        {
            "base.txt": "same\n",
            "shared.txt": "upstream\n",
            "blocked.txt": "safe\n",
        },
        "approved upstream",
    )

    _run(repo, "switch", "--orphan", "snapshot")
    snapshot = _commit(
        repo,
        {
            "base.txt": "same\n",
            "a.txt": "feature a\n",
            "b.txt": "feature b\n",
            "shared.txt": "feature a\nfeature b\n",
            "blocked.txt": "unsafe\n",
        },
        "unrelated source snapshot",
    )
    return repo, target, snapshot


def _registry(target, snapshot):
    entries = (
        R.RegistryEntry(
            customization_id="BANK-OM-001",
            title="A",
            owner="UNASSIGNED",
            owner_status="pending",
            status="active",
            criticality="high",
            manifest="a.yaml",
            contracts=("CONTRACT-A",),
        ),
        R.RegistryEntry(
            customization_id="BANK-OM-002",
            title="B",
            owner="UNASSIGNED",
            owner_status="pending",
            status="active",
            criticality="high",
            manifest="b.yaml",
            contracts=("CONTRACT-B",),
        ),
    )
    return R.Registry(
        source={
            "snapshot_sha": snapshot,
            "upstream_sha": target,
            "changed_path_count": 4,
            "unregistered_findings": [
                {
                    "path": "blocked.txt",
                    "classification": "governance",
                    "severity": "critical",
                    "reason": "unsafe",
                    "disposition": "block",
                }
            ],
        },
        entries=entries,
    )


def _manifests():
    return {
        "BANK-OM-001": {
            "implementation": {
                "allowed_changed_paths": ["a.txt", "shared.txt"]
            }
        },
        "BANK-OM-002": {
            "implementation": {
                "allowed_changed_paths": ["b.txt", "shared.txt"]
            }
        },
    }


def _plan(target, snapshot):
    return VR.build_reconstruction_plan(
        _registry(target, snapshot),
        _manifests(),
        ["a.txt", "b.txt", "shared.txt", "blocked.txt"],
    )


def _candidate(repo, target, *, include_blocked=False, final_shared=None):
    _run(repo, "switch", "-q", "-C", "candidate", target)
    first_files = {
        "a.txt": "feature a\n",
        "shared.txt": "feature a\n",
    }
    if include_blocked:
        first_files["blocked.txt"] = "unsafe\n"
    _commit(
        repo,
        first_files,
        "feature a\n\nCustomization-ID: BANK-OM-001",
    )
    _commit(
        repo,
        {
            "b.txt": "feature b\n",
            "shared.txt": (
                final_shared
                if final_shared is not None
                else "feature a\nfeature b\n"
            ),
        },
        "feature b\n\nCustomization-ID: BANK-OM-002",
    )
    return _run(repo, "rev-parse", "HEAD")


def test_plan_is_deterministic_and_separates_shared_and_excluded_paths(tmp_path):
    _, target, snapshot = _source(tmp_path)
    plan = _plan(target, snapshot)
    assert dict(plan.unique_assignments) == {
        "a.txt": "BANK-OM-001",
        "b.txt": "BANK-OM-002",
    }
    assert dict(plan.shared_candidates) == {
        "shared.txt": ("BANK-OM-001", "BANK-OM-002")
    }
    assert plan.excluded_paths == ("blocked.txt",)
    assert plan.digest() == _plan(target, snapshot).digest()


def test_v2_plan_uses_generated_source_owners_without_splitting_manifest_scope(
    tmp_path,
):
    _, target, snapshot = _source(tmp_path)
    manifests = {
        "BANK-OM-001": {
            "schema_version": 2,
            "implementation": {
                "changed_paths": ["a.txt", "shared.txt"],
                "required_changed_paths": ["a.txt"],
            },
        },
        "BANK-OM-002": {
            "schema_version": 2,
            "implementation": {
                "changed_paths": ["b.txt", "shared.txt"],
                "required_changed_paths": ["b.txt"],
            },
        },
    }
    plan = VR.build_reconstruction_plan(
        _registry(target, snapshot),
        manifests,
        ["a.txt", "b.txt", "shared.txt", "blocked.txt"],
        source_path_owners={
            "a.txt": ("BANK-OM-001",),
            "b.txt": ("BANK-OM-002",),
            "shared.txt": ("BANK-OM-001",),
        },
    )

    assert dict(plan.unique_assignments) == {
        "a.txt": "BANK-OM-001",
        "b.txt": "BANK-OM-002",
        "shared.txt": "BANK-OM-001",
    }
    assert plan.shared_candidates == ()


def test_load_source_snapshot_owners_reads_generated_mapping(tmp_path):
    _write(
        tmp_path,
        "source-snapshot-path-owners.yaml",
        "a.txt:\n- BANK-OM-001\nshared.txt:\n- BANK-OM-001\n- BANK-OM-002\n",
    )

    assert VR.load_source_snapshot_owners(tmp_path) == {
        "a.txt": ("BANK-OM-001",),
        "shared.txt": ("BANK-OM-001", "BANK-OM-002"),
    }


def test_load_source_snapshot_owners_rejects_empty_owner_list(tmp_path):
    _write(tmp_path, "source-snapshot-path-owners.yaml", "a.txt: []\n")

    try:
        VR.load_source_snapshot_owners(tmp_path)
    except VR.ReconstructionError as exc:
        assert "must be a non-empty list" in str(exc)
    else:
        raise AssertionError("empty source owner list must fail closed")


def test_source_inventory_matches_unrelated_pinned_trees(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    result = VR.inspect_source_inventory(str(repo), _plan(target, snapshot))
    assert result.verdict == V.PASS
    assert "source_path_count=4" in result.reasons


def test_stale_inventory_is_analysis_error(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    plan = _plan(target, snapshot)
    stale = VR.ReconstructionPlan(
        upstream_sha=plan.upstream_sha,
        snapshot_sha=plan.snapshot_sha,
        inventory_paths=("a.txt", "b.txt", "blocked.txt"),
        unique_assignments=plan.unique_assignments,
        shared_candidates=plan.shared_candidates,
        excluded_paths=plan.excluded_paths,
        active_ids=plan.active_ids,
    )
    result = VR.inspect_source_inventory(str(repo), stale)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "registered inventory is stale" in result.reasons


def test_missing_source_object_is_analysis_error(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    plan = _plan(target, snapshot)
    missing = VR.ReconstructionPlan(
        upstream_sha=plan.upstream_sha,
        snapshot_sha="0" * 40,
        inventory_paths=plan.inventory_paths,
        unique_assignments=plan.unique_assignments,
        shared_candidates=plan.shared_candidates,
        excluded_paths=plan.excluded_paths,
        active_ids=plan.active_ids,
    )
    result = VR.inspect_source_inventory(str(repo), missing)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "required source commit object missing" in result.reasons[0]


def test_reconstructed_candidate_passes_with_explicit_shared_owners(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    candidate = _candidate(repo, target)
    result = VR.check_reconstructed_candidate(
        str(repo),
        _plan(target, snapshot),
        _manifests(),
        candidate,
        shared_path_owners={
            "shared.txt": ["BANK-OM-001", "BANK-OM-002"]
        },
    )
    assert result.verdict == V.PASS
    assert any(reason == "registered_paths=3" for reason in result.reasons)
    assert any(reason == "excluded_paths=1" for reason in result.reasons)


def test_missing_shared_owner_resolution_blocks(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    candidate = _candidate(repo, target)
    result = VR.check_reconstructed_candidate(
        str(repo), _plan(target, snapshot), _manifests(), candidate
    )
    assert result.verdict == V.BLOCK
    assert "lacks hunk-level owner resolution" in result.reasons[0]


def test_malformed_shared_owner_map_is_analysis_error(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    candidate = _candidate(repo, target)
    result = VR.check_reconstructed_candidate(
        str(repo),
        _plan(target, snapshot),
        _manifests(),
        candidate,
        shared_path_owners={"shared.txt": "BANK-OM-001"},
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "must be a string list" in result.reasons[0]


def test_candidate_that_changes_excluded_path_blocks(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    candidate = _candidate(repo, target, include_blocked=True)
    result = VR.check_reconstructed_candidate(
        str(repo),
        _plan(target, snapshot),
        _manifests(),
        candidate,
        shared_path_owners={
            "shared.txt": ["BANK-OM-001", "BANK-OM-002"]
        },
    )
    assert result.verdict == V.BLOCK
    assert any("excluded path changed" in reason for reason in result.reasons)
    assert any(
        "excluded path differs from approved upstream" in reason
        for reason in result.reasons
    )


def test_candidate_content_must_equal_snapshot(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    candidate = _candidate(repo, target, final_shared="wrong\n")
    result = VR.check_reconstructed_candidate(
        str(repo),
        _plan(target, snapshot),
        _manifests(),
        candidate,
        shared_path_owners={
            "shared.txt": ["BANK-OM-001", "BANK-OM-002"]
        },
    )
    assert result.verdict == V.BLOCK
    assert any(
        "candidate content differs from source snapshot: shared.txt" == reason
        for reason in result.reasons
    )


def test_unrelated_snapshot_itself_cannot_masquerade_as_candidate(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    result = VR.check_reconstructed_candidate(
        str(repo),
        _plan(target, snapshot),
        _manifests(),
        snapshot,
        shared_path_owners={
            "shared.txt": ["BANK-OM-001", "BANK-OM-002"]
        },
    )
    assert result.verdict == V.BLOCK
    assert any("does not descend" in reason for reason in result.reasons)
    assert any("unrelated snapshot commit" in reason for reason in result.reasons)


def test_plan_rejects_uncovered_source_path(tmp_path):
    _, target, snapshot = _source(tmp_path)
    reg = _registry(target, snapshot)
    reg.source["changed_path_count"] = 5
    try:
        VR.build_reconstruction_plan(
            reg,
            _manifests(),
            ["a.txt", "b.txt", "shared.txt", "blocked.txt", "unknown.txt"],
        )
    except VR.ReconstructionError as exc:
        assert "neither registered nor explicitly excluded" in str(exc)
    else:
        raise AssertionError("uncovered source path must fail closed")


def test_plan_rejects_source_scope_globs(tmp_path):
    _, target, snapshot = _source(tmp_path)
    manifests = _manifests()
    manifests["BANK-OM-001"]["implementation"]["allowed_changed_paths"] = [
        "*.txt"
    ]
    try:
        VR.build_reconstruction_plan(
            _registry(target, snapshot),
            manifests,
            ["a.txt", "b.txt", "shared.txt", "blocked.txt"],
        )
    except VR.ReconstructionError as exc:
        assert "must be literal files" in str(exc)
    else:
        raise AssertionError("source snapshot globs must fail closed")


def test_plan_rejects_allowed_path_absent_from_source_inventory(tmp_path):
    _, target, snapshot = _source(tmp_path)
    manifests = _manifests()
    manifests["BANK-OM-001"]["implementation"]["allowed_changed_paths"].append(
        "not-in-source.txt"
    )
    try:
        VR.build_reconstruction_plan(
            _registry(target, snapshot),
            manifests,
            ["a.txt", "b.txt", "shared.txt", "blocked.txt"],
        )
    except VR.ReconstructionError as exc:
        assert "absent from the pinned source inventory" in str(exc)
    else:
        raise AssertionError("extra allowed source paths must fail closed")


def test_shared_owner_resolution_must_equal_manifest_owners(tmp_path):
    repo, target, snapshot = _source(tmp_path)
    candidate = _candidate(repo, target)
    result = VR.check_reconstructed_candidate(
        str(repo),
        _plan(target, snapshot),
        _manifests(),
        candidate,
        shared_path_owners={"shared.txt": ["BANK-OM-001"]},
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "extra_manifest_owners=['BANK-OM-002']" in result.reasons[0]


def test_real_shared_owner_template_tracks_every_ambiguous_path():
    reg, manifests, inventory = VR.load_registration_bundle(_REGISTRATION)
    plan = VR.build_reconstruction_plan(reg, manifests, inventory)
    template = yaml.safe_load(
        (_REGISTRATION / "shared-path-owners.yaml").read_text(encoding="utf-8")
    )
    assert set(template) == {path for path, _ in plan.shared_candidates}
    candidates = dict(plan.shared_candidates)
    assert all(template[path] for path in template)
    assert all(
        set(owners).issubset(candidates[path])
        for path, owners in template.items()
    )


def test_json_content_comparison_is_semantic(tmp_path):
    repo = tmp_path / "json-repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "main")
    _run(repo, "config", "user.email", "test@example.com")
    _run(repo, "config", "user.name", "test")
    _run(repo, "config", "commit.gpgsign", "false")
    compact = _commit(repo, {"config.json": '{"a":1,"b":[2,3]}\n'}, "compact")
    formatted = _commit(
        repo,
        {"config.json": '{\n  "a": 1,\n  "b": [2, 3]\n}\n'},
        "format only",
    )
    changed = _commit(
        repo,
        {"config.json": '{\n  "a": 9,\n  "b": [2, 3]\n}\n'},
        "semantic change",
    )
    assert VR._path_equal(str(repo), compact, formatted, "config.json")
    assert not VR._path_equal(str(repo), compact, changed, "config.json")


def test_real_source_candidate_evidence_closes_the_registered_series():
    evidence = yaml.safe_load(
        (_REGISTRATION / "source-candidate-evidence.yaml").read_text(
            encoding="utf-8"
        )
    )
    registry, manifests, inventory = VR.load_registration_bundle(_REGISTRATION)
    plan = VR.build_reconstruction_plan(registry, manifests, inventory)

    assert evidence["upstream"]["sha"] == plan.upstream_sha
    assert evidence["source_snapshot"]["sha"] == plan.snapshot_sha
    assert evidence["reconstruction"]["plan_digest"] == plan.digest()
    assert evidence["reconstruction"]["inventory_paths"] == len(
        plan.inventory_paths
    )
    assert evidence["reconstruction"]["registered_paths"] == (
        len(plan.inventory_paths) - len(plan.excluded_paths)
    )
    assert set(evidence["reconstruction"]["excluded_paths"]) == set(
        plan.excluded_paths
    )
    commits = evidence["reconstruction"]["commits"]
    assert [item["customization_id"] for item in commits] == list(
        plan.active_ids
    )
    assert len({item["sha"] for item in commits}) == len(plan.active_ids)
    assert all(item["touched_paths"] > 0 for item in commits)
    assert evidence["reconstruction"]["checkpoint_sha"] == commits[-1]["sha"]
    follow_ups = evidence["reconstruction"]["follow_up_commits"]
    assert follow_ups
    assert evidence["candidate"]["commit_sha"] == follow_ups[-1]["sha"]
    assert all(
        item["customization_id"] in registry.active_ids()
        and item["touched_paths"] > 0
        for item in follow_ups
    )
    candidate_only = {
        entry.customization_id
        for entry in registry.entries
        if entry.provenance == "candidate-follow-up"
    }
    assert {
        item["customization_id"]
        for item in follow_ups
        if item["customization_id"] not in plan.active_ids
    } == candidate_only
    gates = evidence["gates"]
    assert (
        gates["t25_r_vendor_reconstructed_candidate"]["candidate"]
        == evidence["reconstruction"]["checkpoint_sha"]
    )
    assert all(
        gate["candidate"] == evidence["candidate"]["commit_sha"]
        for name, gate in gates.items()
        if name
        not in {
            "t25_r_vendor_reconstructed_candidate",
            "t60_i_required_test_implementations",
            "t61_source_patch_kill",
        }
    )
    assert (
        gates["t60_i_required_test_implementations"][
            "implemented_required_tests"
        ]
        == 9
    )
    patch_kill = gates["t61_source_patch_kill"]
    assert patch_kill["verdict"] == V.PASS
    assert patch_kill["scope"] == "source-capable-high-critical"
    assert patch_kill["proven"] == ["BANK-OM-006", "BANK-OM-007"]
    assert patch_kill["pending_runtime"] == [
        "BANK-OM-001",
        "BANK-OM-002",
        "BANK-OM-003",
    ]
    assert all(
        gate["verdict"] == V.PASS
        for gate in gates.values()
    )
    product = evidence["product_verification"]
    assert product["source_candidate_ci"]["action_refs_pinned"] is True
    assert product["source_candidate_ci"]["candidate_sha_locked"] is True
    assert (
        product["source_candidate_ci"]["local_simulation"]["tests_passed"]
        == 316
    )
    assert (
        product["source_candidate_ci"]["local_simulation"][
            "tests_skipped_operational"
        ]
        == 7
    )
    assert (
        product["source_candidate_ci"]["prior_remote_run"]["conclusion"]
        == "success"
    )
    remote = product["source_candidate_ci"]["remote_run"]
    assert remote["conclusion"] == "success"
    assert remote["annotations"] == 0
    assert remote["head_sha"] == "7063b0b23e1816c1480e88d6d6c29d5cc539ae1f"
    runtime_handoff = product["source_candidate_ci"][
        "runtime_handoff_remote_run"
    ]
    assert runtime_handoff["conclusion"] == "success"
    assert (
        runtime_handoff["head_sha"]
        == "45d0994dd3d7e2adcc25592575a2786a4f2132bc"
    )
    assert runtime_handoff["tests_passed"] == 293
    assert runtime_handoff["tests_skipped_operational"] == 5
    assert runtime_handoff["source_gates_passed"] == 5
    source_patch_kill = product["source_candidate_ci"][
        "source_patch_kill_remote_run"
    ]
    assert source_patch_kill["conclusion"] == "success"
    assert (
        source_patch_kill["head_sha"]
        == "17b74279cb48ce282c2c7507c79fbaeff31b5740"
    )
    assert source_patch_kill["tests_passed"] == 297
    assert source_patch_kill["source_patch_kill_experiments_passed"] == 2
    assert (
        source_patch_kill["evidence_artifact"]["digest"]
        == "sha256:"
        "d5afd822d8898e5ed94611f5220caa25ba152a211169f3c990ec73f8a7bfa32f"
    )
    node24_validation = product["source_candidate_ci"][
        "node24_artifact_validation_remote_run"
    ]
    assert node24_validation["conclusion"] == "success"
    assert node24_validation["annotations"] == 0
    assert node24_validation["tests_passed"] == 297
    assert node24_validation["source_patch_kill_experiments_passed"] == 2
    assert (
        node24_validation["evidence_artifact"]["digest"]
        == "sha256:"
        "bb8b97516ea4b39ba5e14a866327ad18785f3b25ee4aeb02b6da3a2cb12cf109"
    )
    hardening = product["source_candidate_ci"][
        "candidate_hardening_remote_run"
    ]
    assert hardening["conclusion"] == "success"
    assert hardening["head_sha"] == (
        "9e95fd06015f97e3ce1b5129a5eb2c0d70b7eab3"
    )
    assert hardening["tests_passed"] == 306
    assert hardening["tests_skipped_operational"] == 7
    assert hardening["source_gates_passed"] == 5
    assert hardening["source_patch_kill_experiments_passed"] == 2
    assert hardening["evidence_artifact"]["digest"] == (
        "sha256:"
        "bbb2bddfeb184442f1ada105dd5a89d1c9dfc5fd734fc1aa39c730fd5ca40a27"
    )
    assert product["prettier"]["verdict"] == V.PASS
    assert product["tibero_jest"]["verdict"] == V.PASS
    assert product["tibero_jest"]["tests"] > 0
    assert product["bank_contract_suite"]["implemented"] == 7
    assert product["bank_contract_suite"]["required_selectors"] == 9
    assert product["bank_contract_suite"]["source_suite_passed"] == 3
    assert product["bank_contract_suite"]["required_contracts_passed"] == 2
    assert product["bank_contract_suite"]["skipped_operational"] == 7
    runtime = product["runtime_contract_gate"]
    assert runtime["junit_exit_reconciled"] is True
    assert runtime["local_no_runtime_simulation"]["verdict"] == V.BLOCK
    assert (
        runtime["local_no_runtime_simulation"]["false_exit_verdict"]
        == V.ANALYSIS_ERROR
    )
    retention = runtime["evidence_retention"]
    assert (
        retention["action_commit"]
        == "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"
    )
    assert retention["action_runtime"] == "node24"
    assert retention["retention_days"] == 90
    assert retention["overwrite"] is False
    assert retention["missing_files"] == "error"
    assert retention["reports_artifact_id_digest_url"] is True
    assert runtime["operational_run_executed"] is False
    runtime_patch_kill = product["runtime_patch_kill_gate"]
    assert runtime_patch_kill["operational_runs_executed"] == 0
    assert runtime_patch_kill["target_repeats"] == 2
    assert set(runtime_patch_kill["source_pending_partition_closed"]) == {
        "BANK-OM-001",
        "BANK-OM-002",
        "BANK-OM-003",
    }
    assert set(
        runtime_patch_kill["local_no_runtime_validation"].values()
    ) == {V.ANALYSIS_ERROR}
    assert product["ui_typecheck"]["verdict"] == "fail"
    assert product["ui_typecheck"]["error_lines_before_candidate_fix"] == 399
    assert product["ui_typecheck"]["error_lines_after_candidate_fix"] == 396
    assert (
        product["ui_typecheck"]["error_lines_after_search_type_hardening"]
        == 357
    )
    assert product["ui_typecheck"]["error_lines_after_alert_id_hardening"] == 356
    assert (
        product["ui_typecheck"]["error_lines_after_listing_transform_contract"]
        == 355
    )
    assert (
        product["ui_typecheck"]["candidate_introduced_error_lines_after_fix"]
        == 0
    )
    assert (
        product["ui_typecheck"]["remaining_error_lines_in_candidate_changed_files"]
        == 12
    )
    assert (
        product["ui_typecheck"][
            "remaining_changed_file_errors_match_upstream_source"
        ]
        is True
    )
