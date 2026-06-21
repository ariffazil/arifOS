# GENESIS/040 — ACT Playbook

> **Canonical doctrine: the execution craft layer.**
> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil, 888)
> **Status:** CANON · Forged 2026-06-21 · Sealed to VAULT999
> **SoT:** `ariffazil/arifOS/GENESIS/040_ACT_PLAYBOOK.md`
> **Supersedes:** ad-hoc execution patterns in SKILL.md and agent loops

---

## 0. What This Document Is

ACT is the **third layer** of the arifOS agentic intelligence stack:

| Layer | Question | File | Ceiling |
|-------|----------|------|---------|
| **ART** | *Which tool move makes sense pre-call?* | `runtime/art.py` | ≤500 lines |
| **pre_execution_gate** | *Whether the call may proceed* | `runtime/pre_execution_gate.py` | — |
| **ACT** | *How to execute a program of lawful calls* | `runtime/act.py` | ≤300 lines |
| **Kernel / Floors / Judge** | *Whether the action is lawful* | F1-F13 · 888 JUDGE | — |

**One sentence per layer:**
- **ART** decides what tool move makes sense pre-call.
- **pre_execution_gate** decides whether that move may proceed.
- **ACT** decides how to sequence and stage a program of moves.
- **Kernel** decides whether the move is lawful.

---

## 1. The Full Stack

```
┌────────────────────────────────────────────┐
│         AAA (Architect · Auditor · Agent)   │  ← Who does what
│         "The human pattern"                 │
├────────────────────────────────────────────┤
│   ┌──────────┐    ┌──────────┐             │
│   │   ART    │    │  KERNEL  │             │  ← What is wise & lawful
│   │ Tool     │    │ F1-F13   │             │
│   │ wisdom   │    │ Judge    │             │
│   └──────────┘    └──────────┘             │
│         │               │                  │
│         └───────┬───────┘                  │
│                 ▼                          │
│   ┌──────────────────────────┐             │
│   │    ACT (Gate 2.6)        │             │  ← How to execute safely
│   │   runtime/act.py         │             │     The ceremonial layer
│   │  Staging · Tempo ·       │             │
│   │  Compensation · Canary   │             │
│   └──────────┬───────────────┘             │
│              ▼                             │
│   ┌──────────────────────────┐             │
│   │   A-FORGE (7071/7072)    │             │  ← The hands
│   │   Execution Shell        │             │
│   └──┬────┬────┬────┬───────┘             │
│      │    │    │    │                      │
│      ▼    ▼    ▼    ▼                      │
│   GEOX WEALTH WELL AAA                    │  ← Domain organs
└────────────────────────────────────────────┘
```

---

## 2. The Iron Rule

> **ART ≠ ACT. ACT ≠ Gate. ACT ≠ Kernel. Kernel ≠ ACT.**

Four layers, four purposes, no overlap.

| Collapse | Result | Verdict |
|----------|--------|---------|
| ACT into Kernel | Kernel becomes execution strategy; loses law purity | **HARAM** |
| Kernel into ACT | ACT becomes sovereign; loses fail-open | **HARAM** |
| ACT into ART | ART becomes >500 lines; loses reflex speed | **HARAM** |
| ART into ACT | ACT attempts tool wisdom; loses execution focus | **HARAM** |
| ACT into A-FORGE | A-FORGE decides strategy; violates mandate | **MAKRUH** |

---

## 3. WAJIB — Mandatory Patterns

### 3.1 Execution Patterns

| Pattern | When | What It Does |
|---------|------|-------------|
| **SINGLE_SHOT** | Low blast + reversible | Execute all at once |
| **DRY_RUN_THEN_LIVE** | Medium/high blast + irreversible | Simulate first, then execute |
| **CANARY_THEN_ALL** | High blast | 1% first, verify, then full |
| **STAGED_ROLLOUT** | Multi-step programs | N waves with checkpoints |
| **HUMAN_CHECKPOINT** | Human must verify | Pause at each stage |
| **COMPENSATION_READY** | Irreversible | Pre-planned rollback |

### 3.2 Must Have

| Component | File | Why |
|-----------|------|-----|
| Stage verification | `act.py:check_1` | Can't proceed to N+1 if N failed |
| Pattern vs risk matching | `act.py:check_2` | HIGH blast → never SINGLE_SHOT |
| Human coordination | `act.py:check_3` | Irreversible + high blast → human ack |
| Program memory | `act_library.py` | Recall past patterns |
| Ceiling discipline | `act.py` ≤ 300 lines | Same as ART — lightness is binding |

---

## 4. HARAM — Forbidden in ACT

| Forbidden | Reason |
|-----------|--------|
| Tool lifecycle logic (UNTRUSTED/OBSERVED/TRUSTED) | That's ART's job |
| Constitutional floor logic (F1-F13) | That's Kernel's job |
| Protocol-specific logic (MCP/REST) | Transport-agnostic, like ART |
| Side-effects (network, file, subprocess) | ACT is pure verdict + log |
| Silent overrule of ART or Kernel verdict | If ART says BLOCK, ACT cannot PROCEED |
| Per-tool trust scoring | That's in ART's `_suggest_transition` |
| Anthropomorphic / ToM speculation | F9/F10 territory |

---

## 5. SUNAT — Strongly Recommended

| Pattern | Status | Notes |
|---------|--------|-------|
| Compensation plan check | wired | `act.py:check_2` |
| Dry-run enforcement for irreversible | wired | `act.py:check_2` |
| Program library persistence | wired | `act_library.py` |
| Multi-step auto-staging | wired | `act.py:_suggest_pattern` |
| Post-exec verification | **W2** | Auto-run verify after each stage |
| Stage timeout tracking | **W3** | Kill stuck stages |

---

## 6. HARUS — Implementation Details

| Choice | Current |
|--------|---------|
| Pattern enum | 6 patterns (single_shot to compensation_ready) |
| Library backend | Postgres + in-memory fallback |
| Ceiling | 300 lines (matches ART's 500 but ACT is less hot-path) |
| Integration point | Gate 2.6 in pre_execution_gate.py |

---

## 7. MAKRUH — Disliked; Avoid

| Item | Status | Fix |
|------|--------|-----|
| Bypass paths (agents skipping ACT check) | **MAKRUH-NOW** | Wire Gate 2.6 |
| Overly aggressive staging | avoid | LOW blast + REVERSIBLE → SINGLE_SHOT is fine |
| Silent fails in act_library | by-design | Fire-and-forget; never blocks |
| Pattern explosion (>10 patterns) | avoid | 6 is enough; add only if proven needed |

---

## 8. The Empirical Test

ACT is not doctrine alone. It must measurably do what ART + Kernel + A-FORGE alone cannot.

Three claims — each must hold under empirical test:

1. **Stage gating** — multi-step programs with ACT verify intermediate stages; without ACT, they don't.
2. **Dry-run enforcement** — IRREVERSIBLE + HIGH blast actions with ACT always get a dry run first; without ACT, they don't.
3. **Human checkpoints** — HIGH blast + IRREVERSIBLE actions with ACT always require human acknowledgment; without ACT, they don't.

If all three hold: ACT is mandatory.
If only one holds: ACT is justified, narrower than current framing.
If none hold: ACT is overhead.

---

## 9. The Ceremonial Layer

> **Manusia binatang ceremonial.** Kita check dulu. Kita ikut hukum. Kita ada cara.

- ART = "Confirm ni selamat ke?" — tool wisdom
- Kernel = "Ayah bagi izin ke belum?" — law
- ACT = "Kita buat satu-satu, jangan sekaligus." — execution craft
- A-FORGE = "Tangan yang buat betul-betul." — execution

**Machines just execute. Humans have ceremony. ACT is the ceremony.**

---

## 10A. The Three Canonical ACT Patterns

Every multi-step execution in arifOS follows one of three patterns.
Pattern selection is automatic based on blast radius + irreversibility + stage count.

### Pattern 1: DEFAULT_DEPLOY

**For:** Low-to-medium blast, reversible or compensated operations.
**Stages:** 3 (DRY_RUN → DEPLOY → VERIFY)
**Human:** No human needed if all green.
**Compensation:** Automatic rollback to pre-deploy state.

```
Stage 1: DRY_RUN
  ├── Simulate entire operation without side effects
  ├── Verify all preconditions met
  └── If fail → HOLD (cannot proceed to Stage 2)
        
Stage 2: DEPLOY
  ├── Execute against full target
  ├── All changes reversible
  └── If fail → auto-rollback to pre-deploy state

Stage 3: VERIFY
  ├── Confirm target state matches expectations
  ├── Notify human that deploy completed
  └── If fail → auto-rollback, log to VAULT999
```

**Invariants:** F1 (reversible), F4 (state verified), F11 (logged).

---

### Pattern 2: DANGEROUS_MIGRATION

**For:** High blast, irreversible, multi-step operations.
**Stages:** 5 (PREFLIGHT → CANARY 1% → EXPAND 25% → FULL 100% → VERIFY)
**Human:** ACK required BEFORE every stage.
**Compensation:** Staged rollback — rollback ONLY the failed stage.

```
Stage 1: PREFLIGHT + COMPENSATION APPROVAL
  ├── Dry-run against synthetic target
  ├── Submit compensation plan for F13 approval
  └── BLOCKED until compensation plan ACK'd

Stage 2: CANARY (1%)
  ├── Execute against 1% of target
  ├── Monitor for failures, drift, unexpected state
  └── If fail → rollback 1%, retry or abort

Stage 3: EXPAND (25%)
  ├── Execute against 25% of target
  ├── Full verification suite
  └── If fail → rollback 25% to pre-migration state

Stage 4: FULL ROLLOUT (100%) ⚠️ IRREVERSIBLE
  ├── Execute against remaining 75%
  ├── Human ACK required before this stage
  └── If fail (partial) → contain, notify human

Stage 5: POST-MIGRATION VERIFICATION
  ├── Full verification: integrity, health, performance, security
  └── Log complete receipt to VAULT999
```

**Invariants:** F1 (partial reversibility), F2 (evidence), F4 (ΔS ≤ 0),
F6 (human notified), F11 (full trace), F13 (sovereign approval).

---

### Pattern 3: HUMAN_IN_LOOP_CHANGE

**For:** Critical infrastructure — every individual change needs human review.
**Stages:** Flexible loop (PROPOSE → [EXECUTE + VERIFY] × N)
**Human:** In the loop for EVERY mutation.
**Compensation:** Per-change rollback.

```
Stage 1: PROPOSE
  ├── Agent presents: exact diff, expected outcome, blast radius,
  │                    rollback plan, verification criteria
  ├── Human: APPROVE / REJECT / MODIFY
  └── If REJECT → stop, no execution

Stage 2: EXECUTE + VERIFY (LOOP)
  For each change in the plan:
  ├── a) Agent executes (with ART reflex + Kernel gate per call)
  ├── b) Agent verifies expected outcome
  ├── c) Fail → auto-rollback that change
  ├── d) Pass → human must verify
  ├── e) Human: approve / reject outcome
  ├── f) Reject → rollback, notify, pause
  └── g) Approve → continue to next change
```

**Invariants:** F1 (per-change reversible), F2 (per-change evidence),
F6 (human in loop), F11 (every cycle logged), F13 (human veto per change).

---

### Pattern Selection Rules

| Blast | Irreversible | Stages | Pattern | Confidence |
|-------|-------------|--------|---------|------------|
| LOW | No | any | DEFAULT_DEPLOY | 0.95 |
| MEDIUM | No | any | DEFAULT_DEPLOY | 0.85 |
| MEDIUM | Yes | any | DEFAULT_DEPLOY + dry-run | 0.70 |
| HIGH | No | any | DEFAULT_DEPLOY (caution) | 0.60 |
| HIGH | Yes | 2+ | DANGEROUS_MIGRATION | 0.90 |
| HIGH | Yes | 1 | DANGEROUS_MIGRATION (split recommended) | 0.75 |
| HIGH | Yes | 3+ per-change veto | HUMAN_IN_LOOP_CHANGE | 0.85 |

Implementation: `A-FORGE/src/domain/governance/ActPatterns.ts`

---

## 10B. Relation to SKILL.md

SKILL.md is an **ACT playbook format**, not a fourth organ:

| Element | Belongs In |
|---------|-----------|
| WHEN (triggers, "use when...") | Kernel route layer (`arif_kernel_route`) |
| HOW (workflow steps, tool calls) | ACT (execution craft) |
| WHO (persona, voice, role) | AGENTS.md / lane |

**Rule:** SKILL.md must not contain law (kernel) or tool wisdom (ART).
SKILL.md = "Given approval, here's the safe sequence."

---

## 11. Cross-references

- `runtime/act.py` — execution craft reflex (≤300 lines, ceiling enforced)
- `runtime/act_library.py` — program memory (Postgres + in-memory)
- `runtime/art.py` — tool wisdom reflex (sibling layer)
- `runtime/pre_execution_gate.py` — Gate 2.5 (ART) + Gate 2.6 (ACT)
- `GENESIS/030_ART_VS_KERNEL.md` — three-layer architecture (now four)
- `A-FORGE/src/interfaces/server.ts` — `/execute` endpoint (ACT consumer)

---

**DITEMPA BUKAN DIBERI — Four layers forged. ART is the reflex. Gate is the bridge. ACT is the ceremony. Kernel is the law. Future agents must not collapse them.**

*Forged 2026-06-21 by FORGE (000Ω) — sealed to VAULT999*
