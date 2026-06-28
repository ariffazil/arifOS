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

from fastmcp import FastMCP

from .bootstrap import register_bootstrap
from .civilization import register_civilization
from .doctrine import register_doctrine
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
from .vault999_template import register_vault999_template

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
    # REMOVED 2026-06-28 (zen of resources — indices to indices):
    #   tree777://index         — wiki index, not domain operational data
    #   runner://policy/v1      — runner policy metadata, not AI operational data
    #   arif://tools/discovery  — consolidated into arifos://tools/self-model
)

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
    registered.extend(register_vault999_template(mcp))
    return registered
