"""T23 single-integrator CAS lock-update tests."""
import subprocess

import pytest

from acgh import integrator as IN
from acgh import patchlock as P

_REF = "refs/bank/patch-lock"
_SHA = "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7"


def _repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "-C", str(r), "init", "-q"], check=True,
                   capture_output=True, text=True)
    return str(r)


def _lock(revision=1):
    return {
        "schema_version": 1,
        "source_release_sha": _SHA,
        "patch_series": [
            {"id": "BANK-OM-001", "revision": revision, "source_commits": ["a" * 40]},
        ],
    }


def test_initial_create_then_read(tmp_path):
    repo = _repo(tmp_path)
    oid = IN.integrate_lock(repo, _REF, _lock(1),
                            base_lock_digest=None, expected_oid=IN._ZERO)
    got = IN.read_lock(repo, _REF)
    assert got is not None and got[0] == oid
    assert got[1].digest() == P.parse_source_lock(_lock(1)).digest()


def test_create_rejects_when_base_supplied_but_absent(tmp_path):
    repo = _repo(tmp_path)
    with pytest.raises(IN.StaleBaseError):
        IN.integrate_lock(repo, _REF, _lock(1),
                          base_lock_digest="sha256:" + "0" * 64,
                          expected_oid="a" * 40)


def test_sequential_update_succeeds(tmp_path):
    repo = _repo(tmp_path)
    oid1 = IN.integrate_lock(repo, _REF, _lock(1),
                             base_lock_digest=None, expected_oid=IN._ZERO)
    base_digest = P.parse_source_lock(_lock(1)).digest()
    oid2 = IN.integrate_lock(repo, _REF, _lock(2),
                             base_lock_digest=base_digest, expected_oid=oid1)
    assert oid2 != oid1
    assert IN.read_lock(repo, _REF)[1].patch_series[0].revision == 2


def test_concurrent_update_from_same_base_is_rejected(tmp_path):
    repo = _repo(tmp_path)
    oid1 = IN.integrate_lock(repo, _REF, _lock(1),
                             base_lock_digest=None, expected_oid=IN._ZERO)
    base_digest = P.parse_source_lock(_lock(1)).digest()
    # Integrator A wins.
    IN.integrate_lock(repo, _REF, _lock(2),
                      base_lock_digest=base_digest, expected_oid=oid1)
    # Integrator B started from the same base -> must be rejected (stale).
    with pytest.raises(IN.StaleBaseError):
        IN.integrate_lock(repo, _REF, _lock(3),
                          base_lock_digest=base_digest, expected_oid=oid1)
    # The lock still reflects A's write, not B's.
    assert IN.read_lock(repo, _REF)[1].patch_series[0].revision == 2


def test_wrong_digest_rejected_even_with_right_oid(tmp_path):
    repo = _repo(tmp_path)
    oid1 = IN.integrate_lock(repo, _REF, _lock(1),
                             base_lock_digest=None, expected_oid=IN._ZERO)
    with pytest.raises(IN.StaleBaseError, match="digest"):
        IN.integrate_lock(repo, _REF, _lock(2),
                          base_lock_digest="sha256:" + "0" * 64, expected_oid=oid1)


def test_malformed_new_lock_rejected_before_write(tmp_path):
    repo = _repo(tmp_path)
    bad = {"schema_version": 1, "source_release_sha": "nope", "patch_series": []}
    with pytest.raises(P.PatchLockError):
        IN.integrate_lock(repo, _REF, bad, base_lock_digest=None, expected_oid=IN._ZERO)
    assert IN.read_lock(repo, _REF) is None  # nothing was written
