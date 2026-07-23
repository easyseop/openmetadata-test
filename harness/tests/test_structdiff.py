"""T51/T52 structured-diff tests.

Diff logic is pure -> synthetic. The file-loading path is exercised against the
REAL OM table.json, which gained a `dataContract` property from 1.12.13 -> 1.13.0.
"""
from acgh import structdiff as SD


def test_added_removed_type_changed():
    old = {"a": 1, "b": {"x": "s"}, "c": [1, 2]}
    new = {"a": 1, "b": {"x": "s", "y": 2}, "c": {"k": 1}, "d": True}
    d = SD.structural_diff(old, new)
    assert "/d" in d.added
    assert "/b/y" in d.added
    assert d.removed == ()
    # c changed array -> object
    assert ("/c", "array", "object") in d.type_changed


def test_removed_key():
    d = SD.structural_diff({"a": 1, "gone": 2}, {"a": 1})
    assert d.removed == ("/gone",)
    assert d.added == ()


def test_identical_is_empty():
    doc = {"a": {"b": [1, 2], "c": "x"}}
    assert SD.structural_diff(doc, doc).is_empty


def test_real_om_schema_gained_datacontract(om_mirror):
    path = "openmetadata-spec/src/main/resources/json/schema/entity/data/table.json"
    d = SD.diff_file(str(om_mirror), "UPSTREAM_A", "UPSTREAM_B", path)
    # 1.13.0 really adds a top-level 'dataContract' property to Table.
    assert "/properties/dataContract" in d.added
    assert not d.is_empty
    assert "+" in d.summary()
