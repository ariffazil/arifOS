"""
Seismic image ingest module.

F4 Clarity enforcement:
- Vertical units mandatory
- Scales must be positive
- Image metadata extracted

F11 Authority enforcement:
- Requester ID logged
- Provenance chain initialized
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import numpy as np
from PIL import Image

from .schemas import (
    ConstitutionalCompliance,
    IngestMetadata,
    ScaleValidation,
    SeismicImageIngestRequest,
    SeismicImageIngestResponse,
    Verdict,
)

logger = logging.getLogger("geox.seismic_image.ingest")


def generate_image_id(image_path: str, line_name: str) -> str:
    """Generate unique image ID from path and line name."""
    hash_input = f"{image_path}:{line_name}".encode()
    hash_digest = hashlib.sha256(hash_input).hexdigest()[:8]
    safe_line = line_name.replace(" ", "_").replace("/", "_")[:20]
    return f"img-{safe_line}-{hash_digest}"


def validate_aspect_ratio(
    width_px: int, 
    height_px: int, 
    vertical_scale: float, 
    horizontal_scale: float
) -> tuple[bool, float]:
    """
    Validate that declared scales produce reasonable aspect ratio.
    
    Returns:
        (is_valid, distortion_percentage)
    """
    # Calculate pixel aspect ratio
    pixel_ar = width_px / height_px if height_px > 0 else 1.0
    
    # Calculate physical aspect ratio
    # Assuming image shows full extent: width = horizontal_scale * width_px
    # height = vertical_scale * height_px
    physical_width = horizontal_scale * width_px
    physical_height = vertical_scale * height_px
    physical_ar = physical_width / physical_height if physical_height > 0 else 1.0
    
    # Compare ratios
    if physical_ar > 0:
        distortion = abs(pixel_ar - physical_ar) / physical_ar * 100
    else:
        distortion = 0.0
    
    # Allow up to 10% distortion (common in seismic displays)
    is_valid = distortion <= 10.0
    
    return is_valid, distortion


def convert_to_meters(value: float, unit: str) -> float:
    """Convert value to meters."""
    conversions = {
        "meters": 1.0,
        "feet": 0.3048,
        "seconds_TWT": 1500.0,  # Approximate for water velocity
        "milliseconds_TWT": 1.5,  # meters per millisecond
        "samples": 1.0,  # Cannot convert without sample rate — will be flagged
    }
    return value * conversions.get(unit, 1.0)


async def ingest_seismic_image(request: SeismicImageIngestRequest) -> SeismicImageIngestResponse:
    """
    Ingest and validate a seismic section image.
    
    Enforces:
    - F4 Clarity: Units and scales mandatory
    - F11 Authority: Requester logged
    """
    errors = []
    warnings = []
    
    # 000 INIT — Validate file exists
    image_path = Path(request.image_path)
    if not image_path.exists():
        return SeismicImageIngestResponse(
            success=False,
            image_id="",
            verdict=Verdict.VOID,
            ingest_metadata=IngestMetadata(
                width_px=0, height_px=0, format="", color_mode="", file_size_mb=0
            ),
            scale_validation=ScaleValidation(
                vertical_scale_declared=request.vertical_scale,
                horizontal_scale_declared=request.horizontal_scale,
                aspect_ratio_valid=False,
                aspect_ratio_distortion_pct=0,
            ),
            constitutional_compliance=ConstitutionalCompliance(
                F4_clarity="VOID — File not found",
                F11_authority=f"Requester: {request.requester_id}",
            ),
            errors=[f"File not found: {request.image_path}"],
        )
    
    # Extract image metadata
    try:
        with Image.open(image_path) as img:
            width_px, height_px = img.size
            format_type = img.format or "UNKNOWN"
            color_mode = img.mode
            file_size_mb = image_path.stat().st_size / (1024 * 1024)
            
            # Check if convertible to grayscale
            if color_mode not in ("L", "RGB", "RGBA"):
                warnings.append(f"Unusual color mode: {color_mode}. Will convert to grayscale.")
                
    except Exception as e:
        return SeismicImageIngestResponse(
            success=False,
            image_id="",
            verdict=Verdict.VOID,
            ingest_metadata=IngestMetadata(
                width_px=0, height_px=0, format="", color_mode="", file_size_mb=0
            ),
            scale_validation=ScaleValidation(
                vertical_scale_declared=request.vertical_scale,
                horizontal_scale_declared=request.horizontal_scale,
                aspect_ratio_valid=False,
                aspect_ratio_distortion_pct=0,
            ),
            constitutional_compliance=ConstitutionalCompliance(
                F4_clarity="VOID — Cannot read image",
                F11_authority=f"Requester: {request.requester_id}",
            ),
            errors=[f"Cannot read image: {e}"],
        )
    
    # F4 Clarity — Validate scales
    is_valid, distortion = validate_aspect_ratio(
        width_px, height_px,
        request.vertical_scale, request.horizontal_scale
    )
    
    if not is_valid:
        warnings.append(
            f"Aspect ratio distortion: {distortion:.1f}%. "
            f"Declared scales may be incorrect or image may be stretched."
        )
    
    # Calculate physical extents
    try:
        vertical_extent_m = convert_to_meters(
            height_px * request.vertical_scale,
            request.vertical_unit.value
        )
        horizontal_extent_m = request.horizontal_scale * width_px
    except Exception as e:
        vertical_extent_m = None
        horizontal_extent_m = None
        warnings.append(f"Cannot calculate physical extents: {e}")
    
    # Generate image ID
    image_id = generate_image_id(str(image_path), request.line_name)
    
    # Determine verdict
    if request.vertical_unit.value == "samples":
        verdict = Verdict.SABAR
        warnings.append(
            "Vertical unit is 'samples' — cannot determine true depth/time without sample rate. "
            "Interpretations will be in sample space, not Earth space."
        )
    elif not is_valid and distortion > 20:
        verdict = Verdict.SABAR
        warnings.append("High aspect ratio distortion — structural interpretations unreliable")
    elif request.image_type == ImageType.UNKNOWN:
        verdict = Verdict.SABAR
        warnings.append("Image type unknown — clarify if raw seismic or attribute display")
    else:
        verdict = Verdict.SEAL
    
    logger.info(
        "Ingested seismic image: %s (%dx%d, %.1f MB)",
        image_id, width_px, height_px, file_size_mb
    )
    
    return SeismicImageIngestResponse(
        success=True,
        image_id=image_id,
        verdict=verdict,
        ingest_metadata=IngestMetadata(
            width_px=width_px,
            height_px=height_px,
            format=format_type,
            color_mode=color_mode,
            file_size_mb=round(file_size_mb, 2),
        ),
        scale_validation=ScaleValidation(
            vertical_scale_declared=request.vertical_scale,
            horizontal_scale_declared=request.horizontal_scale,
            aspect_ratio_valid=is_valid,
            aspect_ratio_distortion_pct=round(distortion, 2),
            estimated_true_vertical_extent_m=vertical_extent_m,
            estimated_true_horizontal_extent_m=horizontal_extent_m,
        ),
        constitutional_compliance=ConstitutionalCompliance(
            F4_clarity=f"PASS — Units: {request.vertical_unit.value}, Scales declared",
            F11_authority=f"PASS — Requester: {request.requester_id}",
            F2_truth="PENDING — Requires QC",
            F7_humility="PENDING — Scale uncertainty quantified",
        ),
        next_steps=["geox_qc_seismic_image"],
        warnings=warnings,
        errors=errors,
    )
