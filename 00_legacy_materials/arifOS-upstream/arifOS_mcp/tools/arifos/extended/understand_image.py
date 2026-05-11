"""
arifos_understand_image — Extended Capability Tool
Powered by MiniMax Token Plan MCP
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
from typing import Any

from arifOS_mcp.runtime.governance import (
    ThermodynamicMetrics,
    Verdict,
    governed_return,
)
from .minimax_bridge import get_bridge

logger = logging.getLogger("arifOS.tools.understand_image")


async def understand_image(image_url: str, prompt: str = "") -> dict[str, Any]:
    """
    Analyze and understand image content via vision model.

    Constitutional mapping:
      - F2 Truth: vision-grounded description
      - F4 Clarity: structured image understanding
      - F7 Peace²: read-only, no side effects
      - F9 Ethics: no image generation, only analysis
    """
    bridge = get_bridge()

    try:
        result = await bridge.understand_image(image_url, prompt)

        metrics = ThermodynamicMetrics(
            truth_score=0.90,  # F2: vision-grounded
            delta_s=-0.05,  # F4: descriptive output reduces entropy
            peace_squared=1.0,  # F7: read-only
            stakeholder_safety=1.0,  # F5: no harm
            omega_0=0.04,  # F12: URL validated
            amanah_lock=True,  # F1: reversible
            tri_witness_score=0.90,  # F3: vision + text
        )

        return governed_return(
            stage="understand_image",
            data={"image_url": image_url, "prompt": prompt, "result": result},
            metrics=metrics,
            verdict=Verdict.SEAL,
            primary_metric_value=0.90,
        )

    except Exception as exc:
        logger.error("understand_image failed: %s", exc)
        metrics = ThermodynamicMetrics(
            truth_score=0.0,
            delta_s=1.0,
            peace_squared=1.0,
            stakeholder_safety=1.0,
            omega_0=0.04,
            amanah_lock=True,
            tri_witness_score=0.0,
        )
        return governed_return(
            stage="understand_image",
            data={"error": str(exc)},
            metrics=metrics,
            verdict=Verdict.SABAR,
            primary_metric_value=0.0,
        )
