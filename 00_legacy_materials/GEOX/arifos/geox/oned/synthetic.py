"""
GEOX 1D Synthetic Seismic — Wavelet convolution.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field

from .canon9_profile import Canon9Profile
from .reflectivity import ZoeppritzModel


class Wavelet(BaseModel):
    """Seismic wavelet definition."""

    amplitude: np.ndarray = Field(..., description="Wavelet amplitudes")
    time: np.ndarray = Field(..., description="Time samples [s]")
    dt: float = Field(..., description="Sample interval [s]")
    fdom: float = Field(..., description="Dominant frequency [Hz]")

    class Config:
        arbitrary_types_allowed = True

    @property
    def duration(self) -> float:
        """Wavelet duration [s]."""
        return len(self.amplitude) * self.dt

    @classmethod
    def ricker(cls, fdom: float, dt: float, duration: float = 0.2) -> Wavelet:
        """
        Generate Ricker wavelet.

        Ricker(t) = (1 - 2π²f²t²) × exp(-π²f²t²)
        """
        t = np.arange(-duration / 2, duration / 2, dt)
        ricker = (1 - 2 * (np.pi * fdom * t) ** 2) * np.exp(-((np.pi * fdom * t) ** 2))
        return cls(amplitude=ricker, time=t, dt=dt, fdom=fdom)

    @classmethod
    def ormsby(
        cls,
        f1: float,
        f2: float,
        f3: float,
        f4: float,
        dt: float,
        duration: float = 0.2,
    ) -> Wavelet:
        """
        Generate Ormsby (trapezoidal) wavelet.
        Common for broadband seismic.
        """
        # Simplified Ormsby
        t = np.arange(-duration / 2, duration / 2, dt)
        fcent = (f2 + f3) / 2
        ricker = (1 - 2 * (np.pi * fcent * t) ** 2) * np.exp(
            -((np.pi * fcent * t) ** 2)
        )
        return cls(amplitude=ricker, time=t, dt=dt, fdom=fcent)


class SyntheticCMP(BaseModel):
    """
    Synthetic Common Midpoint gather.
    1D seismic traces at different angles.
    """

    traces: np.ndarray = Field(..., description="Seismic traces [n_samples, n_angles]")
    time: np.ndarray = Field(..., description="Two-way time [s]")
    angles: np.ndarray = Field(..., description="Incidence angles [degrees]")
    wavelet: Wavelet = Field(..., description="Source wavelet")

    # Source profile info
    well_id: str = Field(..., description="Source well ID")

    class Config:
        arbitrary_types_allowed = True

    @property
    def n_samples(self) -> int:
        return self.traces.shape[0]

    @property
    def n_angles(self) -> int:
        return self.traces.shape[1]

    def get_angle_gather(self, angle_idx: int) -> np.ndarray:
        """Extract trace at specific angle."""
        return self.traces[:, angle_idx]

    def get_stack(self, max_angle: float = 30.0) -> np.ndarray:
        """Partial angle stack."""
        mask = self.angles <= max_angle
        if not np.any(mask):
            return self.traces[:, 0]
        return np.mean(self.traces[:, mask], axis=1)

    def extract_amplitude(
        self, time_window: tuple[float, float], angle: float
    ) -> float:
        """Extract amplitude in time window at given angle."""
        angle_idx = np.argmin(np.abs(self.angles - angle))
        time_mask = (self.time >= time_window[0]) & (self.time <= time_window[1])
        return np.mean(self.traces[time_mask, angle_idx])


class SyntheticSeismic:
    """
    1D synthetic seismic generator.

    Workflow:
    1. Compute reflectivity from CANON_9 profile
    2. Convolve with wavelet
    3. Time-depth conversion
    """

    def __init__(self, wavelet: Wavelet | None = None, dz: float = 0.5):
        self.wavelet = wavelet or Wavelet.ricker(fdom=30, dt=0.004)
        self.dz = dz  # Depth sample interval [m]
        self.reflectivity = ZoeppritzModel(approximation="aki-richards")

    def depth_to_time(
        self, profile: Canon9Profile, reflectivity_depth: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Convert reflectivity from depth to time domain.

        Returns:
            (reflectivity_time, time_axis)
        """
        # Get interval velocities
        depths = profile.depths
        vp = profile.get_property("vp")

        # Compute two-way travel time
        dt_two_way = 2 * np.diff(depths) / vp[:-1]  # [s]
        time = np.cumsum(np.concatenate([[0], dt_two_way]))

        # Regular time grid
        dt = self.wavelet.dt
        t_max = time[-1] + 0.5  # Add buffer
        time_reg = np.arange(0, t_max, dt)

        # Interpolate reflectivity to regular time
        # Use linear interpolation
        refl_time = np.zeros(len(time_reg))
        for i, t in enumerate(time_reg):
            # Find closest depth sample
            idx = np.argmin(np.abs(time - t))
            if idx < len(reflectivity_depth):
                refl_time[i] = reflectivity_depth[idx]

        return refl_time, time_reg

    def generate(
        self, profile: Canon9Profile, angles: np.ndarray | None = None
    ) -> SyntheticCMP:
        """
        Generate synthetic CMP gather from profile.

        Args:
            profile: CANON_9 profile
            angles: Incidence angles [degrees]. Default: [0, 5, 10, 15, 20, 25, 30]

        Returns:
            SyntheticCMP with traces at each angle
        """
        if angles is None:
            angles = np.arange(0, 31, 5)  # 0-30 degrees

        angles_rad = np.deg2rad(angles)

        # Compute reflectivity for each angle
        reflectivity = self.reflectivity.compute_reflectivity(profile, angles_rad)

        # For each angle: depth-to-time + convolve
        n_angles = len(angles)

        # First convert depth reflectivity to time
        # Use normal incidence for time conversion (Vp only)
        refl_0 = reflectivity[:, 0]
        refl_time, time_axis = self.depth_to_time(profile, refl_0)

        # Allocate output traces
        n_samples = len(time_axis)
        traces = np.zeros((n_samples, n_angles))

        # Convolve wavelet with reflectivity for each angle
        wavelet_amp = self.wavelet.amplitude

        for i in range(n_angles):
            # Use angle-dependent reflectivity
            refl = (
                reflectivity[:, i] if i < reflectivity.shape[1] else reflectivity[:, 0]
            )

            # Interpolate to time grid
            refl_time_interp = np.interp(
                time_axis,
                np.linspace(time_axis[0], time_axis[-1], len(refl)),
                refl,
                left=0,
                right=0,
            )

            # Convolve
            trace = np.convolve(refl_time_interp, wavelet_amp, mode="same")
            traces[:, i] = trace

        return SyntheticCMP(
            traces=traces,
            time=time_axis,
            angles=angles,
            wavelet=self.wavelet,
            well_id=profile.well_id,
        )

    def extract_at_depth(
        self, synthetic: SyntheticCMP, profile: Canon9Profile, depth: float
    ) -> np.ndarray:
        """
        Extract synthetic amplitudes at a specific depth.
        Converts depth to time, finds amplitude.
        """
        # Find time for this depth
        t_target = profile.depth_to_time(depth)

        # Find closest time sample
        time_idx = np.argmin(np.abs(synthetic.time - t_target))

        return synthetic.traces[time_idx, :]
