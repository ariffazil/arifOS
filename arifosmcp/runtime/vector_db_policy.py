"""
arifOS Vector DB Decision Policy — Agentic Search v0.1

Intelligence = knowing WHEN to use vector DB, not just HOW.
Embeddings are a tool, not a default. This module encodes 7 decision rules
as callable policy that agents can query at search-time.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataType(str, Enum):
    UNSTRUCTURED = "unstructured"
    STRUCTURED = "structured"
    HYBRID = "hybrid"


class Lifetime(str, Enum):
    EPHEMERAL = "ephemeral"  # per-session, per-user, short-lived
    EXPERIMENTAL = "experimental"  # prototype, exploring
    PERSISTENT = "persistent"  # shared corpus, reused over time


@dataclass
class CorpusProfile:
    """Describes a corpus that an agent might search over."""
    name: str
    n_docs: int              # number of documents/rows
    q_total: int             # expected queries over corpus lifetime
    lifetime: Lifetime
    data_type: DataType
    shared: bool = False     # shared across multiple users/agents
    has_hybrid_engine: bool = False  # already have ES/OS/Meilisearch


@dataclass
class VectorDBDecision:
    use_vector_db: bool
    use_pgvector: bool = False
    use_in_memory: bool = False
    recommended: str = ""  # human-readable recommendation
    rules_matched: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# THE 7 DECISION RULES
# ═══════════════════════════════════════════════════════════════════════════════

def should_use_vector_db(profile: CorpusProfile) -> VectorDBDecision:
    """
    Return VectorDBDecision for a given corpus profile.

    Rules in priority order (first match wins for NO decisions;
    YES decisions accumulate).
    """
    rules_matched: list[str] = []
    use_vector_db = False
    use_pgvector = False
    use_in_memory = False
    reasons: list[str] = []

    # ── RULE 1: Ephemeral → NO ───────────────────────────────────
    # Index build cost doesn't amortise for short-lived corpora.
    if profile.lifetime == Lifetime.EPHEMERAL and profile.q_total < 2000:
        use_in_memory = True
        rules_matched.append("R1_EPHEMERAL_IN_MEMORY")
        reasons.append("Ephemeral corpus with <2k queries — in-memory KNN sufficient")

    # ── RULE 2: Tiny corpus → NO ─────────────────────────────────
    # NumPy/FAISS or BM25 is cheaper and faster.
    elif profile.n_docs < 1000:
        use_in_memory = True
        rules_matched.append("R2_TINY_CORPUS")
        reasons.append("Tiny corpus (<1k docs) — NumPy/FAISS or keyword search sufficient")

    # ── RULE 3: Structured queries → NO ──────────────────────────
    # SQL / search engine beats vector on precision for structured data.
    elif profile.data_type == DataType.STRUCTURED:
        rules_matched.append("R3_STRUCTURED_DATA")
        reasons.append("Structured data — SQL/search engine preferred over vector DB")

    # ── RULE 4: Persistent + big + high Q → YES ───────────────────
    elif (
        profile.lifetime == Lifetime.PERSISTENT
        and profile.n_docs >= 50000
        and profile.q_total >= 10000
    ):
        use_vector_db = True
        rules_matched.append("R4_BIG_PERSISTENT_HIGH_Q")
        reasons.append(
            f"Persistent {profile.n_docs} docs, "
            f"{profile.q_total} queries — dedicated vector DB warranted"
        )

    # ── RULE 5: Shared semantic KB → YES ─────────────────────────
    elif profile.shared and profile.data_type == DataType.UNSTRUCTURED:
        use_vector_db = True
        rules_matched.append("R5_SHARED_SEMANTIC_KB")
        reasons.append("Shared semantic knowledge base — vector DB for reusable embeddings")

    # ── RULE 6: Hybrid engine available → MAYBE (no external vec DB)
    elif profile.has_hybrid_engine:
        rules_matched.append("R6_HYBRID_ENGINE_EXISTS")
        reasons.append("Hybrid search engine already present — no separate vector DB needed")

    # ── RULE 7: One-DB preference → PG + pgvector ─────────────────
    elif profile.n_docs >= 1000 and profile.data_type != DataType.STRUCTURED:
        use_pgvector = True
        rules_matched.append("R7_PGVECTOR_FALLBACK")
        reasons.append("Moderate corpus — pgvector in Postgres sufficient, no extra infra")

    # Default: in-memory
    else:
        use_in_memory = True
        rules_matched.append("DEFAULT_IN_MEMORY")
        reasons.append("Default fallback — in-memory sufficient for this profile")

    # Build recommendation string
    if use_vector_db:
        rec = "Dedicated vector DB (Qdrant, Weaviate, Pinecone, etc.)"
    elif use_pgvector:
        rec = "Postgres + pgvector (single DB, ACID + vectors)"
    elif use_in_memory:
        rec = "In-memory KNN (NumPy, FAISS) or context-only"
    else:
        rec = "SQL / search engine / keyword (no vectors needed)"

    return VectorDBDecision(
        use_vector_db=use_vector_db,
        use_pgvector=use_pgvector,
        use_in_memory=use_in_memory,
        recommended=rec,
        rules_matched=rules_matched,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DECISION TABLE (for documentation / AAA cockpit display)
# ═══════════════════════════════════════════════════════════════════════════════

DECISION_TABLE = [
    {
        "scenario": "Per-session PDF chat",
        "n_docs": "<5k",
        "q_total": "<1k",
        "lifetime": "ephemeral",
        "data_type": "unstructured",
        "decision": "NO — in-memory KNN",
        "rule": "R1",
    },
    {
        "scenario": "Team wiki / shared docs",
        "n_docs": "10k–200k",
        "q_total": "10k–100k+",
        "lifetime": "persistent",
        "data_type": "unstructured",
        "decision": "YES — vector DB or hybrid engine",
        "rule": "R4/R5",
    },
    {
        "scenario": "App DB logs / analytics",
        "n_docs": "10k–1M rows",
        "q_total": "1k–5k",
        "lifetime": "persistent",
        "data_type": "structured",
        "decision": "NO — SQL / search engine",
        "rule": "R3",
    },
    {
        "scenario": "Multi-tenant product docs",
        "n_docs": "50k–1M",
        "q_total": ">50k",
        "lifetime": "persistent",
        "data_type": "unstructured",
        "decision": "YES — dedicated vector DB",
        "rule": "R4",
    },
    {
        "scenario": "Prototype RAG (tiny)",
        "n_docs": "<10k",
        "q_total": "<5k",
        "lifetime": "experimental",
        "data_type": "unstructured",
        "decision": "NO — pgvector or FAISS",
        "rule": "R7/DEFAULT",
    },
    {
        "scenario": "arifOS semantic memory (L3)",
        "n_docs": "50k+",
        "q_total": ">50k",
        "lifetime": "persistent",
        "data_type": "unstructured",
        "decision": "YES — Qdrant (already deployed)",
        "rule": "R4/R5",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# AGENTIC SEARCH HOOK
# ═══════════════════════════════════════════════════════════════════════════════

def decide_for_agentic_search(
    corpus_name: str,
    n_docs: int,
    n_queries_expected: int,
    persistent: bool = False,
    structured: bool = False,
    shared: bool = False,
) -> dict[str, Any]:
    """
    Quick decision hook for agentic search at query time.
    Returns a decision dict suitable for telemetry.
    """
    profile = CorpusProfile(
        name=corpus_name,
        n_docs=n_docs,
        q_total=n_queries_expected,
        lifetime=Lifetime.PERSISTENT if persistent else Lifetime.EPHEMERAL,
        data_type=DataType.STRUCTURED if structured else DataType.UNSTRUCTURED,
        shared=shared,
    )
    decision = should_use_vector_db(profile)
    return {
        "corpus": corpus_name,
        "use_vector_db": decision.use_vector_db,
        "use_pgvector": decision.use_pgvector,
        "use_in_memory": decision.use_in_memory,
        "recommended": decision.recommended,
        "rules_matched": decision.rules_matched,
    }
