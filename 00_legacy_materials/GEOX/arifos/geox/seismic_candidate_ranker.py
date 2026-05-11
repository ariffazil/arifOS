"""
GEOX Stage 6: Structural Candidate Ranker

DITEMPA BUKAN DIBERI

Rank structural candidates by composite score:
  composite = 0.4 * geometry_score + 0.3 * stability_score + 0.3 * geology_score

Stability = seen in N contrast views / total views.
Candidates seen across ALL views are most robust.

Stage 6: Candidate set → Ranked structural models

Output:
  - Ranked list of structural models (best → worst)
  - Per-model: tectonic setting, candidate IDs, scores
  - Uncertainty per model
  - Verdict ceiling: QUALIFY (2D line cannot produce SEAL)

Constitutional floors:
  F4  Clarity — Score components explicit
  F7  Humility — Uncertainty ∈ [0.03, 0.20]
  F8  G (Genius) — Internal coherence score
  F13 Sovereign — Human review for ambiguous structural settings
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from arifos.geox.base_tool import _make_provenance
from arifos.geox.geox_mcp_schemas import (
    GEOXRankedModelSet,
    GEOXRankedStructuralModel,
    GEOXStructuralCandidateSet,
    TectonicSetting,
)


def compute_stability_from_views(
    candidate_id: str,
    n_views: int,
    features_per_view: dict[str, list[str]],
) -> float:
    """
    Compute stability score: fraction of views where candidate was detected.

    Candidates detected in ALL views are most robust (stability = 1.0).
    """
    if n_views == 0:
        return 0.0

    view_count = sum(
        1 for feature_refs in features_per_view.values() if candidate_id in feature_refs
    )

    return min(1.0, view_count / n_views)


def rank_candidates_by_score(
    candidates: list[Any],
    n_views: int = 6,
    features_per_view: dict[str, list[str]] | None = None,
) -> list[Any]:
    """
    Rank candidates by composite score (geometry + stability + geology).

    Returns sorted list best → worst.
    """
    scored = []

    for cand in candidates:
        if cand.rejected:
            composite = 0.0
        else:
            stability = compute_stability_from_views(
                cand.candidate_id, n_views, features_per_view or {}
            )

            geometry = cand.geometry_score
            geology = cand.geology_score

            composite = 0.4 * geometry + 0.3 * stability + 0.3 * geology

            cand = (
                self._update_cand(cand, composite, stability)
                if hasattr(cand, "_update_cand")
                else cand
            )
            cand.composite_score = composite
            cand.stability_score = stability

        scored.append(cand)

    return sorted(scored, key=lambda x: x.composite_score, reverse=True)


async def build_structural_models(
    candidate_set: GEOXStructuralCandidateSet,
    n_contrast_views: int = 6,
) -> GEOXRankedModelSet:
    """
    Stage 6: Rank candidates and build structural models.

    Args:
        candidate_set: GEOXStructuralCandidateSet from Stages 4-5
        n_contrast_views: Number of contrast views (for stability scoring)

    Returns:
        GEOXRankedModelSet with ranked structural models
    """
    image_ref = candidate_set.image_ref
    prov_base = hashlib.sha256(image_ref.encode()).hexdigest()[:8]

    non_rejected = [c for c in candidate_set.candidates if not c.rejected]

    sorted_candidates = sorted(
        non_rejected, key=lambda x: x.composite_score, reverse=True
    )

    [c for c in sorted_candidates if c.candidate_type.value == "fault"]
    [c for c in sorted_candidates if c.candidate_type.value == "horizon"]
    [c for c in sorted_candidates if c.candidate_type.value == "fold"]

    base_uncertainty = candidate_set.aggregate_uncertainty

    best_setting = candidate_set.telemetry.get("tectonic_setting", "uncertain")
    try:
        setting_enum = TectonicSetting(best_setting)
    except (ValueError, TypeError):
        setting_enum = TectonicSetting.UNCERTAIN

    setting_confidence = candidate_set.telemetry.get("setting_confidence", 0.40)

    overall_geometry = (
        float(np.mean([c.geometry_score for c in non_rejected]))
        if non_rejected
        else 0.0
    )
    overall_stability = (
        float(np.mean([c.stability_score for c in non_rejected]))
        if non_rejected
        else 0.0
    )
    overall_geology = (
        float(np.mean([c.geology_score for c in non_rejected])) if non_rejected else 0.0
    )

    composite = 0.4 * overall_geometry + 0.3 * overall_stability + 0.3 * overall_geology

    best_model = GEOXRankedStructuralModel(
        model_id=f"model_{prov_base}_best",
        tectonic_setting=setting_enum,
        setting_confidence=setting_confidence,
        candidate_ids=[c.candidate_id for c in sorted_candidates[:5]],
        geometry_score=overall_geometry,
        stability_score=overall_stability,
        geology_score=overall_geology,
        composite_score=composite,
        alternative_models=[],
        physical_axes=["structural_geometry", "fault_horizon_relationships"],
        anomalous_risk=(
            candidate_set.candidates[0].anomalous_risk
            if candidate_set.candidates
            else {}
        ),
        provenance=_make_provenance(f"MODEL-{prov_base}", "LEM", confidence=composite),
        uncertainty=base_uncertainty,
        telemetry={
            "stage": 6,
            "n_candidates_ranked": len(sorted_candidates),
            "floors": ["F4", "F7", "F8", "F13"],
            "seal": "DITEMPA BUKAN DIBERI",
        },
    )

    alternative_models: list[GEOXRankedStructuralModel] = []

    for alt_setting in [s for s in TectonicSetting if s != setting_enum][:3]:
        alt_score = composite * 0.85

        alt_model = GEOXRankedStructuralModel(
            model_id=f"model_{prov_base}_alt_{alt_setting.value}",
            tectonic_setting=alt_setting,
            setting_confidence=setting_confidence * 0.7,
            candidate_ids=[c.candidate_id for c in sorted_candidates[:3]],
            geometry_score=overall_geometry * 0.9,
            stability_score=overall_stability * 0.9,
            geology_score=overall_geology * 0.85,
            composite_score=alt_score,
            alternative_models=[],
            physical_axes=["structural_geometry"],
            anomalous_risk={
                "risk_level": "high",
                "notes": f"Alternative {alt_setting.value} model — requires validation",
            },
            provenance=_make_provenance(
                f"MODEL-{prov_base}-{alt_setting.value}", "LEM", confidence=alt_score
            ),
            uncertainty=min(0.20, base_uncertainty + 0.03),
            telemetry={"stage": 6, "alternative": True},
        )
        alternative_models.append(alt_model)

    if candidate_set.verdict == "HOLD" or setting_confidence < 0.55:
        final_verdict = "HOLD"
        verdict_explanation = (
            f"Raster input or low confidence ({setting_confidence:.2f}). "
            "Structural model tentative. "
            "Acquire SEG-Y or intersecting line for validation."
        )
    elif composite < 0.50:
        final_verdict = "QUALIFY"
        verdict_explanation = (
            f"Composite score {composite:.2f} < 0.50 — model weak. "
            "QUALIFY verdict. Human review required. "
            "Multiple alternatives equally plausible."
        )
    else:
        final_verdict = "QUALIFY"
        verdict_explanation = (
            f"Best structural model: {setting_enum.value} "
            f"(confidence: {setting_confidence:.2f}, composite: {composite:.2f}). "
            "QUALIFY verdict for 2D line. "
            "This is AI-proposed interpretation — NOT ground truth. "
            "Human review required before acceptance."
        )

    prov_set = _make_provenance(f"RANKED-{prov_base}", "LEM", confidence=composite)

    return GEOXRankedModelSet(
        image_ref=image_ref,
        models=[best_model] + alternative_models,
        best_model_id=best_model.model_id,
        provenance=prov_set,
        aggregate_uncertainty=base_uncertainty,
        verdict=final_verdict,
        verdict_explanation=verdict_explanation,
        telemetry={
            "stage": 6,
            "n_models": len(alternative_models) + 1,
            "best_composite": composite,
            "setting_confidence": setting_confidence,
            "floors": ["F4", "F7", "F8", "F13"],
            "seal": "DITEMPA BUKAN DIBERI",
            "verdict_ceiling": "QUALIFY",
        },
    )
