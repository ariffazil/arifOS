---
title: OPENCLAW Memory Architecture
layer: L2
strand: memory
audience: all
difficulty: intermediate
prerequisites: []
status: active
claim_type: CANONICAL
confidence: HIGH
---

# Concept: OPENCLAW Memory Architecture

**Layer:** L2 Semantic | **Type:** Architecture Specification | **Version:** 1.0

---

## Summary

OPENCLAW memory is a 5-layer cognitive architecture built on markdown files as canonical truth and Ollama bge-m3 vector embeddings in Qdrant as retrieval index.

**The stack:**
- L0: Working memory — live session context
- L1: Episodic — `memory/YYYY-MM-DD.md` + Qdrant indexed
- L2: Semantic — `MEMORY.md` + `wiki/pages/claims/`
- L3: Procedural — `memory/procedures/`
- L4: Reflective — `DREAMS.md` + `wiki/dreams/`

**Key principle:** Files are truth. Vector index is retrieval aid. Promotion between layers requires passing F1-F13 gates.

---

## Vector Pipeline

```
memory_search("query")
  → Ollama bge-m3 (1024-dim, cosine, local sovereign)
  → Qdrant ANN (openclaw_memory collection)
  → F2 truth filter (τ ≥ 0.99)
  → F10 ontology check
  → Temporal decay (e^(-age/30))
  → MMR dedup (λ=0.3)
  → Ranked results with layer tags
```

**Embedding model:** Ollama bge-m3 | **Dimension:** 1024 | **Distance:** Cosine

---

## Layer Details

### L1 — Episodic Memory
- **Location:** `memory/YYYY-MM-DD.md`
- **Indexing:** Indexed in Qdrant with layer=L1 tag
- **Auto-load:** Today + yesterday at session start
- **TTL:** 30 days → archived to `wiki/pages/YYYY-MM/`

### L2 — Semantic Memory
- **Location:** `MEMORY.md` + `wiki/pages/claims/`
- **Promotion:** L1→L2 gate requires F2 (τ≥0.99), F4, F7, F10, non-contradiction
- **Authority:** Persistent across sessions

### L3 — Procedural Memory
- **Location:** `memory/procedures/`
- **Promotion:** L1→L3 requires same tool sequence 3+ times + F8+F12+F1 gates
- **Purpose:** Reusable SOPs from verified repetition

### L4 — Reflective Memory
- **Location:** `DREAMS.md` + `wiki/dreams/`
- **Trigger:** Weekly cron consolidation
- **Output:** Synthesis, not new facts. Contradiction detection + pattern recognition.

---

## Governance Separation

| System | Purpose | Persistence |
|---|---|---|
| OPENCLAW memory | Task continuity | Session + markdown |
| arifOS VAULT999 | Constitutional audit | Immutable ledger |
| WELL telemetry | Biometric state | truth_status=VOID until confirmed |

**Rule:** If a memory influences a governance verdict, it must come from VAULT999 — not from OpenClaw markdown.

---

## Canonical Files

```
memory/
  ARCHITECTURE.md      ← Memory constitution
  PROMOTION_RULES.md   ← Layer gate criteria
  2026-04-29.md        ← This architecture deployed
  procedures/          ← L3 procedural SOPs
    README.md
wiki/pages/
  Concept_OpenClaw_Memory_Architecture.md  ← This page (L2)
```

---

## Retrieval Tools

| Tool | Backend | Scope |
|---|---|---|
| `memory_search` | Ollama bge-m3 + Qdrant | L1+L2+L3 indexed |
| `memory_get` | Direct file read | Any markdown file |
| `memory_append` | Markdown + Qdrant | L1 episodic |
| `arif_memory_recall` (MCP) | vector_query + F2/F10 | L1+L2 |

---

## Confidence: HIGH
**Source:** Verified end-to-end pipeline test 2026-04-29
**Valid until:** Superseded by revised architecture version
**Review:** After first L1→L2 promotion event
