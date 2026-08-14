"""Deterministic plan preflight and fact collection."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from acgh import binding, gitprim
from acgh.verdict import canonical_digest
from acgh.plancore.errors import PlanControlError
from acgh.plancore.markers import (
    bind_run,
    cleanup_pair,
    cleanup_unbound_session,
    load_session_marker,
)
from acgh.plancore.paths import directory_digest, list_dirty_paths
from acgh.plancore.schema import atomic_write, read_data, validate


class PlanAdapter(Protocol):
    name: str

    def validate_request(self, request: dict) -> dict: ...
    def resolve_registration_path(self, request: dict, checker_repo: Path) -> Path | None: ...
    def catalog_paths(self, checker_repo: Path) -> list[Path]: ...
    def collect_documents(self, request: dict, run_dir: Path) -> dict: ...
    def collect_facts(
        self,
        request: dict,
        locked_refs: dict[str, str],
        registration_path: Path | None,
        document_sources: dict,
    ) -> list[dict]: ...


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _repository_id(repo: Path, supplied: str | None) -> str:
    if supplied:
        return supplied
    process = subprocess.run(
        ["git", "-C", str(repo), "config", "--get", "remote.origin.url"],
        text=True,
        capture_output=True,
        check=False,
    )
    value = process.stdout.strip()
    if not value:
        raise PlanControlError(
            "REPOSITORY_ID_REQUIRED",
            "repository has no origin URL; supply repository_ids explicitly",
            details={"repository": str(repo)},
        )
    return value


def _checker_catalog_digest(paths: list[Path]) -> str:
    items = []
    for path in sorted(paths, key=lambda item: item.as_posix()):
        items.append({"name": path.name, "digest": directory_digest(path)})
    return canonical_digest({"catalog": items})


def _request_payload(request: dict, repository_ids: dict[str, str]) -> dict:
    excluded = {"repositories", "registration_path"}
    payload = {key: value for key, value in request.items() if key not in excluded}
    payload["repository_ids"] = repository_ids
    return payload


def _intent_summary(request: dict, locked_refs: dict[str, str]) -> dict:
    """Return the small request summary a human must confirm before planning."""
    return {
        "mode": request["mode"],
        "run_id": request["run_id"],
        "refs": {
            role: {
                "requested": request["refs"][role],
                "pinned_commit_sha": locked_refs[role],
            }
            for role in sorted(request.get("refs") or {})
        },
        "versions": request.get("versions") or {},
        "deployment_method": request.get("deployment_method"),
        "official_documents": request.get("official_documents") or [],
        "customization_id": request.get("customization_id"),
        "requirement": request.get("requirement"),
        "change_path": request.get("change_path"),
        "hop_policy": request.get("hop_policy"),
        "owner": request.get("owner"),
    }


def _build_facts(mode: str, facts: list[dict]) -> dict:
    normalized = []
    for index, item in enumerate(facts):
        value = dict(item)
        value["evidence_ref"] = (
            f"discovered-facts.json#/canonical_payload/items/{index}/value"
        )
        normalized.append(value)
    fact_ids = [item["fact_id"] for item in normalized]
    if len(fact_ids) != len(set(fact_ids)):
        raise PlanControlError("FACT_ID_DUPLICATE", "fact ids must be unique")
    item_digests = {item["fact_id"]: canonical_digest(item) for item in normalized}
    canonical_payload = {"mode": mode, "items": normalized}
    return {
        "schema_version": 1,
        "canonical_payload": canonical_payload,
        "observational_metadata": {"collected_at": _utc_now()},
        "item_digests": item_digests,
        "discovered_facts_digest": canonical_digest(canonical_payload),
    }


def collect_state(
    request: dict,
    adapter: PlanAdapter,
    *,
    run_dir: Path,
    collect_documents: bool,
    locked_refs_override: dict[str, str] | None = None,
) -> tuple[dict, dict, dict]:
    validate("run-request", request)
    adapter_state = adapter.validate_request(request)
    product_repo = Path(request["repositories"]["product"]).resolve()
    checker_repo = Path(request["repositories"]["checker"]).resolve()
    for label, repo in (("product", product_repo), ("checker", checker_repo)):
        if not (repo / ".git").exists() and not (repo / "HEAD").exists():
            raise PlanControlError(
                "REPOSITORY_INVALID",
                f"{label} repository is not a Git worktree",
                details={"repository": str(repo)},
            )

    supplied_ids = request.get("repository_ids") or {}
    repository_ids = {
        "product": _repository_id(product_repo, supplied_ids.get("product")),
        "checker": _repository_id(checker_repo, supplied_ids.get("checker")),
    }
    if locked_refs_override is not None:
        locked_refs = dict(locked_refs_override)
    else:
        locked_refs = {}
        missing_refs = []
        for role, ref in request["refs"].items():
            try:
                locked_refs[role] = binding.pin(str(product_repo), ref)
            except binding.BindingError:
                missing_refs.append({"role": role, "ref": ref})
        if missing_refs:
            raise PlanControlError(
                "REFS_UNAVAILABLE",
                "one or more required refs cannot be resolved",
                details={
                    "missing_refs": missing_refs,
                    "next_action": "fetch or provide the exact required commit objects, then start a new run",
                },
            )
    for role, sha in locked_refs.items():
        if not gitprim.object_exists(str(product_repo), sha):
            raise PlanControlError(
                "PINNED_COMMIT_UNAVAILABLE",
                "a pinned commit is no longer available locally",
                details={"role": role, "sha": sha},
            )
    product_trees = {
        role: gitprim.git(str(product_repo), "rev-parse", f"{sha}^{{tree}}").strip()
        for role, sha in locked_refs.items()
    }
    checker_sha = binding.pin(str(checker_repo), "HEAD")
    checker_tree = gitprim.git(
        str(checker_repo), "rev-parse", f"{checker_sha}^{{tree}}"
    ).strip()
    registration_path = adapter.resolve_registration_path(request, checker_repo)
    registration_exists = bool(registration_path and registration_path.is_dir())
    if request["mode"] == "initial" and registration_exists:
        raise PlanControlError(
            "ACTIVE_REGISTRATION_EXISTS",
            "initial mode does not overwrite an existing active registration",
            details={"registration_path": str(registration_path)},
        )
    if request["mode"] in {"feature", "change", "upgrade"} and not registration_exists:
        raise PlanControlError(
            "ACTIVE_REGISTRATION_MISSING",
            "this mode requires an existing active registration",
            details={"registration_path": str(registration_path) if registration_path else None},
        )
    registration_digest = directory_digest(registration_path, allow_absent=True) if registration_path else canonical_digest({"state": "absent"})
    request_digest = canonical_digest(_request_payload(request, repository_ids))
    version_relation = adapter_state.get("version_relation", "not_applicable")
    if collect_documents:
        document_sources = adapter.collect_documents(request, run_dir)
    else:
        source_path = run_dir / "official-doc-sources.yaml"
        document_sources = (
            read_data(source_path)
            if source_path.is_file()
            else {"schema_version": 1, "documents": []}
        )
    canonical_payload = {
        "run_id": request["run_id"],
        "mode": request["mode"],
        "request_digest": request_digest,
        "repositories": {
            "product": {
                "repository_id": repository_ids["product"],
                "commit_shas": locked_refs,
                "tree_shas": product_trees,
            },
            "checker": {
                "repository_id": repository_ids["checker"],
                "commit_shas": {"head": checker_sha},
                "tree_shas": {"head": checker_tree},
            },
        },
        "registration": {
            "exists": registration_exists,
            "state_digest": registration_digest,
        },
        "checker_catalog_digest": _checker_catalog_digest(
            adapter.catalog_paths(checker_repo)
        ),
        "version_relation": version_relation,
    }
    if request["mode"] == "upgrade":
        canonical_payload["official_doc_sources_digest"] = canonical_digest(
            document_sources
        )
    if request.get("change_path"):
        canonical_payload["change_path"] = request["change_path"]
    if request.get("deployment_method"):
        canonical_payload["deployment_method"] = request["deployment_method"]
    input_lock = {
        "schema_version": 1,
        "canonical_payload": canonical_payload,
        "observational_metadata": {
            "repository_paths": {
                "product": str(product_repo),
                "checker": str(checker_repo),
            },
            "registration_path": str(registration_path) if registration_path else None,
            "collected_at": _utc_now(),
        },
        "input_lock_digest": canonical_digest(canonical_payload),
    }
    validate("input-lock", input_lock)

    facts = _build_facts(
        request["mode"],
        adapter.collect_facts(
            request, locked_refs, registration_path, document_sources
        ),
    )
    validate("discovered-facts", facts)
    return input_lock, facts, document_sources


def run_preflight(
    request_path: str | Path,
    run_dir: str | Path,
    adapter: PlanAdapter,
    *,
    session_marker: str | Path,
) -> dict:
    destination = Path(run_dir).resolve()
    session: dict | None = None
    try:
        request = read_data(request_path)
        validate("run-request", request)
        if destination.exists():
            raise PlanControlError(
                "RUN_DIRECTORY_EXISTS",
                "preflight requires a new run directory",
                details={"run_dir": str(destination)},
            )
        session = load_session_marker(session_marker)
        dirty = {
            name: list_dirty_paths(path)
            for name, path in request["repositories"].items()
        }
        if any(dirty.values()):
            raise PlanControlError(
                "WORKTREE_DIRTY",
                "planning starts only from clean repositories and never cleans them",
                details={"dirty_paths": dirty},
            )
        destination.mkdir(parents=True)
        (destination / "proposal").mkdir()
        (destination / "validation-attempts").mkdir()
        input_lock, facts, document_sources = collect_state(
            request,
            adapter,
            run_dir=destination,
            collect_documents=True,
            locked_refs_override=None,
        )
        atomic_write(destination / "run-request.yaml", request)
        atomic_write(destination / "input-lock.yaml", input_lock)
        atomic_write(destination / "discovered-facts.json", facts)
        if request["mode"] != "upgrade":
            if (destination / "official-doc-sources.yaml").exists():
                (destination / "official-doc-sources.yaml").unlink()
        pair = bind_run(session_marker, destination)
        return {
            "status": "ready_for_proposal",
            "run_dir": str(destination),
            "input_lock_digest": input_lock["input_lock_digest"],
            "request_digest": input_lock["canonical_payload"]["request_digest"],
            "discovered_facts_digest": facts["discovered_facts_digest"],
            "intent_review_required": True,
            "intent_summary": _intent_summary(
                request,
                input_lock["canonical_payload"]["repositories"]["product"][
                    "commit_shas"
                ],
            ),
            "operator_action": (
                "위 요청 내용과 고정된 commit SHA를 사람이 확인한 뒤 "
                "input_lock_digest를 LLM이 수정할 수 없는 곳에 보관하세요."
            ),
            "session_id": pair.session_id,
        }
    except Exception as exc:
        failure = (
            exc
            if isinstance(exc, PlanControlError)
            else PlanControlError("PREFLIGHT_FAILED", str(exc))
        )
        # Never write into a pre-existing run. It may be valid evidence owned
        # by a different or completed session.
        if failure.code != "RUN_DIRECTORY_EXISTS":
            destination.mkdir(parents=True, exist_ok=True)
            atomic_write(
                destination / "preflight-result.json",
                {"status": "analysis_error", **failure.as_dict()},
            )
        if session is None:
            try:
                session = load_session_marker(session_marker)
            except PlanControlError:
                session = None
        if session is not None:
            bound_run = session.get("run_dir")
            if bound_run is None:
                cleanup_unbound_session(session_marker)
            elif Path(bound_run).resolve() == destination:
                pair = type("FailedPair", (), {
                    "session_marker": Path(session_marker).resolve(),
                    "run_marker": destination / ".plan-active",
                    "session_id": session["session_id"],
                    "project_key": session["project_key"],
                })()
                cleanup_pair(pair)
        raise failure from exc
