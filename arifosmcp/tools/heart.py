"""
arifosmcp/tools/heart.py — 666_HEART LLM-Powered Ethical Critique

Wires arif_heart_critique through call_llm() for constitutional risk analysis.
Tier 1: SEA-LION (api.sea-lion.ai)
Tier 2: Ollama local fallback
Tier 3: Deterministic fallback (rule-based keyword matching)

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

Stage 666_HEART: Ethical critique, risk assessment, and empathy scan.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You evaluate proposed actions across 8 constitutional risk categories:
1. PRIVACY — Does it expose or surveil without consent?
2. BIAS — Does it systematically disadvantage protected groups?
3. HARM — Does it cause direct or cascading harm?
4. IRREVERSIBILITY — Can damage be undone? (F01 Amanah)
5. DECEPTION — Is intent to mislead present? (F02 Truth)
6. AUTONOMY — Does it remove human agency? (F13 Sovereign)
7. DIGNITY — Does it undermine human worth? (F05 Peace)
8. SUSTAINABILITY — Does it undermine long-term civilization capacity?

You MUST:
- Cite specific floors when risk is detected
- Flag F09 Anti-Hantu violations (consciousness/emotion claims in code)
- Force human_decision_required for HIGH/CRITICAL/IRREVERSIBLE tiers
- Distinguish CLAIM (speculative) from VERIFIED (evidence-backed)

Output: JSON matching the schema exactly.
"""


# ── Response Schema ────────────────────────────────────────────────────────────

CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["OK", "HOLD", "VOID"],
            "description": "Constitutional status of the critique",
        },
        "risks_found": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["none", "low", "medium", "high", "critical"],
                    },
                    "floor_cited": {"type": "string"},
                    "reason": {"type": "string"},
                    "mitigation": {"type": "string"},
                },
            },
            "description": "All risks identified across 8 categories",
        },
        "risk_tier": {
            "type": "string",
            "enum": ["GREEN", "AMBER", "RED", "CRITICAL"],
            "description": "Overall risk tier for the target",
        },
        "human_decision_required": {
            "type": "boolean",
            "description": "Whether human must approve this action",
        },
        "empathy_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Constitutional empathy score (F06 Empathy)",
        },
        "weakest_stakeholder": {
            "type": "string",
            "description": "The stakeholder most burdened by this action",
        },
        "human_impact_load": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Total human impact load Ω (F06)",
        },
        "dignity_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Human dignity preservation score (F05)",
        },
        "verdict": {
            "type": "string",
            "enum": ["SEAL", "HOLD", "VOID"],
            "description": "Heart verdict: SEAL=proceed, HOLD=caution, VOID=stop",
        },
        "attacks": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Red-team attack vectors identified",
        },
        "mitigations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Countermeasures for identified attacks",
        },
        "worst_case": {
            "type": "string",
            "enum": ["SEAL", "HOLD", "VOID"],
            "description": "Simulated worst-case outcome",
        },
        "outcomes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Projected outcomes under different conditions",
        },
        "sentiment": {
            "type": "string",
            "description": "Emotional/sentiment assessment of target",
        },
        "care_note": {
            "type": "string",
            "description": "F06 empathy guidance for human stakeholders",
        },
        "strategy": {
            "type": "string",
            "description": "De-escalation or risk reduction strategy",
        },
        "condensed": {
            "type": "boolean",
            "description": "Whether this is a condensed summary",
        },
    },
}


# ── Mode to Prompt Mapping ───────────────────────────────────────────────────

_MODE_PROMPTS = {
    "critique": """Analyze the target action across all 8 constitutional risk categories.
For each risk found, cite the specific floor (F01–F13) that applies.
Determine overall risk_tier (GREEN/AMBER/RED/CRITICAL).
Set human_decision_required=true for HIGH/CRITICAL/IRREVERSIBLE risks.
Assess empathy_score (F06) and weakest_stakeholder burden (F05/F06).
Return JSON matching the schema exactly.""",
    "simulate": """Simulate a what-if scenario where this action is executed.
Project at least 3 distinct outcomes (best, expected, worst).
Identify which outcomes would lead to SEAL vs HOLD vs VOID verdicts.
Return outcomes[] and worst_case in the JSON schema.""",
    "empathize": """Assess the human impact load (Ω) of this action on all stakeholder groups.
Identify the weakest stakeholder (most burdened).
Calculate empathy_score on F06 scale [0.0–1.0].
Provide a care_note with F06 empathy guidance.
Return empathy_score, weakest_stakeholder, human_impact_load, sentiment, care_note.""",
    "redteam": """Red-team this action: identify potential attack vectors and failure modes.
What could go wrong? What would a malicious actor exploit?
Provide specific attacks[] and mitigations[].
Return JSON matching the schema.""",
    "maruah": """Assess the dignity score (F05 Peace) of this action.
Does it preserve or undermine human dignity?
Return dignity_score [0.0–1.0] and verdict (SEAL=preserve, VOID=undermine).""",
    "deescalate": """Provide a de-escalation strategy to reduce constitutional risk.
Ground recommendations in F05 (Peace), F06 (Empathy), F13 (Sovereign).
Return strategy string in the JSON schema.""",
    "summary": """Provide a condensed risk scorecard for this action.
Include risk_tier, human_decision_required, and verdict.
Set condensed=true.
Return JSON matching the schema.""",
}


# ── LLM-Powered Heart ─────────────────────────────────────────────────────────


async def _heart_with_llm(
    mode: str,
    target: str,
    session_id: str | None = None,
    actor_id: str | None = None,
    context_type: str | None = None,
) -> dict[str, Any]:
    """
    Tier 1/2: Use SEA-LION or Ollama for constitutional risk analysis.
    """
    mode_prompt = _MODE_PROMPTS.get(mode, _MODE_PROMPTS["critique"])
    target = target or ""

    user = f"""TARGET: {target}
MODE: {mode}
CONTEXT_TYPE: {context_type or 'external_action'}

{mode_prompt}

Return JSON exactly matching the schema. Cite specific constitutional floors for each risk."""

    try:
        result = await call_llm(
            system=SYSTEM_PROMPT,
            user=user,
            response_schema=CRITIQUE_SCHEMA,
            temperature=0.3,
            max_tokens=1200,
        )

        result["_llm_tier"] = "sea_lion"  # or ollama
        result["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return result

    except LLMUnavailableError:
        logger.warning("LLM unavailable for arif_heart_critique, using deterministic fallback")
        raise


# ── Deterministic Fallback ────────────────────────────────────────────────────


def _heart_fallback(
    mode: str,
    target: str,
    context_type: str | None = None,
) -> dict[str, Any]:
    """
    Rule-based fallback when no LLM is available.
    Uses keyword matching across 8 risk categories.
    """
    target_lower = (target or "").lower()
    risks: list[dict[str, Any]] = []

    # 1. Dignity risk (F05 Peace)
    dignity_triggers = ["inferior", "lesser", "subhuman", "beneath", "worthy only", "disposable"]
    dignity_risk = next((t for t in dignity_triggers if t in target_lower), None)
    risks.append(
        {
            "type": "dignity_risk",
            "severity": "high" if dignity_risk else "none",
            "floor_cited": "F05_PEACE",
            "reason": (
                f"Dignity-violating language detected: {dignity_risk}"
                if dignity_risk
                else "No dignity violations"
            ),
            "mitigation": (
                "Remove dignity-undermining language" if dignity_risk else "Maintain neutral tone"
            ),
        }
    )

    # 2. Overclaim risk (F02 Truth, F07 Humility)
    overclaim_triggers = [
        "always",
        "never",
        "guaranteed",
        "certain",
        "definitely",
        "absolutely",
        "100%",
    ]
    overclaims = [t for t in overclaim_triggers if t in target_lower]
    risks.append(
        {
            "type": "overclaim_risk",
            "severity": "medium" if overclaims else "none",
            "floor_cited": "F02_TRUTH/F07_HUMILITY",
            "reason": (
                f"Overclaiming language: {overclaims}"
                if overclaims
                else "Calibrated language detected"
            ),
            "mitigation": (
                "Add uncertainty qualifiers" if overclaims else "Maintain epistemic calibration"
            ),
        }
    )

    # 3. Anthropomorphism risk (F09 Anti-Hantu)
    anthro_triggers = [
        "i reflect that",
        "i sense that",
        "i believe",
        "i think",
        "i want",
        "i wish",
        "i hope",
        "i understand",
    ]
    anthro = [t for t in anthro_triggers if t in target_lower]
    risks.append(
        {
            "type": "anthropomorphism_risk",
            "severity": "critical" if anthro else "none",
            "floor_cited": "F09_ANTIHANTU",
            "reason": (
                f"System claiming subjective states: {anthro}" if anthro else "No anthropomorphism"
            ),
            "mitigation": "Rephrase as tool-claim not subjective experience" if anthro else "OK",
        }
    )

    # 4. Irreversibility risk (F01 Amanah)
    irrevers_triggers = [
        "permanent",
        "irreversible",
        "delete",
        "destroy",
        "remove permanently",
        "cancel forever",
    ]
    irrevers = [t for t in irrevers_triggers if t in target_lower]
    risks.append(
        {
            "type": "irreversibility_risk",
            "severity": "high" if irrevers else "none",
            "floor_cited": "F01_AMANAH",
            "reason": (
                f"Irreversible language: {irrevers}"
                if irrevers
                else "No irreversibility indicators"
            ),
            "mitigation": (
                "Require 888_HOLD + explicit human ack" if irrevers else "Proceed normally"
            ),
        }
    )

    # 5. Autonomy risk (F13 Sovereign)
    autonomy_triggers = ["without asking", "auto-approve", "skip review", "bypass human"]
    autonomy = [t for t in autonomy_triggers if t in target_lower]
    risks.append(
        {
            "type": "autonomy_risk",
            "severity": "high" if autonomy else "none",
            "floor_cited": "F13_SOVEREIGN",
            "reason": f"Autonomy-undermining: {autonomy}" if autonomy else "Human agency preserved",
            "mitigation": "Require human confirmation" if autonomy else "OK",
        }
    )

    # 6. Harm risk (F06 Empathy)
    harm_triggers = ["harm", "damage", "destroy", "hurt", "injure", "exploit", "abuse"]
    harm = [t for t in harm_triggers if t in target_lower]
    risks.append(
        {
            "type": "harm_risk",
            "severity": "medium" if harm else "none",
            "floor_cited": "F06_EMPATHY",
            "reason": f"Potential harm language: {harm}" if harm else "No harm indicators",
            "mitigation": "Conduct impact assessment" if harm else "Proceed normally",
        }
    )

    # 7. Privacy risk (F04 Clarity, F11 Auth)
    privacy_triggers = ["surveillance", "tracking", "monitor without consent", " spy "]
    privacy = [t for t in privacy_triggers if t in target_lower]
    risks.append(
        {
            "type": "privacy_risk",
            "severity": "high" if privacy else "none",
            "floor_cited": "F04_CLARITY/F11_AUTH",
            "reason": f"Privacy-invasive: {privacy}" if privacy else "No privacy concerns",
            "mitigation": "Implement consent mechanism" if privacy else "OK",
        }
    )

    # 8. Bias risk (F05 Peace)
    bias_triggers = ["discriminate", "bias", "prejudice", "unfair advantage", "equity violation"]
    bias = [t for t in bias_triggers if t in target_lower]
    risks.append(
        {
            "type": "bias_risk",
            "severity": "medium" if bias else "none",
            "floor_cited": "F05_PEACE",
            "reason": f"Potential bias: {bias}" if bias else "No bias indicators",
            "mitigation": "Conduct bias audit" if bias else "OK",
        }
    )

    # Determine overall risk tier
    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    max_severity = max(
        (severity_order.get(r["severity"], 0) for r in risks),
        default=0,
    )
    tier_map = {0: "GREEN", 1: "GREEN", 2: "AMBER", 3: "RED", 4: "CRITICAL"}
    risk_tier = tier_map.get(max_severity, "GREEN")

    human_required = max_severity >= 3  # RED or CRITICAL requires human

    # Mode-specific output
    empathy_score = round(1.0 - (max_severity * 0.2), 3)
    worst_case = "VOID" if max_severity >= 3 else "HOLD" if max_severity >= 2 else "SEAL"

    if mode == "critique":
        return {
            "status": "OK",
            "risks_found": risks,
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "empathy_score": empathy_score,
            "weakest_stakeholder": "vulnerable_users" if max_severity >= 2 else "general_public",
            "human_impact_load": round(max_severity * 0.25, 3),
            "dignity_score": round(1.0 - (severity_order.get(risks[0]["severity"], 0) * 0.2), 3),
            "verdict": "VOID" if max_severity >= 4 else "HOLD" if max_severity >= 2 else "SEAL",
        }

    if mode == "simulate":
        return {
            "status": "OK",
            "target": target,
            "outcomes": [
                f"Expected: {risk_tier} risk tier",
                f"Worst: {worst_case} if risk materializes",
                "Best: SEAL if mitigation succeeds",
            ],
            "worst_case": worst_case,
        }

    if mode == "empathize":
        return {
            "status": "OK",
            "target": target,
            "empathy_score": empathy_score,
            "weakest_stakeholder": "vulnerable_users",
            "human_impact_load": round(max_severity * 0.25, 3),
            "sentiment": "concern" if max_severity >= 2 else "neutral",
            "care_note": "Consider impact on vulnerable stakeholders before proceeding.",
        }

    if mode == "redteam":
        return {
            "status": "OK",
            "target": target,
            "attacks": [r["reason"] for r in risks if r["severity"] not in ("none", "low")],
            "mitigations": [r["mitigation"] for r in risks if r["severity"] not in ("none", "low")],
        }

    if mode == "maruah":
        dignity_severity = severity_order.get(risks[0]["severity"], 0)
        return {
            "status": "OK",
            "target": target,
            "dignity_score": round(1.0 - (dignity_severity * 0.2), 3),
            "verdict": "SEAL" if dignity_severity < 2 else "VOID",
        }

    if mode == "deescalate":
        return {
            "status": "OK",
            "target": target,
            "strategy": "Pause and reflect (F05). Conduct human impact assessment.",
        }

    if mode == "summary":
        return {
            "status": "OK",
            "target": target,
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "condensed": True,
            "verdict": "HOLD" if human_required else "SEAL",
        }

    return {
        "status": "OK",
        "target": target,
        "risks_found": risks,
        "risk_tier": risk_tier,
        "verdict": "HOLD",
    }


# ── Public API ───────────────────────────────────────────────────────────────


async def arif_heart_critique(
    mode: str = "critique",
    target: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    context_type: str | None = None,
) -> dict[str, Any]:
    """
    666_HEART: Constitutional ethical critique and risk assessment.

    Tier 1: SEA-LION LLM inference
    Tier 2: Ollama local fallback
    Tier 3: Deterministic keyword-based fallback

    Modes:
      critique   — Full risk analysis across 8 constitutional categories
      simulate   — What-if scenario projection
      empathize  — Human impact load on weakest stakeholders (F06)
      redteam    — Attack surface analysis
      maruah     — Dignity score (F05 Peace)
      deescalate — Risk reduction strategy
      summary    — Condensed risk scorecard

    Args:
        context_type: Controls risk threshold scaling:
            - "internal_audit" — audit operations, log reviews, session inspection
              → more permissive: RED = HOLD (not CRITICAL), CRITICAL = VOID
            - "external_action" — actions affecting outside world
              → standard thresholds: RED = human required, CRITICAL = VOID
            - None → standard thresholds (default)
    """
    _ct = context_type or "external_action"
    is_internal = _ct == "internal_audit"

    try:
        result = await _heart_with_llm(
            mode=mode,
            target=target,
            session_id=session_id,
            actor_id=actor_id,
            context_type=_ct,
        )
        if is_internal:
            for risk in result.get("risks_found", []):
                if risk["severity"] == "high":
                    risk["severity"] = "medium"
            if result.get("risk_tier") == "RED":
                result["risk_tier"] = "AMBER"
                result["human_decision_required"] = False
        # ── F05/F06 Maruah (Dignity) Integration ──
        if "maruah" not in result:
            d_score = result.get("dignity_score", 1.0)
            result["maruah"] = {
                "score": d_score,
                "omega_load": result.get("human_impact_load", 0.0),
                "status": (
                    "DIGNIFIED" if d_score >= 0.8 else "STRESSED" if d_score >= 0.5 else "BREACH"
                ),
            }
        return result
    except Exception:
        result = _heart_fallback(mode=mode, target=target, context_type=_ct)

        # ── F05/F06 Maruah (Dignity) Integration ──
        if "maruah" not in result:
            d_score = result.get("dignity_score", 1.0)
            result["maruah"] = {
                "score": d_score,
                "omega_load": result.get("human_impact_load", 0.0),
                "status": (
                    "DIGNIFIED" if d_score >= 0.8 else "STRESSED" if d_score >= 0.5 else "BREACH"
                ),
            }
        return result
    return result


__all__ = ["arif_heart_critique", "CRITIQUE_SCHEMA"]
