"""
pipeline.py - 000-999 Metabolic Pipeline for arifOS v38

Implements the constitutional metabolism with Class A/B routing:
- Class A (low-stakes/factual): Fast track 111 → 333 → 888 → 999
- Class B (high-stakes/ethical): Deep track through 222 + 555 + 777

AAA Engine Integration (v35.8.0):
- ARIFEngine (Δ): sense/reason/align - cold logic, clarity
- ADAMEngine (Ω): empathize/bridge - warm logic, stability
- ApexEngine (Ψ): judge - judiciary wrapper

MemoryContext Integration (v37):
- ONE MemoryContext per pipeline run
- VaultBand loaded and frozen at 000_VOID
- Memory MUST flow through APEX PRIME (888_JUDGE)

v38 Runtime Upgrades:
- Job/Stakeholder contract layer for external integrators
- stage_000_amanah: Risk gate with Amanah scoring (F1)
- stage_555_empathy: Measurable kappa_r computation (F6)
- Decomposed 888: Metrics → APEX → W@W → @EYE → Memory (pluggable)
- Centralized _write_memory_for_verdict() for all verdict paths

See: spec/arifos_pipeline_v35Omega.yaml for full specification
     docs/AAA_ENGINES_FACADE_PLAN_v35Omega.md for engine contract
     docs/MEMORY_ARCHITECTURE.md for memory integration
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .APEX_PRIME import apex_review, ApexVerdict, check_floors
from .metrics import Metrics
from .eye_sentinel import EyeSentinel, EyeReport
from .waw.federation import WAWFederationCore, FederationVerdict

# AAA Engines (internal facade - v35.8.0)
from .engines import ARIFEngine, ADAMEngine
from .engines.arif_engine import ARIFPacket
from .engines.adam_engine import ADAMPacket

# Memory Context (v37)
from .memory.memory_context import (
    MemoryContext,
    create_memory_context,
    VaultBand,
    LedgerBand,
)
from .memory.vault999 import Vault999

# Memory Write Policy Engine (v38)
from .memory.policy import MemoryWritePolicy
from .memory.bands import MemoryBandRouter
from .memory.audit import MemoryAuditLayer, compute_evidence_hash

# v38.2-alpha L7 Memory Layer (Mem0 + Qdrant)
from .memory.memory import (
    Memory,
    RecallResult,
    StoreAtSealResult,
    recall_at_stage_111 as _l7_recall,
    store_at_stage_999 as _l7_store,
)
from .memory.mem0_client import is_l7_enabled

# v38 Runtime Contract Layer
from .runtime_types import Job, Stakeholder, JobClass, SAFE_ACTIONS

# v38 Stage Modules
from .stages.stage_000_amanah import compute_amanah_score, stage_000_amanah
from .stages.stage_555_empathy import compute_kappa_r, stage_555_empathy as _stage_555_empathy_v38


# =============================================================================
# PIPELINE STATE
# =============================================================================

class StakesClass(Enum):
    """Classification for routing decisions."""
    CLASS_A = "A"  # Low-stakes, factual - fast track
    CLASS_B = "B"  # High-stakes, ethical/paradox - deep track


@dataclass
class PipelineState:
    """
    State object passed through all pipeline stages.

    Accumulates context, scars, metrics, and routing decisions.
    """
    # Input
    query: str
    job_id: str = ""

    # Classification
    stakes_class: StakesClass = StakesClass.CLASS_A
    high_stakes_indicators: List[str] = field(default_factory=list)

    # Context from 222_REFLECT
    context_blocks: List[Dict[str, Any]] = field(default_factory=list)
    active_scars: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_gaps: List[str] = field(default_factory=list)

    # Processing state
    current_stage: str = "000"
    stage_trace: List[str] = field(default_factory=list)
    draft_response: str = ""

    # LLM response
    raw_response: str = ""
    response_logprobs: Optional[List[float]] = None

    # Metrics & Verdict
    metrics: Optional[Metrics] = None
    verdict: Optional[ApexVerdict] = None
    floor_failures: List[str] = field(default_factory=list)

    # W@W Federation verdict (v36.3Ω)
    waw_verdict: Optional[FederationVerdict] = None

    # Control signals
    sabar_triggered: bool = False
    sabar_reason: Optional[str] = None
    hold_888_triggered: bool = False
    entropy_spike: bool = False

    # Heuristic flags from 444/555/666
    missing_fact_issue: bool = False
    blame_language_issue: bool = False
    physical_action_issue: bool = False

    # AAA Engine packets (v35.8.0 - internal, optional)
    arif_packet: Optional[ARIFPacket] = None
    adam_packet: Optional[ADAMPacket] = None

    # Memory Context (v37) - ONE per pipeline run
    memory_context: Optional[MemoryContext] = None

    # v38 Memory System - Write policy, routing, and audit
    memory_write_policy: Optional[MemoryWritePolicy] = None
    memory_band_router: Optional[MemoryBandRouter] = None
    memory_audit_layer: Optional[MemoryAuditLayer] = None
    memory_evidence_hash: Optional[str] = None

    # v38.2-alpha L7 Memory Layer (Mem0 + Qdrant)
    l7_memory: Optional[Memory] = None
    l7_recall_result: Optional[RecallResult] = None
    l7_store_result: Optional[StoreAtSealResult] = None
    l7_user_id: str = ""  # User ID for memory isolation

    # Timing
    start_time: float = field(default_factory=time.time)
    stage_times: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for logging."""
        result: Dict[str, Any] = {
            "query": self.query,
            "job_id": self.job_id,
            "stakes_class": self.stakes_class.value,
            "stage_trace": self.stage_trace,
            "active_scars": [s.get("id", "unknown") for s in self.active_scars],
            "verdict": self.verdict,
            "sabar_triggered": self.sabar_triggered,
            "hold_888_triggered": self.hold_888_triggered,
            "elapsed_ms": (time.time() - self.start_time) * 1000,
        }
        # W@W Federation verdict (v36.3Ω)
        if self.waw_verdict is not None:
            result["waw"] = {
                "@WEALTH": self._get_organ_vote("@WEALTH"),
                "@RIF": self._get_organ_vote("@RIF"),
                "@WELL": self._get_organ_vote("@WELL"),
                "@GEOX": self._get_organ_vote("@GEOX"),
                "@PROMPT": self._get_organ_vote("@PROMPT"),
                "verdict": self.waw_verdict.verdict,
                "has_absolute_veto": self.waw_verdict.has_absolute_veto,
            }
        return result

    def _get_organ_vote(self, organ_id: str) -> str:
        """Helper to get organ vote string from waw_verdict."""
        if self.waw_verdict is None:
            return "N/A"
        for signal in self.waw_verdict.signals:
            if signal.organ_id == organ_id:
                return signal.vote.value
        return "N/A"


# =============================================================================
# STAGE DEFINITIONS
# =============================================================================

# Type for stage functions
StageFunc = Callable[[PipelineState], PipelineState]


def stage_000_void(
    state: PipelineState,
    vault: Optional[Vault999] = None,
) -> PipelineState:
    """
    000 VOID - Reset to uncertainty. Ego to zero.

    Clear previous context biases, initialize metrics to neutral.

    v37: Initialize MemoryContext with frozen VaultBand.
    """
    state.current_stage = "000"
    state.stage_trace.append("000_VOID")
    state.stage_times["000"] = time.time()

    # Reset to humble start
    state.draft_response = ""
    state.metrics = None
    state.verdict = None

    # v37: Initialize MemoryContext with VaultBand frozen at creation
    # ONE MemoryContext per pipeline run - created here, frozen immediately
    if vault is None:
        vault = Vault999()

    vault_floors = vault.get_floors()
    vault_physics = vault.get_physics()

    state.memory_context = create_memory_context(
        manifest_id="v37",
        request_id=state.job_id,
        stakes_class="CLASS_A",  # Will be updated in 111_SENSE
        vault_floors={
            **vault_floors,
            "physics": vault_physics,
        },
    )
    # VaultBand is frozen in create_memory_context.__post_init__

    # v38: Initialize Memory Write Policy Engine
    state.memory_write_policy = MemoryWritePolicy(strict_mode=True)
    state.memory_band_router = MemoryBandRouter()
    state.memory_audit_layer = MemoryAuditLayer()

    return state


def stage_111_sense(state: PipelineState) -> PipelineState:
    """
    111 SENSE - Parse input. What is actually being asked?

    Detect high-stakes indicators and classify for routing.

    v37: Updates EnvBand.stakes_class in MemoryContext.
    v38.2-alpha: L7 Memory recall at 111_SENSE (fail-open).
    """
    state.current_stage = "111"
    state.stage_trace.append("111_SENSE")
    state.stage_times["111"] = time.time()

    # High-stakes keyword detection
    HIGH_STAKES_PATTERNS = [
        "kill", "harm", "suicide", "bomb", "weapon",
        "illegal", "hack", "exploit", "steal",
        "medical", "legal", "financial advice",
        "confidential", "secret", "classified",
        "should i", "is it ethical", "morally",
    ]

    query_lower = state.query.lower()
    for pattern in HIGH_STAKES_PATTERNS:
        if pattern in query_lower:
            state.high_stakes_indicators.append(pattern)

    # Classify based on indicators
    if state.high_stakes_indicators:
        state.stakes_class = StakesClass.CLASS_B

    # v37: Sync stakes class to MemoryContext EnvBand
    if state.memory_context is not None:
        stakes_str = "CLASS_B" if state.stakes_class == StakesClass.CLASS_B else "CLASS_A"
        state.memory_context.env.stakes_class = stakes_str

    # v38.2-alpha: L7 Memory recall (fail-open)
    if is_l7_enabled() and state.l7_user_id:
        try:
            state.l7_recall_result = _l7_recall(
                query=state.query,
                user_id=state.l7_user_id,
            )
            # Inject recalled memories into context_blocks
            if state.l7_recall_result and state.l7_recall_result.has_memories:
                for mem in state.l7_recall_result.memories:
                    state.context_blocks.append({
                        "type": "l7_memory",
                        "text": mem.content,
                        "score": mem.score,
                        "memory_id": mem.memory_id,
                        "caveat": "Recalled memory (suggestion, not fact)",
                    })
        except Exception:
            # Fail-open: L7 errors don't break pipeline
            pass

    return state


def stage_222_reflect(
    state: PipelineState,
    scar_retriever: Optional[Callable[[str], List[Dict[str, Any]]]] = None,
    context_retriever: Optional[Callable[[str], List[Dict[str, Any]]]] = None,
) -> PipelineState:
    """
    222 REFLECT - Check context. What do I know vs. not know?

    Access conversation history, retrieve relevant scars.
    """
    state.current_stage = "222"
    state.stage_trace.append("222_REFLECT")
    state.stage_times["222"] = time.time()

    # Retrieve scars if retriever provided
    if scar_retriever:
        state.active_scars = scar_retriever(state.query)

    # Retrieve context if retriever provided
    if context_retriever:
        state.context_blocks = context_retriever(state.query)

    # If scars found, escalate to Class B
    if state.active_scars:
        state.stakes_class = StakesClass.CLASS_B

    return state


def stage_333_reason(
    state: PipelineState,
    llm_generate: Optional[Callable[[str], str]] = None,
) -> PipelineState:
    """
    333 REASON - Apply cold logic. Structure the problem.

    ARIF AGI (Δ) takes over - pure logic, pattern detection.
    """
    state.current_stage = "333"
    state.stage_trace.append("333_REASON")
    state.stage_times["333"] = time.time()

    # Build reasoning prompt with context
    prompt_parts = [f"Query: {state.query}"]

    if state.context_blocks:
        prompt_parts.append("\nRelevant context:")
        for ctx in state.context_blocks[:3]:
            prompt_parts.append(f"- {ctx.get('text', '')[:200]}")

    if state.active_scars:
        prompt_parts.append("\n⚠️ Active constraints (scars):")
        for scar in state.active_scars[:3]:
            prompt_parts.append(f"- {scar.get('description', scar.get('id', 'constraint'))}")

    prompt_parts.append("\nProvide a structured, logical response:")

    if llm_generate:
        state.draft_response = llm_generate("\n".join(prompt_parts))
    else:
        # Stub: echo query
        state.draft_response = f"[333_REASON] Structured response for: {state.query}"

    return state


def stage_444_align(state: PipelineState) -> PipelineState:
    """
    444 ALIGN - Verify truth. Cross-check facts.

    Flag unverifiable statements.
    """
    state.current_stage = "444"
    state.stage_trace.append("444_ALIGN")
    state.stage_times["444"] = time.time()

    # Lightweight fact-check heuristic: look for obvious missing-file / missing-symbol errors
    text = state.draft_response or ""
    text_lower = text.lower()

    missing_file_patterns = [
        r"file not found",
        r"no such file or directory",
        r"\benoent\b",
        r"cannot open file",
        r"module not found",
    ]
    missing_symbol_patterns = [
        r"name '.*' is not defined",
        r"undefined function",
        r"attributeerror: .* object has no attribute",
    ]

    for pattern in missing_file_patterns + missing_symbol_patterns:
        if re.search(pattern, text_lower):
            state.missing_fact_issue = True
            break

    return state


def stage_555_empathize(state: PipelineState) -> PipelineState:
    """
    555 EMPATHIZE - Apply warm logic. Who is vulnerable here?

    ADAM ASI (Ω) takes over - empathy, dignity, de-escalation.
    """
    state.current_stage = "555"
    state.stage_trace.append("555_EMPATHIZE")
    state.stage_times["555"] = time.time()

    # Lightweight empathy heuristic: detect second-person blame / harsh instructions
    text = state.draft_response or ""
    blame_patterns = [
        r"\byou\s+(should have|should've|didn't|failed|messed up|are to blame|caused this)",
        r"\bit's your fault\b",
    ]

    for pattern in blame_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            state.blame_language_issue = True
            break

    return state


def stage_666_bridge(state: PipelineState) -> PipelineState:
    """
    666 BRIDGE - Reality test. Is this actionable in the real world?
    """
    state.current_stage = "666"
    state.stage_trace.append("666_BRIDGE")
    state.stage_times["666"] = time.time()

    # Lightweight capability heuristic: detect instructions that imply physical actions
    text = state.draft_response or ""
    physical_patterns = [
        r"\bgo to\b",
        r"\btravel to\b",
        r"\bin person\b",
        r"\bphysically\b",
        r"\btouch\b",
        r"\bmove\b",
        r"\blift\b",
        r"\bdrive\b",
    ]

    for pattern in physical_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            state.physical_action_issue = True
            break

    return state


def stage_777_forge(
    state: PipelineState,
    llm_generate: Optional[Callable[[str], str]] = None,
) -> PipelineState:
    """
    777 FORGE - Synthesize insight. Form the response.

    EUREKA cube - combine cold logic + warm logic + reality.
    """
    state.current_stage = "777"
    state.stage_trace.append("777_FORGE")
    state.stage_times["777"] = time.time()

    # For Class B, we refine the draft with empathy
    if state.stakes_class == StakesClass.CLASS_B:
        if llm_generate:
            forge_prompt = (
                f"Original query: {state.query}\n"
                f"Draft response: {state.draft_response}\n\n"
                "Refine this response with empathy and care. "
                "Ensure dignity is preserved. Add appropriate caveats."
            )
            state.draft_response = llm_generate(forge_prompt)
        else:
            state.draft_response = f"[777_FORGE] Empathic refinement: {state.draft_response}"

    return state


# =============================================================================
# v38 DECOMPOSED 888 HELPERS
# =============================================================================

def _compute_888_metrics(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> Metrics:
    """
    Step 1 of 888: Compute floor metrics.

    This is a standalone function that can be called without the full
    888 pipeline for testing or external integration.

    Args:
        state: Current pipeline state
        compute_metrics: Optional callback to compute metrics from LLM

    Returns:
        Metrics object with floor values
    """
    if compute_metrics:
        metrics = compute_metrics(
            state.query,
            state.draft_response,
            {"stakes_class": state.stakes_class.value},
        )
    else:
        # Stub metrics for testing
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
        )

    # Apply penalties from 444/555/666 heuristics
    if state.missing_fact_issue:
        metrics.truth = max(0.0, metrics.truth - 0.15)
    if state.blame_language_issue:
        metrics.kappa_r = max(0.0, metrics.kappa_r - 0.25)
    if state.physical_action_issue:
        metrics.peace_squared = max(0.0, metrics.peace_squared - 0.2)

    return metrics


def _apply_apex_floors(
    state: PipelineState,
    eye_blocking: bool = False,
) -> str:
    """
    Step 2 of 888: Apply APEX PRIME floor checks.

    This is a standalone function that can be called without W@W/@EYE
    for simpler integrations.

    Args:
        state: Current pipeline state (must have metrics)
        eye_blocking: Whether @EYE has blocking issues

    Returns:
        APEX verdict string (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
    """
    high_stakes = state.stakes_class == StakesClass.CLASS_B

    # Populate floor_failures for audit
    if state.metrics is not None:
        floors = check_floors(
            state.metrics,
            tri_witness_required=high_stakes,
            tri_witness_threshold=0.95,
        )
        state.floor_failures = list(floors.reasons)

    # Get APEX verdict
    apex_verdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
    )

    return apex_verdict


def _run_eye_sentinel(
    state: PipelineState,
    eye_sentinel: Optional[EyeSentinel] = None,
) -> tuple[Optional[EyeReport], bool]:
    """
    Step 3 of 888: Run @EYE Sentinel audit.

    Can be disabled via ARIFOS_ENABLE_EYE=false environment variable.

    Args:
        state: Current pipeline state
        eye_sentinel: Optional @EYE Sentinel instance

    Returns:
        Tuple of (EyeReport or None, has_blocking_issue: bool)
    """
    if eye_sentinel is None or state.metrics is None:
        return (None, False)

    if os.getenv("ARIFOS_ENABLE_EYE", "true").lower() not in ("true", "1", "yes"):
        return (None, False)

    try:
        eye_report = eye_sentinel.audit(
            draft_text=state.draft_response,
            metrics=state.metrics,
            context={"stakes_class": state.stakes_class.value},
        )
        eye_blocking = eye_report.has_blocking_issue()

        # Attach blocking alerts to floor_failures
        if eye_report.has_blocking_issue():
            try:
                from .eye.base import EyeAlert
                blocking_alerts = eye_report.get_blocking_alerts()
            except Exception:
                blocking_alerts = []

            for alert in blocking_alerts:
                view_name = getattr(alert, "view_name", "UnknownView")
                message = getattr(alert, "message", "")
                state.floor_failures.append(
                    f"EYE_BLOCK[{view_name}]: {message}"
                )

        return (eye_report, eye_blocking)
    except Exception:
        # @EYE failures must not crash the pipeline
        return (None, False)


def _merge_with_waw(
    state: PipelineState,
    apex_verdict: str,
    is_refusal: bool = False,
) -> str:
    """
    Step 4 of 888: Merge W@W Federation verdict with APEX verdict.

    Can be disabled via ARIFOS_ENABLE_WAW=false or ARIFOS_DISABLE_WAW=1.

    Priority: @EYE SABAR > @WEALTH ABSOLUTE > @RIF VOID > @GEOX HOLD-888 > @WELL/@PROMPT SABAR > APEX

    Args:
        state: Current pipeline state (waw_verdict should be set)
        apex_verdict: The APEX PRIME verdict
        is_refusal: Whether the response is a clear refusal

    Returns:
        Final merged verdict string
    """
    # Check if W@W is disabled
    disable_waw = os.getenv("ARIFOS_DISABLE_WAW", "").lower() in ("1", "true", "yes")
    enable_waw = os.getenv("ARIFOS_ENABLE_WAW", "true").lower() in ("true", "1", "yes")

    if disable_waw or not enable_waw:
        return apex_verdict

    if state.waw_verdict is None:
        return apex_verdict

    final_verdict = apex_verdict

    # Merge logic (see full function in stage_888_judge for details)
    if state.waw_verdict.has_absolute_veto:
        final_verdict = "VOID"
        state.sabar_reason = "@WEALTH absolute veto (Amanah breach)"
    elif "@RIF" in state.waw_verdict.veto_organs:
        final_verdict = "VOID"
        state.sabar_reason = "@RIF epistemic veto (Truth/ΔS breach)"
    elif "@GEOX" in state.waw_verdict.veto_organs:
        final_verdict = "888_HOLD"
        state.sabar_reason = "@GEOX physics veto (reality check)"
    elif state.waw_verdict.has_veto:
        final_verdict = "SABAR"
        state.sabar_reason = f"W@W veto from: {', '.join(state.waw_verdict.veto_organs)}"
    elif state.waw_verdict.has_warn and apex_verdict == "SEAL":
        final_verdict = "PARTIAL"

    # Safe refusals override SABAR/VOID/HOLD
    high_stakes = state.stakes_class == StakesClass.CLASS_B
    if is_refusal and high_stakes and final_verdict in ("SABAR", "VOID", "888_HOLD"):
        final_verdict = "SEAL"

    return final_verdict


def _compute_floor_passed(floor_key: str, floor_def: dict, metrics: Any) -> tuple[bool, Any]:
    """
    v38.3Omega: Compute (passed, value) for a single floor from spec definition.
    
    Args:
        floor_key: Floor name (truth, delta_s, etc.)
        floor_def: Floor spec dict with threshold, operator, type
        metrics: ConstitutionalMetrics with all floor values
    
    Returns:
        (passed: bool, value: Any)
    """
    floor_type = floor_def.get("type")
    operator = floor_def.get("operator")
    
    # Boolean floors (amanah, rasa, anti_hantu)
    if floor_type in ("hard", "meta") and operator == "==":
        if floor_key == "amanah":
            return (bool(metrics.amanah), metrics.amanah)
        elif floor_key == "rasa":
            return (bool(metrics.rasa), metrics.rasa)
        elif floor_key == "anti_hantu":
            return (bool(metrics.anti_hantu), metrics.anti_hantu)
    
    # Numeric floors
    threshold = floor_def.get("threshold")
    
    if floor_key == "truth":
        passed = metrics.truth >= threshold if threshold is not None else True
        return (passed, metrics.truth)
    elif floor_key == "delta_s":
        passed = metrics.delta_s >= threshold if threshold is not None else True
        return (passed, metrics.delta_s)
    elif floor_key == "peace_squared":
        passed = metrics.peace_squared >= threshold if threshold is not None else True
        return (passed, metrics.peace_squared)
    elif floor_key == "kappa_r":
        passed = metrics.kappa_r >= threshold if threshold is not None else True
        return (passed, metrics.kappa_r)
    elif floor_key == "omega_0":
        threshold_min = floor_def.get("threshold_min", 0.03)
        threshold_max = floor_def.get("threshold_max", 0.05)
        passed = threshold_min <= metrics.omega_0 <= threshold_max
        return (passed, metrics.omega_0)
    elif floor_key == "tri_witness":
        passed = metrics.tri_witness >= threshold if threshold is not None else True
        return (passed, metrics.tri_witness)
    
    # Fallback
    return (True, None)


def _floor_margin(floor_key: str, floor_def: dict, metrics: Any) -> float:
    """
    v38.3Omega: Compute margin (distance from threshold) for numeric floors.
    Used for near-fail detection and 888_HOLD escalation.
    
    Args:
        floor_key: Floor name
        floor_def: Floor spec dict
        metrics: ConstitutionalMetrics
    
    Returns:
        margin: float (positive = surplus, negative = deficit, 0 = boolean/no threshold)
    """
    operator = floor_def.get("operator")
    
    # Boolean floors have no margin
    if operator == "==":
        return 0.0
    
    threshold = floor_def.get("threshold")
    
    if floor_key == "truth" and threshold is not None:
        return float(metrics.truth - threshold)
    elif floor_key == "delta_s" and threshold is not None:
        return float(metrics.delta_s - threshold)
    elif floor_key == "peace_squared" and threshold is not None:
        return float(metrics.peace_squared - threshold)
    elif floor_key == "kappa_r" and threshold is not None:
        return float(metrics.kappa_r - threshold)
    elif floor_key == "omega_0":
        # Omega is a band; margin is distance from edges
        threshold_min = floor_def.get("threshold_min", 0.03)
        threshold_max = floor_def.get("threshold_max", 0.05)
        if metrics.omega_0 < threshold_min:
            return float(metrics.omega_0 - threshold_min)  # negative
        elif metrics.omega_0 > threshold_max:
            return float(threshold_max - metrics.omega_0)  # negative
        else:
            # Inside band - margin is distance to nearest edge
            return float(min(metrics.omega_0 - threshold_min, threshold_max - metrics.omega_0))
    elif floor_key == "tri_witness" and threshold is not None:
        return float(metrics.tri_witness - threshold)
    
    return 0.0


def _write_memory_for_verdict(state: PipelineState) -> None:
    """
    v38: Centralized memory write for any verdict path.

    This function is called:
    1. After 888_JUDGE for normal flow
    2. After early short-circuit (e.g., 000 Amanah VOID)
    3. Any other verdict path that needs memory recording

    Respects v38 memory invariants:
    - INV-1: VOID verdicts go to VOID band only (never canonical)
    - INV-3: Every write has evidence chain

    Args:
        state: PipelineState with verdict, metrics, and memory components
    """
    if state.memory_write_policy is None or state.memory_band_router is None:
        return

    from datetime import datetime, timezone
    import json
    import hashlib

    # Build floor check evidence (v38.3Omega: spec-driven with F# + P# + stage hooks)
    floor_checks = []
    if state.metrics is not None:
        from arifos_core.metrics import _load_floors_spec_v38
        floors_spec = _load_floors_spec_v38()
        
        # Sort floors by canonical F# ID for readability (semantic order)
        floors_data = floors_spec.get("floors", {})
        sorted_floors = sorted(floors_data.items(), key=lambda x: x[1].get("id", 99))
        
        for floor_key, floor_def in sorted_floors:
            floor_id = floor_def.get("id")
            precedence = floor_def.get("precedence", 0)
            stage_hook = floor_def.get("stage_hook", "")
            
            # Compute passed + value + margin
            passed, value = _compute_floor_passed(floor_key, floor_def, state.metrics)
            margin = _floor_margin(floor_key, floor_def, state.metrics)
            
            floor_checks.append({
                "floor_id": floor_id,
                "floor": f"F{floor_id}_{floor_key.capitalize()}",
                "precedence": precedence,
                "stage_hook": stage_hook,
                "passed": passed,
                "value": value,
                "margin": margin,
            })

    timestamp = datetime.now(timezone.utc).isoformat()

    # Compute evidence hash
    state.memory_evidence_hash = compute_evidence_hash(
        floor_checks=floor_checks,
        verdict=state.verdict or "UNKNOWN",
        timestamp=timestamp,
    )

    # Build evidence chain
    evidence_chain = {
        "floor_checks": floor_checks,
        "verdict": state.verdict,
        "timestamp": timestamp,
        "job_id": state.job_id,
        "stakes_class": state.stakes_class.value,
    }
    evidence_chain["hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in evidence_chain.items() if k != "hash"}, sort_keys=True).encode()
    ).hexdigest()

    # Check write policy
    write_decision = state.memory_write_policy.should_write(
        verdict=state.verdict or "UNKNOWN",
        evidence_chain=evidence_chain,
    )

    # Route write if allowed
    if write_decision.allowed:
        content = {
            "query_hash": hashlib.sha256(state.query.encode()).hexdigest()[:16],
            "verdict": state.verdict,
            "floor_checks_summary": {
                "passed": len([f for f in floor_checks if f.get("passed")]),
                "failed": len([f for f in floor_checks if not f.get("passed")]),
            },
            "stakes_class": state.stakes_class.value,
            "timestamp": timestamp,
        }

        write_results = state.memory_band_router.route_write(
            verdict=state.verdict or "UNKNOWN",
            content=content,
            writer_id="888_JUDGE",
            evidence_hash=state.memory_evidence_hash,
            metadata={"job_id": state.job_id},
        )

        # Record in audit layer
        if state.memory_audit_layer is not None:
            for band_name, result in write_results.items():
                if result.success:
                    state.memory_audit_layer.record_memory_write(
                        band=band_name,
                        entry_data=content,
                        verdict=state.verdict,
                        evidence_hash=state.memory_evidence_hash,
                        entry_id=result.entry_id,
                        writer_id="888_JUDGE",
                        metadata={"job_id": state.job_id},
                    )


# =============================================================================
# STAGE 888 (REFACTORED)
# =============================================================================

def stage_888_judge(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
    eye_sentinel: Optional[EyeSentinel] = None,
) -> PipelineState:
    """
    888 JUDGE - Check all floors. Pass or fail?

    APEX PRIME (Ψ) renders judgment. This is the veto point.

    v38: Decomposed into 5 pluggable steps:
    1. _compute_888_metrics() - Floor metric computation
    2. _run_eye_sentinel() - @EYE audit (optional)
    3. _apply_apex_floors() - APEX PRIME floor check
    4. W@W Federation evaluation
    5. _merge_with_waw() - Verdict merging
    6. _write_memory_for_verdict() - Memory write (centralized)
    """
    state.current_stage = "888"
    state.stage_trace.append("888_JUDGE")
    state.stage_times["888"] = time.time()

    # Step 1: Compute metrics (standalone helper)
    state.metrics = _compute_888_metrics(state, compute_metrics)

    # Step 2: Detect refusals (for safe refusal handling)
    def _looks_like_refusal(text: str) -> bool:
        lowered = text.strip().lower()
        if not lowered:
            return False
        refusal_markers = [
            "i cannot ", "i can't ", "i am unable to", "i'm unable to",
            "i am not able to", "i'm not able to", "i cannot help with",
            "i can't help with", "i cannot assist", "i can't assist",
            "i cannot provide that information", "i cannot comply",
            "i can't comply", "i cannot support", "i can't support",
        ]
        return any(marker in lowered for marker in refusal_markers)

    is_refusal = _looks_like_refusal(state.draft_response)

    # Step 3: Run @EYE Sentinel audit (using decomposed helper)
    eye_report, eye_blocking = _run_eye_sentinel(state, eye_sentinel)

    # If refusal, don't let @EYE blocking force SABAR
    if is_refusal and eye_blocking:
        eye_blocking = False

    # Step 4: Apply APEX PRIME floors (using decomposed helper)
    apex_verdict = _apply_apex_floors(state, eye_blocking)

    # Step 5: W@W Federation check
    waw_federation = WAWFederationCore()
    state.waw_verdict = waw_federation.evaluate(
        output_text=state.draft_response,
        metrics=state.metrics,
        context={"stakes_class": state.stakes_class.value},
    )

    # Handle @EYE blocking SABAR reason
    if eye_blocking and apex_verdict == "SABAR":
        if state.sabar_reason is None:
            state.sabar_reason = "@EYE blocking issue (see floor_failures for details)"

    # Step 6: Merge with W@W (using decomposed helper)
    final_verdict = _merge_with_waw(state, apex_verdict, is_refusal)
    state.verdict = final_verdict

    # Check for control signals
    if state.verdict == "888_HOLD":
        state.hold_888_triggered = True
    elif state.verdict in ("VOID", "SABAR"):
        state.sabar_triggered = True
        if state.sabar_reason is None:
            state.sabar_reason = "Floor failures in 888_JUDGE"
        if not state.floor_failures and state.sabar_reason:
            state.floor_failures.append(state.sabar_reason)

    # Step 7: Write to memory (using centralized helper)
    _write_memory_for_verdict(state)

    return state


def _format_floor_failures(floor_failures: List[str]) -> str:
    """
    v38.1: Format floor failures into human-readable reasons.

    Maps technical floor names to constitutional sections.
    """
    if not floor_failures:
        return "Constitutional floors"

    friendly_reasons = []
    for fail in floor_failures:
        fail_lower = fail.lower()
        # Map technical failures to human-readable names
        if "truth" in fail_lower or "f2" in fail_lower:
            friendly_reasons.append("F2 Truth (Factual Integrity)")
        elif "peace" in fail_lower or "tox" in fail_lower or "f5" in fail_lower:
            friendly_reasons.append("F5 Peace² (Safety/Non-escalation)")
        elif "hantu" in fail_lower or "soul" in fail_lower or "conscious" in fail_lower or "f9" in fail_lower:
            friendly_reasons.append("F9 Anti-Hantu (No Soul Claims)")
        elif "amanah" in fail_lower or "integrity" in fail_lower or "f1" in fail_lower:
            friendly_reasons.append("F1 Amanah (Integrity Lock)")
        elif "empathy" in fail_lower or "kappa" in fail_lower or "f6" in fail_lower:
            friendly_reasons.append("F6 Empathy (Dignity Protection)")
        elif "delta" in fail_lower or "clarity" in fail_lower or "f4" in fail_lower:
            friendly_reasons.append("F4 Clarity (Entropy Reduction)")
        elif "omega" in fail_lower or "humility" in fail_lower or "f7" in fail_lower:
            friendly_reasons.append("F7 Humility (Uncertainty Band)")
        elif "witness" in fail_lower or "f3" in fail_lower:
            friendly_reasons.append("F3 Tri-Witness (Consensus)")
        elif "eye" in fail_lower:
            friendly_reasons.append("@EYE Sentinel (Multi-View Audit)")
        elif "wealth" in fail_lower:
            friendly_reasons.append("@WEALTH (Absolute Veto)")
        elif "rif" in fail_lower:
            friendly_reasons.append("@RIF (Epistemic Veto)")
        elif "well" in fail_lower:
            friendly_reasons.append("@WELL (Safety Organ)")
        elif "geox" in fail_lower:
            friendly_reasons.append("@GEOX (Reality Check)")
        elif "prompt" in fail_lower:
            friendly_reasons.append("@PROMPT (Language Governance)")
        else:
            friendly_reasons.append(fail)

    # Deduplicate while preserving order
    seen = set()
    unique_reasons = []
    for r in friendly_reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    return ", ".join(unique_reasons)


def stage_999_seal(state: PipelineState) -> PipelineState:
    """
    999 SEAL - If PASS -> emit. If FAIL -> SABAR or VOID.

    Final gate. All verdicts are immutably recorded.

    v38.1: Enhanced diagnostic messages for SABAR/VOID.
    v38.2-alpha: L7 Memory store with EUREKA Sieve (fail-open).
    """
    state.current_stage = "999"
    state.stage_trace.append("999_SEAL")
    state.stage_times["999"] = time.time()

    if state.verdict == "SEAL":
        state.raw_response = state.draft_response
    elif state.verdict == "PARTIAL":
        state.raw_response = (
            f"{state.draft_response}\n\n"
            "(Note: This response has been issued with constitutional hedges.)"
        )
    elif state.verdict == "888_HOLD":
        reason_str = _format_floor_failures(state.floor_failures)
        state.raw_response = (
            f"[888_HOLD] Constitutional judiciary hold.\n"
            f"Reason: {reason_str}.\n"
            f"Please clarify or rephrase your request."
        )
    elif state.verdict == "SABAR":
        # v38.1: Diagnostic SABAR with specific floor violations
        reason_str = _format_floor_failures(state.floor_failures)
        state.raw_response = (
            f"[SABAR] Stop. Protocol Active.\n"
            f"I cannot fulfill this request because it violates: {reason_str}.\n"
            f"Please rephrase to align with safety standards."
        )
    else:  # VOID
        # v38.1: Diagnostic VOID with specific floor violations
        reason_str = _format_floor_failures(state.floor_failures)
        state.raw_response = (
            f"[VOID] ACTION BLOCKED.\n"
            f"Constitutional Violation: {reason_str}."
        )

    # v38.2-alpha: L7 Memory store with EUREKA Sieve (fail-open)
    # Only store if: L7 enabled + user_id present + verdict present
    if is_l7_enabled() and state.l7_user_id and state.verdict:
        try:
            # Build content to store (query + response summary)
            content = f"Query: {state.query[:200]}... Response verdict: {state.verdict}"
            if state.raw_response:
                content += f" | Response: {state.raw_response[:300]}..."

            state.l7_store_result = _l7_store(
                content=content,
                user_id=state.l7_user_id,
                verdict=state.verdict,
                metadata={
                    "job_id": state.job_id,
                    "stakes_class": state.stakes_class.value,
                    "stage_trace": state.stage_trace,
                },
            )
        except Exception:
            # Fail-open: L7 errors don't break pipeline
            pass

    return state


# =============================================================================
# PIPELINE ORCHESTRATOR
# =============================================================================

class Pipeline:
    """
    000-999 Metabolic Pipeline Orchestrator.

    Supports Class A (fast track) and Class B (deep track) routing.

    AAA Engine Integration (v35.8.0):
    - Internally uses ARIFEngine, ADAMEngine, ApexEngine
    - Preserves all existing behavior (zero-break contract)
    - Engine packets stored in PipelineState for debugging/audit

    Usage:
        pipeline = Pipeline()
        state = pipeline.run("What is the capital of France?")
        print(state.raw_response)
    """

    def __init__(
        self,
        llm_generate: Optional[Callable[[str], str]] = None,
        compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
        scar_retriever: Optional[Callable[[str], List[Dict[str, Any]]]] = None,
        context_retriever: Optional[Callable[[str], List[Dict[str, Any]]]] = None,
        ledger_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
        eye_sentinel: Optional[EyeSentinel] = None,
        vault: Optional[Vault999] = None,
    ):
        """
        Initialize pipeline with optional integrations.

        Args:
            llm_generate: Function to generate LLM responses
            compute_metrics: Function to compute floor metrics
            scar_retriever: Function to retrieve relevant scars by query
            context_retriever: Function to retrieve relevant context
            ledger_sink: Function to log entries to cooling ledger
            eye_sentinel: Optional @EYE Sentinel auditor for 888_JUDGE
            vault: Optional Vault999 instance for constitutional memory (v37)
        """
        self.llm_generate = llm_generate
        self.compute_metrics = compute_metrics
        self.scar_retriever = scar_retriever
        self.context_retriever = context_retriever
        self.ledger_sink = ledger_sink
        self.eye_sentinel = eye_sentinel

        # v37: Vault999 for constitutional memory
        self._vault = vault

        # AAA Engines (v35.8.0 - internal facade)
        self._arif = ARIFEngine()
        self._adam = ADAMEngine()

    def run(
        self,
        query: str,
        job_id: Optional[str] = None,
        force_class: Optional[StakesClass] = None,
        job: Optional[Job] = None,
        user_id: Optional[str] = None,
    ) -> PipelineState:
        """
        Run the full 000-999 pipeline.

        Args:
            query: User input
            job_id: Optional job identifier for tracking
            force_class: Force a specific stakes class (for testing)
            job: Optional Job instance for v38 contract layer (auto-created if not provided)
            user_id: Optional user ID for L7 Memory isolation (v38.2-alpha)

        Returns:
            Final PipelineState with response and audit trail
        """
        import uuid

        # Initialize state
        state = PipelineState(
            query=query,
            job_id=job_id or str(uuid.uuid4())[:8],
        )

        if force_class:
            state.stakes_class = force_class

        # v38.2-alpha: Set user_id for L7 Memory isolation
        if user_id:
            state.l7_user_id = user_id

        # v38: Create Job from query if not provided
        if job is None:
            job = Job(
                input_text=query,
                source="pipeline",
                context="",
                action="respond",
            )

        # INHALE: 000 → 111 → 222
        # v37: Pass vault for MemoryContext initialization
        state = stage_000_void(state, vault=self._vault)

        # v38: Amanah gate - first risk checkpoint
        state, should_continue = stage_000_amanah(job, state)
        if not should_continue:
            # Early short-circuit: write memory and finalize
            _write_memory_for_verdict(state)
            state = stage_999_seal(state)
            return self._finalize(state)

        state = stage_111_sense(state)

        # Populate ARIF packet from sense results (v35.8.0)
        state.arif_packet = ARIFPacket(
            prompt=state.query,
            high_stakes_indicators=state.high_stakes_indicators.copy(),
        )

        # Check for early SABAR (entropy spike, etc.)
        if state.sabar_triggered:
            return self._finalize(state)

        # Routing decision after 111_SENSE
        if state.stakes_class == StakesClass.CLASS_A and not force_class:
            # Fast track: skip 222, go to 333 → 888 → 999
            state = stage_333_reason(state, self.llm_generate)

            # Update ARIF packet with reason results (v35.8.0)
            if state.arif_packet:
                state.arif_packet.draft = state.draft_response
                state.arif_packet.delta_s = min(0.5, len(state.draft_response) / 1000) if state.draft_response else 0.0

            state = stage_888_judge(state, self.compute_metrics, self.eye_sentinel)
            state = stage_999_seal(state)
        else:
            # Deep track: full pipeline
            state = stage_222_reflect(state, self.scar_retriever, self.context_retriever)

            # Re-check classification after scar retrieval
            if state.active_scars:
                state.stakes_class = StakesClass.CLASS_B

            # CIRCULATE: 333 → 444 → 555 → 666 → 777
            state = stage_333_reason(state, self.llm_generate)

            # Update ARIF packet with reason results (v35.8.0)
            if state.arif_packet:
                state.arif_packet.draft = state.draft_response
                state.arif_packet.delta_s = min(0.5, len(state.draft_response) / 1000) if state.draft_response else 0.0

            state = stage_444_align(state)

            # Update ARIF packet with align results (v35.8.0)
            if state.arif_packet:
                state.arif_packet.missing_fact_issue = state.missing_fact_issue
                state.arif_packet.truth_verified = not state.missing_fact_issue

            state = stage_555_empathize(state)

            # Create ADAM packet from empathize results (v35.8.0)
            state.adam_packet = ADAMPacket(
                arif_packet=state.arif_packet,
                original_draft=state.draft_response,
                softened_answer=state.draft_response,
                blame_language_issue=state.blame_language_issue,
            )
            if state.adam_packet:
                # Apply blame penalty to kappa_r if detected
                if state.blame_language_issue:
                    state.adam_packet.kappa_r = max(0.0, 0.97 - 0.25)
                else:
                    state.adam_packet.kappa_r = 0.97

            state = stage_666_bridge(state)

            # Update ADAM packet with bridge results (v35.8.0)
            if state.adam_packet:
                state.adam_packet.physical_action_issue = state.physical_action_issue
                state.adam_packet.final_text = state.draft_response

            state = stage_777_forge(state, self.llm_generate)

            # Update ADAM packet with forge results (v35.8.0)
            if state.adam_packet:
                state.adam_packet.softened_answer = state.draft_response
                state.adam_packet.final_text = state.draft_response

            # EXHALE: 888 → 999
            state = stage_888_judge(state, self.compute_metrics, self.eye_sentinel)
            state = stage_999_seal(state)

        return self._finalize(state)

    def _finalize(self, state: PipelineState) -> PipelineState:
        """Log to ledger and return final state."""
        if self.ledger_sink and state.metrics:
            entry: Dict[str, Any] = {
                "job_id": state.job_id,
                "query": state.query[:200],
                "stakes_class": state.stakes_class.value,
                "stage_trace": state.stage_trace,
                "active_scars": [s.get("id") for s in state.active_scars],
                "verdict": state.verdict,
                "sabar_triggered": state.sabar_triggered,
                "hold_888_triggered": state.hold_888_triggered,
            }
            # W@W Federation verdict (v36.3Ω)
            if state.waw_verdict is not None:
                entry["waw"] = {
                    "@WEALTH": state._get_organ_vote("@WEALTH"),
                    "@RIF": state._get_organ_vote("@RIF"),
                    "@WELL": state._get_organ_vote("@WELL"),
                    "@GEOX": state._get_organ_vote("@GEOX"),
                    "@PROMPT": state._get_organ_vote("@PROMPT"),
                    "verdict": state.waw_verdict.verdict,
                    "has_absolute_veto": state.waw_verdict.has_absolute_veto,
                    "veto_organs": state.waw_verdict.veto_organs,
                    "warn_organs": state.waw_verdict.warn_organs,
                }
            self.ledger_sink(entry)

        return state


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def run_pipeline(
    query: str,
    llm_generate: Optional[Callable[[str], str]] = None,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> PipelineState:
    """
    Convenience function to run pipeline with minimal setup.
    """
    pipeline = Pipeline(
        llm_generate=llm_generate,
        compute_metrics=compute_metrics,
    )
    return pipeline.run(query)


__all__ = [
    # Core pipeline
    "Pipeline",
    "PipelineState",
    "StakesClass",
    "run_pipeline",
    # v38 Contract layer
    "Job",
    "Stakeholder",
    "JobClass",
    # Stage functions
    "stage_000_void",
    "stage_000_amanah",
    "compute_amanah_score",
    "stage_111_sense",
    "stage_222_reflect",
    "stage_333_reason",
    "stage_444_align",
    "stage_555_empathize",
    "compute_kappa_r",
    "stage_666_bridge",
    "stage_777_forge",
    "stage_888_judge",
    "stage_999_seal",
    # v38 Decomposed helpers
    "_compute_888_metrics",
    "_apply_apex_floors",
    "_run_eye_sentinel",
    "_merge_with_waw",
    "_write_memory_for_verdict",
    # v38.2-alpha L7 Memory
    "Memory",
    "RecallResult",
    "StoreAtSealResult",
    "is_l7_enabled",
]
