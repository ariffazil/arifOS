"""
arifOS AAA Index — The Cognitive Federation Map
═══════════════════════════════════════════════

Maps the AAA cognitive federation layer into the 6-plane architecture.
Same methodology as arifos://index (resources) and arifos://atlas-repo
(directories) — applied to the mind layer's primitives: identities,
agent cards, skills, peer contracts, federation contracts, and routes.

The fractal:
  arifOS     = Law    (constitutional topology)  → arifos://index
  AAA        = Mind   (cognitive topology)       → arifos://aaa-index
  A-FORGE    = Hands  (capability topology)      → (future: a-forge index)
  VAULT999   = Witness (evidentiary topology)    → (future: vault index)

Entropy baseline:
  57 agent-card.json files across 4+ locations
  23 identity.json files across 5+ locations
  229+ SKILL.md files across 6 trees
  18 skill registry files serving overlapping purposes
  4 copies of 333/555/888 Trinity identities

The disease: copies instead of pointers. The cure: publish the map,
alias second, deprecate last.

DITEMPA BUKAN DIBERI. Forged by 333-AGI Δ MIND.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

# ── ENTROPY BASELINE ──
AAA_STATS: dict[str, Any] = {
    "agent_cards_total": 57,
    "identity_files": 23,
    "skill_files": 229,
    "skill_trees": 6,
    "skill_registry_files": 18,
    "trinity_copies": 4,
    "a2a_peer_contracts": 9,
    "registry_files": 47,
}

# ── CRITICAL FINDINGS ──
CRITICAL_FINDINGS = [
    {
        "id": "CF-AAA-01",
        "title": "333/555/888 Trinity identities duplicated 4×",
        "planes": ["identity"],
        "severity": "CRITICAL",
        "description": "Each Trinity identity (333-AGI, 555-ASI, 888-APEX) appears in 4 locations: top-level .json symlinks, agent-cards/identity/, agents/ workspace, and agents/_lanes/ (full copy). The A2A runtime adds a 5th copy at a2a-server/agent-cards/identity/.",
        "locations": [
            "/root/AAA/{333,555,888}-AGI.json (top-level)",
            "/root/AAA/agent-cards/identity/{333-AGI,555-ASI,888-APEX}/agent-card.json (canonical)",
            "/root/AAA/agents/{333-AGI,555-ASI,888-APEX}/identity.json (workspace)",
            "/root/AAA/agents/_lanes/{333-AGI,555-ASI,888-APEX}/identity.json (full copy)",
            "/root/AAA/a2a-server/agent-cards/identity/{333-AGI,555-ASI,888-APEX}.json (runtime)",
        ],
        "remediation": "agent-cards/identity/ is canonical. Top-level symlinks → pointer. _lanes/ → delete (archive first). agents/*/identity.json → derive from canonical.",
        "paradox": "P02-remember-forget — which copy is truth",
        "paradox_zone": "memory",
    },
    {
        "id": "CF-AAA-02",
        "title": "Three independent agent-card registries",
        "planes": ["cards"],
        "severity": "HIGH",
        "description": "Agent cards live in 3 separate registries: agent-cards/ (14 files, canonical), a2a-server/agent-cards/ (32 files, runtime distribution), and a2a/agent-cards/ (2 files). The A2A runtime has its own full copy of identity, organs, forge, functions, harnesses, extensions, and roles directories.",
        "remediation": "agent-cards/ is canonical source-of-truth. a2a-server/ should read from canonical at boot, not maintain copies. a2a/agent-cards/ → merge.",
        "paradox": "P09-layer-collapse — runtime mirrors canon",
        "paradox_zone": "mind",
    },
    {
        "id": "CF-AAA-03",
        "title": "229+ skills across 6 trees with 18 registry files",
        "planes": ["skills"],
        "severity": "CRITICAL",
        "description": "Skills live in 6 trees: skills/ (119, canonical), wiki/skills/ (53, legacy), registries/antigravity/skills/ (36, platform), federation/claude/skills/ (13, adapter), federation/gemini/plugins/arifos/skills/ (8, adapter), agents/_lanes/555-ASI/skills/. Plus 18 registry files (YAML/JSON) attempting to index them.",
        "remediation": "skills/ is canonical source tree. wiki/skills/ → archive. Platform adapters → thin wrappers referencing canonical. Single FEDERATION_SKILL_PROFILE.json as canonical registry; deprecate duplicates after audit.",
        "paradox": "P08-tradition-innovation — legacy skills vs canonical",
        "paradox_zone": "memory",
    },
    {
        "id": "CF-AAA-04",
        "title": "Federation contracts scattered across 4+ directories",
        "planes": ["contracts"],
        "severity": "HIGH",
        "description": "Contracts live in 4 places: contracts/ (54 entries, primary), federation/contracts/ (2), asi/contracts/ (7), and a2a/peer-contracts/ (9 peer-specific). Plus contracts/_specs-draft/ mirrors contracts/ with subdirectories: org/, governance/, cockpit/, federation/, workflows/, goals/, init/, hosts/, decisions/.",
        "remediation": "contracts/ = canonical. a2a/peer-contracts/ → merge. _specs-draft/ → archive (specs that became contracts should reference their canonical form).",
        "paradox": "P19-story-structure — contract shape vs enactment",
        "paradox_zone": "contour",
    },
    {
        "id": "CF-AAA-05",
        "title": "47 registry files at registries/ — multiple overlapping taxonomies",
        "planes": ["routes"],
        "severity": "MEDIUM",
        "description": "registries/ contains 47 files: skills.yaml, tools.yaml, domains.yaml, agents.yaml, AGENTS_UNIFIED.yaml, FEDERATION_MODEL.json, CAPABILITY_INDEX.json, ROUTE_REGISTRY.json, PORT_REGISTRY.json, plus bindings, bundles, catalogs, missions, servers, hosts, workflows, forge_instruments, integrations. Several of these overlap in scope (agents vs AGENTS_UNIFIED vs AAA_AGENTS_REGISTRY).",
        "remediation": "Consolidate into a single registry scheme with clear ownership: identity registry (who), capability registry (what), route registry (how). Deprecate overlapping files.",
        "paradox": "P04-evidence-claim — registry as claim vs registry as truth",
        "paradox_zone": "contour",
    },
]

# ── 6-PLANE MAPPING (AAA layer) ──
PLANE_MAP = [
    # ═══ identity/ — sovereign agent identity ═══
    {
        "plane": "identity",
        "name": "Agent Identity Plane",
        "canonical_home": "agent-cards/identity/",
        "primitives": ["333-AGI", "555-ASI", "888-APEX", "sovereign", "AAA Gateway identity"],
        "current_locations": [
            "agent-cards/identity/{333-AGI,555-ASI,888-APEX}/** (CANONICAL)",
            "agent-cards/pillars/sovereign/**",
            "agents/{333-AGI,555-ASI,888-APEX}/identity.json (workspace copy)",
            "agents/_lanes/{333-AGI,555-ASI,888-APEX}/ (FULL DUPLICATE)",
        ],
        "files": 23,
        "entropy": "DUPLICATED_4X",
        "paradox": "P02-remember-forget — which copy is truth",
        "paradox_zone": "memory",
    },
    # ═══ cards/ — canonical agent cards ═══
    {
        "plane": "cards",
        "name": "Agent Card Plane",
        "canonical_home": "agent-cards/",
        "primitives": [
            "agent-card.json",
            "identity cards",
            "organ cards",
            "pillar cards",
            "extension cards",
            "function cards",
        ],
        "current_locations": [
            "agent-cards/ (CANONICAL — 14 files)",
            "a2a-server/agent-cards/ (RUNTIME COPY — 32 files)",
            "a2a/agent-cards/ (2 files)",
            "agents/*/agent-card.json (per-agent workspace)",
        ],
        "files": 57,
        "entropy": "DUPLICATED_3X",
        "paradox": "P20-name-shape — card name vs runtime identity",
        "paradox_zone": "contour",
    },
    # ═══ skills/ — agent capability surface ═══
    {
        "plane": "skills",
        "name": "Agent Skill Plane",
        "canonical_home": "skills/",
        "primitives": ["SKILL.md", "skill profiles", "skill-manifest", "skill-trust-status"],
        "current_locations": [
            "skills/ (CANONICAL — 119 skills)",
            "wiki/skills/ (LEGACY — 53 skills)",
            "registries/antigravity/skills/ (PLATFORM — 36 skills)",
            "federation/claude/skills/ (ADAPTER — 13 skills)",
            "federation/gemini/plugins/arifos/skills/ (ADAPTER — 8 skills)",
        ],
        "files": 229,
        "entropy": "SCATTERED_6_TREES",
        "paradox": "P08-tradition-innovation — legacy skills vs canonical",
        "paradox_zone": "memory",
    },
    # ═══ peers/ — A2A peer contracts ═══
    {
        "plane": "peers",
        "name": "A2A Peer Contract Plane",
        "canonical_home": "a2a/peer-contracts/",
        "primitives": ["peer-contract.json", "agent-discovery", "mesh-topology", "policies"],
        "current_locations": [
            "a2a/peer-contracts/ (CANONICAL — 9 files)",
            "a2a/policies/ (3 files — auth, skills-exposure, allowed-peers)",
            "a2a/registry/agents.yaml",
            "asi/contracts/ (7 files — dispatch, falsification, explorer)",
        ],
        "files": 22,
        "entropy": "SCATTERED",
        "paradox": "P22-unity-diversity — one federation, many peer contracts",
        "paradox_zone": "contour",
    },
    # ═══ contracts/ — federation contracts ═══
    {
        "plane": "contracts",
        "name": "Federation Contract Plane",
        "canonical_home": "contracts/",
        "primitives": [
            "federation-contract",
            "governance-gates",
            "tool-manifest",
            "workflow-contract",
        ],
        "current_locations": [
            "contracts/ (PRIMARY — 54 entries)",
            "federation/contracts/ (2 files)",
            "contracts/_specs-draft/ (MIRRORS contracts/ structure)",
        ],
        "files": 56,
        "entropy": "SCATTERED_WITH_MIRROR",
        "paradox": "P19-story-structure — contract shape vs enactment",
        "paradox_zone": "contour",
    },
    # ═══ routes/ — intent routing map ═══
    {
        "plane": "routes",
        "name": "Intent Routing Plane",
        "canonical_home": "registries/",
        "primitives": [
            "route-registry",
            "capability-index",
            "tool-registry",
            "port-registry",
            "mission-map",
        ],
        "current_locations": [
            "registries/ (47 files — CANONICAL but overlapping)",
            "registries/ROUTE_REGISTRY.json",
            "registries/CAPABILITY_INDEX.json",
            "registries/FEDERATION_MODEL.json",
            "registries/tools.yaml",
            "registries/domains.yaml",
            "registries/mission.yaml",
        ],
        "files": 47,
        "entropy": "OVERLAPPING_TAXONOMIES",
        "paradox": "P04-evidence-claim — registry as claim vs registry as truth",
        "paradox_zone": "contour",
    },
]

MIGRATION_RULES = [
    "1. Delete nothing. This is a map, not a migration.",
    "2. Resolve CF-AAA-01 first (Trinity identity duplication) — highest signal reduction.",
    "3. Consolidate agent cards: agent-cards/ is canonical. a2a-server/ should reference, not copy.",
    "4. Consolidate skills: skills/ is canonical tree. wiki/skills/ → archive. Platform adapters → wrappers.",
    "5. Single skill registry: FEDERATION_SKILL_PROFILE.json as canonical. Deprecate 17 others after audit.",
    "6. Merge peer contracts: a2a/peer-contracts/ is canonical. asi/contracts/ → merge.",
    "7. Clean registries: consolidate overlapping files into identity/capability/route scheme.",
]


def build_aaa_index() -> str:
    """Assemble the AAA cognitive federation map."""
    content_hash = hashlib.sha256(
        json.dumps(
            {
                "findings": [f["id"] for f in CRITICAL_FINDINGS],
                "planes": [p["plane"] for p in PLANE_MAP],
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    # Compute some aggregate metrics
    total_agent_card_copies = sum(1 for cf in CRITICAL_FINDINGS if "card" in cf["planes"])
    total_skill_trees = 6

    result = {
        "_meta": {
            "resource": "arifos://aaa-index",
            "title": "arifOS AAA Index — The Cognitive Federation Map",
            "description": "Maps the AAA cognitive federation: 57 agent cards, 23 identity files, 229 skills, 47 registries. 6-plane architecture for the mind layer.",
            "forged": generated_at,
            "forged_by": "333-AGI Δ MIND",
            "content_hash": content_hash,
            "generated_at": generated_at,
            "generator": "arifOS/arifosmcp/resources/aaa_index.py::build_aaa_index",
            "is_derived": False,
            "annotations": {
                "audience": ["assistant"],
                "priority": 0.9,
                "lastModified": generated_at,
            },
        },
        "entropy": AAA_STATS,
        "fractal": {
            "description": "The entropy pattern is fractal, not accidental. Each layer carries the same disease at different scale.",
            "layers": {
                "arifOS (law)": {
                    "resource": "arifos://index",
                    "primitives": "resources, kernels, registries",
                },
                "arifOS (repo)": {
                    "resource": "arifos://atlas-repo",
                    "primitives": "directories, schemas, contracts",
                },
                "AAA (mind)": {
                    "resource": "arifos://aaa-index",
                    "primitives": "identities, cards, skills, peers",
                },
                "A-FORGE (hands)": {"resource": "future", "primitives": "tools, shells, pipelines"},
                "VAULT999 (witness)": {
                    "resource": "future",
                    "primitives": "seals, receipts, attestations",
                },
            },
            "invariant": "One Truth. Many Views. Zero Drift.",
        },
        "architecture": {
            "six_planes_aaa": {
                "identity": {
                    "canonical_home": "agent-cards/identity/",
                    "primitives": ["333-AGI", "555-ASI", "888-APEX", "sovereign"],
                    "cardinality": "3 primary + sovereign",
                    "current_copies": 4,
                    "target_copies": 1,
                },
                "cards": {
                    "canonical_home": "agent-cards/",
                    "primitives": ["agent-card.json"],
                    "cardinality": "57 files",
                    "current_registries": 3,
                    "target_registries": 1,
                },
                "skills": {
                    "canonical_home": "skills/",
                    "primitives": ["SKILL.md"],
                    "cardinality": "229 files",
                    "current_trees": 6,
                    "target_trees": 1,
                },
                "peers": {
                    "canonical_home": "a2a/peer-contracts/",
                    "primitives": ["peer-contract.json"],
                    "cardinality": "22 files",
                    "current_locations": 4,
                    "target_locations": 1,
                },
                "contracts": {
                    "canonical_home": "contracts/",
                    "primitives": ["federation-contract.yaml"],
                    "cardinality": "56 files",
                    "current_locations": 3,
                    "target_locations": 1,
                },
                "routes": {
                    "canonical_home": "registries/",
                    "primitives": ["route-registry", "capability-index", "tool-registry"],
                    "cardinality": "47 files",
                    "current_registries": 47,
                    "target_registries": 3,
                },
            },
        },
        "critical_findings": CRITICAL_FINDINGS,
        "plane_map": PLANE_MAP,
        "migration_rules": MIGRATION_RULES,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def register_aaa_index(mcp: FastMCP) -> list[str]:
    """Register arifos://aaa-index — the AAA cognitive federation map."""

    @mcp.resource(
        "arifos://aaa-index",
        name="AAA Cognitive Federation Index",
        mime_type="application/json",
        description="Cognitive federation map: 57 agent cards, 23 identity files, 229 skills, 47 registries. 6-plane architecture for the mind layer.",
    )
    def aaa_index() -> str:
        """AAA Cognitive Federation Index — the mind layer's migration map.

        57 agent cards, 23 identity files, 229 skills, 47 registries.
        5 critical findings. The fractal pattern confirmed:
        arifOS = Law, AAA = Mind — one organism, two strata.

        Migrate rule: delete nothing, alias second, deprecate last.
        """
        return build_aaa_index()

    return ["arifos://aaa-index"]
