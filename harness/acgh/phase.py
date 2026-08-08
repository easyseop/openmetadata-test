"""Phase bundling — L3 gate execution, L4 aggregation, L5 catalog split, L8 evidence.

This module ORCHESTRATES existing gates; it never reimplements gate judgment
(parity tests are the oracle). Each gate is a ``GateSpec`` whose ``run`` callable
invokes an existing ``acgh`` function / runner and returns a ``GateOutcome``.

L3 — independent execution (설계 §6):
    executed              gate ran and produced one of the 4 verdicts
    skipped_missing_input gate's optional input is absent      -> verdict = None
    blocked_by_preflight  a blocking preflight problem stopped it -> verdict = None
    failed                python exception / timeout / bad JSON / exit-vs-json
                          mismatch -> verdict = analysis_error (NEVER skipped)
    A failing gate does NOT abort the others.

L4 — aggregation (설계 §8):
    overall verdict = verdict.aggregate(...) over EXECUTED, non-advisory gates
    (SEVERITY_RANK.max, never exit-code magnitude). If a REQUIRED+applicable gate
    is not executed -> phase_status=incomplete AND overall=analysis_error.
    Non-applicable gates are excluded from the required set.

L5 — premerge/postmerge catalog split (설계 §5): premerge uses an
    ``active_baseline`` + ``upstream_transition`` run manifest (NOT a CandidateLock)
    and must NOT run T41/T43/T93-exact-scope. postmerge builds/uses a real
    CandidateLock and checks ancestry.

L8 — evidence + approval binding (설계 §9): the canonical result digest covers
    only judgment inputs + per-gate verdict/counts, excluding timestamps/duration/
    display order. Approval binds to that digest; any judgment-input change voids
    it; a human can never turn block/analysis_error into pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from acgh import verdict

# --- execution statuses -----------------------------------------------------
EXECUTED = "executed"
SKIPPED_MISSING_INPUT = "skipped_missing_input"
BLOCKED_BY_PREFLIGHT = "blocked_by_preflight"
FAILED = "failed"
NOT_APPLICABLE = "not_applicable"

# --- phase states -----------------------------------------------------------
COMPLETE = "complete"
INCOMPLETE = "incomplete"

# --- phases -----------------------------------------------------------------
PREMERGE = "premerge"
POSTMERGE = "postmerge"
DEFAULT_GATE_TIMEOUT = 300.0


class MissingInput(Exception):
    """A gate's OPTIONAL input is absent -> skipped_missing_input (not failed)."""


class PhaseError(ValueError):
    """A phase/catalog misuse (e.g. running a non-applicable gate)."""


class GateExecutionError(Exception):
    """A gate could not produce a trustworthy verdict (bad JSON / exit mismatch)."""


@dataclass(frozen=True)
class GateOutcome:
    """What a gate's ``run`` callable returns on success."""
    result: verdict.GateResult
    target_count: int | None = None
    evidence: tuple[str, ...] = ()
    detail: dict = field(default_factory=dict)


@dataclass(frozen=True)
class GateSpec:
    name: str
    run: Callable[[], GateOutcome]
    required: bool = True
    applicable: bool = True
    advisory: bool = False          # excluded from verdict aggregation (C39)
    timeout: float | None = None


@dataclass(frozen=True)
class GateExecution:
    name: str
    execution_status: str
    verdict: str | None
    reasons: tuple[str, ...] = ()
    required: bool = True
    applicable: bool = True
    advisory: bool = False
    target_count: int | None = None
    evidence: tuple[str, ...] = ()
    detail: dict = field(default_factory=dict)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "execution_status": self.execution_status,
            "verdict": self.verdict,
            "reasons": list(self.reasons),
            "required": self.required,
            "applicable": self.applicable,
            "advisory": self.advisory,
            "target_count": self.target_count,
            "evidence": list(self.evidence),
            "detail": self.detail,
        }


# --- L3: independent gate execution -----------------------------------------
def execute_gate(spec: GateSpec, *, preflight_blocked: bool = False) -> GateExecution:
    """Run one gate independently and classify its execution status.

    A raised ``MissingInput`` -> skipped_missing_input (verdict=None).
    ANY other exception (python error, timeout, bad JSON, exit/JSON mismatch)
    -> failed with verdict=analysis_error. This never propagates, so a sibling
    gate keeps running (C52-C57).
    """
    common = dict(
        name=spec.name,
        required=spec.required,
        applicable=spec.applicable,
        advisory=spec.advisory,
    )
    if not spec.applicable:
        return GateExecution(execution_status=NOT_APPLICABLE, verdict=None, **common)
    if preflight_blocked:
        return GateExecution(
            execution_status=BLOCKED_BY_PREFLIGHT,
            verdict=None,
            reasons=("blocked by preflight",),
            **common,
        )
    try:
        outcome = _run_gate_callable(spec)
    except MissingInput as exc:
        return GateExecution(
            execution_status=SKIPPED_MISSING_INPUT,
            verdict=None,
            reasons=(str(exc),) if str(exc) else (),
            **common,
        )
    except Exception as exc:  # noqa: BLE001 - gate failures become analysis_error
        return GateExecution(
            execution_status=FAILED,
            verdict=verdict.ANALYSIS_ERROR,
            reasons=(f"{type(exc).__name__}: {exc}",),
            **common,
        )
    return GateExecution(
        execution_status=EXECUTED,
        verdict=outcome.result.verdict,
        reasons=tuple(outcome.result.reasons),
        target_count=outcome.target_count,
        evidence=tuple(outcome.evidence),
        detail=dict(outcome.detail),
        **common,
    )


def _run_gate_callable(spec: GateSpec) -> GateOutcome:
    """Run a gate with a real wall-clock deadline.

    Phase execution is intentionally sequential.  On POSIX the interval timer
    interrupts the callable itself, so a timed-out gate cannot keep mutating
    state in a background thread.  Unsupported/non-main-thread execution fails
    closed instead of silently ignoring the configured timeout.
    """
    if spec.timeout is None:
        return spec.run()
    if isinstance(spec.timeout, bool) or spec.timeout <= 0:
        raise GateExecutionError(f"invalid timeout for {spec.name}: {spec.timeout!r}")

    import signal
    import threading

    if threading.current_thread() is not threading.main_thread():
        raise GateExecutionError("gate timeout requires execution on the main thread")
    if not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise GateExecutionError("gate timeout is unsupported on this platform")

    def expired(_signum, _frame):
        raise TimeoutError(f"gate {spec.name} exceeded {spec.timeout}s")

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, float(spec.timeout))
    try:
        return spec.run()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


# --- L4: aggregation --------------------------------------------------------
@dataclass(frozen=True)
class PhaseResult:
    phase: str
    executions: tuple[GateExecution, ...]
    overall_verdict: str
    phase_status: str
    exit_code: int
    inputs: dict = field(default_factory=dict)
    run_id: str | None = None
    observational: dict = field(default_factory=dict)

    @property
    def required_not_executed(self) -> tuple[GateExecution, ...]:
        return tuple(
            e for e in self.executions
            if e.required and e.applicable and e.execution_status != EXECUTED
        )

    def canonical_payload(self) -> dict:
        """Judgment-only payload (설계 §9): excludes timestamps/duration/order.

        Gates are sorted by name so display order cannot change the digest.
        """
        return {
            "phase": self.phase,
            "overall_verdict": self.overall_verdict,
            "phase_status": self.phase_status,
            "inputs": self.inputs,
            "gates": [
                {
                    "name": e.name,
                    "verdict": e.verdict,
                    "execution_status": e.execution_status,
                    "required": e.required,
                    "applicable": e.applicable,
                    "advisory": e.advisory,
                    "target_count": e.target_count,
                    "reasons": list(e.reasons),
                    "evidence": list(e.evidence),
                    "detail": e.detail,
                }
                for e in sorted(self.executions, key=lambda x: x.name)
            ],
        }

    def result_digest(self) -> str:
        return verdict.canonical_digest(self.canonical_payload())

    def to_system_json(self) -> dict:
        return {
            "phase": self.phase,
            "phase_status": self.phase_status,
            "overall_verdict": self.overall_verdict,
            "exit_code": self.exit_code,
            "run_id": self.run_id,
            "inputs": self.inputs,
            "gates": [e.to_json() for e in self.executions],
            "result_digest": self.result_digest(),
            "observational_metadata": self.observational,
        }


def aggregate_phase(
    executions,
    *,
    phase: str = PREMERGE,
    inputs: dict | None = None,
    run_id: str | None = None,
    observational: dict | None = None,
) -> PhaseResult:
    """Aggregate executed gate verdicts by SEVERITY_RANK (설계 §8).

    - advisory gates and non-executed gates contribute NO verdict;
    - if any required+applicable gate is not executed -> incomplete +
      analysis_error (a missing required check is never a pass);
    - empty aggregate -> analysis_error (fail-closed, C57).
    """
    executions = tuple(executions)
    required_missing = [
        e for e in executions
        if e.required and e.applicable and e.execution_status != EXECUTED
    ]
    phase_status = INCOMPLETE if required_missing else COMPLETE

    agg_verdicts = [
        e.verdict
        for e in executions
        if e.execution_status == EXECUTED and not e.advisory and e.verdict is not None
    ]
    base_overall = verdict.aggregate(agg_verdicts)  # empty -> analysis_error

    overall = verdict.ANALYSIS_ERROR if phase_status == INCOMPLETE else base_overall
    return PhaseResult(
        phase=phase,
        executions=executions,
        overall_verdict=overall,
        phase_status=phase_status,
        exit_code=verdict.to_exit_code(overall),
        inputs=inputs or {},
        run_id=run_id,
        observational=observational or {},
    )


def run_gates(
    specs,
    *,
    phase: str = PREMERGE,
    preflight_blocked: bool = False,
    inputs: dict | None = None,
    run_id: str | None = None,
    observational: dict | None = None,
) -> PhaseResult:
    """Execute each gate independently, then aggregate (L3 + L4)."""
    specs = tuple(specs)
    names = [s.name for s in specs]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise PhaseError(f"duplicate gates in {phase!r}: {duplicates}")
    for spec in specs:
        assert_gate_applicable(phase, spec.name)
    executions = [execute_gate(s, preflight_blocked=preflight_blocked) for s in specs]
    return aggregate_phase(
        executions,
        phase=phase,
        inputs=inputs,
        run_id=run_id,
        observational=observational,
    )


# --- L5: catalog applicability ----------------------------------------------
# The aggregated + advisory gate names each phase MAY run. T41/T43/exact-scope
# are postmerge-only (설계 §5.1): there is no merged candidate to judge premerge.
PREMERGE_GATES = frozenset({"upgrade-watch", "policy-drift", "structdiff", "watch-suggest"})
PREMERGE_ADVISORY = frozenset({"watch-suggest", "structdiff"})
POSTMERGE_GATES = frozenset({
    "vendor-ancestry", "sensitive-zones", "debt", "exact-scope-history",
    "validate", "source", "contract",
})
# gates that must never run in the wrong phase
POSTMERGE_ONLY = frozenset({"sensitive-zones", "debt", "exact-scope-history"})


def applicable_gates(phase: str) -> frozenset[str]:
    if phase == PREMERGE:
        return PREMERGE_GATES
    if phase == POSTMERGE:
        return POSTMERGE_GATES
    raise PhaseError(f"unknown phase: {phase!r}")


def gate_catalog_digest(specs) -> str:
    """Bind a result to the exact gate catalog metadata used for the run."""
    payload = [
        {
            "name": spec.name,
            "required": spec.required,
            "applicable": spec.applicable,
            "advisory": spec.advisory,
            "timeout": spec.timeout,
        }
        for spec in sorted(specs, key=lambda item: item.name)
    ]
    return verdict.canonical_digest({"gates": payload})


def assert_gate_applicable(phase: str, gate_name: str) -> None:
    """Reject a request to run a non-applicable gate (C36/C37/C38)."""
    if gate_name not in applicable_gates(phase):
        raise PhaseError(
            f"gate {gate_name!r} is not applicable in phase {phase!r} "
            f"(applicable: {sorted(applicable_gates(phase))})"
        )


# --- L5: run manifests + stage-input guards ---------------------------------
def build_premerge_run_manifest(active_baseline: dict, upstream_transition: dict) -> dict:
    """Premerge records active_baseline + upstream_transition, NOT a CandidateLock.

    ``active_baseline`` = {"commit_sha", "tree_sha"} of the approved customization
    baseline; ``upstream_transition`` = {"base_sha", "target_sha"} of the official
    upgrade being previewed (설계 §4).
    """
    for key in ("commit_sha", "tree_sha"):
        if key not in active_baseline:
            raise PhaseError(f"active_baseline missing {key}")
    for key in ("base_sha", "target_sha"):
        if key not in upstream_transition:
            raise PhaseError(f"upstream_transition missing {key}")
    return {
        "phase": PREMERGE,
        "active_baseline": {
            "commit_sha": active_baseline["commit_sha"],
            "tree_sha": active_baseline["tree_sha"],
        },
        "upstream_transition": {
            "base_sha": upstream_transition["base_sha"],
            "target_sha": upstream_transition["target_sha"],
        },
    }


def validate_postmerge_candidate(repo: str, lock) -> None:
    """Reject a candidate that is not a real post-merge upgrade candidate.

    A postmerge candidate MUST descend from the official upstream target
    (설계 §5.2). Passing the pre-upgrade baseline as the postmerge candidate is a
    wrong-stage input (C41); an unrelated candidate is an ancestry error (C40).
    """
    from acgh import gitprim

    target = lock.upstream.target_sha
    candidate = lock.candidate.commit_sha
    if not gitprim.object_exists(repo, target):
        raise PhaseError(f"upstream target object missing: {target}")
    if not gitprim.object_exists(repo, candidate):
        raise PhaseError(f"candidate object missing: {candidate}")
    if candidate == target:
        raise PhaseError(
            "candidate equals the upstream target — no merged customization to judge"
        )
    if not gitprim.is_ancestor(repo, target, candidate):
        raise PhaseError(
            "wrong-stage input: postmerge candidate does not descend from the "
            f"official upstream target (candidate={candidate}, target={target})"
        )


@dataclass(frozen=True)
class OfficialBranch:
    branch: str
    commit_sha: str
    tree_sha: str
    created: bool          # False => already correct (idempotent, C82)


def prepare_official_branch(repo: str, tag_ref: str, branch: str) -> OfficialBranch:
    """Create/verify a local official branch from an upstream tag (C18/C19, C79-C82).

    - tag missing -> PhaseError STOP, branch NOT created (C19);
    - annotated OR lightweight tag -> pins to the underlying COMMIT (C79/C80);
    - existing branch at a different commit -> refuse to overwrite (C81);
    - existing branch already correct -> idempotent success (C82).
    """
    from acgh import binding
    from acgh import gitprim

    try:
        commit = binding.pin(repo, tag_ref)          # ^{commit} handles annotated tags
    except binding.BindingError as exc:
        raise PhaseError(f"official tag not found: {tag_ref} ({exc})") from exc
    tree = gitprim.git(repo, "rev-parse", f"{commit}^{{tree}}").strip()

    existing = subprocess_pin(repo, branch)
    if existing is not None:
        if existing != commit:
            raise PhaseError(
                f"refusing to overwrite existing branch {branch}: "
                f"{existing} != tag commit {commit}"
            )
        return OfficialBranch(branch, commit, tree, created=False)

    gitprim.git(repo, "branch", branch, commit)
    return OfficialBranch(branch, commit, tree, created=True)


def subprocess_pin(repo: str, ref: str) -> str | None:
    """Return the commit SHA a ref resolves to, or None if it does not exist."""
    from acgh import binding

    try:
        return binding.pin(repo, ref)
    except binding.BindingError:
        return None


def assert_target_matches_tag(repo: str, branch_ref: str, expected_tag_sha: str) -> str:
    """STOP if a target branch name resolves to a commit != the official tag (C45)."""
    from acgh import binding

    actual = binding.pin(repo, branch_ref)
    if actual != expected_tag_sha:
        raise PhaseError(
            f"target branch/tag mismatch: {branch_ref} resolves to {actual} "
            f"but the official tag is {expected_tag_sha}"
        )
    return actual


# --- L5: concrete gate catalogs ---------------------------------------------
def build_premerge_catalog(
    repo: str,
    upstream_base: str,
    upstream_target: str,
    active_manifests: dict,
    *,
    layout=None,
    watch_patterns=None,
    candidate_ref: str | None = None,
) -> list[GateSpec]:
    """Wire the premerge gates (설계 §5.1): T42, T93-policy (required) + T51/T52,
    watch-suggest (advisory). NEVER wires T41/T43/T93-exact-scope."""
    from acgh import gitprim
    from acgh import policy_drift
    from acgh import structdiff
    from acgh import upgrade_watch
    from acgh import watch_suggest

    if watch_patterns is None:
        watch_patterns = sorted({
            p
            for m in active_manifests.values()
            for p in m.get("upgrade_watch", {}).get("paths", [])
        })

    def run_upgrade_watch() -> GateOutcome:
        findings = upgrade_watch.evaluate_upgrade_watch(
            repo, upstream_base, upstream_target, active_manifests
        )
        result = upgrade_watch.to_gate_result(findings)
        count = len(gitprim.net_changed_paths(repo, upstream_base, upstream_target))
        return GateOutcome(result, target_count=count)

    def run_policy_drift() -> GateOutcome:
        if layout is None:
            raise MissingInput("repository-layout.yaml not provided")
        result = policy_drift.check_policy_drift(
            repo, upstream_target, watch_patterns, layout, baseline_ref=upstream_base
        )
        return GateOutcome(result, target_count=len(watch_patterns))

    def run_structdiff() -> GateOutcome:
        findings = upgrade_watch.evaluate_upgrade_watch(
            repo, upstream_base, upstream_target, active_manifests
        )
        from pathlib import PurePosixPath

        evidence: list[str] = []
        diffed = 0
        for finding in findings:
            for path in finding.changed_watch_paths:
                if PurePosixPath(path).suffix.lower() not in {".json", ".yaml", ".yml"}:
                    continue
                diff = structdiff.diff_file(repo, upstream_base, upstream_target, path)
                diffed += 1
                evidence.append(f"{path}: {diff.summary()}")
        # advisory: informational structural diff, never a judgment verdict
        return GateOutcome(
            verdict.GateResult("structdiff", verdict.PASS, tuple(evidence)),
            target_count=diffed,
            evidence=tuple(evidence),
        )

    def run_watch_suggest() -> GateOutcome:
        if candidate_ref is None:
            raise MissingInput("candidate ref for watch-suggest not provided")
        suggestions = watch_suggest.suggest_watch_paths(
            repo, upstream_base, upstream_target, candidate_ref, active_manifests
        )
        packet = watch_suggest.review_packet(suggestions)
        return GateOutcome(
            verdict.GateResult("watch-suggest", verdict.PASS, ()),
            target_count=packet["suggestion_count"],
            detail=packet,
        )

    return [
        GateSpec("upgrade-watch", run_upgrade_watch, required=True, timeout=DEFAULT_GATE_TIMEOUT),
        GateSpec("policy-drift", run_policy_drift, required=True, timeout=DEFAULT_GATE_TIMEOUT),
        GateSpec(
            "structdiff", run_structdiff, required=False, advisory=True,
            timeout=DEFAULT_GATE_TIMEOUT,
        ),
        GateSpec(
            "watch-suggest", run_watch_suggest, required=False, advisory=True,
            timeout=DEFAULT_GATE_TIMEOUT,
        ),
    ]


def read_optional_gate_yaml(path, gate: str):
    """Load a per-gate YAML input, DISTINGUISHING missing from malformed (C49).

    Absent file -> MissingInput (gate skips). Present but malformed -> the YAML
    error propagates so the gate becomes failed/analysis_error, never hidden as a
    missing input (a program/parse error must not masquerade as 'no input').
    """
    import yaml
    from pathlib import Path

    if path is None:
        raise MissingInput(f"{gate}: input path not provided")
    p = Path(path)
    if not p.is_file():
        raise MissingInput(f"{gate}: input file not found: {path}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def build_postmerge_catalog(
    repo: str,
    lock,
    active_manifests: dict,
    *,
    zones=None,
    change_intent=...,          # sentinel: ... => not provided (skip T41)
    change_intent_path=None,    # load from file (missing vs malformed, C49)
    thresholds=None,
    conflict_rate=...,          # sentinel: ... => not provided (skip T43)
    upstream_base: str | None = None,
    upstream_target: str | None = None,
) -> list[GateSpec]:
    """Wire the postmerge gates (설계 §5.2). T41/T43 skip (MissingInput) when their
    optional input is absent — never assumed / never a program failure."""
    from acgh import ancestry
    from acgh import debt
    from acgh import gitprim
    from acgh import policy_drift as pd
    from acgh import zones as Z

    target = upstream_target or lock.upstream.target_sha
    candidate = lock.candidate.commit_sha

    def run_ancestry() -> GateOutcome:
        result = ancestry.check_vendor_ancestry(repo, lock)
        return GateOutcome(result)

    def run_sensitive_zones() -> GateOutcome:
        if change_intent_path is not None:
            # missing file -> MissingInput (skip); malformed -> raises -> failed (C49)
            intent = read_optional_gate_yaml(change_intent_path, "sensitive-zones")
        elif change_intent is ... or change_intent is None:
            raise MissingInput("change-intent not provided (T41 skipped)")
        else:
            intent = change_intent
        if zones is None:
            raise MissingInput("sensitive-zones policy not provided")
        candidate_changes = gitprim.net_changed_paths(repo, target, candidate)
        result = Z.check_sensitive_zones(candidate_changes, zones, intent)
        return GateOutcome(result, target_count=len(candidate_changes))

    def run_debt() -> GateOutcome:
        if conflict_rate is ... or conflict_rate is None:
            raise MissingInput("conflict-rate not provided (T43 skipped)")
        if thresholds is None:
            raise GateExecutionError("debt threshold policy not provided")
        metrics = debt.collect_metrics(
            repo, target, candidate, active_manifests, conflict_rate=conflict_rate
        )
        result = debt.evaluate_debt(metrics, thresholds)
        return GateOutcome(result, target_count=metrics.get("core_patch_count"), detail=metrics)

    def run_exact_scope() -> GateOutcome:
        result = pd.check_exact_scope_history(repo, target, candidate, active_manifests)
        return GateOutcome(result)

    return [
        GateSpec("vendor-ancestry", run_ancestry, required=True, timeout=DEFAULT_GATE_TIMEOUT),
        GateSpec("sensitive-zones", run_sensitive_zones, required=True, timeout=DEFAULT_GATE_TIMEOUT),
        GateSpec("debt", run_debt, required=True, timeout=DEFAULT_GATE_TIMEOUT),
        GateSpec("exact-scope-history", run_exact_scope, required=True, timeout=DEFAULT_GATE_TIMEOUT),
    ]


# --- L8: evidence + approval binding ----------------------------------------
class ApprovalError(ValueError):
    """A human approval cannot be honored for this result."""


def build_phase_artifact(result: PhaseResult) -> dict:
    """The persisted phase result: canonical (judgment) payload + digest + views."""
    return {
        "schema_version": 1,
        "canonical_payload": result.canonical_payload(),
        "result_digest": result.result_digest(),
        "system_json": result.to_system_json(),
        "observational_metadata": dict(result.observational),
    }


def evidence_path(base_dir, run_id: str, filename: str = "result.json"):
    """Resolve a per-run evidence path, refusing any run-id that escapes base (C109).

    A run-id containing a path separator, ``..``, or an absolute component is a
    path-traversal attempt and is rejected before any write.
    """
    from pathlib import Path

    if not isinstance(run_id, str) or not run_id.strip():
        raise ApprovalError("run_id must be a non-empty string")
    if "/" in run_id or "\\" in run_id or ".." in run_id or Path(run_id).is_absolute():
        raise ApprovalError(f"unsafe run_id (path traversal): {run_id!r}")
    base = Path(base_dir).resolve()
    target = (base / run_id / filename).resolve()
    if base not in target.parents:
        raise ApprovalError(f"run_id escapes evidence base: {run_id!r}")
    return target


def write_phase_result(result: PhaseResult, out_path, *, overwrite: bool = False) -> str:
    """Atomically persist a phase result; refuse to clobber an existing run (C91).

    Writes to a temp file, fsyncs, then ``os.replace`` — a reader never sees a
    half-written artifact (C93). Reusing a run-id path without ``overwrite`` is a
    hard error so old evidence is never silently overwritten.
    """
    import json
    import os
    from pathlib import Path

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    reservation = out.with_name(f".{out.name}.lock")
    reservation_fd = None
    if not overwrite:
        try:
            reservation_fd = os.open(
                str(reservation), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644
            )
        except FileExistsError as exc:
            raise ApprovalError(
                f"another writer already reserved this evidence path: {out}"
            ) from exc
        if out.exists():
            os.close(reservation_fd)
            reservation_fd = None
            reservation.unlink(missing_ok=True)
            raise ApprovalError(f"refusing to overwrite existing evidence: {out}")

    tmp = out.with_name(f".{out.name}.tmp.{os.getpid()}")
    try:
        artifact = build_phase_artifact(result)
        if verdict.canonical_digest(artifact["canonical_payload"]) != artifact["result_digest"]:
            raise ApprovalError("result_digest self-check failed")
        blob = json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2)
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        try:
            os.write(fd, blob.encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(str(tmp), str(out))  # atomic on POSIX
    finally:
        tmp.unlink(missing_ok=True)
        if reservation_fd is not None:
            os.close(reservation_fd)
            reservation.unlink(missing_ok=True)
    return str(out)


def verify_phase_result(path) -> tuple[bool, str]:
    """Recompute the digest from the stored canonical payload (tamper check, C87)."""
    import json
    from pathlib import Path

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"unreadable/corrupt: {exc}"
    if not isinstance(data, dict) or "canonical_payload" not in data:
        return False, "missing canonical_payload"
    recomputed = verdict.canonical_digest(data["canonical_payload"])
    if recomputed != data.get("result_digest"):
        return False, f"digest mismatch (tampered): stored {data.get('result_digest')} != {recomputed}"
    sysj = data.get("system_json", {})
    if not isinstance(sysj, dict):
        return False, "system_json must be a mapping"
    if sysj.get("result_digest") not in (None, recomputed):
        return False, "system_json result_digest disagrees with canonical digest"
    system_gates = sysj.get("gates")
    if not isinstance(system_gates, list):
        return False, "system_json gates must be a list"
    system_judgment = {
        "phase": sysj.get("phase"),
        "overall_verdict": sysj.get("overall_verdict"),
        "phase_status": sysj.get("phase_status"),
        "inputs": sysj.get("inputs"),
        "gates": sorted(
            [
                {
                    "name": gate.get("name"),
                    "verdict": gate.get("verdict"),
                    "execution_status": gate.get("execution_status"),
                    "required": gate.get("required"),
                    "applicable": gate.get("applicable"),
                    "advisory": gate.get("advisory"),
                    "target_count": gate.get("target_count"),
                    "reasons": gate.get("reasons"),
                    "evidence": gate.get("evidence"),
                    "detail": gate.get("detail"),
                }
                for gate in system_gates
                if isinstance(gate, dict)
            ],
            key=lambda gate: gate["name"] or "",
        ),
    }
    if system_judgment != data["canonical_payload"]:
        return False, "system_json judgment fields disagree with canonical_payload"
    return True, "consistent"


def approval_binds(approval: dict, result: PhaseResult) -> tuple[bool, tuple[str, ...]]:
    """Decide whether a human approval still binds ``result`` (설계 §9).

    An approval names the exact ``result_digest`` and ``phase`` it was granted
    for. Any judgment-input change alters the digest and voids the approval
    (C43/C44/C86/C88/C89). A human may NEVER approve a block/analysis_error into
    a pass (C90): approval is only meaningful when the machine verdict is
    approval (needs sign-off) or pass.
    """
    from acgh.approval import validate_approval_metadata

    reasons: list[str] = list(validate_approval_metadata(approval))
    digest = result.result_digest()
    if approval.get("target_result_digest") != digest:
        reasons.append(
            f"approval digest mismatch: {approval.get('target_result_digest')} != {digest}"
        )
    if approval.get("phase") != result.phase:
        reasons.append(
            f"approval phase mismatch: {approval.get('phase')} != {result.phase}"
        )
    if result.overall_verdict in (verdict.BLOCK, verdict.ANALYSIS_ERROR):
        reasons.append(
            f"machine verdict {result.overall_verdict!r} cannot be approved into pass"
        )
    return (not reasons), tuple(reasons)
