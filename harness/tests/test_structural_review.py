from __future__ import annotations

import subprocess

from acgh import shared_code
from acgh import structural_review as S


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
    assert "BINARY" in findings["binary.bin"]["risk_flags"]
    assert review["review_surface_paths"] == sorted(
        review["review_surface_paths"], key=lambda path: path.encode("utf-8")
    )


def test_rename_diagnostics_do_not_change_canonical_review(tmp_path):
    repo, base, target, custom, candidate = _topology(tmp_path)
    _git(repo, "config", "diff.renames", "true")
    first = S.build_review(str(repo), base, target, custom, candidate, {})
    _git(repo, "config", "diff.renames", "false")
    second = S.build_review(str(repo), base, target, custom, candidate, {})

    assert first == second
    assert first["canonical_policy"] == "rename_detection=disabled (--no-renames)"
    assert all(
        item["policy"].startswith("diagnostic(-M -C")
        for item in first["rename_diagnostics"]
    )


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
    assert result.verdict == "pass"
    assert "DIFFERS_FROM_BOTH" not in result.reasons

    manual_only["findings"][0]["risk_flags"] = [S.CUSTOM_LOSS_SUSPECT]
    result = S.to_gate_result(manual_only, no_shared_failures)
    assert result.verdict == "approval"


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
