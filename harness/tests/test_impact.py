"""T42 impact-analysis tests, incl. the §7 advisory-only property."""
from acgh import evidence as E
from acgh import impact as IM
from acgh import upgrade_watch as UW
from acgh import verdict as V

_CHANGED_DIR = "openmetadata-service/src/main/java/org/openmetadata/service/security/**"


def _manifest(cid):
    return {
        "customization_id": cid, "kind": "core-patch",
        "upgrade_watch": {
            "paths": [_CHANGED_DIR],
            "configuration_keys": ["authenticationConfiguration.provider"],
            "dependencies": ["org.openmetadata:security"],
        },
        "assurance": {"contracts": ["CONTRACT-SSO-LOGIN"]},
    }


def test_impact_surface_maps_full_context():
    finding = UW.WatchFinding("BANK-OM-001",
                              ("openmetadata-service/.../security/JwtFilter.java",))
    items = IM.build_impact_surface([finding], {"BANK-OM-001": _manifest("BANK-OM-001")})
    assert len(items) == 1
    it = items[0]
    assert it.configuration_keys == ("authenticationConfiguration.provider",)
    assert it.dependencies == ("org.openmetadata:security",)
    assert it.contracts == ("CONTRACT-SSO-LOGIN",)


def test_llm_suggestions_have_no_verdict_and_fit_evidence_card():
    finding = UW.WatchFinding("BANK-OM-001",
                              ("openmetadata-service/.../security/JwtFilter.java",))
    items = IM.build_impact_surface([finding], {"BANK-OM-001": _manifest("BANK-OM-001")})
    sugg = IM.to_llm_suggestions(items)
    assert sugg and "verdict" not in sugg[0]
    assert set(sugg[0]) <= {"gate", "memo", "severity_hint"}

    # Advisory memos ride in the card WITHOUT moving the machine verdict (§7).
    result = V.build_result([V.GateResult("upgrade-watch", V.APPROVAL, ())],
                            {"repositories": {"upstream": {"sha": "a" * 40}}},
                            "0.0.1", run_id="r1")
    plain = E.build_evidence_card(result)
    with_memos = E.build_evidence_card(result, llm_suggestions=sugg)
    assert plain["machine_verdict"] == with_memos["machine_verdict"] == V.APPROVAL
    assert plain["result_digest"] == with_memos["result_digest"]
    assert with_memos["llm_suggestions"] == sugg


def test_review_packet_shape():
    finding = UW.WatchFinding("BANK-OM-002", ("conf/openmetadata.yaml",))
    items = IM.build_impact_surface([finding], {"BANK-OM-002": _manifest("BANK-OM-002")})
    pkt = IM.review_packet(items)
    assert pkt["impacted_count"] == 1
    assert pkt["impacted"][0]["customization_id"] == "BANK-OM-002"


def test_review_packet_includes_observed_config_and_dependency_hits():
    finding = UW.WatchFinding(
        "BANK-OM-001",
        (),
        ("authenticationConfiguration.provider",),
        ("org.openmetadata:security",),
    )
    items = IM.build_impact_surface(
        [finding], {"BANK-OM-001": _manifest("BANK-OM-001")}
    )
    packet = IM.review_packet(items)["impacted"][0]
    assert packet["changed_configuration_keys"] == [
        "authenticationConfiguration.provider"
    ]
    assert packet["changed_dependencies"] == [
        "org.openmetadata:security"
    ]
    memo = IM.to_llm_suggestions(items)[0]["memo"]
    assert "changed_config" in memo
    assert "changed_deps" in memo


def test_impact_from_real_mirror_findings(om_mirror):
    findings = UW.evaluate_upgrade_watch(
        str(om_mirror), "UPSTREAM_A", "UPSTREAM_B",
        {"BANK-OM-001": _manifest("BANK-OM-001")})
    items = IM.build_impact_surface(findings, {"BANK-OM-001": _manifest("BANK-OM-001")})
    assert items and items[0].changed_watch_paths  # real changed security files
