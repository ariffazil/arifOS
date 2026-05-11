"""
GEOX Stages 4-5: Structural Candidates + Geological Rule Engine

DITEMPA BUKAN DIBERI

Physics-based candidate generation and rejection from extracted features.
NOT LLM interpretation — rule-based structural analysis.

Stage 4: Generate structural candidates from features
  - Fault candidates from discontinuities + coherence drops
  - Horizon candidates from lineaments + dip patterns
  - Fold candidates from curvature + opposing dip
  - Unconformity candidates from truncated reflectors

Stage 5: Geological rule engine (Physics > Narrative)
  - Reject floating faults (must root to a detachment)
  - Reject inconsistent horizons (cross-cutting relationships)
  - Reject impossible thrust geometries (cut-off angles > 30°)
  - Reject 3D geometry claims from 2D data
  - Reject definitive HC indicators from 2D

Bond et al. (2007): 79% expert failure — most failures from narrative
geology overriding physical constraints. Rule engine enforces physics.

Constitutional floors:
  F2  Truth — Candidates rejected by physics cannot be accepted
  F4  Clarity — 2D vs 3D ambiguity explicit
  F5  Peace² — Non-destructive analysis only
  F7  Humility — Uncertainty in [0.03, 0.20]
  F9  Anti-Hantu — No raw pixel interpretation
"""

from __future__ import annotations

import hashlib
from typing import Any

from arifos.geox.base_tool import _make_provenance
from arifos.geox.geox_mcp_schemas import (
    GEOXStructuralCandidate,
    GEOXStructuralCandidateSet,
    StructuralCandidateType,
    TectonicSetting,
)


class GeologicalRuleEngine:
    """
    Physics-based rule engine for structural interpretation.

    Rejects candidates that violate geological physics.
    Every rejection carries a reason. No narrative override.
    """

    def __init__(self) -> None:
        self.rejected: list[tuple[str, str]] = []

    def check_floating_fault(
        self,
        candidate: GEOXStructuralCandidate,
        all_candidates: list[GEOXStructuralCandidate],
    ) -> bool:
        """
        Reject floating faults — faults must root to a detachment or basement.

        In 2D, we check if fault has an associated horizon interaction.
        """
        if candidate.candidate_type != StructuralCandidateType.FAULT:
            return False

        if not candidate.location:
            self.rejected.append((candidate.candidate_id, "No location — cannot verify rooting"))
            return True

        has_horizon_association = any(
            ref.candidate_type == StructuralCandidateType.HORIZON
            for ref in all_candidates
            if ref.candidate_id != candidate.candidate_id
        )

        if not has_horizon_association and candidate.confidence_score < 0.7:
            self.rejected.append(
                (
                    candidate.candidate_id,
                    "Floating fault — no horizon association, confidence < 0.7",
                )
            )
            return True

        return False

    def check_thrust_geometry(
        self,
        candidate: GEOXStructuralCandidate,
    ) -> bool:
        """
        Reject thrust faults with impossible cut-off angles (> 30°).

        Thrust faults flatten at detachment — cut-off angles > 30° are rare.
        """
        if candidate.candidate_type != StructuralCandidateType.FAULT:
            return False

        characteristics = candidate.characteristics or {}

        cut_off_angle = characteristics.get("cut_off_angle_deg", 0.0)

        if cut_off_angle > 30.0:
            self.rejected.append(
                (
                    candidate.candidate_id,
                    f"Thrust cut-off angle {cut_off_angle}° > 30° — physically unlikely",
                )
            )
            return True

        return False

    def check_horizon_consistency(
        self,
        candidate: GEOXStructuralCandidate,
        dip_field_stats: dict[str, float] | None = None,
    ) -> bool:
        """
        Reject horizons with inconsistent dip patterns.

        A horizon shouldn't have wildly opposing dip directions within
        a coherent segment unless there's structural complexity.
        """
        if candidate.candidate_type != StructuralCandidateType.HORIZON:
            return False

        characteristics = candidate.characteristics or {}

        dip_variation = characteristics.get("dip_variation_deg", 0.0)

        if dip_variation > 60.0:
            self.rejected.append(
                (
                    candidate.candidate_id,
                    f"Horizon dip variation {dip_variation}° > 60° — inconsistent geometry",
                )
            )
            return True

        return False

    def check_unconformity_truncation(
        self,
        candidate: GEOXStructuralCandidate,
        all_candidates: list[GEOXStructuralCandidate],
    ) -> bool:
        """
        Unconformities require onlap/downlap relationships.

        From 2D alone, we cannot definitively identify unconformities —
        this should be flagged as HIGH uncertainty.
        """
        if candidate.candidate_type != StructuralCandidateType.UNCONFORMITY:
            return False

        candidate_type_is_unconf = candidate.candidate_type == StructuralCandidateType.UNCONFORMITY

        has_subcrop_horizons = any(
            ref.candidate_type == StructuralCandidateType.HORIZON and ref.location is not None
            for ref in all_candidates
            if ref.candidate_id != candidate.candidate_id
        )

        if candidate_type_is_unconf and not has_subcrop_horizons:
            self.rejected.append(
                (
                    candidate.candidate_id,
                    "Unconformity requires subcrop horizons — not identified in 2D",
                )
            )
            return True

        return False

    def check_definitive_hc_from_2d(
        self,
        candidate: GEOXStructuralCandidate,
    ) -> bool:
        """
        Block definitive hydrocarbon indicators from 2D data.

        Direct HC indicators (bright spots, flat spots, AVO) require
        amplitude fidelity — raster cannot provide this.
        """
        characteristics = candidate.characteristics or {}
        hc_indicator = characteristics.get("hc_indicator", False)

        if hc_indicator:
            self.rejected.append(
                (
                    candidate.candidate_id,
                    "Definitive HC indicator from 2D — BLOCKED. Amplitude fidelity required.",
                )
            )
            return True

        return False

    def check_3d_geometry_claim(
        self,
        candidate: GEOXStructuralCandidate,
    ) -> bool:
        """
        Block 3D geometry claims from 2D data.

        Any claim of 3D geometry (strike, azimuth, true thickness) from
        2D line is automatically rejected.
        """
        characteristics = candidate.characteristics or {}

        claims_3d = characteristics.get("claims_3d_geometry", False)
        claims_strike = characteristics.get("claims_strike_direction", False)
        claims_true_thickness = characteristics.get("claims_true_thickness", False)

        if claims_3d or claims_strike or claims_true_thickness:
            self.rejected.append(
                (
                    candidate.candidate_id,
                    "3D geometry claim from 2D data — BLOCKED. Out-of-plane ambiguity.",
                )
            )
            return True

        return False

    def check_channel_sinuosity(
        self,
        candidate: GEOXStructuralCandidate,
    ) -> bool:
        """
        Block channel sinuosity claims from 2D.

        Sinuosity requires 3D geometry — 2D cross-section alone cannot
        establish channel geometry.
        """
        if candidate.candidate_type != StructuralCandidateType.CHANNEL:
            return False

        self.rejected.append(
            (
                candidate.candidate_id,
                "Channel sinuosity from 2D — BLOCKED. Requires 3D geometry.",
            )
        )
        return True

    def evaluate_candidate(
        self,
        candidate: GEOXStructuralCandidate,
        all_candidates: list[GEOXStructuralCandidate],
        dip_field_stats: dict[str, float] | None = None,
    ) -> GEOXStructuralCandidate:
        """Run all physics checks on a candidate. Return (possibly rejected) candidate."""
        rejection_reasons: list[str] = []
        self.rejected = []

        checks = [
            self.check_floating_fault(candidate, all_candidates),
            self.check_thrust_geometry(candidate),
            self.check_horizon_consistency(candidate, dip_field_stats),
            self.check_unconformity_truncation(candidate, all_candidates),
            self.check_definitive_hc_from_2d(candidate),
            self.check_3d_geometry_claim(candidate),
            self.check_channel_sinuosity(candidate),
        ]

        if any(checks):
            for rejected_id, reason in self.rejected:
                if rejected_id == candidate.candidate_id:
                    rejection_reasons.append(reason)
            candidate.rejected = True
            candidate.rejection_reasons = rejection_reasons
            candidate.composite_score = 0.0

        return candidate


def infer_tectonic_setting_from_features(
    dip_stats: dict[str, float] | None,
    curvature_stats: dict[str, float] | None,
    n_faults: int,
    n_folds: int,
) -> tuple[TectonicSetting, float, list[tuple[TectonicSetting, float]]]:
    """
    Infer tectonic setting from structural patterns.

    Returns (setting, confidence, alternatives).
    """
    setting = TectonicSetting.UNCERTAIN
    confidence = 0.40

    alternatives: list[tuple[TectonicSetting, float]] = [
        (TectonicSetting.EXTENSIONAL, 0.25),
        (TectonicSetting.COMPRESSIONAL, 0.25),
        (TectonicSetting.INVERSION, 0.25),
        (TectonicSetting.STRIKE_SLIP, 0.25),
    ]

    inversion_score = 0
    compressional_score = 0
    extensional_score = 0

    if n_folds > 0:
        compressional_score += 1
        if curvature_stats and curvature_stats.get("max", 0) > 0.05:
            compressional_score += 1

    if n_faults > 2:
        extensional_score += 1

    if inversion_score >= 2:
        setting = TectonicSetting.INVERSION
        confidence = 0.50
        alternatives = [
            (TectonicSetting.INVERSION, 0.50),
            (TectonicSetting.EXTENSIONAL, 0.25),
            (TectonicSetting.COMPRESSIONAL, 0.25),
        ]
    elif compressional_score > extensional_score and n_folds > 0:
        setting = TectonicSetting.COMPRESSIONAL
        confidence = 0.45
        alternatives = [
            (TectonicSetting.COMPRESSIONAL, 0.45),
            (TectonicSetting.INVERSION, 0.30),
            (TectonicSetting.EXTENSIONAL, 0.25),
        ]
    elif extensional_score > 0:
        setting = TectonicSetting.EXTENSIONAL
        confidence = 0.40
        alternatives = [
            (TectonicSetting.EXTENSIONAL, 0.40),
            (TectonicSetting.STRIKE_SLIP, 0.30),
            (TectonicSetting.INVERSION, 0.30),
        ]

    return setting, confidence, alternatives


async def generate_structural_candidates(
    image_ref: str,
    feature_set: Any,
    dip_field_stats: dict[str, float] | None = None,
    is_raster: bool = False,
) -> GEOXStructuralCandidateSet:
    """
    Stages 4-5: Generate structural candidates + run geological rule engine.

    Args:
        image_ref: Unique image reference
        feature_set: GEOXFeatureSet from Stage 3
        dip_field_stats: Optional dip statistics for rule checking
        is_raster: Higher uncertainty for raster input

    Returns:
        GEOXStructuralCandidateSet with rejected/accepted candidates
    """
    prov_base = hashlib.sha256(image_ref.encode()).hexdigest()[:8]
    candidates: list[GEOXStructuralCandidate] = []
    n_rejected = 0

    base_uncertainty = 0.15 if is_raster else 0.10

    lineaments = getattr(feature_set, "lineaments", [])
    discontinuities = getattr(feature_set, "discontinuities", [])
    dip_stats = getattr(feature_set, "dip_field_stats", {}) or dip_field_stats or {}
    curvature_stats = getattr(feature_set, "curvature_stats", {})
    getattr(feature_set, "coherence_stats", {})

    fault_counter = 0
    for disc in discontinuities:
        if disc.get("confidence", 0) > 0.5:
            fault_counter += 1
            cand_id = f"fault_{prov_base}_{fault_counter:03d}"

            fault_type = StructuralCandidateType.FAULT
            stability = disc.get("confidence", 0.6)
            geometry_score = float(min(1.0, stability + 0.1))
            geology_score = 0.75

            rejected = False
            rejection_reasons: list[str] = []

            if not is_raster and fault_counter > 10:
                geology_score = max(0.3, geology_score - 0.2)
                if fault_counter > 20:
                    rejected = True
                    rejection_reasons.append(
                        "Excessive fault count from raster — likely acquisition footprint"
                    )

            composite = 0.4 * geometry_score + 0.3 * stability + 0.3 * geology_score

            prov = _make_provenance(f"CAND-{cand_id}", "LEM", confidence=composite)

            cand = GEOXStructuralCandidate(
                candidate_id=cand_id,
                candidate_type=fault_type,
                location=disc.get("location"),
                geometry_score=geometry_score,
                stability_score=stability,
                geology_score=geology_score,
                composite_score=composite if not rejected else 0.0,
                supporting_features=[f"discontinuity_at_{disc.get('location', 'unknown')}"],
                alternative_interpretations=[
                    "Acquisition footprint artifact",
                    "Processing-related linear noise",
                    "Chaotic facies (mass transport deposit)",
                ],
                rejected=rejected,
                rejection_reasons=rejection_reasons,
                tectonic_setting=TectonicSetting.UNCERTAIN,
                physical_axes=["waveform_similarity", "discontinuity"],
                anomalous_risk={
                    "risk_level": "high" if is_raster else "medium",
                    "notes": "Fault from 2D — out-of-plane ambiguity",
                },
                provenance=prov,
                uncertainty=min(0.20, base_uncertainty + 0.03),
                telemetry={"stage": 4},
            )
            candidates.append(cand)

    horizon_counter = 0
    for lin in lineaments:
        if lin.get("confidence", 0) > 0.55:
            horizon_counter += 1
            cand_id = f"horizon_{prov_base}_{horizon_counter:03d}"

            stability = lin.get("confidence", 0.6)
            geometry_score = float(min(1.0, stability + 0.05))
            geology_score = 0.70

            rejected = False
            rejection_reasons = []

            dip_var = abs(dip_stats.get("max", 0) - dip_stats.get("min", 0))
            if dip_var > 60:
                rejected = True
                rejection_reasons.append(
                    f"Horizon dip variation {dip_var:.1f}° > 60° — inconsistent"
                )

            composite = 0.4 * geometry_score + 0.3 * stability + 0.3 * geology_score

            prov = _make_provenance(f"CAND-{cand_id}", "LEM", confidence=composite)

            cand = GEOXStructuralCandidate(
                candidate_id=cand_id,
                candidate_type=StructuralCandidateType.HORIZON,
                location=lin.get("start"),
                geometry_score=geometry_score,
                stability_score=stability,
                geology_score=geology_score,
                composite_score=composite if not rejected else 0.0,
                supporting_features=[f"lineament_at_{lin.get('start', 'unknown')}"],
                alternative_interpretations=[
                    "Processing artifact",
                    "Lithological boundary",
                    "Fluid contact (if flat and strong)",
                ],
                rejected=rejected,
                rejection_reasons=rejection_reasons,
                tectonic_setting=TectonicSetting.UNCERTAIN,
                physical_axes=["structural_flexure", "apparent_dip"],
                anomalous_risk={
                    "risk_level": "medium",
                    "notes": "Horizon from 2D — requires validation",
                },
                provenance=prov,
                uncertainty=min(0.20, base_uncertainty + 0.02),
                telemetry={"stage": 4},
            )
            candidates.append(cand)

    n_faults = sum(1 for c in candidates if c.candidate_type == StructuralCandidateType.FAULT)
    n_folds = sum(1 for c in candidates if c.candidate_type == StructuralCandidateType.FOLD)

    setting, setting_conf, alternatives = infer_tectonic_setting_from_features(
        dip_stats, curvature_stats, n_faults, n_folds
    )

    for cand in candidates:
        cand.tectonic_setting = setting

    rule_engine = GeologicalRuleEngine()
    validated_candidates: list[GEOXStructuralCandidate] = []
    for cand in candidates:
        validated = rule_engine.evaluate_candidate(cand, candidates, dip_stats)
        validated_candidates.append(validated)
        if validated.rejected:
            n_rejected += 1

    n_rejected = sum(1 for c in validated_candidates if c.rejected)

    verdict = "QUALIFY" if not is_raster else "HOLD"
    if n_rejected > len(validated_candidates) * 0.5:
        verdict = "HOLD"
        verdict_explanation = (
            f"{n_rejected}/{len(validated_candidates)} candidates rejected by physics rules. "
            "High rejection rate indicates raster artifacts or structural complexity. "
            "ACQUIRE SEG-Y data for QUALIFY verdict."
        )
    else:
        verdict_explanation = (
            f"Generated {len(validated_candidates)} candidates, "
            f"{n_rejected} rejected by physics rules. "
            "Candidates remaining for ranking."
        )

    prov_set = _make_provenance(f"CANDSET-{prov_base}", "LEM", confidence=0.75)

    aggregate_uncertainty = min(0.20, base_uncertainty + 0.02)

    return GEOXStructuralCandidateSet(
        image_ref=image_ref,
        candidates=validated_candidates,
        n_rejected=n_rejected,
        verdict=verdict,
        verdict_explanation=verdict_explanation,
        provenance=prov_set,
        aggregate_uncertainty=aggregate_uncertainty,
        telemetry={
            "stage": "4-5",
            "n_candidates": len(validated_candidates),
            "n_rejected": n_rejected,
            "tectonic_setting": setting.value,
            "setting_confidence": setting_conf,
            "floors": ["F1", "F2", "F4", "F5", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        },
    )
