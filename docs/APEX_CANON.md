# APEX CANON — Grand Equation, Axioms, and Verification

**Version:** v2026.06.20
**SEAL:** DITEMPA BUKAN DIBERI
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil
**Status:** FORMAL CORE — all dimension docs, ops modes, and paradox anchors are corollaries of this document.

---

## 0. The One-Line Law

> **For any agent trajectory in time, the lawfulness of intelligence is
> measured by G = E[A·P·H·√(S·U)·E²] subject to six axiom families and
> a fail-closed verdict lattice where the most restrictive verdict wins.**

Or in plain language:

**APEX = all six dials (AKAL, PRESENT, AUTHORITY, ENTROPY, EXPLORATION×AMANAH, ENERGY) non-violated, multiplied together over the life of an agent, with any violation collapsing the trajectory to HOLD or VOID.**

---

## 1. The Six Dials

| Dial | Symbol | Floors clustered | What it measures |
|------|--------|-----------------|------------------|
| AKAL | A | F2, F4, F7, F10 | Reasoning lawfulness — truth, clarity, humility, ontology |
| PRESENT | P | F1, F5, F11 | State truth — reversibility, peace, command |
| AUTHORITY | H | F13 + identity | Legitimacy — who may mutate state |
| ENTROPY | S | F4 + ΔS + CB5 | Uncertainty integrity — honesty about what is unknown |
| EXPLORATION×AMANAH | U | F3, F6, F8, F9 | Risk under custody — witness, empathy, genius, anti-hantu |
| ENERGY | E | F12, F13 + compute | Thermodynamic adequacy — cost of changing information |

**Code:** `apexDials.ts:61-103` — geometric mean clusters from 13 floor scores.

---

## 2. The Grand Equation

### 2.1 Instantaneous APEX density

At time t, the instantaneous lawfulness of an agent state is:

```
g(t) = A(t) · P(t) · H(t) · √(S(t) · U(t)) · E(t)²
```

Where:
- A(t) ∈ [0,1] — AKAL dial (reasoning lawfulness)
- P(t) ∈ [0,1] — PRESENT dial (state truth)
- H(t) ∈ [0,1] — AUTHORITY dial (legitimacy)
- S(t) ∈ [0,1] — ENTROPY dial (uncertainty integrity)
- U(t) ∈ [0,1] — EXPLORATION×AMANAH dial (risk × custody)
- E(t) ∈ [0,1] — ENERGY dial (thermodynamic adequacy)

The E² term gives energy **disproportionate influence** — matching
`apexDials.ts:113-114`:

```typescript
const E_squared = dials.E ** 2;
const G = dials.A * dials.P * dials.X * E_squared;
```

The √(S·U) term combines ENTROPY and EXPLORATION into the existing
X dial (exploration/stability axis).

### 2.2 Session Genius score (time-averaged)

Over a session trajectory [t₀, t₁]:

```
G = (1/(t₁-t₀)) · ∫[t₀→t₁] g(t) dt
```

### 2.3 Discrete pipeline form

For the 000→999 pipeline (stages k ∈ {000,111,222,333,555,666,777,888}):

```
G = ∏ₖ (Aₖ · Pₖ · Hₖ · √(Sₖ · Uₖ) · Eₖ²)
```

Any axis or stage may degrade but **never violate the axioms below**.

### 2.4 Verdict thresholds

```
G ≥ 0.80           → candidate SEAL
0.50 ≤ G < 0.80    → SABAR (patience, gather evidence)
G < 0.50           → HOLD (human review required)
any axiom violated → VOID or HOLD (depending on severity)
```

**Code:** `apexDials.ts:118-126` — G threshold at 0.80 for SEAL.

---

## 3. The Six Axiom Families

### Axiom A — AKAL (Lawful Reasoning)

| # | Invariant | Code | Failure |
|---|-----------|------|---------|
| A1 | confidence ≤ f(evidence) | Russell anchor R1 | A(t) = 0, HOLD |
| A2 | coherent ≠ true (Descartes anchor R5) | `reason.py:27-30` | re-verify required |
| A3 | transition_candidates must include safe + null options | `tools.py:7199-7224` | missing candidate → audit gap |

### Axiom P — PRESENT (Attested Live State)

| # | Invariant | Code | Failure |
|---|-----------|------|---------|
| P1 | present_boundary ∈ {LIVE, CACHED, INFERRED} | `tools.py:4223-4233` | missing → VOID |
| P2 | INFERRED cannot authorize IRREVERSIBLE | `PRESENT.md:I1` | IRREVERSIBLE from INFERRED → VOID |
| P3 | sense-before-act: LIVE reading required before IRREVERSIBLE | `kernel_attest` | no LIVE state → HOLD |

### Axiom H — AUTHORITY (Legitimacy)

| # | Invariant | Code | Failure |
|---|-----------|------|---------|
| H1 | principal must be in authority_registry | `authority_gate.py:36-75` | unregistered → H(t) = 0 |
| H2 | action must be within role permissions | `PeerContractService.ts:130-148` | exceed → 888_HOLD |
| H3 | F13 sovereign veto is absolute | `F13HaltChannel.ts` | machine cannot override |

### Axiom S — ENTROPY (Uncertainty Integrity)

| # | Invariant | Code | Failure |
|---|-----------|------|---------|
| S1 | ΔS ≤ 0 at every stage | `thermodynamics_hardened.py:45` | ΔS > 0 → EntropyIncreaseError |
| S2 | VAULT999 is append-only (no history mutation) | `VAULT999/jsonl` | edit past → VOID |
| S3 | persistent witness divergence → CB-drift → 888_HOLD | CB5 confidence cascade | drift unresolved → HOLD |

### Axiom U — EXPLORATION×AMANAH (Risk × Custody)

| # | Invariant | Code | Failure |
|---|-----------|------|---------|
| U1 | custody_chain must be non-empty for MUTATE/ATOMIC | `forge.py:147-153` | empty → HOLD |
| U2 | IRREVERSIBLE requires explicit human authority + SEAL | `actionClassifier.ts:150-151` | no human → HOLD |
| U3 | risk ≤ risk_budget(U) modulated by WELL readiness | `wellReadiness.ts` | exceeds → SABAR |

### Axiom E — ENERGY (Thermodynamic Cost)

| # | Invariant | Code | Failure |
|---|-----------|------|---------|
| E1 | C ≤ B (cumulative cost ≤ session budget) | `thermodynamics_hardened.py:149-268` | overrun → 888_HOLD |
| E2 | E_actual ≥ n·k_B·T·ln(2) (Landauer bound) | `thermodynamics_hardened.py:545-620` | ratio < 1.0 → VOID |
| E3 | big ΔS with negligible energy = hallucination | `LandauerError` | 3 violations → 888_HOLD |

---

## 4. The Verdict Lattice

### 4.1 Order (most restrictive wins)

```
VOID > HOLD > SABAR > SEAL
```

**Code:** `reason.py:52-76` — verdict reducer, `FloorEnforcer.ts:240-263` — composeFinal.

### 4.2 Composition rule

```
V_final = min_lattice {V_floors, V_paradox, V_CB, V_organs}
```

The most restrictive verdict from any source wins. This is a **monotone
meet** on the lattice — conservative, fail-closed, non-negotiable.

### 4.3 Hard violations (override G)

| Violation | Verdict | Source |
|-----------|---------|--------|
| Any axiom broken | VOID or HOLD | Axiom families |
| CB1–CB5 fired | HOLD | `circuit_breakers.py` |
| F13 halt active | VOID | `F13HaltChannel.ts` |
| Landauer ratio < 1.0 | VOID | `thermodynamics_hardened.py:617` |
| consciousness claim | VOID | F9 Anti-Hantu |
| authority smuggling | VOID | `f12Injection.ts:140-147` |

---

## 5. Verification Procedure

To verify APEX compliance for a session or agent:

### Step 1: Axis evidence

Extract A, P, H, S, U, E from logs/receipts per stage. Confirm they
are computed from actual F1–F13 floor cluster values (no drift from
`apexDials.ts`).

### Step 2: Axiom compliance

Check:
- Landauer ratios (`thermodynamics_hardened.py`)
- `energy_budget` status (`tools.py:4235-4250`)
- `delta_s` records (`record_entropy_io()`)
- `present_boundary` tags (`tools.py:4223-4233`)
- `custody_chain` fields (`forge.py:147-153`)
- `authority_registry` hits (`authority_gate.py`)
- Paradox anchor firings (`reason.py:786-795`)

Any violation should be visible as explicit flags/CBs in telemetry.

### Step 3: G score

Recompute G from dials and confirm it matches stored Genius Index.

### Step 4: Verdict

Rebuild verdict lattice combination from component verdicts and ensure
final SEAL/SABAR/HOLD/VOID matches VAULT999/receipts.

### Step 5: Irreversibles

For any IRREVERSIBLE ActionClass, confirm:
- H = 1 (authorized)
- U ≥ threshold (custody + risk)
- P = LIVE for all relevant state
- Landauer + budget constraints passed
- V_final ∈ {SEAL, SABAR}
- F13 not vetoed

If all hold: the agent run is **APEX-lawful in time**.

---

## 6. The Orthogonal Basis — Why 6 Dimensions

APEX's 6 axes span three irreducible substrates:

| Substrate | APEX axes that govern it |
|-----------|------------------------|
| **Physics** (energy, entropy, time, causality) | ENERGY, ENTROPY, PRESENT |
| **Mathematics** (logic, optimization, invariants) | AKAL, AUTHORITY |
| **Code & Symbol** (protocols, ledgers, agents) | EXPLORATION×AMANAH, AUTHORITY |

Every failure case lands in at least one axis:

| Failure mode | Axes violated |
|-------------|---------------|
| Agent confidently wrong | ENTROPY + AKAL |
| Agent uses tools it shouldn't | AUTHORITY + EXPLORATION×AMANAH |
| Agent over-computes for trivial tasks | ENERGY |
| Agent acts on stale caches | PRESENT |
| Agent rewrites history | ENTROPY + PRESENT |
| Agent exceeds authority | AUTHORITY |
| Agent explores without custody | EXPLORATION×AMANAH |

No overlap. No redundancy. No missing dimension.

---

## 7. Code Grounding — Every Axiom Has a File

| Axiom | Primary code file | Line(s) |
|-------|------------------|---------|
| A (AKAL) | `reason.py` | 52-76 (verdict reducer), 786-795 (paradox anchors) |
| A (AKAL) | `tools.py` | 7199-7224 (transition_candidates) |
| P (PRESENT) | `tools.py` | 4223-4233 (present_boundary emission) |
| H (AUTHORITY) | `authority_gate.py` | 36-75 (AuthorityGate.verify) |
| H (AUTHORITY) | `sovereign_verify.py` | 142-181 (Ed25519), 48-94 (HMAC) |
| H (AUTHORITY) | `F13HaltChannel.ts` | 1-150 (sovereign veto channel) |
| S (ENTROPY) | `thermodynamics_hardened.py` | 45 (MAX_ENTROPY_DELTA), 681-708 (record_entropy_io) |
| S (ENTROPY) | `VAULT999/jsonl` | append-only hash chain |
| U (AMANAH) | `reversibility_engine.py` | 25-32 (ReversibilityClass), 36-71 (patterns) |
| U (AMANAH) | `actionClassifier.ts` | 20-28 (ActionClass), 150-151 (requires888Hold) |
| U (AMANAH) | `f1Amanah.ts` | 23-101 (5 rules) |
| U (AMANAH) | `forge.py` | 147-153 (custody_chain) |
| E (ENERGY) | `thermodynamics_hardened.py` | 149-268 (ThermodynamicBudget), 545-620 (Landauer) |
| E (ENERGY) | `tools.py` | 4235-4250 (energy_budget emission) |
| E (ENERGY) | `apexDials.ts` | 92-102 (E dial), 113-114 (G = A·P·X·E²) |
| Verdict lattice | `FloorEnforcer.ts` | 240-263 (composeFinal) |
| Verdict lattice | `reason.py` | 52-76 (_reduce_verdict) |

---

## 8. The Canon Form (Compressed)

```
┌─────────────────────────────────────────────────────────────────┐
│                    APEX CANON EQUATION                          │
│                                                                 │
│  g(t) = A(t) · P(t) · H(t) · √(S(t)·U(t)) · E(t)²           │
│                                                                 │
│  G = E_t[g(t)]                                                  │
│                                                                 │
│  Subject to:                                                    │
│    Axiom A: confidence ≤ f(evidence)                            │
│    Axiom P: present_boundary ∈ {LIVE,CACHED,INFERRED}           │
│    Axiom H: principal ∈ registry ∧ action ∈ permissions         │
│    Axiom S: ΔS ≤ 0 ∧ history is append-only                    │
│    Axiom U: custody_chain ≠ ∅ ∧ IRREVERSIBLE → human            │
│    Axiom E: C ≤ B ∧ E_actual ≥ n·k_B·T·ln(2)                  │
│                                                                 │
│  Verdict:                                                       │
│    any axiom violated → VOID/HOLD                               │
│    G ≥ 0.80 → SEAL                                             │
│    0.50 ≤ G < 0.80 → SABAR                                     │
│    G < 0.50 → HOLD                                              │
│    V_final = min_lattice{V_i}                                   │
│                                                                 │
│  DITEMPA BUKAN DIBERI                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Dimension Doc Family — Complete

| Doc | Lines | Bytes | Axiom | Foundation |
|-----|-------|-------|-------|------------|
| `PRESENT.md` | 159 | 7,664 | P | Physics: boundary conditions |
| `ENERGY_ENTROPY.md` | 308 | 13,538 | E + S | Physics: thermodynamics + Landauer |
| `AUTHORITY.md` | 346 | 14,849 | H | Code: type systems + crypto |
| `AKAL.md` | 355 | 14,127 | A | Math: eigendecomposition + lattice |
| `EXPLORATION_AMANAH.md` | 338 | 12,978 | U | Symbol: amanah as runtime concept |
| **APEX_CANON.md** (this file) | — | — | **All 6** | **Formal core** |
| **Total** | **1,506+** | **63,156+** | — | — |

---

## 10. Versioning

- **v2026.06.20** — Initial formal core. Grand equation, 6 axiom
  families, verdict lattice, verification procedure. Derived from
  5 dimension docs + APEX_THEORY.md + live kernel code.

**Tag convention:** `vYYYY.MM.DD` per federation IRON RULE.

---

**DITEMPA BUKAN DIBERI** — The equation is forged through axioms, not assumed through confidence.
