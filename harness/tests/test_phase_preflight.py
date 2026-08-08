"""L2 preflight — C4-C8, C34, C46-C51, C76-C78, C101, C105.

Preflight reports EVERY input problem at once and separates blocking problems
(phase must not start) from per-gate optional misses (only that gate skips).
"""
from __future__ import annotations

import subprocess

import pytest

from acgh import phase as P
from acgh import preflight as PF
from acgh import verdict


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "r"
    r.mkdir()
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    (r / "a.txt").write_text("hello\n", encoding="utf-8")
    _git(r, "add", "a.txt")
    _git(r, "commit", "-qm", "c1")
    sha = subprocess.run(["git", "-C", str(r), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return str(r), sha


_BOGUS = "deadbeef" * 5  # 40-hex, not present


# ---- C8 : base object missing -> blocking STOP; downstream exit 3 ----
def test_c8_missing_base_object_blocks(repo):
    repo_path, head = repo
    report = PF.run_preflight(repo_path, refs={"base": _BOGUS, "target": head, "candidate": head})
    assert not report.ready
    names = {c.name for c in report.blocking_problems}
    assert "base" in names
    # A blocked phase must aggregate to analysis_error / exit 3.
    spec = P.GateSpec("upgrade-watch", lambda: P.GateOutcome(verdict.GateResult("upgrade-watch", verdict.PASS)))
    result = P.run_gates([spec], preflight_blocked=not report.ready)
    assert result.phase_status == P.INCOMPLETE
    assert result.exit_code == 3


# ---- C78 : base present but target absent -> missing SHA shown ----
def test_c78_target_absent_shows_sha(repo):
    repo_path, head = repo
    report = PF.run_preflight(repo_path, refs={"base": head, "target": _BOGUS})
    target = next(c for c in report.checks if c.name == "target")
    assert target.status == PF.UNREACHABLE
    assert target.value == _BOGUS
    assert "fetch" in target.next_action


# ---- C76 : blobless clone missing a required blob -> STOP + fetch guidance ----
def test_c76_missing_blob_blocks_with_guidance(repo):
    repo_path, head = repo
    report = PF.run_preflight(repo_path, required_blobs=[(head, "does/not/exist.json")])
    blob = next(c for c in report.checks if c.name.startswith("blob:"))
    assert blob.status == PF.BLOB_MISSING
    assert not report.ready
    assert "fetch" in blob.next_action


def test_blob_access_ok(repo):
    repo_path, head = repo
    report = PF.run_preflight(repo_path, required_blobs=[(head, "a.txt")])
    assert report.ready


# ---- C4 : all active sources same SHA -> consistent ----
def test_c4_consistent_sources(repo):
    report = PF.run_preflight(
        repo[0],
        active_sources=[("candidate-lock", "a" * 40), ("runtime-lock", "a" * 40)],
    )
    c = next(x for x in report.checks if x.name == "candidate_consistency")
    assert c.status == PF.OK
    assert report.ready


# ---- C5 : runtime lock differs -> STOP, values shown ----
def test_c5_inconsistent_runtime_lock_blocks(repo):
    report = PF.run_preflight(
        repo[0],
        active_sources=[("candidate-lock", "a" * 40), ("runtime-lock", "b" * 40)],
    )
    c = next(x for x in report.checks if x.name == "candidate_consistency")
    assert c.status == PF.INCONSISTENT
    assert not report.ready
    assert "a" * 40 in c.detail and "b" * 40 in c.detail


# ---- C6 / C34 : past snapshot/proposal/evidence SHA differs -> provenance only ----
def test_c6_provenance_sha_excluded_from_consistency(repo):
    report = PF.run_preflight(
        repo[0],
        active_sources=[("candidate-lock", "a" * 40)],
        provenance=[("snapshot_sha", "d" * 40), ("past_evidence", "e" * 40)],
    )
    c = next(x for x in report.checks if x.name == "candidate_consistency")
    assert c.status == PF.OK
    assert report.ready  # provenance mismatch never blocks
    prov = {x.name for x in report.checks if x.name.startswith("provenance:")}
    assert prov == {"provenance:snapshot_sha", "provenance:past_evidence"}


# ---- C7 / C46 : change-intent missing -> only T41 disabled, phase may start ----
def test_c7_missing_change_intent_disables_only_t41(repo, tmp_path):
    report = PF.run_preflight(
        repo[0],
        optional_inputs={
            "change_intent": {"path": tmp_path / "nope.yaml", "required_for": ["sensitive-zones"]},
        },
    )
    assert report.ready  # not blocking
    assert report.disabled_gates() == frozenset({"sensitive-zones"})


# ---- C47 / C101 : conflict-rate missing -> only T43 disabled, never assume 0 ----
def test_c47_missing_conflict_rate_disables_only_t43(repo):
    report = PF.run_preflight(repo[0], conflict_rate=None)
    c = next(x for x in report.checks if x.name == "conflict_rate")
    assert c.status == PF.MISSING
    assert report.disabled_gates() == frozenset({"debt"})
    assert report.ready


# ---- C48 : several missing inputs reported together (not stop at first) ----
def test_c48_reports_all_missing_at_once(repo, tmp_path):
    report = PF.run_preflight(
        repo[0],
        refs={"base": _BOGUS},
        required_files={"layout": tmp_path / "no-layout.yaml"},
        optional_inputs={
            "change_intent": {"path": tmp_path / "no.yaml", "required_for": ["sensitive-zones"]},
        },
        conflict_rate=None,
    )
    problem_names = {c.name for c in report.checks if not c.ok}
    assert {"base", "layout", "change_intent", "conflict_rate"} <= problem_names


# ---- C50 : conflict-rate out of [0,1] -> invalid ----
@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_c50_conflict_rate_out_of_range_invalid(repo, bad):
    report = PF.run_preflight(repo[0], conflict_rate=bad)
    c = next(x for x in report.checks if x.name == "conflict_rate")
    assert c.status == PF.INVALID


# ---- C51 : conflict-rate NaN / Inf -> invalid ----
@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_c51_conflict_rate_nan_inf_invalid(repo, bad):
    report = PF.run_preflight(repo[0], conflict_rate=bad)
    c = next(x for x in report.checks if x.name == "conflict_rate")
    assert c.status == PF.INVALID


def test_conflict_rate_valid(repo):
    report = PF.run_preflight(repo[0], conflict_rate=0.2)
    c = next(x for x in report.checks if x.name == "conflict_rate")
    assert c.status == PF.OK


# ---- required repo/policy files are blocking ----
def test_missing_required_file_blocks(repo, tmp_path):
    report = PF.run_preflight(repo[0], required_files={"registry": tmp_path / "missing.yaml"})
    assert not report.ready
    assert "registry" in {c.name for c in report.blocking_problems}
