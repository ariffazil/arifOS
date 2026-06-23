"""
ART Registry — W2 implementation.

Per-tool persistent state, bucket classification, per-bucket reflex rules.

This is the W2 deliverable. It complements:
  - runtime/art.py       — the reflex (stateless, ≤500 lines)
  - runtime/art_library.py — the memory (90-day RAG)

The registry adds:
  - TOOL_BUCKET              — collapse 26 tools into 5-6 behavioural buckets
  - PER_BUCKET_BLAST         — default blast_radius per bucket
  - PER_BUCKET_REFLEX_RULES  — bucket-specific reflex heuristics
  - DEFAULT_TOOL_STATE       — initial ToolState per tool

WAJIB per GENESIS/030_ART_VS_KERNEL.md §3:
  - Per-tool persistent ToolState (was MAKRUH-NOW, this fixes it)

Doctrine reference: GENESIS/030_ART_VS_KERNEL.md

Wired into: pre_execution_gate._art_reflex_check (Gate 2.5)

DITEMPA BUKAN DIBERI — 26 tools, 5 buckets, one reflex.
"""

from __future__ import annotations

from threading import Lock
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# BUCKET CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════
#
# Collapse 26 registered tools into 5-6 behavioural buckets.
# ART does not see tool NAMES — it sees buckets + lifecycle + blast_radius.
# This is the chaos compressor: from "26 random tools" to "5 patterns + rules".


TOOL_BUCKET: dict[str, str] = {
    # ── SENSE / EVIDENCE — read-only, low blast, frequent use ──────────────
    "arif_observe": "sense",
    "arif_fetch": "sense",
    "arif_schema_echo": "sense",
    "arif_ping": "sense",
    "arif_transport_echo": "sense",
    "arif_version_echo": "sense",
    "arif_initialize_probe": "sense",
    "arif_conformance_report": "sense",
    # ── MIND / ROUTE — mutate belief/routing, not external reality ─────────
    "arif_think": "mind",
    "arif_compose": "mind",
    "arif_kernel_route": "mind",
    "arif_route": "mind",
    "arif_triage": "mind",
    "arif_memory_recall": "mind",
    "arif_kernel_status": "mind",
    "arif_kernel_attest": "mind",
    "arif_kernel_health": "mind",
    # ── HEART — ethical critique, can shape agent behavior ────────────────
    "arif_critique": "heart",
    # ── GATEWAY / BRIDGE — cross-agent, high-blast control plane ───────────
    "arif_gateway_connect": "gateway",
    "arif_bridge": "bridge",
    "arif_bridge_connect": "bridge",
    # ── AUTHORITY — IRREVERSIBLE / APEX lane, sovereign-grade ──────────────
    "arif_init": "authority",
    "arif_measure": "authority",
    "arif_forge": "authority",
    "arif_judge": "authority",
    "arif_seal": "authority",
}


# ═══════════════════════════════════════════════════════════════════════════════
# PER-BUCKET BLAST RADIUS
# ═══════════════════════════════════════════════════════════════════════════════


PER_BUCKET_BLAST: dict[str, str] = {
    "sense": "low",  # read-only, no external side effects
    "mind": "low",  # mutates internal belief/routing only
    "heart": "medium",  # ethical critique shapes downstream behavior
    "gateway": "high",  # cross-agent calls — federation scope
    "bridge": "high",  # direct organ tool calls — out-of-process
    "authority": "high",  # IRREVERSIBLE/APEX — sovereign lane
}


# ═══════════════════════════════════════════════════════════════════════════════
# PER-BUCKET REFLEX RULES
# ═══════════════════════════════════════════════════════════════════════════════


PER_BUCKET_REFLEX_RULES: dict[str, dict[str, Any]] = {
    "sense": {
        "allow_action_class_above_observe": False,  # OBSERVE only
        "downgrade_to": None,  # already at floor
        "trust_state_required": "OBSERVED",  # even OBSERVED is fine for read-only
    },
    "mind": {
        "allow_action_class_above_observe": True,  # can mutate internal state
        "downgrade_to": "observe",  # can downgrade MUTATE to OBSERVE
        "trust_state_required": "OBSERVED",
    },
    "heart": {
        "allow_action_class_above_observe": True,
        "downgrade_to": "observe",
        "trust_state_required": "TRUSTED",  # ethical critique needs trust
    },
    "gateway": {
        "allow_action_class_above_observe": True,
        "downgrade_to": "observe",
        "trust_state_required": "TRUSTED",  # cross-agent requires trust
    },
    "bridge": {
        "allow_action_class_above_observe": True,
        "downgrade_to": "observe",
        "trust_state_required": "TRUSTED",  # direct organ call requires trust
    },
    "authority": {
        "allow_action_class_above_observe": True,
        "downgrade_to": None,  # IRREVERSIBLE cannot safely downgrade
        "trust_state_required": "TRUSTED",  # sovereign lane
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT TOOL STATE (per-tool initial seed)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Per-tool initial ToolState. The runtime state lives in art_library; this is
# just the seed used by pre_execution_gate when no library entry exists yet.
#
# Pre-W2: all manifest tools hardcoded TRUSTED (unsafe — blind trust).
# Post-W2: each tool starts OBSERVED. TRUSTED must be earned (low failure
# rate + schema_locked via art.py state transitions).
#
# Backward compat: tools UNKNOWN to the registry fall back to TRUSTED
# (preserves pre-W2 behavior for tools added without registry update).


DEFAULT_TOOL_STATE: dict[str, str] = {
    tool: "OBSERVED"  # all start observed — TRUSTED is earned, not given
    for tool in TOOL_BUCKET
}


# ═══════════════════════════════════════════════════════════════════════════════
# ART REGISTRY CLASS
# ═══════════════════════════════════════════════════════════════════════════════
#
# Singleton wrapper exposing the registry API used by pre_execution_gate.
# Uses lazy import to avoid circular dependencies.


class ArtRegistry:
    """Per-tool persistent state + bucket classification."""

    _instance: "ArtRegistry | None" = None
    _lock = Lock()

    def __init__(self) -> None:
        self._cache: dict[str, str] = {}  # tool_name → ToolState.value (cached)

    @classmethod
    def instance(cls) -> "ArtRegistry":
        """Return process-wide singleton (thread-safe)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    # ── Tool state ────────────────────────────────────────────────────────

    def get_tool_state_cached(self, tool_name: str) -> str:
        """Return ToolState string for tool. Used by pre_execution_gate.

        Resolution order:
          1. In-process cache (fast path)
          2. DEFAULT_TOOL_STATE (registry seed)
          3. TRUSTED (backward compat for unknown tools)
        """
        if tool_name in self._cache:
            return self._cache[tool_name]
        state = DEFAULT_TOOL_STATE.get(tool_name, "TRUSTED")
        self._cache[tool_name] = state
        return state

    def set_tool_state(self, tool_name: str, state: str) -> None:
        """Update cached state. Called by art.py state transitions."""
        self._cache[tool_name] = state

    def reset_cache(self) -> None:
        """Clear cache — used by tests and explicit refresh."""
        self._cache.clear()

    # ── Bucket classification ─────────────────────────────────────────────

    def get_bucket(self, tool_name: str) -> str | None:
        return TOOL_BUCKET.get(tool_name)

    def get_default_blast(self, bucket: str) -> str:
        return PER_BUCKET_BLAST.get(bucket, "unknown")

    def get_reflex_rules(self, bucket: str) -> dict[str, Any]:
        return PER_BUCKET_REFLEX_RULES.get(bucket, {})

    def get_default_tool_state(self, tool_name: str) -> str:
        return DEFAULT_TOOL_STATE.get(tool_name, "TRUSTED")

    def all_buckets(self) -> list[str]:
        return ["sense", "mind", "heart", "gateway", "bridge", "authority"]

    def tools_in_bucket(self, bucket: str) -> list[str]:
        return sorted(t for t, b in TOOL_BUCKET.items() if b == bucket)

    def bucket_stats(self) -> dict[str, int]:
        counts: dict[str, int] = {b: 0 for b in self.all_buckets()}
        for b in TOOL_BUCKET.values():
            counts[b] = counts.get(b, 0) + 1
        return counts

    def registered_count(self) -> int:
        return len(TOOL_BUCKET)


def get_registry() -> ArtRegistry:
    """Module-level accessor — returns singleton ArtRegistry instance.

    Used by pre_execution_gate._art_reflex_check at Gate 2.5.
    """
    return ArtRegistry.instance()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL CONVENIENCE FUNCTIONS (for callers that don't need the class)
# ═══════════════════════════════════════════════════════════════════════════════


def get_bucket(tool_name: str) -> str | None:
    """Return bucket for tool, or None if unknown."""
    return TOOL_BUCKET.get(tool_name)


def get_default_blast(bucket: str) -> str:
    """Return default blast_radius string for bucket."""
    return PER_BUCKET_BLAST.get(bucket, "unknown")


def get_reflex_rules(bucket: str) -> dict[str, Any]:
    """Return reflex rules dict for bucket."""
    return PER_BUCKET_REFLEX_RULES.get(bucket, {})


def get_default_tool_state(tool_name: str) -> str:
    """Return initial ToolState string for tool.

    Used by callers that want the registry seed without the singleton wrapper.
    """
    return DEFAULT_TOOL_STATE.get(tool_name, "TRUSTED")


__all__ = [
    # data
    "TOOL_BUCKET",
    "PER_BUCKET_BLAST",
    "PER_BUCKET_REFLEX_RULES",
    "DEFAULT_TOOL_STATE",
    # class
    "ArtRegistry",
    "get_registry",
    # convenience
    "get_bucket",
    "get_default_blast",
    "get_reflex_rules",
    "get_default_tool_state",
]
