"""T91 — promote the exact candidate and artifacts that were verified.

The release lock joins source identity, policy/harness/suite identity, test
evidence, images, and Helm content.  Promotion is an equality check over those
immutable identities; rebuilding a nominally equivalent artifact is rejected.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import yaml

from acgh import verdict

_SCHEMA_PATH = Path(__file__).parent / "schema" / "release-lock.schema.json"


class ReleaseError(ValueError):
    """Release-lock construction or validation failed."""


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def validate_release_lock(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ReleaseError("release-lock is not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        loc = lambda error: (
            "/".join(str(part) for part in error.absolute_path) or "<root>"
        )
        raise ReleaseError(
            "schema: "
            + "; ".join(f"{loc(error)}: {error.message}" for error in errors)
        )
    if data["candidate"]["artifact_digest"] not in set(data["images"].values()):
        raise ReleaseError(
            "candidate artifact_digest must be one of the promoted image digests"
        )
    return data


def load_release_lock(path) -> dict:
    return validate_release_lock(
        yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    )


def release_lock_digest(data: dict) -> str:
    return verdict.canonical_digest(validate_release_lock(data))


def _assert_result(result: dict) -> tuple[str, str]:
    try:
        payload = result["canonical_payload"]
        result_digest = result["result_digest"]
        machine_verdict = payload["verdict"]
    except (KeyError, TypeError) as exc:
        raise ReleaseError("source result is malformed") from exc
    if verdict.canonical_digest(payload) != result_digest:
        raise ReleaseError("source result digest mismatch")
    if machine_verdict not in {verdict.PASS, verdict.APPROVAL}:
        raise ReleaseError(
            f"source result is not promotable: {machine_verdict}"
        )
    return result_digest, machine_verdict


def build_release_lock(
    candidate_lock,
    result: dict,
    test_run_set,
    *,
    core_sha: str,
    platform_sha: str,
    policy_digest: str,
    verifier_catalog_digest: str,
    images: dict[str, str],
    helm_digest: str,
    approval_ids=(),
    source_environment: str,
    target_environment: str,
) -> dict:
    """Build a strict lock from already-verified, never rebuilt artifacts."""
    result_digest, machine_verdict = _assert_result(result)
    if test_run_set.candidate_sha != candidate_lock.candidate.commit_sha:
        raise ReleaseError("test run candidate SHA does not match candidate lock")
    if test_run_set.artifact_digest != candidate_lock.candidate.artifact_digest:
        raise ReleaseError(
            "test run artifact digest does not match candidate lock"
        )
    result_inputs = result["canonical_payload"].get("inputs", {})
    if result_inputs.get("candidate_lock_digest") != candidate_lock.digest():
        raise ReleaseError("source result is not bound to candidate lock")
    if (
        result_inputs.get("artifact_digest")
        != candidate_lock.candidate.artifact_digest
    ):
        raise ReleaseError("source result is not bound to candidate artifact")
    if result["canonical_payload"].get("harness_version") != (
        test_run_set.harness_version
    ):
        raise ReleaseError("source result harness version does not match test run")
    if result_inputs.get("verifier_catalog_digest") != verifier_catalog_digest:
        raise ReleaseError("source result is not bound to verifier catalog")
    if result_inputs.get("policy_digest") != policy_digest:
        raise ReleaseError("source result is not bound to policy digest")
    repositories = result_inputs.get("repositories", {})
    if repositories.get("core", {}).get("sha") != core_sha:
        raise ReleaseError("source result is not bound to core SHA")
    if repositories.get("platform", {}).get("sha") != platform_sha:
        raise ReleaseError("source result is not bound to platform SHA")

    data = {
        "schema_version": 1,
        "candidate": {
            "repository": candidate_lock.candidate.repository,
            "commit_sha": candidate_lock.candidate.commit_sha,
            "tree_sha": candidate_lock.candidate.tree_sha,
            "artifact_digest": candidate_lock.candidate.artifact_digest,
            "candidate_lock_digest": candidate_lock.digest(),
        },
        "components": {
            "core_sha": core_sha,
            "platform_sha": platform_sha,
            "policy_digest": policy_digest,
            "harness_version": test_run_set.harness_version,
            "suite_version": test_run_set.suite_version,
            "verifier_catalog_digest": verifier_catalog_digest,
        },
        "source_result_digest": result_digest,
        "source_machine_verdict": machine_verdict,
        "test_run_set_digest": test_run_set.digest(),
        "images": dict(sorted(images.items())),
        "helm_digest": helm_digest,
        "approval_ids": sorted(set(approval_ids)),
        "promotion": {
            "method": "promote-existing",
            "source_environment": source_environment,
            "target_environment": target_environment,
        },
    }
    return validate_release_lock(data)


def check_promotion(
    release_lock,
    *,
    candidate_lock,
    result: dict,
    test_run_set,
    observed_candidate_sha: str,
    observed_images: dict[str, str],
    observed_helm_digest: str,
    rebuilt: bool,
    name: str = "release-digest-promotion",
) -> verdict.GateResult:
    """Verify that deployment promotes the locked objects byte-for-byte."""
    try:
        lock = validate_release_lock(release_lock)
        result_digest, _ = _assert_result(result)
    except ReleaseError as exc:
        return verdict.GateResult(
            name, verdict.ANALYSIS_ERROR, (f"invalid release evidence: {exc}",)
        )

    stale = []
    candidate = lock["candidate"]
    if candidate["candidate_lock_digest"] != candidate_lock.digest():
        stale.append("candidate lock")
    if candidate["commit_sha"] != candidate_lock.candidate.commit_sha:
        stale.append("candidate SHA")
    if candidate["artifact_digest"] != candidate_lock.candidate.artifact_digest:
        stale.append("candidate artifact")
    if lock["source_result_digest"] != result_digest:
        stale.append("source result")
    if lock["test_run_set_digest"] != test_run_set.digest():
        stale.append("test run set")
    if test_run_set.candidate_sha != candidate_lock.candidate.commit_sha:
        stale.append("test run candidate SHA")
    if test_run_set.artifact_digest != candidate_lock.candidate.artifact_digest:
        stale.append("test run artifact")
    components = lock["components"]
    if components["harness_version"] != test_run_set.harness_version:
        stale.append("harness version")
    if components["suite_version"] != test_run_set.suite_version:
        stale.append("suite version")
    result_inputs = result["canonical_payload"].get("inputs", {})
    if components["policy_digest"] != result_inputs.get("policy_digest"):
        stale.append("policy digest")
    if (
        components["verifier_catalog_digest"]
        != result_inputs.get("verifier_catalog_digest")
    ):
        stale.append("verifier catalog")
    repositories = result_inputs.get("repositories", {})
    if components["core_sha"] != repositories.get("core", {}).get("sha"):
        stale.append("core SHA")
    if components["platform_sha"] != repositories.get("platform", {}).get("sha"):
        stale.append("platform SHA")
    if stale:
        return verdict.GateResult(
            name,
            verdict.ANALYSIS_ERROR,
            tuple(f"stale release-lock: {field} mismatch" for field in stale),
        )

    mismatches = []
    if rebuilt:
        mismatches.append("artifact was rebuilt instead of promoted")
    if observed_candidate_sha != candidate["commit_sha"]:
        mismatches.append("deployed candidate SHA differs")
    if observed_images != lock["images"]:
        mismatches.append("deployed image digest set differs")
    if observed_helm_digest != lock["helm_digest"]:
        mismatches.append("deployed Helm digest differs")
    if mismatches:
        return verdict.GateResult(name, verdict.BLOCK, tuple(mismatches))
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"release_lock_digest={release_lock_digest(lock)}",
            "promotion_method=promote-existing",
            "candidate/image/helm digests match",
        ),
    )
