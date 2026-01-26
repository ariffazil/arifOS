"""
arifOS Canonical Core - The Single Source of Truth

DITEMPA BUKAN DIBERI - Forged, Not Given

This module contains the ONE canonical implementation of each constitutional concept.
All other code MUST import from here. Duplicates are forbidden.

Architecture:
    canonical_core/
    ├── stage_000/     # Foundation Initialization (F10-F12, Amanah)
    ├── stage_111/     # SENSE (future)
    ├── stage_222/     # THINK (future)
    └── ...

Version: v52.5.2-CANONICAL
Authority: Muhammad Arif bin Fazil
Sealed: 2026-01-26
"""

from .stage_000 import (
    # Core class
    Stage000VOID,
    stage_000_void,
    # Verdict enum
    VerdictType,
    # Result dataclasses
    SessionInitResult,
    SessionMetadata,
    TelemetryPacket,
    HypervisorGateResult,
    AmanahGateResult,
    ScarEchoCheck,
    ZKPCCommitment,
    # Amanah subsystem
    AmanahSignals,
    compute_amanah_score,
    # Injection defense subsystem
    InjectionDefense,
    # Constants
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    OMEGA_0_DEFAULT,
    AMANAH_THRESHOLD,
    INJECTION_THRESHOLD,
)

__all__ = [
    "Stage000VOID",
    "stage_000_void",
    "VerdictType",
    "SessionInitResult",
    "SessionMetadata",
    "TelemetryPacket",
    "HypervisorGateResult",
    "AmanahGateResult",
    "ScarEchoCheck",
    "ZKPCCommitment",
    "AmanahSignals",
    "compute_amanah_score",
    "InjectionDefense",
    "OMEGA_0_MIN",
    "OMEGA_0_MAX",
    "OMEGA_0_DEFAULT",
    "AMANAH_THRESHOLD",
    "INJECTION_THRESHOLD",
]

__version__ = "v52.5.2-CANONICAL"
__author__ = "Muhammad Arif bin Fazil"
__motto__ = "DITEMPA BUKAN DIBERI"
