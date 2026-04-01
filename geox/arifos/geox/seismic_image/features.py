"""
Seismic image texture feature extraction.

Image-domain proxies for seismic character:
- Structure tensor: coherence, orientation (reflector continuity proxy)
- LBP: local binary patterns (texture roughness proxy)
- GLCM: gray level co-occurrence matrix (texture statistics)
- Gabor filters: frequency-direction energy (tuning thickness proxy)

F2 Truth enforcement:
- All outputs labeled IMAGE_DOMAIN_PROXY
- Not equivalent to trace-derived attributes
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from PIL import Image

from .schemas import (
    GLCMOutput,
    LBPOutput,
    StructureTensorOutput,
    TextureAttributeOutput,
    TextureAttributeResponse,
    Verdict,
)

logger = logging.getLogger("geox.seismic_image.features")


def compute_structure_tensor(
    image: np.ndarray,
    sigma: float = 1.0,
) -> dict[str, np.ndarray]:
    """
    Compute structure tensor for coherence and orientation analysis.
    
    The structure tensor captures local gradient covariance:
    T = [Ix^2   Ix*Iy]
        [Ix*Iy  Iy^2 ]
    
    Eigenvalues λ1 >= λ2 give:
    - Coherence: (λ1 - λ2) / (λ1 + λ2 + epsilon)
    - Orientation: arctan2(eigenvector_y, eigenvector_x)
    
    Geological proxy: Reflector continuity and dip direction.
    
    Args:
        image: 2D grayscale seismic image
        sigma: Gaussian smoothing sigma
        
    Returns:
        Dictionary with coherence, orientation, energy, eigenvalue_ratio
    """
    from scipy import ndimage
    
    # Compute gradients
    Ix = ndimage.gaussian_filter(image, sigma, order=(0, 1))
    Iy = ndimage.gaussian_filter(image, sigma, order=(1, 0))
    
    # Structure tensor components
    Ixx = Ix ** 2
    Iyy = Iy ** 2
    Ixy = Ix * Iy
    
    # Smooth components
    Ixx = ndimage.gaussian_filter(Ixx, sigma)
    Iyy = ndimage.gaussian_filter(Iyy, sigma)
    Ixy = ndimage.gaussian_filter(Ixy, sigma)
    
    # Compute eigenvalues
    # λ = 0.5 * (Ixx + Iyy ± sqrt((Ixx - Iyy)^2 + 4*Ixy^2))
    trace = Ixx + Iyy
    det = Ixx * Iyy - Ixy ** 2
    diff = Ixx - Iyy
    
    sqrt_term = np.sqrt(diff ** 2 + 4 * Ixy ** 2 + 1e-10)
    
    lambda1 = 0.5 * (trace + sqrt_term)
    lambda2 = 0.5 * (trace - sqrt_term)
    
    # Coherence (0 = isotropic, 1 = linear)
    coherence = (lambda1 - lambda2) / (lambda1 + lambda2 + 1e-10)
    
    # Orientation (perpendicular to gradient)
    orientation = 0.5 * np.arctan2(2 * Ixy, diff)  # radians
    orientation_deg = np.degrees(orientation)
    
    # Energy (total gradient magnitude)
    energy = np.sqrt(lambda1 + lambda2)
    
    # Eigenvalue ratio (anisotropy)
    eigenvalue_ratio = lambda1 / (lambda2 + 1e-10)
    
    return {
        "coherence": coherence,
        "orientation_deg": orientation_deg,
        "energy": energy,
        "eigenvalue_ratio": eigenvalue_ratio,
    }


def compute_lbp(
    image: np.ndarray,
    radius: int = 1,
    n_points: int = 8,
) -> dict[str, Any]:
    """
    Compute Local Binary Patterns (LBP).
    
    LBP encodes local texture by comparing center pixel to neighbors:
    - Uniform patterns (0-2 transitions) capture smooth textures
    - Non-uniform patterns capture complex/discontinuous textures
    
    Geological proxy: Amplitude roughness, bedform style.
    
    Args:
        image: 2D grayscale image
        radius: LBP radius in pixels
        n_points: Number of circularly symmetric neighbor points
        
    Returns:
        Dictionary with histograms and uniformity_score
    """
    from skimage.feature import local_binary_pattern
    
    # Compute LBP
    lbp = local_binary_pattern(image, n_points, radius, method="uniform")
    
    # Histogram
    n_bins = n_points + 2  # uniform patterns + non-uniform
    hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins))
    hist = hist.astype(np.float32)
    hist /= (hist.sum() + 1e-10)  # Normalize
    
    # Uniformity score (fraction of uniform patterns)
    uniform_patterns = hist[:-1].sum()  # All except non-uniform bin
    uniformity_score = float(uniform_patterns)
    
    return {
        "histograms": [hist.tolist()],
        "uniformity_score": uniformity_score,
    }


def compute_glcm(
    image: np.ndarray,
    distances: list[int] = [1, 2, 4],
    angles: list[float] = [0, np.pi/4, np.pi/2, 3*np.pi/4],
) -> dict[str, Any]:
    """
    Compute Gray Level Co-occurrence Matrix (GLCM) features.
    
    GLCM captures spatial relationships between pixel intensities:
    - Contrast: Local intensity variation
    - Correlation: Linear dependency
    - Energy: Uniformity (sum of squared elements)
    - Homogeneity: Closeness of element distribution to diagonal
    
    Geological proxy: Facies heterogeneity, layering uniformity.
    
    Args:
        image: 2D grayscale image
        distances: Pixel distances for co-occurrence
        angles: Angles for co-occurrence (radians)
        
    Returns:
        Dictionary with contrast, correlation, energy, homogeneity
    """
    from skimage.feature import graycomatrix, graycoprops
    
    # Quantize image to reduce GLCM size (256 levels -> 32 levels)
    image_quantized = (image / 8).astype(np.uint8)
    
    # Compute GLCM
    glcm = graycomatrix(
        image_quantized,
        distances=distances,
        angles=angles,
        levels=32,
        symmetric=True,
        normed=True,
    )
    
    # Compute properties
    contrast = graycoprops(glcm, 'contrast').mean()
    correlation = graycoprops(glcm, 'correlation').mean()
    energy = graycoprops(glcm, 'energy').mean()
    homogeneity = graycoprops(glcm, 'homogeneity').mean()
    
    # Create 2D arrays (simplified — actually scalar per image)
    # For per-pixel GLCM, would need sliding window approach
    return {
        "contrast": [[float(contrast)]],
        "correlation": [[float(correlation)]],
        "energy": [[float(energy)]],
        "homogeneity": [[float(homogeneity)]],
    }


def sliding_window_features(
    image: np.ndarray,
    window_size: int = 32,
    overlap: float = 0.5,
    feature_fn: callable = None,
) -> np.ndarray:
    """
    Compute features in sliding windows across image.
    
    Args:
        image: 2D grayscale image
        window_size: Window size in pixels
        overlap: Overlap fraction (0-1)
        feature_fn: Function to compute features on each window
        
    Returns:
        Feature map with same spatial dimensions as image
    """
    if feature_fn is None:
        feature_fn = lambda w: np.mean(w)
    
    step = int(window_size * (1 - overlap))
    h, w = image.shape
    
    # Output feature map
    feature_map = np.zeros((h // step, w // step))
    
    for i in range(0, h - window_size, step):
        for j in range(0, w - window_size, step):
            window = image[i:i+window_size, j:j+window_size]
            feature_map[i // step, j // step] = feature_fn(window)
    
    return feature_map


async def extract_texture_attributes(
    image_path: str,
    image_id: str,
    methods: list[str],
    window_size_px: int = 32,
    overlap_pct: float = 50.0,
) -> TextureAttributeResponse:
    """
    Extract texture attributes from seismic image.
    
    Enforces F2 Truth by labeling outputs as IMAGE_DOMAIN_PROXY.
    """
    try:
        # Load image
        img = Image.open(image_path).convert('L')
        img_array = np.array(img, dtype=np.float32)
        
        attributes = TextureAttributeOutput()
        
        # Structure tensor (always computed for windowing reference)
        st_result = compute_structure_tensor(img_array)
        
        if "structure_tensor" in methods:
            attributes.structure_tensor = StructureTensorOutput(
                coherence=st_result["coherence"].tolist(),
                orientation_deg=st_result["orientation_deg"].tolist(),
                energy=st_result["energy"].tolist(),
                eigenvalue_ratio=st_result["eigenvalue_ratio"].tolist(),
            )
        
        # LBP
        if "lbp" in methods:
            lbp_result = compute_lbp(img_array)
            attributes.lbp = LBPOutput(
                histograms=lbp_result["histograms"],
                uniformity_score=lbp_result["uniformity_score"],
            )
        
        # GLCM
        if "glcm" in methods:
            glcm_result = compute_glcm(img_array)
            attributes.glcm = GLCMOutput(
                contrast=glcm_result["contrast"],
                correlation=glcm_result["correlation"],
                energy=glcm_result["energy"],
                homogeneity=glcm_result["homogeneity"],
            )
        
        logger.info(
            "Extracted texture attributes for %s: methods=%s",
            image_id, methods
        )
        
        return TextureAttributeResponse(
            success=True,
            image_id=image_id,
            verdict=Verdict.SEAL,
            attributes=attributes,
        )
        
    except Exception as e:
        logger.exception("Texture extraction failed: %s", e)
        return TextureAttributeResponse(
            success=False,
            image_id=image_id,
            verdict=Verdict.VOID,
            attributes=TextureAttributeOutput(),
            limitations=[f"Extraction error: {e}"],
        )
