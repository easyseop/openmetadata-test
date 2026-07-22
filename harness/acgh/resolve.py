"""T21 — reapply, maintainer-resolve mode (SRS P0-2, 부칙 A-2.2/2.3).

The counterpart to T20's detect mode. Where detect aborts on conflict, resolve
*keeps* the conflict in a persistent worktree so a human can fix it, then
records the resolution so the next reapply reproduces it.

Two invariants make the result reproducible:

- Lineage stamping (부칙 A-2.2): a plain cherry-pick creates no Source-Commit
  trailer, so this tool stamps EVERY applied commit — conflicted or not — via
  ``git interpret-trailers``: Source-Commit(s), Patch-Revision,
  Application-Record-ID, and (when a conflict was resolved) Resolution-Record-ID.
- Revision policy (부칙 A-2.3): a clean port keeps the same Patch-Revision; a
  resolved conflict bumps it (the resolution is a new, distinct artifact).

On completion the applied commit SHAs feed patchlock.build_application_lock so
the run is captured as a candidate_application_lock.

Note: applied commits live on the worktree's detached HEAD. They share the
repo's object store, so they remain inspectable until GC; promotion (T23) is
what gives them a durable ref. Tests inspect them before finish().
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field

from acgh import gitprim
from acgh import patchlock


class ResolveError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlanEntry:
    sha: str                       # source commit to cherry-pick
    customization_id: str
    revision: int                  # current Patch-Revision for this ID
    source_commits: tuple[str, ...]  # lineage to stamp (1:N allowed)
    application_record_id: str


@dataclass(frozen=True)
class Paused:
    index: int
    sha: str
    customization_id: str
    conflicted_paths: tuple[str, ...]


@dataclass
class ResolveSession:
    repo: str
    worktree_dir: str
    target_ref: str
    plan: tuple[PlanEntry, ...]
    index: int = 0
    applied_commits: list = field(default_factory=list)
    resolution_records: list = field(default_factory=list)
    paused: Paused | None = None
    done: bool = False


def _wt(worktree, *args, check=False, env_editor=False):
    kwargs = {}
    if env_editor:
        import os
        env = dict(os.environ)
        env["GIT_EDITOR"] = "true"
        kwargs["env"] = env
    p = subprocess.run(
        ["git", "-C", worktree, *gitprim._STABLE_CONFIG, *args],
        text=True, capture_output=True, **kwargs,
    )
    if check and p.returncode != 0:
        raise ResolveError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p


def _stamp(worktree, entry: PlanEntry, *, revision, resolution_record_id=None):
    """Amend HEAD's message with lineage trailers; return the new SHA."""
    msg = _wt(worktree, "log", "-1", "--format=%B", check=True).stdout
    trailers = []
    for sc in entry.source_commits:
        trailers += ["--trailer", f"Source-Commit: {sc}"]
    trailers += ["--trailer", f"Patch-Revision: {revision}"]
    trailers += ["--trailer", f"Application-Record-ID: {entry.application_record_id}"]
    if resolution_record_id:
        trailers += ["--trailer", f"Resolution-Record-ID: {resolution_record_id}"]
    new = subprocess.run(
        ["git", "-C", worktree, *gitprim._STABLE_CONFIG, "interpret-trailers", *trailers],
        input=msg, text=True, capture_output=True,
    )
    if new.returncode != 0:
        raise ResolveError(f"interpret-trailers failed: {new.stderr.strip()}")
    _wt(worktree, "commit", "--amend", "-m", new.stdout, check=True)
    return _wt(worktree, "rev-parse", "HEAD", check=True).stdout.strip()


def _advance(session: ResolveSession):
    while session.index < len(session.plan) and session.paused is None:
        entry = session.plan[session.index]
        res = _wt(session.worktree_dir, "cherry-pick", entry.sha)
        if res.returncode == 0:
            sha = _stamp(session.worktree_dir, entry, revision=entry.revision)
            session.applied_commits.append(sha)
            session.index += 1
            continue
        unmerged = _wt(session.worktree_dir, "diff", "--name-only",
                       "--diff-filter=U", "-z").stdout
        conflicted = tuple(p for p in unmerged.split("\x00") if p)
        if conflicted:
            session.paused = Paused(session.index, entry.sha,
                                    entry.customization_id, conflicted)
            return
        # Not a conflict: redundant/empty change -> skip (retirement is T92's job).
        _wt(session.worktree_dir, "cherry-pick", "--abort")
        if "empty" in (res.stderr + res.stdout).lower():
            session.index += 1
            continue
        raise ResolveError(f"cherry-pick failed: {res.stderr.strip()}")
    if session.index >= len(session.plan):
        session.done = True


def start_resolve(repo, target_ref, plan, worktree_dir) -> ResolveSession:
    add = _wt(repo, "worktree", "add", "--detach", worktree_dir, target_ref)
    if add.returncode != 0:
        raise ResolveError(f"worktree add failed: {add.stderr.strip()}")
    session = ResolveSession(repo, worktree_dir, target_ref, tuple(plan))
    _advance(session)
    return session


def resolve_continue(session: ResolveSession, resolution_record_id: str) -> ResolveSession:
    """Continue after the maintainer staged the fix (git add) in the worktree."""
    if session.paused is None:
        raise ResolveError("session is not paused on a conflict")
    entry = session.plan[session.paused.index]
    cont = _wt(session.worktree_dir, "cherry-pick", "--continue", "--no-edit",
               env_editor=True)
    if cont.returncode != 0:
        raise ResolveError(
            f"cherry-pick --continue failed (unresolved conflicts?): "
            f"{cont.stderr.strip()}"
        )
    sha = _stamp(session.worktree_dir, entry, revision=entry.revision + 1,
                 resolution_record_id=resolution_record_id)
    session.applied_commits.append(sha)
    session.resolution_records.append(resolution_record_id)
    session.index = session.paused.index + 1
    session.paused = None
    _advance(session)
    return session


def abort_resolve(session: ResolveSession) -> None:
    _wt(session.worktree_dir, "cherry-pick", "--abort")
    _wt(session.repo, "worktree", "remove", "--force", session.worktree_dir)
    _wt(session.repo, "worktree", "prune")


def finish(session: ResolveSession, source_lock=None):
    """Tear down the worktree; optionally build the candidate application lock."""
    if not session.done:
        raise ResolveError("resolve session is not complete")
    result = None
    if source_lock is not None:
        result = patchlock.build_application_lock(
            source_lock, session.applied_commits, session.resolution_records
        )
    _wt(session.repo, "worktree", "remove", "--force", session.worktree_dir)
    _wt(session.repo, "worktree", "prune")
    return result if result is not None else tuple(session.applied_commits)
