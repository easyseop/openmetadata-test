from initialize_registration_workspace import mapping_facts


def test_mapping_facts_separates_registered_shared_and_excluded_paths():
    owners, excluded, shared = mapping_facts(
        {
            "paths": [
                {
                    "path": "a.java",
                    "classification": "shared",
                    "customization_ids": ["BANK-OM-002", "BANK-OM-001"],
                },
                {
                    "path": "b.py",
                    "classification": "exclusive",
                    "customization_ids": ["BANK-OM-003"],
                },
                {
                    "path": "local.yml",
                    "classification": "excluded",
                    "customization_ids": [],
                },
            ]
        }
    )

    assert owners == {
        "a.java": ["BANK-OM-001", "BANK-OM-002"],
        "b.py": ["BANK-OM-003"],
    }
    assert excluded == ["local.yml"]
    assert shared == ["a.java"]
