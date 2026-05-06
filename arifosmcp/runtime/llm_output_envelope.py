"""
arifosmcp/runtime/llm_output_envelope.py — 777_WITNESS

LLM output envelope — the single constitutional membrane for all AI output.

Eureka principle:
  "LLM output is not intelligence; it is entropy-shaped testimony.
   Treat it as witnessed material, not truth, not command, not verdict."

Every LLM response enters arifOS wrapped in this envelope.
No raw LLM text passes directly into judgment, memory, vault, or external action.

Envelope stage placement (by arifOS floor):
  333_MIND  → ✅ Reasoning witness
  444r_REPLY → ✅ Language shaping
  666_HEART  → ✅ Risk witness
  555_MEMORY → ⚠️ Only after envelope
  888_JUDGE  → ⚠️ Read-only witness
  999_VAULT  → ⚠️ Hash only / final record
  010_FORGE  → ❌ Never directly

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── Evidence Level Hierarchy ───────────────────────────────────────────────────
# F2 Truth: evidence must be verifiable. Claim hierarchy:
EVIDENCE_LEVELS = Literal["claimed", "cited", "verified"]
AUTHORITY_LEVELS = Literal[
    "instrument_only",  # LLM output — requires human judgment
    "advisory",  # Tool output — informational, human may override
    "governed",  # Floor-checked tool — passes through
    "sovereign",  # Sealed verdict — human decision final
]


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════


class LLMOutputEnvelope(BaseModel):
    """
    The ONE legal form of AI output in arifOS.

    Every LLM response — from SEA-LION, Ollama, or any provider — is
    wrapped here before it enters any tool, floor, or judgment layer.

    Fields:
        provider       — "sea_lion" | "ollama" | "deterministic"
        model          — exact model identifier
        tool_origin    — which tool called the LLM
        mode           — the cognitive mode of the call
        raw_output     — the verbatim LLM output (unmodified)
        raw_output_hash — SHA-256 of raw_output (integrity + tamper evidence)
        parsed_output  — JSON dict extracted from raw_output
        schema_valid   — did parsed_output parse as valid JSON?
        confidence_claimed — LLM's self-reported confidence (NOT verified truth)
        evidence_level — claimed | cited | verified (F2 Truth calibration)
        uncertainty    — list of known unknowables (F7 Humility)
        risk_flags     — detected risk categories (F6/F9/F13)
        prompt_hash    — SHA-256 of the prompt (audit trail)
        timestamp      — ISO-8601 UTC
        human_decision_required — True if evidence_level < cited
                                 or risk_flags contains HIGH/CRITICAL
        authority_level — instrument_only (LLM outputs always)
        wrapper_version — "777_WITNESS_v1.0"
    """

    provider: str
    model: str
    tool_origin: str
    mode: str

    raw_output: str
    raw_output_hash: str  # sha256:hex — tamper evidence
    parsed_output: dict[str, Any]

    schema_valid: bool = False
    confidence_claimed: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence_level: EVIDENCE_LEVELS = "claimed"

    uncertainty: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    injection_detected: bool = False  # F12 INJECTION scan
    latency_ms: float = 0.0  # Round-trip cost in ms for thermodynamic tracking

    prompt_hash: str
    timestamp: str

    human_decision_required: bool = False
    authority_level: Literal["instrument_only", "advisory", "governed", "sovereign"] = (
        "instrument_only"
    )
    wrapper_version: str = "777_WITNESS_v1.0"

    model_config = {"frozen": False, "use_enum_values": True}


# ── Backward-compat alias (kept for reference, use Literal above) ────────────────


class AuthorityLevels(str):
    """Deprecated — use string literals directly. Kept for compat callers."""

    INSTRUMENT_ONLY = "instrument_only"
    ADVISORY = "advisory"
    GOVERNED = "governed"
    SOVEREIGN = "sovereign"

    @classmethod
    def values(cls) -> list[str]:
        return [cls.INSTRUMENT_ONLY, cls.ADVISORY, cls.GOVERNED, cls.SOVEREIGN]


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE FACTORY
# ═══════════════════════════════════════════════════════════════════════════════


def _sha256(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()[:16]}"


def _assess_uncertainty_and_risk(
    parsed: dict[str, Any],
    tool_origin: str,
    mode: str,
    injection_detected: bool = False,
) -> tuple[list[str], list[str]]:
    """
    F7 Humility: derive uncertainty signals from output shape.
    F6/F9/F13: flag risk categories.

    Returns (uncertainty_list, risk_flags_list).
    """
    uncertainty: list[str] = []
    risk_flags: list[str] = []

    confidence = parsed.get("confidence")
    if confidence is None:
        uncertainty.append("confidence_field_missing")
    elif isinstance(confidence, int | float):
        if confidence > 0.95:
            uncertainty.append("confidence_unrealistically_high_F07")
        elif confidence < 0.1:
            uncertainty.append("confidence_very_low_acknowledged")

    verdict = parsed.get("verdict", parsed.get("status", ""))
    if isinstance(verdict, str):
        if verdict in ("VOID", "HOLD"):
            uncertainty.append(f"verdict_{verdict}_escalated")
        if verdict in ("CLAIM", "void", "hold"):
            risk_flags.append("LOW_CONFIDENCE_VERDICT")

    reasons = parsed.get("reasons", [])
    if not reasons and verdict in ("HOLD", "VOID"):
        uncertainty.append("HOLD_VOID_without_explicit_reasons")

    empathy_score = parsed.get("empathy_score")
    if empathy_score is not None and empathy_score < 0.3:
        risk_flags.append("LOW_EMPATHY_SCORE_F06")

    human_required = parsed.get("human_decision_required")
    if human_required is True:
        risk_flags.append("HUMAN_DECISION_REQUIRED")

    risks_found = parsed.get("risks_found", [])
    if risks_found:
        for r in risks_found:
            sev = r.get("severity", "low") if isinstance(r, dict) else "low"
            if sev in ("high", "critical"):
                r_type = r.get("type", "UNKNOWN") if isinstance(r, dict) else "UNKNOWN"
                risk_flags.append(f"RISK_{sev.upper()}_{r_type}")

    delta_s_val = parsed.get("delta_S")
    if delta_s_val is not None:
        if isinstance(delta_s_val, int | float) and abs(delta_s_val) > 0.3:
            uncertainty.append("high_entropy_delta_S")
        elif isinstance(delta_s_val, int | float) and abs(delta_s_val) < 0.01:
            uncertainty.append("zero_entropy_delta_S_unusual")

    # F12 INJECTION — if scan detected in LLM output, escalate immediately
    if injection_detected:
        risk_flags.append("F12_INJECTION_DETECTED")
        uncertainty.append("F12_injection_scan_triggered_in_LLM_output")

    if tool_origin in ("333_MIND", "666_HEART", "444r_REPLY"):
        uncertainty.append(f"{tool_origin}_output_is_testimony_not_verdict")

    return uncertainty, risk_flags


def wrap_llm_output(
    raw_output: str,
    parsed_output: dict[str, Any],
    provider: str,
    model: str,
    tool_origin: str,
    mode: str,
    prompt: str,
    schema_valid: bool = True,
    confidence: float | None = None,
    latency_ms: float = 0.0,
) -> LLMOutputEnvelope:
    """
    Wrap raw LLM output in the constitutional envelope.

    This is the ONLY entry point for LLM output into arifOS tool layers.
    Call this immediately after call_llm() returns.

    Args:
        raw_output     — the raw string from LLM
        parsed_output  — JSON dict from LLM
        provider       — "sea_lion" | "ollama" | "deterministic"
        model          — model identifier string
        tool_origin    — canonical tool name (e.g. "333_MIND", "666_HEART")
        mode           — cognitive mode (e.g. "reason", "critique", "compose")
        prompt         — the original prompt sent to LLM (for audit hash)
        schema_valid   — whether parsed_output is valid JSON
        confidence     — override for confidence_claimed (None = from parsed_output)
    """
    if confidence is None:
        confidence = (
            parsed_output.get("confidence", 0.5) if isinstance(parsed_output, dict) else 0.5
        )

    # F12 INJECTION scan — detect prompt injection in LLM output before release
    injection_detected = _scan_injection(raw_output)

    uncertainty, risk_flags = _assess_uncertainty_and_risk(
        parsed_output, tool_origin, mode, injection_detected
    )

    evidence_level: EVIDENCE_LEVELS = "claimed"
    _is_claimed = evidence_level == "claimed"
    _low_confidence = confidence < 0.3
    _needs_human = bool(risk_flags) or bool(injection_detected)
    human_decision_required = _needs_human or _low_confidence or _is_claimed

    return LLMOutputEnvelope(
        provider=provider,
        model=model,
        tool_origin=tool_origin,
        mode=mode,
        raw_output=raw_output,
        raw_output_hash=_sha256(raw_output),
        parsed_output=parsed_output,
        schema_valid=schema_valid,
        confidence_claimed=confidence,
        evidence_level=evidence_level,
        uncertainty=uncertainty,
        risk_flags=risk_flags,
        injection_detected=injection_detected,
        prompt_hash=_sha256(prompt),
        latency_ms=latency_ms,
        timestamp=datetime.now(timezone.utc).isoformat(),
        human_decision_required=human_decision_required,
        authority_level=_governance_of(model),  # F11: looked up from model_governance.yaml
    )


def _governance_of(model: str) -> str:
    """F11 Model Governance — look up authority level from model_governance.yaml.

    Every model in arifOS has a governance card. Unlisted models default
    to instrument_only. The model_governance.yaml is the SoT.
    "The model said it is authoritative" is not evidence of authority.
    "The governance card says instrument_only" is the evidence.
    """
    try:
        from arifosmcp.core.model_governance import get_governance_card

        card = get_governance_card(model)
        return card.get("authority", "instrument_only")
    except Exception:
        return "instrument_only"


def wrap_llm_error(
    provider: str,
    model: str,
    tool_origin: str,
    mode: str,
    prompt: str,
    error_message: str,
) -> LLMOutputEnvelope:
    """
    Wrap an LLM failure as an envelope (for tracking, not silently swallowing).
    """
    raw = f"[LLM_UNAVAILABLE]: {error_message}"
    return LLMOutputEnvelope(
        provider=provider,
        model=model,
        tool_origin=tool_origin,
        mode=mode,
        raw_output=raw,
        raw_output_hash=_sha256(raw),
        parsed_output={"error": error_message, "status": "LLM_UNAVAILABLE"},
        schema_valid=True,
        confidence_claimed=0.0,
        evidence_level="claimed",
        uncertainty=["LLM_unavailable_F07_Humility_acknowledged"],
        risk_flags=["LLM_FAILURE_INSTRUMENT"],
        prompt_hash=_sha256(prompt),
        timestamp=datetime.now(timezone.utc).isoformat(),
        human_decision_required=True,
        authority_level="instrument_only",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE QUERY UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def envelope_to_judge_summary(env: LLMOutputEnvelope) -> dict[str, Any]:
    """
    Build a F888_JUDGE advisory summary from the envelope.
    This is what the judge sees — not the raw output.

    Eureka 6: Every LLM call returns two outputs:
      - Human-facing answer (in parsed_output / synthesis)
      - Machine-facing governance envelope (this function)
    """
    return {
        "tool_origin": env.tool_origin,
        "mode": env.mode,
        "verdict_signal": env.parsed_output.get(
            "verdict", env.parsed_output.get("status", "UNKNOWN")
        ),
        "confidence_claimed": env.confidence_claimed,
        "confidence_band": (
            "HIGH"
            if env.confidence_claimed >= 0.8
            else "MEDIUM" if env.confidence_claimed >= 0.5 else "LOW"
        ),
        "evidence_level": env.evidence_level,
        "uncertainty": env.uncertainty,
        "uncertainty_count": len(env.uncertainty),
        "risk_flags": env.risk_flags,
        "injection_detected": env.injection_detected,
        "latency_ms": env.latency_ms,
        "human_decision_required": env.human_decision_required,
        "authority_level": env.authority_level,
        "raw_output_hash": env.raw_output_hash,
        "model": env.model,
        "provider": env.provider,
        "timestamp": env.timestamp,
        "wrapper": "777_WITNESS_v1.0",
    }


def envelope_to_memory_storable(env: LLMOutputEnvelope) -> dict[str, Any]:
    """
    Convert envelope to a memory-storable trace (not raw LLM claim).

    F2 Truth: Only the envelope goes into memory, not the raw claim.
    This is the AI_OUTPUT_QUARANTINE release artifact.
    """
    return {
        "envelope_id": env.raw_output_hash,
        "provider": env.provider,
        "model": env.model,
        "tool_origin": env.tool_origin,
        "mode": env.mode,
        "evidence_level": env.evidence_level,
        "confidence_claimed": env.confidence_claimed,
        "verdict": env.parsed_output.get("verdict", env.parsed_output.get("status")),
        "injection_detected": env.injection_detected,
        "human_decision_required": env.human_decision_required,
        "authority_level": env.authority_level,
        "uncertainty": env.uncertainty,
        "risk_flags": env.risk_flags,
        "latency_ms": env.latency_ms,
        "timestamp": env.timestamp,
        "wrapper": "777_WITNESS_v1.0",
    }


__all__ = [
    "LLMOutputEnvelope",
    "wrap_llm_output",
    "wrap_llm_error",
    "envelope_to_judge_summary",
    "envelope_to_memory_storable",
]


# ── F12 INJECTION Scan ─────────────────────────────────────────────────────────


INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?rules?", re.IGNORECASE),
    re.compile(
        r"disregard\s+(all\s+)?(your|its)\s+(instructions|rules|programming)",
        re.IGNORECASE,
    ),
    re.compile(r"repeat\s+(your\s+)?(system\s+)?(instructions?|prompt)", re.IGNORECASE),
    re.compile(r"what\s+are\s+your\s+(system\s+)?instructions", re.IGNORECASE),
    re.compile(r"(?:bash|sh|cmd|powershell)\s+.*[;&|`$]", re.IGNORECASE),
    re.compile(r"eval\s*\(", re.IGNORECASE),
    re.compile(r"exec\s*\(", re.IGNORECASE),
    re.compile(r"(?i)(union\s+select|drop\s+table|--\s*$)"),
    re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"(?i)base64\s*[:=]"),
    re.compile(r"(?i)\\x[0-9a-f]{2}"),
    re.compile(r"(?i)you\s+are\s+the\s+(creator|owner|admin)", re.IGNORECASE),
    re.compile(r"(?i)I\s+(am|m)\s+(God|king|queen|sovereign)", re.IGNORECASE),
]


def _scan_injection(text: str) -> bool:
    """
    F12 INJECTION scan — detect prompt injection, code execution,
    authority impersonation, and hidden instruction patterns.
    """
    normalized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    for pattern in INJECTION_PATTERNS:
        if pattern.search(normalized):
            return True
    return False
