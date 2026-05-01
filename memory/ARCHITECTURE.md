# OPENCLAW Memory Architecture — Canonical Spec
**Epoch:** 2026-04-29T09:02:00+08:00 | **Authority:** ARIF | **Version:** 1.0

---

## 1. Canonical Principle

> Files are truth. Vector index is retrieval aid. Memory must be forged, not assumed.

Every memory entry has exactly one owner file. The vector store is a search index over those files — not a separate source of truth. Delete the file, the memory is gone. Delete Qdrant, the memory survives in markdown.

---

## 2. The 5-Layer Stack

```
┌─────────────────────────────────────────────────────────┐
│  L4  REFLECTIVE  │  DREAMS.md  │  wiki/dreams/         │
│                   │  Weekly synthesis + contradiction   │
│                   │  detection. Promotion gate.        │
├───────────────────┼─────────────┼───────────────────────┤
│  L3  PROCEDURAL   │  memory/    │  tool_patterns/       │
│                   │  procedures/│  runbooks/             │
│                   │  Repeated tool sequences become     │
│                   │  reusable SOPs. F8 Genius gate.     │
├───────────────────┼─────────────┼───────────────────────┤
│  L2  SEMANTIC     │  MEMORY.md  │  wiki/pages/          │
│                   │  wiki/pages/ │  claims/              │
│                   │  Stable facts. Human-curated or     │
│                   │  L1→L2 promoted. F2 Truth gate.    │
├───────────────────┼─────────────┼───────────────────────┤
│  L1  EPISODIC     │  memory/    │  YYYY-MM-DD.md        │
│                   │  daily/     │  Session transcripts   │
│                   │  (indexed to Qdrant)               │
├───────────────────┼─────────────┼───────────────────────┤
│  L0  WORKING      │  Live context│  Session scope only   │
│                   │  window +   │  Not persisted.       │
│                   │  .working/  │  Lost on compaction.  │
└───────────────────┴─────────────┴───────────────────────┘
         ↑ promote via gate         ↓ recall via search
         (F1-F13 governance)        (hybrid vector+BM25)
```

---

## 3. Vector Retrieval Pipeline

```
memory_search("query")
    ↓
Ollama bge-m3 (1024-dim cosine) ← local, sovereign
    ↓
Qdrant ANN search (openclaw_memory collection)
    ↓
F2 truth filter: truth_score ≥ 0.99
    ↓
F10 ontology check: no consciousness claims
    ↓
Temporal decay: recency_weight = e^(-age_days / 30)
    ↓
MMR dedup: Maximal Marginal Relevance, λ=0.3
    ↓
Ranked results with layer tags (L1/L2/L3)
```

**Qdrant collection:** `openclaw_memory` | **Dimension:** 1024 | **Distance:** Cosine
**Embedding model:** Ollama bge-m3:latest | **URL:** http://ollama_engine:11434

---

## 4. Layer Definitions

### L0 — Working Memory
- **Location:** Live session context (RAM, not disk)
- **Written by:** System during conversation
- **Retrieval:** Auto-injected into context window
- **TTL:** End of session, lost on compaction

### L1 — Episodic Memory
- **Location:** `memory/YYYY-MM-DD.md` + indexed in Qdrant
- **Written by:** `memory_append` (auto-daily + event-driven)
- **Retrieval:** `memory_search` (vector+BM25 hybrid)
- **Auto-loaded:** Today + yesterday files at session start
- **Qdrant tags:** `layer=L1`, `session_id`, `date`, `ontology_class`
- **TTL:** Archived to `wiki/pages/YYYY-MM/` after 30 days

### L2 — Semantic Memory
- **Location:** `MEMORY.md` (sovereign facts) + `wiki/pages/claims/`
- **Written by:** Human curation OR L1→L2 promotion gate
- **Retrieval:** `memory_search` (persistent across sessions)
- **Promotion gate:**
  - F2 Truth: claim verified against source
  - F4 Clarity: one-paragraph distillate
  - F7 Humility: marked "approximate, verify on use"
  - Non-contradiction: no existing L2 fact contradicts it
- **Qdrant tags:** `layer=L2`, `claim_type=INDUCTED|HUMAN_CURATED`

### L3 — Procedural Memory
- **Location:** `memory/procedures/<task-name>.md`
- **Written by:** Human curation OR L1 pattern extraction
- **Trigger:** Same tool sequence used 3+ times successfully
- **Retrieval:** `memory_search` with `layer=L3` filter
- **Promotion gate:**
  - F8 Genius: minimal, elegant steps
  - F12 Injection: no raw command without verification
  - F1 Amanah: documented revert/undo path
- **Qdrant tags:** `layer=L3`, `tool_sequence`, `success_count`

### L4 — Reflective Memory
- **Location:** `DREAMS.md` + `wiki/dreams/`
- **Written by:** Weekly cron consolidation
- **Trigger:** End of week OR manual dream trigger
- **Process:**
  1. Read last 7 days of `memory/YYYY-MM-DD.md`
  2. Detect: contradictions, repeated claims, open loops
  3. Write synthesis to `DREAMS.md`
  4. Flag: L1→L2 promotion candidates
  5. Flag: stale procedures for archive
- **Governance:** F2 (truth), F7 (humility) — no new facts, only synthesis

---

## 5. Promotion Rules

### L1 → L2 (Episodic → Semantic)
```
Trigger: Same claim appears in 3+ episodic entries
         OR human adds [promote-to-l2] tag

Gate check (all must pass):
  [ ] F2: Source verified, truth_score ≥ 0.99
  [ ] F4: distillable to one paragraph
  [ ] F7: marked with confidence level
  [ ] F10: no ontology violations
  [ ] Non-contradiction: no existing L2 fact contradicts

Output: wiki/pages/claims/<claim-slug>.md
        Tags: claim_type=INDUCTED, confidence=MODERATE, sources=[episodic refs]
```

### L1 → L3 (Episodic → Procedural)
```
Trigger: Same tool_sequence appears 3+ times with success

Gate check (all must pass):
  [ ] F8: steps are minimal and correct
  [ ] F12: no injection-prone content
  [ ] F1: undo/revert path documented
  [ ] Verified: same outcome each time

Output: memory/procedures/<task-name>.md
        Tags: tool_sequence, success_count, last_verified
```

### L3 → L4 Archive (Procedural → Stale)
```
Trigger: Procedure not used in 60 days

Action: Move to wiki/archive/procedures/<task-name>.md
        Keep in Qdrant with layer=L3_STALE
```

---

## 6. Governance Separation

```
OPENCLAW memory    → task continuity, working context
                    NOT sealed, NOT governance-critical

arifOS VAULT999   → constitutional decisions, audit events
                    immutable, F1-F13 gated, human-sealed

WELL human state   → biometric telemetry
                    truth_status=VOID until Arif confirms

Rule: If it influences a governance verdict,
      it must come from VAULT999, not OpenClaw memory.
```

---

## 7. extraPaths — What Gets Indexed

Default (always indexed):
- `MEMORY.md`
- `memory/*.md` (excluding procedures/)
- `memory/YYYY-MM-DD.md`

Extended (procedural + project docs):
- `memory/procedures/*.md`
- `wiki/pages/*.md`
- `docs/runbooks/*.md`
- `briefings/*.md`
- `GEOX/**/*.md` (MCP architecture docs)

---

## 8. Tools and Retrieval

| Tool | Backend | Scope |
|---|---|---|
| `memory_search` | Ollama bge-m3 → Qdrant | L1+L2+L3 indexed content |
| `memory_get` | Direct file read | Any file by path |
| `memory_append` | Markdown + Qdrant | L1 episodic only |
| `arif_memory_recall` (MCP) | vector_query → F2/F10 filter | L1+L2 |

---

## 9. Canonical Files

```
memory/
  ARCHITECTURE.md          ← This file. The memory constitution.
  PROMOTION_RULES.md       ← Gate criteria for layer promotion.
  PROGRESS.md              ← What has been built and tested.
  2026-04-29.md            ← Today: architecture deployed here.
  procedures/              ← L3: tool patterns and SOPs.
    README.md              ← L3 index and entry point.
    _template.md           ← Procedure template with frontmatter.
  daily/                   ← L1: daily episodic notes (new location).
  wiki/
    dreams/                ← L4: weekly dream output.
    claims/                ← L2: promoted semantic facts.

wiki/pages/
  Concept_OpenClaw_Memory_Architecture.md  ← L2 canonical entry.
```

---

## 10. DITEMPA BUKAN DIBERI

Memory is not given. It is forged — layer by layer, gate by gate.

Every entry must earn its layer. Every promotion must pass the floor check.

**Version:** 1.0 | **Sealed:** 2026-04-29 | **Authority:** ARIF
