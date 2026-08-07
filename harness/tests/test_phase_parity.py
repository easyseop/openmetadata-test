"""L6 golden parity — C66-C74.

The bundle must NEVER reimplement gate judgment. For every gate, the bundle's
per-gate {name, verdict, reasons, target_count} must EQUAL a DIRECT invocation
of the same underlying acgh function / runner with identical inputs.

- C66-C69: the four verdicts (pass/approval/block/analysis_error) all match.
- C72: order-only differences in reasons still count as parity.
- C73: a single differing reason/path/count breaks parity.
- C74: a mutant gate that reimplements judgment (instead of calling the runner)
  fails the golden parity test.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from acgh import candidate as C
from acgh import phase as P
from acgh import verdict

REPO = "/Users/seop/om-work/om-temp-real-1.13.1"
REG = Path(__file__).resolve().parents[1] / "registrations" / "om-temp-1.13.1"
HARNESS = Path(__file__).resolve().parents[1]
BASE_113_1 = "official/om-1.13.1"
TARGET_113_2 = "official/om-1.13.2"


def _git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, env=env).stdout


def _env():
    return {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def _make_repo(tmp_path, *, base_files, target_files, cand_files, cand_id="BANK-OM-001"):
    r = tmp_path / "repo"
    r.mkdir()
    env = _env()
    _git(r, "init", "-q")

    def _write(files):
        for rel, content in files.items():
            p = r / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    _write(base_files)
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "base", env=env)
    base = _git(r, "rev-parse", "HEAD").strip()
    _write(target_files)
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", "target", env=env)
    target = _git(r, "rev-parse", "HEAD").strip()
    _write(cand_files)
    _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", f"cand\n\nCustomization-ID: {cand_id}", env=env)
    cand = _git(r, "rev-parse", "HEAD").strip()
    return str(r), base, target, cand


def _parity(bundle_exec, direct_result, *, target_count=None):
    """Compare an execution to a direct GateResult; reasons order-independent (C72)."""
    return (
        bundle_exec.name == direct_result.name
        and bundle_exec.verdict == direct_result.verdict
        and set(bundle_exec.reasons) == set(direct_result.reasons)
        and (target_count is None or bundle_exec.target_count == target_count)
    )


def _bundle_gate(specs, name):
    result = P.run_gates(specs, phase=P.PREMERGE if name in P.PREMERGE_GATES else P.POSTMERGE)
    return next(e for e in result.executions if e.name == name)


# ---- C66 : upgrade-watch PASS parity ----
def test_c66_upgrade_watch_pass_parity(tmp_path):
    from acgh import gitprim, upgrade_watch
    repo, base, target, cand = _make_repo(
        tmp_path,
        base_files={"svc/a.java": "A\n", "README.md": "1\n"},
        target_files={"README.md": "2\n"},          # watched path NOT changed
        cand_files={"svc/a.java": "B\n"},
    )
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": ["svc/a.java"]},
                                 "upgrade_watch": {"paths": ["svc/a.java"]}}}
    direct = upgrade_watch.to_gate_result(
        upgrade_watch.evaluate_upgrade_watch(repo, base, target, manifests))
    count = len(gitprim.net_changed_paths(repo, base, target))
    specs = P.build_premerge_catalog(repo, base, target, manifests)
    assert direct.verdict == verdict.PASS
    assert _parity(_bundle_gate(specs, "upgrade-watch"), direct, target_count=count)


# ---- C67 : upgrade-watch APPROVAL parity ----
def test_c67_upgrade_watch_approval_parity(tmp_path):
    from acgh import gitprim, upgrade_watch
    repo, base, target, cand = _make_repo(
        tmp_path,
        base_files={"svc/a.java": "A\n", "README.md": "1\n"},
        target_files={"svc/a.java": "CHANGED\n"},    # watched path changed A->B
        cand_files={"svc/a.java": "B\n"},
    )
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": ["svc/a.java"]},
                                 "upgrade_watch": {"paths": ["svc/a.java"]}}}
    direct = upgrade_watch.to_gate_result(
        upgrade_watch.evaluate_upgrade_watch(repo, base, target, manifests))
    count = len(gitprim.net_changed_paths(repo, base, target))
    specs = P.build_premerge_catalog(repo, base, target, manifests)
    assert direct.verdict == verdict.APPROVAL
    assert _parity(_bundle_gate(specs, "upgrade-watch"), direct, target_count=count)


# ---- C68 : sensitive-zones BLOCK parity (frozen zone) ----
def test_c68_sensitive_zones_block_parity(tmp_path):
    from acgh import gitprim, zones as Z
    frozen = "svc/security/Auth.java"
    repo, base, target, cand = _make_repo(
        tmp_path,
        base_files={frozen: "A\n"},
        target_files={frozen: "A2\n"},
        cand_files={frozen: "BANKED\n"},
    )
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": [frozen]}}}
    zones = Z.Zones({"frozen": Z.L.make_spec(["svc/security/**"]),
                     "protected": Z.L.make_spec([]), "watched": Z.L.make_spec([])})
    intent = {"allowed": [frozen], "forbidden": []}
    changes = gitprim.net_changed_paths(repo, target, cand)
    direct = Z.check_sensitive_zones(changes, zones, intent)
    lock = C.build_candidate_lock(repo, cand, upstream_repository="om", upstream_base_sha=base,
                                  upstream_target_sha=target, candidate_repository="c",
                                  artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree")
    specs = P.build_postmerge_catalog(repo, lock, manifests, zones=zones, change_intent=intent,
                                      conflict_rate=0.0)
    assert direct.verdict == verdict.BLOCK
    assert _parity(_bundle_gate(specs, "sensitive-zones"), direct, target_count=len(changes))


# ---- C69 : sensitive-zones ANALYSIS_ERROR parity (empty allowed scope) ----
def test_c69_sensitive_zones_analysis_error_parity(tmp_path):
    from acgh import gitprim, zones as Z
    repo, base, target, cand = _make_repo(
        tmp_path,
        base_files={"svc/a.java": "A\n"},
        target_files={"svc/a.java": "A2\n"},
        cand_files={"svc/a.java": "B\n"},
    )
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": ["svc/a.java"]}}}
    zones = Z.Zones({lvl: Z.L.make_spec([]) for lvl in Z._ZONE_ORDER})
    intent = {"allowed": [], "forbidden": []}  # no approved scope -> fail closed
    changes = gitprim.net_changed_paths(repo, target, cand)
    direct = Z.check_sensitive_zones(changes, zones, intent)
    lock = C.build_candidate_lock(repo, cand, upstream_repository="om", upstream_base_sha=base,
                                  upstream_target_sha=target, candidate_repository="c",
                                  artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree")
    specs = P.build_postmerge_catalog(repo, lock, manifests, zones=zones, change_intent=intent,
                                      conflict_rate=0.0)
    ex = _bundle_gate(specs, "sensitive-zones")
    assert direct.verdict == verdict.ANALYSIS_ERROR
    assert ex.execution_status == P.EXECUTED   # analysis_error is executed, not hidden
    assert _parity(ex, direct)


# ---- C72 : reason ORDER-only difference still parity ----
def test_c72_reason_order_independent():
    a = P.GateExecution("g", P.EXECUTED, verdict.BLOCK, reasons=("x", "y", "z"))
    direct = verdict.GateResult("g", verdict.BLOCK, ("z", "y", "x"))
    assert _parity(a, direct)


# ---- C73 : a single differing reason/count breaks parity ----
def test_c73_difference_breaks_parity():
    a = P.GateExecution("g", P.EXECUTED, verdict.BLOCK, reasons=("x", "y"), target_count=5)
    assert not _parity(a, verdict.GateResult("g", verdict.BLOCK, ("x", "DIFFERENT")))
    assert not _parity(a, verdict.GateResult("g", verdict.BLOCK, ("x", "y")), target_count=6)
    assert not _parity(a, verdict.GateResult("g", verdict.APPROVAL, ("x", "y")))


# ---- C74 : a mutant that reimplements the gate fails golden parity ----
def test_c74_reimplementing_mutant_fails_parity(tmp_path):
    from acgh import upgrade_watch
    repo, base, target, cand = _make_repo(
        tmp_path,
        base_files={"svc/a.java": "A\n"},
        target_files={"svc/a.java": "CHANGED\n"},
        cand_files={"svc/a.java": "B\n"},
    )
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": ["svc/a.java"]},
                                 "upgrade_watch": {"paths": ["svc/a.java"]}}}
    direct = upgrade_watch.to_gate_result(
        upgrade_watch.evaluate_upgrade_watch(repo, base, target, manifests))

    # Mutant: does NOT call the runner; hardcodes pass.
    def mutant_run():
        return P.GateOutcome(verdict.GateResult("upgrade-watch", verdict.PASS, ()))

    mutant = P.execute_gate(P.GateSpec("upgrade-watch", mutant_run))
    assert direct.verdict == verdict.APPROVAL
    assert not _parity(mutant, direct)   # golden parity kills the mutant


# ================= real-repo T42 subprocess parity (integration) =================
def _real_refs_available() -> bool:
    if not Path(REPO).is_dir() or not (REG / "customization-registry.yaml").is_file():
        return False
    return all(
        subprocess.run(
            ["git", "-C", REPO, "rev-parse", "--verify", "--quiet", ref],
            capture_output=True,
        ).returncode == 0
        for ref in (BASE_113_1, TARGET_113_2)
    )


_HAVE_REAL = _real_refs_available()


@pytest.mark.skipif(not _HAVE_REAL, reason="real OM_CODE_REPO / om-temp-1.13.1 registration not present")
def test_t42_subprocess_runner_vs_bundle_parity(tmp_path):
    """run_upgrade_watch.py (existing runner) vs the bundle's upgrade-watch gate."""
    from acgh import gitprim, upgrade_watch, vendor_rebuild

    out = subprocess.run(
        [sys.executable, str(HARNESS / "run_upgrade_watch.py"),
         "--repo", REPO, "--harness", str(HARNESS), "--registration", str(REG),
         "--upstream-base", BASE_113_1, "--upstream-target", TARGET_113_2],
        capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr
    runner = json.loads(out.stdout)

    registry, manifests, _inv = vendor_rebuild.load_registration_bundle(REG)
    active = {cid: manifests[cid] for cid in registry.active_ids()}
    specs = P.build_premerge_catalog(REPO, BASE_113_1, TARGET_113_2, active)
    ex = _bundle_gate(specs, "upgrade-watch")

    assert ex.verdict == runner["gate"]["verdict"]
    assert set(ex.reasons) == set(runner["gate"]["reasons"])
    assert ex.target_count == runner["upstream"]["changed_path_count"]
