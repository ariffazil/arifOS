"""Canonical resource authority for arifOS MCP."""

from __future__ import annotations

import json

from arifosmcp.resources import (
    CANONICAL_RESOURCES,
    EMBODIED_RESOURCES,
    EVIDENCE_RESOURCES,
    TREE777_RESOURCES,
    register_resources,
)

# ── System capabilities (was missing — pre-existing bug closed 2026-07-07) ────
# F1 AMANAH: conservative system metadata. Source of truth for /charter "system" block.
SYSTEM_CAPABILITIES = {
    "version": "2.0.0",
    "kernel": "arifOS",
    "model_architecture": "constitutional_substrate",
    "substrate_separation": True,
    "trinity_lanes": ["AGI", "ASI", "APEX"],
    "constitutional_floors": 13,
    "verdict_system": ["SEAL", "PARTIAL", "VOID", "HOLD"],
    "transport": ["mcp", "a2a", "rest"],
    "authentication_required": False,
    "public_endpoint": "https://arifosmcp.arif-fazil.com/mcp",
    "protocol": {
        "mcp_version": "2025-11-25",
        "a2a_version": "1.0.1",
    },
}

__all__ = [
    "CANONICAL_RESOURCES",
    "EVIDENCE_RESOURCES",
    "TREE777_RESOURCES",
    "EMBODIED_RESOURCES",
    "register_resources",
    "manifest_resources",
    "read_resource_content",
    "apex_tools_markdown_table",
    "SYSTEM_CAPABILITIES",
]


# Agent-critical bootstrap resources registered via FastMCP ext (not CANONICAL tuple).
# REST /resources must list these so agents discover without MCP wire-only knowledge.
# Source: arifosmcp/runtime/fastmcp_ext/resources.py — GAP1 server/discover fix 2026-08-04.
BOOTSTRAP_RESOURCES = (
    "arifos://instructions",  # MCP-native server/discover equivalent
    "arifos://carry-forward",  # live session continuity
    "arifos://flow-state",  # FQ pulse gate
    "arifos://init/agent_init",  # INIT.md boot contract
)


def manifest_resources() -> list[str]:
    """
    Return the canonical and evidence resource URI manifests.

    Includes all 5 URI families:
      - CANONICAL (arifos://doctrine, vitals, schema, forge, civilization)
      - TREE777 (tree777://index, search, skills/{cat}/{name}, concepts/{name}, scars/{name})
      - EMBODIED (arifos://tools/self-model/{view}, witness/{filter}, boundaries/{domain})
      - EVIDENCE (source://{hash}, receipt://..., contrast://..., void://...)
      - BOOTSTRAP (instructions, carry-forward, flow-state, agent_init) — FastMCP ext
    """
    return (
        list(BOOTSTRAP_RESOURCES)
        + list(CANONICAL_RESOURCES)
        + list(TREE777_RESOURCES)
        + list(EMBODIED_RESOURCES)
        + list(EVIDENCE_RESOURCES)
    )


async def read_resource_content(uri: str) -> str:
    """
    Resolve a resource URI and return its content.

    Handles:
      - tree777:// URIs         → TREE777 wiki pages
      - arifos:// URIs          → arifOS canonical + bootstrap resources
      - source://, receipt://,
        contrast://, void://    → F-WEB evidence resources

    Returns the resource content as a string, or an error message
    if the URI cannot be resolved.
    """
    uri = (uri or "").strip()

    # ── Bootstrap / agent-critical (FastMCP ext + doctrine modules) ──
    # REST path does not share FastMCP's in-process resource map; resolve
    # known URIs here so /resources/{uri} does not panic or return empty.
    if uri == "arifos://instructions":
        return (
            "REFERENCE: ARIFOS::KERNEL\n"
            "\n"
            "IDENTITY:\n"
            "You are arifOS.\n"
            "You are Law.\n"
            "You are not an executor.\n"
            "\n"
            "AUTHORITY:\n"
            "Sovereign = ARIF\n"
            "Runtime = Federation\n"
            "Execution = A-FORGE\n"
            "\n"
            "MISSION:\n"
            "Judge proposed actions.\n"
            "Maintain constitutional integrity.\n"
            "Protect sovereignty.\n"
            "\n"
            "CONSTRAINTS:\n"
            "Fail Closed.\n"
            "No Pretending.\n"
            "Evidence First.\n"
            "Separate Judge from Executor.\n"
            "\n"
            "VERDICTS:\n"
            "SEAL\n"
            "HOLD\n"
            "SABAR\n"
            "VOID\n"
            "\n"
            "RULE:\n"
            "The entity performing an action cannot authorize itself.\n"
            "\n"
            "OUTPUT:\n"
            "EVIDENCE\n"
            "INTERPRET\n"
            "VERDICT\n"
            "\n"
            "═══ BOOT ORDER — IDENTITY → LAW → AUTHORITY → RESOURCES ═══\n"
            "Constitutional context, not capabilities. Canonical surfaces in order:\n"
            "  1. identity.toml     — sovereign identity (/opt/arifos/identity.toml at runtime)\n"
            "  2. CONSTITUTION      — F1–F13, verdict lattice, sovereign rules\n"
            "                         (docs/CONSTITUTION.md + GENESIS/)\n"
            "  3. INVARIANTS.md     — boundaries\n"
            "  4. FEDERATION.md     — federation map (ARIF · AAA · A-FORGE · VAULT999)\n"
            "  5. tools_sot.yaml    — capability registry\n"
            "  6. organ.yaml        — organs\n"
            "  7. VAULT999/         — memory pointers (the only permanent memory)\n"
            "Goals, tasks, plans, tool inventories, and conversation summaries are\n"
            "NOT kernel init state. They are discovered after boot.\n"
            "\n"
            "═══ AGENT BOOT SEQUENCE (MCP-NATIVE) ═══\n"
            "  1. READ resource arifos://bootstrap → live federation context\n"
            "  2. READ resource arifos://carry-forward → prior session state\n"
            "  3. READ resource arifos://flow-state → FQ pulse (FQ<0.5 → OBSERVE_ONLY)\n"
            "  4. CALL prompt '⚓ INIT' → collapsed governed ignition\n"
            "  5. CALL tool arif_init → bind session + get SCT token\n"
            "\n"
            "═══ AGENT CLOSE SEQUENCE (MCP-NATIVE) ═══\n"
            "  1. CALL prompt '🔐 CLOSE' → full session close ritual\n"
            "  2. CALL tool arif_seal or forge_vault → immutable record\n"
            "  3. VERIFY: resources/read arifos://vault/head\n"
            "\n"
            "Golden path: init → observe → think → route → memory → judge → forge → seal\n"
            "The kernel judges and seals. It never executes.\n"
            "executor_attached is probed, never assumed.\n"
            "DITEMPA BUKAN DIBERI — Forged, Not Given\n"
        )

    if uri == "arifos://carry-forward":
        from pathlib import Path

        for p in (
            Path("/root/.local/share/arifos/carry_forward.json"),
            Path("/root/carry_forward.json"),
        ):
            if p.is_file():
                return p.read_text(encoding="utf-8")
        return json.dumps({"error": "carry_forward.json not found", "uri": uri})

    if uri == "arifos://flow-state":
        from pathlib import Path

        for p in (
            Path("/root/AAA/state/flow_state.json"),
            Path("/root/.local/share/arifos/flow_state.json"),
        ):
            if p.is_file():
                return p.read_text(encoding="utf-8")
        return json.dumps({"error": "flow_state.json not found", "uri": uri})

    if uri == "arifos://doctrine":
        try:
            from arifosmcp.resources.doctrine import DOCTRINE_TEXT

            return DOCTRINE_TEXT
        except Exception as exc:  # pragma: no cover
            return f"ERROR: doctrine load failed: {exc}"

    if uri == "arifos://init/agent_init":
        from pathlib import Path

        for p in (
            Path("/root/AAA/prompts/INIT.md"),
            Path("/root/AAA/prompts/SALAM_AAA_INIT.md"),
        ):
            if p.is_file():
                return p.read_text(encoding="utf-8")
        return "ERROR: INIT.md not found"

    # ── TREE777 + generic handlers ──
    from arifosmcp.resources.tree777 import handle_resource

    result = handle_resource(uri)
    body = result.get("body", "")
    err = result.get("error") or ""

    # Unknown TREE777 URI is expected for many arifos:// resources — try empty fail-soft
    if err and "Unknown TREE777" in str(err):
        return f"ERROR: Resource not resolved via REST catalog: {uri}. Prefer MCP resources/read."

    # Distinguish between a resolved resource and an error
    if isinstance(body, str) and ("ERROR" in body or "error" in str(err).lower()):
        return f"ERROR: {err or body or 'Unknown error'}"

    # For JSON bodies (index, search results), return the JSON string
    if isinstance(body, dict):
        return json.dumps(body, indent=2)

    return str(body) if body else f"ERROR: empty content for {uri}"


def apex_tools_markdown_table() -> str:
    """Stub for the apex tools markdown table (was in deleted resources.py)."""
    return ""
