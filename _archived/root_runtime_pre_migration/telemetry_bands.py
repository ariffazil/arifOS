"""
arifOS v2.0 — Telemetry Health Bands
═══════════════════════════════════════════════════════════════════════════
Defines metabolic health categories (HEALTHY, WARNING, CRITICAL) for 
constitutional metrics.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from enum import Enum
from typing import Dict, Any

class HealthCategory(str, Enum):
    HEALTHY  = "HEALTHY"
    WARNING  = "WARNING"
    CRITICAL = "CRITICAL"

class TelemetryBands:
    """
    Maps raw metrics to health bands.
    """
    
    @staticmethod
    def get_ds_band(ds: float) -> HealthCategory:
        if ds <= 0.0: return HealthCategory.HEALTHY
        if ds <= 0.2: return HealthCategory.WARNING
        return HealthCategory.CRITICAL

    @staticmethod
    def get_peace2_band(peace2: float) -> HealthCategory:
        if peace2 >= 0.70: return HealthCategory.HEALTHY
        if peace2 >= 0.40: return HealthCategory.WARNING
        return HealthCategory.CRITICAL

    @staticmethod
    def get_omega_band(omega: float) -> HealthCategory:
        if omega >= 0.95: return HealthCategory.HEALTHY
        if omega >= 0.85: return HealthCategory.WARNING
        return HealthCategory.CRITICAL

    @staticmethod
    def get_w3_band(w3: float) -> HealthCategory:
        if w3 >= 0.95: return HealthCategory.HEALTHY
        if w3 >= 0.80: return HealthCategory.WARNING
        return HealthCategory.CRITICAL

    @staticmethod
    def get_shadow_band(shadow: float) -> HealthCategory:
        if shadow < 0.10: return HealthCategory.HEALTHY
        if shadow < 0.30: return HealthCategory.WARNING
        return HealthCategory.CRITICAL

    @classmethod
    def compute_all_bands(cls, metrics: Dict[str, float]) -> Dict[str, str]:
        return {
            "ds_band": cls.get_ds_band(metrics.get("delta_s", metrics.get("ds", 0.0))).value,
            "peace2_band": cls.get_peace2_band(metrics.get("peace2", 1.0)).value,
            "omega_band": cls.get_omega_band(metrics.get("omega_ortho", metrics.get("omega", 1.0))).value,
            "w3_band": cls.get_w3_band(metrics.get("w3", 1.0)).value,
            "shadow_band": cls.get_shadow_band(metrics.get("shadow_score", metrics.get("shadow", 0.0))).value,
        }
