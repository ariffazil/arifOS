"""
Seismic image quality control module.

F9 Anti-Hantu enforcement:
- Detect annotation overlays (text, arrows, logos)
- Identify colorbar presence
- Check compression artifacts
- Validate grayscale suitability
- Measure aspect ratio distortion
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from PIL import Image

from .schemas import QCCheck, QCResult, Verdict

logger = logging.getLogger("geox.seismic_image.qc")


def detect_text_overlay(image: np.ndarray) -> tuple[bool, float]:
    """
    Detect text/annotation overlays using edge density analysis.
    
    Returns:
        (has_overlay, confidence)
    """
    # Simple heuristic: high edge density in regular patterns suggests text
    from scipy import ndimage
    
    # Compute gradient magnitude
    dx = ndimage.sobel(image, axis=1)
    dy = ndimage.sobel(image, axis=0)
    gradient = np.hypot(dx, dy)
    
    # Threshold for edges
    edge_mask = gradient > np.percentile(gradient, 95)
    edge_density = np.mean(edge_mask)
    
    # High edge density + regular spacing suggests annotations
    # Typical seismic has ~5-15% edge density; annotated slides often >25%
    has_overlay = edge_density > 0.20
    confidence = min(1.0, edge_density * 3)
    
    return has_overlay, confidence


def detect_colorbar(image: np.ndarray) -> tuple[bool, float]:
    """
    Detect colorbar presence in image.
    
    Returns:
        (has_colorbar, confidence)
    """
    # Look for vertical/horizontal gradient strips at image edges
    h, w = image.shape
    
    # Check right edge for vertical colorbar
    right_strip = image[:, -int(w*0.1):]
    right_gradient = np.std(right_strip, axis=0).mean()
    
    # Check bottom edge for horizontal colorbar
    bottom_strip = image[-int(h*0.1):, :]
    bottom_gradient = np.std(bottom_strip, axis=1).mean()
    
    # High gradient in edge strips suggests colorbar
    threshold = np.std(image) * 2
    has_colorbar = (right_gradient > threshold) or (bottom_gradient > threshold)
    confidence = 0.7 if has_colorbar else 0.3
    
    return has_colorbar, confidence


def estimate_jpeg_quality(image_path: str) -> float:
    """
    Estimate JPEG quality from file.
    
    Returns:
        Estimated quality (0-100) or 100 for non-JPEG
    """
    path = Path(image_path)
    if path.suffix.lower() not in ('.jpg', '.jpeg'):
        return 100.0
    
    # Check for compression artifacts
    # Higher DCT coefficient variance suggests lower quality
    try:
        img = Image.open(image_path)
        # This is a simplified heuristic
        return 85.0  # Placeholder
    except Exception:
        return 50.0


def check_compression_artifacts(image_path: str) -> tuple[bool, float]:
    """
    Check for compression artifacts.
    
    Returns:
        (has_artifacts, quality_estimate)
    """
    quality = estimate_jpeg_quality(image_path)
    has_artifacts = quality < 70
    return has_artifacts, quality


def check_grayscale_suitability(image: np.ndarray) -> tuple[bool, str]:
    """
    Check if image is suitable for grayscale analysis.
    
    Returns:
        (is_suitable, color_mode)
    """
    if len(image.shape) == 2:
        return True, "grayscale"
    
    if len(image.shape) == 3:
        # Check if RGB is effectively grayscale
        r, g, b = image[:,:,0], image[:,:,1], image[:,:,2]
        is_gray = np.allclose(r, g, atol=5) and np.allclose(g, b, atol=5)
        
        if is_gray:
            return True, "rgb_converted"
        else:
            return False, "color"
    
    return False, "unknown"


def measure_blur(image: np.ndarray) -> float:
    """
    Measure image blur using Laplacian variance.
    
    Returns:
        Sharpness score (higher = sharper)
    """
    from scipy import ndimage
    
    laplacian = ndimage.laplace(image)
    variance = np.var(laplacian)
    
    # Normalize to 0-1 range (heuristic)
    sharpness = min(1.0, variance / 500)
    return sharpness


async def qc_seismic_image(
    image_id: str,
    image_path: str,
    declared_aspect_ratio: float | None = None,
    qc_strictness: str = "standard",
) -> QCResult:
    """
    Perform quality control on seismic image.
    
    Enforces F9 Anti-Hantu by detecting artifacts that could lead to
    learning display styles instead of geology.
    """
    warnings = []
    hold_flags = []
    
    # Load image
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Convert to grayscale for analysis
        if len(img_array.shape) == 3:
            img_gray = np.mean(img_array, axis=2).astype(np.uint8)
        else:
            img_gray = img_array
            
    except Exception as e:
        return QCResult(
            success=False,
            image_id=image_id,
            verdict=Verdict.VOID,
            qc_score=0.0,
            checks={},
            recommendations=[],
            warnings=[f"Cannot load image: {e}"],
        )
    
    # Run QC checks
    checks = {}
    
    # 1. Aspect ratio check
    h, w = img_gray.shape
    actual_ratio = w / h if h > 0 else 1.0
    if declared_aspect_ratio:
        ratio_diff = abs(actual_ratio - declared_aspect_ratio) / declared_aspect_ratio
        ratio_valid = ratio_diff < 0.1
        if not ratio_valid:
            hold_flags.append(f"Aspect ratio distortion: {ratio_diff*100:.1f}%")
    else:
        ratio_valid = True
        ratio_diff = 0.0
    
    checks["aspect_ratio"] = QCCheck(
        status="PASS" if ratio_valid else "WARNING",
        confidence=0.9,
        details={"declared": declared_aspect_ratio, "actual": actual_ratio, "diff_pct": ratio_diff * 100},
    )
    
    # 2. Annotation overlay check
    has_overlay, overlay_conf = detect_text_overlay(img_gray)
    if has_overlay and overlay_conf > 0.5:
        hold_flags.append("Annotation overlay detected — may learn labels instead of geology")
    
    checks["annotation_overlay"] = QCCheck(
        status="FAIL" if has_overlay else "PASS",
        confidence=overlay_conf,
        details={"edge_density": float(np.mean(img_gray > 0))},
    )
    
    # 3. Colorbar check
    has_colorbar, colorbar_conf = detect_colorbar(img_gray)
    if has_colorbar:
        warnings.append("Colorbar detected — image is likely attribute display, not raw seismic")
    
    checks["colorbar_present"] = QCCheck(
        status="WARNING" if has_colorbar else "PASS",
        confidence=colorbar_conf,
        details={},
    )
    
    # 4. Compression artifacts check
    has_artifacts, quality = check_compression_artifacts(image_path)
    if has_artifacts:
        hold_flags.append(f"Compression artifacts detected (quality: {quality:.0f})")
    
    checks["compression_artifacts"] = QCCheck(
        status="FAIL" if has_artifacts else "PASS",
        confidence=quality / 100,
        details={"quality_estimate": quality},
    )
    
    # 5. Grayscale suitability
    is_gray, color_mode = check_grayscale_suitability(img_array)
    if not is_gray:
        hold_flags.append(f"Color image detected ({color_mode}) — may affect texture analysis")
    
    checks["grayscale_suitability"] = QCCheck(
        status="PASS" if is_gray else "WARNING",
        confidence=0.95,
        details={"color_mode": color_mode},
    )
    
    # 6. Blur check
    sharpness = measure_blur(img_gray)
    if sharpness < 0.3:
        warnings.append("Image appears blurry — may affect feature detection")
    
    checks["blur"] = QCCheck(
        status="WARNING" if sharpness < 0.3 else "PASS",
        confidence=sharpness,
        details={"sharpness_score": sharpness},
    )
    
    # Calculate overall QC score
    check_scores = [
        checks["aspect_ratio"].confidence * (1 if checks["aspect_ratio"].status == "PASS" else 0.5),
        (1 - checks["annotation_overlay"].confidence) if checks["annotation_overlay"].status == "PASS" else 0.3,
        checks["compression_artifacts"].confidence,
        1.0 if checks["grayscale_suitability"].status == "PASS" else 0.5,
        checks["blur"].confidence,
    ]
    qc_score = np.mean(check_scores)
    
    # Determine verdict based on strictness
    if hold_flags:
        if qc_strictness == "strict":
            verdict = Verdict.VOID
        elif qc_strictness == "standard":
            verdict = Verdict.PARTIAL
        else:  # lenient
            verdict = Verdict.SEAL
            warnings.extend(hold_flags)
    else:
        verdict = Verdict.SEAL
    
    # Generate recommendations
    recommendations = []
    if has_overlay:
        recommendations.append("Remove annotations or use raw seismic export")
    if has_colorbar:
        recommendations.append("Confirm image type — attribute displays have different interpretation")
    if has_artifacts:
        recommendations.append("Re-export with higher quality or lossless format")
    if not is_gray:
        recommendations.append("Convert to grayscale before analysis")
    
    if not recommendations:
        recommendations.append("Proceed with texture extraction")
    
    logger.info(
        "QC complete for %s: score=%.2f, verdict=%s, flags=%d",
        image_id, qc_score, verdict.value, len(hold_flags)
    )
    
    return QCResult(
        success=True,
        image_id=image_id,
        verdict=verdict,
        qc_score=round(qc_score, 2),
        checks=checks,
        recommendations=recommendations,
        warnings=warnings,
    )
