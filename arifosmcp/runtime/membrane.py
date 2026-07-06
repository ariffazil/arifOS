"""
membrane.py — The Kernel/Actuator Membrane Contract
====================================================

The membrane is the ONLY interface between A-FORGE (actuator) and arifOS (kernel).

MEMBRANE-01: Any function inside arifOS kernel that directly computes G, C_dark,
             W³, MALU, PHI, nine_signal, SESAT severity, or HANTAR state is a
             layer violation unless marked as test fixture or verifier.

MEMBRANE-02: Any function inside A-FORGE that emits SEAL, HOLD, VOID, or SABAR
             as final constitutional verdict is a layer violation. It may recommend,
             never decide.

MEMBRANE-03: Only MeasurementPackets cross actuator → kernel.
             Only VerdictPackets cross kernel → actuator.

MEMBRANE-04: Kernel may verify packet shape and trace integrity, but must not
             recompute packet contents.

MEMBRANE-05: A-FORGE may recommend risk posture, but any verdict field inside
             actuator output is advisory metadata only unless wrapped by kernel.

Phase 2 status (2026-07-06):
  - arif_judge accepts MeasurementPacket (measurement dict) ✅
  - Kernel uses G, C_dark for F9/F8 floor checks ✅
  - A-FORGE forge_judge_proxy forwards measurement ✅
  - APEX modules copied to A-FORGE/src/domain/apex/ ✅
  - MALU migrated to SQLite ✅
  - SESAT wired into _sabar ✅
  - HANTAR utility added ✅
  - D-MEMBRANE tests: 11/11 PASS ✅

Phase 3 status (2026-07-06):
  - record_tool_call() wired into _ok, _hold, _sabar, _error_envelope ✅
  - record_tool_call() wired into _wrap_handler (sync + async) ✅
  - compute_apex_from_metrics() enriches MeasurementPacket in forge_judge_proxy ✅
  - record_comparison() wired into _arif_judge_deliberate ✅
  - APEX metrics DB at /var/lib/arifos/apex_metrics.db (arifos user writable) ✅
  - Real A,P,E,X,Φ values from live tool calls ✅

The measurement crosses up. The verdict crosses down. Anything else recreates
cosmetic governance in a cleaner costume.

Forged: 2026-07-06 by FORGE (000Ω)
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# MeasurementPacket — A-FORGE → Kernel
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class MeasurementPacket:
    """What A-FORGE passes to the kernel for judgment.

    The kernel NEVER computes these. It reads them and judges against floors.
    A-FORGE NEVER issues verdicts from these. It reports and lets the kernel decide.
    """

    # ── APEX primitives (computed by A-FORGE) ──
    G: float = 0.0  # A·P·E·X·Φ — intelligence quality
    C_dark: float = 0.0  # A·(1-P)·(1-X) — hallucination detector
    W3: float = 0.0  # ∛(H×AI×Ext) — witness consensus
    malu_total: float = 0.0  # accumulated failure pressure
    phi: float = 1.0  # scar wisdom factor

    # ── Primitive breakdown (for traceability) ──
    A: float = 0.0  # Authority / Agency alignment
    P: float = 0.0  # Provenance / probability-of-truth
    E: float = 0.0  # Evidence strength
    X: float = 0.0  # Execution safety / reversibility

    # ── Witness confidences ──
    H: float = 0.0  # Human witness confidence
    AI: float = 0.0  # AI/model critique confidence
    Ext: float = 0.0  # External evidence confidence

    # ── Failure state ──
    sesat_active: bool = False
    sesat_severity: str | None = None  # GREEN/YELLOW/ORANGE/RED/BLACK
    sesat_failure_code: str | None = None  # JALAN_* code
    hantar_state: str = "LURUS"  # LURUS/SESAT/HOLD/VOID

    # ── Provenance ──
    source: str = "A-FORGE"
    calculator: str = "forge_evaluate"
    version: str = "apex-v1"
    inputs_hash: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "measurement": {
                "G": self.G,
                "C_dark": self.C_dark,
                "W3": self.W3,
                "MALU": self.malu_total,
                "PHI": self.phi,
                "primitives": {
                    "A": self.A,
                    "P": self.P,
                    "E": self.E,
                    "X": self.X,
                },
                "witness": {
                    "H": self.H,
                    "AI": self.AI,
                    "Ext": self.Ext,
                },
                "sesat": {
                    "active": self.sesat_active,
                    "severity": self.sesat_severity,
                    "failure_code": self.sesat_failure_code,
                },
                "hantar": {
                    "state": self.hantar_state,
                },
                "trace": {
                    "source": self.source,
                    "calculator": self.calculator,
                    "version": self.version,
                    "inputs_hash": self.inputs_hash,
                    "timestamp": self.timestamp,
                },
            },
        }


# ═══════════════════════════════════════════════════════════════════════
# VerdictPacket — Kernel → A-FORGE
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class VerdictPacket:
    """What the kernel returns to A-FORGE after judgment.

    The kernel NEVER computes APEX. It reads the MeasurementPacket,
    checks against F1-F13 floors, and returns a verdict.
    A-FORGE NEVER issues this. It receives it and acts accordingly.
    """

    verdict: str = "SABAR"  # SEAL | HOLD | VOID | SABAR
    floors_triggered: list[str] = field(default_factory=list)
    reason: str = ""
    seal_eligible: bool = False
    requires_saksi: bool = False
    requires_tebus: bool = False

    # ── What the kernel measured (from the packet, not computed) ──
    G_received: float | None = None
    C_dark_received: float | None = None
    W3_received: float | None = None

    # ── Provenance ──
    judge_id: str = "arif_judge"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "floors_triggered": self.floors_triggered,
            "reason": self.reason,
            "seal_eligible": self.seal_eligible,
            "requires_saksi": self.requires_saksi,
            "requires_tebus": self.requires_tebus,
            "received_measurement": {
                "G": self.G_received,
                "C_dark": self.C_dark_received,
                "W3": self.W3_received,
            },
            "trace": {
                "judge_id": self.judge_id,
                "timestamp": self.timestamp,
            },
        }


# ═══════════════════════════════════════════════════════════════════════
# Membrane Invariants
# ═══════════════════════════════════════════════════════════════════════

MEMBRANE_INVARIANTS = {
    "MEMBRANE-01": (
        "Any function inside arifOS kernel that directly computes G, C_dark, "
        "W³, MALU, PHI, nine_signal, SESAT severity, or HANTAR state is a "
        "layer violation unless marked as test fixture or verifier."
    ),
    "MEMBRANE-02": (
        "Any function inside A-FORGE that emits SEAL, HOLD, VOID, or SABAR "
        "as final constitutional verdict is a layer violation. It may recommend, "
        "never decide."
    ),
    "MEMBRANE-03": (
        "Only MeasurementPackets cross actuator → kernel. "
        "Only VerdictPackets cross kernel → actuator."
    ),
    "MEMBRANE-04": (
        "Kernel may verify packet shape and trace integrity, but must not "
        "recompute packet contents. The kernel may reject a packet; it must "
        "never recreate it."
    ),
    "MEMBRANE-05": (
        "A-FORGE may recommend risk posture, but any SEAL/HOLD/VOID/SABAR field "
        "inside actuator output is advisory metadata only unless wrapped by "
        "kernel VerdictPacket."
    ),
}


def validate_measurement(packet: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate that a dict is a proper MeasurementPacket.

    Returns (is_valid, violations).
    """
    violations = []
    m = packet.get("measurement", packet)

    required = ["G", "C_dark", "W3"]
    for key in required:
        if key not in m:
            violations.append(f"Missing required field: {key}")

    if "trace" not in m:
        violations.append("Missing trace (provenance)")

    if "source" not in m.get("trace", {}):
        violations.append("Missing trace.source")

    # Check for verdict language (MEMBRANE-02 violation)
    verdict_words = {"SEAL", "HOLD", "VOID", "SABAR"}
    for word in verdict_words:
        if m.get("verdict") == word:
            violations.append(f"MEMBRANE-02: Measurement contains verdict '{word}'")

    return len(violations) == 0, violations


def validate_verdict(packet: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate that a dict is a proper VerdictPacket.

    Returns (is_valid, violations).
    """
    violations = []

    if "verdict" not in packet:
        violations.append("Missing verdict")
    elif packet["verdict"] not in ("SEAL", "HOLD", "VOID", "SABAR"):
        violations.append(f"Invalid verdict: {packet['verdict']}")

    if "floors_triggered" not in packet:
        violations.append("Missing floors_triggered")

    # Check for computation (MEMBRANE-01 violation)
    computation_keys = {"G", "C_dark", "W3", "MALU", "PHI"}
    top_level = set(packet.keys())
    leaked = top_level & computation_keys
    if leaked:
        violations.append(f"MEMBRANE-01: Verdict contains computation: {leaked}")

    return len(violations) == 0, violations
