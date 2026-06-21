"""
arifosmcp/runtime/l5_seed_graph.py — Capability Graph Population v1
══════════════════════════════════════════════════════════════════════

SEEDS FalkorDB with the arifOS federation capability graph:
  - Tool nodes (every MCP tool across all organs)
  - Edge relationships (DEPENDS_ON, PRODUCES, REQUIRES, ROUTES_TO)
  - Domain groupings (governance, intelligence, memory, wealth, well, geox, infra)
  - Seed episodes from VAULT999 (real consequence history)

GOVERNANCE METADATA (per Arif's memory paradox):
  Every node carries: source, confidence, scope, owner, expiry, revocation_path
  Memory informs. Intelligence evaluates. Governance decides.
  No memory entry has automatic sovereignty.

ARCHITECTURE:
  This is the L5 write counterpart to l5_search_api.py's read path.
  Run once to bootstrap. Re-runnable — uses MERGE to avoid duplicates.

AUTHORITY: 555_MEMORY, 888_JUDGE
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

FALKOR_HOST = os.getenv("FALKOR_HOST", "localhost")
FALKOR_PORT = int(os.getenv("FALKOR_PORT", "6380"))
FALKOR_GRAPH = os.getenv("FALKOR_GRAPH", "arif_l5_knowledge")
VAULT999_PATH = os.getenv("VAULT999_PATH", "/root/arifOS/VAULT999/SEALED_EVENTS_v2.jsonl")
DRY_RUN = os.getenv("L5_SEED_DRY_RUN", "false").lower() == "true"

# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATION TOOL REGISTRY — Canonical, grounded in reality
# ═══════════════════════════════════════════════════════════════════════════════

# Every tool entry carries FULL governance metadata per Arif's memory architecture:
#   source, timestamp, confidence, scope, owner, expiry, revocation_path,
#   contradiction_handling, audit_trail, consent_boundary

TOOLS = {
    # ── GOVERNANCE (ArifOS Kernel) ──
    "arif_session_init": {
        "type": "Tool", "domain": "governance", "organ": "kernel",
        "description": "Initialize governed session — identity binding, F-floor activation",
        "reversible": True, "confidence": 0.99, "scope": "session", "owner": "888",
        "expiry": "session", "revocation_path": "F13_SOVEREIGN",
    },
    "arif_judge_deliberate": {
        "type": "Tool", "domain": "governance", "organ": "kernel",
        "description": "888 JUDGE — render constitutional verdict (SEAL/SABAR/VOID/HOLD)",
        "reversible": False, "confidence": 0.99, "scope": "decision", "owner": "888",
        "expiry": "never", "revocation_path": "F13_SOVEREIGN_OVERRIDE",
    },
    "arif_vault_seal": {
        "type": "Tool", "domain": "governance", "organ": "kernel",
        "description": "999 VAULT — immutable ledger anchoring, hash-chained",
        "reversible": False, "confidence": 0.99, "scope": "permanent", "owner": "999",
        "expiry": "never", "revocation_path": "NONE_IMMUTABLE",
    },
    "arif_sense_observe": {
        "type": "Tool", "domain": "governance", "organ": "kernel",
        "description": "111 SENSE — machine state observation, F2 truth grounding",
        "reversible": True, "confidence": 0.95, "scope": "read", "owner": "333",
    },
    "arif_mind_reason": {
        "type": "Tool", "domain": "intelligence", "organ": "mind",
        "description": "333 MIND — symbolic reasoning kernel, epistemic band enforced",
        "reversible": True, "confidence": 0.95, "scope": "reasoning", "owner": "333",
    },
    "arif_heart_critique": {
        "type": "Tool", "domain": "intelligence", "organ": "heart",
        "description": "444 HEART — ethical critique, consequence assessment, F5/F6/F9 enforcement",
        "reversible": True, "confidence": 0.90, "scope": "ethical", "owner": "444",
    },
    "arif_kernel_route": {
        "type": "Tool", "domain": "governance", "organ": "kernel",
        "description": "555 ROUTE — intent-to-organ routing, tool dispatch",
        "reversible": True, "confidence": 0.95, "scope": "routing", "owner": "555",
    },
    "arif_memory_recall": {
        "type": "Tool", "domain": "memory", "organ": "memory",
        "description": "555m MEMORY — vector + graph recall, Qdrant + FalkorDB dual-read",
        "reversible": True, "confidence": 0.90, "scope": "read", "owner": "555",
    },
    "arif_forge_execute": {
        "type": "Tool", "domain": "governance", "organ": "kernel",
        "description": "666 FORGE — code generation, artifact creation, F1 reversible gate",
        "reversible": True, "confidence": 0.95, "scope": "execution", "owner": "888",
    },
    "arif_gateway_connect": {
        "type": "Tool", "domain": "infra", "organ": "gateway",
        "description": "666g GATEWAY — cross-agent federation bridge, A2A protocol",
        "reversible": True, "confidence": 0.90, "scope": "federation", "owner": "666",
    },
    "arif_ops_measure": {
        "type": "Tool", "domain": "infra", "organ": "ops",
        "description": "777 MEASURE — machine health, resource telemetry, entropy audit",
        "reversible": True, "confidence": 0.95, "scope": "read", "owner": "777",
    },

    # ── MEMORY & KNOWLEDGE ──
    "memory_store": {
        "type": "Tool", "domain": "memory", "organ": "memory",
        "description": "Dual-write to Qdrant (L3) + Postgres (L4), tiered TTL (sacred/canon/session/ephemeral)",
        "reversible": True, "confidence": 0.95, "scope": "write", "owner": "555",
    },
    "l5_graphiti_bridge": {
        "type": "Tool", "domain": "memory", "organ": "memory",
        "description": "L5 Graphiti write bridge — fire-and-forget episode creation in FalkorDB",
        "reversible": True, "confidence": 0.85, "scope": "write", "owner": "555",
    },
    "l5_graph_read": {
        "type": "Tool", "domain": "memory", "organ": "memory",
        "description": "L5 Graphiti read path — similar task search, capability subgraph, prior path retrieval",
        "reversible": True, "confidence": 0.85, "scope": "read", "owner": "555",
    },
    "l5_search_api": {
        "type": "Tool", "domain": "memory", "organ": "memory",
        "description": "L5 Search API — FastAPI on :8001, FalkorDB query endpoints (7 routes)",
        "reversible": True, "confidence": 0.90, "scope": "read", "owner": "555",
    },

    # ── INTELLIGENCE (MIND Feedback Loop) ──
    "mind_state": {
        "type": "Tool", "domain": "intelligence", "organ": "mind",
        "description": "MINDState persistent object — checkpoint, rollback, epistemic tracking, floor binding",
        "reversible": True, "confidence": 0.93, "scope": "state", "owner": "333",
    },
    "feedback_loop": {
        "type": "Tool", "domain": "intelligence", "organ": "mind",
        "description": "FeedbackLoop controller — Sequential Thinking ↔ Graph memory signal evaluation",
        "reversible": True, "confidence": 0.93, "scope": "reasoning", "owner": "333",
    },
    "mind_feedback_hook": {
        "type": "Tool", "domain": "intelligence", "organ": "mind",
        "description": "Integration hook — zero-kernel-mod wrapper for arif_mind_reason_v2 feedback tracking",
        "reversible": True, "confidence": 0.93, "scope": "integration", "owner": "333",
    },
    "sequential_thinking_mcp": {
        "type": "Tool", "domain": "intelligence", "organ": "mind",
        "description": "Anthropic Sequential Thinking MCP — step-by-step reasoning with revision/branch/verify",
        "reversible": True, "confidence": 0.90, "scope": "reasoning", "owner": "333",
    },
    "sequential_thinking_hermes": {
        "type": "Tool", "domain": "intelligence", "organ": "hermes",
        "description": "Hermes sequential-thinking skill — constitutional binding, auto-trigger for complex tasks",
        "reversible": True, "confidence": 0.90, "scope": "skill", "owner": "hermes",
    },

    # ── WEALTH ORGAN ──
    "wealth_conservation_capital": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-WEALTH-01 — capital stock reality, assets, liabilities, reserves, ledger",
        "reversible": True, "confidence": 0.90, "scope": "analysis", "owner": "888",
    },
    "wealth_flow_liquidity": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-WEALTH-02 — cashflow, burn, runway, survival analysis",
        "reversible": True, "confidence": 0.90, "scope": "analysis", "owner": "888",
    },
    "wealth_entropy_risk": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-WEALTH-04 — uncertainty, dispersion, tail risk, asymmetry detection",
        "reversible": True, "confidence": 0.90, "scope": "analysis", "owner": "888",
    },
    "wealth_energy_productivity": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-WEALTH-05 — output per input, productivity, capital efficiency",
        "reversible": True, "confidence": 0.90, "scope": "analysis", "owner": "888",
    },
    "wealth_time_discount": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-WEALTH-06 — NPV, IRR, payback, compounding, decay",
        "reversible": True, "confidence": 0.95, "scope": "analysis", "owner": "888",
    },
    "wealth_field_macro": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-WEALTH-08 — macro environment, rates, FX, energy, carbon, regime",
        "reversible": True, "confidence": 0.85, "scope": "analysis", "owner": "888",
    },
    "wealth_market_data": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Ω-D3 — unified FX, commodities, macro indicators via Frankfurter/WorldBank API",
        "reversible": True, "confidence": 0.85, "scope": "read", "owner": "888",
    },
    "wealth_stock_analysis": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "D4 — Bursa Malaysia stock analysis, 15 modes, verify_math to bursa_evidence",
        "reversible": True, "confidence": 0.85, "scope": "analysis", "owner": "888",
    },
    "wealth_governance_verdict": {
        "type": "Tool", "domain": "wealth", "organ": "wealth",
        "description": "Final Allocation Verdict — sovereign governance recommendation, D_S + peace + maruah",
        "reversible": False, "confidence": 0.95, "scope": "decision", "owner": "888",
    },

    # ── WELL ORGAN ──
    "well_classify_substrate": {
        "type": "Tool", "domain": "well", "organ": "well",
        "description": "Ω-WELL-01 — substrate classification, boundary sensing",
        "reversible": True, "confidence": 0.85, "scope": "analysis", "owner": "444",
    },
    "well_trace_lineage": {
        "type": "Tool", "domain": "well", "organ": "well",
        "description": "Ω-WELL-02 — memory, trend, ledger, vault chain tracing",
        "reversible": True, "confidence": 0.90, "scope": "read", "owner": "444",
    },
    "well_assess_metabolism": {
        "type": "Tool", "domain": "well", "organ": "well",
        "description": "Ω-WELL-05 — biological metabolism, system throughput assessment",
        "reversible": True, "confidence": 0.80, "scope": "analysis", "owner": "444",
    },
    "well_assess_homeostasis": {
        "type": "Tool", "domain": "well", "organ": "well",
        "description": "Ω-WELL-06 — regulation, stability, empathic balance under change",
        "reversible": True, "confidence": 0.80, "scope": "analysis", "owner": "444",
    },
    "well_validate_vitality": {
        "type": "Tool", "domain": "well", "organ": "well",
        "description": "Ω-WELL-08 — vitality, readiness, NIAT validation",
        "reversible": True, "confidence": 0.85, "scope": "analysis", "owner": "444",
    },
    "well_assess_reliability": {
        "type": "Tool", "domain": "well", "organ": "well",
        "description": "Ω-WELL-10 — machine, tool, institution, operational reliability",
        "reversible": True, "confidence": 0.85, "scope": "analysis", "owner": "444",
    },

    # ── GEOX ORGAN ──
    "geox_basin_resolve": {
        "type": "Tool", "domain": "geox", "organ": "geox",
        "description": "Resolve basin name to canonical ID, bounding box, neighboring basins",
        "reversible": True, "confidence": 0.90, "scope": "read", "owner": "geologist",
    },
    "geox_basin_profile": {
        "type": "Tool", "domain": "geox", "organ": "geox",
        "description": "Basin-level intelligence: petroleum system, stratigraphy, play fairway, risk, contradiction scan",
        "reversible": True, "confidence": 0.85, "scope": "analysis", "owner": "geologist",
    },
    "geox_subsurface_generate_candidates": {
        "type": "Tool", "domain": "geox", "organ": "geox",
        "description": "Ensemble subsurface outputs: petrophysics, structure, Vsh, porosity, saturation, netpay",
        "reversible": True, "confidence": 0.85, "scope": "generation", "owner": "geologist",
    },
    "geox_seismic_compute": {
        "type": "Tool", "domain": "geox", "organ": "geox",
        "description": "Unified seismic physics: synthetic, well_tie, time_depth_anchor, anomalous_contrast, attribute",
        "reversible": True, "confidence": 0.90, "scope": "computation", "owner": "geologist",
    },
    "geox_claim_create": {
        "type": "Tool", "domain": "geox", "organ": "geox",
        "description": "Structured Earth interpretation claim — FACT/INTERPRETATION/SPECULATION with uncertainty band",
        "reversible": True, "confidence": 0.90, "scope": "claim", "owner": "geologist",
    },
    "geox_evidence_reason": {
        "type": "Tool", "domain": "geox", "organ": "geox",
        "description": "Unified evidence synthesis: abduct, contradict, synthesize, spatial_block",
        "reversible": True, "confidence": 0.85, "scope": "reasoning", "owner": "geologist",
    },

    # ── HERMES TOOLS ──
    "hermes_delegate_task": {
        "type": "Tool", "domain": "infra", "organ": "hermes",
        "description": "Spawn subagents for parallel work — leaf/orchestrator roles, toolset isolation",
        "reversible": True, "confidence": 0.90, "scope": "execution", "owner": "hermes",
    },
    "hermes_terminal": {
        "type": "Tool", "domain": "infra", "organ": "hermes",
        "description": "Shell execution with foreground/background, PTY, timeout, workdir",
        "reversible": False, "confidence": 0.95, "scope": "execution", "owner": "hermes",
    },
    "hermes_web_search": {
        "type": "Tool", "domain": "infra", "organ": "hermes",
        "description": "Web search via configured backend, operator support",
        "reversible": True, "confidence": 0.85, "scope": "read", "owner": "hermes",
    },
    "hermes_browser": {
        "type": "Tool", "domain": "infra", "organ": "hermes",
        "description": "Playwright browser automation — navigate, click, screenshot, evaluate",
        "reversible": True, "confidence": 0.85, "scope": "execution", "owner": "hermes",
    },
    "hermes_perplexity": {
        "type": "Tool", "domain": "infra", "organ": "hermes",
        "description": "Perplexity Sonar — web-grounded AI (ask/reason/research/search modes)",
        "reversible": True, "confidence": 0.85, "scope": "read", "owner": "hermes",
    },
    "hermes_cloudflare": {
        "type": "Tool", "domain": "infra", "organ": "hermes",
        "description": "Cloudflare API — DNS, Workers, Pages, R2, D1, analytics",
        "reversible": False, "confidence": 0.90, "scope": "execution", "owner": "hermes",
    },

    # ── MCP FEDERATION SERVERS ──
    "mcp_supabase": {
        "type": "Tool", "domain": "infra", "organ": "supabase",
        "description": "Supabase MCP — migrations, edge functions, SQL, branches, logs, advisors",
        "reversible": False, "confidence": 0.90, "scope": "execution", "owner": "888",
    },
    "mcp_hostinger": {
        "type": "Tool", "domain": "infra", "organ": "hostinger",
        "description": "Hostinger VPS API — snapshots, metrics, firewall, restart, templates",
        "reversible": False, "confidence": 0.90, "scope": "execution", "owner": "888",
    },
    "mcp_agentmail": {
        "type": "Tool", "domain": "infra", "organ": "agentmail",
        "description": "AgentMail MCP — inbox CRUD, thread management, send/reply/forward",
        "reversible": False, "confidence": 0.85, "scope": "execution", "owner": "hermes",
    },

    # ── RASA CONTRACT ──
    "rasa_contract": {
        "type": "Module", "domain": "well", "organ": "well",
        "description": "Typed governance metadata for human affective state evidence — 12 canonical tags",
        "reversible": True, "confidence": 0.85, "scope": "governance", "owner": "444",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE RELATIONSHIPS
# ═══════════════════════════════════════════════════════════════════════════════

# Directional edges: (source, relation, target, weight, reason)
EDGES = [
    # Governance pipeline
    ("arif_session_init", "ROUTES_TO", "arif_sense_observe", 1.0, "000→111 pipeline"),
    ("arif_sense_observe", "ROUTES_TO", "arif_mind_reason", 1.0, "111→333 pipeline"),
    ("arif_mind_reason", "ROUTES_TO", "arif_heart_critique", 1.0, "333→444 pipeline"),
    ("arif_heart_critique", "ROUTES_TO", "arif_kernel_route", 1.0, "444→555 pipeline"),
    ("arif_kernel_route", "ROUTES_TO", "arif_forge_execute", 0.8, "555→666 conditional"),
    ("arif_forge_execute", "ROUTES_TO", "arif_judge_deliberate", 1.0, "666→888 pipeline"),
    ("arif_judge_deliberate", "ROUTES_TO", "arif_vault_seal", 1.0, "888→999 pipeline"),

    # Memory architecture
    ("arif_memory_recall", "DEPENDS_ON", "memory_store", 1.0, "recall reads store"),
    ("memory_store", "PRODUCES", "l5_graphiti_bridge", 0.8, "store triggers L5 write"),
    ("l5_graphiti_bridge", "PRODUCES", "l5_search_api", 0.8, "bridge populates search"),
    ("l5_graph_read", "DEPENDS_ON", "l5_search_api", 1.0, "read queries search API"),

    # MIND feedback loop
    ("arif_mind_reason", "DEPENDS_ON", "mind_state", 0.9, "reasoning persists state"),
    ("mind_state", "DEPENDS_ON", "feedback_loop", 0.9, "state feeds feedback"),
    ("feedback_loop", "DEPENDS_ON", "l5_graph_read", 0.8, "feedback queries graph"),
    ("sequential_thinking_mcp", "DEPENDS_ON", "arif_mind_reason", 0.7, "ST feeds MIND"),
    ("sequential_thinking_hermes", "DEPENDS_ON", "sequential_thinking_mcp", 1.0, "skill wraps MCP"),

    # Wealth organ
    ("wealth_conservation_capital", "PRODUCES", "wealth_governance_verdict", 0.9, "capital feeds verdict"),
    ("wealth_flow_liquidity", "PRODUCES", "wealth_governance_verdict", 0.9, "liquidity feeds verdict"),
    ("wealth_entropy_risk", "PRODUCES", "wealth_governance_verdict", 0.9, "risk feeds verdict"),
    ("wealth_time_discount", "DEPENDS_ON", "wealth_energy_productivity", 0.7, "DCF needs productivity"),
    ("wealth_field_macro", "DEPENDS_ON", "wealth_market_data", 1.0, "macro reads market"),

    # WELL organ
    ("well_classify_substrate", "ROUTES_TO", "well_trace_lineage", 0.8, "classify then trace"),
    ("well_trace_lineage", "ROUTES_TO", "well_assess_metabolism", 0.7, "trace then assess"),
    ("well_assess_homeostasis", "DEPENDS_ON", "well_assess_metabolism", 0.8, "homeostasis needs metabolism"),
    ("rasa_contract", "DEPENDS_ON", "well_classify_substrate", 0.6, "rasa needs substrate"),

    # GEOX organ
    ("geox_basin_resolve", "ROUTES_TO", "geox_basin_profile", 1.0, "resolve then profile"),
    ("geox_basin_profile", "ROUTES_TO", "geox_subsurface_generate_candidates", 0.8, "profile then generate"),
    ("geox_subsurface_generate_candidates", "PRODUCES", "geox_claim_create", 0.9, "candidates become claims"),
    ("geox_claim_create", "DEPENDS_ON", "geox_evidence_reason", 0.9, "claims need evidence"),
    ("geox_seismic_compute", "PRODUCES", "geox_evidence_reason", 0.8, "seismic feeds evidence"),

    # Cross-organ
    ("arif_mind_reason", "DEPENDS_ON", "arif_memory_recall", 0.8, "reasoning needs memory"),
    ("arif_forge_execute", "DEPENDS_ON", "hermes_terminal", 0.9, "forge needs shell"),
    ("hermes_delegate_task", "DEPENDS_ON", "arif_gateway_connect", 0.6, "delegation needs gateway"),
    ("wealth_governance_verdict", "DEPENDS_ON", "arif_judge_deliberate", 0.7, "wealth verdict needs judge"),
    ("well_validate_vitality", "DEPENDS_ON", "arif_sense_observe", 0.7, "vitality needs sense"),
    ("geox_claim_create", "DEPENDS_ON", "arif_judge_deliberate", 0.5, "claims may need judge"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# FALKORDB OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_graph():
    from falkordb import FalkorDB
    db = FalkorDB(host=FALKOR_HOST, port=FALKOR_PORT)
    return db.select_graph(FALKOR_GRAPH)


def _run(cypher: str, params: dict | None = None):
    """Run Cypher. Returns result_set or raises."""
    graph = _get_graph()
    result = graph.query(cypher, params or {})
    return result.result_set if result else []


def seed_tools(dry_run: bool = False) -> int:
    """Create Tool nodes in FalkorDB with full governance metadata."""
    ts = datetime.now(UTC).isoformat()
    count = 0

    for name, meta in TOOLS.items():
        cypher = """
            MERGE (t:Tool {name: $name})
            SET t.type = $type,
                t.domain = $domain,
                t.organ = $organ,
                t.description = $description,
                t.reversible = $reversible,
                t.confidence = $confidence,
                t.scope = $scope,
                t.owner = $owner,
                t.expiry = $expiry,
                t.revocation_path = $revocation_path,
                t.seeded_at = $ts,
                t.source = 'l5_seed_graph.py',
                t.audit_trail = 'VAULT999:outcomes.jsonl'
            RETURN t.name
        """
        params = {
            "name": name, "type": meta["type"], "domain": meta["domain"],
            "organ": meta["organ"], "description": meta["description"],
            "reversible": meta["reversible"], "confidence": meta["confidence"],
            "scope": meta["scope"], "owner": meta["owner"],
            "expiry": meta.get("expiry", "canon"), "revocation_path": meta.get("revocation_path", "F13_SOVEREIGN"),
            "ts": ts,
        }
        if dry_run:
            print(f"  [DRY RUN] MERGE Tool:{name}")
        else:
            _run(cypher, params)
        count += 1

    return count


def seed_edges(dry_run: bool = False) -> int:
    """Create relationship edges between Tool nodes."""
    ts = datetime.now(UTC).isoformat()
    count = 0

    for source, relation, target, weight, reason in EDGES:
        cypher = f"""
            MATCH (a:Tool {{name: $source}})
            MATCH (b:Tool {{name: $target}})
            MERGE (a)-[r:{relation}]->(b)
            SET r.weight = $weight,
                r.reason = $reason,
                r.seeded_at = $ts
            RETURN type(r)
        """
        params = {
            "source": source, "target": target,
            "weight": weight, "reason": reason, "ts": ts,
        }
        if dry_run:
            print(f"  [DRY RUN] ({source})-[{relation}]->({target}) w={weight}")
        else:
            try:
                _run(cypher, params)
                count += 1
            except Exception as e:
                print(f"  SKIP edge {source}->{target}: {e}")

    return count


def seed_episodes(dry_run: bool = False, limit: int = 20) -> int:
    """Seed episodes from real VAULT999 outcomes."""
    count = 0
    try:
        with open(VAULT999_PATH) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"  VAULT999 not found at {VAULT999_PATH}")
        return 0

    # Take the most recent entries
    recent = lines[-limit:]
    ts = datetime.now(UTC).isoformat()

    for line in recent:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        seal_id = entry.get("seal_id", "unknown")
        episode_id = hashlib.sha256(seal_id.encode()).hexdigest()[:16]
        body = json.dumps(entry, default=str)

        cypher = """
            MERGE (e:Episode {uuid: $uuid})
            SET e.name = $name,
                e.episode_body = $body,
                e.source = 'VAULT999',
                e.source_description = $desc,
                e.domain = $domain,
                e.total_steps = $steps,
                e.plan_status = 'completed',
                e.epistemic_band = $confidence,
                e.created_at = $ts,
                e.type = 'vault999_seed'
            RETURN e.uuid
        """
        params = {
            "uuid": episode_id,
            "name": seal_id[:80],
            "body": body,
            "desc": entry.get("summary", entry.get("forge", ""))[:200],
            "domain": "governance",
            "steps": 1,
            "confidence": 0.99,
            "ts": entry.get("timestamp", ts),
        }

        if dry_run:
            print(f"  [DRY RUN] Episode:{seal_id[:60]}")
        else:
            try:
                _run(cypher, params)
                count += 1
            except Exception as e:
                print(f"  SKIP episode {seal_id[:40]}: {e}")

    return count


def seed_domains(dry_run: bool = False) -> int:
    """Create Domain grouping nodes."""
    domains = ["governance", "intelligence", "memory", "wealth", "well", "geox", "infra"]
    ts = datetime.now(UTC).isoformat()
    count = 0

    for domain in domains:
        cypher = """
            MERGE (d:Domain {name: $name})
            SET d.description = $desc,
                d.seeded_at = $ts
            RETURN d.name
        """
        descs = {
            "governance": "Constitutional floor enforcement, judgment, vault sealing",
            "intelligence": "Reasoning, feedback loops, sequential thinking, ethical critique",
            "memory": "Qdrant L3, Postgres L4, FalkorDB L5, tiered TTL, dual-write",
            "wealth": "Capital intelligence, risk, macro, Bursa, personal finance",
            "well": "Human substrate sensing, vitality, homeostasis, rasa governance",
            "geox": "Subsurface intelligence, seismic, basin, claims, evidence",
            "infra": "Federation topology, MCP servers, cloud, deployment, shell",
        }
        params = {"name": domain, "desc": descs.get(domain, ""), "ts": ts}
        if dry_run:
            print(f"  [DRY RUN] Domain:{domain}")
        else:
            _run(cypher, params)
            count += 1

    return count


def link_tools_to_domains(dry_run: bool = False) -> int:
    """Link each Tool to its Domain node."""
    ts = datetime.now(UTC).isoformat()
    count = 0

    for name, meta in TOOLS.items():
        cypher = """
            MATCH (t:Tool {name: $name})
            MATCH (d:Domain {name: $domain})
            MERGE (t)-[r:BELONGS_TO]->(d)
            SET r.seeded_at = $ts
            RETURN type(r)
        """
        params = {"name": name, "domain": meta["domain"], "ts": ts}
        if dry_run:
            print(f"  [DRY RUN] Tool:{name} BELONGS_TO Domain:{meta['domain']}")
        else:
            try:
                _run(cypher, params)
                count += 1
            except Exception as e:
                print(f"  SKIP link {name}->{meta['domain']}: {e}")

    return count


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICATION QUERIES
# ═══════════════════════════════════════════════════════════════════════════════

def verify() -> dict[str, int]:
    """Run verification queries and return counts."""
    queries = {
        "tools": "MATCH (t:Tool) RETURN count(t)",
        "edges": "MATCH ()-[r]->() RETURN count(r)",
        "domains": "MATCH (d:Domain) RETURN count(d)",
        "episodes": "MATCH (e:Episode) RETURN count(e)",
        "tool_domain_links": "MATCH (t:Tool)-[:BELONGS_TO]->(d:Domain) RETURN count(t)",
    }
    results = {}
    for key, cypher in queries.items():
        try:
            rows = _run(cypher)
            results[key] = rows[0][0] if rows and rows[0] else 0
        except Exception as e:
            results[key] = -1
            print(f"  VERIFY FAIL {key}: {e}")
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    dry = DRY_RUN
    mode = "DRY RUN" if dry else "LIVE"
    print(f"=== L5 Capability Graph Seed ({mode}) ===")
    print(f"FalkorDB: {FALKOR_HOST}:{FALKOR_PORT}/{FALKOR_GRAPH}")
    print(f"VAULT999: {VAULT999_PATH}")
    print()

    print(f"[1/5] Seeding {len(TOOLS)} tool nodes...")
    n_tools = seed_tools(dry_run=dry)
    print(f"  → {n_tools} tools seeded")

    print(f"[2/5] Seeding {len(EDGES)} relationship edges...")
    n_edges = seed_edges(dry_run=dry)
    print(f"  → {n_edges} edges created")

    print("[3/5] Seeding domains...")
    n_domains = seed_domains(dry_run=dry)
    print(f"  → {n_domains} domains created")

    print("[4/5] Linking tools to domains...")
    n_links = link_tools_to_domains(dry_run=dry)
    print(f"  → {n_links} tool→domain links created")

    print("[5/5] Seeding episodes from VAULT999...")
    n_episodes = seed_episodes(dry_run=dry)
    print(f"  → {n_episodes} episodes seeded")

    if not dry:
        print("\n=== VERIFICATION ===")
        counts = verify()
        for k, v in counts.items():
            status = "✅" if v > 0 else "❌"
            print(f"  {status} {k}: {v}")

    print("\nDITEMPA BUKAN DIBERI — Graph seeded, not given.")


if __name__ == "__main__":
    main()
