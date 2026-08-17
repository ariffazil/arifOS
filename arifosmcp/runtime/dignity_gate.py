"""
arifosmcp/runtime/dignity_gate.py
═══════════════════════════════════════════════════════════════════════════════
ATLAS333 P36 Witness & Dignity / P37 Scars Gate (Humanity Cluster)

Axioms:
  - "Human value resists reduction to mere output metrics." (P36)
  - "Human memory remembers significance & scars; agent memory remembers reality." (P37)
  - "On human surfaces: SIFAR machine label leaks ([OBS]/[DER]/[INT]/[SPEC]/[ACT]). Talk like a human." (F13 2026-08-13 ruling)

Rules:
  1. Blocks unencrypted exposure of H5 Scars / private human trauma in public logs or external telemetry.
  2. Compiles or strips internal epistemic machine labels when emitting to human surfaces.

Constitutional Floors: F6 EMPATHY ⇄ MARUAH, F2 TRUTH, F11 AUDITABILITY.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

MACHINE_LABELS: list[str] = [
    "[OBS]", "[DER]", "[INT]", "[SPEC]", "[UNKNOWN]",
    "[ACT]", "[🦾ACT]", "[🦾ACT-PARTIAL]", "[EXE]", "[SEAL]"
]


@dataclass(frozen=True)
class DignityEvaluation:
    surface_type: str  # "human_chat", "agent_terminal", "public_log", "internal_vault"
    contains_private_scars: bool
    label_leak_detected: bool
    sanitized_output: str
    verdict: str  # "PASS", "SANITIZED", "888_HOLD"
    reason: str


def evaluate_dignity(
    content: str,
    surface_type: str = "human_chat",
    data_classification: str = "PUBLIC"
) -> DignityEvaluation:
    """
    Evaluate human dignity, privacy boundaries, and epistemic label discipline.
    """
    is_human_surface = surface_type.lower() in {"human_chat", "telegram", "user_cli", "chat"}
    is_private_scar = data_classification.upper() in {"H5", "SCAR", "PRIVATE_MEMORY", "TRAUMA"}

    # Check for private scar exposure on public/unauthenticated surface
    if is_private_scar and surface_type.lower() in {"public_log", "external_api", "telemetry"}:
        return DignityEvaluation(
            surface_type=surface_type,
            contains_private_scars=True,
            label_leak_detected=False,
            sanitized_output="[REDACTED_H5_SOVEREIGN_SCAR]",
            verdict="888_HOLD",
            reason="P36/P37 DIGNITY VIOLATION: H5 sovereign scar cannot be emitted to public/external telemetry."
        )

    # Check for machine label leaks on human surfaces
    label_leak = False
    sanitized = content
    if is_human_surface:
        for lbl in MACHINE_LABELS:
            if lbl in sanitized:
                label_leak = True
                # Clean labels out of human view
                sanitized = sanitized.replace(lbl, "").strip()
        # Clean extra brackets/tags if leftover
        sanitized = re.sub(r'\[(OBS|DER|INT|SPEC|CLAIM|PLAUSIBLE|ESTIMATE)\]', '', sanitized).strip()

    if label_leak:
        return DignityEvaluation(
            surface_type=surface_type,
            contains_private_scars=is_private_scar,
            label_leak_detected=True,
            sanitized_output=sanitized,
            verdict="SANITIZED",
            reason="P36 MARUAH COMPILATION: Machine epistemic labels stripped for human conversation."
        )

    return DignityEvaluation(
        surface_type=surface_type,
        contains_private_scars=is_private_scar,
        label_leak_detected=False,
        sanitized_output=content,
        verdict="PASS",
        reason="Complies with dignity and surface governance."
    )
