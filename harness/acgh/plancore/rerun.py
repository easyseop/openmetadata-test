"""Fail-closed retry table for incomplete and completed runs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:
    new_run_required: bool
    proposal_only: bool
    reusable: tuple[str, ...]


_RETRY_TABLE = {
    "preflight": RetryDecision(True, False, ()),
    "fact_collection": RetryDecision(True, False, ()),
    "document_collection": RetryDecision(True, False, ("verified_document_snapshot",)),
    "proposal_interrupted": RetryDecision(False, True, ("input_lock", "facts", "document_snapshot")),
    "proposal_validation": RetryDecision(False, True, ("input_lock", "facts", "document_snapshot")),
    "fact_recalculation": RetryDecision(True, False, ()),
    "completed": RetryDecision(True, False, ()),
}


def retry_decision(failure_stage: str) -> RetryDecision:
    try:
        return _RETRY_TABLE[failure_stage]
    except KeyError as exc:
        raise ValueError(f"unknown failure stage: {failure_stage}") from exc
