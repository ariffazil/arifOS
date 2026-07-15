"""
arifOS Resources — Canonical URI Surface
═══════════════════════════════════════

Core public + supplemental resources (intelligence, not chaos).

TRUTH HIERARCHY (all resources carry a truth_level):
  1 SOVEREIGN_CANON  — Immutable constitution, seals, sovereign directives
  2 SEALED_VAULT     — Append-only ledger entries, signed judgments
  3 TRUSTED_REPO     — Version-controlled source of truth (git)
  4 OBSERVED_EXTERNAL — Web evidence, real-time sensor data
  5 USER_CLAIM       — Human input without verification
  6 MODEL_INFERENCE  — LLM-generated content, may hallucinate
  7 UNTRUSTED        — Unverified external, requires quarantine

CANONICAL (16 — includes loop-engineering + quickstart):
  arifos://doctrine          — Immutable law (F1–L13)
  arifos://trinity           — AAA lane definitions and separation of powers
  arifos://schema            — Complete blueprint (tools, lanes, forge bridge)
  arifos://civilization      — Organs, strata, and constitutional boundaries
  arifos://seal-readiness    — Vault integrity and seal gate
  arifos://jurisdiction      — Autonomy bands and capability grants
  arifos://identity          — Sovereign identity manifest and authority chain
  arifos://memory            — 6-layer memory architecture (L1–L6)
  arifos://vitals            — Metric reference and thresholds
  arifos://bootstrap         — Full federation knowledge-graph context (v2026.06.14)
  arifos://human/metabolized — Compact sovereign context (nutrient, not food)
  arifos://loop-engineering  — 7-stage reality engineering loop (K1 dual naming)
  arifos://quickstart        — LLM client getting started guide
  tree777://index            — TREE777 wiki index
  runner://policy/v1         — Context runner pinned policy (F2, F11)

SUPPLEMENTAL (3):
  arifos://mcp-alignment     — MCP spec conformance matrix (protocol, extensions, deprecations)
  arifos://resources/index   — Machine-readable JSON catalog of all resources
  arifos://skills-catalog    — Machine-readable skill registry (dynamic from filesystem)

ATLAS333 RESOURCES (13):
  arifos://atlas333/index            — Root index (all available ATLAS333 resources)
  arifos://atlas333/paradox/list     — All 33 paradoxes with axes, zones, organs
  arifos://atlas333/paradox/{id}     — Single paradox (1-33) with full context
  arifos://atlas333/quote/list       — All 33 quotes (M1-M11, R1-R11, J1-J11)
  arifos://atlas333/quote/{id}       — Single quote with author, organ, trigger
  arifos://atlas333/zones            — 7 paradox zones with paradox ranges
  arifos://atlas333/organs           — 3 quote organs (Memory/Mind/Judge)
  arifos://atlas333/thresholds       — TEARFRAME (trm≥0.94, echo≥0.87, rasa≥0.85)
  arifos://atlas333/activation/rules — GPV→paradox activation matrix
  arifos://atlas333/flow             — 10-stage pipeline
  arifos://atlas333/geometry         — Full cognitive geometry map
  arifos://atlas333/scar/{id}        — Sealed scar by ID (read-only)
  arifos://atlas333/seal/head        — VAULT999 chain head (cache-friendly)

GOVERNANCE RESOURCE:
  arifos://resources/audit   — Governed resource audit with hashes, truth levels, authority

REMOVED (chaos reduction):
  arifos://philosophy — beautiful, not operational. Agents don't load it.
  arifos://forge      — merged into arifos://schema
  source://list       — dynamic data → belongs in arif_fetch tool
  receipt://list      — dynamic data → belongs in arif_fetch tool
  tree777://search    — search → belongs in arif_memory_recall tool
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

from .bootstrap import register_bootstrap
from .civilization import register_civilization
from .doctrine import register_doctrine

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# RESOURCE PROVENANCE — MCP-spec-aligned metadata for all core resources
# ══════════════════════════════════════════════════════════════════════════════
# Per MCP spec: resources are application-driven context. Provenance tracks
# source, freshness, and evidence layer for constitutional compliance.
# ══════════════════════════════════════════════════════════════════════════════

_RESOURCE_PROVENANCE: dict[str, dict[str, Any]] = {
    "arifos://doctrine": {
        "source": "constitution",
        "truth_level": 1,
        "truth_label": "SOVEREIGN_CANON",
        "mutability": "immutable",
        "staleness": "never_stale",
        "evidence_layer": "constitutional",
    },
    "arifos://trinity": {
        "source": "aaa_control_plane",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "governance",
    },
    "arifos://schema": {
        "source": "arifosmcp_schema",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "structural",
    },
    "arifos://civilization": {
        "source": "arifosmcp_ontology",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "ontological",
    },
    "arifos://seal-readiness": {
        "source": "kernel_health_probe",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "dynamic",
        "staleness": "real_time",
        "evidence_layer": "operational",
    },
    "arifos://jurisdiction": {
        "source": "arifosmcp_governance",
        "truth_level": 2,
        "truth_label": "SEALED_VAULT",
        "mutability": "append_only",
        "staleness": "refresh_on_seal",
        "evidence_layer": "governance",
    },
    "arifos://identity": {
        "source": "identity_toml",
        "truth_level": 1,
        "truth_label": "SOVEREIGN_CANON",
        "mutability": "immutable",
        "staleness": "never_stale",
        "evidence_layer": "identity",
    },
    "arifos://memory": {
        "source": "arifosmcp_memory_arch",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "architectural",
    },
    "arifos://vitals": {
        "source": "kernel_metrics",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "dynamic",
        "staleness": "real_time",
        "evidence_layer": "operational",
    },
    "arifos://bootstrap": {
        "source": "federation_knowledge_graph",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "contextual",
    },
    "arifos://loop-engineering": {
        "source": "canonical_pipeline",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "procedural",
    },
    "arifos://quickstart": {
        "source": "documentation",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "documentation",
    },
    "arifos://mcp-alignment": {
        "source": "mcp_spec_comparison",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_spec_update",
        "evidence_layer": "conformance",
    },
    "arifos://human/metabolized": {
        "source": "sovereign_context",
        "truth_level": 5,
        "truth_label": "USER_CLAIM",
        "mutability": "session_scoped",
        "staleness": "per_session",
        "evidence_layer": "human",
    },
    "arifos://reality/state": {
        "source": "kernel_runtime",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "dynamic",
        "staleness": "real_time",
        "evidence_layer": "operational",
    },
    "arifos://mcp/surface-map": {
        "source": "tool_registry",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "dynamic",
        "staleness": "real_time",
        "evidence_layer": "operational",
    },
    # Evidence resource templates (F-WEB)
    "source://{hash}": {
        "source": "web_fetch",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "immutable_after_ingest",
        "staleness": "frozen_at_fetch",
        "evidence_layer": "evidence",
    },
    "receipt://web/{id}": {
        "source": "evidence_store",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "immutable_after_write",
        "staleness": "frozen_at_receipt",
        "evidence_layer": "evidence",
    },
    "contrast://{id}": {
        "source": "evidence_store",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "immutable_after_write",
        "staleness": "frozen_at_creation",
        "evidence_layer": "evidence",
    },
    "void://{id}": {
        "source": "evidence_store",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "immutable_after_write",
        "staleness": "frozen_at_creation",
        "evidence_layer": "evidence",
    },
    # Tree777 wiki
    "tree777://index": {
        "source": "wiki",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "knowledge",
    },
    "tree777://skills/{category}/{name}": {
        "source": "wiki",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "knowledge",
    },
    "tree777://concepts/{name}": {
        "source": "wiki",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "knowledge",
    },
    "tree777://scars/{name}": {
        "source": "wiki",
        "truth_level": 2,
        "truth_label": "SEALED_VAULT",
        "mutability": "append_only",
        "staleness": "never_stale",
        "evidence_layer": "scar",
    },
    # Sovereign
    "sovereign://{file}": {
        "source": "sovereign_fs",
        "truth_level": 1,
        "truth_label": "SOVEREIGN_CANON",
        "mutability": "sovereign_controlled",
        "staleness": "sovereign_determined",
        "evidence_layer": "sovereign",
    },
    # VAULT999
    "arifos://vault/{vault_type}": {
        "source": "vault999",
        "truth_level": 2,
        "truth_label": "SEALED_VAULT",
        "mutability": "append_only",
        "staleness": "never_stale",
        "evidence_layer": "audit",
    },
    # Witness
    "arifos://witness/log/{filter}": {
        "source": "witness_oracle",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "append_only",
        "staleness": "real_time",
        "evidence_layer": "witness",
    },
    "arifos://witness/stats/{period}": {
        "source": "witness_oracle",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "dynamic",
        "staleness": "real_time",
        "evidence_layer": "witness",
    },
    # Boundaries
    "arifos://boundaries/domain/{domain_id}": {
        "source": "boundary_sense",
        "truth_level": 4,
        "truth_label": "OBSERVED_EXTERNAL",
        "mutability": "dynamic",
        "staleness": "real_time",
        "evidence_layer": "operational",
    },
    # ATLAS333 — Cognitive Geometry Resources
    "arifos://atlas333/index": {
        "source": "atlas333_cognitive_geometry",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/paradox/list": {
        "source": "atlas333_evergreen",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/paradox/{id}": {
        "source": "paradox_quotes_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/quote/list": {
        "source": "paradox_quotes_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/quote/{id}": {
        "source": "paradox_quotes_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/zones": {
        "source": "atlas333_cognitive_geometry",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/organs": {
        "source": "paradox_quotes_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/thresholds": {
        "source": "types_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/activation/rules": {
        "source": "atlas_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/flow": {
        "source": "atlas333_cognitive_geometry",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/geometry": {
        "source": "atlas333_cognitive_geometry",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    "arifos://atlas333/scar/{id}": {
        "source": "scar_registry",
        "truth_level": 2,
        "truth_label": "SEALED_VAULT",
        "mutability": "append_only",
        "staleness": "never_stale",
        "evidence_layer": "scar",
    },
    "arifos://atlas333/seal/head": {
        "source": "vault999",
        "truth_level": 2,
        "truth_label": "SEALED_VAULT",
        "mutability": "append_only",
        "staleness": "real_time",
        "evidence_layer": "audit",
    },
}


def get_resource_provenance(uri: str) -> dict[str, Any] | None:
    """Get provenance metadata for a resource URI."""
    # Exact match first
    if uri in _RESOURCE_PROVENANCE:
        return _RESOURCE_PROVENANCE[uri]
    # Template match (e.g., source://{hash} → source://)
    for pattern, meta in _RESOURCE_PROVENANCE.items():
        if "{" in pattern and uri.startswith(pattern.split("{")[0]):
            return meta
    return None


from .embodied_resources import register_embodied_resources
from .evidence import register_evidence_resources
from .human_context import register_human_context
from .identity import register_identity
from .jurisdiction import register_jurisdiction
from .loop_engineering import register_loop_engineering
from .mcp_alignment import register_mcp_alignment
from .memory import register_memory
from .resources_index import register_resources_index
from .runner import register_runner_resources
from .schema import register_schema
from .reality_state import register_reality_state
from .seal_readiness import register_seal_readiness
from .skills_catalog import register_skills_catalog
from .sovereign import register_sovereign_resources
from .quickstart import register_quickstart
from .tree777 import register_tree777_resources
from .trinity import register_trinity
from .vitals import register_vitals
from .tool_discovery import register_tool_discovery
from .retrieve_tools import register_retrieve_tools
from .vault999_template import register_vault999_template
from .surface_map import register_surface_map
from .wisdom_resources import register_wisdom_resources
from .atlas333 import attach_to_mcp_resource as _atlas333_attach

CANONICAL_RESOURCES = (
    "arifos://doctrine",
    "arifos://trinity",
    "arifos://schema",
    "arifos://civilization",
    "arifos://seal-readiness",
    "arifos://jurisdiction",
    "arifos://identity",
    "arifos://memory",
    "arifos://vitals",
    "arifos://bootstrap",
    "arifos://human/metabolized",
    "arifos://loop-engineering",
    "arifos://quickstart",
    "arifos://mcp-alignment",  # MCP spec conformance — useful for debugging
    "arifos://mcp/surface-map",
)  # REMOVED 2026-06-28 (zen of resources — indices to indices):
#   tree777://index         — wiki index, not domain operational data
#   runner://policy/v1      — runner policy metadata, not AI operational data
#   arif://tools/discovery  — consolidated into arifos://tools/self-model

SUPPLEMENTAL_RESOURCES = (
    # REMOVED 2026-06-28 (catalog-of-catalog — meta, not domain data):
    #   arifos://resources/index — catalog of resources → meta
    #   arifos://skills-catalog — catalog of skills → meta
)

TREE777_RESOURCES = (
    # REMOVED 2026-06-28: tree777://index (meta, not domain data)
    # Keep concepts/scars — these are domain knowledge (geology concepts, scars)
    "tree777://concepts/{name}",
    "tree777://scars/{name}",
)

EMBODIED_RESOURCES = (
    # REMOVED 2026-06-28 (zen of resources — system introspection, not domain data):
    #   arifos://tools/self-model/{view}     — tool usage stats → system introspection
    #   arifos://tools/permissions/{scope}  — permission state → system state
    #   arifos://tools/composition-matrix/{format} — tool composition → meta
    # KEEP: audit trail + domain boundaries (AI needs this for governance work):
    "arifos://witness/log/{filter}",  # AI reads its own sealed audit trail
    "arifos://witness/stats/{period}",  # witness statistics
    "arifos://boundaries/domain/{domain_id}",  # domain policy per organ — AI needs this
)

EVIDENCE_RESOURCES = (
    # KEEP — template resources (one template → many instances).
    # These are domain data the AI fetched from the web, not catalogs or metadata.
    "source://{hash}",  # ingested web source content
    "receipt://web/{id}",  # evidence receipt for web fetch
    "contrast://{id}",  # cross-source contrast report
    "void://{id}",  # missing data taxonomy report
)

# Context Engine Runner — REMOVED 2026-06-28 (indices, not domain data):
#   runner://receipt/{run_id}  — receipt lookup → arif_fetch tool
#   runner://policy/v1         — runner policy metadata → not AI operational data
RUNNER_RESOURCES = ()


def register_resources(mcp: FastMCP) -> list[str]:
    """Register canonical + embodied + TREE777 concepts + human context families.

    ZEN OF RESOURCES (2026-06-28): Removed catalog-of-catalog, indices-to-indices,
    dynamic URI patterns. MCP resources = domain data AI needs for work, not
    metadata about metadata or filesystem mirrors.
    """
    registered: list[str] = []
    registered.extend(register_doctrine(mcp))
    registered.extend(register_trinity(mcp))
    registered.extend(register_schema(mcp))
    registered.extend(register_civilization(mcp))
    registered.extend(register_seal_readiness(mcp))
    registered.extend(register_jurisdiction(mcp))
    registered.extend(register_identity(mcp))
    registered.extend(register_memory(mcp))
    registered.extend(register_vitals(mcp))
    registered.extend(register_bootstrap(mcp))
    registered.extend(register_loop_engineering(mcp))
    registered.extend(register_quickstart(mcp))
    registered.extend(register_mcp_alignment(mcp))
    # DISABLED 2026-06-28 — catalog-of-catalog, not domain operational data:
    # registered.extend(register_resources_index(mcp))    # arifos://resources/index
    # registered.extend(register_skills_catalog(mcp))   # arifos://skills-catalog
    registered.extend(register_evidence_resources(mcp))
    registered.extend(register_embodied_resources(mcp))
    registered.extend(register_tree777_resources(mcp))
    # DISABLED 2026-06-28 — indices, not domain operational data:
    # registered.extend(register_runner_resources(mcp))   # runner://*
    registered.extend(register_sovereign_resources(mcp))
    registered.extend(register_human_context(mcp))
    registered.extend(register_reality_state(mcp))
    registered.extend(register_tool_discovery(mcp))
    registered.extend(register_retrieve_tools(mcp))
    registered.extend(register_vault999_template(mcp))
    registered.extend(register_surface_map(mcp))
    registered.extend(register_wisdom_resources(mcp))
    if _atlas333_attach:
        registered.extend(_atlas333_attach(mcp))
    return registered
