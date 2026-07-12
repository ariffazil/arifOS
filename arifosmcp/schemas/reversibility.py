"""
Reversibility Class — The R-Scale for Governance Interception.
══════════════════════════════════════════════════════════════

As requested by the Sovereign (F13), every action must be classified on a
machine-readable reversibility scale. This replaces vague 'risk' or 'impact'
metrics with a brutal, operational assessment of how hard it is to undo.

R4 and R5 automatically trigger 888 HOLD.
"""

from enum import StrEnum


class ReversibilityClass(StrEnum):
    """Machine-readable reversibility scale for constitutional enforcement.

    Canonical source — unified 2026-07-11 (Phase 2 Gate Consolidation).
    Supersedes: core/reversibility_engine.py ReversibilityClass (same semantic order).
    Mapping: R0↔TRIVIAL, R1↔REVERSIBLE, R2↔PARTIAL, R3↔COSTLY, R4↔IRREVERSIBLE, R5↔CRITICAL.
    """

    R0_OBSERVATION = "R0"
    # Meaning: Pure observation, read-only. No side effects.
    # Trigger: None. Logged.

    R1_SIMULATION = "R1"
    # Meaning: Draft, simulation, local sandbox. No side effects.
    # Trigger: None. Logged.

    R2_REVERSIBLE_WRITE = "R2"
    # Meaning: Reversible write. Local state change, easily rolled back.
    # Trigger: Authorized autonomously, audit locked.

    R3_COSTLY_REVERSIBLE = "R3"
    # Meaning: Costly reversible action. API calls, large compute, complex rollback.
    # Trigger: Authorized autonomously, audit locked, alerts Sovereign.

    R4_IRREVERSIBLE = "R4"
    # Meaning: Irreversible or external action. External messages, non-versioned writes.
    # Trigger: 888 HOLD automatically triggered.

    R5_SOVEREIGN = "R5"
    # Meaning: High-blast-radius sovereign action. Capital transfer, constitution edit.
    # Trigger: 888 HOLD automatically triggered. Requires F13 cryptographic signature.

    # ── Legacy aliases (Phase 2 unification — backward compat) ──
    TRIVIAL = "R0"
    REVERSIBLE = "R1"
    PARTIAL = "R2"
    COSTLY = "R3"
    IRREVERSIBLE = "R4"
    CRITICAL = "R5"

    @classmethod
    def triggers_hold(cls, r_class: "ReversibilityClass") -> bool:
        """Returns True if the class structurally mandates an 888 HOLD."""
        return r_class in {cls.R4_IRREVERSIBLE, cls.R5_SOVEREIGN}

    @classmethod
    def requires_audit(cls, r_class: "ReversibilityClass") -> bool:
        """Returns True if the action must be permanently hashed in VAULT999."""
        # All state mutations require an audit hash.
        return r_class not in {cls.R0_OBSERVATION, cls.R1_SIMULATION}
