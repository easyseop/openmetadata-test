"""Safe proposal-only continuation for an incomplete planning run."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from acgh.plancore.errors import PlanControlError
from acgh.plancore.markers import bind_run, cleanup_unbound_session
from acgh.plancore.schema import canonical_payload_digest, read_data, validate
from acgh.verdict import canonical_digest


def _verify_immutable_files(run_dir: Path) -> None:
    input_lock = read_data(run_dir / "input-lock.yaml")
    facts = read_data(run_dir / "discovered-facts.json")
    validate("input-lock", input_lock)
    validate("discovered-facts", facts)
    if canonical_payload_digest(input_lock) != input_lock["input_lock_digest"]:
        raise PlanControlError(
            "RESUME_INPUT_LOCK_CHANGED",
            "input-lock changed; start a new run",
        )
    if canonical_payload_digest(facts) != facts["discovered_facts_digest"]:
        raise PlanControlError(
            "RESUME_FACTS_CHANGED",
            "discovered facts changed; start a new run",
        )
    item_digests = {
        item["fact_id"]: canonical_digest(item)
        for item in facts["canonical_payload"]["items"]
    }
    if item_digests != facts["item_digests"]:
        raise PlanControlError(
            "RESUME_FACT_ITEMS_CHANGED",
            "one or more discovered fact items changed; start a new run",
        )


def resume_proposal_run(
    run_dir: str | Path,
    session_marker: str | Path,
    *,
    verify_external_inputs: Callable[[Path], None] | None = None,
) -> dict:
    """Bind a new protected session only to a proposal-validation block."""
    root = Path(run_dir).resolve()
    try:
        result = read_data(root / "validation-result.json")
        validate("result", result)
        if result["verdict"] != "block":
            raise PlanControlError(
                "RUN_NOT_PROPOSAL_REVISABLE",
                "only a proposal validation block can resume in the same run",
                details={"verdict": result["verdict"]},
            )
        _verify_immutable_files(root)
        if verify_external_inputs is not None:
            verify_external_inputs(root)
        pair = bind_run(session_marker, root)
        return {
            "status": "proposal_revision_allowed",
            "run_dir": str(root),
            "session_id": pair.session_id,
            "allowed_path": str(root / "proposal"),
        }
    except Exception:
        cleanup_unbound_session(session_marker)
        raise
