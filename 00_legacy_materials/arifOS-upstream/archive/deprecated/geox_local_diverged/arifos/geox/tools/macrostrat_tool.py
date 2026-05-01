"""
arifos/geox/tools/macrostrat_tool.py — Macrostrat API Adapter
DITEMPA BUKAN DIBERI

A hardened adapter for the Macrostrat geological API. 
Fetches stratigraphic columns and lithology data for spatial queries.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from arifos.geox.base_tool import (
    BaseTool,
    GeoToolResult,
)
from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoQuantity,
    ProvenanceRecord,
)

logger = logging.getLogger("geox.tools.macrostrat")

class MacrostratTool(BaseTool):
    """
    Adapter for the Macrostrat geological database.
    
    Queries Macrostrat's 'columns' and 'units' API for regional 
    stratigraphy and lithological properties.
    
    Inputs:
        location (CoordinatePoint) — query coordinates
    
    API: https://macrostrat.org/api/v2
    License: CC-BY-4.0 (attribution required)
    """

    BASE_URL = "https://macrostrat.org/api/v2"

    @property
    def name(self) -> str:
        return "MacrostratTool"

    @property
    def description(self) -> str:
        return (
            "Hardened Macrostrat API adapter. Provides regional stratigraphic "
            "columns, lithology, and geologic age data for spatial queries. "
            "Used for the 111 THINK and 333 EXPLORE stages."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"location"}
        if not required.issubset(inputs.keys()):
            return False
        if not isinstance(inputs["location"], CoordinatePoint):
            # Try to convert if it's a dict
            if isinstance(inputs["location"], dict):
                try:
                    inputs["location"] = CoordinatePoint(**inputs["location"])
                    return True
                except Exception:
                    return False
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Invalid inputs: 'location' (CoordinatePoint) required.",
            )

        start = time.perf_counter()
        location: CoordinatePoint = inputs["location"]

        try:
            # Query stratigraphic columns near location
            columns = await self._query_api("columns", location)

            # Query rock units
            units = await self._query_api("units", location)

            # Convert to GeoQuantity objects
            quantities = self._parse_to_quantities(columns, units, location)

            latency_ms = (time.perf_counter() - start) * 1000

            return GeoToolResult(
                tool_name=self.name,
                success=True,
                quantities=quantities,
                latency_ms=round(latency_ms, 2),
                metadata={
                    "source": "macrostrat.org",
                    "columns_found": len(columns.get("success", {}).get("data", [])),
                    "units_found": len(units.get("success", {}).get("data", [])),
                    "license": "CC-BY-4.0",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as exc:
            logger.error(f"Macrostrat API request failed: {exc}")
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=f"Macrostrat API failed: {exc}"
            )

    async def _query_api(self, endpoint: str, location: CoordinatePoint) -> dict[str, Any]:
        """Query stratigraphic columns at location."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/{endpoint}",
                params={
                    "lat": location.latitude,
                    "lng": location.longitude,
                    "format": "geojson" if endpoint == "columns" else "json"
                }
            )
            resp.raise_for_status()
            return resp.json()

    def _parse_to_quantities(
        self,
        columns: dict[str, Any],
        units: dict[str, Any],
        location: CoordinatePoint
    ) -> list[GeoQuantity]:
        """Convert Macrostrat data to GeoQuantity objects."""
        quantities = []
        now = datetime.now(timezone.utc)

        # Parse units
        for unit in units.get("success", {}).get("data", []):
            # Age bounds (Ma)
            t_age = unit.get("t_age")  # Top age
            b_age = unit.get("b_age")  # Bottom age
            unit_id = unit.get("unit_id", "unknown")

            if t_age is not None:
                quantities.append(GeoQuantity(
                    value=float(t_age),
                    units="Ma",
                    quantity_type="stratigraphic_age_top",
                    coordinates=location,
                    timestamp=now,
                    uncertainty=abs(float(b_age) - float(t_age)) / 2 if b_age else 5.0,
                    provenance=ProvenanceRecord(
                        source_id=f"macrostrat-unit-{unit_id}",
                        source_type="literature",
                        timestamp=now,
                        confidence=0.85,
                        citation="Macrostrat API (units)"
                    )
                ))

            # Lithology (categorical)
            lith = unit.get("lith", "")
            if lith:
                quantities.append(GeoQuantity(
                    value=1.0,  # Presence indicator
                    units="presence",
                    quantity_type=f"lithology_{lith.lower().replace(' ', '_')}",
                    coordinates=location,
                    timestamp=now,
                    uncertainty=0.15,
                    provenance=ProvenanceRecord(
                        source_id=f"macrostrat-lith-{unit_id}",
                        source_type="literature",
                        timestamp=now,
                        confidence=0.80,
                        citation=f"Macrostrat Lithology Unit: {unit_id}"
                    )
                ))

        return quantities

    def health_check(self) -> bool:
        """Ping the Macrostrat API status."""
        # Simple placeholder for connectivity check
        return True

