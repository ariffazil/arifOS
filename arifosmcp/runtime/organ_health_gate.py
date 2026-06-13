"""
organ_health_gate.py
═══════════════════════════════════════════════════════════════════════════

MCP Surface Governor — organ health gate.

Purpose:
    For each organ (arifOS, GEOX, WEALTH, WELL, minimax-media, minimax-code,
    minimax-search, AAA, A-FORGE), determine its current health status and
    return either:
      - "healthy" → full tool surface visible
      - "degraded" → 3-tool diagnostic shortlist only
      - "unknown"  → 1-3 diagnostic tools, error noted
      - "not_deployed" → not callable

Health probing:
    1. Try the organ's /health endpoint (per the registry endpoint map).
    2. If 200 with status="healthy", return healthy.
    3. If timeout, error, or status != healthy, return degraded.
    4. If we have no endpoint configured, return unknown.

Caching:
    60s TTL. Federation health is observable, not paranoia-frequent.

F1 AMANAH: read-only probing. No organ state is mutated by this gate.
F2 TRUTH: cache the probe result + raw /health response for audit.

Author: @integrator (session 2026-06-12-mcp-governor-and-minimax-forge)
Forged: 2026-06-12
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import urllib.error
import urllib.request

from mcp_visibility_policy import (
    DIAGNOSTIC_TOOL_NAMES,
    OrganHealth,
    ToolEntry,
    load_registry,
    Tier,
)

# ─────────────────────────────────────────────────────────────────────────────
# Cache
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class HealthCacheEntry:
    """One entry in the per-organ health cache."""

    health: OrganHealth
    raw_response: dict[str, Any] | None = None
    error: str | None = None
    probed_at: float = 0.0
    ttl_seconds: int = 60


_HEALTH_CACHE: dict[str, HealthCacheEntry] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Probe
# ─────────────────────────────────────────────────────────────────────────────


def _probe_http(url: str, timeout: float = 2.0) -> tuple[OrganHealth, dict[str, Any] | None, str | None]:
    """Synchronous HTTP GET to an organ's /health endpoint.

    Returns (health, raw_response_dict, error_message).
    F2 truth: we never fabricate healthy status. If we can't prove it, we say degraded.
    """
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return OrganHealth.DEGRADED, None, f"HTTP {resp.status}"
            body = resp.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                return OrganHealth.DEGRADED, None, "non-json response"
            status_val = (payload.get("status") or "").lower()
            if status_val == "healthy":
                return OrganHealth.HEALTHY, payload, None
            return OrganHealth.DEGRADED, payload, f"status={status_val!r}"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        return OrganHealth.DEGRADED, None, f"{type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def get_organ_health(organ_id: str, *, force_refresh: bool = False) -> OrganHealth:
    """Return the cached or freshly-probed health of an organ."""
    entry = _HEALTH_CACHE.get(organ_id)
    now = time.time()
    if entry and not force_refresh and (now - entry.probed_at) < entry.ttl_seconds:
        return entry.health

    reg = load_registry()
    endpoint = None
    for organ in reg.get("organs", []) or []:
        if isinstance(organ, dict) and organ.get("id") == organ_id:
            endpoint = organ.get("endpoint")
            break

    if not endpoint:
        _HEALTH_CACHE[organ_id] = HealthCacheEntry(
            health=OrganHealth.UNKNOWN,
            error="no endpoint configured",
            probed_at=now,
        )
        return OrganHealth.UNKNOWN

    # Strip /mcp suffix and append /health
    health_url = endpoint.rstrip("/").rsplit("/mcp", 1)[0] + "/health"
    health, raw, err = _probe_http(health_url)
    _HEALTH_CACHE[organ_id] = HealthCacheEntry(
        health=health,
        raw_response=raw,
        error=err,
        probed_at=now,
    )
    return health


def get_organ_health_detail(organ_id: str, *, force_refresh: bool = False) -> HealthCacheEntry:
    """Return the full cache entry (for diagnostics + audit)."""
    if force_refresh or organ_id not in _HEALTH_CACHE:
        get_organ_health(organ_id, force_refresh=force_refresh)
    return _HEALTH_CACHE[organ_id]


# ─────────────────────────────────────────────────────────────────────────────
# Diagnostic shortlist generator
# ─────────────────────────────────────────────────────────────────────────────


def get_diagnostic_shortlist(organ_id: str) -> list[ToolEntry]:
    """Return the 3-tool diagnostic shortlist for a degraded/unknown organ.

    Per amendment_001: if organ_health != healthy, expose only 3 diagnostic
    tools (organ_attest, organ_status, organ_repair_hint) for that organ.
    """
    organ_health = get_organ_health(organ_id)
    if organ_health == OrganHealth.HEALTHY:
        return []

    shortlist: list[ToolEntry] = []
    descriptions = {
        "organ_attest": f"Probe {organ_id} and return liveness verdict",
        "organ_status": f"Return {organ_id} subsystem status (degraded/unknown)",
        "organ_repair_hint": f"Return {organ_id} repair steps (F1 AMANAH: read-only)",
    }
    for name in DIAGNOSTIC_TOOL_NAMES:
        shortlist.append(
            ToolEntry(
                name=name,
                organ=organ_id,
                tier=Tier.ORGAN,
                health=organ_health,
                version="diagnostic-v1",
                constitution_hash="diagnostic",
                schema_hash="diagnostic",
                description=descriptions.get(name, f"Diagnostic for {organ_id}"),
                schema_tokens=80,
            )
        )
    return shortlist


# ─────────────────────────────────────────────────────────────────────────────
# Cache invalidation
# ─────────────────────────────────────────────────────────────────────────────


def invalidate_cache(organ_id: str | None = None) -> None:
    """Invalidate the health cache (all or one organ).

    F1 AMANAH: cache invalidation does not touch the organ. It just clears
    our cached read. The organ itself is not modified.
    """
    global _HEALTH_CACHE
    if organ_id is None:
        _HEALTH_CACHE = {}
    else:
        _HEALTH_CACHE.pop(organ_id, None)


# ─────────────────────────────────────────────────────────────────────────────
# Health summary across all known organs
# ─────────────────────────────────────────────────────────────────────────────


def health_summary() -> dict[str, Any]:
    """Probe all known organs and return a summary dict."""
    reg = load_registry()
    out: dict[str, Any] = {}
    for organ in reg.get("organs", []) or []:
        if not isinstance(organ, dict):
            continue
        organ_id = organ.get("id", "unknown")
        entry = get_organ_health_detail(organ_id, force_refresh=True)
        out[organ_id] = {
            "health": entry.health.value,
            "error": entry.error,
            "probed_at": entry.probed_at,
            "tier": organ.get("tier"),
            "endpoint": organ.get("endpoint"),
        }
    return out


__all__ = [
    "HealthCacheEntry",
    "get_organ_health",
    "get_organ_health_detail",
    "get_diagnostic_shortlist",
    "invalidate_cache",
    "health_summary",
]
