"""
GEOX ENGINE Layer — Contrast-Aware Processing Core
DITEMPA BUKAN DIBERI

The ENGINE implements the Theory of Anomalous Contrast (ToAC) from the
THEORY layer. It provides:

  - ContrastSpace: Unified representation of all contrast types
  - TransformRegistry: Catalog of visual transforms with risk metadata
  - AnomalyDetector: Automatic detection of conflation errors
"""

from .contrast_space import ContrastSpace, ContrastFeature
from .transform_registry import TransformRegistry, TransformProfile, get_registry
from .anomaly_detector import AnomalyDetector, ConflationAlert

__all__ = [
    "ContrastSpace",
    "ContrastFeature",
    "TransformRegistry",
    "TransformProfile",
    "get_registry",
    "AnomalyDetector",
    "ConflationAlert",
]
