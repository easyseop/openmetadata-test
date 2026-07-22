"""T23 — single-integrator, serialized lock update (SRS 부칙 A-2.5).

Resolution is serialized: maintainers only PROPOSE code; a single integrator is
the only writer of the patch-lock, and every write is compare-and-swap. A stale
base is rejected and must be redone on the fresh lock — two integrators racing
from the same base cannot both win.

Two CAS layers, both must hold:
- logical: the proposed update's ``base_lock_digest`` must equal the digest of
  the CURRENT lock (patchlock.digest()).
- physical: ``git update-ref`` with the expected old OID, so even a digest
  collision or an out-of-band write is caught at the ref level.

The lock is stored as a blob under a ref (e.g. ``refs/bank/patch-lock``); the
ref's OID is the physical CAS token.
"""
from __future__ import annotations

import subprocess

import yaml

from acgh import gitprim
from acgh import patchlock

_ZERO = "0" * 40


class StaleBaseError(RuntimeError):
    """The base the integrator worked from is no longer current — redo."""


def _git(repo, *args, input=None, check=True):
    p = subprocess.run(
        ["git", "-C", repo, *gitprim._STABLE_CONFIG, *args],
        input=input, text=True, capture_output=True,
    )
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p


def read_lock(repo, ref):
    """Return (oid, PatchSourceLock) for the current lock, or None if unset."""
    p = _git(repo, "rev-parse", "--verify", "--quiet", ref, check=False)
    oid = p.stdout.strip()
    if p.returncode != 0 or not oid:
        return None
    content = _git(repo, "cat-file", "-p", oid).stdout
    return oid, patchlock.parse_source_lock(yaml.safe_load(content))


def integrate_lock(repo, ref, new_lock: dict, *, base_lock_digest, expected_oid):
    """CAS-write ``new_lock`` to ``ref``; raise StaleBaseError on a stale base.

    Initial creation: pass ``base_lock_digest=None`` and ``expected_oid`` of 40
    zeros (or None). Subsequent updates must pass the digest and OID the
    integrator started from.
    """
    # Validate the proposed lock is well-formed BEFORE any write.
    patchlock.parse_source_lock(new_lock)

    current = read_lock(repo, ref)
    if current is None:
        if base_lock_digest is not None or (expected_oid not in (None, _ZERO)):
            raise StaleBaseError("lock ref absent but a base was supplied")
        old = _ZERO
    else:
        cur_oid, cur_lock = current
        if base_lock_digest is None:
            raise StaleBaseError("lock exists; base_lock_digest required")
        if cur_lock.digest() != base_lock_digest:
            raise StaleBaseError(
                f"stale base digest: current {cur_lock.digest()} "
                f"!= supplied {base_lock_digest}"
            )
        if expected_oid != cur_oid:
            raise StaleBaseError(
                f"stale base oid: current {cur_oid} != supplied {expected_oid}"
            )
        old = cur_oid

    content = yaml.safe_dump(new_lock, sort_keys=True, allow_unicode=True)
    new_oid = _git(repo, "hash-object", "-w", "--stdin", input=content).stdout.strip()
    upd = _git(repo, "update-ref", ref, new_oid, old, check=False)
    if upd.returncode != 0:
        # Someone moved the ref between our read and write — physical CAS lost.
        raise StaleBaseError(f"update-ref CAS failed: {upd.stderr.strip()}")
    return new_oid
