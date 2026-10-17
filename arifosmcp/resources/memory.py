"""
arifos://memory — 6-Layer Memory Architecture
═════════════════════════════════════════════
Memory does not become truth until it has provenance.
Truth does not become final until sealed.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

MEMORY_TEXT = """\
---arifos_meta
resource_class: architecture
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.10.16
mutation_allowed: false
requires_actor_verified: true
requires_session: true
lease_required: false
blast_radius: LOW
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-10-16T10:30:00Z
truth_level: 1
---end_arifos_meta

arifOS Memory — 6-Layer Architecture

┌──────────────────────────────────────────────────────────┐
│  L1 Redis        → now / ephemeral electrical spark      │
│  L2 Redis        → session thread / conversation          │
│  L3 Qdrant       → fuzzy similarity / "what feels like?" │
│  L4 Supabase     → official structured record              │
│  L5 (RETIRED)    → Graphiti deprecated → L3 Qdrant + L4   │
│  L6 VAULT999     → immutable sealed / "what is final?"    │
│  AAA             → display layer for Arif                  │
└──────────────────────────────────────────────────────────┘

TOOL (canonical name):
  arif_memory  — one tool, many modes. `arif_memory_recall` is a DEPRECATED
  legacy alias that resolves to arif_memory(mode=recall) server-side.

MODES (read — OBSERVE class, no lease):
  recall            — semantic search (L3 Qdrant cascade; L2 session in scope)
  inspect           — read one memory object by id (L4 direct lookup)
  attest            — verify a memory_id against the L6 vault seal chain
  audit             — JITU contradiction engine: action vs memory state

MODES (write — MUTATE class, lease_id required):
  remember          — write a candidate memory (confidence<0.3 → SABAR
                      unless human_ack; B3 truth_class floor)
  promote           — move a candidate to a higher tier (irreversible;
                      human_ack required)
  revise            — supersede/merge a prior memory (B5: supersedes_memory_id
                      required; irreversible)
  forget            — soft-delete / tombstone (L13 SOVEREIGN human_approval
                      required; execution stays disabled until the F13
                      forget flow is ratified)

TIERS (the `tier` / `tier_hint` parameter of recall):
  L2 / L3 (default) — the recall cascade (Qdrant). Every recall response
                      returns `hits`, `tiers_requested`, `tiers_searched`,
                      `tier_honored`, and on empty a `reason` — so
                      "not found" is never silent and never ambiguous.
  L4                — NOT searched by recall. Use inspect(memory_id=...).
  L5                — retired; graph requests are gated (SABAR/UNMEASURED)
                      before any vector fallback.
  L6                — NOT searched and NOT written by arif_memory. An L6
                      request returns hits:[] with the reason. L6 has ONE
                      path only: arif_seal(mode=seal).

DISCIPLINES:

  L1 — EPHEMERAL (Redis, ~60s TTL)
    Electrical spark. Current context window. Never persisted.
    Tool: implicit (session state)

  L2 — SESSION (Redis, session TTL)
    Conversation thread. Prior turns in this session.
    Tool: arif_memory(mode=recall)

  L3 — SEMANTIC (Qdrant, 1024-dim BGE-M3)
    Fuzzy similarity search. "What feels similar to this?"
    Tool: arif_memory(mode=recall, tier="L3")

  L4 — STRUCTURED (Supabase Postgres)
    Official structured record. Domain tables, tool calls, receipts.
    Tool: arif_memory(mode=inspect) for a known memory_id.

  L5 — RETIRED (Graphiti + FalkorDB, tombstoned 2026-09-04)
    Relationship graph deprecated; replaced by L3 Qdrant + L4 Postgres.
    Tool: none — do not probe :8000.

  L6 — IMMUTABLE (VAULT999, append-only hash-chained)
    Final sealed truth. Cannot be modified, only appended.
    Tool: arif_seal(mode=seal) — the ONLY path to L6.

IRON RULE:
  Memory does not become truth until it has provenance.
  Truth does not become final until sealed (L6).
  No secret values in VAULT999 — it's an audit ledger, not a secret store.

DITEMPA BUKAN DIBERI
"""


def register_memory(mcp: FastMCP) -> list[str]:
    """Register arifos://memory — 6-layer memory architecture."""
    resource = TextResource(
        uri="arifos://memory",
        name="Memory Architecture (L1–L6)",
        description=(
            "The six-layer memory architecture: L1 ephemeral (Redis), L2 session (Redis), "
            "L3 semantic (Qdrant/BGE-M3), L4 structured (Supabase), L5 retired (Graphiti, → L3/L4), "
            "L6 immutable (VAULT999). Memory does not become truth until it has provenance. "
            "Truth does not become final until sealed."
        ),
        text=MEMORY_TEXT,
        tags={"resource", "memory", "architecture", "layers"},
    )
    mcp.add_resource(resource)
    return ["arifos://memory"]
