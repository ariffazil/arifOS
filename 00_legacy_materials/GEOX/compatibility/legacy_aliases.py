"""
GEOX Compatibility Zone — Legacy Aliases
═══════════════════════════════════════════════════════════════════════════════
This module serves as the quarantine zone for deprecated aliases.
NO NEW FEATURES SHOULD BE BORN HERE.

This prevents the core contract layer from being polluted by backward compatibility mappings.
"""

import logging
from fastmcp import FastMCP

logger = logging.getLogger("geox.compatibility")


def register_legacy_aliases(mcp: FastMCP):
    """
    Registers legacy aliases mapping to the canonical tools.
    These aliases exist only to prevent existing workflows from breaking.
    """

    # ─── PROSPECT ALIASES ──────────────────────────────────────────────
    @mcp.tool(name="geox_evaluate_prospect")
    async def legacy_geox_evaluate_prospect(area_id: str) -> dict:
        """[DEPRECATED] Use prospect_evaluate instead."""
        # Wait, due to the FastMCP decorator mechanics, these aliases need to be dynamically registered
        # or we just rely on the ones we left inside the contracts/tools/ modules until fully deprecated.
        logger.warning(
            "Call to deprecated tool: geox_evaluate_prospect. Migrate to prospect_evaluate."
        )
        # For now, the legacy wrappers are physically located inside the contracts/tools modules
        # so they can be discovered easily. Over time, they should be migrated here.
        pass

    # ─── WELL ALIASES ──────────────────────────────────────────────────
    @mcp.tool(name="geox_compute_petrophysics")
    async def legacy_geox_compute_petrophysics(
        model: str, rw: float, rt: float, phi: float, a: float = 1.0, m: float = 2.0, n: float = 2.0
    ) -> dict:
        """[DEPRECATED] Use well_compute_petrophysics instead."""
        logger.warning(
            "Call to deprecated tool: geox_compute_petrophysics. Migrate to well_compute_petrophysics."
        )
        pass

    logger.info("Registered legacy compatibility aliases.")
