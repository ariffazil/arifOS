"""
arifOS Capability Drift — Phase A of Reality Observatory.

Capability drift is a first-class panel: a tool can be DECLARED in the
authoritative registry, REGISTERED in the kernel, EXPOSED in the discovery
manifest, INVOCABLE through the transport, TESTED recently with a passing
round-trip, and SCHEMA-matching between input and output contracts.

Truth = (declared ∧ registered ∧ exposed ∧ invocable ∧ tested
          ∧ input_schema_match ∧ output_schema_match)

Anything less ⇒ DEGRADED.
Missing entirely ⇒ VOID.

This module is F1-safe: additive read-only probes. No side-effects.

Forged 2026-07-14 — companion to /api/observatory/v1/snapshot.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Where the OS-level capability test cache lives.
# Each entry: {tool_name: {"last_invocation_at": epoch_seconds, "last_pass": bool, "last_error": str|null}}
TEST_CACHE_PATH = Path("/var/lib/arifos/observatory/capability-test-cache.json")
TEST_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Canonical namespace per arifOS constitution (FLOOR_PUBLIC_MAP.md, public_surface.py).
PUBLIC_NAMESPACE_PREFIX = "arif_"

# Public constitutional wire (8 tools). Matrix counters must use this set, not full registry.
PUBLIC_CANONICAL_TOOLS: frozenset[str] = frozenset(
    {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    }
)

# Snapshot TTL — observations older than this are marked stale at the snapshot layer.
TEST_FRESHNESS_SECONDS = 300  # 5 min — matches `cadence: capability graph` in plan §telemetry
# Durable SUCCESS within this window counts as proven_live (not necessarily "fresh").
PROVEN_LIVE_SECONDS = 86_400  # 24h


def _canonical_tool_record(
    tool_name: str, registry_index: dict[str, dict[str, Any]]
) -> dict[str, Any] | None:
    """Return the canonical record for `tool_name` from TOOLREGISTRY.json shape, or None."""
    return registry_index.get(tool_name)


def _load_registry_index() -> dict[str, dict[str, Any]]:
    """Load authoritative TOOLREGISTRY.json (substrate SOT) + tool_registry.json (kernel live affordance SOT).

    Returns a flat dict of `{tool_name: {metadata}}` where metadata is taken
    from whichever registry carries it. We never throw — observability surfaces
    MUST degrade gracefully.
    """
    out: dict[str, dict[str, Any]] = {}

    # ── 1) Substrate SOT: /root/AAA/docs/TOOLREGISTRY.json (canonical arif_* taxonomy) ──
    sots_candidates = [
        Path("/root/AAA/docs/TOOLREGISTRY.json"),
        Path("/root/arifOS/TOOL_MANIFEST.json"),
        Path("/opt/arifos/TOOL_MANIFEST.json"),
        Path("/opt/arifos/app/TOOL_MANIFEST.json"),
    ]
    for path in sots_candidates:
        if not path.exists():
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                raw = json.load(fh)
            break
        except Exception as exc:
            logger.warning("Failed to read registry %s: %s", path, exc)
            raw = None
            continue
    else:
        raw = None

    if isinstance(raw, dict):
        sots_index = raw.get("_index") or {}
        for entry in raw.get("skills") or []:
            if isinstance(entry, dict) and entry.get("name"):
                name = entry["name"]
                out[name] = {**out.get(name, {}), **entry, "_source": "TOOLREGISTRY.json"}

    # ── 2) Live affordance SOT: /root/arifOS/arifosmcp/tool_registry.json (canonical_count: 18) ──
    affordance_candidates = [
        Path("/root/arifOS/arifosmcp/tool_registry.json"),
        Path("/opt/arifos/app/arifosmcp/tool_registry.json"),
    ]
    for path in affordance_candidates:
        if not path.exists():
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                affordance = json.load(fh)
            break
        except Exception:
            continue
    else:
        affordance = None

    if isinstance(affordance, dict):
        # canonical_order = list of canonical public tools in execution order
        canonical_set = set(affordance.get("canonical_order") or [])
        tools_dict = affordance.get("tools") or {}
        # If tools is a dict (name -> metadata), traverse it.
        if isinstance(tools_dict, dict):
            for name, entry in tools_dict.items():
                if not isinstance(entry, dict):
                    continue
                merged = {
                    **out.get(name, {}),
                    **entry,
                    "_source": out.get(name, {}).get("_source", "tool_registry.json")
                    + " + tool_registry.json"
                    if name in out
                    else "tool_registry.json",
                }
                merged["canonical"] = name in canonical_set
                out[name] = merged
        elif isinstance(tools_dict, list):
            for entry in tools_dict:
                if isinstance(entry, dict) and entry.get("name"):
                    name = entry["name"]
                    merged = {**out.get(name, {}), **entry, "_source": "tool_registry.json"}
                    merged["canonical"] = name in canonical_set
                    out[name] = merged

    return out


def _declared_arif_tools(registry_index: dict[str, dict[str, Any]]) -> set[str]:
    """Declared = canonical namespace arif_* in TOOLREGISTRY.json."""
    return {
        name
        for name, entry in registry_index.items()
        if name.startswith(PUBLIC_NAMESPACE_PREFIX) and entry.get("canonical", True)
    }


def _registered_tools(mcp: Any) -> set[str]:
    """Registered = live kernel tool names.

    Fallback chain (F2: never silently return empty):
        1. _tool_registry (legacy FastMCP 2.x)
        2. mcp.list_tools() via event loop (FastMCP 3.x async)
        3. public_tool_names_for_mode() — same source as /health tools_loaded
        4. _tool_manager._tools — internal enumeration (last resort)
    """
    if mcp is None:
        return set()

    # ── 1) Legacy: _tool_registry attribute ──
    registry = getattr(mcp, "_tool_registry", None)
    if registry:
        out: set[str] = set()
        for tool in registry:
            if hasattr(tool, "name"):
                out.add(tool.name)
            elif isinstance(tool, str):
                out.add(tool)
        if out:
            return out

    # ── 2) FastMCP 3.x: list_tools() is async ──
    # P1-5 deadlock fix: when asyncio.get_running_loop() succeeds, we are ON
    # the event loop thread.  run_coroutine_threadsafe followed by
    # future.result() blocks the loop for the timeout because the submitted
    # coroutine cannot execute until *this thread yields* — which it won't
    # while blocked on result().  Under connection storm this serialises
    # across concurrent callers (e.g. /api/observatory/v1/health →
    # seven_state_health → compute_capability_matrix → _registered_tools),
    # starving the loop.
    #
    # Strategy: detect event-loop-thread context and skip immediately to the
    # non-blocking fallback (public_tool_names_for_mode).  In a worker thread
    # (RuntimeError) we can safely spin a temporary event loop.
    try:
        loop = asyncio.get_running_loop()
        # Event-loop thread detected.  DO NOT block with run_coroutine_threadsafe.
        # Fall through to fallback 3 (public_surface).
    except RuntimeError:
        # No event loop running — we are in a worker thread or sync context.
        # Safe to create a temporary event loop.
        try:

            async def _get_tools():
                tools = await mcp.list_tools()
                return {t.name for t in tools if hasattr(t, "name")}

            result = asyncio.run(_get_tools())
            if result:
                return result
        except Exception:
            pass

    # ── 3) Fallback: public_surface (same source as /health tools_loaded) ──
    try:
        from arifosmcp.runtime.public_surface import public_tool_names_for_mode

        names = public_tool_names_for_mode()
        if names:
            return set(names)
    except Exception:
        pass

    # ── 4) Last resort: internal _tool_manager ──
    try:
        tm = getattr(mcp, "_tool_manager", None)
        if tm is not None:
            tools_dict = getattr(tm, "_tools", {})
            if tools_dict:
                return set(tools_dict.keys())
    except Exception:
        pass

    return set()


async def _registered_tools_async(mcp: Any) -> set[str]:
    """Async version — preferred when caller is async.

    Fallback chain (F2: never silently return empty):
        1. mcp.list_tools() — primary async path
        2. public_tool_names_for_mode() — same source as /health tools_loaded
        3. mcp._tool_manager._tools.keys() — internal enumeration (last resort)
    """
    if mcp is None:
        return set()

    # ── 1) Primary: mcp.list_tools() (FastMCP 3.x async) ──
    try:
        tools = await mcp.list_tools()
        names = {t.name for t in tools if hasattr(t, "name")}
        if names:
            return names
    except Exception:
        pass

    # ── 2) Fallback: public_surface (same source as /health tools_loaded) ──
    try:
        from arifosmcp.runtime.public_surface import public_tool_names_for_mode

        names = public_tool_names_for_mode()
        if names:
            return set(names)
    except Exception:
        pass

    # ── 3) Last resort: internal _tool_manager ──
    try:
        tm = getattr(mcp, "_tool_manager", None)
        if tm is not None:
            tools_dict = getattr(tm, "_tools", {})
            if tools_dict:
                return set(tools_dict.keys())
    except Exception:
        pass

    return set()


def _exposed_tools(server_json: dict[str, Any] | None) -> set[str]:
    """Exposed = /.well-known/mcp/server.json tools array."""
    if not server_json:
        return set()
    tools = server_json.get("tools") or server_json.get("canonical_tools") or []
    names: set[str] = set()
    for entry in tools:
        if isinstance(entry, dict) and entry.get("name"):
            names.add(entry["name"])
        elif isinstance(entry, str):
            names.add(entry)
    return names


def _load_test_cache() -> dict[str, dict[str, Any]]:
    """Read the per-tool test cache from disk. Returns {} on miss/error."""
    try:
        if not TEST_CACHE_PATH.exists():
            return {}
        with open(TEST_CACHE_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_test_cache(cache: dict[str, dict[str, Any]]) -> None:
    """Persist the per-tool test cache. Best-effort — never raises into the request path."""
    try:
        TEST_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = TEST_CACHE_PATH.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=2, sort_keys=True)
        tmp.replace(TEST_CACHE_PATH)
    except Exception as exc:
        logger.warning("Could not write capability-test-cache: %s", exc)


def record_test_result(
    tool_name: str,
    *,
    passed: bool,
    error: str | None = None,
    input_schema_hash: str | None = None,
    output_schema_hash: str | None = None,
    invoked_at: float | int | None = None,
) -> None:
    """Public hook for live MCP tool paths and observatory seal/test probes.

    Records the most recent invocation result. The snapshot marks a tool as
    `tested` if the latest pass is within TEST_FRESHNESS_SECONDS, and as
    `proven_live` if within PROVEN_LIVE_SECONDS.
    """
    cache = _load_test_cache()
    prior = cache.get(tool_name) if isinstance(cache.get(tool_name), dict) else {}
    epoch = int(invoked_at if invoked_at is not None else time.time())
    # Never regress a newer observation with an older backfill.
    if prior.get("last_invocation_at") and int(prior["last_invocation_at"]) > epoch:
        return
    row = {
        "last_invocation_at": epoch,
        "last_pass": bool(passed),
        "last_error": error,
        "input_schema_hash": input_schema_hash or prior.get("input_schema_hash"),
        "output_schema_hash": output_schema_hash or prior.get("output_schema_hash"),
        "source": "record_test_result",
    }
    cache[tool_name] = row
    _save_test_cache(cache)


def _parse_event_epoch(event: dict[str, Any]) -> float | None:
    """Best-effort epoch from a durable bus event."""
    for key in (
        "timestamp",
        "timestamp_start",
        "timestamp_end",
        "_emitted_at",
        "ts",
        "created_at",
        "observed_at",
    ):
        raw = event.get(key)
        if raw is None:
            continue
        if isinstance(raw, (int, float)):
            return float(raw)
        if isinstance(raw, str) and raw.strip():
            try:
                from datetime import datetime

                return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
            except Exception:
                continue
    return None


def hydrate_test_cache_from_durable_bus(*, limit: int = 50_000) -> int:
    """Merge durable operation SUCCESS events into the capability test cache.

    Returns number of public tools updated. F2 honesty: only SUCCESS/ok/pass
    statuses count as proven; STARTED alone never does.

    Default limit raised 5k → 50k (2026-07-30): operations.log + receipts.log
    combined exceeds 5k lines, so the old window was mostly receipts and
    missed recent arif_* SUCCESS operations — proven_live stuck at 3/8.
    """
    try:
        from arifosmcp.runtime.event_bus import read_durable_events
    except Exception as exc:
        logger.debug("durable bus import failed: %s", exc)
        return 0

    try:
        events = read_durable_events(limit=limit)
    except Exception as exc:
        logger.debug("durable bus read failed: %s", exc)
        return 0

    latest: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        tool = event.get("capability") or event.get("tool") or event.get("name")
        if not isinstance(tool, str) or not tool.startswith(PUBLIC_NAMESPACE_PREFIX):
            continue
        if tool not in PUBLIC_CANONICAL_TOOLS:
            continue
        status = str(event.get("status") or "").upper()
        success = event.get("success")
        passed = status in {"SUCCESS", "OK", "PASS", "SEAL", "COMPLETED"} or success is True
        if not passed:
            continue
        epoch = _parse_event_epoch(event)
        if epoch is None:
            continue
        prev = latest.get(tool)
        if prev is None or epoch > float(prev["last_invocation_at"]):
            latest[tool] = {
                "last_invocation_at": int(epoch),
                "last_pass": True,
                "last_error": None,
                "source": "durable_event_bus",
            }

    if not latest:
        return 0

    cache = _load_test_cache()
    updated = 0
    for tool, row in latest.items():
        prior = cache.get(tool) if isinstance(cache.get(tool), dict) else {}
        prior_at = int(prior.get("last_invocation_at") or 0)
        if row["last_invocation_at"] >= prior_at:
            cache[tool] = {
                **prior,
                **row,
                "input_schema_hash": prior.get("input_schema_hash"),
                "output_schema_hash": prior.get("output_schema_hash"),
            }
            updated += 1
    if updated:
        _save_test_cache(cache)
    return updated


def _schema_hash(value: Any) -> str | None:
    """Deterministic sha256 over canonical-json of a value, or None."""
    if value is None:
        return None
    try:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        return None
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def compute_capability_matrix(
    mcp: Any | None,
    server_json: dict[str, Any] | None,
    registry_index: dict[str, dict[str, Any]] | None = None,
    registered_tools: set[str] | None = None,
) -> dict[str, Any]:
    """Build the canonical capability-drift matrix.

    Args:
        mcp: FastMCP instance (used only if registered_tools is None)
        server_json: server.json for exposed tools
        registry_index: pre-loaded registry index
        registered_tools: pre-computed set of registered tool names (preferred —
                          avoids async issues with FastMCP 3.x list_tools())

    Returns:
        {
          "declared_count": int,
          "registered_count": int,
          "exposed_count": int,
          "invocable_count": int,
          "tested_count": int,
          "degraded_count": int,
          "matrix": [{ name, declared, registered, exposed, invocable, tested,
                        input_schema_hash_match, output_schema_hash_match,
                        last_test_at, last_failure, capability_truth }, ...],
          "as_of": iso8601,
        }
    """
    if registry_index is None:
        registry_index = _load_registry_index()

    # Wire live MCP SUCCESS (durable bus) into the test cache before scoring.
    try:
        hydrate_test_cache_from_durable_bus()
    except Exception as exc:
        logger.debug("hydrate_test_cache_from_durable_bus failed: %s", exc)

    declared = _declared_arif_tools(registry_index)
    # Public surface discipline: matrix rows are the constitutional 8, plus any
    # extra declared arif_* so drift still surfaces — but headline counts use public 8.
    registered = registered_tools if registered_tools is not None else _registered_tools(mcp)
    exposed = _exposed_tools(server_json)
    # Prefer explicit public wire when registries are noisy/multi-tier.
    if not declared:
        declared = set(PUBLIC_CANONICAL_TOOLS)
    public_declared = declared & PUBLIC_CANONICAL_TOOLS or set(PUBLIC_CANONICAL_TOOLS)
    # Restrict registered/exposed counters to public wire for F-001 honesty.
    registered_public = registered & PUBLIC_CANONICAL_TOOLS
    exposed_public = exposed & PUBLIC_CANONICAL_TOOLS if exposed else set(PUBLIC_CANONICAL_TOOLS)
    if not exposed:
        # server.json miss: if registered on public wire, treat as exposed on public facade
        exposed_public = set(registered_public)
        exposed = set(registered)

    test_cache = _load_test_cache()

    # Rows: public 8 first; include any other declared arif_* for drift visibility.
    all_tools = public_declared | (declared - PUBLIC_CANONICAL_TOOLS)
    matrix: list[dict[str, Any]] = []

    invocable_count = 0
    tested_count = 0
    proven_live_count = 0
    degraded_count = 0
    now = time.time()

    for tool_name in sorted(all_tools):
        canon = registry_index.get(tool_name, {})
        is_public = tool_name in PUBLIC_CANONICAL_TOOLS
        in_registered = tool_name in registered or tool_name in registered_public
        in_exposed = tool_name in exposed or tool_name in exposed_public
        live_invocable = in_registered and in_exposed
        cache_row = (
            test_cache.get(tool_name, {}) if isinstance(test_cache.get(tool_name), dict) else {}
        )
        last_at = cache_row.get("last_invocation_at")
        age = (now - float(last_at)) if last_at else None
        fresh = age is not None and age <= TEST_FRESHNESS_SECONDS
        proven = age is not None and age <= PROVEN_LIVE_SECONDS and bool(cache_row.get("last_pass"))
        last_pass = bool(cache_row.get("last_pass"))
        # `tested` ⇒ fresh successful invocation (matrix "tested" column).
        # `proven_live` ⇒ durable SUCCESS within 24h (auditor "proven live").
        tested = fresh and last_pass

        registry_in_hash = _schema_hash(canon.get("input_schema"))
        registry_out_hash = _schema_hash(canon.get("output_schema"))
        observed_in_hash = cache_row.get("input_schema_hash")
        observed_out_hash = cache_row.get("output_schema_hash")
        # Hash-match only meaningful when we have BOTH sides; missing observed ⇒ unknown.
        in_match = (
            observed_in_hash is not None
            and registry_in_hash is not None
            and observed_in_hash == registry_in_hash
        )
        out_match = (
            observed_out_hash is not None
            and registry_out_hash is not None
            and observed_out_hash == registry_out_hash
        )

        # Truth ladder — PROVEN for durable success without full schema match.
        if tool_name not in declared and tool_name not in PUBLIC_CANONICAL_TOOLS:
            truth = "VOID"
        elif all(
            [
                tool_name in declared or is_public,
                in_registered,
                in_exposed,
                tested,
                in_match,
                out_match,
            ]
        ):
            truth = "PASS"
        elif live_invocable and proven:
            truth = "PROVEN"
        elif live_invocable and not proven:
            truth = "EXPOSED_UNPROVEN"
        else:
            truth = "DEGRADED"

        if is_public and in_registered and in_exposed:
            invocable_count += 1
        if is_public and tested:
            tested_count += 1
        if is_public and proven:
            proven_live_count += 1
        if is_public and truth not in {"PASS", "PROVEN"}:
            degraded_count += 1

        matrix.append(
            {
                "name": tool_name,
                "declared": tool_name in declared or is_public,
                "registered": in_registered,
                "exposed": in_exposed,
                "invocable": live_invocable,
                "tested": tested,
                "proven_live": proven,
                "input_schema_hash_match": in_match,
                "output_schema_hash_match": out_match,
                "last_test_at": (
                    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(last_at)))
                    if last_at
                    else None
                ),
                "age_seconds": int(age) if age is not None else None,
                "last_failure": cache_row.get("last_error"),
                "capability_truth": truth,
                "evidence_source": cache_row.get("source"),
            }
        )

    return {
        "as_of": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "declared_count": len(public_declared),
        "registered_count": len(registered_public)
        if registered_public
        else len(public_declared & registered),
        "exposed_count": len(exposed_public) if exposed_public else len(public_declared),
        "invocable_count": invocable_count,
        "callable_public": invocable_count,
        "tested_count": tested_count,
        "proven_live_count": proven_live_count,
        "degraded_count": degraded_count,
        "untested_count": max(0, len(public_declared) - tested_count),
        "matrix": matrix,
        "semantics": {
            "callable_public": "declared ∧ registered ∧ exposed on public wire",
            "proven_live": f"durable SUCCESS within {PROVEN_LIVE_SECONDS}s",
            "tested": f"fresh SUCCESS within {TEST_FRESHNESS_SECONDS}s",
            "operational_tools": "alias of proven_live_count (not invocable alone)",
        },
    }


def per_field(
    value: Any,
    *,
    source: str,
    observed_at: str | None = None,
    state: str = "observed",
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Envelope helper: every cell of the snapshot uses this shape.

    `state` is one of: observed | derived | reported | unknown.
    `source` MUST be a free-text endpoint/file/probe name (audit clause: no claim without source).
    """
    return {
        "value": value,
        "state": state,
        "source": source,
        "observed_at": observed_at or time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime()),
        "age_seconds": 0,
        "confidence": confidence,
    }


def per_field_age(
    value: Any,
    *,
    source: str,
    observed_at_epoch: float | None,
    state: str = "observed",
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Like per_field() but computes age_seconds from a past epoch.

    When `observed_at_epoch` is None we fall back to per_field() with state="unknown".
    """
    if observed_at_epoch is None:
        return per_field(value, source=source, state="unknown", confidence=0.0)
    age = max(0, int(time.time() - observed_at_epoch))
    return {
        "value": value,
        "state": state,
        "source": source,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(observed_at_epoch)),
        "age_seconds": age,
        "confidence": confidence,
    }
