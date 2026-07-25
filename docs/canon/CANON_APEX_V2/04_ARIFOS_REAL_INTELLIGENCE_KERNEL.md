---
canon_id: 04_ARIFOS_REAL_INTELLIGENCE_KERNEL
bundle: CANON_APEX_V2
version: v2026.07.APEX
status: SEALED_CANON
apex_theory: T-000
floors_version: 2026.07
epoch: 2026-07-26T00:30+08
source: GENESIS/000_KERNEL_CANON.md · arifOS kernel :8088
---

# arifOS — Real Intelligence Kernel

> **DITEMPA BUKAN DIBERI — Intelligence is forged, not given.**

## What arifOS Is

arifOS is the **constitutional governance kernel** for the AI agent federation.
It is NOT a model, a chatbot, a startup, or a replacement for human judgment.
It IS the law layer between agents and tools — the engine that enforces
13 constitutional floors, the single gate for irreversible actions, and
the owner of VAULT999.

**One sentence:** arifOS decides what must NOT be done, so agents can be
trusted with what they CAN do.

## Federation Architecture

```
Arif (F13 SOVEREIGN — human, final veto)
         │
    arifOS (Ω — constitutional kernel, :8088)
    ├── F1–F13 floor enforcement
    ├── 888 JUDGE (verdict engine)
    ├── 999 VAULT (immutable ledger)
         │
    ┌────┼────┬────────┬────────┬────────┐
    │    │    │        │        │        │
  GEOX  WEALTH  WELL   AAA     A-FORGE  APEX
  Earth Capital Human  Cockpit  Forge   888 Judge
  8081  18082  18083   3001     7071    (absorbed)
```

## Core Invariants

### 1. Separation of Powers
- **arifOS judges** — never executes
- **A-FORGE executes** — never judges
- **GEOX/WEALTH/WELL witness** — never decide
- **AAA routes** — never overrides kernel judgment
- **Arif vetoes** — F13 absolute, no machine override

### 2. The Metabolic Pipeline (000→999)
```
000 INIT     → Session bootstrap, actor bind, intent scan
111 OBSERVE  → Reality grounding, 8-stage pipeline
333 THINK    → Structured reasoning, contradiction detection
444 ROUTE    → Intent → organ dispatch
555 MEMORY   → Governed semantic recall (L1–L6)
666 JUDGE    → Constitutional verdict: SEAL/HOLD/SABAR/VOID
777 FORGE    → Guarded execution (SEAL required)
999 SEAL     → Immutable VAULT999 append (irreversible)
```

### 3. 13 Constitutional Floors
As defined in 01_000_THEORY_UNIFIED_MAP (binding). Every organ references
this table verbatim. No organ may redefine F1–F13.

### 4. VAULT999 Immutability
Append-only, hash-chained JSONL ledger. Ed25519 signing. chattr +a
immutability. New entries only — never edit, rewrite, or "clean up."
Derivative queries via Supabase vault_sealed_events — for queries only,
NEVER source of truth.

### 5. Session Binding
Every session requires `arif_init(actor_id, intent)` → session_id +
session_token (sct_v1.*). No session = no mutation. No session_token =
no seal. OBSERVE_ONLY + mutation intent = 888_HOLD.

### 6. Epistemic Discipline
All claims carry OBS/DER/INT/SPEC label. Confidence cap = 1 − Ω₀ ∈
[0.95, 0.97]. Overconfidence = F7 violation.

## Organ Boundaries (Hard)

| Organ | CAN | CANNOT |
|:------|:----|:-------|
| arifOS | Judge, seal, govern | Execute, compute domain evidence |
| A-FORGE | Build, deploy, execute | Judge, seal, self-authorize |
| GEOX | Earth evidence, geophysics | Issue verdicts, allocate capital |
| WEALTH | Capital math, market data | Allocate capital, issue verdicts |
| WELL | Vitality reflect, substrate classify | Diagnose, adjudicate, allocate |
| AAA | Route, identify, display | Judge, execute, override kernel |

## Live Truth

- Kernel: `curl :8088/health` → verdict, floors, drift
- Vault: `curl :999/verify` → head hash, chain status
- Human root: `https://arif-fazil.com/000/`

DITEMPA BUKAN DIBERI — Governance is forged through walls, not through trust.

---
CANON_STATUS: SEALED · APEX THEORY
CANON_BUNDLE: CANON_APEX_V2 (13 files)
GOVERNANCE_CORE: arifOS · APEX Theory · F1–F13 Floors
VAULT999_HASH: <pending>
TRI-WITNESS: human · AI · earth >= 0.75
