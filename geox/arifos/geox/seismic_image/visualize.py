"""
Visualization utilities for seismic image interpretation.

Generates overlay images for human verification:
- Reflector candidates overlay
- Fault likelihood heatmap
- Facies segmentation overlay
- Uncertainty maps
"""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("geox.seismic_image.visualize")


def array_to_heatmap(
    array: np.ndarray,
    colormap: str = "viridis",
) -> np.ndarray:
    """
    Convert scalar array to RGB heatmap.
    
    Args:
        array: 2D scalar array (0-1)
        colormap: Colormap name
        
    Returns:
        RGB array (H, W, 3)
    """
    import matplotlib.cm as cm
    
    # Normalize to 0-1
    array_norm = np.clip(array, 0, 1)
    
    # Apply colormap
    cmap = cm.get_cmap(colormap)
    rgb = cmap(array_norm)
    
    # Convert to uint8
    rgb_uint8 = (rgb[:, :, :3] * 255).astype(np.uint8)
    
    return rgb_uint8


def overlay_reflectors(
    image: np.ndarray,
    reflectors: list[dict[str, Any]],
    color: tuple[int, int, int] = (255, 0, 0),
    alpha: float = 0.7,
) -> np.ndarray:
    """
    Overlay reflector candidates on seismic image.
    
    Args:
        image: Grayscale seismic image
        reflectors: List of reflector dictionaries with 'pixels'
        color: Overlay color (R, G, B)
        alpha: Overlay opacity
        
    Returns:
        RGB image with overlays
    """
    # Convert grayscale to RGB
    if len(image.shape) == 2:
        img_rgb = np.stack([image] * 3, axis=-1).astype(np.uint8)
    else:
        img_rgb = image.copy()
    
    # Create overlay
    overlay = img_rgb.copy()
    
    for refl in reflectors:
        pixels = refl.get("pixels", [])
        if len(pixels) > 1:
            # Draw line connecting pixels
            for i in range(len(pixels) - 1):
                y1, x1 = pixels[i]
                y2, x2 = pixels[i + 1]
                # Simple line drawing (could use cv2 for anti-aliasing)
                overlay[y1, x1] = color
                overlay[y2, x2] = color
    
    # Blend
    result = (alpha * overlay + (1 - alpha) * img_rgb).astype(np.uint8)
    
    return result


def overlay_fault_likelihood(
    image: np.ndarray,
    fault_map: np.ndarray,
    threshold: float = 0.5,
) -> np.ndarray:
    """
    Overlay fault likelihood heatmap on seismic image.
    
    Args:
        image: Grayscale seismic image
        fault_map: Fault likelihood (0-1)
        threshold: Minimum likelihood to show
        
    Returns:
        RGB image with heatmap overlay
    """
    # Convert image to RGB
    if len(image.shape) == 2:
        img_rgb = np.stack([image] * 3, axis=-1).astype(np.uint8)
    else:
        img_rgb = image.copy()
    
    # Create heatmap
    heatmap = array_to_heatmap(fault_map, colormap="hot")
    
    # Apply threshold
    mask = fault_map > threshold
    
    # Blend
    result = img_rgb.copy()
    result[mask] = (0.5 * heatmap[mask] + 0.5 * img_rgb[mask]).astype(np.uint8)
    
    return result


def overlay_facies(
    image: np.ndarray,
    segmentation: np.ndarray,
    class_colors: dict[int, tuple[int, int, int]] | None = None,
    alpha: float = 0.4,
) -> np.ndarray:
    """
    Overlay facies segmentation on seismic image.
    
    Args:
        image: Grayscale seismic image
        segmentation: Class index map (H, W)
        class_colors: Mapping from class index to RGB color
        alpha: Overlay opacity
        
    Returns:
        RGB image with segmentation overlay
    """
    # Default colors
    if class_colors is None:
        class_colors = {
            0: (128, 128, 128),  # Shale - gray
            1: (255, 255, 0),    # Sandstone - yellow
            2: (0, 255, 255),    # Limestone - cyan
            3: (255, 0, 255),    # Salt - magenta
        }
    
    # Convert image to RGB
    if len(image.shape) == 2:
        img_rgb = np.stack([image] * 3, axis=-1).astype(np.uint8)
    else:
        img_rgb = image.copy()
    
    # Create colored segmentation
    seg_rgb = np.zeros_like(img_rgb)
    for class_idx, color in class_colors.items():
        mask = segmentation == class_idx
        seg_rgb[mask] = color
    
    # Blend
    result = (alpha * seg_rgb + (1 - alpha) * img_rgb).astype(np.uint8)
    
    return result


def create_uncertainty_overlay(
    image: np.ndarray,
    uncertainty: np.ndarray,
) -> np.ndarray:
    """
    Create uncertainty heatmap overlay.
    
    Args:
        image: Grayscale seismic image
        uncertainty: Uncertainty map (0-1, higher = more uncertain)
        
    Returns:
        RGB image with uncertainty overlay
    """
    # Uncertainty as red overlay (more red = more uncertain)
    heatmap = array_to_heatmap(uncertainty, colormap="hot")
    
    # Convert image to RGB
    if len(image.shape) == 2:
        img_rgb = np.stack([image] * 3, axis=-1).astype(np.uint8)
    else:
        img_rgb = image.copy()
    
    # Blend with higher alpha in uncertain regions
    alpha_map = uncertainty[:, :, np.newaxis]
    result = (alpha_map * heatmap + (1 - alpha_map) * img_rgb).astype(np.uint8)
    
    return result


def image_to_base64(
    image: np.ndarray,
    format: str = "PNG",
) -> str:
    """
    Convert numpy array to base64-encoded image string.
    
    Args:
        image: RGB or grayscale image array
        format: Image format (PNG, JPEG)
        
    Returns:
        Base64-encoded image string
    """
    pil_img = Image.fromarray(image)
    
    buffer = io.BytesIO()
    pil_img.save(buffer, format=format)
    
    base64_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/{format.lower()};base64,{base64_str}"


def save_overlay(
    image: np.ndarray,
    output_path: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Save overlay image with optional metadata.
    
    Args:
        image: RGB image array
        output_path: Output file path
        metadata: Optional metadata to embed
        
    Returns:
        Absolute path to saved file
    """
    pil_img = Image.fromarray(image)
    
    # Add metadata as text overlay
    if metadata:
        draw = ImageDraw.Draw(pil_img)
        
        # Simple metadata text
        text_lines = [
            f"GEOX Seismic Image Interpretation",
            f"Seal: DITEMPA BUKAN DIBERI",
        ]
        
        # Add key metadata
        for key, value in metadata.items():
            if isinstance(value, (int, float, str)):
                text_lines.append(f"{key}: {value}")
        
        # Draw text (top-left corner)
        y_offset = 10
        for line in text_lines:
            draw.text((10, y_offset), line, fill=(255, 255, 0))
            y_offset += 15
    
    # Save
    pil_img.save(output_path)
    
    return str(Path(output_path).absolute())


async def generate_visualization(
    image_path: str,
    visualization_type: str,
    data: dict[str, Any],
    output_path: str | None = None,
) -> dict[str, Any]:
    """
    Generate visualization for seismic interpretation.
    
    Args:
        image_path: Path to original seismic image
        visualization_type: Type of visualization (reflectors, faults, facies, uncertainty)
        data: Visualization data (reflectors, fault_map, etc.)
        output_path: Optional output path
        
    Returns:
        Dictionary with base64_image and file_path
    """
    try:
        # Load image
        img = Image.open(image_path).convert('L')
        img_array = np.array(img, dtype=np.uint8)
        
        # Generate overlay
        if visualization_type == "reflectors":
            result = overlay_reflectors(
                img_array,
                data.get("reflectors", []),
            )
        elif visualization_type == "faults":
            # Create mock fault map from candidates
            fault_map = np.zeros_like(img_array, dtype=float)
            for fault in data.get("candidates", []):
                for pixel in fault.get("pixels", []):
                    y, x = pixel
                    if 0 <= y < fault_map.shape[0] and 0 <= x < fault_map.shape[1]:
                        fault_map[y, x] = fault.get("likelihood_score", 0.5)
            result = overlay_fault_likelihood(img_array, fault_map)
        elif visualization_type == "facies":
            # Mock segmentation from class probabilities
            seg = np.zeros_like(img_array, dtype=int)
            result = overlay_facies(img_array, seg)
        elif visualization_type == "uncertainty":
            uncertainty = np.array(data.get("uncertainty_map", [[0]]))
            result = create_uncertainty_overlay(img_array, uncertainty)
        else:
            result = np.stack([img_array] * 3, axis=-1)
        
        # Convert to base64
        base64_image = image_to_base64(result)
        
        # Save if path provided
        file_path = None
        if output_path:
            metadata = {
                "type": visualization_type,
                "image_path": image_path,
            }
            file_path = save_overlay(result, output_path, metadata)
        
        return {
            "success": True,
            "visualization_type": visualization_type,
            "base64_image": base64_image,
            "file_path": file_path,
            "dimensions": result.shape[:2],
        }
        
    except Exception as e:
        logger.exception("Visualization failed: %s", e)
        return {
            "success": False,
            "error": str(e),
        }
