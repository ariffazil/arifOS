"""
GEOX 1D Essential ToAC — Minimal contrast governance.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field
from typing import Literal

from .canon9_profile import Canon9Profile
from .synthetic import Wavelet, SyntheticSeismic


class Alert(BaseModel):
    """ToAC alert for contrast violations."""
    type: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    floor: str = Field(..., description="Constitutional floor violated")
    message: str
    mitigation: str | None = None


class StabilityScore(BaseModel):
    """Frequency stability test result."""
    stable: bool
    variance: float
    recommendation: str


def check_tuning_risk(
    bed_thickness: float,
    wavelet: Wavelet,
    vp: float | None = None
) -> Alert | None:
    """
    ESSENTIAL ToAC: Bed thickness vs. wavelength check.
    
    Physics: Bed thickness < λ/4 causes tuning - amplitude is NOT
    proportional to reflectivity contrast.
    
    ToAC Risk: Interpreter mistakes tuning amplitude for fluid effect.
    Floor: F2 Truth (amplitude misinterpreted as physical property)
    
    Args:
        bed_thickness: Layer thickness [m]
        wavelet: Source wavelet
        vp: P-wave velocity [m/s] (uses wavelet default if None)
    
    Returns:
        Alert if tuning risk detected, None otherwise
    """
    velocity = vp if vp is not None else 3000.0  # Default if unknown
    wavelength = velocity / wavelet.fdom
    tuning_threshold = wavelength / 4
    
    if bed_thickness < tuning_threshold:
        return Alert(
            type="TUNING_RISK",
            severity="HIGH",
            floor="F2_Truth",
            message=(
                f"Bed thickness {bed_thickness:.2f}m < λ/4={tuning_threshold:.1f}m "
                f"(f={wavelet.fdom}Hz, Vp={velocity:.0f}m/s). "
                "Amplitude unreliable for Sw/φ estimation."
            ),
            mitigation=(
                "Use thickness-independent inversion or spectral decomposition. "
                "Do not interpret amplitude as direct fluid indicator."
            )
        )
    return None


def propagate_td_uncertainty(
    profile: Canon9Profile,
    td_time_std: float = 0.005  # 5ms standard error on TDR
) -> Canon9Profile:
    """
    ESSENTIAL ToAC: Propagate time-depth uncertainty to depth axis.
    
    Physics: Check-shot times have measurement uncertainty.
    This propagates to depth uncertainty via local velocity.
    
    ToAC Risk: Sharp depth picks hide true uncertainty.
    Floor: F4 Clarity (uncertainty must be explicit)
    
    Args:
        profile: CANON_9 profile
        td_time_std: Time-depth curve uncertainty [s]
    
    Returns:
        Profile with depth_uncertainty field added to samples
    """
    for sample in profile.samples:
        # Uncertainty propagation: dz = dt × Vp / 2 (two-way)
        dz_std = td_time_std * sample.vp / 2
        
        # Store uncertainty in sample metadata (F4 requirement)
        if not hasattr(sample, 'metadata'):
            sample.metadata = {}
        sample.metadata['depth_uncertainty'] = dz_std
        sample.metadata['td_time_std'] = td_time_std
    
    return profile


def dual_frequency_stability_test(
    profile: Canon9Profile,
    f1: float = 25.0,
    f2: float = 35.0,
    angles: np.ndarray | None = None
) -> StabilityScore:
    """
    ESSENTIAL ToAC: Two-frequency stability test.
    
    Physics: Different frequencies sample different effective bed thicknesses.
    If inversion changes dramatically with frequency → display artifact.
    
    ToAC Risk: Single-frequency overconfidence (F7 violation).
    Floor: F7 Humility (must acknowledge frequency-dependent uncertainty)
    
    Args:
        profile: CANON_9 profile to test
        f1: First frequency [Hz]
        f2: Second frequency [Hz]
        angles: Incidence angles (default 0-30°)
    
    Returns:
        StabilityScore indicating if interpretation is frequency-stable
    """
    if angles is None:
        angles = np.arange(0, 31, 5)
    
    # Generate synthetics at two frequencies
    syn1 = SyntheticSeismic(Wavelet.ricker(f1, dt=0.004)).generate(profile, angles)
    syn2 = SyntheticSeismic(Wavelet.ricker(f2, dt=0.004)).generate(profile, angles)
    
    # Compute amplitude envelope difference (simplified stability metric)
    # In full implementation: run inversion, compare φ(z), Sw(z)
    env1 = np.abs(hilbert_transform(syn1.traces[:, 0]))  # Near trace
    env2 = np.abs(hilbert_transform(syn2.traces[:, 0]))
    
    # Normalize
    env1 = env1 / (np.max(env1) + 1e-10)
    env2 = env2 / (np.max(env2) + 1e-10)
    
    # Variance between frequency responses
    variance = np.mean((env1 - env2) ** 2)
    
    # Threshold: variance > 0.05 indicates significant frequency dependence
    threshold = 0.05
    
    if variance > threshold:
        return StabilityScore(
            stable=False,
            variance=variance,
            recommendation=(
                f"888_HOLD: Frequency-dependent artifacts detected "
                f"(variance={variance:.3f} > {threshold}). "
                "Interpretation unstable across frequencies. "
                "Consider multi-frequency inversion or spectral decomposition."
            )
        )
    
    return StabilityScore(
        stable=True,
        variance=variance,
        recommendation=f"Frequency stable (variance={variance:.3f}). Proceed with caution."
    )


def hilbert_transform(signal: np.ndarray) -> np.ndarray:
    """Simple Hilbert transform for envelope extraction."""
    from scipy.fft import fft, ifft
    n = len(signal)
    h = np.zeros(n)
    h[0] = 1
    h[1:n//2] = 2
    if n % 2 == 0:
        h[n//2] = 1
    
    xf = fft(signal)
    x_hilbert = ifft(xf * h)
    return x_hilbert.real


def run_essential_toac_checks(
    profile: Canon9Profile,
    wavelet: Wavelet,
    layer_thicknesses: list[float] | None = None
) -> list[Alert]:
    """
    Run all essential ToAC checks on a 1D profile.
    
    Returns list of alerts (empty if all checks pass).
    """
    alerts = []
    
    # 1. Tuning check for key layers
    if layer_thicknesses:
        for thickness in layer_thicknesses:
            alert = check_tuning_risk(thickness, wavelet)
            if alert:
                alerts.append(alert)
    
    # 2. TDR uncertainty propagation (side effect: adds metadata)
    propagate_td_uncertainty(profile)
    
    # 3. Dual-frequency stability
    stability = dual_frequency_stability_test(profile)
    if not stability.stable:
        alerts.append(Alert(
            type="FREQUENCY_INSTABILITY",
            severity="MEDIUM",
            floor="F7_Humility",
            message=stability.recommendation,
            mitigation="Use multi-frequency inversion or increase prior uncertainty."
        ))
    
    return alerts


# Export essential functions
__all__ = [
    "check_tuning_risk",
    "propagate_td_uncertainty",
    "dual_frequency_stability_test",
    "run_essential_toac_checks",
    "Alert",
    "StabilityScore",
]
