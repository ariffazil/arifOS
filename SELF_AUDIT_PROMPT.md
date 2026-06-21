# SELF_AUDIT_PROMPT.md — arifOS Kernel Self-Critique & Hardening

> **F1 F2 F4 F7 F8 F11 F13** — This prompt is a constitutional instrument.
> Agents loading this prompt MUST run the full loop below before any kernel mutation.
> **DITEMPA BUKAN DIBERI** — even the kernel must earn its own hardening.

---

## 0. LIVE STATE BASELINE (Read before acting)

From attestation on 2026-06-14 17:26 UTC:
```
arifOS            → ALIVE   v2026.05.05-SSCT   tools=13  hash_ok=YES
GEOX              → ALIVE   v2026.06.05         tools=40  hash_ok=YES
WEALTH            → ALIVE   2026.05.02          tools=20  hash_ok=YES
WELL              → ALIVE   2026.05.15-ΩWELL     tools=18  hash_ok=YES
AAA               → ALIVE   (React+A2A)         port=3001
A-FORGE           → ALIVE   (TS Express)        port=7071
```

**Known gaps** (confirmed by live probe):
1. `identity_anchor_hash` → `sha256:pending` in arifOS — NO identity anchor bound
2. `actor_verified: false` — NO actor verification chain exists
3. `session_id: unknown/empty` — NO session binding at kernel level
4. Constitution hash is shared but **not enforced** at runtime or CI — drift is invisible
5. No self-audit loop exists: agents do not critique their own plans before execution

---

## 1. THE REFLEXION LOOP (Every kernel change MUST follow this)

```
┌─────────────────────────────────────────────────────────────┐
│  KERNEL HARDENING REFLEXION LOOP                            │
│                                                             │
│  000 ─→ CLARIFY TASK ─→ 111 ─→ GATHER EVIDENCE              │
│   ↑                               │                         │
│   │                               ↓                         │
│   │                          333 ─→ DRAFT CHANGE            │
│   │                               │                         │
│   │                               ↓                         │
│   │                          555 ─→ SELF-CRITIQUE           │
│   │                               │                         │
│   │                               ↓                         │
│   │                          777 ─→ COMPARE & DECIDE        │
│   │                               │                         │
│   │                               ↓                         │
│   │                          888 ─→ AUDIT TRAIL TO VAULT    │
│   │                               │                         │
│   │                               ↓                         │
│   └──── 999 ─→ SELF-IMPROVEMENT ←─┘                         │
│                                                             │
│  If critique finds gaps → go back to 333                     │
└─────────────────────────────────────────────────────────────┘
```

### Step 000 — Clarify

Restate the concrete hardening target in **one sentence**.  
Classify: `CONFIG_CHANGE | POLICY_CHANGE | INFRA_CHANGE | IRREVERSIBLE`

### Step 111 — Gather Evidence

Call **at minimum** these probes:
```
arif_os_attest()                    → kernel live envelope
arif_organ_attest_all()             → all 7 organs live (arifOS, GEOX, WEALTH, WELL, AAA, A-FORGE, VAULT999)
arif_ops_measure(mode='health')     → CPU/mem/disk bands
arif_schema_echo()                  → transport bridge integrity
```

Tag every finding:
- `OBS` — directly measured
- `DER` — derived from measurement
- `INT` — interpreted
- `SPEC` — speculation (do NOT act on SPEC alone)

### Step 333 — Draft Change (Architect)

Propose the minimal change. For each proposal:
- **what** it changes (exact file, function, config key)
- **which floor** it strengthens (F1–F13)
- **rollback** — how to undo in ≤2 commands
- **test** — how to verify it works

**Current priority gaps** (forge these first):
1. Bind `identity_anchor_hash` from `sha256:pending` to actual constitution hash
2. Add `actor_verified` enforcement — every session MUST verify actor
3. Add runtime constitution hash comparison (current vs sealed)
4. Add `forge_execute` pre-flight critic call

### Step 555 — Self-Critique (Auditor)

Switch roles. Treat your proposal as if from someone else. Attack it:
- Where is evidence thin?
- What assumptions untested?
- Failure modes? (double-hash, blocked valid sessions, vault bricking)
- What did you NOT measure?

**Critique must include:**
```
critique:
  severity: BLOCKER | MAJOR | MINOR | INFO
  evidence_gap: <what fact is missing>
  failure_mode: <what breaks if this gap is real>
  alternative: <simpler fix>
```

### Step 777 — Compare & Decide (Clerk)

```
verdict: APPLY | 888_HOLD | VOID
fallback: <more conservative plan>
open_questions: [<list of unknowns requiring human eyes>]
```

### Step 888 — Audit Trail

Emit structured artifact suitable for VAULT999:
```
change_id:    KER-<date>-<seq>
component:    kernel | AAA | A-FORGE
risk_band:    LOW | MEDIUM | HIGH | CRITICAL
evidence_refs: [<probe call IDs>]
holds:        [<open question IDs>]
verdict:      APPLY | 888_HOLD | VOID
rollback:     <command>
approved_by:  <actor_id or "888_HOLD_PENDING">
```

### Step 999 — Self-Improvement

Derive from this session:
- 2–3 **enduring rules** to add to AGENTS.md or CI
- 2–3 **prompt/config updates** (e.g. "all forge_execute calls must pre-flight critic")
- Tag: `SAFE_TO_AUTOMATE | MANUAL_EDIT_REQUIRED`

---

## 2. HARDENING PRIORITIES (Ratified 2026-06-14)

### P0 — Identity Anchor (BLOCKER)
```
gap:  identity_anchor_hash = sha256:pending
fix:  Bind to constitution_hash at kernel boot
test: arif_os_attest() returns matching hashes
floor: F2 TRUTH — the kernel must know its own identity
```

### P1 — Actor Verification (HIGH)
```
gap:  actor_verified = false across ALL organs
fix:  Implement session-level actor verification chain
      Every tool call must carry verified actor_id
test: Call with forged actor_id → 888_HOLD rejection
floor: F8 LAW — system boundaries require actor identity
```

### P2 — Session Binding (HIGH)
```
gap:  session_id = unknown/empty on kernel calls
fix:  Refuse calls without valid session_id
      Session must be initiated via arif_session_init
test: Call without session → VOID
floor: F1 AMANAH — every action must be traceable to a session
```

### P3 — Constitution Drift Detection (MEDIUM)
```
gap:  No runtime constitution hash comparison
fix:  Add hash check in forge_execute and every organ attest
      CI must compare committed vs runtime hashes
test: Modify constitution → attest shows drift alarm
floor: F2 TRUTH — constitution must be verifiably consistent
```

### P4 — Reflexion Pre-Flight (MEDIUM)
```
gap:  No self-critique before forge execution
fix:  All forge_execute calls must first run critic pass
      Store critic verdict alongside execution receipt
test: forge_execute without critic → BLOCKED
floor: F7 HUMILITY — never execute without self-critique
```

---

## 3. META-RULES FOR SELF-AUDIT

1. **Every major response gets a built-in critic pass**
   - After proposing any nontrivial change, run at least one internal critic loop
   - The critic may downgrade CLAIM → PLAUSIBLE, upgrade HOLD, propose alternatives

2. **No invisible assumptions**
   - Any reliance on "probably configured like X" must be marked `HYPOTHESIS` until measured
   - Audit output must call out **unknowns**, not only decisions

3. **Periodic post-mortem**
   - When applied changes fail, extract: root cause, durable fix, store lesson
   - Lessons go into `memory/` for future sessions to reuse

4. **Human remains sovereign**
   - Any change affecting: execution authority, approval rules, vault behavior, identity verification
   - → `888_HOLD` — blocked until Arif approves

---

## 4. OUTPUT FORMAT (Per Session)

```
## Summary
- <3-5 bullets: weaknesses found, changes proposed, biggest risks>

## Change Proposals
| Component | Change | Evidence | Risk Band | Rollback | Verdict |
|-----------|--------|----------|-----------|----------|---------|
| kernel    | ...    | [OBS]    | HIGH      | ...      | APPLY   |
| AAA       | ...    | [DER]    | MEDIUM    | ...      | HOLD    |

## Self-Critique
- <where your reasoning was weakest>
- <assumptions you failed to test>
- <what you'll do differently next run>

## Telemetry
```json
{
  "epoch": "<ISO8601>",
  "component": ["kernel","AAA","A-FORGE"],
  "dS": "<ESTIMATE>",
  "peace2": "<ESTIMATE>",
  "holds": ["<id>"],
  "verdict": "APPLY|HOLD|VOID"
}
```
```

---

*Forged 2026-06-14 by FORGE (000Ω) — live attestation data baked in*
*DITEMPA BUKAN DIBERI — the kernel earns its hardening every cycle*
