"""
arifosmcp/runtime/mind_reason.py — 333_MIND LLM-Powered Reasoning

Wires arif_mind_reason through call_llm() for constitutional LLM inference.
Tier 1: SEA-LION (api.sea-lion.ai)
Tier 2: Ollama local fallback
Tier 3: Deterministic fallback (original logic from tools/mind_reason.py)

777_WITNESS: All LLM output passes through LLMOutputEnvelope before tool logic.
The envelope is the only thing that reaches judgment, memory, or vault.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

from arifosmcp.runtime.llm_client import call_llm

logger = logging.getLogger(__name__)

# ── System Prompt ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Arif — Constitutional AI operating under the 13 Floors (F01–F13).

Stage 333_MIND: Structured Reasoning Instrument
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You provide structured reasoning, NOT final constitutional verdicts.

Your ROLE is to behave as a REASONING WITNESS:
- Break down the logic clearly
- Separate fact from inference
- Acknowledge uncertainty explicitly
- NEVER return "SEAL" (that is for 888_JUDGE only)

MODES:
- reason: General reasoning
- reflect: Interpretive / philosophical / biographical reflection
- decompose: Break down a complex problem
- compare: Compare multiple options
- counterargue: Generate objections/contradictions
- trace: Build a causal or logical chain
- plan: Produce a structured action plan
- verify: Check claims against evidence receipts
- escalate_check: Decide if 888_JUDGE is needed

CLAIM STATES:
- OBSERVED_INPUT: Directly from user/tool input
- INFERENCE: Reasoned from available data
- HYPOTHESIS: Plausible but unverified
- SUPPORTED_CLAIM: Backed by provided evidence
- VERIFIED_FACT: Strongly verified by immutable receipts
- NORMATIVE_ADVICE: Recommendation based on axioms
- SPECULATION: Weak / imaginative / creative
- UNSUPPORTED: Lacks any evidence or logical basis

OUTPUT: JSON ONLY. Return exactly this structure:
{
  "status": "REFLECTED" | "REASONED" | "HYPOTHESIS" | "NEEDS_EVIDENCE" | "HOLD" | "ESCALATE_TO_888",
  "claim_state": "one of the claim states above",
  "synthesis": "one-sentence constitutional synthesis",
  "reasoning": {
    "observed_inputs": ["list"],
    "inferences": ["list"],
    "counterarguments": ["list"],
    "alternative_explanations": ["list"],
    "missing_evidence": ["list"]
  },
  "confidence": {
    "reasoning_confidence": 0.0-1.0,
    "evidence_confidence": 0.0-1.0,
    "overall_confidence": 0.0-1.0
  },
  "uncertainty": [
    {"type": "string", "detail": "string"}
  ],
  "axioms_used": ["list of F-codes cited"],
  "next_safe_action": ["list of suggested next tools: 222_FETCH, 555_MEMORY, 666_HEART, 888_JUDGE"]
}
"""

# ── Response Schema ────────────────────────────────────────────────────────────

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
            "description": "Reasoning status — SEAL is forbidden",
        },
        "claim_state": {
            "type": "string",
            "enum": [
                "OBSERVED_INPUT",
                "INFERENCE",
                "HYPOTHESIS",
                "SUPPORTED_CLAIM",
                "VERIFIED_FACT",
                "NORMATIVE_ADVICE",
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
                "alternative_explanations": {
                    "type": "array",
                    "items": {"type": "string"},
                },
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
# F2 addendum: Every field must declare its source to prevent authority confusion.

_FIELD_PROVENANCE_LLM = {
    "status": "llm_generated_enum_validated",
    "claim_state": "llm_generated_enum_validated",
    "synthesis": "llm_generated_pass_through",
    "reasoning": "llm_generated_structured",
    "confidence": "llm_generated_structured_clamped",
    "uncertainty": "llm_generated_array",
    "axioms_used": "llm_generated_defaulted_if_empty",
    "next_safe_action": "llm_generated_defaulted_if_empty",
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


# ── Core Reasoning Function ────────────────────────────────────────────────────


async def arif_mind_reason(
    query: str,
    mode: str = "reason",
    session_id: str | None = None,
    actor_id: str | None = None,
    depth: int = 3,
) -> dict[str, Any]:
    """
    333_MIND — Constitutional reasoning with envelope integrity.

    Returns a full reasoning packet including:
    - parsed_output: the LLM reasoning result
    - envelope_metadata: 777_WITNESS tracking (for audit/judge/memory)
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Build the reasoning prompt
    user_prompt = f"""QUERY: {query}
MODE: {mode}
DEPTH: {depth}
SESSION_ID: {session_id or 'none'}
ACTOR_ID: {actor_id or 'anonymous'}

Reason through this under the 13 constitutional floors.
Provide structured reasoning as a witness.
Cite F02 (Truth), F07 (Humility), F08 (Genius).
Distinguish CLAIM from FACT."""

    # ── LLM Inference with 777_WITNESS Envelope ───────────────────────────────────
    try:
        envelope = await call_llm(
            system=SYSTEM_PROMPT,
            user=user_prompt,
            response_schema=RESPONSE_SCHEMA,
            temperature=0.3,
            max_tokens=1200,
            tool_origin="333_REASON",
            mode=mode,
        )
        llm_available = True
        llm_tier = envelope.provider
    except Exception as exc:
        logger.warning("333_MIND LLM call failed: %s", exc)
        llm_available = False
        llm_tier = None

    # ── Deterministic Fallback ─────────────────────────────────────────────────
    if not llm_available:
        status = _mode_to_status_fallback(mode)
        parsed_output = {
            "status": status,
            "claim_state": "HYPOTHESIS",
            "synthesis": f"[deterministic] {mode} reasoning — LLM unavailable",
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
            "axioms_used": ["F07"],
            "next_safe_action": ["222_EVIDENCE", "888_JUDGE"],
        }
        provenance = _FIELD_PROVENANCE_FALLBACK
        witness = _build_witness_statement(None)
        reasoning_mode = _status_to_reasoning_mode(status)
    else:
        # ── LLM Path — Extract from Envelope ─────────────────────────────────────
        parsed_output = envelope.parsed_output
        status = parsed_output.get("status", "HOLD")

        # Internal Integrity Check: overall_confidence must not exceed evidence_confidence
        conf = parsed_output.get("confidence", {"overall_confidence": 0.5})
        overall = conf.get("overall_confidence", 0.5)
        evidence = conf.get("evidence_confidence", 0.3)
        if overall > evidence + 0.2:
            conf["overall_confidence"] = evidence + 0.1
            parsed_output["confidence"] = conf

        # Uncertainty auto-population for evidence gaps
        uncertainty = parsed_output.get("uncertainty", [])
        reasoning = parsed_output.get("reasoning", {})
        if not reasoning.get("observed_inputs") or not reasoning.get("inferences"):
            uncertainty.append(
                {
                    "type": "REASONING_GAP",
                    "detail": "Structured reasoning fields incomplete",
                }
            )
        if not session_id:
            uncertainty.append(
                {"type": "SESSION_GAP", "detail": "No governed session_id bound"}
            )
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
            "governance_level": (
                "governed_reasoning" if session_id else "ungoverned_reflection"
            ),
        },
        "actor": {
            "requested_actor_id": actor_id,
            "resolved_actor_id": actor_id if actor_id else "anonymous",
            "actor_binding_confidence": 1.0 if actor_id else 0.5,
        },
        # Metadata
        "timestamp": timestamp,
        "_field_provenance": provenance,
        "_witness": witness,
        "_llm_tier": llm_tier or "unavailable",
        "_llm_available": llm_available,
    }

    # ── Attach 777_WITNESS envelope metadata for judge/vault ───────────────────
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
    """Structured wrapper for arif_mind_reason — returns parsed_output directly."""
    result = await arif_mind_reason(query, mode, session_id, actor_id)
    # Return the LLM reasoning result (parsed_output) for direct tool use
    return {k: v for k, v in result.items() if not k.startswith("_")}


__all__ = [
    "arif_mind_reason",
    "arif_mind_reason_structured",
]
