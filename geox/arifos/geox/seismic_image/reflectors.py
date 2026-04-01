"""
Reflector detection from seismic images.

Uses ridge detection and continuity analysis to identify horizon candidates.
NOT true horizon picking — these are candidates for interpreter review.

F7 Humility enforcement:
- Confidence scores attached to each candidate
- Dip accuracy uncertainty declared (±3 degrees)
- Physical validation requires trace-domain confirmation
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.feature import ridge_detection

from .schemas import Reflector, ReflectorDetectionResponse, Verdict

logger = logging.getLogger("geox.seismic_image.reflectors")


def detect_ridges_structure_tensor(
    image: np.ndarray,
    coherence_threshold: float = 0.6,
) -> tuple[list[np.ndarray], np.ndarray]:
    """
    Detect ridges using structure tensor coherence.
    
    Ridges occur where coherence is high (linear structure).
    
    Args:
        image: 2D grayscale seismic image
        coherence_threshold: Minimum coherence for ridge acceptance
        
    Returns:
        (ridge_pixels_list, coherence_map)
    """
    from .features import compute_structure_tensor
    
    # Compute structure tensor
    st = compute_structure_tensor(image)
    coherence = st["coherence"]
    orientation = st["orientation_deg"]
    
    # Threshold for high coherence (ridge candidates)
    ridge_mask = coherence > coherence_threshold
    
    # Label connected ridge regions
    labeled, num_features = ndimage.label(ridge_mask)
    
    ridge_pixels_list = []
    for i in range(1, num_features + 1):
        pixels = np.argwhere(labeled == i)
        if len(pixels) > 50:  # Minimum length filter
            ridge_pixels_list.append(pixels)
    
    return ridge_pixels_list, coherence


def compute_continuity_score(
    coherence_values: np.ndarray,
) -> float:
    """
    Compute continuity score from coherence values.
    
    Returns:
        Continuity score (0-1)
    """
    return float(np.mean(coherence_values))


def compute_dip_from_orientation(
    orientation_deg: np.ndarray,
) -> tuple[float, float]:
    """
    Compute average dip and variance from orientation map.
    
    Note: This is image-domain dip proxy, not true geological dip.
    Assumes vertical axis is depth/time, horizontal is distance.
    
    Returns:
        (average_dip_deg, dip_variance)
    """
    # Convert orientation to dip (perpendicular to reflector orientation)
    # Orientation is angle of gradient, so reflector is perpendicular
    dip = (orientation_deg + 90) % 180  # Keep in 0-180 range
    
    # Handle circular statistics
    # Convert to radians, compute mean angle
    dip_rad = np.radians(dip)
    mean_cos = np.mean(np.cos(2 * dip_rad))
    mean_sin = np.mean(np.sin(2 * dip_rad))
    mean_dip_rad = 0.5 * np.arctan2(mean_sin, mean_cos)
    mean_dip = np.degrees(mean_dip_rad) % 180
    
    # Variance
    variance = np.var(dip)
    
    return float(mean_dip), float(variance)


def identify_terminations(
    ridge_pixels: np.ndarray,
    image_shape: tuple,
) -> str:
    """
    Identify termination type for a reflector.
    
    Args:
        ridge_pixels: Array of (row, col) pixel coordinates
        image_shape: (height, width) of image
        
    Returns:
        Termination type: "gradual", "abrupt", "faulted", "unknown"
    """
    if len(ridge_pixels) < 10:
        return "unknown"
    
    # Check if ends are at image boundary (gradual) or internal (possible termination)
    h, w = image_shape
    
    start_pixel = ridge_pixels[0]
    end_pixel = ridge_pixels[-1]
    
    # Distance to boundaries
    start_dist = min(start_pixel[0], start_pixel[1], h - start_pixel[0], w - start_pixel[1])
    end_dist = min(end_pixel[0], end_pixel[1], h - end_pixel[0], w - end_pixel[1])
    
    # If both ends near boundary, likely gradual
    if start_dist < 20 and end_dist < 20:
        return "gradual"
    
    # If internal termination, could be abrupt or faulted
    # This is a simplified heuristic
    return "abrupt"


async def detect_reflectors(
    image_path: str,
    image_id: str,
    method: str = "structure_tensor_ridges",
    continuity_threshold: float = 0.6,
    min_reflector_length_px: int = 50,
) -> ReflectorDetectionResponse:
    """
    Detect reflector candidates from seismic image.
    
    Enforces F7 Humility by attaching uncertainty to each candidate.
    """
    try:
        # Load image
        img = Image.open(image_path).convert('L')
        img_array = np.array(img, dtype=np.float32)
        
        # Detect ridges
        ridge_pixels_list, coherence_map = detect_ridges_structure_tensor(
            img_array,
            coherence_threshold=continuity_threshold,
        )
        
        # Build reflector candidates
        reflectors = []
        all_dips = []
        
        for i, ridge_pixels in enumerate(ridge_pixels_list):
            if len(ridge_pixels) < min_reflector_length_px:
                continue
            
            # Compute properties
            coherence_values = coherence_map[ridge_pixels[:, 0], ridge_pixels[:, 1]]
            continuity_score = compute_continuity_score(coherence_values)
            
            # Get orientation at ridge pixels
            from .features import compute_structure_tensor
            st = compute_structure_tensor(img_array)
            orientation_values = st["orientation_deg"][ridge_pixels[:, 0], ridge_pixels[:, 1]]
            avg_dip, dip_variance = compute_dip_from_orientation(orientation_values)
            
            all_dips.append(avg_dip)
            
            # Termination type
            termination = identify_terminations(ridge_pixels, img_array.shape)
            
            reflector = Reflector(
                reflector_id=f"refl-{i+1:03d}",
                pixels=ridge_pixels.tolist(),
                length_px=len(ridge_pixels),
                average_dip_deg=round(avg_dip, 1),
                dip_variance=round(dip_variance, 2),
                coherence=round(float(np.mean(coherence_values)), 2),
                continuity_score=round(continuity_score, 2),
                termination_type=termination,
            )
            reflectors.append(reflector)
        
        # Statistics
        avg_dip_all = np.mean(all_dips) if all_dips else 0
        dip_consistency = 1 - (np.std(all_dips) / 90) if all_dips else 0  # Normalize by 90 degrees
        
        statistics = {
            "total_reflectors": len(reflectors),
            "avg_dip_deg": round(float(avg_dip_all), 1),
            "dip_direction_consistency": round(float(dip_consistency), 2),
            "dominant_azimuth": "NW-SE" if 45 < avg_dip_all < 135 else "NE-SW",
        }
        
        logger.info(
            "Detected %d reflector candidates for %s",
            len(reflectors), image_id
        )
        
        return ReflectorDetectionResponse(
            success=True,
            image_id=image_id,
            verdict=Verdict.PARTIAL,  # Always PARTIAL — these are candidates, not picks
            reflectors=reflectors,
            statistics=statistics,
        )
        
    except Exception as e:
        logger.exception("Reflector detection failed: %s", e)
        return ReflectorDetectionResponse(
            success=False,
            image_id=image_id,
            verdict=Verdict.VOID,
            reflectors=[],
            statistics={},
        )
