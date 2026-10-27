"""
arifosmcp/contracts/governed_transition.py — ADR-015 Canonical Governed Transition Contract

Ratified by ARIF F13 on 2026-10-28 (ADR-015, commit a1a75cc1d, SHA-256 da38c7be...).
Implements:
  1. Orthogonal Authority Domains (SessionCapabilityLease, ExecutionAuthorizationGrant,
     EpistemicActionTier, FederationAuthorityBand) composed under AuthorityEnvelope.
  2. Bounded ExecutionAuthorizationGrant with single-use, expiry, and hash binding.
  3. SovereignAttestation with strict subject binding.
  4. Typed Receipt Taxonomy (AUTH, EXEC, DEPLOY, VERIFY, ACCEPTANCE, CLOSE).
  5. GovernedTransition lifecycle contract (authorization != execution != deployment != outcome != acceptance).
  6. Consumer-Specific Legacy Projections (LegacySealProjection).
  7. Formula-Version Registry (apex-g-v2-runtime vs apex-g-v3-proposed).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ORTHOGONAL AUTHORITY DOMAINS (ADR-015 Decision 1)
# ═══════════════════════════════════════════════════════════════════════════════

class AssuranceLevel(StrEnum):
    ANONYMOUS = "anonymous"
    DECLARED = "declared"
    ED25519_VERIFIED = "ed25519_verified"
    SCT_VERIFIED = "sct_verified"
    SOVEREIGN_CRYPTOGRAPHIC = "sovereign_cryptographic"


class IdentityAssurance(BaseModel):
    """Identity verification domain — who is claiming and what was proven."""
    model_config = ConfigDict(frozen=True)

    claimed_actor_id: str = Field(default="anonymous", description="Claimed identity string")
    verified_actor_id: str | None = Field(default=None, description="Cryptographically proven identity")
    assurance_level: AssuranceLevel = Field(default=AssuranceLevel.ANONYMOUS)
    verification_method: str = Field(default="none", description="e.g. ed25519, sct, jwt, none")
    verified_at: str | None = Field(default=None, description="ISO-8601 verification timestamp")


class ConstitutionalRole(StrEnum):
    SOVEREIGN = "SOVEREIGN"
    OPERATOR = "OPERATOR"
    AUDITOR = "AUDITOR"
    AGENT = "AGENT"
    ANONYMOUS = "ANONYMOUS"


class ConstitutionalAuthority(BaseModel):
    """Constitutional tier and floor governance scope."""
    model_config = ConfigDict(frozen=True)

    role: ConstitutionalRole = Field(default=ConstitutionalRole.ANONYMOUS)
    jurisdiction: str = Field(default="standard", description="Organ or territory boundary")
    floors_enforced: list[str] = Field(default_factory=lambda: [f"F{i}" for i in range(1, 14)])
    verdict_authority: bool = Field(default=False, description="True ONLY for 888_APEX / kernel judge")


class EpistemicActionTier(StrEnum):
    """Epistemic action permission tier — derived from truth kernel."""
    OBSERVE = "OBSERVE"
    ADVISE = "ADVISE"
    REVERSIBLE_EXECUTE = "REVERSIBLE_EXECUTE"
    REQUIRE_F13 = "REQUIRE_F13"


class FederationAuthorityBand(StrEnum):
    """Inter-organ wire authority band — four-plane protocol."""
    DENIED = "DENIED"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    AUTHORIZED = "AUTHORIZED"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"


class SessionCapabilityLease(BaseModel):
    """Time-bounded, scope-bounded capability lease issued at 000_INIT."""
    model_config = ConfigDict(frozen=True)

    lease_id: str = Field(..., description="Unique capability lease identifier")
    session_id: str = Field(..., description="Bound session ID")
    resource_scope: list[str] = Field(default_factory=list, description="Allowed directory/repo paths")
    allowed_verbs: list[str] = Field(default_factory=list, description="Permitted canonical actions")
    mutation_allowed: bool = Field(default=False)
    destructive_allowed: bool = Field(default=False)
    issued_at: str = Field(..., description="ISO-8601 lease creation time")
    expires_at: str = Field(..., description="ISO-8601 lease expiration time")
    revoked_at: str | None = Field(default=None)

    def is_active(self, at_time: datetime | None = None) -> bool:
        if self.revoked_at is not None:
            return False
        now = at_time or datetime.now(timezone.utc)
        exp = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        return now < exp


class ExecutionAuthorizationGrant(BaseModel):
    """
    Bounded, single-use authorization grant issued by arif_judge at station 888.
    A-FORGE requires this grant before station 900 physical execution.
    Replaces raw 'constitutional_chain_id' as execution credential.
    """
    model_config = ConfigDict(frozen=True)

    authorization_grant_id: str = Field(..., description="Unique grant identifier authz_...")
    proposal_hash: str = Field(..., description="SHA-256 of evaluated proposal")
    plan_hash: str = Field(..., description="SHA-256 of execution plan (dry-run)")
    session_id: str = Field(..., description="Bound session ID")
    actor_id: str = Field(..., description="Bound actor identity")
    executor_id: str = Field(default="a-forge", description="Authorized executor organ")
    allowed_operation: str = Field(..., description="Exact operation allowed")
    target_scope: list[str] = Field(default_factory=list, description="Exact target files/services")
    baseline_hash: str = Field(..., description="Pre-state reality baseline hash")
    policy_version: str = Field(default="2026.10-F13", description="Governing policy version")
    issued_at: str = Field(..., description="ISO-8601 issuance timestamp")
    expires_at: str = Field(..., description="ISO-8601 expiration timestamp")
    single_use: bool = Field(default=True)
    used_at: str | None = Field(default=None)
    revoked_at: str | None = Field(default=None)
    issuer: str = Field(default="arif_judge", description="Authority that issued grant")

    # Backward compatibility alias
    @property
    def constitutional_chain_id(self) -> str:
        """Deprecated lineage alias for legacy A-FORGE callers."""
        return self.authorization_grant_id

    def is_valid_for(
        self,
        proposal_hash: str,
        plan_hash: str,
        executor_id: str,
        target: str,
        at_time: datetime | None = None,
    ) -> tuple[bool, str]:
        """Strict falsifiable verification of the authorization grant."""
        if self.revoked_at is not None:
            return False, f"grant_revoked at {self.revoked_at}"
        if self.single_use and self.used_at is not None:
            return False, f"grant_already_used at {self.used_at}"
        now = at_time or datetime.now(timezone.utc)
        exp = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if now >= exp:
            return False, f"grant_expired at {self.expires_at}"
        if self.proposal_hash != proposal_hash:
            return False, f"proposal_hash_mismatch: expected {self.proposal_hash}, got {proposal_hash}"
        if self.plan_hash != plan_hash:
            return False, f"plan_hash_mismatch: expected {self.plan_hash}, got {plan_hash}"
        if self.executor_id != executor_id:
            return False, f"executor_mismatch: authorized for {self.executor_id}, called by {executor_id}"
        if self.target_scope and target not in self.target_scope:
            return False, f"target_scope_escape: {target} not in {self.target_scope}"
        return True, "valid"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. COMPOSED AUTHORITY ENVELOPE (ADR-015 Decision 1)
# ═══════════════════════════════════════════════════════════════════════════════

class HumanMandate(BaseModel):
    """Sovereign mandate scope and risk limit."""
    sovereign: str = "ARIF"
    mandate_ref: str | None = None
    risk_limit: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW"
    explicit_acceptance_required: bool = True


class RuntimeLifecycleState(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class RuntimeLifecycle(BaseModel):
    state: RuntimeLifecycleState = RuntimeLifecycleState.NOT_STARTED
    started_at: str | None = None
    completed_at: str | None = None
    exit_code: int | None = None


class WitnessStatus(BaseModel):
    receipt_refs: list[str] = Field(default_factory=list)
    w3_coherence: float = Field(default=0.0, ge=0.0, le=1.0)
    independent_verified: bool = False


class AcceptanceStatus(StrEnum):
    UNATTESTED = "UNATTESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


class AuthorityEnvelope(BaseModel):
    """
    CANONICAL COMPOSED AUTHORITY ENVELOPE (ADR-015).
    Composes orthogonal authority domains without collapsing them.
    Preserves backward compatibility via legacy projection methods.
    """
    model_config = ConfigDict(populate_by_name=True)

    identity: IdentityAssurance = Field(default_factory=IdentityAssurance)
    constitutional: ConstitutionalAuthority = Field(default_factory=ConstitutionalAuthority)
    human_mandate: HumanMandate = Field(default_factory=HumanMandate)
    capability_lease: SessionCapabilityLease | None = None
    execution_grant: ExecutionAuthorizationGrant | None = None
    lifecycle: RuntimeLifecycle = Field(default_factory=RuntimeLifecycle)
    witness: WitnessStatus = Field(default_factory=WitnessStatus)
    acceptance: AcceptanceStatus = AcceptanceStatus.UNATTESTED

    # ── Legacy Compatibility Adapters ──────────────────────────────
    @property
    def legacy_execution_authority(self) -> str:
        """Adapter for legacy AuthorityState.execution_authority ('HOLD' | 'SEAL_AUTHORIZED' | 'VOID')."""
        if self.execution_grant is not None:
            valid, _ = self.execution_grant.is_valid_for(
                self.execution_grant.proposal_hash,
                self.execution_grant.plan_hash,
                self.execution_grant.executor_id,
                self.execution_grant.target_scope[0] if self.execution_grant.target_scope else "",
            )
            return "SEAL_AUTHORIZED" if valid else "HOLD"
        return "HOLD"

    def is_sealed_legacy(self) -> bool:
        """DEPRECATED legacy adapter: mirrors AuthorityState.is_sealed()."""
        return self.legacy_execution_authority == "SEAL_AUTHORIZED"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. TYPED RECEIPT TAXONOMY & SOVEREIGN ATTESTATION (ADR-015 Decisions 3 & 6)
# ═══════════════════════════════════════════════════════════════════════════════

class ReceiptType(StrEnum):
    AUTH_RECORD = "AUTH_RECORD"          # Pre-action authorization grant recorded
    EXEC_RECORD = "EXEC_RECORD"          # Execution completion recorded
    DEPLOY_RECORD = "DEPLOY_RECORD"      # Target deployment recorded
    VERIFY_RECORD = "VERIFY_RECORD"      # Independent witness verification recorded
    ACCEPTANCE_RECORD = "ACCEPTANCE_RECORD" # Sovereign human acceptance recorded
    CLOSE_RECORD = "CLOSE_RECORD"        # Session closure and carry-forward recorded


class SovereignAttestation(BaseModel):
    """
    Station 990: Cryptographic or Deliberate Human Outcome Acceptance.
    Never inferred from ambient chat strings. Must bind exact subject hash.
    """
    model_config = ConfigDict(frozen=True)

    decision: Literal["ACCEPTED", "REJECTED", "DEFERRED"]
    subject_type: Literal["DEPLOYMENT", "ARTIFACT", "CONSTITUTIONAL_MUTATION", "SESSION_OUTCOME"]
    subject_id: str = Field(..., description="Identifier of the accepted object")
    subject_hash: str = Field(..., description="Exact SHA-256 hash of the subject outcome")
    outcome_witness_ref: str = Field(..., description="Reference to OutcomeWitness receipt")
    actor: str = Field(default="ARIF", description="Human principal")
    assurance_level: Literal["LOW_SESSION", "MEDIUM_BOUND", "HIGH_CRYPTOGRAPHIC"] = "MEDIUM_BOUND"
    signature: str | None = Field(default=None, description="Optional Ed25519 signature for high-consequence")
    recorded_at: str = Field(..., description="ISO-8601 acceptance timestamp")
    scope: str = Field(default="standard", description="Accepted scope boundary")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GOVERNED TRANSITION LIFECYCLE (ADR-015 Decision 2)
# ═══════════════════════════════════════════════════════════════════════════════

class AuthorizationVerdict(StrEnum):
    SEAL = "SEAL"
    HOLD = "HOLD"
    SABAR = "SABAR"
    VOID = "VOID"


class AuthorizationDimension(BaseModel):
    verdict: AuthorizationVerdict = AuthorizationVerdict.HOLD
    grant: ExecutionAuthorizationGrant | None = None
    judge: str = "arif_judge"
    evaluated_at: str | None = None


class LifecycleDimension(BaseModel):
    execution_state: RuntimeLifecycleState = RuntimeLifecycleState.NOT_STARTED
    deployment_state: Literal["NOT_STARTED", "DEPLOYED", "FAILED", "ROLLED_BACK"] = "NOT_STARTED"
    session_closed: bool = False


class WitnessDimension(BaseModel):
    receipt_id: str | None = None
    receipt_type: ReceiptType | None = None
    chain_hash: str | None = None
    outcome_observed: bool = False


class GovernedTransition(BaseModel):
    """
    THE GOVERNED TRANSITION CONTRACT (ADR-015).
    Maintains invariant: authorization != execution != deployment != outcome != acceptance.
    """
    transition_id: str
    authorization: AuthorizationDimension = Field(default_factory=AuthorizationDimension)
    lifecycle: LifecycleDimension = Field(default_factory=LifecycleDimension)
    witness: WitnessDimension = Field(default_factory=WitnessDimension)
    attestation: SovereignAttestation | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CONSUMER-SPECIFIC LEGACY PROJECTIONS (ADR-015 Section 3)
# ═══════════════════════════════════════════════════════════════════════════════

class LegacySealProjection:
    """
    Consumer-specific projections to prevent global boolean ambiguity.
    Every projection explicitly declares its target consumer and meaning.
    """

    @staticmethod
    def project_authorized(t: GovernedTransition) -> bool:
        """Target: Pre-execution gates checking if action is authorized by Judge."""
        return t.authorization.verdict == AuthorizationVerdict.SEAL

    @staticmethod
    def project_receipt_written(t: GovernedTransition) -> bool:
        """Target: Ledger checkers verifying a receipt was written to VAULT999."""
        return t.witness.receipt_id is not None

    @staticmethod
    def project_completed(t: GovernedTransition) -> bool:
        """Target: Actuator clients checking if execution command finished."""
        return t.lifecycle.execution_state == RuntimeLifecycleState.COMPLETED

    @staticmethod
    def project_deployed(t: GovernedTransition) -> bool:
        """Target: Observatories checking if code/config reached target runtime."""
        return t.lifecycle.deployment_state == "DEPLOYED"

    @staticmethod
    def project_ratified(t: GovernedTransition) -> bool:
        """Target: High-assurance auditors checking if Arif accepted the outcome."""
        return t.attestation is not None and t.attestation.decision == "ACCEPTED"

    @staticmethod
    def project_session_closed(t: GovernedTransition) -> bool:
        """Target: Session drivers checking if session carry-forward closed."""
        return t.lifecycle.session_closed is True


# ═══════════════════════════════════════════════════════════════════════════════
# 6. FORMULA-VERSION REGISTRY (ADR-015 Decision 4)
# ═══════════════════════════════════════════════════════════════════════════════

FORMULA_VERSION_REGISTRY = {
    "apex-g-v2-runtime": {
        "formula": "A * P * E * X * Phi",
        "status": "CURRENT_OBSERVED_IMPLEMENTATION",
        "source": "arifosmcp/geometry/eureka_zen.py:246",
        "epistemic_class": "heuristic_scoring",
        "description": "5-factor product runtime function.",
    },
    "apex-g-v3-proposed": {
        "formula": "(A * P * E * X) ** 0.25",
        "status": "CANONICAL_CANDIDATE",
        "source": "core/laws.py / ADR-015",
        "epistemic_class": "heuristic_aggregate",
        "description": "4-factor geometric mean candidate. Phi separated as scar gate.",
    },
}


def assert_jacobian_non_authority(role: str) -> None:
    """
    Enforces the Jacobian Invariant:
    Jacobian estimates sensitivity in J-Space; it cannot issue verdicts or grant authority.
    """
    if "verdict" in role.lower() or "authority" in role.lower() or "constitutional" in role.lower():
        raise PermissionError(
            f"JACOBIAN INVARIANT VIOLATION: Role '{role}' cannot claim constitutional authority or issue verdicts."
        )


__all__ = [
    "AssuranceLevel",
    "IdentityAssurance",
    "ConstitutionalRole",
    "ConstitutionalAuthority",
    "EpistemicActionTier",
    "FederationAuthorityBand",
    "SessionCapabilityLease",
    "ExecutionAuthorizationGrant",
    "HumanMandate",
    "RuntimeLifecycleState",
    "RuntimeLifecycle",
    "WitnessStatus",
    "AcceptanceStatus",
    "AuthorityEnvelope",
    "ReceiptType",
    "SovereignAttestation",
    "AuthorizationVerdict",
    "AuthorizationDimension",
    "LifecycleDimension",
    "WitnessDimension",
    "GovernedTransition",
    "LegacySealProjection",
    "FORMULA_VERSION_REGISTRY",
    "assert_jacobian_non_authority",
]
