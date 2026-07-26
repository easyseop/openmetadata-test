from pathlib import Path

import yaml

from acgh import tsc_baseline as T
from acgh import verdict as V


def _line(path="src/a.ts", code="TS1000", message="broken"):
    return f"{path}(1,2): error {code}: {message}\n"


def test_clean_upstream_and_candidate_pass():
    result = T.compare("", "", upstream_exit=0, candidate_exit=0)
    assert result.verdict == V.PASS


def test_identical_nonzero_baseline_requires_approval():
    log = _line()
    result = T.compare(log, log, upstream_exit=2, candidate_exit=2)
    assert result.verdict == V.APPROVAL
    assert "new_diagnostics=0" in result.reasons
    assert result.reasons[-1].startswith("non-zero upstream baseline")


def test_new_candidate_diagnostic_blocks():
    result = T.compare(
        _line(),
        _line() + _line("src/b.ts", "TS2000"),
        upstream_exit=2,
        candidate_exit=2,
    )
    assert result.verdict == V.BLOCK
    assert "new_diagnostics=1" in result.reasons
    assert result.reasons[-1] == "first_new=src/b.ts|TS2000"


def test_increased_multiplicity_blocks():
    result = T.compare(
        _line(),
        _line() + _line(),
        upstream_exit=2,
        candidate_exit=2,
    )
    assert result.verdict == V.BLOCK
    assert "new_diagnostics=1" in result.reasons


def test_removed_diagnostic_still_requires_baseline_approval():
    result = T.compare(
        _line() + _line("src/b.ts", "TS2000"),
        _line(),
        upstream_exit=2,
        candidate_exit=2,
    )
    assert result.verdict == V.APPROVAL
    assert "removed_diagnostics=1" in result.reasons


def test_same_path_and_code_message_substitution_is_reported_for_review():
    result = T.compare(
        _line(message="upstream message"),
        _line(message="candidate message"),
        upstream_exit=2,
        candidate_exit=2,
    )
    assert result.verdict == V.APPROVAL
    assert "new_diagnostics=0" in result.reasons
    assert "new_message_variants=1" in result.reasons
    assert "removed_message_variants=1" in result.reasons
    assert (
        next(
            reason
            for reason in result.reasons
            if reason.startswith("upstream_message_fingerprint=")
        )
        != next(
            reason
            for reason in result.reasons
            if reason.startswith("candidate_message_fingerprint=")
        ).replace("candidate_", "upstream_", 1)
    )


def test_exit_diagnostic_mismatch_is_analysis_error():
    result = T.compare(_line(), _line(), upstream_exit=0, candidate_exit=2)
    assert result.verdict == V.ANALYSIS_ERROR


def test_malformed_or_unsafe_diagnostic_is_analysis_error():
    malformed = "not-a-path(1,2): error TS1000:\n"
    result = T.compare(malformed, _line(), upstream_exit=2, candidate_exit=2)
    assert result.verdict == V.ANALYSIS_ERROR

    unsafe = _line("../outside.ts")
    result = T.compare(unsafe, _line(), upstream_exit=2, candidate_exit=2)
    assert result.verdict == V.ANALYSIS_ERROR


def test_untrusted_process_exit_is_analysis_error():
    result = T.compare("", "", upstream_exit=137, candidate_exit=0)
    assert result.verdict == V.ANALYSIS_ERROR


def test_registered_node22_baseline_evidence_is_honest():
    evidence = yaml.safe_load(
        (
            Path(__file__).parents[1]
            / "registrations"
            / "kb-openmetadata"
            / "ui-typecheck-baseline-evidence.yaml"
        ).read_text(encoding="utf-8")
    )
    comparison = evidence["comparison"]
    assert evidence["upstream"]["sha"] == (
        "afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9"
    )
    assert evidence["candidate"]["sha"] == (
        "b80d24d83124435733d5af05d56515b3a855330e"
    )
    assert comparison["verdict"] == V.APPROVAL
    assert comparison["upstream_diagnostics"] == 396
    assert comparison["candidate_diagnostics"] == 356
    assert comparison["new_diagnostics"] == 0
    assert comparison["removed_diagnostics"] == 40
    assert comparison["new_message_variants"] == 4
    assert comparison["removed_message_variants"] == 44
    assert comparison["upstream_path_code_multiset_fingerprint"].startswith(
        "sha256:"
    )
    assert comparison["candidate_message_fingerprint"].startswith("sha256:")
    review = evidence["message_variant_review"]
    assert len(review["variants"]) == comparison["new_message_variants"]
    assert {
        item["classification"] for item in review["variants"]
    } == {
        "equivalent_type_rendering",
        "equivalent_union_ordering",
        "expected_mapped_type_expansion",
    }
    assert all(item["path"].startswith("src/") for item in review["variants"])
    assert "not designated-owner baseline approval" in review["scope"]
    assert "never emits pass" in evidence["limitation"]
