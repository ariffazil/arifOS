"""
Vault Liveness Contract — AAA-GOV-VAULT-LIVENESS-v1
═════════════════════════════════════════════════════

Defines when VAULT999 audit state is fresh enough to trust.
Without this contract, the federation cannot distinguish between
"the vault is sealed" and "the vault was sealed 3 days ago and is stale."

Production hardening rule:
  - Fresh vault → execution authority is current
  - Stale vault → execution is HOLD until vault is re-verified
  - Broken chain → execution is VOID (evidence chain compromised)

DITEMPA BUKAN DIBERI — The bloodstream contract, now forged.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

# ═══════════════════════════════════════════════════════════════════════════════
# LIVENESS STATE
# ═══════════════════════════════════════════════════════════════════════════════


class VaultLivenessState(StrEnum):
    """Liveness verdict for the VAULT999 audit trail."""

    FRESH = "FRESH"          # Last seal within freshness window, chain intact
    STALE = "STALE"          # Last seal too old, but chain is intact
    DEGRADED = "DEGRADED"    # Chain has gaps within tolerance
    COMPROMISED = "COMPROMISED"  # Chain broken beyond tolerance
    UNKNOWN = "UNKNOWN"      # Cannot determine (e.g., vault unreachable)


class LivenessCheckResult(BaseModel):
    """Result of a single vault liveness check."""

    state: VaultLivenessState
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_seal_age_seconds: float = Field(default=float("inf"))
    chain_height: int = Field(default=0)
    chain_gaps: int = Field(default=0)
    merkle_verified: bool = Field(default=False)
    signature_verified: bool = Field(default=False)
    detail: str = Field(default="")


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT LIVENESS CONTRACT
# ═══════════════════════════════════════════════════════════════════════════════


class VaultLivenessContract(BaseModel):
    """
    Defines freshness thresholds for the VAULT999 audit trail.

    The vault is the bloodstream of the federation. Every consequential action
    writes to it. If the vault is stale, the federation has amnesia — it cannot
    attest to what was authorized, when, or by whom.

    Contract ID: AAA-GOV-VAULT-LIVENESS-v1
    Version: 1.0.0

    Thresholds:
      - max_seal_age_seconds: How long since the last seal before state is STALE.
          Default 300s (5 min) — aggressive for production. Relaxed to 3600s (1h)
          for development. Set to 0 to disable freshness checks.

      - max_chain_gap_tolerance: How many missing prev_seal_id links are tolerated
          before the chain is COMPROMISED. Default 0 (no gaps allowed). Set > 0
          only if you understand the implications.

      - min_chain_height: Minimum number of seals in the chain to consider it
          trustworthy. Default 1. A chain with 0 seals is UNKNOWN.

    Verification:
      - require_merkle_chain: Must verify the hash chain integrity.
      - require_signature: Must verify actor_signature on each seal.

    Authority: arifOS reads this contract before any MUTATE/ATOMIC action.
    If vault is not FRESH, MUTATE is downgraded to PREPARE, ATOMIC is HOLD.
    """

    # Identity
    contract_id: str = Field(
        default="AAA-GOV-VAULT-LIVENESS-v1",
        description="Canonical contract identifier",
    )
    version: str = Field(default="1.0.0", description="Contract version")

    # ── Freshness thresholds ─────────────────────────────────────────────

    max_seal_age_seconds: int = Field(
        default=300,
        ge=0,
        description="Maximum seconds since last seal before state is STALE. 0 = disabled.",
    )
    max_chain_gap_tolerance: int = Field(
        default=0,
        ge=0,
        description="How many missing prev_seal_id links tolerated before COMPROMISED.",
    )
    min_chain_height: int = Field(
        default=1,
        ge=0,
        description="Minimum chain length (seal count) to trust.",
    )

    # ── Verification flags ───────────────────────────────────────────────

    require_merkle_chain: bool = Field(
        default=True,
        description="Must verify merkle hash chain integrity.",
    )
    require_signature: bool = Field(
        default=True,
        description="Must verify actor_signature on each seal.",
    )
    liveness_check_interval_seconds: int = Field(
        default=60,
        ge=10,
        description="How often to probe vault health (seconds).",
    )

    # ── Computed: current liveness state ──────────────────────────────────

    _last_check: LivenessCheckResult | None = None

    # ── Judgment methods ──────────────────────────────────────────────────

    def check(
        self,
        last_seal_age_seconds: float,
        chain_height: int,
        chain_gaps: int = 0,
        merkle_verified: bool = False,
        signature_verified: bool = False,
    ) -> LivenessCheckResult:
        """
        Evaluate vault liveness against contract thresholds.

        Order of judgment (strictest wins):
          1. Chain height < min_chain_height → UNKNOWN
          2. Gaps > tolerance → COMPROMISED
          3. Verification failures → DEGRADED
          4. Age > threshold → STALE
          5. Everything passes → FRESH
        """
        # 1. Chain height
        if chain_height < self.min_chain_height:
            result = LivenessCheckResult(
                state=VaultLivenessState.UNKNOWN,
                last_seal_age_seconds=last_seal_age_seconds,
                chain_height=chain_height,
                chain_gaps=chain_gaps,
                merkle_verified=merkle_verified,
                signature_verified=signature_verified,
                detail=f"Chain height {chain_height} < minimum {self.min_chain_height}",
            )
            self._last_check = result
            return result

        # 2. Chain gaps
        if chain_gaps > self.max_chain_gap_tolerance:
            result = LivenessCheckResult(
                state=VaultLivenessState.COMPROMISED,
                last_seal_age_seconds=last_seal_age_seconds,
                chain_height=chain_height,
                chain_gaps=chain_gaps,
                merkle_verified=merkle_verified,
                signature_verified=signature_verified,
                detail=f"Chain gaps {chain_gaps} > tolerance {self.max_chain_gap_tolerance}",
            )
            self._last_check = result
            return result

        # 3. Verification failures (partial = DEGRADED, not COMPROMISED)
        verifications_failed: list[str] = []
        if self.require_merkle_chain and not merkle_verified:
            verifications_failed.append("merkle")
        if self.require_signature and not signature_verified:
            verifications_failed.append("signature")

        if verifications_failed:
            result = LivenessCheckResult(
                state=VaultLivenessState.DEGRADED,
                last_seal_age_seconds=last_seal_age_seconds,
                chain_height=chain_height,
                chain_gaps=chain_gaps,
                merkle_verified=merkle_verified,
                signature_verified=signature_verified,
                detail=f"Verification failed: {', '.join(verifications_failed)}",
            )
            self._last_check = result
            return result

        # 4. Freshness
        if self.max_seal_age_seconds > 0 and last_seal_age_seconds > self.max_seal_age_seconds:
            result = LivenessCheckResult(
                state=VaultLivenessState.STALE,
                last_seal_age_seconds=last_seal_age_seconds,
                chain_height=chain_height,
                chain_gaps=chain_gaps,
                merkle_verified=merkle_verified,
                signature_verified=signature_verified,
                detail=(
                    f"Last seal age {last_seal_age_seconds:.0f}s "
                    f"> threshold {self.max_seal_age_seconds}s"
                ),
            )
            self._last_check = result
            return result

        # 5. FRESH
        result = LivenessCheckResult(
            state=VaultLivenessState.FRESH,
            last_seal_age_seconds=last_seal_age_seconds,
            chain_height=chain_height,
            chain_gaps=chain_gaps,
            merkle_verified=merkle_verified,
            signature_verified=signature_verified,
            detail="Vault fresh: all thresholds passed",
        )
        self._last_check = result
        return result

    @model_validator(mode="after")
    def _validate_thresholds(self) -> VaultLivenessContract:
        """Contract semantics validation."""
        if self.min_chain_height < 0:
            raise ValueError("min_chain_height must be >= 0")
        if self.max_chain_gap_tolerance < 0:
            raise ValueError("max_chain_gap_tolerance must be >= 0")
        if self.max_seal_age_seconds < 0:
            raise ValueError("max_seal_age_seconds must be >= 0")
        if self.liveness_check_interval_seconds < 10:
            raise ValueError("liveness_check_interval_seconds must be >= 10")
        return self

    def allows_execution(self, action_class: str) -> tuple[bool, str]:
        """
        Determine if vault liveness permits an action class.

        MUTATE/ATOMIC require FRESH vault.
        PREPARE/OBSERVE can proceed with STALE or DEGRADED (but warn).
        COMPROMISED blocks everything.
        UNKNOWN blocks MUTATE/ATOMIC.
        """
        if self._last_check is None:
            return False, "Vault LivenessCheck has not been performed yet"

        state = self._last_check.state

        if state == VaultLivenessState.COMPROMISED:
            return False, "VOID: Vault chain is COMPROMISED — no execution permitted"

        if action_class in ("MUTATE", "ATOMIC"):
            if state == VaultLivenessState.FRESH:
                return True, "SEAL"
            if state == VaultLivenessState.UNKNOWN:
                return False, "HOLD: Vault state UNKNOWN — cannot authorize MUTATE/ATOMIC"
            if state == VaultLivenessState.STALE:
                return False, f"HOLD: Vault STALE ({self._last_check.detail})"
            if state == VaultLivenessState.DEGRADED:
                return False, f"HOLD: Vault DEGRADED ({self._last_check.detail})"

        # PREPARE / OBSERVE — allow with warning
        if state in (VaultLivenessState.STALE, VaultLivenessState.DEGRADED):
            return True, f"WARN: Vault {state.value} — {self._last_check.detail}"
        if state == VaultLivenessState.UNKNOWN:
            return True, "WARN: Vault state UNKNOWN — proceed with caution"

        return True, "SEAL"

    def last_check_summary(self) -> dict[str, Any]:
        """Return last check result as a dict for logging."""
        if self._last_check is None:
            return {"state": "UNCHECKED", "detail": "No liveness check performed yet"}
        return {
            "state": self._last_check.state.value,
            "checked_at": self._last_check.checked_at.isoformat(),
            "last_seal_age_seconds": self._last_check.last_seal_age_seconds,
            "chain_height": self._last_check.chain_height,
            "chain_gaps": self._last_check.chain_gaps,
            "merkle_verified": self._last_check.merkle_verified,
            "signature_verified": self._last_check.signature_verified,
            "detail": self._last_check.detail,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTION CONTRACT SUITE
# ═══════════════════════════════════════════════════════════════════════════════


class ContractStatus(StrEnum):
    """Status of a production contract."""

    SEALED = "SEALED"       # Contract is signed, tested, and enforced
    PARTIAL = "PARTIAL"     # Contract exists but has gaps (tests missing, etc.)
    DRAFT = "DRAFT"         # Contract spec exists but no enforcement yet
    ABSENT = "ABSENT"       # Contract does not exist yet


class ContractEntry(BaseModel):
    """A single production contract in the manifest."""

    contract_id: str = Field(description="Canonical contract identifier")
    status: ContractStatus = Field(default=ContractStatus.DRAFT)
    description: str = Field(default="")
    schema_file: str | None = Field(default=None, description="Pydantic schema location")
    test_file: str | None = Field(default=None, description="Test file location")
    enforcement_path: str | None = Field(default=None, description="Runtime enforcement location")
    gaps: list[str] = Field(
        default_factory=list,
        description="Known gaps preventing SEALED status",
    )


class ProductionContractManifest(BaseModel):
    """
    The manifest of all production contracts in the arifOS federation.

    This is the single source of truth for what is sealed vs partial vs absent.
    It answers: "Can this federation be trusted in production?"

    Contract statuses as of forge date (2026-06-09):
      - FederationEnvelope v2       → PARTIAL (exists, tested, signing gap)
      - EvidenceEnvelope v1         → PARTIAL (exists, used, needs cross-organ tests)
      - BudgetContract              → PARTIAL (exists, enforced, needs budget schema)
      - VaultLivenessContract       → DRAFT   (forged now, needs tests + enforcement)
      - DriftDetection              → PARTIAL (exists, tested, needs auto-HOLD)
      - RiskPassport                → PARTIAL (exists, tested, ceiling calibration needed)
      - IntentEnvelope V1           → PARTIAL (exists, needs end-to-end)
      - Identity/Authority Proof    → DRAFT   (schema gap, identity = "claimed" not crypto)
      - Independent Attestation     → ABSENT  (no attestation runtime yet)
      - Regression Test Matrix      → PARTIAL (some tests exist, not comprehensive)
    """

    manifest_id: str = Field(default="AAA-GOV-PRODUCTION-CONTRACTS-v1")
    forge_date: str = Field(default="2026-06-09")
    auditors: list[str] = Field(default_factory=lambda: ["omega-forge-agent"])

    contracts: list[ContractEntry] = Field(
        default_factory=lambda: [
            ContractEntry(
                contract_id="AAA-GOV-FEDERATION-ENVELOPE-v2",
                status=ContractStatus.PARTIAL,
                description="Signed, authority-bearing envelope for all cross-organ messages",
                schema_file="arifosmcp/schemas/federation_envelope.py",
                test_file="tests/foundation/test_federation_envelope.py",
                enforcement_path="arifosmcp/runtime/law.py",
                gaps=["actor_signature crypto verification not enforced at envelope level"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-EVIDENCE-ENVELOPE-v1",
                status=ContractStatus.PARTIAL,
                description="Cross-organ evidence envelope with epistemic ladder",
                schema_file="arifosmcp/schemas/envelope.py",
                test_file="tests/core/test_envelope.py",
                gaps=["cross-organ tests not yet comprehensive"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-BUDGET-v1",
                status=ContractStatus.PARTIAL,
                description="Session budget: turns, tools, context, retries, no-progress",
                schema_file="arifosmcp/runtime/budget.py",
                test_file="tests/test_budget_contract.py",
                enforcement_path="arifosmcp/runtime/floor.py",
                gaps=["budget limits are defaults, not per-tool risk-calibrated"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-VAULT-LIVENESS-v1",
                status=ContractStatus.DRAFT,
                description="Vault freshness contract — when audit state is trustworthy",
                schema_file="arifosmcp/schemas/vault_liveness.py",
                test_file=None,  # to be written
                gaps=["tests not yet written", "enforcement in law.py not yet wired"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-DRIFT-DETECTION-v1",
                status=ContractStatus.PARTIAL,
                description="Tool surface drift detection — declared vs actual",
                schema_file="arifosmcp/tools/drift_check.py",
                test_file="tests/test_mcp_drift_check.py",
                gaps=["drift does not auto-trigger HOLD on envelopes"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-RISK-PASSPORT-v1",
                status=ContractStatus.PARTIAL,
                description="Risk classification for every tool call",
                schema_file="arifosmcp/schemas/federation_envelope.py",
                test_file="tests/foundation/test_risk_classifier.py",
                gaps=["risk_ceiling not calibrated per-organ"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-INTENT-ENVELOPE-v1",
                status=ContractStatus.PARTIAL,
                description="Atomic authorization object for sovereign approval",
                schema_file="arifosmcp/schemas/intent_envelope.py",
                test_file="tests/constitutional/test_intent_envelope.py",
                gaps=["end-to-end flow not tested"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-IDENTITY-PROOF-v1",
                status=ContractStatus.DRAFT,
                description="Cryptographic identity proof replacing 'claimed' actor",
                schema_file=None,
                gaps=["signature verification schema not yet built"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-ATTESTATION-v1",
                status=ContractStatus.ABSENT,
                description="Runtime attestation proving gates are active",
                gaps=["no attestation runtime exists"],
            ),
            ContractEntry(
                contract_id="AAA-GOV-REGRESSION-MATRIX-v1",
                status=ContractStatus.PARTIAL,
                description="Comprehensive regression tests across all 13 tools",
                test_file="tests/ (distributed)",
                gaps=["not all tools tested under degraded/hostile states"],
            ),
        ]
    )

    def sealed_count(self) -> int:
        return sum(1 for c in self.contracts if c.status == ContractStatus.SEALED)

    def partial_count(self) -> int:
        return sum(1 for c in self.contracts if c.status == ContractStatus.PARTIAL)

    def draft_count(self) -> int:
        return sum(1 for c in self.contracts if c.status == ContractStatus.DRAFT)

    def absent_count(self) -> int:
        return sum(1 for c in self.contracts if c.status == ContractStatus.ABSENT)

    def summary(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "forge_date": self.forge_date,
            "total_contracts": len(self.contracts),
            "sealed": self.sealed_count(),
            "partial": self.partial_count(),
            "draft": self.draft_count(),
            "absent": self.absent_count(),
            "readiness": (
                "PRODUCTION_READY"
                if self.absent_count() == 0 and self.sealed_count() >= 8
                else "HARDENING"
                if self.absent_count() == 0
                else "PARTIAL"
            ),
        }
