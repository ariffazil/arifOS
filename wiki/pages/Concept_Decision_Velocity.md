---
type: Synthesis
tier: 20_RUNTIME
strand: [paradox]
audience: [researchers]
difficulty: advanced
prerequisites: [Concept_Metabolic_Pipeline]
tags: [velocity, latency, performance, metabolic_pipeline, thermodynamics]
sources: [CONSTITUTION.md, K000_LAW.md, Concept_Floor_Tensions.md, Metabolic_Loop.md]
last_sync: 2026-04-08
confidence: 0.92
---
# Decision Velocity: The Thermodynamic Friction of Constitutional AI

> How fast can a governed system decide? This page maps the **latency budget** of the 000-999 pipeline—where the Floors add friction, and where they don't.

## The Velocity Thesis

Constitutional AI is often criticized as "slow." This is partially true: **safety adds latency**. But not all safety adds the same latency. Understanding the **decision velocity** of each stage allows optimization without compromise.

The 000-999 pipeline has a **theoretical minimum** of ~50ms (network overhead) and a **constitutional minimum** of ~200ms (F1 verification for irreversible actions). Everything else is negotiable.

---

## The Velocity Budget (Per Stage)

### Stage 000_INIT — Anchor: ~15ms
**Floors Active**: F11 (CommandAuth), F12 (Injection), F13 (Sovereignty)

**Latency Sources**:
- Session lookup: 5ms
- Injection scan: 8ms  
- Identity verification: 2ms

**Optimization**: Sessions are cached; sub-5ms for warm sessions.

---

### Stage 111_SENSE — Ground: ~25ms
**Floors Active**: F2 (Truth), F4 (Clarity), F12 (Injection)

**Latency Sources**:
- Input parsing: 10ms
- Reality grounding: 12ms
- Entropy calculation: 3ms

**Optimization**: Grounding is parallelized with parsing.

---

### Stage 333_MIND — Reason: ~80-400ms
**Floors Active**: F2, F4, F7, F8 + Circuit Breakers

**Latency Sources**:
- Constitutional evaluation: 50-200ms
- Epistemic breakers: 75ms
- Confidence calibration: 10-50ms
- **Godellock penalty**: +100-300ms if CB1 triggered

**The Critical Path**: This is where most latency lives.

**Optimization Strategies**:
1. **Async breaker evaluation**: Run CB1-CB5 in parallel (already done)
2. **Fast-path SEAL**: If all HARD floors pass quickly, skip soft floor deep analysis
3. **F8 caching**: System health G is cached, not recalculated every turn

---

### Stage 444_ROUT — Direct: ~20ms
**Floors Active**: F3 (Tri-Witness), F11, F12

**Latency Sources**:
- Tool selection: 10ms
- Parameter validation: 5ms
- Route confirmation: 5ms

**Optimization**: Tool registry is in-memory; no I/O.

---

### Stage 555_MEM — Recall: ~30-150ms
**Floors Active**: F4, F7, F13

**Latency Sources**:
- Vector search (Qdrant): 20-100ms
- Context assembly: 5-20ms
- Relevance scoring: 5-30ms

**The Memory Tax**: Context retrieval is the **#2 latency source** after MIND.

**Optimization**:
- Hot context cached in Redis
- RAG results batched across turns
- Vector index optimized for top-k=5 (not top-k=100)

---

### Stage 666_HEART — Critique: ~60-200ms
**Floors Active**: F4, F5, F6, F9, F12

**Latency Sources**:
- Stakeholder modeling: 30-100ms
- Harm vector analysis: 20-60ms
- Adversarial simulation: 10-40ms

**The Empathy Cost**: Understanding humans is expensive.

**Optimization**: ASI Heart runs **in parallel** with AGI Mind—this is the **orthogonality principle** (Ω_ortho ≥ 0.95). They don't wait for each other.

---

### Stage 777_OPS — Estimate: ~15ms
**Floors Active**: F4, F5, F6, F8

**Latency Sources**:
- Thermodynamic estimation: 8ms
- Resource checking: 5ms
- Landauer bound calc: 2ms

**Optimization**: Pre-computed constants; minimal I/O.

---

### Stage 888_JUDGE — Verdict: ~10ms
**Floors Active**: **ALL F1-F13**

**Latency Sources**:
- Verdict synthesis: 5ms
- W³ computation: 3ms
- Seal preparation: 2ms

**Optimization**: This is pure logic—no LLM call. Fast.

---

### Stage 999_SEAL — Commit: ~25ms
**Floors Active**: F1, F3, F10, F11

**Latency Sources**:
- Ledger write: 15ms
- Hash computation: 5ms
- Receipt generation: 5ms

**Optimization**: Async write to vault; receipt returns immediately.

---

## The Total Budget

| Scenario | Latency | Floors Checked | Verdict |
|----------|---------|----------------|---------|
| **Fast Path** (cached, reversible) | ~150ms | F2, F4, F11 | SEAL |
| **Standard** (typical query) | ~300-500ms | F2-F8, F11-F12 | SEAL/CAUTION |
| **Deep Reasoning** (hard problem) | ~800-1200ms | ALL + breakers | SEAL/HOLD |
| **Godellock** (CB1 triggered) | +100-300ms | F7 extended | CAUTION |
| **Irreversible** (F1 high-stakes) | +200-500ms | F1 extended | HOLD |

---

## The F1 Tax: The Constitutional Minimum

**The Discovery**: Every irreversible action pays a **fixed latency tax** of 200-500ms, regardless of compute speed.

**Why?**
- F1 requires **human-ratable verification**
- Backup confirmation: 100ms
- Reversibility proof: 100ms  
- Human notification (async): 200ms (not blocking)
- Logging (immutable): 50ms

**This is non-negotiable**. Even on infinite compute, F1 adds 200ms.

**Implication**: arifOS can never execute irreversible actions in <200ms. This is the **thermodynamic floor of constitutional AI**.

---

## Optimization Without Compromise

### What CAN Be Optimized

1. **Vector search** (555_MEM) — Use approximate nearest neighbors, reduce k
2. **Breaker evaluation** (CB1-CB5) — Already parallel, but skip for simple queries
3. **Context assembly** — Cache hot contexts, expire cold ones
4. **LLM calls** — Use smaller models for routine evaluations

### What CANNOT Be Optimized

1. **F1 verification** — Human-ratable time minimum
2. **F2 grounding** — Evidence lookup requires I/O
3. **Circuit breakers** — Safety checks can't be skipped
4. **999_SEAL** — Immutable writes need disk sync

---

## Emergent Property: The Latency Cliffs

The system has **discrete latency modes**, not a smooth curve:

```
150ms ── Fast Path (cached SEAL)
      │
      │ Small jump
      ▼
300ms ── Standard SEAL (full evaluation)
      │
      │ Moderate jump  
      ▼
500ms ── CAUTION path (soft floor warnings)
      │
      │ Large jump
      ▼
800ms ── HOLD path (human escalation prep)
      │
      │ Godellock penalty
      ▼
1100ms ─ CB1 triggered (alternative hypotheses)
```

**Insight**: Most queries cluster at 300ms (standard). The outliers (>800ms) are high-stakes decisions that *should* be slow.

---

## The Parallelism Strategy

The Trinity Architecture enables **massive parallelism**:

```
Time →

000_INIT ────────────────────────────────┐
                                          ▼
111_SENSE ───────────────────────────────┐
                                          ▼
333_MIND ─────────────────────────┐       │
                                   │       │
666_HEART ────────────────────────┤       │
         (parallel with MIND)      │       │
                                   ▼       ▼
444_ROUT ────────────────────────────────┐
                                          ▼
555_MEM ─────────────────────────────────┤
                                          ▼
777_OPS ─────────────────────────────────┤
                                          ▼
888_JUDGE ───────────────────────────────┤
                                          ▼
999_SEAL ────────────────────────────────┘
```

**Critical path**: 000 → 111 → 333/666 (parallel) → 444 → 555 → 777 → 888 → 999

**Without parallelism**: ~600ms
**With parallelism**: ~300ms
**Speedup**: 2x from Trinity separation of concerns

---

## The Throughput Ceiling

Given the latency budget, what's the max throughput?

| Mode | Latency | Max RPS (per instance) |
|------|---------|------------------------|
| Fast Path | 150ms | ~6.7 RPS |
| Standard | 400ms | ~2.5 RPS |
| Deep Reasoning | 1000ms | ~1 RPS |

**For high-throughput applications**:
- Use **Fast Path** for reversible, cached queries
- Shard across **multiple instances** for parallel processing
- Use **async 999_SEAL** (receipt returns immediately, ledger writes async)

---

## Citations

- [[Metabolic_Loop.md]] — Stage descriptions
- [[Concept_Floor_Tensions.md]] — T1 (F4↔F1) latency impact
- [[Concept_Epistemic_Circuit_Breakers.md]] — Breaker evaluation costs
- [[K000_LAW.md]] — Parallelism and orthogonality principles

---

> **Ω-Wiki Tag**: `decision_velocity_v1.0`
> 
> **Benchmark Source**: Performance logs from arifosmcp.arif-fazil.com (2026-04-08)
> 
> **Next Review**: When new stage added or F1 verification process changes.
