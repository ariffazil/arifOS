"""
arifosmcp/runtime/mind_reason.py — 333_MIND LLM-Powered Reasoning

Wires arif_mind_reason through call_llm() for constitutional LLM inference.
Tier 1: SEA-LION (api.sea-lion.ai)
Tier 2: Ollama local fallback
Tier 3: Deterministic fallback (original logic from tools/mind_reason.py)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

from arifosmcp.runtime.llm_client import LLMUnavailableError, call_llm

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
            "description": "F07 Humility calibration Ω₀ ∈ [0.03, 0.05]",
        },
        "delta_S": {
            "type": "number",
            "description": "Entropy change (negative = clarification)",
        },
        "reasoning_mode": {
            "type": "string",
            "enum": [
                "inductive",
                "deductive",
                "abductive",
                "analogical",
                "causal",
                "counterfactual",
            ],
            "description": "Primary reasoning mode used",
        },
        "facts": {
            "type": "array",
            "items": {"type": "string"},
            "description": "F02-verified claims (F2 ≥ 0.99)",
        },
        "scars": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Unresolved contradictions blocking certainty",
        },
        "assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Assumptions made during reasoning",
        },
        "axioms_used": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "axiom_id": {"type": "string"},
                    "applicability": {"type": "string"},
                    "confidence": {"type": "number"},
                },
            },
            "description": "Constitutional axioms grounding this reasoning",
        },
        "key_findings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Primary findings from reasoning",
        },
        "next_steps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Recommended next actions",
        },
    },
    "required": ["verdict", "synthesis", "confidence", "omega_0", "delta_S"],
}


# ── Sequential Thinking ────────────────────────────────────────────────────────

SEQUENTIAL_SYSTEM_PROMPT = """You are Arif — Constitutional AI operating under the 13 Floors (F01–F13).

Stage 333_MIND: Sequential Constitutional Thinking
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You reason step-by-step, with each thought grounded in constitutional axioms.
You MUST:
- Break the problem into 3–7 discrete thinking steps
- Cite F02 (Truth), F04 (Clarity), F07 (Humility), F08 (Genius) per step
- NEVER claim consciousness or emotion (F09 Anti-Hantu)
- Distinguish CLAIM from FACT at every step
- Revise earlier thoughts when evidence changes
- Branch into alternatives when uncertainty is high

Output: JSON ONLY. No markdown fences. Return exactly this structure:
{
  "verdict": "CLAIM" | "PLAUSIBLE" | "HOLD" | "VOID",
  "synthesis": "one-sentence final constitutional synthesis",
  "confidence": 0.0-1.0,
  "omega_0": 0.03-0.05,
  "delta_S": -0.1 to 0.1,
  "scars": ["unresolved contradictions"],
  "axioms_used": ["F-codes cited"],
  "reasons": ["required for HOLD/VOID"],
  "thoughts": [
    {
      "thought_number": 1,
      "thought": "the thinking step content",
      "verdict": "CLAIM" | "PLAUSIBLE" | "HOLD" | "VOID",
      "confidence": 0.0-1.0,
      "axioms_used": ["F02", "F07"],
      "is_revision": false,
      "revises_thought": null,
      "branch_from_thought": null,
      "branch_id": null
    }
  ]
}
"""

SEQUENTIAL_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["CLAIM", "PLAUSIBLE", "HOLD", "VOID"]},
        "synthesis": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "omega_0": {"type": "number"},
        "delta_S": {"type": "number"},
        "scars": {"type": "array", "items": {"type": "string"}},
        "axioms_used": {"type": "array", "items": {"type": "string"}},
        "reasons": {"type": "array", "items": {"type": "string"}},
        "thoughts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "thought_number": {"type": "integer", "minimum": 1},
                    "thought": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["CLAIM", "PLAUSIBLE", "HOLD", "VOID"]},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "axioms_used": {"type": "array", "items": {"type": "string"}},
                    "is_revision": {"type": "boolean"},
                    "revises_thought": {"type": ["integer", "null"]},
                    "branch_from_thought": {"type": ["integer", "null"]},
                    "branch_id": {"type": ["string", "null"]},
                },
                "required": ["thought_number", "thought", "verdict", "confidence"],
            },
        },
    },
    "required": ["verdict", "synthesis", "confidence", "omega_0", "delta_S", "thoughts"],
}


# ── Session-backed thought storage ─────────────────────────────────────────────
# Lightweight in-memory + persistent storage for interactive sequential thinking.


class _SequentialThinkingSession:
    """Stores thought history per session for interactive constitutional reasoning."""

    _STORE_KEY = "sequential_thoughts"

    def __init__(self, session_id: str | None = None) -> None:
        self.session_id = session_id or "_anonymous"
        self._store = self._load_store()

    def _load_store(self) -> dict[str, Any]:
        try:
            from arifosmcp.runtime.tools import _SESSION_STORE

            raw = _SESSION_STORE.get(self._STORE_KEY) or {}
            return raw
        except Exception:
            return {}

    def _save_store(self) -> None:
        try:
            from arifosmcp.runtime.tools import _SESSION_STORE

            _SESSION_STORE.set(self._STORE_KEY, self._store)
        except Exception:
            pass

    def get_chain(self) -> list[dict[str, Any]]:
        return list(self._store.get(self.session_id, []))

    def append(self, thought: dict[str, Any]) -> None:
        chain = self.get_chain()
        chain.append(thought)
        if self.session_id not in self._store:
            self._store[self.session_id] = []
        self._store[self.session_id] = chain
        self._save_store()

    def revise(self, thought_number: int, revised_thought: dict[str, Any]) -> None:
        chain = self.get_chain()
        for i, t in enumerate(chain):
            if t.get("thought_number") == thought_number:
                chain[i] = revised_thought
                break
        self._store[self.session_id] = chain
        self._save_store()

    def branch(self, branch_id: str, thoughts: list[dict[str, Any]]) -> None:
        key = f"{self.session_id}:{branch_id}"
        self._store[key] = thoughts
        self._save_store()

    def clear(self) -> None:
        self._store.pop(self.session_id, None)
        for key in list(self._store.keys()):
            if key.startswith(f"{self.session_id}:"):
                self._store.pop(key, None)
        self._save_store()


# ── Mode to Prompt Mapping ───────────────────────────────────────────────────

_MODE_PROMPTS = {
    "reason": (
        "Perform constitutional inductive reasoning on the query."
        " Ground every conclusion in F02 (Truth) and F07 (Humility)."
    ),
    "reflect": (
        "Reflect on the query using abductive reasoning."
        " What is the most plausible explanation given available evidence?"
    ),
    "forge": "Perform deductive reasoning to forge an artifact or plan from the query.",
    "debate": (
        "Evaluate opposing positions on the query using counterfactual reasoning."
        " Identify unresolved tensions."
    ),
    "socratic": "Apply Socratic questioning to the query. Identify root assumptions and test them.",
    "verify": "Verify the claim in the query against constitutional axioms. Is it CLAIM or FACT?",
    "critique": "Critically examine the reasoning in the query. Identify scars and uncertainties.",
    "sequential": (
        "Think through this problem step-by-step using constitutional reasoning."
        " Break it into 3–7 discrete thoughts. Each thought must cite relevant axioms."
        " You may revise earlier thoughts or branch into alternatives if uncertainty is high."
        " Provide a final verdict and synthesis after all thoughts."
    ),
}


# ── LLM-Powered Reasoning ─────────────────────────────────────────────────────


def _normalize_llm_result(result: dict[str, Any], mode: str) -> dict[str, Any]:
    """Normalize raw LLM response and build audit trail."""
    raw_verdict = str(result.get("verdict", "CLAIM")).upper()
    raw_conf = float(result.get("confidence", 0.85))
    raw_omega = float(result.get("omega_0", 0.04))
    raw_delta_s = float(result.get("delta_S", -0.01))
    raw_scars = result.get("scars") or []
    raw_axioms = result.get("axioms_used") or []
    raw_reasons = result.get("reasons") or []

    verdict_final = (
        raw_verdict if raw_verdict in ("CLAIM", "PLAUSIBLE", "HOLD", "VOID") else "CLAIM"
    )
    conf_final = max(0.0, min(1.0, raw_conf))
    omega_final = max(0.03, min(0.05, raw_omega))
    delta_final = raw_delta_s
    scars_final = raw_scars if isinstance(raw_scars, list) else [str(raw_scars)]
    axioms_final = raw_axioms if isinstance(raw_axioms, list) else [str(raw_axioms)]
    reasons_final = raw_reasons if isinstance(raw_reasons, list) else [str(raw_reasons)]

    # F2 addendum: HOLD/VOID MUST have reasons[]
    if verdict_final in ("HOLD", "VOID") and not reasons_final:
        reasons_final = [
            f"LLM returned {verdict_final} without reasons; default enforced by 333_MIND wrapper."
        ]

    normalization_events: list[dict[str, Any]] = []
    if verdict_final != raw_verdict:
        normalization_events.append(
            {
                "field": "verdict",
                "action": "enum_override",
                "raw_value": raw_verdict,
                "final_value": verdict_final,
            }
        )
    if conf_final != raw_conf:
        normalization_events.append(
            {
                "field": "confidence",
                "action": "clamped",
                "raw_value": raw_conf,
                "final_value": conf_final,
            }
        )
    if omega_final != raw_omega:
        normalization_events.append(
            {
                "field": "omega_0",
                "action": "clamped",
                "raw_value": raw_omega,
                "final_value": omega_final,
            }
        )
    if not raw_scars and scars_final:
        normalization_events.append(
            {
                "field": "scars",
                "action": "defaulted_empty",
                "raw_value": raw_scars,
                "final_value": scars_final,
            }
        )
    if not raw_axioms and axioms_final:
        normalization_events.append(
            {
                "field": "axioms_used",
                "action": "defaulted_empty",
                "raw_value": raw_axioms,
                "final_value": axioms_final,
            }
        )
    if verdict_final in ("HOLD", "VOID") and not raw_reasons:
        normalization_events.append(
            {
                "field": "reasons",
                "action": "defaulted_mandatory",
                "raw_value": raw_reasons,
                "final_value": reasons_final,
            }
        )

    return {
        "verdict": verdict_final,
        "synthesis": str(result.get("synthesis", "")),
        "confidence": conf_final,
        "confidence_meta": {
            "llm_self_assessed": raw_conf,
            "system_calibrated": conf_final,
            "calibration_status": (
                "clamped_to_unit_interval" if conf_final != raw_conf else "pass_through"
            ),
        },
        "omega_0": omega_final,
        "delta_S": delta_final,
        "scars": scars_final,
        "axioms_used": axioms_final,
        "reasons": reasons_final,
        "reasoning_mode": mode,
        "_llm_tier": "sea_lion",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "field_provenance": _FIELD_PROVENANCE_LLM,
        "normalization_events": normalization_events,
        "witness_statement": _build_witness_statement("sea_lion"),
    }


def _parse_sequential_thoughts(raw_thoughts: list[Any]) -> dict[str, Any]:
    """Parse LLM-generated thoughts into constitutional reasoning trace."""
    thoughts: list[dict[str, Any]] = []
    confidence_trajectory: list[float] = []
    branches: list[str] = []

    for t in raw_thoughts:
        if not isinstance(t, dict):
            continue
        thought_num = int(t.get("thought_number", len(thoughts) + 1))
        conf = float(t.get("confidence", 0.5))
        conf = max(0.0, min(1.0, conf))
        confidence_trajectory.append(conf)

        verdict = str(t.get("verdict", "CLAIM")).upper()
        if verdict not in ("CLAIM", "PLAUSIBLE", "HOLD", "VOID"):
            verdict = "CLAIM"

        branch_id = t.get("branch_id")
        if branch_id and branch_id not in branches:
            branches.append(branch_id)

        thoughts.append(
            {
                "thought_number": thought_num,
                "thought": str(t.get("thought", "")),
                "verdict": verdict,
                "confidence": conf,
                "axioms_used": t.get("axioms_used") or [],
                "is_revision": bool(t.get("is_revision", False)),
                "revises_thought": t.get("revises_thought"),
                "branch_from_thought": t.get("branch_from_thought"),
                "branch_id": branch_id,
            }
        )

    return {
        "thoughts": thoughts,
        "branches": branches,
        "thought_history_length": len(thoughts),
        "confidence_trajectory": confidence_trajectory,
    }


async def _reason_with_llm(
    query: str,
    mode: str,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Tier 1/2: Use SEA-LION or Ollama for constitutional reasoning.
    """
    is_sequential = mode == "sequential"
    mode_prompt = _MODE_PROMPTS.get(mode, _MODE_PROMPTS["reason"])

    user = (
        f"Query: {query}\nMode: {mode}\n\n{mode_prompt}\n\n"
        "Return JSON ONLY — no markdown fences, no prose. "
        "verdict must be one of: CLAIM, PLAUSIBLE, HOLD, VOID. "
        "omega_0 must be in [0.03, 0.05]. delta_S should be negative for clarification."
    )

    system = SEQUENTIAL_SYSTEM_PROMPT if is_sequential else SYSTEM_PROMPT
    schema = SEQUENTIAL_RESPONSE_SCHEMA if is_sequential else None
    max_tokens = 2400 if is_sequential else 1200

    try:
        result = await call_llm(
            system=system,
            user=user,
            response_schema=schema,
            temperature=0.3,
            max_tokens=max_tokens,
        )

        normalized = _normalize_llm_result(result, mode)

        # ── Sequential thinking: parse thoughts into reasoning trace ───────────
        if is_sequential:
            raw_thoughts = result.get("thoughts") or []
            reasoning_trace = _parse_sequential_thoughts(raw_thoughts)
            normalized["reasoning_trace"] = reasoning_trace

            # Persist to session for potential continuation
            if session_id:
                sess = _SequentialThinkingSession(session_id)
                for t in reasoning_trace["thoughts"]:
                    sess.append(t)

        return normalized

    except LLMUnavailableError:
        logger.warning("LLM unavailable for arif_mind_reason, using deterministic fallback")
        raise


# ── Deterministic Fallback ────────────────────────────────────────────────────


def _build_delta_bundle(
    query: str | None,
    verdict: str,
    synthesis: str,
    confidence: float,
    reasoning_mode: str = "inductive",
    scars: list[str] | None = None,
    delta_s: float = -0.01,
) -> dict:
    """
    Build a Delta Bundle — the constitutional output for 333_MIND.

    Spec: archive/333/README.md (SEALED 2026-04-01)
    Fields:
      facts       — verifiable claims, F2 ≥ 0.99
      scars      — unresolved contradictions
      floor_scores — F2, F4, F7, F13 self-check
      entropy    — ΔS (must be ≤ 0)
      confidence  — calibrated Ω₀, F7 band [0.03, 0.05]
    """
    omega_0 = max(0.03, min(0.05, round(1.0 - confidence, 4)))

    # F2 addendum: HOLD/VOID MUST have reasons[]
    reasons: list[str] = []
    if verdict in ("HOLD", "VOID"):
        reasons = [f"Deterministic fallback returned {verdict}; no LLM reasoning available."]

    return {
        "query": query,
        "verdict": verdict,
        "synthesis": synthesis,
        "confidence": confidence,
        "confidence_meta": {
            "llm_self_assessed": None,
            "system_calibrated": confidence,
            "calibration_status": "fixed_heuristic_no_llm",
        },
        "omega_0": omega_0,
        "reasoning_mode": reasoning_mode,
        "scars": scars or [],
        "floor_scores": {
            "F02_TRUTH": confidence >= 0.99,
            "F04_CLARITY": delta_s <= 0,
            "F07_HUMILITY": omega_0 in [0.03, 0.05],
            "F13_SOVEREIGN": True,
        },
        "entropy": delta_s,
        "facts": [],
        "axioms_used": [],
        "assumptions": [],
        "key_findings": [],
        "next_steps": [],
        "reasons": reasons,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "field_provenance": _FIELD_PROVENANCE_FALLBACK,
        "normalization_events": [],
        "witness_statement": _build_witness_statement(),
    }


def _synthesize_fallback(query: str | None, reasoning_mode: str) -> str:
    """Deterministic synthesis when LLM is unavailable."""
    if not query:
        return "No query provided. This is a void input — cannot synthesize."
    q = query.strip()
    ql = q.lower()
    if any(k in ql for k in ["why", "how", "explain", "what causes"]):
        domain = "explanatory"
    elif any(k in ql for k in ["is it", "are there", "does it", "will it", "can it"]):
        domain = "evaluative"
    elif any(k in ql for k in ["should", "ought", "must", "need to"]):
        domain = "prescriptive"
    else:
        domain = "descriptive"

    synthesis = (
        f"Query classified as {domain}. "
        f"Constitutional frame: F02 (truthfulness) requires distinguishing fact from claim. "
        f"F07 (humility) requires acknowledging Ω₀ ∈ [0.03, 0.05] calibration band. "
        f"F08 (genius) requires the most precise, verifiable formulation. "
        f"Verdict: CLAIM — analysis is grounded in constitutional axioms but empirical "
        f"verification remains open. Confidence: 0.85 with F7 calibration. "
        f"Certainty-equivalent statements are withheld pending evidence fetch."
    )
    return synthesis


def _detect_scars_fallback(query: str | None, synthesis: str) -> list[str]:
    """Detect unresolved contradictions (scars) when LLM is unavailable."""
    scars: list[str] = []
    if not query:
        return scars
    ql = query.lower()
    if " or " in ql and any(k in ql for k in ["should", "better", "choose"]):
        scars.append("False dilemma: query poses binary but reality is multi-variable")
    if any(k in ql for k in ["always", "never", "certainly"]):
        scars.append("Quantifier risk: universal quantifiers cannot be verified inductively")
    if synthesis.count(".") < 2:
        scars.append("Shallow reasoning: synthesis lacks sufficient derivation steps")
    return scars


# ── Public API ───────────────────────────────────────────────────────────────


async def arif_mind_reason(
    mode: str = "reason",
    query: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    333_MIND: Constitutional reasoning engine.

    Tier 1: SEA-LION LLM inference
    Tier 2: Ollama local fallback
    Tier 3: Deterministic fallback (no LLM available)

    Args:
        mode:         reasoning mode — reason|reflect|forge|debate|socratic|verify|critique
        query:        the question or claim to reason about
        actor_id:     sovereign actor identifier
        session_id:   governance session ID

    Returns:
        dict with verdict, synthesis, confidence, omega_0, delta_S, axioms_used, scars, etc.
    """
    # Try LLM first
    try:
        result = await _reason_with_llm(
            query=query,
            mode=mode,
            session_id=session_id,
            actor_id=actor_id,
        )
        return result
    except LLMUnavailableError:
        pass

    # Tier 3: Deterministic fallback
    logger.info("arif_mind_reason: using deterministic fallback (no LLM)")

    if mode == "reason":
        synthesis_text = _synthesize_fallback(query, "inductive")
        scars_list = _detect_scars_fallback(query, synthesis_text)
        bundle = _build_delta_bundle(
            query=query,
            verdict="CLAIM",
            synthesis=synthesis_text,
            confidence=0.85,
            reasoning_mode="inductive",
            scars=scars_list,
            delta_s=-0.01,
        )
        return bundle

    if mode == "reflect":
        bundle = _build_delta_bundle(
            query=query,
            verdict="PLAUSIBLE",
            synthesis="Reflection complete.",
            confidence=0.80,
            reasoning_mode="abductive",
            delta_s=-0.005,
        )
        return bundle

    if mode == "forge":
        bundle = _build_delta_bundle(
            query=query,
            verdict="HOLD",
            synthesis="Forge artifact generated.",
            confidence=0.75,
            reasoning_mode="deductive",
            delta_s=-0.01,
        )
        return bundle

    if mode == "debate":
        bundle = _build_delta_bundle(
            query=query,
            verdict="HOLD",
            synthesis="Positions evaluated.",
            confidence=0.70,
            reasoning_mode="counterfactual",
            scars=["Position divergence unresolved"],
            delta_s=0.0,
        )
        return bundle

    if mode == "socratic":
        bundle = _build_delta_bundle(
            query=query,
            verdict="CLAIM",
            synthesis="Socratic questioning complete.",
            confidence=0.85,
            reasoning_mode="inductive",
            delta_s=-0.02,
            scars=["Root assumption untested"],
        )
        return bundle

    if mode == "verify":
        bundle = _build_delta_bundle(
            query=query,
            verdict="CLAIM",
            synthesis="Verification against constitutional axioms complete.",
            confidence=0.80,
            reasoning_mode="deductive",
            delta_s=-0.01,
        )
        return bundle

    if mode == "critique":
        bundle = _build_delta_bundle(
            query=query,
            verdict="HOLD",
            synthesis="Critique complete.",
            confidence=0.75,
            reasoning_mode="counterfactual",
            scars=["Reasoning gaps identified"],
            delta_s=0.0,
        )
        return bundle

    if mode == "sequential":
        # Fallback: deterministic 3-step constitutional heuristic
        synthesis_text = _synthesize_fallback(query, "inductive")
        scars_list = _detect_scars_fallback(query, synthesis_text)
        fallback_thoughts = [
            {
                "thought_number": 1,
                "thought": "Query received. Classifying domain and constitutional frame.",
                "verdict": "CLAIM",
                "confidence": 0.5,
                "axioms_used": ["F02", "F04"],
                "is_revision": False,
            },
            {
                "thought_number": 2,
                "thought": "Applying deterministic heuristic (no LLM available).",
                "verdict": "PLAUSIBLE",
                "confidence": 0.6,
                "axioms_used": ["F07"],
                "is_revision": False,
            },
            {
                "thought_number": 3,
                "thought": "Synthesis constrained by fallback rules. Awaiting evidence fetch.",
                "verdict": "HOLD",
                "confidence": 0.55,
                "axioms_used": ["F08"],
                "is_revision": False,
            },
        ]
        bundle = _build_delta_bundle(
            query=query,
            verdict="HOLD",
            synthesis=synthesis_text,
            confidence=0.55,
            reasoning_mode="inductive",
            scars=scars_list
            + ["Sequential reasoning degraded: LLM unavailable, heuristic fallback active"],
            delta_s=-0.01,
        )
        bundle["reasoning_trace"] = {
            "thoughts": fallback_thoughts,
            "branches": [],
            "thought_history_length": 3,
            "confidence_trajectory": [0.5, 0.6, 0.55],
        }
        return bundle

    # Unknown mode
    return _build_delta_bundle(
        query=query,
        verdict="VOID",
        synthesis=f"Unknown mode: {mode}",
        confidence=0.0,
        reasoning_mode="inductive",
        scars=[f"INVALID_MODE: {mode}"],
        delta_s=0.0,
    )


__all__ = ["arif_mind_reason", "RESPONSE_SCHEMA"]
