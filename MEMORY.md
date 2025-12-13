# L7 Memory Layer Documentation

**Version:** v38.2-alpha
**Status:** Implemented
**Tests:** 81 passing (70 unit + 11 integration)

---

## Overview

The L7 Memory Layer provides **cross-session user context persistence** for arifOS using Mem0 + Qdrant as the backend. This layer enables the pipeline to recall relevant prior interactions at the start of processing (111_SENSE) and store outcomes at the end (999_SEAL).

**Key Principle:** Memory is governance, not just storage. What gets remembered is controlled by verdict through the EUREKA Sieve.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       arifOS Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│  000_VOID → 111_SENSE → ... → 888_JUDGE → 999_SEAL             │
│               ↓                              ↓                  │
│        ┌──────┴──────┐              ┌────────┴────────┐        │
│        │ L7 RECALL   │              │   L7 STORE      │        │
│        │ (memory.py) │              │ (EUREKA Sieve)  │        │
│        └──────┬──────┘              └────────┬────────┘        │
│               ↓                              ↓                  │
│        ┌──────┴──────────────────────────────┴──────┐          │
│        │           Mem0Client (mem0_client.py)      │          │
│        │     ┌─────────────────────────────────┐    │          │
│        │     │   Mem0 + Qdrant (External)      │    │          │
│        │     └─────────────────────────────────┘    │          │
│        └────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## EUREKA Sieve — TTL Policy

The EUREKA Sieve determines what gets stored based on the APEX verdict:

| Verdict | TTL | Storage Behavior |
|---------|-----|------------------|
| **SEAL** | Forever (None) | Canonical memory — stored permanently |
| **PARTIAL** | 730 days | Stored with hedged status |
| **888_HOLD** | 730 days | Awaiting human approval |
| **VETO** | 730 days | Stored for audit trail |
| **FLAG** | 30 days | Short-term retention |
| **SUNSET** | 30 days | Revocation event stored |
| **VOID** | 0 (never) | **Never stored** — immediate discard |
| **SABAR** | 0 (never) | **Never stored** — immediate discard |

**Core Rule:** VOID and SABAR verdicts are **never** written to cross-session memory.

---

## Pipeline Integration

### 111_SENSE — Recall

At the start of 111_SENSE, if a `user_id` is provided:

1. Query Mem0 for relevant prior interactions
2. Apply similarity threshold (default: 0.65)
3. Limit results (default: top 8)
4. Apply confidence ceiling (0.85) to all scores
5. Inject memories into `context_blocks` with caveat

```python
# From pipeline.py
if is_l7_enabled() and state.l7_user_id:
    state.l7_recall_result = recall_at_stage_111(
        query=state.query,
        user_id=state.l7_user_id,
    )
    # Memories are injected into context_blocks
```

**Confidence Ceiling:** All recalled memories are capped at 0.85 confidence because **memory is suggestion, not fact**.

### 999_SEAL — Store

At the end of 999_SEAL, if verdict is sievable:

1. Apply EUREKA Sieve to verdict
2. If storable (not VOID/SABAR), store to Mem0
3. Include job metadata (job_id, stakes_class, stage_trace)
4. Store result in `state.l7_store_result`

```python
# From pipeline.py
if is_l7_enabled() and state.l7_user_id and state.verdict:
    state.l7_store_result = store_at_stage_999(
        content=f"Query: {state.query}... Response: {state.raw_response}...",
        user_id=state.l7_user_id,
        verdict=state.verdict,
        metadata={"job_id": state.job_id, ...},
    )
```

---

## Fail-Open Design

L7 Memory is designed to **never break the pipeline**:

- If L7 is disabled → pipeline continues, recall returns empty
- If Mem0 throws exception → caught silently, pipeline continues
- If user_id is missing → L7 operations are skipped
- If Qdrant is unavailable → graceful degradation

```python
try:
    state.l7_recall_result = _l7_recall(...)
except Exception:
    # Fail-open: L7 errors don't break pipeline
    pass
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ARIFOS_L7_ENABLED` | `true` | Enable/disable L7 Memory |
| `MEM0_API_KEY` | (none) | Mem0 API key |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `ARIFOS_L7_SIMILARITY_THRESHOLD` | `0.65` | Similarity threshold for recall |
| `ARIFOS_L7_TOP_K` | `8` | Max memories to recall |

### Programmatic Configuration

```python
from arifos_core.memory import Mem0Config, Mem0Client, Memory

config = Mem0Config(
    enabled=True,
    similarity_threshold=0.70,
    top_k=10,
)

client = Mem0Client(config=config)
memory = Memory(client=client)
```

---

## User Isolation

**CRITICAL:** All memory operations are isolated by `user_id`.

- `search()` always filters by user_id
- `add()` always tags entries with user_id
- Cross-user memory access is **impossible** by design

```python
# Always include user_id
result = memory.recall_at_stage_111(
    query="What is Amanah?",
    user_id="user-123",  # REQUIRED
)
```

---

## API Reference

### Memory Class

```python
from arifos_core.memory import Memory

memory = Memory()

# Recall at 111_SENSE
result = memory.recall_at_stage_111(
    query="What is Amanah?",
    user_id="user-123",
    top_k=8,
    threshold=0.65,
)

# Store at 999_SEAL
result = memory.store_at_stage_999(
    content="User asked about governance",
    user_id="user-123",
    verdict="SEAL",
    metadata={"topic": "governance"},
)

# Apply EUREKA Sieve
sieve = memory.apply_sieve("SEAL")
print(sieve.should_store)  # True
print(sieve.ttl_days)      # None (forever)
```

### Convenience Functions

```python
from arifos_core.memory import (
    recall_at_stage_111,
    store_at_stage_999,
    apply_eureka_sieve,
    is_l7_enabled,
    is_l7_available,
)

# Check if L7 is enabled
if is_l7_enabled():
    result = recall_at_stage_111(query, user_id)
```

### RecallResult

```python
@dataclass
class RecallResult:
    memories: List[MemoryHit]
    total_found: int
    confidence_ceiling: float  # 0.85
    l7_available: bool
    error: Optional[str]

    @property
    def has_memories(self) -> bool: ...
    def to_context_injection(self) -> Dict[str, Any]: ...
```

### StoreAtSealResult

```python
@dataclass
class StoreAtSealResult:
    success: bool
    sieve_result: SieveResult
    memory_id: Optional[str]
    error: Optional[str]
```

### SieveResult

```python
@dataclass
class SieveResult:
    should_store: bool
    verdict: str
    ttl_days: Optional[int]  # None = forever, 0 = never
    reason: str
```

---

## Pipeline Usage

```python
from arifos_core.pipeline import Pipeline

pipeline = Pipeline()

# Run with user_id for L7 Memory
state = pipeline.run(
    query="What is Amanah?",
    user_id="user-123",  # Enables L7 Memory
)

# Check recall result
if state.l7_recall_result and state.l7_recall_result.has_memories:
    for mem in state.l7_recall_result.memories:
        print(f"Recalled: {mem.content} (score: {mem.score})")

# Check store result
if state.l7_store_result:
    print(f"Stored: {state.l7_store_result.success}")
    print(f"Sieve: {state.l7_store_result.sieve_result.reason}")
```

---

## Testing

### Run Unit Tests

```bash
pytest tests/unit/test_l7_memory.py -v
# 70 tests
```

### Run Integration Tests

```bash
pytest tests/integration/test_pipeline_with_memory.py -v
# 11 tests
```

### Run All L7 Tests

```bash
pytest tests/unit/test_l7_memory.py tests/integration/test_pipeline_with_memory.py -v
# 81 tests total
```

---

## Embedding

The `embed()` method generates vector embeddings for semantic search:

```python
from arifos_core.memory import Mem0Client

client = Mem0Client()
result = client.embed("What is Amanah?")

if result.success:
    print(f"Model: {result.model}")         # "mem0" or "stub-hash-384"
    print(f"Dimensions: {result.dimensions}")  # 384
    print(f"Vector: {result.embedding[:5]}...")
```

**Fallback Behavior:**
- If Mem0 available: Uses Mem0's embedding model
- If Mem0 unavailable: Uses deterministic stub embedding (hash-based)
- Stub embedding is normalized (L2 norm = 1.0)

---

## File Structure

```
arifos_core/memory/
├── mem0_client.py      # Mem0 + Qdrant client wrapper
├── memory.py           # L7 Memory layer with EUREKA Sieve
├── __init__.py         # Exports (updated for L7)
└── ...

tests/
├── unit/
│   └── test_l7_memory.py           # 70 unit tests
└── integration/
    └── test_pipeline_with_memory.py # 11 integration tests
```

---

## Invariants

| # | Invariant | Enforcement |
|---|-----------|-------------|
| **INV-L7-1** | VOID/SABAR verdicts NEVER stored | EUREKA Sieve |
| **INV-L7-2** | User isolation via user_id | Mem0Client filter |
| **INV-L7-3** | Confidence ceiling 0.85 | RecallResult |
| **INV-L7-4** | Fail-open on errors | try/except in pipeline |

---

## Future Work

- **Cohere Reranker:** Add reranking for improved relevance
- **Batch Operations:** Bulk recall/store for efficiency
- **Qdrant Direct:** Bypass Mem0 for more control
- **Memory Compaction:** Merge similar memories over time

---

**DITEMPA BUKAN DIBERI** — Forged, not given; memory must pass floors before it rules.
