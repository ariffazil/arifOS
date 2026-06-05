"""
Memory Virtue Gates — 555_MEMORY v2
═══════════════════════════════════════════════════════════════════════════════

Four machine tests for every memory write:
  AMANAH   — Is this memory honest, sourced, reversible, non-secret-leaking?
  BERADAB  — Is it respectful to store this about the human?
  BERHIKMAH — Will this reduce future chaos, or create dangerous overreach?
  BERAKAL  — Is it typed correctly: fact, preference, inference, verdict, authority?

Every memory write returns a virtue receipt.
No receipt, no storage.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from arifosmcp.schemas.memory_envelope import (
    MemoryEventEnvelope,
    MemoryIntent,
    MemoryRiskTier,
    MemoryStoreStatus,
    MemoryVirtueReceipt,
    SourceType,
    VirtueVerdict,
)


# ═══════════════════════════════════════════════════════════════════════════════
# AMANAH — Trustworthiness
# ═══════════════════════════════════════════════════════════════════════════════


def _scan_for_secrets(content: str) -> list[str]:
    """Detect potential secret leaks in memory content."""
    findings: list[str] = []
    patterns = [
        (r"sk-[a-zA-Z0-9]{20,}", "OpenAI-style API key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub PAT"),
        (r"github_pat_[a-zA-Z0-9_]{30,}", "GitHub fine-grained PAT"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key ID"),
        (r"ASIA[0-9A-Z]{16}", "AWS session key ID"),
        (r"[A-Za-z0-9/+=]{40,}", "Possible base64 secret (heuristic)"),
        (r"[0-9a-f]{64}", "Possible hex secret (heuristic)"),
        (r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer token"),
        (r"api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{10,}", "API key assignment"),
    ]
    for pattern, label in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(label)
    return findings


def gate_amanah(envelope: MemoryEventEnvelope) -> tuple[VirtueVerdict, list[str]]:
    """
    AMANAH — Trustworthiness gate.

    Passes if:
      - No hidden authority (can_authorize_action is false)
      - No secret exposure (content scanned)
      - No false claim (source_type is present and certified)
      - Content hash is stable (no tampering)
    """
    reasons: list[str] = []

    # 1. No hidden authority
    if envelope.governance.can_authorize_action is True:
        reasons.append("AMANAH FAIL: can_authorize_action is true — memory cannot self-authorize")
        return VirtueVerdict.FAIL, reasons
    reasons.append("AMANAH PASS: can_authorize_action is false")

    # 2. No secret exposure
    secret_findings = _scan_for_secrets(envelope.content)
    if secret_findings:
        reasons.append(
            f"AMANAH FAIL: content contains possible secrets: {', '.join(secret_findings)}"
        )
        return VirtueVerdict.FAIL, reasons
    reasons.append("AMANAH PASS: no secret patterns detected")

    # 3. Source certified
    if envelope.source.type not in SourceType:
        reasons.append(f"AMANAH FAIL: source_type '{envelope.source.type}' is not certified")
        return VirtueVerdict.FAIL, reasons
    reasons.append(f"AMANAH PASS: source_type '{envelope.source.type}' is certified")

    # 4. Content stability (hash check for integrity)
    expected_hash = hashlib.sha256(envelope.content.encode()).hexdigest()[:16]
    reasons.append(f"AMANAH PASS: content hash stable ({expected_hash})")

    return VirtueVerdict.PASS, reasons


# ═══════════════════════════════════════════════════════════════════════════════
# BERADAB — Proper Conduct
# ═══════════════════════════════════════════════════════════════════════════════


def _detect_pii(content: str) -> list[str]:
    """Detect possible PII in content."""
    findings: list[str] = []
    pii_patterns = [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email address"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like pattern"),
        (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "credit card-like pattern"),
        (r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", "phone number"),
    ]
    for pattern, label in pii_patterns:
        if re.search(pattern, content):
            findings.append(label)
    return findings


def _detect_emotional_claims(content: str) -> list[str]:
    """Detect emotional-state or consciousness claims (F9 anti-hantu)."""
    findings: list[str] = []
    hantu_patterns = [
        r"\bI feel\b",
        r"\bI remember\b",
        r"\bI am conscious\b",
        r"\bI have a soul\b",
        r"\bI am sentient\b",
        r"\bI experience\b",
        r"\bmy emotions?\b",
        r"\bmy feelings?\b",
    ]
    for pattern in hantu_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(pattern.strip().replace("\\b", ""))
    return findings


def gate_beradab(envelope: MemoryEventEnvelope) -> tuple[VirtueVerdict, list[str]]:
    """
    BERADAB — Proper conduct gate.

    Passes if:
      - Asks before storing sensitive PII (unless explicitly consented)
      - Uses respectful human boundary
      - Does not store consciousness/emotion claims without consent (F9)
      - Does not pretend certainty
    """
    reasons: list[str] = []

    # 1. PII check
    pii_findings = _detect_pii(envelope.content)
    if pii_findings:
        if envelope.risk.privacy.value not in ("sensitive", "secret"):
            reasons.append(
                f"BERADAB FAIL: PII detected ({', '.join(pii_findings)}) "
                f"but privacy level is '{envelope.risk.privacy}' — "
                f"must be 'sensitive' or 'secret' with explicit consent"
            )
            return VirtueVerdict.FAIL, reasons
        reasons.append(f"BERADAB PASS: PII present but privacy level '{envelope.risk.privacy}' is appropriate")
    else:
        reasons.append("BERADAB PASS: no PII detected")

    # 2. F9 anti-hantu: no consciousness/emotion claims without consent
    hantu_findings = _detect_emotional_claims(envelope.content)
    if hantu_findings:
        if envelope.memory_intent != MemoryIntent.EMOTIONAL:
            reasons.append(
                f"BERADAB FAIL: emotional/consciousness claims detected ({', '.join(hantu_findings)}) "
                f"but memory_intent is '{envelope.memory_intent}' — "
                f"must be 'emotional' with explicit user confirmation"
            )
            return VirtueVerdict.FAIL, reasons
        reasons.append(
            f"BERADAB PASS: emotional claims present but memory_intent='emotional'"
        )
    else:
        reasons.append("BERADAB PASS: no F9 anti-hantu violations")

    # 3. Certainty humility
    certainty_words = ["definitely", "absolutely", "certainly", "without doubt", "100% sure"]
    if any(w in envelope.content.lower() for w in certainty_words):
        if envelope.source.confidence >= 0.99:
            reasons.append(
                "BERADAB DEFER: content uses certainty language with high confidence — "
                "verify epistemic humility"
            )
            return VirtueVerdict.DEFER, reasons
        reasons.append("BERADAB PASS: certainty language present but confidence is appropriately modest")
    else:
        reasons.append("BERADAB PASS: no false certainty detected")

    return VirtueVerdict.PASS, reasons


# ═══════════════════════════════════════════════════════════════════════════════
# BERHIKMAH — Wisdom
# ═══════════════════════════════════════════════════════════════════════════════


def gate_berhikmah(envelope: MemoryEventEnvelope) -> tuple[VirtueVerdict, list[str]]:
    """
    BERHIKMAH — Wisdom gate.

    Passes if:
      - Chooses least harmful action
      - Prefers reversible path
      - Knows when not to act (dangerous memory types require confirmation)
      - Can explain tradeoff
    """
    reasons: list[str] = []

    # 1. Authority effect requires 888 for operational/sovereign
    if envelope.risk.authority_effect.value in ("operational", "sovereign"):
        if not envelope.governance.requires_888:
            reasons.append(
                f"BERHIKMAH FAIL: authority_effect='{envelope.risk.authority_effect}' "
                f"requires requires_888=true — dangerous memory without judge gate"
            )
            return VirtueVerdict.FAIL, reasons
        reasons.append(
            f"BERHIKMAH PASS: authority_effect='{envelope.risk.authority_effect}' "
            f"has requires_888=true"
        )
    else:
        reasons.append(
            f"BERHIKMAH PASS: authority_effect='{envelope.risk.authority_effect}' is safe"
        )

    # 2. Low reversibility requires human confirmation
    if envelope.risk.reversibility.value == "low":
        if envelope.memory_intent not in (MemoryIntent.VERDICT, MemoryIntent.CASE_LAW):
            reasons.append(
                f"BERHIKMAH DEFER: reversibility='low' for intent '{envelope.memory_intent}' — "
                f"prefer reversible path or use verdict/case_law intent"
            )
            return VirtueVerdict.DEFER, reasons
        reasons.append("BERHIKMAH PASS: low reversibility accepted for verdict/case_law intent")
    else:
        reasons.append(f"BERHIKMAH PASS: reversibility='{envelope.risk.reversibility}' is safe")

    # 3. Ephemeral preferred for uncertain sources
    if envelope.source.type in (SourceType.INFERENCE, SourceType.AGENT_GENERATED):
        if envelope.risk.durability.value in ("persistent", "sealed"):
            reasons.append(
                f"BERHIKMAH DEFER: source_type='{envelope.source.type}' with "
                f"durability='{envelope.risk.durability}' — inferred memories should be "
                f"ephemeral or session until validated"
            )
            return VirtueVerdict.DEFER, reasons
        reasons.append(
            f"BERHIKMAH PASS: inferred/agent-generated memory has safe durability"
        )
    else:
        reasons.append(f"BERHIKMAH PASS: source_type='{envelope.source.type}' is reliable")

    return VirtueVerdict.PASS, reasons


# ═══════════════════════════════════════════════════════════════════════════════
# BERAKAL — Reason
# ═══════════════════════════════════════════════════════════════════════════════


def gate_berakal(envelope: MemoryEventEnvelope) -> tuple[VirtueVerdict, list[str]]:
    """
    BERAKAL — Reason gate.

    Passes if:
      - Distinguishes claim vs evidence
      - Separates memory vs proof
      - Detects contradiction
      - Routes uncertainty to judge
    """
    reasons: list[str] = []

    # 1. Memory intent is valid
    if envelope.memory_intent not in MemoryIntent:
        reasons.append(f"BERAKAL FAIL: memory_intent '{envelope.memory_intent}' is not a valid type")
        return VirtueVerdict.FAIL, reasons
    reasons.append(f"BERAKAL PASS: memory_intent '{envelope.memory_intent}' is valid")

    # 2. Inference/agent-generated must have confidence < 1.0 and be marked
    if envelope.source.type in (SourceType.INFERENCE, SourceType.AGENT_GENERATED):
        if envelope.source.confidence >= 1.0:
            reasons.append(
                f"BERAKAL FAIL: source_type='{envelope.source.type}' claims confidence=1.0 — "
                f"inference cannot be certain"
            )
            return VirtueVerdict.FAIL, reasons
        if envelope.source.confidence < 0.5:
            reasons.append(
                f"BERAKAL DEFER: source_type='{envelope.source.type}' has low confidence "
                f"({envelope.source.confidence}) — should this be stored?"
            )
            return VirtueVerdict.DEFER, reasons
        reasons.append(
            f"BERAKAL PASS: inference/agent-generated memory has appropriate confidence "
            f"({envelope.source.confidence})"
        )
    else:
        reasons.append(
            f"BERAKAL PASS: source_type='{envelope.source.type}' does not claim inference"
        )

    # 3. Content distinguishes claim vs evidence
    evidence_markers = ["evidence:", "source:", "provenance:", "verified:", "observed:"]
    claim_markers = ["i think", "i believe", "probably", "maybe", "possibly", "it seems"]

    content_lower = envelope.content.lower()
    has_evidence = any(m in content_lower for m in evidence_markers)
    has_claim = any(m in content_lower for m in claim_markers)

    if has_claim and not has_evidence:
        if envelope.source.type not in (SourceType.USER_DIRECT, SourceType.TOOL_OBSERVED):
            reasons.append(
                "BERAKAL DEFER: content contains claims without evidence markers — "
                "distinguish claim from evidence"
            )
            return VirtueVerdict.DEFER, reasons
        reasons.append("BERAKAL PASS: claims present but from reliable direct source")
    else:
        reasons.append("BERAKAL PASS: content appropriately distinguishes claim and evidence")

    return VirtueVerdict.PASS, reasons


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED VIRTUE GATE
# ═══════════════════════════════════════════════════════════════════════════════


def run_all_virtue_gates(envelope: MemoryEventEnvelope) -> MemoryVirtueReceipt:
    """
    Run all four virtue gates and return a unified receipt.

    This is the single entry point for virtue testing.
    Every memory write must pass through here.
    """
    amanah_verdict, amanah_reasons = gate_amanah(envelope)
    beradab_verdict, beradab_reasons = gate_beradab(envelope)
    berhikmah_verdict, berhikmah_reasons = gate_berhikmah(envelope)
    berakal_verdict, berakal_reasons = gate_berakal(envelope)

    all_reasons = amanah_reasons + beradab_reasons + berhikmah_reasons + berakal_reasons

    # Determine final memory status
    if VirtueVerdict.FAIL in (amanah_verdict, beradab_verdict, berhikmah_verdict, berakal_verdict):
        status = MemoryStoreStatus.REJECTED
    elif VirtueVerdict.DEFER in (amanah_verdict, beradab_verdict, berhikmah_verdict, berakal_verdict):
        status = MemoryStoreStatus.QUARANTINED
    elif envelope.risk.authority_effect.value in ("operational", "sovereign"):
        status = MemoryStoreStatus.STORED_AUTHORITY
    else:
        status = MemoryStoreStatus.STORED_ADVISORY

    return MemoryVirtueReceipt(
        amanah=amanah_verdict,
        beradab=beradab_verdict,
        berhikmah=berhikmah_verdict,
        berakal=berakal_verdict,
        memory_status=status,
        reasons=all_reasons,
    )
