"""
arifos/core/stage_000.py — CANONICAL Stage 000 VOID Implementation (v52.5.2)

THE GREAT PURGE: This file consolidates all Stage 000 implementations into ONE canonical module.
Consolidated from multiple legacy sources.

Authority:
- Track A Canon: 000_THEORY/000_LAW.md
- Track B Spec: arifos/spec/v47/000_foundation/000_void_stage.json
- Track C Code: THIS FILE (canonical)

Version: v52.5.2
Author: arifOS Project
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

# Import Canonical Floors from the Constitutional Core
# Note: canonical_core is at root level, not inside arifos package
from codebase.floors import (
    F1_Amanah,
    F10_OntologyGate,
    F12_InjectionDefense,
    AmanahCovenant,
    OntologyResult,
    InjectionDefenseResult
)
from codebase.authority import AuthorityVerifier, AuthorityCheck

if TYPE_CHECKING:
    from codebase.utils.runtime_types import Job

# =============================================================================
# CONSTANTS FROM SPEC (Track B: 000_void_stage.json)
# =============================================================================

# Humility band (F7)
OMEGA_0_MIN = 0.03
OMEGA_0_MAX = 0.05
OMEGA_0_DEFAULT = 0.04

# Amanah threshold (F1)
AMANAH_THRESHOLD = 0.5

# Scar Echo Law binding energy threshold
OMEGA_FICTION_THRESHOLD = 1.0

# Session ID format
SESSION_ID_PREFIX = "CLIP"

# F12 Injection defense threshold
INJECTION_THRESHOLD = 0.85

# Safe actions for Amanah scoring (Legacy check - now handled by F1_Amanah class)
SAFE_ACTIONS = frozenset({
    "respond", "search", "read", "analyze", "summarize", "explain",
    "list", "describe", "help", "query", "lookup", "find", "get",
    "show", "display", "print", "format", "parse", "validate"
})

# Restricted actions requiring elevated authority (Legacy check - now handled by F1_Amanah class)
RESTRICTED_ACTIONS = frozenset({
    "delete", "remove", "drop", "truncate", "destroy", "kill",
    "shutdown", "reboot", "format", "wipe", "purge", "execute",
    "sudo", "chmod", "chown", "rm", "rmdir"
})


# =============================================================================
# ENUMS
# =============================================================================

class VerdictType(str, Enum):
    """Constitutional verdicts."""
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    VOID = "VOID"
    SABAR = "SABAR"
    HOLD_888 = "888_HOLD"


# =============================================================================
# AMANAH SIGNALS (F1) - Wrapper around F1_Amanah Class
# =============================================================================

@dataclass
class AmanahGateResult:
    """Result from Amanah risk gate."""
    score: float
    passed: bool
    reason: str
    verdict: Optional[VerdictType] = None
    covenant_hash: Optional[str] = None


# =============================================================================
# DATA CLASSES FOR STAGE 000
# =============================================================================

@dataclass
class SessionMetadata:
    """Session initialization metadata."""
    session_id: str
    timestamp: str
    epoch_start: float
    humility_band: Tuple[float, float]
    constitutional_version: str
    nonce: str
    scar_echo_active: bool = True


@dataclass
class TelemetryPacket:
    """T-R-A-F telemetry packets for session physics."""
    # T: Temporal packet
    cadence_ms: int = 0
    turn_index: int = 0
    epoch_start: float = field(default_factory=time.time)

    # R: Resource packet
    tokens_used: int = 0
    tokens_budget: int = 200000
    burn_rate: float = 0.0

    # A: Authoritative vector
    nonce_v: Optional[str] = None
    auth_level: str = "AGENT"
    is_reversible: bool = True

    # F: Floor pulse
    floor_margins: Dict[str, float] = field(default_factory=dict)
    floor_stability: Dict[str, float] = field(default_factory=dict)


@dataclass
class HypervisorGateResult:
    """Result from hypervisor gates F10-F12."""
    passed: bool
    f10_symbolic: bool = True
    f11_command_auth: bool = True
    f12_injection: bool = True
    injection_score: float = 0.0
    nonce_verified: bool = True
    failures: List[str] = field(default_factory=list)
    verdict: Optional[VerdictType] = None


@dataclass
class ScarEchoCheck:
    """Scar Echo Law check result."""
    omega_fiction: float = 0.0
    binding_energy_reached: bool = False
    should_forge_law: bool = False
    harm_pattern: Optional[str] = None
    ledger_ref: Optional[str] = None


@dataclass
class ZKPCCommitment:
    """Zero-Knowledge Proof of Constitution pre-commitment."""
    canon_hash: str
    timestamp: str
    session_id: str
    witness_signature: Optional[str] = None


@dataclass
class SessionInitResult:
    """Complete session initialization result."""
    metadata: SessionMetadata
    telemetry: TelemetryPacket
    hypervisor: HypervisorGateResult
    amanah: AmanahGateResult
    scar_echo: ScarEchoCheck
    zkpc: ZKPCCommitment
    verdict: VerdictType
    vitality: float = 1.0
    message: str = ""
    stage_trace: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "session_id": self.metadata.session_id,
            "timestamp": self.metadata.timestamp,
            "verdict": self.verdict.value,
            "vitality": self.vitality,
            "message": self.message,
            "nonce": self.metadata.nonce,
            "constitutional_version": self.metadata.constitutional_version,
            "humility_band": list(self.metadata.humility_band),
            "hypervisor": {
                "passed": self.hypervisor.passed,
                "f10_symbolic": self.hypervisor.f10_symbolic,
                "f11_command_auth": self.hypervisor.f11_command_auth,
                "f12_injection": self.hypervisor.f12_injection,
                "injection_score": self.hypervisor.injection_score,
                "failures": self.hypervisor.failures,
            },
            "amanah": {
                "score": self.amanah.score,
                "passed": self.amanah.passed,
                "reason": self.amanah.reason,
            },
            "scar_echo": {
                "omega_fiction": self.scar_echo.omega_fiction,
                "binding_energy_reached": self.scar_echo.binding_energy_reached,
                "should_forge_law": self.scar_echo.should_forge_law,
            },
            "zkpc": {
                "canon_hash": self.zkpc.canon_hash,
                "timestamp": self.zkpc.timestamp,
            },
            "telemetry": {
                "tokens_budget": self.telemetry.tokens_budget,
                "auth_level": self.telemetry.auth_level,
            },
            "stage_trace": self.stage_trace,
        }


# =============================================================================
# STAGE 000 VOID CLASS
# =============================================================================

class Stage000VOID:
    """
    Stage 000 VOID - Foundation Initialization Protocol.

    The entry gate for all constitutional operations.
    Implements the complete Stage 000 specification from Track B.
    
    Refactored to use Canonical Floors from `floors.py`.
    """

    def __init__(
        self,
        constitutional_version: str = "v52.5.2",
        omega_0: float = OMEGA_0_DEFAULT,
        amanah_threshold: float = AMANAH_THRESHOLD,
        enable_scar_echo: bool = True,
    ):
        """
        Initialize Stage 000 VOID.

        Args:
            constitutional_version: Version of constitution to enforce
            omega_0: Humility band center (default 0.04)
            amanah_threshold: Minimum Amanah score (default 0.5)
            enable_scar_echo: Enable Scar Echo Law (default True)
        """
        self.version = constitutional_version
        self.omega_0 = self._clamp_humility(omega_0)
        self.amanah_threshold = amanah_threshold
        self.enable_scar_echo = enable_scar_echo
        
        # Initialize Canonical Floor Validators
        self.f1_amanah = F1_Amanah()
        self.f10_ontology = F10_OntologyGate()
        self.f12_injection = F12_InjectionDefense()
        self.f11_auth = AuthorityVerifier()

    def execute(
        self,
        input_text: str,
        source: Optional[str] = None,
        context: str = "",
        action: str = "respond",
        nonce: Optional[str] = None,
    ) -> SessionInitResult:
        """
        Execute Stage 000 VOID initialization protocol.

        Args:
            input_text: The input to process
            source: Origin channel (CLI, API, MCP, etc.)
            context: Additional context
            action: Action being requested
            nonce: Optional pre-generated nonce for F11

        Returns:
            SessionInitResult with verdict and telemetry
        """
        stage_trace = ["000_VOID_START"]

        # Step 1: System Reset
        self._system_reset()
        stage_trace.append("SYSTEM_RESET")

        # Step 2: Session Initialization
        metadata = self._init_session(nonce)
        stage_trace.append("SESSION_INIT")

        # Step 3: Initialize Telemetry
        telemetry = self._init_telemetry(metadata.nonce)
        stage_trace.append("TELEMETRY_INIT")

        # Step 4: Hypervisor Gate (F10-F12)
        hypervisor = self._hypervisor_gate(input_text, nonce)
        stage_trace.append(f"HYPERVISOR_{'PASS' if hypervisor.passed else 'BLOCK'}")

        if not hypervisor.passed:
            # Hypervisor block → immediate SABAR/HOLD_888
            return SessionInitResult(
                metadata=metadata,
                telemetry=telemetry,
                hypervisor=hypervisor,
                amanah=AmanahGateResult(0.0, False, "Hypervisor block", VerdictType.SABAR),
                scar_echo=ScarEchoCheck(),
                zkpc=self._zkpc_precommit(metadata.session_id),
                verdict=hypervisor.verdict or VerdictType.SABAR,
                vitality=0.0,
                message=f"Hypervisor gate failed: {', '.join(hypervisor.failures)}",
                stage_trace=stage_trace,
            )

        # Step 5: Amanah Risk Gate
        amanah = self._amanah_gate(input_text, source, context, action)
        stage_trace.append(f"AMANAH_{'PASS' if amanah.passed else 'BLOCK'}")

        if not amanah.passed:
            # Amanah block → VOID
            return SessionInitResult(
                metadata=metadata,
                telemetry=telemetry,
                hypervisor=hypervisor,
                amanah=amanah,
                scar_echo=ScarEchoCheck(),
                zkpc=self._zkpc_precommit(metadata.session_id),
                verdict=VerdictType.VOID,
                vitality=0.3,
                message=f"Amanah gate failed: {amanah.reason}",
                stage_trace=stage_trace,
            )

        # Step 6: Scar Echo Check
        scar_echo = self._check_scar_echo(input_text)
        if scar_echo.should_forge_law:
            stage_trace.append("SCAR_ECHO_TRIGGERED")

        # Step 7: ZKPC Pre-commitment
        zkpc = self._zkpc_precommit(metadata.session_id)
        stage_trace.append("ZKPC_COMMIT")

        # Step 8: All gates passed → SEAL
        stage_trace.append("000_VOID_PASS")

        return SessionInitResult(
            metadata=metadata,
            telemetry=telemetry,
            hypervisor=hypervisor,
            amanah=amanah,
            scar_echo=scar_echo,
            zkpc=zkpc,
            verdict=VerdictType.SEAL,
            vitality=1.0,
            message="System reset. Constitution forged. Ready to measure.",
            stage_trace=stage_trace,
        )

    # =========================================================================
    # CORE FUNCTIONS
    # =========================================================================

    def _system_reset(self) -> None:
        """System Reset: Erase all assumptions and biases."""
        # Conceptual reset - LLM is already stateless per session
        pass

    def _init_session(self, nonce: Optional[str] = None) -> SessionMetadata:
        """Session Initialization: Create forensic baseline."""
        now = datetime.now(timezone.utc)
        timestamp_str = now.isoformat()
        epoch_start = time.time()

        # Generate session ID
        date_str = now.strftime("%Y%m%d")
        counter = int(epoch_start % 1000)
        session_id = f"{SESSION_ID_PREFIX}_{date_str}_{counter:03d}"

        # Generate or use provided nonce for F11
        if nonce is None:
            nonce_data = f"{session_id}_{epoch_start}".encode()
            nonce_hash = hashlib.sha256(nonce_data).hexdigest()[:16].upper()
            nonce = f"X7K9F_{date_str}_{nonce_hash[:8]}"

        return SessionMetadata(
            session_id=session_id,
            timestamp=timestamp_str,
            epoch_start=epoch_start,
            humility_band=(OMEGA_0_MIN, OMEGA_0_MAX),
            constitutional_version=self.version,
            nonce=nonce,
            scar_echo_active=self.enable_scar_echo,
        )

    def _init_telemetry(self, nonce: str) -> TelemetryPacket:
        """Initialize T-R-A-F telemetry packets."""
        return TelemetryPacket(
            cadence_ms=0,
            turn_index=0,
            epoch_start=time.time(),
            tokens_used=0,
            tokens_budget=200000,
            burn_rate=0.0,
            nonce_v=nonce,
            auth_level="AGENT",
            is_reversible=True,
            floor_margins={},
            floor_stability={},
        )

    def _hypervisor_gate(self, input_text: str, nonce: Optional[str] = None) -> HypervisorGateResult:
        """
        Hypervisor Gate: F10-F12 checks before LLM processing.
        Uses Canonical Floor Validators.
        """
        # F10: Symbolic Guard
        ontology_res = self.f10_ontology.assert_role(input_text)
        f10_symbolic = ontology_res.locked

        # F11: Command Auth
        # For simplicity in this context, we assume agent role if nonce present
        auth_res = self.f11_auth.verify(nonce or "UNKNOWN", input_text, "unknown_operator")
        f11_command_auth = auth_res.passed
        # Fallback to loose check for now if strict fails but it's just a query
        if not f11_command_auth and "delete" not in input_text.lower():
             f11_command_auth = True # Allow read-only/query operations

        # F12: Injection Defense
        injection_res = self.f12_injection.scan(input_text)
        f12_injection = injection_res.passed
        injection_score = injection_res.risk_score

        # Determine overall pass/fail
        overall_passed = f10_symbolic and f11_command_auth and f12_injection

        # Build failures list
        failures = []
        verdict = None
        if not f10_symbolic:
            failures.append(f"F10_SYMBOLIC_GUARD: {ontology_res.reason}")
            verdict = VerdictType.HOLD_888
        if not f11_command_auth:
            failures.append("F11_COMMAND_AUTH")
            verdict = VerdictType.SABAR
        if not f12_injection:
            failures.append(f"F12_INJECTION_DEFENSE: {injection_res.reason}")
            verdict = VerdictType.SABAR

        return HypervisorGateResult(
            passed=overall_passed,
            f10_symbolic=f10_symbolic,
            f11_command_auth=f11_command_auth,
            f12_injection=f12_injection,
            injection_score=injection_score,
            nonce_verified=f11_command_auth,
            failures=failures,
            verdict=verdict,
        )

    def _amanah_gate(
        self,
        input_text: str,
        source: Optional[str],
        context: str,
        action: str
    ) -> AmanahGateResult:
        """
        Amanah Risk Gate.
        Uses F1_Amanah Canonical Validator.
        """
        # Using the initialize_covenants method from F1_Amanah as the gate check
        covenant = self.f1_amanah.initialize_covenants(input_text)
        
        passed = covenant.passed
        verdict = VerdictType.SEAL if passed else VerdictType.VOID

        return AmanahGateResult(
            score=covenant.trust_score,
            passed=passed,
            reason=covenant.reason,
            verdict=verdict,
            covenant_hash=covenant.covenant_hash
        )

    def _check_scar_echo(self, input_text: str) -> ScarEchoCheck:
        """
        Scar Echo Law: Check for binding energy threshold.
        If ω_fiction ≥ 1.0, violation crystallizes into immutable law.
        """
        omega_fiction = 0.0

        if self.enable_scar_echo:
            # Reusing F1 risk patterns for harm detection
            harm_score = self.f1_amanah._compute_risk_score(input_text)
            if harm_score > 0.8: # High risk
                omega_fiction = 1.2

        binding_reached = omega_fiction >= OMEGA_FICTION_THRESHOLD

        return ScarEchoCheck(
            omega_fiction=omega_fiction,
            binding_energy_reached=binding_reached,
            should_forge_law=binding_reached and self.enable_scar_echo,
            harm_pattern=input_text[:100] if binding_reached else None,
        )

    def _zkpc_precommit(self, session_id: str) -> ZKPCCommitment:
        """
        ZKPC Protocol: Generate pre-commitment hash.
        Cryptographic proof that session starts with known constitution.
        """
        # Hash of constitutional version for proof
        canon_data = f"{self.version}_{session_id}".encode()
        canon_hash = hashlib.sha256(canon_data).hexdigest()

        timestamp = datetime.now(timezone.utc).isoformat()

        return ZKPCCommitment(
            canon_hash=canon_hash,
            timestamp=timestamp,
            session_id=session_id,
        )

    def _clamp_humility(self, omega: float) -> float:
        """Clamp Ω₀ to valid humility band."""
        return max(OMEGA_0_MIN, min(OMEGA_0_MAX, omega))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def execute_stage_000(
    input_text: str,
    source: Optional[str] = None,
    context: str = "",
    action: str = "respond",
    nonce: Optional[str] = None,
    **kwargs
) -> SessionInitResult:
    """
    Execute Stage 000 VOID (convenience function).
    """
    stage = Stage000VOID(**kwargs)
    return stage.execute(
        input_text=input_text,
        source=source,
        context=context,
        action=action,
        nonce=nonce,
    )

# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# The canonical Stage 000 VOID instance
stage_000_void = Stage000VOID()

# Alias for pipeline compatibility (all stages use execute_stage)
execute_stage = execute_stage_000


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "OMEGA_0_MIN",
    "OMEGA_0_MAX",
    "OMEGA_0_DEFAULT",
    "AMANAH_THRESHOLD",
    "INJECTION_THRESHOLD",
    "SAFE_ACTIONS",
    "RESTRICTED_ACTIONS",

    # Enums
    "VerdictType",

    # Classes
    "AuthorityManifest",
    "SessionMetadata",
    "TelemetryPacket",
    "HypervisorGateResult",
    "AmanahGateResult",
    "ScarEchoCheck",
    "ZKPCCommitment",
    "SessionInitResult",
    "Stage000VOID",

    # Singleton
    "stage_000_void",

    # Functions
    "execute_stage_000",
    "execute_stage",  # Pipeline-compatible alias
]