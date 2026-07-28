# NEXT HORIZON ARCHITECTURE — Unified Federation
**Date:** 2026-07-28 | **Session:** SEAL-ff91ae20f90a4985
**Authority:** OBSERVE_ONLY | **Status:** Target architecture (not executed)

---

## 1. Organ Boundaries

### Kernel (arifOS) — Constitutional Authority
```
Port: 8088
Stack: Python 3.13, FastMCP 3.4.4
Role: JUDGE. Owns floors, verdicts, identity, seal.
```

**Owns:**
- F1–F13 floor definitions and evaluation
- Verdict grammar: SEAL / HOLD / VOID / SABAR
- F13 SOVEREIGN authority — human veto
- Ed25519 identity verification (challenge-response nonce)
- VAULT999 immutable seal chain
- Gödel Lock — refusal to act when confidence < threshold
- F7 Humility — anti-overclaim enforcement, Ω₀ ∈ [0.03, 0.05]
- G-space / J-space category boundary
- APEX scalars: G, C_dark, W3, h, QDF

**Forbidden:**
- Cannot execute (no mutation tools on kernel)
- Cannot route (no organ dispatch — use arif_route)
- Cannot metabolize (no receipt ingestion — use arifFlow)

**Public tools:** 8 kernel tools: `arif_init`, `arif_observe`, `arif_think`, `arif_route`, `arif_memory`, `arif_judge`, `arif_forge`, `arif_seal`

---

### AAA — Coordination / Mind State
```
Port: 3001
Stack: React 19, Vite, Tailwind 4
Role: COORDINATE. Emits proposals, reasoning envelopes, critique envelopes.
```

**Owns:**
- SALAM boot ceremony prompts
- AAA-ZEN-ALIGNMENT doctrine
- QQQ recommendation protocol
- A2A agent cards and protocol
- Carry-forward state (coordination memory, NOT truth)
- Federation cockpit UI

**Forbidden:**
- Cannot SEAL — no seal authority
- Cannot authorize — no self-approve
- Cannot execute mutations — must route through A-FORGE
- Cannot judge — must route to arif_judge
- Cannot define floors — reference arifOS only

**Deliverables:** `proposal {id, reasoning, alternatives, recommendation, verdict_hint}`

---

### A-FORGE — Actuation / Governed Execution
```
Ports: 7071 (API), 7072 (MCP)
Stack: Node 22+, TypeScript 6, Express 5
Role: EXECUTE. Runs under lease with plan-id, judge-state-hash.
```

**Owns:**
- Execution tools (file, code, deploy, git, network)
- `PlanGovernanceGate` — validates plans before execution
- `ModelCapabilityGate` — validates tool capability
- `AmanahLockManager` — distributed mutex for reversible-first
- `ApprovalBoundary` — hold queue for human-in-loop
- Dry-run default — explicit override required for mutation

**Forbidden:**
- Cannot judge — must route to arif_judge
- Cannot seal — must route to arif_seal
- Cannot self-authorize — requires approved plan + authority envelope
- Cannot skip receipt — every execution emits receipt to arifFlow

**Gate pipeline (actual, verified 2026-07-27):**
```
Request → ModelCapabilityGate (thin) → PlanGovernanceGate (deliberative)
        → [HOLD → ApprovalBoundary] | [ALLOW → Execute → Receipt]
```

---

### arifFlow — Metabolism / Receipt Flow
```
Port: 7073
Stack: Rust (daemon) + Python bindings
Role: METABOLIZE. Tracks flow quotient, receipt ratios, execution verification.
```

**Owns:**
- Flow Quotient (FQ = verify/execute ratio)
- Receipt routing — canonical channel for execution evidence
- BSP (Bulk Synchronous Parallel) scheduling
- Simulation-collapse detection
- Attention checkpointing — cooling signals

**Forbidden:**
- Cannot judge — routes receipts, never adjudicates
- Cannot execute — no execution tools
- Cannot seal — no seal authority

**Known gap:** Daemon loses in-memory state on restart. FQ and receipt count reset to 0. Needs persistence layer.

---

### Hermes — Communication / Routing
```
Stack: Python, Telethon, Telegram Bot API
Role: BRIDGE. Routes between Telegram ↔ arifOS ↔ agents.
```

**Owns:**
- Telegram DM/group routing
- Skill catalog index (`skills/`)
- Channel directory
- RESTART protocol (gateway/restart_loop.json)

**Forbidden:**
- Cannot become judge
- Cannot escalate own authority
- Cannot mutate federation state

---

### Organs (Witness Layer)

| Organ | Port | Role | Witness Domain |
|---|---|---|---|
| **GEOX** | :8081 | Reality witness | Earth science, wells, seismic, petrophysics |
| **WEALTH** | :18082 | Allocation witness | Capital, NPV, IRR, EMV (compute, never allocate) |
| **WELL** | :18083 | Vitality witness | Human readiness, biometrics, fatigue (REFLECT_ONLY) |

**All witness organs share:**
- Compute, never adjudicate
- APEX scalars mirrored from arifOS
- Cannot evaluate floors
- Cannot self-certify
- Outputs tagged with epistemic uncertainty

---

## 2. Authority Flow

```
Arif (F13)
  │
  ▼
arif_init → arif_think → arif_judge → [SEAL] → arif_forge → arif_seal
  000        333          888           GO       777          999
  │          │            │                       │            │
  │          │            ├─ HOLD → AAA(hold queue)│            │
  │          │            ├─ VOID → stop           │            │
  │          │            └─ SABAR → wait          │            │
  │          │                                    │            │
  │          └── arif_route ──┬── GEOX             └── Receipt ─┘
  │                           ├── WEALTH                      │
  │                           └── WELL                         ▼
  └── arif_memory ───── L1-L6 memory                     arifFlow
```

---

## 3. Receipt Flow

```
A-FORGE execution → receipt {plan_id, tool, action, result_hash, timestamp}
       │
       ▼
   arifFlow.ingest(receipt)
       │
       ├── update FQ = verify_count / execute_count
       ├── store receipt (in-memory, targeted: persistent)
       ├── check simulation-collapse threshold
       └── emit cooling signal if FQ < 1.0
```

---

## 4. Failure Flow

| Failure | Detect | Action |
|---|---|---|
| arif_judge unreachable | Health probe failure | Gate all mutation. Hold queue fills. Arif notified. |
| A-FORGE lease timeout | arifFlow detects max step exceeded | Close lease. Seal a HOLD receipt. |
| arifFlow down | Health probe failure | Receipts stale. FQ frozen at last value. No metabolic signal. |
| C_dark > 0.30 | F9 floor evaluation | arif_judge returns HOLD. Contradiction scan triggered. |
| Identity challenge failed | arif_init returns actor_verified=false | Remain OBSERVE_ONLY. No mutation. No seal. |

---

## 5. Rollback Flow

```
1. arif_seal(mode=reversion, previous_sha=..., reason=...)
   → VAULT999 appends reversion entry (new SHA, references old SHA)
   → A-FORGE reverts execution state
   → arifFlow updates FQ
   → Memory reindexed
   
Rule: Never overwrite. Always append.
The reversion IS the history.
```
