"""
test_phoenix_72_entropy_rot.py — v38.2 Entropy Rot + SUNSET Tests

Tests for v38.2 Constitutional Hardening:
1. test_entropy_decay() — PARTIAL > 72h → VOID
2. test_sabar_escalation() — SABAR > 24h → PARTIAL
3. test_sunset_revocation() — SUNSET moves LEDGER → PHOENIX

Per: spec/arifos_v38_2.yaml
Canon: canon/000_ARIFOS_CANON_v35Omega.md §§6–8

Invariants tested:
- TIME-1: "Time is a Constitutional Force. Entropy Rot is automatic."
- TIME-2: "Hope has a half-life; governance does not."

Author: arifOS Project
Version: v38.2
"""

import pytest
from datetime import datetime, timezone, timedelta

from arifos_core.system.kernel import (
    VerdictPacket,
    EntropyRotResult,
    check_entropy_rot,
    route_memory,
    SABAR_TIMEOUT_HOURS,
    PHOENIX_LIMIT_HOURS,
)
from arifos_core.memory.bands import (
    MemoryBandRouter,
    BandName,
)
from arifos_core.memory.policy import Verdict, VERDICT_BAND_ROUTING


# =============================================================================
# HELPERS
# =============================================================================

def _make_timestamp_hours_ago(hours: float) -> str:
    """Create an ISO timestamp from `hours` hours ago."""
    ts = datetime.now(timezone.utc) - timedelta(hours=hours)
    return ts.isoformat(timespec="milliseconds").replace("+00:00", "Z")


# =============================================================================
# TEST 1: ENTROPY DECAY (PARTIAL > 72h → VOID)
# =============================================================================

class TestEntropyDecay:
    """
    Test PARTIAL verdicts decay to VOID after PHOENIX_LIMIT (72 hours).

    Per spec/arifos_v38_2.yaml::scheduler.phoenix_limit:
    - value: "72h"
    - effect: "PARTIAL -> VOID"
    - rule: "If verdict == PARTIAL and age > 72h, decay to VOID (entropy dump)."
    """

    def test_partial_decays_to_void_after_73_hours(self):
        """PARTIAL verdict older than 72h should decay to VOID."""
        packet = VerdictPacket(
            verdict="PARTIAL",
            timestamp=_make_timestamp_hours_ago(73),  # 73 hours old
        )

        result = check_entropy_rot(packet)

        assert result.rotted is True
        assert result.original_verdict == "PARTIAL"
        assert result.final_verdict == "VOID"
        assert "PHOENIX_LIMIT" in result.reason
        assert result.age_hours >= 72

    def test_partial_within_72_hours_unchanged(self):
        """PARTIAL verdict within 72h should NOT decay."""
        packet = VerdictPacket(
            verdict="PARTIAL",
            timestamp=_make_timestamp_hours_ago(71),  # 71 hours old
        )

        result = check_entropy_rot(packet)

        assert result.rotted is False
        assert result.original_verdict == "PARTIAL"
        assert result.final_verdict == "PARTIAL"

    def test_partial_just_under_boundary(self):
        """PARTIAL just under 72h should NOT decay (boundary test)."""
        packet = VerdictPacket(
            verdict="PARTIAL",
            timestamp=_make_timestamp_hours_ago(71.9),  # Just under 72h
        )

        result = check_entropy_rot(packet)

        # Just under 72h should not rot
        assert result.final_verdict == "PARTIAL"

    def test_route_memory_applies_entropy_rot_to_partial(self):
        """route_memory should apply entropy rot and route PARTIAL→VOID correctly."""
        packet = VerdictPacket(
            verdict="PARTIAL",
            timestamp=_make_timestamp_hours_ago(73),
        )

        result = route_memory(packet, apply_entropy_rot=True)

        assert result.entropy_rot_applied is True
        assert result.verdict == "VOID"
        assert result.target_bands == ["VOID"]  # VOID only goes to VOID band


# =============================================================================
# TEST 2: SABAR ESCALATION (SABAR > 24h → PARTIAL)
# =============================================================================

class TestSabarEscalation:
    """
    Test SABAR verdicts escalate to PARTIAL after SABAR_TIMEOUT (24 hours).

    Per spec/arifos_v38_2.yaml::scheduler.sabar_timeout:
    - value: "24h"
    - effect: "SABAR -> PARTIAL"
    - rule: "If verdict == SABAR and age > 24h, escalate to PARTIAL."
    """

    def test_sabar_escalates_to_partial_after_25_hours(self):
        """SABAR verdict older than 24h should escalate to PARTIAL."""
        packet = VerdictPacket(
            verdict="SABAR",
            timestamp=_make_timestamp_hours_ago(25),  # 25 hours old
        )

        result = check_entropy_rot(packet)

        assert result.rotted is True
        assert result.original_verdict == "SABAR"
        assert result.final_verdict == "PARTIAL"
        assert "SABAR_TIMEOUT" in result.reason
        assert result.age_hours >= 24

    def test_sabar_within_24_hours_unchanged(self):
        """SABAR verdict within 24h should NOT escalate."""
        packet = VerdictPacket(
            verdict="SABAR",
            timestamp=_make_timestamp_hours_ago(23),  # 23 hours old
        )

        result = check_entropy_rot(packet)

        assert result.rotted is False
        assert result.original_verdict == "SABAR"
        assert result.final_verdict == "SABAR"

    def test_sabar_just_under_boundary(self):
        """SABAR just under 24h should NOT escalate (boundary test)."""
        packet = VerdictPacket(
            verdict="SABAR",
            timestamp=_make_timestamp_hours_ago(23.9),  # Just under 24h
        )

        result = check_entropy_rot(packet)

        # Just under 24h should not rot
        assert result.final_verdict == "SABAR"

    def test_route_memory_applies_entropy_rot_to_sabar(self):
        """route_memory should apply entropy rot and route SABAR→PARTIAL correctly."""
        packet = VerdictPacket(
            verdict="SABAR",
            timestamp=_make_timestamp_hours_ago(25),
        )

        result = route_memory(packet, apply_entropy_rot=True)

        assert result.entropy_rot_applied is True
        assert result.verdict == "PARTIAL"
        # PARTIAL routes to PHOENIX + LEDGER
        assert "PHOENIX" in result.target_bands or "LEDGER" in result.target_bands


# =============================================================================
# TEST 3: SUNSET REVOCATION (LEDGER → PHOENIX)
# =============================================================================

class TestSunsetRevocation:
    """
    Test SUNSET verdict triggers move from LEDGER → PHOENIX.

    Per spec/arifos_v38_2.yaml::verdict_routing.SUNSET:
    - from_band: "LEDGER"
    - to_band: "PHOENIX"
    - canonical_after: false
    - Description: revocation pulse — un-seal previously canonical memory.
    """

    def test_sunset_verdict_in_enum(self):
        """SUNSET should be in the Verdict enum."""
        assert Verdict.SUNSET.value == "SUNSET"

    def test_sunset_routing_targets_phoenix(self):
        """SUNSET verdict should route to PHOENIX band."""
        assert "SUNSET" in VERDICT_BAND_ROUTING
        assert VERDICT_BAND_ROUTING["SUNSET"] == ["PHOENIX"]

    def test_sunset_revocation_via_router(self):
        """
        Test execute_sunset moves entry from LEDGER → PHOENIX.

        Steps:
        1. Create a router with LEDGER and PHOENIX bands
        2. Write a SEAL entry to LEDGER
        3. Execute SUNSET on that entry
        4. Verify entry exists in PHOENIX with revocation metadata
        5. Verify original entry_id is referenced
        """
        router = MemoryBandRouter()

        # Step 1: Write a SEAL entry to LEDGER
        ledger_result = router.route_write(
            verdict="SEAL",
            content={"test": "original sealed truth"},
            writer_id="APEX_PRIME",
            target_band="LEDGER",
            evidence_hash="abc123",
        )

        assert "LEDGER" in ledger_result
        assert ledger_result["LEDGER"].success is True
        original_entry_id = ledger_result["LEDGER"].entry_id

        # Step 2: Execute SUNSET on that entry
        success, message, phoenix_entry_id = router.execute_sunset(
            reference_id=original_entry_id,
            reason="Test revocation: reality changed",
        )

        assert success is True
        assert "moved to PHOENIX" in message
        assert phoenix_entry_id is not None

        # Step 3: Verify entry exists in PHOENIX
        phoenix_band = router.get_band(BandName.PHOENIX)
        phoenix_entries = phoenix_band.query(
            filter_fn=lambda e: e.entry_id == phoenix_entry_id
        )

        assert phoenix_entries.total_count == 1
        phoenix_entry = phoenix_entries.entries[0]

        # Step 4: Verify revocation metadata preserved
        assert phoenix_entry.content["revoked_from"] == "LEDGER"
        assert phoenix_entry.content["original_entry_id"] == original_entry_id
        assert phoenix_entry.content["revocation_reason"] == "Test revocation: reality changed"
        assert phoenix_entry.verdict == "SUNSET"
        assert phoenix_entry.metadata.get("sunset_type") == "revocation"
        # For SUNSET, proposals should surface in PHOENIX as
        # "awaiting_review" so humans can explicitly re-evaluate.
        assert phoenix_entry.metadata.get("status") == "awaiting_review"

    def test_sunset_preserves_evidence_chain(self):
        """SUNSET should preserve the original evidence hash."""
        router = MemoryBandRouter()

        # Write original entry
        original_hash = "evidence_hash_123"
        ledger_result = router.route_write(
            verdict="SEAL",
            content={"data": "some sealed fact"},
            writer_id="APEX_PRIME",
            target_band="LEDGER",
            evidence_hash=original_hash,
        )

        original_entry_id = ledger_result["LEDGER"].entry_id

        # Execute SUNSET
        success, _, phoenix_entry_id = router.execute_sunset(
            reference_id=original_entry_id,
            reason="Evidence chain test",
        )

        assert success is True

        # Verify evidence hash preserved
        phoenix_band = router.get_band(BandName.PHOENIX)
        phoenix_entries = phoenix_band.query(
            filter_fn=lambda e: e.entry_id == phoenix_entry_id
        )

        phoenix_entry = phoenix_entries.entries[0]
        assert phoenix_entry.evidence_hash == original_hash

    def test_sunset_on_nonexistent_entry_fails(self):
        """SUNSET on non-existent entry should fail gracefully."""
        router = MemoryBandRouter()

        success, message, _ = router.execute_sunset(
            reference_id="nonexistent-id-12345",
            reason="Should fail",
        )

        assert success is False
        assert "not found in LEDGER" in message


# =============================================================================
# TEST: INVARIANT ENFORCEMENT
# =============================================================================

class TestTimeInvariants:
    """
    Test TIME-1 and TIME-2 invariants from spec/arifos_v38_2.yaml.

    TIME-1: "Time is a Constitutional Force. Entropy Rot is automatic."
    TIME-2: "Hope has a half-life; governance does not."
    """

    def test_seal_not_affected_by_entropy_rot(self):
        """SEAL verdicts should never be affected by entropy rot."""
        packet = VerdictPacket(
            verdict="SEAL",
            timestamp=_make_timestamp_hours_ago(1000),  # Very old
        )

        result = check_entropy_rot(packet)

        assert result.rotted is False
        assert result.final_verdict == "SEAL"

    def test_void_not_affected_by_entropy_rot(self):
        """VOID verdicts should never be affected by entropy rot."""
        packet = VerdictPacket(
            verdict="VOID",
            timestamp=_make_timestamp_hours_ago(1000),
        )

        result = check_entropy_rot(packet)

        assert result.rotted is False
        assert result.final_verdict == "VOID"

    def test_888_hold_not_affected_by_entropy_rot(self):
        """888_HOLD verdicts should never be affected by entropy rot."""
        packet = VerdictPacket(
            verdict="888_HOLD",
            timestamp=_make_timestamp_hours_ago(1000),
        )

        result = check_entropy_rot(packet)

        assert result.rotted is False
        assert result.final_verdict == "888_HOLD"

    def test_sunset_not_affected_by_entropy_rot(self):
        """SUNSET verdicts should not be auto-generated by entropy rot."""
        # SUNSET is policy-triggered, not time-triggered
        packet = VerdictPacket(
            verdict="SUNSET",
            timestamp=_make_timestamp_hours_ago(1000),
        )

        result = check_entropy_rot(packet)

        assert result.rotted is False
        assert result.final_verdict == "SUNSET"

    def test_chain_decay_sabar_to_partial_to_void(self):
        """Test the full chain: SABAR (>24h) → PARTIAL (>72h) → VOID."""
        # First decay: SABAR > 24h → PARTIAL
        packet1 = VerdictPacket(
            verdict="SABAR",
            timestamp=_make_timestamp_hours_ago(25),
        )
        result1 = check_entropy_rot(packet1)
        assert result1.final_verdict == "PARTIAL"

        # Second decay: PARTIAL > 72h → VOID
        # Simulate that the PARTIAL has now aged beyond 72h total
        packet2 = VerdictPacket(
            verdict="PARTIAL",
            timestamp=_make_timestamp_hours_ago(73),
        )
        result2 = check_entropy_rot(packet2)
        assert result2.final_verdict == "VOID"


# =============================================================================
# TEST: SCHEDULER CONSTANTS
# =============================================================================

class TestSchedulerConstants:
    """Verify scheduler constants match spec."""

    def test_sabar_timeout_is_24_hours(self):
        """SABAR_TIMEOUT should be 24 hours per spec."""
        assert SABAR_TIMEOUT_HOURS == 24

    def test_phoenix_limit_is_72_hours(self):
        """PHOENIX_LIMIT should be 72 hours per spec."""
        assert PHOENIX_LIMIT_HOURS == 72


# =============================================================================
# TEST: ROUTE MEMORY WITH ENTROPY ROT DISABLED
# =============================================================================

class TestRouteMemoryNoRot:
    """Test route_memory with apply_entropy_rot=False."""

    def test_no_rot_when_disabled(self):
        """When apply_entropy_rot=False, verdicts should not decay."""
        packet = VerdictPacket(
            verdict="PARTIAL",
            timestamp=_make_timestamp_hours_ago(100),  # Very stale
        )

        result = route_memory(packet, apply_entropy_rot=False)

        assert result.entropy_rot_applied is False
        assert result.verdict == "PARTIAL"
        # Should route to PARTIAL's bands, not VOID
        assert "PHOENIX" in result.target_bands or "LEDGER" in result.target_bands
