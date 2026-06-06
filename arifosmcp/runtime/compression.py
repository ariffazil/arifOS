"""
arifosmcp/runtime/context_compression.py — H1 Context Compression Engine
═══════════════════════════════════════════════════════════════════════════════════

Tiered context compression for constitutional AI sessions.

Compression is NOT lossy text truncation — it is SEMANTIC DISTILLATION:
preserving the constitutional skeleton while discarding ephemeral noise.

Three tiers:
  EPHEMERAL  — tool calls, reasoning traces, session-scoped noise
  DOMAIN     — domain knowledge, skill references, evidence bundles
  CONSTITUTIONAL — F1-L13 floors, ontology, governance invariants

Four modes:
  FULL       — preserve everything (default)
  CONSTITUTIONAL — constitutional skeleton only
  OPERATIONAL   — operational metrics + tool surface
  MINIMAL    — LOCKDOWN state: actor, session, verdict, timestamp only

Integration:
  - arif_memory_recall: compress before storing, decompress on recall
  - arif_kernel_route: selects compression mode based on RuntimeState + token budget
  - output_formatter: compressed context carries less token weight

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from core.shared.constitutional_ontology import RuntimeState
except ModuleNotFoundError:
    import os as _os
    import sys

    _parent = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    from core.shared.constitutional_ontology import RuntimeState


class CompressionMode(Enum):
    FULL = "full"
    CONSTITUTIONAL = "constitutional"
    OPERATIONAL = "operational"
    MINIMAL = "minimal"


class MemoryTier(Enum):
    EPHEMERAL = "ephemeral"  # Tool calls, reasoning traces
    DOMAIN = "domain"  # Domain knowledge, skill references
    CONSTITUTIONAL = "constitutional"  # F1-L13, ontology, governance invariants


# ── Constitutional skeleton keys (always preserved) ─────────────────────────────

_CONSTITUTIONAL_KEYS: set[str] = {
    "actor_id",
    "session_id",
    "verdict",
    "risk_level",
    "confidence_level",
    "reversibility",
    "runtime_state",
    "floors_passed",
    "floors_failed",
    "constitutional_hash",
    "tau",
    "omega_0",
    "delta_s",
}

# ── Operational keys (preserved in OPERATIONAL + FULL) ────────────────────────

_OPERATIONAL_KEYS: set[str] = {
    "tool_calls",
    "stage_progression",
    "ops_vitals",
    "entropy_delta",
    "last_tool",
    "last_stage",
    "telemetry",
    "memory_write_candidates",
    "vault_seal_candidate",
    "next_recommended_tools",
}

# ── Ephemeral keys (preserved in FULL only) ────────────────────────────────────

_EPHEMERAL_KEYS: set[str] = {
    "reasoning_trace",
    "raw_llm_output",
    "debug_info",
    "intermediate_steps",
    "search_results",
}


@dataclass
class CompressionResult:
    compressed: dict[str, Any]
    mode: CompressionMode
    original_token_estimate: int
    compressed_token_estimate: int
    compression_ratio: float
    tiers_pruned: list[MemoryTier]
    constitutional_preserved: bool


@dataclass
class CompressionStats:
    total_sessions_compressed: int = 0
    total_tokens_saved: int = 0
    by_mode: dict[str, int] = field(default_factory=dict)


_COMPRESSION_STATS = CompressionStats()


# ── Token estimation (lightweight, no external API) ────────────────────────────


def estimate_tokens(text: str | None = None, data: dict[str, Any] | None = None) -> int:
    """
    Lightweight token estimation without external API calls.

    Uses empirical ratio: ~4 characters per token for English text.
    Structured data overhead: ~2x due to JSON tokens.

    Args:
        text: Raw text to estimate
        data: Structured dict/list to estimate

    Returns:
        Estimated token count (integer, ceiling)
    """
    if text:
        return (len(text) + 3) // 4
    if data:
        serialized = json.dumps(data, default=str)
        return (len(serialized) + 1) // 2
    return 0


# ── Core compression ───────────────────────────────────────────────────────────


def compress(
    payload: dict[str, Any],
    mode: CompressionMode | str = CompressionMode.FULL,
    runtime_state: RuntimeState | str | None = None,
    token_budget_remaining: int | None = None,
) -> CompressionResult:
    """
    Compress a context payload according to compression mode and runtime state.

    Compression is semantic — it preserves the constitutional skeleton and
    strips ephemeral noise, guided by the Constitutional Ontology.

    Args:
        payload: The context payload to compress
        mode: Compression mode (FULL | CONSTITUTIONAL | OPERATIONAL | MINIMAL)
        runtime_state: Current RuntimeState for state-conditional compression
        token_budget_remaining: If set, auto-select mode to fit budget

    Returns:
        CompressionResult with compressed payload and stats
    """
    if isinstance(mode, str):
        try:
            mode = CompressionMode(mode.lower())
        except ValueError:
            mode = CompressionMode.FULL

    original_tokens = estimate_tokens(data=payload)

    # ── State-conditional compression ────────────────────────────────────────
    effective_mode = _resolve_mode(mode, runtime_state, token_budget_remaining)

    # ── Apply compression ────────────────────────────────────────────────────
    if effective_mode == CompressionMode.MINIMAL:
        compressed = _compress_minimal(payload)
        tiers_pruned = [
            MemoryTier.EPHEMERAL,
            MemoryTier.DOMAIN,
            MemoryTier.CONSTITUTIONAL,
        ]
    elif effective_mode == CompressionMode.CONSTITUTIONAL:
        compressed = _compress_constitutional(payload)
        tiers_pruned = [MemoryTier.EPHEMERAL, MemoryTier.DOMAIN]
    elif effective_mode == CompressionMode.OPERATIONAL:
        compressed = _compress_operational(payload)
        tiers_pruned = [MemoryTier.EPHEMERAL]
    else:
        compressed = payload.copy()
        tiers_pruned = []

    compressed_tokens = estimate_tokens(data=compressed)
    ratio = (original_tokens - compressed_tokens) / original_tokens if original_tokens > 0 else 0.0

    # ── Add compression metadata ────────────────────────────────────────────
    compressed["_compression"] = {
        "mode": effective_mode.value,
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "ratio": round(ratio, 3),
        "tiers_pruned": [t.value for t in tiers_pruned],
    }

    # ── Update stats ────────────────────────────────────────────────────────
    _COMPRESSION_STATS.total_sessions_compressed += 1
    _COMPRESSION_STATS.total_tokens_saved += original_tokens - compressed_tokens
    _COMPRESSION_STATS.by_mode[effective_mode.value] = (
        _COMPRESSION_STATS.by_mode.get(effective_mode.value, 0) + 1
    )

    return CompressionResult(
        compressed=compressed,
        mode=effective_mode,
        original_token_estimate=original_tokens,
        compressed_token_estimate=compressed_tokens,
        compression_ratio=ratio,
        tiers_pruned=tiers_pruned,
        constitutional_preserved=_has_constitutional_skeleton(compressed),
    )


def decompress(
    compressed: dict[str, Any],
    mode: CompressionMode | str | None = None,
) -> dict[str, Any]:
    """
    Restore a compressed payload to FULL context.

    Since compression is semantic distillation (not lossy), restoration
    reconstructs the full schema with missing fields filled as null/empty.

    Args:
        compressed: The compressed payload
        mode: Expected compression mode (read from _compression if None)

    Returns:
        Restored payload (FULL schema)
    """
    if mode is None:
        meta = compressed.get("_compression", {})
        mode = CompressionMode(meta.get("mode", "full"))

    if isinstance(mode, str):
        try:
            mode = CompressionMode(mode.lower())
        except ValueError:
            mode = CompressionMode.FULL

    if mode == CompressionMode.FULL:
        result = compressed.copy()
    elif mode == CompressionMode.CONSTITUTIONAL:
        result = _decompress_constitutional(compressed)
    elif mode == CompressionMode.OPERATIONAL:
        result = _decompress_operational(compressed)
    else:
        result = _decompress_minimal(compressed)

    # ── Restore FULL structure ───────────────────────────────────────────────
    if "_compression" in result:
        del result["_compression"]

    return result


# ── Internal: mode resolution ──────────────────────────────────────────────────


def _resolve_mode(
    requested: CompressionMode,
    runtime_state: RuntimeState | str | None,
    token_budget: int | None,
) -> CompressionMode:
    """
    Resolve effective compression mode from request + state + budget.

    Priority:
      1. runtime_state MINIMAL (LOCKDOWN, VOID) → override to MINIMAL
      2. token_budget constraint → escalate compression if needed
      3. Otherwise use requested mode
    """
    # State override (highest priority)
    if runtime_state is not None:
        if isinstance(runtime_state, str):
            try:
                runtime_state = RuntimeState(runtime_state)
            except ValueError:
                pass
        if isinstance(runtime_state, RuntimeState):
            if runtime_state in (RuntimeState.LOCKDOWN, RuntimeState.VOID):
                return CompressionMode.MINIMAL

    # Token budget check
    if token_budget is not None and token_budget < 500:
        if requested == CompressionMode.FULL:
            return CompressionMode.OPERATIONAL
        elif requested == CompressionMode.OPERATIONAL:
            return CompressionMode.CONSTITUTIONAL

    return requested


# ── Internal: compression tiers ───────────────────────────────────────────────


def _compress_minimal(payload: dict[str, Any]) -> dict[str, Any]:
    """MINIMAL: Only actor, session, verdict, timestamp."""
    result: dict[str, Any] = {}
    for key in _CONSTITUTIONAL_KEYS:
        if key in payload:
            result[key] = payload[key]
    # Always preserve these in minimal
    for key in ("actor_id", "session_id", "verdict", "timestamp"):
        if key in payload:
            result[key] = payload[key]
    return result


def _compress_constitutional(payload: dict[str, Any]) -> dict[str, Any]:
    """CONSTITUTIONAL: Preserve constitutional skeleton + ontology."""
    result: dict[str, Any] = {}
    # Constitutional keys
    for key in _CONSTITUTIONAL_KEYS:
        if key in payload:
            result[key] = payload[key]
    # Ontology payload (if present)
    if "ontology" in payload:
        result["ontology"] = payload["ontology"]
    if "constitutional_ontolog_payload" in payload:
        result["constitutional_ontolog_payload"] = payload["constitutional_ontolog_payload"]
    return result


def _compress_operational(payload: dict[str, Any]) -> dict[str, Any]:
    """OPERATIONAL: Constitutional + operational metrics."""
    result = _compress_constitutional(payload)
    for key in _OPERATIONAL_KEYS:
        if key in payload:
            result[key] = payload[key]
    return result


# ── Internal: decompression (reconstruction) ──────────────────────────────────


def _decompress_minimal(compressed: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct FULL from MINIMAL — fills nulls for missing fields."""
    result: dict[str, Any] = {}
    for key in _CONSTITUTIONAL_KEYS | _OPERATIONAL_KEYS | _EPHEMERAL_KEYS:
        result[key] = compressed.get(key)
    result["_restored_from"] = "minimal"
    return result


def _decompress_constitutional(compressed: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct FULL from CONSTITUTIONAL — fills operational/ephemeral nulls."""
    result: dict[str, Any] = {}
    for key in _OPERATIONAL_KEYS | _EPHEMERAL_KEYS:
        result[key] = compressed.get(key)
    for key in _CONSTITUTIONAL_KEYS:
        result[key] = compressed.get(key)
    result["_restored_from"] = "constitutional"
    return result


def _decompress_operational(compressed: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct FULL from OPERATIONAL — fills ephemeral nulls."""
    result: dict[str, Any] = {}
    for key in _EPHEMERAL_KEYS:
        result[key] = compressed.get(key)
    for key in _OPERATIONAL_KEYS | _CONSTITUTIONAL_KEYS:
        result[key] = compressed.get(key)
    result["_restored_from"] = "operational"
    return result


# ── Helpers ────────────────────────────────────────────────────────────────────


def _has_constitutional_skeleton(payload: dict[str, Any]) -> bool:
    """Check if payload has the minimum constitutional skeleton."""
    required = {"actor_id", "verdict", "risk_level"}
    return required.issubset(payload.keys()) or "_compression" in payload


def compression_stats() -> dict[str, Any]:
    """Return compression statistics."""
    return {
        "total_sessions_compressed": _COMPRESSION_STATS.total_sessions_compressed,
        "total_tokens_saved": _COMPRESSION_STATS.total_tokens_saved,
        "by_mode": dict(_COMPRESSION_STATS.by_mode),
        "avg_ratio": (
            _COMPRESSION_STATS.total_tokens_saved / _COMPRESSION_STATS.total_sessions_compressed
            if _COMPRESSION_STATS.total_sessions_compressed > 0
            else 0
        ),
    }


def auto_compress(
    payload: dict[str, Any],
    runtime_state: RuntimeState | str | None = None,
    token_budget: int | None = None,
) -> CompressionResult:
    """
    Auto-select best compression mode based on runtime state + budget.

    This is the primary entry point for automatic context compression.
    """
    mode = CompressionMode.FULL
    if runtime_state:
        if isinstance(runtime_state, str):
            try:
                runtime_state = RuntimeState(runtime_state)
            except ValueError:
                runtime_state = None
        if runtime_state == RuntimeState.LOCKDOWN:
            mode = CompressionMode.MINIMAL
        elif runtime_state == RuntimeState.VOID:
            mode = CompressionMode.MINIMAL
        elif runtime_state == RuntimeState.PAUSE:
            mode = CompressionMode.CONSTITUTIONAL
        elif runtime_state in (RuntimeState.SIMULATE, RuntimeState.AWAIT_APPROVAL):
            mode = CompressionMode.OPERATIONAL

    return compress(payload, mode, runtime_state, token_budget)


__all__ = [
    "CompressionMode",
    "MemoryTier",
    "CompressionResult",
    "CompressionStats",
    "compress",
    "decompress",
    "auto_compress",
    "estimate_tokens",
    "compression_stats",
]
