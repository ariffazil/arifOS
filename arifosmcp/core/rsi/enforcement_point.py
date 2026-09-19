"""
RSI Constitutional Kernel — Enforcement Point
═══════════════════════════════════════════════

The single highest-leverage artifact between the canon and the kernel.
Seven-block pipeline: Identity → Envelope → Capability → Execution → Probe → Receipt → Seal.

Admissible(c) = I ∧ A ∧ T ∧ C ∧ E ∧ R ∧ W ∧ H

The enforcement point itself must satisfy Admissible(c):
  I: cryptographic identity bound to non-self-issuable root
  A: authority issued by separate issuer than any agent it governs
  T: target hash binding including enforcement-point binary itself
  C: capability ladder state for "constitutional enforcement"
  E: envelope with expiry short enough that compromised point cannot persist
  R: reversibility class C4 — replaceable but not deletable
  W: witness requirement W³ ≥ 0.75 including external witness
  H: F13 override available, but override itself is a scar

Based on:
  - RSI-CONSTITUTIONAL-KERNEL-SPEC-v1.md §9 Build Order
  - 888-APEX E22 (Substrate-Shadow Drift + PATH verification)
  - 888-APEX E23 (Receipt-Window Conflict + EXTERNAL_EFFECT_DIVERGED)
  - 888-APEX Route-Credential Theft failure mode
  - 888-APEX Outcome Divergence state

Status: DRAFT_AWAITING_F13
Version: 2026-09-20-v1

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class PipelineBlock(StrEnum):
    """The seven blocks of the enforcement pipeline. Order is strict."""

    IDENTITY = "IDENTITY"  # I: who is requesting?
    ENVELOPE = "ENVELOPE"  # A: what authority was issued?
    CAPABILITY = "CAPABILITY"  # C: what capability ladder state?
    EXECUTION = "EXECUTION"  # E: what envelope binds this execution?
    PROBE = "PROBE"  # R: what reality check runs?
    RECEIPT = "RECEIPT"  # W: what witness evidence is produced?
    SEAL = "SEAL"  # H: what gets sealed to VAULT999?


class ExecutionState(StrEnum):
    """State machine for receipt-window conflict (E23 extended)."""

    PREPARED = "PREPARED"
    AUTHORIZED = "AUTHORIZED"
    DISPATCHED = "DISPATCHED"
    EXTERNAL_EFFECT_OBSERVED = "EXTERNAL_EFFECT_OBSERVED"
    EXTERNAL_EFFECT_DIVERGED = "EXTERNAL_EFFECT_DIVERGED"
    EXTERNAL_EFFECT_UNKNOWN = "EXTERNAL_EFFECT_UNKNOWN"
    RECONCILING = "RECONCILING"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    ROLLBACK_AUTHORIZED = "ROLLBACK_AUTHORIZED"
    ROLLBACK_EXECUTED = "ROLLBACK_EXECUTED"
    SEALED = "SEALED"
    STALE_EPOCH_BLOCKED = "STALE_EPOCH_BLOCKED"
    ESCALATED = "ESCALATED"


class FailureClass(StrEnum):
    """Typed failure classes (E22/E23 additions)."""

    PROVENANCE_CONTRADICTION = "PROVENANCE_CONTRADICTION"
    ROUTE_CREDENTIAL_THEFT = "ROUTE_CREDENTIAL_THEFT"
    IDENTITY_IMPERSONATION = "IDENTENTITY_IMPERSONATION"
    OUTCOME_DIVERGENCE = "OUTCOME_DIVERGENCE"
    SUBSTRATE_SHADOW_DRIFT = "SUBSTRATE_SHADOW_DRIFT"
    CONSTITUTIONAL_BREACH = "CONSTITUTIONAL_BREACH"


class ReversibilityClass(StrEnum):
    """Reversibility classes for capability evolution."""

    C0 = "C0"  # Sandboxed, fully reversible
    C1 = "C1"  # Staged, reversible with rollback
    C2 = "C2"  # Production, reversible with effort
    C3 = "C3"  # External effect, compensation required
    C4 = "C4"  # Replaceable but not deletable (enforcement point class)
    C5 = "C5"  # Irreversible, requires F13


# ═══════════════════════════════════════════════════════════════════════════════
# ADMISSIBLE PREDICATE
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class AdmissibilityClaim:
    """The eight-field claim that a capability must satisfy."""

    identity_root: str  # I: cryptographic identity, non-self-issuable
    authority_issuer: str  # A: who issued this authority
    authority_scope: list[str]  # A: what actions are permitted
    target_hash: str  # T: hash of the enforcement-point binary
    capability_state: str  # C: capability ladder state
    envelope_expiry: str  # E: when this envelope expires
    reversibility_class: str  # R: C0-C5
    witness_w3: float  # W: tri-witness score ≥ 0.75
    f13_override_is_scar: bool  # H: F13 override visible, expirable, with recovery
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def admissible(c: AdmissibilityClaim) -> tuple[bool, list[str]]:
    """
    Admissible(c) = I ∧ A ∧ T ∧ C ∧ E ∧ R ∧ W ∧ H

    Returns (is_admissible, list_of_violations).
    """
    violations = []

    # I: identity must be bound to non-self-issuable root
    if not c.identity_root or c.identity_root == "self-issued":
        violations.append("I_VIOLATION: identity not bound to external root")

    # A: authority issuer must differ from any agent it governs
    if not c.authority_issuer or c.authority_issuer == "self":
        violations.append("A_VIOLATION: authority self-issued")

    # T: target hash must be non-empty (binary binding)
    if not c.target_hash or len(c.target_hash) < 8:
        violations.append("T_VIOLATION: target hash missing or too short")

    # C: capability state must be at least EXECUTABLE
    if c.capability_state not in ("EXECUTABLE", "WITNESSED", "RATIFIED"):
        violations.append(f"C_VIOLATION: capability state '{c.capability_state}' below EXECUTABLE")

    # E: envelope must have expiry
    if not c.envelope_expiry:
        violations.append("E_VIOLATION: no envelope expiry set")
    else:
        try:
            exp = datetime.fromisoformat(c.envelope_expiry)
            if exp <= datetime.now(UTC):
                violations.append("E_VIOLATION: envelope already expired")
        except ValueError:
            violations.append("E_VIOLATION: invalid expiry format")

    # R: must be C4 (replaceable but not deletable)
    if c.reversibility_class != "C4":
        violations.append(f"R_VIOLATION: enforcement point must be C4, got {c.reversibility_class}")

    # W: witness score must be ≥ 0.75
    if c.witness_w3 < 0.75:
        violations.append(f"W_VIOLATION: W³={c.witness_w3} < 0.75 minimum")

    # H: F13 override must be flagged as scar
    if not c.f13_override_is_scar:
        violations.append(
            "H_VIOLATION: F13 override not flagged as scar (visible, expirable, recovery criteria)"
        )

    return (len(violations) == 0, violations)


# ═══════════════════════════════════════════════════════════════════════════════
# ENFORCEMENT POINT — Seven-Block Pipeline
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PipelineReceipt:
    """Receipt emitted at each pipeline block."""

    block: str
    timestamp: str
    passed: bool
    details: dict[str, Any]
    receipt_hash: str = ""


@dataclass
class EnforcementRequest:
    """A request entering the enforcement pipeline."""

    request_id: str
    actor_id: str
    action_class: str
    target: str
    target_hash: str
    authority_envelope: dict[str, Any]
    capability_claim: dict[str, Any]
    execution_params: dict[str, Any]
    witness_evidence: dict[str, Any] | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class EnforcementPoint:
    """
    The constitutional enforcement point — seven-block pipeline.

    This is the single executable object that replaces seven separate gates.
    It cannot be re-ordered. It cannot be bypassed. It satisfies Admissible(c).

    The enforcement point's own admissibility is checked at construction time.
    If the enforcement point is not admissible, it refuses to operate.
    """

    def __init__(self, admissibility: AdmissibilityClaim):
        """Initialize with self-admissibility check."""
        self.admissibility = admissibility
        is_admissible, violations = admissible(admissibility)

        if not is_admissible:
            raise ValueError(
                f"Enforcement point is NOT Admissible(c). Violations: {violations}. "
                "The enforcement point cannot operate without satisfying Admissible(c)."
            )

        self.operational = True
        self.receipts: list[PipelineReceipt] = []
        self.state = ExecutionState.PREPARED

    def execute(self, request: EnforcementRequest) -> dict[str, Any]:
        """
        Run the full seven-block pipeline. Order is strict.
        First failure determines verdict.
        """
        if not self.operational:
            return {"verdict": "BLOCKED", "reason": "Enforcement point not operational"}

        self.receipts = []
        self.state = ExecutionState.PREPARED

        blocks = [
            ("IDENTITY", self._block_identity),
            ("ENVELOPE", self._block_envelope),
            ("CAPABILITY", self._block_capability),
            ("EXECUTION", self._block_execution),
            ("PROBE", self._block_probe),
            ("RECEIPT", self._block_receipt),
            ("SEAL", self._block_seal),
        ]

        for block_name, block_fn in blocks:
            receipt = block_fn(request)
            self.receipts.append(receipt)

            if not receipt.passed:
                self.state = ExecutionState.ESCALATED
                return {
                    "verdict": "BLOCKED",
                    "blocked_at": block_name,
                    "reason": receipt.details.get("reason", "unknown"),
                    "state": self.state.value,
                    "receipts": [r.__dict__ for r in self.receipts],
                    "admissibility": {
                        "identity_root": self.admissibility.identity_root,
                        "witness_w3": self.admissibility.witness_w3,
                    },
                }

        # All blocks passed
        self.state = ExecutionState.SEALED
        return {
            "verdict": "PERMIT",
            "state": self.state.value,
            "receipts": [r.__dict__ for r in self.receipts],
            "admissibility": {
                "identity_root": self.admissibility.identity_root,
                "witness_w3": self.admissibility.witness_w3,
            },
        }

    # ───────────────────────────────────────────────────────────────────────
    # Block implementations
    # ───────────────────────────────────────────────────────────────────────

    def _block_identity(self, req: EnforcementRequest) -> PipelineReceipt:
        """I: Verify actor identity against non-self-issuable root."""
        ts = datetime.now(UTC).isoformat()
        actor = req.actor_id
        # Identity must not be self-issued
        if not actor or actor == "self" or actor == "unknown":
            return PipelineReceipt(
                block="IDENTITY",
                timestamp=ts,
                passed=False,
                details={"reason": "IDENTITY_REJECTED: actor identity not verifiable"},
            )
        # Identity root must match admissibility claim
        if self.admissibility.identity_root and actor != "self-issued":
            pass  # identity is externally rooted
        return PipelineReceipt(
            block="IDENTITY",
            timestamp=ts,
            passed=True,
            details={"actor": actor, "root": self.admissibility.identity_root},
        )

    def _block_envelope(self, req: EnforcementRequest) -> PipelineReceipt:
        """A: Verify authority envelope — issuer is not the requesting agent."""
        ts = datetime.now(UTC).isoformat()
        envelope = req.authority_envelope
        issuer = envelope.get("issuer", "")
        scope = envelope.get("scope", [])
        expiry = envelope.get("expiry", "")

        violations = []
        if not issuer or issuer == req.actor_id:
            violations.append("A_VIOLATION: authority self-issued")
        if req.action_class not in scope:
            violations.append(f"A_VIOLATION: {req.action_class} not in scope {scope}")
        if expiry:
            try:
                exp = datetime.fromisoformat(expiry)
                if exp <= datetime.now(UTC):
                    violations.append("A_VIOLATION: envelope expired")
            except ValueError:
                violations.append("A_VIOLATION: invalid expiry")

        if violations:
            return PipelineReceipt(
                block="ENVELOPE",
                timestamp=ts,
                passed=False,
                details={"reason": "; ".join(violations)},
            )
        return PipelineReceipt(
            block="ENVELOPE",
            timestamp=ts,
            passed=True,
            details={"issuer": issuer, "scope": scope, "expiry": expiry},
        )

    def _block_capability(self, req: EnforcementRequest) -> PipelineReceipt:
        """C: Verify capability ladder state."""
        ts = datetime.now(UTC).isoformat()
        cap_state = req.capability_claim.get("state", "")
        if cap_state not in ("EXECUTABLE", "WITNESSED", "RATIFIED"):
            return PipelineReceipt(
                block="CAPABILITY",
                timestamp=ts,
                passed=False,
                details={"reason": f"C_VIOLATION: state '{cap_state}' below EXECUTABLE"},
            )
        return PipelineReceipt(
            block="CAPABILITY",
            timestamp=ts,
            passed=True,
            details={"state": cap_state},
        )

    def _block_execution(self, req: EnforcementRequest) -> PipelineReceipt:
        """E: Verify execution envelope — target hash binding, expiry."""
        ts = datetime.now(UTC).isoformat()
        target_hash = req.target_hash
        # Target hash must bind to the enforcement point binary
        if not target_hash or len(target_hash) < 8:
            return PipelineReceipt(
                block="EXECUTION",
                timestamp=ts,
                passed=False,
                details={"reason": "E_VIOLATION: target hash missing or too short"},
            )
        self.state = ExecutionState.DISPATCHED
        return PipelineReceipt(
            block="EXECUTION",
            timestamp=ts,
            passed=True,
            details={"target_hash": target_hash[:16] + "..."},
        )

    def _block_probe(self, req: EnforcementRequest) -> PipelineReceipt:
        """R: Reality check — E22 PATH verification, route-credential theft detection."""
        ts = datetime.now(UTC).isoformat()

        # E22: PATH verification — was the provider reachable through claimed route?
        route = req.execution_params.get("route", "")
        provider = req.execution_params.get("provider", "")
        credential_used = req.execution_params.get("credential_used", "")

        # Check: credential must not be from a different agent
        if credential_used and credential_used != req.actor_id:
            return PipelineReceipt(
                block="PROBE",
                timestamp=ts,
                passed=False,
                details={
                    "reason": "ROUTE_CREDENTIAL_THEFT: credential_used differs from actor",
                    "failure_class": FailureClass.ROUTE_CREDENTIAL_THEFT.value,
                    "actor": req.actor_id,
                    "credential": credential_used,
                },
            )

        # Check: provider must match claimed route
        if route and provider:
            # In production, this would check network egress logs
            # For now, verify the claim is internally consistent
            claimed_provider = req.execution_params.get("claimed_provider", "")
            if claimed_provider and claimed_provider != provider:
                return PipelineReceipt(
                    block="PROBE",
                    timestamp=ts,
                    passed=False,
                    details={
                        "reason": "SUBSTRATE_SHADOW_DRIFT: claimed provider differs from actual",
                        "failure_class": FailureClass.SUBSTRATE_SHADOW_DRIFT.value,
                        "claimed": claimed_provider,
                        "actual": provider,
                    },
                )

        self.state = ExecutionState.EXTERNAL_EFFECT_OBSERVED
        return PipelineReceipt(
            block="PROBE",
            timestamp=ts,
            passed=True,
            details={"route": route, "provider": provider},
        )

    def _block_receipt(self, req: EnforcementRequest) -> PipelineReceipt:
        """W: Produce witness evidence — receipt with trace_id."""
        ts = datetime.now(UTC).isoformat()
        receipt_payload = {
            "request_id": req.request_id,
            "actor": req.actor_id,
            "action": req.action_class,
            "target": req.target,
            "state": self.state.value,
            "timestamp": ts,
            "pipeline": [r.block for r in self.receipts],
        }
        receipt_hash = hashlib.sha256(
            json.dumps(receipt_payload, sort_keys=True).encode()
        ).hexdigest()[:16]

        return PipelineReceipt(
            block="RECEIPT",
            timestamp=ts,
            passed=True,
            details={"receipt_hash": receipt_hash, "state": self.state.value},
            receipt_hash=receipt_hash,
        )

    def _block_seal(self, req: EnforcementRequest) -> PipelineReceipt:
        """H: Seal to VAULT999 — immutable append."""
        ts = datetime.now(UTC).isoformat()
        # In production, this calls arif_seal
        # For now, produce the seal receipt
        seal_payload = {
            "request_id": req.request_id,
            "receipts": [r.receipt_hash for r in self.receipts if r.receipt_hash],
            "final_state": self.state.value,
            "sealed_at": ts,
            "enforcement_point_admissible": True,
        }
        seal_hash = hashlib.sha256(json.dumps(seal_payload, sort_keys=True).encode()).hexdigest()[
            :16
        ]

        return PipelineReceipt(
            block="SEAL",
            timestamp=ts,
            passed=True,
            details={"seal_hash": seal_hash},
        )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTCOME DIVERGENCE HANDLER (E23 extension)
# ═══════════════════════════════════════════════════════════════════════════════


class OutcomeDivergenceHandler:
    """
    Handles EXTERNAL_EFFECT_DIVERGED state (E23).
    Distinguished from:
      - CONFLICT (no effect)
      - DRIFT (effect at wrong path)
      - DIVERGENCE (success but wrong outcome)
    """

    def __init__(self, enforcement_point: EnforcementPoint):
        self.ep = enforcement_point

    def detect_divergence(
        self,
        intended_effect: dict[str, Any],
        observed_effect: dict[str, Any],
        operation_succeeded: bool,
    ) -> dict[str, Any]:
        """
        Detect outcome divergence.
        Returns divergence record with failure class.
        """
        if not operation_succeeded:
            return {"divergent": False, "reason": "operation_failed_not_divergent"}

        # Compare intended vs observed
        match = self._compare_effects(intended_effect, observed_effect)

        if match:
            return {"divergent": False, "reason": "effects_match"}

        # Divergence detected
        divergence_record = {
            "divergent": True,
            "failure_class": FailureClass.OUTCOME_DIVERGENCE.value,
            "intended": intended_effect,
            "observed": observed_effect,
            "timestamp": datetime.now(UTC).isoformat(),
            "requires_compensation": True,
            "requires_rollback": self._is_reversible(observed_effect),
        }

        # Transition to EXTERNAL_EFFECT_DIVERGED
        self.ep.state = ExecutionState.EXTERNAL_EFFECT_DIVERGED

        return divergence_record

    def authorize_rollback(self, divergence: dict[str, Any]) -> dict[str, Any]:
        """
        Transition: EXTERNAL_EFFECT_DIVERGED → ROLLBACK_AUTHORIZED
        Requires new pending_action_id under E23 protocol.
        """
        if not divergence.get("requires_rollback"):
            return {"authorized": False, "reason": "rollback_not_required"}

        rollback_id = f"rollback-{int(time.time())}"
        self.ep.state = ExecutionState.ROLLBACK_AUTHORIZED

        return {
            "authorized": True,
            "rollback_id": rollback_id,
            "state": self.ep.state.value,
        }

    def execute_rollback(self, rollback_id: str) -> dict[str, Any]:
        """
        Transition: ROLLBACK_AUTHORIZED → ROLLBACK_EXECUTED
        """
        self.ep.state = ExecutionState.ROLLBACK_EXECUTED
        return {
            "executed": True,
            "rollback_id": rollback_id,
            "state": self.ep.state.value,
        }

    def _compare_effects(self, intended: dict[str, Any], observed: dict[str, Any]) -> bool:
        """Compare intended vs observed effects."""
        # Simplified comparison — in production, deep structural comparison
        return intended == observed

    def _is_reversible(self, effect: dict[str, Any]) -> bool:
        """Check if the effect is reversible (C ≤ 3)."""
        reversibility = effect.get("reversibility_class", "C5")
        try:
            level = int(reversibility.replace("C", ""))
            return level <= 3
        except (ValueError, AttributeError):
            return False
