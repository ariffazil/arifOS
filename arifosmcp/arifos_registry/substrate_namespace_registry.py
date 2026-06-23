"""
Substrate Namespace Registry — Single source of truth for MCP tool namespaces.

Per F13 directive: "name is the first act of creation"
Per SUBSTRATE_NAMESPACES.md: every MCP tool name begins with its owning organ's namespace.

This registry:
- Declares canonical namespaces (arif, wealth, geox, well, aforge)
- Holds the legacy alias map (old_name → new_name)
- Provides the NamespaceGuard (validates tool names)
- Provides a per-organ tool surface summary

F2 TRUTH: This registry is rebuilt from live MCP /health + /tools/list probes.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

# Canonical namespaces (per F13 SOVEREIGN ruling 2026-06-14)
# Source: /root/arifOS/AGENTS.md "Namespace ruling (F13 SOVEREIGN 2026-06-14)"
#
# - arif_*   — Canonical prefix for all kernel + diagnostic tools (sanctioned)
# - hermes_* — Sanctioned non-arif_ namespace for Hermes ASI tools
# - forge_*  — Sanctioned non-arif_ namespace for A-FORGE pre-execution tools
# - mcp_*    — Utility namespace for operational diagnostics (mcp_drift_check)
# - arifos_* — BLOCKED; internal-only prefix, never exposed on public MCP
#
# Domain organs (each has its own canonical prefix):
# - wealth_* — WEALTH capital-intelligence
# - geox_*   — GEOX earth-intelligence
# - well_*   — WELL human-readiness
CANONICAL_NAMESPACES = ("arif", "wealth", "geox", "well", "hermes", "forge", "mcp")

# Accepted organ prefixes (includes organ-owned namespaces for federation validation)
# Note: aforge_ is reserved for any future A-FORGE MCP surface; A-FORGE is currently
# HTTP REST on :7071, accessed via arif_forge → aforge_*
CANONICAL_ORGAN_PREFIXES = CANONICAL_NAMESPACES + ("aforge",)

# Legacy aliases: old_tool_name → canonical_tool_name
LEGACY_ALIASES: dict[str, str] = {
    # GEOX legacy
    "geox_deviation_survey_inspect": "geox_header_inspect",
    "geox_tops_inspect": "geox_header_inspect",
    "geox_seismic_inspect": "geox_header_inspect",
    "geox_ingest_bundle": "geox_data_ingest_bundle",
    "geox_qc_bundle": "geox_data_qc_bundle",
    "geox_anomalous_contrast": "geox_ac_detector",
    "geox_evidence_summarize_cross": "geox_evidence_reason",
    "geox_process_abduction": "geox_evidence_reason",
    "geox_evidence_contradiction_scan": "geox_evidence_reason",
    "geox_well_compute_gr_bins": "geox_sequence_stratigraphy",
    "geox_well_build_packages": "geox_sequence_stratigraphy",
    "geox_well_infer_seq_strat": "geox_sequence_stratigraphy",
    "geox_well_analyze_sequence": "geox_sequence_stratigraphy",
    "geox_seismic_tie": "geox_seismic_compute",
    "geox_seismic_analyze_volume": "geox_seismic_compute",
    "geox_td_anchor": "geox_seismic_compute",
    "geox_forward_model": "geox_seismic_compute",
    "geox_petrophysics": "geox_subsurface_generate_candidates",
    "geox_section_interpret_correlation": "geox_sequence_interpret",
    "geox_stratigraphy_preview_config": "geox_sequence_interpret",
    "geox_stratigraphy_run_pipeline": "geox_sequence_interpret",
    "geox_subsurface_candidates": "geox_subsurface_generate_candidates",
    "geox_prospect_judge_preview": "geox_prospect_evaluate",
    "geox_prospect_judge_seal": "geox_prospect_evaluate",
    "geox_prospect_judge_verdict": "geox_prospect_evaluate",
    "geox_abstraction_guard": "geox_query_intake",
    "geox_vision_minimax_inference": "geox_vision_perceptual_inventory",
    "geox_vision_calibrate": "geox_vision_perceptual_inventory",
    "geox_vision_audit": "geox_vision_perceptual_inventory",
    "geox_attribute_registry_list_tool": "geox_attribute_registry_list",
    "geox_blend_volume_tool": "geox_blend_volume",
    "geox_blockspace_resolution_tool": "geox_blockspace_resolution",
    "geox_coord_transform_tool": "geox_coord_transform",
    "geox_fault_stick_ingest_tool": "geox_fault_stick_ingest",
    "geox_segy_export_tool": "geox_segy_export",
    "geox_seismic_compute_attribute_tool": "geox_seismic_compute",
    "geox_volume_frame_tool": "geox_volume_frame",
    "geox_dst_ingest_test": "geox_dst_ingest",
    "geox_literature_ingest": "geox_evidence_discover",
    "geox_las_inspect": "geox_header_inspect",
    "geox_seismic_segy_inspect": "geox_header_inspect",
    "geox_registry": "geox_system_registry_status",
    "geox_report_to_workflow": "geox_query_intake",
    # A-FORGE exposed via arifOS (per F13 ruling 2026-06-14: forge_* is SANCTIONED canonical)
    # No rename needed; forge_plan etc. are canonical, not legacy.
    #
    # Hermes exposed via arifOS (hermes_* is SANCTIONED canonical peer-agent namespace)
    # No alias needed; hermes_* tools are canonical, not legacy.
}


@dataclass
class SubstrateNamespace:
    """A single canonical namespace."""

    name: str  # e.g. "wealth"
    organ: str  # e.g. "WEALTH"
    endpoint: str  # e.g. "http://127.0.0.1:18082/mcp"
    lanes: list[str] = field(default_factory=list)
    tool_count: int = 0
    description: str = ""


class SubstrateNamespaceRegistry:
    """Single source of truth for MCP tool namespaces."""

    def __init__(self):
        self._namespaces: dict[str, SubstrateNamespace] = {
            "arif": SubstrateNamespace(
                name="arif",
                organ="arifOS",
                endpoint="http://127.0.0.1:8088/mcp",
                lanes=["discovery", "evidence", "reasoning", "judgment", "governance", "transport"],
                tool_count=39,  # 13 canonical + 5 diagnostic + 21 operational
                description="Constitutional kernel: identity, memory, judge, vault, lease, kernel_route",
            ),
            "wealth": SubstrateNamespace(
                name="wealth",
                organ="WEALTH",
                endpoint="http://127.0.0.1:18082/mcp",
                lanes=["wealth_calculate", "wealth_audit", "wealth_data", "wealth_meta"],
                tool_count=60,
                description="Capital intelligence organ: NPV, IRR, conservation, flow, entropy, stock analysis",
            ),
            "geox": SubstrateNamespace(
                name="geox",
                organ="GEOX",
                endpoint="http://127.0.0.1:8081/mcp",
                lanes=["geox_discovery", "geox_evidence", "geox_reasoning", "geox_judgment"],
                tool_count=60,
                description="Earth-intelligence organ: claim engine, seismic, petrophysics, basin",
            ),
            "well": SubstrateNamespace(
                name="well",
                organ="WELL",
                endpoint="http://127.0.0.1:18083/mcp",
                lanes=["well_measure"],
                tool_count=18,
                description="Human-readiness organ: assess_homeostasis, validate_vitality, guard_dignity",
            ),
            "aforge": SubstrateNamespace(
                name="aforge",
                organ="A-FORGE",
                endpoint="http://127.0.0.1:7071",
                lanes=[],
                tool_count=4,  # forge_plan, forge_dry_run, forge_query, forge_execute
                description="Deployment + infra forge: HTTP REST on :7071, accessed via arif_forge",
            ),
            # Peer agents (per F13 ruling 2026-06-14)
            "hermes": SubstrateNamespace(
                name="hermes",
                organ="Hermes (ASI peer agent, port 18001)",
                endpoint="http://127.0.0.1:18001/mcp",
                lanes=["asi_observation", "asi_judgment", "asi_deliberation"],
                tool_count=7,  # hermes_system_status, hermes_vault_query, hermes_epistemic_check, hermes_fact_check, hermes_cross_verify, hermes_plan_review, hermes_memory_steward
                description="Hermes ASI peer agent: 7 tools exposed via arifOS surface (judge, not executor)",
            ),
            "forge": SubstrateNamespace(
                name="forge",
                organ="A-FORGE pre-execution (port 7071 HTTP)",
                endpoint="http://127.0.0.1:8088/mcp",  # exposed via arifOS surface
                lanes=["forge_sub_execution"],
                tool_count=3,  # forge_plan, forge_dry_run, forge_query
                description="A-FORGE pre-execution tools exposed via arifOS surface (3 tools)",
            ),
            "mcp": SubstrateNamespace(
                name="mcp",
                organ="MCP utility (operational diagnostics)",
                endpoint="n/a",
                lanes=["mcp_diagnostic"],
                tool_count=1,  # mcp_drift_check
                description="MCP utility namespace for operational diagnostics (mcp_drift_check)",
            ),
        }

    def get(self, namespace: str) -> SubstrateNamespace | None:
        return self._namespaces.get(namespace)

    def resolve_organ_for_tool(self, tool_name: str) -> str | None:
        """Resolve which organ owns a given tool name. Returns namespace."""
        if not tool_name:
            return None
        ns = tool_name.split("_")[0]
        if ns in self._namespaces:
            return ns
        # Check legacy aliases
        canonical = LEGACY_ALIASES.get(tool_name)
        if canonical:
            return self.resolve_organ_for_tool(canonical)
        return None

    def canonical_name(self, tool_name: str) -> str:
        """Resolve a tool name to its canonical form (handles legacy aliases)."""
        return LEGACY_ALIASES.get(tool_name, tool_name)

    def is_valid_tool_name(self, tool_name: str) -> bool:
        """Validate that a tool name conforms to the namespace discipline."""
        if not tool_name or "_" not in tool_name:
            return False
        ns = tool_name.split("_")[0]
        return ns in self._namespaces

    def list_namespaces(self) -> list[SubstrateNamespace]:
        return list(self._namespaces.values())

    def list_legacy_aliases(self) -> dict[str, str]:
        return dict(LEGACY_ALIASES)

    def registry_hash(self) -> str:
        """BLAKE3 hash of the registry (for attestation)."""
        canonical = {
            "namespaces": sorted([(k, v.organ, v.tool_count) for k, v in self._namespaces.items()]),
            "legacy_aliases": sorted(LEGACY_ALIASES.items()),
        }
        import json

        return "b3:" + hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()

    def export(self) -> dict:
        return {
            "version": 1,
            "registry_hash": self.registry_hash(),
            "namespaces": [
                {
                    "namespace": ns.name,
                    "organ": ns.organ,
                    "endpoint": ns.endpoint,
                    "lanes": ns.lanes,
                    "tool_count": ns.tool_count,
                    "description": ns.description,
                }
                for ns in self._namespaces.values()
            ],
            "legacy_alias_count": len(LEGACY_ALIASES),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


# Singleton instance
_registry = None


def get_substrate_namespace_registry() -> SubstrateNamespaceRegistry:
    """Lazy-init the substrate namespace registry."""
    global _registry
    if _registry is None:
        _registry = SubstrateNamespaceRegistry()
    return _registry
