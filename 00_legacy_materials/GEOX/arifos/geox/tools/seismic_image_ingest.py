"""
GEOX Seismic Image Ingest — Stage 1
DITEMPA BUKAN DIBERI

Normalization and validation of raw image inputs.
Ensures we work with consistently scaled grayscale arrays.
"""

from __future__ import annotations

import logging
import os

import numpy as np
from PIL import Image

from ..contrast_wrapper import contrast_governed_tool
from ..schemas.seismic_image import (
    GEOX_SEISMIC_IMAGE_INPUT,
    GEOX_SEISMIC_RASTER,
)

logger = logging.getLogger(__name__)


@contrast_governed_tool(physical_axes=["inline", "depth"])
async def ingest_seismic_image(inputs: GEOX_SEISMIC_IMAGE_INPUT) -> GEOX_SEISMIC_RASTER:
    """
    Load, normalize, and return the image as a numpy array with metadata.
    """
    if not os.path.exists(inputs.image_path):
        raise FileNotFoundError(f"Seismic image not found: {inputs.image_path}")

    with Image.open(inputs.image_path) as img:
        # Convert to grayscale
        gray = img.convert("L")
        arr = np.array(gray).astype(np.float32)

    # Normalize to [0, 1]
    arr_min, arr_max = arr.min(), arr.max()
    if arr_max > arr_min:
        arr = (arr - arr_min) / (arr_max - arr_min)
    else:
        arr = np.zeros_like(arr)

    # Cache normalized version (in production, use a dedicated cache dir)
    cache_path = inputs.image_path + ".normalized.npy"
    np.save(cache_path, arr)

    return {
        "line_id": inputs.line_id,
        "raw_path": inputs.image_path,
        "normalized_path": cache_path,
        "shape": arr.shape,
        "metadata": inputs.model_dump(),
    }
