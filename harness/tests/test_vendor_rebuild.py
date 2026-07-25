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
        item["customization_id"] in plan.active_ids
        and item["touched_paths"] > 0
        for item in follow_ups
    )
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
        }
    )
    assert (
        gates["t60_i_required_test_implementations"][
            "implemented_required_tests"
        ]
        == 7
    )
    assert all(
        gate["verdict"] == V.PASS
        for gate in gates.values()
    )
    product = evidence["product_verification"]
    assert product["source_candidate_ci"]["action_refs_pinned"] is True
    assert product["source_candidate_ci"]["candidate_sha_locked"] is True
    assert (
        product["source_candidate_ci"]["local_simulation"]["tests_passed"]
        == 280
    )
    assert (
        product["source_candidate_ci"]["local_simulation"][
            "tests_skipped_live"
        ]
        == 4
    )
    assert (
        product["source_candidate_ci"]["prior_remote_run"]["conclusion"]
        == "success"
    )
    remote = product["source_candidate_ci"]["remote_run"]
    assert remote["conclusion"] == "success"
    assert remote["annotations"] == 0
    assert remote["head_sha"] == "7063b0b23e1816c1480e88d6d6c29d5cc539ae1f"
    assert product["prettier"]["verdict"] == V.PASS
    assert product["tibero_jest"]["verdict"] == V.PASS
    assert product["tibero_jest"]["tests"] > 0
    assert product["bank_contract_suite"]["implemented"] == 7
    assert product["bank_contract_suite"]["passed"] == 3
    assert product["bank_contract_suite"]["skipped_live"] == 4
    assert product["ui_typecheck"]["verdict"] == "fail"
    assert product["ui_typecheck"]["error_lines"] > 0
    assert product["ui_typecheck"]["changed_path_error_lines"] == 0
