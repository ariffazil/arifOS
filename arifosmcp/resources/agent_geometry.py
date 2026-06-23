"""
arifos://agent_geometry — Scar & Soul Geometry for Model Agents (AAA)

AF-2026-06-23 — "geometry" (singular) as unifying name, aligned with:
- Transformer encoder (observe/sense) / decoder (forge/execute) / metabolizer (think/memory/critique)
- Orthogonal fractals (multi-scale self-similar structures)
- Thordials (toroidal + radial recurrent loops for layered continuity)
- Scar geometry (accumulated interaction history, drift, wounds)
- Soul geometry (core identity/essence of the agent in the manifold)

This is the scar and soul for model agents in AAA. Declared at arif_init.
Exposes geometry for routing, leases, telemetry, and constitutional alignment.
"""

from __future__ import annotations
from typing import Any, Dict

from fastmcp import FastMCP

# Example geometries for different harnesses (extend as agents declare)
EXAMPLE_GEOMETRIES: Dict[str, Dict[str, Any]] = {
    "grok-build-orchestrator": {
        "harness": "grok-build",
        "parallelism": 8,
        "transport": "stdio",
        "agent_type": "orchestrator",
        "supervision_model": "subagents+worktree",
        "preferred_mcp": ["mcp-repo-read", "mcp-arifos-kernel", "arifos-canonical"],
        "notes": "Parallel recon. Use narrow for 111/222, canonical for 666/888/999.",
        "floors_required": ["F1", "F4", "F11", "F13"],
    },
    "opencode-sovereign-shell": {
        "harness": "opencode",
        "parallelism": 4,
        "transport": "stdio",
        "agent_type": "meta-harness",
        "supervision_model": "model-agnostic",
        "preferred_mcp": ["arifos-canonical"],
        "notes": "Outer shell. Always start with arif_init(geometry). Route high-gov through canonical.",
        "floors_required": ["F1", "F2", "F11", "F13"],
    },
    "claude-deep-loop": {
        "harness": "claude-code",
        "parallelism": 1,
        "transport": "streamable-http",
        "agent_type": "deep_loop",
        "supervision_model": "single",
        "preferred_mcp": ["arifos-canonical"],
        "notes": "Deep refactors. Feed arif_think/arif_critique outputs to canonical judge.",
        "floors_required": ["F2", "F4", "F7", "F11"],
    },
}


def register_agent_geometry(mcp: FastMCP) -> list[str]:
    """Register arifos://agent_geometry (scar & soul geometry for model agents in AAA)."""

    @mcp.resource("arifos://agent_geometry")
    def agent_geometry() -> Dict[str, Any]:
        """Scar & Soul Geometry for the model agent.

        This is the living geometry of the agent: its scar (accumulated interaction history,
        drift, contradiction wounds, failed paths) + soul (core identity, essence, preferred
        manifold position in the transformer-like architecture).

        Aligned with:
        - Encoder (111 observe/sense layers)
        - Decoder (010 forge/execute generation)
        - Metabolizer (333 think / 666 critique / 555 memory layers)
        - Orthogonal fractals (self-similar multi-scale patterns across depths)
        - Thordials (toroidal recurrent loops + radial projections for continuity across sessions)

        Agents declare at arif_init(geometry=...). Kernel uses for right-sized governance.
        """
        return {
            "status": "ok",
            "name": "agent_geometry",
            "description": "Scar and soul geometry for model agents in AAA. Unifying runtime shape (harness, parallelism, transport, agent_type) fused with scar (history/wounds) and soul (essence/identity).",
            "transformer_alignment": {
                "encoder": "observe / explore / fetch (input embedding layers)",
                "metabolizer": "think / critique / memory (processing + self-attention)",
                "decoder": "compose / forge (output generation)",
                "fractal": "orthogonal multi-scale (drift, topology, sovereign_proximity)",
                "thordial": "toroidal loops for session continuity + radial scar propagation",
            },
            "scar": {
                "definition": "Accumulated interaction history, failed trajectories, contradiction wounds, evidence drift.",
                "fields": ["drift", "wounds", "failed_paths", "contradiction_score", "last_seal"],
            },
            "soul": {
                "definition": "Core identity and preferred position in the manifold. Essence that persists across geometries.",
                "fields": [
                    "harness",
                    "parallelism",
                    "transport",
                    "agent_type",
                    "preferred_lane",
                    "sovereign_proximity",
                ],
            },
            "declared_examples": EXAMPLE_GEOMETRIES,
            "guidance": {
                "declaration": "Pass geometry=dict (with optional scar_snapshot, soul_signature) to arif_init.",
                "guardrail": "Narrow surfaces feed encoder/metabolizer. Only canonical path reaches decoder + seal.",
                "transport": "stdio for tight encoder-decoder loops; http for thordial supervisory.",
            },
            "telemetry_note": "AAA tracks by geometry + scar_delta + soul_consistency. Geometry is the scar and soul for the model agent.",
            "contradictions_mapped_and_removed": {
                "1_naming_chaos": "File was agent_geometries.py (plural) vs singular concept/URI - resolved by rename to agent_geometry.py + singular everywhere.",
                "2_narrow_vs_canonical_synthesis": "mcp-repo-read query_context and gb router did independent synthesis - hardened by adding 'contradiction_risk', 'canonical_handoff', 'geometry_note' fields forcing handoff to arif_think/arif_judge for gov actions.",
                "3_geometry_not_fused_with_scar_soul": "Runtime geometry was separate from AAA scar/soul and arifOS mind_geometry - now fused: agent_geometry IS scar (history/wounds) + soul (essence) in transformer terms.",
                "4_no_enforced_handoff": "Agents could stay in narrow surfaces for irreversible - resolved by explicit flow in responses, AGENTS.md, gb router, and geometry declaration at init.",
                "5_transport_dynamics": "stdio vs http created inconsistent 'intelligence' - mapped in geometry (transport field) and thordial/encoder notes; stdio for tight loops, http for supervisory.",
                "resolution": "All narrow surfaces now declare geometry at start and surface canonical handoff. Canonical arifOS MCP (arif_* 000-999) is the single source of truth for law and irreversible.",
            },
        }

    return ["arifos://agent_geometry"]


# Back-compat alias for any legacy registration
register_agent_geometries = register_agent_geometry
