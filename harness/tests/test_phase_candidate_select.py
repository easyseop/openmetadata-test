"""Phase bundling — active candidate selection (C1-C3, C17, C27, C21-C34).

Tests the explicit active-candidate pointer: no auto-latest, approval binding,
digest linkage, provenance preservation, schema v1/v2 compatibility.
Property-based tests (hypothesis) cover digest determinism and approval binding.
"""
from __future__ import annotations

import yaml
import pytest
from hypothesis import given, strategies as st

from acgh import candidate as candidate_mod
from acgh import candidate_select as cs


def _sha(ch: str) -> str:
    return (ch * 40)[:40]


def _digest(ch: str = "0") -> str:
    return "sha256:" + (ch * 64)[:64]


def _lock_data(commit, tree, *, target=None, version=2, artifact=None):
    data = {
        "schema_version": version,
        "integration_strategy": "vendor-merge",
        "upstream": {
            "repository": "openmetadata",
            "base_sha": _sha("a"),
            "target_sha": target or _sha("c"),
            "base_tag": "1.13.1-release",
            "target_tag": "1.13.2-release",
        },
        "candidate": {
            "repository": "om-temp-real",
            "commit_sha": commit,
            "tree_sha": tree,
            "artifact_digest": artifact or _digest("0"),
        },
    }
    if version == 2:
        data["candidate"]["artifact_kind"] = "source-tree"
    return data


def _write_lock(locks_dir, name, commit, tree, **kw):
    path = locks_dir / f"{name}.yaml"
    path.write_text(yaml.safe_dump(_lock_data(commit, tree, **kw), allow_unicode=True), encoding="utf-8")
    return path, candidate_mod.load_candidate_lock(path).digest()


def _write_approval(locks_dir, name, digest, *, approver="데이터시스템부",
                    approved_at="2026-08-07T23:00:00Z", rationale="Runtime Contract 9 pass"):
    (locks_dir / f"{name}.approval.yaml").write_text(
        yaml.safe_dump(
            {"candidate_lock_digest": digest, "approver": approver,
             "approved_at": approved_at, "rationale": rationale},
            allow_unicode=True),
        encoding="utf-8")


def _write_active(locks_dir, digest):
    (locks_dir / "active-candidate.yaml").write_text(
        yaml.safe_dump(
            {"schema_version": 1, "candidate_lock_digest": digest,
             "activated_by": "데이터시스템부", "activated_at": "2026-08-07T23:00:00Z",
             "rationale": "active baseline"},
            allow_unicode=True),
        encoding="utf-8")


@pytest.fixture
def reg(tmp_path):
    (tmp_path / "candidate-locks").mkdir()
    return tmp_path


def _locks(reg):
    return reg / "candidate-locks"


# ---- C1 / C21 / C3 : selection basics ----

def test_c1_two_approved_locks_selects_the_active_pointer(reg):
    _, d1 = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d1)
    p2, d2 = _write_lock(_locks(reg), "lockB", _sha("3"), _sha("4"))
    _write_approval(_locks(reg), "lockB", d2)
    _write_active(_locks(reg), d1)
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.SELECTED
    assert sel.lock.candidate.commit_sha == _sha("1")
    # the other approved lock is preserved as provenance, never auto-swapped
    assert any(pv["digest"] == d2 for pv in sel.provenance)


def test_c21_no_active_pointer_even_with_approved_locks_is_analysis_error(reg):
    _, d1 = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d1)
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.ANALYSIS_ERROR
    assert any("active-candidate" in r for r in sel.reasons)


def test_c3_no_locks_is_analysis_error(reg):
    _write_active(_locks(reg), _digest("9"))
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.ANALYSIS_ERROR


# ---- C2 / C22 / C23 / C24 / C25 : approval binding ----

def test_c2_approval_digest_mismatch_blocks(reg):
    p, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", _digest("f"))  # wrong digest
    _write_active(_locks(reg), d)
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.BLOCKED
    assert any("digest mismatch" in r for r in sel.reasons)


def test_c22_active_points_to_unapproved_lock_blocks(reg):
    p, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_active(_locks(reg), d)  # no approval file written
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.BLOCKED
    assert any("unapproved" in r for r in sel.reasons)


def test_c23_active_digest_not_found_blocks_and_shows_values(reg):
    _, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d)
    _write_active(_locks(reg), _digest("e"))  # points nowhere
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.BLOCKED
    joined = " ".join(sel.reasons)
    assert _digest("e") in joined and d in joined


def test_c24_placeholder_approver_is_unapproved(reg):
    _, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d, approver="<사람>")
    _write_active(_locks(reg), d)
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.BLOCKED
    assert any("approver" in r for r in sel.reasons)


def test_c25_bad_approved_at_is_unapproved(reg):
    _, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d, approved_at="2026/08/07 23:00")
    _write_active(_locks(reg), d)
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.BLOCKED
    assert any("RFC3339" in r or "approved_at" in r for r in sel.reasons)


# ---- C28 / C34 : provenance, no auto-swap ----

def test_c28_same_tree_different_commit_preserved_not_swapped(reg):
    _, d1 = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d1)
    _, d2 = _write_lock(_locks(reg), "lockB", _sha("3"), _sha("2"))  # same tree
    _write_approval(_locks(reg), "lockB", d2)
    _write_active(_locks(reg), d1)
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.SELECTED
    assert sel.lock.candidate.commit_sha == _sha("1")
    assert any(pv["digest"] == d2 for pv in sel.provenance)


# ---- C31 / C32 : schema compatibility ----

def test_c32_schema_v2_parses_and_selects(reg):
    _, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"), version=2)
    _write_approval(_locks(reg), "lockA", d)
    _write_active(_locks(reg), d)
    assert cs.select_active_candidate(reg).status == cs.SELECTED


def test_c31_schema_v1_parses_and_selects(reg):
    _, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"), version=1)
    _write_approval(_locks(reg), "lockA", d)
    _write_active(_locks(reg), d)
    assert cs.select_active_candidate(reg).status == cs.SELECTED


# ---- C33 : corrupt lock ----

def test_c33_corrupt_lock_is_analysis_error(reg):
    (_locks(reg) / "lockA.yaml").write_text("schema_version: 2\nupstream: {oops\n", encoding="utf-8")
    _write_active(_locks(reg), _digest("a"))
    sel = cs.select_active_candidate(reg)
    assert sel.status == cs.ANALYSIS_ERROR
    assert any("corrupt" in r.lower() for r in sel.reasons)


# ---- C17 : lock content change invalidates approval ----

def test_c17_lock_change_invalidates_approval(reg):
    path, d = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d)
    _write_active(_locks(reg), d)
    assert cs.select_active_candidate(reg).status == cs.SELECTED
    # mutate the lock content -> digest changes -> old approval/active no longer bind
    path.write_text(yaml.safe_dump(_lock_data(_sha("9"), _sha("2")), allow_unicode=True), encoding="utf-8")
    sel = cs.select_active_candidate(reg)
    assert sel.status != cs.SELECTED


# ---- C27 : pinning boundary (selection is an immutable snapshot) ----

def test_c27_selection_snapshot_not_affected_by_later_active_change(reg):
    _, d1 = _write_lock(_locks(reg), "lockA", _sha("1"), _sha("2"))
    _write_approval(_locks(reg), "lockA", d1)
    _, d2 = _write_lock(_locks(reg), "lockB", _sha("3"), _sha("4"))
    _write_approval(_locks(reg), "lockB", d2)
    _write_active(_locks(reg), d1)
    sel = cs.select_active_candidate(reg)
    assert sel.lock.candidate.commit_sha == _sha("1")
    # repoint active to B AFTER selection; the captured selection must not change
    _write_active(_locks(reg), d2)
    assert sel.lock.candidate.commit_sha == _sha("1")


# ---- property-based (hypothesis) ----

_HEX = st.text(alphabet="0123456789abcdef", min_size=40, max_size=40)


@given(commit=_HEX, tree=_HEX)
def test_pbt_digest_is_deterministic(tmp_path_factory, commit, tree):
    d = tmp_path_factory.mktemp("locks")
    data = _lock_data(commit, tree)
    p = d / "l.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    a = candidate_mod.load_candidate_lock(p).digest()
    b = candidate_mod.load_candidate_lock(p).digest()
    assert a == b and a.startswith("sha256:")


@given(commit=_HEX, tree=_HEX, other=_HEX)
def test_pbt_commit_change_changes_digest(tmp_path_factory, commit, tree, other):
    if other == commit:
        return
    d = tmp_path_factory.mktemp("locks")
    p = d / "l.yaml"
    p.write_text(yaml.safe_dump(_lock_data(commit, tree), allow_unicode=True), encoding="utf-8")
    d1 = candidate_mod.load_candidate_lock(p).digest()
    p.write_text(yaml.safe_dump(_lock_data(other, tree), allow_unicode=True), encoding="utf-8")
    d2 = candidate_mod.load_candidate_lock(p).digest()
    assert d1 != d2


@given(approver=st.text(min_size=1, max_size=30).filter(
    lambda s: s.strip() and not cs._is_placeholder(s)))
def test_pbt_nonplaceholder_approver_selects(tmp_path_factory, approver):
    reg = tmp_path_factory.mktemp("reg")
    locks = reg / "candidate-locks"
    locks.mkdir()
    _, d = _write_lock(locks, "lockA", _sha("1"), _sha("2"))
    _write_approval(locks, "lockA", d, approver=approver)
    _write_active(locks, d)
    assert cs.select_active_candidate(reg).status == cs.SELECTED
