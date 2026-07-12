"""
arifosmcp/tools/somatic.py — Somatic Paradox Engine (Agent-Facing)

Exposes the Paradox Engine to agents via `arif_somatic`.

This is the WIRING that connects A-FORGE's Paradox Engine
into the arifOS kernel as an agent-accessible tool.

Signal flow:
  DSP/text/WELL → MotifState → ParadoxEngine → SomaticSnapshot → Agent

The agent does NOT process audio. It operates upon somatic motif state
that has been abstracted from audio, text, or other sources.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import sys
from typing import Any

# Add A-FORGE paradox-engine to path
sys.path.insert(0, "/root/A-FORGE/paradox-engine")

from kernel_bridge import get_somatic_kernel


def arif_somatic(
    mode: str = "state",
    motif_id: str = "",
    intensity: float = 0.5,
    text: str = "",
    candidate_output: str = "",
    motif_a: str = "",
    motif_b: str = "",
) -> dict[str, Any]:
    """
    Somatic Paradox Engine — agent interface.

    The agent's window into its somatic state. Not audio processing,
    not sentiment analysis — somatic motif state with cultural
    contradiction rules and paradox persistence.

    Modes:
      state       — Current somatic snapshot (motifs, paradoxes, score)
      feed        — Inject a motif activation (from DSP/text/external)
      text_scan   — Scan text for motif activations
      gate        — Check if candidate output resolves active paradoxes
      paradoxes   — List active paradoxes with tension/duration
      emergence   — List emergence events
      relation    — Get relationship between two motifs
      motifs      — List all available motifs in the taxonomy
      bridge      — Constitutional bridge (somatic → governance signals)
      score       — Quick paradox score only

    Args:
      mode: operation mode
      motif_id: motif to activate (feed mode)
      intensity: activation intensity [0,1] (feed mode)
      text: text to scan (text_scan mode)
      candidate_output: output to gate (gate mode)
      motif_a: first motif (relation mode)
      motif_b: second motif (relation mode)
    """
    kernel = get_somatic_kernel()

    if mode == "state":
        ctx = kernel.agent_context()
        score = kernel.paradox_score()
        state = kernel.get_state()
        return {
            "context": ctx,
            "paradox_score": round(score, 3),
            "active_motifs": len(state.get("active_motifs", {})),
            "paradox_count": state.get("engine", {}).get("paradox_count", 0),
            "emergence_count": state.get("engine", {}).get("emergence_count", 0),
        }

    elif mode == "feed":
        if not motif_id:
            return {
                "error": "motif_id required for feed mode",
                "available": kernel.list_motifs()[:10],
            }
        result = kernel.feed_motif(motif_id, intensity)
        # Auto-tick after feed
        tick_result = kernel.tick()
        result["tick"] = tick_result
        return result

    elif mode == "text_scan":
        if not text:
            return {"error": "text required for text_scan mode"}
        activated = kernel.feed_text(text)
        tick_result = kernel.tick()
        return {
            "activated": activated,
            "count": len(activated),
            "tick": tick_result,
        }

    elif mode == "gate":
        if not candidate_output:
            return {"error": "candidate_output required for gate mode"}
        return kernel.gate_output(candidate_output)

    elif mode == "paradoxes":
        return {
            "paradoxes": kernel.api.get_active_paradoxes(),
            "count": len(kernel.api.get_active_paradoxes()),
            "score": round(kernel.paradox_score(), 3),
        }

    elif mode == "emergence":
        return {
            "events": kernel.get_emergence_log(),
            "count": len(kernel.get_emergence_log()),
        }

    elif mode == "relation":
        if not motif_a or not motif_b:
            return {"error": "motif_a and motif_b required for relation mode"}
        return kernel.get_relation(motif_a, motif_b)

    elif mode == "motifs":
        motifs = kernel.list_motifs()
        return {
            "motifs": motifs,
            "count": len(motifs),
        }

    elif mode == "bridge":
        return kernel.constitutional_bridge()

    elif mode == "score":
        return {"paradox_score": round(kernel.paradox_score(), 3)}

    else:
        return {
            "error": f"Unknown mode: {mode}",
            "available_modes": [
                "state",
                "feed",
                "text_scan",
                "gate",
                "paradoxes",
                "emergence",
                "relation",
                "motifs",
                "bridge",
                "score",
            ],
        }
