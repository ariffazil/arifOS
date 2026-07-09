"""
arifosmcp/tools/kernel_canonical.py — 444_KERNEL_CANONICAL
═══════════════════════════════════════════════════════════

RULE 14 MODE-FIRST NAMING canonical tools.
Replaces the 16-mode bloat in arif_kernel_route with 5 clean named tools.

Each tool has ONE responsibility. Modes are internal expansion, not naming.

Canonical tools (stable names):
  arif_route        — route intent to organ (new canonical routing entry point)
  arif_triage       — session status, priority, preflight
  arif_kernel_status — telemetry, discovery, prediction health
  arif_bridge_connect — direct organ tool call (canonical noun_verb name, forged 2026-06-21)
  arif_bridge       — [DEPRECATED] legacy noun-only name, retained for backward compat

Soft-deprecated (still work, emit warning):
  arif_kernel_route — absorbs all old modes via passthrough

Ratified: 2026-06-20
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
from pathlib import Path
from typing import Any

from arifosmcp.core.federation_contracts import validate_organ_output
from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _hold, _ok

logger = logging.getLogger(__name__)

try:
    from arifosmcp.core.tool_self_model import SURPRISE_WINDOW_SIZE
except ImportError:
    SURPRISE_WINDOW_SIZE = 10

_BRIDGE_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# ─── Intent map cache ────────────────────────────────────────────────────────
_intent_map_cache: dict[str, Any] | None = None


def _load_intent_map() -> dict[str, Any]:
    """Load organ intent map once, cache forever."""
    global _intent_map_cache
    if _intent_map_cache is not None:
        return _intent_map_cache
    try:
        import yaml

        map_path = Path(__file__).parent.parent / "config" / "organ_intent_map.yaml"
        if map_path.exists():
            with open(map_path) as f:
                _intent_map_cache = yaml.safe_load(f)
                return _intent_map_cache
    except Exception:
        pass
    # Fallback: hardcoded map — G13 FIX (2026-06-30): machine domain + AAA added
    _intent_map_cache = {
        "organ_routes": {
            "arifos": {
                "organ": "arifOS",
                "port": 8088,
                "intent_keywords": [
                    # Machine / MCP surface
                    "MCP",
                    "MCP server",
                    "MCP tool",
                    "MCP endpoint",
                    "MCP connector",
                    "MCP diagnostic",
                    "MCP conformance",
                    "MCP surface",
                    "ChatGPT connector",
                    "OpenAI connector",
                    "Copilot connector",
                    "surface drift",
                    "connector schema",
                    "connector cache",
                    "protocol version",
                    "protocol drift",
                    "protocol conformance",
                    "tool registry",
                    "tool schema",
                    "tool conformance",
                    "tool surface",
                    "tool manifest",
                    "tools/list",
                    "tools/call",
                    "capability surface",
                    "capability lease",
                    # Governance / constitutional
                    "kernel health",
                    "kernel status",
                    "kernel route",
                    "kernel attest",
                    "arifos kernel",
                    "arifos health",
                    "arifos status",
                    "constitutional floor",
                    "constitutional check",
                    "governance check",
                    "governance status",
                    "seal boundary",
                    "seal verdict",
                    "authority envelope",
                    "epistemic tag",
                    "cognitive axis",
                    # Session / memory / vault
                    "initialize session",
                    "session init",
                    "session anchor",
                    "memory recall",
                    "memory search",
                    "vault seal",
                    "vault ledger",
                    "lease request",
                    "belief state",
                    "runtime schema",
                    # Canonical tool names
                    "arif init",
                    "arif route",
                    "arif triage",
                    "arif judge",
                    "arif seal",
                    "arif measure",
                    "arif observe",
                    "arif think",
                    "arif critique",
                    "arif bridge",
                    "arif gateway",
                    "arif forge",
                    "arif_forge",
                    "arif memory",
                    "arif_memory",
                    "arif session",
                    "arif vault",
                    # Federation
                    "federation contract",
                    "federation manifest",
                    "organ attestation",
                    "organ health",
                    "agentic search",
                    "agent registry",
                    # Sovereign / personal decisions
                    "life roadmap",
                    "career decision",
                    "personal decision",
                    "what should i do",
                    "life direction",
                    "should i leave",
                    "should i stay",
                    "human sovereign",
                    "sovereign decision",
                    "life choice",
                    "exit strategy",
                    "what do i want",
                    "my future",
                ],
            },
            "aaa": {
                "organ": "AAA",
                "port": 3001,
                "intent_keywords": [
                    "cockpit",
                    "dashboard",
                    "control plane",
                    "AAA cockpit",
                    "AAA dashboard",
                    "agent identity",
                    "agent registry cockpit",
                    "permission list",
                    "access control",
                    "audit log",
                    "federation health",
                    "approval queue",
                    "A2A gateway",
                    "identity anchor",
                    "throttle",
                ],
            },
            "a_forge": {
                "organ": "A-FORGE",
                "port": 7071,
                "intent_keywords": [
                    "build",
                    "deploy",
                    "forge",
                    "compile",
                    "commit",
                    "push",
                    "git",
                    "docker",
                    "container",
                    "image",
                    "pipeline",
                    "ci/cd",
                    "jenkins",
                    "github",
                    "repository",
                    "version",
                    "dry run",
                    "dry-run",
                    "execute plan",
                    "node install",
                    "npm install",
                    "npm build",
                    "npm test",
                    "uv sync",
                    "docker compose",
                    "systemctl restart",
                    "systemd unit",
                    "service restart",
                    "make deploy",
                    "code deploy",
                    "rollback",
                    "mutate file",
                    "forge execute",
                    "forge plan",
                    "forge dryrun",
                ],
            },
            "geox": {
                "organ": "GEOX",
                "port": 8081,
                "intent_keywords": [
                    "seismic",
                    "well log",
                    "las",
                    "petrophysics",
                    "horizon",
                    "fault",
                    "amplitude",
                    "basin",
                    "prospect",
                    "subsurface",
                    "velocity",
                    "lithology",
                    "porosity",
                    "permeability",
                    "resistivity",
                    "gamma ray",
                    "sonic",
                    "density",
                    "structural",
                    "trap",
                    # SERP API: academic/local domain (2026-07-07)
                    "scholar",
                    "academic paper",
                    "research paper",
                    "citation",
                    "patent",
                    "patent search",
                    "geology consultant",
                    "local business",
                    "geological survey",
                ],
            },
            "wealth": {
                "organ": "WEALTH",
                "port": 18082,
                "intent_keywords": [
                    "portfolio",
                    "npv",
                    "irr",
                    "emv",
                    "option",
                    "derivative",
                    "capital",
                    "hedge",
                    "risk metric",
                    "allocation",
                    "stress test",
                    # SERP API: finance/commerce/trends domain (2026-07-07)
                    "stock price",
                    "stock quote",
                    "market data",
                    "market overview",
                    "crypto price",
                    "forex rate",
                    "exchange rate",
                    "commodity price",
                    "bond yield",
                    "finance search",
                    "product price",
                    "shopping",
                    "price comparison",
                    "market trends",
                    "search trends",
                    "trending topics",
                    "fiscal data",
                    "gdp",
                    "inflation",
                ],
            },
            "well": {
                "organ": "WELL",
                "port": 18083,
                "intent_keywords": [
                    # G13 FIX: human-vitality-only keywords
                    "human health",
                    "personal health",
                    "wellness",
                    "vitality",
                    "biometric",
                    "sleep",
                    "heart rate",
                    "hrv",
                    "metabolic",
                    "readiness",
                    "recovery",
                    "autonomic",
                    "wellbeing",
                    "maruah",
                    "fatigue",
                    "cognition load",
                    # SERP API: travel domain (2026-07-07)
                    "flight search",
                    "hotel search",
                    "travel planning",
                    "flight deal",
                    "hotel review",
                    "travel destination",
                    "rest planning",
                    "vacation",
                ],
            },
        }
    }
    return _intent_map_cache


def _route_intent_to_organ(intent: str, explicit_organ: str | None = None) -> str:
    """Resolve organ by keyword matching against intent map."""
    if explicit_organ:
        return explicit_organ.lower()
    if not intent:
        return "arifOS"
    intent_lower = intent.lower()

    # ── Hard kernel guard (2026-06-30): MCP/kernel/diagnostic queries MUST route ─
    # to arifOS. These are kernel-level concerns, never domain-organ concerns.
    # The keyword map below handles normal cases; this guard catches edge cases
    # where a domain organ (e.g. WELL "health") would otherwise win.
    #
    # G14 FIX (2026-07-04): The original guard was over-greedy — it caught
    # "organ health" and "organ attestation" even when the intent was an
    # organ-qualified query like "WELL organ health" or "GEOX organ health",
    # which should route to the named organ, not to arifOS. Fix: detect an
    # organ-qualified phrase first (e.g. "WELL organ X", "GEOX earth Y")
    # and route to that organ BEFORE the kernel guard fires.
    _ORGAN_NAMES = ("WELL", "GEOX", "WEALTH", "AAA", "A-FORGE", "AFORGE", "ARIFOS")

    # Step 1: organ-qualified phrases win. If intent starts with an organ
    # name OR contains "<organ> organ" / "<organ> health", route to it.
    for organ_name in _ORGAN_NAMES:
        # "WELL organ health" → WELL; "GEOX earth evidence" → GEOX; etc.
        organ_lower = organ_name.lower().replace("-", " ").replace("a forge", "a_forge")
        if (
            intent_lower.startswith(organ_lower + " ")
            or f" {organ_lower} " in intent_lower
            or f" {organ_lower} organ " in intent_lower
            or f" {organ_lower} health" in intent_lower
        ):
            return organ_lower.replace(" ", "_").replace("a_forge", "a-forge")

    # Step 2: kernel guard for kernel-level concerns (MCP / constitutional / governance)
    _KERNEL_GUARD_PATTERNS: list[str] = [
        "mcp ",
        "mcp server",
        "mcp tool",
        "mcp endpoint",
        "mcp connector",
        "mcp surface",
        "mcp diagnostic",
        "mcp conformance",
        "mcp protocol",
        "chatgpt connector",
        "openai connector",
        "copilot connector",
        "tool registry",
        "tool schema",
        "tool conformance",
        "tool list",
        "tools/list",
        "tools/call",
        "tool surface",
        "tool manifest",
        "surface drift",
        "connector schema",
        "connector cache",
        "protocol version",
        "protocol drift",
        "protocol conformance",
        "capability surface",
        "capability lease",
        "kernel health",
        "kernel status",
        "kernel route",
        "kernel attest",
        "arifos kernel",
        "arifos health",
        "arifos status",
        "arifos mcp",
        "constitutional floor",
        "constitutional check",
        "governance check",
        "governance status",
        "seal boundary",
        "seal verdict",
        "authority envelope",
        "federation contract",
        "federation manifest",
        # G14 FIX: removed "organ attestation" and "organ health" from the
        # kernel guard. Organ-qualified phrases are caught in Step 1 above.
        # Unqualified "organ attestation" still routes to arifOS via the
        # YAML keyword map (arifos.intent_keywords: "organ attestation").
        "arifos organ attestation",
        "arifos organ health",
    ]
    for pattern in _KERNEL_GUARD_PATTERNS:
        if pattern in intent_lower:
            return "arifOS"

    # Step 3: YAML intent map — longest keyword match wins
    intent_map = _load_intent_map()
    organ_routes = intent_map.get("organ_routes", {})
    best_match = None
    best_len = 0
    for organ_key, organ_config in organ_routes.items():
        for kw in organ_config.get("intent_keywords", []):
            if kw.lower() in intent_lower and len(kw) > best_len:
                best_len = len(kw)
                best_match = organ_config.get("organ", organ_key.upper())
    return best_match or "arifOS"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 1: arif_route
# ═══════════════════════════════════════════════════════════════════════════════


def _bind_identity(
    actor_id: str | None, session_id: str | None
) -> tuple[str | None, str | None]:
    """Recover actor/session from session store when MCP drops or nulls identity.

    Explicit non-anon actor_id always wins. Session-bound actor fills gaps.
    Prevents wrap_legacy_call / outer envelope coercing to openclaw-anon when
    the caller already passed a verified session.
    """
    _ANON = frozenset({None, "", "anonymous", "openclaw-anon", "unknown", "null"})
    aid = actor_id if actor_id not in _ANON else None
    sid = session_id if session_id not in _ANON else None
    if sid:
        try:
            from arifosmcp.runtime.tools import _SESSIONS

            sess = _SESSIONS.get(sid) or {}
            if not aid:
                cand = sess.get("actor_id") or sess.get("canonical_actor_id")
                if cand and cand not in _ANON:
                    aid = str(cand)
        except Exception:
            pass
    return aid, sid


def arif_route(
    intent: str,
    organ: str | None = None,
    task: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    organ_tool: str | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Canonical routing entry point. Routes an intent to the correct organ.

    RULE 14: Mode-first. This is ONE tool for all routing decisions.
    The mode parameter does not exist here — routing is the only operation.

    Args:
        intent:        Natural-language description of what the user wants.
                      e.g. "interpret this seismic section", "assess portfolio risk"
        organ:        Optional explicit organ override. If provided, intent matching
                      is skipped and this organ is used directly.
        task:         Alias for intent (backward compat).
        actor_id:     Calling actor.
        session_id:   Governing session.
        organ_tool:   The tool name on the target organ to call.
                      If absent, returns routing decision only (no bridge call).
        arguments:    Arguments to pass to organ_tool.

    Returns:
        routing_decision:  organ, port, tool_prefix
        bridge_result:    (if organ_tool provided) result from organ tool call

    Example:
        arif_route(intent="seismic interpretation")
        → {"organ": "GEOX", "port": 8081, "tool_prefix": "geox_", "status": "routed"}

        arif_route(intent="portfolio stress test", organ_tool="wealth_portfolio",
                   arguments={"mode": "stress"})
        → routes to WEALTH, calls wealth_portfolio(mode="stress"), returns result
    """
    actor_id, session_id = _bind_identity(actor_id, session_id)
    # Prefer identity inside arguments._envelope if tool args lost top-level fields
    if arguments and isinstance(arguments, dict):
        env = arguments.get("_envelope") or {}
        if isinstance(env, dict):
            if not actor_id and env.get("actor_id"):
                actor_id = env.get("actor_id")
            if not session_id and env.get("session_id"):
                session_id = env.get("session_id")
            actor_id, session_id = _bind_identity(actor_id, session_id)

    floor_check = check_laws("arif_route", {"intent": intent}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold(
            "arif_route",
            floor_check["reason"],
            floor_check["violated_laws"],
            session_id=session_id,
        )

    # Kernel dispatch gate: if _envelope provided (cross-organ), session must match live issued one
    # (This is before organ runs — wall, not policy)
    if arguments and "_envelope" in (arguments or {}):
        env = arguments.get("_envelope") or {}
        if session_id and env.get("session_id") and env.get("session_id") != session_id:
            return _hold("arif_route", "Kernel reject: _envelope.session_id does not match live session issued by kernel")

    target_organ = _route_intent_to_organ(intent, organ)
    intent_map = _load_intent_map()
    # G15 FIX (2026-07-04): normalize organ lookup key so "A-FORGE" → "a_forge"
    # matches the YAML key. Previously hyphens caused A-FORGE route to miss config
    # and return port=0 / tool_prefix="".
    lookup_key = target_organ.lower().replace("-", "_")
    organ_config = intent_map.get("organ_routes", {}).get(lookup_key, {})

    # Fix 2026-07-06 ROUND-2: Organ registry allowlist — reject unknown organs.
    # Previously, any string as organ would get routed with port=0, tool_prefix="",
    # routing_confidence=0.95. Now: if organ_config is empty AND the organ was
    # explicitly provided (not inferred from intent), reject with HOLD.
    if not organ_config and organ:
        return _hold(
            "arif_route",
            f"UNKNOWN_ORGAN: '{organ}' is not a registered federation organ. "
            f"Known organs: {sorted(intent_map.get('organ_routes', {}).keys())}. "
            f"Cannot route to unregistered organ (F8 GENIUS: simplest correct path).",
            ["L08"],
        )
    # If organ was inferred from intent and still no config, default to arifOS
    if not organ_config:
        organ_config = intent_map.get("organ_routes", {}).get("arifos", {})
        target_organ = "arifos"

    port = organ_config.get("port", 0)
    tool_prefix = organ_config.get("tool_prefix", "")

    routing = {
        "intent": intent,
        "organ": target_organ.upper(),
        "port": port,
        "tool_prefix": tool_prefix,
        "organ_tool": organ_tool,
        "status": "routed",
        "routing_rule": "intent_map",
        # TIME INVARIANT: source_of_truth chain — tracks provenance of this
        # routing decision. When bridged to an organ, the organ receives this
        # chain so it knows where the request originated and with what context.
        "source_of_truth": {
            "origin": "arif_route",
            "actor_id": actor_id,
            "session_id": session_id,
            "timestamp": __import__("time").time(),
            "routing_confidence": 0.95 if organ else 0.85,
            "chain": [
                {"step": "intent_received", "timestamp": __import__("time").time()},
                {
                    "step": "organ_resolved",
                    "organ": target_organ.upper(),
                    "timestamp": __import__("time").time(),
                },
            ],
        },
    }

    # P2 FIX 2026-06-30: Verdict monotonicity — HOLD > DEGRADED > SEAL.
    # ChatGPT audit caught: arif_route returned verdict: SEAL while inner signals
    # said hold_required: true + floor_passed: false. That is a contradiction.
    # Rule: if any critical subsignal fires HOLD, outer verdict CANNOT be SEAL.
    def _routing_hold_required(r: dict) -> bool:
        """Check if any inner subsignal requires HOLD."""
        if r.get("hold_required") is True:
            return True
        if r.get("floor_passed") is False:
            return True
        nine = r.get("nine_signal") or {}
        if isinstance(nine, dict):
            overall = nine.get("overall") or {}
            if isinstance(overall, dict) and overall.get("state") in ("SYUBHAH", "HOLD", "VOID"):
                return True
        return False

    def _route_ok(payload: dict[str, Any]) -> dict[str, Any]:
        payload = {
            **payload,
            "actor_id": actor_id,
            "session_id": session_id,
        }
        return _ok(
            "arif_route",
            payload,
            meta={"actor_id": actor_id},
            session_id=session_id,
        )

    def _route_hold(reason: str, extra: dict | None = None) -> dict[str, Any]:
        return _hold(
            "arif_route",
            reason,
            extra_meta={**(extra or {}), "actor_id": actor_id, "session_id": session_id},
            session_id=session_id,
        )

    # If no organ_tool specified, return routing decision only
    if not organ_tool:
        if _routing_hold_required(routing):
            return _route_hold(
                "Routing HOLD: inner subsignal requires hold (floor_passed=false or hold_required=true)",
                {"routing": routing},
            )
        return _route_ok(routing)

    # Build transport _envelope from live session state (ALWAYS populated, never re-typed by caller)
    _envelope = {
        "session_id": session_id,
        "constitutional_chain_id": session_id or "cc-none",
        "actor_id": actor_id,
        "trace_id": f"trace_{int(__import__('time').time() * 1000)}_{actor_id or 'anon'}",
    }
    call_args = dict(arguments or {})
    # Force envelope identity — do not let stale null envelope win
    prev_env = call_args.get("_envelope") if isinstance(call_args.get("_envelope"), dict) else {}
    call_args["_envelope"] = {**prev_env, **{k: v for k, v in _envelope.items() if v is not None}}

    # Bridge call to organ
    if target_organ.lower() == "geox":
        result = _bridge_geox(organ_tool, call_args, session_id, actor_id)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        if _routing_hold_required(routing):
            return _route_hold("Bridge HOLD: inner subsignal requires hold", {"routing": routing})
        return _route_ok(routing)

    if target_organ.lower() == "wealth":
        result = _bridge_wealth(organ_tool, call_args, session_id, actor_id)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        if _routing_hold_required(routing):
            return _route_hold("Bridge HOLD: inner subsignal requires hold", {"routing": routing})
        return _route_ok(routing)

    if target_organ.lower() == "well":
        result = _bridge_well(organ_tool, call_args, session_id, actor_id)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        if _routing_hold_required(routing):
            return _route_hold("Bridge HOLD: inner subsignal requires hold", {"routing": routing})
        return _route_ok(routing)

    if target_organ.lower() == "a-forge":
        return _route_ok({**routing, "bridge_status": "a-forge: use A-FORGE MCP directly"})

    if target_organ.lower() == "aaa":
        return _route_ok(
            {**routing, "bridge_status": "aaa: cockpit/identity — use AAA:3001"}
        )

    if target_organ.lower() == "arifos":
        return _route_ok({**routing, "bridge_status": "kernel-local: no bridge needed"})

    return _route_hold(f"Unknown organ: {target_organ}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 2: arif_triage
# ═══════════════════════════════════════════════════════════════════════════════


def arif_triage(
    mode: str = "status",
    session_id: str | None = None,
    stage: str | None = None,
    actor_id: str | None = None,
    priority: str | None = None,
    _envelope: Any = None,
) -> dict[str, Any]:
    """
    Session status, priority queue, and preflight checks.

    RULE 14: One tool, defined modes.
    Modes:
        status     — active session count and current stage
        preflight  — pre-session safety probe (no session required)
        triage     — priority assessment for a task

    Args:
        mode:        "status" | "preflight" | "triage"
        session_id:   Optional session to query
        stage:       Stage hint (used if session_id not provided)
        actor_id:    Calling actor
        priority:    Task priority hint for triage mode

    Returns:
        Structured triage data appropriate to mode.
    """
    floor_check = check_laws("arif_triage", {"mode": mode}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_triage", floor_check["reason"], floor_check["violated_laws"])

    from arifosmcp.runtime.tools import _SESSIONS

    if mode == "status":
        prediction_health = _get_prediction_health()
        live_stage = "unknown"
        stage_source = "unknown"
        if session_id:
            sess = _SESSIONS.get(session_id, {})
            live_stage = sess.get("stage", stage or "unknown")
            stage_source = "session"
        elif stage:
            live_stage = stage
            stage_source = "parameter"
        else:
            # F5 FIX (2026-07-07): When no session_id provided, find the most
            # recent session's stage instead of returning "unknown". Claude
            # feedback: 63 sessions all showing stage="unknown" is misleading.
            try:
                most_recent = None
                most_recent_ts = 0
                for sid, sess in _SESSIONS.items():
                    if isinstance(sess, dict):
                        ts = (
                            sess.get("expires_at_unix", 0)
                            or sess.get("created_at_unix", 0)
                            or sess.get("issued_at", 0)
                            or sess.get("created_at_ts", 0)
                        )
                        if isinstance(ts, (int, float)) and ts > most_recent_ts:
                            most_recent_ts = ts
                            most_recent = sess
                if most_recent and most_recent.get("stage"):
                    live_stage = most_recent["stage"]
                    stage_source = "most_recent_session"
            except Exception:
                pass
        return _ok(
            "arif_triage",
            {
                "active_sessions": len(_SESSIONS),
                "stage": live_stage,
                "stage_source": stage_source,
                "prediction_health": prediction_health,
                "mode": "status",
            },
        )

    if mode == "preflight":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        session_id_present = bool(session_id)
        actor_id_present = bool(actor_id)
        preflight_payload: dict[str, Any] = {
            "kernel": "alive",
            "observe_only": True,
            "mutation_allowed": False,
            "external_side_effects_allowed": False,
            "irreversible_allowed": False,
            "session_required": True,
            "session_id_present": session_id_present,
            "actor_id_present": actor_id_present,
            "actor_verified": False,
            "authority_mode": "OBSERVE_ONLY",
            "stage": stage or "000",
            "canonical_tool_count": len(CANONICAL_TOOLS),
            "active_sessions": len(_SESSIONS),
            "next_safe_action": "Call arif_init(mode='ping' | 'light' | 'full')",
            "mode": "preflight",
        }
        # Verdict gate normalization (PATCH 1, 2026-07-03):
        # If session is required but missing, the constitutional verdict
        # CANNOT be SEAL — must be HOLD with SESSION_REQUIRED.
        if not session_id_present:
            return _hold(
                "arif_triage",
                reason="SESSION_REQUIRED",
                floors=["F11"],
                extra_meta={
                    "hold_reason": "SESSION_REQUIRED",
                    "required_precondition_failed": "session_id",
                    "next_safe_action": "arif_init",
                    "preflight_diagnostics": preflight_payload,
                },
            )
        return _ok("arif_triage", preflight_payload)

    if mode == "triage":
        # Simple priority classification
        priority_map = {
            "critical": 1,
            "high": 2,
            "normal": 3,
            "low": 4,
        }
        q_priority = priority_map.get(priority.lower() if priority else "normal", 3)
        return _ok(
            "arif_triage",
            {
                "priority": priority or "normal",
                "priority_score": q_priority,
                "queue_depth": 0,
                "recommended_lane": "AGI" if q_priority <= 2 else "AGI",
                "mode": "triage",
            },
        )

    return _hold("arif_triage", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 3: arif_bridge_connect (low-level organ call)
# ═══════════════════════════════════════════════════════════════════════════════
# arif_bridge_connect (CANONICAL, forged 2026-06-21): follows arif_<noun>_<verb> convention.


def arif_bridge_connect(
    organ: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Low-level direct organ tool call.
    Bypasses intent map — caller must know which organ and tool to call.

    RULE 14: This is a direct bridge, not routing by intent.
    Use arif_route for intent-based routing. Use arif_bridge only when
    the organ and tool are known ahead of time.

    This is the internal bridge implementation also used by arif_route.

    Args:
        organ:       "geox" | "wealth" | "well" | "geox" (case-insensitive)
        tool_name:   MCP tool name on the target organ
        arguments:   Tool arguments dict
        actor_id:    Calling actor (injected into envelope)
        session_id:  Governing session

    Returns:
        Kernel-wrapped organ output with envelope.
    """
    actor_id, session_id = _bind_identity(actor_id, session_id)
    floor_check = check_laws("arif_bridge", {"organ": organ, "tool": tool_name}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold(
            "arif_bridge",
            floor_check["reason"],
            floor_check["violated_laws"],
            session_id=session_id,
        )

    # IDENTITY PROPAGATION: always inject _envelope; merge, never drop identity.
    _args = dict(arguments or {})
    _env = {
        "session_id": session_id,
        "actor_id": actor_id,
        "source_organ": "arifOS",
    }
    prev = _args.get("_envelope") if isinstance(_args.get("_envelope"), dict) else {}
    _args["_envelope"] = {**prev, **{k: v for k, v in _env.items() if v is not None}}

    organ_lower = organ.lower()
    if organ_lower == "geox":
        return _bridge_geox(tool_name, _args, session_id, actor_id)
    if organ_lower == "wealth":
        return _bridge_wealth(tool_name, _args, session_id, actor_id)
    if organ_lower == "well":
        return _bridge_well(tool_name, _args, session_id, actor_id)
    return _hold("arif_bridge", f"Unknown organ: {organ}", session_id=session_id)


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 5: arif_kernel_attest (organ attestation)
# ═══════════════════════════════════════════════════════════════════════════════


def arif_kernel_attest(
    organ: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Live organ attestation. One tool, organ is a parameter.

    RULE 14: One tool, organ is a parameter, not a name.
    If organ is None, attest all organs.

    Args:
        organ:      Specific organ to attest, or None for all
        actor_id:   Calling actor
        session_id: Governing session

    Returns:
        Per-organ attestation records with liveness.
    """
    floor_check = check_laws("arif_kernel_attest", {"organ": organ or "all"}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_attest", floor_check["reason"], floor_check["violated_laws"])

    import asyncio

    from arifosmcp.runtime.heartbeat_registry import federation_liveness
    from arifosmcp.runtime.organ_attestation import attest_all_organs, attest_organ

    if organ and organ.upper() in ("GEOX", "WEALTH", "WELL", "arifOS"):
        result = asyncio.run(attest_organ(organ.upper(), actor_id=actor_id, session_id=session_id))
        return _ok("arif_kernel_attest", {"mode": "single", "organ": organ.upper(), **result})

    result = asyncio.run(attest_all_organs(actor_id=actor_id, session_id=session_id))
    liveness = federation_liveness()
    return _ok(
        "arif_kernel_attest",
        {
            "mode": "all",
            "attestation": result,
            "liveness": liveness,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 6: arif_kernel_health (federation health)
# ═══════════════════════════════════════════════════════════════════════════════


def arif_kernel_health(
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Federation liveness heartbeat snapshot.
    One tool, no modes needed — health is singular.

    Args:
        actor_id: Calling actor

    Returns:
        Federation-wide liveness data.
    """
    floor_check = check_laws("arif_kernel_health", {}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_health", floor_check["reason"], floor_check["violated_laws"])

    from arifosmcp.runtime.heartbeat_registry import federation_liveness

    liveness = federation_liveness()
    return _ok("arif_kernel_health", {"liveness": liveness})


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _run_async(coro) -> Any:
    """Run async coroutine from sync context."""
    try:
        asyncio.get_running_loop()
        future = _BRIDGE_EXECUTOR.submit(asyncio.run, coro)
        return future.result(timeout=60)
    except RuntimeError:
        return asyncio.run(coro)


def _assert_organ_attested(organ: str) -> dict[str, Any] | None:
    """Fail-closed gate: require recent ALIVE attestation before bridging.

    Lazy re-attest once if registry is empty/stale after kernel restart
    (in-memory attestation evaporates on process recycle while organs stay live).
    """
    from arifosmcp.runtime.heartbeat_registry import is_organ_stale
    from arifosmcp.runtime.organ_attestation import (
        attest_organ,
        get_organ_attestation,
        is_healthy,
    )

    oid = organ.upper()
    rec = get_organ_attestation(oid)

    def _needs_refresh(r) -> bool:
        if r is None:
            return True
        if r.status in ("REVOKED", "DEGRADED_CLAIM", "DEGRADED", "UNATTESTED"):
            return True
        try:
            if is_organ_stale(oid):
                return True
        except Exception:
            return True
        return False

    if _needs_refresh(rec):
        try:
            result = _run_async(attest_organ(oid))
            # attest_organ returns dict; re-read registry
            rec = get_organ_attestation(oid)
            if rec is None and isinstance(result, dict):
                # Some paths return inline status without registry write
                st = (result.get("status") or result.get("attestation", {}).get("status") or "")
                if not is_healthy(st) and st not in ("ALIVE", "alive"):
                    return _hold(
                        "arif_bridge",
                        f"Organ {organ} re-attest failed: {result.get('status') or result}",
                    )
        except Exception as exc:
            return _hold(
                "arif_bridge",
                f"Organ {organ} has no live attestation and re-attest failed: {exc}",
            )

    rec = get_organ_attestation(oid)
    if rec is None:
        return _hold("arif_bridge", f"Organ {organ} has no live attestation.")
    if rec.status in ("REVOKED", "DEGRADED_CLAIM", "DEGRADED", "UNATTESTED"):
        return _hold("arif_bridge", f"Organ {organ} status={rec.status}")
    if rec.status not in ("ALIVE", "DEGRADED_NOT_FAILED", "CONSTITUTIONAL_HOLD"):
        # Allow ALIVE family only
        if rec.status != "ALIVE":
            try:
                if is_organ_stale(oid):
                    return _hold("arif_bridge", f"Organ {organ} heartbeat stale. Re-attest.")
            except Exception:
                pass
    return None


def _bridge_geox(
    tool_name: str, arguments: dict, session_id: str | None, actor_id: str | None
) -> dict[str, Any]:
    """Bridge a call to GEOX organ. Populates and expects echo of _envelope."""
    hold = _assert_organ_attested("geox")
    if hold:
        return hold
    _envelope = arguments.get("_envelope")
    try:
        from arifosmcp.federation.kernel_envelope import wrap_geox_output
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.geox_bridge import call_geox_tool

        result = _run_async(call_geox_tool(tool_name, arguments))
        validated = validate_organ_output("geox", result)
        wrapped = wrap_geox_output(
            validated["output"],
            tool_name=tool_name,
            session_id=session_id,
            actor_id=actor_id,
            lease_id=arguments.get("lease_id"),
        )
        # Echo _envelope unchanged for integrity check (free drift detector)
        if isinstance(wrapped, dict) and _envelope:
            wrapped.setdefault("_envelope", _envelope)
        elif isinstance(result, dict) and _envelope:
            result.setdefault("_envelope", _envelope)

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        # Check if the bridged result claims executive authority but is AI-generated.
        # AI may recommend action, not self-approve action.
        _source_epi = read_epistemic(wrapped) if isinstance(wrapped, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: GEOX bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        # Kernel-side: if echoed _envelope.session_id does not match sent, flag (drift detector)
        echoed = (wrapped or result) if isinstance(wrapped or result, dict) else {}
        echoed_env = echoed.get("_envelope") or echoed.get("envelope") or {}
        if _envelope and echoed_env.get("session_id") != _envelope.get("session_id"):
            logger.warning("ENVELOPE DRIFT DETECTED in GEOX response")
            return _hold("arif_bridge", "Envelope session_id mismatch — identity rewrite suspected")

        return _ok(
            "arif_bridge",
            {
                "organ": "GEOX",
                "tool": tool_name,
                "result": wrapped,
                "status": "bridged",
                "boundary_enforced": validated["boundary_enforced"],
                "violations": validated["violations"],
                "_epistemic_checked": True,
                "_envelope_echoed": bool(_envelope),
            },
        )
    except Exception as e:
        return _hold("arif_bridge", f"GEOX bridge failed: {e}")


def _bridge_wealth(
    tool_name: str, arguments: dict, session_id: str | None, actor_id: str | None
) -> dict[str, Any]:
    """Bridge a call to WEALTH organ. Echo _envelope for identity integrity."""
    hold = _assert_organ_attested("wealth")
    if hold:
        return hold
    _envelope = arguments.get("_envelope")
    try:
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.wealth_bridge import call_wealth_tool

        result = _run_async(call_wealth_tool(tool_name, arguments))
        validated = validate_organ_output("wealth", result)

        # Echo unchanged
        out = validated.get("output", result)
        if isinstance(out, dict) and _envelope:
            out.setdefault("_envelope", _envelope)

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = read_epistemic(out) if isinstance(out, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: WEALTH bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        # Kernel check for echo match
        echoed_env = out.get("_envelope") or out.get("envelope") or {} if isinstance(out, dict) else {}
        if _envelope and echoed_env.get("session_id") != _envelope.get("session_id"):
            return _hold(
                "arif_bridge", "Envelope session_id mismatch — identity rewrite suspected (WEALTH)"
            )

        return _ok(
            "arif_bridge",
            {
                "organ": "WEALTH",
                "tool": tool_name,
                "result": out,
                "status": "bridged",
                "boundary_enforced": validated["boundary_enforced"],
                "violations": validated["violations"],
                "_epistemic_checked": True,
                "_envelope_echoed": bool(_envelope),
            },
        )
    except Exception as e:
        return _hold("arif_bridge", f"WEALTH bridge failed: {e}")


def _bridge_well(
    tool_name: str, arguments: dict, session_id: str | None, actor_id: str | None
) -> dict[str, Any]:
    """Bridge a call to WELL organ. Echo _envelope unchanged."""
    hold = _assert_organ_attested("well")
    if hold:
        return hold
    _envelope = arguments.get("_envelope")
    try:
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.well_bridge import call_well_tool

        result = _run_async(call_well_tool(tool_name, arguments))

        # Echo _envelope
        if isinstance(result, dict) and _envelope:
            result.setdefault("_envelope", _envelope)

        # Kernel echo match check
        echoed_env = result.get("_envelope") or result.get("envelope") or {} if isinstance(result, dict) else {}
        if _envelope and echoed_env.get("session_id") != _envelope.get("session_id"):
            return _hold(
                "arif_bridge", "Envelope session_id mismatch — identity rewrite suspected (WELL)"
            )

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = read_epistemic(result) if isinstance(result, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: WELL bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        return _ok(
            "arif_bridge",
            {
                "organ": "WELL",
                "tool": tool_name,
                "result": result,
                "status": "bridged",
                "_epistemic_checked": True,
                "_envelope_echoed": bool(_envelope),
            },
        )
    except Exception as e:
        return _hold("arif_bridge", f"WELL bridge failed: {e}")


def _get_prediction_health() -> dict[str, Any]:
    """Get self-model prediction health summary."""
    try:
        from arifosmcp.core.tool_self_model import get_tool_self_model

        model = get_tool_self_model()
        return model.get_prediction_summary()
    except Exception:
        return {"error": "prediction model not available"}
