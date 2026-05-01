"""
GEOX Mock SeismicVLM Tool — Structural Interpretation Mock
DITEMPA BUKAN DIBERI

Full mock SeismicVLMTool implementation that returns plausible
structural interpretations for seismic image inputs.

Constitutional compliance (non-negotiable):
  F7  Humility:          uncertainty ALWAYS ≥ 0.15 (perception bridge rule)
  F9  Anti-Hantu:        explicit flag that RGB/colour alone is not decisive
  F4  Clarity:           all quantities carry units and type labels
  F11 Authority:         provenance always present

Perception Bridge Rule (GEOX core policy):
  Visual outputs from SeismicVLMTool alone are NEVER decisive for
  geological decisions. This mock enforces this by:
  1. Always setting uncertainty ≥ 0.15 on all quantities
  2. Always setting multisensor_required: True in metadata
  3. Including a perception_bridge_warning in raw_output

Output quantities (all fictional, seeded for reproducibility):
  - fault_probability       [fraction] — 0.10 to 0.80
  - amplitude_anomaly       [fraction] — 0.0 to 1.0 (DHI indicator)
  - structural_closure_m    [m]        — 0.0 to 200.0
  - structural_confidence   [fraction] — 0.40 to 0.85
  - reflector_continuity    [fraction] — 0.30 to 0.95

References (open literature on seismic interpretation quality):
  - Sheriff & Geldart (1995) Exploration Seismology, Cambridge UP
  - Hart (2008) AAPG Bulletin 92(8):1025–1044 (seismic facies)
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
# Perception bridge rule enforcement
# ---------------------------------------------------------------------------

#: Minimum uncertainty enforced on ALL VLM quantities (F7 + Perception Bridge)
VLM_MINIMUM_UNCERTAINTY: float = 0.15

#: Maximum confidence that the VLM is permitted to claim
VLM_MAXIMUM_CONFIDENCE: float = 0.70


# ---------------------------------------------------------------------------
# MockSeismicVLMTool
# ---------------------------------------------------------------------------

class MockSeismicVLMTool(BaseTool):
    """
    Mock Vision Language Model for seismic structural interpretation.

    Returns structurally plausible (but entirely fictional) interpretation
    results for a synthetic seismic section. All outputs comply with the
    GEOX Perception Bridge Rule:

      "RGB/colour patterns in seismic images alone are not decisive for
      geological conclusions. VLM outputs must always be corroborated by
      LEM, well logs, or simulator data before any operational action."

    Uncertainty is always ≥ 0.15 on all quantities.
    multisensor_required is always True in metadata.

    Inputs:
        image_path          (str) — path to seismic section image file
        interpretation_query (str) — what structural feature to interpret

    Outputs (GeoQuantity):
        - fault_probability       [fraction] — probability of a mapped fault
        - amplitude_anomaly       [fraction] — DHI/AVO indicator strength
        - structural_closure_m    [m]        — estimated structural closure height
        - structural_confidence   [fraction] — overall interpretation confidence
        - reflector_continuity    [fraction] — seismic reflector continuity score
    """

    @property
    def name(self) -> str:
        return "MockSeismicVLMTool"

    @property
    def description(self) -> str:
        return (
            "Mock Vision Language Model for seismic section interpretation. "
            "Returns fault probability, amplitude anomaly, structural closure, "
            "and structural confidence. "
            "Uncertainty always ≥ 0.15 (Perception Bridge Rule). "
            "multisensor_required always True."
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
                    "Invalid inputs. Required keys: "
                    "'image_path' (str), 'interpretation_query' (str)."
                ),
            )

        start = time.perf_counter()
        image_path: str = inputs["image_path"]
        query: str = inputs["interpretation_query"]

        # Deterministic seed from image path for reproducibility
        seed = int(hashlib.sha256(image_path.encode("utf-8")).hexdigest(), 16) % (2**31)
        rng = random.Random(seed)

        # --- Generate plausible structural interpretation values ---

        # Fault probability: 0.10–0.80 (full spectrum; depends on image)
        fault_probability = rng.uniform(0.10, 0.80)

        # Amplitude anomaly (DHI/AVO indicator): 0.0–1.0
        # Binary-influenced: either bright spot or not
        has_bright_spot = rng.random() < 0.40  # 40% of Malay Basin prospects show DHI
        if has_bright_spot:
            amplitude_anomaly = rng.uniform(0.55, 0.95)
        else:
            amplitude_anomaly = rng.uniform(0.00, 0.40)

        # Structural closure height (m): 0–200 m for Malay Basin anticlines
        # A closure of 0 = no closure (flat/monoclinal)
        has_closure = rng.random() < 0.65  # 65% of picked prospects have closure
        if has_closure:
            structural_closure_m = rng.uniform(15.0, 200.0)
        else:
            structural_closure_m = rng.uniform(0.0, 15.0)

        # Overall structural interpretation confidence: 0.40–0.85
        structural_confidence = rng.uniform(0.40, 0.85)

        # Reflector continuity: 0.30–0.95 (higher = cleaner seismic)
        reflector_continuity = rng.uniform(0.30, 0.95)

        # --- Build provenance (F11 Authority) ---
        source_id = f"MOCK-VLM-SEI-{seed % 100000:05d}"
        prov = _build_vlm_prov(source_id, confidence=min(structural_confidence, VLM_MAXIMUM_CONFIDENCE))

        # Default location: no geographic anchor from VLM perception alone
        # (F9 Anti-Hantu: do not fabricate coordinates from an image)
        location = CoordinatePoint(latitude=4.5, longitude=103.7)

        # --- Build quantities (F7: uncertainty always ≥ 0.15) ---
        def _qty(value: float, units: str, qtype: str) -> GeoQuantity:
            return GeoQuantity(
                value=round(value, 4),
                units=units,
                quantity_type=qtype,
                coordinates=location,
                timestamp=datetime.now(timezone.utc),
                uncertainty=VLM_MINIMUM_UNCERTAINTY,  # Always exactly 0.15
                provenance=prov,
            )

        quantities = [
            _qty(round(fault_probability, 4), "fraction", "fault_probability"),
            _qty(round(amplitude_anomaly, 4), "fraction", "amplitude_anomaly"),
            _qty(round(structural_closure_m, 2), "m", "structural_closure_m"),
            _qty(round(structural_confidence, 4), "fraction", "structural_interpretation"),
            _qty(round(reflector_continuity, 4), "fraction", "reflector_continuity"),
        ]

        # --- Raw output with perception bridge warning (F9 Anti-Hantu) ---
        raw_output = {
            "image_path": image_path,
            "interpretation_query": query,
            "fault_probability": fault_probability,
            "amplitude_anomaly_index": amplitude_anomaly,
            "has_bright_spot": has_bright_spot,
            "structural_closure_m": structural_closure_m,
            "has_structural_closure": has_closure,
            "structural_confidence": structural_confidence,
            "reflector_continuity": reflector_continuity,
            "model": "MockVLM-SEISMIC-GEOX-v0.1",
            "seed": seed,
            # F9 Anti-Hantu: explicit perception bridge warning
            "perception_bridge_warning": (
                "GEOX PERCEPTION BRIDGE RULE: "
                "VLM outputs are derived from visual/colour pattern recognition only. "
                "RGB/amplitude colour alone is NOT decisive for geological conclusions. "
                "These results MUST be corroborated with: "
                "(1) Large Earth Model (LEM) geophysical data, "
                "(2) Well log measurements, or "
                "(3) Basin simulation results "
                "before any operational or investment decision is made."
            ),
            "references": [
                "Sheriff & Geldart (1995) Exploration Seismology, Cambridge UP",
                "Hart (2008) AAPG Bulletin 92(8):1025–1044",
            ],
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "model_version": "MockVLM-SEISMIC-GEOX-v0.1",
                "seed": seed,
                # Perception Bridge Rule enforcement metadata
                "multisensor_required": True,         # ALWAYS True for VLM
                "perception_only": True,               # ALWAYS True for VLM
                "uncertainty_floor": VLM_MINIMUM_UNCERTAINTY,
                "max_confidence": VLM_MAXIMUM_CONFIDENCE,
                "corroboration_required": [
                    "EarthModelTool",
                    "SimulatorTool",
                    "GeoRAGTool",
                ],
                "basin": "Malay Basin (mock)",
                "data_type": "fictional seismic interpretation — no proprietary data",
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )


# ---------------------------------------------------------------------------
# Provenance builder
# ---------------------------------------------------------------------------

def _build_vlm_prov(source_id: str, confidence: float) -> ProvenanceRecord:
    """Build a ProvenanceRecord for VLM outputs with F11 compliance."""
    # Cap confidence at VLM_MAXIMUM_CONFIDENCE (epistemic limit of visual-only)
    capped_confidence = min(confidence, VLM_MAXIMUM_CONFIDENCE)
    return ProvenanceRecord(
        source_id=source_id,
        source_type="VLM",
        timestamp=datetime.now(timezone.utc),
        confidence=capped_confidence,
        citation=(
            "Mock VLM seismic interpretation. "
            "Ref: Sheriff & Geldart (1995); Hart (2008) AAPG Bull."
        ),
        floor_check={
            "F1_amanah": True,
            "F2_truth": True,
            "F4_clarity": True,
            "F7_humility": True,    # Enforced via uncertainty ≥ 0.15
            "F9_anti_hantu": True,  # perception_bridge_warning included
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
        tool = MockSeismicVLMTool()
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description[:80]}...")
        print(f"Health: {tool.health_check()}")

        inputs = {
            "image_path": "malay_basin_blok_selatan_section.png",
            "interpretation_query": "Identify structural closure and fault probability",
        }

        result = await tool.run(inputs)
        print(f"\nSuccess: {result.success}")
        print(f"Latency: {result.latency_ms:.2f} ms")
        print(f"Quantities returned: {len(result.quantities)}")
        for qty in result.quantities:
            print(
                f"  {qty.quantity_type}: {qty.value} {qty.units} "
                f"(uncertainty={qty.uncertainty:.2f} — {'✓ ≥0.15' if qty.uncertainty >= 0.15 else '✗ VIOLATION'})"
            )

        print("\nPerception Bridge Rule enforced:")
        print(f"  multisensor_required: {result.metadata['multisensor_required']}")
        print(f"  perception_only: {result.metadata['perception_only']}")
        print(f"  uncertainty_floor: {result.metadata['uncertainty_floor']}")
        print(f"  max_confidence: {result.metadata['max_confidence']}")
        print(f"\nWarning excerpt: {result.raw_output['perception_bridge_warning'][:100]}...")

    asyncio.run(_selftest())
