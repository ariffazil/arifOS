"""
Tests for EvidenceEnvelope — the universal evidence contract.
═══════════════════════════════════════════════════════════════

Covers:
  1. Construction + defaults
  2. Canonical hash computation
  3. Tier-layer allowance enforcement
  4. Temporal validity (valid_from, valid_until, is_expired, is_valid)
  5. Qdrant payload conversion (governance fields present)
  6. Graphiti edge conversion (validity windows present)
  7. VAULT999 seal candidate (canonical representation)
  8. Provenance-aware retrieval scoring
  9. Boundary cases (expired, future-dated, max confidence)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest

from arifosmcp.schemas.evidence_envelope import (
    AuthorityClass,
    DerivationMethod,
    EvidenceEnvelope,
    MemoryTier,
    PolicyLabel,
    SourceType,
    StorageLayer,
    TIER_LAYER_ALLOWANCE,
    provenance_score,
    tier_layer_allowed,
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _make_envelope(**kwargs) -> EvidenceEnvelope:
    """Create a minimal valid EvidenceEnvelope for testing."""
    defaults = {
        "actor_id": "qwen-code/FI-003",
        "claim": "The Volve field produces 120,000 bbl/day",
        "source_type": SourceType.TOOL,
        "source_locator": "geox://volve-wells/production-data",
    }
    defaults.update(kwargs)
    return EvidenceEnvelope(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CONSTRUCTION + DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstruction:
    def test_minimal_envelope(self):
        env = _make_envelope()
        assert env.actor_id == "qwen-code/FI-003"
        assert env.memory_tier == MemoryTier.M1
        assert env.storage_layer == StorageLayer.L3
        assert env.confidence == 0.5
        assert env.authority_class == AuthorityClass.UNVERIFIED
        assert env.tenant_id == "arifos"

    def test_event_id_is_uuid(self):
        env = _make_envelope()
        assert len(env.event_id) == 36  # UUID format
        assert env.event_id != env.trace_id  # Different UUIDs

    def test_custom_tier(self):
        env = _make_envelope(memory_tier=MemoryTier.M4, storage_layer=StorageLayer.L6)
        assert env.memory_tier == MemoryTier.M4
        assert env.storage_layer == StorageLayer.L6

    def test_extensions_default_empty(self):
        env = _make_envelope()
        assert env.extensions == {}

    def test_floors_default_empty(self):
        env = _make_envelope()
        assert env.floors == []

    def test_policy_labels_default_internal(self):
        env = _make_envelope()
        assert env.policy_labels == [PolicyLabel.INTERNAL]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CANONICAL HASH
# ═══════════════════════════════════════════════════════════════════════════════


class TestCanonicalHash:
    def test_hash_computed_from_claim(self):
        env = _make_envelope()
        expected = "sha256:" + hashlib.sha256(env.claim.encode("utf-8")).hexdigest()
        assert env.integrity.canonical_hash == expected

    def test_same_claim_same_hash(self):
        env1 = _make_envelope(event_id="test-1", trace_id="test-1")
        env2 = _make_envelope(event_id="test-2", trace_id="test-2")
        assert env1.integrity.canonical_hash == env2.integrity.canonical_hash

    def test_different_claim_different_hash(self):
        env1 = _make_envelope(claim="A")
        env2 = _make_envelope(claim="B")
        assert env1.integrity.canonical_hash != env2.integrity.canonical_hash

    def test_hash_starts_with_sha256_prefix(self):
        env = _make_envelope()
        assert env.integrity.canonical_hash.startswith("sha256:")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. TIER-LAYER ALLOWANCE
# ═══════════════════════════════════════════════════════════════════════════════


class TestTierLayerAllowance:
    def test_m0_allows_l1_l2(self):
        assert tier_layer_allowed(MemoryTier.M0, StorageLayer.L1)
        assert tier_layer_allowed(MemoryTier.M0, StorageLayer.L2)
        assert not tier_layer_allowed(MemoryTier.M0, StorageLayer.L3)
        assert not tier_layer_allowed(MemoryTier.M0, StorageLayer.L6)

    def test_m4_allows_only_l6(self):
        assert tier_layer_allowed(MemoryTier.M4, StorageLayer.L6)
        assert not tier_layer_allowed(MemoryTier.M4, StorageLayer.L3)
        assert not tier_layer_allowed(MemoryTier.M4, StorageLayer.L1)

    def test_m2_allows_l3_l4(self):
        assert tier_layer_allowed(MemoryTier.M2, StorageLayer.L3)
        assert tier_layer_allowed(MemoryTier.M2, StorageLayer.L4)
        assert not tier_layer_allowed(MemoryTier.M2, StorageLayer.L1)
        assert not tier_layer_allowed(MemoryTier.M2, StorageLayer.L6)

    def test_m1_allows_l1_l2_l3(self):
        assert tier_layer_allowed(MemoryTier.M1, StorageLayer.L1)
        assert tier_layer_allowed(MemoryTier.M1, StorageLayer.L2)
        assert tier_layer_allowed(MemoryTier.M1, StorageLayer.L3)
        assert not tier_layer_allowed(MemoryTier.M1, StorageLayer.L4)

    def test_m3_allows_l4_l5(self):
        assert tier_layer_allowed(MemoryTier.M3, StorageLayer.L4)
        assert tier_layer_allowed(MemoryTier.M3, StorageLayer.L5)
        assert not tier_layer_allowed(MemoryTier.M3, StorageLayer.L3)
        assert not tier_layer_allowed(MemoryTier.M3, StorageLayer.L6)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. TEMPORAL VALIDITY
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemporalValidity:
    def test_no_dates_is_always_valid(self):
        env = _make_envelope()
        assert env.is_valid()
        assert not env.is_expired()

    def test_expired_envelope(self):
        env = _make_envelope(
            valid_until=(datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        )
        assert env.is_expired()
        assert not env.is_valid()

    def test_future_valid_from(self):
        env = _make_envelope(
            valid_from=(datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        )
        assert not env.is_valid()

    def test_valid_window(self):
        now = datetime.now(UTC)
        env = _make_envelope(
            valid_from=(now - timedelta(hours=1)).isoformat(),
            valid_until=(now + timedelta(hours=1)).isoformat(),
        )
        assert env.is_valid()
        assert not env.is_expired()


# ═══════════════════════════════════════════════════════════════════════════════
# 5. QDRANT PAYLOAD
# ═══════════════════════════════════════════════════════════════════════════════


class TestQdrantPayload:
    def test_all_governance_fields_present(self):
        env = _make_envelope(
            memory_tier=MemoryTier.M3,
            authority_class=AuthorityClass.CORROBORATED,
            policy_labels=[PolicyLabel.INTERNAL, PolicyLabel.CONSTITUTIONAL],
            valid_until=(datetime.now(UTC) + timedelta(days=90)).isoformat(),
        )
        payload = env.to_qdrant_payload()

        required_fields = [
            "event_id", "trace_id", "actor_id", "tenant_id",
            "memory_tier", "storage_layer", "claim",
            "source_type", "source_locator", "source_hash",
            "observed_at", "recorded_at", "valid_from", "valid_until",
            "derivation_method", "parent_event_ids", "model_id", "tool_id",
            "confidence", "authority_class", "policy_labels",
            "canonical_hash", "previous_seal", "signature",
            "floors", "requires_888", "vault_event_id",
        ]
        for field in required_fields:
            assert field in payload, f"Missing field: {field}"

    def test_policy_labels_are_values(self):
        env = _make_envelope(
            policy_labels=[PolicyLabel.SENSITIVE, PolicyLabel.FINANCIAL],
        )
        payload = env.to_qdrant_payload()
        assert "sensitive" in payload["policy_labels"]
        assert "financial" in payload["policy_labels"]

    def test_derivation_fields_flattened(self):
        env = _make_envelope(
            derivation={
                "method": DerivationMethod.INFERRED,
                "parent_event_ids": ["evt-1", "evt-2"],
                "model_id": "deepseek-v4-pro",
                "tool_id": "geox.geox_basin",
            },
        )
        payload = env.to_qdrant_payload()
        assert payload["derivation_method"] == "inferred"
        assert payload["parent_event_ids"] == ["evt-1", "evt-2"]
        assert payload["model_id"] == "deepseek-v4-pro"
        assert payload["tool_id"] == "geox.geox_basin"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. GRAPHITI EDGE
# ═══════════════════════════════════════════════════════════════════════════════


class TestGraphitiEdge:
    def test_validity_window_in_edge(self):
        now = datetime.now(UTC)
        env = _make_envelope(
            valid_from=(now - timedelta(days=30)).isoformat(),
            valid_until=(now + timedelta(days=60)).isoformat(),
        )
        edge = env.to_graphiti_edge()

        assert edge["valid_from"] is not None
        assert edge["valid_until"] is not None
        assert edge["is_expired"] is False

    def test_source_event_ids_in_edge(self):
        env = _make_envelope(
            derivation={
                "method": DerivationMethod.AGGREGATED,
                "parent_event_ids": ["parent-1", "parent-2"],
                "model_id": None,
                "tool_id": None,
            },
        )
        edge = env.to_graphiti_edge()
        assert edge["source_event_ids"] == ["parent-1", "parent-2"]

    def test_expired_edge(self):
        env = _make_envelope(
            valid_until=(datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        )
        edge = env.to_graphiti_edge()
        assert edge["is_expired"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# 7. VAULT999 SEAL CANDIDATE
# ═══════════════════════════════════════════════════════════════════════════════


class TestVaultCandidate:
    def test_seal_candidate_has_l6(self):
        env = _make_envelope(storage_layer=StorageLayer.L3)
        candidate = env.to_vault_candidate()
        assert candidate["storage_layer"] == "L6"

    def test_seal_candidate_has_integrity_block(self):
        env = _make_envelope()
        candidate = env.to_vault_candidate()
        assert "canonical_hash" in candidate["integrity"]
        assert "previous_seal" in candidate["integrity"]
        assert "signature" in candidate["integrity"]

    def test_seal_candidate_has_derivation_block(self):
        env = _make_envelope()
        candidate = env.to_vault_candidate()
        assert "method" in candidate["derivation"]
        assert "parent_event_ids" in candidate["derivation"]


# ═══════════════════════════════════════════════════════════════════════════════
# 8. PROVENANCE-AWARE SCORING
# ═══════════════════════════════════════════════════════════════════════════════


class TestProvenanceScoring:
    def test_zero_relevance_gives_zero_score(self):
        env = _make_envelope()
        score = provenance_score(env, semantic_relevance=0.0)
        assert score == 0.0

    def test_full_relevance_sealed_gives_max(self):
        env = _make_envelope(authority_class=AuthorityClass.SEALED)
        score = provenance_score(env, semantic_relevance=1.0, freshness_days=0)
        # 1.0 * 1.0 * 1.0 * 1.0 * 1.0 = 1.0
        assert score == 1.0

    def test_unverified_has_lower_weight(self):
        env_unverified = _make_envelope(authority_class=AuthorityClass.UNVERIFIED)
        env_sealed = _make_envelope(authority_class=AuthorityClass.SEALED)
        s1 = provenance_score(env_unverified, semantic_relevance=1.0, freshness_days=0)
        s2 = provenance_score(env_sealed, semantic_relevance=1.0, freshness_days=0)
        assert s1 < s2  # unverified < sealed

    def test_corroboration_bonus(self):
        env = _make_envelope(authority_class=AuthorityClass.CORROBORATED)
        s_no = provenance_score(env, semantic_relevance=1.0, freshness_days=0, corroboration_count=0)
        s_yes = provenance_score(env, semantic_relevance=1.0, freshness_days=0, corroboration_count=3)
        assert s_yes > s_no

    def test_expired_envelope_scores_zero(self):
        env = _make_envelope(
            valid_until=(datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        )
        score = provenance_score(env, semantic_relevance=1.0)
        assert score == 0.0

    def test_freshness_decay(self):
        env = _make_envelope()
        s_new = provenance_score(env, semantic_relevance=1.0, freshness_days=0)
        s_old = provenance_score(env, semantic_relevance=1.0, freshness_days=180)
        assert s_new > s_old

    def test_score_capped_at_two(self):
        env = _make_envelope(authority_class=AuthorityClass.SEALED)
        score = provenance_score(
            env, semantic_relevance=1.0, freshness_days=0, corroboration_count=10
        )
        assert score <= 2.0


# ═══════════════════════════════════════════════════════════════════════════════
# 9. BOUNDARY CASES
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundaryCases:
    def test_empty_claim(self):
        env = _make_envelope(claim="")
        assert env.claim == ""
        assert env.integrity.canonical_hash.startswith("sha256:")

    def test_very_long_claim(self):
        long_claim = "x" * 1_000_000
        env = _make_envelope(claim=long_claim)
        assert len(env.claim) == 1_000_000

    def test_unicode_claim(self):
        env = _make_envelope(claim="Ditempa bukan diberi 🔥")
        assert "🔥" in env.claim

    def test_max_confidence(self):
        env = _make_envelope(confidence=1.0)
        assert env.confidence == 1.0

    def test_zero_confidence(self):
        env = _make_envelope(confidence=0.0)
        assert env.confidence == 0.0

    def test_many_policy_labels(self):
        labels = list(PolicyLabel)
        env = _make_envelope(policy_labels=labels)
        assert len(env.policy_labels) == len(labels)
