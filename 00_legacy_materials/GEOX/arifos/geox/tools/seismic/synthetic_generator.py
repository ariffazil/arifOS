"""
SeismicSyntheticGenerator — ToAC Grounded Structural Synthetic Engine
DITEMPA BUKAN DIBERI

Generates synthetic seismic data informed by a structural model.
Allows the Earth Witness to "visualize" subsurface candidates even without
external SEGY ingestion.
"""

from __future__ import annotations

import numpy as np
from scipy import signal


class SeismicSyntheticGenerator:
    """
    Generator for governed synthetic seismic lines.
    """

    def generate_extensional_block(
        self,
        shape: tuple[int, int] = (256, 512),
        dt: float = 0.004,
        dominant_freq: float = 30.0,
    ) -> np.ndarray:
        """
        Generate a synthetic extensional fault block.
        """
        nt, nx = shape

        # 1. Create reflectors (impedance model)
        # Random but spatially coherent layers
        np.arange(nt)
        reflectivity = np.zeros((nt, nx))

        # Add 10 continuous reflectors
        reflector_positions = np.linspace(0.1 * nt, 0.9 * nt, 10).astype(int)
        for pos in reflector_positions:
            # Add some "geological" noise to the thickness
            pos_offset = np.random.normal(0, 2)
            reflectivity[pos + int(pos_offset), :] = np.random.uniform(0.1, 0.5)

        # 2. Add Fault Displacement
        # NW-SE trending normal fault
        fault_location = nx // 2
        for x in range(nx):
            if x > fault_location:
                # Displace down by 20 samples
                reflectivity[:, x] = np.roll(reflectivity[:, x], 20)

        # 3. Wavelet Convolution (Ricker)
        wavelet = self._ricker_wavelet(dominant_freq, dt)

        # Convolve along time axis
        seismic = np.zeros_like(reflectivity)
        for x in range(nx):
            seismic[:, x] = signal.convolve(reflectivity[:, x], wavelet, mode="same")

        # 4. Add Noise (low level for clarity)
        noise = np.random.normal(0, 0.05, seismic.shape)
        return seismic + noise

    def _ricker_wavelet(self, f: float, dt: float) -> np.ndarray:
        """Standard Ricker wavelet."""
        n = int(2.0 / (f * dt))
        if n % 2 == 0:
            n += 1

        t = np.linspace(-n * dt / 2, n * dt / 2, n)
        a = (np.pi * f * t) ** 2
        return (1.0 - 2.0 * a) * np.exp(-a)


def generate_demo_seismic() -> np.ndarray:
    """Convenience function for demo ingestion."""
    gen = SeismicSyntheticGenerator()
    return gen.generate_extensional_block()
