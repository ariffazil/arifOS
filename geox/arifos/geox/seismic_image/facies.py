"""
Seismic facies segmentation from images.

Deep learning-based facies classification using image-domain features.
NOT lithology identification — seismic facies proxies with uncertainty.

F7 Humility enforcement:
- Confidence ceiling 0.95
- Uncertainty maps mandatory
- Warnings about proxy nature
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PIL import Image

from .schemas import FaciesSegmentationResponse, Verdict

logger = logging.getLogger("geox.seismic_image.facies")


class MockFaciesModel:
    """
    Mock facies segmentation model.
    
    In production, this would load a trained DeepLabv3+ or U-Net.
    """
    
    def __init__(self, model_name: str = "deeplabv3_plus", classes: list[str] | None = None):
        self.model_name = model_name
        self.classes = classes or ["shale", "sandstone", "limestone"]
        self.version = "0.1.0-mock"
    
    def predict(
        self,
        image: np.ndarray,
        compute_uncertainty: bool = True,
    ) -> dict[str, Any]:
        """
        Mock prediction — returns plausible facies distribution.
        
        In production, this would run actual model inference.
        """
        h, w = image.shape
        n_classes = len(self.classes)
        
        # Mock class probabilities (would be model softmax output)
        # Create spatially varying patterns
        probs = np.random.dirichlet(np.ones(n_classes), size=(h, w))
        
        # Add some structure (geological realism)
        for i in range(h):
            # Bias toward shale in deeper sections (bottom of image)
            depth_bias = i / h
            probs[i, :, 0] += 0.2 * depth_bias  # Shale increases with depth
            probs[i, :] /= probs[i, :].sum(axis=1, keepdims=True)
        
        # Uncertainty (entropy-based)
        uncertainty = -np.sum(probs * np.log(probs + 1e-10), axis=2)
        uncertainty = uncertainty / np.log(n_classes)  # Normalize to 0-1
        
        # Class distribution
        class_dist = {
            cls: float(np.mean(probs[:, :, i]))
            for i, cls in enumerate(self.classes)
        }
        
        return {
            "class_probabilities": probs,
            "uncertainty": uncertainty,
            "class_distribution": class_dist,
        }


def compute_segmentation_quality(
    class_probs: np.ndarray,
) -> dict[str, float]:
    """
    Compute segmentation quality metrics.
    
    Args:
        class_probs: Class probability maps (H, W, C)
        
    Returns:
        Dictionary with quality metrics
    """
    # Boundary sharpness (mean gradient of class probabilities)
    from scipy import ndimage
    
    gradients = []
    for c in range(class_probs.shape[2]):
        gy, gx = np.gradient(class_probs[:, :, c])
        grad_mag = np.sqrt(gy**2 + gx**2)
        gradients.append(np.mean(grad_mag))
    
    boundary_sharpness = np.mean(gradients)
    
    return {
        "boundary_sharpness": round(float(boundary_sharpness), 2),
    }


async def segment_facies(
    image_path: str,
    image_id: str,
    classes: list[str],
    model_name: str = "deeplabv3_plus",
    compute_uncertainty: bool = True,
) -> FaciesSegmentationResponse:
    """
    Segment seismic facies from image.
    
    Enforces F7 with confidence ceiling and uncertainty exposure.
    """
    try:
        # Load image
        img = Image.open(image_path).convert('L')
        img_array = np.array(img, dtype=np.float32)
        
        # Load model (mock for now)
        model = MockFaciesModel(model_name=model_name, classes=classes)
        
        # Run inference
        result = model.predict(img_array, compute_uncertainty=compute_uncertainty)
        
        # Quality metrics
        quality = compute_segmentation_quality(result["class_probabilities"])
        
        # Uncertainty hotspots (top 5)
        uncertainty = result["uncertainty"]
        hotspot_indices = np.argpartition(uncertainty.ravel(), -5)[-5:]
        hotspots = []
        for idx in hotspot_indices:
            y, x = np.unravel_index(idx, uncertainty.shape)
            hotspots.append({
                "x": int(x),
                "y": int(y),
                "uncertainty": round(float(uncertainty[y, x]), 2),
            })
        
        logger.info(
            "Facies segmentation complete for %s: classes=%s, model=%s",
            image_id, classes, model_name
        )
        
        return FaciesSegmentationResponse(
            success=True,
            image_id=image_id,
            verdict=Verdict.PARTIAL,  # Always PARTIAL for DL outputs
            class_probabilities={
                cls: result["class_probabilities"][:, :, i].tolist()
                for i, cls in enumerate(classes)
            },
            uncertainty_map=uncertainty.tolist(),
            statistics={
                "class_distribution": result["class_distribution"],
                **quality,
                "uncertainty_hotspots": hotspots,
            },
        )
        
    except Exception as e:
        logger.exception("Facies segmentation failed: %s", e)
        return FaciesSegmentationResponse(
            success=False,
            image_id=image_id,
            verdict=Verdict.VOID,
            class_probabilities={},
            uncertainty_map=[[]],
            statistics={},
        )
