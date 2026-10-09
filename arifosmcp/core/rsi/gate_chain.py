"""
RSI Constitutional Kernel — Gate Chain (/777)
═══════════════════════════════════════════════════════════════════════════════

Boolean gate chain for promotion decisions.
Each gate is true/false with fixed thresholds.
Formula becomes metadata on evidence sheet for F13.

Ratified: 2026-09-15
Authority: F13 SOVEREIGN

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class ActionClass(StrEnum):
    READ = "READ"
    REASON = "REASON"
    BUILD = "BUILD"
    PROMOTE = "PROMOTE"
    EXECUTE = "EXECUTE"
    CONSTITUTE = "CONSTITUTE"
    REVOKE = "REVOKE"


class GateVerdict(StrEnum):
    PERMIT = "PERMIT"
    HOLD = "HOLD"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"


# ═══════════════════════════════════════════════════════════════════════════════
# PROPOSAL
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Proposal:
    case_id: str
    action_class: ActionClass
    proposed_by: str
    authorised_by: str | None = None
    scope: list[str] = field(default_factory=list)
    requires_f13: bool = False
    is_irreversible: bool = False
    alters_constitution: bool = False
    changes_its_own_authority: bool = False
    changes_its_own_evaluator: bool = False
    changes_its_own_permissions: bool = False
    blast_radius: str = "low"  # low | medium | high | critical
    evidence_provenance_complete: bool = True
    rollback_tested: bool = True
    independent_verification_passed: bool = True
    authority_valid: bool = True
    authority_scope: list[str] = field(default_factory=list)
    verifier_id: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GATE RESULT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GateResult:
    verdict: GateVerdict
    reason: str
    scope: str | None = None
    expiry: str | None = None
    receipt_required: bool = False
    receipt_hash: str | None = None
    gate_chain: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# GATE CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

class GateChain:
    """
    Boolean gate chain for /777 constitutional burden comparison.
    
    Gates execute in strict order. First failure determines verdict.
    INV-10: Fail closed on authority ambiguity.
    """

    # Blast radius → expiry mapping
    BLAST_RADIUS_EXPIRY: dict[str, timedelta] = {
        "low": timedelta(hours=24),
        "medium": timedelta(hours=12),
        "high": timedelta(hours=6),
        "critical": timedelta(hours=1),
    }

    def evaluate(self, proposal: Proposal) -> GateResult:
        """Run the full gate chain. Returns first failure or PERMIT."""
        gates: list[tuple[str, Any]] = [
            ("G1_AUTHORITY_VALID", self._gate_authority_valid),
            ("G2_NO_SELF_AMENDMENT", self._gate_no_self_amendment),
            ("G3_EVIDENCE_PROVENANCE", self._gate_evidence_provenance),
            ("G4_ROLLBACK_TESTED", self._gate_rollback_tested),
            ("G5_INDEPENDENT_VERIFICATION", self._gate_independent_verification),
            ("G6_F13_REQUIRED", self._gate_f13_required),
            ("G7_REVERSIBILITY_CHECK", self._gate_reversibility_check),
        ]

        passed_gates: list[str] = []
        for gate_name, gate_fn in gates:
            result = gate_fn(proposal)
            if result is not None:
                # Gate failed
                return GateResult(
                    verdict=result[0],
                    reason=f"{gate_name}: {result[1]}",
                    gate_chain=passed_gates + [gate_name],
                )
            passed_gates.append(gate_name)

        # All gates passed → PERMIT
        expiry_dt = datetime.now(UTC) + self.BLAST_RADIUS_EXPIRY.get(
            proposal.blast_radius, timedelta(hours=24)
        )
        receipt = self._make_receipt(proposal)

        return GateResult(
            verdict=GateVerdict.PERMIT,
            reason="All gates passed",
            scope=json.dumps(proposal.scope),
            expiry=expiry_dt.isoformat(),
            receipt_required=True,
            receipt_hash=receipt,
            gate_chain=passed_gates,
        )

    # ───────────────────────────────────────────────────────────────────────
    # Individual gates
    # ───────────────────────────────────────────────────────────────────────

    def _gate_authority_valid(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G1: Authority must be valid for this action class."""
        if not p.authority_valid:
            return (GateVerdict.REJECTED, "AUTHORITY_INVALID: authority not valid for this action")
        if p.action_class.value not in p.authority_scope and p.authority_scope:
            return (
                GateVerdict.REJECTED,
                f"AUTHORITY_SCOPE: {p.action_class.value} not in authority scope {p.authority_scope}",
            )
        return None

    def _gate_no_self_amendment(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G2: Agent cannot change its own authority or evaluator."""
        if p.changes_its_own_authority:
            return (
                GateVerdict.REJECTED,
                "SELF_AMENDMENT: agent cannot change its own authority",
            )
        if p.changes_its_own_evaluator:
            return (
                GateVerdict.REJECTED,
                "SELF_AMENDMENT: agent cannot change its own evaluator",
            )
        return None

    def _gate_evidence_provenance(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G3: Evidence provenance must be complete."""
        if not p.evidence_provenance_complete:
            return (
                GateVerdict.REJECTED,
                "PROVENANCE_INCOMPLETE: evidence provenance must be complete",
            )
        return None

    def _gate_rollback_tested(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G4: Rollback must be tested for irreversible actions."""
        if p.is_irreversible and not p.rollback_tested:
            return (
                GateVerdict.REJECTED,
                "ROLLBACK_UNTESTED: irreversible action requires tested rollback",
            )
        return None

    def _gate_independent_verification(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G5: Independent verification required for PROMOTE/EXECUTE."""
        if p.action_class in (ActionClass.PROMOTE, ActionClass.EXECUTE):
            if not p.independent_verification_passed:
                return (
                    GateVerdict.QUARANTINED,
                    "INDEPENDENT_VERIFICATION_REQUIRED: promotion/execution requires verification",
                )
            # Also check: verifier cannot be the same as proposer
            if p.verifier_id and p.verifier_id == p.proposed_by:
                return (
                    GateVerdict.REJECTED,
                    "SEPARATION_OF_POWERS: verifier cannot be the same agent as proposer",
                )
        return None

    def _gate_f13_required(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G6: F13 required when declared or for high-consequence actions."""
        if p.requires_f13 and p.authorised_by is None:
            return (
                GateVerdict.REJECTED,
                "F13_REQUIRED: proposal requires F13 ratification but none provided",
            )
        if p.alters_constitution and p.authorised_by is None:
            return (
                GateVerdict.REJECTED,
                "F13_REQUIRED: constitutional change requires F13 ratification",
            )
        if p.action_class == ActionClass.EXECUTE and p.blast_radius in ("high", "critical"):
            if p.authorised_by is None:
                return (
                    GateVerdict.REJECTED,
                    "F13_REQUIRED: high-consequence execution requires F13",
                )
        return None

    def _gate_reversibility_check(self, p: Proposal) -> tuple[GateVerdict, str] | None:
        """G7: Irreversible actions need explicit scope and blast radius assessment."""
        if p.is_irreversible:
            if p.blast_radius == "critical":
                if p.authorised_by is None:
                    return (
                        GateVerdict.REJECTED,
                        "CRITICAL_REVERSIBILITY: critical irreversible action requires F13",
                    )
        return None

    # ───────────────────────────────────────────────────────────────────────
    # Receipt
    # ───────────────────────────────────────────────────────────────────────

    def _make_receipt(self, p: Proposal) -> str:
        """Generate content hash for the proposal receipt."""
        payload = json.dumps({
            "case_id": p.case_id,
            "action_class": p.action_class.value,
            "proposed_by": p.proposed_by,
            "scope": p.scope,
            "created_at": p.created_at,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
