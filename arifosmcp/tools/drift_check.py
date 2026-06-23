"""
mcp_drift_check — Read-only surface drift detector.

Compares the canonical manifest against the live registered MCP surface.
Does NOT mutate registry by default.

Modes:
    report  = read-only drift report (default)
    warn    = logs drift, does not fail
    strict  = raises on drift (opt-in, gated by ARIFOS_DRIFT_ENFORCEMENT)

PHOENIX-72 gate: drift_detected=false + counts match target.

C2-3 fix (2026-06-21): added `compute_surface_hash()` — SHA256 of the
canonical tool surface (names + descriptions). This is the kernel's
self-attestation for the live tool surface. If it changes between boots
without a 999_SEAL, that is surface drift and must be investigated.

C2-1 fix (2026-06-21): added `check_tool_exists()` + `arif_tool_exists`
canary handler — fabrication defense for tool names. If a model claims
a tool exists that doesn't, this returns `exists: False` with the
closest real tool name.

C2-4 fix (2026-06-21): per-tool `tool_schema_hash` exposed so clients
can detect schema drift.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Default enforcement level from environment
DRIFT_ENFORCEMENT = os.getenv("ARIFOS_DRIFT_ENFORCEMENT", "report")


def _load_manifest() -> dict[str, Any]:
    """Load the canonical tool manifest."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS
    from arifosmcp.runtime.public_surface import DIAGNOSTIC_TOOLS, EXPANDED_45

    return {
        "canonical13": list(CANONICAL_TOOLS.keys()),
        "expanded45": list(EXPANDED_45),
        "diagnostic": list(DIAGNOSTIC_TOOLS),
    }


def _get_live_tools(mcp_server: Any | None = None) -> list[str]:
    """Extract live registered tool names from the MCP server."""
    # If an mcp server instance is passed, use it
    if mcp_server is not None:
        try:
            return sorted(mcp_server._tools.keys())
        except Exception:
            pass
    # Fallback: derive from canonical handlers + env-gated diagnostic tools.
    # NOTE: EXPANDED_45 aliases are NOT included here because they have no
    # FastMCP handlers. Including them falsely inflates the registered count.
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.public_surface import DIAGNOSTIC_TOOLS
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        # Canonical surface = all entries in CANONICAL_TOOLS that have handlers.
        # The implementation is split between _CANONICAL_HANDLERS (legacy 13)
        # and _RUNTIME_DIAGNOSTIC_HANDLERS (Rule-14 6 + diagnostics).
        live = set(CANONICAL_TOOLS.keys()) & set(CANONICAL_TOOL_HANDLERS.keys())
        if os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "").lower() in ("true", "1", "yes"):
            live.update(DIAGNOSTIC_TOOLS)
        return sorted(live)
    except Exception as e:
        logger.warning(f"Failed to enumerate live tools: {e}")
        return []


# ── C2-3: surface_hash computation ──────────────────────────────────────────


def compute_surface_hash(include_descriptions: bool = True) -> str:
    """SHA256 of the canonical tool surface (names + descriptions).

    This is the kernel's self-attestation for the live tool surface.
    If it changes between boots without a 999_SEAL, that is surface drift
    and the kernel must surface it loudly.

    Args:
        include_descriptions: If True, hash includes tool descriptions.
            Set False to hash only names (smaller, less sensitive to
            description edits).

    Returns:
        "sha256:<64-hex-chars>" of the canonical surface, sorted by name.
    """
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        surface: dict[str, Any] = {}
        for name in sorted(CANONICAL_TOOLS.keys()):
            spec = CANONICAL_TOOLS[name] or {}
            entry: dict[str, Any] = {"name": name}
            if include_descriptions and isinstance(spec, dict):
                if "description" in spec:
                    entry["description"] = spec["description"]
            surface[name] = entry
        payload = json.dumps(surface, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"
    except Exception as _e:
        logger.warning(f"compute_surface_hash failed: {_e}")
        return "sha256:unavailable"


def compute_tool_schema_hash(tool_name: str) -> str:
    """SHA256 of a single tool's schema fingerprint.

    C2-4 fix: surface per-tool schema hash so clients can detect when a
    tool's schema has changed between calls.

    B1 fix (2026-06-21): widened lookup to include DIAGNOSTIC_TOOLS so
    the 6 canary / transport / conformance tools
    (arif_ping, arif_conformance_report, arif_schema_echo,
    arif_version_echo, arif_transport_echo, arif_initialize_probe) get
    real SHA256 fingerprints instead of the fabrication-defense sentinel
    `sha256:unknown_tool`. CANONICAL_TOOLS is still consulted first to
    preserve the canonical-priority contract; DIAGNOSTIC_TOOLS is the
    fallback for live-registered diagnostic tools whose specs are
    declared in `arifosmcp.constitutional_map`.

    Returns "sha256:unknown_tool" only when the tool is genuinely absent
    from BOTH maps — the C2-1 fabrication defense is preserved.
    """
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS

        spec = CANONICAL_TOOLS.get(tool_name)
        if spec is None:
            spec = DIAGNOSTIC_TOOLS.get(tool_name)
        if spec is None:
            return "sha256:unknown_tool"
        payload = json.dumps(spec, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"
    except Exception:
        return "sha256:unavailable"


def check_tool_exists(tool_name: str) -> dict[str, Any]:
    """C2-1 fabrication defense: is this tool real?

    Returns a verdict + closest real match if the tool doesn't exist.
    ChatGPT review named `arif_lease_issue`, `arif_os_attest`,
    `arif_organ_attest_all` as "favorites" — but NONE of these exist
    in the live surface. This function makes fabrication cheap to detect.
    """
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.public_surface import CANONICAL13_PUBLIC_SURFACE
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        exists = tool_name in CANONICAL_TOOLS
        registered = tool_name in CANONICAL_TOOL_HANDLERS
        access = "unknown"
        if exists:
            spec = CANONICAL_TOOLS[tool_name] or {}
            access = spec.get("access", "public") if isinstance(spec, dict) else "public"

        closest = ""
        if not exists:
            best_score = -1
            candidates = sorted(
                set(list(CANONICAL_TOOLS.keys()) + list(CANONICAL13_PUBLIC_SURFACE))
            )
            for candidate in candidates:
                common = 0
                for a, b in zip(tool_name, candidate):
                    if a == b:
                        common += 1
                    else:
                        break
                score = common * 1000 - abs(len(candidate) - len(tool_name))
                if score > best_score:
                    best_score = score
                    closest = candidate

        deprecated_aliases: list[str] = []
        deprecated_map = {
            "arif_os_attest": "arif_kernel_attest (renamed in RULE-14)",
            "arif_organ_attest_all": "arif_organ_attest (single organ, not all)",
            "arif_lease_issue": ("leases are internal-only; use arif_init for authority bootstrap"),
            "arif_daily_intelligence_brief": "not yet registered (planned)",
        }
        if tool_name in deprecated_map:
            deprecated_aliases.append(deprecated_map[tool_name])

        verdict = "SEAL" if registered else "VOID"
        return {
            "name": tool_name,
            "exists": exists,
            "registered": registered,
            "accessible": registered and access != "internal_only",
            "access": access,
            "closest_match": closest,
            "deprecated_aliases": deprecated_aliases,
            "schema_hash": compute_tool_schema_hash(tool_name) if exists else "sha256:unknown_tool",
            "verdict": verdict,
            "canonical_count": len(CANONICAL_TOOLS),
            "registered_count": len(CANONICAL_TOOL_HANDLERS),
        }
    except Exception as _e:
        logger.warning(f"check_tool_exists({tool_name}) failed: {_e}")
        return {
            "name": tool_name,
            "exists": False,
            "registered": False,
            "accessible": False,
            "access": "unknown",
            "closest_match": "",
            "deprecated_aliases": [],
            "schema_hash": "sha256:unavailable",
            "verdict": "VOID",
            "canonical_count": 0,
            "registered_count": 0,
            "error": str(_e),
        }


def mcp_drift_check(
    mode: str = "report",
    target_manifest: str = "canonical13",
    mcp_server: Any | None = None,
) -> dict[str, Any]:
    """Detect drift between manifest and live registered surface.

    C2-3/C2-4 additions (2026-06-21): the report now includes
    `surface_hash` (boot-time drift signal) and `tool_schema_hashes`
    (per-tool schema fingerprints for client-side verification).
    """
    manifest = _load_manifest()
    allowed: set[str] = set()
    if target_manifest in ("all", "canonical13"):
        allowed.update(manifest["canonical13"])
    if target_manifest in ("all", "expanded45"):
        allowed.update(manifest["expanded45"])
    if target_manifest in ("all", "diagnostic"):
        allowed.update(manifest["diagnostic"])

    live = set(_get_live_tools(mcp_server))
    missing = sorted(allowed - live)
    extra = sorted(live - allowed)
    drift_detected = bool(missing or extra)

    surface_hash = compute_surface_hash()
    tool_schema_hashes = {name: compute_tool_schema_hash(name) for name in sorted(live)}

    report = {
        "mode": mode,
        "target_manifest": target_manifest,
        "allowed_count": len(allowed),
        "registered_count": len(live),
        "missing": missing,
        "extra": extra,
        "drift_detected": drift_detected,
        "verdict": "SEAL" if not drift_detected else "HOLD",
        "enforcement": DRIFT_ENFORCEMENT,
        "surface_hash": surface_hash,
        "tool_schema_hashes": tool_schema_hashes,
    }

    if mode == "strict" and drift_detected and DRIFT_ENFORCEMENT == "strict":
        raise RuntimeError(
            f"MCP drift detected: missing={missing}, extra={extra}. "
            f"Set ARIFOS_DRIFT_ENFORCEMENT=report to downgrade to warning."
        )

    if drift_detected:
        logger.warning(
            "mcp_drift_check: drift_detected=true missing=%s extra=%s",
            missing,
            extra,
        )
    else:
        logger.info(
            "mcp_drift_check: drift_detected=false allowed=%d registered=%d",
            len(allowed),
            len(live),
        )

    return report


# ── FastMCP-compatible wrapper ──────────────────────────────────────────────
async def arif_mcp_drift_check(
    mode: str = "report",
    target_manifest: str = "canonical13",
) -> dict[str, Any]:
    """Async wrapper for FastMCP tool registration."""
    return mcp_drift_check(mode=mode, target_manifest=target_manifest)


async def arif_tool_exists(tool_name: str) -> dict[str, Any]:
    """C2-1 fabrication defense canary handler.

    Returns whether `tool_name` exists in the canonical surface and is
    registered with a FastMCP handler. If not, returns `closest_match`
    pointing at the real tool name.

    This is the kernel's defense against tool-result fabrication —
    the failure mode where a model reports using a tool that doesn't
    exist (Opus 4.8 finding).
    """
    return check_tool_exists(tool_name)


# ── CROSS-MODEL ATTESTATION (Phase 1, 2026-06-21) ──────────────────────


async def arif_cross_attest(
    claim_call_hash: str = "",
    claim_trace_id: str = "",
    claim_session_id: str = "",
    claim_tool_name: str = "",
    claim_timestamp: str = "",
    claim_result_summary: str = "",
    mode: str = "verify_call_hash",
) -> dict[str, Any]:
    """CROSS-MODEL ATTESTATION: verify one model's tool call claim against
    the kernel's record of truth.

    This is the kernel's cross-model shadow-detection endpoint. Any model
    (ChatGPT, Claude, DeepSeek, etc.) that claims to have called an arifOS
    tool can be check by another model by submitting the claim's call_hash,
    trace_id, session_id, or tool_name.

    Modes:
      verify_call_hash   — Re-compute call_hash from claim parameters and
                           compare against the submitted claim_call_hash.
                           If they match, the claim is internally consistent.
                           If not, the model is shadowing (narrating a tool
                           call it did not actually make).

      verify_trace_id    — Check that the claim_trace_id exists in the
                           session trace_packet in memory. Returns whether
                           the session ever conducted a tool call under that
                           trace_id.

      verify_session     — Check that claim_session_id is a valid active
                           session in the kernel. Returns session metadata
                           (age, tool count, epoch status).

      tool_in_surface    — Check claim_tool_name exists in the canonical
                           surface. Returns exists/registered/schema_hash.
                           This is a re-export of check_tool_exists() for
                           the cross-attest workflow.

    Authority: OBSERVE_ONLY. No mutation, no vault writes.
    Cross-model attestation is always reversible.
    """
    result: dict[str, Any] = {
        "mode": mode,
        "claim_received": {
            "call_hash": claim_call_hash[:24] + "..."
            if len(claim_call_hash) > 24
            else claim_call_hash,
            "trace_id": claim_trace_id,
            "session_id": claim_session_id,
            "tool_name": claim_tool_name,
            "timestamp": claim_timestamp,
        },
    }

    if mode == "verify_call_hash":
        # Re-compute hash from claim parameters if available
        expected_hash = ""
        if claim_tool_name and claim_timestamp:
            from arifosmcp.runtime.tools import _compute_call_hash

            expected_hash = _compute_call_hash(
                claim_tool_name,
                {"result_summary": claim_result_summary} if claim_result_summary else {},
                claim_timestamp,
                session_id=claim_session_id or None,
            )
        match = claim_call_hash == expected_hash if expected_hash else False
        if not claim_call_hash:
            result["verdict"] = "UNKNOWN"
            result["detail"] = "No claim_call_hash provided. Cannot verify."
            result["advice"] = "Ask the claiming model for the call_hash from the arifOS response."
        elif not expected_hash:
            result["verdict"] = "INCONCLUSIVE"
            result["detail"] = "claim_tool_name + claim_timestamp required to re-compute hash."
        elif match:
            result["verdict"] = "SEAL"
            result["detail"] = (
                "Claim hash matches re-computed hash. Claim is internally consistent."
            )
            result["confidence"] = "HIGH"
        else:
            result["verdict"] = "HOLD"
            result["detail"] = (
                f"Claim hash ({claim_call_hash[:24]}...) does NOT match "
                f"re-computed hash ({expected_hash[:24]}...). "
                "The model is likely shadowing — narrating a tool call it did not make."
            )
            result["confidence"] = "HIGH"

    elif mode == "verify_trace_id":
        if not claim_trace_id:
            result["verdict"] = "UNKNOWN"
            result["detail"] = "No trace_id provided."
        else:
            # Check all active sessions for matching trace_id
            from arifosmcp.runtime.tools import _SESSIONS

            found = False
            session_ref = ""
            for sid, sess in (
                getattr(_SESSIONS, "_data", {}) if hasattr(_SESSIONS, "_data") else {}
            ).items():
                trace_packet = sess.get("trace_packet", {})
                if trace_packet.get("trace_id") == claim_trace_id:
                    found = True
                    session_ref = sid
                    break
            # Fallback: iterate as regular dict
            if not found:
                for sid, sess in dict(_SESSIONS).items():
                    trace_packet = sess.get("trace_packet", {})
                    if trace_packet.get("trace_id") == claim_trace_id:
                        found = True
                        session_ref = sid
                        break
            if found:
                result["verdict"] = "SEAL"
                result["detail"] = f"trace_id verified in session {session_ref[:24]}..."
                result["session_found"] = True
            else:
                result["verdict"] = "DEGRADED"
                result["detail"] = "trace_id not found in any active session."
                result["session_found"] = False
                result["advice"] = (
                    "The session may have expired or the trace_id was fabricated. "
                    "Ask the claiming model for the session_id to cross-verify."
                )

    elif mode == "verify_session":
        if not claim_session_id:
            result["verdict"] = "UNKNOWN"
            result["detail"] = "No session_id provided."
        else:
            from arifosmcp.runtime.tools import _SESSIONS

            sess = dict(_SESSIONS).get(claim_session_id)
            if sess:
                import time

                now = time.time()
                created = sess.get("created_at_unix", 0)
                age_secs = now - created
                result["verdict"] = "SEAL"
                result["session_active"] = True
                result["session_age_seconds"] = round(age_secs, 1)
                result["actor_id"] = sess.get("actor_id")
                result["trace_id"] = sess.get("trace_packet", {}).get("trace_id")
                result["stage"] = sess.get("stage")
                result["epoch_id"] = sess.get("epoch_id")
                result["expired"] = age_secs > 3600  # default TTL
                # ── EPISTEMIC STRAIN GAUGE ─────────────────
                result["invocation_count"] = sess.get("invocation_count", 0)
                result["invocation_tools"] = sess.get("invocation_tools", [])
            else:
                result["verdict"] = "VOID"
                result["session_active"] = False
                result["detail"] = "Session not found in kernel memory."

    elif mode == "tool_in_surface":
        if not claim_tool_name:
            result["verdict"] = "UNKNOWN"
            result["detail"] = "No tool_name provided."
        else:
            check = check_tool_exists(claim_tool_name)
            result["verdict"] = "SEAL" if check.get("exists") else "VOID"
            result["exists"] = check.get("exists")
            result["registered"] = check.get("registered")
            result["accessible"] = check.get("accessible")
            result["closest_match"] = check.get("closest_match")
            result["schema_hash"] = check.get("schema_hash")
            result["canonical_count"] = check.get("canonical_count")

    else:
        result["verdict"] = "VOID"
        result["detail"] = f"Unknown mode: {mode}"
        result["supported_modes"] = [
            "verify_call_hash",
            "verify_trace_id",
            "verify_session",
            "tool_in_surface",
        ]

    return result


__all__ = [
    "mcp_drift_check",
    "arif_mcp_drift_check",
    "arif_tool_exists",
    "arif_cross_attest",
    "compute_surface_hash",
    "compute_tool_schema_hash",
    "check_tool_exists",
]
