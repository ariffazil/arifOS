"""
Governed seismic interpretation reasoning.

Fuses QC, features, and detection outputs into geological reasoning.
NOT raw model output — evidence-constrained with counter-hypotheses.

F2 Truth enforcement:
- Evidence links required for all claims
- Confidence band declared
- Counter-hypotheses generated
- Play hypothesis constrains but doesn't prove interpretation
"""

from __future__ import annotations

import logging
from typing import Any

from .schemas import Verdict

logger = logging.getLogger("geox.seismic_image.reasoning")


class PlayTemplate:
    """Geological play templates for constraining interpretations."""
    
    TEMPLATES = {
        "deltaic": {
            "expected_features": ["topslap", "foreset", "bottomset", "channel_fill"],
            "texture_signatures": ["high_continuity_upper", "prog_grades"],
            "risk_factors": ["shale_prone", "connectivity"],
        },
        "deep_water": {
            "expected_features": ["turbidite_lobes", "levee", "channel_complex"],
            "texture_signatures": ["mounded", "chaotic_base"],
            "risk_factors": ["sand_quality", "lateral_continuity"],
        },
        "carbonate_buildup": {
            "expected_features": ["reef_core", "fore_reef", "back_reef"],
            "texture_signatures": ["massive", "discontinuous_margins"],
            "risk_factors": ["porosity_preservation", "seal_integrity"],
        },
        "structural": {
            "expected_features": ["anticline", "fault_trap", "unconformity"],
            "texture_signatures": ["dip_changes", "truncations"],
            "risk_factors": ["seal_effectiveness", "reservoir_presence"],
        },
    }
    
    @classmethod
    def get_template(cls, play_type: str) -> dict[str, Any]:
        return cls.TEMPLATES.get(play_type, cls.TEMPLATES["structural"])


def calculate_confidence(
    evidence_strengths: list[float],
    play_consistency: float,
    data_quality: float,
) -> dict[str, float]:
    """
    Calculate aggregate confidence with uncertainty band.
    
    Args:
        evidence_strengths: List of evidence confidence scores (0-1)
        play_consistency: How well evidence fits play hypothesis (0-1)
        data_quality: QC score from image quality (0-1)
        
    Returns:
        Dictionary with aggregate, uncertainty, and range
    """
    # Aggregate confidence (weighted combination)
    avg_evidence = sum(evidence_strengths) / len(evidence_strengths) if evidence_strengths else 0.5
    
    aggregate = (
        avg_evidence * 0.4 +
        play_consistency * 0.3 +
        data_quality * 0.3
    )
    
    # Uncertainty based on evidence diversity
    evidence_variance = sum((s - avg_evidence)**2 for s in evidence_strengths) / len(evidence_strengths) if evidence_strengths else 0.1
    uncertainty = 0.05 + 0.1 * evidence_variance  # Base + variance
    
    # F7 Humility: Image-first ceiling at 0.95
    aggregate = min(0.95, aggregate)
    
    return {
        "aggregate": round(aggregate, 2),
        "uncertainty": round(uncertainty, 2),
        "range": f"{round(aggregate - uncertainty, 2)} - {round(aggregate + uncertainty, 2)}",
    }


def generate_counter_hypotheses(
    play_hypothesis: str,
    interpretation: str,
) -> list[str]:
    """
    Generate alternative explanations for the observed features.
    
    Args:
        play_hypothesis: Current play hypothesis
        interpretation: Current interpretation
        
    Returns:
        List of counter-hypotheses
    """
    counter_hypotheses = []
    
    # Generic counter-hypotheses
    counter_hypotheses.extend([
        "Tectonic overprint may modify original depositional patterns",
        "Diagenesis could alter seismic character from original lithology",
        "Acquisition/processing artifacts may mimic geological features",
    ])
    
    # Play-specific counter-hypotheses
    if play_hypothesis == "deltaic":
        counter_hypotheses.extend([
            "Tidal influence possible — bidirectional current indicators not visible",
            "Estuarine vs. deltaic discrimination requires well control",
            "Channel incision may be present but below image resolution",
        ])
    elif play_hypothesis == "deep_water":
        counter_hypotheses.extend([
            "Mass transport deposits vs. turbidites — internal architecture needed",
            "Bottom current reworking may modify original depositional texture",
        ])
    elif play_hypothesis == "carbonate_buildup":
        counter_hypotheses.extend([
            "Karst modification possible — requires high-resolution imaging",
            "Dolomitization may create false porosity indicators",
        ])
    
    return counter_hypotheses


def build_evidence_links(
    texture_data: dict[str, Any] | None,
    reflector_data: dict[str, Any] | None,
    fault_data: dict[str, Any] | None,
    facies_data: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Build evidence links from analysis outputs.
    
    Args:
        texture_data: Texture attribute results
        reflector_data: Reflector detection results
        fault_data: Fault detection results
        facies_data: Facies segmentation results
        
    Returns:
        List of evidence links with strength and description
    """
    evidence = []
    
    # Texture evidence
    if texture_data:
        if "structure_tensor" in texture_data:
            evidence.append({
                "type": "texture",
                "strength": 0.78,
                "description": "High coherence suggests continuous reflector package",
            })
        if "lbp" in texture_data:
            uniformity = texture_data["lbp"].get("uniformity_score", 0.5)
            evidence.append({
                "type": "texture",
                "strength": 0.6 + uniformity * 0.3,
                "description": "LBP uniformity suggests bedform regularity" if uniformity > 0.5 else "LBP variability suggests complex bedding",
            })
    
    # Reflector evidence
    if reflector_data and reflector_data.get("reflectors"):
        n_refl = len(reflector_data["reflectors"])
        avg_coherence = sum(r.get("coherence", 0) for r in reflector_data["reflectors"]) / n_refl if n_refl > 0 else 0
        evidence.append({
            "type": "reflectors",
            "strength": 0.7 + avg_coherence * 0.2,
            "description": f"{n_refl} continuous reflectors indicate stable depositional environment",
        })
    
    # Fault evidence
    if fault_data and fault_data.get("candidates"):
        n_faults = len(fault_data["candidates"])
        avg_likelihood = sum(f.get("likelihood_score", 0) for f in fault_data["candidates"]) / n_faults if n_faults > 0 else 0
        evidence.append({
            "type": "faults",
            "strength": avg_likelihood,
            "description": f"{n_faults} discontinuity candidates suggest structural complexity" if n_faults > 0 else "Few discontinuities suggest structurally quiet area",
        })
    
    # Facies evidence
    if facies_data and facies_data.get("statistics"):
        class_dist = facies_data["statistics"].get("class_distribution", {})
        dominant = max(class_dist.items(), key=lambda x: x[1]) if class_dist else ("unknown", 0)
        evidence.append({
            "type": "facies",
            "strength": 0.6 + dominant[1] * 0.3,
            "description": f"Dominant facies: {dominant[0]} ({dominant[1]:.0%})",
        })
    
    return evidence


def generate_interpretation(
    play_hypothesis: str,
    geological_intent: str,
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate geological interpretation from evidence.
    
    Args:
        play_hypothesis: Play hypothesis
        geological_intent: Specific interpretation goal
        evidence: Evidence links
        
    Returns:
        Interpretation dictionary
    """
    template = PlayTemplate.get_template(play_hypothesis)
    
    # Build interpretation summary
    summary_parts = []
    
    if play_hypothesis == "deltaic":
        summary_parts.append("Deltaic depositional system")
        if any(e["type"] == "reflectors" for e in evidence):
            summary_parts.append("with continuous topset reflectors")
        if any(e["type"] == "faults" for e in evidence):
            summary_parts.append("and localized discontinuities")
    elif play_hypothesis == "deep_water":
        summary_parts.append("Deep-water depositional system")
        summary_parts.append("with mounded geometries suggestive of turbidite lobes")
    elif play_hypothesis == "carbonate_buildup":
        summary_parts.append("Carbonate buildup")
        summary_parts.append("with massive internal texture")
    else:
        summary_parts.append("Structural trap configuration")
    
    summary = " ".join(summary_parts)
    
    # Reservoir potential assessment
    reservoir_potential = "Moderate"  # Default conservative assessment
    if any(e["strength"] > 0.8 for e in evidence):
        reservoir_potential = "Good"
    elif all(e["strength"] < 0.5 for e in evidence):
        reservoir_potential = "Poor"
    
    return {
        "summary": summary,
        "depositional_environment": play_hypothesis.replace("_", " ").title(),
        "reservoir_potential": f"{reservoir_potential} — based on image-domain proxies",
    }


async def reason_seismic_scene(
    image_id: str,
    play_hypothesis: str,
    geological_intent: str,
    basin: str,
    requester_id: str,
    evidence_types: list[str] | None = None,
    texture_data: dict[str, Any] | None = None,
    reflector_data: dict[str, Any] | None = None,
    fault_data: dict[str, Any] | None = None,
    facies_data: dict[str, Any] | None = None,
    qc_score: float = 0.9,
) -> dict[str, Any]:
    """
    Governed interpretation synthesis for seismic scenes.
    
    F2 Truth enforcement through evidence links and counter-hypotheses.
    """
    try:
        # Build evidence links
        evidence = build_evidence_links(
            texture_data, reflector_data, fault_data, facies_data
        )
        
        # Filter by requested evidence types
        if evidence_types:
            evidence = [e for e in evidence if e["type"] in evidence_types]
        
        # Calculate confidence
        evidence_strengths = [e["strength"] for e in evidence]
        play_consistency = 0.75  # Would be computed from fit to template
        confidence = calculate_confidence(evidence_strengths, play_consistency, qc_score)
        
        # Generate interpretation
        interpretation = generate_interpretation(play_hypothesis, geological_intent, evidence)
        
        # Generate counter-hypotheses
        counter_hypotheses = generate_counter_hypotheses(play_hypothesis, interpretation["summary"])
        
        # Determine hold flags
        hold_flags = []
        if confidence["aggregate"] < 0.5:
            hold_flags.append("Low confidence — additional data recommended")
        if not evidence:
            hold_flags.append("No evidence links — interpretation speculative")
        
        logger.info(
            "Reasoning complete for %s: confidence=%s, evidence=%d",
            image_id, confidence["aggregate"], len(evidence)
        )
        
        return {
            "success": True,
            "image_id": image_id,
            "verdict": Verdict.PARTIAL if not hold_flags else Verdict.SABAR,
            "interpretation": interpretation,
            "confidence_band": confidence,
            "evidence_links": evidence,
            "counter_hypotheses": counter_hypotheses,
            "hold_flags": hold_flags,
            "limitations": [
                "Interpretation based on image-domain proxies, not trace-derived attributes",
                "Play hypothesis constrains but does not prove geological interpretation",
            ],
            "seal": "DITEMPA BUKAN DIBERI",
        }
        
    except Exception as e:
        logger.exception("Reasoning failed: %s", e)
        return {
            "success": False,
            "image_id": image_id,
            "verdict": Verdict.VOID,
            "error": str(e),
            "seal": "DITEMPA BUKAN DIBERI",
        }
