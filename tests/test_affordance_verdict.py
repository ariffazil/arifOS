"""WAJIB-2: Tests for affordance→verdict wiring.

Verifies that the verdict engine respects the affordance_contract:
- OBSERVE-class + safe_autonomous_use + no mutation + no irreversible
  → HOLD on identity grounds narrows to SEAL_OBSERVE_ONLY
- EXECUTE-class / irreversible → HOLD stays HOLD (never narrowed)
- VOID/SABAR → never narrowed (these are terminal states)
"""

from __future__ import annotations


from arifosmcp.runtime.tools import _derive_affordance_verdict


class TestDeriveAffordanceVerdict:
    """Test the affordance→verdict derivation function."""

    # ── OBSERVE-class tools: HOLD should narrow to SEAL_OBSERVE_ONLY ─────

    def test_observe_hold_narrows_to_seal_observe_only(self):
        """An OBSERVE-class tool held on identity grounds is over-gated."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_ping", "HOLD", affordance)
        assert result == "SEAL_OBSERVE_ONLY"

    def test_observe_seal_stays_seal(self):
        """An OBSERVE-class tool that already passed stays SEAL."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_ping", "SEAL", affordance)
        assert result == "SEAL"

    def test_observe_degraded_stays_degraded(self):
        """DEGRADED is not narrowed — it means something else is wrong."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_ping", "DEGRADED", affordance)
        assert result == "DEGRADED"

    def test_observe_seal_observe_only_stays(self):
        """Already narrowed verdict stays."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_ping", "SEAL_OBSERVE_ONLY", affordance)
        assert result == "SEAL_OBSERVE_ONLY"

    # ── EXECUTE-class tools: never narrow ─────────────────────────────────

    def test_execute_hold_stays_hold(self):
        """EXECUTE-class tools must keep full gates."""
        affordance = {
            "action_class": "EXECUTE",
            "mutation": True,
            "irreversible": "possible",
            "safe_autonomous_use": False,
        }
        result = _derive_affordance_verdict("arif_forge_execute", "HOLD", affordance)
        assert result == "HOLD"

    def test_irreversible_hold_stays_hold(self):
        """Irreversible tools must keep full gates."""
        affordance = {
            "action_class": "DRAFT",
            "mutation": False,
            "irreversible": True,
            "safe_autonomous_use": False,
        }
        result = _derive_affordance_verdict("arif_vault_seal", "HOLD", affordance)
        assert result == "HOLD"

    # ── VOID/SABAR: never narrow (terminal states) ────────────────────────

    def test_void_never_narrows(self):
        """VOID is a terminal state — never narrow."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_ping", "VOID", affordance)
        assert result == "VOID"

    def test_sabar_never_narrows(self):
        """SABAR is a recoverable state — never narrow."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_ping", "SABAR", affordance)
        assert result == "SABAR"

    # ── Mutation tools: HOLD stays even if not irreversible ───────────────

    def test_mutation_hold_stays_hold(self):
        """A mutating tool that's not irreversible still keeps HOLD."""
        affordance = {
            "action_class": "DRAFT",
            "mutation": True,
            "irreversible": False,
            "safe_autonomous_use": False,
        }
        result = _derive_affordance_verdict("arif_mind_reason", "HOLD", affordance)
        assert result == "HOLD"

    # ── Unknown affordance (conservative default) ─────────────────────────

    def test_unknown_affordance_hold_stays_hold(self):
        """Unknown affordance = conservative. Never narrow."""
        affordance = {
            "action_class": "UNKNOWN",
            "mutation": "unknown",
            "irreversible": "unknown",
            "safe_autonomous_use": False,
        }
        result = _derive_affordance_verdict("unknown_tool", "HOLD", affordance)
        assert result == "HOLD"

    # ── Edge cases ────────────────────────────────────────────────────────

    def test_observe_no_safe_autonomous_stays_hold(self):
        """OBSERVE but safe_autonomous_use=False → don't narrow."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": False,
            "irreversible": False,
            "safe_autonomous_use": False,
        }
        result = _derive_affordance_verdict("arif_sense_observe", "HOLD", affordance)
        assert result == "HOLD"

    def test_observe_with_mutation_stays_hold(self):
        """OBSERVE but mutation=True → don't narrow."""
        affordance = {
            "action_class": "OBSERVE",
            "mutation": True,
            "irreversible": False,
            "safe_autonomous_use": True,
        }
        result = _derive_affordance_verdict("arif_sense_observe", "HOLD", affordance)
        assert result == "HOLD"
