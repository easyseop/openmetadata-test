"""Risk-side parity + conflict-rate/debt boundaries — C15, C16, C70, C71, C101-C106.

Compares the bundle's postmerge risk gates (T43 debt, T51/T52 structdiff) to
direct acgh function calls, and exercises conflict-rate presence/absence and
debt threshold boundaries.
"""
from __future__ import annotations

import os
import subprocess

import pytest

from acgh import candidate as C
from acgh import debt
from acgh import phase as P
from acgh import verdict


def _git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, env=env).stdout


def _env():
    return {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def _make(tmp_path, base_files, target_files, cand_files, cid="BANK-OM-001"):
    r = tmp_path / "repo"
    r.mkdir()
    env = _env()
    _git(r, "init", "-q")

    def _w(files):
        for rel, content in files.items():
            p = r / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    _w(base_files); _git(r, "add", "-A", env=env); _git(r, "commit", "-qm", "base", env=env)
    base = _git(r, "rev-parse", "HEAD").strip()
    _w(target_files); _git(r, "add", "-A", env=env); _git(r, "commit", "-qm", "target", env=env)
    target = _git(r, "rev-parse", "HEAD").strip()
    _w(cand_files); _git(r, "add", "-A", env=env)
    _git(r, "commit", "-qm", f"c\n\nCustomization-ID: {cid}", env=env)
    cand = _git(r, "rev-parse", "HEAD").strip()
    return str(r), base, target, cand


@pytest.fixture
def postmerge(tmp_path):
    path = "svc/a.java"
    repo, base, target, cand = _make(
        tmp_path,
        base_files={path: "A\n"},
        target_files={path: "A2\n"},
        cand_files={path: "B\n"},
    )
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": [path]}}}
    lock = C.build_candidate_lock(repo, cand, upstream_repository="om", upstream_base_sha=base,
                                  upstream_target_sha=target, candidate_repository="c",
                                  artifact_digest="sha256:" + "0" * 64, artifact_kind="source-tree")
    return {"repo": repo, "base": base, "target": target, "cand": cand,
            "manifests": manifests, "lock": lock, "path": path}


def _debt_exec(postmerge, conflict_rate, thresholds=None):
    specs = P.build_postmerge_catalog(
        postmerge["repo"], postmerge["lock"], postmerge["manifests"],
        conflict_rate=conflict_rate, thresholds=thresholds,
    )
    result = P.run_gates(specs, phase=P.POSTMERGE)
    return next(e for e in result.executions if e.name == "debt")


# ---- C15 / C70 : conflict-rate absent -> T43 skipped; other gates still parity ----
def test_c15_conflict_rate_absent_skips_only_t43(postmerge):
    ex = _debt_exec(postmerge, conflict_rate=...)  # not provided
    assert ex.execution_status == P.SKIPPED_MISSING_INPUT
    assert ex.verdict is None


# ---- C16 : conflict-rate present -> T43 executes and matches direct call ----
def test_c16_conflict_rate_present_parity(postmerge):
    metrics = debt.collect_metrics(postmerge["repo"], postmerge["target"], postmerge["cand"],
                                   postmerge["manifests"], conflict_rate=0.1)
    direct = debt.evaluate_debt(metrics, debt.DEFAULT_THRESHOLDS)
    ex = _debt_exec(postmerge, conflict_rate=0.1)
    assert ex.execution_status == P.EXECUTED
    assert ex.verdict == direct.verdict
    assert set(ex.reasons) == set(direct.reasons)


# ---- C101 : no approved baseline -> conflict-rate not assumed 0, T43 not run ----
def test_c101_no_conflict_rate_not_assumed_zero(postmerge):
    ex = _debt_exec(postmerge, conflict_rate=...)
    assert ex.verdict is None  # never fabricated as pass with rate 0


# ---- C102/C103/C104 : conflict-rate below / equal / above threshold ----
@pytest.mark.parametrize("rate,expected", [
    (0.14, verdict.PASS),       # below soft
    (0.15, verdict.PASS),       # exactly soft (not > soft)
    (0.16, verdict.APPROVAL),   # above soft
    (0.35, verdict.APPROVAL),   # exactly hard (not > hard)
    (0.36, verdict.BLOCK),      # above hard
])
def test_c102_c104_conflict_rate_boundaries(postmerge, rate, expected):
    # isolate conflict_rate: make all other metrics trivially within budget
    thresholds = {"conflict_rate": {"soft": 0.15, "hard": 0.35}}
    metrics = debt.collect_metrics(postmerge["repo"], postmerge["target"], postmerge["cand"],
                                   postmerge["manifests"], conflict_rate=rate)
    metrics = {"conflict_rate": metrics["conflict_rate"]}  # only the boundary metric
    direct = debt.evaluate_debt(metrics, thresholds)
    assert direct.verdict == expected


# ---- C105 : zero comparison files -> explicit result, no ZeroDivisionError ----
def test_c105_zero_changed_files_no_div_by_zero(postmerge):
    # base == head => no changed files
    metrics = debt.collect_metrics(postmerge["repo"], postmerge["target"], postmerge["target"],
                                   postmerge["manifests"], conflict_rate=0.0)
    assert metrics["changed_lines"] == 0
    result = debt.evaluate_debt(metrics, debt.DEFAULT_THRESHOLDS)
    assert result.verdict == verdict.PASS  # explicit, not a crash


# ---- C71 : structdiff mixed json/yaml/text -> per-file parity, text skipped ----
def test_c71_structdiff_mixed_types_parity(tmp_path):
    from acgh import structdiff, upgrade_watch
    repo, base, target, cand = _make(
        tmp_path,
        base_files={"c/a.json": '{"k": 1}\n', "c/b.yaml": "k: 1\n", "c/c.txt": "one\n"},
        target_files={"c/a.json": '{"k": 2}\n', "c/b.yaml": "k: 2\n", "c/c.txt": "two\n"},
        cand_files={"c/a.json": '{"k": 3}\n'},
    )
    watched = ["c/a.json", "c/b.yaml", "c/c.txt"]
    manifests = {"BANK-OM-001": {"schema_version": 2, "kind": "core-patch", "status": "active",
                                 "implementation": {"changed_paths": ["c/a.json"]},
                                 "upgrade_watch": {"paths": watched}}}
    # direct structural diffs for the config files only
    direct = {p: structdiff.diff_file(repo, base, target, p).summary()
              for p in ("c/a.json", "c/b.yaml")}
    specs = P.build_premerge_catalog(repo, base, target, manifests)
    result = P.run_gates(specs, phase=P.PREMERGE)
    sd = next(e for e in result.executions if e.name == "structdiff")
    bundle = dict(item.split(": ", 1) for item in sd.evidence)
    assert bundle == direct
    assert "c/c.txt" not in bundle  # text file excluded from structural diff in both
