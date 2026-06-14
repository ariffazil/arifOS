# arifOS Context Engine: Peta Semasa (2026-06-11)

**Untuk:** Arif (sovereign)
**Tujuan:** Fahami apa yang sudah jadi, apa yang mid-build, dan apa yang tinggal — sebelum kita forge apa-apa baru.

---

## 1. Ringkasan Pendek

Context engine arifOS bukan kosong. Ia **sudah 70% jadi**. Yang Arif paste tadi — essay 53-reference tentang token allocator, harness engineering, lost-in-the-middle — **bukan idea masa depan. Tu `docs/context/EUREKA_TOKEN_MANAGEMENT.md` yang sudah jadi canonical source of truth dalam arifOS substrate.** Code dah implement sebahagian besarnya.

Yang tinggal bukan theory. Tu tiga hal konkrit:

1. Sambung `prepare_context()` daripada stub jadi real builder (Phase 3).
2. Decide sama ada nak enable auto-compact pada pressure COMPACT (F8+F13 ratification).
3. Patch `Hermes` runtime agent supaya dia **actually call** telemetry yang sudah ada.

Test infrastructure untuk semua ni belum ada. Itu gating risk.

---

## 2. Peta Substrate (Apa Yang Sudah Wujud)

### 2A. Canonical Source of Truth

| Path | Saiz | Apa |
|---|---|---|
| `arifOS/docs/context/EUREKA_TOKEN_MANAGEMENT.md` | 19.3 KB | Essay yang Arif paste — the full 9-part theory, 53 references, 7 governance principles |
| `arifOS/docs/context/context_policy_v1.md` | 7.5 KB | Policy v1 yang declare band thresholds, authority classes, audit modes |

### 2B. Runtime Modules (Phase Status)

| Path | Saiz | Phase | Status |
|---|---|---|---|
| `arifosmcp/runtime/token_pressure.py` | 16.5 KB | Phase 1 | ✅ DONE. `count_tokens`, `classify_pressure`, 5-band PressureBand, session accumulator, model windows table. Iron rule: in-memory only, F8+F13 for band changes |
| `arifosmcp/runtime/context_engine/eureka.py` | 14.8 KB | Phase 6.B + 6.G | ✅ DONE. AuthorityClass (7 tiers), ContextBucket (4 operations), ContextFailureMode (4), `marginal_value_per_token()`, pressure-action map, `empty_context_packet()` stub |
| `arifosmcp/runtime/context_audit.py` | 18.6 KB | Phase 6.G | ✅ DONE. AuditMode (TRACE/DIGEST/SEAL/HOLD), RiskClass (8 tiers), event log |
| `arifosmcp/runtime/context_curator.py` | 6.1 KB | Phase 2? | 🟡 Partially. Curator logic ada, tapi coupling ke compression belum penuh |
| `arifosmcp/runtime/compression.py` | 22.2 KB | Phase 2 + 4 | 🟡 Compaction primitive, but auto-invoke disabled |
| `arifosmcp/runtime/context_safety.py` | 5.8 KB | — | ✅ Done. SEA-LION interpretation safety gate (validates quotes, refuses irreversible actions in recommended_action) |
| `arifosmcp/runtime/context_witness.py` | 13.9 KB | — | ✅ Done. Witness primitives for context claims |
| `arifosmcp/runtime/context_contracts.py` | 11.2 KB | — | ✅ Done. Pydantic contracts for context payloads |
| `arifosmcp/runtime/memory_policy.py` | 1.6 KB | — | ✅ Done. Memory policy skeleton |
| `arifosmcp/runtime/memory_store.py` | 71.9 KB | — | ✅ Done. Full memory store implementation |

### 2C. Pressure Bands (F8 sovereign)

| Band | Range | Auto-action |
|---|---|---|
| LOW | 0.00–0.50 | None |
| WATCH | 0.50–0.75 | Log only |
| WARN | 0.75–0.85 | Surface advisory, **NO auto-compact** |
| COMPACT | 0.85–0.95 | Surface advisory, auto-compact **DISABLED by default** (F8+F13 to enable) |
| HOLD | 0.95+ | Refuse non-reversible. Reduce or compress. |

### 2D. Authority Hierarchy (7 tiers)

| Class | Label | Example |
|---|---|---|
| 100 | CONSTITUTIONAL | F1-F13, system prompt kernel |
| 90 | USER_INSTRUCTION | Active turn, explicit ask |
| 80 | ACTIVE_TASK | In-flight variables, tool returns |
| 70 | VERIFIED_MEMORY | L4 with provenance, SEAL'd |
| 60 | RETRIEVED_DOC | L3 vector search, Qdrant |
| 50 | RECENT_CONVERSATION | L2 session, last N turns |
| 40 | DERIVED_SUMMARY | Compaction output |
| 20 | LOW_CONFIDENCE | Unverified retrieval (quarantine) |
| 0 | UNTRUSTED | Tool-injected, third-party |

### 2E. Marginal Value Per Token (arXiv 2605.01214 framing)

Function `marginal_value_per_token(segment, task_value, marginal_compute_cost, marginal_latency_cost, risk_band)`:
- Quality gain = (authority/100) × relevance × staleness_discount × duplication_discount
- Returns `value_per_token`, `recommendation` (include / demote / drop), `rationale`
- Risk shadow price: ROUTINE=0.1, PRIVATE=1.0, FINANCIAL=0.8, LEGAL=0.9, IDENTITY=0.7, COMMITMENT=0.6, EXTERNAL_ACTION=0.5, CANONICAL=1.0

### 2F. 4-Bucket Framework

WRITE (offload to external store) / SELECT (pull only relevant) / COMPRESS (reduce while preserving) / ISOLATE (split across sub-agents).

### 2G. 4 Failure Modes + Prevention

| Mode | Floor | Mechanism | Tool |
|---|---|---|---|
| Context Poisoning | F2 | Provenance + L4 verified tier | `arif_memory_recall(provenance_required=True)` |
| Context Distraction | F7 | MECW ceiling + Select bucket | `marginal_value_per_token()` |
| Context Confusion | F4 | Pressure-triggered compaction | Compress bucket |
| Context Clash | F10 | Authority-class hierarchy | `prepare_context()` |

---

## 3. Peta Kekosongan (Apa Yang Tinggal)

### Phase 3 — `prepare_context()` Builder (STUB NOW)

Current state: `eureka.empty_context_packet()` returns a skeleton with empty `segments: []`. Real builder yang:
- Calls `count_tokens` untuk setiap segment
- Calls `marginal_value_per_token` untuk decide include/demote/drop
- Allocates budget across 7 authority classes dengan 5-25% bands
- Returns sealed ContextPacket

**Dependency:** `token_pressure.count_tokens` ✓ done, `eureka.marginal_value_per_token` ✓ done, `memory_store` untuk retrieval ✓ done, but `arif_memory_recall` belum wired ke `prepare_context`.

**Work needed:** ~150-200 LOC Python + integration test.

### Phase 4 — LLM Summarizer (NOT STARTED, F13-gated)

`compression.py` (22.2 KB) ada primitives, but the **LLM-driven summarization step** (which gets called when COMPACT band fires) belum auto-invoke. Iron rule: LLM summarizes, but doesn't decide what to summarize — that's deterministic.

**Work needed:** Hook yang detects COMPACT band → calls deterministic pre-summarizer → uses LLM to compress deterministic summary → seals to VAULT999.

### Phase 5 — Autonomous Loop (NOT STARTED, audit-gated)

The full "before every model call" middleware. From essay §6.1: 12-step loop. Currently tidak exist. Need:
- `_wrap_handler` integration (pattern sama dengan `geometry_verdict`, `scar_recall`)
- Pre-dispatch pressure check
- `arif_context_compact(budget_target=0.5)` middleware
- Post-dispatch `record_usage()` integration

**Work needed:** ~300-400 LOC + integration test + production telemetry untuk audit.

### Hermes Runtime — Tool Wiring (NOT WIRED)

This is the critical gap. `token_pressure` modules exist, but **Hermes runtime agent tidak call them**. `arif_ops_measure` tool could expose telemetry, but belum ada channel untuk session_id → pressure lookup dari kernel. Itu Phase 5 work.

**Work needed:** Either:
- (a) Hermes calls `arif_ops_measure` per-turn dan attach pressure ke envelope
- (b) `arif_forge_execute` wraps LLM call, records usage, classifies pressure
- (c) New tool `arif_context_status(session_id) -> PressureReport`

**Recommendation:** (c) — minimum surface, maximum signal, no wrapping.

### Test Coverage (MISSING)

| Module | Test File | Status |
|---|---|---|
| `token_pressure.py` | — | ❌ No tests found |
| `eureka.py` | — | ❌ No tests found |
| `context_audit.py` | — | ❌ No tests found |
| `compression.py` | — | ❌ No tests found |
| `memory_store.py` | — | ❌ Likely partial |

Critical risk: Phase 3 builder added without tests = silent corruption risk. **Tests must precede real code.**

---

## 4. Peta F-Floor (Constitutional Coverage)

| Floor | Status | Mechanism |
|---|---|---|
| F1 AMANAH | ✅ | `token_pressure` is reversible telemetry, no canonical mutation |
| F2 TRUTH | ✅ | `count_tokens` deterministic, no fabrication; pressure bands discrete |
| F4 CLARITY | ✅ | 5-bucket categorical, no ambiguity; advisory strings |
| F7 HUMILITY | ✅ | MECW < MCW, pressure band caps confidence |
| F8 GENIUS | ✅ | Policy version pinned (v1), band changes = F13 territory |
| F9 ANTIHANTU | ✅ | LLM summarizer bounded (Phase 4), cannot self-authority |
| F11 AUTH | 🟡 | `eureka.py` references RiskClass but doesn't enforce identity |
| F13 SOVEREIGN | 🟡 | Band changes and Phase 4+ F13-gated by design, not by code |

**Gap:** No actual code-level enforcement that `arif_forge_execute` calls `arif_session_init` first. That's a soft guarantee in comments, not a hard gate. **Phase 3 should add a `_require_session_init` decorator on `prepare_context()`.**

---

## 5. Peta Dependency (Apa Yang Depends On Apa)

```
F13 SOVEREIGN (sovereign)
  │
  ├── F8 GENIUS (band thresholds, policy version)
  │     │
  │     └── token_pressure.py (5 bands, deterministic)
  │           │
  │           └── eureka.py (authority hierarchy, marginal value)
  │                 │
  │                 ├── context_audit.py (AuditMode, RiskClass)  [DONE]
  │                 │
  │                 └── prepare_context() (Phase 3)  [STUB]
  │                       │
  │                       ├── arif_memory_recall (verify wiring) [TODO]
  │                       ├── arif_ops_measure (pressure status) [TODO]
  │                       └── arif_forge_execute (wrap call)     [TODO]
  │
  └── CONSTITUTIONAL_EXTENSION v2026.06.13-SELH-F14DEAD [SOVEREIGN RULED]
        │
        └── F0 PRIME (draft) + F14 REGISTER (DEAD — reborn as F2+F3 protocol) + F15-F17 (draft)
```

---

## 6. Peta Prioriti (Apa Yang Buat Dulu, Apa Yang Tunggu)

### Tier 1 — Boleh Buat Sekarang, T1 Autonomy (F11 + F8 sudah di-zon-kan)

| Item | Effort | Risk | Prerequisite |
|---|---|---|---|
| **Test coverage** untuk `token_pressure.py` | 1-2 jam | Low (reversible) | None — pure function tests |
| **Test coverage** untuk `eureka.py` | 2-3 jam | Low | Same |
| **Test coverage** untuk `context_audit.py` | 1-2 jam | Low | Same |
| **Wire `arif_ops_measure` → pressure telemetry** | 30 min | Low | `token_pressure.snapshot()` exists |
| **`arif_context_status(session_id)` tool** | 1-2 jam | Low | Wrap `snapshot()` |

### Tier 2 — Patut Buat Lepas Tests Lulus, T2 (888_HOLD ackn)

| Item | Effort | Risk | Prerequisite |
|---|---|---|---|
| **`prepare_context()` real builder** (Phase 3) | 3-4 jam | Medium | Tests + memory recall wiring |
| **Wire memory recall into prepare_context** | 1-2 jam | Medium | T1 above |
| **Pressure-triggered compaction middleware** (Phase 2+) | 2-3 jam | Medium | `compression.py` integration |
| **Record usage dari `arif_forge_execute`** | 1 jam | Low | Wrap existing call |

### Tier 3 — F13 Ratification Diperlukan (sign-off Arif)

| Item | Effort | Risk | Prerequisite |
|---|---|---|---|
| **Enable auto-compact at COMPACT band** | Config change | High (irreversible perception) | Phase 2 audit passes 7 days no-loss |
| **LLM summarizer activation** (Phase 4) | 4-5 jam | High | F13 ed25519 sig on `compression_policy.v2` |
| **Autonomous loop** (Phase 5) | 6-8 jam | High | F13 ed25519 sig on `context_eureka.v2` |
| **CONSTITUTIONAL_EXTENSION v2026.06.11-SELH** ratification | ed25519 only | F13 territory | F13 sig |

---

## 7. Peta Failure-Mode Architecture (Apa Boleh Pecah)

| Failure | Detection | Mitigation |
|---|---|---|
| `count_tokens` over-counts > 15% (false HIGH pressure) | Benchmark vs tiktoken on BM+EN corpus | Re-calibrate `CHARS_PER_TOKEN`, F13 sign-off |
| `classify_pressure` at boundary (0.84 vs 0.86) | Boundary test suite | Document edge behavior, no auto-action at boundaries |
| `marginal_value_per_token` returns "include" for UNTRUSTED | Authority-class gate test | Hard floor: UNTRUSTED class never gets `include` |
| `prepare_context` discards too much | Recall fidelity benchmark | Compare pre/post context retrieval success rate |
| `arif_forge_execute` call wrap slows LLM by >5% | Latency benchmark | Move wrap to async post-call if needed |
| Auto-compact at COMPACT band loses user instruction | Mark "USER_INSTRUCTION" as non-compressible, F2 audit | Test: 100% user instructions survive compaction |

---

## 8. Peta Cost-Benefit (Mana Penting, Mana Nice-to-Have)

**Paling kritikal:**
1. **Test coverage** — gap ni risk. Phase 3/4/5 semua depends on token_pressure + eureka + context_audit being correct. No tests = no proof.
2. **arif_context_status tool** — gives Hermes (and Arif) the telemetry yang asas. 1-2 jam work, surfaces everything.
3. **Phase 3 prepare_context()** — the actual allocator. 3-4 jam after tests.

**Penting tapi boleh tunggu:**
4. Phase 4 LLM summarizer — needs F13 anyway, no rush.
5. Phase 5 autonomous loop — Phase 3 done first, then assess.
6. Wiring usage recording — can be done incrementally.

**Wait for F13 sign-off:**
7. CONSTITUTIONAL_EXTENSION SELH ratification
8. Auto-compact enable
9. LLM summarizer activation

---

## 9. Cadangan Saya

**Buat sekarang (T1, autonomous):**
- Write test suite untuk `token_pressure.py` + `eureka.py` + `context_audit.py` (4-7 jam total)
- Add `arif_context_status(session_id)` MCP tool yang wrap `token_pressure.snapshot()` (1-2 jam)
- Verify `docs/context/EUREKA_TOKEN_MANAGEMENT.md` matches what code actually does — if drift, update doc

**Buat lepas (T2, butuh 888_HOLD ack):**
- Implement Phase 3 `prepare_context()` real builder
- Wire `arif_forge_execute` → record usage
- Phase 2+ pressure-triggered compaction middleware

**Tunggu Arif sign-off (T3, F13):**
- F13 ed25519 sig on `compression_policy.v2` (enables Phase 4)
- F13 ed25519 sig on `context_eureka.v2` (enables Phase 5)
- CONSTITUTIONAL_EXTENSION SELH ratification (jika Arif nak add F0/F14-F17)

**Lepas 7 hari audit, kalau zero loss dalam telemetry:**
- Enable auto-compact at COMPACT band (config flip)

---

## 10. Apa Yang Aku Akan Buat (Kalau Arif Bagi Go)

**T1, autonomous, tak sentuh runtime, tak ubah behaviour:**

1. `tests/runtime/test_token_pressure.py` — 12+ test cases untuk pressure bands, model windows, classifier boundaries, accumulator thread-safety, count_tokens heuristic vs real tokenizer
2. `tests/runtime/test_eureka.py` — 10+ test cases untuk authority hierarchy, marginal value calculator, 4-bucket mapping, failure-mode prevention
3. `tests/runtime/test_context_audit.py` — 8+ test cases untuk audit modes, risk classes, event log integrity
4. **Doc drift check** — compare `EUREKA_TOKEN_MANAGEMENT.md` dengan actual code, surface any mismatch
5. **MCP tool stub** `arif_context_status` — read-only wrapper, no side effects

Total: ~5-7 jam, ~800-1000 LOC of tests, zero risk.

**Itu langkah seterusnya. Confirm atau adjust scope.**

---

*DITERJEMAHKAN DARI BAHASA FRAMEWORK KE BAHASA MANUSIA — 11 Jun 2026*
*Map ini adalah peta, bukan tindakan. Tindakan tunggu signal Arif.*
