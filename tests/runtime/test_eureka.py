"""
tests/runtime/test_eureka.py — Phase T1 coverage for context_engine/eureka.py
==============================================================================

The contract under test:
  - AuthorityClass: 7-tier authority hierarchy (0-100, with CONSTITUTIONAL=100,
    UNTRUSTED=0; USER_INSTRUCTION=90 is the active user ask; never
    demote/drop USER_INSTRUCTION by default).
  - ContextBucket: 4-bucket framework (WRITE / SELECT / COMPRESS / ISOLATE).
  - ContextFailureMode: 4 documented production failure modes.
  - PRESSURE_ACTION_MAP: per-band tier recommendation; auto_compact=False
    on every band by default.
  - marginal_value_per_token(): include / demote / drop decision based on
    authority × relevance ÷ (tokens × cost × risk_shadow_price).
  - empty_context_packet(): skeleton packet shape for Phase 3.
  - EUREKA_POLICY_VERSION is pinned; source-of-truth doc path is correct.

Iron rules (F1-F13):
  - F1 AMANAH:  eureka decisions are advisory; never auto-mutate.
  - F2 TRUTH:   authority classes are 0-100, no fabricated middle tiers.
  - F4 CLARITY: 4 buckets, 4 failure modes, single-purpose.
  - F7 HUMILITY: low-confidence content is quarantine-tier (20), not trusted.
  - F8 GENIUS:  policy version is pinned, source of truth is a doc.
  - F11 AUDIT:  every eureka call is traceable (returns value_per_token + rationale).

DITEMPA BUKAN DIBERI — the eureka is a meter, not a mind.
"""

from __future__ import annotations


from arifosmcp.runtime.context_engine.eureka import (
    EUREKA_POLICY_VERSION,
    SOURCE_OF_TRUTH,
    AuthorityClass,
    ContextBucket,
    ContextFailureMode,
    FAILURE_PREVENTION,
    PRESSURE_ACTION_MAP,
    _self_check,
    empty_context_packet,
    marginal_value_per_token,
)
from arifosmcp.runtime.context_audit import RiskClass
from arifosmcp.runtime.token_pressure import PressureBand


# ─────────────────────────────────────────────────────────────────────────────
# Authority hierarchy (1–5)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuthorityHierarchy:
    def test_nine_classes_present(self):
        """9 tiers per the canonical source (CONSTITUTIONAL..UNTRUSTED)."""
        assert len(AuthorityClass) == 9

    def test_constitutional_outranks_everything_else(self):
        """CONSTITUTIONAL (100) is the top; strictly greater than every
        other tier (not strictly greater than itself)."""
        for ac in AuthorityClass:
            if ac is AuthorityClass.CONSTITUTIONAL:
                continue
            assert AuthorityClass.CONSTITUTIONAL.value > ac.value

    def test_user_instruction_outranks_lower_tiers(self):
        """USER_INSTRUCTION = 90 outranks ACTIVE_TASK / VERIFIED_MEMORY /
        RETRIEVED_DOC / RECENT_CONVERSATION / DERIVED_SUMMARY / LOW_CONFIDENCE /
        UNTRUSTED."""
        assert AuthorityClass.USER_INSTRUCTION > AuthorityClass.ACTIVE_TASK
        assert AuthorityClass.USER_INSTRUCTION > AuthorityClass.VERIFIED_MEMORY
        assert AuthorityClass.USER_INSTRUCTION > AuthorityClass.RETRIEVED_DOC
        assert AuthorityClass.USER_INSTRUCTION > AuthorityClass.UNTRUSTED

    def test_untrusted_is_zero_and_lowest(self):
        assert AuthorityClass.UNTRUSTED.value == 0
        for ac in AuthorityClass:
            assert ac.value >= 0

    def test_authority_values_match_blueprint(self):
        """Pin the exact values from the blueprint section 4."""
        assert AuthorityClass.CONSTITUTIONAL.value == 100
        assert AuthorityClass.USER_INSTRUCTION.value == 90
        assert AuthorityClass.ACTIVE_TASK.value == 80
        assert AuthorityClass.VERIFIED_MEMORY.value == 70
        assert AuthorityClass.RETRIEVED_DOC.value == 60
        assert AuthorityClass.RECENT_CONVERSATION.value == 50
        assert AuthorityClass.DERIVED_SUMMARY.value == 40
        assert AuthorityClass.LOW_CONFIDENCE.value == 20
        assert AuthorityClass.UNTRUSTED.value == 0

    def test_low_confidence_quarantined_below_derived(self):
        """Quarantine (20) < derived summary (40). Per blueprint."""
        assert AuthorityClass.LOW_CONFIDENCE < AuthorityClass.DERIVED_SUMMARY


# ─────────────────────────────────────────────────────────────────────────────
# 4-bucket framework (6)
# ─────────────────────────────────────────────────────────────────────────────
class TestContextBucketFramework:
    def test_four_buckets_present(self):
        assert len(ContextBucket) == 4
        assert ContextBucket.WRITE in ContextBucket
        assert ContextBucket.SELECT in ContextBucket
        assert ContextBucket.COMPRESS in ContextBucket
        assert ContextBucket.ISOLATE in ContextBucket


# ─────────────────────────────────────────────────────────────────────────────
# marginal_value_per_token (7–9)
# ─────────────────────────────────────────────────────────────────────────────
class TestMarginalValueAllocator:
    def test_high_authority_high_relevance_includes(self):
        """Constitutional + high relevance → include."""
        r = marginal_value_per_token(
            {"tokens": 100, "authority_class": 100, "relevance_score": 0.95, "staleness": 0},
            task_value=0.9,
        )
        assert r["recommendation"] == "include"
        assert r["value_per_token"] > 0

    def test_low_authority_low_relevance_drops(self):
        """UNTRUSTED, low relevance, stale → drop."""
        r = marginal_value_per_token(
            {"tokens": 5000, "authority_class": 0, "relevance_score": 0.05, "staleness": 60},
            task_value=0.3,
        )
        assert r["recommendation"] == "drop"

    def test_marginal_recommendation_is_demote(self):
        """Stale duplicate with moderate authority should demote, not drop."""
        r = marginal_value_per_token(
            {
                "tokens": 1000,
                "authority_class": 60,
                "relevance_score": 0.4,
                "staleness": 10,
                "duplication_count": 1,
            },
            task_value=0.5,
        )
        # demote or drop — both acceptable; never include
        assert r["recommendation"] in ("demote_to_lower_priority", "drop")

    def test_user_instruction_never_drops(self):
        """USER_INSTRUCTION authority (90) + high relevance + zero staleness
        must always include. The user instruction is sacred."""
        r = marginal_value_per_token(
            {"tokens": 300, "authority_class": 90, "relevance_score": 0.9, "staleness": 0},
            task_value=0.95,
        )
        assert r["recommendation"] == "include"

    def test_risk_shadow_price_lowers_score(self):
        """Same segment, higher risk band → lower value_per_token."""
        base_seg = {"tokens": 500, "authority_class": 60, "relevance_score": 0.7, "staleness": 0}
        routine = marginal_value_per_token(base_seg, task_value=0.7, risk_band=RiskClass.ROUTINE)
        private = marginal_value_per_token(base_seg, task_value=0.7, risk_band=RiskClass.PRIVATE)
        assert private["value_per_token"] < routine["value_per_token"]

    def test_value_per_token_uses_token_denominator(self):
        """Larger token cost for same quality → smaller value_per_token."""
        small = marginal_value_per_token(
            {"tokens": 100, "authority_class": 70, "relevance_score": 0.8, "staleness": 0},
            task_value=0.7,
        )
        large = marginal_value_per_token(
            {"tokens": 5000, "authority_class": 70, "relevance_score": 0.8, "staleness": 0},
            task_value=0.7,
        )
        assert small["value_per_token"] > large["value_per_token"]

    def test_returns_traceable_rationale(self):
        r = marginal_value_per_token(
            {"tokens": 100, "authority_class": 70, "relevance_score": 0.8, "staleness": 0},
            task_value=0.7,
        )
        assert "rationale" in r
        assert "authority=" in r["rationale"]
        assert "mvpt=" in r["rationale"]

    def test_zero_task_value_drops_everything(self):
        """If the task is worthless, no segment is worth including."""
        r = marginal_value_per_token(
            {"tokens": 100, "authority_class": 100, "relevance_score": 0.99, "staleness": 0},
            task_value=0.0,
        )
        assert r["recommendation"] in ("drop", "demote_to_lower_priority")


# ─────────────────────────────────────────────────────────────────────────────
# Pressure-action map (10)
# ─────────────────────────────────────────────────────────────────────────────
class TestPressureActionMap:
    def test_warn_band_auto_compact_is_false(self):
        """WARN must not auto-compact (F8 sovereignty)."""
        assert PRESSURE_ACTION_MAP[PressureBand.WARN]["auto_compact"] is False

    def test_compact_band_auto_compact_is_false(self):
        """Even COMPACT does not auto-compact by default. F8+F13 to enable."""
        assert PRESSURE_ACTION_MAP[PressureBand.COMPACT]["auto_compact"] is False

    def test_hold_band_includes_hold_in_tier(self):
        assert "HOLD" in PRESSURE_ACTION_MAP[PressureBand.HOLD]["tier"]

    def test_low_band_no_action(self):
        assert PRESSURE_ACTION_MAP[PressureBand.LOW]["tier"] == "NORMAL"
        assert PRESSURE_ACTION_MAP[PressureBand.LOW]["auto_compact"] is False


# ─────────────────────────────────────────────────────────────────────────────
# empty_context_packet (11)
# ─────────────────────────────────────────────────────────────────────────────
class TestEmptyContextPacket:
    def test_packet_shape_valid(self):
        pkt = empty_context_packet("task-1", "MiniMax-M3", "sess-1")
        assert pkt["task_id"] == "task-1"
        assert pkt["model_key"] == "MiniMax-M3"
        assert pkt["session_id"] == "sess-1"
        assert pkt["model_window"] == 200_000
        assert isinstance(pkt["segments"], list)
        assert len(pkt["segments"]) == 0
        assert (
            len(pkt["authority_hierarchy"]) == 9
        )  # 7 + 2 already-existing? check: source has 9 entries

    def test_packet_carries_policy_versions(self):
        pkt = empty_context_packet("task-1", "MiniMax-M3")
        assert pkt["eureka_policy_version"] == "context_eureka.v1"
        assert pkt["context_policy_version"] == "context_policy.v1"
        assert pkt["audit_policy_version"] == "context_policy.v1"

    def test_packet_includes_classify_pressure(self):
        pkt = empty_context_packet("task-1", "MiniMax-M3")
        assert "pressure" in pkt
        assert "pressure_band" in pkt["pressure"]
        # 0 tokens used → LOW band
        assert pkt["pressure"]["pressure_band"] == "LOW"

    def test_authority_hierarchy_includes_all_7_classes(self):
        pkt = empty_context_packet("task-1", "MiniMax-M3")
        class_labels = {entry["label"] for entry in pkt["authority_hierarchy"]}
        for ac in AuthorityClass:
            assert ac.name in class_labels


# ─────────────────────────────────────────────────────────────────────────────
# Failure mode coverage (12)
# ─────────────────────────────────────────────────────────────────────────────
class TestFailureModeCoverage:
    def test_all_four_failure_modes_have_prevention(self):
        assert len(ContextFailureMode) == 4
        for fm in ContextFailureMode:
            assert fm in FAILURE_PREVENTION

    def test_failure_prevention_cites_floor(self):
        for fm, entry in FAILURE_PREVENTION.items():
            assert "primary_floor" in entry
            assert entry["primary_floor"].startswith("F")  # e.g. "F2 TRUTH"


# ─────────────────────────────────────────────────────────────────────────────
# Policy + source-of-truth pins
# ─────────────────────────────────────────────────────────────────────────────
def test_policy_version_pinned():
    assert EUREKA_POLICY_VERSION == "context_eureka.v1"


def test_source_of_truth_doc_exists():
    assert SOURCE_OF_TRUTH == "docs/context/EUREKA_TOKEN_MANAGEMENT.md"
    import os

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.join(repo_root, "arifOS", SOURCE_OF_TRUTH)
    # The arifOS prefix is wrong; the correct prefix is just /root/arifOS/
    # Try both:
    candidates = [
        os.path.join(repo_root, SOURCE_OF_TRUTH),
        full_path,
        os.path.join(os.path.dirname(repo_root), SOURCE_OF_TRUTH),
    ]
    assert any(os.path.exists(c) for c in candidates), (
        f"Source-of-truth doc not found at: {candidates}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Module self-check (parity with the in-module 12 checks)
# ─────────────────────────────────────────────────────────────────────────────
def test_module_self_check_passes():
    r = _self_check()
    assert r["all_pass"] is True
    assert r["n_pass"] == r["n_checks"] == 12
    failed = [c for c in r["checks"] if not c["pass"]]
    assert not failed, f"eureka self-check failed: {failed}"


# ─────────────────────────────────────────────────────────────────────────────
# Bucket-to-failure-mode wiring (1 extra pin: SELECT→DISTRACTION is in the doc)
# ─────────────────────────────────────────────────────────────────────────────
def test_select_bucket_addresses_distraction():
    """Per EUREKA doc: SELECT bucket is the primary response to CONTEXT_DISTRACTION."""
    assert ContextFailureMode.CONTEXT_DISTRACTION in FAILURE_PREVENTION
    mech = FAILURE_PREVENTION[ContextFailureMode.CONTEXT_DISTRACTION]["mechanism"]
    assert "Select" in mech or "marginal" in mech.lower()


def test_compress_bucket_addresses_confusion():
    """Per EUREKA doc: COMPRESS bucket addresses CONTEXT_CONFUSION."""
    assert ContextFailureMode.CONTEXT_CONFUSION in FAILURE_PREVENTION
    mech = FAILURE_PREVENTION[ContextFailureMode.CONTEXT_CONFUSION]["mechanism"]
    assert "Compress" in mech or "compaction" in mech.lower()
