"""
GEOX Mock EarthNet Tool — Malay Basin Mock LEM
DITEMPA BUKAN DIBERI

Full mock implementation of EarthModelTool (Large Earth Model adapter)
returning realistic but entirely fictional geophysical data for the
Malay Basin range.

Data ranges (Malay Basin analogues, no proprietary data):
  Seismic P-wave velocity: 2200–3800 m/s
  Porosity:                0.08–0.28 (fraction)
  Bulk density:            2.10–2.65 g/cm³
  S-wave velocity:         1100–2200 m/s
  Acoustic impedance:      4.6–9.9 MRayl
  Net-to-gross ratio:      0.25–0.85

Reproducibility: seed = hash(lat, lon, depth) → all outputs deterministic
given the same spatial input.

All values are scientifically plausible for Tertiary clastic reservoirs
in SE Asian back-arc basin settings. References (open literature):
  - Madon et al. (2004) Petroleum Geoscience 10(1):5–29
  - Hutchison (1996) Geology of North-West Borneo
  - Tingay et al. (2009) AAPG Bulletin 93(4):549–590
"""

from __future__ import annotations

import hashlib
import random
import time
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoQuantity,
    ProvenanceRecord,
)
from arifos.geox.geox_tools import BaseTool, GeoToolResult

# ---------------------------------------------------------------------------
# Malay Basin geophysical parameter ranges
# (open-literature values, no proprietary data)
# ---------------------------------------------------------------------------

_MALAY_BASIN_RANGES = {
    # Velocity (m/s): shallow sands 2200–2800, deeper carbonates 3200–3800
    "vp_shallow_ms":   (2200.0, 2800.0),  # Pliocene–Miocene clastics, <1500 m
    "vp_mid_ms":       (2600.0, 3200.0),  # Early Miocene, 1500–3000 m
    "vp_deep_ms":      (3000.0, 3800.0),  # Oligocene and deeper, >3000 m

    # S-wave velocity (m/s): typically ~0.55–0.60 × Vp for wet sandstones
    "vs_ratio": (0.55, 0.60),

    # Porosity (fraction): decreases with depth
    "phi_shallow": (0.20, 0.28),
    "phi_mid":     (0.13, 0.22),
    "phi_deep":    (0.08, 0.16),

    # Bulk density (g/cm3): increases with depth / compaction
    "rho_shallow": (2.10, 2.35),
    "rho_mid":     (2.25, 2.50),
    "rho_deep":    (2.40, 2.65),

    # Net-to-gross ratio (fraction)
    "ntg":         (0.25, 0.85),

    # Acoustic impedance (MRayl = 10^6 kg/m2/s)
    # AI = Vp * rho; approximate for realism check
    "ai_range":    (4.6, 9.9),

    # Vp/Vs ratio (dimensionless): ~1.7–2.2 for water-saturated sands
    "vpvs_ratio":  (1.72, 2.15),
}

# ---------------------------------------------------------------------------
# Depth zone classifier
# ---------------------------------------------------------------------------

def _depth_zone(depth_m: float) -> str:
    """Classify depth into shallow / mid / deep for parameter selection."""
    if depth_m < 1500.0:
        return "shallow"
    elif depth_m < 3000.0:
        return "mid"
    else:
        return "deep"


# ---------------------------------------------------------------------------
# MockEarthNetTool
# ---------------------------------------------------------------------------

class MockEarthNetTool(BaseTool):
    """
    Mock Large Earth Model (LEM) tool for Malay Basin geophysical properties.

    Returns deterministic, seeded synthetic geophysical quantities that
    are scientifically plausible for Tertiary clastic reservoirs in the
    Malay Basin. No proprietary PETRONAS data.

    Seismic velocities:    2200–3800 m/s (depth-dependent)
    Porosity:              0.08–0.28 fraction (depth-dependent)
    Bulk density:          2.10–2.65 g/cm³ (depth-dependent)
    S-wave velocity:       1100–2200 m/s (derived from Vp)
    Acoustic impedance:    4.6–9.9 MRayl
    Net-to-gross ratio:    0.25–0.85
    Vp/Vs ratio:           1.72–2.15

    All values are seeded from the spatial input for reproducibility.
    """

    @property
    def name(self) -> str:
        return "MockEarthNetTool"

    @property
    def description(self) -> str:
        return (
            "Mock Large Earth Model (LEM) for Malay Basin. Returns realistic "
            "but fictional geophysical quantities including P-wave velocity, "
            "porosity, density, S-wave velocity, acoustic impedance, and "
            "net-to-gross ratio. Seeded for reproducibility."
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
                error="Invalid inputs. Required: 'query', 'location' (CoordinatePoint), 'depth_range_m' (2-tuple).",
            )

        start = time.perf_counter()
        location: CoordinatePoint = inputs["location"]
        depth_range: tuple[float, float] = tuple(inputs["depth_range_m"])
        query: str = inputs.get("query", "geophysical characterisation")

        mid_depth = (depth_range[0] + depth_range[1]) / 2.0
        zone = _depth_zone(mid_depth)

        # Deterministic seed from location + depth
        seed_str = f"{location.latitude:.6f}:{location.longitude:.6f}:{mid_depth:.1f}"
        seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (2**31)
        rng = random.Random(seed)

        # --- P-wave velocity (depth-dependent) ---
        vp_lo, vp_hi = _MALAY_BASIN_RANGES[f"vp_{zone}_ms"]
        vp_ms = rng.uniform(vp_lo, vp_hi)

        # Add a mild depth gradient within the zone
        depth_fraction = (mid_depth - {"shallow": 0, "mid": 1500, "deep": 3000}[zone]) / 1500.0
        vp_ms += depth_fraction * (vp_hi - vp_lo) * 0.2
        vp_ms = max(vp_lo, min(vp_hi, vp_ms))

        # --- S-wave velocity ---
        vs_ratio = rng.uniform(*_MALAY_BASIN_RANGES["vs_ratio"])
        vs_ms = vp_ms * vs_ratio

        # --- Vp/Vs ratio ---
        vpvs = vp_ms / vs_ms

        # --- Porosity (depth-dependent, anti-correlated with velocity) ---
        phi_lo, phi_hi = _MALAY_BASIN_RANGES[f"phi_{zone}"]
        # Velocity-porosity anti-correlation: high Vp → low phi
        vp_norm = (vp_ms - vp_lo) / max(vp_hi - vp_lo, 1.0)  # 0→1
        phi = phi_hi - vp_norm * (phi_hi - phi_lo) * 0.7 + rng.uniform(-0.02, 0.02)
        phi = max(phi_lo, min(phi_hi, phi))

        # --- Bulk density ---
        rho_lo, rho_hi = _MALAY_BASIN_RANGES[f"rho_{zone}"]
        # Density-porosity anti-correlation
        rho = rho_hi - phi * (rho_hi - rho_lo) * 2.0 + rng.uniform(-0.02, 0.02)
        rho = max(rho_lo, min(rho_hi, rho))

        # --- Acoustic impedance (Vp × density) ---
        ai_mrayl = (vp_ms * rho) / 1e6  # g/cm3 × m/s → MRayl
        ai_mrayl = max(4.6, min(9.9, ai_mrayl))

        # --- Net-to-gross ratio ---
        ntg = rng.uniform(*_MALAY_BASIN_RANGES["ntg"])

        # --- Build provenance ---
        source_id = f"MOCK-EARTHNET-{seed % 100000:05d}"
        prov = _build_mock_prov(source_id, "LEM", confidence=0.82)

        # --- Build quantities ---
        def _qty(value: float, units: str, qtype: str, unc: float = 0.08) -> GeoQuantity:
            unc_clamped = max(0.03, min(0.15, unc))
            return GeoQuantity(
                value=round(value, 4),
                units=units,
                quantity_type=qtype,
                coordinates=location,
                timestamp=datetime.now(timezone.utc),
                uncertainty=unc_clamped,
                provenance=prov,
            )

        quantities = [
            _qty(round(vp_ms, 1), "m/s", "seismic_velocity_vp", 0.07),
            _qty(round(vs_ms, 1), "m/s", "seismic_velocity_vs", 0.09),
            _qty(round(phi, 5), "fraction", "porosity", 0.10),
            _qty(round(rho, 4), "g/cm3", "density", 0.06),
            _qty(round(ai_mrayl, 4), "MRayl", "acoustic_impedance", 0.08),
            _qty(round(ntg, 4), "fraction", "net_to_gross", 0.12),
            _qty(round(vpvs, 4), "fraction", "vp_vs_ratio", 0.08),
        ]

        raw_output = {
            "query": query,
            "depth_range_m": list(depth_range),
            "mid_depth_m": mid_depth,
            "depth_zone": zone,
            "vp_ms": vp_ms,
            "vs_ms": vs_ms,
            "vpvs_ratio": vpvs,
            "porosity_fraction": phi,
            "density_gcm3": rho,
            "acoustic_impedance_mrayl": ai_mrayl,
            "net_to_gross": ntg,
            "model": "MockEarthNet-GEOX-v0.1",
            "seed": seed,
            "references": [
                "Madon et al. (2004) Petroleum Geoscience 10(1):5–29",
                "Hutchison (1996) Geology of North-West Borneo",
                "Tingay et al. (2009) AAPG Bulletin 93(4):549–590",
            ],
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "model_version": "MockEarthNet-GEOX-v0.1",
                "seed": seed,
                "depth_zone": zone,
                "basin": "Malay Basin (mock)",
                "data_type": "fictional — no proprietary data",
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_mock_prov(source_id: str, source_type: str, confidence: float) -> ProvenanceRecord:
    return ProvenanceRecord(
        source_id=source_id,
        source_type=source_type,  # type: ignore[arg-type]
        timestamp=datetime.now(timezone.utc),
        confidence=confidence,
        citation=(
            "Mock data — Malay Basin analogues. "
            "Ref: Madon et al. (2004); Hutchison (1996); Tingay et al. (2009)."
        ),
        floor_check={
            "F1_amanah": True,
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,
            "F9_anti_hantu": True,
            "F11_authority": True,
            "F13_sovereign": True,
        },
    )


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import asyncio

    async def _selftest() -> None:
        tool = MockEarthNetTool()
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Health: {tool.health_check()}")

        loc = CoordinatePoint(latitude=4.5, longitude=103.7, depth_m=2500.0)
        inputs = {
            "query": "Malay Basin porosity and velocity at 2500 m",
            "location": loc,
            "depth_range_m": (2000.0, 3000.0),
        }

        result = await tool.run(inputs)
        print(f"\nSuccess: {result.success}")
        print(f"Latency: {result.latency_ms:.2f} ms")
        print(f"Quantities returned: {len(result.quantities)}")
        for qty in result.quantities:
            print(f"  {qty.quantity_type}: {qty.value} {qty.units} (±{qty.uncertainty:.0%})")

        print(f"\nRaw output keys: {list(result.raw_output.keys())}")
        print(f"Seed: {result.metadata['seed']}")

    asyncio.run(_selftest())
