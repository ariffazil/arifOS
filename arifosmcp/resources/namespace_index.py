"""
arifOS Namespace Index — The Migration Map
═══════════════════════════════════════════

A governance artifact that maps every existing resource URI to its proposed
home in the 6-plane architecture. Not a catalog of catalogs — an architect's
map for the namespace migration.

Each entry carries:
  - current_uri     → where the resource lives today
  - proposed_uri    → where it goes under the 6-plane architecture
  - plane           → law | state | surface | identity | method | corpus
  - source_of_truth → canonical file or registry that owns this data
  - duplicate_of    → null | URI of the canonical copy this one duplicates
  - is_derived      → true if generated from SOT (not hand-authored)
  - has_attestation → true if it carries content_hash + generated_at
  - naming_grammar  → which of 6 naming conventions it follows today
  - change_rate     → amendment | per-call | generated | rare | versioned | append-only

Zen (2026-08-07): This IS operational data. Every agent reads it to navigate
the namespace during migration. It is the map — delete nothing, alias second,
deprecate last.

Arif's directive: "Publish the map before the migration. Then you can measure
H before and after and have a receipt for it."

DITEMPA BUKAN DIBERI. Forged by 333-AGI Δ MIND under F13 SOVEREIGN directive.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

# ── 6-PLANE ARCHITECTURE ──────────────────────────────────────────────────
# Plane     Contains                                      Change Rate
# law/      floors, constitution, refusal, jurisdiction   amendment only (F13)
# state/    vitals, flow, carry-forward, vault head       per-call, auto-generated
# surface/  schema, affordances, conformance              generated, never authored
# identity/ sovereign, actor registry, attestation        rare
# method/   loop, init, bootstrap, trinity, quickstart    versioned
# corpus/   wisdom, ATLAS333, tree777, memory, ontology   append-only
# ───────────────────────────────────────────────────────────────────────────

# ── CACHE POLICY (§16 — derived from MCP spec ttlMs / cacheScope) ──
# Every resource SHOULD declare caching hints. The protocol gives us
# ttlMs (freshness) and cacheScope (public/private). change_rate is
# the geometric primitive — cache policy is the derived field.
CACHE_POLICY: dict[str, dict[str, Any]] = {
    "amendment": {
        "ttl_ms": 86400000,
        "cache_scope": "public",
        "rationale": "24h — constitutions don't change mid-session",
    },
    "per-call": {
        "ttl_ms": 0,
        "cache_scope": "private",
        "rationale": "no cache — state changes every call",
    },
    "generated": {
        "ttl_ms": 300000,
        "cache_scope": "public",
        "rationale": "5min — regenerated on source change, can stale",
    },
    "rare": {
        "ttl_ms": 86400000,
        "cache_scope": "private",
        "rationale": "24h — sovereign identity, not public",
    },
    "versioned": {
        "ttl_ms": 3600000,
        "cache_scope": "public",
        "rationale": "1h — version bumps are deliberate",
    },
    "append-only": {
        "ttl_ms": 3600000,
        "cache_scope": "public",
        "rationale": "1h — new entries appended, existing stable",
    },
}

# ── PRIORITY POLICY (§1 annotations.priority) ──
# The spec ranks primitives: tools bend geometry most (model-controlled),
# then prompts (user-framed), then resources (passive, volumetric).
# Resources without annotations.priority give no signal for selective
# context injection — everything or nothing. Priority hints enable
# clients to inject high-value resources and drop low-value ones.
# Derived from plane (the geometric primitive). 0/42 arifOS resources
# currently carry priority annotations — the index fills this gap.
PRIORITY_POLICY: dict[str, float] = {
    "law": 0.9,  # constitutional — highest signal per token
    "identity": 0.8,  # sovereign authority — shapes all downstream routing
    "method": 0.7,  # operational — needed for correct execution
    "surface": 0.5,  # generated metadata — useful but derivable
    "corpus": 0.4,  # reference — context-heavy, rarely needed in full
    "state": 0.3,  # volatile — stale on arrival, poll only when needed
}

INDEX_ENTRIES: list[dict[str, Any]] = [
    # ═══ law/ — amendment only, F13 ack ═══
    {
        "current_uri": "arifos://doctrine",
        "proposed_uri": "arifos://law/constitution",
        "plane": "law",
        "source_of_truth": "/root/arifOS/GENESIS/FLOOR_TABLE.json",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "amendment",
        "note": "THE canonical constitution. Single source of truth for all 13 floors.",
    },
    {
        "current_uri": "arifos://floors",
        "proposed_uri": "arifos://law/floors",
        "plane": "law",
        "source_of_truth": "/root/arifOS/GENESIS/FLOOR_TABLE.json",
        "duplicate_of": "arifos://law/constitution",
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "suffix_typed",
        "change_rate": "amendment",
        "note": "Derived list view. Changes when doctrine changes — non-orthogonal.",
    },
    {
        "current_uri": "arifos://refusal-surface",
        "proposed_uri": "arifos://law/refusal",
        "plane": "law",
        "source_of_truth": "/root/arifOS/arifosmcp/resources/refusal_surface.py",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "kebab_noun",
        "change_rate": "amendment",
        "note": "Negative space of the constitution — what the kernel refuses.",
    },
    {
        "current_uri": "arifos://jurisdiction",
        "proposed_uri": "arifos://law/jurisdiction",
        "plane": "law",
        "source_of_truth": "/root/AAA/governance/AGENCY_LEVELS.md",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "amendment",
        "note": "Autonomy bands, capability grants, jurisdiction rules.",
    },
    {
        "current_uri": "arifos://epistemic",
        "proposed_uri": "arifos://law/epistemic",
        "plane": "law",
        "source_of_truth": "/root/arifOS/GENESIS/000_KERNEL_CANON.md §4",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "suffix_typed",
        "change_rate": "amendment",
        "note": "OBS/DER/INT/SPEC label ontology + provenance rules.",
    },
    {
        "current_uri": "arifos://atlas333/thresholds",
        "proposed_uri": "arifos://law/thresholds",
        "plane": "law",
        "source_of_truth": "arifos://atlas333 — TEARFRAME constants",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "amendment",
        "note": "TRM≥0.94, ECHO≥0.87, RASA≥0.85 — constitutional tuning parameters.",
    },
    {
        "current_uri": "arifos://atlas333/activation/rules",
        "proposed_uri": "arifos://law/activation-rules",
        "plane": "law",
        "source_of_truth": "ATLAS333 GPV→paradox activation matrix",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "amendment",
        "note": "8 canonical GPV activation patterns. Tuning, not operational.",
    },
    # ═══ state/ — per-call, never hand-edited ═══
    {
        "current_uri": "arifos://vitals",
        "proposed_uri": "arifos://state/vitals",
        "plane": "state",
        "source_of_truth": "live telemetry (:8088/health → thermodynamic)",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "verb_prefixed",
        "change_rate": "per-call",
        "note": "Real-time CPU, memory, G, ΔS, Ω, Ψ. Updated continuously.",
    },
    {
        "current_uri": "arifos://flow-state",
        "proposed_uri": "arifos://state/flow",
        "plane": "state",
        "source_of_truth": "arifFlow :7073/health → .fq",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "verb_prefixed",
        "change_rate": "per-call",
        "note": "FQ pulse — FQ<0.5 → ALL agents HOLD. Cache TTL 15 min.",
    },
    {
        "current_uri": "arifos://carry-forward",
        "proposed_uri": "arifos://state/carry-forward",
        "plane": "state",
        "source_of_truth": "/root/.local/share/arifos/carry_forward.json",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "verb_prefixed",
        "change_rate": "per-call",
        "note": "Session continuity — prior session ID, open loops, completed tasks.",
    },
    {
        "current_uri": "arifos://reality/state",
        "proposed_uri": "arifos://state/reality",
        "plane": "state",
        "source_of_truth": "multi-layer snapshot (PHYSICAL/DIGITAL/BIOLOGICAL/UNCERTAINTY)",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "per-call",
        "note": "Causally-consistent reality snapshot. Every value carries epistemic label.",
    },
    {
        "current_uri": "arifos://vault/head",
        "proposed_uri": "arifos://state/vault-head",
        "plane": "state",
        "source_of_truth": "/root/arifOS/VAULT999/outcomes.jsonl",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "per-call",
        "note": "CANONICAL vault chain head. Live from filesystem, not cached.",
    },
    {
        "current_uri": "arifos://atlas333/seal/head",
        "proposed_uri": "arifos://state/vault-head",
        "plane": "state",
        "source_of_truth": "/root/arifOS/VAULT999/outcomes.jsonl",
        "duplicate_of": "arifos://vault/head",
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "per-call",
        "note": "DUPLICATE. Same data as vault/head, ATLAS333-cached. Wrong namespace.",
    },
    {
        "current_uri": "arifos://seal-readiness",
        "proposed_uri": "arifos://state/seal-readiness",
        "plane": "state",
        "source_of_truth": "VAULT999 integrity report + seal gate logic",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "kebab_noun",
        "change_rate": "per-call",
        "note": "Vault integrity + seal gate requirements. NOTE: partially overlaps with vault/head.",
    },
    # ═══ surface/ — generated, never authored ═══
    {
        "current_uri": "arifos://schema",
        "proposed_uri": "arifos://surface/schema",
        "plane": "surface",
        "source_of_truth": "abi/capability_registry.json",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "generated",
        "note": "Complete MCP surface blueprint — tools, floors, separation of powers.",
    },
    {
        "current_uri": "arifos://affordances",
        "proposed_uri": "arifos://surface/affordances",
        "plane": "surface",
        "source_of_truth": "tool manifests → action classes, blast radius, reversibility",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "suffix_typed",
        "change_rate": "generated",
        "note": "Action classes, blast radius, reversibility per tool.",
    },
    {
        "current_uri": "arifos://mcp/surface-map",
        "proposed_uri": "arifos://surface/map",
        "plane": "surface",
        "source_of_truth": "live introspection → tools/resources/rules map",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "generated",
        "note": "Canonical agent surface map (tools, resources, rules).",
    },
    {
        "current_uri": "arifos://mcp-alignment",
        "proposed_uri": "arifos://surface/conformance",
        "plane": "surface",
        "source_of_truth": "MCP 2025-11-25 spec vs live surface",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "kebab_noun",
        "change_rate": "generated",
        "note": "MCP spec conformance matrix — protocol, extensions, deprecations.",
    },
    # ═══ identity/ — rare ═══
    {
        "current_uri": "arifos://identity",
        "proposed_uri": "arifos://identity/manifest",
        "plane": "identity",
        "source_of_truth": "/root/arifOS/identity.toml",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "rare",
        "note": "Sovereign identity manifest — authority chain from Arif through kernel.",
    },
    {
        "current_uri": "arifos://human/metabolized",
        "proposed_uri": "arifos://identity/sovereign",
        "plane": "identity",
        "source_of_truth": "/root/arifOS/scar-terrain-arif-fazil.md",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "rare",
        "note": "Compacted sovereign context — the nutrient, not the food.",
    },
    # ═══ method/ — versioned ═══
    {
        "current_uri": "arifos://loop-engineering",
        "proposed_uri": "arifos://method/loop",
        "plane": "method",
        "source_of_truth": "/root/AAA/docs/EUREKA_SIX_PLANE_EXECUTION_LOOP.md",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "kebab_noun",
        "change_rate": "versioned",
        "note": "7-stage reality engineering loop — the operating system of the federation.",
    },
    {
        "current_uri": "arifos://trinity",
        "proposed_uri": "arifos://method/trinity",
        "plane": "method",
        "source_of_truth": "/root/AAA/prompts/INIT.md §Trinity",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "versioned",
        "note": "AAA Trinity lane architecture — 333-AGI, 555-ASI, 888-APEX.",
    },
    {
        "current_uri": "arifos://init/agent_init",
        "proposed_uri": "arifos://method/init",
        "plane": "method",
        "source_of_truth": "/root/AAA/prompts/INIT.md",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "versioned",
        "note": "Canonical agent ignition sequence. SUPERSEDES bootstrap for session bind.",
    },
    {
        "current_uri": "arifos://bootstrap",
        "proposed_uri": "arifos://method/bootstrap",
        "plane": "method",
        "source_of_truth": "aggregated from doctrine + trinity + schema + civilization + memory + identity",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "versioned",
        "note": "Full federation knowledge-graph context. AGGREGATOR — change any SOT, this must change. Non-orthogonal by design.",
    },
    {
        "current_uri": "arifos://quickstart",
        "proposed_uri": "arifos://method/quickstart",
        "plane": "method",
        "source_of_truth": "/root/arifOS/arifosmcp/resources/quickstart.py",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "versioned",
        "note": "LLM client getting started guide. OVERLAPS with instructions.",
    },
    {
        "current_uri": "arifos://instructions",
        "proposed_uri": "arifos://method/instructions",
        "plane": "method",
        "source_of_truth": "/root/arifOS/arifosmcp/runtime/fastmcp_ext/resources.py",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "verb_prefixed",
        "change_rate": "versioned",
        "note": "Agent bootstrap instructions. OVERLAPS with quickstart and init.",
    },
    {
        "current_uri": "skill://index",
        "proposed_uri": "arifos://method/skills",
        "plane": "method",
        "source_of_truth": "/root/AAA/skills/FEDERATION_SKILL_PROFILE.json",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "versioned",
        "note": "Federation skill index — 107+ skills. skill://{name}/SKILL.md for details.",
    },
    # ═══ corpus/ — append-only ═══
    {
        "current_uri": "arifos://civilization",
        "proposed_uri": "arifos://corpus/civilization",
        "plane": "corpus",
        "source_of_truth": "/root/AAA/docs/ORGAN.md + organ.yaml",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "append-only",
        "note": "Organ topology, intelligence strata, constitutional boundaries. STATEMENT OF ONTOLOGY — should be index with provenance_source, not static assertion (F2 gate).",
    },
    {
        "current_uri": "arifos://memory",
        "proposed_uri": "arifos://corpus/memory",
        "plane": "corpus",
        "source_of_truth": "/root/arifOS/GENESIS/000_KERNEL_CANON.md §Memory",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "append-only",
        "note": "L1–L6 memory architecture. Memory≠truth, truth≠final until sealed.",
    },
    {
        "current_uri": "arifos://atlas333/index",
        "proposed_uri": "arifos://corpus/atlas333/index",
        "plane": "corpus",
        "source_of_truth": "/root/arifOS/arifosmcp/resources/atlas333.py",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "snake_case",
        "change_rate": "append-only",
        "note": "ATLAS333 root index — 33 paradoxes, 7 zones, cognitive geometry.",
    },
    {
        "current_uri": "arifos://atlas333/paradox/list",
        "proposed_uri": "arifos://corpus/atlas333/paradoxes",
        "plane": "corpus",
        "source_of_truth": "ATLAS333 paradox registry",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "All 33 paradoxes with axes, zones, organs.",
    },
    {
        "current_uri": "arifos://atlas333/quote/list",
        "proposed_uri": "arifos://corpus/atlas333/quotes",
        "plane": "corpus",
        "source_of_truth": "ATLAS333 quote registry",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "All 36 quotes with trigger metadata.",
    },
    {
        "current_uri": "arifos://atlas333/zones",
        "proposed_uri": "arifos://corpus/atlas333/zones",
        "plane": "corpus",
        "source_of_truth": "ATLAS333 zone definitions",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "append-only",
        "note": "7 paradox zones with paradox ranges.",
    },
    {
        "current_uri": "arifos://atlas333/organs",
        "proposed_uri": "arifos://corpus/atlas333/organs",
        "plane": "corpus",
        "source_of_truth": "ATLAS333 quote organ definitions",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "append-only",
        "note": "4 quote organs (Memory/Mind/Judge/Contour). CONFUSING NAME — not federation organs.",
    },
    {
        "current_uri": "arifos://atlas333/flow",
        "proposed_uri": "arifos://corpus/atlas333/flow",
        "plane": "corpus",
        "source_of_truth": "ATLAS333 10-stage pipeline definition",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "append-only",
        "note": "10-stage ATLAS333 intelligence pipeline (INGEST→SEAL).",
    },
    {
        "current_uri": "arifos://atlas333/geometry",
        "proposed_uri": "arifos://corpus/atlas333/geometry",
        "plane": "corpus",
        "source_of_truth": "ATLAS333 cognitive geometry map",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "bare_noun",
        "change_rate": "append-only",
        "note": "Full cognitive geometry — territories × geometries × depths.",
    },
    {
        "current_uri": "arifos://wisdom/contract",
        "proposed_uri": "arifos://corpus/wisdom/contract",
        "plane": "corpus",
        "source_of_truth": "wisdom namespace contract",
        "duplicate_of": None,
        "is_derived": False,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "Federation contract for the wisdom/quote namespace — 7 APEX organs, G formula.",
    },
    {
        "current_uri": "arifos://wisdom/quotes/all",
        "proposed_uri": "arifos://corpus/wisdom/quotes",
        "plane": "corpus",
        "source_of_truth": "canonical quote registry",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "All quotes with provenance metadata. 5 wisdom resources → 1 index + sub-views.",
    },
    {
        "current_uri": "arifos://wisdom/quotes/disputed",
        "proposed_uri": "arifos://corpus/wisdom/quotes?filter=disputed",
        "plane": "corpus",
        "source_of_truth": "canonical quote registry (filtered view)",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "Filtered view — consider making this a query param on the canonical endpoint.",
    },
    {
        "current_uri": "arifos://wisdom/quotes/arifos-doctrine",
        "proposed_uri": "arifos://corpus/wisdom/quotes?filter=doctrine",
        "plane": "corpus",
        "source_of_truth": "canonical quote registry (filtered view)",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "arifOS doctrine entries separated from inherited quotations.",
    },
    {
        "current_uri": "arifos://wisdom/quotes/prohibited-uses",
        "proposed_uri": "arifos://corpus/wisdom/prohibited-uses",
        "plane": "corpus",
        "source_of_truth": "wisdom namespace contract §prohibited",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "Prohibited use patterns for quotations. Could be part of wisdom/contract.",
    },
    {
        "current_uri": "tree777://index",
        "proposed_uri": "arifos://corpus/tree777",
        "plane": "corpus",
        "source_of_truth": "/root/A-FORGE? tree777 wiki files",
        "duplicate_of": None,
        "is_derived": True,
        "has_attestation": False,
        "naming_grammar": "nested_path",
        "change_rate": "append-only",
        "note": "TREE777 wiki index — skills by category, concepts, scars.",
    },
]


def build_index() -> str:
    """Assemble the full namespace index with entropy metrics."""
    import math

    total = len(INDEX_ENTRIES)

    # ── ENTROPY METRICS ──
    # Redundancy
    duplicates = [e for e in INDEX_ENTRIES if e["duplicate_of"] is not None]
    duplicate_clusters = set(e["duplicate_of"] for e in duplicates if e["duplicate_of"])
    redundant_uri_count = len(duplicates)
    unique_subjects = total - redundant_uri_count + len(duplicate_clusters)
    redundancy = round(1.0 - (unique_subjects / total), 3)

    # Grammar variance
    grammar_counts: dict[str, int] = {}
    for e in INDEX_ENTRIES:
        g = e["naming_grammar"]
        grammar_counts[g] = grammar_counts.get(g, 0) + 1
    num_grammars = len(grammar_counts)
    uniform = total / num_grammars
    variance = sum((c - uniform) ** 2 for c in grammar_counts.values()) / num_grammars
    grammar_variance = round(math.sqrt(variance) / uniform, 3) if uniform > 0 else 0.0

    # Orphan rate
    orphans = [e for e in INDEX_ENTRIES if e.get("_estimated_orphan")]
    orphan_rate = round(len(orphans) / total, 3) if total > 0 else 0.0

    # Composite H
    H = round((redundancy * 0.35 + grammar_variance * 0.25 + orphan_rate * 0.20) / 0.80, 3)

    # ── INJECT CACHE POLICY + PRIORITY (§16 + §1 — derived from change_rate / plane) ──
    enriched_entries = []
    for e in INDEX_ENTRIES:
        enriched = dict(e)
        policy = CACHE_POLICY.get(e["change_rate"], CACHE_POLICY["versioned"])
        enriched["ttl_ms"] = policy["ttl_ms"]
        enriched["cache_scope"] = policy["cache_scope"]
        enriched["priority"] = PRIORITY_POLICY.get(e["plane"], 0.5)
        enriched_entries.append(enriched)

    # Plane distribution
    plane_dist: dict[str, int] = {}
    for e in INDEX_ENTRIES:
        p = e["plane"]
        plane_dist[p] = plane_dist.get(p, 0) + 1

    # ── ATTESTATION (Tension 2 resolution — MCP spec gap) ──
    # Hash the STABLE content (42 entries + architecture + migration rules,
    # excluding dynamic timestamps). This proves the index hasn't drifted.
    stable_content = json.dumps(
        {
            "resources": enriched_entries,
            "architecture_planes": sorted(plane_dist.keys()),
            "migration_rules": [
                "1. Delete nothing.",
                "2. Publish this index (DONE — this is it).",
                "3. Add aliases at proposed URIs (redirect or content-negotiate).",
                "4. Update tools and agents to use proposed URIs.",
                "5. Deprecate old URIs (keep serving, add deprecation header).",
                "6. Remove old URIs only when zero callers remain (90-day window).",
            ],
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    content_hash = hashlib.sha256(stable_content.encode()).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    result = {
        "_meta": {
            "resource": "arifos://index",
            "title": "arifOS Namespace Index — The Migration Map",
            "description": "Maps every existing resource URI to its proposed home in the 6-plane architecture. Delete nothing, alias second, deprecate last.",
            "forged": "2026-08-07T22:57Z",
            "forged_by": "333-AGI Δ MIND",
            "directive": "F13 SOVEREIGN — Arif bin Fazil",
            "doctrine": "DITEMPA BUKAN DIBERI",
            "total_resources": total,
            "content_hash": content_hash,
            "generated_at": generated_at,
            "generator": "arifOS/arifosmcp/resources/namespace_index.py::build_index",
            "is_derived": False,
            "annotations": {
                "audience": ["assistant"],
                "priority": 1.0,
                "lastModified": generated_at,
                "cacheScope": "public",
                "ttlMsHint": 3600000,
            },
        },
        "entropy": {
            "H": H,
            "redundancy": redundancy,
            "redundancy_note": f"{redundant_uri_count} URIs in {len(duplicate_clusters)} duplicate clusters",
            "grammar_variance": grammar_variance,
            "grammar_variance_note": f"{num_grammars} naming conventions across {total} resources",
            "orphan_rate": orphan_rate,
            "staleness": "UNMEASURED — requires content_hash attestation",
            "target_after_migration": "< 0.15",
        },
        "architecture": {
            "planes": {
                "law": {
                    "resources": plane_dist.get("law", 0),
                    "change_rate": "amendment only (F13 ack)",
                    "description": "Constitution, floors, refusal, jurisdiction, thresholds",
                },
                "state": {
                    "resources": plane_dist.get("state", 0),
                    "change_rate": "per-call, auto-generated",
                    "description": "Vitals, flow, carry-forward, vault head, reality",
                },
                "surface": {
                    "resources": plane_dist.get("surface", 0),
                    "change_rate": "generated, never authored",
                    "description": "Schema, affordances, conformance, surface map",
                },
                "identity": {
                    "resources": plane_dist.get("identity", 0),
                    "change_rate": "rare",
                    "description": "Sovereign manifest, actor registry, attestation",
                },
                "method": {
                    "resources": plane_dist.get("method", 0),
                    "change_rate": "versioned",
                    "description": "Loop, init, bootstrap, trinity, quickstart, skills",
                },
                "corpus": {
                    "resources": plane_dist.get("corpus", 0),
                    "change_rate": "append-only",
                    "description": "Wisdom, ATLAS333, tree777, memory, civilization",
                },
            },
            "orthogonality_rule": "Planes separated by change rate. Nothing per-call sits next to something per-amendment.",
            "fractal_rule": "Every plane: index · subject · subject/attestation. Learn one, navigate all.",
            "caching": {
                "description": "MCP §16 — every resource SHOULD declare ttlMs + cacheScope. Derived from change_rate (the geometric primitive).",
                "policy": {
                    "amendment": CACHE_POLICY["amendment"],
                    "per-call": CACHE_POLICY["per-call"],
                    "generated": CACHE_POLICY["generated"],
                    "rare": CACHE_POLICY["rare"],
                    "versioned": CACHE_POLICY["versioned"],
                    "append-only": CACHE_POLICY["append-only"],
                },
                "progressive_discovery": "Load arifos://index (ttl=1h, public). Navigate plane. Read only needed resources. Cache per policy above.",
                "subscription_hint": "Subscribe to resources/listChanged for plane-level awareness. Per-resource subscriptions for state/ resources (per-call, no cache).",
            },
            "priority": {
                "description": "MCP §1 annotations.priority — 0/42 arifOS resources carry it. Index fills the gap. Derived from plane (the geometric primitive). Enables selective context injection — clients inject high-priority resources, drop low-priority ones.",
                "policy": {
                    "law": {
                        "priority": PRIORITY_POLICY["law"],
                        "rationale": "Constitutional — highest signal per token",
                    },
                    "identity": {
                        "priority": PRIORITY_POLICY["identity"],
                        "rationale": "Sovereign authority — shapes all downstream routing",
                    },
                    "method": {
                        "priority": PRIORITY_POLICY["method"],
                        "rationale": "Operational instructions — needed for correct execution",
                    },
                    "surface": {
                        "priority": PRIORITY_POLICY["surface"],
                        "rationale": "Generated metadata — useful but derivable",
                    },
                    "corpus": {
                        "priority": PRIORITY_POLICY["corpus"],
                        "rationale": "Reference material — context-heavy, rarely needed in full",
                    },
                    "state": {
                        "priority": PRIORITY_POLICY["state"],
                        "rationale": "Volatile telemetry — stale on arrival, poll only when needed",
                    },
                },
            },
        },
        "attestation_gap": {
            "resources_with_attestation": sum(1 for e in INDEX_ENTRIES if e["has_attestation"]),
            "resources_without_attestation": sum(
                1 for e in INDEX_ENTRIES if not e["has_attestation"]
            ),
            "required_fields": [
                "content_hash",
                "generated_at",
                "generator",
                "source_of_truth",
                "is_derived",
            ],
            "note": "0 of {total} resources carry attestation. The vault-count contradiction is structurally possible because derived resources don't carry their generator hash. Adding attestation makes the contradiction structurally impossible.",
        },
        "priority_gap": {
            "resources_with_priority": 1,
            "resources_without_priority": total - 1,
            "note": "Only arifos://index carries annotations.priority. The other 42 resources have no signal for selective context injection — MCP clients must inject everything or nothing. Index fills this gap via PRIORITY_POLICY per entry.",
        },
        "migration_rules": [
            "1. Delete nothing.",
            "2. Publish this index (DONE — this is it).",
            "3. Add aliases at proposed URIs (redirect or content-negotiate).",
            "4. Update tools and agents to use proposed URIs.",
            "5. Deprecate old URIs (keep serving, add deprecation header).",
            "6. Remove old URIs only when zero callers remain (90-day window).",
        ],
        "resources": enriched_entries,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def register_namespace_index(mcp: FastMCP) -> list[str]:
    """Register arifos://index — the namespace migration map.

    DIFFERENT FROM THE OLD resources/index (disabled 2026-06-28):
    The old index was a catalog-of-catalog — metadata about metadata.
    This index IS operational data: every agent reads it to navigate
    the namespace during migration. It carries entropy metrics and
    the 6-plane architecture map.

    NOT a Zen violation — this is governance data, not a mirror.
    """

    @mcp.resource(
        "arifos://index",
        name="arifOS Namespace Index",
        mime_type="application/json",
        description="Migration map: 42 resources → 6-plane architecture. Entropy H=0.26. Every entry carries current_uri, proposed_uri, plane, source_of_truth, duplicate_of, attestation gap. Rule: delete nothing, alias second, deprecate last.",
    )
    def namespace_index() -> str:
        """arifOS Namespace Index — complete migration map with entropy metrics.

        Maps all 42 existing resource URIs to their proposed homes in the
        6-plane architecture (law/state/surface/identity/method/corpus).
        Every entry carries: current_uri, proposed_uri, plane, source_of_truth,
        duplicate_of, is_derived, has_attestation, naming_grammar, change_rate.

        This is an architect's map, not a catalog of catalogs.

        Migrate rule: delete nothing, alias second, deprecate last.
        """
        return build_index()

    # ── ALIAS (Tension 1 resolution — handler-level aliasing) ──
    # MCP spec has no redirect primitive. This is the least-wrong pattern:
    # one handler, two URIs. Single source of truth, no content duplication.
    # The old arifos://resources/index was disabled 2026-06-28 as
    # "catalog-of-catalog" — resurrected as an alias for the migration map.
    @mcp.resource(
        "arifos://resources/index",
        name="arifOS Namespace Index (alias)",
        mime_type="application/json",
        description="ALIAS for arifos://index — the namespace migration map. Same handler, same content, different URI. MCP spec has no redirect; handler-level aliasing is the least-wrong pattern.",
    )
    def namespace_index_alias() -> str:
        """ALIAS: arifos://index → arifos://resources/index."""
        return build_index()

    return ["arifos://index", "arifos://resources/index"]
