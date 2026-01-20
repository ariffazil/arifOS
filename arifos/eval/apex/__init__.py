"""
APEX Measurement Layer (v45.0)

This module provides evaluation harness for APEX PRIME judiciary metrics.
It is separate from arifos to allow independent testing and iteration.

**v45.0 Update:** Aligned with Phoenix-72 constitutional framework and Track B v45 specs.

Usage:
    from arifos_eval.apex import ApexMeasurement

    apex = ApexMeasurement("apex_standards_v45.json")
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

__version__ = "45.0.0"
__epoch__ = "v45.0"
