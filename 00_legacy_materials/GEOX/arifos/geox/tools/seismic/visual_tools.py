"""
GEOX Visual Extraction — Multimodal seismic encoding
DITEMPA BUKAN DIBERI

Implements the Encoder/Metabolizer stage for multimodal LLM ignition.
Returns base64-encoded contrast variants for MCP.
"""

import os
import io
import base64
from typing import List, Dict
import numpy as np
from PIL import Image, ImageOps, ImageFilter

from arifos.geox.ENGINE.contrast_wrapper import contrast_governed_tool


def encode_image_to_base64(img: Image.Image) -> str:
    """Helper to convert PIL Image to base64 PNG."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@contrast_governed_tool
async def extract_seismic_views(seismic_data: str) -> List[Dict[str, str]]:
    """
    Extract multiple contrast-variant images for multimodal LLM consumption.
    Returns a list of dictionaries with 'label', 'base64', and 'mimeType'.
    """
    try:
        # For demo, if path doesn't exist, generate a structured synthetic pattern
        if not os.path.exists(seismic_data):
            # Generate synthetic 'folded' seismic pattern
            arr = np.zeros((400, 600), dtype=np.uint8)
            for i in range(400):
                arr[i, :] = 127 + 50 * np.sin(
                    np.pi * (np.arange(600) / 100 + 4 * np.sin(i / 100))
                )
            raw_img = Image.fromarray(arr).convert("L")
        else:
            raw_img = Image.open(seismic_data).convert("L")
    except Exception:
        # Fallback to noise
        raw_img = Image.fromarray(np.random.randint(0, 255, (400, 600), dtype=np.uint8))

    # Variant 1: Standard
    v1_base64 = encode_image_to_base64(raw_img)

    # Variant 2: High Saliency (CLAHE-like / Equalized)
    v2_img = ImageOps.equalize(raw_img)
    v2_base64 = encode_image_to_base64(v2_img)

    # Variant 3: Edge Enhance (Structure focused)
    v3_img = raw_img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    v3_base64 = encode_image_to_base64(v3_img)

    return [
        {"label": "Standard Contrast", "base64": v1_base64, "mimeType": "image/png"},
        {
            "label": "High Saliency (Equalized)",
            "base64": v2_base64,
            "mimeType": "image/png",
        },
        {
            "label": "Structural Edge Enhancement",
            "base64": v3_base64,
            "mimeType": "image/png",
        },
    ]
