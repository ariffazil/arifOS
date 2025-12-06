"""
APEX Measurement Layer (v36.1Ω)

This module provides evaluation harness for APEX PRIME judiciary metrics.
It is separate from arifos_core to allow independent testing and iteration.

Usage:
    from arifos_eval.apex import ApexMeasurement

    apex = ApexMeasurement("apex_standards_v36.json")
    result = apex.judge(dials, output_text, output_metrics)
"""

from .apex_measurements import (
    ApexMeasurement,
    Normalizer,
    AntiHantuDetector,
    measure_genius,
    measure_dark_cleverness,
    compute_vitality,
)

__all__ = [
    "ApexMeasurement",
    "Normalizer",
    "AntiHantuDetector",
    "measure_genius",
    "measure_dark_cleverness",
    "compute_vitality",
]

__version__ = "36.1.0"
__epoch__ = "v36.1Ω"
