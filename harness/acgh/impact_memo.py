"""T80/T81 — advisory, evidence-backed upgrade Impact Memo.

This module validates already-produced analysis; it does not invoke a model,
shell, Git writer, pull-request API, or network client.  The strict schema has
no verdict or deployment-action field.  Facts and inferences are separate and
every claim must carry at least one snapshot-bound evidence reference.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "impact-memo.schema.json"
_BANNED_CONCLUSIONS = ("영향 없음", "no impact")


class ImpactMemoError(ValueError):
    """Impact Memo is malformed, ungrounded, or overclaims certainty."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def validate_impact_memo(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ImpactMemoError("impact memo is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise ImpactMemoError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )

    strings = []
    strings.extend(item["claim"] for item in data["facts"])
    strings.extend(item["claim"] for item in data["inferences"])
    strings.extend(data["unknowns"])
    for text in strings:
        lowered = text.casefold()
        for banned in _BANNED_CONCLUSIONS:
            if banned.casefold() in lowered:
                raise ImpactMemoError(
                    f"forbidden certainty phrase {banned!r}; "
                    "use '확인된 후보 없음' and list unknowns"
                )

    snapshot = data["snapshot_sha"]
    for section in ("facts", "inferences"):
        for item in data[section]:
            for evidence in item["evidence"]:
                if evidence["snapshot_sha"] != snapshot:
                    raise ImpactMemoError(
                        f"{section} evidence snapshot does not match memo snapshot"
                    )
    return data


def load_impact_memo(path) -> dict:
    return validate_impact_memo(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def impact_memo_digest(data: dict) -> str:
    return verdict.canonical_digest(validate_impact_memo(data))


def to_evidence_suggestion(
    data: dict,
    *,
    gate: str = "llm-impact-memo",
) -> dict:
    """Convert a memo to the non-authoritative T14 card field."""
    memo = validate_impact_memo(data)
    ids = sorted(memo["affected_customization_ids"])
    candidates = ",".join(ids) if ids else "확인된 후보 없음"
    summary = (
        f"memo_digest={impact_memo_digest(memo)}; "
        f"snapshot={memo['snapshot_sha']}; "
        f"model={memo['model_id']}; prompt={memo['prompt_version']}; "
        f"affected_candidates={candidates}; "
        f"facts={len(memo['facts'])}; "
        f"inferences={len(memo['inferences'])}; "
        f"unknowns={len(memo['unknowns'])}"
    )
    severity = "high" if ids else "info"
    return {"gate": gate, "memo": summary, "severity_hint": severity}


def assess_memo_quality(
    data: dict,
    *,
    known_impacted_ids,
    reviewer_adopted_ids=(),
) -> dict:
    """T81 release-local quality metrics for deciding whether Wiki scale helps."""
    memo = validate_impact_memo(data)
    predicted = set(memo["affected_customization_ids"])
    known = set(known_impacted_ids)
    adopted = set(reviewer_adopted_ids)
    true_positive = predicted & known
    false_positive = predicted - known
    return {
        "known_impacted_count": len(known),
        "predicted_count": len(predicted),
        "recall": (
            len(true_positive) / len(known) if known else None
        ),
        "false_positive_rate": (
            len(false_positive) / len(predicted) if predicted else 0.0
        ),
        "adoption_rate": (
            len(predicted & adopted) / len(predicted) if predicted else 0.0
        ),
        "ungrounded_claim_rate": 0.0,
    }
