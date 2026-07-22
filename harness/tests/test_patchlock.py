"""T11 patch-lock structure / digest / ordering / preflight tests."""
import copy
import subprocess

import pytest

from acgh import patchlock as P


def _lock_dict():
    return {
        "schema_version": 1,
        "source_release_tag": "om-1.12.13-bank.1",
        "source_release_sha": "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7",
        "patch_series": [
            {
                "id": "BANK-OM-002",
                "revision": 1,
                "source_commits": ["a" * 40],
            },
            {
                "id": "BANK-OM-001",
                "revision": 4,
                "source_commits": ["b" * 40, "c" * 40],
                "depends_on": ["BANK-OM-002"],
            },
        ],
    }


def test_parse_and_lineage_map():
    lock = P.parse_source_lock(_lock_dict())
    assert lock.lineage_map() == {
        "BANK-OM-002": ["a" * 40],
        "BANK-OM-001": ["b" * 40, "c" * 40],
    }


def test_digest_is_stable_and_key_order_independent():
    d1 = _lock_dict()
    d2 = copy.deepcopy(d1)
    # Reorder keys within an entry; digest must not change.
    d2["patch_series"][1] = {
        "depends_on": ["BANK-OM-002"],
        "source_commits": ["b" * 40, "c" * 40],
        "revision": 4,
        "id": "BANK-OM-001",
    }
    assert P.parse_source_lock(d1).digest() == P.parse_source_lock(d2).digest()


def test_series_reorder_changes_digest():
    # Application ORDER is judgment-relevant, so reordering entries must differ.
    d1 = _lock_dict()
    d2 = copy.deepcopy(d1)
    # Can't just swap (would break topo order); make an independent 2-entry lock.
    base = {
        "schema_version": 1,
        "source_release_sha": "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7",
        "patch_series": [
            {"id": "BANK-OM-001", "revision": 1, "source_commits": ["a" * 40]},
            {"id": "BANK-OM-002", "revision": 1, "source_commits": ["b" * 40]},
        ],
    }
    swapped = copy.deepcopy(base)
    swapped["patch_series"].reverse()
    assert P.parse_source_lock(base).digest() != P.parse_source_lock(swapped).digest()


def test_dependency_after_dependent_rejected():
    d = _lock_dict()
    d["patch_series"].reverse()  # dependent now precedes its dependency
    with pytest.raises(P.PatchLockError, match="topological"):
        P.parse_source_lock(d)


def test_unknown_dependency_rejected():
    d = _lock_dict()
    d["patch_series"][1]["depends_on"] = ["BANK-OM-999"]
    with pytest.raises(P.PatchLockError, match="unknown id"):
        P.parse_source_lock(d)


def test_self_dependency_rejected():
    d = _lock_dict()
    d["patch_series"][0]["depends_on"] = ["BANK-OM-002"]
    with pytest.raises(P.PatchLockError, match="does not precede|itself"):
        P.parse_source_lock(d)


def test_duplicate_id_rejected():
    d = _lock_dict()
    d["patch_series"][1]["id"] = "BANK-OM-002"
    with pytest.raises(P.PatchLockError, match="duplicate"):
        P.parse_source_lock(d)


def test_bad_sha_rejected_by_schema():
    d = _lock_dict()
    d["source_release_sha"] = "not-a-sha"
    with pytest.raises(P.PatchLockError, match="schema"):
        P.parse_source_lock(d)


def test_application_lock_binds_parent_digest():
    lock = P.parse_source_lock(_lock_dict())
    app = P.build_application_lock(lock, applied_commits=["d" * 40], resolution_record_ids=["R1"])
    assert app.parent_lock_digest == lock.digest()
    assert app.applied_commits == ("d" * 40,)


def _run(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


def test_verify_source_objects_preflight(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()
    _run(repo, "init", "-q")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")
    (repo / "f").write_text("x\n")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-m", "c1")
    real = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()

    present = P.parse_source_lock({
        "schema_version": 1,
        "source_release_sha": "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7",
        "patch_series": [{"id": "BANK-OM-001", "revision": 1,
                          "source_commits": [real]}],
    })
    assert P.verify_source_objects(str(repo), present) == []

    missing = P.parse_source_lock({
        "schema_version": 1,
        "source_release_sha": "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7",
        "patch_series": [{"id": "BANK-OM-001", "revision": 1,
                          "source_commits": ["0" * 40]}],
    })
    assert P.verify_source_objects(str(repo), missing) == ["0" * 40]
