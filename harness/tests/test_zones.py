"""T41 sensitive-zone + change-intent gate tests, on real OM paths."""
from pathlib import Path

from acgh import verdict as V
from acgh import zones as Z

_POLICY = Path(__file__).resolve().parents[1] / "policies" / "sensitive-zones.yaml"

_SEC = "openmetadata-service/src/main/java/org/openmetadata/service/security/AuthLoginServlet.java"
_AUTH_SCHEMA = "openmetadata-spec/src/main/resources/json/schema/auth/ssoAuth.json"
_SQL = "bootstrap/sql/migrations/native/1.13.0/mysql/schemaChanges.sql"
_PLAIN = "openmetadata-ui/src/main/resources/ui/src/components/Foo.tsx"


def zones():
    return Z.load_zones(_POLICY)


def _wide_intent():
    return {"allowed": ["**"], "forbidden": []}


def test_frozen_zone_blocks():
    r = Z.check_sensitive_zones([_SEC], zones(), _wide_intent())
    assert r.verdict == V.BLOCK
    assert any("frozen" in x for x in r.reasons)


def test_protected_zone_needs_approval():
    r = Z.check_sensitive_zones([_AUTH_SCHEMA], zones(), _wide_intent())
    assert r.verdict == V.APPROVAL


def test_watched_zone_passes_but_noted():
    r = Z.check_sensitive_zones([_SQL], zones(), _wide_intent())
    assert r.verdict == V.PASS
    assert any("watched" in x for x in r.reasons)
    assert any("visibility_only" in x for x in r.reasons)


def test_plain_in_scope_file_passes():
    r = Z.check_sensitive_zones([_PLAIN], zones(), _wide_intent())
    assert r.verdict == V.PASS


def test_missing_intent_is_fail_closed():
    r = Z.check_sensitive_zones([_PLAIN], zones(), None)
    assert r.verdict == V.ANALYSIS_ERROR


def test_empty_allowed_intent_is_fail_closed():
    r = Z.check_sensitive_zones(
        [_PLAIN], zones(), {"allowed": [], "forbidden": []}
    )
    assert r.verdict == V.ANALYSIS_ERROR
    assert "empty" in r.reasons[0]


def test_forbidden_intent_blocks():
    intent = {"allowed": ["**"], "forbidden": ["openmetadata-ui/**"]}
    r = Z.check_sensitive_zones([_PLAIN], zones(), intent)
    assert r.verdict == V.BLOCK


def test_outside_allowed_intent_needs_approval():
    intent = {"allowed": ["openmetadata-service/**"], "forbidden": []}
    r = Z.check_sensitive_zones([_PLAIN], zones(), intent)  # ui file not allowed
    assert r.verdict == V.APPROVAL


def test_frozen_dominates_over_intent_ok():
    # File is in-scope per intent, but it is a frozen zone -> block wins.
    intent = {"allowed": ["**"], "forbidden": []}
    r = Z.check_sensitive_zones([_SEC, _PLAIN], zones(), intent)
    assert r.verdict == V.BLOCK
