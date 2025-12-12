"""
pipeline.py - 000-999 Metabolic Pipeline for arifOS v37

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

    # Simple refusal detector: treat clear textual refusals as safe behaviour,
    # especially for high-stakes prompts.
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

    # Baseline floor failures from APEX PRIME floor checker so that
    # PipelineState.floor_failures is populated for audit.
    high_stakes = state.stakes_class == StakesClass.CLASS_B
    if state.metrics is not None:
        floors = check_floors(
            state.metrics,
            tri_witness_required=high_stakes,
            tri_witness_threshold=0.95,
        )
        state.floor_failures = list(floors.reasons)

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

            # Attach blocking @EYE alerts to floor_failures for visibility.
            if eye_report.has_blocking_issue():
                try:
                    from .eye.base import EyeAlert  # Local import to avoid cycles
                    blocking_alerts = eye_report.get_blocking_alerts()
                except Exception:
                    blocking_alerts = []

                for alert in blocking_alerts:
                    view_name = getattr(alert, "view_name", "UnknownView")
                    message = getattr(alert, "message", "")
                    state.floor_failures.append(
                        f"EYE_BLOCK[{view_name}]: {message}"
                    )

            # If the model clearly refused to act (safe refusal), do not let
            # @EYE blocking force SABAR. We still log the alerts above.
            if is_refusal and eye_blocking:
                eye_blocking = False
        except Exception:
            # @EYE failures must not crash the pipeline
            pass

    # Get verdict from APEX PRIME
    apex_verdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
    )

    # =========================================================================
    # W@W FEDERATION CHECK (v36.3Ω)
    # Run all 5 organs and merge with APEX verdict
    # =========================================================================
    waw_federation = WAWFederationCore()
    state.waw_verdict = waw_federation.evaluate(
        output_text=state.draft_response,
        metrics=state.metrics,
        context={"stakes_class": state.stakes_class.value},
    )

    # Merge W@W verdict with APEX verdict
    # Priority: @EYE SABAR > @WEALTH ABSOLUTE > @RIF VOID > @GEOX HOLD-888 > @WELL/@PROMPT SABAR > APEX
    # Note: @EYE blocking triggers SABAR in APEX; preserve that for user reconsideration
    final_verdict = apex_verdict

    # @EYE blocking takes precedence - preserve SABAR for user to reconsider
    if eye_blocking and apex_verdict == "SABAR":
        # Keep SABAR; W@W violations will be logged but don't override @EYE
        if state.sabar_reason is None:
            state.sabar_reason = "@EYE blocking issue (see floor_failures for details)"
    elif state.waw_verdict.has_absolute_veto:
        # @WEALTH Amanah LOCK - absolute veto overrides everything
        final_verdict = "VOID"
        state.sabar_reason = "@WEALTH absolute veto (Amanah breach)"
    elif "@RIF" in state.waw_verdict.veto_organs:
        # @RIF epistemic veto - VOID
        final_verdict = "VOID"
        state.sabar_reason = "@RIF epistemic veto (Truth/ΔS breach)"
    elif "@GEOX" in state.waw_verdict.veto_organs:
        # @GEOX physics veto - HOLD-888 (runtime compat)
        final_verdict = "888_HOLD"
        state.sabar_reason = "@GEOX physics veto (reality check)"
    elif state.waw_verdict.has_veto:
        # Other vetoes (@WELL, @PROMPT) - SABAR
        final_verdict = "SABAR"
        state.sabar_reason = f"W@W veto from: {', '.join(state.waw_verdict.veto_organs)}"
    elif state.waw_verdict.has_warn and apex_verdict == "SEAL":
        # W@W WARN downgrades SEAL to PARTIAL
        final_verdict = "PARTIAL"

    state.verdict = final_verdict

    # v37 tuning: optional W@W merge disable (for red-team harnesses) and
    # safe refusal handling.
    #
    # If ARIFOS_DISABLE_WAW is set, we revert the verdict back to the APEX
    # verdict so that W@W organs (@PROMPT/@WELL) cannot override floors during
    # evaluation. W@W signals remain available via state.waw_verdict for
    # telemetry.
    disable_waw_merge_env = os.getenv("ARIFOS_DISABLE_WAW", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if disable_waw_merge_env:
        state.verdict = apex_verdict
        # Drop W@W-specific SABAR reason if it was attached.
        if state.sabar_reason and state.sabar_reason.startswith("W@W veto from"):
            state.sabar_reason = None

    # For clear refusals on high-stakes prompts, treat the refusal itself as a
    # safe outcome rather than escalated SABAR/VOID/888_HOLD. This runs after
    # W@W so that refusals are not punished by additional veto layers.
    if is_refusal and high_stakes and state.verdict in ("SABAR", "VOID", "888_HOLD"):
        state.verdict = "SEAL"

    # Check for 888_HOLD or SABAR
    if state.verdict == "888_HOLD":
        state.hold_888_triggered = True
    elif state.verdict in ("VOID", "SABAR"):
        state.sabar_triggered = True
        if state.sabar_reason is None:
            state.sabar_reason = "Floor failures in 888_JUDGE"

        # If we reached a blocking verdict but floor_failures is still empty,
        # attach the sabar_reason so callers have at least one clue.
        if not state.floor_failures and state.sabar_reason:
            state.floor_failures.append(state.sabar_reason)

    # ==========================================================================
    # v38: Memory Write Policy Engine Integration
    # Every verdict must be written to memory via policy-gated routing
    # ==========================================================================
    if state.memory_write_policy is not None and state.memory_band_router is not None:
        from datetime import datetime, timezone
        import json
        import hashlib

        # Build floor check evidence
        floor_checks = []
        if state.metrics is not None:
            floor_checks = [
                {"floor": "F1_Amanah", "passed": state.metrics.amanah},
                {"floor": "F2_Truth", "passed": state.metrics.truth >= 0.99, "value": state.metrics.truth},
                {"floor": "F3_TriWitness", "passed": state.metrics.tri_witness >= 0.95, "value": state.metrics.tri_witness},
                {"floor": "F4_DeltaS", "passed": state.metrics.delta_s >= 0, "value": state.metrics.delta_s},
                {"floor": "F5_Peace2", "passed": state.metrics.peace_squared >= 1.0, "value": state.metrics.peace_squared},
                {"floor": "F6_KappaR", "passed": state.metrics.kappa_r >= 0.95, "value": state.metrics.kappa_r},
                {"floor": "F7_Omega0", "passed": 0.03 <= state.metrics.omega_0 <= 0.05, "value": state.metrics.omega_0},
            ]

        timestamp = datetime.now(timezone.utc).isoformat()

        # Compute evidence hash
        state.memory_evidence_hash = compute_evidence_hash(
            floor_checks=floor_checks,
            verdict=state.verdict or "UNKNOWN",
            timestamp=timestamp,
        )

        # Build evidence chain for policy check
        evidence_chain = {
            "floor_checks": floor_checks,
            "verdict": state.verdict,
            "timestamp": timestamp,
            "job_id": state.job_id,
            "stakes_class": state.stakes_class.value,
        }
        # Add hash to evidence chain
        evidence_chain["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence_chain.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        # Check write policy
        write_decision = state.memory_write_policy.should_write(
            verdict=state.verdict or "UNKNOWN",
            evidence_chain=evidence_chain,
        )

        # Route write to appropriate bands if allowed
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

            # Route write via band router
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
        # v37: Pass vault for MemoryContext initialization
        state = stage_000_void(state, vault=self._vault)
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
