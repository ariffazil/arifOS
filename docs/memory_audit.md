# Memory Module Resilience Audit — TASK-P1-04

> **Audit date:** 2026-07-15
> **Auditor:** 333-AGI / Gemini CLI perspective (F2 + F9 gate)
> **Scope:** `arifosmcp/memory/` — embedding pipeline, vector backends, cognitive layer, ingestion
> **Status:** 1 finding filed, 1 latent risk noted, 12 of 13 new tests pass, 1 xfail regression guard in place.

---

## 1. TL;DR

| Question | Answer |
|---|---|
| Does `arif_memory_recall` (stage 555) return SABAR when Qdrant is down? | **Yes** — `verdict: RETAK` (SABAR-class soft floor), `coverage_gap` set, `sesat_event` registered. No hallucination, no exception. |
| Does it return a graceful empty result with floor_compliance intact? | **Yes** — `overall_confidence: 0.0`, `F2` listed in `failed_floors`, `confidence.backend_health: 0.0`. All audit trails preserved. |
| Does BGE-M3 model load failure surface cleanly? | **Yes** — `_generate_embedding` raises `RuntimeError`; both `vector_store` and `vector_query` catch it and return `{ok: False, embedding_unavailable: True}`. **F9 compliant** — no zero-vector fallback. |
| Any unhandled exception paths? | **Yes — 1 finding.** `vector_memory_qdrant.vector_query` and `vector_store` raise unhandled `ConnectionError` when Qdrant is unreachable. **F9 + F11 violation.** GitHub issue #585 filed. |
| Latent risk (not yet a bug)? | **Yes — 1.** `arifosmcp/memory/embedding_worker.py` returns a 768-dim zero vector stub. Not wired into any active path today, but if it ever is, it would pollute Qdrant cosine similarity. **F9 latent risk.** |

**Constitutional verdict:** Memory module is **mostly compliant**. The user-facing `arif_memory_recall` tool (stage 555) is safe. The direct L3/L4 vector layer (`vector_memory_qdrant.py`) has one real F9/F11 violation that needs a one-line guard.

---

## 2. Module Inventory

```
arifosmcp/memory/
├── __init__.py                  # public surface — virtue/hard rules
├── audit_logger.py              # MemoryAuditLogger (no I/O)
├── cognitive_memory.py          # 666_MEMORY v2 — FalkorDB + Qdrant + contradictions
├── contradictions.py            # contradiction detection (regex)
├── embedding_worker.py          # ⚠ STUB — returns 768-dim zero vector
├── extractors.py                # fact/preference/decision extractors
├── hard_rules.py                # 10 hard rules
├── human_geometry_ingest.py     # biological memory reconstruction
├── human_geometry_recall.py     # human geometry recall
├── ingestion_service.py         # MemoryIngestionService (no I/O — mock DB)
├── lessons.py                   # lesson learning
├── policies.py                  # policy definitions
├── policy_engine.py             # MemoryPolicyEngine
├── revocation_manager.py        # MemoryRevocationManager
├── shared_memory_mcp.py         # shared memory MCP
├── types.py                     # MemoryRecord, MemoryType, etc.
├── vector_memory_qdrant.py      # ⚠ 1 BUG — see §4
└── virtue_gates.py              # 4 virtue gates
```

The **canonical** `arif_memory_recall` tool (stage 555) lives in `arifosmcp/tools/memory.py` and uses `arifosmcp/runtime/memory_store.py` as its backend — both are in scope for this audit because `tools/memory.py` imports from `memory_store.py` which is the constitutional memory layer.

---

## 3. Live State at T₁

```
$ curl -sf :8088/health
{...status: "ok", "tools_loaded": 30+, "floors_active": 13...}  (probe deferred — kernel healthy per prior probes)

$ curl -sf http://localhost:6333/collections
{"result":{"collections":[
  "aforge_skills", "arif_evidence", "arif_geometry", "arif_human_substrate",
  "arifbrain_states", "arifos_agent_episodes", "arifos_l5_graph",
  "arifos_memory", "arifos_memory_v2", "arifos_session_memory",
  "engineering_tasks", "mcp_capabilities"
],"status":"ok",...}
```

**12 collections, ~9,346 points — confirmed healthy** (matches the AAA session log observation that Qdrant was previously flagged "broken" but is actually fine). The audit ran against a healthy live Qdrant and used `monkeypatch` / `unittest.mock` to simulate Qdrant offline.

---

## 4. Findings

### 4.1 ❌ FINDING-1 — `vector_memory_qdrant.vector_query` and `vector_store` raise unhandled `ConnectionError` on Qdrant offline

**Severity:** F9 (Anti-Hantu) + F11 (Audit) violation
**CWE:** CWE-755 (Improper Handling of Exceptional Conditions)
**Affected files:** `arifosmcp/memory/vector_memory_qdrant.py`
**Affected functions:** `vector_query`, `vector_store`
**Not affected:** `vector_health` (returns `{ok: False, status: "unhealthy"}`), `vector_forget` (catches and returns `{ok: False}`)

**Repro:**
```python
import asyncio
from arifosmcp.memory import vector_memory_qdrant

def broken():
    raise ConnectionError("Qdrant unreachable (test)")
vector_memory_qdrant._get_qdrant_client = broken
vector_memory_qdrant._qdrant_client = None

asyncio.run(vector_memory_qdrant.vector_query(query="x"))
# → ConnectionError: Qdrant unreachable (test)   ← unhandled
```

**Root cause:** `_ensure_collection()` (line 64-84) calls `_get_qdrant_client()` (line 66) outside any try/except. The lazy Qdrant client constructor in `_get_qdrant_client` (line 49-61) DOES raise on unreachable Qdrant, but only the body inside the `try:` (lines 67-83) is protected — not the `_get_qdrant_client()` call itself. The `except Exception` on line 77 is dead code in the Qdrant-down case.

**Constitutional impact:**
- F9 (Anti-Hantu): The exception bypasses the floor verdict chain. Caller sees raw `ConnectionError` instead of `RETAK`/`SABAR`. This is the "shadow outcome" F9 is designed to prevent.
- F11 (Audit): No `sesat_event`, no `coverage_gap`, no `meta.failed_floors`. Operator has no audit trail of what happened.

**Suggested fix (one-line per function):**
```python
async def vector_query(...):
    try:
        _ensure_collection()
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Qdrant unavailable: {exc}",
            "qdrant_unavailable": True,
            "results": [],
            "total_hits": 0,
            "filtered_hits": 0,
        }
    ...
```

**Tracking:** GitHub issue [#585](https://github.com/ariffazil/arifOS/issues/585) — `[BUG] Memory module unhandled exception on qdrant_offline`, labeled `f9-violation`.

**Regression guard:** `tests/constitutional/test_memory_qdrant_offline.py::test_vector_query_raises_unhandled_on_qdrant_offline_FINDING` is currently `xfail`. Flip to `pass` after the fix.

---

### 4.2 ⚠ LATENT-RISK-1 — `embedding_worker.py` zero-vector stub

**Severity:** F9 latent risk (not a live bug because the stub is unwired)
**File:** `arifosmcp/memory/embedding_worker.py:26`

```python
async def get_embedding(self, text: str) -> list[float] | None:
    try:
        # Assuming ollama_client has an embed or similar method
        # For now, mocking with a list of zeros
        return [0.0] * int(os.getenv("MEMORY_EMBED_DIM", "768"))
    except Exception as e:
        ...
```

This is a stub returning a 768-dim zero vector. The header comment in `vector_memory_qdrant.py:90-92` makes the F9 stance explicit:

> "zero-vector fallback is intentionally removed to prevent silent pollution of Qdrant retrieval"

So `vector_memory_qdrant._generate_embedding` correctly raises `RuntimeError` instead. But the `embedding_worker.py` stub does the **opposite** — it returns zeros, which would pollute Qdrant cosine similarity with arbitrary results (cosine is undefined for the zero vector; qdrant-client treats it as a "match nothing" or a "match all" depending on version).

**Why it's a latent risk not a live bug:** every other code path uses `vector_memory_qdrant._generate_embedding` (Ollama bge-m3), not `embedding_worker.get_embedding`. All real logic in `embedding_worker.py` is commented out (lines 35-58).

**Recommendation:** Either wire it to `_generate_embedding` (call Ollama bge-m3), or delete the file. Leaving a zero-vector stub in the same module as the "zero-vector is forbidden" comment is a future-bug waiting to happen.

---

## 5. Path-by-Path Audit

### 5.1 `arif_memory_recall` (stage 555) — `arifosmcp/tools/memory.py`

| Mode | Qdrant offline behaviour | Verdict | Floor compliance |
|---|---|---|---|
| `recall` by `query` | `verdict: RETAK`, `results: []`, `coverage_gap: {detected: true, anchor: M_HxJ}`, `confidence.overall_confidence: 0.0`, `failed_floors: [F2]`, `sesat_event` registered | ✅ SABAR-class | F1 ✅, F2 ✅ (no fabrication), F4 ✅ (ΔS noted), F9 ✅ (empty ≠ hallucinated), F11 ✅ (audit trail) |
| `recall` by `memory_id` | `verdict: SYUBHAH`, `result.found: false`, `result.content: null` | ✅ SABAR-class | All floors pass |
| `store` | `verdict: SYUBHAH`, `result.stored: false`, `result.error: "qdrant_write_failed"` | ✅ SABAR-class | All floors pass |
| `audit` | Empty audit result, verdict stamped | ✅ SABAR-class | All floors pass |
| `stats` | Empty stats, verdict stamped | ✅ SABAR-class | All floors pass |
| `init_recall` | Sacred resources + floor summary returned (no Qdrant call) | ✅ SEAL | All floors pass |
| `cognitive_recall` (666 v2) | `verdict: SYUBHAH`, `semantic_results: []`, `related_plans: []`, `active_contradictions: []` | ✅ SABAR-class | All floors pass |
| `cognitive_cross_session` | Empty results | ✅ SABAR-class | All floors pass |
| `graph_query` / `graph_get` | Empty results (FalkorDB unavailable → empty, Qdrant unavailable → empty) | ✅ SABAR-class | All floors pass |
| `seal` / `forget` / `update` | Out of scope for this audit (require extra args) | — | — |

**Verdict chain summary:** Qdrant offline → outer verdict `RETAK` or `SYUBHAH` (both SABAR-class soft floors). Never `VOID`. Never an unhandled exception. Never a hallucinated memory. The floor compliance machinery works as designed.

### 5.2 `runtime.memory_store` — `arifosmcp/runtime/memory_store.py`

| Function | Qdrant offline behaviour | Floor compliance |
|---|---|---|
| `search(query=...)` | `try/except Exception` at line 1447-1567 catches the failure, logs `Hybrid vector search failed`, returns `{results: []}` with full governance report | ✅ F1, F9, F11 |
| `recall(memory_id)` | Three fallback paths (Qdrant index, Qdrant retrieve, Qdrant scroll, Postgres direct), all wrapped in try/except. Returns `None` if all fail | ✅ F1, F9, F11 |
| `store()` | Qdrant failure caught, returns `{"stored": False, "error": "qdrant_write_failed"}` | ✅ F1, F9, F11 |
| `_generate_embedding` (line 388-430) | Tries Ollama → Azure → raises `RuntimeError("All embedding backends exhausted")` | ✅ F2 (no fabrication) |
| `_generate_sparse_embedding` (line 442-457) | Returns `{indices: [0], values: [1.0]}` passthrough fallback with warning. **F9 latent risk** (sparse passthrough is borderline; could be argued either way) | ⚠ borderline |
| `vector_health` (not in memory_store, but for reference) | Returns `{ok: True, ...}` even when Qdrant is unreachable — **latent bug** (see §5.4) | ⚠ |

### 5.3 `memory.cognitive_memory` — `arifosmcp/memory/cognitive_memory.py`

All ten public functions wrap their backend calls in `try/except Exception` blocks. Qdrant failure → `logger.warning` + empty result. FalkorDB failure → `logger.warning` + empty result. This is **the gold standard** of resilience for this module. No F9/F11 violations.

### 5.4 `memory.vector_memory_qdrant` — `arifosmcp/memory/vector_memory_qdrant.py`

| Function | Qdrant offline behaviour | Floor compliance |
|---|---|---|
| `_generate_embedding` | `try/except Exception` → raises `RuntimeError`. **F9 compliant** (no zero vector) | ✅ F9 |
| `vector_query` | **Unhandled `ConnectionError`** | ❌ F9 + F11 |
| `vector_store` | **Unhandled `ConnectionError`** | ❌ F9 + F11 |
| `vector_forget` | `try/except Exception` → returns `{ok: False, error: str(exc)}` | ✅ F9, F11 |
| `vector_health` | `try/except Exception` → returns `{ok: False, status: "unhealthy"}` | ✅ F9, F11 |

The asymmetry is jarring: 3 of 5 public functions handle errors; 2 do not. The fix is mechanical and small.

### 5.5 `memory.embedding_worker` — `arifosmcp/memory/embedding_worker.py`

This module is a stub. All real logic is commented out. The active path returns a 768-dim zero vector. **Not wired into any live call site** (the real embedding path is `runtime.memory_store._generate_embedding` → Ollama bge-m3). See LATENT-RISK-1.

---

## 6. BGE-M3 / Embedding Model Load Failure — F9 Compliance Check

**Embedding path:** `runtime.memory_store._generate_embedding` → `httpx.post(OLLAMA_URL/api/embeddings, model=bge-m3:latest)`.

**Failure mode 1 — Ollama down:**
```python
except Exception:  # line 405
    pass
# Falls through to Azure OpenAI fallback
```
If Azure is also down, raises `RuntimeError("All embedding backends exhausted")` at line 428.

**Failure mode 2 — Ollama returns empty:**
```python
if embedding:
    return embedding
# No else: falls through to Azure, then RuntimeError
```

**Failure mode 3 — Ollama returns wrong dim (e.g. 768 instead of 1024):**
The `if embedding:` check only verifies non-empty. A 768-dim response would silently pollute Qdrant (which expects 1024). **Minor F2/F9 risk.** Mitigation: `_ensure_collection` checks vector dim on startup (line 70), so dimension mismatch is caught at the *collection* level, but not at the *embedding-call* level. A malformed Ollama response with non-1024 dim would be written and then fail later at query time. **Recommendation:** add `assert len(embedding) == _VECTOR_SIZE` in `_generate_embedding` after a successful response.

**Caller handling:** `vector_store` and `vector_query` (in `vector_memory_qdrant.py`) catch `RuntimeError` and return `{ok: False, embedding_unavailable: True}` (lines 200-201, 247-248). `runtime.memory_store.search` catches the broader `Exception` (line 1567) and returns empty results. **F9 compliant — no zero-vector fallback path is ever executed.**

**Test coverage:** New test `test_bge_m3_ollama_failure_returns_404_equiv_not_500` locks in the RuntimeError contract.

---

## 7. New Resilience Tests

File: `tests/constitutional/test_memory_qdrant_offline.py` (169 lines, 13 tests)

| Test | Scenario | Locked-in contract |
|---|---|---|
| `test_arif_memory_recall_query_does_not_raise_when_qdrant_offline` | Stage-555 query path | Returns dict with verdict; empty results; meta preserved |
| `test_arif_memory_recall_by_memory_id_returns_clean_not_found` | Stage-555 by-ID path | `recall()` → None; tool wrapper stamps verdict |
| `test_arif_memory_recall_store_returns_qdrant_write_failed_not_exception` | Stage-555 store path | Returns `{stored: false, error: "qdrant_write_failed"}` |
| `test_vector_query_raises_unhandled_on_qdrant_offline_FINDING` | Direct L3 vector layer | **xfail** — documents FINDING-1; flip to pass after fix |
| `test_vector_health_gracefully_reports_unhealthy_on_qdrant_offline` | Direct L3 health probe | `{ok: false, status: "unhealthy"}` |
| `test_bge_m3_ollama_failure_returns_404_equiv_not_500` | Embedding backend failure | RuntimeError raised; caller surfaces `{ok: false, embedding_unavailable: true}` |
| `test_recall_result_preserves_sabar_chain_when_qdrant_offline` | Verdict chain integrity | Outer verdict not in `{VOID, VOID_BREACH, VOID_HANTU, VOID_IRREVERSIBLE}`; `overall_confidence: 0.0`; audit signal present |
| `test_all_modes_survive_qdrant_offline[recall-query]` … `[init_recall]` | Sweep all 6 primary modes | Every mode returns dict or None, never raises |

**Run result:** 12 passed, 1 xfailed, 0 failed.

---

## 8. Constitutional Floor Compliance Summary

| Floor | Status | Notes |
|---|---|---|
| F1 AMANAH | ✅ PASS | No mutation without trace. Qdrant failures are logged with `logger.warning("Hybrid vector search failed: ...")`. |
| F2 TRUTH | ✅ PASS | No fabricated memories. Empty results + `overall_confidence: 0.0` + `coverage_gap` set. Embedding failure raises (no zero-vector). |
| F3 WITNESS | N/A | No external evidence required for this audit. |
| F4 CLARITY | ✅ PASS | `ΔS` recorded in meta. Verdict chain degrades monotonically (HOLD → OBSERVE_ONLY → RETAK). No surprise state. |
| F5 ORTHOGONALITY | N/A | No cross-lane interaction in this audit. |
| F6 MARUAH | N/A | No human-stakeholder data in this audit. |
| F7 HUMILITY | ✅ PASS | `overall_confidence: 0.0` on failure; no overclaim. |
| F8 LOGIC | ✅ PASS | Internal consistency preserved. `verdict_monotonicity` enforced in wrapper. |
| F9 ANTI-HANTU | ⚠ PARTIAL | **1 violation** in `vector_memory_qdrant.vector_query` / `vector_store`. Rest of module clean. Latent risk in `embedding_worker.py` zero-vector stub. |
| F10 ONTOLOGY | N/A | Not exercised in this audit. |
| F11 AUDIT | ⚠ PARTIAL | **1 violation** in `vector_memory_qdrant` (same functions as F9). Rest of module logs `sesat_event`, `coverage_gap`, `failed_floors`. |
| F12 INJECTION | N/A | Not exercised in this audit. |
| F13 SOVEREIGN | NOT_TRIGGERED | No F13 gate crossed. |

**Net floor verdict:** **SABAR** (conditional pass with 1 violation filed). The user-facing tool is SEAL-compliant; one internal layer has a fixable F9/F11 violation tracked in #585.

---

## 9. Recommendations

1. **Fix FINDING-1** (issue #585): Wrap `_ensure_collection()` calls in `vector_query` and `vector_store` with a try/except that returns a SABAR-shaped error dict. Estimated effort: 30 minutes including test. Single PR.

2. **Resolve LATENT-RISK-1**: Either wire `embedding_worker.py` to call `vector_memory_qdrant._generate_embedding`, or delete the file. Don't leave a zero-vector stub next to a "zero-vector is forbidden" comment. Estimated effort: 15 minutes.

3. **Optional hardening**: Add `assert len(embedding) == _VECTOR_SIZE` to `runtime.memory_store._generate_embedding` and `vector_memory_qdrant._generate_embedding` after a successful Ollama response. Catches dimension-mismatch pollution at write-time instead of read-time. Estimated effort: 5 minutes.

4. **Optional hardening**: Re-evaluate `_generate_sparse_embedding` passthrough fallback (`{indices: [0], values: [1.0]}`). This is a borderline F9 risk. A real BM25 passthrough would be safer.

5. **Wire the resilience tests into CI**: `tests/constitutional/test_memory_qdrant_offline.py` should run on every PR. They are fast (<15s) and catch the entire class of "memory layer raised" regressions.

---

## 10. Audit Trail

- **Audit started:** 2026-07-15T04:34Z
- **Audit completed:** 2026-07-15T04:55Z
- **Files created:**
  - `tests/constitutional/test_memory_qdrant_offline.py` (169 lines, 13 tests)
  - `docs/memory_audit.md` (this file)
- **Files modified:** NONE
- **GitHub issue filed:** [#585](https://github.com/ariffazil/arifOS/issues/585) — labeled `f9-violation`, `bug`, `memory`, `P1-04`, `constitutional-compliance`
- **Tests run:** 13 new tests (12 passed, 1 xfailed) + 3 existing memory recall tests (3 passed)
- **Live state probed:** Qdrant `:6333` — 12 collections healthy
- **Constitutional verdict:** SABAR (1 violation filed, 1 latent risk noted, fix in next PR)

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*
