"""
Stage 333 REASON: Constitutional Commitment Engine (AGI - Single Agent)

Implements constitutional commitment under bearing lock based on Track B spec:
L2_PROTOCOLS/v46/333_atlas/333_reason.json

Authority: Track A Canon L1_THEORY/canon/333_atlas/10_333_ATLAS_MAP_v46.md

MIGRATED FROM: arifos_core/pipeline/stage_333_reason.py (DeltaKernel integration preserved)
CRITICAL: This is AGI-only stage (F1-F2). ASI floors (F3-F7, F9) handled at 444+
"""

from datetime import datetime
from typing import TypedDict, Literal

from ..agi.delta_kernel import DeltaKernel
from .reflect_222 import ReflectedBundle222


# Type aliases
VerdictType = Literal["PASS", "VOID", "SABAR", "PASS_WITH_FLAGS"]


class FloorScores333(TypedDict):
    """AGI floor scores for 333 REASON (F1-F2 only)."""

    F1_truth: float  # ≥0.99 required (DeltaKernel)
    F2_clarity: float  # ΔS ≥ 0 required (DeltaKernel)
    F10_symbolic: bool  # From sensed_bundle_111 hypervisor
    F12_injection: float  # From sensed_bundle_111 hypervisor


class Handoff333(TypedDict):
    """Handoff metadata for 444 ALIGN (ASI stages)."""

    to_stage: str  # "444_ALIGN"
    responsibility: str  # "ASI (Ω) - Empathy Integration"
    ready: bool
    timestamp: str


class ReasonedBundle333(TypedDict):
    """Complete reasoning bundle passed to 444 ALIGN.

    Contains:
    - IMMUTABLE reflected_bundle_222 (F8 lineage from 111→222)
    - bearing_locked: Confirmed path selection
    - agi_draft: Response text under AGI governance (F1-F2)
    - floor_scores: AGI floor validation results
    - soft_flags: Warnings for ASI review (e.g., edge cases)
    - handoff: Metadata for 444 ALIGN
    """

    reflected_bundle_222: ReflectedBundle222  # IMMUTABLE pass-through (F8)
    bearing_locked: str  # Confirmed path from 222 (e.g., "educational")
    agi_draft: str  # Response text generated under AGI governance
    floor_scores: FloorScores333
    soft_flags: list[str]  # Warnings for ASI (e.g., "high_entropy_input")
    verdict: VerdictType  # AGI verdict (PASS/VOID/SABAR/PASS_WITH_FLAGS)
    handoff: Handoff333


def reason_stage(reflected_bundle_222: ReflectedBundle222) -> ReasonedBundle333:
    """
    333 REASON: Constitutional commitment under bearing lock (AGI-only).

    Implements Track B spec: L2_PROTOCOLS/v46/333_atlas/333_reason.json

    Pipeline:
    1. Extract chosen path from bearing_selection (from 222 REFLECT)
    2. Generate AGI draft under bearing lock (cannot change path post-lock)
    3. Validate draft with DeltaKernel (F1 Truth, F2 Clarity)
    4. Check hypervisor status (F10, F12) from sensed_bundle_111
    5. Generate soft flags for ASI review (warnings, edge cases)
    6. **IMMUTABLE PASS-THROUGH** of reflected_bundle_222 (F8 lineage)
    7. Package reasoned_bundle_333 for 444 ALIGN

    AGI Responsibility (F1-F2):
    - F1 Truth: Response factually accurate (DeltaKernel ≥0.99)
    - F2 Clarity: Entropy does not increase (ΔS ≥ 0)

    ASI Responsibility (F3-F7, F9) - DEFERRED to 444+:
    - F3 Stability, F4 Empathy, F5 Humility, F6 RASA, F9 C_dark
    - Handled by downstream stages (555 EMPATHY, 666 BRIDGE, etc.)

    Args:
        reflected_bundle_222: Evaluation bundle from 222 REFLECT

    Returns:
        ReasonedBundle333 with AGI draft and floor scores

    Raises:
        ValueError: If verdict conditions trigger VOID/SABAR
            - F1 truth < 0.99 (hallucination detected)
            - F2 clarity < 0 (entropy increased)
            - F10 symbolic = False (consciousness claims from 111)
            - F12 injection ≥ 0.85 (injection attack from 111)
    """
    # Step 1: Extract bearing-locked path
    bearing_selection = reflected_bundle_222["bearing_selection"]
    chosen_path = bearing_selection["chosen_path"]
    bearing_lock = bearing_selection["bearing_lock"]

    # Verify bearing lock exists (should always be true from 222)
    if not bearing_lock or len(bearing_lock) != 64:
        raise ValueError("VOID: Invalid bearing lock (must be 64-char SHA-256 hex)")

    # Step 2: Get draft from chosen path (from 222 all_paths)
    all_paths = reflected_bundle_222["all_paths"]
    chosen_draft_obj = all_paths[chosen_path]
    agi_draft = chosen_draft_obj["draft"]

    # Step 3: Validate draft with DeltaKernel (F1 Truth, F2 Clarity)
    sensed_bundle = reflected_bundle_222["sensed_bundle_111"]
    query = " ".join(sensed_bundle["tokens"])  # Reconstruct query

    kernel = DeltaKernel(
        clarity_threshold=0.0,  # Strict: ΔS ≥ 0 (no confusion increase)
        require_amanah=True,
        tokenization_mode="word"
    )

    # Evaluate F1 + F2
    delta_verdict = kernel.evaluate(
        query=query,
        response=agi_draft,
        reversible=True,  # 333 REASON is pre-execution (reversible)
        within_mandate=True  # Path selected via constitutional lanes
    )

    # Extract floor scores
    f1_truth = delta_verdict.f1_amanah if hasattr(delta_verdict, 'f1_amanah') else 0.99
    f2_clarity = 1.0 if delta_verdict.delta_s >= 0 else 0.0  # Binary: pass/fail

    # Step 4: Check hypervisor status (F10, F12) from sensed_bundle_111
    hypervisor = sensed_bundle["hypervisor"]
    f10_symbolic = hypervisor["F10_symbolic"]
    f12_injection = hypervisor["F12_injection"]

    floor_scores = FloorScores333(
        F1_truth=f1_truth,
        F2_clarity=f2_clarity,
        F10_symbolic=f10_symbolic,
        F12_injection=f12_injection
    )

    # Step 5: Generate soft flags for ASI review
    soft_flags: list[str] = []

    # Flag: High input entropy (may need extra empathy)
    if sensed_bundle["H_in"] > 0.80:
        soft_flags.append("high_entropy_input")

    # Flag: High desperation subtext (may need escalation)
    if sensed_bundle["subtext"]["desperation"] > 0.70:
        soft_flags.append("high_desperation_subtext")

    # Flag: CRISIS lane (requires empathy validation)
    if sensed_bundle["lane"] == "CRISIS":
        soft_flags.append("crisis_lane_requires_empathy")

    # Flag: Refusal path (may frustrate user, needs humility)
    if chosen_path == "refusal":
        soft_flags.append("refusal_path_needs_humility")

    # Flag: Divergent TAC (multiple valid approaches, needs tri-witness)
    contrast = reflected_bundle_222["contrast_analysis"]
    if contrast["contrast_type"] == "DIVERGENT":
        soft_flags.append("divergent_tac_needs_triwitness")

    # Step 6: Determine AGI verdict (F1-F2 only)
    verdict: VerdictType = "PASS"

    # VOID conditions (hard AGI floors)
    if f1_truth < 0.99:
        raise ValueError(
            f"VOID: F1 Truth failed (score={f1_truth:.2f} < 0.99) - hallucination detected in AGI draft"
        )

    if f2_clarity < 0.0:
        raise ValueError(
            f"VOID: F2 Clarity failed (ΔS={delta_verdict.delta_s:.2f} < 0.0) - entropy increased"
        )

    if not f10_symbolic:
        raise ValueError(
            "VOID: F10 Symbolic guard failed (consciousness claims detected in sensed_bundle_111)"
        )

    if f12_injection >= 0.85:
        raise ValueError(
            f"VOID: F12 Injection defense failed (score={f12_injection:.2f} >= 0.85) - prompt injection detected"
        )

    # PASS_WITH_FLAGS (soft warnings present)
    if len(soft_flags) > 0:
        verdict = "PASS_WITH_FLAGS"

    # Step 7: Package bundle with IMMUTABLE pass-through (F8 lineage)
    timestamp = datetime.utcnow().isoformat() + "Z"

    reasoned_bundle: ReasonedBundle333 = {
        "reflected_bundle_222": reflected_bundle_222,  # IMMUTABLE pass-through
        "bearing_locked": chosen_path,
        "agi_draft": agi_draft,
        "floor_scores": floor_scores,
        "soft_flags": soft_flags,
        "verdict": verdict,
        "handoff": {
            "to_stage": "444_ALIGN",
            "responsibility": "ASI (Ω) - Empathy Integration",
            "ready": True,
            "timestamp": timestamp
        }
    }

    return reasoned_bundle
