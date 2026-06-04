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
arifOS Memory — 6-Layer Architecture

┌──────────────────────────────────────────────────────────┐
│  L1 Redis        → now / ephemeral electrical spark      │
│  L2 Redis        → session thread / conversation          │
│  L3 Qdrant       → fuzzy similarity / "what feels like?" │
│  L4 Supabase     → official structured record              │
│  L5 Graphiti     → relationships / "connected to what?"   │
│  L6 VAULT999     → immutable sealed / "what is final?"    │
│  AAA             → display layer for Arif                  │
└──────────────────────────────────────────────────────────┘

DISCIPLINES:

  L1 — EPHEMERAL (Redis, ~60s TTL)
    Electrical spark. Current context window. Never persisted.
    Tool: implicit (session state)

  L2 — SESSION (Redis, session TTL)
    Conversation thread. Prior turns in this session.
    Tool: arif_memory_recall(mode=recall)

  L3 — SEMANTIC (Qdrant, 1024-dim BGE-M3)
    Fuzzy similarity search. "What feels similar to this?"
    Tool: arif_memory_recall(mode=recall, tier=L3)

  L4 — STRUCTURED (Supabase Postgres)
    Official structured record. Domain tables, tool calls, receipts.
    Tool: arif_memory_recall(mode=recall, tier=L4)

  L5 — RELATIONSHIPS (Graphiti + FalkorDB)
    Entity graph. "Who is connected to what?"
    Tool: arif_memory_recall(mode=recall, tier=L5)

  L6 — IMMUTABLE (VAULT999, append-only hash-chained)
    Final sealed truth. Cannot be modified, only appended.
    Tool: arif_vault_seal(mode=seal)

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
            "L3 semantic (Qdrant/BGE-M3), L4 structured (Supabase), L5 relationships (Graphiti), "
            "L6 immutable (VAULT999). Memory does not become truth until it has provenance. "
            "Truth does not become final until sealed."
        ),
        text=MEMORY_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://memory"]
