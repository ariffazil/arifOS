"""
GEOX 1D CANON_9 Profile — Vertical column state.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field
from typing import Literal


class DepthSample(BaseModel):
    """
    CANON_9 at a single depth sample.
    The 9 fundamental geophysical variables.
    """
    
    # Depth position
    depth: float = Field(..., description="True vertical depth (TVD) [m]")
    
    # Mechanical (3)
    density: float = Field(..., ge=1000, le=3000, description="Bulk density ρ [kg/m³]")
    vp: float = Field(..., ge=1500, le=8000, description="P-wave velocity Vp [m/s]")
    vs: float = Field(..., ge=0, le=5000, description="S-wave velocity Vs [m/s]")
    
    # EM-Thermal (3)
    resistivity: float = Field(..., ge=0.01, le=10000, description="Electrical resistivity ρₑ [Ω·m]")
    magnetic_suscept: float = Field(default=0.0, ge=-1, le=100, description="Magnetic susceptibility χ [SI]")
    thermal_conduct: float = Field(default=2.5, ge=0.5, le=10, description="Thermal conductivity k [W/(m·K)]")
    
    # State (3)
    pressure: float = Field(..., ge=0, le=200e6, description="Pore pressure P [Pa]")
    temperature: float = Field(..., ge=273, le=800, description="Temperature T [K]")
    porosity: float = Field(..., ge=0, le=1, description="Porosity φ [fraction]")
    porosity_type: Literal["total", "effective", "isolated", "primary", "secondary"] = "total"
    
    # Fluid state (LAYER-2 context)
    sw: float = Field(default=1.0, ge=0, le=1, description="Water saturation Sw [fraction]")
    salinity: float = Field(default=35000, ge=0, le=300000, description="Salinity [ppm]")
    
    # Provenance (F11)
    sources: dict[str, str] = Field(default_factory=dict, description="Measurement sources")
    
    @property
    def acoustic_impedance(self) -> float:
        """I = ρ × Vp [kg/(m²·s)]"""
        return self.density * self.vp
    
    @property
    def shear_impedance(self) -> float:
        """Is = ρ × Vs [kg/(m²·s)]"""
        return self.density * self.vs
    
    @property
    def poisson_ratio(self) -> float:
        """ν = (Vp² - 2Vs²) / 2(Vp² - Vs²) [dimensionless]"""
        if self.vs == 0:
            return 0.5
        return (self.vp**2 - 2*self.vs**2) / (2*(self.vp**2 - self.vs**2))
    
    @property
    def bulk_modulus(self) -> float:
        """K = ρ(Vp² - 4/3 Vs²) [Pa]"""
        return self.density * (self.vp**2 - (4/3)*self.vs**2)
    
    @property
    def shear_modulus(self) -> float:
        """μ = ρ × Vs² [Pa]"""
        return self.density * self.vs**2
    
    def to_array(self) -> np.ndarray:
        """Return CANON_9 as numpy array [ρ, Vp, Vs, ρₑ, χ, k, P, T, φ]"""
        return np.array([
            self.density, self.vp, self.vs,
            self.resistivity, self.magnetic_suscept, self.thermal_conduct,
            self.pressure, self.temperature, self.porosity
        ])
    
    @classmethod
    def from_array(cls, depth: float, arr: np.ndarray, **kwargs) -> DepthSample:
        """Create from CANON_9 array."""
        return cls(
            depth=depth,
            density=arr[0], vp=arr[1], vs=arr[2],
            resistivity=arr[3], magnetic_suscept=arr[4], thermal_conduct=arr[5],
            pressure=arr[6], temperature=arr[7], porosity=arr[8],
            **kwargs
        )


class Canon9Profile(BaseModel):
    """
    1D vertical column of CANON_9 samples.
    The canonical GEOX state representation.
    """
    
    well_id: str = Field(..., description="Well identifier")
    samples: list[DepthSample] = Field(default_factory=list)
    
    # Time-depth relationship
    tdr_depths: list[float] = Field(default_factory=list, description="Check-shot depths")
    tdr_times: list[float] = Field(default_factory=list, description="Two-way times [s]")
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def depths(self) -> np.ndarray:
        """Return depth array [m]."""
        return np.array([s.depth for s in self.samples])
    
    @property
    def dz(self) -> float:
        """Sample interval [m]."""
        if len(self.samples) < 2:
            return 0.5
        return np.mean(np.diff(self.depths))
    
    def get_property(self, name: str) -> np.ndarray:
        """Extract property array by name."""
        return np.array([getattr(s, name) for s in self.samples])
    
    def time_to_depth(self, time_s: float) -> float:
        """Convert two-way time to depth using TDR."""
        if len(self.tdr_depths) < 2:
            # Linear velocity approximation
            vavg = np.mean(self.get_property("vp"))
            return time_s * vavg / 2
        return np.interp(time_s, self.tdr_times, self.tdr_depths)
    
    def depth_to_time(self, depth_m: float) -> float:
        """Convert depth to two-way time using TDR."""
        if len(self.tdr_depths) < 2:
            vavg = np.mean(self.get_property("vp"))
            return 2 * depth_m / vavg
        return np.interp(depth_m, self.tdr_depths, self.tdr_times)
    
    def resample(self, new_depths: np.ndarray) -> Canon9Profile:
        """Resample profile to new depth grid."""
        old_depths = self.depths
        new_samples = []
        
        for d in new_depths:
            # Find bracketing samples
            idx = np.searchsorted(old_depths, d)
            if idx == 0:
                new_samples.append(self.samples[0])
            elif idx >= len(self.samples):
                new_samples.append(self.samples[-1])
            else:
                # Linear interpolation
                d0, d1 = old_depths[idx-1], old_depths[idx]
                s0, s1 = self.samples[idx-1], self.samples[idx]
                w = (d - d0) / (d1 - d0)
                
                new_samples.append(DepthSample(
                    depth=d,
                    density=s0.density + w * (s1.density - s0.density),
                    vp=s0.vp + w * (s1.vp - s1.vp),
                    vs=s0.vs + w * (s1.vs - s0.vs),
                    resistivity=s0.resistivity + w * (s1.resistivity - s0.resistivity),
                    magnetic_suscept=s0.magnetic_suscept + w * (s1.magnetic_suscept - s0.magnetic_suscept),
                    thermal_conduct=s0.thermal_conduct + w * (s1.thermal_conduct - s0.thermal_conduct),
                    pressure=s0.pressure + w * (s1.pressure - s0.pressure),
                    temperature=s0.temperature + w * (s1.temperature - s0.temperature),
                    porosity=s0.porosity + w * (s1.porosity - s0.porosity),
                    sw=s0.sw + w * (s1.sw - s0.sw),
                    salinity=s0.salinity,
                    sources={"resampling": "linear interpolation"}
                ))
        
        return Canon9Profile(well_id=self.well_id, samples=new_samples)
    
    def to_telemetry(self) -> str:
        """Canonical telemetry string."""
        n = len(self.samples)
        if n == 0:
            return "[CANON9_PROFILE | empty | NO SEAL]"
        
        avg_phi = np.mean(self.get_property("porosity"))
        avg_vp = np.mean(self.get_property("vp"))
        
        return (
            f"[CANON9_PROFILE | {self.well_id} | n={n} | "
            f"z:[{self.samples[0].depth:.0f},{self.samples[-1].depth:.0f}]m | "
            f"⟨φ⟩={avg_phi:.3f} | ⟨Vp⟩={avg_vp:.0f}m/s | SEALED]"
        )
