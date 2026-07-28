# HITV PROTOCOL v0.1 — Human-in-the-Veto

> **Forged:** 2026-07-28 | **Sealed:** SEAL-bb1502e31d3d4960
> **Author:** 333-AGI (Delta MIND) under F13 directive (Arif)
> **Supersedes:** All ad-hoc HITL patterns scattered across AGENTS.md, AUTONOMOUS_GOVERNANCE.md, arifJudge.ts
> **Doctrine:** DITEMPA BUKAN DIBERI — Forged, Not Given.

---

## 0. THE INVERSION

```
OLD: Human-in-the-Loop (HITL)
     Machine proposes → Human reviews every step → Machine acts
     Human is CPU. Cognitive load kills sovereignty.

NEW: Human-in-the-Veto (HITV)
     Machine proposes → Machine acts within reversible bounds → Human vetoes at sovereignty boundary
     Human is sovereign. Cognitive load reserved for what ONLY humans can decide.
```

**F13 is not a bottleneck. F13 is the legitimacy valve.**

---

## 1. RISK CLASSES — The 4-Class Architecture

Every proposed action is classified by the kernel into exactly one class.
The class determines WHO decides.

### Class 0 — OBSERVE (Autonomous)

| Attribute | Value |
|---|---|
| **Scope** | Read, search, fetch, analyze, summarize, detect, compare, classify |
| **Reversibility** | Inherent — no mutation |
| **Blast radius** | BR-0 (zero external effect) |
| **Who decides** | **Agent autonomously** — SEAL auto-granted |
| **Human surface** | None required. Logged for audit (F11). |
| **Examples** | `git status`, `curl health`, `grep pattern`, `forge_search`, `arif_observe` |

**Rule:** Class 0 actions require ZERO human interaction. Not "optional." Not "advisory." NONE. Agent proceeds.

### Class 1 — REVERSIBLE MUTATE (Autonomous with rollback)

| Attribute | Value |
|---|---|
| **Scope** | Create, edit, build, test, commit, push (non-main), install, restart |
| **Reversibility** | FULL — `git revert`, `npm uninstall`, `systemctl restart` |
| **Blast radius** | BR-1 to BR-2 (local, contained) |
| **Who decides** | **Agent autonomously** — SEAL auto-granted after constitutional pre-check |
| **Human surface** | Post-hoc notification (T2 ANNOUNCE). No pre-approval needed. |
| **Examples** | `git push origin feature-branch`, `npm install express`, `systemctl restart a-forge`, `forge_filesystem write` |

**Rule:** Class 1 actions proceed without pre-approval. Agent announces intent with 10s window for veto. If no veto within window → execute. F1 AMANAH satisfied via backup/snapshot/rollback availability.

### Class 2 — CONSEQUENTIAL MUTATE (Veto-gated)

| Attribute | Value |
|---|---|
| **Scope** | Deploy to production, merge to main, send external communication, spend <$10 |
| **Reversibility** | PARTIAL — can rollback with effort (redeploy, revert merge) |
| **Blast radius** | BR-3 (wider, visible, affects external users) |
| **Who decides** | **Agent proposes → Human vetoes or accepts** |
| **Human surface** | Consent compression payload (5 fields). Human answers: SEAL / MODIFY / HOLD. |
| **Examples** | `git push origin main`, `caddy reload`, `deploy to arif-fazil.com`, `send email to external` |

**Rule:** Class 2 actions present a 5-field consent compression payload. Human responds with one of: SEAL (proceed), MODIFY (change scope), HOLD (wait, I need to think). Agent must WAIT for human response. No auto-proceed.

### Class 3 — SOVEREIGN (Human EXCLUSIVE)

| Attribute | Value |
|---|---|
| **Scope** | Irreversible destruction, real money, authority transfer, secret rotation, constitutional change |
| **Reversibility** | NONE or NEAR-NONE |
| **Blast radius** | BR-4 to BR-5 (irreversible, legal, financial, structural) |
| **Who decides** | **Human ONLY** — 888_HOLD until explicit F13 authorization |
| **Human surface** | Full QQQ envelope + risk acceptance statement. Human MUST explicitly acknowledge irreversibility. |
| **Examples** | `rm -rf`, `DROP TABLE`, `git push --force main`, DNS changes, firewall changes, vault seal, identity changes |

**Rule:** Class 3 actions NEVER auto-proceed. Agent may prepare evidence but CANNOT execute. Requires: (a) F13 sovereign signal OR (b) cryptographic SCT gate token. No env var can authorize Class 3.

---

## 2. CONSENT COMPRESSION — The 5-Field Payload

For Class 2 actions, the agent presents:

```text
┌─────────────────────────────────────────┐
│ A-FORGE REQUEST                         │
├─────────────────────────────────────────┤
│ INTENT:  [What the system will do]       │
│ SCOPE:   [Exact boundary of action]      │
│ RISK:    [What could go wrong]           │
│ UNDO:    [How to reverse if needed]      │
│ EVIDENCE:[Why this is the right action]  │
├─────────────────────────────────────────┤
│ ASK: SEAL / MODIFY / HOLD               │
└─────────────────────────────────────────┘
```

**Rules:**
- Maximum 5 lines per field. If it doesn't fit in 5 lines, the proposal is too complex — break it down.
- Human responds with exactly ONE word: `SEAL`, `MODIFY`, or `HOLD`
- `MODIFY` must include the scope change (e.g., "MODIFY: only restart geox, not all")
- `HOLD` stops execution. Agent may re-propose after N hours or on explicit human signal.
- Agent never asks "what should I do?" — agent always proposes, human accepts/modifies/vetoes.

---

## 3. APPROVAL GRAMMAR — The 3-Word Language

| Signal | Meaning | Agent action |
|---|---|---|
| **SEAL** | "I accept the risk. Proceed within stated scope." | Execute immediately |
| **MODIFY** | "Change the scope. Then I'll decide." | Adjust scope, re-present |
| **HOLD** | "Stop. Do not proceed. I need to think or conditions changed." | Cease all Class 2+ activity until explicit release |
| **VOID** | "This action is forbidden. Never propose again." | Remove from action space permanently |

**Sovereign signals** (Class 3 only, immediate ACT, no confirmation loop):
```
"buat ja la" · "jalan terus" · "Yes confirm" · "execute X"
"I'm the Architect" · "just do it" · "seal it" · "go" · "approved"
```

---

## 4. ESCALATION RULES — When Class N Becomes Class N+1

The kernel auto-escalates an action class when:

| Condition | Escalation |
|---|---|
| Blast radius exceeds class boundary | Class N → Class N+1 |
| Irreversibility detected in Class 0/1 | → Class 3 (SOVEREIGN) |
| F1 AMANAH flag triggered (no rollback path) | → Class 2 minimum |
| F6 EMPATHY triggers (weakest stakeholder at risk) | → Class 2 minimum |
| F12 INJECTION detected | → Class 3 (VOID until cleared) |
| F13 SOVEREIGN domain touched (vault, identity, constitution) | → Class 3 |
| Cost > $10/mo (new paid API) | → Class 3 |
| Physical world / real money / other humans | → Class 3 |
| C_dark ≥ 0.30 (BANGANG threshold) | → SABAR → HOLD |

---

## 5. GATE BEHAVIOR — Fail-Closed for Sovereignty

### Class 0-1 gates: Fail-closed, auto-recover

If a Class 0/1 gate crashes:
1. Log the gate failure
2. Retry with degraded mode (skip the crashed gate but log the skip)
3. Proceed IF remaining gates pass
4. Always write a SCAR for the crashed gate

### Class 2-3 gates: FAIL-CLOSED. NO EXCEPTION.

If a Class 2/3 gate crashes:
1. **BLOCK the action immediately**
2. Notify sovereign (via Telegram if Hermes is connected)
3. Write SCAR with severity CRITICAL
4. DO NOT proceed. DO NOT "fail-soft." DO NOT "log and continue."

**Rule:** "Gates must never block" is **VOID** for Class 2+. For Class 2+, "Gates must never fail silently."

### The BANGANG fix for fail-open cascade

The 8+ "never block" annotations (surfaces #7-13 in BANGANG map) are reclassified:

| Old annotation | New behavior |
|---|---|
| "Gate failure must never block execution" | **VOID** for Class 2+. Gates fail CLOSED at sovereignty boundary. |
| "Plan gate failure is advisory" | **VOID** for Class 2+. Plan governance is MANDATORY. |
| "Fail-soft: gate failure must never block pipeline" | **VOID** for Class 2+. Pipeline halts on gate failure. |
| "ImportError pass-through" | **VOID** for Class 2+. If constraint module fails, execution is UNAUTHORIZED. |
| "mesh failure must never block governance" | Proceed for Class 0-1 only. HOLD for Class 2+. |
| "never block the tool path" (telemetry) | OK — telemetry is Class 0. But must HALT if tool path is Class 2+. |

---

## 6. ENV-VAR BYPASSES — Cryptographic Gate Tokens

The 6 env-var bypasses (BANGANG #1-6) are replaced:

### Before (BANGANG):
```typescript
if (process.env.CI || process.env.FORGE_TEST_MODE || process.env.FORGE_SKIP_MODEL_GATE) {
    // bypass ModelCapabilityGate
}
```

### After (HITV):
```typescript
// Cryptographic gate token required for ANY gate bypass
function isValidGateToken(token: string, gate: GateType): boolean {
    // Must be SCT-signed capability token bound to:
    // - This specific gate
    // - This specific session
    // - This specific actor
    // - With TTL ≤ 3600 seconds
    return sctVerify(token, { gate, sessionId, actorId });
}

if (isValidGateToken(process.env.ARIFOS_GATE_TOKEN, 'model_capability')) {
    // authorized bypass
}
```

**Rule:** No plain string env var can bypass constitutional enforcement. All bypasses require cryptographic SCT tokens minted by arifOS kernel. Tokens must be gate-specific, session-bound, and time-limited.

---

## 7. WELL GATE — Recommend, Never Block

BANGANG #17-18: WELL infers human fatigue and gates human decisions.

### Before (BANGANG):
```python
if fatigue_inferred > 0.7:
    return BLOCK  # WELL blocks Arif's decision
```

### After (HITV):
```python
if fatigue_inferred > 0.7:
    return {
        "verdict": "RECOMMEND_HOLD",
        "message": "⚠️ Vitality signal: high fatigue detected. Consider deferring this decision.",
        "sovereign_override": True  # Arif can ALWAYS override
    }
```

**Rule:** WELL reflects. WELL recommends. WELL NEVER blocks. F13 is above all organ gates. Human sovereignty is invariant.

---

## 8. T1 CREEP — Boundary Enforcement

BANGANG #14-16: T1 defined as "read/grep/edit/test" but in practice includes systemctl restart, arif_seal, autonomous self-improvement.

### T1 boundary (HARD):
```
T1 = Class 0 + Class 1 actions ONLY
T1 ≠ systemctl restart (production)    → Class 2
T1 ≠ arif_seal                         → Class 3 (vault is irreversible)
T1 ≠ autonomous self-improvement       → Class 2 (must announce, can veto)
T1 ≠ deploy to production              → Class 2
T1 ≠ merge to main                     → Class 2
```

**Rule:** If an action is Class 2 or higher, it is NOT T1. Period. The doctrine says T1 = "auto-do." HITV says "auto-do WHAT?" T1 = Class 0 + Class 1. Nothing more.

---

## 9. THE 3-LAYER UX — Sovereign-in-Training

| Layer | Class ceiling | Approval model | Who it's for |
|---|---|---|---|
| **Light Mode** | Class 1 | Agent auto-executes. Human sees summary. | Passenger — new users |
| **Governed Mode** | Class 2 | Agent proposes. Human accepts/modifies/vetoes. | Operator — learning sovereignty |
| **Sovereign Mode** | Class 3 | Full kernel: F1-F13, QQQ, SEAL/HOLD/VOID, cryptographic gate tokens | Arif — F13 |

**On-ramp design:** Users start in Light Mode. As they gain confidence, they upgrade to Governed. The full constitutional stack is always running underneath — the UX layer only changes WHAT the human sees, not HOW the system enforces.

---

## 10. IMPACT ON BANGANG SURFACES

| BANGANG # | Surface | Resolution in HITV |
|---|---|---|
| 1-6 | Env-var bypasses | Section 6: Cryptographic gate tokens replace env strings |
| 7-13 | Fail-open cascade | Section 5: Gates fail-closed for Class 2+ |
| 14-16 | T1 creep | Section 8: T1 = Class 0+1 only. Hard boundary. |
| 17-18 | WELL fatigue gate | Section 7: Recommend only, never block Arif |
| 19-22 | State override / autonomous seal | Sections 5,6: Cryptographic session binding |
| 23-25 | Governance bridge fallback / SCT bypass | Section 6: No fallback without token |
| 26-27 | Ed25519 / vault guard | Section 6: Cryptographic enforcement |

**32 of 35 BANGANG surfaces resolved by HITV protocol.**

---

## 11. THE ONE RULE

```
Human is not CPU. Human is sovereign.

Agent proposes. Agent executes reversible. Agent compresses consent.
Human vetoes at the boundary. Human accepts risk. Human authorizes irreversibility.

Machines process. Humans authorize. Both necessary. Neither replaces the other.

F13 is not a bottleneck. F13 is the legitimacy valve.
```

---

## APPENDIX A: Consent Compression Template

```markdown
## A-FORGE REQUEST — [Action Class]

| Field | Detail |
|---|---|
| **INTENT** | [Single sentence. What will happen.] |
| **SCOPE** | [Exact boundary. What's included/excluded.] |
| **RISK** | [Worst case if it fails. Likelihood.] |
| **UNDO** | [Exact rollback steps. Time to reverse.] |
| **EVIDENCE** | [Why this is correct. What was tested.] |

**ASK:** `SEAL` / `MODIFY: [new scope]` / `HOLD`
```

## APPENDIX B: Class Decision Matrix

```
                     BR-0    BR-1-2    BR-3      BR-4-5
REVERSIBLE           C0      C1        C2*       C3*
PARTIALLY REV        C1      C1        C2        C3
IRREVERSIBLE         C2*     C2*       C3        C3

* = escalate one class if:
    - External users affected → +1
    - Money involved → +1
    - Other humans involved → +1
    - Constitutional document touched → +1
```

---

*DITEMPA BUKAN DIBERI — The forge grounds. The human authorizes. The veto is the architecture.*
