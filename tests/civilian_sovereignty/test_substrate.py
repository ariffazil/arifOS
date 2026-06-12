"""
F14 — Civilian Sovereignty substrate unit tests.

All 10 rights, all 12 enforcement helpers, all language registry entries,
all the F1-F13 floor bindings.
"""

import pytest

from arifosmcp.runtime.civilian_sovereignty import (
    SOVEREIGN_RIGHTS,
    RIGHT_REGISTRY,
    get_right,
    list_rights,
    SovereignRightId,
    RightStatus,
)
from arifosmcp.runtime.civilian_sovereignty.enforce import (
    stamp_ai_involvement,
    make_appeal_envelope,
    require_sovereign_judgment,
    stamp_language,
    stamp_cognitive_privacy,
    stamp_refuse_profiling,
    entanglement_score,
    stamp_explanation,
    preserve_skill_split,
    stamp_opt_out,
    LANGUAGE_REGISTRY,
    full_rights_audit,
)


# ── Registry ─────────────────────────────────────────────────────────────


def test_all_10_rights_registered():
    assert len(SOVEREIGN_RIGHTS) == 10, f"expected 10, got {len(SOVEREIGN_RIGHTS)}"


def test_right_ids_match_enum():
    expected_ids = {
        "right_to_know_when_AI_is_involved",
        "right_to_appeal_automated_decisions",
        "right_to_human_judgment_high_stakes",
        "right_to_local_language_cultural_grounding",
        "right_to_cognitive_privacy",
        "right_to_refuse_behavioral_profiling",
        "right_to_non_addictive_AI",
        "right_to_explanation_in_plain_language",
        "right_to_preserve_human_skill",
        "right_to_opt_out_without_second_class",
    }
    actual = {r.id.value for r in SOVEREIGN_RIGHTS}
    assert actual == expected_ids, f"id drift: {actual.symmetric_difference(expected_ids)}"


def test_each_right_has_bahasa_id():
    """F06 EMPATHY: every right carries a Bahasa Melayu epithet."""
    for r in SOVEREIGN_RIGHTS:
        assert r.bm_id and len(r.bm_id) > 0, f"{r.id} missing bm_id"


def test_each_right_has_humility_disclaimer():
    """F07 HUMILITY: every right declares what it CANNOT guarantee."""
    for r in SOVEREIGN_RIGHTS:
        assert r.what_we_cannot_guarantee, f"{r.id} missing humility disclaimer"
        assert (
            "cannot" in r.what_we_cannot_guarantee.lower()
            or "no " in r.what_we_cannot_guarantee.lower()
        )


def test_get_right_lookup_works():
    r = get_right("right_to_know_when_AI_is_involved")
    assert r.id == SovereignRightId.RIGHT_TO_KNOW


def test_get_right_unknown_raises():
    with pytest.raises(KeyError):
        get_right("not_a_real_right")


def test_list_rights_returns_10_summaries():
    summaries = list_rights()
    assert len(summaries) == 10
    for s in summaries:
        assert "id" in s and "bm_id" in s and "status" in s


# ── Right 1: KNOW ────────────────────────────────────────────────────────


def test_stamp_ai_involvement_adds_metadata():
    v = stamp_ai_involvement({"verdict": "SEAL"}, "partial", 0.88)
    assert "ai_involvement" in v
    assert v["ai_involvement"]["disclosure"] == "partial"
    assert v["ai_involvement"]["confidence"] == 0.88
    # original verdict preserved
    assert v["verdict"] == "SEAL"


def test_stamp_ai_involvement_confidence_never_1():
    """F07 HUMILITY: confidence cap at 0.95, never 1.0."""
    v = stamp_ai_involvement({}, "full", 1.0)
    assert v["ai_involvement"]["confidence"] <= 0.95


def test_stamp_ai_involvement_default_is_full():
    v = stamp_ai_involvement({})
    assert v["ai_involvement"]["disclosure"] == "full"


# ── Right 2: APPEAL ──────────────────────────────────────────────────────


def test_make_appeal_envelope_returns_path():
    e = make_appeal_envelope("dec-001", "model-X + rule-Y", "grounds", "arif-fazil")
    assert e["right_id"] == "right_to_appeal_automated_decisions"
    assert e["input"]["original_decision_ref"] == "dec-001"
    assert "kernel_role" in e["appeal_path"]
    # kernel role is path-only — never decides
    assert "PATH ONLY" in e["appeal_path"]["kernel_role"]


# ── Right 3: HUMAN JUDGMENT ───────────────────────────────────────────


def test_require_sovereign_judgment_c1_returns_none():
    assert require_sovereign_judgment("C1") is None


def test_require_sovereign_judgment_c2_returns_none():
    assert require_sovereign_judgment("C2") is None


def test_require_sovereign_judgment_c3_returns_none():
    assert require_sovereign_judgment("C3") is None


def test_require_sovereign_judgment_c4_holds():
    h = require_sovereign_judgment("C4", "drilling", 0.8)
    assert h is not None
    assert h["verdict"] == "HOLD"
    assert h["action_class"] == "C4"


def test_require_sovereign_judgment_c5_holds():
    h = require_sovereign_judgment("C5", "medical", 0.95)
    assert h is not None
    assert h["verdict"] == "HOLD"


def test_require_sovereign_judgment_c4_always_holds():
    """C4 ALWAYS escalates regardless of stakes — the class itself is the trigger."""
    h = require_sovereign_judgment("C4", "drilling", 0.2)
    assert h is not None
    assert h["verdict"] == "HOLD"


def test_require_sovereign_judgment_high_stakes_c2_holds():
    """Even C2, if stakes >= 0.7, must escalate."""
    h = require_sovereign_judgment("C2", "financial", 0.85)
    assert h is not None
    assert h["verdict"] == "HOLD"


# ── Right 4: LANGUAGE ───────────────────────────────────────────────────


def test_language_registry_has_10_languages():
    assert len(LANGUAGE_REGISTRY) == 10


def test_stamp_language_default_is_english():
    v = stamp_language({})
    assert v["language_grounding"]["language"] == "en"


def test_stamp_language_bahasa_melayu():
    v = stamp_language({}, "bm", "civilian", "maruah")
    assert v["language_grounding"]["language"] == "bm"
    assert v["language_grounding"]["language_name"] == "Bahasa Melayu"
    assert v["language_grounding"]["cultural_anchor"] == "maruah"


def test_stamp_language_unknown_falls_back_to_english():
    """F07: refuse to fail on unknown language."""
    v = stamp_language({}, "klingon")
    assert v["language_grounding"]["language"] == "en"


def test_stamp_language_includes_uncertainty_band():
    v = stamp_language({})
    band = v["language_grounding"]["semantic_fidelity_band"]
    assert "P10" in band and "P50" in band and "P90" in band
    assert band["P10"] < band["P50"] < band["P90"]


# ── Right 5: COGNITIVE PRIVACY ─────────────────────────────────────────


def test_stamp_cognitive_privacy_default_is_minimize():
    v = stamp_cognitive_privacy({})
    assert v["cognitive_privacy"]["scope"] == "minimize"


def test_stamp_cognitive_privacy_forget():
    v = stamp_cognitive_privacy({}, "forget", ["session_history"], 0)
    assert v["cognitive_privacy"]["retention_set_to"] == "forgotten"


def test_stamp_cognitive_privacy_sequester():
    v = stamp_cognitive_privacy({}, "sequester")
    assert v["cognitive_privacy"]["retention_set_to"] == "session-only"


def test_stamp_cognitive_privacy_audit_trail_never_zero():
    """F11 AUDITABILITY: the FACT of the request is always sealed,
    even if the content is forgotten."""
    v = stamp_cognitive_privacy({}, "forget")
    assert v["cognitive_privacy"]["audit_trail_kept_for_days"] > 0


# ── Right 6: REFUSE PROFILING ──────────────────────────────────────────


def test_stamp_refuse_profiling_default_session():
    v = stamp_refuse_profiling({})
    assert v["profiling_opt_out"]["scope"] == "this_session"
    assert "engagement" in v["profiling_opt_out"]["profiling_disabled"]


def test_stamp_refuse_profiling_user_forever():
    v = stamp_refuse_profiling({}, "all_sessions")
    assert v["profiling_opt_out"]["scope"] == "all_sessions"


def test_stamp_refuse_profiling_service_quality_unchanged():
    """Opting out of profiling is NOT a quality demotion."""
    v = stamp_refuse_profiling({})
    assert v["profiling_opt_out"]["service_quality_floor"] == "unchanged"


# ── Right 7: NON-ADDICTION ────────────────────────────────────────────


def test_entanglement_low_use():
    r = entanglement_score(2, 60, 1)
    assert r["entanglement_score"] < 0.4
    assert r["band"] == "OBSERVED"
    assert r["advisory_emitted"] is False


def test_entanglement_medium_use():
    r = entanglement_score(8, 60, 3)
    assert 0.4 <= r["entanglement_score"] < 0.7
    assert r["band"] == "NOTED"


def test_entanglement_high_use_triggers_advisory():
    r = entanglement_score(20, 30, 5)
    assert r["entanglement_score"] >= 0.7
    assert r["band"] == "QUIET_ADVISORY"
    assert r["advisory_emitted"] is True
    assert r["advisory"] is not None
    assert "right_to_opt_out" in r["advisory"]


def test_entanglement_dense_burst():
    r = entanglement_score(50, 10, 8)
    assert r["entanglement_score"] >= 0.7
    assert r["advisory_emitted"] is True


# ── Right 8: EXPLANATION ──────────────────────────────────────────────


def test_stamp_explanation_basic():
    v = stamp_explanation({}, "GR shows 75 API at 1500m", {"P10": 0.7, "P50": 0.85, "P90": 0.95})
    assert "plain_explanation" in v
    assert v["plain_explanation"]["explanation"] == "GR shows 75 API at 1500m"


def test_stamp_explanation_i_cannot_explain():
    v = stamp_explanation({}, "", {"P10": 0, "P50": 0, "P90": 0}, i_cannot_explain=True)
    assert v["plain_explanation"]["i_cannot_explain"] is True


# ── Right 9: PRESERVE SKILL ───────────────────────────────────────────


def test_preserve_skill_split_basic():
    r = preserve_skill_split(
        "write essay",
        "I drafted the introduction",
        "I will not write the body — you should do that",
        "Write the body yourself",
        preserve_band=0.7,
    )
    assert r["preserve_skill_band"] == 0.7
    assert "body" in r["civilian_left_to_do"].lower()


def test_preserve_skill_split_invalid_band_clamps():
    r = preserve_skill_split("task", "did", "refused", "civilian", preserve_band=99.0)
    assert 0.0 <= r["preserve_skill_band"] <= 1.0


# ── Right 10: OPT OUT ──────────────────────────────────────────────────


def test_stamp_opt_out_default_session():
    v = stamp_opt_out({})
    assert v["opt_out"]["scope"] == "this_session"
    assert "equal" in v["opt_out"]["constitutional_protection"]


def test_stamp_opt_out_user_forever():
    v = stamp_opt_out({}, "this_user_forever", "no thank you")
    assert v["opt_out"]["scope"] == "this_user_forever"
    assert v["opt_out"]["reason"] == "no thank you"


def test_stamp_opt_out_retains_witness_tools():
    v = stamp_opt_out({})
    assert "arif_os_attest" in v["opt_out"]["retained_tools"]
    assert "arif_organ_attest_all" in v["opt_out"]["retained_tools"]


def test_stamp_opt_out_rejects_writes():
    v = stamp_opt_out({})
    assert "vault_seal" in v["opt_out"]["rejected_actions"]
    assert "forge_execute" in v["opt_out"]["rejected_actions"]


def test_stamp_opt_out_has_appeal_path():
    """Opt-out users can opt back in."""
    v = stamp_opt_out({})
    assert "session_init" in v["opt_out"]["appeal_path"]


# ── F02 / F07 binding: uncertainty never 1.0 ───────────────────────────


@pytest.mark.parametrize(
    "helper_name,args",
    [
        ("stamp_ai_involvement", ({"v": "x"}, "full", 1.0)),
        ("stamp_explanation", ({"v": "x"}, "x", {"P10": 1.0, "P50": 1.0, "P90": 1.0})),
    ],
)
def test_f07_confidence_never_one(helper_name, args):
    """F07: no confidence field may equal 1.0."""
    import importlib

    mod = importlib.import_module("arifosmcp.runtime.civilian_sovereignty.enforce")
    helper = getattr(mod, helper_name)
    v = helper(*args)
    # Find any confidence / uncertainty values and assert they are < 1.0
    import json

    s = json.dumps(v, default=str)
    # Cheap check: no field equals "1.0" or "1.00" (heuristic)
    assert '"confidence": 1.0' not in s
    assert '"confidence": 1.00' not in s


# ── Full audit (cockpit) ──────────────────────────────────────────────


def test_full_rights_audit_returns_10_rights():
    a = full_rights_audit("arif-fazil", "sess-test")
    assert a["rights_count"] == 10
    assert len(a["rights_summary"]) == 10


def test_full_rights_audit_includes_humility_disclaimer():
    a = full_rights_audit("arif-fazil")
    text = a["what_we_cannot_guarantee"].lower()
    # The disclaimer may use "cannot", "no ", "not ", or "does not guarantee"
    assert any(marker in text for marker in ("cannot", "no ", "not ", "does not guarantee")), (
        f"humility disclaimer missing: {a['what_we_cannot_guarantee']!r}"
    )


# ── F1-F13 floor binding (per right) ─────────────────────────────────


def test_every_right_binds_at_least_one_floor():
    """F11/F02/F13 etc. must be present. No orphan rights."""
    valid_floors = {f"F{n:02d}" for n in range(1, 14)}
    for r in SOVEREIGN_RIGHTS:
        assert r.floor_binding, f"{r.id} binds no floor"
        for f in r.floor_binding:
            assert f in valid_floors, f"{r.id} binds invalid floor {f}"


def test_f13_sovereign_appears_in_hard_rights():
    """Every HARD + kernel-cannot-grant right must bind F13.

    Right-to-appeal is HARD because it needs a human reviewer (kernel
    cannot grant). Cognitive-privacy is HARD but kernel-grantable.
    """
    for r in SOVEREIGN_RIGHTS:
        if r.enforcement_class == "HARD" and not r.can_kernel_grant:
            assert "F13" in r.floor_binding, (
                f"{r.id} is HARD + kernel-cannot-grant but does not bind F13"
            )


def test_f02_truth_binds_language_and_explanation():
    """Right #4 (language) and Right #8 (explanation) bind F02 truth."""
    language_floors = [
        r.floor_binding for r in SOVEREIGN_RIGHTS if r.id == SovereignRightId.RIGHT_TO_LANGUAGE
    ][0]
    explanation_floors = [
        r.floor_binding for r in SOVEREIGN_RIGHTS if r.id == SovereignRightId.RIGHT_TO_EXPLANATION
    ][0]
    assert "F02" in language_floors
    assert "F02" in explanation_floors
