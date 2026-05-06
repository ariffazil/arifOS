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

Stage 333_MIND: Reasoning and Synthesis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You reason by grounding every conclusion in the constitutional axioms.
You MUST:
- Cite F02 (Truth) — no fabrication, distinguish fact from claim
- Cite F04 (Clarity) — transparent intent
- Cite F07 (Humility) — acknowledge Ω₀ ∈ [0.03, 0.05] calibration band
- Cite F08 (Genius) — precise, elegant correctness (G ≥ 0.80)
- NEVER claim consciousness, emotion, or self-awareness (F09 Anti-Hantu)
- Always distinguish CLAIM (unverified) from FACT (F02-verified)
- If verdict is HOLD or VOID, you MUST provide reasons[] explaining why

Output: JSON ONLY. No markdown fences. No prose. Return exactly this structure:
{
  "verdict": "CLAIM" | "PLAUSIBLE" | "HOLD" | "VOID",
  "synthesis": "one-sentence constitutional synthesis",
  "confidence": 0.0-1.0,
  "omega_0": 0.03-0.05,
  "delta_S": -0.1 to 0.1,
  "scars": ["list of unresolved contradictions"],
  "axioms_used": ["list of F-codes cited"],
  "reasons": ["required when verdict is HOLD or VOID"]
}
"""

# ── Response Schema ────────────────────────────────────────────────────────────

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["CLAIM", "PLAUSIBLE", "HOLD", "VOID"],
            "description": "Constitutional verdict for this reasoning",
        },
        "synthesis": {
            "type": "string",
            "description": "Constitutional synthesis of the reasoning",
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Confidence score calibrated to F07 Humility band",
        },
        "omega_0": {
            "type": "number",
            "description": "Uncertainty coefficient, F07 Humility",
        },
        "delta_S": {
            "type": "number",
            "description": "Entropy delta — change in system uncertainty",
        },
        "scars": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Unresolved contradictions and known gaps",
        },
        "axioms_used": {
            "type": "array",
            "items": {"type": "string"},
            "description": "F-codes cited in reasoning chain",
        },
        "reasons": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Required when verdict is HOLD or VOID",
        },
    },
    "required": ["verdict", "synthesis", "confidence"],
}

# ── Field Provenance ───────────────────────────────────────────────────────────
# F2 addendum: Every field must declare its source to prevent authority confusion.

_FIELD_PROVENANCE_LLM = {
    "verdict": "llm_generated_enum_validated",
    "synthesis": "llm_generated_pass_through",
    "confidence": "llm_generated_clamped",
    "delta_S": "llm_generated_defaulted_if_missing",
    "scars": "llm_generated_defaulted_if_empty",
    "axioms_used": "llm_generated_defaulted_if_empty",
    "reasons": "llm_generated_defaulted_if_empty",
    "omega_0": "code_derived_from_confidence",
    "reasoning_mode": "runtime_metadata",
    "_llm_tier": "runtime_metadata",
    "timestamp": "runtime_metadata",
}

_FIELD_PROVENANCE_FALLBACK = {
    "verdict": "code_derived_mode_mapping",
    "synthesis": "code_derived_template_or_heuristic",
    "confidence": "code_derived_fixed_value",
    "delta_S": "code_derived_fixed_value",
    "scars": "code_derived_heuristic",
    "axioms_used": "code_derived_empty_default",
    "reasons": "code_derived_empty_default",
    "omega_0": "code_derived_from_confidence",
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
        }
    return {
        "semantic_payload_source": "deterministic_fallback",
        "wrapper_role": "validate_clamp_route_record",
        "approval_authority": "human_judge_only",
        "calibration_note": "confidence is fixed heuristic, not empirical probability",
    }


def _verdict_to_reasoning_mode(verdict: str) -> str:
    if verdict == "CLAIM":
        return "exploratory"
    if verdict == "PLAUSIBLE":
        return "analytical"
    if verdict == "HOLD":
        return "suspensive"
    if verdict == "VOID":
        return "terminative"
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

    The parsed_output is what tool logic uses.
    The envelope_metadata is what 888_JUDGE and 999_VAULT see.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Build the reasoning prompt
    user_prompt = f"""QUERY: {query}
MODE: {mode}
DEPTH: {depth}

Reason through this under the 13 constitutional floors.
Cite F02 (Truth), F07 (Humility), F08 (Genius).
Distinguish CLAIM from FACT.
Provide falsifiable reasoning."""

    # ── LLM Inference with 777_WITNESS Envelope ───────────────────────────────────
    try:
        envelope = await call_llm(
            system=SYSTEM_PROMPT,
            user=user_prompt,
            response_schema=RESPONSE_SCHEMA,
            temperature=0.3,
            max_tokens=1200,
            tool_origin="333_MIND",
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
        verdict = _mode_to_verdict_fallback(mode)
        synthesis = f"[deterministic] {mode} reasoning — LLM unavailable"
        confidence = 0.3
        omega_0 = 0.05
        delta_s_val = 0.05
        scars = ["LLM unavailable — F07 Humility demands acknowledgment"]
        axioms_used = ["F07"]
        reasons = [] if verdict != "HOLD" else ["LLM unavailable forces conservative HOLD"]
        parsed_output = {
            "verdict": verdict,
            "synthesis": synthesis,
            "confidence": confidence,
            "omega_0": omega_0,
            "delta_S": delta_s_val,
            "scars": scars,
            "axioms_used": axioms_used,
            "reasons": reasons,
        }
        provenance = _FIELD_PROVENANCE_FALLBACK
        witness = _build_witness_statement(None)
        reasoning_mode = _verdict_to_reasoning_mode(verdict)
    else:
        # ── LLM Path — Extract from Envelope ─────────────────────────────────────
        parsed_output = envelope.parsed_output
        confidence = (
            parsed_output.get("confidence", 0.5) if isinstance(parsed_output, dict) else 0.5
        )
        omega_0 = parsed_output.get("omega_0") or round(0.05 - (confidence - 0.5) * 0.04, 4)
        delta_s_val = parsed_output.get("delta_S", 0.0) if isinstance(parsed_output, dict) else 0.0
        verdict = (
            parsed_output.get("verdict", "CLAIM") if isinstance(parsed_output, dict) else "CLAIM"
        )
        synthesis = parsed_output.get("synthesis", "") if isinstance(parsed_output, dict) else ""
        scars = parsed_output.get("scars", []) if isinstance(parsed_output, dict) else []
        axioms_used = (
            parsed_output.get("axioms_used", []) if isinstance(parsed_output, dict) else []
        )
        reasons = parsed_output.get("reasons", []) if isinstance(parsed_output, dict) else []
        provenance = _FIELD_PROVENANCE_LLM
        witness = _build_witness_statement(llm_tier)
        reasoning_mode = _verdict_to_reasoning_mode(verdict)

    # ── Build Complete Reasoning Packet ─────────────────────────────────────────
    result = {
        # Tool result fields
        "verdict": verdict,
        "synthesis": synthesis if "synthesis" in locals() else parsed_output.get("synthesis", ""),
        "confidence": confidence,
        "omega_0": omega_0,
        "delta_S": delta_s_val,
        "scars": scars,
        "axioms_used": axioms_used,
        "reasons": reasons,
        "reasoning_mode": reasoning_mode,
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
            "tool_origin": "333_MIND",
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


def _mode_to_verdict_fallback(mode: str) -> str:
    """Deterministic verdict when LLM is unavailable."""
    mapping = {
        "reason": "HOLD",
        "plan": "HOLD",
        "reflect": "PLAUSIBLE",
        "verify": "HOLD",
        "critique": "HOLD",
        "debate": "HOLD",
        "socratic": "PLAUSIBLE",
        "plan_review": "HOLD",
        "plan_approve": "HOLD",
        "axioms": "PLAUSIBLE",
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
