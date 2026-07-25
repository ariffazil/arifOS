"""
enforcement/substrate.py — Δ·Ω·Ψ Evidence Substrate Validation Gate

GENESIS/055 Multimodal Kernel Hardening:
  KH-1: Raw LLM output is not evidence. Only claims that carry a
        delta_substrate_hash may enter the G computation.
  KH-2: Every organ's /health must expose g_primitive_state.
  KH-4: C_dark must incorporate multimodal hallucination detection.
  KH-5: Ext_witness >= 0.85 required for SEAL.

This module provides the validation gates that run BEFORE any G computation
in the arifOS kernel. It ensures multimodal evidence has been metabolized
through the correct organ's Δ substrate before contributing to the verdict.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# Evidence Substrate Record
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class EvidenceSubstrate:
    """Extended evidence record for multimodal provenance tracking.

    Maps to the Ω-envelope fields produced by organ Δ substrates.
    """

    source: str  # "geox", "wealth", "well", "arifos", "raw_llm"
    modality: str | None = None  # "seismic", "well_log", etc. — None = invalid
    g_primitive: str | None = None  # "P", "E", "X", "A", "Φ" — None = not G-contributor
    delta_substrate_hash: str | None = None  # SHA256 of Δ pipeline — None = not metabolized
    verification_status: str = "UNVERIFIED"  # "VERIFIED", "UNVERIFIED", "FALSIFIED"
    claim_state: str = "HYPOTHESIS"  # "OBSERVED", "DERIVED", "INTERPRETED", "HYPOTHESIS"
    contradiction_scan: str = "UNMEASURED"  # "PASS", "KILL_<K00N>", "UNMEASURED"
    envelope: dict[str, Any] | None = None  # Full Ω-envelope from organ


@dataclass
class SubstrateValidation:
    """Result of evidence substrate validation (KH-1 enforcement)."""

    valid: bool
    violations: list[str] = field(default_factory=list)
    g_primitive_map: dict[str, float] = field(default_factory=dict)  # primitive → confidence
    c_dark_modifier: float = 0.0  # How much to increase C_dark
    degraded_modalities: list[str] = field(default_factory=list)
    falsified_count: int = 0
    unmetabolized_count: int = 0
    gate_status: str = "IDLE"  # IDLE | PASS | DEGRADED | REJECTED


@dataclass
class ContradictionReport:
    """Result of cross-modal contradiction detection (KH-4 enforcement)."""

    contradictions: list[dict[str, Any]] = field(default_factory=list)
    c_dark_modifier: float = 0.0
    g_primitive_adjustments: dict[str, float] = field(default_factory=dict)
    kill_triggers: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# KH-1: Evidence Substrate Validation
# ═══════════════════════════════════════════════════════════════════════════════


def validate_evidence_substrate(evidence: list[EvidenceSubstrate]) -> SubstrateValidation:
    """KH-1 enforcement: verify every evidence record passed through an organ's Δ substrate.

    Rules:
    - Raw LLM output (source="raw_llm" and no delta_substrate_hash) → REJECT
    - No delta_substrate_hash → DEGRADE (C_dark += 0.10)
    - UNVERIFIED verification → DEGRADE (C_dark += 0.05)
    - FALSIFIED → REJECT (VOID if on critical path)
    - No modality tag → DEGRADE (C_dark += 0.05)
    - Metabolized + VERIFIED → ACCEPT (contribute to G)

    Returns:
        SubstrateValidation with gate status, violations, and C_dark modifier.
    """
    violations: list[str] = []
    g_primitive_map: dict[str, float] = {}
    c_dark_mod = 0.0
    degraded_modalities: list[str] = []
    falsified_count = 0
    unmetabolized_count = 0

    for i, ev in enumerate(evidence):
        idx_label = f"evidence[{i}] ({ev.source}/{ev.modality or '?'})"

        # ── RAW LLM REJECTION ──
        if ev.source == "raw_llm" and ev.delta_substrate_hash is None:
            violations.append(f"{idx_label}: Raw LLM output rejected — no Δ-substrate provenance.")
            unmetabolized_count += 1
            c_dark_mod += 0.10
            continue

        # ── NO SUBSTRATE HASH ──
        if ev.delta_substrate_hash is None:
            violations.append(
                f"{idx_label}: No delta_substrate_hash — unmetabolized evidence. Degraded to HOLD."
            )
            unmetabolized_count += 1
            c_dark_mod += 0.10
            degraded_modalities.append(ev.modality or "unknown")
            continue

        # ── UNVERIFIED ──
        if ev.verification_status == "UNVERIFIED":
            violations.append(f"{idx_label}: verification_status=UNVERIFIED — degraded.")
            c_dark_mod += 0.05
            if ev.modality:
                degraded_modalities.append(ev.modality)

        # ── FALSIFIED ──
        if ev.verification_status == "FALSIFIED":
            violations.append(f"{idx_label}: FALSIFIED evidence — REJECTED.")
            falsified_count += 1
            c_dark_mod += 0.15
            continue  # Do not contribute to G

        # ── MISSING MODALITY ──
        if ev.modality is None:
            violations.append(f"{idx_label}: No modality tag — cannot cross-check. Degraded.")
            c_dark_mod += 0.05

        # ── ACCEPT: contribute to G primitive map ──
        if ev.g_primitive and ev.verification_status != "FALSIFIED":
            current = g_primitive_map.get(ev.g_primitive, 0.0)
            # Higher weight for VERIFIED evidence
            weight = 0.9 if ev.verification_status == "VERIFIED" else 0.6
            g_primitive_map[ev.g_primitive] = max(current, weight)

    # ── Determine gate status ──
    gate_status = "PASS"
    if falsified_count > 0:
        gate_status = "REJECTED"
    elif unmetabolized_count > 0:
        gate_status = "DEGRADED"
    elif c_dark_mod > 0.0:
        gate_status = "DEGRADED"

    # Clamp C_dark modifier
    c_dark_mod = min(0.30, c_dark_mod)

    return SubstrateValidation(
        valid=(gate_status != "REJECTED"),
        violations=violations,
        g_primitive_map=g_primitive_map,
        c_dark_modifier=round(c_dark_mod, 4),
        degraded_modalities=list(set(degraded_modalities)),
        falsified_count=falsified_count,
        unmetabolized_count=unmetabolized_count,
        gate_status=gate_status,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# KH-4: Cross-Modal Contradiction Detection
# ═══════════════════════════════════════════════════════════════════════════════


def detect_cross_modal_contradiction(evidence: list[EvidenceSubstrate]) -> ContradictionReport:
    """KH-4 enforcement: detect when two modalities contradict within an organ.

    Checks:
    1. If two evidence records have the same g_primitive but different modalities,
       check their contradiction_scan fields for KILL results.
    2. Any KILL in contradiction_scan → flag for C_dark increase.
    3. Modality that has been falsified → exclude from G computation.

    Returns:
        ContradictionReport with contradictions, C_dark modifier, and G adjustments.
    """
    contradictions: list[dict[str, Any]] = []
    c_dark_mod = 0.0
    g_adj: dict[str, float] = {}
    kill_triggers: list[str] = []

    # Group by g_primitive
    by_primitive: dict[str, list[EvidenceSubstrate]] = {}
    for ev in evidence:
        if ev.g_primitive and ev.verification_status != "FALSIFIED":
            by_primitive.setdefault(ev.g_primitive, []).append(ev)

    # Check for contradictions within each primitive group
    for primitive, group in by_primitive.items():
        modalities_in_group = {ev.modality for ev in group if ev.modality}

        # More than one modality contributing to the same primitive → check for kills
        if len(modalities_in_group) > 1:
            for ev in group:
                if ev.contradiction_scan and ev.contradiction_scan.startswith("KILL"):
                    contradictions.append(
                        {
                            "primitive": primitive,
                            "modality": ev.modality,
                            "kill": ev.contradiction_scan,
                            "source": ev.source,
                        }
                    )
                    kill_triggers.append(ev.contradiction_scan)
                    c_dark_mod += 0.08  # Each contradictory pair adds 0.08

        # Check for kills within the same modality
        for ev in group:
            if ev.contradiction_scan and ev.contradiction_scan.startswith("KILL"):
                # If a KILL was found, reduce this primitive's confidence
                current_adj = g_adj.get(primitive, 1.0)
                g_adj[primitive] = max(0.3, current_adj - 0.15)

    return ContradictionReport(
        contradictions=contradictions,
        c_dark_modifier=round(min(0.30, c_dark_mod), 4),
        g_primitive_adjustments=g_adj,
        kill_triggers=list(set(kill_triggers)),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# KH-5: Ext_witness Threshold Enforcement
# ═══════════════════════════════════════════════════════════════════════════════


def compute_ext_witness(g_primitive_map: dict[str, float]) -> float:
    """KH-5: Compute Ext_witness from G-primitive contributions.

    Ext_witness is the geometric mean of active G-primitive confidences.
    Default 0.70 if no organ has contributed (insufficient for SEAL).
    Minimum 0.85 required for SEAL-grade verdict.

    Returns:
        Ext_witness score in [0.0, 1.0]
    """
    if not g_primitive_map:
        return 0.70  # No organ contribution — insufficient for SEAL

    values = list(g_primitive_map.values())
    product = 1.0
    for v in values:
        product *= max(0.01, v)
    return product ** (1.0 / len(values))


def ext_witness_meets_threshold(ext_witness: float, threshold: float = 0.85) -> bool:
    """KH-5 check: Is Ext_witness sufficient for SEAL?"""
    return ext_witness >= threshold


# ═══════════════════════════════════════════════════════════════════════════════
# Evidence Envelope Parser
# ═══════════════════════════════════════════════════════════════════════════════


def parse_evidence_from_envelope(
    envelope: dict[str, Any], source: str = "unknown"
) -> EvidenceSubstrate:
    """Parse an Ω-envelope from an organ into an EvidenceSubstrate record.

    This is the bridge between organ-produced envelopes (GEOX, WEALTH, WELL)
    and the kernel's substrate validation gate.
    """
    return EvidenceSubstrate(
        source=source,
        modality=envelope.get("modality"),
        g_primitive=envelope.get("g_primitive"),
        delta_substrate_hash=envelope.get("delta_substrate_hash"),
        verification_status=envelope.get("verification_status", "UNVERIFIED"),
        claim_state=envelope.get("claim_state", "HYPOTHESIS"),
        contradiction_scan=envelope.get("contradiction_scan", "UNMEASURED"),
        envelope=envelope,
    )
