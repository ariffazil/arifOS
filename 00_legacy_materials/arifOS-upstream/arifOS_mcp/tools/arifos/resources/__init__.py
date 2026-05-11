"""
arifOS Resources — Organ Context Providers
DITEMPA BUKAN DIBERI — 999 SEAL

All organ context is fetched via internal adapters (not external MCP calls).
GEOX = earth science | WEALTH = capital intelligence | WELL = biological substrate
"""

from fastmcp.resources import Resource

from ..adapters.geox_adapter import geox_witness
from ..adapters.wealth_adapter import wealth_witness
from ..adapters.well_adapter import well_witness

geox_context_resource = Resource(
    uri="resource://geox/context",
    name="GEOX Context",
    description="Earth science evidence from GEOX organ (geological, seismic, volumetric)",
    mime_type="application/json",
)

wealth_context_resource = Resource(
    uri="resource://wealth/context",
    name="WEALTH Context",
    description="Capital intelligence from WEALTH organ (NPV, EMV, market signals)",
    mime_type="application/json",
)

well_context_resource = Resource(
    uri="resource://well/context",
    name="WELL Context",
    description="Biological substrate readiness from WELL organ (HRV, stability, health)",
    mime_type="application/json",
)


async def get_geox_context(ctx, query: str) -> dict:
    """Fetch GEOX Tri-Witness evidence via internal adapter."""
    return await geox_witness(zone_id=query or "DEFAULT")


async def get_wealth_context(ctx, query: str) -> dict:
    """Fetch WEALTH Tri-Witness evidence via internal adapter."""
    return await wealth_witness(prospect_id=query or "DEFAULT")


async def get_well_context(ctx, query: str) -> dict:
    """Fetch WELL Tri-Witness evidence via internal adapter."""
    return await well_witness(zone_id=query or "SYSTEM")
