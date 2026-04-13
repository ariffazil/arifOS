"""
arifosmcp/apps/__init__.py
═══════════════════════════════════════════════════════════════════════════════
arifOS Constitutional MCP Apps — Registry
═══════════════════════════════════════════════════════════════════════════════

Auto-discovery and registration of all FastMCPApp constitutional surfaces.

Tier 1 (Governance Gate):
  - JudgeApp   (888_JUDGE)  — Constitutional verdict surface
  - VaultApp   (999_VAULT)  — Immutable ledger surface
  - ForgeApp   (FORGE)      — Double-gated execution surface

Tier 2 (Session):
  - InitApp    (000_INIT)   — Session anchoring surface

Tier 3 (Observability):
  - MetabolicMonitor        — F1-F13 floor radar (legacy @mcp.tool(app=True))

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ── App module registry (import path → human label) ──────────────────────────
_APP_MODULES: list[tuple[str, str]] = [
    ("arifosmcp.apps.metabolic_monitor", "MetabolicMonitor (F1-F13 Radar)"),
    ("arifosmcp.apps.judge_app",         "JudgeApp (888_JUDGE)"),
    ("arifosmcp.apps.vault_app",         "VaultApp (999_VAULT)"),
    ("arifosmcp.apps.init_app",          "InitApp (000_INIT)"),
    ("arifosmcp.apps.forge_app",         "ForgeApp (FORGE Double-Gate)"),
]


def register_all_apps(mcp: "FastMCP") -> list[str]:
    """
    Register all constitutional MCP apps onto the given FastMCP server.
    Returns list of successfully registered app labels.

    Each app module must expose a `_register(mcp)` function.
    """
    registered: list[str] = []
    for module_path, label in _APP_MODULES:
        try:
            import importlib
            mod = importlib.import_module(module_path)
            reg_fn = getattr(mod, "_register", None)
            if reg_fn is not None:
                reg_fn(mcp)
                registered.append(label)
                logger.info(f"MCP Apps: {label} registered")
            else:
                logger.warning(f"MCP Apps: {label} has no _register function")
        except Exception as exc:
            logger.warning(f"MCP Apps: {label} unavailable: {exc}")
    return registered
