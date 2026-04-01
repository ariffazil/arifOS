"""
GEOX Seismic Image Package — Image-First Seismic Intelligence

Physics-based, governed seismic interpretation from 2D image sections.

⚠️  IMAGE-FIRST DISCLAIMER:
    This package operates on IMAGE-DOMAIN PROXIES of seismic data.
    Outputs are NOT equivalent to trace-derived seismic attributes.
    They are valid for: interpretation assistance, pattern retrieval,
    horizon candidate detection, and facies segmentation WITH UNCERTAINTY.

    They are NOT valid for: AVO analysis, quantitative rock physics,
    or definitive reservoir property estimation without trace-domain validation.

Earth Scale Requirements:
    - Vertical units must be declared (meters, feet, or TWT)
    - Pixel-to-meter ratio must be known or estimated
    - Aspect ratio distortion must be < 10%

Constitutional Floors:
    F2 — All outputs labeled "PROXY — Image Domain"
    F4 — Units and scales mandatory
    F7 — Uncertainty quantified and exposed
    F9 — Anti-hallucination via QC gates

Seal: DITEMPA BUKAN DIBERI
"""

__version__ = "0.1.0-alpha"
__author__ = "Muhammad Arif bin Fazil"
__status__ = "PRE-PRODUCTION"

from .ingest import ingest_seismic_image
from .qc import qc_seismic_image
from .features import extract_texture_attributes
from .reflectors import detect_reflectors
from .faults import detect_fault_candidates
from .facies import segment_facies
from .retrieval import compare_sections
from .reasoning import reason_seismic_scene
from .audit import audit_seismic_interpretation

__all__ = [
    "ingest_seismic_image",
    "qc_seismic_image", 
    "extract_texture_attributes",
    "detect_reflectors",
    "detect_fault_candidates",
    "segment_facies",
    "compare_sections",
    "reason_seismic_scene",
    "audit_seismic_interpretation",
]
