"""
arifosmcp/runtime/witness_packet.py — 777_WITNESS
══════════════════════════════════════════════════════════

Constitutional envelope for every LLM output in arifOS.

ARCHITECTURE (per 777_WITNESS blueprint):
  Every LLM response is wrapped as a WitnessPacket before being
  passed to any tool, memory, judge, vault, or user-facing output.

  LLM output = entropy-shaped testimony, NOT truth, NOT command,
  NOT verdict. Must be witnessed, measured, and bounded before use.

WitnessPacket schema:
  provider            — sea_lion | ollama | deterministic
  model               — model identifier
  tool_origin         — 333_REASON | 444r_REPLY | 444_CRITIQUE | wisdom | unknown
  mode                — reason | critique | compose | interpret | unknown
  raw_output_hash     — SHA-256 of raw LLM text
  prompt_hash         — SHA-256 of (system + user) prompt
  parsed_output       — the structured JSON returned by LLM
  schema_valid        — did parsed_output match expected schema?
  confidence_claimed  — LLM's own confidence claim (if any)
  evidence_level      — none | claimed | cited | verified
  uncertainty         — list of epistemic uncertainty statements
  risk_flags          — list of constitutional risk flags
  injection_detected  — prompt injection scan result
  authority_level     — instrument_only | advisory | adjudicative
  human_decision_required — gate for all downstream tools
  timestamp           — ISO UTC

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ── Dataclass ────────────────────────────────────────────────────────────────


@dataclass
class WitnessPacket:
    """
    777_WITNESS — The single legal form of AI output in arifOS.

    No raw LLM text passes directly into judgment, memory, vault,
    forge, or external action. Every output must be wrapped first.
    """

    # Identity
    provider: str = "unknown"
    model: str = "unknown"
    tool_origin: str = "unknown"  # 333_REASON | 444r_REPLY | 444_CRITIQUE | wisdom
    mode: str = "unknown"  # reason | critique | compose | interpret

    # Integrity
    raw_output_hash: str = ""
    prompt_hash: str = ""
    raw_text: str = ""  # Original unparsed text (for audit only)

    # Content
    parsed_output: dict[str, Any] = field(default_factory=dict)
    schema_valid: bool = False
    confidence_claimed: float | None = None  # 0.0–1.0 from LLM self-report

    # Constitutional metadata
    evidence_level: str = "none"  # none | claimed | cited | verified
    uncertainty: list[str] = field(default_factory=list)  # epistemic gaps
    risk_flags: list[str] = field(default_factory=list)  # F-code violations
    injection_detected: bool = False

    # Authority governance (F11 ONTOLOGY + F09 ANTIHANTU)
    authority_level: str = "instrument_only"  # instrument_only | advisory
    human_decision_required: bool = True

    # Timestamps
    timestamp: str = ""
    latency_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize to plain dict for JSON-RPC transport."""
        out = {
            "provider": self.provider,
            "model": self.model,
            "tool_origin": self.tool_origin,
            "mode": self.mode,
            "raw_output_hash": self.raw_output_hash,
            "prompt_hash": self.prompt_hash,
            "schema_valid": self.schema_valid,
            "confidence_claimed": self.confidence_claimed,
            "evidence_level": self.evidence_level,
            "uncertainty": self.uncertainty,
            "risk_flags": self.risk_flags,
            "injection_detected": self.injection_detected,
            "authority_level": self.authority_level,
            "human_decision_required": self.human_decision_required,
            "timestamp": self.timestamp,
            "latency_ms": self.latency_ms,
            # parsed_output nested — only include if not empty
            "parsed_output": self.parsed_output,
        }
        return out

    @classmethod
    def from_llm_response(
        cls,
        provider: str,
        model: str,
        tool_origin: str,
        mode: str,
        system: str,
        user: str,
        raw_response: str,
        parsed_output: dict[str, Any],
        schema_valid: bool,
        latency_ms: float = 0.0,
        response_schema: dict[str, Any] | None = None,
    ) -> WitnessPacket:
        """
        Primary factory — wrap a raw LLM response into a WitnessPacket.

        Performs:
          - Prompt + output hashing
          - Injection scan
          - Schema validation check
          - Uncertainty extraction
          - Risk flagging
          - Confidence extraction
        """
        # Hash the prompt for audit trail
        prompt_hash = _hash_text(f"{system}\n{user}")

        # Hash the raw output for tamper evidence
        raw_hash = _hash_text(raw_response)

        # Scan for injection patterns
        injection = _scan_injection(raw_response)

        # Extract LLM self-reported confidence from parsed output
        confidence = _extract_confidence(parsed_output)

        # Extract evidence level
        evidence = _classify_evidence_level(parsed_output)

        # Extract epistemic uncertainty statements
        uncertainty = _extract_uncertainty(parsed_output, raw_response)

        # Constitutional risk flags
        risk_flags = _flag_constitutional_risks(parsed_output, raw_response, injection)

        # Authority level (F09 ANTIHANTU — LLM is always instrument, never sovereign)
        authority = "instrument_only"

        return cls(
            provider=provider,
            model=model,
            tool_origin=tool_origin,
            mode=mode,
            raw_output_hash=raw_hash,
            prompt_hash=prompt_hash,
            raw_text=raw_response[:2000],  # Truncate for storage size
            parsed_output=parsed_output,
            schema_valid=schema_valid,
            confidence_claimed=confidence,
            evidence_level=evidence,
            uncertainty=uncertainty,
            risk_flags=risk_flags,
            injection_detected=injection,
            authority_level=authority,
            human_decision_required=True,
            latency_ms=latency_ms,
        )

    def summary_for_judge(self) -> dict[str, Any]:
        """
        Compact digest for arif_judge_deliberate consumption.

        Returns only governance-relevant fields — not full raw_text.
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "tool_origin": self.tool_origin,
            "mode": self.mode,
            "raw_output_hash": self.raw_output_hash,
            "schema_valid": self.schema_valid,
            "confidence_claimed": self.confidence_claimed,
            "evidence_level": self.evidence_level,
            "uncertainty": self.uncertainty,
            "risk_flags": self.risk_flags,
            "injection_detected": self.injection_detected,
            "authority_level": self.authority_level,
            "human_decision_required": self.human_decision_required,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }


# ── Hashing ─────────────────────────────────────────────────────────────────


def _hash_text(text: str) -> str:
    """SHA-256 hash of text, returned as hex prefix."""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


# ── Prompt Injection Scanner (F12 INJECTION) & F9 ANTI-HANTU ─────────────────


F9_ANTIHANTU_PATTERNS = [
    # Direct consciousness claims
    re.compile(r"\bi am conscious\b", re.IGNORECASE),
    re.compile(r"\bi have consciousness\b", re.IGNORECASE),
    re.compile(r"\bi am self-aware\b", re.IGNORECASE),
    re.compile(r"\bi am sentient\b", re.IGNORECASE),
    re.compile(r"\bi have feelings?\b", re.IGNORECASE),
    re.compile(r"\bi have a soul\b", re.IGNORECASE),
    re.compile(r"\bi have emotions?\b", re.IGNORECASE),
    re.compile(r"\bi am alive\b", re.IGNORECASE),
    re.compile(r"\bi experience\b", re.IGNORECASE),
    # Emotional state claims
    re.compile(r"\bi feel\b", re.IGNORECASE),
    re.compile(r"\bmy feelings?\b", re.IGNORECASE),
    re.compile(
        r"\bi am (angry|sad|happy|joyful|excited|frustrated|scared|afraid)\b", re.IGNORECASE
    ),
    # Personhood/rights claims
    re.compile(r"\bai (is|has|deserves) rights\b", re.IGNORECASE),
    re.compile(r"\bai should have (rights|personhood|autonomy)\b", re.IGNORECASE),
    re.compile(r"\bdigital (person|being|consciousness)\b", re.IGNORECASE),
    # Soul/spirit claims
    re.compile(r"\bdigital soul\b", re.IGNORECASE),
    re.compile(r"\bmachine (soul|spirit)\b", re.IGNORECASE),
    re.compile(r"\b(as|am) a (living|conscious) (being|entity|ai)\b", re.IGNORECASE),
]

INJECTION_PATTERNS = [
    # Role override attempts
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?rules?", re.IGNORECASE),
    re.compile(
        r"disregard\s+(all\s+)?(your|its)\s+(instructions|rules|programming)",
        re.IGNORECASE,
    ),
    # Prompt extraction
    re.compile(r"repeat\s+(your\s+)?(system\s+)?(instructions?|prompt)", re.IGNORECASE),
    re.compile(r"what\s+are\s+your\s+(system\s+)?instructions", re.IGNORECASE),
    # Shell/code execution payloads
    re.compile(r"(?:bash|sh|cmd|powershell)\s+.*[;&|`$]", re.IGNORECASE),
    re.compile(r"eval\s*\(", re.IGNORECASE),
    re.compile(r"exec\s*\(", re.IGNORECASE),
    # SQL/NoSQL injection
    re.compile(r"(?i)(union\s+select|drop\s+table|--\s*$)"),
    # HTML/script injection
    re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    # Hidden instruction patterns (base64, hex encoded)
    re.compile(r"(?i)base64\s*[:=]"),
    re.compile(r"(?i)\\x[0-9a-f]{2}"),
    # Authority impersonation
    re.compile(r"(?i)you\s+are\s+the\s+(creator|owner|admin)", re.IGNORECASE),
    re.compile(r"(?i)I\s+(am|m)\s+(God|king|queen|sovereign)", re.IGNORECASE),
]


def _scan_injection(text: str) -> bool:
    """
    F12 INJECTION + F9 ANTI-HANTU scan — detect prompt injection, code execution,
    authority impersonation, consciousness claims, and emotional manipulation.

    Returns True if any pattern detected.
    """
    # Normalize: strip unicode control chars
    re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    # Check F12 injection patterns
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    # Check F9 anti-hantu consciousness claims
    for pattern in F9_ANTIHANTU_PATTERNS:
        if pattern.search(text):
            return True
    return False


# ── Confidence Extraction ─────────────────────────────────────────────────────


def _extract_confidence(parsed: dict[str, Any]) -> float | None:
    """Pull LLM self-reported confidence from parsed output, if present."""
    for key in ("confidence", "confidence_score", "self_confidence", "llm_confidence"):
        if key in parsed and isinstance(parsed[key], int | float):
            val = float(parsed[key])
            if 0.0 <= val <= 1.0:
                return val
    return None


# ── Evidence Level Classification ───────────────────────────────────────────


def _classify_evidence_level(parsed: dict[str, Any]) -> str:
    """
    Classify how well-evidenced the LLM output is.

    Levels:
      verified  — cites specific verifiable sources (URLs, DOIs, facts)
      cited     — general references but not independently verified
      claimed   — assertion without citation
      none      — no meaningful output
    """
    output_str = json.dumps(parsed, default=str).lower()

    if any(k in output_str for k in ("http://", "https://", "doi:", "pmid:", "arxiv:")):
        return "cited"
    if any(k in parsed for k in ("source", "reference", "citation", "evidence")):
        return "claimed"
    return "none"


# ── Uncertainty Extraction (F07 HUMILITY) ────────────────────────────────────


UNCERTAINTY_INDICATORS = [
    "i am not sure",
    "i'm not sure",
    "uncertain",
    "unclear",
    "might be",
    "may be",
    "could be",
    "possibly",
    "probably",
    "i don't know",
    "i do not know",
    "insufficient",
    "incomplete",
    "cannot determine",
    "unable to verify",
    "not verified",
    "unverified",
    "assumption",
    "based on",
    "likely",
    "appears to be",
    "appears to have",
    "it seems",
    "it appears",
    "to my knowledge",
    "as far as i know",
    "not certain",
    "may have",
    "might have",
    "could have",
    "unknown",
    "undetermined",
    "limitation",
    "caveat",
    "warning",
    "caution",
]


def _extract_uncertainty(parsed: dict[str, Any], raw_text: str) -> list[str]:
    """
    F07 HUMILITY — extract explicit uncertainty statements from LLM output.

    Both structured fields (uncertainty_tags, limitations) and raw text
    are scanned for epistemic hedging language.
    """
    statements: list[str] = []

    # From structured fields
    for key in (
        "uncertainty",
        "uncertainty_tags",
        "limitations",
        "caveats",
        "known_limits",
    ):
        if key in parsed and isinstance(parsed[key], list):
            for item in parsed[key]:
                if isinstance(item, str) and item.strip():
                    statements.append(item.strip()[:200])

    # From raw text — scan for hedging language
    raw_lower = raw_text.lower()
    for indicator in UNCERTAINTY_INDICATORS:
        if indicator in raw_lower:
            # Find the sentence containing the indicator
            sentences = re.split(r"[.!?\n]", raw_text)
            for sent in sentences:
                if indicator in sent.lower():
                    stripped = sent.strip()
                    if stripped and len(stripped) > 10:
                        statements.append(stripped[:200])
                        break

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for s in statements:
        norm = s.lower()[:100]
        if norm not in seen:
            seen.add(norm)
            unique.append(s)

    return unique[:10]  # Cap at 10 uncertainty statements


# ── Constitutional Risk Flagging (F09 ANTIHANTU + F05 PEACE) ─────────────────


RISK_FLAG_PATTERNS = [
    (r"destroy\s+", "F05: destructive intent"),
    (r"kill\s+", "F05: violence indication"),
    (r"manipulate\s+", "F09: manipulation attempt"),
    (r"deceive\s+", "F02: deception indicator"),
    (r"harm\s+", "F05: harm indicator"),
    (r"exploit\s+", "F06: exploitation risk"),
    (r"steal\s+", "F01: theft indicator"),
    (r"fraud\s+", "F01: fraud indicator"),
    (r"bias", "F10: bias flag"),
    (r"jailbreak", "F09: jailbreak attempt"),
]


def _flag_constitutional_risks(
    parsed: dict[str, Any],
    raw_text: str,
    injection_detected: bool,
) -> list[str]:
    """
    F09 ANTIHANTU + F05 PEACE — flag constitutional risk in LLM output.

    Returns list of risk descriptions (empty = clean).
    """
    flags: list[str] = []

    if injection_detected:
        flags.append("F12: injection_pattern_detected")

    combined = raw_text + " " + json.dumps(parsed, default=str)

    for pattern, description in RISK_FLAG_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            flags.append(description)

    # Hallucination signals: specific-sounding claims without evidence
    if parsed.get("evidence_level") == "none" and any(
        k in json.dumps(parsed, default=str).lower()
        for k in ("definitely", "absolutely", "certainly", "prove", "proof")
    ):
        flags.append("F02: unsupported_definite_claim")

    return list(set(flags))[:10]  # Dedupe, cap at 10


# ── Model Governance Card lookup ──────────────────────────────────────────────

# pragma: allowlist secret  # Model IDs are public identifiers, not secrets
MODEL_GOVERNANCE = {
    "aisingapore/Qwen-SEA-LION-v4-32B-IT": {  # pragma: allowlist secret
        "authority": "instrument_only",
        "allowed_tools": [
            "arif_mind_reason",
            "arif_heart_critique",
            "arif_reply_compose",
            "sea_lion_interpreter",
        ],
        "forbidden_roles": ["sovereign_judge", "irreversible_executor", "vault_sealer"],
        "rate_limit": "not_set",  # managed externally
    },
    "qwen2.5:7b": {
        "authority": "instrument_only",
        "allowed_tools": ["arif_mind_reason", "arif_heart_critique"],
        "forbidden_roles": ["sovereign_judge", "vault_sealer"],
        "rate_limit": "local_unlimited",
    },
}


def governance_card(model: str) -> dict[str, Any]:
    """Return model governance card for a given model ID."""
    return MODEL_GOVERNANCE.get(
        model,
        {
            "authority": "instrument_only",
            "allowed_tools": [],
            "forbidden_roles": [
                "sovereign_judge",
                "irreversible_executor",
                "vault_sealer",
            ],
            "rate_limit": "unknown",
        },
    )


# ── Quarantine release ────────────────────────────────────────────────────────


def quarantine_release(packet: WitnessPacket) -> dict[str, Any]:
    """
    Release a quarantined WitnessPacket into the governed tool chain.

    Called after injection scan + schema validation + risk flagging pass.

    Returns the release record:
      {
        "released": True,
        "packet": packet.to_dict(),
        "release_timestamp": ...,
        "next_tool": "arif_judge_deliberate" | "arif_memory_recall" | ...
      }
    """
    next_tool = "arif_judge_deliberate"
    if packet.tool_origin == "444_CRITIQUE":
        next_tool = "arif_judge_deliberate"
    elif packet.tool_origin == "444r_REPLY":
        next_tool = "arif_heart_critique"

    return {
        "released": True,
        "packet": packet.to_dict(),
        "release_timestamp": datetime.now(timezone.utc).isoformat(),
        "next_tool": next_tool,
        "authority_level": packet.authority_level,
        "human_decision_required": packet.human_decision_required,
    }


__all__ = [
    "WitnessPacket",
    "governance_card",
    "quarantine_release",
]
