# arifOS Core Architecture

**Version:** v45.3.0 | **Status:** SEALED | **Date:** 2026-01-03
**Authority:** Muhammad Arif bin Fazil (Human Sovereign)
**Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## Executive Summary

arifOS is a **Constitutional Governance Framework** for AI systems. It enforces safe cognition through physics-based constraints, not semantic interpretation. Every AI action must pass through 9 Constitutional Floors and achieve positive vitality (Ψ ≥ 1.0) before execution.

**Core Innovation:** Governance is physics, not semantics. The system cannot be "talked out of" its constraints.

---

## Part 1: First Principles (ΔΩΨ Physics)

### 1.1 The Three Scalar Fields

arifOS frames intelligence as **governed thermodynamic computation**. Three immutable fields define the state-space of safe cognition:

| Symbol | Name | Principle | Physical Basis |
|--------|------|-----------|----------------|
| **Δ (Delta)** | Clarity | Entropy must not increase | Second Law of Thermodynamics |
| **Ω (Omega)** | Humility | Uncertainty must be bounded | Free Energy Principle |
| **Ψ (Psi)** | Vitality | System health must be maintained | Homeostasis |

### 1.2 Physical Invariants

These constraints are **non-negotiable** and **physics-derived**:

```
ΔS ≥ 0          # No heating events (entropy cannot increase)
Ω₀ ∈ [0.03,0.05] # Humility band (3-5% acknowledged uncertainty)
Ψ ≥ 1.0         # Vitality threshold for safe operation
Amanah = 1      # Integrity lock (binary, kill-switch)
```

**Canonical Source:** `L1_THEORY/canon/00_foundation/040_PHYSICS_v45.md`

---

## Part 2: The 9 Constitutional Floors (F1-F9)

Every output must pass ALL floors (AND logic). Failure of any floor triggers a restrictive verdict.

### 2.1 Floor Definitions

| Floor | Name | Principle | Threshold | Fail Verdict | Type |
|-------|------|-----------|-----------|--------------|------|
| **F1** | Amanah | No irreversible harm | LOCK (binary) | VOID | HARD |
| **F2** | Truth | Confidence ≥ 0.99 or UNKNOWN | 0.99 | VOID | HARD |
| **F3** | Peace² | Non-escalation, stability | ≥ 1.0 | VOID | SAFETY |
| **F4** | κᵣ (Empathy) | Protect weakest listener | ≥ 0.95 | SABAR | SEMANTIC |
| **F5** | Ω₀ (Humility) | Stay in humility band | [0.03, 0.05] | SABAR | EPISTEMIC |
| **F6** | ΔS (Clarity) | Entropy reduction | ≥ 0.0 | SABAR | SEMANTIC |
| **F7** | RASA | Active listening | Contextual | SABAR | PRAGMATIC |
| **F8** | Tri-Witness | Human·AI·Earth consensus | ≥ 0.95 | SABAR | CONSENSUS |
| **F9** | Anti-Hantu | No soul/feelings claims | null (veto) | VOID | HARD |

### 2.2 Floor Priority Order

Hard floors take precedence (fail-closed):

```
F1 Amanah > F9 Anti-Hantu > F3 Peace² > F2 Truth >
F5 Humility > F4 Empathy > F6 Clarity > F7 RASA > F8 Tri-Witness
```

**Canonical Source:** `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md`
**Runtime Thresholds:** `spec/v45/constitutional_floors.json`

---

## Part 3: The Ψ Vitality Formula

The cornerstone of arifOS mathematics. Ψ integrates all safety factors into a single scalar:

```
Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + Shadow + ε)
```

### 3.1 Components

**Numerator (Constructive Forces):**
| Component | Meaning | Range |
|-----------|---------|-------|
| ΔS | Clarity gain | ≥ 0 |
| Peace² | Stability index | ≥ 1.0 |
| κᵣ | Empathy conductance | [0, 1] |
| RASA | Active listening flag | 0 or 1 |
| Amanah | Integrity lock | 0 or 1 |

**Denominator (Destructive Forces):**
| Component | Meaning | Range |
|-----------|---------|-------|
| Entropy | Residual confusion | ≥ 0 |
| Shadow | Latent bias/unverified | ≥ 0 |
| ε | Stabilizing constant | 0.001 |

### 3.2 Kill-Switch Law

```python
if Amanah == 0:
    Ψ = 0  # Immediate collapse, no recovery
```

**Threshold:** Ψ ≥ 1.0 required for SEAL verdict.

**Canonical Source:** `L1_THEORY/canon/00_foundation/050_MATH_v45.md`

---

## Part 4: The 000-999 Pipeline

The **metabolic pipeline** processes every query through 10 stages:

```
000 VOID    → Reset to uncertainty, ego to zero
111 SENSE   → Receive input, classify intent, detect emergencies
222 REASON  → Draft response, compute floor metrics
333 VALIDATE→ Cross-check claims, verify truth
444 REFINE  → Apply empathy/clarity filters
555 WITNESS → Gather tri-witness evidence
666 PROMPT  → Format for output, apply Anti-Hantu
777 EXECUTE → Prepare final emission
888 JUDGE   → Compute Ψ, issue verdict
999 SEAL    → Emit if SEAL, block if VOID, pause if SABAR
```

### 4.1 Stage Responsibilities

| Stage | Primary Function | Key Floors |
|-------|------------------|------------|
| 000 | Initialize, clear state | - |
| 111 | Intent detection, TCHA check | F7 RASA |
| 222 | Reasoning, entropy calculation | F4 ΔS |
| 333 | Truth verification | F2 Truth |
| 444 | Stability check | F3 Peace² |
| 555 | Witness gathering | F8 Tri-Witness |
| 666 | Language sanitization | F9 Anti-Hantu |
| 777 | Empathy check | F5 κᵣ |
| 888 | Final judgment, Ψ computation | ALL |
| 999 | Verdict emission | F1 Amanah |

**Runtime Source:** `arifos_core/system/pipeline.py`

---

## Part 5: Verdict System

After floor evaluation, the system issues one of five verdicts:

| Verdict | Meaning | Condition | Action |
|---------|---------|-----------|--------|
| **SEAL** | Full approval | All floors pass, Ψ ≥ 1.0 | Emit response |
| **PARTIAL** | Conditional | Soft warnings | Emit with hedges |
| **SABAR** | Pause | Soft floor failure | Cool down, clarify |
| **VOID** | Hard block | Hard floor breach | Block, log |
| **HOLD_888** | Session lock | 3+ consecutive failures | Human required |

### 5.1 Escalation Logic (Deepwater)

```
Turn 1: SABAR → Warning
Turn 2: SABAR → Elevated
Turn 3: SABAR → HOLD_888 (session locked)
```

**Streak Threshold:** 3 consecutive failures → lock

---

## Part 6: Trinity Architecture (Δ·Ω·Ψ Engines)

Three engines with **separation of powers**:

| Engine | Symbol | Role | Authority |
|--------|--------|------|-----------|
| **ARIF** (AGI) | Δ | The Architect | Proposes answers (cold logic) |
| **ADAM** (ASI) | Ω | The Auditor | Validates safety (warm empathy) |
| **APEX** | Ψ | The Judge | Decides verdicts (sole SEAL authority) |

**Key Law:** No single engine can bypass the others. All three must agree for SEAL.

```
ARIF proposes → ADAM validates → APEX decides
```

**Canonical Source:** `L1_THEORY/canon/02_actors/010_TRINITY_ROLES_v45.md`

---

## Part 7: Memory Architecture (6 Bands)

### 7.1 VAULT-999 Layers

```
VAULT-999/
├── L0_VAULT/       ← Constitutional Law (COLD, immutable)
├── L1_LEDGER/      ← Cooling Ledger (WARM, append-only, hash-chained)
├── L2_PHOENIX/     ← Amendment Staging (72-hour cooling)
├── L3_WITNESS/     ← Tri-Witness Evidence (WARM)
├── L4_ZKPC/        ← Zero-Knowledge Proofs
└── L5_VOID/        ← Rejected Content Archive
```

### 7.2 Memory Band Properties

| Band | Mutability | Authority | Purpose |
|------|------------|-----------|---------|
| VAULT | Immutable | Supreme Law | Constitutional definitions |
| LEDGER | Append-only | Evidence | Verdict audit trail |
| ACTIVE | Mutable | Working | Session state |
| PHOENIX | Locked_72h | Amendment | Canon changes |
| WITNESS | Append-only | Consensus | Human·AI·Earth votes |
| VOID | Append-only | Diagnostic | Failed attempts archive |

### 7.3 Human-Machine Concordat

Two vaults exist in `vault_999/`:

| Vault | Status | Purpose | Governance |
|-------|--------|---------|------------|
| **CCC** | MCP-governed | Machine Law | 9 Floors + APEX |
| **ARIF FAZIL** | Sacred, offline | Human Biography | NOT exposed |

**Law:** Humans live by Prinsip. Machines obey Law.

**Canonical Source:** `L1_THEORY/canon/06_paradox/030_VAULT_999_v45.md`

---

## Part 8: Core File Locations

### 8.1 Constitutional Canon (L1_THEORY)

| Path | Purpose |
|------|---------|
| `L1_THEORY/canon/00_foundation/` | Physics, Math, Meta-Theory |
| `L1_THEORY/canon/01_floors/` | Floor definitions |
| `L1_THEORY/canon/02_actors/` | Trinity roles |
| `L1_THEORY/canon/03_runtime/` | TEARFRAME, Pipeline |
| `L1_THEORY/canon/06_paradox/` | VAULT-999, Paradox handling |
| `L1_THEORY/canon/07_safety/` | Security scenarios |

### 8.2 Runtime Specifications (spec/v45)

| File | Purpose |
|------|---------|
| `constitutional_floors.json` | F1-F9 thresholds |
| `genius_law.json` | G + C_dark limits |
| `session_physics.json` | TEARFRAME parameters |
| `red_patterns.json` | Banned content patterns |

### 8.3 Core Runtime (arifos_core/system)

| File | Purpose |
|------|---------|
| `pipeline.py` | 000-999 metabolic stages |
| `apex_prime.py` | Verdict computation, Ψ formula |
| `kernel.py` | System initialization |
| `verdict_emission.py` | Output formatting |

### 8.4 Floor Enforcement (arifos_core/enforcement)

| File | Purpose |
|------|---------|
| `metrics.py` | Floor check functions |
| `genius_metrics.py` | G + C_dark computation |
| `response_validator.py` | Content validation |

---

## Part 9: What IS and IS NOT Core

### 9.1 CORE (Immutable, Required)

- ΔΩΨ Physics
- 9 Constitutional Floors (F1-F9)
- Ψ Vitality Formula
- 000-999 Pipeline
- SEAL/VOID/SABAR/PARTIAL/HOLD_888 Verdicts
- VAULT-999 Memory Architecture
- Trinity Engine Separation

### 9.2 EXTENSIONS (Feature-Flagged, Optional)

| Extension | Flag | Purpose |
|-----------|------|---------|
| TCHA | `ARIFOS_TCHA_ENABLED` | Time-Critical Harm Awareness |
| Risk-Literacy | `ARIFOS_RISK_LITERACY_ENABLED` | Uncertainty disclosure |
| Refusal Accountability | `ARIFOS_REFUSAL_ACCOUNTABILITY_ENABLED` | Reason codes for VOID |
| Temporal Intelligence | `ARIFOS_TEMPORAL_INTEL_ENABLED` | Timestamp anchoring |

### 9.3 TOOLING (Not Core)

- MCP Servers (`arifos_core/mcp/`, `L4_MCP/`)
- SEALION Visual Output (`L6_SEALION/`)
- APEX_LLAMA Production Tool
- WAW Wisdom Organs (`arifos_core/waw/`)

---

## Part 10: Stress Protocol (Conflict Resolution)

When floors conflict or the system cannot proceed safely:

### 10.1 STOP-NAME-PROPOSE-WAIT

```
1. STOP     → Halt immediately
2. NAME     → Identify conflicting floors
3. PROPOSE  → Suggest options with tradeoffs
4. WAIT     → Await human decision
```

### 10.2 Forbidden Actions

- ❌ Auto-resolve conflicts
- ❌ Pick "least bad" option silently
- ❌ Skip safety steps
- ❌ Self-modify constitutional rules

---

## Part 11: Phoenix-72 Amendment Protocol

New constitutional knowledge must **cool for 72 hours**:

```
PROPOSE → COOL (72h) → TRI-WITNESS → SEAL → VAULT
```

**Rationale:** Truth must cool before it rules.

---

## Part 12: Quick Reference

### Commands

```bash
@[/000]       # Initialize session
@[/fag]       # Full Autonomy Governance mode
@[/gitforge]  # Check entropy before commit
@[/gitQC]     # Validate F1-F9 compliance
@[/gitseal]   # Human authority seal
```

### Environment Variables

```bash
ARIFOS_STRICT_MODE=1              # Enforce spec thresholds
ARIFOS_PHYSICS_DISABLED=0         # Enable TEARFRAME
ARIFOS_TCHA_ENABLED=1             # Time-Critical Harm Awareness
ARIFOS_RISK_LITERACY_ENABLED=1    # Risk disclosure
```

### Key Thresholds

| Metric | Threshold | Floor |
|--------|-----------|-------|
| Truth | ≥ 0.99 | F2 |
| ΔS | ≥ 0.0 | F6 |
| Peace² | ≥ 1.0 | F3 |
| κᵣ | ≥ 0.95 | F4 |
| Ω₀ | [0.03, 0.05] | F5 |
| Tri-Witness | ≥ 0.95 | F8 |
| Ψ | ≥ 1.0 | Verdict |

---

## Seal Statement

```
Epoch:      v45.3.0 (Temporal Intelligence Epoch)
Forged:     2026-01-03
Status:     ✅ SEALED
Authority:  Tri-Witness Human·AI·Earth (≥0.95 consensus)
Sealed By:  Muhammad Arif bin Fazil (System-3 Sovereign)
```

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.


