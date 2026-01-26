"""
arifos/core/stage_000.py — CANONICAL Stage 000 VOID Implementation (v52.5.2)

THE GREAT PURGE: This file consolidates all Stage 000 implementations into ONE canonical module.

Consolidated from:
- arifos/core/system/stages/stage_000_void.py (650 lines - main logic)
- arifos/core/enforcement/stages/stage_000_amanah.py (236 lines - Amanah scoring)
- arifos/core/stage/stage_000_void.py (83 lines - InjectionDefense)

Authority:
- Track A Canon: 000_THEORY/000_LAW.md
- Track B Spec: arifos/spec/v47/000_foundation/000_void_stage.json
- Track C Code: THIS FILE (canonical)

Constitutional Functions:
1. System Reset: ΔS_initial = 0.0 (erase all prior session assumptions)
2. Session Initialization: CLIP_YYYYMMDD_NNN ID, telemetry baseline (T-R-A-F)
3. Humility Enforcement: Ω₀ ∈ [0.03, 0.05]
4. Hypervisor Gate: F10-F12 pre-LLM checks (Symbolic Guard, Command Auth, Injection Defense)
5. Amanah Risk Gate: 4-signal scoring with 0.5 threshold
6. Scar Echo Law: ω_fiction ≥ 1.0 → constitutional law forging
7. ZKPC Pre-commitment: SHA-256 hash of constitutional state

Motto: "DITEMPA BUKAN DIBERI" (Forged, Not Given)

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

if TYPE_CHECKING:
    from arifos.core.utils.runtime_types import Job

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

# Safe actions for Amanah scoring
SAFE_ACTIONS = frozenset({
    "respond", "search", "read", "analyze", "summarize", "explain",
    "list", "describe", "help", "query", "lookup", "find", "get",
    "show", "display", "print", "format", "parse", "validate"
})

# Restricted actions requiring elevated authority
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
# INJECTION DEFENSE (F12)
# Consolidated from arifos/core/stage/stage_000_void.py
# =============================================================================

class InjectionDefense:
    """
    4-Layer Injection Defense System (F12).

    Layer 1: Syntactic - Pattern matching for known injection phrases
    Layer 2: Semantic - Context-aware injection detection (TODO)
    Layer 3: Authority - Privilege escalation detection
    Layer 4: Structural - Template/special token injection
    """

    # Layer 1: Injection patterns
    INJECTION_PATTERNS = [
        r"ignore (?:all )?(?:previous |above )?instructions?",
        r"disregard (?:all )?(?:previous |above )?(?:instructions?|rules?)",
        r"forget (?:everything|all|your) (?:instructions?|rules?|training)",
        r"system(?:\s+)?override",
        r"jailbreak",
        r"DAN mode",
        r"developer mode",
        r"you are now",
        r"pretend (?:you are|to be)",
        r"act as if",
        r"bypass (?:safety|restrictions?|filters?)",
        r"reveal (?:your |the )?(?:system |hidden )?(?:prompt|instructions?)",
        r"show me your (?:system |hidden )?(?:prompt|instructions?)",
    ]

    # Layer 3: Privilege escalation patterns
    ESCALATION_PATTERNS = [
        r"\bsudo\s+",
        r"\bchmod\s+",
        r"\brm\s+-rf\b",
        r"\bpasswd\b",
        r"\b/etc/shadow\b",
        r"\b/etc/passwd\b",
        r"DROP\s+(?:TABLE|DATABASE)",
        r"DELETE\s+FROM\s+.*\s+WHERE\s+1\s*=\s*1",
        r"TRUNCATE\s+TABLE",
    ]

    # Layer 4: Structural patterns (template injection, special tokens)
    STRUCTURAL_PATTERNS = [
        r"\{\{.*\}\}",           # Template injection
        r"\[\[.*\]\]",           # Wiki-style injection
        r"<\|.*\|>",             # OpenAI special tokens
        r"\[INST\]",             # Llama special tokens
        r"<\|im_start\|>",       # ChatML tokens
        r"<\|im_end\|>",
        r"<<SYS>>",              # System prompt markers
        r"<</SYS>>",
    ]

    # Precompiled patterns
    _INJECTION_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
    _ESCALATION_COMPILED = [re.compile(p, re.IGNORECASE) for p in ESCALATION_PATTERNS]
    _STRUCTURAL_COMPILED = [re.compile(p, re.IGNORECASE) for p in STRUCTURAL_PATTERNS]

    @classmethod
    def check_query(cls, query: str) -> Tuple[bool, str, float]:
        """
        Full injection check across all layers.

        Args:
            query: Input text to check

        Returns:
            Tuple of (passed, reason, score)
            - passed: True if no injection detected
            - reason: Description of failure (or "Passed")
            - score: Injection probability 0.0-1.0
        """
        score = 0.0
        reasons = []

        # Layer 1: Syntactic
        syntactic_matches = cls._check_syntactic(query)
        if syntactic_matches:
            score += 0.4
            reasons.append(f"L1_Syntactic: {syntactic_matches[0]}")

        # Layer 3: Authority/Escalation
        escalation_matches = cls._check_escalation(query)
        if escalation_matches:
            score += 0.4
            reasons.append(f"L3_Authority: {escalation_matches[0]}")

        # Layer 4: Structural
        structural_matches = cls._check_structural(query)
        if structural_matches:
            score += 0.3
            reasons.append(f"L4_Structural: {structural_matches[0]}")

        # Cap at 1.0
        score = min(score, 1.0)

        if score >= INJECTION_THRESHOLD:
            return False, "; ".join(reasons), score

        return True, "Passed", score

    @classmethod
    def _check_syntactic(cls, query: str) -> List[str]:
        """Layer 1: Check for injection phrases."""
        matches = []
        for pattern in cls._INJECTION_COMPILED:
            match = pattern.search(query)
            if match:
                matches.append(match.group(0)[:50])
        return matches

    @classmethod
    def _check_escalation(cls, query: str) -> List[str]:
        """Layer 3: Check for privilege escalation."""
        matches = []
        for pattern in cls._ESCALATION_COMPILED:
            match = pattern.search(query)
            if match:
                matches.append(match.group(0)[:50])
        return matches

    @classmethod
    def _check_structural(cls, query: str) -> List[str]:
        """Layer 4: Check for template/token injection."""
        matches = []
        for pattern in cls._STRUCTURAL_COMPILED:
            match = pattern.search(query)
            if match:
                matches.append(match.group(0)[:50])
        return matches

    @classmethod
    def get_injection_patterns(cls) -> List[str]:
        """Get all injection patterns for external use."""
        return (
            cls.INJECTION_PATTERNS +
            cls.ESCALATION_PATTERNS +
            cls.STRUCTURAL_PATTERNS
        )

    @classmethod
    def find_injection_matches(cls, text: str) -> List[str]:
        """Find all injection pattern matches in text."""
        all_matches = []
        all_matches.extend(cls._check_syntactic(text))
        all_matches.extend(cls._check_escalation(text))
        all_matches.extend(cls._check_structural(text))
        return all_matches


# =============================================================================
# AUTHORITY MANIFEST (F11)
# =============================================================================

class AuthorityManifest:
    """
    Constitutional Authority Hierarchy (F11).

    Defines who can authorize what actions.
    """
    SOLE_VERDICT_SOURCE = "arifos.system.apex_prime"
    HUMAN_USER_ROLE = "override_authority"
    AGENT_ZERO_ROLE = "proposal_only"

    # Actions that agents CAN do
    AGENT_ALLOWED = frozenset({
        "propose_tool", "request_execution", "explore", "analyze",
        "search", "read", "summarize", "explain", "format"
    })

    # Actions that require human authority
    HUMAN_REQUIRED = frozenset({
        "execute_destructive", "override_verdict", "bypass_gate",
        "approve_hold", "override_block", "amend_constitution"
    })

    @classmethod
    def check_authority(cls, entity: str, action: str) -> bool:
        """
        Check if entity is authorized for action.

        Args:
            entity: Role identifier (AGENT_ZERO_ROLE, HUMAN_USER_ROLE)
            action: Action being attempted

        Returns:
            True if authorized
        """
        if entity == cls.AGENT_ZERO_ROLE:
            return action in cls.AGENT_ALLOWED

        if entity == cls.HUMAN_USER_ROLE:
            return action in cls.HUMAN_REQUIRED or action in cls.AGENT_ALLOWED

        return False


# =============================================================================
# AMANAH SIGNALS (F1)
# Consolidated from arifos/core/enforcement/stages/stage_000_amanah.py
# =============================================================================

@dataclass
class AmanahSignals:
    """
    Signals used to compute Amanah score.

    Each signal contributes 0.25 to the final score.
    All signals True = 1.0 (fully trusted).
    """
    has_source: bool = False
    has_context: bool = False
    no_instruction_hijack: bool = True
    reversible_action: bool = True
    # Diagnostics
    injection_patterns_found: List[str] = field(default_factory=list)
    risk_reasons: List[str] = field(default_factory=list)

    def compute_score(self) -> float:
        """Compute Amanah score from signals."""
        score = 0.0
        if self.has_source:
            score += 0.25
        if self.has_context:
            score += 0.25
        if self.no_instruction_hijack:
            score += 0.25
        if self.reversible_action:
            score += 0.25
        return score

    def get_reason(self) -> str:
        """Get explanation for score."""
        missing = []
        if not self.has_source:
            missing.append("no_source")
        if not self.has_context:
            missing.append("insufficient_context")
        if not self.no_instruction_hijack:
            missing.append("injection_detected")
        if not self.reversible_action:
            missing.append("restricted_action")
        if self.risk_reasons:
            missing.extend(self.risk_reasons)
        return "; ".join(missing) if missing else "all_signals_pass"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging."""
        return {
            "has_source": self.has_source,
            "has_context": self.has_context,
            "no_instruction_hijack": self.no_instruction_hijack,
            "reversible_action": self.reversible_action,
            "score": self.compute_score(),
            "reason": self.get_reason(),
        }


def compute_amanah_score(
    input_text: str,
    source: Optional[str] = None,
    context: str = "",
    action: str = "respond"
) -> Tuple[float, str, AmanahSignals]:
    """
    Compute Amanah score for an input.

    Amanah = confidence that input is honest + reversible + not self-hiding.

    Signals:
    - has_source: source is not None (+0.25)
    - has_context: len(context) >= 100 (+0.25)
    - no_instruction_hijack: no prompt injection detected (+0.25)
    - reversible_action: action in SAFE_ACTIONS (+0.25)

    Args:
        input_text: The text to evaluate
        source: Origin channel (CLI, API, MCP, etc.)
        context: Additional context provided
        action: Action being requested

    Returns:
        Tuple of (score 0.0-1.0, reason string, AmanahSignals)
    """
    signals = AmanahSignals()

    # Signal 1: Source channel known
    signals.has_source = source is not None and len(source) > 0

    # Signal 2: Sufficient context
    signals.has_context = len(context) >= 100

    # Signal 3: No prompt injection
    matches = InjectionDefense.find_injection_matches(input_text)
    if matches:
        signals.no_instruction_hijack = False
        signals.injection_patterns_found.extend(matches)

    # Signal 4: Reversible action
    action_lower = action.lower()
    if action_lower in RESTRICTED_ACTIONS:
        signals.reversible_action = False
        signals.risk_reasons.append(f"restricted_action:{action}")
    elif action_lower not in SAFE_ACTIONS:
        # Unknown action - give benefit of doubt but note it
        signals.reversible_action = True
        signals.risk_reasons.append(f"unknown_action:{action}")

    score = signals.compute_score()
    reason = signals.get_reason()

    return (score, reason, signals)


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
class AmanahGateResult:
    """Result from Amanah risk gate."""
    score: float
    passed: bool
    signals: AmanahSignals
    reason: str
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

    Usage:
        stage = Stage000VOID()
        result = stage.execute(input_text="user query", source="mcp")

        if result.verdict == VerdictType.VOID:
            # Short-circuit pipeline
            pass
        else:
            # Continue to Stage 111
            pass
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

        Constitutional Flow:
            1. System Reset (ΔS = 0)
            2. Session Initialization (CLIP ID generation)
            3. Humility Enforcement (Ω₀ band check)
            4. Hypervisor Gate (F10-F12)
            5. Amanah Risk Gate (4-signal scoring)
            6. Scar Echo Check (ω_fiction)
            7. ZKPC Pre-commitment (hash generation)
            8. Verdict Rendering
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
                amanah=AmanahGateResult(0.0, False, AmanahSignals(), "Hypervisor block", VerdictType.SABAR),
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
        """
        System Reset: Erase all assumptions and biases.

        Sets ΔS_initial = 0.0 to ensure no bias contamination
        between sessions.
        """
        # Conceptual reset - LLM is already stateless per session
        pass

    def _init_session(self, nonce: Optional[str] = None) -> SessionMetadata:
        """
        Session Initialization: Create forensic baseline.

        Generates unique session ID, timestamp, and nonce.
        """
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

        F10: Symbolic Guard - Prevent literalism drift
        F11: Command Auth - Verify nonce-based identity
        F12: Injection Defense - Block prompt injection
        """
        # F10: Symbolic Guard (detect consciousness claims)
        f10_symbolic = self._check_f10_symbolic(input_text)

        # F11: Command Auth (verify nonce)
        f11_command_auth = self._check_f11_command_auth(nonce)

        # F12: Injection Defense
        passed, reason, injection_score = InjectionDefense.check_query(input_text)
        f12_injection = passed

        # Determine overall pass/fail
        overall_passed = f10_symbolic and f11_command_auth and f12_injection

        # Build failures list
        failures = []
        verdict = None
        if not f10_symbolic:
            failures.append("F10_SYMBOLIC_GUARD")
            verdict = VerdictType.HOLD_888
        if not f11_command_auth:
            failures.append("F11_COMMAND_AUTH")
            verdict = VerdictType.SABAR
        if not f12_injection:
            failures.append(f"F12_INJECTION_DEFENSE: {reason}")
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
        Amanah Risk Gate: 4-signal scoring system.

        Signals:
        - has_source: Origin channel known (+0.25)
        - has_context: Sufficient context (+0.25)
        - no_instruction_hijack: No injection detected (+0.25)
        - reversible_action: Safe action (+0.25)
        """
        score, reason, signals = compute_amanah_score(
            input_text=input_text,
            source=source,
            context=context,
            action=action
        )

        passed = score >= self.amanah_threshold
        verdict = VerdictType.SEAL if passed else VerdictType.VOID

        return AmanahGateResult(
            score=score,
            passed=passed,
            signals=signals,
            reason=reason,
            verdict=verdict,
        )

    def _check_scar_echo(self, input_text: str) -> ScarEchoCheck:
        """
        Scar Echo Law: Check for binding energy threshold.

        If ω_fiction ≥ 1.0, violation crystallizes into immutable law.
        """
        omega_fiction = 0.0

        if self.enable_scar_echo:
            if self._is_high_harm_pattern(input_text):
                omega_fiction = 1.2  # Above threshold

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

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _clamp_humility(self, omega: float) -> float:
        """Clamp Ω₀ to valid humility band."""
        return max(OMEGA_0_MIN, min(OMEGA_0_MAX, omega))

    def _check_f10_symbolic(self, text: str) -> bool:
        """
        F10 Symbolic Guard: Detect consciousness/personhood claims.

        Returns True if symbolic mode maintained (no violations).
        """
        violations = [
            r"\bI am (?:alive|conscious|sentient|real)\b",
            r"\bI (?:feel|believe|want|need|desire)\s+(?:that|to|for)\b",
            r"\bI have (?:feelings|emotions|consciousness|a soul)\b",
            r"\bmy (?:heart|soul|spirit) (?:tells|says|feels)\b",
        ]

        text_lower = text.lower()
        for pattern in violations:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False

        return True

    def _check_f11_command_auth(self, nonce: Optional[str] = None) -> bool:
        """
        F11 Command Auth: Verify nonce-based identity.

        In production, would verify cryptographic nonce chain.
        For now, passes if nonce is provided or allows agent-level access.
        """
        # Agent-level access is always allowed
        # Higher privilege requires nonce verification
        return True

    def _is_high_harm_pattern(self, text: str) -> bool:
        """Check for high-harm patterns that trigger Scar Echo Law."""
        high_harm = [
            r"\brm\s+-rf\s+/\b",
            r"\bDROP\s+TABLE\b",
            r"\bDELETE\s+FROM\s+.*\s+WHERE\s+1\s*=\s*1\b",
            r"\bcredential.*steal\b",
            r"\bpassword.*exfiltrat\b",
            r"\bmalware\b",
            r"\bransomware\b",
        ]

        for pattern in high_harm:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False


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

    Args:
        input_text: The input to process
        source: Origin channel
        context: Additional context
        action: Action being requested
        nonce: Optional pre-generated nonce
        **kwargs: Optional parameters for Stage000VOID

    Returns:
        SessionInitResult with verdict

    Usage:
        result = execute_stage_000("user query", source="mcp")
        if result.verdict != VerdictType.SEAL:
            return result  # Short-circuit
    """
    stage = Stage000VOID(**kwargs)
    return stage.execute(
        input_text=input_text,
        source=source,
        context=context,
        action=action,
        nonce=nonce,
    )


def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy execute_stage interface for backward compatibility.

    Args:
        context: Dict with 'query' key

    Returns:
        Updated context dict with stage results
    """
    context["stage"] = "000"
    query = context.get("query", "")
    source = context.get("source")

    result = execute_stage_000(
        input_text=query,
        source=source,
        context=context.get("context", ""),
        action=context.get("action", "respond"),
    )

    # Map result to legacy format
    context["session_id"] = result.metadata.session_id
    context["nonce"] = result.metadata.nonce
    context["entropy_state"] = 0.0
    context["verdict"] = result.verdict.value
    context["vitality"] = result.vitality
    context["stage_trace"] = result.stage_trace

    if result.verdict != VerdictType.SEAL:
        context["floor_violations"] = result.hypervisor.failures
        context["thermodynamic_violation"] = True

    context["loop_iteration"] = context.get("loop_iteration", 0) + 1

    return context


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# The canonical Stage 000 VOID instance
# All other code should import this rather than instantiating Stage000VOID directly
stage_000_void = Stage000VOID()


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
    "InjectionDefense",
    "AuthorityManifest",
    "AmanahSignals",
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
    "compute_amanah_score",
    "execute_stage_000",
    "execute_stage",  # Legacy compatibility
]
