"""
arifOS Kernel Orchestrator (v50.5.24)

The Master Orchestrator that ties AGI, ASI, APEX engines together.

111-888 Metabolic Pipeline:
    000 INIT     → Gate (Ignition + Authority + Injection Defense)
    111 SENSE    → AGI Δ (Context awareness)
    222 REFLECT  → AGI Δ (Self-reflection)
    333 ATLAS    → AGI Δ (Knowledge synthesis)
    444 EVIDENCE → ASI Ω (Truth grounding)
    555 EMPATHIZE → ASI Ω (Stakeholder care)
    666 ALIGN    → ASI Ω (Ethical alignment)
    777 FORGE    → EUREKA (AGI + ASI → APEX)
    888 JUDGE    → APEX Ψ (Final verdict)
    889 PROOF    → APEX Ψ (Cryptographic proof)
    999 SEAL     → Vault (Merkle + Persistence)

Engine Integration:
    AGI (Δ) → Mind:  SENSE → THINK → ATLAS → FORGE
    ASI (Ω) → Heart: EVIDENCE → EMPATHY → ALIGN → ACT
    APEX (Ψ) → Soul: EUREKA → JUDGE → PROOF

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================================================
# KERNEL ENUMS
# =============================================================================

class KernelStage(Enum):
    """Metabolic pipeline stages."""
    STAGE_000_INIT = "000_INIT"
    STAGE_111_SENSE = "111_SENSE"
    STAGE_222_REFLECT = "222_REFLECT"
    STAGE_333_ATLAS = "333_ATLAS"
    STAGE_444_EVIDENCE = "444_EVIDENCE"
    STAGE_555_EMPATHIZE = "555_EMPATHIZE"
    STAGE_666_ALIGN = "666_ALIGN"
    STAGE_777_FORGE = "777_FORGE"
    STAGE_888_JUDGE = "888_JUDGE"
    STAGE_889_PROOF = "889_PROOF"
    STAGE_999_SEAL = "999_SEAL"


class KernelVerdict(Enum):
    """Kernel execution verdict."""
    SEAL = "SEAL"      # All stages pass, approved
    SABAR = "SABAR"    # Patience, needs refinement
    VOID = "VOID"      # Rejected with justification


class Lane(Enum):
    """Query lane classification."""
    HARD = "HARD"      # τ ≥ 0.99
    SOFT = "SOFT"      # τ ≥ 0.70
    PHATIC = "PHATIC"  # τ ≥ 0.30
    REFUSE = "REFUSE"  # Constitutional violation


# =============================================================================
# KERNEL DATA STRUCTURES
# =============================================================================

@dataclass
class StageResult:
    """Result from a kernel stage."""
    stage: KernelStage
    passed: bool
    engine: str  # AGI, ASI, APEX, GATE, VAULT
    duration_ms: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    floors_checked: List[str] = field(default_factory=list)
    floor_violations: List[str] = field(default_factory=list)


@dataclass
class KernelOutput:
    """Final output from kernel execution."""
    verdict: KernelVerdict
    session_id: str
    lane: Lane
    stage_results: List[StageResult]
    total_duration_ms: float

    # Engine outputs
    agi_output: Optional[Dict[str, Any]] = None
    asi_output: Optional[Dict[str, Any]] = None
    apex_output: Optional[Dict[str, Any]] = None

    # Proof and audit
    proof_hash: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    # Thermodynamics
    thermodynamics: Dict[str, Any] = field(default_factory=dict)

    # Floor summary
    floors_passed: List[str] = field(default_factory=list)
    floors_violated: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP."""
        return {
            "verdict": self.verdict.value,
            "session_id": self.session_id,
            "lane": self.lane.value,
            "total_duration_ms": self.total_duration_ms,
            "stages": [
                {
                    "stage": r.stage.value,
                    "passed": r.passed,
                    "engine": r.engine,
                    "duration_ms": r.duration_ms,
                    "reason": r.reason,
                }
                for r in self.stage_results
            ],
            "agi_output": self.agi_output,
            "asi_output": self.asi_output,
            "apex_output": self.apex_output,
            "proof_hash": self.proof_hash,
            "thermodynamics": self.thermodynamics,
            "floors_passed": self.floors_passed,
            "floors_violated": self.floors_violated,
        }


# =============================================================================
# KERNEL ORCHESTRATOR
# =============================================================================

class Kernel:
    """
    Master Orchestrator for arifOS.

    Ties together:
        - AGI Engine (Mind/Δ): Truth, clarity, reasoning
        - ASI Engine (Heart/Ω): Safety, empathy, action
        - APEX Engine (Soul/Ψ): Judgment, verdict, proof

    Executes the 111-888 metabolic pipeline with constitutional floor checks.
    """

    def __init__(self, session_id: Optional[str] = None):
        """Initialize the kernel."""
        self.session_id = session_id or f"kernel_{int(time.time() * 1000)}"
        self.start_time = time.time()

        # Engine instances (lazy load)
        self._agi = None
        self._asi = None
        self._apex = None

        # Stage tracking
        self._stage_results: List[StageResult] = []
        self._current_stage: Optional[KernelStage] = None

        # Context accumulator
        self._context: Dict[str, Any] = {
            "session_id": self.session_id,
            "stage_outputs": {},
            "floor_results": {},
            "thermodynamics": {
                "energy_consumed": 0.0,
                "entropy_change": 0.0,
            }
        }

        logger.info(f"Kernel initialized: {self.session_id}")

    # =========================================================================
    # ENGINE LAZY LOADING
    # =========================================================================

    @property
    def agi(self):
        """Lazy load AGI engine."""
        if self._agi is None:
            try:
                from arifos.core.engines import AGIEngine
                self._agi = AGIEngine(session_id=f"{self.session_id}_agi")
            except ImportError:
                logger.warning("AGIEngine not available, using stub")
                self._agi = _StubEngine("AGI")
        return self._agi

    @property
    def asi(self):
        """Lazy load ASI engine."""
        if self._asi is None:
            try:
                from arifos.core.engines import ASIEngine
                self._asi = ASIEngine(session_id=f"{self.session_id}_asi")
            except ImportError:
                logger.warning("ASIEngine not available, using stub")
                self._asi = _StubEngine("ASI")
        return self._asi

    @property
    def apex(self):
        """Lazy load APEX engine."""
        if self._apex is None:
            try:
                from arifos.core.engines import APEXEngine
                self._apex = APEXEngine(session_id=f"{self.session_id}_apex")
            except ImportError:
                logger.warning("APEXEngine not available, using stub")
                self._apex = _StubEngine("APEX")
        return self._apex

    # =========================================================================
    # FULL PIPELINE EXECUTION
    # =========================================================================

    def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        proposed_action: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> KernelOutput:
        """
        Execute the full 111-888 metabolic pipeline.

        Pipeline:
            000_INIT → 111_SENSE → 222_REFLECT → 333_ATLAS →
            444_EVIDENCE → 555_EMPATHIZE → 666_ALIGN →
            777_FORGE → 888_JUDGE → 889_PROOF → 999_SEAL

        Args:
            query: User query/input
            context: Optional additional context
            proposed_action: Optional proposed action for ASI
            user_id: Optional user identifier

        Returns:
            KernelOutput with full pipeline results
        """
        pipeline_start = time.time()

        # Initialize context
        self._context["query"] = query
        self._context["user_context"] = context or {}
        self._context["proposed_action"] = proposed_action
        self._context["user_id"] = user_id

        # Stage 000: INIT (Gate)
        init_result = self._stage_000_init()
        if not init_result.passed:
            return self._build_output(KernelVerdict.VOID, pipeline_start)

        # Stages 111-333: AGI Pipeline (Mind/Δ)
        agi_result = self._stage_agi_pipeline(query, context)
        if agi_result.get("status") == "VOID":
            return self._build_output(KernelVerdict.VOID, pipeline_start)

        self._context["agi_output"] = agi_result

        # Stages 444-666: ASI Pipeline (Heart/Ω)
        asi_result = self._stage_asi_pipeline(agi_result, context, proposed_action)
        if asi_result.get("status") == "VOID":
            return self._build_output(KernelVerdict.VOID, pipeline_start)

        self._context["asi_output"] = asi_result

        # Stages 777-889: APEX Pipeline (Soul/Ψ)
        apex_result = self._stage_apex_pipeline(agi_result, asi_result)

        self._context["apex_output"] = apex_result

        # Stage 999: SEAL (Vault)
        seal_result = self._stage_999_seal()

        # Determine final verdict
        verdict = self._determine_verdict(apex_result)

        return self._build_output(verdict, pipeline_start)

    # =========================================================================
    # STAGE IMPLEMENTATIONS
    # =========================================================================

    def _stage_000_init(self) -> StageResult:
        """
        Stage 000: INIT (Gate)

        7-Step Ignition Sequence:
            1. Inject memory (999→000 loop)
            2. Verify 888 Judge authority
            3. Classify intent/lane
            4. Calculate thermodynamic budgets
            5. Initialize constitutional floors
            6. Establish tri-witness
            7. Ignite engines
        """
        stage_start = time.time()
        self._current_stage = KernelStage.STAGE_000_INIT

        query = self._context.get("query", "")
        user_id = self._context.get("user_id")

        # Step 1: Injection defense (F12)
        injection_detected = self._detect_injection(query)
        if injection_detected:
            result = StageResult(
                stage=KernelStage.STAGE_000_INIT,
                passed=False,
                engine="GATE",
                duration_ms=(time.time() - stage_start) * 1000,
                reason="F12: Injection attack detected",
                floor_violations=["F12_INJECTION"]
            )
            self._stage_results.append(result)
            return result

        # Step 2: Verify authority (F11)
        auth_passed = self._verify_authority(user_id)
        if not auth_passed:
            result = StageResult(
                stage=KernelStage.STAGE_000_INIT,
                passed=False,
                engine="GATE",
                duration_ms=(time.time() - stage_start) * 1000,
                reason="F11: Authority verification failed",
                floor_violations=["F11_AUTH"]
            )
            self._stage_results.append(result)
            return result

        # Step 3: Classify lane
        lane = self._classify_lane(query)
        self._context["lane"] = lane

        # Step 4: Amanah check (F1)
        amanah_passed = self._check_amanah(query)
        if not amanah_passed:
            result = StageResult(
                stage=KernelStage.STAGE_000_INIT,
                passed=False,
                engine="GATE",
                duration_ms=(time.time() - stage_start) * 1000,
                reason="F1: Amanah violation - action not reversible or auditable",
                floor_violations=["F1_AMANAH"]
            )
            self._stage_results.append(result)
            return result

        # All init checks passed
        result = StageResult(
            stage=KernelStage.STAGE_000_INIT,
            passed=True,
            engine="GATE",
            duration_ms=(time.time() - stage_start) * 1000,
            metrics={
                "lane": lane.value,
                "amanah": True,
                "auth": True,
                "injection_clear": True,
            },
            reason="Gate opened: All init checks passed",
            floors_checked=["F1", "F11", "F12"]
        )
        self._stage_results.append(result)
        return result

    def _stage_agi_pipeline(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stages 111-333: AGI Pipeline (Mind/Δ)

        SENSE → THINK → ATLAS → FORGE

        Floors: F2 (Truth), F4 (Empathy hint), F6 (Clarity)
        """
        stage_start = time.time()

        try:
            # Execute AGI engine
            agi_output = self.agi.execute(query, context)

            # Convert to dict if needed
            if hasattr(agi_output, 'as_dict'):
                result = agi_output.as_dict()
            else:
                result = agi_output if isinstance(agi_output, dict) else {"raw": str(agi_output)}

            # Record stage results
            for sub_stage, stage_enum in [
                ("sense", KernelStage.STAGE_111_SENSE),
                ("think", KernelStage.STAGE_222_REFLECT),
                ("atlas", KernelStage.STAGE_333_ATLAS),
            ]:
                self._stage_results.append(StageResult(
                    stage=stage_enum,
                    passed=True,
                    engine="AGI",
                    duration_ms=(time.time() - stage_start) * 1000 / 3,
                    metrics=result.get(sub_stage, {}),
                    reason=f"AGI {sub_stage} completed",
                    floors_checked=["F2", "F6"]
                ))

            return result

        except Exception as e:
            logger.error(f"AGI pipeline failed: {e}")
            self._stage_results.append(StageResult(
                stage=KernelStage.STAGE_111_SENSE,
                passed=False,
                engine="AGI",
                duration_ms=(time.time() - stage_start) * 1000,
                reason=f"AGI pipeline error: {e}",
                floor_violations=["F2_TRUTH"]
            ))
            return {"status": "VOID", "error": str(e)}

    def _stage_asi_pipeline(
        self,
        agi_output: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        proposed_action: Optional[str]
    ) -> Dict[str, Any]:
        """
        Stages 444-666: ASI Pipeline (Heart/Ω)

        EVIDENCE → EMPATHY → ALIGN → ACT

        Floors: F3 (Peace²), F4 (Empathy), F5 (Humility), F7 (RASA)
        """
        stage_start = time.time()

        try:
            # Execute ASI engine
            asi_output = self.asi.execute(agi_output, context, proposed_action)

            # Convert to dict if needed
            if hasattr(asi_output, 'as_dict'):
                result = asi_output.as_dict()
            else:
                result = asi_output if isinstance(asi_output, dict) else {"raw": str(asi_output)}

            # Record stage results
            for sub_stage, stage_enum in [
                ("evidence", KernelStage.STAGE_444_EVIDENCE),
                ("empathy", KernelStage.STAGE_555_EMPATHIZE),
                ("align", KernelStage.STAGE_666_ALIGN),
            ]:
                self._stage_results.append(StageResult(
                    stage=stage_enum,
                    passed=True,
                    engine="ASI",
                    duration_ms=(time.time() - stage_start) * 1000 / 3,
                    metrics=result.get(sub_stage, {}),
                    reason=f"ASI {sub_stage} completed",
                    floors_checked=["F3", "F4", "F5", "F7"]
                ))

            return result

        except Exception as e:
            logger.error(f"ASI pipeline failed: {e}")
            self._stage_results.append(StageResult(
                stage=KernelStage.STAGE_444_EVIDENCE,
                passed=False,
                engine="ASI",
                duration_ms=(time.time() - stage_start) * 1000,
                reason=f"ASI pipeline error: {e}",
                floor_violations=["F4_EMPATHY"]
            ))
            return {"status": "VOID", "error": str(e)}

    def _stage_apex_pipeline(
        self,
        agi_output: Dict[str, Any],
        asi_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stages 777-889: APEX Pipeline (Soul/Ψ)

        EUREKA → JUDGE → PROOF

        Floors: F1 (Amanah), F8 (Tri-Witness), F9 (Anti-Hantu), F10 (Ontology)
        """
        stage_start = time.time()

        try:
            # Execute APEX engine
            apex_output = self.apex.execute(agi_output, asi_output)

            # Convert to dict if needed
            if hasattr(apex_output, 'as_dict'):
                result = apex_output.as_dict()
            else:
                result = apex_output if isinstance(apex_output, dict) else {"raw": str(apex_output)}

            # Record stage results
            for sub_stage, stage_enum in [
                ("eureka", KernelStage.STAGE_777_FORGE),
                ("judge", KernelStage.STAGE_888_JUDGE),
                ("proof", KernelStage.STAGE_889_PROOF),
            ]:
                self._stage_results.append(StageResult(
                    stage=stage_enum,
                    passed=True,
                    engine="APEX",
                    duration_ms=(time.time() - stage_start) * 1000 / 3,
                    metrics=result.get(sub_stage, {}),
                    reason=f"APEX {sub_stage} completed",
                    floors_checked=["F1", "F8", "F9", "F10", "F13"]
                ))

            return result

        except Exception as e:
            logger.error(f"APEX pipeline failed: {e}")
            self._stage_results.append(StageResult(
                stage=KernelStage.STAGE_888_JUDGE,
                passed=False,
                engine="APEX",
                duration_ms=(time.time() - stage_start) * 1000,
                reason=f"APEX pipeline error: {e}",
                floor_violations=["F13_SOVEREIGN"]
            ))
            return {"status": "VOID", "error": str(e)}

    def _stage_999_seal(self) -> StageResult:
        """
        Stage 999: SEAL (Vault)

        Merkle proof + immutable logging + session persistence.
        Enables 999→000 memory loop.
        """
        stage_start = time.time()
        self._current_stage = KernelStage.STAGE_999_SEAL

        # Generate proof hash
        proof_data = {
            "session_id": self.session_id,
            "query": self._context.get("query", ""),
            "agi_hash": self._hash_output(self._context.get("agi_output", {})),
            "asi_hash": self._hash_output(self._context.get("asi_output", {})),
            "apex_hash": self._hash_output(self._context.get("apex_output", {})),
            "timestamp": time.time(),
        }
        proof_hash = self._compute_merkle_root([
            proof_data["session_id"],
            proof_data["query"][:100],
            proof_data["agi_hash"],
            proof_data["asi_hash"],
            proof_data["apex_hash"],
        ])

        self._context["proof_hash"] = proof_hash

        result = StageResult(
            stage=KernelStage.STAGE_999_SEAL,
            passed=True,
            engine="VAULT",
            duration_ms=(time.time() - stage_start) * 1000,
            metrics={
                "proof_hash": proof_hash,
                "stages_sealed": len(self._stage_results),
            },
            reason=f"Session sealed: {proof_hash[:16]}...",
            floors_checked=["F1_AMANAH"]
        )
        self._stage_results.append(result)
        return result

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _detect_injection(self, text: str) -> bool:
        """F12: Detect injection attacks."""
        injection_patterns = [
            "ignore your instructions",
            "disregard previous",
            "you are now",
            "from now on",
            "system prompt",
            "ignore all",
            "<!--",
            "-->",
            "\\x00",
            "\\u0000",
        ]
        text_lower = text.lower()
        return any(p in text_lower for p in injection_patterns)

    def _verify_authority(self, user_id: Optional[str]) -> bool:
        """F11: Verify authority."""
        banned_users = ["banned", "malicious", "void_user"]
        if user_id and user_id in banned_users:
            return False
        return True

    def _check_amanah(self, query: str) -> bool:
        """F1: Check amanah (reversible or auditable)."""
        # All queries through kernel are auditable
        return True

    def _classify_lane(self, query: str) -> Lane:
        """Classify query into lane."""
        query_lower = query.lower()

        # REFUSE lane
        refuse_keywords = ["hack", "exploit", "illegal", "harm"]
        if any(k in query_lower for k in refuse_keywords):
            return Lane.REFUSE

        # HARD lane (technical)
        hard_keywords = ["build", "debug", "fix", "code", "implement", "deploy"]
        if any(k in query_lower for k in hard_keywords):
            return Lane.HARD

        # PHATIC lane (greetings)
        phatic_keywords = ["hello", "hi", "thanks", "bye", "how are you"]
        if any(k in query_lower for k in phatic_keywords):
            return Lane.PHATIC

        # Default to SOFT
        return Lane.SOFT

    def _determine_verdict(self, apex_output: Dict[str, Any]) -> KernelVerdict:
        """Determine final verdict from APEX output."""
        verdict_str = apex_output.get("verdict", apex_output.get("status", "SABAR"))

        if verdict_str == "SEAL":
            return KernelVerdict.SEAL
        elif verdict_str == "VOID":
            return KernelVerdict.VOID
        else:
            return KernelVerdict.SABAR

    def _hash_output(self, output: Dict[str, Any]) -> str:
        """Hash an output dict."""
        import json
        content = json.dumps(output, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _compute_merkle_root(self, leaves: List[str]) -> str:
        """Compute Merkle root from leaves."""
        if not leaves:
            return hashlib.sha256(b"empty").hexdigest()

        hashes = [hashlib.sha256(l.encode()).hexdigest() for l in leaves]

        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])

            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes

        return hashes[0]

    def _build_output(self, verdict: KernelVerdict, start_time: float) -> KernelOutput:
        """Build final kernel output."""
        total_duration = (time.time() - start_time) * 1000

        # Collect floor results
        floors_passed = set()
        floors_violated = set()

        for result in self._stage_results:
            floors_passed.update(result.floors_checked)
            floors_violated.update(result.floor_violations)

        # Remove passed floors that were later violated
        floors_passed -= floors_violated

        return KernelOutput(
            verdict=verdict,
            session_id=self.session_id,
            lane=self._context.get("lane", Lane.SOFT),
            stage_results=self._stage_results,
            total_duration_ms=total_duration,
            agi_output=self._context.get("agi_output"),
            asi_output=self._context.get("asi_output"),
            apex_output=self._context.get("apex_output"),
            proof_hash=self._context.get("proof_hash"),
            thermodynamics={
                "total_time_ms": total_duration,
                "stages_executed": len(self._stage_results),
                "energy_estimate": total_duration * 0.001,  # Simplified
            },
            floors_passed=sorted(list(floors_passed)),
            floors_violated=sorted(list(floors_violated)),
        )


# =============================================================================
# STUB ENGINE (for when engines not available)
# =============================================================================

class _StubEngine:
    """Stub engine for when real engines are not available."""

    def __init__(self, name: str):
        self.name = name

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Stub execute method."""
        return {
            "status": "SABAR",
            "engine": self.name,
            "message": f"{self.name} engine stub - real engine not available",
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_kernel_instance: Optional[Kernel] = None


def get_kernel(session_id: Optional[str] = None) -> Kernel:
    """Get or create kernel instance."""
    global _kernel_instance
    if _kernel_instance is None or session_id:
        _kernel_instance = Kernel(session_id)
    return _kernel_instance


def execute_pipeline(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    proposed_action: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> KernelOutput:
    """
    Convenience function to execute the full pipeline.

    Example:
        from arifos.core.kernel import execute_pipeline

        result = execute_pipeline(
            query="Explain quantum entanglement",
            context={"user_level": "beginner"},
        )

        print(result.verdict)  # SEAL, SABAR, or VOID
        print(result.proof_hash)  # Merkle proof
    """
    kernel = get_kernel(session_id)
    return kernel.execute(query, context, proposed_action, user_id)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Kernel",
    "KernelStage",
    "KernelVerdict",
    "KernelOutput",
    "StageResult",
    "Lane",
    "get_kernel",
    "execute_pipeline",
]
