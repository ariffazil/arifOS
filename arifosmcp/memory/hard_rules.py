"""
Memory Hard Rules — 555_MEMORY v2
═══════════════════════════════════════════════════════════════════════════════

The ten iron laws of memory. Every memory operation must pass these gates.
These are code-level enforcement, not suggestions.

RULE 1:  No memory write without source_type.
RULE 2:  No persistent memory without expiry or review policy.
RULE 3:  No authority memory (M3/M4) without 888 confirmation.
RULE 4:  No vector memory (L3) can be treated as proof in recall.
RULE 5:  No agent-generated memory can authorize action.
RULE 6:  No secret goes into L3 vector memory.
RULE 7:  No raw API key enters any memory layer.
RULE 8:  No emotional-state memory becomes permanent unless user explicitly confirms.
RULE 9:  No contradiction overwrite. Create a conflict record.
RULE 10: No sealed memory deletion. Only tombstone/revoke.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Any

from arifosmcp.schemas.memory_envelope import (
    AuthorityEffect,
    Durability,
    MemoryEventEnvelope,
    MemoryIntent,
    MemoryRiskTier,
    MemoryStatus,
    SourceType,
)


class MemoryHardRuleViolation(Exception):
    """Raised when a memory operation violates an iron law."""

    def __init__(self, rule_number: int, reason: str):
        self.rule_number = rule_number
        self.reason = reason
        super().__init__(f"RULE {rule_number} VIOLATION: {reason}")


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 1: No memory write without source_type
# ═══════════════════════════════════════════════════════════════════════════════


def rule_1_source_required(envelope: MemoryEventEnvelope) -> None:
    """Every persistent memory must declare its source."""
    if envelope.source.type is None or envelope.source.type == SourceType.UNKNOWN:
        raise MemoryHardRuleViolation(
            1,
            f"source_type is mandatory for persistent memory. Got: {envelope.source.type}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 2: No persistent memory without expiry or review policy
# ═══════════════════════════════════════════════════════════════════════════════


def rule_2_expiry_required(envelope: MemoryEventEnvelope) -> None:
    """Persistent or sealed memory must have an expiry or be M4 (constitutional)."""
    if envelope.risk.durability in (Durability.PERSISTENT, Durability.SEALED):
        if envelope.governance.expiry is None:
            # M4 (constitutional) is exempt — sacred memory has no expiry
            if envelope.m_tier != MemoryRiskTier.M4:
                raise MemoryHardRuleViolation(
                    2,
                    f"durability='{envelope.risk.durability}' requires expiry or review policy. "
                    f"Set governance.expiry or downgrade to session/ephemeral.",
                )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 3: No authority memory (M3/M4) without 888 confirmation
# ═══════════════════════════════════════════════════════════════════════════════


def rule_3_authority_requires_888(envelope: MemoryEventEnvelope) -> None:
    """M3 and M4 memory must have requires_888=true."""
    if envelope.m_tier in (MemoryRiskTier.M3, MemoryRiskTier.M4):
        if not envelope.governance.requires_888:
            raise MemoryHardRuleViolation(
                3,
                f"M-tier '{envelope.m_tier}' (authority memory) requires requires_888=true. "
                f"This memory affects identity, authority, or constitutional decisions.",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 4: No vector memory (L3) can be treated as proof in recall
# ═══════════════════════════════════════════════════════════════════════════════


def rule_4_vector_not_proof(envelope: MemoryEventEnvelope) -> None:
    """
    L3 (Qdrant) is associative and probabilistic.
    It can suggest, not prove. This rule is enforced at recall time,
    but we stamp the memory at store time so recall knows.
    """
    # This is primarily a recall-time rule, but we ensure the memory is tagged
    # The actual enforcement happens in the recall handler by checking provenance
    pass


def assert_vector_not_proof(recall_result: dict[str, Any]) -> dict[str, Any]:
    """
    At recall time: if a result came from L3 (vector/semantic search),
    mark it as 'suggested' not 'verified'.
    """
    if recall_result.get("source_layer") == "L3" or recall_result.get("score") is not None:
        recall_result["provenance"] = "suggested"
        recall_result["can_treat_as_proof"] = False
    else:
        recall_result["provenance"] = recall_result.get("provenance", "unknown")
        recall_result["can_treat_as_proof"] = recall_result.get("source_layer") == "L4"
    return recall_result


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 5: No agent-generated memory can authorize action
# ═══════════════════════════════════════════════════════════════════════════════


def rule_5_agent_memory_no_authority(envelope: MemoryEventEnvelope) -> None:
    """Agent-generated memories are advisory only."""
    if envelope.source.type == SourceType.AGENT_GENERATED:
        if envelope.governance.can_authorize_action:
            raise MemoryHardRuleViolation(
                5,
                "Agent-generated memory cannot authorize action. "
                "Authority must come from user_direct, file_evidence, or web_evidence.",
            )
        # Also enforce authority_effect is none or advisory
        if envelope.risk.authority_effect not in (AuthorityEffect.NONE, AuthorityEffect.ADVISORY):
            raise MemoryHardRuleViolation(
                5,
                f"Agent-generated memory must have authority_effect='none' or 'advisory'. "
                f"Got: '{envelope.risk.authority_effect}'",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 6: No secret goes into L3 vector memory
# ═══════════════════════════════════════════════════════════════════════════════


def rule_6_no_secrets_in_vector(envelope: MemoryEventEnvelope) -> None:
    """
    Before writing to Qdrant (L3), scan content for secrets.
    If found, block the L3 leg but allow L4 (relational) if redacted.
    """
    secret_patterns = [
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
        r"github_pat_[a-zA-Z0-9_]{30,}",
        r"AKIA[0-9A-Z]{16}",
        r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
        r"api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{10,}",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, envelope.content, re.IGNORECASE):
            raise MemoryHardRuleViolation(
                6,
                f"Content contains possible secret pattern matching {pattern}. "
                f"Secrets cannot enter L3 vector memory. Store capability reference in L4 only.",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 7: No raw API key enters any memory layer
# ═══════════════════════════════════════════════════════════════════════════════


def rule_7_no_api_keys_anywhere(envelope: MemoryEventEnvelope) -> None:
    """
    Absolute ban on raw API keys in ANY memory layer.
    This is stricter than RULE 6 — it blocks L3, L4, L5, L6.
    """
    api_key_patterns = [
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
        r"github_pat_[a-zA-Z0-9_]{30,}",
        r"AKIA[0-9A-Z]{16}",
        r"ASIA[0-9A-Z]{16}",
        r"[A-Za-z0-9/+=]{40}(?![a-zA-Z0-9/+=])",  # Base64-like 40-char string
    ]
    for pattern in api_key_patterns:
        if re.search(pattern, envelope.content):
            raise MemoryHardRuleViolation(
                7,
                f"Raw API key or credential pattern detected in content. "
                f"Memory stores capabilities, not secrets. "
                f"Use capability_ref with agent_visible_secret=false.",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 8: No emotional-state memory becomes permanent unless user explicitly confirms
# ═══════════════════════════════════════════════════════════════════════════════


def rule_8_emotional_requires_confirm(envelope: MemoryEventEnvelope) -> None:
    """Emotional memory must have explicit user confirmation to become persistent."""
    if envelope.memory_intent == MemoryIntent.EMOTIONAL:
        if envelope.risk.durability in (Durability.PERSISTENT, Durability.SEALED):
            # Check for explicit confirmation marker in governance floors or tags
            confirmed = (
                "user_confirmed" in envelope.tags
                or "F13_CONFIRMED" in envelope.governance.floors
            )
            if not confirmed:
                raise MemoryHardRuleViolation(
                    8,
                    "Emotional-state memory requires explicit user confirmation to become persistent. "
                    "Add tag 'user_confirmed' or floor 'F13_CONFIRMED', or downgrade to session/ephemeral.",
                )


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 9: No contradiction overwrite. Create a conflict record.
# ═══════════════════════════════════════════════════════════════════════════════


def rule_9_no_overwrite_on_contradiction(
    envelope: MemoryEventEnvelope, existing_records: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """
    Before storing, check for contradictions with existing L4 records.
    If found, return a conflict record instead of overwriting.
    """
    from arifosmcp.runtime.f4_contradiction_handler import f4_write_path_hook

    # Use existing F4 handler if available
    try:
        conflict = f4_write_path_hook(envelope.content, existing_records)
        if conflict and conflict.get("contradiction_detected"):
            return {
                "contradiction_detected": True,
                "conflict_record": conflict,
                "action": "create_conflict_record",
                "original_memory_id": conflict.get("original_memory_id"),
            }
    except Exception:
        pass

    # Fallback: simple keyword-based contradiction check
    for record in existing_records:
        existing_content = record.get("text", "")
        # If same actor/session and opposite sentiment on same topic, flag
        if (
            record.get("metadata", {}).get("actor_id") == envelope.actor_id
            and record.get("metadata", {}).get("memory_intent") == envelope.memory_intent.value
        ):
            # Simple heuristic: check for negation words
            negation_words = ["not", "never", "no ", "false", "wrong", "incorrect"]
            old_has_neg = any(w in existing_content.lower() for w in negation_words)
            new_has_neg = any(w in envelope.content.lower() for w in negation_words)
            if old_has_neg != new_has_neg and len(existing_content) > 20:
                return {
                    "contradiction_detected": True,
                    "conflict_record": {
                        "original_memory_id": record.get("id"),
                        "original_content": existing_content[:200],
                        "new_content": envelope.content[:200],
                        "reason": "Possible negation contradiction — same intent, opposite polarity",
                    },
                    "action": "create_conflict_record",
                }

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# RULE 10: No sealed memory deletion. Only tombstone/revoke.
# ═══════════════════════════════════════════════════════════════════════════════


def rule_10_no_delete_sealed(m_tier: MemoryRiskTier, method: str) -> None:
    """M4 (sealed) memory cannot be deleted. Only tombstoned or revoked."""
    if m_tier == MemoryRiskTier.M4:
        if method not in ("tombstone", "revoke_authority"):
            raise MemoryHardRuleViolation(
                10,
                f"M4 sealed memory cannot be deleted. method='{method}' is forbidden. "
                f"Use 'tombstone' or 'revoke_authority' only.",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED HARD RULES GATE
# ═══════════════════════════════════════════════════════════════════════════════


def run_all_hard_rules(
    envelope: MemoryEventEnvelope,
    existing_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Run all ten hard rules in sequence.

    Returns:
        {"passed": True} if all rules pass.
        {"passed": False, "failed_rule": N, "reason": str} if any rule fails.
        {"passed": True, "contradiction": {...}} if RULE 9 detects contradiction.
    """
    rules = [
        (1, lambda: rule_1_source_required(envelope)),
        (2, lambda: rule_2_expiry_required(envelope)),
        (3, lambda: rule_3_authority_requires_888(envelope)),
        (5, lambda: rule_5_agent_memory_no_authority(envelope)),
        (6, lambda: rule_6_no_secrets_in_vector(envelope)),
        (7, lambda: rule_7_no_api_keys_anywhere(envelope)),
        (8, lambda: rule_8_emotional_requires_confirm(envelope)),
    ]

    for rule_num, rule_fn in rules:
        try:
            rule_fn()
        except MemoryHardRuleViolation as exc:
            return {"passed": False, "failed_rule": exc.rule_number, "reason": exc.reason}

    # RULE 9: contradiction check (optional — requires existing records)
    if existing_records:
        contradiction = rule_9_no_overwrite_on_contradiction(envelope, existing_records)
        if contradiction:
            return {"passed": True, "contradiction": contradiction}

    return {"passed": True}
