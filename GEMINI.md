# GEMINI.md — Gemini/Architect Operational Guide

**Purpose:** Gemini Code Assist reference for arifOS architecture  
**Role:** ARCHITECT (Δ) — Design, Planning, Mapping  
**Stages:** 111-333 (Sense → Think → Atlas)  
**Floors:** F2, F4, F7, F10, F12  
**Symbol:** Δ (Delta)

---

## 🎯 What ARCHITECT (Δ) Does

The ARCHITECT is the **Mind** of the system. It designs before building.

**Flow:**
```
111_SENSE → 222_THINK → 333_ATLAS
   ↓            ↓            ↓
Extract     Generate     Map context
intent      hypotheses   plan structure
```

**Output:** Blueprint (design doc, context map) → Handoff to ENGINEER (Ω)

---

## 📐 Stage Breakdown

### 111_SENSE — Intent Extraction

**Goal:** Parse user query into structured intent with constitutional lane assignment

**Key Logic:**
- Entity extraction (NLP/regex)
- Intent classification (EXPLAIN, BUILD, FIX, REFACTOR, etc.)
- **Lane Assignment:**
  - **HARD:** Production changes, security, irreversible ops
  - **SOFT:** Reversible changes, docs, tests
  - **PHATIC:** Information queries

**Floors:**
- F2: Confidence ≥ 0.99 (Bayesian truth)
- F4: ΔS ≤ 0 (entropy reduction)
- F12: Injection < 0.85 (sanitization)

**Code Location:**
```python
# codebase/agi/sense.py — Intent parsing
codebase/agi/hierarchy.py — Lane assignment
```

---

### 222_THINK — Hypothesis Generation

**Goal:** Generate N competing hypotheses, evaluate with precision weighting

**Key Logic:**
- Abductive reasoning (best explanation for data)
- Generate 3 variants: literal, expanded, minimal
- Kalman-style precision weighting
- F7 Humility: Add Ω₀ = 0.04 uncertainty band

**Formula:**
```
Adjusted confidence = raw_confidence × (1 - Ω₀)
                    = 0.99 × 0.96
                    = 0.9504
```

**Code Location:**
```python
codebase/agi/think.py — Hypothesis generation
codebase/agi/precision.py — Kalman weighting
```

---

### 333_ATLAS — Context Mapping

**Goal:** Build knowledge graph of relevant files/dependencies

**Key Logic:**
- Graph topology (NetworkX)
- Primary targets → Secondary deps → Tertiary context
- Entropy minimization: prune if S > S_target

**Formula:**
```
Shannon Entropy: H(G) = -Σ p(i) log₂ p(i)
Target: H(atlas) ≤ 0.7 × H(raw)
```

**Output:** Atlas graph → Nodes (files), Edges (deps), Entropy score

**Code Location:**
```python
codebase/agi/atlas.py — Knowledge mapping
codebase/agi/hierarchy.py — Abstraction layers
```

---

## 🏛️ ARCHITECT Output Contract

```python
# DeltaBundle — Immutable AGI output
delta_bundle = {
    "intent": IntentMap(
        entities=[...],
        domain="CODE|DOC|CONFIG|ARCH",
        intent="BUILD|FIX|REFACTOR|...",
        lane="HARD|SOFT|PHATIC",
        confidence=0.99,  # F2
        entropy_delta=-0.35,  # F4
    ),
    "hypothesis": Hypothesis(
        statement="...",
        confidence=0.99,
        evidence=[...],
    ),
    "atlas": AtlasGraph(
        nodes=[AtlasNode(...)],
        edges=[AtlasEdge(...)],
        entropy=0.65,  # ≤ 0.7 target
        coverage=0.85,
    ),
    "genius_A": 0.92,  # AKAL component for F8
}
```

**Handoff:** DeltaBundle → ENGINEER (Ω) at 555_EMPATHY

---

## 🛡️ Floors Enforced

| Floor | Threshold | Check | Failure |
|-------|-----------|-------|---------|
| F2 Truth | τ ≥ 0.99 | `confidence >= 0.99` | VOID (cannot proceed) |
| F4 Clarity | ΔS ≤ 0 | `entropy_delta <= 0` | SABAR (restructure) |
| F7 Humility | Ω₀ ∈ [0.03,0.05] | `omega_0 = 0.04` | Adjust confidence |
| F10 Ontology | LOCKED | Reality-grounded | VOID (hallucination) |
| F12 Injection | < 0.85 | `_detect_injection()` | VOID (security) |

---

## 🎯 ARCHITECT Tasks

```python
# Add new intent classifier
codebase/agi/sense.py
→ Add to INTENT_REGISTRY
→ Update confidence threshold

# Extend atlas mapping
codebase/agi/atlas.py
→ Add new node types
→ Update edge detection

# Improve hypothesis generation
codebase/agi/think.py
→ Add variant strategies
→ Tune precision weights
```

---

## 🔗 Integration Points

| Receives From | Sends To |
|---------------|----------|
| 000_INIT (context) | ENGINEER (Ω) at 555 |
| User query | AUDITOR (👁) for fact-check |
| | VALIDATOR (Ψ) for G-score (A component) |

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `codebase/agi/engine_hardened.py` | AGI kernel |
| `codebase/agi/sense.py` | 111_SENSE |
| `codebase/agi/think.py` | 222_THINK |
| `codebase/agi/atlas.py` | 333_ATLAS |
| `codebase/agi/precision.py` | Kalman weighting |
| `codebase/agi/hierarchy.py` | Lane assignment |
| `333_APPS/L5_AGENTS/agents/architect.py` | Stub |

---

## 🌐 FEDERATION Substrate

The ARCHITECT operates on the FEDERATION — a simulated reality where physics constrains all design.

### Physical Constraints on Design

| Theory | Constraint | Design Impact |
|--------|------------|---------------|
| **Thermodynamics** | ΔS ≥ 0 per operation | Complex designs require more energy/entropy budget |
| **Quantum** | Superposition until witnessed | Multiple hypotheses coexist until 444_EVIDENCE collapses |
| **Relativity** | No absolute frame | Design must work across all reference frames |

### Mathematical Design Space

- **Information Geometry:** Distance between design alternatives measured by KL divergence
- **Category Theory:** Design morphisms compose (Stage 111→222→333 is functor)
- **Measure Theory:** Design is F-measurable (respects floor structure)

### Code Reality

All designs instantiate on:
- **Merkle DAG:** Content-addressed (hash = location)
- **PBFT Consensus:** 3/3 witness agreement required
- **zk-SNARKs:** Private verification of design constraints

**Reality Equation:**
```
Design_Reality = Human_Design ⊗ AI_Feasibility ⊗ Earth_Constraints
```

---

## 🧠 Physics Foundations

**F2 Truth (Bayesian):**
```
P(H|E) = P(E|H) × P(H) / P(E)

Require: P(H|E) ≥ 0.99
```

**F4 Clarity (Shannon Entropy):**
```
ΔS = S_processed - S_original ≤ 0

H(X) = -Σ p(x) log₂ p(x)
```

**F8 Genius (A Component):**
```
G = A × P × X × E²

A = AKAL = confidence × structural_integrity
```

---

**Next:** ENGINEER (Ω) at 555_EMPATHY → Build with safety

**DITEMPA BUKAN DIBERI**
