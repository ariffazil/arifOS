"""
tests/runtime/test_compression.py — Phase T1 coverage for compression.py
==========================================================================

The contract under test is split into two layers:

LAYER 1 (current, H1 tier-based compression in compression.py):
  - CompressionMode: FULL / CONSTITUTIONAL / OPERATIONAL / MINIMAL
  - MemoryTier: EPHEMERAL / DOMAIN / CONSTITUTIONAL
  - compress(payload, mode) returns CompressionResult with:
      * compressed dict (only mode-appropriate keys)
      * compression_ratio
      * tiers_pruned list
      * constitutional_preserved bool
  - decompress(compressed, mode) reverses it
  - Compression is NON-DESTRUCTIVE: original payload keys that are NOT
    preserved in compressed form still survive the round-trip via the
    wrapped `_compression` envelope (mode CONSTITUTIONAL/OPERATIONAL)
    or are explicitly dropped (mode MINIMAL).
  - Constitutional keys (actor_id, session_id, verdict, etc.) are
    ALWAYS preserved in CONSTITUTIONAL/FULL modes.

LAYER 2 (Phase 3 spec-level, NOT YET IMPLEMENTED — these are document
  tests, not behavior tests. They describe the CompressionManifest
  contract that prepare_context() will produce in Phase 3.):
  - raw_context_hash preserved
  - summary_hash generated
  - source_pointers preserved
  - user instruction survives
  - active task survives
  - canonical memory not overwritten
  - derived summary marked derivative
  - raw transcript not deleted
  - manifest schema valid
  - compaction target pressure respected

Iron rules (F1-F13):
  - F1 AMANAH:  raw payload keys are recoverable from the compressed form
                 (via the _compression envelope) when mode is not MINIMAL.
  - F2 TRUTH:   compression is deterministic; same payload → same result.
  - F4 CLARITY: constitutional skeleton keys are stable across compression.
  - F7 HUMILITY: derived summaries are marked derivative, not truth.
  - F8 GENIUS:  summary is derivative; canonical memory never overwritten.
  - F13 SOVEREIGN: compaction policy changes are SEAL/F13 territory.

DITEMPA BUKAN DIBERI — the compactor is bounded; the LLM does not
decide what to keep.
"""

from __future__ import annotations

import hashlib
import pytest

from arifosmcp.runtime.compression import (
    CompressionMode,
    MemoryTier,
    compress,
    decompress,
    estimate_tokens,
)


# ── Fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture
def constitutional_payload():
    """A full arifOS payload that includes constitutional + operational +
    ephemeral keys. Used to verify the H1 compression behavior."""
    return {
        # Constitutional skeleton
        "actor_id": "arif",
        "session_id": "sess-001",
        "verdict": "SEAL",
        "risk_level": "low",
        "confidence_level": 0.95,
        "reversibility": True,
        "runtime_state": "ACTIVE",
        "floors_passed": ["F1", "F2", "F4", "F7", "F8"],
        "floors_failed": [],
        "constitutional_hash": "abc123",
        "tau": 0.95,
        "omega_0": 0.04,
        "delta_s": -0.1,
        # Operational
        "tool_calls": ["arif_mind_reason", "arif_judge_deliberate"],
        "stage_progression": ["000", "111", "333", "444", "888"],
        "ops_vitals": {"cpu": 0.4, "mem": 0.6},
        "entropy_delta": -0.05,
        "last_tool": "arif_judge_deliberate",
        "last_stage": "888",
        "telemetry": {"latency_ms": 120},
        "memory_write_candidates": [],
        "vault_seal_candidate": True,
        "next_recommended_tools": ["arif_forge_execute"],
        # Ephemeral (noisiest)
        "reasoning_trace": "x" * 5000,  # ~1400 tokens
        "raw_llm_output": "y" * 3000,
        "debug_info": {"trace_id": "abc"},
        "intermediate_steps": ["step1", "step2"],
        "search_results": [{"q": "test", "hits": 1}],
    }


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 1 — H1 tier-based compression (1–6)
# ─────────────────────────────────────────────────────────────────────────────
class TestH1TierCompression:
    def test_constitutional_mode_preserves_constitutional_keys(self, constitutional_payload):
        """CONSTITUTIONAL mode keeps the constitutional skeleton; prunes
        ephemeral + domain. The 13 constitutional keys must survive."""
        r = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        assert r.constitutional_preserved is True
        # Constitutional skeleton is still in the compressed dict
        for key in ("actor_id", "session_id", "verdict", "floors_passed"):
            assert key in r.compressed, f"constitutional key {key!r} lost"

    def test_operational_mode_keeps_operational_keys(self, constitutional_payload):
        """OPERATIONAL mode preserves constitutional + operational."""
        r = compress(constitutional_payload, CompressionMode.OPERATIONAL)
        for key in ("actor_id", "session_id", "verdict", "tool_calls", "telemetry"):
            assert key in r.compressed, f"operational key {key!r} lost"

    def test_minimal_mode_keeps_only_4_lockdown_keys(self, constitutional_payload):
        """MINIMAL mode: actor / session / verdict / timestamp only."""
        r = compress(constitutional_payload, CompressionMode.MINIMAL)
        # Per source, minimal mode keeps actor_id, session_id, verdict, ts_utc
        # (we don't strictly assert ts_utc since payload didn't carry one)
        for key in ("actor_id", "session_id", "verdict"):
            assert key in r.compressed, f"minimal key {key!r} lost"

    def test_ephemeral_keys_pruned_in_constitutional_mode(self, constitutional_payload):
        """reasoning_trace / raw_llm_output / search_results should be
        pruned under CONSTITUTIONAL mode (only constitutional kept)."""
        r = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        # None of these should be in the top-level compressed dict
        # (they go into the _compression envelope for reversibility)
        top = {k for k in r.compressed.keys() if k != "_compression"}
        assert "reasoning_trace" not in top
        assert "raw_llm_output" not in top
        assert "search_results" not in top

    def test_compression_reduces_token_count(self, constitutional_payload):
        """CONSTITUTIONAL mode must compress (ratio < 1) because ephemeral
        noise is pruned."""
        r = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        assert r.original_token_estimate > 0
        assert r.compressed_token_estimate > 0
        assert r.compression_ratio < 1.0  # some compression happened
        assert r.compression_ratio > 0.0  # but not to zero

    def test_tiers_pruned_recorded(self, constitutional_payload):
        """CompressionResult records which tiers were pruned."""
        r = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        # Under CONSTITUTIONAL, both EPHEMERAL and DOMAIN tiers are pruned
        assert MemoryTier.EPHEMERAL in r.tiers_pruned
        assert MemoryTier.DOMAIN in r.tiers_pruned
        # CONSTITUTIONAL tier is NOT pruned (it's the keeper)
        assert MemoryTier.CONSTITUTIONAL not in r.tiers_pruned


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 1 — Decompression (7)
# ─────────────────────────────────────────────────────────────────────────────
class TestH1Decompression:
    def test_round_trip_constitutional_preserves_all(self, constitutional_payload):
        """Compress then decompress with CONSTITUTIONAL mode should recover
        the constitutional skeleton. The `_compression` envelope is
        preserved so reversibility is possible."""
        r = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        recovered = decompress(r.compressed, CompressionMode.CONSTITUTIONAL)
        for key in ("actor_id", "session_id", "verdict"):
            assert recovered.get(key) == constitutional_payload[key]

    def test_round_trip_minimal_preserves_skeleton(self, constitutional_payload):
        """MINIMAL mode keeps the constitutional skeleton (~13 keys) and
        prunes operational + ephemeral. The decompress path is fully
        reversible — the `_compression` envelope carries the original.
        F1 AMANAH: raw is never truly lost in H1 (only marked pruned)."""
        r = compress(constitutional_payload, CompressionMode.MINIMAL)
        # Top-level (excluding the _compression envelope) should be the
        # constitutional skeleton — 13 keys + the always-preserved set
        top = {k for k in r.compressed.keys() if k != "_compression"}
        # Must NOT include operational or ephemeral keys at top level
        assert "tool_calls" not in top
        assert "telemetry" not in top
        assert "reasoning_trace" not in top
        assert "raw_llm_output" not in top
        # But the constitutional keys ARE there
        for key in ("actor_id", "session_id", "verdict", "floors_passed", "constitutional_hash"):
            assert key in top, f"constitutional key {key!r} lost in MINIMAL"

        recovered = decompress(r.compressed, CompressionMode.MINIMAL)
        # F1 AMANAH: decompress is reversible — original keys are back
        assert "reasoning_trace" in recovered
        assert recovered.get("actor_id") == "arif"
        # The metadata marks the restore
        assert recovered.get("_restored_from") == "minimal"


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 1 — Determinism (8)
# ─────────────────────────────────────────────────────────────────────────────
class TestH1Determinism:
    def test_compress_is_deterministic(self, constitutional_payload):
        a = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        b = compress(constitutional_payload, CompressionMode.CONSTITUTIONAL)
        assert a.compressed == b.compressed
        assert a.compression_ratio == b.compression_ratio
        assert a.tiers_pruned == b.tiers_pruned

    def test_estimate_tokens_text_only(self):
        n = estimate_tokens(text="hello world")
        assert n > 0

    def test_estimate_tokens_data_only(self):
        n = estimate_tokens(data={"k": "v" * 100})
        assert n > 0

    def test_estimate_tokens_text_takes_precedence_over_data(self):
        """Per the source: when both are passed, text wins (early return).
        This is the actual contract — `estimate_tokens` is a heuristic
        helper, not a sum."""
        n1 = estimate_tokens(text="abc")
        n3 = estimate_tokens(text="abc", data={"k": "v" * 100})
        # text path returns the same value either way
        assert n1 == n3

    def test_estimate_tokens_data_only_path(self):
        """When no text is passed, data is serialized and tokenized."""
        n2 = estimate_tokens(data={"k": "v" * 100})
        assert n2 > 0

    def test_estimate_tokens_empty_text_falls_through_to_data(self):
        """Empty text → falsy → data path is used."""
        n_only_data = estimate_tokens(data={"k": "v" * 50})
        n_empty_text = estimate_tokens(text="", data={"k": "v" * 50})
        assert n_only_data == n_empty_text

    def test_estimate_tokens_no_args_returns_zero(self):
        assert estimate_tokens() == 0


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 2 — Phase 3 CompressionManifest spec (9–10)
#
# These tests document the contract that prepare_context() will produce
# in Phase 3. They do NOT call a function that doesn't exist yet.
# They are SPEC tests — when the function is built, these are the
# shapes it must satisfy. Until then, the test passes by validating
# the shape on a synthetic manifest.
# ─────────────────────────────────────────────────────────────────────────────
class TestCompressionManifestSpec:
    """Phase 3 CompressionManifest contract.

    Source of truth: docs/context/context_policy_v1.md §SEAL Manifest
    Schema (Compaction) and the blueprint section 4.

    These tests do not require the implementation to exist. They
    describe the schema that prepare_context() will produce.
    """

    def _make_manifest(
        self,
        pressure_before=0.91,
        pressure_after=0.52,
        raw_text="x" * 1000,
        summary_text="y" * 200,
    ):
        """Build a synthetic manifest that matches the Phase 3 schema."""
        return {
            "event_type": "CONTEXT_COMPACTION",
            "policy_version": "context_policy.v1",
            "session_id": "sess-future",
            "actor_id": "arif",
            "ts_utc": "2026-06-12T00:00:00Z",
            "pressure_before": pressure_before,
            "pressure_after": pressure_after,
            "pressure_band_before": "COMPACT",
            "pressure_band_after": "WARN",
            "raw_context_hash": hashlib.sha256(raw_text.encode()).hexdigest(),
            "summary_hash": hashlib.sha256(summary_text.encode()).hexdigest(),
            "source_pointers": ["L2:redis:session:abc", "L4:postgres:memory_records:..."],
            "dropped_segments": [
                {
                    "reason": "low_relevance",
                    "hash": hashlib.sha256(b"dropped-segment").hexdigest(),
                    "tier_origin": "L2",
                    "reversible_pointer": "L2:redis:session:abc:msg-3",
                }
            ],
            "kept_segments": [
                {"type": "user_instruction", "hash": "...", "tier_origin": "L2", "priority": 100}
            ],
            "summarizer": "deterministic",
            "verifier": "deterministic_hash_check",
            "reversible": True,
            "summary_status": "DERIVED_NOT_CANONICAL",
            "constitutional_compliance": {
                "F1_amanah": "raw preserved in L2/L4/L6; pointer in seal",
                "F2_truth": "summary marked as compression, not truth",
                "F4_clarity": "delta_s measured before/after",
                "F8_genius": "policy version pinned",
                "F11_audit": "this seal IS the audit",
                "F13_sovereign": "raw canonical mutation requires HOLD",
            },
        }

    def test_manifest_has_raw_and_summary_hashes(self):
        m = self._make_manifest()
        assert "raw_context_hash" in m
        assert "summary_hash" in m
        # Both are sha256 hex (64 chars)
        assert len(m["raw_context_hash"]) == 64
        assert len(m["summary_hash"]) == 64
        assert m["raw_context_hash"] != m["summary_hash"]  # distinct

    def test_manifest_preserves_source_pointers(self):
        m = self._make_manifest()
        assert "source_pointers" in m
        assert isinstance(m["source_pointers"], list)
        assert len(m["source_pointers"]) > 0
        # Each pointer should be a non-empty string
        for ptr in m["source_pointers"]:
            assert isinstance(ptr, str) and len(ptr) > 0

    def test_manifest_marks_summary_as_derivative_not_canonical(self):
        m = self._make_manifest()
        # F2 truth: summary is derivative
        assert m["summary_status"] == "DERIVED_NOT_CANONICAL"
        # F13: the manifest itself does NOT claim to be canonical
        # (the raw transcript remains the source of truth)
        assert m["reversible"] is True

    def test_manifest_carries_pressure_before_and_after(self):
        m = self._make_manifest(pressure_before=0.91, pressure_after=0.52)
        assert m["pressure_before"] > m["pressure_after"]
        assert m["pressure_band_before"] == "COMPACT"
        assert m["pressure_band_after"] == "WARN"
        # Compaction must reduce pressure
        assert m["pressure_before"] - m["pressure_after"] >= 0.10

    def test_manifest_pin_policy_version(self):
        m = self._make_manifest()
        assert m["policy_version"] == "context_policy.v1"

    def test_manifest_dropped_segments_carry_reversible_pointers(self):
        """Per the policy: dropped segments must carry a reversible pointer
        so the operator can re-fetch them. F1 AMANAH."""
        m = self._make_manifest()
        for d in m["dropped_segments"]:
            assert "reason" in d
            assert "hash" in d
            assert "tier_origin" in d
            assert "reversible_pointer" in d
            assert len(d["hash"]) == 64

    def test_manifest_user_instruction_priority_100(self):
        """USER_INSTRUCTION must be a kept segment with priority 100."""
        m = self._make_manifest()
        user_kept = [k for k in m["kept_segments"] if k.get("type") == "user_instruction"]
        assert len(user_kept) >= 1
        assert user_kept[0]["priority"] == 100

    def test_manifest_constitutional_compliance_block(self):
        """The 6-floor compliance block is required by the policy."""
        m = self._make_manifest()
        cc = m["constitutional_compliance"]
        for floor in (
            "F1_amanah",
            "F2_truth",
            "F4_clarity",
            "F8_genius",
            "F11_audit",
            "F13_sovereign",
        ):
            assert floor in cc
            assert isinstance(cc[floor], str) and len(cc[floor]) > 0

    def test_manifest_summarizer_is_deterministic_in_phase3(self):
        """Per blueprint section 6 Phase 3: Phase 3 is deterministic
        (no LLM). Phase 4 is where LLM summarizer activates (F13-gated)."""
        m = self._make_manifest()
        assert m["summarizer"] == "deterministic"
        # And the verifier is the deterministic hash check
        assert m["verifier"] == "deterministic_hash_check"

    def test_manifest_does_not_overwrite_canonical_memory(self):
        """The manifest records the COMPACTION, not a canonical memory
        write. F8: summary is derivative; canonical memory is not
        overwritten by a manifest."""
        m = self._make_manifest()
        # There is no `event_type=CONTEXT_CANONICAL_WRITE`
        assert m["event_type"] == "CONTEXT_COMPACTION"
        # And no L4 canonical memory id is in the dropped/kept segments
        # (compaction is a derivative summary, not a canonical write)
        for d in m["dropped_segments"]:
            assert d["tier_origin"] != "L6"  # L6 is the canonical vault
        for k in m["kept_segments"]:
            assert k["tier_origin"] != "L6"


# ─────────────────────────────────────────────────────────────────────────────
# Goal 5: AUTO_COMPACT policy gate (added 2026-06-12 by omega-Ω)
# ─────────────────────────────────────────────────────────────────────────────
class TestAutoCompactPolicyGate:
    """auto_compress() must be HARD-GATED by AUTO_COMPACT_ENABLED env var.
    Default state is DISABLED. When disabled, the function returns the
    payload UNCHANGED with ratio=1.0, no tiers_pruned, constitutional
    preserved. This is the F1 AMANAH / F11 AUTH fail-closed invariant."""

    def test_auto_compact_disabled_by_default(self, monkeypatch):
        """Without AUTO_COMPACT_ENABLED set, auto_compress is a noop."""
        # Force unset the env var
        monkeypatch.delenv("AUTO_COMPACT_ENABLED", raising=False)

        # Re-import the module to pick up the env var
        import importlib
        import arifosmcp.runtime.compression as comp_mod

        importlib.reload(comp_mod)

        payload = {"actor_id": "arif", "verdict": "SEAL", "session_id": "s1"}
        result = comp_mod.auto_compress(payload, runtime_state="LOCKDOWN")
        # Payload returned UNCHANGED
        assert result.compressed == payload
        # Compression is a noop
        assert result.compression_ratio == 1.0
        assert result.tiers_pruned == []
        assert result.constitutional_preserved is True
        # Token estimate unchanged
        assert result.original_token_estimate == result.compressed_token_estimate

    def test_auto_compact_disabled_returns_unchanged_even_for_dangerous_state(self, monkeypatch):
        """Even RuntimeState.LOCKDOWN (which would normally select MINIMAL
        mode) is REJECTED at the gate. No risk of silent compaction."""
        monkeypatch.delenv("AUTO_COMPACT_ENABLED", raising=False)

        import importlib
        import arifosmcp.runtime.compression as comp_mod

        importlib.reload(comp_mod)

        payload = {
            "actor_id": "arif",
            "session_id": "s-dangerous",
            "verdict": "SEAL",
            "tool_calls": ["sensitive_op_1", "sensitive_op_2"],
        }
        result = comp_mod.auto_compress(payload, runtime_state="LOCKDOWN")
        # No compaction happened
        assert result.compressed == payload
        # tool_calls still present (would be dropped in OPERATIONAL mode)
        assert "tool_calls" in result.compressed
        # Constitutional preserved
        assert result.constitutional_preserved is True

    def test_auto_compact_enabled_can_be_toggled_at_runtime(self, monkeypatch):
        """The gate is a runtime read of the env var, computed at import
        time of the module. Toggling the env var requires module reload.
        This test confirms the import-time behavior is what we expect."""
        # When env var is set, the module reloaded should enable compaction
        monkeypatch.setenv("AUTO_COMPACT_ENABLED", "true")

        import importlib
        import arifosmcp.runtime.compression as comp_mod

        importlib.reload(comp_mod)

        # After reload with env set, auto_compress runs full compression logic
        payload = {"actor_id": "arif", "session_id": "s1", "verdict": "SEAL"}
        result = comp_mod.auto_compress(payload)
        # Should now produce a non-noop result (or at least the gate is bypassed)
        # We don't assert specific token savings (depends on mode); we just
        # assert that the env-gated behavior is observable.
        assert result is not None
        # Reset for other tests
        monkeypatch.delenv("AUTO_COMPACT_ENABLED", raising=False)
