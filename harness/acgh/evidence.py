"""T14 — change-evidence card: aggregate gates + evidence, keep advice separate.

One candidate produces one card that a human can read: every gate's verdict,
the reasons and structured evidence behind it, and — in clearly separated
fields — the human approvals and the LLM's advisory memos.

The load-bearing property (G4 / REQ-GZ-04 / §7): ``machine_verdict`` and
``result_digest`` are copied VERBATIM from the immutable acgh-result. Neither
``approvals`` (human) nor ``llm_suggestions`` (advisory) can move them — the
schema even forbids a ``verdict`` field on an LLM suggestion, so the model can
hint but never decide. Adding advice to a card leaves the machine judgment
byte-identical.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "change-evidence.schema.json"


class EvidenceError(ValueError):
    """Evidence card fails structural or consistency validation."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def build_evidence_card(
    result: dict,
    *,
    evidence_by_gate: dict | None = None,
    approvals: list | None = None,
    llm_suggestions: list | None = None,
) -> dict:
    """Assemble a change-evidence card from an acgh-result (verdict.build_result).

    ``evidence_by_gate`` maps gate name -> list of evidence strings. Approvals
    and llm_suggestions are attached to their own fields, never merged into the
    gate verdicts.
    """
    payload = result["canonical_payload"]
    evidence_by_gate = evidence_by_gate or {}
    card = {
        "schema_version": 1,
        "machine_verdict": payload["verdict"],
        "result_digest": result["result_digest"],
        "inputs": payload["inputs"],
        "harness_version": payload["harness_version"],
        "gates": [
            {
                "name": g["name"],
                "verdict": g["verdict"],
                "reasons": list(g["reasons"]),
                "evidence": list(evidence_by_gate.get(g["name"], [])),
            }
            for g in payload["gates"]
        ],
        "approvals": list(approvals or []),
        "llm_suggestions": list(llm_suggestions or []),
        "observational_metadata": dict(result.get("observational_metadata", {})),
    }
    validate_evidence_card(card)
    return card


def validate_evidence_card(card: dict) -> dict:
    """Structural + consistency validation.

    Beyond the schema: machine_verdict must equal the severity-rank aggregate of
    the card's own gate verdicts, so a card can never present a milder headline
    than its gates justify (P0-3/P0-4 carried into the human artifact).
    """
    errs = sorted(
        _schema_validator().iter_errors(card),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    if errs:
        loc = lambda e: "/".join(str(p) for p in e.absolute_path) or "<root>"
        raise EvidenceError(
            "schema: " + "; ".join(f"{loc(e)}: {e.message}" for e in errs)
        )
    agg = verdict.aggregate([g["verdict"] for g in card["gates"]])
    if agg != card["machine_verdict"]:
        raise EvidenceError(
            f"machine_verdict {card['machine_verdict']!r} != aggregate of gates {agg!r}"
        )
    return card
