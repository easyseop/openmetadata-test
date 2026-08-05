"""Shared code-definition draft generator tests."""

from generate_shared_code_definition_draft import build_draft


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
