"""
ContrastViewGenerator — Multi-Contrast View Generation
DITEMPA BUKAN DIBERI

Implements Contrast Canon: Never trust single-view interpretation.
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ContrastViewGenerator:
    """
    Generate multiple contrast-variant views for ToAC compliance.
    """

    VIEW_CONFIGS = {
        "standard": {
            "transforms": ["colormap_mapping"],
            "description": "Original display",
        },
        "high_saliency": {
            "transforms": ["colormap_mapping", "histogram_equalization"],
            "description": "Enhanced local contrast",
        },
        "edge_enhanced": {
            "transforms": ["colormap_mapping", "edge_enhancement"],
            "description": "Structural edges emphasized",
        },
        "inverted": {
            "transforms": ["colormap_mapping", "polarity_inversion"],
            "description": "Inverted polarity",
        },
        "high_contrast": {
            "transforms": ["colormap_mapping", "gamma_adjustment"],
            "description": "Increased contrast",
        },
    }

    def generate(self, image: Image.Image) -> list[dict]:
        """Generate all contrast views."""
        views = []

        # Standard
        views.append(
            {
                "name": "standard",
                "image": image,
                **self.VIEW_CONFIGS["standard"],
            }
        )

        # High saliency
        eq = ImageOps.equalize(image.convert("L"))
        views.append(
            {
                "name": "high_saliency",
                "image": eq,
                **self.VIEW_CONFIGS["high_saliency"],
            }
        )

        # Edge enhanced
        edges = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        views.append(
            {
                "name": "edge_enhanced",
                "image": edges,
                **self.VIEW_CONFIGS["edge_enhanced"],
            }
        )

        # Inverted
        inv = ImageOps.invert(image.convert("L"))
        views.append(
            {
                "name": "inverted",
                "image": inv,
                **self.VIEW_CONFIGS["inverted"],
            }
        )

        # High contrast
        enhancer = ImageEnhance.Contrast(image)
        hc = enhancer.enhance(1.5)
        views.append(
            {
                "name": "high_contrast",
                "image": hc,
                **self.VIEW_CONFIGS["high_contrast"],
            }
        )

        return views
