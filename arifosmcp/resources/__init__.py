"""
arifOS Resources — Canonical URI Surface
═══════════════════════════════════════

Core public resources — 30 canonical URIs across 6 chambers.
Reduced 2026-08-08 from 48 → 30 (chaos reduction, deprecated-alias removal).

TRUTH HIERARCHY (all resources carry a truth_level):
  1 SOVEREIGN_CANON  — Immutable constitution, seals, sovereign directives
  2 SEALED_VAULT     — Append-only ledger entries, signed judgments
  3 TRUSTED_REPO     — Version-controlled source of truth (git)
  4 OBSERVED_EXTERNAL — Web evidence, real-time sensor data
  5 USER_CLAIM       — Human input without verification
  6 MODEL_INFERENCE  — LLM-generated content, may hallucinate
  7 UNTRUSTED        — Unverified external, requires quarantine

CANONICAL (30 — organized by chamber):

  IDENTITY chamber (2):
    arifos://identity          — Sovereign identity manifest and authority chain
    arifos://human/metabolized — Compact sovereign context (nutrient, not food)

  LAW chamber (5):
    arifos://doctrine          — Immutable law (F1–L13)
    arifos://floors            — All 13 constitutional floors (reference list)
    arifos://refusal-surface   — Refusal taxonomy and boundaries
    arifos://jurisdiction      — Autonomy bands and capability grants
    arifos://civilization      — Organs, strata, and constitutional boundaries

  STATE chamber (5):
    arifos://vitals            — Metric reference and thresholds
    arifos://carry-forward     — Cross-turn carry-forward state
    arifos://flow-state        — Pipeline flow state
    arifos://reality/state     — Reality contact state (F1)
    arifos://vault/head        — VAULT999 chain head (live from filesystem)

  MIND chamber (7):
    arifos://epistemic         — Epistemic label ontology (OBS/DER/INT/SPEC)
    arifos://loop-engineering  — 7-stage reality engineering loop (K1 dual naming)
    arifos://schema            — Complete blueprint (tools, lanes, forge bridge)
    arifos://bootstrap         — Full federation knowledge-graph context
    arifos://quickstart        — LLM client getting started guide
    arifos://init/agent_init   — Agent initialization bootstrap
    arifos://memory            — 6-layer memory architecture (L1–L6)

  DEEP chamber (6):
    arifos://atlas333/index        — ATLAS333 root index (cognitive geometry)
    arifos://atlas333/paradox/list — Canonical paradox catalog (36 rows, 35 IDs)
    arifos://atlas333/geometry     — Full cognitive geometry map
    arifos://atlas333/flow         — 10-stage ATLAS333 pipeline
    arifos://wisdom/contract       — Federation contract for wisdom namespace
    arifos://wisdom/quotes/all     — All quotes + doctrine + disputed + prohibited-uses

  DOORS chamber (2):
    tree777://index            — TREE777 wiki index
    skill://index              — Skill registry index

  Plus structural anchors (3):
    arifos://index             — Namespace migration map (6-plane architecture)
    arifos://trinity           — AAA lane definitions and separation of powers
    arifos://affordances       — Tool affordances (action classes, blast radius)

REMOVED 2026-08-08 (48 → 30 — deprecated/redundant registrations):
  arifos://resources/index        — alias of arifos://index, redundant
  arifos://resources/audit        — governance resource, agent-only
  arifos://atlas-repo             — dynamic numbers, agent-only
  arifos://aaa-index              — dynamic numbers, agent-only
  arifos://a-forge-index          — dynamic numbers, agent-only
  arifos://vault999-index         — dynamic numbers, agent-only
  arifos://mcp/surface-map        — duplicate of arifos://schema
  arifos://mcp-alignment          — technical conformance, agent-only
  arifos://seal-readiness         — concept merged into arifos://doctrine
  arifos://atlas333/seal/head     — DEPRECATED alias, use arifos://vault/head
  arifos://atlas333/zones         — merged into atlas333/paradox/list
  arifos://atlas333/organs        — merged into atlas333/paradox/list
  arifos://atlas333/thresholds    — merged into atlas333/paradox/list
  arifos://atlas333/activation/rules — merged into atlas333/paradox/list
  arifos://atlas333/quote/list    — merged into atlas333/paradox/list
  arifos://wisdom/quotes/disputed — merged into wisdom/quotes/all
  arifos://wisdom/quotes/prohibited-uses — merged into wisdom/quotes/all
  arifos://wisdom/quotes/arifos-doctrine — merged into wisdom/quotes/all

REMOVED (chaos reduction, 2026-06-28 and earlier):
  arifos://philosophy — beautiful, not operational. Agents don't load it.
  arifos://forge      — merged into arifos://schema
  source://list       — dynamic data → belongs in arif_fetch tool
  receipt://list      — dynamic data → belongs in arif_fetch tool
  tree777://search    — search → belongs in arif_memory_recall tool

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

# REMOVED 2026-08-08 — dynamic-number index resources, agent-only:
# from .aaa_index import register_aaa_index          # arifos://aaa-index
# from .aforge_index import register_aforge_index    # arifos://a-forge-index
# from .atlas_repo import register_atlas_repo        # arifos://atlas-repo
# from .vault999_index import register_vault999_index  # arifos://vault999-index
from .bootstrap import register_bootstrap
from .civilization import register_civilization
from .doctrine import register_doctrine
from .floor_table import register_floor_template
from .namespace_index import register_namespace_index
from .refusal_surface import register_refusal_surface

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
    # REMOVED 2026-08-08: arifos://seal-readiness provenance
    # (concept merged into arifos://doctrine; resource deregistered)
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
    # REMOVED 2026-08-08: arifos://mcp-alignment provenance
    # (technical conformance — agent-only, deregistered)
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
    # REMOVED 2026-08-08: arifos://mcp/surface-map provenance
    # (duplicate of arifos://schema — deregistered)
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
    # REMOVED 2026-08-08: arifos://atlas333/quote/list provenance
    # (merged into atlas333/paradox/list)
    "arifos://atlas333/quote/{id}": {
        "source": "paradox_quotes_py",
        "truth_level": 3,
        "truth_label": "TRUSTED_REPO",
        "mutability": "version_controlled",
        "staleness": "refresh_on_deploy",
        "evidence_layer": "cognitive_geometry",
    },
    # REMOVED 2026-08-08: provenance for atlas333/zones, atlas333/organs,
    # atlas333/thresholds, atlas333/activation/rules
    # (all merged into atlas333/paradox/list)
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
    # REMOVED 2026-08-08: arifos://atlas333/seal/head provenance
    # (DEPRECATED alias — canonical is arifos://vault/head)
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


from . import alignment_gap  # noqa: F401 — registers provenance-gap resources
from .atlas333 import attach_to_mcp_resource as _atlas333_attach
from .embodied_resources import register_embodied_resources
from .evidence import register_evidence_resources
from .human_context import register_human_context
from .identity import register_identity
from .jurisdiction import register_jurisdiction
from .loop_engineering import register_loop_engineering
from .memory import register_memory
from .quickstart import register_quickstart
from .reality_state import register_reality_state
from .retrieve_tools import register_retrieve_tools
from .runner import register_runner_resources
from .schema import register_schema
from .skills_catalog import register_skills_catalog
from .sovereign import register_sovereign_resources
from .tool_discovery import register_tool_discovery
from .tree777 import register_tree777_resources
from .trinity import register_trinity
from .vault999_template import register_vault999_template
from .vitals import register_vitals
from .wisdom_resources import register_wisdom_resources

# REMOVED 2026-08-08 imports (resources deregistered):
# from .mcp_alignment import register_mcp_alignment   # arifos://mcp-alignment
# from .resources_index import register_resources_index  # arifos://resources/index + /audit
# from .seal_readiness import register_seal_readiness  # arifos://seal-readiness
# from .surface_map import register_surface_map       # arifos://mcp/surface-map

CANONICAL_RESOURCES = (
    # IDENTITY chamber
    "arifos://identity",
    "arifos://human/metabolized",
    # LAW chamber
    "arifos://doctrine",
    "arifos://floors",
    "arifos://refusal-surface",
    "arifos://jurisdiction",
    "arifos://civilization",
    # STATE chamber
    "arifos://vitals",
    "arifos://carry-forward",
    "arifos://flow-state",
    "arifos://reality/state",
    "arifos://vault/head",
    # MIND chamber
    "arifos://epistemic",
    "arifos://loop-engineering",
    "arifos://schema",
    "arifos://bootstrap",
    "arifos://quickstart",
    "arifos://init/agent_init",
    "arifos://memory",
    # DEEP chamber
    "arifos://atlas333/index",
    "arifos://atlas333/paradox/list",
    "arifos://atlas333/geometry",
    "arifos://atlas333/flow",
    "arifos://wisdom/contract",
    "arifos://wisdom/quotes/all",
    # DOORS chamber
    "tree777://index",
    "skill://index",
    # Structural anchors
    "arifos://index",
    "arifos://trinity",
    "arifos://affordances",
)  # REMOVED 2026-08-08 (48 → 30):
#   arifos://resources/index, arifos://resources/audit, arifos://atlas-repo,
#   arifos://aaa-index, arifos://a-forge-index, arifos://vault999-index,
#   arifos://mcp/surface-map, arifos://mcp-alignment, arifos://seal-readiness,
#   arifos://atlas333/seal/head, atlas333/zones, atlas333/organs,
#   atlas333/thresholds, atlas333/activation/rules, atlas333/quote/list,
#   wisdom/quotes/disputed, wisdom/quotes/prohibited-uses, wisdom/quotes/arifos-doctrine

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

    REDUCTION (2026-08-08): 48 → 30 resources. Removed deprecated aliases,
    dynamic-number indices, duplicate surface maps, and merge-target resources.
    See module docstring REMOVED section for the full list.
    """
    registered: list[str] = []
    registered.extend(register_doctrine(mcp))
    registered.extend(register_namespace_index(mcp))
    # REMOVED 2026-08-08 — dynamic-number index resources, agent-only:
    # registered.extend(register_atlas_repo(mcp))      # arifos://atlas-repo
    # registered.extend(register_aaa_index(mcp))       # arifos://aaa-index
    # registered.extend(register_aforge_index(mcp))    # arifos://a-forge-index
    # registered.extend(register_vault999_index(mcp))  # arifos://vault999-index
    registered.extend(register_floor_template(mcp))
    registered.extend(register_refusal_surface(mcp))
    registered.extend(register_trinity(mcp))
    registered.extend(register_schema(mcp))
    registered.extend(register_civilization(mcp))
    # REMOVED 2026-08-08 — arifos://seal-readiness (concept merged into doctrine):
    # registered.extend(register_seal_readiness(mcp))
    registered.extend(register_jurisdiction(mcp))
    registered.extend(register_identity(mcp))
    registered.extend(register_memory(mcp))
    registered.extend(register_vitals(mcp))
    registered.extend(register_bootstrap(mcp))
    registered.extend(register_loop_engineering(mcp))
    registered.extend(register_quickstart(mcp))
    # REMOVED 2026-08-08 — arifos://mcp-alignment (technical conformance, agent-only):
    # registered.extend(register_mcp_alignment(mcp))
    # DISABLED 2026-06-28 — catalog-of-catalog, not domain operational data:
    # registered.extend(register_resources_index(mcp))    # arifos://resources/index + /audit
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
    # REMOVED 2026-08-08 — arifos://mcp/surface-map (duplicate of arifos://schema):
    # registered.extend(register_surface_map(mcp))
    registered.extend(register_wisdom_resources(mcp))
    registered.extend(alignment_gap.register_alignment_gap_resources(mcp))
    if _atlas333_attach:
        registered.extend(_atlas333_attach(mcp))
    return registered
