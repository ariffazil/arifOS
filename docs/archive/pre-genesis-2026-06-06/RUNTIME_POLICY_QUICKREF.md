# arifOS Runtime Policy — Quick Reference Card

## The 5 Axioms 🔒

| Axiom | Core Truth | Maps to |
|-------|-----------|---------|
| **Finite Attention** | Attention scarce regardless of model size | F4 ΔS Clarity |
| **Entropy Budget** | ΔS_context ≤ 0 (net entropy must decrease) | F4 Constitutional Floor |
| **Inflation** | Cost per mistake grows faster than cost per token | F2 Truth, F13 Sovereign |
| **Workspace Primacy** | Design for minimal sufficient context | Externalized memory |
| **Humility** | Never assume context is complete | F7 Humility, F13 Sovereign |

---

## Token Budget Tiers 💰

| Tier | Size | Use Case | Tools | Max Calls |
|------|------|----------|-------|-----------|
| 🟢 **Tier 0** | ≤ 2k | Simple query | None | 0 |
| 🟡 **Tier 1** | 2k–20k | Multi-step reasoning | sense + mind | ≤ 2 |
| 🟠 **Tier 2** | 20k–200k | Long docs, synthesis | Full ΔΩΨ | ≤ 5 |
| 🔴 **Tier 3** | 200k+ | Agents, architecture | Full pipeline + audit | Bounded |

**Inflation Rule:** 10× model ≠ 10× context. Maybe 2–3×.

---

## Call Rules ⚙️

### Call Threshold
```
Call if: ΔS_reduction > ΔS_overhead
```

### Must Call When
- [ ] Ambiguity exceeds threshold
- [ ] Context exceeds workspace
- [ ] Persistence required
- [ ] Verification required

### Never Call When
- [ ] Task is trivial
- [ ] No ambiguity
- [ ] No persistence needed
- [ ] No verification needed

### Compression Rule
> Output must be smaller or more structured than input.

---

## Attention Priority 🎯

```
1. OBJECTIVE (highest)
2. Constraints
3. Verified facts
4. Current state
5. Supporting context
6. Background noise (lowest)
```

---

## Memory Discipline 🧬

| Rule | Principle |
|------|-----------|
| **Write** | Must reduce future token usage |
| **Compress** | Minimal, structured, reversible |
| **Prune** | Decay based on relevance |

---

## Verification Hierarchy 🔍

```
1. Internal consistency (mind)
2. Retrieval grounding (sense)
3. Tool validation (ops)
4. Human escalation (judge HOLD)
```

**No verification = No authority**

---

## Escalation Triggers ⚖️

Escalate to human (F13) when:
- Irreversible decision
- Ethical ambiguity
- Insufficient data
- High consequence

---

## Ultimate Formula 🔥

```
Intelligence ∝ Relevance Density × Governance Strength

G* = f(τ, σ, C, ΔS, Ω₀)
```

---

## One-Liner Doctrine

> **A system does not become powerful by increasing context, but by reducing the entropy required to reach correct action.**

**DITEMPA, BUKAN DIBERI** — Forged, Not Given [ΔΩΨ | ARIF]
