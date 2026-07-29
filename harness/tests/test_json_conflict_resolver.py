from tools.resolve_nonoverlapping_json_conflicts import (
    MISSING,
    Change,
    apply_change,
    changes,
    flatten,
)


def test_flatten_uses_full_leaf_paths():
    assert flatten({"label": {"instance-code": "Instance Code"}}) == {
        ("label", "instance-code"): "Instance Code"
    }


def test_changes_distinguishes_add_update_and_delete():
    result = changes(
        {"label": {"old": "before", "remove": "value"}},
        {"label": {"old": "after", "add": "value"}},
    )
    by_path = {item.path: item.value for item in result}
    assert by_path[("label", "old")] == "after"
    assert by_path[("label", "add")] == "value"
    assert by_path[("label", "remove")] is MISSING


def test_apply_change_updates_official_json_without_replacing_other_keys():
    target = {"label": {"official-new": "keep", "shared": "official"}}
    apply_change(target, Change(("label", "instance-code"), "Instance Code"))
    assert target == {
        "label": {
            "official-new": "keep",
            "shared": "official",
            "instance-code": "Instance Code",
        }
    }
