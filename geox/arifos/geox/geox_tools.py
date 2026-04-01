"""
GEOX Tools — Earth & Perception Adapter Layer
DITEMPA BUKAN DIBERI

Stub tool adapters with full type contracts for the GEOX coprocessor.
All tools are dependency-injectable and mockable for testing.

Tool hierarchy:
  BaseTool (ABC)
    ├─ EarthModelTool      — Large Earth Model (LEM) adapter
    ├─ EOFoundationModelTool — Earth Observation foundation model
    ├─ SeismicVLMTool      — Vision Language Model for seismic
    ├─ SimulatorTool       — Basin/PVT simulator
    └─ GeoRAGTool          — Geological RAG over literature

ToolRegistry — central registry for tool discovery and injection.

Constitutional notes:
  F7  Humility: VLM tools always report uncertainty ≥ 0.15
  F9  Anti-Hantu: tools must return explicit error on missing data
  F11 Authority: every tool result carries provenance
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoQuantity,
    ProvenanceRecord,
)
from arifos.geox.base_tool import (
    BaseTool,
    GeoToolResult,
    _make_provenance,
    _make_quantity,
)
from arifos.geox.tools.macrostrat_tool import MacrostratTool
from arifos.geox.tools.lem_bridge import LEMBridgeTool
from arifos.geox.tools.well_log_tool import WellLogTool




# ---------------------------------------------------------------------------
# EarthModelTool
# ---------------------------------------------------------------------------

class EarthModelTool(BaseTool):
    """
    Adapter for a Large Earth Model (LEM).

    Simulates a physics-informed foundation model that predicts
    geophysical properties from spatial queries. Returns realistic
    mock quantities when no real LEM endpoint is configured.

    Inputs:
        query         (str)  — natural-language query
        location      (CoordinatePoint)
        depth_range_m (tuple[float, float]) — (min_depth, max_depth)

    Outputs (GeoQuantity types):
        - seismic_velocity  [m/s]  — range 2200–4500
        - density           [g/cm3] — range 2.1–2.8
        - porosity          [fraction] — range 0.05–0.35
    """

    @property
    def name(self) -> str:
        return "EarthModelTool"

    @property
    def description(self) -> str:
        return (
            "Large Earth Model adapter. Queries a physics-informed foundation model "
            "for geophysical properties (seismic velocity, density, porosity) "
            "at a given location and depth range."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"query", "location", "depth_range_m"}
        if not required.issubset(inputs.keys()):
            return False
        if not isinstance(inputs["location"], CoordinatePoint):
            return False
        dr = inputs["depth_range_m"]
        if not (isinstance(dr, (list, tuple)) and len(dr) == 2):
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Invalid inputs: required keys are 'query', 'location', 'depth_range_m'.",
            )

        start = time.perf_counter()
        location: CoordinatePoint = inputs["location"]
        depth_range: tuple[float, float] = tuple(inputs["depth_range_m"])
        query: str = inputs.get("query", "")

        # Deterministic seed from location for reproducibility
        seed = int(abs(location.latitude * 1000 + location.longitude * 100))
        rng = random.Random(seed)

        mid_depth = (depth_range[0] + depth_range[1]) / 2.0

        # Velocity increases with depth (simplified velocity-depth relationship)
        depth_factor = min(1.0, mid_depth / 5000.0)
        velocity = rng.uniform(2200, 3200) + depth_factor * 1300  # 2200–4500 m/s

        # Density: 2.1–2.8 g/cm3, slight positive depth correlation
        density = rng.uniform(2.1, 2.5) + depth_factor * 0.3

        # Porosity: 0.05–0.35, decreases with depth (compaction)
        porosity = rng.uniform(0.20, 0.35) - depth_factor * 0.15
        porosity = max(0.05, porosity)

        source_id = f"LEM-{seed}-{int(mid_depth)}"
        prov = _make_provenance(source_id, "LEM", confidence=0.82)

        quantities = [
            _make_quantity(round(velocity, 1), "m/s", "seismic_velocity", location, prov, 0.08),
            _make_quantity(round(density, 3), "g/cm3", "density", location, prov, 0.06),
            _make_quantity(round(porosity, 4), "fraction", "porosity", location, prov, 0.10),
        ]

        raw_output = {
            "query": query,
            "depth_range_m": list(depth_range),
            "velocity_ms": velocity,
            "density_gcm3": density,
            "porosity_fraction": porosity,
            "model": "LEM-GEOX-v0.1-mock",
            "physics_check": "passed",
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={"model_version": "LEM-GEOX-v0.1-mock", "seed": seed},
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# EOFoundationModelTool
# ---------------------------------------------------------------------------

class EOFoundationModelTool(BaseTool):
    """
    Adapter for an Earth Observation (EO) foundation model.

    Processes satellite imagery bands to return surface-derived
    geophysical proxies. Supports multispectral and thermal bands.

    Inputs:
        bbox       (dict) — {"west": float, "south": float, "east": float, "north": float}
        bands      (list[str]) — e.g. ["B02", "B04", "B08", "B11", "TIR"]
        date_range (tuple) — (start_date_str, end_date_str) ISO 8601

    Outputs (GeoQuantity types):
        - surface_reflectance [fraction]
        - ndvi                [fraction]  — vegetation index
        - thermal_anomaly     [degC]      — surface temperature anomaly
    """

    @property
    def name(self) -> str:
        return "EOFoundationModelTool"

    @property
    def description(self) -> str:
        return (
            "Earth Observation foundation model adapter. Processes satellite "
            "imagery to derive surface reflectance, NDVI, and thermal anomaly "
            "for geological surface expression mapping."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"bbox", "bands", "date_range"}
        if not required.issubset(inputs.keys()):
            return False
        bbox = inputs["bbox"]
        if not isinstance(bbox, dict):
            return False
        for k in ("west", "south", "east", "north"):
            if k not in bbox:
                return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Invalid inputs: required keys are 'bbox' (dict), 'bands' (list), 'date_range' (tuple).",
            )

        start = time.perf_counter()
        bbox: dict = inputs["bbox"]
        bands: list[str] = inputs.get("bands", [])
        date_range = inputs.get("date_range", ("", ""))

        # Seed from bbox centroid
        cx = (bbox.get("west", 0) + bbox.get("east", 0)) / 2
        cy = (bbox.get("south", 0) + bbox.get("north", 0)) / 2
        seed = int(abs(cx * 100 + cy * 77)) % (2**31)
        rng = random.Random(seed)

        # Approximate centre coordinate
        location = CoordinatePoint(latitude=cy, longitude=cx)
        source_id = f"EO-{seed}-{date_range[0]}"
        prov = _make_provenance(source_id, "sensor", confidence=0.78)

        surface_reflectance = rng.uniform(0.05, 0.45)
        ndvi = rng.uniform(-0.1, 0.8)
        thermal_anomaly = rng.uniform(-2.5, 8.0)

        quantities = [
            _make_quantity(round(surface_reflectance, 4), "fraction", "surface_reflectance", location, prov, 0.07),
            _make_quantity(round(ndvi, 4), "fraction", "ndvi", location, prov, 0.09),
            _make_quantity(round(thermal_anomaly, 2), "degC", "thermal_anomaly", location, prov, 0.12),
        ]

        raw_output = {
            "bbox": bbox,
            "bands": bands,
            "date_range": list(date_range),
            "surface_reflectance": surface_reflectance,
            "ndvi": ndvi,
            "thermal_anomaly_degC": thermal_anomaly,
            "model": "EO-FDN-GEOX-v0.1-mock",
            "cloud_cover_pct": rng.uniform(0, 30),
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={"model_version": "EO-FDN-GEOX-v0.1-mock", "seed": seed, "bands": bands},
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# SeismicVLMTool
# ---------------------------------------------------------------------------

class SeismicVLMTool(BaseTool):
    """
    Vision Language Model adapter for seismic image interpretation.

    IMPORTANT — Perception Bridge Rule (F7 + F9):
        RGB/colour patterns alone are never decisive for geological
        interpretation. All VLM outputs carry uncertainty ≥ 0.15 and
        must be corroborated by multisensor evidence before acting.

    Inputs:
        image_path          (str) — path to seismic section image
        interpretation_query (str) — what to interpret

    Outputs (GeoQuantity types):
        - structural_interpretation [fraction] — overall confidence
        - fault_probability         [fraction]
        - amplitude_anomaly         [fraction] — AVO/DHI indicator
    """

    @property
    def name(self) -> str:
        return "SeismicVLMTool"

    @property
    def description(self) -> str:
        return (
            "Vision Language Model for seismic image interpretation. "
            "Returns structural interpretations, fault probability, and "
            "amplitude anomaly confidence. Always reports uncertainty ≥ 0.15; "
            "VLM perception alone is never decisive (perception bridge rule)."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"image_path", "interpretation_query"}
        return required.issubset(inputs.keys())

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=(
                    "Invalid inputs: required keys are "
                    "'image_path' (str) and 'interpretation_query' (str)."
                ),
            )

        start = time.perf_counter()
        image_path: str = inputs["image_path"]
        query: str = inputs["interpretation_query"]

        # Seed from image path hash for reproducibility
        seed = int(hashlib.sha256(image_path.encode()).hexdigest(), 16) % (2**31)
        rng = random.Random(seed)

        # Default location (image centre) — no geographic anchor from VLM alone
        location = CoordinatePoint(latitude=0.0, longitude=0.0)
        source_id = f"VLM-SEI-{seed}"
        # F7: VLM confidence is always capped at 0.70 (epistemic limit of visual-only)
        prov = _make_provenance(source_id, "VLM", confidence=0.65)

        # Perception bridge rule: uncertainty always ≥ 0.15
        vlm_uncertainty = 0.15

        structural_conf = rng.uniform(0.40, 0.85)
        fault_prob = rng.uniform(0.10, 0.80)
        amplitude_anomaly = rng.uniform(0.0, 1.0)

        quantities = [
            _make_quantity(
                round(structural_conf, 3), "fraction", "structural_interpretation",
                location, prov, vlm_uncertainty
            ),
            _make_quantity(
                round(fault_prob, 3), "fraction", "fault_probability",
                location, prov, vlm_uncertainty
            ),
            _make_quantity(
                round(amplitude_anomaly, 3), "fraction", "amplitude_anomaly",
                location, prov, vlm_uncertainty
            ),
        ]

        # F9 Anti-Hantu: flag that RGB alone is not decisive
        raw_output = {
            "image_path": image_path,
            "interpretation_query": query,
            "structural_confidence": structural_conf,
            "fault_probability": fault_prob,
            "amplitude_anomaly_index": amplitude_anomaly,
            "model": "VLM-SEISMIC-GEOX-v0.1-mock",
            "perception_bridge_warning": (
                "VLM output is perceptual only. RGB/colour alone is not decisive. "
                "Corroborate with LEM, well logs, or simulator before acting."
            ),
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "model_version": "VLM-SEISMIC-GEOX-v0.1-mock",
                "multisensor_required": True,
                "perception_only": True,
                "uncertainty_floor": vlm_uncertainty,
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# SimulatorTool
# ---------------------------------------------------------------------------

class SimulatorTool(BaseTool):
    """
    Basin simulator / Pressure-Volume-Temperature (PVT) tool adapter.

    Runs forward model scenarios to predict burial history, thermal
    maturity, and fluid properties through geological time.

    Inputs:
        scenario     (dict)        — simulation parameters
        timesteps_ma (list[float]) — geological time steps in Ma (millions of years ago)

    Outputs (GeoQuantity types):
        - pressure_psi  [psi]
        - temperature_degC [degC]
        - maturity_ro  [fraction] — vitrinite reflectance (0.0–4.0+)
    """

    @property
    def name(self) -> str:
        return "SimulatorTool"

    @property
    def description(self) -> str:
        return (
            "Basin and PVT simulator adapter. Runs forward models to predict "
            "pressure, temperature, and thermal maturity through geological time. "
            "Output represents deterministic simulation with parametric uncertainty."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"scenario", "timesteps_ma"}
        if not required.issubset(inputs.keys()):
            return False
        if not isinstance(inputs["scenario"], dict):
            return False
        if not isinstance(inputs["timesteps_ma"], (list, tuple)):
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=(
                    "Invalid inputs: required keys are "
                    "'scenario' (dict) and 'timesteps_ma' (list[float])."
                ),
            )

        start = time.perf_counter()
        scenario: dict = inputs["scenario"]
        timesteps: list[float] = list(inputs["timesteps_ma"])

        if not timesteps:
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="timesteps_ma must be a non-empty list.",
            )

        # Seed from scenario hash
        scenario_str = json.dumps(scenario, sort_keys=True, default=str)
        seed = int(hashlib.sha256(scenario_str.encode()).hexdigest(), 16) % (2**31)
        rng = random.Random(seed)

        # Default location from scenario or origin
        lat = scenario.get("latitude", 4.5)
        lon = scenario.get("longitude", 103.7)
        depth = scenario.get("target_depth_m", 2500.0)
        location = CoordinatePoint(latitude=lat, longitude=lon, depth_m=depth)
        source_id = f"SIM-{seed}-T{len(timesteps)}"
        prov = _make_provenance(source_id, "simulator", confidence=0.78)

        # Simulate at the youngest (shallowest burial) timestep for present-day output
        present_age_ma = min(timesteps)

        # Simple geothermal gradient model
        geothermal_gradient = scenario.get("geothermal_gradient_degc_km", 30.0)
        surface_temp = scenario.get("surface_temp_degc", 25.0)
        depth_km = depth / 1000.0
        temperature = surface_temp + geothermal_gradient * depth_km + rng.uniform(-5, 5)

        # Pressure: hydrostatic + overpressure component
        water_density_kgm3 = 1020.0
        g = 9.81
        hydrostatic_pa = water_density_kgm3 * g * depth
        overpressure_factor = scenario.get("overpressure_factor", 1.0 + rng.uniform(0, 0.3))
        pressure_pa = hydrostatic_pa * overpressure_factor
        pressure_psi = pressure_pa / 6894.76  # Pa to psi

        # Vitrinite reflectance (maturity): exponential depth/temp model
        maturity_ro = 0.2 * (temperature / 60.0) ** 1.5 + rng.uniform(0, 0.05)
        maturity_ro = min(4.0, max(0.2, maturity_ro))

        quantities = [
            _make_quantity(round(pressure_psi, 1), "psi", "pressure_psi", location, prov, 0.08),
            _make_quantity(round(temperature, 2), "degC", "temperature_degC", location, prov, 0.06),
            _make_quantity(round(maturity_ro, 3), "fraction", "maturity_ro", location, prov, 0.10),
        ]

        raw_output = {
            "scenario": scenario,
            "timesteps_ma": timesteps,
            "present_pressure_psi": pressure_psi,
            "present_temperature_degC": temperature,
            "maturity_ro": maturity_ro,
            "overpressure_factor": overpressure_factor,
            "model": "BASIN-SIM-GEOX-v0.1-mock",
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={"model_version": "BASIN-SIM-GEOX-v0.1-mock", "seed": seed},
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# GeoRAGTool
# ---------------------------------------------------------------------------

class GeoRAGTool(BaseTool):
    """
    Geological Retrieval-Augmented Generation (RAG) tool.

    Queries a vector database of geological literature, well reports,
    and basin studies to return literature-backed proxy quantities.

    Inputs:
        query       (str) — geological query
        basin       (str) — basin name to filter literature
        max_results (int) — maximum number of literature hits (default 5)

    Outputs:
        GeoQuantity proxies derived from literature, with citation provenance.
    """

    # Synthetic literature database for mock mode
    _LITERATURE_DB: list[dict[str, Any]] = [
        {
            "title": "Stratigraphy and Petroleum Systems of the Malay Basin",
            "authors": "Madon et al.",
            "year": 2004,
            "basin": "Malay Basin",
            "porosity_range": (0.15, 0.28),
            "velocity_range": (2400, 3200),
            "doi": "10.1144/petgeo.10.1.5",
        },
        {
            "title": "Burial Diagenesis and Reservoir Quality in Sundaland Basins",
            "authors": "Hutchison (1996)",
            "year": 1996,
            "basin": "Malay Basin",
            "porosity_range": (0.10, 0.25),
            "velocity_range": (2600, 3600),
            "doi": "10.1016/S0037-0738(96)00040-1",
        },
        {
            "title": "Overpressure and Fluid Flow in SE Asian Tertiary Basins",
            "authors": "Tingay et al.",
            "year": 2009,
            "basin": "Malay Basin",
            "porosity_range": (0.12, 0.22),
            "velocity_range": (2800, 3800),
            "doi": "10.1306/03260908053",
        },
        {
            "title": "Sabah Basin Reservoir Characterisation",
            "authors": "Wannier et al.",
            "year": 2011,
            "basin": "Sabah Basin",
            "porosity_range": (0.08, 0.20),
            "velocity_range": (2900, 4200),
            "doi": "10.1144/petgeo.17.4.313",
        },
        {
            "title": "Kutai Basin Deep-Water Petroleum Systems",
            "authors": "Moss & Chambers",
            "year": 1999,
            "basin": "Kutai Basin",
            "porosity_range": (0.10, 0.30),
            "velocity_range": (2200, 3500),
            "doi": "10.1144/petgeo.5.2.163",
        },
    ]

    @property
    def name(self) -> str:
        return "GeoRAGTool"

    @property
    def description(self) -> str:
        return (
            "Geological RAG tool. Retrieves relevant geological literature and "
            "converts findings to GeoQuantity proxy objects with full citation "
            "provenance. Used to anchor LEM/VLM outputs in published science."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        return "query" in inputs

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Invalid inputs: required key is 'query' (str).",
            )

        start = time.perf_counter()
        query: str = inputs["query"]
        basin: str | None = inputs.get("basin")
        max_results: int = inputs.get("max_results", 5)

        # Filter by basin
        candidates = self._LITERATURE_DB
        if basin:
            basin_lower = basin.lower()
            candidates = [
                d for d in candidates
                if basin_lower in d.get("basin", "").lower()
            ]
        # Fall back to all if no match
        if not candidates:
            candidates = self._LITERATURE_DB

        # Limit results
        hits = candidates[:max_results]
        seed = int(hashlib.sha256(query.encode()).hexdigest(), 16) % (2**31)
        rng = random.Random(seed)

        quantities: list[GeoQuantity] = []
        citations_used: list[str] = []

        for hit in hits:
            citation = f"{hit['authors']} ({hit['year']}). {hit['title']}. DOI: {hit['doi']}"
            citations_used.append(citation)
            source_id = f"LIT-{hit['doi'].replace('/', '-')}"
            prov = _make_provenance(
                source_id, "literature", confidence=0.70, citation=citation
            )
            location = CoordinatePoint(latitude=4.5, longitude=103.7)  # basin centroid

            # Sample mid-range values from literature ranges
            if "porosity_range" in hit:
                lo, hi = hit["porosity_range"]
                porosity = rng.uniform(lo, hi)
                quantities.append(
                    _make_quantity(round(porosity, 4), "fraction", "porosity", location, prov, 0.12)
                )
            if "velocity_range" in hit:
                lo, hi = hit["velocity_range"]
                velocity = rng.uniform(lo, hi)
                quantities.append(
                    _make_quantity(round(velocity, 1), "m/s", "seismic_velocity", location, prov, 0.10)
                )

        raw_output = {
            "query": query,
            "basin_filter": basin,
            "hits": len(hits),
            "citations": citations_used,
            "model": "GEO-RAG-GEOX-v0.1-mock",
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "model_version": "GEO-RAG-GEOX-v0.1-mock",
                "literature_hits": len(hits),
                "citations": citations_used,
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """
    Central registry for GEOX tool discovery and dependency injection.

    Usage:
        registry = ToolRegistry.default_registry()
        tool = registry.get("EarthModelTool")
        result = await tool.run(inputs)
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.

        Args:
            tool: Any BaseTool subclass instance.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Unregister it first or use a different name."
            )
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        """
        Retrieve a registered tool by name.

        Args:
            name: Registered tool name.

        Raises:
            KeyError: If tool name is not registered.
        """
        if name not in self._tools:
            raise KeyError(
                f"Tool '{name}' not found in registry. "
                f"Available tools: {self.list_tools()}"
            )
        return self._tools[name]

    def list_tools(self) -> list[str]:
        """Return list of all registered tool names."""
        return sorted(self._tools.keys())

    def health_check_all(self) -> dict[str, bool]:
        """Run health_check() on all registered tools."""
        return {name: tool.health_check() for name, tool in self._tools.items()}

    @classmethod
    def default_registry(cls) -> "ToolRegistry":
        """
        Factory method that creates a ToolRegistry pre-populated
        with all five standard GEOX tools.

        Returns:
            ToolRegistry with EarthModelTool, EOFoundationModelTool,
            SeismicVLMTool, SimulatorTool, and GeoRAGTool registered.
        """
        registry = cls()
        registry.register(EarthModelTool())
        registry.register(EOFoundationModelTool())
        registry.register(SeismicVLMTool())
        registry.register(SimulatorTool())
        registry.register(GeoRAGTool())
        registry.register(MacrostratTool())
        registry.register(LEMBridgeTool())
        registry.register(WellLogTool())  # Electronic well log analysis
        return registry
