"""
GEOX Contrast Wrapper — Enforces Contrast Canon at Tool Boundary
DITEMPA BUKAN DIBERI

Mandatory metadata for every seismic/image/attribute output.
Never let perceptual contrast be silently confused with physical contrast.

Constitutional Floors Enforced:
  F1  Amanah — Reversibility through explicit provenance
  F4  Clarity — Physical vs perceptual axes clearly labeled
  F7  Humility — Uncertainty bounds on all meta-attributes
  F9  Anti-Hantu — No phantom geological meaning from display artifacts
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from .geox_schemas import (
    ContrastMetadata,
    GeoxGovernance,
    GeoxMcpEnvelope,
    GeoxUncertainty,
)

T = TypeVar("T")


def contrast_governed_tool(
    physical_axes: list[str] | None = None,
    equation_ref: str | None = None,
    is_meta_attribute: bool = False,
) -> Callable:
    """
    Decorator factory for seismic attribute functions.

    Automatically attaches ContrastMetadata and enforces
    constitutional floors on all attribute outputs.
    Handles both dict and Pydantic model outputs.
    """

    def decorator(func: Callable) -> Callable:
        # If physical_axes is None, we might be calling it as @contrast_governed_tool
        # without parentheses, or just with defaults.
        axes = physical_axes or ["perceptual_lineaments"]

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> GeoxMcpEnvelope:
            result = await func(*args, **kwargs)

            # If already wrapped, don't double wrap
            if isinstance(result, GeoxMcpEnvelope):
                return result

            attr_name = kwargs.get("attribute_name", func.__name__)

            # 1. Build Contrast Metadata
            contrast_dict = ContrastMetadata(
                attribute_name=attr_name,
                physical_axes=axes,
                processing_steps=kwargs.get("processing_steps", ["default"]),
                visual_encoding=kwargs.get(
                    "visual_encoding",
                    {
                        "colormap": "gray_inverted",
                        "dynamic_range": "p2-p98",
                        "gamma": 1.0,
                    },
                ),
                anomalous_risk=_generate_anomalous_risk(attr_name, is_meta_attribute),
                equation_reference=equation_ref,
                uncertainty_factors=_generate_uncertainty_factors(attr_name),
            )

            # 2. Build Governance Block
            floors = ["F1", "F4", "F7"]
            if is_meta_attribute:
                floors.append("F9")

            warnings = []
            if is_meta_attribute and not kwargs.get("well_ties"):
                warnings.append(
                    "Meta-attribute without well tie validation. "
                    "Perceptual contrast may dominate physical signal."
                )

            gov = GeoxGovernance(floors_ok=floors, warnings=warnings)

            # 3. Build Uncertainty Block
            unc = GeoxUncertainty(
                level=0.12 if is_meta_attribute else 0.05,
                type=(
                    "image_only_structural_interpretation"
                    if "line" in attr_name
                    else "perceptual_lineament"
                ),
                notes=_generate_uncertainty_factors(attr_name),
            )

            # 4. Construct Final Envelope
            return GeoxMcpEnvelope(
                ok=True,
                verdict="PASS" if not warnings else "PARTIAL",
                source_domain="geox-earth-witness",
                uncertainty=unc,
                contrast_metadata=contrast_dict,
                governance=gov,
                result=result,
            )

        return wrapper

    # Handle the case where the decorator is used as @contrast_governed_tool
    if callable(physical_axes):
        f = physical_axes
        physical_axes = None
        return decorator(f)

    return decorator


def _generate_anomalous_risk(name: str, is_meta: bool) -> dict[str, Any]:
    """
    Generate anomalous risk assessment based on attribute type.

    Classical attributes (coherence, curvature) have low display bias.
    Meta-attributes (ML fusion) have high risk of perceptual artifacts.
    """
    if is_meta or "meta" in name.lower() or "fault_prob" in name.lower():
        return {
            "display_bias": "high",
            "risk_level": "critical",
            "notes": (
                "Learned meta-attribute may amplify perceptual contrast not fully "
                "grounded in physics. Physical traceability is partial. "
                "Mandatory validation: well ties, horizon flattening, structural timing. "
                "F7 Humility enforced: uncertainty >= 0.12"
            ),
            "mitigation": [
                "Cross-validate with classical attributes",
                "Require well tie verification",
                "Check for acquisition footprint artifacts",
                "Validate against known geology",
            ],
        }

    classical_notes = {
        "coherence": "Semblance-based: high physical traceability to waveform similarity",
        "curvature": "Volumetric curvature: measures structural flexure directly",
        "spectral": "Frequency decomposition: tied to tuning thickness",
    }

    for key, note in classical_notes.items():
        if key in name.lower():
            return {
                "display_bias": "low",
                "risk_level": "minimal",
                "notes": f"Classical attribute — {note}",
                "mitigation": ["Standard QC: check for edge artifacts"],
            }

    return {
        "display_bias": "medium",
        "risk_level": "moderate",
        "notes": "Attribute type unknown — apply standard QC",
        "mitigation": ["Review processing chain", "Validate against wells"],
    }


def _generate_uncertainty_factors(name: str) -> list[str]:
    """Generate list of uncertainty sources for this attribute type."""
    factors = [
        "acquisition_footprint",
        "processing_noise",
        "velocity_model_uncertainty",
    ]

    if "coherence" in name.lower():
        factors.extend(["spatial_window_size", "dip_estimation_error"])
    elif "curvature" in name.lower():
        factors.extend(["derivative_estimation_noise", "structural_complexity"])
    elif "meta" in name.lower() or "fault_prob" in name.lower():
        factors.extend(
            [
                "training_data_bias",
                "generalization_gap",
                "fusion_artifact_amplification",
                "perceptual_conflation_risk",
            ]
        )

    return factors


def compute_contrast_verdict(
    attributes: dict[str, Any],
    well_ties: list[str] | None = None,
) -> dict[str, Any]:
    """
    Compute constitutional verdict for an attribute set.

    Returns SEAL, PARTIAL, or GEOX_BLOCK based on grounding status.
    """
    has_ungrounded_meta = False
    warnings: list[str] = []

    for name, attr in attributes.items():
        is_meta = attr.get("_is_meta_attribute", False)
        grounding = attr.get("_grounding_status", "UNKNOWN")

        if is_meta and grounding == "UNGROUNDED":
            has_ungrounded_meta = True
            warnings.append(
                f"Meta-attribute '{name}' lacks well tie validation. "
                "Perceptual contrast risk elevated."
            )

    if has_ungrounded_meta and not well_ties:
        return {
            "verdict": "GEOX_BLOCK",
            "explanation": (
                "Meta-attribute(s) without well tie validation. "
                "Perceptual contrast may dominate physical signal. "
                "Provide well_ties or remove meta attributes."
            ),
            "warnings": warnings,
            "floors_triggered": ["F7_humility", "F9_anti_hantu"],
        }
    elif warnings:
        return {
            "verdict": "PARTIAL",
            "explanation": "Some attributes have elevated uncertainty. Proceed with caution.",
            "warnings": warnings,
            "floors_triggered": ["F7_humility"],
        }
    else:
        return {
            "verdict": "SEAL",
            "explanation": "All attributes properly grounded.",
            "warnings": [],
            "floors_triggered": [],
        }


contrast_governed = contrast_governed_tool  # Alias for backward compatibility
