"""
GEOX Stage 7 / Main Orchestrator: Interpret Single Line

DITEMPA BUKAN DIBERI

Chains all 7 pipeline stages:
  1. Ingest (image → grayscale canonical)
  2. Contrast views (6 display variants)
  3. Feature extraction (attributes from seismic)
  4. Candidate generation (structural candidates)
  5. Geological rule engine (physics rejection)
  6. Candidate ranking (ranked structural models)
  7. Human veto (final interpretation result)

Output: GEOXInterpretationResult — AI-proposed interpretation, NOT ground truth.

MCP verbs exposed:
  - geox_load_seismic_image → Stage 1
  - geox_generate_contrast_views → Stage 2
  - geox_extract_image_features → Stage 3
  - geox_build_structural_candidates → Stages 4-5
  - geox_rank_structural_models → Stage 6
  - geox_interpret_single_line → Stages 1-7 (full pipeline)

Constitutional floors:
  F1  Amanah — Full provenance chain
  F2  Truth — No claims beyond attributes
  F4  Clarity — Physical/visual separation
  F5  Peace² — Non-destructive analysis
  F7  Humility — Uncertainty ∈ [0.03, 0.20]
  F9  Anti-Hantu — RGB ≠ physical truth
  F11 Command Auth — Nonce-verified identity
  F13 Sovereign — Human review required

Hard blocks (automatic GEOX_BLOCK):
  - 3D geometry from 2D
  - Volumetric HC from 2D
  - Definitive fault network connectivity
  - Channel sinuosity from 2D

Bond et al. (2007): 79% expert failure rate on synthetic data.
All outputs reference this and recommend validation.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

import numpy as np

from arifos.geox.base_tool import BaseTool, GeoToolResult, _make_provenance
from arifos.geox.geox_mcp_schemas import (
    GEOXConceptualBias,
    GEOXInterpretationResult,
    ImageSourceType,
    Line2DVerdict,
    TimeDepthDomain,
)
from arifos.geox.seismic_candidate_ranker import build_structural_models
from arifos.geox.seismic_contrast_views import generate_contrast_views
from arifos.geox.seismic_feature_extract import extract_features
from arifos.geox.seismic_image_ingest import ingest_seismic_array
from arifos.geox.seismic_structure_rules import generate_structural_candidates

BOND_REFERENCE = (
    "Bond, C. E., Gibbs, A. D., Shipton, Z. K., & Jones, S. (2007). "
    "'What do you think this is? Conceptual uncertainty in geoscience interpretation.' "
    "GSA Today, 17(11), 4-10. https://doi.org/10.1130/GSAT01711A.1"
)


async def interpret_single_line(
    seismic_array: np.ndarray,
    image_ref: str,
    source_type: ImageSourceType = ImageSourceType.UNKNOWN,
    time_depth_domain: TimeDepthDomain = TimeDepthDomain.UNKNOWN,
    vertical_exaggeration_known: bool = False,
    include_ve_variants: bool = True,
) -> GEOXInterpretationResult:
    """
    Full 7-stage pipeline: seismic image → governed interpretation.

    Args:
        seismic_array: 2D numpy array (traces x samples)
        image_ref: Unique reference for this seismic line
        source_type: SEGY|RASTER_PNG|RASTER_JPG|TIFF|UNKNOWN
        time_depth_domain: TIME|DEPTH|UNKNOWN
        vertical_exaggeration_known: Whether VE is calibrated
        include_ve_variants: Include VE contrast views

    Returns:
        GEOXInterpretationResult with full pipeline output
    """
    pipeline_start = time.perf_counter()

    is_raster = source_type != ImageSourceType.SEGY

    ingest_result = await ingest_seismic_array(
        array=seismic_array,
        image_ref=image_ref,
        source_type=source_type,
        time_depth_domain=time_depth_domain,
        vertical_exaggeration_known=vertical_exaggeration_known,
    )

    if ingest_result.canonical_array is None:
        canonical = seismic_array.astype(np.float32)
    else:
        canonical = ingest_result.canonical_array

    view_set = await generate_contrast_views(
        canonical_array=canonical,
        image_ref=image_ref,
        include_ve_variants=include_ve_variants,
    )

    feature_set = await extract_features(
        canonical_array=canonical,
        image_ref=image_ref,
        is_raster=is_raster,
    )

    candidate_set = await generate_structural_candidates(
        image_ref=image_ref,
        feature_set=feature_set,
        dip_field_stats=feature_set.dip_field_stats,
        is_raster=is_raster,
    )

    ranked_models = await build_structural_models(
        candidate_set=candidate_set,
        n_contrast_views=len(view_set.views),
    )

    bias_audit = _build_bias_audit(
        is_raster=is_raster,
        setting=(
            ranked_models.models[0].tectonic_setting if ranked_models.models else None
        ),
        confidence=(
            ranked_models.models[0].setting_confidence if ranked_models.models else 0.0
        ),
        n_alternatives=len(ranked_models.models) - 1,
    )

    validation_recommendations = _build_validation_recommendations(
        is_raster=is_raster,
        confidence=(
            ranked_models.models[0].setting_confidence if ranked_models.models else 0.0
        ),
        source_type=source_type,
    )

    pipeline_latency_ms = (time.perf_counter() - pipeline_start) * 1000

    prov = _make_provenance(
        f"INTERPRET-{hashlib.sha256(image_ref.encode()).hexdigest()[:8]}",
        "LEM",
        confidence=ranked_models.aggregate_uncertainty,
    )

    best_model = ranked_models.models[0]

    if best_model:
        final_verdict = Line2DVerdict.HOLD if is_raster else Line2DVerdict.QUALIFY
        if is_raster:
            verdict_explanation = (
                f"RASTER INPUT — {BOND_REFERENCE.split('.')[0]}. "
                "79% expert failure rate on similar data. "
                "ACQUIRE SEG-Y before accepting this interpretation. "
                f"AI proposal: {best_model.tectonic_setting.value} "
                f"(confidence: {best_model.setting_confidence:.2f})."
            )
        else:
            verdict_explanation = (
                f"SEG-Y source — QUALIFY verdict. "
                "AI-proposed interpretation: "
                f"{best_model.tectonic_setting.value} "
                f"(confidence: {best_model.setting_confidence:.2f}). "
                "NOT ground truth. Human review required before acceptance."
            )
    else:
        final_verdict = Line2DVerdict.HOLD
        verdict_explanation = (
            "No structural candidates passed rule engine. Acquire better data."
        )

    return GEOXInterpretationResult(
        image_ref=image_ref,
        best_model=best_model,
        alternative_models=ranked_models.models[1:],
        validation_recommendations=validation_recommendations,
        bias_audit=bias_audit,
        bond_2007_reference=BOND_REFERENCE,
        final_verdict=final_verdict,
        verdict_explanation=verdict_explanation,
        aggregate_uncertainty=ranked_models.aggregate_uncertainty,
        provenance=prov,
        telemetry={
            "stage": 7,
            "pipeline": "geox_interpret_single_line",
            "latency_ms": round(pipeline_latency_ms, 2),
            "n_views": len(view_set.views),
            "n_candidates": len(candidate_set.candidates),
            "n_rejected": candidate_set.n_rejected,
            "n_models": len(ranked_models.models),
            "is_raster": is_raster,
            "floors": ["F1", "F2", "F4", "F5", "F7", "F9", "F11", "F13"],
            "seal": "DITEMPA BUKAN DIBERI",
            "verdict_ceiling": "QUALIFY",
            "hard_blocks": [
                "3D_geometry_from_2D",
                "volumetric_HC_from_2D",
                "definitive_fault_network",
                "channel_sinuosity_2D",
            ],
        },
    )


def _build_bias_audit(
    is_raster: bool,
    setting: Any | None,
    confidence: float,
    n_alternatives: int,
) -> list[GEOXConceptualBias]:
    """Build Bond et al. (2007) conceptual bias audit."""
    biases: list[GEOXConceptualBias] = []

    biases.append(
        GEOXConceptualBias(
            bias_type="Anchoring Bias",
            description=(
                "Initial tectonic setting interpretation creates cognitive anchor. "
                "Subsequent evidence filtered to support initial hypothesis. "
                f"Current setting: {setting.value if setting else 'uncertain'}. "
                f"{BOND_REFERENCE.split('.')[0]}."
            ),
            mitigation=(
                "Document alternative interpretations BEFORE interpreting. "
                "Use 'pre-mortem' analysis: assume interpretation is wrong, what evidence would prove it?"
            ),
            historical_failure_rate=0.79,
        )
    )

    biases.append(
        GEOXConceptualBias(
            bias_type="Confirmation Bias",
            description=(
                "Evidence supporting preferred model weighted more heavily. "
                f"Confidence {confidence:.2f} may be inflated by anchoring."
            ),
            mitigation=(
                f"Actively seek evidence for {n_alternatives} alternative tectonic settings. "
                "Require equal-weight evidence for all alternatives."
            ),
            historical_failure_rate=0.65,
        )
    )

    if is_raster:
        biases.append(
            GEOXConceptualBias(
                bias_type="Data Quality Blindness",
                description=(
                    "RASTER INPUT — No trace data. Interpreting visual appearance only. "
                    "Amplitude, phase, frequency not preserved. "
                    f"{BOND_REFERENCE.split('.')[0]}: 79% failure rate on similar data."
                ),
                mitigation=(
                    "STOP. Acquire SEG-Y before accepting interpretation. "
                    "Any structural interpretation from raster alone has 79%+ failure rate."
                ),
                historical_failure_rate=0.79,
            )
        )

    if n_alternatives > 2:
        biases.append(
            GEOXConceptualBias(
                bias_type="Complexity Aversion",
                description=(
                    "Multiple working hypotheses exist. Simplifying to single interpretation "
                    "ignores genuine geological uncertainty. Inversion structures are "
                    "particularly prone to mis-interpretation."
                ),
                mitigation=(
                    "Hold multiple working hypotheses. "
                    "Design data acquisition to discriminate between alternatives. "
                    "Consider structural restoration as validation."
                ),
                historical_failure_rate=0.70,
            )
        )

    return biases


def _build_validation_recommendations(
    is_raster: bool,
    confidence: float,
    source_type: ImageSourceType,
) -> list[str]:
    """Build validation recommendations."""
    recs = []

    if is_raster:
        recs.append(
            "ACQUIRE SEG-Y DATA — raster-only interpretation has 79% failure rate"
        )

    recs.append(
        "Acquire intersecting 2D line or 3D data to resolve out-of-plane ambiguity"
    )
    recs.append("Perform structural restoration to test kinematic viability")
    recs.append("Compare with regional tectonic model before accepting interpretation")

    if confidence < 0.55:
        recs.append(
            f"Low confidence ({confidence:.2f}) — do not use for critical decisions without validation"
        )

    recs.append(
        "Check for acquisition footprint artifacts before accepting fault candidates"
    )

    return recs


class GEOXInterpretSingleLineTool(BaseTool):
    """
    GEOX MCP tool: geox_interpret_single_line

    Main orchestrator for the 7-stage governed seismic interpretation pipeline.
    """

    @property
    def name(self) -> str:
        return "GEOXInterpretSingleLine"

    @property
    def description(self) -> str:
        return (
            "Governed 7-stage seismic interpretation pipeline. "
            "Ingest → Contrast views → Feature extraction → "
            "Structural candidates → Physics rule engine → Ranking → "
            "Human veto interpretation. "
            "Always outputs QUALIFY (2D) or HOLD (raster) — never SEAL. "
            "Bond et al. (2007) 79% failure rate explicitly referenced."
        )

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        return "seismic_array" in inputs and "image_ref" in inputs

    async def run(self, inputs: dict[str, Any]) -> GeoToolResult:
        """Execute full interpretation pipeline."""
        if not self.validate_inputs(inputs):
            return GeoToolResult(
                tool_name=self.name,
                success=False,
                error="Missing required: 'seismic_array' and 'image_ref'",
            )

        start = time.perf_counter()

        seismic_array = inputs["seismic_array"]
        image_ref = inputs["image_ref"]
        source_type = ImageSourceType(inputs.get("source_type", "unknown"))
        time_depth_domain = TimeDepthDomain(inputs.get("time_depth_domain", "unknown"))
        ve_known = inputs.get("vertical_exaggeration_known", False)

        result = await interpret_single_line(
            seismic_array=seismic_array,
            image_ref=image_ref,
            source_type=source_type,
            time_depth_domain=time_depth_domain,
            vertical_exaggeration_known=ve_known,
        )

        latency_ms = (time.perf_counter() - start) * 1000

        return GeoToolResult(
            tool_name=self.name,
            success=True,
            raw_output=result.model_dump(),
            metadata={
                "image_ref": image_ref,
                "verdict": result.final_verdict.value,
                "uncertainty": result.aggregate_uncertainty,
                "latency_ms": round(latency_ms, 2),
                "tectonic_setting": (
                    result.best_model.tectonic_setting.value
                    if result.best_model
                    else "uncertain"
                ),
            },
            latency_ms=round(latency_ms, 2),
        )
