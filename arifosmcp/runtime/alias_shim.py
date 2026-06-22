"""
arifosmcp.runtime.alias_shim — Phase 2 dual-mode dispatcher
═══════════════════════════════════════════════════════════════════════════════
PHASE 2 EVIDENCE — Registered when ARIFOS_MCP_DUAL_MODE=true.

Purpose:
  During the 14-ACT refactor migration, both old (arif_noun_verb) and new
  (arif_verb) tool names must work on the wire. This module registers the
  12 NEW canonical names as thin wrappers that dispatch to the existing
  handlers.

Behavior:
  - When ARIFOS_MCP_DUAL_MODE=true (Phase 2, default):
      tools/list returns 27 old + 12 new = 39 tools
      Old names: unchanged behavior
      New names: identical result + _meta._canonical block

  - When ARIFOS_MCP_DUAL_MODE=false (Phase 3 cutover):
      This module is a no-op. Only 14 new names registered.

Date: 2026-06-21
Live commit at authoring: 84c71c1
Operator: FORGE (000Ω)

DITEMPA BUKAN DIBERI — Forged, Not Given
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
import os
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT TOGGLE
# ═════════════════════════════════════════════════════════════════════════════


def dual_mode_enabled() -> bool:
    """
    True if dual-mode is active (Phase 2).
    Default: True (Phase 2 in progress).
    Set ARIFOS_MCP_DUAL_MODE=false for Phase 3 cutover.
    """
    val = os.getenv("ARIFOS_MCP_DUAL_MODE", "true").strip().lower()
    return val in ("true", "1", "yes", "on")


# ═════════════════════════════════════════════════════════════════════════════
# WRAPPER FACTORY — adds _meta._canonical block to identify new-name calls
# ═════════════════════════════════════════════════════════════════════════════


def _make_canonical_wrapper(
    handler: Callable[..., Any],
    new_name: str,
    legacy_target: str,
) -> Callable[..., Any]:
    """
    Wrap a legacy handler so calls to the new canonical name are tagged
    with provenance metadata. Does NOT change behavior — only adds metadata.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = handler(*args, **kwargs)
        if isinstance(result, dict):
            # Ensure _meta exists
            meta = result.setdefault("_meta", {})
            if isinstance(meta, dict):
                meta["_canonical"] = {
                    "called_as": new_name,
                    "legacy_target": legacy_target,
                    "shim_active": True,
                    "migration_note": f"{new_name} is the new canonical name; {legacy_target} will be deprecated.",
                }
        return result
    return wrapper


# ═════════════════════════════════════════════════════════════════════════════
# DISPATCH REGISTRATION — register the 12 NEW canonical tools
# ═════════════════════════════════════════════════════════════════════════════


def register_new_canonical_tools(
    mcp: Any,  # FastMCP instance
    canonical_handlers: dict[str, Callable[..., Any]],
    diagnostic_handlers: dict[str, Callable[..., Any]],
) -> list[str]:
    """
    Register the 12 NEW canonical tool names (13 ACT + 1 ART, minus the
    2 that already exist as arif_route and arif_bridge).

    Returns: list of newly registered names.
    """
    if not dual_mode_enabled():
        logger.info("alias_shim: ARIFOS_MCP_DUAL_MODE=false, skipping registration")
        return []

    registered: list[str] = []

    # ── Map from new name → (handler, legacy target name) ────────────────
    new_to_legacy: dict[str, tuple[Callable[..., Any], str]] = {
        # 1:1 renames (old name's handler is reused)
        "arif_init":       (canonical_handlers.get("arif_init"),  "arif_init"),
        "arif_observe":    (canonical_handlers.get("arif_observe"), "arif_observe"),
        "arif_evidence":   (canonical_handlers.get("arif_fetch"), "arif_fetch"),
        "arif_reason":     (canonical_handlers.get("arif_think_tool") or canonical_handlers.get("arif_think"), "arif_think"),
        "arif_critique":   (canonical_handlers.get("arif_critique"), "arif_critique"),
        "arif_reply":      (canonical_handlers.get("arif_compose_tool") or canonical_handlers.get("arif_compose"), "arif_compose"),
        "arif_measure":    (canonical_handlers.get("arif_measure"),  "arif_measure"),
        "arif_judge":      (canonical_handlers.get("arif_judge_tool") or canonical_handlers.get("arif_judge"), "arif_judge"),
        "arif_seal":       (canonical_handlers.get("arif_seal_tool") or canonical_handlers.get("arif_seal"), "arif_seal"),
        "arif_forge":      (canonical_handlers.get("arif_forge_tool") or canonical_handlers.get("arif_forge"), "arif_forge"),
    }

    for new_name, (handler, legacy_target) in new_to_legacy.items():
        if handler is None:
            logger.warning(f"alias_shim: no handler for {new_name} (legacy: {legacy_target})")
            continue
        wrapped = _make_canonical_wrapper(handler, new_name, legacy_target)
        try:
            mcp.tool(
                name=new_name,
                description=(
                    f"[NEW CANONICAL NAME] {new_name} — alias for {legacy_target}. "
                    f"This is the post-14-ACT-refactor canonical name. "
                    f"Calls {legacy_target} internally with same args."
                ),
                tags={"canonical", "new-name", "phase2-shim"},
            )(wrapped)
            registered.append(new_name)
            logger.info(f"alias_shim: registered {new_name} → {legacy_target}")
        except Exception as e:
            logger.error(f"alias_shim: failed to register {new_name}: {e}")

    # ── Special: arif_recall — dispatches to memory v5 or v4 by mode ────
    _register_arif_recall(mcp, canonical_handlers, diagnostic_handlers, registered)

    # ── Special: arif_probe — dispatches to 6 canary probes by mode ─────
    _register_arif_probe(mcp, canonical_handlers, diagnostic_handlers, registered)

    return registered


def _register_arif_recall(
    mcp: Any,
    canonical_handlers: dict[str, Callable[..., Any]],
    diagnostic_handlers: dict[str, Callable[..., Any]],
    registered_out: list[str],
) -> None:
    """
    Register arif_recall — unified memory tool.

    Mode dispatch:
      v5 modes (store/seal/forget/promote/revise/audit/stats/learn) → v5 router
      v4 modes (recall/etc) → v4 legacy _arif_memory_recall
    """
    v5_handler = canonical_handlers.get("arif_memory")
    v4_handler = canonical_handlers.get("arif_memory_recall")

    if v5_handler is None and v4_handler is None:
        logger.warning("alias_shim: no memory handlers found, skipping arif_recall")
        return

    V5_MODES = {"store", "seal", "forget", "promote", "revise", "audit", "stats", "learn", "v5"}
    V4_MODES = {"recall", "v4", "get", "list", "context", "repo_ingest", "repo_search", "manage"}

    def arif_recall_wrapper(*args: Any, **kwargs: Any) -> Any:
        mode = kwargs.get("mode") or (args[0] if args else None) or "recall"
        if mode in V5_MODES and v5_handler is not None:
            handler = v5_handler
        elif v4_handler is not None:
            handler = v4_handler
        else:
            handler = v5_handler  # fallback

        result = handler(*args, **kwargs)
        if isinstance(result, dict):
            meta = result.setdefault("_meta", {})
            if isinstance(meta, dict):
                meta["_canonical"] = {
                    "called_as": "arif_recall",
                    "dispatched_to": "v5" if mode in V5_MODES else "v4",
                    "legacy_targets": ["arif_memory", "arif_memory_recall"],
                    "shim_active": True,
                }
        return result

    try:
        mcp.tool(
            name="arif_recall",
            description=(
                "[NEW CANONICAL NAME] arif_recall — unified memory tool. "
                "Replaces arif_memory (v5) and arif_memory_recall (v4). "
                "Mode dispatches to v5 (store/seal/forget/...) or v4 (recall/etc) automatically."
            ),
            tags={"canonical", "new-name", "phase2-shim", "memory"},
        )(arif_recall_wrapper)
        registered_out.append("arif_recall")
        logger.info("alias_shim: registered arif_recall (v5+v4 unified)")
    except Exception as e:
        logger.error(f"alias_shim: failed to register arif_recall: {e}")


def _register_arif_probe(
    mcp: Any,
    canonical_handlers: dict[str, Callable[..., Any]],
    diagnostic_handlers: dict[str, Callable[..., Any]],
    registered_out: list[str],
) -> None:
    """
    Register arif_probe — unified transport probe.

    Mode dispatch:
      'ping' → arif_ping
      'conformance' → arif_conformance_report
      'schema_echo' → arif_schema_echo
      'version_echo' → arif_version_echo
      'transport_echo' → arif_transport_echo
      'initialize' → arif_initialize_probe
    """
    probe_targets: dict[str, str] = {
        "ping": "arif_ping",
        "conformance": "arif_conformance_report",
        "schema_echo": "arif_schema_echo",
        "version_echo": "arif_version_echo",
        "transport_echo": "arif_transport_echo",
        "initialize": "arif_initialize_probe",
    }

    # Collect handlers from both dicts (probe tools are in diagnostic)
    all_handlers: dict[str, Callable[..., Any]] = {}
    all_handlers.update(diagnostic_handlers)
    all_handlers.update(canonical_handlers)

    def arif_probe_wrapper(*args: Any, **kwargs: Any) -> Any:
        mode = kwargs.get("mode") or (args[0] if args else None) or "ping"
        target_name = probe_targets.get(mode, "arif_ping")
        handler = all_handlers.get(target_name)
        if handler is None:
            return {
                "_error": "probe_handler_missing",
                "mode": mode,
                "expected_target": target_name,
                "available_modes": list(probe_targets.keys()),
            }
        result = handler(*args, **kwargs)
        if isinstance(result, dict):
            meta = result.setdefault("_meta", {})
            if isinstance(meta, dict):
                meta["_canonical"] = {
                    "called_as": "arif_probe",
                    "mode_dispatched": mode,
                    "legacy_target": target_name,
                    "shim_active": True,
                }
        return result

    try:
        mcp.tool(
            name="arif_probe",
            description=(
                "[NEW CANONICAL NAME] arif_probe — unified transport probe. "
                "Replaces 6 canary probes (arif_ping, arif_conformance_report, "
                "arif_schema_echo, arif_version_echo, arif_transport_echo, arif_initialize_probe). "
                "Use mode parameter: ping | conformance | schema_echo | version_echo | transport_echo | initialize."
            ),
            tags={"canonical", "new-name", "phase2-shim", "probe", "transport"},
        )(arif_probe_wrapper)
        registered_out.append("arif_probe")
        logger.info("alias_shim: registered arif_probe (6 canary modes unified)")
    except Exception as e:
        logger.error(f"alias_shim: failed to register arif_probe: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ═════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    print("=" * 70)
    print("ALIAS SHIM — Phase 2 dual-mode dispatcher")
    print("=" * 70)
    print(f"\nDual mode enabled: {dual_mode_enabled()}")
    print(f"  (ARIFOS_MCP_DUAL_MODE env var)")

    new_names_to_register = [
        "arif_init", "arif_observe", "arif_evidence", "arif_reason",
        "arif_critique", "arif_reply", "arif_recall", "arif_measure",
        "arif_judge", "arif_seal", "arif_forge", "arif_probe",
    ]
    print(f"\nNew names to register ({len(new_names_to_register)}):")
    for n in new_names_to_register:
        print(f"  - {n}")

    print(f"\narif_recall mode dispatch:")
    print(f"  v5: store, seal, forget, promote, revise, audit, stats, learn")
    print(f"  v4: recall, get, list, context, repo_ingest, repo_search, manage")

    print(f"\narif_probe mode dispatch:")
    for mode, target in [
        ("ping", "arif_ping"),
        ("conformance", "arif_conformance_report"),
        ("schema_echo", "arif_schema_echo"),
        ("version_echo", "arif_version_echo"),
        ("transport_echo", "arif_transport_echo"),
        ("initialize", "arif_initialize_probe"),
    ]:
        print(f"  mode={mode!r} → {target}")

    print(f"\nPhase 2 behavior:")
    print(f"  DUAL_MODE=true  → 27 old + 12 new = 39 tools on wire")
    print(f"  DUAL_MODE=false → 27 old only (Phase 3 cutover requires code update)")
    print(f"\nDITEMPA BUKAN DIBERI.")