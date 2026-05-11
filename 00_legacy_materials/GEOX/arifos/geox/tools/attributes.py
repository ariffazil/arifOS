"""
arifos/geox/tools/attributes.py — Classical Seismic Attribute Engine
DITEMPA BUKAN DIBERI

Plane 1/2 Bridge: Computes classical seismic attributes from trace data.
These are the mathematical foundations that all 7 meta-intelligence
attributes build on.

Supported attribute families:
  1. Coherence / Semblance      — waveform similarity (discontinuity)
  2. Volumetric Curvature       — most-positive, most-negative, Gaussian, mean
  3. Spectral Decomposition     — CWT / STFT frequency slices
  4. Amplitude                  — RMS, Envelope, Sweetness
  5. Dip / Azimuth              — structural orientation

Every attribute output carries:
  - ContrastMetadata (Contrast Canon compliance)
  - Uncertainty bounds
  - Processing provenance

Constitutional enforcement:
  F2  Truth:     Only physics-based computations, no learned weights
  F4  Clarity:   Units + equations documented per attribute
  F7  Humility:  Uncertainty tracked per computation
  F9  Anti-Hantu: Classical attributes are transparent math, not black boxes
  F11 Authority: Full processing provenance
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np

from arifos.geox.base_tool import (
    BaseTool,
    GeoToolResult,
    _make_provenance,
    _make_quantity,
)
from arifos.geox.geox_schemas import CoordinatePoint
from arifos.geox.tools.contrast_metadata import (
    ConfidenceClass,
    ContrastMetadata,
    ContrastSourceDomain,
    PhysicalProxy,
    VisualTransform,
)

logger = logging.getLogger("geox.tools.attributes")


# ---------------------------------------------------------------------------
# Attribute Result
# ---------------------------------------------------------------------------


@dataclass
class AttributeResult:
    """Output from a single attribute computation."""

    name: str
    volume: np.ndarray
    units: str
    equation_reference: str
    uncertainty: float
    contrast_metadata: ContrastMetadata
    processing_time_ms: float
    notes: str = ""


@dataclass
class AttributeStack:
    """Collection of computed attributes with governance metadata."""

    attributes: dict[str, AttributeResult] = field(default_factory=dict)
    source_volume_checksum: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def add(self, result: AttributeResult) -> None:
        self.attributes[result.name] = result

    @property
    def names(self) -> list[str]:
        return list(self.attributes.keys())

    @property
    def governance_summary(self) -> dict[str, str]:
        """Returns governance status for every attribute in the stack."""
        return {
            name: result.contrast_metadata.governance_status
            for name, result in self.attributes.items()
        }


# ---------------------------------------------------------------------------
# 1. COHERENCE / SEMBLANCE
# ---------------------------------------------------------------------------


def compute_coherence(
    volume: np.ndarray,
    window_shape: tuple[int, int, int] = (3, 3, 5),
    method: str = "semblance",
) -> AttributeResult:
    """
    Compute semblance-based coherence for discontinuity detection.

    Measures waveform similarity in a local window. Low coherence
    indicates structural discontinuities (faults, fracture zones).

    Based on: Marfurt et al. (1998) "Multi-trace semblance"

    Args:
        volume: 3D seismic array (inline, xline, samples)
        window_shape: (inline_size, xline_size, sample_size)
        method: 'semblance' (energy-ratio based)

    Returns:
        AttributeResult with coherence values [0.0, 1.0]
    """
    start = time.perf_counter()

    if volume.ndim == 2:
        volume = volume[np.newaxis, :, :]  # Promote to 3D

    ni, nx, ns = volume.shape
    wi, wx, ws = window_shape
    hi, hx, hs = wi // 2, wx // 2, ws // 2

    padded = np.pad(volume.astype(np.float64), ((hi, hi), (hx, hx), (hs, hs)), mode="reflect")

    coherence = np.zeros((ni, nx, ns), dtype=np.float64)

    for i in range(ni):
        for x in range(nx):
            for s in range(ns):
                window = padded[i : i + wi, x : x + wx, s : s + ws]
                n_traces = wi * wx

                # Reshape to (n_traces, samples)
                traces = window.reshape(n_traces, ws)

                # Semblance = (sum of traces)^2 / (n * sum of traces^2)
                sum_trace = traces.sum(axis=0)
                numerator = (sum_trace**2).sum()
                denominator = n_traces * (traces**2).sum()

                if denominator > 0:
                    coherence[i, x, s] = numerator / denominator
                else:
                    coherence[i, x, s] = 0.0

    # Clip to [0, 1]
    coherence = np.clip(coherence, 0.0, 1.0)
    elapsed = (time.perf_counter() - start) * 1000

    cm = ContrastMetadata(
        source_domain=ContrastSourceDomain(
            domain="reflectivity",
            measurement_units="dimensionless",
            acquisition_type="seismic_3d",
        ),
        processing_chain=[
            VisualTransform(
                transform_type="custom",
                parameters={
                    "method": method,
                    "window_shape": list(window_shape),
                    "equation": "Marfurt_semblance_1998",
                },
                order_index=0,
                reversible=False,
                contrast_amplification_factor=1.0,
                notes="Semblance coherence: energy ratio of summed vs individual traces.",
            ),
        ],
        physical_proxy=PhysicalProxy(
            proxy_name="structural_discontinuity",
            proxy_type="calibrated_proxy",
            physical_range=(0.0, 1.0),
            physical_units="dimensionless",
        ),
        confidence_class=ConfidenceClass(
            signal_confidence=0.75,
            interpretation_confidence=0.55,
            anomalous_contrast_risk="low",
            risk_factors=["window_size_sensitivity", "velocity_dependence"],
        ),
        requires_non_visual_confirmation=True,
        created_by="compute_coherence",
    )

    return AttributeResult(
        name="coherence_semblance",
        volume=coherence,
        units="dimensionless",
        equation_reference="Marfurt et al. (1998), Multitrace semblance",
        uncertainty=0.10,
        contrast_metadata=cm,
        processing_time_ms=round(elapsed, 2),
        notes="Low coherence = probable discontinuity. Cross-check with curvature and dip.",
    )


# ---------------------------------------------------------------------------
# 2. VOLUMETRIC CURVATURE
# ---------------------------------------------------------------------------


def compute_curvature(
    volume: np.ndarray,
    curvature_type: str = "most_positive",
) -> AttributeResult:
    """
    Compute volumetric curvature from a 2D/3D seismic slice/volume.

    Curvature measures the rate of change of dip across a surface.
    Highlights flexures, drag folds, fracture density, and karst.

    Supported types:
      - most_positive: highlights anticlines, dome crests, drag folds
      - most_negative: highlights synclines, troughs, channels
      - gaussian: product of K1 * K2 (dome/saddle discriminator)
      - mean: average curvature (K1 + K2) / 2

    Based on: Roberts (2001), Al-Dossary & Marfurt (2006)

    Args:
        volume: 2D or 3D seismic array
        curvature_type: 'most_positive', 'most_negative', 'gaussian', 'mean'

    Returns:
        AttributeResult with curvature values
    """
    start = time.perf_counter()

    if volume.ndim == 2:
        # 2D curvature via second derivatives
        img = volume.astype(np.float64)

        # First derivatives (central difference)
        dy, dx = np.gradient(img)

        # Second derivatives
        dyy, dyx = np.gradient(dy)
        dxy, dxx = np.gradient(dx)

        # Principal curvatures via eigenvalues of Hessian
        # K1 (most positive), K2 (most negative)
        trace = dxx + dyy
        det = dxx * dyy - dxy * dyx

        discriminant = np.sqrt(np.maximum(trace**2 - 4 * det, 0))
        k1 = (trace + discriminant) / 2.0  # Most positive
        k2 = (trace - discriminant) / 2.0  # Most negative

        if curvature_type == "most_positive":
            result_vol = k1
        elif curvature_type == "most_negative":
            result_vol = k2
        elif curvature_type == "gaussian":
            result_vol = k1 * k2
        elif curvature_type == "mean":
            result_vol = (k1 + k2) / 2.0
        else:
            raise ValueError(f"Unknown curvature_type: {curvature_type}")

    else:
        # 3D: compute curvature along inline-xline per time/depth slice
        ni, nx, ns = volume.shape
        result_vol = np.zeros_like(volume, dtype=np.float64)

        for s in range(ns):
            slice_2d = volume[:, :, s].astype(np.float64)
            dy, dx = np.gradient(slice_2d)
            dyy, dyx = np.gradient(dy)
            dxy, dxx = np.gradient(dx)

            trace = dxx + dyy
            det = dxx * dyy - dxy * dyx
            discriminant = np.sqrt(np.maximum(trace**2 - 4 * det, 0))

            if curvature_type == "most_positive":
                result_vol[:, :, s] = (trace + discriminant) / 2.0
            elif curvature_type == "most_negative":
                result_vol[:, :, s] = (trace - discriminant) / 2.0
            elif curvature_type == "gaussian":
                k1 = (trace + discriminant) / 2.0
                k2 = (trace - discriminant) / 2.0
                result_vol[:, :, s] = k1 * k2
            elif curvature_type == "mean":
                result_vol[:, :, s] = trace / 2.0
            else:
                raise ValueError(f"Unknown curvature_type: {curvature_type}")

    elapsed = (time.perf_counter() - start) * 1000

    cm = ContrastMetadata(
        source_domain=ContrastSourceDomain(
            domain="reflectivity",
            measurement_units="1/m",
            acquisition_type="seismic_3d",
        ),
        processing_chain=[
            VisualTransform(
                transform_type="custom",
                parameters={
                    "curvature_type": curvature_type,
                    "equation": "Hessian_eigenvalue_decomposition",
                },
                order_index=0,
                reversible=False,
                contrast_amplification_factor=1.3,
                notes=f"Volumetric {curvature_type} curvature via Hessian eigenvalues.",
            ),
        ],
        physical_proxy=PhysicalProxy(
            proxy_name=f"structural_curvature_{curvature_type}",
            proxy_type="calibrated_proxy",
            physical_units="1/m",
        ),
        confidence_class=ConfidenceClass(
            signal_confidence=0.70,
            interpretation_confidence=0.50,
            anomalous_contrast_risk="low",
            risk_factors=["noise_sensitivity", "derivative_amplification"],
        ),
        requires_non_visual_confirmation=True,
        created_by="compute_curvature",
    )

    return AttributeResult(
        name=f"curvature_{curvature_type}",
        volume=result_vol,
        units="1/m",
        equation_reference="Roberts (2001), Al-Dossary & Marfurt (2006)",
        uncertainty=0.12,
        contrast_metadata=cm,
        processing_time_ms=round(elapsed, 2),
        notes=f"{curvature_type} curvature. Positive = anticline/dome, negative = syncline/trough.",
    )


# ---------------------------------------------------------------------------
# 3. SPECTRAL DECOMPOSITION
# ---------------------------------------------------------------------------


def compute_spectral_decomposition(
    traces: np.ndarray,
    sample_rate_ms: float = 4.0,
    freq_bands_hz: list[tuple[float, float]] | None = None,
    method: str = "stft",
    window_samples: int = 32,
) -> list[AttributeResult]:
    """
    Short-Time Fourier Transform (STFT) spectral decomposition.

    Decomposes seismic traces into frequency band energy slices.
    Useful for:
      - Thin bed tuning detection
      - Channel sinuosity mapping (different frequencies highlight
        different thicknesses)
      - DHI (direct hydrocarbon indicator) workflows

    Args:
        traces: 2D array (traces, samples) or 3D (inline, xline, samples)
        sample_rate_ms: sampling interval in milliseconds
        freq_bands_hz: list of (low_hz, high_hz) bands. Default: 5 standard bands
        method: 'stft' (Short-Time Fourier Transform)
        window_samples: STFT window length

    Returns:
        List of AttributeResult, one per frequency band
    """
    if freq_bands_hz is None:
        freq_bands_hz = [
            (5.0, 15.0),
            (15.0, 25.0),
            (25.0, 40.0),
            (40.0, 60.0),
            (60.0, 80.0),
        ]

    start = time.perf_counter()

    if traces.ndim == 2:
        n_traces, n_samples = traces.shape
        data = traces.astype(np.float64)
    elif traces.ndim == 3:
        ni, nx, n_samples = traces.shape
        n_traces = ni * nx
        data = traces.reshape(n_traces, n_samples).astype(np.float64)
    else:
        raise ValueError(f"traces must be 2D or 3D, got {traces.ndim}D")

    sample_rate_s = sample_rate_ms / 1000.0
    nyquist = 1.0 / (2.0 * sample_rate_s)

    # Compute STFT per trace
    half_win = window_samples // 2
    freqs = np.fft.rfftfreq(window_samples, d=sample_rate_s)
    hann_window = np.hanning(window_samples)

    results = []

    for band_low, band_high in freq_bands_hz:
        # Frequency mask for this band
        freq_mask = (freqs >= band_low) & (freqs <= band_high)

        band_energy = np.zeros((n_traces, n_samples), dtype=np.float64)

        for t in range(n_traces):
            trace = data[t, :]
            padded_trace = np.pad(trace, half_win, mode="reflect")

            for s in range(n_samples):
                segment = padded_trace[s : s + window_samples] * hann_window
                spectrum = np.fft.rfft(segment)
                # RMS energy in band
                band_energy[t, s] = (
                    np.sqrt(np.mean(np.abs(spectrum[freq_mask]) ** 2)) if freq_mask.any() else 0.0
                )

        # Reshape back if 3D input
        if traces.ndim == 3:
            band_volume = band_energy.reshape(ni, nx, n_samples)
        elif traces.ndim == 2:
            band_volume = band_energy.reshape(n_traces, n_samples)
        else:
            band_volume = band_energy

        band_elapsed = (time.perf_counter() - start) * 1000

        band_name = f"spectral_rms_{int(band_low)}_{int(band_high)}Hz"

        cm = ContrastMetadata(
            source_domain=ContrastSourceDomain(
                domain="frequency_content",
                measurement_units="Hz",
                acquisition_type="computed",
            ),
            processing_chain=[
                VisualTransform(
                    transform_type="spectral_decomposition",
                    parameters={
                        "method": method,
                        "window_samples": window_samples,
                        "band_hz": [band_low, band_high],
                        "nyquist_hz": nyquist,
                    },
                    order_index=0,
                    reversible=False,
                    contrast_amplification_factor=1.4,
                    notes=f"STFT spectral decomposition, band {band_low}-{band_high} Hz.",
                ),
            ],
            physical_proxy=PhysicalProxy(
                proxy_name="frequency_band_energy",
                proxy_type="calibrated_proxy",
                physical_range=(band_low, band_high),
                physical_units="Hz",
            ),
            confidence_class=ConfidenceClass(
                signal_confidence=0.70,
                interpretation_confidence=0.45,
                anomalous_contrast_risk="medium",
                risk_factors=[
                    "window_length_vs_wavelength",
                    "tuning_ambiguity",
                    "spectral_leakage",
                ],
            ),
            requires_non_visual_confirmation=True,
            created_by="compute_spectral_decomposition",
        )

        results.append(
            AttributeResult(
                name=band_name,
                volume=band_volume,
                units="amplitude",
                equation_reference="STFT spectral decomposition, Partyka et al. (1999)",
                uncertainty=0.12,
                contrast_metadata=cm,
                processing_time_ms=round(band_elapsed, 2),
                notes=f"RMS energy in {band_low}-{band_high} Hz band. Tuning effects may amplify thin beds.",
            )
        )

    return results


# ---------------------------------------------------------------------------
# 4. AMPLITUDE ATTRIBUTES
# ---------------------------------------------------------------------------


def compute_rms_amplitude(
    volume: np.ndarray,
    window_samples: int = 11,
) -> AttributeResult:
    """
    RMS amplitude in a sliding window.

    Measures total reflected energy. High RMS may indicate
    lithology changes, fluid contacts, or bright spots.
    """
    start = time.perf_counter()

    if volume.ndim == 2:
        volume = volume[np.newaxis, :, :]

    result = np.zeros_like(volume, dtype=np.float64)
    half_w = window_samples // 2

    for i in range(volume.shape[0]):
        for x in range(volume.shape[1]):
            trace = volume[i, x, :].astype(np.float64)
            padded = np.pad(trace, half_w, mode="reflect")
            for s in range(volume.shape[2]):
                window = padded[s : s + window_samples]
                result[i, x, s] = np.sqrt(np.mean(window**2))

    elapsed = (time.perf_counter() - start) * 1000

    cm = ContrastMetadata(
        source_domain=ContrastSourceDomain(
            domain="reflectivity",
            measurement_units="amplitude",
            acquisition_type="seismic_3d",
        ),
        processing_chain=[
            VisualTransform(
                transform_type="custom",
                parameters={"window_samples": window_samples},
                order_index=0,
                contrast_amplification_factor=1.0,
                notes="RMS amplitude in sliding window.",
            ),
        ],
        physical_proxy=PhysicalProxy(
            proxy_name="reflected_energy",
            proxy_type="calibrated_proxy",
            physical_units="amplitude",
        ),
        confidence_class=ConfidenceClass(
            signal_confidence=0.80,
            interpretation_confidence=0.55,
            anomalous_contrast_risk="low",
            risk_factors=["gain_artefacts", "multiples"],
        ),
        requires_non_visual_confirmation=True,
        created_by="compute_rms_amplitude",
    )

    return AttributeResult(
        name="rms_amplitude",
        volume=result.squeeze(),
        units="amplitude",
        equation_reference="Standard RMS amplitude, Taner et al. (1979)",
        uncertainty=0.08,
        contrast_metadata=cm,
        processing_time_ms=round(elapsed, 2),
        notes="RMS amplitude. High values may indicate bright spots or lithology change.",
    )


def compute_envelope(volume: np.ndarray) -> AttributeResult:
    """
    Instantaneous amplitude (envelope) via Hilbert transform approximation.

    The envelope is the magnitude of the analytic signal.
    Highlights energy concentrations independent of phase.
    """
    start = time.perf_counter()

    if volume.ndim == 2:
        volume = volume[np.newaxis, :, :]

    result = np.zeros_like(volume, dtype=np.float64)

    for i in range(volume.shape[0]):
        for x in range(volume.shape[1]):
            trace = volume[i, x, :].astype(np.float64)
            n = len(trace)

            # Hilbert transform via FFT
            spectrum = np.fft.fft(trace)
            h = np.zeros(n)
            if n > 0:
                h[0] = 1
                if n % 2 == 0:
                    h[n // 2] = 1
                    h[1 : n // 2] = 2
                else:
                    h[1 : (n + 1) // 2] = 2
            analytic = np.fft.ifft(spectrum * h)
            result[i, x, :] = np.abs(analytic)

    elapsed = (time.perf_counter() - start) * 1000

    cm = ContrastMetadata(
        source_domain=ContrastSourceDomain(
            domain="reflectivity",
            measurement_units="amplitude",
            acquisition_type="seismic_3d",
        ),
        processing_chain=[
            VisualTransform(
                transform_type="custom",
                parameters={"method": "hilbert_transform_fft"},
                order_index=0,
                contrast_amplification_factor=1.0,
                notes="Instantaneous amplitude via analytic signal.",
            ),
        ],
        physical_proxy=PhysicalProxy(
            proxy_name="instantaneous_energy",
            proxy_type="calibrated_proxy",
            physical_units="amplitude",
        ),
        confidence_class=ConfidenceClass(
            signal_confidence=0.80,
            interpretation_confidence=0.50,
            anomalous_contrast_risk="low",
            risk_factors=["end_effects", "bandwidth_dependence"],
        ),
        requires_non_visual_confirmation=True,
        created_by="compute_envelope",
    )

    return AttributeResult(
        name="envelope",
        volume=result.squeeze(),
        units="amplitude",
        equation_reference="Taner, Koehler & Sheriff (1979), Complex trace analysis",
        uncertainty=0.08,
        contrast_metadata=cm,
        processing_time_ms=round(elapsed, 2),
        notes="Envelope (instantaneous amplitude). Phase-independent energy measure.",
    )


# ---------------------------------------------------------------------------
# 5. COMPUTE ATTRIBUTES — Main Orchestrator
# ---------------------------------------------------------------------------

SUPPORTED_ATTRIBUTES = {
    "coherence": "Semblance-based coherence for discontinuity detection",
    "curvature_most_positive": "Most-positive curvature (anticlines, domes)",
    "curvature_most_negative": "Most-negative curvature (synclines, channels)",
    "curvature_gaussian": "Gaussian curvature (dome/saddle discriminator)",
    "curvature_mean": "Mean curvature (average structural bending)",
    "rms_amplitude": "RMS amplitude in sliding window",
    "envelope": "Instantaneous amplitude (Hilbert envelope)",
    "spectral": "Spectral decomposition (STFT frequency band slices)",
}


def compute_attributes(
    volume: np.ndarray,
    attribute_list: list[str],
    sample_rate_ms: float = 4.0,
    coherence_window: tuple[int, int, int] = (3, 3, 5),
    spectral_bands_hz: list[tuple[float, float]] | None = None,
) -> AttributeStack:
    """
    Main orchestrator: compute multiple seismic attributes from a volume.

    Args:
        volume: 2D or 3D seismic array
        attribute_list: list of attribute names from SUPPORTED_ATTRIBUTES
        sample_rate_ms: sampling interval
        coherence_window: window for coherence computation
        spectral_bands_hz: frequency bands for spectral decomposition

    Returns:
        AttributeStack with all computed attributes + ContrastMetadata
    """
    import hashlib

    checksum = hashlib.sha256(volume.tobytes()).hexdigest()[:16]

    stack = AttributeStack(source_volume_checksum=checksum)

    for attr_name in attribute_list:
        if attr_name == "coherence":
            result = compute_coherence(volume, window_shape=coherence_window)
            stack.add(result)

        elif attr_name.startswith("curvature_"):
            curv_type = attr_name.replace("curvature_", "")
            result = compute_curvature(volume, curvature_type=curv_type)
            stack.add(result)

        elif attr_name == "rms_amplitude":
            result = compute_rms_amplitude(volume)
            stack.add(result)

        elif attr_name == "envelope":
            result = compute_envelope(volume)
            stack.add(result)

        elif attr_name == "spectral":
            results = compute_spectral_decomposition(
                volume,
                sample_rate_ms=sample_rate_ms,
                freq_bands_hz=spectral_bands_hz,
            )
            for r in results:
                stack.add(r)

        else:
            logger.warning(
                f"Unknown attribute '{attr_name}'. Supported: {list(SUPPORTED_ATTRIBUTES.keys())}"
            )

    return stack


# ---------------------------------------------------------------------------
# SeismicAttributeTool — BaseTool for ToolRegistry
# ---------------------------------------------------------------------------


class SeismicAttributeTool(BaseTool):
    """
    GEOX Plane 1-2 Bridge: Classical Seismic Attribute Computation.

    Computes governed seismic attributes from trace data.
    Every output carries ContrastMetadata (Contrast Canon) and provenance.

    Inputs:
        volume       (np.ndarray)  — 2D/3D seismic data
        attributes   (list[str])   — attribute names to compute
        sample_rate_ms (float)     — sampling interval
        location     (CoordinatePoint) — geographic anchor

    Outputs:
        GeoToolResult with attribute metrics + full ContrastMetadata
    """

    @property
    def name(self) -> str:
        return "SeismicAttributeTool"

    @property
    def description(self) -> str:
        return (
            "Classical seismic attribute computation tool. Computes coherence, "
            "curvature, spectral decomposition, RMS amplitude, and envelope. "
            "All outputs carry Contrast Canon metadata (physical contrast ≠ "
            "perceptual contrast). Requires non-visual confirmation."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        if "volume" not in inputs:
            return False
        if "attributes" not in inputs:
            return False
        if not isinstance(inputs["attributes"], list):
            return False
        return True

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=(
                    "Invalid inputs. Required: 'volume' (ndarray), "
                    f"'attributes' (list from {list(SUPPORTED_ATTRIBUTES.keys())})"
                ),
            )

        start = time.perf_counter()
        volume = inputs["volume"]
        attribute_list = inputs["attributes"]
        sample_rate_ms = inputs.get("sample_rate_ms", 4.0)
        location = inputs.get("location", CoordinatePoint(latitude=0.0, longitude=0.0))
        if isinstance(location, dict):
            location = CoordinatePoint(**location)

        try:
            stack = compute_attributes(
                volume,
                attribute_list,
                sample_rate_ms=sample_rate_ms,
            )
        except Exception as exc:
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error=f"Attribute computation failed: {exc}",
            )

        # Build GeoQuantity outputs
        prov = _make_provenance(
            source_id=f"SAT-{stack.source_volume_checksum}",
            source_type="simulator",
            confidence=0.70,
            checksum=stack.source_volume_checksum,
        )

        quantities = []
        for attr_name, result in stack.attributes.items():
            # Mean value as representative metric
            mean_val = float(np.mean(result.volume))
            std_val = float(np.std(result.volume))

            quantities.append(
                _make_quantity(
                    round(mean_val, 6),
                    result.units,
                    f"attr_mean_{attr_name}",
                    location,
                    prov,
                    min(0.15, max(0.03, result.uncertainty)),
                )
            )
            quantities.append(
                _make_quantity(
                    round(std_val, 6),
                    result.units,
                    f"attr_std_{attr_name}",
                    location,
                    prov,
                    min(0.15, max(0.03, result.uncertainty)),
                )
            )

        # Raw output with governance
        raw_output = {
            "source_volume_checksum": stack.source_volume_checksum,
            "attributes_computed": stack.names,
            "governance_summary": stack.governance_summary,
            "attribute_details": {
                name: {
                    "units": r.units,
                    "equation": r.equation_reference,
                    "uncertainty": r.uncertainty,
                    "processing_time_ms": r.processing_time_ms,
                    "contrast_risk": r.contrast_metadata.confidence_class.anomalous_contrast_risk,
                    "governance_status": r.contrast_metadata.governance_status,
                    "notes": r.notes,
                }
                for name, r in stack.attributes.items()
            },
            "contrast_canon_enforced": True,
            "perception_bridge_warning": (
                "All attribute outputs require non-visual confirmation. "
                "Classical attributes are transparent math but interpretation "
                "remains human/agent responsibility. RGB ≠ truth."
            ),
        }

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            quantities=quantities,
            raw_output=raw_output,
            metadata={
                "tool_version": "SAT-GEOX-v0.1.0",
                "attributes_computed": stack.names,
                "governance_summary": stack.governance_summary,
                "contrast_canon_enforced": True,
                "source_checksum": stack.source_volume_checksum,
            },
            tool_name=self.name,
            latency_ms=round(latency_ms, 2),
            success=True,
        )
