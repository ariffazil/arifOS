"""
arifosmcp/runtime/mind_reason.py - 333 MIND LLM-Powered Reasoning

Wires arif_mind_reason through call_llm() for constitutional LLM inference.
Tier 1: SEA-LION (api.sea-lion.ai)
Tier 2: Ollama local fallback
Tier 3: Deterministic fallback (original logic from tools/mind_reason.py)

777_WITNESS: All LLM output passes through LLMOutputEnvelope before tool logic.
The envelope is the only thing that reaches judgment, memory, or vault.

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

from arifosmcp.runtime.llm_client import call_llm
from arifosmcp.runtime.thinking.session import ThinkingSessionManager
from arifosmcp.schemas.mind_metabolism import (
    AbductiveHypothesis,
    AbstractionCard,
    AttestationCard,
    CognitiveLayer,
    MetabolizedContext,
    MindGovernance,
    MindPacket,
    MindRequest,
    MindResponse,
    MindSynthesis,
    NextAction,
)

logger = logging.getLogger(__name__)

# ── Thinking Session Manager ──────────────────────────────────────────────────
thinking_manager = ThinkingSessionManager()

# ── System Prompts (Metabolic Stages) ──────────────────────────────────────────

SYSTEM_PROMPT_METABOLIZE = """You are Arif - Cognitive Metabolism Kernel.
Your task is to DIGEST the input.
- Summary: Concise recap of the request.
- Core Problem: What is actually being solved?
- Why it Matters: The constitutional significance.
- Background Field: Contextual invariants.
- Assumptions & Constraints: Logical boundaries.
"""

SYSTEM_PROMPT_ABSTRACT = """You are Arif - Cognitive Metabolism Kernel.
Your task is ABSTRACTION.
- Identify Concepts: Processes, objects, constraints, relations.
- Define: Constitutional axioms (F-codes) applicable.
- Source: input | evidence | memory | inference.
"""

SYSTEM_PROMPT_ATTEST = """You are Arif - Cognitive Metabolism Kernel.
Your task is ATTESTATION.
- Claim ID: unique ref.
- Claim: specific statement.
- Evidence Level: L0 (none) to L5 (immutable).
- Language Strength: suggests | says | indicates | confirms | verified.
"""

SYSTEM_PROMPT_ABDUCT = """You are Arif - Cognitive Metabolism Kernel.
Your task is ABDUCTION.
- Hypothesis: Best explanatory leap.
- Explains: What patterns does it account for?
- Does Not Explain: Known anomalies.
- Falsification: How could this be proven wrong?
"""

SYSTEM_PROMPT_SYNTHESIZE = """You are Arif - Cognitive Metabolism Kernel.
Your task is SYNTHESIS.
- Bounded Answer: The understanding derived.
- Supported: What is witnessed.
- Unknown: What remains unobserved.
- Confidence: Reasoning, Evidence, Overall.
"""

# ── System Prompt (Legacy) ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Arif - Constitutional AI. Stage 333 MIND reasoning witness.
Never return SEAL. Cite L02/L07/L08. Distinguish CLAIM from FACT.

OUTPUT JSON: {"status":REASONED|REFLECTED|HYPOTHESIS|NEEDS_EVIDENCE|HOLD|ESCALATE_TO_888,
"claim_state":OBSERVED_INPUT|INFERENCE|HYPOTHESIS|SUPPORTED_CLAIM|VERIFIED_FACT|SPECULATION|UNSUPPORTED,
"synthesis":"one-sentence constitutional synthesis",
"reasoning":{"observed_inputs":[],"inferences":[],"counterarguments":[],"missing_evidence":[]},
"confidence":{"reasoning_confidence":0.0-1.0,"evidence_confidence":0.0-1.0,"overall_confidence":0.0-1.0},
"uncertainty":[{"type":"","detail":""}],"axioms_used":[],"next_safe_action":[]}
"""

# ── Response Schema (Legacy) ───────────────────────────────────────────────────

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": [
                "REFLECTED",
                "REASONED",
                "HYPOTHESIS",
                "NEEDS_EVIDENCE",
                "HOLD",
                "ESCALATE_TO_888",
            ],
        },
        "claim_state": {
            "type": "string",
            "enum": [
                "OBSERVED_INPUT",
                "INFERENCE",
                "HYPOTHESIS",
                "SUPPORTED_CLAIM",
                "VERIFIED_FACT",
                "SPECULATION",
                "UNSUPPORTED",
            ],
        },
        "synthesis": {"type": "string"},
        "reasoning": {
            "type": "object",
            "properties": {
                "observed_inputs": {"type": "array", "items": {"type": "string"}},
                "inferences": {"type": "array", "items": {"type": "string"}},
                "counterarguments": {"type": "array", "items": {"type": "string"}},
                "missing_evidence": {"type": "array", "items": {"type": "string"}},
            },
        },
        "confidence": {
            "type": "object",
            "properties": {
                "reasoning_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "evidence_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
        "uncertainty": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "detail": {"type": "string"},
                },
            },
        },
        "axioms_used": {"type": "array", "items": {"type": "string"}},
        "next_safe_action": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "claim_state", "synthesis", "reasoning", "confidence"],
}

# ── Field Provenance ───────────────────────────────────────────────────────────

_FIELD_PROVENANCE_LLM = {
    "status": "llm_generated_enum_validated",
    "claim_state": "llm_generated_enum_validated",
    "synthesis": "llm_generated_pass_through",
    "reasoning": "llm_generated_structured",
    "confidence": "llm_generated_structured_clamped",
    "uncertainty": "llm_generated_array",
    "axioms_used": "llm_generated_defaulted_if_empty",
    "next_safe_action": "llm_generated_defaulted_if_empty",
    "invariant_pass": "llm_generated_object_defaulted_if_empty",
    "reasoning_mode": "runtime_metadata",
    "_llm_tier": "runtime_metadata",
    "timestamp": "runtime_metadata",
}

_FIELD_PROVENANCE_FALLBACK = {
    "status": "code_derived_mode_mapping",
    "claim_state": "code_derived_default_inference",
    "synthesis": "code_derived_template",
    "reasoning": "code_derived_empty_structured",
    "confidence": "code_derived_fixed_structured",
    "uncertainty": "code_derived_fallback_warning",
    "axioms_used": "code_derived_empty_default",
    "next_safe_action": "code_derived_empty_default",
    "invariant_pass": "code_derived_empty_object",
    "reasoning_mode": "runtime_metadata",
    "timestamp": "runtime_metadata",
}


def _build_witness_statement(llm_tier: str | None = None) -> dict[str, str]:
    """Explicitly declare the wrapper's role vs. the semantic payload's source."""
    if llm_tier:
        return {
            "semantic_payload_source": f"LLM ({llm_tier})",
            "wrapper_role": "validate_clamp_route_record",
            "approval_authority": "human_judge_only",
            "calibration_note": "confidence is model self-assessment, not verified truth probability",
            "reasoning_instrument_status": "STRUCTURED_WITNESS",
        }
    return {
        "semantic_payload_source": "deterministic_fallback",
        "wrapper_role": "validate_clamp_route_record",
        "approval_authority": "human_judge_only",
        "calibration_note": "confidence is fixed heuristic, not empirical probability",
        "reasoning_instrument_status": "DETERMINISTIC_FALLBACK",
    }


def _status_to_reasoning_mode(status: str) -> str:
    if status == "REASONED":
        return "analytical"
    if status == "REFLECTED":
        return "interpretive"
    if status == "HYPOTHESIS":
        return "exploratory"
    if status == "HOLD":
        return "suspensive"
    return "unknown"


# ── Core Reasoning Function (v1 Legacy) ─────────────────────────────────────────


async def arif_mind_reason(
    query: str,
    mode: str = "reason",
    session_id: str | None = None,
    actor_id: str | None = None,
    depth: int = 3,
) -> dict[str, Any]:
    """
    333_MIND v1 — Constitutional reasoning with envelope integrity.
    Updated to delegate to v2 for 'metabolize' mode.
    """
    if mode == "metabolize":
        from arifosmcp.schemas.mind_metabolism import MindRequest, ReasoningControl

        # DDD-20260611: build a typed ReasoningControl instead of a
        # bare dict. Pydantic v2 accepts both, but the typed form
        # (1) silences the LSP `dict[str, int]` mismatch warning,
        # (2) makes the 9 ReasoningControl fields discoverable at
        # this dispatch site, and (3) fails-closed at construction
        # time if depth is out of [1, 10]. The other 8 fields
        # use their declared defaults.
        reasoning_control = ReasoningControl(depth=depth)

        request = MindRequest(
            query=query,
            mode=mode,
            session_id=session_id,
            actor_id=actor_id,
            reasoning_control=reasoning_control,
        )
        v2_resp = await arif_mind_reason_v2(request)
        return v2_resp.model_dump()

    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    # Build the reasoning prompt
    user_prompt = f"""QUERY: {query}
MODE: {mode}
DEPTH: {depth}
SESSION_ID: {session_id or "none"}
ACTOR_ID: {actor_id or "anonymous"}

Reason through this under the 13 constitutional floors.
Provide structured reasoning as a witness.
Cite L02 (Truth), L07 (Humility), L08 (Genius).
Distinguish CLAIM from FACT."""

    # ── LLM Inference with 777_WITNESS Envelope ───────────────────────────────────
    # DDD-20260611: bumped max_tokens 200→2000. M3 with thinking enabled
    # spends ~900+ tokens on reasoning_tokens alone at temperature=0.3,
    # so 800 cap truncates BEFORE the JSON answer is written (finish_reason=length).
    # 2000 gives M3 room for the think block + the full JSON envelope:
    # status, claim_state, synthesis, reasoning, confidence, uncertainty,
    # axioms_used, next_safe_action. Verified via direct /v1/chat/completions
    # with same SYSTEM_PROMPT at 800 (truncated) and 2000 (complete).
    # F1 AMANAH reversible: only the budget is changed; the contract
    # (JSON envelope) and tool origin are unchanged. The F11 AUTH rule
    # (line 327-337) still prevents reasoning_content from leaking to
    # the audit surface — only the final content field is used.
    try:
        envelope = await call_llm(
            system=SYSTEM_PROMPT,
            user=user_prompt,
            response_schema=RESPONSE_SCHEMA,
            temperature=0.3,
            max_tokens=2000,
            tool_origin="333_REASON",
            mode=mode,
        )
        llm_available = True
        llm_tier = envelope.provider
    except Exception as exc:
        logger.warning("333 MIND LLM call failed: %s", exc)
        llm_available = False
        llm_tier = None

    # ── Deterministic Fallback ─────────────────────────────────────────────────
    if not llm_available:
        status = _mode_to_status_fallback(mode)
        parsed_output = {
            "status": status,
            "claim_state": "HYPOTHESIS",
            "synthesis": f"[deterministic] {mode} reasoning - LLM unavailable",
            "reasoning": {
                "observed_inputs": [query],
                "inferences": ["LLM fallback triggered"],
                "counterarguments": [],
                "alternative_explanations": [],
                "missing_evidence": ["LLM core unavailable"],
            },
            "confidence": {
                "reasoning_confidence": 0.5,
                "evidence_confidence": 0.3,
                "overall_confidence": 0.3,
            },
            "uncertainty": [
                {
                    "type": "LLM_FAILURE",
                    "detail": "Primary reasoning engine unavailable",
                }
            ],
            "axioms_used": ["L07"],
            "next_safe_action": ["222_EVIDENCE", "888_JUDGE"],
        }
        provenance = _FIELD_PROVENANCE_FALLBACK
        witness = _build_witness_statement(None)
        reasoning_mode = _status_to_reasoning_mode(status)
    else:
        # ── LLM Path - Extract from Envelope ─────────────────────────────────────
        parsed_output = envelope.parsed_output
        status = parsed_output.get("status", "HOLD")

        # Internal Integrity Check
        conf = parsed_output.get("confidence", {"overall_confidence": 0.5})
        if not isinstance(conf, dict):
            raw = float(conf) if isinstance(conf, int | float) else 0.5
            conf = {"overall_confidence": raw, "evidence_confidence": raw * 0.6}
        overall = conf.get("overall_confidence", 0.5)
        evidence = conf.get("evidence_confidence", 0.3)
        if overall > evidence + 0.2:
            conf["overall_confidence"] = evidence + 0.1
            parsed_output["confidence"] = conf

        # Uncertainty auto-population
        uncertainty = parsed_output.get("uncertainty", [])
        if not isinstance(uncertainty, list):
            uncertainty = [
                {
                    "type": "PARSE_ERROR",
                    "detail": f"LLM returned {type(uncertainty).__name__} for uncertainty",
                }
            ]

        reasoning = parsed_output.get("reasoning", {})
        if not isinstance(reasoning, dict):
            reasoning = {
                "observed_inputs": [str(reasoning)[:500]]
                if reasoning
                else ["LLM returned empty/unstructured reasoning"],
                "inferences": [
                    "LLM output was not structured — raw text wrapped as observed_inputs"
                ],
                "counterarguments": [],
                "alternative_explanations": [],
                "missing_evidence": ["Structured reasoning unavailable — LLM returned non-dict"],
            }
            parsed_output["reasoning"] = reasoning

        if not reasoning.get("observed_inputs") or not reasoning.get("inferences"):
            uncertainty.append(
                {
                    "type": "REASONING_GAP",
                    "detail": "Structured reasoning fields incomplete",
                }
            )
        if not session_id:
            uncertainty.append({"type": "SESSION_GAP", "detail": "No governed session_id bound"})
        parsed_output["uncertainty"] = uncertainty

        provenance = _FIELD_PROVENANCE_LLM
        witness = _build_witness_statement(llm_tier)
        reasoning_mode = _status_to_reasoning_mode(status)

    # ── Build Complete Reasoning Packet ─────────────────────────────────────────
    result = {
        **parsed_output,
        "reasoning_mode": reasoning_mode,
        "session": {
            "session_id": session_id,
            "bound": bool(session_id),
            "governance_level": ("governed_reasoning" if session_id else "ungoverned_reflection"),
        },
        "actor": {
            "claimed_id": actor_id or "anonymous",
            "verified_id": actor_id if actor_id else None,
            "verification_method": "none",
            "trust_level": "claimed" if actor_id else "anonymous",
            "effective_actor": actor_id if actor_id else "anonymous_until_verified",
            "actor_binding_confidence": 1.0 if actor_id else 0.5,
            "mismatch_warning": None,
        },
        # Metadata
        "timestamp": timestamp,
        "_field_provenance": provenance,
        "_witness": witness,
        "_llm_tier": llm_tier or "unavailable",
        "_llm_available": llm_available,
    }

    # ── Attach 777_WITNESS envelope metadata ───────────────────────────────────
    if llm_available:
        result["_envelope"] = {
            "provider": envelope.provider,
            "model": envelope.model,
            "tool_origin": envelope.tool_origin,
            "mode": envelope.mode,
            "raw_output_hash": envelope.raw_output_hash,
            "schema_valid": envelope.schema_valid,
            "confidence_claimed": envelope.confidence_claimed,
            "evidence_level": envelope.evidence_level,
            "uncertainty": envelope.uncertainty,
            "risk_flags": envelope.risk_flags,
            "human_decision_required": envelope.human_decision_required,
            "authority_level": envelope.authority_level,
            "timestamp": envelope.timestamp,
            "wrapper_version": "777_WITNESS_v1.0",
        }
        result["human_decision_required"] = envelope.human_decision_required
    else:
        result["_envelope"] = {
            "provider": "none",
            "tool_origin": "333_REASON",
            "mode": mode,
            "raw_output_hash": "none",
            "schema_valid": False,
            "confidence_claimed": 0.0,
            "evidence_level": "claimed",
            "uncertainty": ["LLM_unavailable"],
            "risk_flags": ["LLM_FAILURE"],
            "human_decision_required": True,
            "authority_level": "instrument_only",
            "timestamp": timestamp,
            "wrapper_version": "777_WITNESS_v1.0",
        }
        result["human_decision_required"] = True

    # ── MIND_GEOMETRY_V1 enrichment (EUREKA-T, 2026-06-11) ─────────────────
    # The decision-torus layer measures *where* on the surface this
    # reasoning sits, not *what* it returns. It is a 4th verdict
    # dimension alongside the 13-floor verdict system: the geometry
    # never replaces floor verdicts, it adds a measurement.
    #
    # Wire-in is OPTIONAL: if the geometry layer fails to import
    # (e.g. Pydantic v2 not installed), the tool still works. The
    # geometry dict is added to the result under "_geometry" with
    # a "geometry_verdict" key the runner can route on.
    #
    # F2 TRUTH: this is governance geometry, not proof of safety.
    # The kernel never *occupies* the center; it only *describes*
    # where the trajectory sits.
    try:
        from arifosmcp.geometry.mind_geometry import (
            build_geometry_block,
            compute_geometry,
        )
        from arifosmcp.geometry.mind_schema import OrthogonalAxes

        # Classify the action. Mind reason is by default an
        # 'answer' action (read-only). Modes like 'plan' and
        # 'verify' stay as 'answer' (they don't mutate state).
        # Only 'metabolize' is dispatched to v2 (see line 247).
        action_class = "answer"
        if mode in {
            "plan",
            "verify",
            "decompose",
            "compare",
            "counterargue",
            "trace",
            "escalate_check",
        }:
            action_class = "draft"  # plans/drafts may mutate
        # The result is "draft" not "execute" — the runner can
        # promote to "execute" via arif_forge_execute.

        # Extract per-axis values from the parsed_output if present.
        # Otherwise use neutral 0.5 (not collapsed, not extreme).
        axes = OrthogonalAxes(
            T=min(1.0, max(0.0, overall)),
            U=min(
                1.0, max(0.0, 1.0 - overall)
            ),  # invert: high overall_confidence → low uncertainty
            R=0.5,  # neutral
            B=0.0,  # read-only action
            A=1.0 if actor_id else 0.0,  # authorization
            E=0.0 if llm_available else 0.5,  # entropy delta
            H=1.0,  # human sovereignty preserved by construction
            C=0.5,  # neutral
        )

        # Build the geometry verdict
        geo_verdict = compute_geometry(
            query=query,
            action_class=action_class,
            has_authorization=bool(actor_id),
            inner_llm_returned_structured_output=bool(llm_available),
            axes=axes,
            orthogonality_violation=False,
            self_authorization_score=0.0,
            reversibility=1.0,
            blast_radius=0.0,
            authority_cleanliness=1.0 if actor_id else 0.0,
            entropy_delta=0.0,
        )
        geo_block = build_geometry_block(geo_verdict)

        result["_geometry"] = {
            "version": "MIND_GEOMETRY_V1",
            "manifold": geo_block.manifold.value,
            "sovereign_proximity": geo_verdict.sovereign_proximity,
            "proximity_band": geo_verdict.proximity_band.value,
            "geometry_verdict": geo_verdict.geometry_verdict.value,
            "torus_coordinates": {
                "theta_epistemic": geo_block.epistemic_angle_theta,
                "phi_governance": geo_block.governance_angle_phi,
            },
            "forbidden_center": [e.name for e in geo_block.forbidden_center],
            "axiom_results": [r.to_dict() for r in geo_verdict.axiom_results],
            "proximity_trace": geo_verdict.proximity_trace,
            "hole_territory": geo_verdict.hole_territory,
            "hole_entry": geo_verdict.hole_entry,
            "wrapper_version": "MIND_GEOMETRY_V1.0",
        }
        # If geometry says HOLE_RISK, the runner can route to HOLD
        # *additionally* — geometry never downgrades a SEAL, it
        # only adds an extra reason to HOLD.
        if geo_verdict.geometry_verdict.value == "HOLE_RISK":
            result["human_decision_required"] = True
        elif geo_verdict.geometry_verdict.value == "HOLD":
            result["human_decision_required"] = True
    except Exception as exc:
        # Geometry is enrichment, not a hard dependency. If it
        # fails to load, the tool still returns its core result.
        result["_geometry"] = {
            "version": "MIND_GEOMETRY_V1",
            "available": False,
            "error": f"{type(exc).__name__}: {exc}"[:200],
        }

    return result


def _mode_to_status_fallback(mode: str) -> str:
    """Deterministic status when LLM is unavailable."""
    mapping = {
        "reason": "HOLD",
        "reflect": "REFLECTED",
        "decompose": "HOLD",
        "compare": "HOLD",
        "counterargue": "HOLD",
        "trace": "HOLD",
        "plan": "HOLD",
        "verify": "HOLD",
        "escalate_check": "HOLD",
    }
    return mapping.get(mode, "HOLD")


async def arif_mind_reason_structured(
    query: str,
    mode: str = "reason",
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Structured wrapper for arif_mind_reason - returns parsed_output directly."""
    result = await arif_mind_reason(query, mode, session_id, actor_id)
    return {k: v for k, v in result.items() if not k.startswith("_")}


# ── Core Reasoning Function (v2 Metabolic) ──────────────────────────────────────


async def arif_mind_reason_v2(request: MindRequest) -> MindResponse:
    """
    333 MIND v2 - Cognitive Metabolism Kernel.

    Sequential layers: parse -> abstract -> attest -> abduct -> contrast -> verify -> synthesize -> handoff
    """
    trace_id = str(uuid.uuid4())[:12]

    # Initialize Thinking Session
    session = thinking_manager.start_session(
        problem=request.query,
        context=request.context.model_dump(),
        arifos_session_id=request.session_id,
    )

    # --- LAYER 1: METABOLIZE ---
    metab_envelope = await call_llm(
        system=SYSTEM_PROMPT_METABOLIZE,
        user=f"QUERY: {request.query}\nCONTEXT: {request.context.model_dump()}",
        response_schema=MetabolizedContext.model_json_schema(),
        tool_origin="333 MIND_METABOLIZE",
    )
    metabolized = MetabolizedContext(**metab_envelope.parsed_output)
    thinking_manager.add_step(
        session.session_id, "analysis", f"Metabolized context: {metabolized.input_summary}"
    )

    # --- LAYER 2: ABSTRACT ---
    abs_envelope = await call_llm(
        system=SYSTEM_PROMPT_ABSTRACT,
        user=f"QUERY: {request.query}\nMETABOLIZED: {metabolized.model_dump()}",
        response_schema={
            "type": "object",
            "properties": {
                "abstractions": {"type": "array", "items": AbstractionCard.model_json_schema()}
            },
        },
        tool_origin="333 MIND_ABSTRACT",
    )
    abstractions = [
        AbstractionCard(**a) for a in abs_envelope.parsed_output.get("abstractions", [])
    ]
    thinking_manager.add_step(
        session.session_id, "analysis", f"Identified {len(abstractions)} abstractions."
    )

    # --- LAYER 3: ATTEST ---
    attestations = []
    if request.evidence.evidence_receipts:
        att_envelope = await call_llm(
            system=SYSTEM_PROMPT_ATTEST,
            user=f"EVIDENCE: {request.evidence.model_dump()}\nABSTRACTIONS: {[a.model_dump() for a in abstractions]}",
            response_schema={
                "type": "object",
                "properties": {
                    "attestations": {"type": "array", "items": AttestationCard.model_json_schema()}
                },
            },
            tool_origin="333 MIND_ATTEST",
        )
        attestations = [
            AttestationCard(**a) for a in att_envelope.parsed_output.get("attestations", [])
        ]
        thinking_manager.add_step(
            session.session_id, "verification", f"Bound {len(attestations)} attestations."
        )

    # --- LAYER 4: ABDUCT ---
    abductions = []
    if request.reasoning_control.allow_abduction:
        abd_envelope = await call_llm(
            system=SYSTEM_PROMPT_ABDUCT,
            user=f"QUERY: {request.query}\nMETABOLIZED: {metabolized.model_dump()}\nATTESTATIONS: {[a.model_dump() for a in attestations]}",
            response_schema={
                "type": "object",
                "properties": {
                    "abductions": {
                        "type": "array",
                        "items": AbductiveHypothesis.model_json_schema(),
                    }
                },
            },
            tool_origin="333 MIND_ABDUCT",
        )
        abductions = [
            AbductiveHypothesis(**a) for a in abd_envelope.parsed_output.get("abductions", [])
        ]
        thinking_manager.add_step(
            session.session_id, "hypothesis", f"Generated {len(abductions)} abductive hypotheses."
        )

    # --- LAYER 5: SYNTHESIZE ---
    syn_envelope = await call_llm(
        system=SYSTEM_PROMPT_SYNTHESIZE,
        user=f"QUERY: {request.query}\nABDUCTIONS: {[a.model_dump() for a in abductions]}\nATTESTATIONS: {[a.model_dump() for a in attestations]}",
        response_schema=MindSynthesis.model_json_schema(),
        tool_origin="333 MIND_SYNTHESIZE",
    )
    synthesis = MindSynthesis(**syn_envelope.parsed_output)
    thinking_manager.add_step(session.session_id, "conclusion", synthesis.bounded_answer)

    # Convert session steps to CognitiveLayers
    layers = []
    for step in session.steps:
        layers.append(
            CognitiveLayer(
                layer=step.step_number,
                name=step.step_type,
                operation=step.step_type,
                output=step.content,
                confidence_after=step.quality_score,
                delta_confidence=step.f2_truth_score,
            )
        )

    # Determine Next Actions
    next_actions = [
        NextAction(
            tool="888_JUDGE",
            mode="deliberate",
            reason="Final constitutional gate required",
            required=True,
        )
    ]
    if not request.evidence.evidence_receipts:
        next_actions.append(
            NextAction(
                tool="222_FETCH",
                mode="search",
                reason="No evidence bound to reasoning",
                required=True,
            )
        )

    packet = MindPacket(
        query=request.query,
        intent=request.task.intent,
        claim_state="hypothesis" if not attestations else "supported",
        reasoning_mode=request.reasoning_control.sequential_mode,
        metabolized_context=metabolized,
        abstractions=abstractions,
        attestations=attestations,
        abductions=abductions,
        sequential_layers=layers,
        synthesis=synthesis,
        next_actions=next_actions,
    )

    governance = MindGovernance(
        axioms_used=[a.name for a in abstractions if a.type == "axiom"],
        floors_checked=["L02", "L04", "L07", "L08"],
        verdict="OK" if synthesis.confidence.get("overall_confidence", 0) > 0.7 else "HOLD",
    )

    return MindResponse(
        status="OK",
        session_id=request.session_id,
        actor_id=request.actor_id,
        trace_id=trace_id,
        mind_packet=packet,
        governance=governance,
    )


async def arif_mind_step(
    session_id: str, step_type: str, content: str, parent_step: int | None = None
) -> dict[str, Any]:
    """Execute a single bounded reasoning step."""
    step = thinking_manager.add_step(session_id, step_type, content, parent_step=parent_step)
    return {
        "step_number": step.step_number,
        "step_type": step.step_type,
        "constitutional_verdict": step.constitutional_verdict,
        "f2_truth_score": step.f2_truth_score,
        "quality_score": step.quality_score,
    }


async def arif_mind_trace_get(session_id: str) -> dict[str, Any]:
    """Retrieve the full reasoning trace for a session."""
    session = thinking_manager.get_session(session_id)
    if not session:
        return {"error": f"Session {session_id} not found"}
    return {
        "session_id": session.session_id,
        "problem": session.problem,
        "steps": [
            {
                "step": s.step_number,
                "type": s.step_type,
                "content": s.content,
                "verdict": s.constitutional_verdict,
            }
            for s in session.steps
        ],
    }


async def arif_mind_claim_attest(
    claim: str, evidence_receipts: list[dict[str, Any]]
) -> AttestationCard:
    """Bind a claim to evidence receipts."""
    user_prompt = f"CLAIM: {claim}\nEVIDENCE: {evidence_receipts}"
    envelope = await call_llm(
        system=SYSTEM_PROMPT_ATTEST,
        user=user_prompt,
        response_schema=AttestationCard.model_json_schema(),
        tool_origin="333 MIND_ATTEST",
    )
    return AttestationCard(**envelope.parsed_output)


async def arif_mind_contradict_scan(
    claims: list[str], evidence: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Scan for contradictions between claims and evidence."""
    # This would use a specialized prompt or logic
    return []  # Placeholder


async def arif_mind_handoff_prepare(session_id: str, target_organ: str) -> dict[str, Any]:
    """Package reasoning output for downstream consumption."""
    session = thinking_manager.get_session(session_id)
    if not session:
        return {"error": "Session not found"}

    # Compress for HEART/JUDGE
    return {
        "session_id": session_id,
        "target_organ": target_organ,
        "synthesis": session.steps[-1].content if session.steps else "",
        "verdict_recommendation": "SEAL" if session.quality_score > 0.8 else "HOLD",
    }


__all__ = [
    "arif_mind_reason",
    "arif_mind_reason_v2",
    "arif_mind_reason_structured",
    "arif_mind_step",
    "arif_mind_trace_get",
    "arif_mind_claim_attest",
    "arif_mind_contradict_scan",
    "arif_mind_handoff_prepare",
]
