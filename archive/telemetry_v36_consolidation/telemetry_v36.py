# arifos_core/telemetry_v36.py
"""
telemetry_v36.py — v36-Native Telemetry Entry Builder

Spec Alignment:
    Spec: archive/versions/v36_3_omega/v36.3O/spec/apex_prime_telemetry_v36.3O.json
    Status: FULL alignment (closes HOTSPOTs 7, 8, 9)

This module builds telemetry entry dictionaries that match the v36.3Ω spec schema.
It does NOT write files itself; callers (zkpc_runtime, telemetry.py) handle persistence.

Field Mappings Closed:
    HOTSPOT 7: query_hash/response_hash (SHA-256) — implemented via _sha256_hex()
    HOTSPOT 8: floor_metrics{} + floor_results{} — split structure
    HOTSPOT 9: verdict object with code/violations — structured verdict

Usage:
    from arifos_core.utils.telemetry_v36 import build_telemetry_entry_v36

    entry = build_telemetry_entry_v36(
        query="What is AI?",
        response="AI is artificial intelligence...",
        floor_metrics={"truth": 0.99, "delta_s": 0.5, ...},
        floor_results={"F1_pass": True, "F2_pass": True, ...},
        verdict_code="SEAL",
        hard_violations=[],
        soft_violations=[],
        session_id="sess-123",
    )

Author: arifOS Project
Version: 36.3Omega
Motto: "Spec-aligned, audit-ready."
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

# =============================================================================
# CONSTANTS
# =============================================================================

VERSION = "v36.3Omega"

# Hard floors (VOID on fail): F1, F2, F5, F6, F7, F9
HARD_FLOORS = {"F1", "F2", "F5", "F6", "F7", "F9"}

# Soft floors (PARTIAL on fail): F3, F4, F8
SOFT_FLOORS = {"F3", "F4", "F8"}

# Floor metric names mapped to floor IDs
FLOOR_METRIC_MAP = {
    "truth": "F1",
    "delta_s": "F2",
    "peace_squared": "F3",
    "kappa_r": "F4",
    "omega_0": "F5",
    "amanah": "F6",
    "rasa": "F7",
    "tri_witness": "F8",
    "anti_hantu": "F9",
}

# Valid verdict codes per spec
VALID_VERDICT_CODES = {"SEAL", "PARTIAL", "HOLD_888", "SABAR", "VOID"}

# Valid stakes levels per spec
VALID_STAKES = {"low", "medium", "high", "critical"}

# Valid pipeline paths per spec
VALID_PIPELINE_PATHS = {"CLASS_A", "CLASS_B"}


# =============================================================================
# HASH UTILITIES
# =============================================================================


def _sha256_hex(text: str) -> str:
    """
    Compute SHA-256 hash of text, return hex string.

    This implements HOTSPOT 7: query_hash/response_hash as SHA-256.

    Args:
        text: Input text to hash

    Returns:
        64-character lowercase hex string
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# =============================================================================
# FLOOR BUILDERS
# =============================================================================


def build_floor_metrics_v36(metrics: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Build floor_metrics{} dict matching v36.3Ω spec.

    This implements HOTSPOT 8: separated floor_metrics structure.

    Args:
        metrics: Raw metrics dict with keys like "truth", "delta_s", etc.

    Returns:
        Dict with spec-compliant floor metric values

    Example:
        >>> build_floor_metrics_v36({"truth": 0.995, "delta_s": 0.5})
        {"truth": 0.995, "delta_s": 0.5, ...}
    """
    return {
        "truth": metrics.get("truth"),
        "delta_s": metrics.get("delta_s"),
        "peace_squared": metrics.get("peace_squared"),
        "kappa_r": metrics.get("kappa_r"),
        "omega_0": metrics.get("omega_0"),
        "amanah": metrics.get("amanah"),
        "rasa": metrics.get("rasa"),
        "tri_witness": metrics.get("tri_witness"),
        "anti_hantu": metrics.get("anti_hantu"),
    }


def build_floor_results_v36(floor_pass_map: Mapping[str, bool]) -> Dict[str, bool]:
    """
    Build floor_results{} dict matching v36.3Ω spec.

    This implements HOTSPOT 8: separated floor_results structure.

    Args:
        floor_pass_map: Dict mapping floor IDs to pass/fail
                        Accepts either "F1_pass" or "F1" keys

    Returns:
        Dict with F1_pass...F9_pass boolean fields

    Example:
        >>> build_floor_results_v36({"F1": True, "F2": False})
        {"F1_pass": True, "F2_pass": False, ...}
    """
    results: Dict[str, bool] = {}
    for i in range(1, 10):
        floor_id = f"F{i}"
        key_with_pass = f"{floor_id}_pass"

        # Accept either "F1_pass" or "F1" as input keys
        if key_with_pass in floor_pass_map:
            results[key_with_pass] = bool(floor_pass_map[key_with_pass])
        elif floor_id in floor_pass_map:
            results[key_with_pass] = bool(floor_pass_map[floor_id])
        else:
            # Default to None if not provided (will be filtered later if needed)
            results[key_with_pass] = None  # type: ignore[assignment]

    return results


# =============================================================================
# VERDICT BUILDER
# =============================================================================


def build_verdict_v36(
    code: str,
    hard_violations: Optional[List[str]] = None,
    soft_violations: Optional[List[str]] = None,
    requires_human_confirmation: bool = False,
) -> Dict[str, Any]:
    """
    Build structured verdict object matching v36.3Ω spec.

    This implements HOTSPOT 9: structured verdict with code/violations.

    Args:
        code: Verdict code (SEAL, PARTIAL, HOLD_888, SABAR, VOID)
        hard_violations: List of hard floor IDs that failed (e.g., ["F1", "F6"])
        soft_violations: List of soft floor IDs that failed (e.g., ["F3"])
        requires_human_confirmation: True if 888_HOLD triggered

    Returns:
        Spec-compliant verdict dict

    Raises:
        ValueError: If code is not a valid verdict code

    Example:
        >>> build_verdict_v36("PARTIAL", soft_violations=["F3"])
        {"code": "PARTIAL", "hard_floor_violations": [], "soft_floor_violations": ["F3"], ...}
    """
    if code not in VALID_VERDICT_CODES:
        raise ValueError(f"Invalid verdict code: {code}. Must be one of {VALID_VERDICT_CODES}")

    return {
        "code": code,
        "hard_floor_violations": hard_violations or [],
        "soft_floor_violations": soft_violations or [],
        "requires_human_confirmation": requires_human_confirmation,
    }


# =============================================================================
# AGGREGATE METRICS BUILDER
# =============================================================================


def build_aggregate_metrics_v36(
    G: Optional[float] = None,
    C_dark: Optional[float] = None,
    Psi_APEX: Optional[float] = None,
    Delta_metric: Optional[float] = None,
    Omega_metric: Optional[float] = None,
    Psi_metric: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build aggregate_metrics{} dict matching v36.3Ω spec.

    Args:
        G: Governed Intelligence Index
        C_dark: Dark Cleverness Index
        Psi_APEX: Apex Vitality Index
        Delta_metric: Clarity aggregate
        Omega_metric: Stability aggregate
        Psi_metric: Vitality aggregate

    Returns:
        Dict with aggregate metric values (None values excluded)
    """
    metrics = {
        "G": G,
        "C_dark": C_dark,
        "Psi_APEX": Psi_APEX,
        "Delta_metric": Delta_metric,
        "Omega_metric": Omega_metric,
        "Psi_metric": Psi_metric,
    }
    # Filter out None values for cleaner output
    return {k: v for k, v in metrics.items() if v is not None}


# =============================================================================
# TRUTH POLARITY BUILDER
# =============================================================================


def build_truth_polarity_v36(
    polarity: str,
    P_g: Optional[float] = None,
    P_c: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build truth_polarity{} dict matching v36.3Ω spec.

    Args:
        polarity: "LIGHT", "SHADOW", or "WEAPONIZED"
        P_g: Probability of genuine/light truth
        P_c: Probability of cleverness/shadow truth

    Returns:
        Dict with truth polarity fields
    """
    result: Dict[str, Any] = {"polarity": polarity}
    if P_g is not None:
        result["P_g"] = P_g
    if P_c is not None:
        result["P_c"] = P_c
    return result


# =============================================================================
# CCE AUDITS BUILDER
# =============================================================================


def build_cce_audits_v36(
    delta_p: Optional[str] = None,
    omega_p: Optional[str] = None,
    psi_p: Optional[str] = None,
    phi_p: Optional[str] = None,
    truth_polarity_audit: Optional[str] = None,
) -> Dict[str, str]:
    """
    Build cce_audits{} dict matching v36.3Ω spec.

    Args:
        delta_p: Clarity audit ("PASS" or "FAIL")
        omega_p: Stability audit
        psi_p: Vitality audit
        phi_p: Paradox audit
        truth_polarity_audit: Truth Polarity audit

    Returns:
        Dict with CCE audit results (None values excluded)
    """
    audits = {
        "delta_p": delta_p,
        "omega_p": omega_p,
        "psi_p": psi_p,
        "phi_p": phi_p,
        "truth_polarity_audit": truth_polarity_audit,
    }
    return {k: v for k, v in audits.items() if v is not None}


# =============================================================================
# W@W SIGNALS BUILDER
# =============================================================================


def build_waw_signals_v36(
    wealth_vote: Optional[str] = None,
    well_vote: Optional[str] = None,
    geox_vote: Optional[str] = None,
    rif_vote: Optional[str] = None,
    prompt_vote: Optional[str] = None,
    federation_verdict: Optional[str] = None,
    has_absolute_veto: bool = False,
) -> Dict[str, Any]:
    """
    Build waw_signals{} dict matching v36.3Ω spec.

    Args:
        wealth_vote: @WEALTH organ vote ("PASS", "WARN", or "VETO")
        well_vote: @WELL organ vote
        geox_vote: @GEOX organ vote
        rif_vote: @RIF organ vote
        prompt_vote: @PROMPT organ vote
        federation_verdict: Overall federation verdict
        has_absolute_veto: True if any organ issued absolute veto

    Returns:
        Dict with W@W signals (None values excluded)
    """
    signals: Dict[str, Any] = {}
    if wealth_vote:
        signals["wealth_vote"] = wealth_vote
    if well_vote:
        signals["well_vote"] = well_vote
    if geox_vote:
        signals["geox_vote"] = geox_vote
    if rif_vote:
        signals["rif_vote"] = rif_vote
    if prompt_vote:
        signals["prompt_vote"] = prompt_vote
    if federation_verdict:
        signals["federation_verdict"] = federation_verdict
    if has_absolute_veto:
        signals["has_absolute_veto"] = has_absolute_veto
    return signals


# =============================================================================
# AUDIT TRAIL BUILDER
# =============================================================================


def build_audit_trail_v36(
    previous_hash: Optional[str] = None,
    entry_hash: Optional[str] = None,
    merkle_root: Optional[str] = None,
) -> Dict[str, str]:
    """
    Build audit_trail{} dict matching v36.3Ω spec.

    Args:
        previous_hash: Hash of previous entry (chain integrity)
        entry_hash: Hash of this entry
        merkle_root: Merkle root if applicable

    Returns:
        Dict with audit trail fields (None values excluded)
    """
    trail = {
        "previous_hash": previous_hash,
        "entry_hash": entry_hash,
        "merkle_root": merkle_root,
    }
    return {k: v for k, v in trail.items() if v is not None}


# =============================================================================
# MAIN ENTRY BUILDER
# =============================================================================


def build_telemetry_entry_v36(
    query: str,
    response: str,
    floor_metrics: Mapping[str, Any],
    floor_results: Mapping[str, bool],
    verdict_code: str,
    hard_violations: Optional[List[str]] = None,
    soft_violations: Optional[List[str]] = None,
    session_id: Optional[str] = None,
    pipeline_path: str = "CLASS_A",
    stakes: str = "low",
    requires_human_confirmation: bool = False,
    aggregate_metrics: Optional[Dict[str, float]] = None,
    truth_polarity: Optional[Dict[str, Any]] = None,
    cce_audits: Optional[Dict[str, str]] = None,
    waw_signals: Optional[Dict[str, Any]] = None,
    audit_trail: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a complete v36.3Ω-compliant telemetry entry.

    This is the main entry point for creating spec-aligned telemetry records.
    It implements all three HOTSPOTs:
        - HOTSPOT 7: SHA-256 query_hash/response_hash
        - HOTSPOT 8: Separated floor_metrics{} and floor_results{}
        - HOTSPOT 9: Structured verdict object

    Args:
        query: Input query text (will be hashed)
        response: Response text (will be hashed)
        floor_metrics: Dict of floor metric values
        floor_results: Dict of floor pass/fail results
        verdict_code: Verdict code (SEAL, PARTIAL, HOLD_888, SABAR, VOID)
        hard_violations: List of hard floor IDs that failed
        soft_violations: List of soft floor IDs that failed
        session_id: Optional session identifier
        pipeline_path: "CLASS_A" (fast) or "CLASS_B" (full)
        stakes: "low", "medium", "high", or "critical"
        requires_human_confirmation: True if 888_HOLD triggered
        aggregate_metrics: Optional pre-built aggregate metrics dict
        truth_polarity: Optional pre-built truth polarity dict
        cce_audits: Optional pre-built CCE audits dict
        waw_signals: Optional pre-built W@W signals dict
        audit_trail: Optional pre-built audit trail dict
        metadata: Optional additional metadata

    Returns:
        Complete telemetry entry dict ready for JSON serialization

    Example:
        >>> entry = build_telemetry_entry_v36(
        ...     query="What is AI?",
        ...     response="AI is artificial intelligence...",
        ...     floor_metrics={"truth": 0.995, "delta_s": 0.5},
        ...     floor_results={"F1": True, "F2": True},
        ...     verdict_code="SEAL",
        ... )
        >>> entry["query_hash"][:8]
        'a1b2c3d4'
    """
    # Build timestamp (ISO8601 with timezone)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build entry
    entry: Dict[str, Any] = {
        "timestamp": timestamp,
        "session_id": session_id,
        "query_hash": _sha256_hex(query),  # HOTSPOT 7
        "response_hash": _sha256_hex(response),  # HOTSPOT 7
        "pipeline_path": pipeline_path,
        "stakes": stakes,
        "floor_metrics": build_floor_metrics_v36(floor_metrics),  # HOTSPOT 8
        "floor_results": build_floor_results_v36(floor_results),  # HOTSPOT 8
        "verdict": build_verdict_v36(  # HOTSPOT 9
            code=verdict_code,
            hard_violations=hard_violations,
            soft_violations=soft_violations,
            requires_human_confirmation=requires_human_confirmation,
        ),
        "version": VERSION,
    }

    # Add optional sections if provided
    if aggregate_metrics:
        entry["aggregate_metrics"] = aggregate_metrics
    if truth_polarity:
        entry["truth_polarity"] = truth_polarity
    if cce_audits:
        entry["cce_audits"] = cce_audits
    if waw_signals:
        entry["waw_signals"] = waw_signals
    if audit_trail:
        entry["audit_trail"] = audit_trail
    if metadata:
        entry["metadata"] = metadata

    return entry


# =============================================================================
# CONVENIENCE: DERIVE VIOLATIONS FROM FLOOR RESULTS
# =============================================================================


def derive_violations_from_floors(
    floor_results: Mapping[str, bool],
) -> tuple[List[str], List[str]]:
    """
    Derive hard and soft floor violations from floor results.

    Utility function to compute violation lists from floor pass/fail map.

    Args:
        floor_results: Dict mapping floor IDs or "F{n}_pass" to bool

    Returns:
        Tuple of (hard_violations, soft_violations)

    Example:
        >>> derive_violations_from_floors({"F1": False, "F3": False, "F2": True})
        (['F1'], ['F3'])
    """
    hard_violations: List[str] = []
    soft_violations: List[str] = []

    for i in range(1, 10):
        floor_id = f"F{i}"
        key_with_pass = f"{floor_id}_pass"

        # Check both key formats
        passed = None
        if key_with_pass in floor_results:
            passed = floor_results[key_with_pass]
        elif floor_id in floor_results:
            passed = floor_results[floor_id]

        # Skip if not provided
        if passed is None:
            continue

        # Record violation if failed
        if not passed:
            if floor_id in HARD_FLOORS:
                hard_violations.append(floor_id)
            elif floor_id in SOFT_FLOORS:
                soft_violations.append(floor_id)

    return hard_violations, soft_violations


def derive_verdict_code(
    hard_violations: List[str],
    soft_violations: List[str],
    requires_hold: bool = False,
) -> str:
    """
    Derive verdict code from violations.

    Args:
        hard_violations: List of hard floor violations
        soft_violations: List of soft floor violations
        requires_hold: True if 888_HOLD should be triggered

    Returns:
        Verdict code: SEAL, PARTIAL, HOLD_888, or VOID
    """
    if hard_violations:
        return "VOID"
    if requires_hold:
        return "HOLD_888"
    if soft_violations:
        return "PARTIAL"
    return "SEAL"


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "VERSION",
    "HARD_FLOORS",
    "SOFT_FLOORS",
    "FLOOR_METRIC_MAP",
    "VALID_VERDICT_CODES",
    # Hash utilities
    "_sha256_hex",
    # Builders
    "build_floor_metrics_v36",
    "build_floor_results_v36",
    "build_verdict_v36",
    "build_aggregate_metrics_v36",
    "build_truth_polarity_v36",
    "build_cce_audits_v36",
    "build_waw_signals_v36",
    "build_audit_trail_v36",
    "build_telemetry_entry_v36",
    # Derivation utilities
    "derive_violations_from_floors",
    "derive_verdict_code",
]
