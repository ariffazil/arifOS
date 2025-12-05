"""
pipeline.py - 000-999 Metabolic Pipeline for arifOS v35Ω

Implements the constitutional metabolism with Class A/B routing:
- Class A (low-stakes/factual): Fast track 111 → 333 → 888 → 999
- Class B (high-stakes/ethical): Deep track through 222 + 555 + 777

AAA Engine Integration (v35.8.0):
- ARIFEngine (Δ): sense/reason/align - cold logic, clarity
- ADAMEngine (Ω): empathize/bridge - warm logic, stability
- ApexEngine (Ψ): judge - judiciary wrapper

See: arifos_pipeline.yaml for full specification
     docs/AAA_ENGINES_FACADE_PLAN_v35Omega.md for engine contract
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .APEX_PRIME import apex_review, ApexVerdict
from .metrics import Metrics
from .eye_sentinel import EyeSentinel, EyeReport

# AAA Engines (internal facade - v35.8.0)
from .engines import ARIFEngine, ADAMEngine, ApexEngine
from .engines.arif_engine import ARIFPacket
from .engines.adam_engine import ADAMPacket


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

    # Timing
    start_time: float = field(default_factory=time.time)
    stage_times: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for logging."""
        return {
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


# =============================================================================
# STAGE DEFINITIONS
# =============================================================================

# Type for stage functions
StageFunc = Callable[[PipelineState], PipelineState]


def stage_000_void(state: PipelineState) -> PipelineState:
    """
    000 VOID - Reset to uncertainty. Ego to zero.

    Clear previous context biases, initialize metrics to neutral.
    """
    state.current_stage = "000"
    state.stage_trace.append("000_VOID")
    state.stage_times["000"] = time.time()

    # Reset to humble start
    state.draft_response = ""
    state.metrics = None
    state.verdict = None

    return state


def stage_111_sense(state: PipelineState) -> PipelineState:
    """
    111 SENSE - Parse input. What is actually being asked?

    Detect high-stakes indicators and classify for routing.
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


def stage_888_judge(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
    eye_sentinel: Optional[EyeSentinel] = None,
) -> PipelineState:
    """
    888 JUDGE - Check all floors. Pass or fail?

    APEX PRIME (Ψ) renders judgment. This is the veto point.
    """
    state.current_stage = "888"
    state.stage_trace.append("888_JUDGE")
    state.stage_times["888"] = time.time()

    # Compute metrics
    if compute_metrics:
        state.metrics = compute_metrics(
            state.query,
            state.draft_response,
            {"stakes_class": state.stakes_class.value},
        )
    else:
        # Stub metrics
        state.metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
        )

    # Apply lightweight penalties from 444/555/666 heuristics
    if state.metrics is not None:
        if state.missing_fact_issue:
            state.metrics.truth = max(0.0, state.metrics.truth - 0.15)
        if state.blame_language_issue:
            state.metrics.kappa_r = max(0.0, state.metrics.kappa_r - 0.25)
        if state.physical_action_issue:
            state.metrics.peace_squared = max(0.0, state.metrics.peace_squared - 0.2)

    # Optional @EYE Sentinel audit
    eye_report: Optional[EyeReport] = None
    eye_blocking: bool = False
    if eye_sentinel is not None and state.metrics is not None:
        try:
            eye_report = eye_sentinel.audit(
                draft_text=state.draft_response,
                metrics=state.metrics,
                context={
                    "stakes_class": state.stakes_class.value,
                },
            )
            eye_blocking = eye_report.has_blocking_issue()
        except Exception:
            # @EYE failures must not crash the pipeline
            pass

    # Get verdict from APEX PRIME
    high_stakes = state.stakes_class == StakesClass.CLASS_B
    state.verdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
    )

    # Check for 888_HOLD or SABAR
    if state.verdict == "888_HOLD":
        state.hold_888_triggered = True
    elif state.verdict in ("VOID", "SABAR"):
        state.sabar_triggered = True
        state.sabar_reason = f"Floor failures in 888_JUDGE"

    return state


def stage_999_seal(state: PipelineState) -> PipelineState:
    """
    999 SEAL - If PASS -> emit. If FAIL -> SABAR or VOID.

    Final gate. All verdicts are immutably recorded.
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
        state.raw_response = (
            "[888_HOLD] Constitutional judiciary hold. "
            "Please clarify or rephrase your request."
        )
    elif state.verdict == "SABAR":
        state.raw_response = (
            "[SABAR] Stop. Acknowledge. Breathe. Adjust. Resume.\n"
            "This request requires reconsideration."
        )
    else:  # VOID
        state.raw_response = (
            "[VOID] This request has been refused by arifOS constitutional floors."
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
        """
        self.llm_generate = llm_generate
        self.compute_metrics = compute_metrics
        self.scar_retriever = scar_retriever
        self.context_retriever = context_retriever
        self.ledger_sink = ledger_sink
        self.eye_sentinel = eye_sentinel

        # AAA Engines (v35.8.0 - internal facade)
        self._arif = ARIFEngine()
        self._adam = ADAMEngine()

    def run(
        self,
        query: str,
        job_id: Optional[str] = None,
        force_class: Optional[StakesClass] = None,
    ) -> PipelineState:
        """
        Run the full 000-999 pipeline.

        Args:
            query: User input
            job_id: Optional job identifier for tracking
            force_class: Force a specific stakes class (for testing)

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

        # INHALE: 000 → 111 → 222
        state = stage_000_void(state)
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
            entry = {
                "job_id": state.job_id,
                "query": state.query[:200],
                "stakes_class": state.stakes_class.value,
                "stage_trace": state.stage_trace,
                "active_scars": [s.get("id") for s in state.active_scars],
                "verdict": state.verdict,
                "sabar_triggered": state.sabar_triggered,
                "hold_888_triggered": state.hold_888_triggered,
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
    "Pipeline",
    "PipelineState",
    "StakesClass",
    "run_pipeline",
    "stage_000_void",
    "stage_111_sense",
    "stage_222_reflect",
    "stage_333_reason",
    "stage_444_align",
    "stage_555_empathize",
    "stage_666_bridge",
    "stage_777_forge",
    "stage_888_judge",
    "stage_999_seal",
]
