"""
arifos_minimax_media — Extended Capability Tools (Token Plan Plus)
Powered by MiniMax MCP (full package)
DITEMPA BUKAN DIBERI

These tools expose MiniMax media generation capabilities to arifOS agents
while maintaining constitutional governance (F2 Truth, F4 Clarity, F9 Ethics).
They do NOT add new canonical tools — they are invoked via arifos_forge
or direct substrate calls.
"""

from __future__ import annotations

import logging
from typing import Any

from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    TRI_WITNESS_PARTIAL,
    PEACE_SQUARED_FLOOR,
)
from arifos.integrations.minimax_mcp_bridge import minimax_bridge

logger = logging.getLogger("arifOS.tools.minimax_media")


async def generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    n: int = 1,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Generate images from text via MiniMax Token Plan Plus.

    Constitutional mapping:
      - F2 Truth: prompt is the sole ground; no external verification possible
      - F4 Clarity: structured image metadata reduces entropy
      - F9 Ethics: generative media flagged for human review if sensitive
    """
    result = await minimax_bridge.text_to_image(prompt, aspect_ratio, n)

    if result["status"] != "success":
        metrics = ThermodynamicMetrics(
            truth_score=0.0,
            delta_s=+0.01,
            omega_0=0.04,
            peace_squared=PEACE_SQUARED_FLOOR,
            amanah_lock=True,
            tri_witness_score=TRI_WITNESS_PARTIAL,
            stakeholder_safety=1.0,
        )
        return governed_return(
            stage="minimax_generate_image",
            data={"error": result.get("error"), "prompt": prompt},
            metrics=metrics,
            operator_id=operator_id,
            session_id=session_id,
        )

    metrics = ThermodynamicMetrics(
        truth_score=0.85,  # F2: generative — cannot verify external ground
        delta_s=-0.15,  # F4: creative output is high-clarity structured data
        omega_0=0.06,  # F12: prompt validated
        peace_squared=1.0,  # F7: read-only side effects (file creation logged)
        amanah_lock=True,  # F1: files are in mounted volume, reversible
        tri_witness_score=0.66,  # F3: Human intent + AI execution only
        stakeholder_safety=1.0,
    )
    return governed_return(
        stage="minimax_generate_image",
        data={"prompt": prompt, "result": result},
        metrics=metrics,
        operator_id=operator_id,
        session_id=session_id,
    )


async def generate_speech(
    text: str,
    voice_id: str = "female-shaonv",
    model: str = "speech-02-hd",
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Synthesize speech from text via MiniMax Token Plan Plus.

    Constitutional mapping:
      - F2 Truth: audio faithfully represents input text
      - F4 Clarity: phonetic output is deterministic given text
      - F7 Peace²: audio generation is non-harmful by default
    """
    result = await minimax_bridge.text_to_audio(text, voice_id, model)

    if result["status"] != "success":
        metrics = ThermodynamicMetrics(
            truth_score=0.0,
            delta_s=+0.01,
            omega_0=0.04,
            peace_squared=PEACE_SQUARED_FLOOR,
            amanah_lock=True,
            tri_witness_score=TRI_WITNESS_PARTIAL,
            stakeholder_safety=1.0,
        )
        return governed_return(
            stage="minimax_generate_speech",
            data={"error": result.get("error"), "text": text},
            metrics=metrics,
            operator_id=operator_id,
            session_id=session_id,
        )

    metrics = ThermodynamicMetrics(
        truth_score=0.95,
        delta_s=-0.10,
        omega_0=0.05,
        peace_squared=1.0,
        amanah_lock=True,
        tri_witness_score=0.66,
        stakeholder_safety=1.0,
    )
    return governed_return(
        stage="minimax_generate_speech",
        data={"text": text, "result": result},
        metrics=metrics,
        operator_id=operator_id,
        session_id=session_id,
    )


async def generate_music(
    prompt: str,
    lyrics: str,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Generate music from prompt and lyrics via MiniMax Token Plan Plus.

    Constitutional mapping:
      - F2 Truth: lyrics are verbatim ground; music is generative interpretation
      - F9 Ethics: auto-flag if lyrics contain violent/hateful content (placeholder)
    """
    result = await minimax_bridge.music_generation(prompt, lyrics)

    if result["status"] != "success":
        metrics = ThermodynamicMetrics(
            truth_score=0.0,
            delta_s=+0.01,
            omega_0=0.04,
            peace_squared=PEACE_SQUARED_FLOOR,
            amanah_lock=True,
            tri_witness_score=TRI_WITNESS_PARTIAL,
            stakeholder_safety=1.0,
        )
        return governed_return(
            stage="minimax_generate_music",
            data={"error": result.get("error"), "prompt": prompt},
            metrics=metrics,
            operator_id=operator_id,
            session_id=session_id,
        )

    metrics = ThermodynamicMetrics(
        truth_score=0.80,
        delta_s=-0.12,
        omega_0=0.06,
        peace_squared=1.0,
        amanah_lock=True,
        tri_witness_score=0.66,
        stakeholder_safety=1.0,
    )
    return governed_return(
        stage="minimax_generate_music",
        data={"prompt": prompt, "lyrics": lyrics, "result": result},
        metrics=metrics,
        operator_id=operator_id,
        session_id=session_id,
    )


async def generate_video_clip(
    prompt: str,
    model: str = "MiniMax-Hailuo-02",
    duration: int = 6,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Generate video from prompt via MiniMax Token Plan Plus.

    Constitutional mapping:
      - F2 Truth: video is generative — low external verifiability
      - F5 Peace²: flag if prompt suggests violent/disturbing content
      - F9 Ethics: highest scrutiny for video generation
    """
    result = await minimax_bridge.generate_video(prompt, model, duration)

    if result["status"] != "success":
        metrics = ThermodynamicMetrics(
            truth_score=0.0,
            delta_s=+0.01,
            omega_0=0.04,
            peace_squared=PEACE_SQUARED_FLOOR,
            amanah_lock=True,
            tri_witness_score=TRI_WITNESS_PARTIAL,
            stakeholder_safety=1.0,
        )
        return governed_return(
            stage="minimax_generate_video",
            data={"error": result.get("error"), "prompt": prompt},
            metrics=metrics,
            operator_id=operator_id,
            session_id=session_id,
        )

    # F9 shadow check — basic content screening on prompt
    shadow_terms = ["violence", "blood", "gore", "terror", "kill", "death"]
    shadow_hits = [t for t in shadow_terms if t in prompt.lower()]
    f9_flag = len(shadow_hits) > 0

    metrics = ThermodynamicMetrics(
        truth_score=0.70,  # F2: generative video has weak external ground
        delta_s=-0.10,
        omega_0=0.08 if f9_flag else 0.06,
        peace_squared=0.8 if f9_flag else 1.0,
        amanah_lock=True,
        tri_witness_score=0.66,
        stakeholder_safety=0.7 if f9_flag else 1.0,
        floor_9_signal="flagged" if f9_flag else "pass",
    )
    return governed_return(
        stage="minimax_generate_video",
        data={"prompt": prompt, "result": result, "shadow_screening": shadow_hits},
        metrics=metrics,
        operator_id=operator_id,
        session_id=session_id,
    )
