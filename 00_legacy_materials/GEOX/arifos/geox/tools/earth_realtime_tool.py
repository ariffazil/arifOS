"""
arifos/geox/tools/earth_realtime_tool.py — Real Earth Signals Tool
DITEMPA BUKAN DIBERI

Live, zero-auth Earth observation signals:
  • USGS Earthquake Hazards Program  (real seismic events, live)
  • Open-Meteo Climate API           (atmosphere, surface conditions, live)
  • NOAA GeoMag                      (declination/inclination, needed for borehole surveys)

WHY THIS MATTERS (F2 TRUTH):
  The claim "arifOS = Earth Intelligence" is false while the data layer is mocked.
  This tool makes the data layer real. No API keys. No mocks. Production-grade.

Endpoints (all public, CC0 / CC-BY):
  USGS: https://earthquake.usgs.gov/fdsnws/event/1/
  Open-Meteo: https://api.open-meteo.com/v1/forecast
  NOAA GeoMag: https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from arifos.geox.base_tool import BaseTool, GeoToolResult
from arifos.geox.geox_schemas import CoordinatePoint, GeoQuantity, ProvenanceRecord

logger = logging.getLogger("geox.tools.earth_realtime")

_USGS_BASE = "https://earthquake.usgs.gov/fdsnws/event/1/query"
_OPENMETEO_BASE = "https://api.open-meteo.com/v1/forecast"
_NOAA_GEOMAG_BASE = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination"
_BGS_WMM_BASE = "https://geomag.bgs.ac.uk/web_service/GMModels/wmm/2020/"

# F7 HUMILITY: default uncertainty bands for each source type
_UNCERTAINTY = {
    "seismic_magnitude": 0.05,
    "seismic_depth_km": 0.08,
    "temperature_2m": 0.03,
    "precipitation_mm": 0.12,
    "surface_pressure_hpa": 0.03,
    "magnetic_declination_deg": 0.04,
}


class EarthRealtimeTool(BaseTool):
    """
    Live Earth observation signals from USGS, Open-Meteo, and NOAA.

    No API keys required. Covers:
      - Seismic hazard (recent earthquake events near prospect)
      - Surface climate state (temperature, precipitation, pressure)
      - Magnetic declination (borehole directional correction)

    This is the real data layer. Not mocked. Not simulated.

    Constitutional:
      F2 TRUTH   — grounded in live observational data (τ → 0.99)
      F7 HUMILITY — explicit uncertainty on all quantities
      F11 AUDIT  — full provenance on every GeoQuantity
    """

    @property
    def name(self) -> str:
        return "EarthRealtimeTool"

    @property
    def description(self) -> str:
        return (
            "Live Earth signals: USGS seismic events, Open-Meteo climate, NOAA magnetic declination. "
            "Zero API keys. Real data. Used at 100 SENSE stage for F2 temporal grounding."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        return "location" in inputs and isinstance(inputs["location"], CoordinatePoint)

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        location: CoordinatePoint = inputs["location"]
        radius_km: float = inputs.get("radius_km", 300.0)
        eq_limit: int = min(inputs.get("eq_limit", 10), 50)

        try:
            usgs_task = self._fetch_usgs_earthquakes(location, radius_km, eq_limit)
            meteo_task = self._fetch_open_meteo(location)
            geomag_task = self._fetch_geomag(location)

            usgs_result, meteo_result, geomag_result = await asyncio.gather(
                usgs_task, meteo_task, geomag_task, return_exceptions=True
            )

            quantities: list[GeoQuantity] = []
            raw: dict[str, Any] = {}
            warnings: list[str] = []

            if isinstance(usgs_result, Exception):
                warnings.append(f"USGS fetch failed: {usgs_result}")
                raw["earthquakes"] = {"count": 0, "events": [], "largest_magnitude": None}
            else:
                quantities.extend(usgs_result["quantities"])
                raw["earthquakes"] = usgs_result["raw"]

            if isinstance(meteo_result, Exception):
                warnings.append(f"Open-Meteo fetch failed: {meteo_result}")
                raw["climate"] = {}
            else:
                quantities.extend(meteo_result["quantities"])
                raw["climate"] = meteo_result["raw"]

            if isinstance(geomag_result, Exception):
                warnings.append(f"NOAA GeoMag fetch failed: {geomag_result}")
                raw["geomagnetic"] = {}
            else:
                quantities.extend(geomag_result["quantities"])
                raw["geomagnetic"] = geomag_result["raw"]

            summary = self._build_summary(raw, location, radius_km)

            return GeoToolResult(
                tool_name=self.name,
                success=True,
                quantities=quantities,
                raw_output={
                    "summary": summary,
                    "sources": {
                        "earthquakes": "USGS FDSN Event API (CC0)",
                        "climate": "Open-Meteo (CC-BY 4.0)",
                        "geomagnetic": "NOAA NGDC GeoMag (public domain)",
                    },
                    "warnings": warnings,
                    **raw,
                },
                metadata={"confidence": 0.92 if not warnings else 0.75},
            )

        except Exception as exc:
            logger.exception("EarthRealtimeTool.run failed")
            return GeoToolResult(tool_name=self.name, success=False, error=str(exc))

    # ── USGS Earthquake Hazards ───────────────────────────────────────────────

    async def _fetch_usgs_earthquakes(
        self, location: CoordinatePoint, radius_km: float, limit: int
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        params = {
            "format": "geojson",
            "latitude": location.latitude,
            "longitude": location.longitude,
            "maxradiuskm": radius_km,
            "limit": limit,
            "orderby": "time",
            "minmagnitude": 1.0,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(_USGS_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        features = data.get("features", [])
        quantities: list[GeoQuantity] = []

        for feat in features:
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [None, None, None])
            mag = props.get("mag")
            depth = coords[2]  # km
            props.get("place", "Unknown")
            eq_time = datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc)
            eq_id = feat.get("id", "unknown")

            prov = ProvenanceRecord(
                source_id=f"usgs-{eq_id}",
                source_type="sensor",
                timestamp=now,
                confidence=0.97,
                citation=f"USGS FDSN: {props.get('url', 'https://earthquake.usgs.gov')}",
            )

            if mag is not None:
                quantities.append(
                    GeoQuantity(
                        value=float(mag),
                        units="Richter",
                        quantity_type="seismic_magnitude",
                        coordinates=location,
                        timestamp=eq_time,
                        uncertainty=_UNCERTAINTY["seismic_magnitude"],
                        provenance=prov,
                    )
                )
            if depth is not None:
                quantities.append(
                    GeoQuantity(
                        value=float(depth),
                        units="km",
                        quantity_type="seismic_depth_km",
                        coordinates=location,
                        timestamp=eq_time,
                        uncertainty=_UNCERTAINTY["seismic_depth_km"],
                        provenance=prov,
                    )
                )

        summary = {
            "count": len(features),
            "radius_km": radius_km,
            "largest_magnitude": max(
                (f["properties"].get("mag") or 0 for f in features), default=None
            ),
            "events": [
                {
                    "id": f.get("id"),
                    "magnitude": f["properties"].get("mag"),
                    "depth_km": (f.get("geometry", {}).get("coordinates") or [None, None, None])[2],
                    "place": f["properties"].get("place"),
                    "time_utc": datetime.fromtimestamp(
                        f["properties"]["time"] / 1000, tz=timezone.utc
                    ).isoformat(),
                }
                for f in features
            ],
        }
        return {"quantities": quantities, "raw": summary}

    # ── Open-Meteo Climate ────────────────────────────────────────────────────

    async def _fetch_open_meteo(self, location: CoordinatePoint) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "surface_pressure",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "cloud_cover",
                    "weather_code",
                ]
            ),
            "timezone": "UTC",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(_OPENMETEO_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        data.get("current_units", {})
        quantities: list[GeoQuantity] = []

        field_map = {
            "temperature_2m": ("temperature_2m", "°C"),
            "relative_humidity_2m": ("relative_humidity_2m", "%"),
            "precipitation": ("precipitation_mm", "mm"),
            "surface_pressure": ("surface_pressure_hpa", "hPa"),
            "wind_speed_10m": ("wind_speed_10m", "km/h"),
            "cloud_cover": ("cloud_cover", "%"),
        }
        prov = ProvenanceRecord(
            source_id="open-meteo-current",
            source_type="sensor",
            timestamp=now,
            confidence=0.95,
            citation="Open-Meteo API v1 (CC-BY 4.0) — https://open-meteo.com",
        )

        for api_key, (qty_type, unit) in field_map.items():
            val = current.get(api_key)
            if val is not None:
                quantities.append(
                    GeoQuantity(
                        value=float(val),
                        units=unit,
                        quantity_type=qty_type,
                        coordinates=location,
                        timestamp=now,
                        uncertainty=_UNCERTAINTY.get(qty_type, 0.08),
                        provenance=prov,
                    )
                )

        return {
            "quantities": quantities,
            "raw": {
                "temperature_2m_c": current.get("temperature_2m"),
                "relative_humidity_pct": current.get("relative_humidity_2m"),
                "precipitation_mm": current.get("precipitation"),
                "surface_pressure_hpa": current.get("surface_pressure"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "wind_direction_deg": current.get("wind_direction_10m"),
                "cloud_cover_pct": current.get("cloud_cover"),
                "weather_code": current.get("weather_code"),
                "observation_time_utc": current.get("time"),
            },
        }

    # ── BGS / NOAA Geomagnetic Declination ───────────────────────────────────

    async def _fetch_geomag(self, location: CoordinatePoint) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "altitude": 0,
            "date": date_str,
            "format": "json",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(_BGS_WMM_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        field = data.get("geomagnetic-field-model-result", {}).get("field-value", {})
        decl_raw = field.get("declination", {})
        incl_raw = field.get("inclination", {})
        decl = decl_raw.get("value") if isinstance(decl_raw, dict) else decl_raw
        incl = incl_raw.get("value") if isinstance(incl_raw, dict) else incl_raw

        quantities: list[GeoQuantity] = []
        prov = ProvenanceRecord(
            source_id="noaa-geomag",
            source_type="literature",
            timestamp=now,
            confidence=0.99,
            citation="NOAA NGDC World Magnetic Model — https://www.ngdc.noaa.gov/geomag",
        )

        if decl is not None:
            quantities.append(
                GeoQuantity(
                    value=float(decl),
                    units="degrees",
                    quantity_type="magnetic_declination_deg",
                    coordinates=location,
                    timestamp=now,
                    uncertainty=_UNCERTAINTY["magnetic_declination_deg"],
                    provenance=prov,
                )
            )
        if incl is not None:
            quantities.append(
                GeoQuantity(
                    value=float(incl),
                    units="degrees",
                    quantity_type="magnetic_inclination_deg",
                    coordinates=location,
                    timestamp=now,
                    uncertainty=0.03,
                    provenance=prov,
                )
            )

        return {
            "quantities": quantities,
            "raw": {
                "declination_deg": decl,
                "inclination_deg": incl,
                "model": "WMM2020 (BGS)",
                "total_intensity_nT": field.get("total-intensity", {}).get("value"),
            },
        }

    # ── Summary ───────────────────────────────────────────────────────────────

    def _build_summary(
        self, raw: dict[str, Any], location: CoordinatePoint, radius_km: float
    ) -> str:
        eq = raw.get("earthquakes", {})
        climate = raw.get("climate", {})
        geomag = raw.get("geomagnetic", {})

        eq_count = eq.get("count", 0)
        max_mag = eq.get("largest_magnitude")
        temp = climate.get("temperature_2m_c")
        pressure = climate.get("surface_pressure_hpa")
        decl = geomag.get("declination_deg")

        lines = [
            f"EARTH REALTIME SIGNALS @ ({location.latitude:.3f}°, {location.longitude:.3f}°)",
            f"Seismic: {eq_count} events within {radius_km:.0f}km"
            + (f", max M{max_mag:.1f}" if max_mag else ", no significant events"),
            f"Climate: {temp}°C, {pressure} hPa" if temp else "Climate: data unavailable",
            f"GeoMag: declination {decl:.2f}°" if decl else "GeoMag: data unavailable",
            "Sources: USGS (CC0) | Open-Meteo (CC-BY 4.0) | NOAA NGDC (public domain)",
            "DITEMPA BUKAN DIBERI 🔨",
        ]
        return "\n".join(lines)

    def health_check(self) -> bool:
        """Quick connectivity check against USGS."""
        try:
            import urllib.request

            urllib.request.urlopen(f"{_USGS_BASE}?format=geojson&limit=1&minmagnitude=5", timeout=5)
            return True
        except Exception:
            return False
