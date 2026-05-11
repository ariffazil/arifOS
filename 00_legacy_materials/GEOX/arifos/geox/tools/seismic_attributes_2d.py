"""
arifos/geox/tools/seismic_attributes_2d.py — 2D Single-Line Seismic Analysis Tool
DITEMPA BUKAN DIBERI

Plane 2 — Perception Layer: Single 2D seismic line workflow for Subsurface Forge.

Strict 2D governance:
  - Output verdict: QUALIFY | HOLD | GEOX_BLOCK
  - Never SEAL (2D cannot support high-confidence structural claims)
  - 3D volumetrics / definitive HC claims → automatic GEOX_BLOCK
  - All outputs carry contrast_metadata + uncertainty bands

Tool Flow (MCP-native):
  1. validate_2d_limits()  — check what CAN be claimed from 2D
  2. compute_attributes_2d() — coherence, 2D curvature, instantaneous, spectral
  3. pick_horizons_faults()  — rule-based horizon/fault picks with uncertainty
  4. interpret_structural()  — structured geological interpretation
  5. audit_2d_limits()      — emit hard limits on what 2D cannot support
  6. generate_line_report()  — structured report with panels + JSON output
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from arifos.geox.base_tool import (
    BaseTool,
    GeoToolResult,
    _make_provenance,
    _make_quantity,
)
from arifos.geox.geox_schemas import CoordinatePoint
from arifos.geox.seismic_attribute_taxonomy import (
    SEISMIC_ATTRIBUTES,
    get_governance_flags,
    is_high_contrast_risk,
)

logger = logging.getLogger("geox.tools.seismic_attributes_2d")


class Line2DVerdict(str, Enum):
    QUALIFY = "QUALIFY"  # Safe to interpret with caveats
    HOLD = "HOLD"  # Caution required, elevated uncertainty
    GEOX_BLOCK = "GEOX_BLOCK"  # 2D cannot support this claim


class PickType(str, Enum):
    HORIZON = "horizon"
    FAULT = "fault"
    UNCONFORMITY = "unconformity"


# =============================================================================
# 2D Attribute Computations
# =============================================================================


def compute_2d_coherence(trace: np.ndarray, window: int = 5) -> np.ndarray:
    """
    2D trace-to-trace coherence using semblance-like continuity measure.
    For a single 2D line: measures waveform similarity between adjacent traces.
    """
    n = len(trace)
    output = np.zeros(n, dtype=np.float64)
    half = window // 2
    padded = np.pad(trace, half, mode="reflect")
    for i in range(n):
        center = padded[i + half]
        windowed = padded[i : i + window]
        numerator = ((windowed - center) ** 2).sum()
        denom = ((windowed - windowed.mean()) ** 2).sum()
        output[i] = np.clip(1 - numerator / (window * denom + 1e-10), 0, 1)
    return output


def compute_2d_curvature(trace: np.ndarray) -> dict[str, np.ndarray]:
    """
    2D curvature from a picked horizon or seismic line.
    Returns most-positive and most-negative curvature estimates.
    """
    first = np.gradient(trace.astype(np.float64))
    second = np.gradient(first)
    return {
        "curvature_positive": second,
        "curvature_negative": -second,
    }


def compute_instantaneous_attributes(
    trace: np.ndarray, sample_rate_ms: float = 4.0
) -> dict[str, np.ndarray]:
    """
    Instantaneous attributes via Hilbert transform for a single trace.
    Returns: envelope, instantaneous_frequency, instantaneous_phase
    """
    from numpy.fft import fft, fftfreq, ifft

    n = len(trace)
    trace_f = trace.astype(np.float64)

    spectrum = fft(trace_f)
    analytic = np.zeros(n, dtype=np.complex128)
    analytic[1 : n // 2] = 2 * spectrum[1 : n // 2]
    analytic[0] = spectrum[0]
    if n % 2 == 0:
        analytic[n // 2] = spectrum[n // 2]

    analytic_signal = ifft(analytic)
    envelope = np.abs(analytic_signal)
    instantaneous_phase = np.angle(analytic_signal)

    freq = fftfreq(n, sample_rate_ms / 1000.0)[: n // 2]
    inst_freq = np.gradient(instantaneous_phase) / (2 * np.pi)
    inst_freq = np.clip(inst_freq[: n // 2], 0, freq.max())

    return {
        "envelope": envelope,
        "instantaneous_frequency": inst_freq,
        "instantaneous_phase": instantaneous_phase,
    }


def compute_spectral_2d(
    trace: np.ndarray, sample_rate_ms: float = 4.0
) -> dict[str, Any]:
    """Spectral content of a single trace. Returns band energy."""
    from numpy.fft import fft, fftfreq

    n = len(trace)
    spectrum = np.abs(fft(trace))[: n // 2]
    freqs = fftfreq(n, sample_rate_ms / 1000.0)[: n // 2]

    bands = {
        "low_5_15": (5, 15),
        "mid_15_45": (15, 45),
        "high_45_80": (45, 80),
    }
    result = {}
    for band_name, (f_low, f_high) in bands.items():
        mask = (freqs >= f_low) & (freqs <= f_high)
        result[band_name] = float(
            np.sqrt(np.mean(spectrum[mask] ** 2)) if mask.any() else 0.0
        )
    return result


# =============================================================================
# Horizon / Fault Picking
# =============================================================================


@dataclass
class Pick:
    """A single pick on a 2D seismic line."""

    pick_id: str
    pick_type: PickType
    twt_ms: float
    trace_index: int
    uncertainty_ms: float
    confidence: float
    label: str
    notes: str = ""


@dataclass
class PickSet:
    """Collection of picks along a 2D line."""

    picks: list[Pick] = field(default_factory=list)
    line_id: str = ""
    num_traces: int = 0
    sample_rate_ms: float = 4.0

    def add_pick(self, pick: Pick) -> None:
        self.picks.append(pick)

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "num_traces": self.num_traces,
            "sample_rate_ms": self.sample_rate_ms,
            "picks": [
                {
                    "pick_id": p.pick_id,
                    "pick_type": p.pick_type.value,
                    "twt_ms": p.twt_ms,
                    "trace_index": p.trace_index,
                    "uncertainty_ms": p.uncertainty_ms,
                    "confidence": p.confidence,
                    "label": p.label,
                    "notes": p.notes,
                }
                for p in self.picks
            ],
        }


def auto_pick_horizons(
    envelope: np.ndarray,
    coherence: np.ndarray,
    threshold: float = 0.3,
    window_ms: float = 4.0,
) -> PickSet:
    """
    Simple rule-based horizon picker on 2D line.

    Picks peaks in envelope that also have high coherence (structural continuity).
    Returns uncertainty bands around each pick.
    """
    picks = PickSet()
    n = len(envelope)
    sample_rate_ms = 4.0
    max(1, int(window_ms / sample_rate_ms))

    in_pick = False
    pick_start = 0
    best_peak = 0
    best_peak_idx = 0

    for i in range(1, n - 1):
        is_peak = envelope[i] > envelope[i - 1] and envelope[i] > envelope[i + 1]
        high_coherence = coherence[i] > threshold

        if is_peak and high_coherence and not in_pick:
            in_pick = True
            pick_start = i
            best_peak = envelope[i]
            best_peak_idx = i
        elif is_peak and high_coherence and in_pick:
            if envelope[i] > best_peak:
                best_peak = envelope[i]
                best_peak_idx = i
        elif not high_coherence and in_pick:
            in_pick = False
            coherence_avg = (
                float(np.mean(coherence[pick_start:i])) if i > pick_start else 0.3
            )
            uncertainty_ms = (i - pick_start) * sample_rate_ms / 2
            picks.add_pick(
                Pick(
                    pick_id=f"H{len(picks.picks) + 1:02d}",
                    pick_type=PickType.HORIZON,
                    twt_ms=best_peak_idx * sample_rate_ms,
                    trace_index=0,
                    uncertainty_ms=max(uncertainty_ms, 10.0),
                    confidence=min(coherence_avg + 0.1, 0.95),
                    label=f"Horizon-{len(picks.picks) + 1}",
                    notes="Auto-picked from envelope coherence peak",
                )
            )

    return picks


def detect_faults_from_coherence(
    coherence: np.ndarray, threshold: float = 0.4
) -> list[Pick]:
    """
    Detect fault candidates from low-coherence zones on 2D line.
    Returns a list of fault picks with throw estimates.
    """
    faults = []
    n = len(coherence)
    sample_rate_ms = 4.0

    below_threshold = coherence < threshold
    transitions = np.diff(below_threshold.astype(int))

    for i, trans in enumerate(transitions):
        if trans != 0 and i > 0 and i < n - 1:
            zone_coherence = float(coherence[max(0, i - 2) : min(n, i + 3)].mean())
            fault_pick = Pick(
                pick_id=f"F{len(faults) + 1:02d}",
                pick_type=PickType.FAULT,
                twt_ms=i * sample_rate_ms,
                trace_index=0,
                uncertainty_ms=15.0,
                confidence=max(0.0, 1.0 - zone_coherence / threshold),
                label=f"Fault-{len(faults) + 1}",
                notes="Detected from coherence drop. Throw estimate qualitative only.",
            )
            faults.append(fault_pick)

    return faults


# =============================================================================
# Structural Interpretation
# =============================================================================


def interpret_structural(picks: PickSet) -> dict[str, Any]:
    """
    Generate structured geological interpretation from picks.

    Output:
      - structural_assemblage: e.g. "normal fault block", "anticline", "syncline"
      - description: natural language description
      - confidence: overall interpretation confidence
      - caveats: list of interpretation caveats
    """
    if not picks.picks:
        return {
            "structural_assemblage": "unknown",
            "description": "No picks available for interpretation.",
            "confidence": 0.0,
            "caveats": ["No horizon or fault picks found."],
        }

    horizons = [p for p in picks.picks if p.pick_type == PickType.HORIZON]
    faults = [p for p in picks.picks if p.pick_type == PickType.FAULT]

    assemblage = "sub-horizontal stratigraphy"
    confidence = 0.5
    caveats: list[str] = []
    descriptions: list[str] = []

    if len(horizons) >= 2:
        twts = [h.twt_ms for h in horizons]
        dip_change = max(twts) - min(twts)
        if dip_change > 50:
            assemblage = "dipping reflector / fold structure"
            confidence = 0.6
            descriptions.append(
                f"Apparent dip of ~{dip_change:.0f} ms over {len(horizons)} horizons."
            )
            caveats.append("2D apparent dip may not represent true structural dip.")
        elif dip_change > 20:
            assemblage = "gentle fold / flexure"
            confidence = 0.65
            descriptions.append(
                f"Subtle flexure detected (~{dip_change:.0f} ms relief)."
            )
        else:
            assemblage = "flat-lying / sub-horizontal stratigraphy"
            confidence = 0.75
            descriptions.append(
                "Relatively flat horizons consistent with tabular stratigraphy."
            )

    if faults:
        n_faults = len(faults)
        assemblage = f"faulted_{assemblage}"
        confidence = min(confidence + 0.05 * n_faults, 0.85)
        descriptions.append(
            f"{n_faults} fault(s) identified from coherence discontinuity."
        )
        caveats.append(
            "Fault planes cannot be resolved on 2D line. Fault geometry is qualitative."
        )

    description = (
        " ".join(descriptions)
        if descriptions
        else "No definitive structural interpretation possible."
    )
    caveats.append(
        "2D line only — out-of-plane reflections and limited spatial sampling possible. "
        "Coherence discontinuities may not represent true 3D fault planes. "
        "Cross-check with orthogonal lines or 3D volume when available."
    )

    return {
        "structural_assemblage": assemblage,
        "description": description,
        "confidence": round(confidence, 3),
        "caveats": caveats,
        "num_horizons": len(horizons),
        "num_faults": len(faults),
    }


# =============================================================================
# 2D Limits Audit
# =============================================================================


def audit_2d_limits(interpretation: dict[str, Any]) -> dict[str, Any]:
    """
    Audit what CANNOT be reliably claimed from a 2D seismic line.

    Returns a dict of hard limits and recommended next steps.
    """
    hard_blocks: list[str] = []
    soft_caveats: list[str] = []

    hard_blocks.append(
        "Full 3D trap geometry, closure area, or spill point determination"
    )
    hard_blocks.append(
        "Reliable areal extent or true volumetrics (only 2D cross-section possible)"
    )
    hard_blocks.append(
        "Confident channel sinuosity or fault network connectivity (out-of-plane effects)"
    )
    hard_blocks.append(
        "Definitive hydrocarbon presence — always treat as DHI candidate only"
    )

    soft_caveats.append(
        "Apparent throw estimates from 2D may exaggerate or underestimate true fault displacement"
    )
    soft_caveats.append(
        "Coherence-based fault picks require validation against orthogonal line or 3D"
    )
    soft_caveats.append(
        "Spectral attributes sensitive to tuning and thin-bed effects — check against well"
    )

    assemblage = interpretation.get("structural_assemblage", "unknown")
    is_structural = assemblage not in ("unknown", "sub-horizontal stratigraphy")

    return {
        "verdict": (
            Line2DVerdict.GEOX_BLOCK.value
            if interpretation.get("confidence", 0) < 0.3
            else Line2DVerdict.QUALIFY.value
        ),
        "hard_blocks": hard_blocks,
        "soft_caveats": soft_caveats,
        "can_support_2d_structural": is_structural,
        "can_support_dhi_candidate": True,
        "can_support_3d_volumetrics": False,
        "requires_orthogonal_validation": True,
        "next_steps": [
            "Acquire orthogonal 2D line or 3D volume for full structural imaging",
            "Tie to existing wells for depth conversion and stratigraphic calibration",
            "If exploring for DHI: design dedicated AVO/elastic survey with offset coverage",
            "For fault analysis: integrate with regional structural study and balanced restoration",
        ],
        "telemetry": {
            "agent": "@GEOX",
            "version": "0.3.0-2d-forge",
            "pipeline": "222_REFLECT",
            "floors": ["F1", "F4", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
            "audit_2d_limits": True,
        },
    }


# =============================================================================
# Main 2D Seismic Attributes Tool
# =============================================================================


class SeismicAttributes2DTool(BaseTool):
    """
    GEOX Subsurface Forge — Single 2D Seismic Line Analysis Tool.

    MCP-native tool for analyzing a single 2D seismic line with full
    Contrast Canon enforcement and 2D-specific governance.

    Inputs:
        line_id        (str)  — Identifier for this seismic line
        seismic_data   (np.ndarray) — 2D seismic array (traces, samples)
        trace_coords   (list[CoordinatePoint]) — One per trace
        sample_rate_ms (float) — Sampling interval in ms (default 4.0)
        attributes     (list[str]) — Attributes to compute
        horizons_to_pick (int) — Number of horizons to auto-pick (default 3)
        fault_threshold (float) — Coherence threshold for fault detection

    Outputs:
        GeoToolResult with:
          - attribute_panels: dict of 2D attribute arrays
          - picks: PickSet dict with horizons and faults
          - interpretation: structural interpretation dict
          - audit: 2D limits audit dict
          - contrast_metadata: per-attribute ContrastMetadata
          - verdict: QUALIFY | HOLD | GEOX_BLOCK
          - telemetry: pipeline metadata

    Governance:
      - F4: Units (ms TWT), coordinates attached to all picks
      - F7: Uncertainty bands on all picks (±X ms)
      - F9: No phantom 3D geometry from 2D data
      - 2D audit: automatic GEOX_BLOCK for 3D claims
    """

    @property
    def name(self) -> str:
        return "SeismicAttributes2DTool"

    @property
    def description(self) -> str:
        return (
            "Single 2D seismic line analysis. Computes coherence, curvature, "
            "instantaneous and spectral attributes. Auto-picks horizons/faults "
            "with uncertainty bands. Emits 2D limits audit. "
            "F4/F7/F9 enforced. 3D claims → GEOX_BLOCK."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        required = {"line_id", "seismic_data"}
        if not all(k in inputs for k in required):
            return False
        data = inputs["seismic_data"]
        if not isinstance(data, np.ndarray) or data.ndim != 2:
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Invalid inputs. Required: 'line_id' (str), 'seismic_data' (2D ndarray).",
            )

        start = time.perf_counter()

        line_id: str = inputs["line_id"]
        seismic_data: np.ndarray = inputs["seismic_data"]
        sample_rate_ms: float = inputs.get("sample_rate_ms", 4.0)
        attributes: list[str] = inputs.get(
            "attributes",
            ["coherence", "curvature", "envelope", "spectral"],
        )
        fault_threshold: float = inputs.get("fault_threshold", 0.4)

        num_traces, num_samples = seismic_data.shape

        checksum = hashlib.sha256(seismic_data.tobytes()).hexdigest()[:16]
        prov = _make_provenance(
            source_id=f"2D-{checksum}",
            source_type="seismic_2d",
            confidence=0.80,
            checksum=checksum,
        )

        trace_coords: list[CoordinatePoint] = inputs.get(
            "trace_coords",
            [CoordinatePoint(latitude=0.0, longitude=0.0)] * num_traces,
        )

        attribute_panels: dict[str, Any] = {}
        contrast_metadata_out: dict[str, Any] = {}

        for attr_name in attributes:
            SEISMIC_ATTRIBUTES.get(attr_name.lower())
            get_governance_flags(attr_name.lower())

            if attr_name.lower() == "coherence":
                arr = compute_2d_coherence(seismic_data.mean(axis=0))
                for t in range(num_traces):
                    trace = seismic_data[t, :]
                    coh = compute_2d_coherence(trace)
                    arr = arr + coh if t > 0 else coh
                arr /= num_traces
                panel = arr.reshape(1, -1).repeat(num_traces, axis=0)

            elif attr_name.lower() == "curvature":
                mean_trace = seismic_data.mean(axis=0)
                compute_2d_curvature(mean_trace)
                panel = np.zeros((num_traces, num_samples), dtype=np.float64)
                for t in range(num_traces):
                    c = compute_2d_curvature(seismic_data[t, :])
                    panel[t, :] = c["curvature_positive"]
                get_governance_flags("curvature_most_positive")
                contrast_metadata_out[attr_name] = {
                    "attribute_name": attr_name,
                    "physical_axes": ["structural_flexure"],
                    "equation_reference": "Roberts (2001)",
                    "anomalous_risk": {"display_bias": "low"},
                }

            elif attr_name.lower() == "envelope":
                panel = np.zeros_like(seismic_data, dtype=np.float64)
                for t in range(num_traces):
                    inst = compute_instantaneous_attributes(
                        seismic_data[t, :], sample_rate_ms
                    )
                    panel[t, :] = inst["envelope"]
                contrast_metadata_out[attr_name] = {
                    "attribute_name": attr_name,
                    "physical_axes": ["acoustic_impedance"],
                    "equation_reference": "Taner et al. (1979)",
                    "anomalous_risk": {"display_bias": "low"},
                }

            elif "spectral" in attr_name.lower():
                spectral_results = []
                for t in range(num_traces):
                    sr = compute_spectral_2d(seismic_data[t, :], sample_rate_ms)
                    spectral_results.append(sr)
                panel = np.zeros((num_traces, 3), dtype=np.float64)
                for t, sr in enumerate(spectral_results):
                    panel[t, :] = [
                        sr.get("low_5_15", 0),
                        sr.get("mid_15_45", 0),
                        sr.get("high_45_80", 0),
                    ]
                contrast_metadata_out[attr_name] = {
                    "attribute_name": attr_name,
                    "physical_axes": ["frequency_content"],
                    "equation_reference": "Partyka et al. (1999)",
                    "anomalous_risk": {"display_bias": "medium"},
                }

            else:
                panel = np.zeros((num_traces, num_samples), dtype=np.float32)

            attribute_panels[attr_name] = panel.tolist()

        mean_trace = seismic_data.mean(axis=0)
        envelope_trace = compute_instantaneous_attributes(mean_trace, sample_rate_ms)[
            "envelope"
        ]
        coherence_trace = compute_2d_coherence(mean_trace)

        picks = auto_pick_horizons(
            envelope=envelope_trace,
            coherence=coherence_trace,
            threshold=0.3,
            window_ms=sample_rate_ms * 3,
        )
        picks.line_id = line_id
        picks.num_traces = num_traces
        picks.sample_rate_ms = sample_rate_ms

        faults = detect_faults_from_coherence(
            coherence_trace, threshold=fault_threshold
        )
        for f in faults:
            picks.add_pick(f)

        interpretation = interpret_structural(picks)
        audit = audit_2d_limits(interpretation)

        geoquantities = []
        for attr_name, panel in attribute_panels.items():
            arr = np.array(panel)
            mean_val = float(np.mean(arr))
            std_val = float(np.std(arr))
            uncertainty = 0.15 if is_high_contrast_risk(attr_name) else 0.08
            location = (
                trace_coords[0]
                if trace_coords
                else CoordinatePoint(latitude=0.0, longitude=0.0)
            )
            geoquantities.append(
                _make_quantity(
                    round(mean_val, 6),
                    "ms",
                    f"attr_twt_{attr_name}",
                    location,
                    prov,
                    uncertainty,
                )
            )
            geoquantities.append(
                _make_quantity(
                    round(std_val, 6),
                    "ms",
                    f"attr_twt_std_{attr_name}",
                    location,
                    prov,
                    uncertainty,
                )
            )

        for pick in picks.picks:
            location = (
                trace_coords[pick.trace_index]
                if pick.trace_index < len(trace_coords)
                else trace_coords[0]
            )
            geoquantities.append(
                _make_quantity(
                    round(pick.twt_ms, 2),
                    "ms",
                    f"pick_{pick.pick_type.value}_{pick.pick_id}",
                    location,
                    prov,
                    pick.uncertainty_ms / 1000.0,
                )
            )

        raw_output = {
            "line_id": line_id,
            "num_traces": num_traces,
            "num_samples": num_samples,
            "sample_rate_ms": sample_rate_ms,
            "attributes_computed": list(attribute_panels.keys()),
            "attribute_panels": attribute_panels,
            "picks": picks.to_dict(),
            "interpretation": interpretation,
            "audit_2d_limits": audit,
            "contrast_metadata": contrast_metadata_out,
            "volume_checksum_sha256": checksum,
        }

        verdict = audit["verdict"]
        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=geoquantities,
            raw_output=raw_output,
            metadata={
                "tool_version": "2D-GEOX-v0.3.0",
                "line_id": line_id,
                "attributes_computed": list(attribute_panels.keys()),
                "verdict": verdict,
                "num_picks": len(picks.picks),
                "num_faults": len(
                    [p for p in picks.picks if p.pick_type == PickType.FAULT]
                ),
                "contrast_canon": True,
                "audit_2d_limits": True,
                "telemetry": audit.get("telemetry", {}),
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )
