from __future__ import annotations

import os
import subprocess
from copy import deepcopy

from acgh import layout
from acgh import shared_code
from acgh import structural_review as S
from acgh import zones as zones_module


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo, message):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", message)
    return _git(repo, "rev-parse", "HEAD")


def _topology(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "both.txt").write_text("base\n")
    (repo / "deleted.txt").write_text("official-v1\n")
    (repo / "old.ts").write_text("export const BANK_TOKEN = 1;\n")
    (repo / "old-comment.ts").write_text("export const COMMENT_ONLY = 1;\n")
    (repo / "partial.ts").write_text(
        "export const REQUIRED_ONE = 1;\nexport const REQUIRED_TWO = 2;\n"
    )
    (repo / "binary.bin").write_bytes(b"base\x00value")
    base = _commit(repo, "merge base")

    _git(repo, "switch", "-qc", "custom", base)
    (repo / "both.txt").write_text("custom\n")
    (repo / "custom-only.txt").write_text("bank only\n")
    (repo / "partial.ts").write_text(
        "export const REQUIRED_ONE = 10;\nexport const REQUIRED_TWO = 20;\n"
    )
    custom = _commit(repo, "custom")

    _git(repo, "switch", "-qc", "target", base)
    (repo / "both.txt").write_text("target\n")
    (repo / "deleted.txt").unlink()
    (repo / "old.ts").unlink()
    (repo / "old-comment.ts").unlink()
    (repo / "new.ts").write_text("export const BANK_TOKEN = 1;\n")
    (repo / "commented.ts").write_text("// export const COMMENT_ONLY = 1;\n")
    (repo / "partial.ts").write_text(
        "export const REQUIRED_ONE = 3;\nexport const upstream = true;\n"
    )
    (repo / "binary.bin").write_bytes(b"target\x00value")
    target = _commit(repo, "target")

    _git(repo, "switch", "-qc", "candidate", target)
    (repo / "deleted.txt").write_text("official-v1\n")
    (repo / "candidate-only.txt").write_text("manual resolution\n")
    candidate = _commit(repo, "candidate")
    return repo, base, target, custom, candidate


def _by_path(review):
    return {item["path"]: item for item in review["findings"]}


def test_review_surface_classifies_loss_suspects_without_exclusion(tmp_path):
    repo, base, target, custom, candidate = _topology(tmp_path)
    manifests = {
        "BANK-OM-004": {
            "implementation": {"changed_paths": ["both.txt", "custom-only.txt"]},
            "upgrade_watch": {"paths": ["deleted.txt"]},
        }
    }
    review = S.build_review(
        str(repo), base, target, custom, candidate, manifests
    )
    findings = _by_path(review)

    assert findings["both.txt"]["change_origin"] == S.BOTH_CHANGED_PARENTS_DIVERGE
    assert findings["both.txt"]["result_relation"] == S.EQUALS_TARGET
    assert S.CUSTOM_LOSS_SUSPECT in findings["both.txt"]["risk_flags"]

    assert findings["custom-only.txt"]["change_origin"] == S.CUSTOM_ONLY
    assert findings["custom-only.txt"]["result_relation"] == S.EQUALS_TARGET
    assert S.CUSTOM_LOSS_SUSPECT in findings["custom-only.txt"]["risk_flags"]

    assert findings["deleted.txt"]["change_origin"] == S.TARGET_ONLY
    assert findings["deleted.txt"]["result_relation"] == S.EQUALS_CUSTOM
    assert S.OFFICIAL_LOSS_SUSPECT in findings["deleted.txt"]["risk_flags"]

    assert findings["candidate-only.txt"]["change_origin"] == S.NEITHER_PARENT_CHANGED
    assert findings["candidate-only.txt"]["result_relation"] == S.DIFFERS_FROM_BOTH
    assert "BINARY" in findings["binary.bin"]["diagnostic_flags"]
    assert review["review_surface_paths"] == sorted(
        review["review_surface_paths"], key=lambda path: path.encode("utf-8")
    )


def test_rename_diagnostics_do_not_change_canonical_review(tmp_path, monkeypatch):
    repo, base, target, custom, candidate = _topology(tmp_path)
    _git(repo, "config", "diff.renameLimit", "1")
    monkeypatch.setattr(S.gitprim, "git_version", lambda: "git version first")
    first = S.build_review(
        str(repo), base, target, custom, candidate, {}, diagnostic_threshold=50
    )
    _git(repo, "config", "diff.renameLimit", "20000")
    monkeypatch.setattr(S.gitprim, "git_version", lambda: "git version second")
    second = S.build_review(
        str(repo), base, target, custom, candidate, {}, diagnostic_threshold=90
    )

    assert first["review_digest"] == second["review_digest"]
    assert [
        {key: value for key, value in item.items() if key != "diagnostic_flags"}
        for item in first["findings"]
    ] == [
        {key: value for key, value in item.items() if key != "diagnostic_flags"}
        for item in second["findings"]
    ]
    assert first["rename_diagnostics"] != second["rename_diagnostics"]
    assert all("POSSIBLE_RENAME" not in item["risk_flags"] for item in first["findings"])
    assert first["canonical_policy"] == "rename_detection=disabled (--no-renames)"
    assert all(
        item["policy"].startswith("diagnostic(-M -C")
        for item in first["rename_diagnostics"]
    )
    S.verify_review(str(repo), first, {})


def test_verify_review_does_not_recompute_diagnostics(tmp_path, monkeypatch):
    repo, base, target, custom, candidate = _topology(tmp_path)
    review = S.build_review(str(repo), base, target, custom, candidate, {})

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("diagnostic rename must not run during canonical verification")

    monkeypatch.setattr(S.gitprim, "diagnostic_rename_report", fail_if_called)
    S.verify_review(str(repo), review, {})


def test_verify_review_rejects_canonical_and_diagnostic_tampering(tmp_path):
    repo, base, target, custom, candidate = _topology(tmp_path)
    review = S.build_review(str(repo), base, target, custom, candidate, {})

    canonical_tamper = deepcopy(review)
    canonical_tamper["findings"][0]["risk_flags"].append("FORGED")
    try:
        S.verify_review(str(repo), canonical_tamper, {})
    except S.StructuralReviewError as exc:
        assert "canonical digest mismatch" in str(exc)
    else:
        raise AssertionError("canonical evidence tamper must be rejected")

    diagnostic_tamper = deepcopy(review)
    diagnostic_tamper["findings"][0]["diagnostic_flags"].append("FORGED")
    try:
        S.verify_review(str(repo), diagnostic_tamper, {})
    except S.StructuralReviewError as exc:
        assert "diagnostics digest mismatch" in str(exc)
    else:
        raise AssertionError("diagnostic evidence tamper must be rejected")


def test_manifest_watch_and_sensitive_zone_watch_are_distinct(tmp_path):
    repo, base, target, custom, candidate = _topology(tmp_path)
    manifests = {
        "BANK-OM-004": {
            "upgrade_watch": {"paths": ["both.txt"]},
        }
    }
    zones = zones_module.Zones({
        zones_module.WATCHED: layout.make_spec(["both.txt"]),
    })
    finding = _by_path(S.build_review(
        str(repo), base, target, custom, candidate, manifests, zones=zones
    ))["both.txt"]

    assert "MANIFEST_WATCHED" in finding["risk_flags"]
    assert "WATCHED" in finding["risk_flags"]


def test_relocation_is_approval_but_comment_only_and_partial_loss_block(tmp_path):
    repo, base, target, custom, candidate = _topology(tmp_path)
    review = S.build_review(str(repo), base, target, custom, candidate, {})
    catalog = shared_code.parse_catalog({
        "schema_version": 1,
        "definitions": [
            {
                "path": "old.ts",
                "customization_id": "BANK-OM-004",
                "assertions": [{
                    "id": "moved",
                    "matcher": "code_fragment",
                    "fragment": "export const BANK_TOKEN = 1;",
                }],
            },
            {
                "path": "old-comment.ts",
                "customization_id": "BANK-OM-004",
                "assertions": [{
                    "id": "comment-only",
                    "matcher": "code_fragment",
                    "fragment": "export const COMMENT_ONLY = 1;",
                }],
            },
            {
                "path": "partial.ts",
                "customization_id": "BANK-OM-004",
                "assertions": [
                    {
                        "id": "one",
                        "matcher": "code_fragment",
                        "fragment": "export const REQUIRED_ONE = 10;",
                    },
                    {
                        "id": "two",
                        "matcher": "code_fragment",
                        "fragment": "export const REQUIRED_TWO = 20;",
                    },
                ],
            },
        ],
    })
    relocation = S.find_relocations(
        str(repo), candidate, catalog, review["review_surface_paths"]
    )
    by_id = {item["definition_id"]: item for item in relocation["findings"]}

    moved = by_id["BANK-OM-004:old.ts"]
    assert moved["verdict"] == "approval"
    assert [item["path"] for item in moved["candidates"]] == ["new.ts"]

    comment_only = by_id["BANK-OM-004:old-comment.ts"]
    assert comment_only["verdict"] == "block"
    assert comment_only["candidate_count"] == 0

    partial = by_id["BANK-OM-004:partial.ts"]
    assert partial["verdict"] == "block"
    assert relocation["verdict"] == "block"
    gate = S.to_gate_result(review, relocation)
    assert gate.verdict == "block"


def test_differs_from_both_is_not_a_safe_bucket_but_needs_independent_evidence():
    manual_only = {
        "review_digest": "sha256:" + "0" * 64,
        "review_surface_paths": ["manual.ts"],
        "findings": [{
            "path": "manual.ts",
            "change_origin": S.BOTH_CHANGED_PARENTS_DIVERGE,
            "result_relation": S.DIFFERS_FROM_BOTH,
            "risk_flags": [],
        }],
    }
    no_shared_failures = {
        "verdict": "pass",
        "finding_count": 0,
        "findings": [],
    }
    result = S.to_gate_result(manual_only, no_shared_failures)
    assert result.verdict == "pass"  # no loss evidence in this synthetic payload

    manual_only["findings"][0]["risk_flags"] = [S.CUSTOM_LOSS_SUSPECT]
    result = S.to_gate_result(manual_only, no_shared_failures)
    assert result.verdict == "approval"


def test_candidate_reverted_to_merge_base_is_flagged(tmp_path):
    repo, base, target, custom, _candidate = _topology(tmp_path)
    review = S.build_review(str(repo), base, target, custom, base, {})
    finding = _by_path(review)["both.txt"]

    assert finding["change_origin"] == S.BOTH_CHANGED_PARENTS_DIVERGE
    assert finding["result_relation"] == S.DIFFERS_FROM_BOTH
    assert set(finding["risk_flags"]) >= {
        S.CUSTOM_LOSS_SUSPECT,
        S.OFFICIAL_LOSS_SUSPECT,
        "REVERTED_TO_MERGE_BASE",
    }
    gate = S.to_gate_result(
        review, {"verdict": "pass", "finding_count": 0, "findings": []}
    )
    assert gate.verdict == "approval"


def test_deleted_then_recreated_identical_blob_is_flagged(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "shared.txt").write_text("base\n")
    base = _commit(repo, "base")

    _git(repo, "switch", "-qc", "target", base)
    (repo / "shared.txt").unlink()
    target = _commit(repo, "target deletes")

    _git(repo, "switch", "-qc", "custom", base)
    (repo / "shared.txt").write_text("custom\n")
    custom = _commit(repo, "custom changes")

    _git(repo, "switch", "-qc", "candidate", target)
    (repo / "shared.txt").write_text("base\n")
    candidate = _commit(repo, "candidate recreates base")

    finding = _by_path(
        S.build_review(str(repo), base, target, custom, candidate, {})
    )["shared.txt"]
    assert set(finding["risk_flags"]) >= {
        S.CUSTOM_LOSS_SUSPECT,
        S.OFFICIAL_LOSS_SUSPECT,
        "REVERTED_TO_MERGE_BASE",
    }


def test_type_change_symlink_submodule_and_mode_states_are_preserved(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@example.com")
    for name in ("linkish", "subish", "executable.sh"):
        (repo / name).write_text("base\n")
    base = _commit(repo, "base")

    (repo / "linkish").unlink()
    os.symlink("target.txt", repo / "linkish")
    (repo / "subish").unlink()
    _git(repo, "add", "linkish")
    _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{base},subish")
    os.chmod(repo / "executable.sh", 0o755)
    _git(repo, "add", "executable.sh")
    _git(repo, "commit", "-qm", "type and mode changes")
    target = _git(repo, "rev-parse", "HEAD")

    findings = _by_path(S.build_review(str(repo), base, target, base, target, {}))
    assert findings["linkish"]["statuses"]["base_to_target"] == "T"
    assert findings["subish"]["statuses"]["base_to_target"] == "T"
    assert findings["executable.sh"]["statuses"]["base_to_target"] == "M"
    assert findings["linkish"]["states"]["target"].startswith("120000:blob:")
    assert findings["subish"]["states"]["target"].startswith("160000:commit:")
    assert findings["executable.sh"]["states"]["target"].startswith("100755:blob:")


def test_refactored_tsx_to_ts_is_only_a_human_review_candidate(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@example.com")
    (repo / "old.tsx").write_text(
        "export const buildBankValue = () => createBankValue(BANK_MODE);\n"
    )
    base = _commit(repo, "base")
    (repo / "old.tsx").unlink()
    (repo / "new.ts").write_text(
        "export const buildBankValue = () => createBankValue(OFFICIAL_MODE);\n"
    )
    candidate = _commit(repo, "refactor")
    catalog = shared_code.parse_catalog({
        "schema_version": 1,
        "definitions": [{
            "path": "old.tsx",
            "customization_id": "BANK-OM-004",
            "assertions": [{
                "id": "bank-value",
                "matcher": "code_fragment",
                "fragment": (
                    "export const buildBankValue = () => "
                    "createBankValue(BANK_MODE);"
                ),
            }],
        }],
    })
    relocation = S.find_relocations(
        str(repo), candidate, catalog, ["old.tsx", "new.ts"]
    )
    finding = relocation["findings"][0]

    assert finding["verdict"] == "approval"
    assert finding["candidates"][0]["path"] == "new.ts"
    assert finding["candidates"][0]["evidence_strength"] == "symbol_overlap"
    assert finding["candidates"][0]["eligible_for_migration"] is True
