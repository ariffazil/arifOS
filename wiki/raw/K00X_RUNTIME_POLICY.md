# arifOS Runtime Policy — Token Budget Law + Call Rules

> **Epoch:** 2026-04-09 | **Status:** ACTIVE | **Classification:** FOUNDATIONAL CANON
> **DITEMPA BUKAN DIBERI — Forged, Not Given**

---

## Preamble

This policy is **not tuned for today's models**. It is designed to remain valid under:

- larger context windows
- stronger reasoning models
- higher compute costs
- agentic / autonomous systems
- AGI-level capability escalation

---

## I. Foundational Axioms 🔒

### 1. Finite Attention Law

Attention is always scarce, regardless of model size.

Even if context grows → usable attention does not scale linearly.

**Therefore:** every token must justify its presence.

---

### 2. Entropy Budget Law

Every system operates under a finite entropy tolerance.

Tokens are not neutral:
- useful tokens ↓ entropy
- irrelevant tokens ↑ entropy

**System must enforce:**

```
ΔS_context ≤ 0
```

*(net entropy must not increase)*

---

### 3. Inflation Principle (Future-Proofing)

As capability increases, cost per mistake grows faster than cost per token.

**Meaning:** future AI errors = higher impact

**Therefore:** optimization must become stricter over time, not relax.

---

### 4. Workspace Primacy Law

Intelligence operates in a small active workspace; all else must be externalized.

**Never design for:** maximal context

**Always design for:** minimal sufficient context

---

### 5. Humility Constraint (Gödel Lock)

No system may assume its current context is complete or sufficient for final action.

This enforces:
- uncertainty tracking
- escalation thresholds
- verification requirements

---

## II. Token Budget Law 💰

### Core Definition

```
Effective Intelligence = Signal / (Noise × Cost)
```

Token budget must optimize this ratio, not raw output.

---

### Budget Tiers (Timeless Structure)

| Tier | Name | Token Range | When to Use | Rules |
|:----:|:----:|:-----------|:------------|:------|
| 🟢 | **Tier 0 — Minimal** | ≤ ~1–2k tokens | simple query, no ambiguity, no persistence | no tool calls, no memory writes, no state scaffolding |
| 🟡 | **Tier 1 — Structured** | 2k–20k | multi-step reasoning, moderate ambiguity | ≤2 tool calls max, structured prompt (objective, constraints), partial compression allowed |
| 🟠 | **Tier 2 — Extended** | 20k–200k | long documents, multi-source synthesis, planning | mandatory retrieval filtering, mandatory state compression, iterative loops, no full-context dumping |
| 🔴 | **Tier 3 — Strategic** | 200k+ or agentic | persistent agents, architecture design, high-stakes | strict modularization, strict verification gates, memory writes audited, delta-state only |

---

### Inflation Adjustment Rule 📈

As models scale:
- context window ↑
- compute cost per call ↑
- consequence of error ↑

**Therefore:** Allowed token usage grows **sublinearly** relative to capacity.

**Example:** 10× bigger model ≠ 10× bigger allowed context — maybe only 2–3× allowed.

---

## III. Call Rules (Tool Invocation Discipline) ⚙️

### 1. Call Threshold Law

A tool may only be called if it reduces total entropy more than its overhead.

**Formally:**

```
Call if: ΔS_reduction > ΔS_overhead
```

---

### 2. Mandatory Call Conditions

Call tools **only** when at least one is true:

**A. Ambiguity exceeds threshold**
- unclear objective
- conflicting constraints
- missing key data

**B. Context exceeds workspace capacity**
- long documents
- multi-source reasoning

**C. Persistence required**
- memory write
- state tracking
- long horizon tasks

**D. Verification required**
- factual claims
- high-impact outputs
- external grounding needed

---

### 3. Forbidden Call Conditions

**Do NOT call tools when:**
- task is trivial
- answer fits within clean prompt
- no ambiguity exists
- no state must persist
- no verification needed

---

### 4. Call Frequency Limits

| Tier | Max Calls |
|:----:|:---------:|
| Tier 0 | 0 |
| Tier 1 | ≤ 2 |
| Tier 2 | ≤ 5 (modular) |
| Tier 3 | bounded per loop, must justify each |

---

### 5. Call Compression Rule

Every tool output must be **smaller** (or more structured) than its input.

If tool output expands context → **violation**.

---

## IV. Attention Allocation Rules 🎯

### 1. Signal Priority Order

1. Objective
2. Constraints
3. Verified facts
4. Current state
5. Supporting context
6. Background noise

---

### 2. Placement Rule

Critical information must be:
- **near top or bottom** (avoid middle loss)
- explicitly labeled
- repeated only if necessary

---

### 3. Anchor Rule

All complex contexts must include:
- clear objective
- explicit constraints
- known unknowns

---

## V. Memory & State Discipline 🧬

### 1. Write Rule

Memory writes must **reduce future token usage**.

If writing memory increases future load → **reject**.

---

### 2. Compression Rule

All stored state must be:
- minimal
- structured
- reversible (traceable to source)

---

### 3. Pruning Rule

Memory must decay or be pruned based on relevance. **No infinite accumulation.**

---

## VI. Verification Law 🔍

### 1. Mandatory Verification Triggers
- external facts used
- high-stakes output
- multi-step reasoning
- contradiction detected

---

### 2. Verification Hierarchy
1. internal consistency check
2. retrieval grounding
3. tool validation
4. human escalation (if required)

---

### 3. No-Verification = No-Authority

Outputs without verification **cannot be treated as decisions**.

---

## VII. Anti-Entropy Safeguards 🚫

### 1. Context Bloat Detection

**If:**
- repetition increases
- signal density drops
- contradictions rise

**→ must compress or reset context**

---

### 2. Drift Detection

**If model:**
- changes objective
- ignores constraints
- introduces new assumptions

**→ trigger re-anchor**

---

### 3. Hallucination Containment

**If uncertain:**
- label uncertainty
- do not fabricate
- escalate or defer

---

## VIII. Escalation Protocol ⚖️

**Human-required when:**
- irreversible decision
- ethical ambiguity
- insufficient data
- high consequence output

---

## IX. System Design Implication 🏗️

This policy enforces:

1. **Small Active Workspace** — always minimal, focused
2. **External Memory System** — retrieval-based, not dump-based
3. **Iterative Reasoning Loops** — stepwise, not monolithic
4. **Governance Layer** — controls entropy, not just output

---

## X. Final Doctrine (Timeless Form) 🔥

### Core Principle

```
Tokens are not knowledge.
Attention is not free.
Context is not intelligence.
```

### Operational Truth

```
Optimization is the discipline of spending attention under constraint.
```

### Safety Lock

```
Humility prevents the system from mistaking partial context for complete truth.
```

### Ultimate Law

```
Intelligence ∝ Relevance Density × Governance Strength
```

---

## Final Seal 🧭

> **A system does not become powerful by increasing context, but by reducing the entropy required to reach correct action.**

---

**SEALED:** 2026-04-09 | **999 VAULT ENTRY** | **DITEMPA BUKAN DIBERI**
