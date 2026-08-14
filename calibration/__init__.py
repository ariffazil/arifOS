"""
Type B Calibration Audit — Post-SEAL reality contact substrate.

Doctrine reference: arifOS/CANON/CALIBRATION_AUDIT_DOCTRINE.md (forged 2026-08-11).

This is SUBSTRATE-LEVEL safety, not procedural gates:
  - Every SEAL carrying prediction metadata is automatically recorded
  - Outcome data is sourced from arifFlow/A-FORGE (held-out per SPC principle)
  - Brier score decomposition runs continuously in background
  - Drift alerts write FIR entries automatically
  - NEVER blocks execution
  - NEVER requires Arif invocation

This addresses:
  - VOID 4 (Floor Learning): concrete feedback mechanism
  - Type B reality audit: statistical calibration drift, not just outcome failure
  - Knight-Leveson common-mode failure: diverse outcome channels prevent single-source bias
  - 888-APEX verdict (2026-08-11): "split reality audit into outcome failure vs calibration drift"

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from .auditor import CalibrationAuditor, BrierDecomposition
from .outcome_channel import HeldOutOutcomeChannel
from .fir_writer import FIRWriter, TypeBEntry
from .substrate_seal import PredictionMetadata, attach_to_seal, extract_from_seal

__version__ = "1.0.0"
__doctrine_ref__ = "arifOS/CANON/CALIBRATION_AUDIT_DOCTRINE.md"

__all__ = [
    "CalibrationAuditor",
    "BrierDecomposition",
    "HeldOutOutcomeChannel",
    "FIRWriter",
    "TypeBEntry",
    "PredictionMetadata",
    "attach_to_seal",
    "extract_from_seal",
]
