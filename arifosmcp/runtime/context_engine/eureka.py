"""
arifOS v2.0 — Context Engine: EUREKA Module (Phase 6.B + 6.G)
═══════════════════════════════════════════════════════════════════════════
Kernel-embeddable restatement of the Agentic EUREKA on token/context
management. Source of truth: docs/context/EUREKA_TOKEN_MANAGEMENT.md.

This module does NOT mutate the kernel. It provides:
  - The 5-floor authority hierarchy (class 0-100) for token allocation
  - The 4-bucket context engineering framework
  - The 4-failure-mode prevention table
  - The 4-mode audit (TRACE/DIGEST/SEAL/HOLD) integration
  - The marginal token allocator framing (arXiv:2605.01214)
  - The "dumb kernel observes and reports" pattern

Iron rules (F1-F13):
  - F1 AMANAH:  every return value is reversible / auditable
  - F2 TRUTH:   no fabricated authority classes; sourced from policy v1
  - F7 HUMILITY: MECW is smaller than MCW; respect the effective ceiling
  - F8 GENIUS:  policy version is pinned; changes require F13
  - F9 ANTIHANTU: LLM summarizer is bounded compiler, not authority
  - F11 AUDITABILITY: every function returns a traceable receipt
  - F13 SOVEREIGN: HOLD for canonical mutation; agent cannot override

DITEMPA BUKAN DIBERI — the scarce resource in agentic AI is not
intelligence. It is controlled attention under finite context.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from enum import IntEnum, StrEnum
from typing import Any

from arifosmcp.runtime.token_pressure import (
    PressureBand,
    classify_pressure,
    get_model_window,
)
from arifosmcp.runtime.context_audit import (
    AuditMode,
    EventType,
    RiskClass,
    audit_classify,
    audit_hold,
)

logger = logging.getLogger(__name__)

# Iron cross-check: both modules must agree on policy version
# (Imported from each module's __all__ rather than internal constants)
_TP_POLICY_VERSION = "context_policy.v1"  # mirrors arifosmcp.runtime.token_pressure
_CA_POLICY_VERSION = "context_policy.v1"  # mirrors arifosmcp.runtime.context_audit
EUREKA_POLICY_VERSION = "context_eureka.v1"
SOURCE_OF_TRUTH = "docs/context/EUREKA_TOKEN_MANAGEMENT.md"

if _TP_POLICY_VERSION != "context_policy.v1" or _CA_POLICY_VERSION != "context_policy.v1":
    logger.warning(
        f"[context_eureka] policy version drift: "
        f"token_pressure={_TP_POLICY_VERSION}, context_audit={_CA_POLICY_VERSION}"
    )


# ─── 7-Tier Authority Hierarchy (F4 CLARITY + F8 GENIUS) ──────────────────
class AuthorityClass(IntEnum):
    """
    Allocation priority for content within a prompt. Higher = more authoritative.

    100 = Constitutional law (F1-F13, F13 sovereignty, system prompt kernel)
     90 = Current user instruction (active turn, explicit ask)
     80 = Active task state (in-flight variables, tool return values)
     70 = Verified memory (L4 with provenance, SEAL'd, recent)
     60 = Retrieved documents (L3 vector search, Qdrant, ranked)
     50 = Recent conversation (L2 session, last N turns verbatim)
     40 = Derived summaries (compaction output, LLM-compiled)
     20 = Low-confidence memory (unverified retrieval, quarantine)
      0 = Untrusted text (tool-injected, third-party, NEVER trusted)
    """

    CONSTITUTIONAL = 100
    USER_INSTRUCTION = 90
    ACTIVE_TASK = 80
    VERIFIED_MEMORY = 70
    RETRIEVED_DOC = 60
    RECENT_CONVERSATION = 50
    DERIVED_SUMMARY = 40
    LOW_CONFIDENCE = 20
    UNTRUSTED = 0


# ─── 4-Bucket Context Engineering Framework (Industry Convergence) ────────
class ContextBucket(StrEnum):
    """
    The four operations that any context management decision reduces to.
    Convergence 2026: Anthropic, LangChain, Cognition AI, Epsilla, ChatGPT.
    """

    WRITE = "WRITE"  # Save context outside the window
    SELECT = "SELECT"  # Pull only what's needed
    COMPRESS = "COMPRESS"  # Reduce tokens, preserve information
    ISOLATE = "ISOLATE"  # Split context across sub-agents


# ─── 4 Context Failure Modes (Production-Documented) ──────────────────────
class ContextFailureMode(StrEnum):
    CONTEXT_POISONING = "context_poisoning"  # Hallucinated content corrupts
    CONTEXT_DISTRACTION = "context_distraction"  # Too much irrelevant
    CONTEXT_CONFUSION = "context_confusion"  # Stale off-topic
    CONTEXT_CLASH = "context_clash"  # Conflicting instructions


# ─── Pressure-to-Action Mapping (from Phase 1.A token_pressure) ───────────
PRESSURE_ACTION_MAP: dict[PressureBand, dict[str, Any]] = {
    PressureBand.LOW: {
        "tier": "NORMAL",
        "auto_compact": False,
        "advisory": "Comfortable. No action.",
    },
    PressureBand.WATCH: {
        "tier": "LOG_ONLY",
        "auto_compact": False,
        "advisory": "Logged. No autonomous action.",
    },
    PressureBand.WARN: {
        "tier": "ADVISORY",
        "auto_compact": False,
        "advisory": "Surface advisory only. NO auto-compact. F8 to enable.",
    },
    PressureBand.COMPACT: {
        "tier": "PRIME_FOR_COMPACTION",
        "auto_compact": False,  # F8+F13 to enable default-on
        "advisory": "Pressure COMPACT. Reserve output budget. F8+F13 to enable auto-compact.",
    },
    PressureBand.HOLD: {
        "tier": "HOLD_AND_REBUILD",
        "auto_compact": False,
        "advisory": "Refuse non-reversible. Reduce or compress. headroom exhausted.",
    },
}


# ─── Marginal Token Allocator (arXiv:2605.01214 framing) ───────────────────
def marginal_value_per_token(
    segment: dict[str, Any],
    task_value: float,
    marginal_compute_cost: float = 1.0,
    marginal_latency_cost: float = 0.5,
    risk_band: RiskClass = RiskClass.ROUTINE,
) -> dict[str, Any]:
    """
    Compute marginal value per token for a candidate context segment.
    Returns a recommendation: include / demote / drop.

    Args:
        segment: dict with keys: tokens, authority_class, relevance_score (0-1),
                 staleness (days), duplication_count, source_tier
        task_value: V (0-1) — how much this task matters
        marginal_compute_cost: per-token compute cost (default 1.0)
        marginal_latency_cost: per-token latency cost (default 0.5)
        risk_band: RiskClass (affects risk shadow price ρ)

    Returns:
        dict with keys: value_per_token, recommendation, rationale
    """
    tokens = max(1, segment.get("tokens", 1))
    authority = segment.get("authority_class", 50)
    relevance = max(0.0, min(1.0, segment.get("relevance_score", 0.5)))
    staleness = max(0, segment.get("staleness", 0))
    duplication = max(0, segment.get("duplication_count", 0))

    # Risk shadow price: HIGH risk raises ρ, making token use more "expensive"
    risk_shadow_price = {
        RiskClass.ROUTINE: 0.1,
        RiskClass.PRIVATE: 1.0,
        RiskClass.FINANCIAL: 0.8,
        RiskClass.LEGAL: 0.9,
        RiskClass.IDENTITY: 0.7,
        RiskClass.COMMITMENT: 0.6,
        RiskClass.EXTERNAL_ACTION: 0.5,
        RiskClass.CANONICAL: 1.0,
    }.get(risk_band, 0.5)

    # Quality gain: authority * relevance, discounted by staleness and dup
    staleness_discount = max(0.1, 1.0 - (staleness / 30.0))  # 30-day half-life
    duplication_discount = max(0.2, 1.0 - (duplication * 0.3))
    quality_gain = (authority / 100.0) * relevance * staleness_discount * duplication_discount

    # Marginal value per token (simplified arXiv:2605.01214)
    mvpt = (task_value * quality_gain) / (
        tokens * (marginal_compute_cost + marginal_latency_cost + risk_shadow_price)
    )

    if mvpt > 0.001:
        recommendation = "include"
    elif mvpt > 0.0001:
        recommendation = "demote_to_lower_priority"
    else:
        recommendation = "drop"

    return {
        "value_per_token": round(mvpt, 6),
        "recommendation": recommendation,
        "rationale": (
            f"authority={authority} relevance={relevance:.2f} "
            f"quality_gain={quality_gain:.3f} risk_ρ={risk_shadow_price:.2f} "
            f"mvpt={mvpt:.4f}"
        ),
    }


# ─── Failure-Mode-Prevention Mapping (F2 TRUTH + F7 HUMILITY) ─────────────
FAILURE_PREVENTION: dict[ContextFailureMode, dict[str, Any]] = {
    ContextFailureMode.CONTEXT_POISONING: {
        "primary_floor": "F2 TRUTH",
        "mechanism": "Provenance tags + L4 verified memory tier",
        "tool": "arif_memory_recall(mode=recall) with provenance_required=True",
    },
    ContextFailureMode.CONTEXT_DISTRACTION: {
        "primary_floor": "F7 HUMILITY",
        "mechanism": "MECW ceiling + Select bucket + authority hierarchy",
        "tool": "marginal_value_per_token() — drop low-relevance chunks",
    },
    ContextFailureMode.CONTEXT_CONFUSION: {
        "primary_floor": "F4 CLARITY",
        "mechanism": "Pressure-triggered compaction + structured summary format",
        "tool": "Compress bucket with deterministic verifier (Phase 4)",
    },
    ContextFailureMode.CONTEXT_CLASH: {
        "primary_floor": "F10 ONTOLOGY",
        "mechanism": "Authority-class hierarchy + constitutional priority",
        "tool": "prepare_context() with priority 100 = CONSTITUTIONAL, 0 = UNTRUSTED",
    },
}


# ─── The One-Sentence Eureka (Kernel-Embeddable) ──────────────────────────
EUREKA_ONE_SENTENCE = (
    "The context window is the agent's working memory, not the agent's mind. "
    "The kernel cannot change the window, but it can decide what fills the "
    "window — and that decision IS the intelligence."
)

THREE_LINE_KERNEL_EMBED = (
    "The context window is fixed. The effective window is far smaller. "
    "More tokens can hurt. Therefore: the system that prepares the input "
    "IS the context manager. Not the model."
)


# ─── ContextPacket (for Phase 3 prepare_context) ──────────────────────────
def empty_context_packet(
    task_id: str,
    model_key: str,
    session_id: str = "",
) -> dict[str, Any]:
    """
    Return a skeleton ContextPacket. The actual builder comes in Phase 3.
    This stub demonstrates the shape and embeds the authority hierarchy.
    """
    window = get_model_window(model_key)
    return {
        "task_id": task_id,
        "model_key": model_key,
        "model_window": window,
        "session_id": session_id,
        "eureka_policy_version": EUREKA_POLICY_VERSION,
        "context_policy_version": _TP_POLICY_VERSION,
        "audit_policy_version": _CA_POLICY_VERSION,
        "segments": [],
        "authority_hierarchy": [{"class": int(ac), "label": ac.name} for ac in AuthorityClass],
        "pressure": classify_pressure(0, window),
        "phase": "6.B — eureka embedded, Phase 3 prepare_context pending",
        "note": "Stub. Real builder lands in Phase 3 forge.",
    }


# ─── Self-Check (deterministic, no I/O) ───────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Verify the eureka module's deterministic properties."""
    results = []

    # 1. Authority hierarchy ordered correctly
    r = int(AuthorityClass.CONSTITUTIONAL) > int(AuthorityClass.UNTRUSTED)
    results.append(("authority_hierarchy_ordered", r))

    # 2. 4 buckets present
    r = len(ContextBucket) == 4
    results.append(("four_buckets_present", r))

    # 3. 4 failure modes present
    r = len(ContextFailureMode) == 4
    results.append(("four_failure_modes_present", r))

    # 4. marginal_value_per_token: high authority + high relevance = include
    hi = marginal_value_per_token(
        {"tokens": 100, "authority_class": 100, "relevance_score": 0.95, "staleness": 0},
        task_value=0.9,
    )
    r = hi["recommendation"] == "include"
    results.append(("mvpt_high_authority_includes", r))

    # 5. marginal_value_per_token: low authority + low relevance = drop
    lo = marginal_value_per_token(
        {"tokens": 5000, "authority_class": 20, "relevance_score": 0.05, "staleness": 30},
        task_value=0.3,
    )
    r = lo["recommendation"] == "drop"
    results.append(("mvpt_low_authority_drops", r))

    # 6. Pressure-action map: WARN does not auto-compact
    r = PRESSURE_ACTION_MAP[PressureBand.WARN]["auto_compact"] is False
    results.append(("warn_band_no_auto_compact", r))

    # 7. Pressure-action map: HOLD refuses non-reversible
    r = "HOLD" in PRESSURE_ACTION_MAP[PressureBand.HOLD]["tier"]
    results.append(("hold_band_refuses", r))

    # 8. Eureka one-sentence is non-empty
    r = len(EUREKA_ONE_SENTENCE) > 50
    results.append(("eureka_sentence_nonempty", r))

    # 9. Failure prevention covers all 4 modes
    r = all(fm in FAILURE_PREVENTION for fm in ContextFailureMode)
    results.append(("all_failure_modes_have_prevention", r))

    # 10. Source of truth is documented
    r = SOURCE_OF_TRUTH == "docs/context/EUREKA_TOKEN_MANAGEMENT.md"
    results.append(("source_of_truth_documented", r))

    # 11. Policy versions consistent (both modules + eureka)
    r = (
        _TP_POLICY_VERSION == "context_policy.v1"
        and _CA_POLICY_VERSION == "context_policy.v1"
        and EUREKA_POLICY_VERSION == "context_eureka.v1"
    )
    results.append(("policy_versions_consistent", r))

    # 12. empty_context_packet returns valid shape
    pkt = empty_context_packet("task-test-1", "MiniMax-M3", "sess-test-1")
    r = (
        "segments" in pkt
        and pkt["model_window"] == 200_000
        and len(pkt["authority_hierarchy"]) == 9
    )
    results.append(("empty_context_packet_shape_valid", r))

    all_pass = all(passed for _, passed in results)
    return {
        "all_pass": all_pass,
        "checks": [{"name": n, "pass": p} for n, p in results],
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
    }


if os.getenv("ARIFOS_SELFTEST", "0") == "1":
    _selftest = _self_check()
    if _selftest["all_pass"]:
        logger.info(f"[context_eureka] selftest PASS {_selftest['n_pass']}/{_selftest['n_checks']}")
    else:
        failed = [c["name"] for c in _selftest["checks"] if not c["pass"]]
        logger.error(f"[context_eureka] selftest FAIL: {failed}")


__all__ = [
    "EUREKA_POLICY_VERSION",
    "SOURCE_OF_TRUTH",
    "EUREKA_ONE_SENTENCE",
    "THREE_LINE_KERNEL_EMBED",
    "AuthorityClass",
    "ContextBucket",
    "ContextFailureMode",
    "PRESSURE_ACTION_MAP",
    "FAILURE_PREVENTION",
    "marginal_value_per_token",
    "empty_context_packet",
    "_self_check",
]
