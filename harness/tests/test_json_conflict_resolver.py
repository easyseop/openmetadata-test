from tools.resolve_nonoverlapping_json_conflicts import (
    detect_indent,
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


def test_detect_indent_follows_the_incoming_version():
    """해결된 파일은 다시 써지므로 들여쓰기를 쓰는 쪽이 정한다.

    폭을 고정해 두면 새 버전이 다른 폭을 쓸 때 파일 전체가 다시 써져,
    커스터마이징과 무관한 변경이 통째로 diff 에 잡힌다.
    """
    two = b'{\n  "a": {\n    "b": 1\n  }\n}\n'
    four = b'{\n    "a": {\n        "b": 1\n    }\n}\n'
    tab_free_flat = b'{"a": 1}\n'
    assert detect_indent(two) == 2
    assert detect_indent(four) == 4
    assert detect_indent(tab_free_flat) == 4, "들여쓴 줄이 없으면 기본값"
    assert detect_indent(b'{\n}\n') == 4


def test_resolver_does_not_hardcode_an_indent_width():
    import inspect
    import tools.resolve_nonoverlapping_json_conflicts as mod

    body = inspect.getsource(mod)
    assert "indent=4," not in body, "폭을 고정하지 말고 들어오는 쪽을 따라야 한다"
    assert "indent=indent," in body
