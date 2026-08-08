"""L5 premerge/postmerge catalog split + stage guards — C35-C45.

Uses a self-contained synthetic git repo so the phase-separation invariants are
tested without external infrastructure.
"""
from __future__ import annotations

import subprocess

import pytest

from acgh import candidate as C
from acgh import phase as P
from acgh import verdict


def _git(repo, *args, env=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=env
    ).stdout


def _rev(repo, ref):
    return _git(repo, "rev-parse", ref).strip()


@pytest.fixture
def synth(tmp_path):
    """base(B) -> target(T) -> candidate(C, touches a scoped path w/ Customization-ID)."""
    import os

    r = tmp_path / "repo"
    r.mkdir()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    _git(r, "init", "-q")
    path = "openmetadata-service/x.java"
    (r / "openmetadata-service").mkdir()
    (r / path).write_text("class X {}\n", encoding="utf-8")
    (r / "README.md").write_text("base\n", encoding="utf-8")
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "base", env=env)
    base = _rev(r, "HEAD")
    (r / "README.md").write_text("target\n", encoding="utf-8")
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "official target", env=env)
    target = _rev(r, "HEAD")
    (r / path).write_text("class X { int bank; }\n", encoding="utf-8")
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "bank change\n\nCustomization-ID: BANK-OM-001", env=env)
    cand = _rev(r, "HEAD")

    manifests = {
        "BANK-OM-001": {
            "schema_version": 2,
            "kind": "core-patch",
            "status": "active",
            "implementation": {"changed_paths": [path]},
            "upgrade_watch": {"paths": [path]},
        }
    }
    lock = C.build_candidate_lock(
        str(r), cand,
        upstream_repository="openmetadata",
        upstream_base_sha=base,
        upstream_target_sha=target,
        candidate_repository="om-temp",
        artifact_digest="sha256:" + "0" * 64,
        artifact_kind="source-tree",
    )
    return {"repo": str(r), "base": base, "target": target, "cand": cand,
            "path": path, "manifests": manifests, "lock": lock, "env": env}


# ---- C35 : premerge runs T42 + T93-policy + T51/T52 ----
def test_c35_premerge_catalog_runs_expected_gates(synth):
    from acgh import layout as L

    layout = L.Layout(synth["base"], ["openmetadata-service/**"], [".bank/**"],
                      ["ext/**"], "analysis_error")
    specs = P.build_premerge_catalog(
        synth["repo"], synth["base"], synth["target"], synth["manifests"],
        layout=layout, candidate_ref=synth["cand"],
    )
    names = {s.name for s in specs}
    assert {"upgrade-watch", "policy-drift", "structdiff"} <= names
    result = P.run_gates(specs, phase=P.PREMERGE)
    by = {e.name: e for e in result.executions}
    assert by["upgrade-watch"].execution_status == P.EXECUTED
    assert by["policy-drift"].execution_status == P.EXECUTED
    assert by["structdiff"].execution_status == P.EXECUTED


# ---- C36 / C37 / C38 : premerge must NOT run T41 / T43 / exact-scope ----
def test_c36_c37_c38_premerge_excludes_postmerge_gates(synth):
    specs = P.build_premerge_catalog(
        synth["repo"], synth["base"], synth["target"], synth["manifests"],
    )
    names = {s.name for s in specs}
    assert not (names & {"sensitive-zones", "debt", "exact-scope-history"})
    for g in ("sensitive-zones", "debt", "exact-scope-history"):
        with pytest.raises(P.PhaseError):
            P.assert_gate_applicable(P.PREMERGE, g)


# ---- C39 : watch-suggest advisory, excluded from verdict ----
def test_c39_watch_suggest_is_advisory(synth):
    specs = P.build_premerge_catalog(
        synth["repo"], synth["base"], synth["target"], synth["manifests"],
        candidate_ref=synth["cand"],
    )
    ws = next(s for s in specs if s.name == "watch-suggest")
    assert ws.advisory and not ws.required


# ---- C42 : correct postmerge candidate -> T41/T43/exact-scope runnable ----
def test_c42_correct_candidate_runs_postmerge_gates(synth):
    from acgh import zones as Z

    zones = Z.Zones({lvl: Z.L.make_spec([]) for lvl in Z._ZONE_ORDER})
    change_intent = {"allowed": [synth["path"]], "forbidden": []}
    P.validate_postmerge_candidate(synth["repo"], synth["lock"])  # must not raise
    specs = P.build_postmerge_catalog(
        synth["repo"], synth["lock"], synth["manifests"],
        zones=zones, change_intent=change_intent, conflict_rate=0.0,
    )
    names = {s.name for s in specs}
    assert {"vendor-ancestry", "sensitive-zones", "debt", "exact-scope-history"} <= names
    result = P.run_gates(specs, phase=P.POSTMERGE)
    by = {e.name: e for e in result.executions}
    for g in ("vendor-ancestry", "sensitive-zones", "debt", "exact-scope-history"):
        assert by[g].execution_status == P.EXECUTED, (g, by[g])
    assert result.phase_status == P.COMPLETE


# ---- C40 : candidate not a descendant of target -> STOP ----
def test_c40_candidate_not_descendant_stops(synth):
    # Build a lock whose target is the candidate's own child (candidate cannot
    # descend from it) => wrong-stage input.
    import os
    r = synth["repo"]
    (open(r + "/README.md", "w")).write("later\n")
    _git(r, "add", "-A", env=synth["env"])
    _git(r, "commit", "-qm", "future target", env=synth["env"])
    future = _rev(r, "HEAD")
    bad_lock = C.build_candidate_lock(
        r, synth["cand"],
        upstream_repository="openmetadata",
        upstream_base_sha=synth["base"],
        upstream_target_sha=future,        # candidate predates this
        candidate_repository="om-temp",
        artifact_digest="sha256:" + "0" * 64,
        artifact_kind="source-tree",
    )
    with pytest.raises(P.PhaseError):
        P.validate_postmerge_candidate(r, bad_lock)


# ---- C41 : the pre-upgrade baseline passed as postmerge candidate -> rejected ----
def test_c41_baseline_as_postmerge_candidate_rejected(synth):
    # The baseline (== target here) is not a merged upgrade candidate.
    baseline_lock = C.build_candidate_lock(
        synth["repo"], synth["target"],
        upstream_repository="openmetadata",
        upstream_base_sha=synth["base"],
        upstream_target_sha=synth["target"],
        candidate_repository="om-temp",
        artifact_digest="sha256:" + "0" * 64,
        artifact_kind="source-tree",
    )
    with pytest.raises(P.PhaseError):
        P.validate_postmerge_candidate(synth["repo"], baseline_lock)


# ---- C43 : premerge result digest cannot approve a postmerge result ----
def test_c43_cross_phase_approval_rejected():
    pre = P.aggregate_phase(
        [P.GateExecution("a", P.EXECUTED, verdict.APPROVAL)], phase=P.PREMERGE
    )
    post = P.aggregate_phase(
        [P.GateExecution("a", P.EXECUTED, verdict.APPROVAL)], phase=P.POSTMERGE
    )
    approval = {"target_result_digest": pre.result_digest(), "phase": P.PREMERGE}
    binds, reasons = P.approval_binds(approval, post)
    assert not binds
    assert any("phase mismatch" in r or "digest mismatch" in r for r in reasons)


# ---- C45 : target branch name matches but commit != official tag -> STOP ----
def test_c45_branch_commit_vs_tag_mismatch_stops(synth):
    # Point a branch "official/target" at base while the official tag is target.
    _git(synth["repo"], "branch", "official/target", synth["base"])
    with pytest.raises(P.PhaseError) as ei:
        P.assert_target_matches_tag(synth["repo"], "official/target", synth["target"])
    msg = str(ei.value)
    assert synth["base"] in msg and synth["target"] in msg


def test_c45_matching_tag_ok(synth):
    _git(synth["repo"], "branch", "official/ok", synth["target"])
    assert P.assert_target_matches_tag(synth["repo"], "official/ok", synth["target"]) == synth["target"]
