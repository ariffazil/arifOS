"""
GEOX Structural Overlay — Draws features on seismic images
DITEMPA BUKAN DIBERI

Uses Pillow (PIL) for image-only structural markup.
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageDraw

OUTPUT_DIR = Path("geox_output")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

async def create_overlay(base_image_path: str, features: List[Dict[str, Any]], overlay_type: str = "faults") -> Path:
    """Draw fault sticks or horizons on a seismic image using Pillow."""
    try:
        # Load base image (mocking with a noise image if file missing for demo)
        if not os.path.exists(base_image_path):
             base = Image.new("RGB", (600, 400), (40, 40, 40))
        else:
             base = Image.open(base_image_path).convert("RGB")
    except Exception:
        base = Image.new("RGB", (600, 400), (30, 30, 30))

    draw = ImageDraw.Draw(base)
    
    # Colors: Green for faults, Blue for horizons (Standard GEOX Palette)
    color = (0, 255, 0) if overlay_type == "faults" else (0, 100, 255)
    
    # Overlay from features
    for feature in features:
        # Expected: x1, y1, x2, y2 coordinates
        coords = [feature.get("x1", 0), feature.get("y1", 0), feature.get("x2", 0), feature.get("y2", 0)]
        strength = float(feature.get("strength", 1.0))
        draw.line(coords, fill=color, width=int(3 * strength))

    # Add Legend/Text (Requires font file for full text, fallback to rectangle)
    draw.rectangle([10, 10, 200, 40], outline=color, width=2)
    # Simple label mockup
    
    filename = f"overlay_{overlay_type}_{int(time.time())}.png"
    output_path = OUTPUT_DIR / filename
    base.save(output_path)

    return output_path
