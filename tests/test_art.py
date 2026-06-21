"""
Test: ART — Agentic Recursive Tooling

Tests the complete reflex: state-based gates, POWER/TRUST/SYSTEM checks,
state transitions, and bool conversion.

DITEMPA BUKAN DIBERI — The reflex is forged. These tests prove it.
"""

import pytest
import sys
sys.path.insert(0, "/opt/arifos/app")

from arifosmcp.runtime.art import (
    art,
    ArtRequest,
    ArtResult,
    ArtVerdict,
    ArtReason,
    ToolState,
)


# ── STATE-BASED GATES ─────────────────────────────────────────────────


class TestStateGates:
    """CHECK 0: Tool lifecycle state enforcement."""

    def test_abandoned_block(self):
        """Abandoned tool → BLOCK regardless of action_class."""
        for action in ("observe", "mutate", "execute"):
            r = art(ArtRequest(action_class=action, tool_state="abandoned"))
            assert r.verdict == ArtVerdict.BLOCK, f"{action} on abandoned should BLOCK"
            assert r.reason == ArtReason.TOOL_ABANDONED

    def test_fallback_hold_mutate(self):
        """Fallback tool + mutate → HOLD."""
        r = art(ArtRequest(action_class="mutate", tool_state="fallback",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.TOOL_FALLBACK

    def test_fallback_hold_execute(self):
        """Fallback tool + execute → HOLD."""
        r = art(ArtRequest(action_class="execute", tool_state="fallback",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.TOOL_FALLBACK

    def test_fallback_proceed_observe(self):
        """Fallback tool + observe → PROCEED (still boleh observe)."""
        r = art(ArtRequest(action_class="observe", tool_state="fallback",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED

    def test_untrusted_observe_proceed(self):
        """Untrusted tool + observe → PROCEED."""
        r = art(ArtRequest(action_class="observe", tool_state="untrusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED

    def test_untrusted_mutate_default_observe(self):
        """Untrusted tool + mutate → DEFAULT_OBSERVE."""
        r = art(ArtRequest(action_class="mutate", tool_state="untrusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.DEFAULT_OBSERVE
        assert r.reason == ArtReason.TOOL_UNTRUSTED

    def test_observed_observe_proceed(self):
        """Observed tool + observe → PROCEED."""
        r = art(ArtRequest(action_class="observe", tool_state="observed",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED

    def test_observed_mutate_hold(self):
        """Observed tool + mutate → HOLD (propose only)."""
        r = art(ArtRequest(action_class="mutate", tool_state="observed",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.TOOL_OBSERVED_MUTATE

    def test_observed_execute_default_observe(self):
        """Observed tool + execute → DEFAULT_OBSERVE."""
        r = art(ArtRequest(action_class="execute", tool_state="observed",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.DEFAULT_OBSERVE
        assert r.reason == ArtReason.TOOL_OBSERVED_EXECUTE


# ── CHECK 1: POWER ────────────────────────────────────────────────────


class TestPowerCheck:
    """CHECK 1: Apa tool ni boleh buat pada aku?"""

    def test_unknown_blast_default_observe(self):
        """Unknown blast radius → DEFAULT_OBSERVE."""
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="unknown"))
        assert r.verdict == ArtVerdict.DEFAULT_OBSERVE
        assert r.reason == ArtReason.BLAST_RADIUS_UNKNOWN

    def test_irreversible_no_rollback_hold(self):
        """Mutate tanpa reversible → HOLD."""
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=False))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.IRREVERSIBLE_NO_ROLLBACK

    def test_execute_needs_ack(self):
        """Execute sentiasa HOLD."""
        r = art(ArtRequest(action_class="execute", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.EXECUTE_NEEDS_ACK


# ── CHECK 2: TRUST ────────────────────────────────────────────────────


class TestTrustCheck:
    """CHECK 2: Boleh aku percaya apa tool ni cakap?"""

    def test_unresolved_actor_block(self):
        """Mutate tanpa actor resolved → BLOCK."""
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=False, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.BLOCK
        assert r.reason == ArtReason.ACTOR_UNRESOLVED

    def test_unresolved_actor_observe_proceed(self):
        """Observe tanpa actor resolved → masih PROCEED (observe tak perlukan identity)."""
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=False, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED

    def test_trust_unknown_default_observe(self):
        """Unknown trust level → DEFAULT_OBSERVE."""
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="unknown"))
        assert r.verdict == ArtVerdict.DEFAULT_OBSERVE
        assert r.reason == ArtReason.TRUST_LEVEL_UNKNOWN

    def test_verdict_without_schema_hold(self):
        """Tool return verdict tapi schema unlocked → HOLD."""
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="verdict",
                           actor_resolved=True, schema_locked=False,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.VERDICT_WITHOUT_SCHEMA


# ── CHECK 3: SYSTEM STATE ─────────────────────────────────────────────


class TestSystemCheck:
    """CHECK 3: System sihat ke nak aku buat action ni?"""

    def test_degraded_mutate_hold(self):
        """Degraded system + mutate → HOLD."""
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=True, reversible=True))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.DEGRADED_MUTATION

    def test_degraded_observe_proceed(self):
        """Degraded system + observe → masih PROCEED."""
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=True, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED


# ── CLEAN PATHS ───────────────────────────────────────────────────────


class TestCleanPaths:
    """Semua check lulus — PROCEED."""

    def test_trusted_clean_observe(self):
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED
        assert r.reason == ArtReason.ALL_CHECKS_PASSED

    def test_trusted_clean_mutate(self):
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.verdict == ArtVerdict.PROCEED
        assert r.reason == ArtReason.ALL_CHECKS_PASSED


# ── UTILITY ───────────────────────────────────────────────────────────


class TestUtility:
    """Bool conversion dan ArtResult integrity."""

    def test_bool_proceed_true(self):
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert bool(r) is True

    def test_bool_hold_false(self):
        r = art(ArtRequest(action_class="execute", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert bool(r) is False

    def test_bool_block_false(self):
        r = art(ArtRequest(action_class="mutate", tool_state="abandoned"))
        assert bool(r) is False

    def test_result_always_has_check_blocked(self):
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert hasattr(r, "check_blocked")


# ── STATE TRANSITIONS ────────────────────────────────────────────────


class TestStateTransitions:
    """Tool lifecycle transitions — suggested next state."""

    def test_untrusted_to_observed(self):
        """First observe on untrusted → suggest OBSERVED."""
        r = art(ArtRequest(action_class="observe", tool_state="untrusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True))
        assert r.next_tool_state == ToolState.OBSERVED

    def test_observed_to_trusted(self):
        """Observed + low failure + schema locked → suggest TRUSTED."""
        r = art(ArtRequest(action_class="observe", tool_state="observed",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True,
                           failure_rate=0.02))
        assert r.next_tool_state == ToolState.TRUSTED

    def test_trusted_to_fallback_failure(self):
        """Trusted + high failure → suggest FALLBACK.
        
        Note: reason is still ALL_CHECKS_PASSED because no check blocked.
        The transition suggestion is in next_tool_state, not in reason.
        """
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True,
                           failure_rate=0.5))
        assert r.next_tool_state == ToolState.FALLBACK
        assert r.reason == ArtReason.ALL_CHECKS_PASSED  # no check blocked, just suggested

    def test_trusted_to_fallback_drift(self):
        """Trusted + drift ≥3 → suggest FALLBACK."""
        r = art(ArtRequest(action_class="mutate", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True,
                           drift_count=4))
        assert r.next_tool_state == ToolState.FALLBACK
        assert r.reason == ArtReason.ALL_CHECKS_PASSED

    def test_fallback_to_trusted(self):
        """Fallback + recovered → suggest TRUSTED."""
        r = art(ArtRequest(action_class="observe", tool_state="fallback",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True,
                           failure_rate=0.01))
        assert r.next_tool_state == ToolState.TRUSTED

    def test_fallback_to_abandoned(self):
        """Fallback + catastrophic → suggest ABANDONED."""
        r = art(ArtRequest(action_class="observe", tool_state="fallback",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True,
                           failure_rate=0.7, drift_count=6))
        assert r.next_tool_state == ToolState.ABANDONED

    def test_trusted_stale_to_abandoned(self):
        """Trusted + stale >90 days → suggest ABANDONED."""
        r = art(ArtRequest(action_class="observe", tool_state="trusted",
                           blast_radius="low", trust_level="evidence",
                           actor_resolved=True, schema_locked=True,
                           degraded=False, reversible=True,
                           days_since_use=95))
        assert r.next_tool_state == ToolState.ABANDONED
        assert r.reason == ArtReason.ALL_CHECKS_PASSED


# ── v3.1 — DISCOVERY SURFACE HARDENING ────────────────────────────────


class TestV31UnverifiedSchema:
    """E1: schema_verified=False + MUTATE/EXECUTE → DEFAULT_OBSERVE.

    Trust-on-first-hash. MCP server / user-supplied schemas without
    signature verification cannot run state-changing actions.
    """

    def _trusted_base(self, **overrides):
        """Build a baseline ArtRequest that would otherwise PROCEED."""
        base = dict(
            action_class="observe", tool_state="trusted",
            blast_radius="low", trust_level="evidence",
            actor_resolved=True, schema_locked=True,
            degraded=False, reversible=True,
            schema_verified=True,  # default to verified so test isolates E1
        )
        base.update(overrides)
        return ArtRequest(**base)

    def test_unverified_schema_downgrades_mutate(self):
        """E1: MUTATE + schema_verified=False → DEFAULT_OBSERVE."""
        r = art(self._trusted_base(action_class="mutate", schema_verified=False))
        assert r.verdict == ArtVerdict.DEFAULT_OBSERVE
        assert r.reason == ArtReason.UNVERIFIED_SCHEMA_SOURCE
        assert r.check_blocked == 2  # TRUST check

    def test_unverified_schema_execute_holds_earlier(self):
        """E1 + EXECUTE: EXECUTE always HOLDs (Check 1) before E1 can fire.
        E1 only downgrades MUTATE; EXECUTE has its own tighter gate."""
        r = art(self._trusted_base(action_class="execute", schema_verified=False))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.EXECUTE_NEEDS_ACK

    def test_unverified_schema_does_not_downgrade_observe(self):
        """E1: OBSERVE with unverified schema is still allowed (read is safe)."""
        r = art(self._trusted_base(action_class="observe", schema_verified=False))
        assert r.verdict == ArtVerdict.PROCEED
        assert r.reason == ArtReason.ALL_CHECKS_PASSED

    def test_verified_schema_proceeds(self):
        """E1: schema_verified=True → existing checks apply (sanity)."""
        r = art(self._trusted_base(action_class="mutate", schema_verified=True))
        assert r.verdict == ArtVerdict.PROCEED


class TestV31ExternalSurface:
    """E2: external_surface + MUTATE + not acknowledged_remote → HOLD.

    Closes Hermes #16462 (no first-call approval for MCP tools).
    Local mutation (mcp_filesystem_write) is unaffected.
    """

    def _trusted_base(self, **overrides):
        base = dict(
            action_class="mutate", tool_state="trusted",
            blast_radius="low", trust_level="evidence",
            actor_resolved=True, schema_locked=True,
            degraded=False, reversible=True,
            schema_verified=True,
            external_surface=False, acknowledged_remote=False,
        )
        base.update(overrides)
        return ArtRequest(**base)

    def test_external_mutate_unacknowledged_holds(self):
        """E2: MUTATE + external + not acked → HOLD."""
        r = art(self._trusted_base(
            action_class="mutate",
            external_surface=True,
            acknowledged_remote=False,
        ))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.EXTERNAL_SURFACE_UNACKNOWLEDGED
        assert r.check_blocked == 1  # POWER check

    def test_external_mutate_acknowledged_proceeds(self):
        """E2: MUTATE + external + acked → PROCEED."""
        r = art(self._trusted_base(
            action_class="mutate",
            external_surface=True,
            acknowledged_remote=True,
        ))
        assert r.verdict == ArtVerdict.PROCEED

    def test_local_mutate_unaffected(self):
        """E2: MUTATE + NOT external → PROCEED (no ack needed)."""
        r = art(self._trusted_base(
            action_class="mutate",
            external_surface=False,
            acknowledged_remote=False,
        ))
        assert r.verdict == ArtVerdict.PROCEED


class TestV31CumulativeSilentFallback:
    """E3: silent_fallback_count >= threshold (2) → HOLD.

    Catches cumulative drift that per-call STATE snapshots miss.
    Caller pushes the counter; reflex itself stays stateless.
    """

    def _trusted_base(self, **overrides):
        base = dict(
            action_class="observe", tool_state="trusted",
            blast_radius="low", trust_level="evidence",
            actor_resolved=True, schema_locked=True,
            degraded=False, reversible=True,
            schema_verified=True,
            silent_fallback_count=0,
        )
        base.update(overrides)
        return ArtRequest(**base)

    def test_silent_fallback_count_one_proceeds(self):
        """E3: 1 silent fallback → no downgrade (single fallback is fine)."""
        r = art(self._trusted_base(silent_fallback_count=1))
        assert r.verdict == ArtVerdict.PROCEED

    def test_silent_fallback_count_two_holds(self):
        """E3: 2 silent fallbacks → HOLD (catches cumulative drift)."""
        r = art(self._trusted_base(silent_fallback_count=2))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.CUMULATIVE_SILENT_FALLBACK
        assert r.check_blocked == 3  # SYSTEM check
        assert r.next_tool_state == ToolState.FALLBACK

    def test_silent_fallback_count_three_still_holds(self):
        """E3: 3+ silent fallbacks → still HOLD (no upper bound check)."""
        r = art(self._trusted_base(silent_fallback_count=5))
        assert r.verdict == ArtVerdict.HOLD
        assert r.reason == ArtReason.CUMULATIVE_SILENT_FALLBACK
