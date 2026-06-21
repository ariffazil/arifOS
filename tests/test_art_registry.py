"""
Tests for art_registry — W2 bucket classification + per-tool persistent state.

Doctrine reference: GENESIS/030_ART_VS_KERNEL.md §3 (WAJIB per-tool persistent ToolState)

DITEMPA BUKAN DIBERI — chaos compressor forged, 26 → 5 buckets.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.art_registry import (
    ArtRegistry,
    DEFAULT_TOOL_STATE,
    PER_BUCKET_BLAST,
    PER_BUCKET_REFLEX_RULES,
    TOOL_BUCKET,
    get_bucket,
    get_default_blast,
    get_default_tool_state,
    get_registry,
    get_reflex_rules,
)


# ── ALL 19 CANONICAL TOOLS CLASSIFIED ───────────────────────────────────────


class TestAllCanonicalClassified:
    """All 19 canonical arif_* tools must have a bucket."""

    CANONICAL_19 = [
        "arif_session_init", "arif_forge_execute", "arif_sense_observe",
        "arif_evidence_fetch", "arif_mind_reason", "arif_reply_compose",
        "arif_kernel_route", "arif_route", "arif_triage",
        "arif_kernel_status", "arif_kernel_attest", "arif_kernel_health",
        "arif_bridge", "arif_memory_recall", "arif_ops_measure",
        "arif_heart_critique", "arif_gateway_connect",
        "arif_judge_deliberate", "arif_vault_seal",
    ]

    def test_all_19_canonical_in_registry(self):
        for tool in self.CANONICAL_19:
            assert tool in TOOL_BUCKET, f"{tool} not classified"

    def test_all_19_canonical_have_default_state(self):
        for tool in self.CANONICAL_19:
            state = get_default_tool_state(tool)
            assert state in ("OBSERVED", "TRUSTED", "UNTRUSTED"), (
                f"{tool} has invalid default state: {state}"
            )

    def test_all_19_canonical_have_bucket(self):
        buckets = {get_bucket(t) for t in self.CANONICAL_19}
        assert None not in buckets, "Some canonical tools missing bucket"
        assert len(buckets) >= 4, f"Too few buckets for 19 tools: {buckets}"


class TestAllRegisteredToolsClassified:
    """All 26 tools exposed via MCP must be classified (canary probes too)."""

    REGISTERED_26 = [
        "arif_bridge", "arif_bridge_connect", "arif_conformance_report",
        "arif_evidence_fetch", "arif_forge_execute", "arif_gateway_connect",
        "arif_heart_critique", "arif_initialize_probe", "arif_judge_deliberate",
        "arif_kernel_attest", "arif_kernel_health", "arif_kernel_route",
        "arif_kernel_status", "arif_memory_recall", "arif_mind_reason",
        "arif_ops_measure", "arif_ping", "arif_reply_compose", "arif_route",
        "arif_schema_echo", "arif_sense_observe", "arif_session_init",
        "arif_transport_echo", "arif_triage", "arif_vault_seal",
        "arif_version_echo",
    ]

    def test_all_26_in_registry(self):
        for tool in self.REGISTERED_26:
            assert tool in TOOL_BUCKET, f"{tool} not classified"


# ── BUCKET BOUNDARIES ───────────────────────────────────────────────────────


class TestBucketBoundaries:
    """5-6 buckets maximum (chaos compression invariant)."""

    def test_max_6_buckets(self):
        buckets = set(TOOL_BUCKET.values())
        assert len(buckets) <= 6, f"Too many buckets: {len(buckets)}"

    def test_all_buckets_have_blast_radius(self):
        for bucket in set(TOOL_BUCKET.values()):
            assert bucket in PER_BUCKET_BLAST, f"{bucket} missing blast_radius"
            assert PER_BUCKET_BLAST[bucket] in ("low", "medium", "high")

    def test_all_buckets_have_reflex_rules(self):
        for bucket in set(TOOL_BUCKET.values()):
            rules = get_reflex_rules(bucket)
            assert "allow_action_class_above_observe" in rules
            assert "downgrade_to" in rules
            assert "trust_state_required" in rules


# ── PER-BUCKET BLAST RADIUS ────────────────────────────────────────────────


class TestPerBucketBlast:
    """Blast radius must match doctrine: sense=low, authority=high."""

    def test_sense_low_blast(self):
        assert PER_BUCKET_BLAST["sense"] == "low"

    def test_mind_low_blast(self):
        assert PER_BUCKET_BLAST["mind"] == "low"

    def test_heart_medium_blast(self):
        assert PER_BUCKET_BLAST["heart"] == "medium"

    def test_gateway_high_blast(self):
        assert PER_BUCKET_BLAST["gateway"] == "high"

    def test_bridge_high_blast(self):
        assert PER_BUCKET_BLAST["bridge"] == "high"

    def test_authority_high_blast(self):
        assert PER_BUCKET_BLAST["authority"] == "high"

    def test_get_default_blast_function(self):
        assert get_default_blast("sense") == "low"
        assert get_default_blast("authority") == "high"
        assert get_default_blast("nonexistent") == "unknown"


# ── PER-BUCKET REFLEX RULES ────────────────────────────────────────────────


class TestPerBucketReflexRules:
    """Each bucket has rules matching its risk profile."""

    def test_sense_observe_only(self):
        rules = get_reflex_rules("sense")
        assert rules["allow_action_class_above_observe"] is False
        assert rules["downgrade_to"] is None

    def test_mind_can_downgrade(self):
        rules = get_reflex_rules("mind")
        assert rules["allow_action_class_above_observe"] is True
        assert rules["downgrade_to"] == "observe"

    def test_authority_irreversible_no_downgrade(self):
        rules = get_reflex_rules("authority")
        assert rules["downgrade_to"] is None  # IRREVERSIBLE cannot safely downgrade

    def test_heart_requires_trust(self):
        rules = get_reflex_rules("heart")
        assert rules["trust_state_required"] == "TRUSTED"

    def test_gateway_requires_trust(self):
        rules = get_reflex_rules("gateway")
        assert rules["trust_state_required"] == "TRUSTED"

    def test_bridge_requires_trust(self):
        rules = get_reflex_rules("bridge")
        assert rules["trust_state_required"] == "TRUSTED"

    def test_authority_requires_trust(self):
        rules = get_reflex_rules("authority")
        assert rules["trust_state_required"] == "TRUSTED"


# ── PERSISTENT TOOL STATE (DOCTRINE WAJIB) ─────────────────────────────────


class TestPersistentToolState:
    """Per-tool persistent ToolState replaces hardcoded TRUSTED (MAKRUH-NOW fix)."""

    def test_all_tools_have_default_state(self):
        for tool in TOOL_BUCKET:
            state = get_default_tool_state(tool)
            assert state in ("OBSERVED", "TRUSTED", "UNTRUSTED")

    def test_default_state_is_observed_not_trusted(self):
        """Per doctrine: TRUSTED is earned, not given."""
        for tool in TOOL_BUCKET:
            state = get_default_tool_state(tool)
            assert state == "OBSERVED", (
                f"{tool} starts at {state} — should be OBSERVED (TRUSTED must be earned)"
            )

    def test_authority_tools_start_observed(self):
        """Authority bucket tools start OBSERVED — need earned TRUSTED for IRREVERSIBLE."""
        for tool in TOOL_BUCKET:
            if TOOL_BUCKET[tool] == "authority":
                assert get_default_tool_state(tool) == "OBSERVED"

    def test_unknown_tool_falls_back_to_trusted(self):
        """Backward compat: unknown tools default to TRUSTED (pre-W2 behavior)."""
        assert get_default_tool_state("unknown_tool_xyz") == "TRUSTED"

    def test_get_registry_singleton(self):
        """get_registry() returns same instance across calls."""
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_registry_caches_tool_state(self):
        """get_tool_state_cached returns same result on repeated calls."""
        r = get_registry()
        r.reset_cache()
        s1 = r.get_tool_state_cached("arif_forge_execute")
        s2 = r.get_tool_state_cached("arif_forge_execute")
        assert s1 == s2

    def test_registry_set_state_overrides(self):
        """set_tool_state updates cache."""
        r = get_registry()
        r.reset_cache()
        r.set_tool_state("arif_forge_execute", "FALLBACK")
        assert r.get_tool_state_cached("arif_forge_execute") == "FALLBACK"
        # restore for other tests
        r.set_tool_state("arif_forge_execute", "OBSERVED")


# ── CHAOS COMPRESSION ──────────────────────────────────────────────────────


class TestChaosCompression:
    """ART reduces chaos: 26 tools → 5-6 behavioural buckets."""

    def test_sense_is_largest_bucket(self):
        """Most tools should be sense (low risk, frequent use)."""
        sense_count = sum(1 for b in TOOL_BUCKET.values() if b == "sense")
        authority_count = sum(1 for b in TOOL_BUCKET.values() if b == "authority")
        assert sense_count >= authority_count

    def test_authority_is_small(self):
        """Authority bucket (IRREVERSIBLE lane) must be small."""
        authority_count = sum(1 for b in TOOL_BUCKET.values() if b == "authority")
        assert authority_count <= 6

    def test_bucket_stats_method(self):
        r = get_registry()
        stats = r.bucket_stats()
        assert "sense" in stats
        assert "authority" in stats
        assert sum(stats.values()) == len(TOOL_BUCKET)

    def test_tools_in_bucket_method(self):
        r = get_registry()
        sense_tools = r.tools_in_bucket("sense")
        assert "arif_sense_observe" in sense_tools
        assert "arif_ping" in sense_tools
        # sense bucket should NOT contain authority tools
        assert "arif_forge_execute" not in sense_tools

    def test_registered_count_matches(self):
        r = get_registry()
        assert r.registered_count() == len(TOOL_BUCKET)
