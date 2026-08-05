"""Shared-file BANK-OM code-definition gate tests."""
import subprocess

from acgh import shared_code as S
from acgh import verdict as V


def _run(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repo(tmp_path, files):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "main")
    _run(repo, "config", "user.email", "test@example.com")
    _run(repo, "config", "user.name", "test")
    _run(repo, "config", "commit.gpgsign", "false")
    for path, content in files.items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    _run(repo, "add", "-A")
    _run(repo, "commit", "-m", "candidate")
    return repo, _run(repo, "rev-parse", "HEAD")


def _catalog(*definitions):
    return S.parse_catalog(
        {
            "schema_version": 1,
            "definitions": list(definitions),
        }
    )


def _definition(path, customization_id, *assertions):
    return {
        "path": path,
        "customization_id": customization_id,
        "assertions": list(assertions),
    }


def test_code_definitions_distinguish_two_ids_in_one_java_file(tmp_path):
    repo, candidate = _repo(
        tmp_path,
        {
            "Entity.java": (
                "public final class Entity {\n"
                "  public static final String INSTANCE_CODE = \"instanceCode\";\n"
                "  public static final String QUERY_REPORT = \"queryReport\";\n"
                "}\n"
            )
        },
    )
    catalog = _catalog(
        _definition(
            "Entity.java",
            "BANK-OM-001",
            {
                "id": "instance-code-field",
                "matcher": "code_fragment",
                "fragment": (
                    'public static final String INSTANCE_CODE = "instanceCode";'
                ),
            },
        ),
        _definition(
            "Entity.java",
            "BANK-OM-002",
            {
                "id": "query-report-field",
                "matcher": "code_fragment",
                "fragment": (
                    'public static final String QUERY_REPORT = "queryReport";'
                ),
            },
        ),
    )
    result = S.check_shared_code_definitions(
        str(repo),
        candidate,
        catalog,
        {"Entity.java": ["BANK-OM-001", "BANK-OM-002"]},
    )
    assert result.verdict == V.PASS
    assert "shared_owner_pairs=2" in result.reasons


def test_comment_with_symbol_does_not_satisfy_code_definition(tmp_path):
    repo, candidate = _repo(
        tmp_path,
        {
            "Entity.java": (
                "public final class Entity {\n"
                "  // public static final String QUERY_REPORT = \"queryReport\";\n"
                "}\n"
            )
        },
    )
    catalog = _catalog(
        _definition(
            "Entity.java",
            "BANK-OM-002",
            {
                "id": "query-report-field",
                "matcher": "code_fragment",
                "fragment": (
                    'public static final String QUERY_REPORT = "queryReport";'
                ),
            },
        )
    )
    result = S.check_shared_code_definitions(
        str(repo), candidate, catalog, {"Entity.java": ["BANK-OM-002"]}
    )
    assert result.verdict == V.BLOCK
    assert "expected=1 actual=0" in result.reasons[0]


def test_symbol_with_wrong_initializer_blocks(tmp_path):
    repo, candidate = _repo(
        tmp_path,
        {
            "Entity.java": (
                "public final class Entity {\n"
                "  public static final String QUERY_REPORT = \"wrong\";\n"
                "}\n"
            )
        },
    )
    catalog = _catalog(
        _definition(
            "Entity.java",
            "BANK-OM-002",
            {
                "id": "query-report-field",
                "matcher": "code_fragment",
                "fragment": (
                    'public static final String QUERY_REPORT = "queryReport";'
                ),
            },
        )
    )
    result = S.check_shared_code_definitions(
        str(repo), candidate, catalog, {"Entity.java": ["BANK-OM-002"]}
    )
    assert result.verdict == V.BLOCK


def test_code_copied_inside_string_does_not_satisfy_definition(tmp_path):
    repo, candidate = _repo(
        tmp_path,
        {
            "Entity.java": (
                "public final class Entity {\n"
                "  String example = \"public static final String QUERY_REPORT "
                "= \\\"queryReport\\\";\";\n"
                "}\n"
            )
        },
    )
    catalog = _catalog(
        _definition(
            "Entity.java",
            "BANK-OM-002",
            {
                "id": "query-report-field",
                "matcher": "code_fragment",
                "fragment": (
                    'public static final String QUERY_REPORT = "queryReport";'
                ),
            },
        )
    )
    result = S.check_shared_code_definitions(
        str(repo), candidate, catalog, {"Entity.java": ["BANK-OM-002"]}
    )
    assert result.verdict == V.BLOCK


def test_json_pointer_checks_key_and_value_per_owner(tmp_path):
    repo, candidate = _repo(
        tmp_path,
        {"labels.json": '{"label":{"instance-code":"Instance Code"}}\n'},
    )
    catalog = _catalog(
        _definition(
            "labels.json",
            "BANK-OM-001",
            {
                "id": "instance-code-label",
                "matcher": "json_value",
                "pointer": "/label/instance-code",
                "expected": "Instance Code",
            },
        ),
        _definition(
            "labels.json",
            "BANK-OM-002",
            {
                "id": "query-report-label",
                "matcher": "json_value",
                "pointer": "/label/query-report",
                "expected": "Query Report",
            },
        ),
    )
    result = S.check_shared_code_definitions(
        str(repo),
        candidate,
        catalog,
        {"labels.json": ["BANK-OM-001", "BANK-OM-002"]},
    )
    assert result.verdict == V.BLOCK
    assert "BANK-OM-002" in result.reasons[0]
    assert "JSON pointer missing" in result.reasons[0]


def test_every_shared_path_owner_pair_requires_a_definition(tmp_path):
    repo, candidate = _repo(tmp_path, {"Entity.java": "class Entity {}\n"})
    catalog = _catalog(
        _definition(
            "Entity.java",
            "BANK-OM-001",
            {
                "id": "entity-class",
                "matcher": "code_fragment",
                "fragment": "class Entity {}",
            },
        )
    )
    result = S.check_shared_code_definitions(
        str(repo),
        candidate,
        catalog,
        {"Entity.java": ["BANK-OM-001", "BANK-OM-002"]},
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "missing=[('Entity.java', 'BANK-OM-002')]" in result.reasons[0]


def test_duplicate_path_owner_definition_is_rejected():
    raw = _definition(
        "Entity.java",
        "BANK-OM-001",
        {
            "id": "entity-class",
            "matcher": "code_fragment",
            "fragment": "class Entity {}",
        },
    )
    try:
        _catalog(raw, raw)
    except S.SharedCodeError as exc:
        assert "duplicate shared code definition" in str(exc)
    else:
        raise AssertionError("duplicate path-owner definitions must fail closed")


def test_sql_comments_do_not_satisfy_definition(tmp_path):
    repo, candidate = _repo(
        tmp_path,
        {"schema.sql": "-- CREATE TABLE query_report_entity (id INT);\n"},
    )
    catalog = _catalog(
        _definition(
            "schema.sql",
            "BANK-OM-002",
            {
                "id": "query-report-table",
                "matcher": "code_fragment",
                "fragment": "CREATE TABLE query_report_entity (id INT);",
            },
        )
    )
    result = S.check_shared_code_definitions(
        str(repo), candidate, catalog, {"schema.sql": ["BANK-OM-002"]}
    )
    assert result.verdict == V.BLOCK
