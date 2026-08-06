from propose_shared_code_definitions import (
    _added_runs,
    _best_surviving_fragment,
    _changed_leaves,
    _structured_assertions,
)


def test_changed_leaves_uses_json_pointers_and_only_changed_values():
    before = {"label": {"old": "same", "query/report": "before"}}
    after = {"label": {"old": "same", "query/report": "쿼리 리포트"}}

    assert _changed_leaves(before, after) == [
        ("/label/query~1report", "쿼리 리포트")
    ]


def test_structured_assertions_excludes_value_changed_again_in_candidate():
    assertions = _structured_assertions(
        '{"a": 1, "b": 1}',
        '{"a": 2, "b": 2}',
        '{"a": 2, "b": 3}',
        "json_value",
        "bank-om-001-values",
    )

    assert assertions == [
        {
            "id": "bank-om-001-values-1",
            "matcher": "json_value",
            "pointer": "/a",
            "expected": 2,
        }
    ]


def test_added_runs_ignores_headers_and_splits_separate_additions():
    diff = """diff --git a/a.ts b/a.ts
--- a/a.ts
+++ b/a.ts
@@ -1,0 +2,2 @@
+const FIRST = true;
+
 existing();
@@ -4,0 +6 @@
+const SECOND = true;
"""

    assert _added_runs(diff) == [
        ["const FIRST = true;", ""],
        ["const SECOND = true;"],
    ]


def test_best_surviving_fragment_uses_added_code_not_comment_only_text():
    lines = [
        "// QUERY_REPORT is documented here",
        'public static final String QUERY_REPORT = "queryReport";',
    ]
    final = 'public static final String QUERY_REPORT = "queryReport";\n'

    fragment, occurrences = _best_surviving_fragment(lines, final, ".java")

    assert "public static final String QUERY_REPORT" in fragment
    assert occurrences == 1
