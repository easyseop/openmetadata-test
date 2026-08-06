"""Shared code-definition draft generator tests."""

import json

import yaml

from generate_shared_code_definition_draft import build_draft, main


def test_draft_contains_every_shared_path_owner_pair():
    draft = build_draft(
        {
            "Entity.java": ["BANK-OM-002", "BANK-OM-001"],
            "labels.json": ["BANK-OM-004", "BANK-OM-001"],
        }
    )
    assert [
        (item["path"], item["customization_id"])
        for item in draft["definitions"]
    ] == [
        ("Entity.java", "BANK-OM-001"),
        ("Entity.java", "BANK-OM-002"),
        ("labels.json", "BANK-OM-001"),
        ("labels.json", "BANK-OM-004"),
    ]
    assert all(not item["assertions"] for item in draft["definitions"])
    assert "draft_notice" in draft


def test_draft_rejects_nonshared_owner_entries():
    try:
        build_draft({"Entity.java": ["BANK-OM-001"]})
    except ValueError as exc:
        assert "at least two" in str(exc)
    else:
        raise AssertionError("single-owner path must not enter the shared draft")


def test_existing_matching_draft_is_reused_without_overwrite(tmp_path, capsys):
    owners = tmp_path / "owners.yaml"
    output = tmp_path / "draft.yaml"
    owners.write_text(
        yaml.safe_dump({"Entity.java": ["BANK-OM-001", "BANK-OM-002"]}),
        encoding="utf-8",
    )
    existing = build_draft(
        {"Entity.java": ["BANK-OM-001", "BANK-OM-002"]}
    )
    existing["definitions"][0]["assertions"] = [{"contains": "INSTANCE_CODE"}]
    original_text = yaml.safe_dump(existing, sort_keys=False)
    output.write_text(original_text, encoding="utf-8")

    assert main(["--owners", str(owners), "--output", str(output)]) == 0

    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "DRAFT_ALREADY_EXISTS"
    assert result["definition_pairs"] == 2
    assert result["completed_pairs"] == 1
    assert result["remaining_pairs"] == 1
    assert output.read_text(encoding="utf-8") == original_text


def test_existing_stale_draft_is_analysis_error(tmp_path, capsys):
    owners = tmp_path / "owners.yaml"
    output = tmp_path / "draft.yaml"
    owners.write_text(
        yaml.safe_dump({"Entity.java": ["BANK-OM-001", "BANK-OM-002"]}),
        encoding="utf-8",
    )
    output.write_text(
        yaml.safe_dump(build_draft({"Other.java": ["BANK-OM-001", "BANK-OM-002"]})),
        encoding="utf-8",
    )

    assert main(["--owners", str(owners), "--output", str(output)]) == 3

    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "ANALYSIS_ERROR"
    assert "does not match" in result["message"]
