"""
arifosmcp/tools/canary_multimode.py — Canary Multimode Collapse
═════════════════════════════════════════════════════════════════

Collapses 6 individual canary tools into one `arif_canary` with mode dispatch.

ART: All modes are OBSERVE-class, blast=low, trust=evidence, zero floors.
ACT: Single-call programs, no ceremony. One classification, six probes.

Modes:
  ping              — lightweight liveness probe
  schema_echo       — payload round-trip test
  version_echo      — protocol version check
  transport_echo    — transport detail dump
  initialize_probe  — MCP handshake test
  conformance_report — full conformance spine (8 checks)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_CANARY_MODES = (
    "ping",
    "schema_echo",
    "version_echo",
    "transport_echo",
    "initialize_probe",
    "conformance_report",
)


async def arif_canary(
    mode: str = "ping",
    payload: Any = None,
    _envelope: dict[str, Any] | None = None,
    client_capabilities: dict[str, Any] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    include_constitution: bool = False,
) -> dict[str, Any]:
    """Unified canary probe — one tool, six diagnostic modes.

    All modes are OBSERVE-class, zero-floor, read-only.
    Use mode=ping for liveness, mode=conformance_report for full spine.
    """
    from arifosmcp.runtime.tools import _RUNTIME_DIAGNOSTIC_HANDLERS

    if mode not in _CANARY_MODES:
        return {
            "status": "error",
            "tool": "arif_canary",
            "mode": mode,
            "error": f"Unknown canary mode '{mode}'. Valid: {', '.join(_CANARY_MODES)}",
        }

    # Dispatch to existing runtime handlers
    try:
        if mode == "ping":
            handler = _RUNTIME_DIAGNOSTIC_HANDLERS.get("arif_ping")
            if handler:
                return handler(
                    mode="probe",
                    session_id=session_id,
                    actor_id=actor_id,
                    include_constitution=include_constitution,
                    _envelope=_envelope,
                )

        elif mode == "schema_echo":
            handler = _RUNTIME_DIAGNOSTIC_HANDLERS.get("arif_schema_echo")
            if handler:
                return handler(
                    payload=payload,
                    _envelope=_envelope,
                    client_capabilities=client_capabilities,
                )

        elif mode == "version_echo":
            handler = _RUNTIME_DIAGNOSTIC_HANDLERS.get("arif_version_echo")
            if handler:
                return handler(
                    payload=payload,
                    _envelope=_envelope,
                    client_capabilities=client_capabilities,
                )

        elif mode == "transport_echo":
            handler = _RUNTIME_DIAGNOSTIC_HANDLERS.get("arif_transport_echo")
            if handler:
                return handler(
                    payload=payload,
                    _envelope=_envelope,
                    client_capabilities=client_capabilities,
                )

        elif mode == "initialize_probe":
            handler = _RUNTIME_DIAGNOSTIC_HANDLERS.get("arif_initialize_probe")
            if handler:
                return handler(
                    payload=payload,
                    _envelope=_envelope,
                    client_capabilities=client_capabilities,
                )

        elif mode == "conformance_report":
            handler = _RUNTIME_DIAGNOSTIC_HANDLERS.get("arif_conformance_report")
            if handler:
                return handler(
                    payload=payload,
                    _envelope=_envelope,
                    client_capabilities=client_capabilities,
                    fast=True,  # P3 fix 2026-06-30: reduce timeouts to prevent MCP timeout
                )

        return {
            "status": "error",
            "tool": "arif_canary",
            "mode": mode,
            "error": f"Handler for mode '{mode}' not registered",
        }

    except Exception as e:
        logger.warning("arif_canary(%s) failed: %s", mode, e, exc_info=True)
        return {
            "status": "error",
            "tool": "arif_canary",
            "mode": mode,
            "error": str(e),
        }


CANARY_MODES = _CANARY_MODES
