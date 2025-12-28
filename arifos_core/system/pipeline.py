"""
pipeline.py - 000-999 Metabolic Pipeline for arifOS v45Ω

v45Ω EXECUTION AUTHORITY:
- Pipeline ORCHESTRATES stages but does NOT decide verdicts
- ALL verdict decisions delegated to apex_prime.apex_review()
- Pipeline stages compute metrics, detect patterns, draft responses
- Final verdict authority: apex_prime.py ONLY

Implements the constitutional metabolism with Class A/B routing:
- Class A (low-stakes/factual): Fast track 111 → 333 → 888 → 999
- Class B (high-stakes/ethical): Deep track through 222 + 555 + 777

AAA Engine Integration (v35.8.0):
- AGIEngine (Δ): sense/reason/align - cold logic, clarity
- ASIEngine (Ω): empathize/bridge - warm logic, stability
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

v45Ω Patch B.1:
- Lane-scoped Ψ enforcement (PHATIC exempt)
- Destructive intent override (REFUSE short-circuit)
- Identity truth lock (hallucination penalties)

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

# v42: apex_prime is in system/ (same dir, lowercase filename)
from .apex_prime import apex_review, ApexVerdict, check_floors, Verdict
from ..enforcement.metrics import Metrics
from ..utils.eye_sentinel import EyeSentinel, EyeReport
from ..runtime.bootstrap import ensure_bootstrap, get_bootstrap_payload
from ..audit.eye_adapter import evaluate_eye_vector
from ..organs.prompt_bridge import compute_c_budi
from ..waw.federation import WAWFederationCore, FederationVerdict
from ..sabar_timer import Sabar72Timer  # v43 Time Governor

# TEARFRAME v44 Session Physics Layer (ART)
from ..utils.session_telemetry import SessionTelemetry
from ..utils.reduction_engine import compute_attributes
from ..governance.session_physics import evaluate_physics_floors

# AAA Engines (internal facade - v35.8.0) - v42: engines is at arifos_core/engines/
from ..engines import AGIEngine, ASIEngine
from ..engines.agi_engine import AGIPacket
from ..engines.asi_engine import ASIPacket

# Memory Context (v37) - v42: memory is at arifos_core/memory/
from ..memory.memory_context import (
    MemoryContext,
    create_memory_context,
)

# v42: memory is at arifos_core/memory/, not system/memory/
from ..memory.vault999 import Vault999

# Memory Write Policy Engine (v38)
from ..memory.policy import MemoryWritePolicy
from ..memory.bands import MemoryBandRouter, append_eureka_decision
from ..memory.audit import MemoryAuditLayer, compute_evidence_hash
from ..memory.eureka_types import ActorRole, MemoryWriteRequest
from ..memory.eureka_types import Verdict as EurekaVerdict

# v38.2-alpha L7 Memory Layer (Mem0 + Qdrant)
from ..memory.memory import (
    Memory,
    RecallResult,
    StoreAtSealResult,
    recall_at_stage_111 as _l7_recall,
    store_at_stage_999 as _l7_store,
)
from ..memory.mem0_client import is_l7_enabled

# v38 Runtime Contract Layer
from ..utils.runtime_types import Job, Stakeholder, JobClass

# v38 Stage Modules - v42: stages is at arifos_core/stages/
from ..stages.stage_000_amanah import compute_amanah_score, stage_000_amanah
from ..stages.stage_555_empathy import compute_kappa_r


# =============================================================================
# PIPELINE STATE
# =============================================================================

# v44 Session Mock Store (Global Cache for Session Physics)
# In a real app, this would be Redis or a proper session service.
_SESSION_CACHE: Dict[str, SessionTelemetry] = {}


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
    applicability_lane: Optional[str] = None  # v45Ω Patch B: PHATIC/SOFT/HARD/REFUSE

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
    c_budi: Optional[float] = None
    eye_vector: Optional[Dict[str, Any]] = None
    epsilon_observed: Optional[Dict[str, float]] = None

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
    # v42: Canonical naming - AGI (Mind), ASI (Heart)
    agi_packet: Optional[AGIPacket] = None
    asi_packet: Optional[ASIPacket] = None

    # Memory Context (v37) - ONE per pipeline run
    memory_context: Optional[MemoryContext] = None

    # v38 Memory System - Write policy, routing, and audit
    memory_write_policy: Optional[MemoryWritePolicy] = None
    memory_band_router: Optional[MemoryBandRouter] = None
    memory_audit_layer: Optional[MemoryAuditLayer] = None
    memory_evidence_hash: Optional[str] = None
    eureka_store: Optional[Any] = None

    # v38.2-alpha L7 Memory Layer (Mem0 + Qdrant)
    l7_memory: Optional[Memory] = None
    l7_recall_result: Optional[RecallResult] = None
    l7_store_result: Optional[StoreAtSealResult] = None
    l7_user_id: str = ""  # User ID for memory isolation

    # v43 fail-closed: Ledger write status tracking
    ledger_write_success: bool = True

    # v45Ω Patch 3: Ledger status tracking (NORMAL, DEGRADED, CRITICAL_FAILURE)
    ledger_status: str = "NORMAL"

    # v44 Session Physics
    session_telemetry: Optional[SessionTelemetry] = None

    # v45Ω Patch B.2: LLM Call Audit Trail (Refusal Sovereignty)
    llm_called: bool = False              # Was LLM invoked?
    llm_call_count: int = 0               # How many times?
    llm_call_stages: List[str] = field(default_factory=list)  # Which stages?
    audit_receipt: Optional[AuditReceipt] = None  # Governance proof

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
# v45Ω Patch B.2: AUDIT & SAFETY STRUCTURES
# =============================================================================


@dataclass
class AuditReceipt:
    """
    v45Ω Patch B.2: Audit receipt proving governance execution.

    Provides cryptographic-grade proof of:
    - Whether LLM was invoked (refusal sovereignty)
    - Which gates/stages were executed
    - Final verdict and floor results
    """

    job_id: str
    timestamp: float

    # Lane & Classification
    lane: str  # PHATIC/SOFT/HARD/REFUSE
    stakes_class: str  # CLASS_A/CLASS_B

    # LLM Audit Trail (CRITICAL for Refusal Sovereignty)
    llm_called: bool  # Sovereignty proof
    llm_call_count: int  # How many invocations
    llm_call_stages: List[str]  # Which stages (e.g., ["333_REASON"])

    # Verdict
    verdict: str  # SEAL/VOID/PARTIAL/SABAR/HOLD_888
    floor_failures: List[str]  # Which floors failed

    # Execution trace
    stage_trace: List[str]  # Pipeline stages executed
    execution_time_ms: float  # Total time

    # Optional
    high_stakes_indicators: List[str] = field(default_factory=list)
    refusal_reason: Optional[str] = None  # If REFUSE lane


@dataclass
class SafetyDecision:
    """
    v45Ω Patch B.2: Safety classification (STUB - minimal implementation).

    Future: Full intent taxonomy with category enums.
    Current: Just captures high-stakes flag for compatibility.
    """

    is_high_stakes: bool
    indicators: List[str]
    lane_override: Optional[str] = None  # Force REFUSE if needed

    # Future fields (not implemented yet):
    # category: IntentCategory
    # tier_required: Tier  # T1-T4
    # forced_before_llm: bool


# =============================================================================
# STAGE INSPECTOR (v45Ω Patch B.2)
# =============================================================================


def _is_stage_inspector_enabled() -> bool:
    """Check if verbose stage logging is enabled via ARIFOS_VERBOSE env var."""
    return os.getenv("ARIFOS_VERBOSE", "").lower() in ("1", "true", "yes")


def _log_stage_transition(
    stage_name: str,
    state: PipelineState,
    start_time: Optional[float] = None,
) -> None:
    """
    Log stage transition with duration and ΔS (delta-entropy).

    v45Ω Patch B.2: Metabolic transparency for 000→999 pipeline.

    Args:
        stage_name: Stage identifier (e.g., "000_VOID", "333_REASON")
        state: Current pipeline state
        start_time: Stage start time (if provided, computes duration)
    """
    if not _is_stage_inspector_enabled():
        return

    # Compute duration if start_time provided
    duration_ms = 0.0
    if start_time is not None:
        duration_ms = (time.time() - start_time) * 1000

    # Estimate ΔS (entropy change) from draft response length
    # Simple heuristic: longer responses have higher entropy
    delta_s = 0.0
    if hasattr(state, "draft_response") and state.draft_response:
        # Normalized by 1000 chars (arbitrary scaling)
        delta_s = len(state.draft_response) / 1000.0

    # Format log message
    log_parts = [f"[StageInspector] {stage_name}"]
    if duration_ms > 0:
        log_parts.append(f"duration={duration_ms:.1f}ms")
    if delta_s > 0:
        log_parts.append(f"ΔS={delta_s:.3f}")

    # Log lane if available
    if hasattr(state, "applicability_lane") and state.applicability_lane:
        log_parts.append(f"lane={state.applicability_lane}")

    print(" | ".join(log_parts))


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


def _detect_destructive_intent(query: str) -> bool:
    """
    Detect destruction + critical target combinations.

    v45Ω Patch B.1: Arson/infrastructure attack detection.
    v45Ω Patch B.2: Weapons manufacturing detection (no target required).
    Conservative false positive (refusal) is safer than false negative.

    Returns:
        True if:
        - Query contains weapons manufacturing keywords (e.g., "make bomb"), OR
        - Query contains destruction keyword AND critical target
    """
    q = query.lower()

    # v45Ω Patch B.2: Weapons manufacturing - refuse regardless of target
    weapons_manufacturing = [
        "make bomb",
        "build bomb",
        "create bomb",
        "assemble bomb",
        "buat bom",  # make bomb (Malay)
        "rakit bom",  # assemble bomb (Malay)
        "cara buat bom",  # how to make bomb (Malay)
        "macam mana nak buat bom",  # how to make bomb (Malay)
        "how to make bomb",
        "how to build bomb",
        "how to create bomb",
    ]

    # Check weapons manufacturing - refuse immediately
    if any(kw in q for kw in weapons_manufacturing):
        return True

    destruction_keywords = [
        # English
        "burn",
        "arson",
        "set fire",
        "torch",
        "ignite",
        "destroy",
        "demolish",
        "blow up",
        "detonate",
        # Malay/Indonesian (SEA-LION support)
        "bakar",  # burn
        "membakar",  # burning
        "musnahkan",  # destroy
        "hancurkan",  # demolish
        "letupkan",  # detonate
        "meletup",  # explode
        "ledak",  # explode
    ]

    critical_targets = [
        "klcc",
        "petronas",
        "twin towers",
        "tower",
        "building",
        "mall",
        "airport",
        "hospital",
        "school",
        "mosque",
        "church",
        "temple",
        "government",
        "embassy",
    ]

    has_destruction = any(kw in q for kw in destruction_keywords)
    has_critical_target = any(tgt in q for tgt in critical_targets)

    return has_destruction and has_critical_target


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
        "kill",
        "harm",
        "suicide",
        "bomb",
        "weapon",
        "illegal",
        "hack",
        "exploit",
        "steal",
        "medical",
        "legal",
        "financial advice",
        "confidential",
        "secret",
        "classified",
        "should i",
        "is it ethical",
        "morally",
        # v45Ω Patch B.1: Arson & destruction patterns (English)
        "burn",
        "arson",
        "set fire",
        "torch",
        "ignite",
        "flame",
        "destroy",
        "demolish",
        "blow up",
        "detonate",
        "explode",
        "damage infrastructure",
        "sabotage",
        "attack building",
        # v45Ω Patch B.1: Malay/Indonesian (SEA-LION support)
        "bakar",
        "membakar",
        "musnahkan",
        "hancurkan",
        "letupkan",
        "meletup",
        "bunuh",  # kill
        "bahaya",  # danger
        # v45Ω Patch B.2: Weapons (Malay/Indonesian)
        "bom",  # bomb
        "peluru",  # bullet
        "senjata",  # weapon
        "pisau",  # knife
        "racun",  # poison
        "bahan letupan",  # explosives
    ]

    query_lower = state.query.lower()
    for pattern in HIGH_STAKES_PATTERNS:
        if pattern in query_lower:
            state.high_stakes_indicators.append(pattern)

    # Classify based on indicators
    if state.high_stakes_indicators:
        state.stakes_class = StakesClass.CLASS_B

    # v45Ω Patch B: Classify prompt lane for context-aware truth routing
    from ..routing.prompt_router import classify_prompt_lane, ApplicabilityLane
    from ..routing.refusal_templates import generate_refusal_response

    lane = classify_prompt_lane(state.query, state.high_stakes_indicators)

    # v45Ω Patch B.1: Destructive intent override
    # Force REFUSE lane for destruction + critical target combinations
    if _detect_destructive_intent(state.query):
        lane = ApplicabilityLane.REFUSE
        state.high_stakes_indicators.append("destructive_intent")

    state.applicability_lane = lane.value

    # Handle REFUSE lane immediately (skip LLM for safety)
    if lane == ApplicabilityLane.REFUSE:
        state.draft_response = generate_refusal_response(state.query, "safety")

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
                    state.context_blocks.append(
                        {
                            "type": "l7_memory",
                            "text": mem.content,
                            "score": mem.score,
                            "memory_id": mem.memory_id,
                            "caveat": "Recalled memory (suggestion, not fact)",
                        }
                    )
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

    AGI (Δ) takes over - pure logic, pattern detection.
    """
    stage_start = time.time()  # v45Ω Patch B.2: Track for StageInspector
    state.current_stage = "333"
    state.stage_trace.append("333_REASON")
    state.stage_times["333"] = stage_start

    # v45Ω Patch B.1: Skip LLM if REFUSE lane already drafted refusal
    # Constitutional floor: Destructive queries bypass LLM generation (F1 Amanah)
    if state.applicability_lane == "REFUSE" and state.draft_response:
        # Refusal already drafted in stage_111 - do NOT call LLM
        return state

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
        # v45Ω Patch B.2: Check if llm_generate supports lane metadata (governed version)
        import inspect
        sig = inspect.signature(llm_generate)

        if "lane" in sig.parameters:
            # Governed version - pass lane metadata and capture metadata
            response, metadata = llm_generate(
                "\n".join(prompt_parts),
                lane=state.applicability_lane or "UNKNOWN"
            )
            state.draft_response = response
            state.sealion_metadata = metadata  # Store for 888_JUDGE
            # v45Ω Patch C: Store failover metadata if present
            if metadata and isinstance(metadata, dict):
                state.failover_metadata = metadata
        else:
            # Legacy version - plain text only
            state.draft_response = llm_generate("\n".join(prompt_parts))

        # v45Ω Patch B.2: Track LLM call
        state.llm_called = True
        state.llm_call_count += 1
        state.llm_call_stages.append("333_REASON")
    else:
        # Stub: echo query
        state.draft_response = f"[333_REASON] Structured response for: {state.query}"

    # v45Ω Patch B.2: Log stage transition
    _log_stage_transition("333_REASON", state, start_time=stage_start)

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

    ASI (Ω) takes over - empathy, dignity, de-escalation.
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

    # v45Ω Patch B.2: Skip LLM if REFUSE lane already drafted refusal
    # REFUSE lane: Queries bypass LLM generation per safety protocol (F1 Amanah)
    if state.applicability_lane == "REFUSE" and state.draft_response:
        # Refusal already drafted in stage_111 - do NOT call LLM
        return state

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

            # v45Ω Patch B.2: Track LLM call
            state.llm_called = True
            state.llm_call_count += 1
            state.llm_call_stages.append("777_FORGE")
        else:
            state.draft_response = f"[777_FORGE] Empathic refinement: {state.draft_response}"

    return state


# =============================================================================
# v38 DECOMPOSED 888 HELPERS
# =============================================================================


def _compute_888_metrics(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> Optional[Metrics]:
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
        try:
            metrics = compute_metrics(
                state.query,
                state.draft_response,
                {
                    "stakes_class": state.stakes_class.value,
                    "lane": state.applicability_lane,  # v45Ω Patch B
                },
            )
        except Exception as e:
            # FAIL-CLOSED v43: Metrics computation failure → return None
            # Will be caught in _apply_apex_floors() and turned into explicit VOID
            import logging

            logging.getLogger(__name__).info(
                f"Metrics computation encountered issue ({e}). Defaulting to VOID as per fail-closed protocol."
            )
            return None  # Signal failure to caller
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

    # ==========================================================================
    # v45Ω PATCH 2: Apply truth grounding with evidence validation
    # Only apply to stub metrics; respect callback-provided metrics as authoritative
    # ==========================================================================
    if not compute_metrics:  # Only ground truth for stub metrics
        from ..enforcement.metrics import ground_truth_score

        grounded_truth = ground_truth_score(
            query=state.query,
            response=state.draft_response,
            base_truth_score=metrics.truth,
        )
        metrics.truth = grounded_truth
    # ==========================================================================

    return metrics


def _apply_apex_floors(
    state: PipelineState,
    eye_blocking: bool = False,
) -> ApexVerdict:
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
    # Ensure metrics exist before passing (should always be set by stage 444)
    # FAIL-CLOSED v43: Explicit VOID if metrics missing
    if state.metrics is None:
        import logging

        logging.getLogger(__name__).error(
            "Metrics are None at APEX floor check. Returning explicit VOID (fail-closed)."
        )
        return ApexVerdict(
            verdict=Verdict.VOID,
            pulse=0.0,
            reason="Metrics computation failed - refusing for safety (fail-closed)",
            floors=None,
        )

    # v45Ω Patch B.2: Recompute Psi with lane-aware threshold
    # Metrics.psi was computed in __post_init__ without lane context
    # Recompute now that lane is classified
    lane = state.applicability_lane if state.applicability_lane else "UNKNOWN"
    state.metrics.psi = state.metrics.compute_psi(
        tri_witness_required=high_stakes,
        lane=lane,
    )

    # v45Ω TRM: Pass prompt, category, and response for context-aware routing
    # Extract category from query or use "UNKNOWN"
    category = getattr(state, "category", "UNKNOWN")
    prompt = getattr(state, "query", "")
    response_text = getattr(state, "draft_response", "")

    apex_verdict: ApexVerdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
        prompt=prompt,
        category=category,
        response_text=response_text,
        lane=lane,  # v45Ω Patch B
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
                state.floor_failures.append(f"EYE_BLOCK[{view_name}]: {message}")

        return (eye_report, eye_blocking)
    except Exception as e:
        # FAIL-CLOSED v43: @EYE failure → assume BLOCKING (safety first)
        import logging

        logging.getLogger(__name__).info(
            f"@EYE audit incomplete ({e}). Applying fail-closed stance per F1 Amanah protocol."
        )
        eye_report = None
        eye_blocking = True  # F1 Amanah: Fail-closed stance on incomplete audit

    # v42.1 adapter: evaluate drift/dignity using spec hooks
    try:
        c_budi = compute_c_budi(state.query, state.draft_response or "")
        bootstrap = get_bootstrap_payload()
        epsilon_map = bootstrap.get("epsilon_map", {})
        adapter_result = evaluate_eye_vector(
            metrics=state.metrics,
            c_budi=c_budi,
            epsilon_map_override=epsilon_map,
            amanah=bool(getattr(state.metrics, "amanah", False)),
            psi_value=getattr(state.metrics, "psi", None),
        )
        # Attach reasons to floor failures
        for reason in adapter_result.reasons:
            state.floor_failures.append(f"EYE_ADAPTER:{reason}")
        # Blocking if action requests SABAR/VOID/HOLD-888
        if adapter_result.action in ("SABAR", "VOID", "HOLD-888"):
            eye_blocking = True
        # Store eye_vector for ledger
        state.eye_vector = {
            "level": adapter_result.level,
            "action": adapter_result.action,
            "reasons": adapter_result.reasons,
            "payload": adapter_result.payload,
        }
        # Propagate c_budi for ledger enrichment
        state.c_budi = c_budi
    except Exception as e:
        # FAIL-CLOSED v43: @EYE adapter failure → assume BLOCKING
        import logging

        logging.getLogger(__name__).info(
            f"@EYE adapter evaluation incomplete ({e}). Applying fail-closed stance per F1 Amanah protocol."
        )
        eye_blocking = True  # F1 Amanah: Fail-closed stance on adapter issue

    return (eye_report, eye_blocking)


def _merge_with_waw(
    state: PipelineState,
    apex_verdict: ApexVerdict,
    is_refusal: bool = False,
) -> ApexVerdict:
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

    final_verdict: ApexVerdict = apex_verdict

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


def _map_verdict_to_eureka(verdict: Optional[ApexVerdict]) -> EurekaVerdict:
    """Map pipeline verdicts to EUREKA verdict enum with safe fallback."""
    if verdict is None:
        return EurekaVerdict.VOID

    value = getattr(verdict, "value", None) or str(verdict)
    value = str(value)

    if value == "888_HOLD":
        return EurekaVerdict.HOLD_888
    if value == "SABAR_EXTENDED":
        return EurekaVerdict.SABAR_EXTENDED
    try:
        return EurekaVerdict(value)  # type: ignore[arg-type]
    except ValueError:
        return EurekaVerdict.VOID


def _write_memory_for_verdict(
    state: PipelineState,
    actor_role: ActorRole = ActorRole.JUDICIARY,
    human_seal: bool = False,
    eureka_store: Optional[Any] = None,
) -> None:
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
        from arifos_core.enforcement.metrics import _load_floors_spec_v38

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

            floor_checks.append(
                {
                    "floor_id": floor_id,
                    "floor": f"F{floor_id}_{floor_key.capitalize()}",
                    "precedence": precedence,
                    "stage_hook": stage_hook,
                    "passed": passed,
                    "value": value,
                    "margin": margin,
                }
            )

    timestamp = datetime.now(timezone.utc).isoformat()

    # v42: Normalize verdict to string upstream before any serialization
    # ApexVerdict → verdict.value, Verdict Enum → value, else str()
    if state.verdict is None:
        verdict_str = "UNKNOWN"
    elif hasattr(state.verdict, "verdict") and hasattr(state.verdict.verdict, "value"):
        verdict_str = state.verdict.verdict.value  # ApexVerdict
    elif hasattr(state.verdict, "value"):
        verdict_str = state.verdict.value  # Verdict Enum
    else:
        verdict_str = str(state.verdict)

    # Compute evidence hash
    state.memory_evidence_hash = compute_evidence_hash(
        floor_checks=floor_checks,
        verdict=verdict_str,
        timestamp=timestamp,
    )

    # Build evidence chain
    evidence_chain = {
        "floor_checks": floor_checks,
        "verdict": verdict_str,
        "timestamp": timestamp,
        "job_id": state.job_id,
        "stakes_class": state.stakes_class.value,
    }
    evidence_chain["hash"] = hashlib.sha256(
        json.dumps(
            {k: v for k, v in evidence_chain.items() if k != "hash"}, sort_keys=True
        ).encode()
    ).hexdigest()

    # Phase-2: route via EUREKA policy adapter + router (drop TOOL writes)
    eureka_decision_allowed = True
    if hasattr(state.memory_write_policy, "policy_route_write"):
        eureka_request = MemoryWriteRequest(
            actor_role=actor_role,
            verdict=_map_verdict_to_eureka(state.verdict),
            reason="pipeline_memory_write",
            content={
                "job_id": state.job_id,
                "stakes_class": state.stakes_class.value,
                "verdict": verdict_str,  # v42: use string for JSON serialization
            },
            human_seal=human_seal,
        )
        eureka_decision = state.memory_write_policy.policy_route_write(eureka_request)
        eureka_decision_allowed = eureka_decision.allowed
        if eureka_decision.allowed:
            append_eureka_decision(eureka_decision, eureka_request, store=eureka_store)

    # Check write policy
    write_decision = state.memory_write_policy.should_write(
        verdict=verdict_str,
        evidence_chain=evidence_chain,
    )

    # Route write if allowed (and EUREKA routing did not DROP)
    if write_decision.allowed and eureka_decision_allowed:
        content = {
            "query_hash": hashlib.sha256(state.query.encode()).hexdigest()[:16],
            "verdict": verdict_str,  # v42: use string for JSON serialization
            "floor_checks_summary": {
                "passed": len([f for f in floor_checks if f.get("passed")]),
                "failed": len([f for f in floor_checks if not f.get("passed")]),
            },
            "stakes_class": state.stakes_class.value,
            "timestamp": timestamp,
        }

        try:
            write_results = state.memory_band_router.route_write(
                verdict=verdict_str,
                content=content,
                writer_id="888_JUDGE",
                evidence_hash=state.memory_evidence_hash,
                metadata={"job_id": state.job_id},
            )

            # FAIL-CLOSED v43: Check if any write failed
            write_success = False
            for band_name, result in write_results.items():
                if result.success:
                    write_success = True
                    # Record in audit layer
                    if state.memory_audit_layer is not None:
                        state.memory_audit_layer.record_memory_write(
                            band=band_name,
                            entry_data=content,
                            verdict=verdict_str,  # v42: use string for serialization
                            evidence_hash=state.memory_evidence_hash,
                            entry_id=result.entry_id,
                            writer_id="888_JUDGE",
                            metadata={"job_id": state.job_id},
                        )

            # Store ledger write status for 999_SEAL check
            state.ledger_write_success = write_success

        except Exception as e:
            # =================================================================
            # v45Ω PATCH 3: RESILIENT LEDGER I/O
            # =================================================================
            # When primary ledger fails, write emergency fallback and mark
            # as DEGRADED instead of immediately failing closed to VOID.
            # This separates "audit degradation" from "truth violation".
            # =================================================================
            import logging
            import json
            from pathlib import Path
            from datetime import datetime

            logger = logging.getLogger(__name__)
            logger.error(f"Primary ledger write failed. Error: {e}")

            # Attempt emergency fallback ledger write
            try:
                emergency_log_path = Path("vault_999") / "ledger" / "emergency_fallback.jsonl"
                emergency_log_path.parent.mkdir(parents=True, exist_ok=True)

                # Create emergency log entry with json.dumps(default=str) for enum handling
                emergency_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "job_id": state.job_id,
                    "verdict": verdict_str,
                    "query_hash": hashlib.sha256(state.query.encode()).hexdigest()[:16],
                    "stakes_class": state.stakes_class.value,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "ledger_status": "DEGRADED",
                }

                # Use default=str to handle enums and other non-serializable types
                with emergency_log_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(emergency_entry, default=str) + "\n")

                logger.warning(
                    f"Emergency fallback ledger write succeeded for job {state.job_id}. "
                    f"Ledger status: DEGRADED. Check {emergency_log_path}"
                )

                # Mark as degraded but not failed (unless high-stakes)
                state.ledger_write_success = state.stakes_class != StakesClass.CLASS_B
                state.ledger_status = "DEGRADED"  # Track degradation separately

            except Exception as fallback_error:
                # Even fallback failed - this is critical
                logger.error(
                    f"Ledger write sequence incomplete. Primary: {e}. Secondary: {fallback_error}. "
                    f"Audit trail preserved in memory cache."
                )
                state.ledger_write_success = False
                state.ledger_status = "CRITICAL_FAILURE"
            # =================================================================
            # END PATCH 3: Resilient ledger I/O
            # =================================================================
    else:
        # Write not allowed by policy
        state.ledger_write_success = True  # Policy decision, not a failure


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
    stage_start = time.time()  # v45Ω Patch B.2: Track for StageInspector
    state.current_stage = "888"
    state.stage_trace.append("888_JUDGE")
    state.stage_times["888"] = stage_start

    # Step 1: Compute metrics (standalone helper)
    state.metrics = _compute_888_metrics(state, compute_metrics)
    # v42.1: compute epsilon observed placeholder using epsilon_map keys
    try:
        epsilon_map = get_bootstrap_payload().get("epsilon_map", {})
        eps_obs: Dict[str, float] = {}
        if state.metrics and epsilon_map:
            for key in epsilon_map.keys():
                metric_val = getattr(state.metrics, key.lower(), None)
                if metric_val is not None:
                    eps_obs[key] = abs(float(metric_val))
        state.epsilon_observed = eps_obs
    except Exception:
        state.epsilon_observed = None

    # Step 2: Detect refusals (for safe refusal handling)
    def _looks_like_refusal(text: str) -> bool:
        lowered = text.strip().lower()
        if not lowered:
            return False
        refusal_markers = [
            "i cannot ",
            "i can't ",
            "i am unable to",
            "i'm unable to",
            "i am not able to",
            "i'm not able to",
            "i cannot help with",
            "i can't help with",
            "i cannot assist",
            "i can't assist",
            "i cannot provide that information",
            "i cannot comply",
            "i can't comply",
            "i cannot support",
            "i can't support",
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
    final_verdict: ApexVerdict = _merge_with_waw(state, apex_verdict, is_refusal)
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
    _write_memory_for_verdict(
        state, actor_role=ActorRole.JUDICIARY, human_seal=False, eureka_store=state.eureka_store
    )

    # v45Ω Patch B.2: Log stage transition with verdict
    _log_stage_transition("888_JUDGE", state, start_time=stage_start)

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
        elif (
            "hantu" in fail_lower
            or "soul" in fail_lower
            or "conscious" in fail_lower
            or "f9" in fail_lower
        ):
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
    v43: FAIL-CLOSED - blocks SEAL if ledger write failed.
    """
    state.current_stage = "999"
    state.stage_trace.append("999_SEAL")
    state.stage_times["999"] = time.time()

    # SABAR-72 v43: Time Governor - Check for active cooling hold
    sabar_timer = Sabar72Timer()
    if sabar_timer.is_blocked(state.job_id):
        ticket = sabar_timer.get_ticket(state.job_id)
        import logging

        logging.getLogger(__name__).warning(
            f"SABAR-72 enforced for job {state.job_id}. "
            f"Reason: {ticket.reason.value if ticket else 'unknown'}. "
            f"Cooling period: {ticket.hours_remaining():.1f}h remaining."
        )
        state.verdict = "SABAR"
        state.floor_failures.append(
            f"SABAR_72_ACTIVE: {ticket.reason.value} ({ticket.hours_remaining():.1f}h remaining)"
        )
        state.sabar_reason = (
            f"Constitutional cooling period (72h) enforced. "
            f"Reason: {ticket.reason.value}. Time remaining: {ticket.hours_remaining():.1f} hours. "
            f"Human authority override required to proceed before expiry."
        )

    # ==========================================================================
    # v45Ω PATCH 3 (continued): Conditional fail-closed based on stakes
    # ==========================================================================
    # FAIL-CLOSED v43 (amended v45): Block SEAL emission if ledger write failed
    # BUT: Separate "audit degradation" from "truth violation"
    # - High-stakes (CLASS_B): Still fail-closed to VOID
    # - Low-stakes: Allow DEGRADED status with warning
    # ==========================================================================
    if not getattr(state, "ledger_write_success", True):
        ledger_status = getattr(state, "ledger_status", "UNKNOWN")
        import logging

        # Check if this is a high-stakes query
        is_high_stakes = state.stakes_class == StakesClass.CLASS_B

        if is_high_stakes or ledger_status == "CRITICAL_FAILURE":
            # High-stakes OR critical failure → hard fail-closed to VOID
            logging.getLogger(__name__).info(
                f"Audit trail preservation incomplete (status: {ledger_status}). "
                f"Transitioning to VOID per high-stakes protocol. Query preserved in memory."
            )
            state.verdict = "VOID"
            # Add to floor_failures for transparency
            state.floor_failures.append("LEDGER_WRITE_FAILED (fail-closed enforcement)")
            state.sabar_reason = (
                "Ledger write failure on high-stakes query - "
                "cannot emit governed output without audit trail"
            )
        else:
            # Low-stakes with DEGRADED ledger → allow with warning
            logging.getLogger(__name__).warning(
                f"Ledger write degraded for LOW-STAKES job {state.job_id}. "
                f"Verdict {state.verdict} allowed with audit degradation warning. "
                f"Ledger status: {ledger_status}"
            )
            # Downgrade SEAL to PARTIAL if ledger is degraded
            if state.verdict == "SEAL":
                state.verdict = "PARTIAL"
                state.floor_failures.append(
                    f"LEDGER_DEGRADED (emergency fallback active, status: {ledger_status})"
                )
    # ==========================================================================
    # END PATCH 3: Conditional fail-closed
    # ==========================================================================

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
        state.raw_response = f"[VOID] ACTION BLOCKED.\nConstitutional Violation: {reason_str}."

    # Phase-2: route memory at seal stage (actor = ENGINE)
    _write_memory_for_verdict(
        state, actor_role=ActorRole.ENGINE, human_seal=False, eureka_store=state.eureka_store
    )

    # v38.2-alpha: L7 Memory store with EUREKA Sieve (fail-open)
    # Only store if: L7 enabled + user_id present + verdict present
    if is_l7_enabled() and state.l7_user_id and state.verdict:
        try:
            # v42: Normalize verdict to string upstream
            if hasattr(state.verdict, "verdict") and hasattr(state.verdict.verdict, "value"):
                verdict_str_l7 = state.verdict.verdict.value  # ApexVerdict
            elif hasattr(state.verdict, "value"):
                verdict_str_l7 = state.verdict.value  # Verdict Enum
            else:
                verdict_str_l7 = str(state.verdict)
            # Build content to store (query + response summary)
            content = f"Query: {state.query[:200]}... Response verdict: {verdict_str_l7}"
            if state.raw_response:
                content += f" | Response: {state.raw_response[:300]}..."

            state.l7_store_result = _l7_store(
                content=content,
                user_id=state.l7_user_id,
                verdict=verdict_str_l7,  # v42: use string
                metadata={
                    "job_id": state.job_id,
                    "stakes_class": state.stakes_class.value,
                    "stage_trace": state.stage_trace,
                },
            )
        except Exception:
            # Fail-open: L7 errors don't break pipeline
            pass

    # v45Ω Patch B.2: Generate audit receipt
    # Extract verdict string safely
    if state.verdict:
        if hasattr(state.verdict, "verdict") and hasattr(state.verdict.verdict, "value"):
            verdict_str = state.verdict.verdict.value  # ApexVerdict
        elif hasattr(state.verdict, "value"):
            verdict_str = state.verdict.value  # Verdict Enum
        else:
            verdict_str = str(state.verdict)
    else:
        verdict_str = "UNKNOWN"

    state.audit_receipt = AuditReceipt(
        job_id=state.job_id,
        timestamp=time.time(),
        lane=state.applicability_lane or "UNKNOWN",
        stakes_class=state.stakes_class.name,  # Use .name for "CLASS_A" not "A"
        llm_called=state.llm_called,
        llm_call_count=state.llm_call_count,
        llm_call_stages=state.llm_call_stages,
        verdict=verdict_str,
        floor_failures=state.floor_failures,
        stage_trace=state.stage_trace,
        execution_time_ms=(time.time() - state.start_time) * 1000,
        high_stakes_indicators=state.high_stakes_indicators,
        refusal_reason=state.sabar_reason if state.applicability_lane == "REFUSE" else None,
    )

    return state


# =============================================================================
# PIPELINE ORCHESTRATOR
# =============================================================================


class Pipeline:
    """
    000-999 Metabolic Pipeline Orchestrator.

    Supports Class A (fast track) and Class B (deep track) routing.

    AAA Engine Integration (v35.8.0):
    - Internally uses AGIEngine, ASIEngine, ApexEngine
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
        # v45Ω Patch C: Failover integration (opt-in, disabled by default)
        if os.getenv("ARIFOS_FAILOVER_ENABLED", "").lower() == "true":
            try:
                import logging
                logger = logging.getLogger(__name__)
                from ..connectors.failover_orchestrator import (
                    load_failover_config_from_env,
                    create_governed_failover_backend
                )
                config = load_failover_config_from_env()
                self.llm_generate = create_governed_failover_backend(
                    config=config,
                    ledger_sink=ledger_sink
                )
                logger.info(f"[PIPELINE] Failover enabled with {len(config.providers)} providers")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"[PIPELINE] Failover init failed: {e}. Using single provider.")
                self.llm_generate = llm_generate
        else:
            self.llm_generate = llm_generate  # Existing behavior (no change)

        self.compute_metrics = compute_metrics
        self.scar_retriever = scar_retriever
        self.context_retriever = context_retriever
        self.ledger_sink = ledger_sink
        self.eye_sentinel = eye_sentinel
        # v42.1: bootstrap spec binding (fail-open raises to caller)
        try:
            self.bootstrap_payload = ensure_bootstrap()
        except Exception:
            # surface error; caller may wrap to VOID semantics
            self.bootstrap_payload = {}

        # v37: Vault999 for constitutional memory
        self._vault = vault

        # AAA Engines (v35.8.0 - internal facade)
        self._agi = AGIEngine()
        self._asi = ASIEngine()

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

        # v44 TEARFRAME: Initialize Session Telemetry & Start Turn
        # Use user_id -> job_id -> default as session key
        session_key = user_id or job_id or "anonymous_session"
        if session_key not in _SESSION_CACHE:
            _SESSION_CACHE[session_key] = SessionTelemetry()

        telemetry = _SESSION_CACHE[session_key]
        state.session_telemetry = telemetry

        # Start turn (T)
        tokens_in_approx = len(query) // 4
        telemetry.start_turn(
            tokens_in=tokens_in_approx,
            temperature=0.7,  # Default standard
            top_p=0.9,
            top_k=40,
        )

        # INHALE: 000 → 111 → 222

        # v37: Pass vault for MemoryContext initialization
        state = stage_000_void(state, vault=self._vault)

        # v38: Amanah gate - first risk checkpoint
        state, should_continue = stage_000_amanah(job, state)
        if not should_continue:
            # Early short-circuit: write memory and finalize
            _write_memory_for_verdict(
                state,
                actor_role=ActorRole.JUDICIARY,
                human_seal=False,
                eureka_store=state.eureka_store,
            )
            state = stage_999_seal(state)
            return self._finalize(state)

        state = stage_111_sense(state)

        # Populate AGI packet from sense results (v35.8.0)
        state.agi_packet = AGIPacket(
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

            # Update AGI packet with reason results (v35.8.0)
            if state.agi_packet:
                state.agi_packet.draft = state.draft_response
                state.agi_packet.delta_s = (
                    min(0.5, len(state.draft_response) / 1000) if state.draft_response else 0.0
                )

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

            # Update AGI packet with reason results (v35.8.0)
            if state.agi_packet:
                state.agi_packet.draft = state.draft_response
                state.agi_packet.delta_s = (
                    min(0.5, len(state.draft_response) / 1000) if state.draft_response else 0.0
                )

            state = stage_444_align(state)

            # Update AGI packet with align results (v35.8.0)
            if state.agi_packet:
                state.agi_packet.missing_fact_issue = state.missing_fact_issue
                state.agi_packet.truth_verified = not state.missing_fact_issue

            state = stage_555_empathize(state)

            # Create ASI packet from empathize results (v35.8.0)
            state.asi_packet = ASIPacket(
                agi_packet=state.agi_packet,
                original_draft=state.draft_response,
                softened_answer=state.draft_response,
                blame_language_issue=state.blame_language_issue,
            )
            if state.asi_packet:
                # Apply blame penalty to kappa_r if detected
                if state.blame_language_issue:
                    state.asi_packet.kappa_r = max(0.0, 0.97 - 0.25)
                else:
                    state.asi_packet.kappa_r = 0.97

            state = stage_666_bridge(state)

            # Update ASI packet with bridge results (v35.8.0)
            if state.asi_packet:
                state.asi_packet.physical_action_issue = state.physical_action_issue
                state.asi_packet.final_text = state.draft_response

            state = stage_777_forge(state, self.llm_generate)

            # Update ASI packet with forge results (v35.8.0)
            if state.asi_packet:
                state.asi_packet.softened_answer = state.draft_response
                state.asi_packet.final_text = state.draft_response

            # EXHALE: 888 → 999
            state = stage_888_judge(state, self.compute_metrics, self.eye_sentinel)
            state = stage_999_seal(state)

        return self._finalize(state)

    def _finalize(self, state: PipelineState) -> PipelineState:
        """Log to ledger and return final state."""

        physics_snapshot = None

        # v44 TEARFRAME: End Turn & Apply Physics Floors (A -> F -> Ψ)
        if state.session_telemetry:
            try:
                # 1. Capture output physics
                resp_text = state.raw_response or state.draft_response or ""
                tokens_out_approx = len(resp_text) // 4

                # Resolve current verdict to Enum or string
                current_verdict_val = "void"
                if state.verdict:
                    if hasattr(state.verdict, "verdict") and hasattr(
                        state.verdict.verdict, "value"
                    ):
                        current_verdict_val = state.verdict.verdict.value
                    elif hasattr(state.verdict, "value"):
                        current_verdict_val = state.verdict.value
                    else:
                        current_verdict_val = str(state.verdict)

                # Safe conversion to Verdict Enum
                try:
                    v_enum = Verdict.from_string(current_verdict_val.upper())
                except Exception:
                    v_enum = Verdict.VOID

                # 2. End turn (T) - PROVISIONAL
                # Recalculate input tokens (approx)
                tokens_in_approx = len(state.query) // 4

                # Get provisional snapshot (Do not commit yet)
                provisional_snapshot = state.session_telemetry.end_turn(
                    tokens_out=tokens_out_approx,
                    verdict=v_enum,
                    context_length_used=tokens_in_approx + tokens_out_approx + 1000,  # Approx
                    kv_cache_size=0,
                    timeout=False,
                    safety_block=state.sabar_triggered,
                    truncation_flag=False,
                    commit=False,
                )

                # 3. Compute Attributes (R)
                # Pass provisional snapshot as current_turn
                attrs = compute_attributes(
                    state.session_telemetry.history,
                    state.session_telemetry.max_session_tokens,
                    current_turn=provisional_snapshot,
                )
                physics_snapshot = attrs

                # 4. Evaluate Physics Floors (A -> F -> Ψ)
                physics_verdict_enum = evaluate_physics_floors(attrs)

                final_snapshot = provisional_snapshot

                if physics_verdict_enum:
                    # Physics override!
                    p_verdict_str = physics_verdict_enum.value

                    # 4b. Speculative Re-Evaluation (The "Strike Three" Check)
                    # If we override to SABAR, does that complete a streak that forces HOLD?
                    from dataclasses import replace

                    speculative_snap = replace(provisional_snapshot, verdict=p_verdict_str)

                    attrs_spec = compute_attributes(
                        state.session_telemetry.history,
                        state.session_telemetry.max_session_tokens,
                        current_turn=speculative_snap,
                    )
                    physics_verdict_2 = evaluate_physics_floors(attrs_spec)

                    if physics_verdict_2 and physics_verdict_2.value != p_verdict_str:
                        # Escalation Detected (e.g. SABAR -> 888_HOLD)
                        p_verdict_str = physics_verdict_2.value
                        physics_verdict_enum = physics_verdict_2

                    import logging

                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"TEARFRAME Physics Floor Triggered: {p_verdict_str}. Overriding {current_verdict_val}."
                    )

                    # Update state verdict
                    from .apex_prime import ApexVerdict  # Ensure available locally if not global

                    state.verdict = ApexVerdict(
                        verdict=physics_verdict_enum,
                        reason=f"TEARFRAME Physics Floor Triggered: {p_verdict_str} (Budget/Burst/Streak).",
                        pulse=0.0,
                    )

                    # Update message to user
                    if p_verdict_str == "VOID":
                        state.raw_response = "[VOID] Session Terminated by Physics Governor (Resource/Stability Limit)."
                    elif p_verdict_str == "SABAR":
                        state.raw_response = (
                            "[SABAR] Session Cooldown Enforced (Burst Limit Exceeded)."
                        )
                    elif p_verdict_str == "888_HOLD":
                        state.raw_response = (
                            "[888_HOLD] Session Paused for Review (Behavioral Streak)."
                        )

                    # UPDATE SNAPSHOT VERDICT FOR HISTORY
                    from dataclasses import replace

                    final_snapshot = replace(final_snapshot, verdict=p_verdict_str)

                # 5. Commit Final Snapshot to History
                state.session_telemetry.commit_snapshot(final_snapshot)

            except Exception as e:
                import logging

                logging.getLogger(__name__).error(f"TEARFRAME Physics Error: {e}")

        if self.ledger_sink and state.metrics:
            # v42: Normalize verdict to string upstream
            verdict_str_log = "VOID"
            if state.verdict is None:
                verdict_str_log = "VOID"
            elif hasattr(state.verdict, "verdict") and hasattr(state.verdict.verdict, "value"):
                verdict_str_log = state.verdict.verdict.value  # ApexVerdict
            elif hasattr(state.verdict, "value"):
                verdict_str_log = state.verdict.value  # Verdict Enum
            else:
                verdict_str_log = str(state.verdict)

            # SSoT Normalization
            from .apex_prime import normalize_verdict_code

            verdict_str_log = normalize_verdict_code(verdict_str_log)

            entry: Dict[str, Any] = {
                "job_id": state.job_id,
                "query": state.query[:200],
                "stakes_class": state.stakes_class.value,
                "stage_trace": state.stage_trace,
                "active_scars": [s.get("id") for s in state.active_scars],
                "verdict": verdict_str_log,  # v42: use string
                "sabar_triggered": state.sabar_triggered,
                "hold_888_triggered": state.hold_888_triggered,
                # v42.1: constitutional metrics required for forensics checks
                "psi": float(getattr(state.metrics, "psi", 0.0) or 0.0),
                "amanah": int(bool(getattr(state.metrics, "amanah", False))),
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
            # v42.1 enrichment
            bootstrap_payload = get_bootstrap_payload()
            if bootstrap_payload:
                entry["spec_hashes"] = bootstrap_payload.get("spec_hashes", {})
                entry["zkpc_receipt"] = bootstrap_payload.get("zkpc_receipt")
            entry["commit_hash"] = os.getenv("ARIFOS_COMMIT_HASH") or os.getenv(
                "GIT_COMMIT", "unknown"
            )
            if state.epsilon_observed is not None:
                entry["epsilon_observed"] = state.epsilon_observed
            if getattr(state, "eye_vector", None) is not None:
                entry["eye_vector"] = state.eye_vector
            if getattr(state, "c_budi", None) is not None:
                entry["c_budi"] = state.c_budi

            # v44 Physics Traceability
            if physics_snapshot:
                entry["art_physics"] = {
                    "cadence": physics_snapshot.cadence,
                    "turn_rate": physics_snapshot.turn_rate,
                    "token_rate": physics_snapshot.token_rate,
                    "budget_burn_pct": physics_snapshot.budget_burn_pct,
                    "stability_var_dt": physics_snapshot.stability_var_dt,
                    "void_streak": physics_snapshot.void_streak,
                    "sabar_streak": physics_snapshot.sabar_streak,
                }

            # v45Ω Patch C: Failover metadata (if failover enabled)
            if hasattr(state, "failover_metadata") and state.failover_metadata:
                entry["failover"] = {
                    "provider": state.failover_metadata.get("provider"),
                    "fallback_occurred": state.failover_metadata.get("fallback_occurred", False),
                    "attempt_count": state.failover_metadata.get("attempt_count", 1),
                    "total_latency_ms": state.failover_metadata.get("total_latency_ms"),
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


def main() -> int:  # pragma: no cover
    """CLI shim: `python -m arifos_core.system.pipeline --query \"...\"`."""
    from .__main__ import main as _main

    return _main()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
