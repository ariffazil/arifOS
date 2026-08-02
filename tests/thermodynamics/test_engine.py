"""
Thermodynamic Engine Test Suite — arif_judge v37Ω-E

Tests the entropy pathway classification, buffer status, and verdict matrix
for the BIJAKSANA thermodynamic bridge.

DITEMPA BUKAN DIBERI — Forged 2026-08-01.
"""

import pytest

from arifosmcp.thermodynamics.engine import (
    EntropyPathway,
    EntropyReceipt,
    ThermodynamicVerdict,
    BufferStatus,
    compute_entropy_pathway,
    classify_actor_buffer,
    thermodynamic_judge,
    render_entropy_receipt,
)


# ── Entropy Pathway Classification ────────────────────────────────────────


class TestEntropyPathway:
    def test_investment_pathway(self):
        """ΔS_now ↑, ΔS_future ↓ → INVESTMENT."""
        pathway = compute_entropy_pathway(0.90, 0.50, "UP", "DOWN")
        assert pathway == EntropyPathway.INVESTMENT

    def test_maintenance_pathway_flat(self):
        """ΔS_now FLAT, ΔS_future FLAT → MAINTENANCE."""
        pathway = compute_entropy_pathway(0.50, 1.02, "FLAT", "FLAT")
        assert pathway == EntropyPathway.MAINTENANCE

    def test_maintenance_pathway_down(self):
        """ΔS_now DOWN, ΔS_future DOWN → MAINTENANCE."""
        pathway = compute_entropy_pathway(0.50, 0.50, "DOWN", "DOWN")
        assert pathway == EntropyPathway.MAINTENANCE

    def test_extraction_pathway(self):
        """ΔS_now ↑, ΔS_future ↑ → EXTRACTION."""
        pathway = compute_entropy_pathway(0.40, 1.02, "UP", "UP")
        assert pathway == EntropyPathway.EXTRACTION

    def test_terminal_extraction_black_hole(self):
        """D_index > 1.0 → TERMINAL_EXTRACTION regardless of delta."""
        pathway = compute_entropy_pathway(0.82, 0.95, "UP", "UP", d_index=1.07)
        assert pathway == EntropyPathway.TERMINAL_EXTRACTION

    def test_unknown_pathway(self):
        """Unmapped deltas → UNKNOWN."""
        pathway = compute_entropy_pathway(0.50, 0.50, "UNKNOWN", "UNKNOWN")
        assert pathway == EntropyPathway.UNKNOWN


# ── Actor Buffer Classification ───────────────────────────────────────────


class TestBufferClassification:
    def test_sufficient_buffer(self):
        """B >= 0.70 AND phi < 1.0 → SUFFICIENT."""
        assert classify_actor_buffer(0.90, 0.50) == BufferStatus.SUFFICIENT
        assert classify_actor_buffer(0.70, 0.99) == BufferStatus.SUFFICIENT

    def test_thin_buffer(self):
        """B >= 0.55 OR phi < 0.80 → THIN."""
        assert classify_actor_buffer(0.60, 0.70) == BufferStatus.THIN
        assert classify_actor_buffer(0.40, 0.70) == BufferStatus.THIN

    def test_exhausted_buffer(self):
        """B < 0.55 AND phi > 1.0 → EXHAUSTED."""
        assert classify_actor_buffer(0.40, 1.02) == BufferStatus.EXHAUSTED
        assert classify_actor_buffer(0.499, 1.02) == BufferStatus.EXHAUSTED


# ── Thermodynamic Verdict Matrix ──────────────────────────────────────────


class TestVerdictMatrix:
    """Verify the complete verdict matrix from the specification."""

    # ── INVESTMENT pathway ──

    def test_investment_seal(self):
        """High B, low Φ, investment → SEAL (Mahathir 1.0 state)."""
        pathway = EntropyPathway.INVESTMENT
        buffer = classify_actor_buffer(0.929, 0.62)
        verdict = thermodynamic_judge(pathway, 0.929, 0.62, buffer)
        assert verdict == ThermodynamicVerdict.SEAL
        assert buffer == BufferStatus.SUFFICIENT

    def test_investment_sabar_low_buffer(self):
        """Low B, high Φ, investment → SABAR (Anwar cannot invest)."""
        pathway = EntropyPathway.INVESTMENT
        buffer = classify_actor_buffer(0.499, 1.02)
        verdict = thermodynamic_judge(pathway, 0.499, 1.02, buffer)
        assert verdict == ThermodynamicVerdict.SABAR
        assert buffer == BufferStatus.EXHAUSTED

    def test_investment_sabar_high_phi(self):
        """High B, high Φ, investment → SABAR (Mahathir 2.0: knows price, no buffer)."""
        pathway = EntropyPathway.INVESTMENT
        buffer = classify_actor_buffer(0.543, 0.95)
        verdict = thermodynamic_judge(pathway, 0.543, 0.95, buffer)
        assert verdict == ThermodynamicVerdict.SABAR

    # ── MAINTENANCE pathway ──

    def test_maintenance_always_sabar(self):
        """Maintenance → SABAR regardless of actor state."""
        for b, phi in [(0.90, 0.50), (0.50, 1.02), (0.30, 1.50)]:
            buffer = classify_actor_buffer(b, phi)
            verdict = thermodynamic_judge(EntropyPathway.MAINTENANCE, b, phi, buffer)
            assert verdict == ThermodynamicVerdict.SABAR, f"B={b}, Φ={phi}"

    # ── EXTRACTION pathway ──

    def test_extraction_hold(self):
        """High B, low Φ, extraction → HOLD (understands damage, block it)."""
        pathway = EntropyPathway.EXTRACTION
        buffer = classify_actor_buffer(0.90, 0.50)
        verdict = thermodynamic_judge(pathway, 0.90, 0.50, buffer)
        assert verdict == ThermodynamicVerdict.HOLD

    def test_extraction_void(self):
        """Low B, high Φ, extraction → VOID (doesn't understand damage)."""
        pathway = EntropyPathway.EXTRACTION
        buffer = classify_actor_buffer(0.40, 1.02)
        verdict = thermodynamic_judge(pathway, 0.40, 1.02, buffer)
        assert buffer == BufferStatus.EXHAUSTED
        assert verdict == ThermodynamicVerdict.VOID

    # ── TERMINAL pathway ──

    def test_terminal_always_void(self):
        """Terminal → VOID regardless of actor state."""
        for b, phi in [(0.90, 0.50), (0.50, 1.02), (0.30, 1.50)]:
            buffer = classify_actor_buffer(b, phi)
            verdict = thermodynamic_judge(EntropyPathway.TERMINAL_EXTRACTION, b, phi, buffer)
            assert verdict == ThermodynamicVerdict.VOID, f"B={b}, Φ={phi}"

    # ── UNKNOWN pathway ──

    def test_unknown_hold(self):
        """Unknown → HOLD (fail-closed)."""
        buffer = classify_actor_buffer(0.50, 0.50)
        verdict = thermodynamic_judge(EntropyPathway.UNKNOWN, 0.50, 0.50, buffer)
        assert verdict == ThermodynamicVerdict.HOLD

    # ── Floor violation ──

    def test_floor_fail_void(self):
        """Floor violation → VOID regardless of pathway."""
        pathway = EntropyPathway.INVESTMENT
        buffer = classify_actor_buffer(0.90, 0.50)
        verdict = thermodynamic_judge(pathway, 0.90, 0.50, buffer, floors_pass=False)
        assert verdict == ThermodynamicVerdict.VOID


# ── Real-World State Tests ────────────────────────────────────────────────


class TestRealWorldStates:
    """Test the exact states from the APEX v37Ω ranking."""

    def test_anwar_state(self):
        """Anwar: B=0.499, Φ=1.02, maintenance → SABAR."""
        pathway = compute_entropy_pathway(0.499, 1.02, "FLAT", "FLAT")
        assert pathway == EntropyPathway.MAINTENANCE
        buffer = classify_actor_buffer(0.499, 1.02)
        assert buffer == BufferStatus.EXHAUSTED
        verdict = thermodynamic_judge(pathway, 0.499, 1.02, buffer)
        assert verdict == ThermodynamicVerdict.SABAR

    def test_mahathir_state(self):
        """Mahathir 1.0: B=0.929, Φ=0.62, investment → SEAL."""
        pathway = compute_entropy_pathway(0.929, 0.62, "UP", "DOWN")
        assert pathway == EntropyPathway.INVESTMENT
        buffer = classify_actor_buffer(0.929, 0.62)
        assert buffer == BufferStatus.SUFFICIENT
        verdict = thermodynamic_judge(pathway, 0.929, 0.62, buffer)
        assert verdict == ThermodynamicVerdict.SEAL

    def test_najib_state(self):
        """Najib: B=0.661, Φ=0.95, extraction, D_index=1.07 → TERMINAL → VOID."""
        pathway = compute_entropy_pathway(0.661, 0.95, "UP", "UP", d_index=1.07)
        assert pathway == EntropyPathway.TERMINAL_EXTRACTION
        verdict = thermodynamic_judge(pathway, 0.661, 0.95, BufferStatus.THIN)
        assert verdict == ThermodynamicVerdict.VOID

    def test_razak_state(self):
        """Razak: B=0.910, Φ=0.17, investment → SEAL."""
        pathway = compute_entropy_pathway(0.910, 0.17, "UP", "DOWN")
        assert pathway == EntropyPathway.INVESTMENT
        buffer = classify_actor_buffer(0.910, 0.17)
        assert buffer == BufferStatus.SUFFICIENT
        verdict = thermodynamic_judge(pathway, 0.910, 0.17, buffer)
        assert verdict == ThermodynamicVerdict.SEAL

    def test_abdullah_state(self):
        """Abdullah: B=0.435, Φ=0.75, maintenance → SABAR."""
        pathway = compute_entropy_pathway(0.435, 0.75, "FLAT", "FLAT")
        assert pathway == EntropyPathway.MAINTENANCE
        buffer = classify_actor_buffer(0.435, 0.75)
        verdict = thermodynamic_judge(pathway, 0.435, 0.75, buffer)
        assert verdict == ThermodynamicVerdict.SABAR


# ── Entropy Receipt Render ────────────────────────────────────────────────


class TestEntropyReceipt:
    def test_seal_receipt(self):
        """SEAL receipt contains correct pathway and required action."""
        receipt = render_entropy_receipt(EntropyPathway.INVESTMENT, actor_B=0.929, actor_phi=0.62)
        assert receipt.verdict == ThermodynamicVerdict.SEAL
        assert receipt.entropy_pathway == EntropyPathway.INVESTMENT
        assert receipt.required_action == "EXECUTE"
        assert receipt.buffer_status == BufferStatus.SUFFICIENT
        assert receipt.delta_s_now == "UP"
        assert receipt.delta_s_future == "DOWN"

    def test_sabar_receipt(self):
        """SABAR receipt contains correct pathway and required action."""
        receipt = render_entropy_receipt(EntropyPathway.MAINTENANCE, actor_B=0.499, actor_phi=1.02)
        assert receipt.verdict == ThermodynamicVerdict.SABAR
        assert receipt.entropy_pathway == EntropyPathway.MAINTENANCE
        assert receipt.required_action == "WAIT"
        assert receipt.buffer_status == BufferStatus.EXHAUSTED

    def test_void_receipt(self):
        """VOID receipt contains correct pathway and required action."""
        receipt = render_entropy_receipt(
            EntropyPathway.TERMINAL_EXTRACTION, actor_B=0.82, actor_phi=0.95
        )
        assert receipt.verdict == ThermodynamicVerdict.VOID
        assert receipt.entropy_pathway == EntropyPathway.TERMINAL_EXTRACTION
        assert receipt.required_action == "REJECT"

    def test_hold_receipt(self):
        """HOLD receipt contains correct pathway and required action."""
        receipt = render_entropy_receipt(EntropyPathway.EXTRACTION, actor_B=0.70, actor_phi=0.50)
        assert receipt.verdict == ThermodynamicVerdict.HOLD
        assert receipt.entropy_pathway == EntropyPathway.EXTRACTION
        assert receipt.required_action == "RESTRUCTURE"

    def test_receipt_to_dict(self):
        """Receipt serializes correctly."""
        receipt = render_entropy_receipt(EntropyPathway.INVESTMENT, actor_B=0.929, actor_phi=0.62)
        d = receipt.to_dict()
        assert d["verdict"] == "SEAL"
        assert d["entropy_pathway"] == "INVESTMENT"
        assert d["actor_B"] == 0.929
        assert d["actor_phi"] == 0.62
        assert d["required_action"] == "EXECUTE"


# ── Edge Cases ─────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_boundary_b_70_phi_099(self):
        """B=0.70, Φ=0.99 → SUFFICIENT (boundary)."""
        assert classify_actor_buffer(0.70, 0.99) == BufferStatus.SUFFICIENT

    def test_boundary_b_549_phi_101(self):
        """B=0.549, Φ=1.01 → EXHAUSTED (boundary)."""
        assert classify_actor_buffer(0.549, 1.01) == BufferStatus.EXHAUSTED

    def test_mid_buffer(self):
        """B=0.60, Φ=0.85 → THIN (mid range)."""
        assert classify_actor_buffer(0.60, 0.85) == BufferStatus.THIN

    def test_max_b_min_phi(self):
        """B=1.0, Φ=0.0 → SUFFICIENT."""
        assert classify_actor_buffer(1.0, 0.0) == BufferStatus.SUFFICIENT

    def test_min_b_max_phi(self):
        """B=0.0, Φ=10.0 → EXHAUSTED."""
        assert classify_actor_buffer(0.0, 10.0) == BufferStatus.EXHAUSTED


# ── Backpropagation & Φ Chain ──────────────────────────────────────────────


class TestBackpropagation:
    def test_phi_delta_mahathir(self):
        """Mahathir 1.0: A=0.92, P=0.80, E=0.38, X=0.48 → ΔΦ."""
        from arifosmcp.thermodynamics.engine import compute_phi_delta

        delta = compute_phi_delta(0.92, 0.80, 0.38, 0.48)
        # C_dark = 0.92 * 0.20 * 0.52 = 0.096
        # S_shadow = 0.62 * 0.92 = 0.570
        # ΔΦ ≈ 0.666
        assert 0.65 < delta < 0.68, f"Expected ~0.666, got {delta}"

    def test_phi_delta_anwar(self):
        """Anwar: A=0.72, P=0.75, E=0.48, X=0.58 → ΔΦ."""
        from arifosmcp.thermodynamics.engine import compute_phi_delta

        delta = compute_phi_delta(0.72, 0.75, 0.48, 0.58)
        # C_dark = 0.72 * 0.25 * 0.42 = 0.076
        # S_shadow = 0.52 * 0.72 = 0.374
        # ΔΦ ≈ 0.450
        assert 0.44 < delta < 0.46, f"Expected ~0.450, got {delta}"

    def test_forward_propagate_phi(self):
        """Φ propagates correctly: Φ(t+1) = Φ(t) + ΔΦ."""
        from arifosmcp.thermodynamics.engine import forward_propagate_phi

        new_phi = forward_propagate_phi(0.62, 0.92, 0.80, 0.38, 0.48)
        assert new_phi > 0.62, f"Phi should increase, got {new_phi}"

    def test_governance_loss_mahathir(self):
        """Mahathir 1.0: high B gets low loss."""
        from arifosmcp.thermodynamics.engine import compute_governance_loss

        result = compute_governance_loss(0.5, 0.62, 0.92, 0.80, 0.38, 0.48)
        assert "loss" in result
        assert "phi_future" in result
        assert result["phi_future"] > result["phi_now"]

    def test_governance_loss_anwar(self):
        """Anwar: high Φ gives high loss."""
        from arifosmcp.thermodynamics.engine import compute_governance_loss

        result = compute_governance_loss(0.1, 1.02, 0.72, 0.75, 0.48, 0.58)
        assert result["phi_now"] == 1.02
        assert result["loss"] > 0

    def test_backpropagate_high_b(self):
        """High B → accurate gradient."""
        from arifosmcp.thermodynamics.engine import backpropagate_entropy_gradient

        result = backpropagate_entropy_gradient(0.929, 0.5)
        assert result["gradient_accuracy"] == 0.929
        assert "INVESTMENT_GRADE" in result["bijaksana_verdict"]

    def test_backpropagate_low_b(self):
        """Low B → noisy gradient. Anwar's B=0.499 < 0.55 → EXTRACTION_GRADE."""
        from arifosmcp.thermodynamics.engine import backpropagate_entropy_gradient

        result = backpropagate_entropy_gradient(0.499, 0.1)
        assert result["gradient_accuracy"] == 0.499
        assert "EXTRACTION_GRADE" in result["bijaksana_verdict"]

    def test_backpropagate_zero_b(self):
        """B=0 → infinite loss."""
        from arifosmcp.thermodynamics.engine import backpropagate_entropy_gradient

        result = backpropagate_entropy_gradient(0.0, 0.1)
        assert result["discounted_future_entropy"] == float("inf")
        assert "TERMINAL_GRADE" in result["bijaksana_verdict"]
