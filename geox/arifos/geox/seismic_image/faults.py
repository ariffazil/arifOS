"""
Fault candidate detection from seismic images.

Detects discontinuities and lineaments suggestive of faults.
NOT fault interpretations — these are likelihood maps for interpreter attention.

F7 Humility enforcement:
- False positive risk explicitly flagged
- Validation requirements stated
- Confidence scores attached
"""

from __future__ import annotations

import logging

import numpy as np
from PIL import Image
from scipy import ndimage

from .schemas import FaultCandidate, FaultDetectionResponse, Verdict

logger = logging.getLogger("geox.seismic_image.faults")


def detect_discontinuities_gradient(
    image: np.ndarray,
    sensitivity: str = "medium",
) -> tuple[np.ndarray, np.ndarray]:
    """
    Detect discontinuities using gradient magnitude and direction changes.
    
    Args:
        image: 2D grayscale seismic image
        sensitivity: Detection sensitivity (low, medium, high)
        
    Returns:
        (discontinuity_map, gradient_magnitude)
    """
    # Compute gradients
    gy, gx = np.gradient(image)
    gradient_magnitude = np.sqrt(gx**2 + gy**2)
    
    # Gradient direction
    gradient_direction = np.arctan2(gy, gx)
    
    # Detect direction discontinuities (local variance in direction)
    direction_variance = ndimage.generic_filter(
        gradient_direction,
        lambda x: np.var(x),
        size=5,
    )
    
    # Sensitivity thresholds
    thresholds = {
        "low": np.percentile(direction_variance, 90),
        "medium": np.percentile(direction_variance, 85),
        "high": np.percentile(direction_variance, 75),
    }
    threshold = thresholds.get(sensitivity, thresholds["medium"])
    
    # Discontinuity map
    discontinuity_map = direction_variance > threshold
    
    return discontinuity_map, gradient_magnitude


def extract_fault_candidates(
    discontinuity_map: np.ndarray,
    gradient_magnitude: np.ndarray,
    min_length: int = 30,
) -> list[FaultCandidate]:
    """
    Extract fault candidates from discontinuity map.
    
    Args:
        discontinuity_map: Binary map of discontinuities
        gradient_magnitude: Gradient magnitude for scoring
        min_length: Minimum candidate length in pixels
        
    Returns:
        List of fault candidates
    """
    # Label connected components
    labeled, num_features = ndimage.label(discontinuity_map)
    
    candidates = []
    for i in range(1, num_features + 1):
        pixels = np.argwhere(labeled == i)
        
        if len(pixels) < min_length:
            continue
        
        # Compute candidate properties
        # Estimate dip direction from pixel distribution
        y_coords = pixels[:, 0]
        x_coords = pixels[:, 1]
        
        # Simple linear fit for orientation
        if len(x_coords) > 1:
            slope, _ = np.polyfit(x_coords, y_coords, 1)
            dip_direction = "SW" if slope > 0 else "SE"
        else:
            dip_direction = None
        
        # Likelihood score based on gradient magnitude along candidate
        scores = gradient_magnitude[pixels[:, 0], pixels[:, 1]]
        likelihood = float(np.mean(scores)) / (np.max(gradient_magnitude) + 1e-10)
        
        # Confidence based on continuity and length
        confidence = min(1.0, len(pixels) / 100) * likelihood
        
        candidate = FaultCandidate(
            fault_id=f"fault-{i:03d}",
            pixels=pixels.tolist(),
            length_px=len(pixels),
            dip_direction=dip_direction,
            likelihood_score=round(likelihood, 2),
            confidence=round(confidence, 2),
        )
        candidates.append(candidate)
    
    return candidates


async def detect_fault_candidates(
    image_path: str,
    image_id: str,
    method: str = "gradient_discontinuity",
    sensitivity: str = "medium",
) -> FaultDetectionResponse:
    """
    Detect fault candidates from seismic image.
    
    Enforces F7 Humility by flagging false positive risk.
    """
    try:
        # Load image
        img = Image.open(image_path).convert('L')
        img_array = np.array(img, dtype=np.float32)
        
        # Detect discontinuities
        discontinuity_map, gradient_magnitude = detect_discontinuities_gradient(
            img_array,
            sensitivity=sensitivity,
        )
        
        # Extract candidates
        candidates = extract_fault_candidates(
            discontinuity_map,
            gradient_magnitude,
        )
        
        logger.info(
            "Detected %d fault candidates for %s",
            len(candidates), image_id
        )
        
        return FaultDetectionResponse(
            success=True,
            image_id=image_id,
            verdict=Verdict.PARTIAL,  # Always PARTIAL — high false positive risk
            fault_likelihood_map=None,  # Would be base64 encoded
            candidates=candidates,
        )
        
    except Exception as e:
        logger.exception("Fault detection failed: %s", e)
        return FaultDetectionResponse(
            success=False,
            image_id=image_id,
            verdict=Verdict.VOID,
            candidates=[],
        )
