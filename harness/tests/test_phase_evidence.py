"""L8 evidence digest + approval binding — C84-C93.

The canonical result digest covers judgment inputs + per-gate verdict/counts and
EXCLUDES observational metadata (timestamps, duration, display order). Approval
binds to that digest; any judgment-input change voids it; a human can never turn
block/analysis_error into pass.
"""
from __future__ import annotations

import json

import pytest
from hypothesis import given, settings, strategies as st

from acgh import phase as P
from acgh import verdict


def _result(verdicts, *, inputs=None, phase=P.POSTMERGE, observational=None, run_id="r"):
    execs = [P.GateExecution(f"g{i}", P.EXECUTED, v) for i, v in enumerate(verdicts)]
    return P.aggregate_phase(execs, phase=phase, inputs=inputs or {},
                             run_id=run_id, observational=observational or {})


_VERDICTS = st.lists(st.sampled_from(verdict.VERDICTS), min_size=1, max_size=5)
_INPUTS = st.dictionaries(
    st.sampled_from(["base_sha", "target_sha", "candidate_lock_digest", "policy_digest"]),
    st.text(min_size=1, max_size=12), min_size=1, max_size=4,
)


# ---- C84 : same judgment inputs -> identical digest (PBT) ----
@given(vs=_VERDICTS, inputs=_INPUTS)
def test_c84_same_inputs_same_digest(vs, inputs):
    a = _result(vs, inputs=inputs)
    b = _result(vs, inputs=inputs)
    assert a.result_digest() == b.result_digest()


# ---- C85 : timestamp/duration-only change -> same digest (PBT) ----
@given(vs=_VERDICTS, inputs=_INPUTS,
       d1=st.floats(min_value=0, max_value=1e6, allow_nan=False),
       d2=st.floats(min_value=0, max_value=1e6, allow_nan=False))
def test_c85_observational_only_change_same_digest(vs, inputs, d1, d2):
    a = _result(vs, inputs=inputs, observational={"duration_s": d1, "timestamp": "t1"}, run_id="A")
    b = _result(vs, inputs=inputs, observational={"duration_s": d2, "timestamp": "t2"}, run_id="B")
    assert a.result_digest() == b.result_digest()


# ---- C86 : any judgment input change -> digest changes (PBT) ----
@given(vs=_VERDICTS, inputs=_INPUTS, extra=st.text(min_size=1, max_size=8))
def test_c86_input_change_changes_digest(vs, inputs, extra):
    a = _result(vs, inputs=inputs)
    changed = {**inputs, "candidate_lock_digest": inputs.get("candidate_lock_digest", "") + extra + "!"}
    b = _result(vs, inputs=changed)
    assert a.result_digest() != b.result_digest()


# ---- C87 : manually edited stored JSON -> digest verification fails ----
def test_c87_tampered_file_fails_verification(tmp_path):
    r = _result([verdict.PASS], inputs={"base_sha": "aaa"})
    path = tmp_path / "run.json"
    P.write_phase_result(r, path)
    ok, _ = P.verify_phase_result(path)
    assert ok
    data = json.loads(path.read_text())
    data["canonical_payload"]["overall_verdict"] = "pass"  # tamper: was maybe pass; force flip a field
    data["canonical_payload"]["inputs"]["base_sha"] = "zzz"
    path.write_text(json.dumps(data), encoding="utf-8")
    ok2, reason = P.verify_phase_result(path)
    assert not ok2 and "mismatch" in reason


# ---- C88 : after approval, an input file change voids the old approval ----
def test_c88_input_change_voids_approval():
    r1 = _result([verdict.APPROVAL], inputs={"policy_digest": "p1"})
    approval = {"target_result_digest": r1.result_digest(), "phase": r1.phase}
    assert P.approval_binds(approval, r1)[0]
    r2 = _result([verdict.APPROVAL], inputs={"policy_digest": "p2"})  # policy changed
    binds, reasons = P.approval_binds(approval, r2)
    assert not binds and any("digest mismatch" in x for x in reasons)


# ---- C44 : adding a commit to the candidate voids the prior result/approval ----
def test_c44_new_candidate_commit_invalidates_result_and_approval():
    before = _result([verdict.APPROVAL], inputs={"candidate_lock_digest": "sha256:before"})
    approval = {"target_result_digest": before.result_digest(), "phase": before.phase}
    assert P.approval_binds(approval, before)[0]
    # a new candidate commit => new candidate_lock_digest => new result identity
    after = _result([verdict.APPROVAL], inputs={"candidate_lock_digest": "sha256:after"})
    assert after.result_digest() != before.result_digest()
    binds, reasons = P.approval_binds(approval, after)
    assert not binds  # re-check + re-approval required


# ---- C89 : candidate A's approval used on candidate B -> rejected ----
def test_c89_approval_of_a_not_valid_for_b():
    a = _result([verdict.APPROVAL], inputs={"candidate_lock_digest": "A"})
    b = _result([verdict.APPROVAL], inputs={"candidate_lock_digest": "B"})
    approval = {"target_result_digest": a.result_digest(), "phase": a.phase}
    assert not P.approval_binds(approval, b)[0]


# ---- C90 : a human cannot approve block/analysis_error into pass ----
@pytest.mark.parametrize("v", [verdict.BLOCK, verdict.ANALYSIS_ERROR])
def test_c90_cannot_approve_block_into_pass(v):
    r = _result([v], inputs={"base_sha": "x"})
    approval = {"target_result_digest": r.result_digest(), "phase": r.phase}
    binds, reasons = P.approval_binds(approval, r)
    assert not binds
    assert any("cannot be approved" in x for x in reasons)
    # machine verdict itself never mutates
    assert r.overall_verdict == v


# ---- C91 : reusing a run-id path must not overwrite existing evidence ----
def test_c91_run_id_reuse_no_overwrite(tmp_path):
    r = _result([verdict.PASS], inputs={"base_sha": "x"})
    path = tmp_path / "run-1.json"
    P.write_phase_result(r, path)
    with pytest.raises(P.ApprovalError):
        P.write_phase_result(r, path)  # same run-id path
    assert P.verify_phase_result(path)[0]


# ---- C92 : two concurrent phases -> separate folders, complete results ----
def test_c92_two_phases_separate_folders(tmp_path):
    pre = _result([verdict.PASS], phase=P.PREMERGE, inputs={"base_sha": "x"})
    post = _result([verdict.APPROVAL], phase=P.POSTMERGE, inputs={"base_sha": "x"})
    p1 = P.write_phase_result(pre, tmp_path / "premerge" / "r.json")
    p2 = P.write_phase_result(post, tmp_path / "postmerge" / "r.json")
    assert p1 != p2
    assert P.verify_phase_result(p1)[0] and P.verify_phase_result(p2)[0]


# ---- C109 : run-id with ../ must not escape the evidence base ----
@pytest.mark.parametrize("bad", ["../escape", "a/b", "/abs", "..", "x/../../y"])
def test_c109_run_id_path_traversal_rejected(tmp_path, bad):
    with pytest.raises(P.ApprovalError):
        P.evidence_path(tmp_path, bad)


def test_c109_safe_run_id_ok(tmp_path):
    p = P.evidence_path(tmp_path, "run-2026-08-07")
    assert str(p).startswith(str(tmp_path.resolve()))


# ---- C93 : no half-written artifact left behind (atomic write) ----
def test_c93_atomic_write_no_partial(tmp_path):
    r = _result([verdict.PASS], inputs={"base_sha": "x"})
    path = tmp_path / "run.json"
    P.write_phase_result(r, path)
    leftovers = [p.name for p in tmp_path.iterdir() if p.name.startswith(".run.json.tmp")]
    assert leftovers == []
    assert P.verify_phase_result(path)[0]
