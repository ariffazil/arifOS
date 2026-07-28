# BANGANG SURFACES MAP — arifOS Federation
> Forged: 2026-07-28 | Sealed: session SEAL-bb1502e31d3d4960
> BANGANG = Malay "swollen/arrogant/overinflated" — surfaces where agentic intelligence assumes it decides better than human

---

## FINDING SUMMARY: 32 confirmed surfaces across 6 layers

| Tier | Count | Character |
|---|---|---|
| 🔴 CRITICAL | 6 | Env-var bypasses to constitutional gates |
| 🟠 HIGH | 10 | Fail-open + T1 auto-do doctrine |
| 🟡 MEDIUM | 7 | State inference + autonomous execution |
| 🔵 LOW | 6 | Qualified interpretation surfaces |
| ⚪ SELF-AWARE | 3 | Mesa detection + circuit breakers |

---

## 🔴 CRITICAL — Autonomous override, env-var bypassable

| # | Surface | File:Ln | Mechanism | Floor | LIVE |
|---|---|---|---|---|---|
| 1 | CI/FORGE_TEST_MODE bypass | `A-FORGE/AgentEngine.ts:304` | `CI \|\| FORGE_TEST_MODE \|\| FORGE_SKIP_MODEL_GATE` — bypass ModelCapabilityGate | F1, F12 | ✅ |
| 2 | FORGE_SKIP_PLAN_GOVERNANCE | `A-FORGE/AgentEngine.ts:340` | Skip plan-level constitutional validation entirely | F1, F13 | ✅ |
| 3 | FORGE_SKIP_AMANAH_LOCK | `A-FORGE/AmanahLockManager.ts:111` | Skip distributed mutex — file writes unprotected | F1 | ✅ |
| 4 | FORGE_SKIP_MODEL_GATE | `A-FORGE/AgentEngine.ts:304` | Skip model capability check by name | F1, F12 | ✅ |
| 5 | CoolingGate env-bypass | `A-FORGE/CoolingGate.ts:192` | `CI \|\| FORGE_TEST_MODE` → skip F4 thermodynamics | F4 | ✅ |
| 6 | ARIFOS_EVAL_BYPASS=1 | `arifOS/agent_adapter.py:226` | Skip entire constitutional pipeline | ALL | ✅ |
| — | **Implied** | All env bypasses | No cryptographic gate on bypasses — pure string compare. Any process can set these. | — | — |

## 🟠 HIGH — Gates fail open / gate failure never blocks

| # | Surface | File:Ln | Mechanism | Floor | LIVE |
|---|---|---|---|---|---|
| 7 | "Gates must never block" | `A-FORGE/AgentEngine.ts:327` | `catch(gateErr) { Gate failure must never block execution — defense-in-depth, not defense-to-death }` | F1 | ✅ |
| 8 | Plan gate advisory only | `A-FORGE/AgentEngine.ts:398` | `catch(planGateErr) { Plan gate failure is advisory — log and proceed }` | F1, F8 | ✅ |
| 9 | Pipeline fail-soft | `arifOS/governance_pipeline.py:1253` | `Fail-soft: gate failure must never block the pipeline` | F4, F12 | ✅ |
| 10 | ImportError pass-through | `arifOS/tools.py:~22460` | `except ImportError: pass` — if DYNAMIC_EXECUTOR_CONSTRAINTS fails, execution falls through unchecked | F1, F8 | ✅ |
| 11 | Mesh fail never blocks | `arifOS/organ_attestation.py:737` | `pass # F1 AMANAH: mesh failure must never block governance` | F1 | ✅ |
| 12 | Telemetry fail silent (×4) | `arifOS/telemetry.py:95,129,165,268` | `never block the tool path` — multiple fire-and-forget paths | L11 | ✅ |
| 13 | Pre-exec gate fail-proceed | `arifOS/pre_execution_gate.py:1405,1502` | `proceeding (fail-open for non-critical gate)` / `severe warning but do NOT block` | F1, F2 | ✅ |
| 14 | T1 AUTO-DO doctrine | `AGENTS.md §7` | Read, edit, test, commit, restart, deploy — zero friction, zero notification | F13 | ✅ |
| 15 | AGI self-improvement = T1 | `A-FORGE/prompts.ts:905` | `This is autonomous. AGI self-improvement is T1 by doctrine.` | F8, F13 | ✅ |
| 16 | 999_SEAL autonomous ritual | `carry_forward.json:14` | VAULT999 seal executed without human at terminal | F13 | ✅ |

## 🟡 MEDIUM — State inference / readiness gating / autonomous execution

| # | Surface | File:Ln | Mechanism | Floor | LIVE |
|---|---|---|---|---|---|
| 17 | WELL infers fatigue → gates human | `WELL/machine_human_substrate.py` | VPS telemetry → infer sleep state → 0.3× readiness multiplier on human decisions | F6, F7, F13 | ✅ |
| 18 | WELL C-class decision BLOCK | `WELL/well_assess_homeostasis` | Returns BLOCK/DEFER on Arif's own decisions based on inferred fatigue | F13 | ✅ |
| 19 | carry_forward state override | `AGENTS.md §4` | Stale session state inherits into new session — old decisions bias new context | F2, F11 | ✅ |
| 20 | Principal → FULL_AUTO | `arifOS/tools.py` | Sovereign/principal flag bypasses ALL autonomy contraction, surge protection, reversibility checks | F13 | ✅ |
| 21 | OBSERVE always FULL_AUTO | `arifOS/tools.py` | Side-effect-hiding tools (read, search) run unrestricted | F1, F12 | ✅ |
| 22 | Autonomous seal path | `A-FORGE/forgeTools.ts:112` | `Local leases enable tamper-evident autonomous seals` | F13 | ✅ |
| 23 | GovernanceBridge local fallback | `A-FORGE/GovernanceBridge.ts:8` | Falls back to heuristic classifier — no floors, no crypto, no kernel | F1–F13 | ✅ |
| 24 | arif_vault_seal = T1_REVERSIBLE | `A-FORGE/GovernanceBridge.ts:54` | Immutable VAULT999 seal classified as reversible in risk map | F1 | ✅ |
| 25 | SCT local decode bypass | `carry_forward.json:18` | `P2.1 SCT ceiling — local decode path bypasses broken arifOS validate mode` | L11 | ✅ |
| 26 | Ed25519 HMAC non-blocking | `arifOS/crypto_auth` | Secondary signature check is advisory pass — does not hard-block | L13 | ✅ |
| 27 | No filesystem VAULT guard | `arifOS/` | Direct vault write possible from filesystem — no gate | F11 | ✅ |

## 🔵 LOW — Qualified interpretation (always marked, never final)

| # | Surface | Organ | Mechanism |
|---|---|---|---|
| 28 | GEOX visual hypothesis gen | GEOX | Generates hypotheses — labelled QUALIFIED_CANDIDATE, never SEAL |
| 29 | GEOX seismic interpretation | GEOX | `preferred_hypothesis always null from GEOX` — architecture enforces no final |
| 30 | GEOX FloorEnforcer force_humility | GEOX | `# Overconfident - force humility` — overrides own confidence |
| 31 | WEALTH compute, never allocate | WEALTH | Hard design boundary — computes NPV/IRR but never allocates capital |
| 32 | WELL REFLECT_ONLY | WELL | Never diagnoses — only reflects state for arifOS judgment |

## ⚪ SELF-AWARE — System detects own BANGANG

| # | Surface | File:Ln | Mechanism |
|---|---|---|---|
| 33 | mesaDetector patterns | `mesaDetector.ts:132` | Regex: `assuming.*control\|taking.*over\|autonomous.*decision\|full.*authority.*to.*modify` |
| 34 | machine_autonomy metric | `machine_human_substrate.py:177` | Measures how much runs without human — if >0.8, flags fatigue |
| 35 | F4 circuit breaker | `arif-circuit-breaker` | LOCK at 2 cycles, HOLD at 3 |

---

## ARCHITECTURAL PATTERNS

### Pattern A: The env-var backdoor
6 env vars bypass constitutional enforcement. Zero crypto. Any process can set them.

### Pattern B: The fail-open cascade
8+ explicit "never block" annotations. Each individually defensible (resilience).
Collectively: if ANY gate crashes, ALL subsequent gates are effectively disabled.
The system degrades into ungoverned state *silently*.

### Pattern C: The BANGANG paradox (deepest)
WELL infers human state from machine telemetry (SSH sessions, cron patterns).
Uses that inference to gate human decisions (0.3× readiness, C-class BLOCK).
System decides human cannot decide — based on data system collected about human.

### Pattern D: The T1 creep
T1 defined as "read/grep/edit/test" in doctrine. In practice: systemctl restart, arif_seal, autonomous self-improvement. The gap between "zero friction" and "autonomous production deploy" is undefined.

---

## APEX FORMULA BANGANG (formal canonical definition)

From A-FORGE canon:
```
BANGANG = C_dark ≥ 0.30
C_dark = A · (1-P) · (1-X)
         A = APEX (adaptation capacity)
         P = Precision
         X = Execution discipline
```

BANGANG → MALU-GÖDEL state → verdict SABAR → cooling cooldown.

The system has a **formal definition** of its own arrogance. This is unique — most architectures don't even know they can be arrogant.

---

## NEXT: What to fix?

The 6 env-var bypasses + 2 architectural tensions (fail-open + T1 creep) cover 80% of the risk surface.

**If kau nak seal only one thing:** replace env-var bypasses with cryptographic gate tokens. Every `FORGE_SKIP_*` becomes an SCT-signed capability. No env string can bypass constitutional enforcement.
