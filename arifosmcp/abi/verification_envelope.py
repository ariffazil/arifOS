"""
verification_envelope.py — VERIFY111 Proof Spine Contract (2026-07-30)
══════════════════════════════════════════════════════════════════════════

THE shared schema for verification across arifOS, A-FORGE, arifFlow, and VAULT999.
Wraps existing independent_verifier.py + attestation_verifier.py components.
Does NOT replace them — gives them a common contract.

One envelope travels through:
  arif_think(expected state) → arif_judge(approve) →
  A-FORGE(execute) → independent_verifier(observe) →
  arif_judge(compare) → VAULT999(record)

5 Hard Rejection Rules (from independent_verifier.py WAJIB 2):
  R1: Verifier ≠ Executor (separate identity)
  R2: Evidence from outside executor's session
  R3: Verifier OBSERVE-only (no mutation authority)
  R4: Evidence freshness ≤ max_age
  R5: Success criteria explicitly defined and verified

Authority: T3 F13 (ratified 2026-07-19)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Disposition(str, Enum):
    """Post-verification disposition."""

    PASS = "PASS"  # Expected == Actual, proceed to SEAL
    HOLD = "HOLD"  # Cannot verify, missing evidence
    ROLLBACK = "ROLLBACK"  # Expected != Actual, revert
    ESCALATE = "ESCALATE"  # Value/sovereignty conflict → Arif


class ReasonCode(str, Enum):
    """Typed HOLD reason codes — machine-readable, not narrative."""

    DEPLOYED_COMMIT_MISMATCH = "DEPLOYED_COMMIT_MISMATCH"
    STATE_MISMATCH = "STATE_MISMATCH"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    AUTHORITY_MISSING = "AUTHORITY_MISSING"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    EVIDENCE_CONFLICT = "EVIDENCE_CONFLICT"
    AUTOMATED_POLICY_FAIL = "AUTOMATED_POLICY_FAIL"
    AUTOMATED_EVIDENCE_FAIL = "AUTOMATED_EVIDENCE_FAIL"
    HUMAN_JUDGMENT_REQUIRED = "HUMAN_JUDGMENT_REQUIRED"
    SYSTEM_FAULT = "SYSTEM_FAULT"
    VERIFIER_IDENTITY_VIOLATION = "VERIFIER_IDENTITY_VIOLATION"
    FRESHNESS_EXCEEDED = "FRESHNESS_EXCEEDED"
    SUCCESS_CRITERIA_UNDEFINED = "SUCCESS_CRITERIA_UNDEFINED"


@dataclass
class ExpectedState:
    """What the mission intends to achieve — declared BEFORE execution."""

    assertions: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    forbidden_states: list[str] = field(default_factory=list)
    state_hash: str = ""


@dataclass
class PreVerification:
    """Pre-execution checks — run BEFORE mutation."""

    checks: list[str] = field(default_factory=list)
    result: bool = False
    evidence_hash: str = ""


@dataclass
class ExecutionRecord:
    """What the executor claims happened."""

    executor: str = ""
    plan_hash: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0
    claimed_delta: dict[str, Any] = field(default_factory=dict)
    receipt_hash: str = ""


@dataclass
class PostVerification:
    """What the independent verifier observed."""

    verifier: str = ""
    independent_from_executor: bool = True
    observations: list[str] = field(default_factory=list)
    assertion_results: dict[str, bool] = field(default_factory=dict)
    actual_state_hash: str = ""


@dataclass
class TypedHOLD:
    """Machine-readable HOLD — answers 5 mandatory questions."""

    reason_code: ReasonCode = ReasonCode.EVIDENCE_MISSING
    failed_assertion: str = ""
    evidence_missing: str = ""
    cheapest_resolution: str = ""
    automatic_recheck: bool = False
    human_attention_required: bool = False
    expires_at: float = 0.0


@dataclass
class VerificationEnvelope:
    """THE contract. One envelope from intent to vault.

    Travels through: think → judge → execute → verify → compare → seal.
    Every component reads/writes this same shape.
    """

    # ── Identity ──
    mission_id: str = ""
    action_id: str = ""
    actor: str = ""
    authority: str = "OBSERVE_ONLY"
    capability: str = ""
    risk_class: str = (
        "OBSERVE"  # OBSERVE | COMPUTE | MUTATE | PUBLISH | TRANSACT | DELETE | PHYSICAL
    )

    # ── Intent ──
    desired_outcome: str = ""
    forbidden_outcomes: list[str] = field(default_factory=list)

    # ── Expected state (from arif_think) ──
    expected_state: ExpectedState = field(default_factory=ExpectedState)

    # ── Pre-verification (from arif_judge pre-gate) ──
    pre_verification: PreVerification = field(default_factory=PreVerification)

    # ── Execution (from A-FORGE) ──
    execution: ExecutionRecord = field(default_factory=ExecutionRecord)

    # ── Post-verification (from independent verifier) ──
    post_verification: PostVerification = field(default_factory=PostVerification)

    # ── Comparison ──
    expected_state_hash: str = ""
    actual_state_hash: str = ""
    match: bool = False
    deviations: list[str] = field(default_factory=list)

    # ── Disposition ──
    disposition: Disposition = Disposition.HOLD
    reason_codes: list[ReasonCode] = field(default_factory=list)
    automatic_recheck: bool = False
    human_attention_required: bool = False

    # ── Typed HOLD (populated when disposition != PASS) ──
    hold: TypedHOLD | None = None

    # ── Lineage ──
    merkle_root: str = ""
    vault_entry: str = ""
    previous_receipt: str = ""
    sealed_at: float = 0.0

    # ── Audit ──
    envelope_version: str = "v1.0"
    forged_at: float = field(default_factory=time.time)


# ── Factory helpers ──────────────────────────────────────────────────────


def new_envelope(
    mission_id: str = "",
    actor: str = "",
    desired_outcome: str = "",
    risk_class: str = "OBSERVE",
) -> VerificationEnvelope:
    """Create a fresh envelope for a new mission."""
    action_id = hashlib.sha256(f"{mission_id}|{actor}|{time.time()}".encode()).hexdigest()[:16]
    return VerificationEnvelope(
        mission_id=mission_id,
        action_id=action_id,
        actor=actor,
        risk_class=risk_class,
        desired_outcome=desired_outcome,
    )


def make_hold(
    reason_code: ReasonCode,
    failed_assertion: str = "",
    evidence_missing: str = "",
    cheapest_resolution: str = "",
    automatic_recheck: bool = False,
    human_attention_required: bool = False,
) -> TypedHOLD:
    """Create a typed HOLD — machine-readable, 5 mandatory fields."""
    return TypedHOLD(
        reason_code=reason_code,
        failed_assertion=failed_assertion,
        evidence_missing=evidence_missing,
        cheapest_resolution=cheapest_resolution,
        automatic_recheck=automatic_recheck,
        human_attention_required=human_attention_required,
    )


def compare_states(envelope: VerificationEnvelope) -> VerificationEnvelope:
    """Compare expected vs actual state. Populates match + disposition."""
    expected = (
        envelope.expected_state_hash
        or hashlib.sha256(str(envelope.expected_state).encode()).hexdigest()[:16]
    )
    actual = envelope.post_verification.actual_state_hash

    envelope.expected_state_hash = expected
    envelope.actual_state_hash = actual

    if not actual:
        envelope.match = False
        envelope.disposition = Disposition.HOLD
        envelope.reason_codes = [ReasonCode.EVIDENCE_MISSING]
        envelope.hold = make_hold(
            reason_code=ReasonCode.EVIDENCE_MISSING,
            evidence_missing="No actual state hash from independent verifier",
            cheapest_resolution="Re-run with independent verifier wired",
            automatic_recheck=True,
            human_attention_required=False,
        )
        return envelope

    if expected == actual:
        envelope.match = True
        envelope.disposition = Disposition.PASS
    else:
        envelope.match = False
        envelope.disposition = Disposition.ROLLBACK
        envelope.reason_codes = [ReasonCode.STATE_MISMATCH]
        envelope.deviations = [f"Expected hash {expected}, got {actual}"]
        envelope.hold = make_hold(
            reason_code=ReasonCode.STATE_MISMATCH,
            failed_assertion=f"expected_state_hash == actual_state_hash ({expected} != {actual})",
            cheapest_resolution="Rollback to previous state or repair to match expected",
            automatic_recheck=False,
            human_attention_required=False,
        )

    return envelope


# ── Verification telemetry (for arif_init validate) ────────────────────


@dataclass
class VerificationTelemetry:
    """Public proof summary — returned by arif_init(mode=validate)."""

    kernel_alive: bool = False
    protocol_conformant: bool = False
    active_profile: str = "public_agent"
    actor_verified: bool = False
    authority: str = "OBSERVE_ONLY"
    vault_replay: bool = False
    receipt_chain_valid: bool = False
    verifier_plane_ready: bool = False
    independent_verifier_available: bool = False
    attestation_verifier_available: bool = False
    last_verified_mission: str = ""
    substrate_gate: str = "AMBER"  # GREEN | AMBER | RED
    verified_at: float = field(default_factory=time.time)


def collect_verification_telemetry() -> VerificationTelemetry:
    """Probe live components and return verification health."""
    telemetry = VerificationTelemetry()

    # Check independent verifier
    try:
        from arifosmcp.runtime.independent_verifier import (
            VerificationVerdict,
            verify_independent,
        )

        telemetry.independent_verifier_available = True
    except ImportError:
        pass

    # Check attestation verifier
    try:
        from arifosmcp.abi.attestation_verifier import AttestationVerifier

        telemetry.attestation_verifier_available = True
    except ImportError:
        pass

    # Check vault
    try:
        from arifosmcp.core.vault999.verify import (
            verify_chain as _vault_verify_chain,
        )

        telemetry.vault_replay = True
    except ImportError:
        pass

    # Verifier plane ready = independent verifier reachable
    telemetry.verifier_plane_ready = telemetry.independent_verifier_available

    # Substrate gate
    if telemetry.verifier_plane_ready and telemetry.vault_replay:
        telemetry.substrate_gate = "GREEN"
    elif telemetry.independent_verifier_available or telemetry.attestation_verifier_available:
        telemetry.substrate_gate = "AMBER"
    else:
        telemetry.substrate_gate = "RED"

    # Kernel alive = we're executing this code
    telemetry.kernel_alive = True
    telemetry.protocol_conformant = True

    return telemetry
