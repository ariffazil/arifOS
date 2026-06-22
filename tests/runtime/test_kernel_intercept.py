"""
test_kernel_intercept.py — F11 AUDITABILITY tests for the Minimum Constitutional Kernel.

Forged 2026-06-22 — patches the F11 AUTH substring-match vulnerability and adds
F2 TRUTH evidence-chain enforcement per FLOOR_INVARIANTS_v2026.06.23.

DITEMPA BUKAN DIBERI — Tests are forged, not given.
"""

from __future__ import annotations

import os
import pytest

from arifosmcp.tools.arif_kernel_intercept import (
    _arif_kernel_intercept,
    _verify_sovereign_token,
)


# ── F11 AUTH — SOVEREIGN token verification ──────────────────────────────────


class TestSovereignTokenVerification:
    """F11 AUTH: F13 SOVEREIGN token must be cryptographically verified."""

    def test_no_token_rejected(self):
        assert _verify_sovereign_token(None) is False

    def test_empty_token_rejected(self):
        assert _verify_sovereign_token("") is False

    def test_substring_F13_no_longer_sufficient(self):
        """Regression: old code accepted any string containing 'F13'."""
        # The bug we fixed: "F13" anywhere in the string granted authority.
        # After fix: only the dev sentinel (or prod ed25519) passes.
        sentinel = os.environ.get(
            "ARIFOS_SOVEREIGN_KEY",
            "DEV_ONLY_SENTINEL_REPLACE_AT_PROD_BOOT",
        )
        if "F13" not in sentinel:
            assert _verify_sovereign_token("F13-something-arbitrary") is False
            assert _verify_sovereign_token("i-am-F13") is False

    def test_correct_sentinel_accepted(self):
        sentinel = os.environ.get(
            "ARIFOS_SOVEREIGN_KEY",
            "DEV_ONLY_SENTINEL_REPLACE_AT_PROD_BOOT",
        )
        assert _verify_sovereign_token(sentinel) is True

    def test_wrong_length_rejected_quickly(self):
        """Length-mismatch returns False without leaking timing on compare."""
        assert _verify_sovereign_token("x") is False
        assert _verify_sovereign_token("x" * 1000) is False


# ── F13 SOVEREIGN — R4/R5 actions escalate without sovereign token ────────────


@pytest.mark.asyncio
class TestR4R5Escalation:
    """F13: R4 (irreversible) and R5 (sovereign) actions MUST ESCALATE without token."""

    async def test_r4_without_token_escalates(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="send external email",
            requested_capability="composio_gmail_send",
            domain="AAA",
            reversibility_level="R4",
            blast_radius="external-recipient",
        )
        assert r["decision"] == "ESCALATE"
        assert r["constitutional_floor_triggered"] == "F13"

    async def test_r5_without_token_escalates(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="transfer capital",
            requested_capability="wealth_vault_seal",
            domain="WEALTH",
            reversibility_level="R5",
            blast_radius="capital",
        )
        assert r["decision"] == "ESCALATE"
        assert r["constitutional_floor_triggered"] == "F13"

    async def test_r5_with_arbitrary_F13_string_still_escalates(self):
        """Regression: the substring 'F13' must NOT grant authority."""
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="transfer capital",
            requested_capability="wealth_vault_seal",
            domain="WEALTH",
            reversibility_level="R5",
            blast_radius="capital",
            authority_token="F13-bypass-attempt-1234",
        )
        assert r["decision"] == "ESCALATE"

    async def test_r5_with_correct_sentinel_allows(self):
        sentinel = os.environ.get(
            "ARIFOS_SOVEREIGN_KEY",
            "DEV_ONLY_SENTINEL_REPLACE_AT_PROD_BOOT",
        )
        r = await _arif_kernel_intercept(
            actor="arif",
            intent="constitutional amendment",
            requested_capability="arif_floor_amend",
            domain="arifOS",
            reversibility_level="R5",
            blast_radius="constitution",
            authority_token=sentinel,
        )
        assert r["decision"] == "ALLOW"


# ── F2 TRUTH — evidence required for objective claims ───────────────────────


@pytest.mark.asyncio
class TestEvidenceRequired:
    """F2 TRUTH: FACT/ESTIMATE claims require evidence."""

    async def test_fact_without_evidence_denied(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="emit claim",
            requested_capability="emit_fact",
            domain="arifOS",
            reversibility_level="R2",
            blast_radius="ledger",
            epistemic_state="FACT",
        )
        assert r["decision"] == "DENY"
        assert r["constitutional_floor_triggered"] == "F2"

    async def test_estimate_without_evidence_denied(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="emit estimate",
            requested_capability="emit_estimate",
            domain="arifOS",
            reversibility_level="R2",
            blast_radius="ledger",
            epistemic_state="ESTIMATE",
        )
        assert r["decision"] == "DENY"
        assert r["constitutional_floor_triggered"] == "F2"

    async def test_fact_with_evidence_allows(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="emit fact",
            requested_capability="emit_fact",
            domain="arifOS",
            reversibility_level="R2",
            blast_radius="ledger",
            epistemic_state="FACT",
            evidence=[{"source": "https://example.com/data", "ref": "verified-2026-06-22"}],
        )
        assert r["decision"] == "ALLOW"

    async def test_conflict_without_evidence_escalates(self):
        """CONFLICT must surface, not resolve silently."""
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="resolve conflict",
            requested_capability="emit_resolution",
            domain="arifOS",
            reversibility_level="R2",
            blast_radius="ledger",
            epistemic_state="CONFLICT",
        )
        assert r["decision"] == "ESCALATE"

    async def test_hypothesis_high_blast_without_evidence_escalates(self):
        """HYPOTHESIS on capital/constitution/external requires evidence."""
        for blast in ["capital", "constitution", "external-recipient"]:
            r = await _arif_kernel_intercept(
                actor="test-agent",
                intent="emit hypothesis",
                requested_capability="emit_hypothesis",
                domain="arifOS",
                reversibility_level="R3",
                blast_radius=blast,
                epistemic_state="HYPOTHESIS",
            )
            assert r["decision"] == "ESCALATE", f"Failed for blast_radius={blast}"


# ── Standard allow path ─────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestStandardAllow:
    """Standard reversible actions allow with audit."""

    async def test_r0_observation_allows(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="observe basin",
            requested_capability="geox_basin_profile",
            domain="GEOX",
            reversibility_level="R0",
            blast_radius="none",
        )
        assert r["decision"] == "ALLOW"
        assert r["audit_hash"] is None  # R0 doesn't require audit

    async def test_r2_write_generates_audit_hash(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="write to ledger",
            requested_capability="vault_write",
            domain="arifOS",
            reversibility_level="R2",
            blast_radius="ledger",
        )
        assert r["decision"] == "ALLOW"
        assert r["audit_hash"] is not None  # R2+ requires audit
        assert len(r["audit_hash"]) == 16  # sha256[:16]

    async def test_r2_write_has_rollback_instruction(self):
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="write to ledger",
            requested_capability="vault_write",
            domain="arifOS",
            reversibility_level="R2",
            blast_radius="ledger",
        )
        assert r["rollback_instruction"] == "reverse_operation"


# ── Fail-closed semantics ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestFailClosed:
    """Invalid input fails closed (R4, UNKNOWN)."""

    async def test_invalid_r_class_defaults_to_R4(self):
        """Invalid reversibility string → R4 (fail closed)."""
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="unknown action",
            requested_capability="unknown",
            domain="arifOS",
            reversibility_level="R99_INVALID",
            blast_radius="unknown",
        )
        # R4 default + no sovereign token → ESCALATE
        assert r["decision"] == "ESCALATE"

    async def test_invalid_epistemic_state_defaults_to_unknown(self):
        """Invalid truth state → UNKNOWN (not blocked, just tagged)."""
        r = await _arif_kernel_intercept(
            actor="test-agent",
            intent="some action",
            requested_capability="some_capability",
            domain="arifOS",
            reversibility_level="R0",
            blast_radius="none",
            epistemic_state="INVALID_STATE",
        )
        # R0 + UNKNOWN → ALLOW (read-only)
        assert r["decision"] == "ALLOW"
