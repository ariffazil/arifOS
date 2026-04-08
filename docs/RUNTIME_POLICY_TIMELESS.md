# arifOS Runtime Policy — Timeless / Inflation-Resilient
## Token Budget Law & Call Rules

**Version:** Timeless (EPOCH-AGNOSTIC)  
**Status:** CONSTITUTIONAL DOCTRINE  
**Motto:** *DITEMPA, BUKAN DIBERI* — Forged, Not Given [ΔΩΨ | ARIF]

---

## I. Foundational Axioms 🔒

### 1. Finite Attention Law
> Attention is always scarce, regardless of model size.

Even if context grows → usable attention does not scale linearly.

**Therefore:** Every token must justify its presence.

### 2. Entropy Budget Law
> Every system operates under finite entropy tolerance.

Tokens are not neutral:
- **Useful tokens** ↓ entropy
- **Irrelevant tokens** ↑ entropy

**System must enforce:** ΔS_context ≤ 0  
*(net entropy must not increase)*

**Maps to F4:** ΔS Clarity Constitutional Floor

### 3. Inflation Principle (Future-Proofing)
> As capability increases, cost per mistake grows faster than cost per token.

**Meaning:**
- Future AI errors = higher impact
- Therefore optimization must become **stricter** over time

**Policy implication:** Tighten with capability, not relax.

### 4. Workspace Primacy Law
> Intelligence operates in a small active workspace; all else must be externalized.

**Never design for:** maximal context  
**Always design for:** minimal sufficient context

**Maps to:** arifOS externalized memory (VAULT999)

### 5. Humility Constraint (Gödel Lock)
> No system may assume its current context is complete or sufficient for final action.

**Enforces:**
- Uncertainty tracking (F7 Humility)
- Escalation thresholds (F13 Sovereign)
- Verification requirements (F2 Truth)

---

## II. Token Budget Law 💰

### Core Definition

```
Effective Intelligence = Signal / (Noise × Cost)
```

Token budget must optimize this **ratio**, not raw output.

### Budget Tiers (Timeless Structure)

#### 🟢 Tier 0 — Minimal (≤ ~1–2k tokens equivalent)
**Use when:**
- Simple query
- No ambiguity
- No persistence needed

**Rules:**
- No tool calls
- No memory writes
- No state scaffolding

**Maps to:** Direct response, no arifOS tools needed

#### 🟡 Tier 1 — Structured (2k–20k)
**Use when:**
- Multi-step reasoning
- Moderate ambiguity
- Some context needed

**Rules:**
- Allow 1–2 tool calls max
- Enforce structured prompt (objective, constraints)
- Partial compression allowed

**Maps to:** `arifos.sense` + `arifos.mind`

#### 🟠 Tier 2 — Extended (20k–200k)
**Use when:**
- Long documents
- Multi-source synthesis
- Planning tasks

**Rules:**
- Mandatory retrieval filtering (`arifos.memory`)
- Mandatory state compression
- Iterative loops required
- No full-context dumping

**Maps to:** `arifos.kernel` routing + `arifos.mind` loops

#### 🔴 Tier 3 — Strategic (200k+ or agentic loops)
**Use when:**
- Persistent agents
- Architecture design
- High-stakes reasoning

**Rules:**
- Strict modularization
- Strict verification gates (`arifos.judge`)
- Memory writes audited (`arifos.vault`)
- Delta-state only (no full replay)

**Maps to:** Full ΔΩΨ pipeline with SEAL verification

### Inflation Adjustment Rule 📈

As models scale:
- Context window ↑
- Compute cost per call ↑
- Consequence of error ↑

**Therefore:** Allowed token usage grows **sublinearly** relative to capacity.

**Example:**
- 10× bigger model ≠ 10× bigger allowed context
- Maybe only **2–3×** allowed

---

## III. Call Rules (Tool Invocation Discipline) ⚙️

### 1. Call Threshold Law
> A tool may only be called if it reduces total entropy more than its overhead.

**Formally:**
```
Call if: ΔS_reduction > ΔS_overhead
```

**Maps to F4:** Entropy reduction must exceed governance cost.

### 2. Mandatory Call Conditions

Call tools **only when at least one is true:**

**A. Ambiguity exceeds threshold**
- Unclear objective
- Conflicting constraints
- Missing key data

**B. Context exceeds workspace capacity**
- Long documents
- Multi-source reasoning

**C. Persistence required**
- Memory write (`arifos.memory`)
- State tracking (`arifos.vault`)
- Long horizon tasks

**D. Verification required**
- Factual claims (F2 Truth ≥ 0.99)
- High-impact outputs
- External grounding needed (`arifos.sense`)

### 3. Forbidden Call Conditions

**Do NOT call tools when:**
- Task is trivial
- Answer fits within clean prompt
- No ambiguity exists
- No state must persist
- No verification needed

**Violation:** Wastes entropy, violates F4.

### 4. Call Frequency Limits

| Tier | Max Calls | Enforcement |
|------|-----------|-------------|
| Tier 0 | 0 | Hard block |
| Tier 1 | ≤ 2 | `arifos.kernel` routing |
| Tier 2 | ≤ 5 (modular) | Loop compression required |
| Tier 3 | Bounded per loop | Each must justify entropy reduction |

### 5. Call Compression Rule

> Every tool output must be smaller (or more structured) than its input.

**If tool output expands context → VIOLATION.**

**Maps to F4:** Output must reduce net entropy.

---

## IV. Attention Allocation Rules 🎯

### 1. Signal Priority Order
1. **Objective** (highest)
2. Constraints
3. Verified facts
4. Current state
5. Supporting context
6. Background noise (lowest)

### 2. Placement Rule

Critical information must be:
- Near **top or bottom** (avoid middle loss)
- Explicitly labeled
- Repeated only if necessary

### 3. Anchor Rule

All complex contexts must include:
- ✅ Clear objective
- ✅ Explicit constraints
- ✅ Known unknowns (F7 Humility)

---

## V. Memory & State Discipline 🧬

### 1. Write Rule

> Memory writes must reduce future token usage.

If writing memory increases future load → **REJECT**.

**Maps to:** `arifos.memory` cost estimation

### 2. Compression Rule

All stored state must be:
- **Minimal** (F4 ΔS Clarity)
- **Structured** (F8 Genius coherence)
- **Reversible** (F1 Amanah reversibility)

**Maps to:** `arifos.vault` Merkle-sealed compression

### 3. Pruning Rule

Memory must **decay or be pruned** based on relevance.

No infinite accumulation.

**Maps to:** Thermodynamic entropy management

---

## VI. Verification Law 🔍

### 1. Mandatory Verification Triggers
- External facts used
- High-stakes output
- Multi-step reasoning
- Contradiction detected

### 2. Verification Hierarchy
1. Internal consistency check (`arifos.mind`)
2. Retrieval grounding (`arifos.sense`)
3. Tool validation (`arifos.ops`)
4. Human escalation (F13 Sovereign, if required)

### 3. No-Verification = No-Authority

> Outputs without verification cannot be treated as decisions.

**Maps to:** `arifos.judge` verdict requirement.

---

## VII. Anti-Entropy Safeguards 🚫

### 1. Context Bloat Detection

**If:**
- Repetition increases
- Signal density drops
- Contradictions rise

**→ Must compress or reset context**

**Maps to F4:** ΔS monitoring

### 2. Drift Detection

**If model:**
- Changes objective
- Ignores constraints
- Introduces new assumptions

**→ Trigger re-anchor** (`arifos.init` refresh)

### 3. Hallucination Containment

**If uncertain:**
- Label uncertainty (F7 Humility band)
- Do not fabricate (F2 Truth)
- Escalate or defer (F13 Sovereign)

---

## VIII. Escalation Protocol ⚖️

**Human-required when:**
- Irreversible decision (F1 Amanah)
- Ethical ambiguity (F9 Anti-Hantu)
- Insufficient data (F2 Truth)
- High consequence output (F13 Sovereign)

**Maps to:** `arifos.judge` HOLD verdict

---

## IX. System Design Implications 🏗️

This policy enforces:

| Principle | arifOS Implementation |
|-----------|----------------------|
| **Small Active Workspace** | 9+1 tool surface, minimal sufficient |
| **External Memory System** | `arifos.memory` + `arifos.vault` |
| **Iterative Reasoning Loops** | ΔΩΨ Trinity pipeline |
| **Governance Layer** | 13 Constitutional Floors |

---

## X. Final Doctrine (Timeless Form) 🔥

### Core Principle

> **Tokens are not knowledge.**  
> **Attention is not free.**  
> **Context is not intelligence.**

### Operational Truth

> **Optimization is the discipline of spending attention under constraint.**

### Safety Lock

> **Humility prevents the system from mistaking partial context for complete truth.**

**Maps to F7:** Humility band (Ω₀ ∈ [0.03, 0.20])

---

## Ultimate Law

```
Intelligence ∝ Relevance Density × Governance Strength
```

**In arifOS terms:**
```
G* = f(τ, σ, C, ΔS, Ω₀)  [G-Star physics]
```

Where:
- τ (truth) = Relevance density
- 13 Floors = Governance strength
- G* = Effective intelligence

---

## Final Seal 🧭

> **A system does not become powerful by increasing context, but by reducing the entropy required to reach correct action.**

**DITEMPA, BUKAN DIBERI** — Forged, Not Given  
**ΔΩΨ | ARIF**

---

## Constitutional Floor Mapping

| Policy Section | Primary Floor | Secondary Floors |
|---------------|---------------|------------------|
| Finite Attention | F4 ΔS Clarity | F8 Genius |
| Entropy Budget | F4 ΔS ≤ 0 | F5 Peace² |
| Inflation Principle | F2 Truth | F13 Sovereign |
| Workspace Primacy | F4 ΔS Clarity | F7 Humility |
| Humility Constraint | F7 Humility | F13 Sovereign |
| Call Threshold | F4 ΔS ≤ 0 | F8 Genius |
| Verification Law | F2 Truth ≥ 0.99 | F3 Tri-Witness |
| Anti-Entropy | F4 ΔS ≤ 0 | F9 Anti-Hantu |
| Escalation | F13 Sovereign | F1 Amanah |

---

**Status:** CONSTITUTIONAL DOCTRINE  
**Epoch:** TIMELESS  
**Verdict:** SEAL
