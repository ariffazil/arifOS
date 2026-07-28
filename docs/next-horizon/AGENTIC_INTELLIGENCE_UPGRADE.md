# AGENTIC INTELLIGENCE UPGRADE PLAN — Measurable Governance
**Date:** 2026-07-28 | **Session:** SEAL-ff91ae20f90a4985
**Authority:** OBSERVE_ONLY | **Status:** Plan only (not executed)

---

## 1. Definitions

### "Higher Agentic Intelligence Level" means:

| Capability | Before | Target | Measurement |
|---|---|---|---|
| Sensing | Relies on agent context + memory | Multi-organ sensing pipeline | % of decisions with ≥2 evidence sources |
| Decomposition | Manual task breakdown | DAG-based plan with verified edges | % of plans passing PlanGovernanceGate |
| Invariant detection | None — trust agent self-report | Runtime floor evaluation (F1-F13) | Number of FLOOR violations caught |
| Falsification | Optional human review | Mandatory Kill Matrix (K001-K007) | % of claims falsified before SEAL |
| Execution gating | Agent decides | 2-gate pipeline (Model + Governance) | Gate pass/fail rate |
| Receipt metabolism | Optional | Mandatory arifFlow receipt per execution | FQ trend over 100 executions |
| Contradiction surfacing | None — hallucination unchecked | C_dark computed per session | C_dark trend (target: <0.30) |
| Attention cost | High — full context dump | Focused, routed, provenance-tagged | % reduction in input tokens per verdict |
| Rollback | Manual git revert | Sealed reversion receipts | Rollback completion time |
| Human authority | Prompt-level only | F13 SOVEREIGN enforced at kernel level | % of unauthorized executions blocked |

### What it does NOT mean:

- ❌ More autonomous loops — unbounded recursion is blocked by F4 monitor
- ❌ More tools — tool surface is 8 canonical tools (stable)
- ❌ More activity — activity is noise without governance
- ❌ Bigger claims — F7 caps certainty at Ω₀ ∈ [0.03, 0.05]
- ❌ Self-certification — always false without external verification
- ❌ Artificial confidence — epistemic labels required on all outputs

---

## 2. Metrics Dashboard

### Primary Metrics

| Metric | Current | Target | Source |
|---|---|---|---|
| **FQ** (verify/execute ratio) | 2.0 → 0.0 (post-restart) | ≥ 2.0 | arifFlow `/health` |
| **Drift count** | 1 → 0 ✅ | 0 | arifOS `deployment_invariant.drift` |
| **Open HOLD count** | 1 (identity) | 0 | Session verdict count |
| **Receipt latency** | Unknown | < 1s from execution → arifFlow | arifFlow timing |
| **Failed gate count** | Unknown | Track per session | PlanGovernanceGate stats |
| **Self-certification blocked** | Unknown | Track per session | Kernel floor evaluator |
| **Human attention cost** | Unlimited per session | < 5KB per routine verdict | Input token count |
| **Rollback readiness** | Partial (git revert) | Full sealed reversion path | `arif_seal(mode=reversion)` test |
| **Test coverage** | Varies by organ | > 80% per organ | Coverage reports |
| **Source/built/deployed consistency** | ✅ now resolved | 100% | Health endpoint sweep |

### C_dark Components

| Component | Weight | Current | Target | Source |
|---|---|---|---|---|
| H (Hantu — consciousness claims) | 0.25 | Unknown | < 0.10 | Kernel floor evaluator |
| ToM (Theory of Mind) | 0.25 | Unknown | < 0.10 | Kernel floor evaluator |
| Scar (contradictions) | 0.20 | Unknown | < 0.05 | Contradiction scan |
| Gödel (self-reference) | 0.15 | Unknown | < 0.05 | Kernel floor evaluator |
| Humility (Ω₀ band) | 0.15 | Unknown | < 0.03 | Kernel floor evaluator |
| **C_dark total** | 1.00 | **0.4456** | **< 0.30** | Health endpoint |

---

## 3. Upgrade Path (Staged)

### Stage 1 — Foundation (P0)
- ✅ Resolve kernel drift (DONE)
- ❏ Verify identity (awaits your Ed25519 signature)
- ❏ Measure and surface C_dark components individually

### Stage 2 — Sensing (P1)
- ❏ Federation contract unified — one SOT for all organ boundaries
- ❏ AGENTS.md consolidated — organ role clarity
- ❏ Floor consistency verified

### Stage 3 — Invariant Detection (P2)
- ❏ Ω₀ range gate on all SEAL attempts
- ❏ Overclaim phrase detection (`always`, `never`, `certain`, `proven`)
- ❏ Self-certification blocker in floor evaluator

### Stage 4 — Metabolism (P3)
- ❏ arifFlow receipt persistence (survive restart)
- ❏ FQ telemetry surfaced to all organs
- ❏ Simulation-collapse threshold: FQ < 0.5 triggers HOLD

### Stage 5 — Execution Gating (P4)
- ❏ Dry-run default documented in all A-FORGE commands
- ❏ Plan-id + judge-state-hash required for execution
- ❏ Receipt mandatory after every A-FORGE mutation

### Stage 6 — Coordination Hygiene (P5)
- ❏ AAA emits proposal envelopes only (no self-judge)
- ❏ Critique envelopes carry C_dark estimate
- ❏ Verdict envelopes reference arif_judge session

### Stage 7 — Verification (P6)
- ❏ Federation e2e test: init → observe → think → judge → forge → seal → verify
- ❏ Receipt e2e test: A-FORGE → arifFlow → persist → recover
- ❏ Rollback e2e test: seal reversion → verify state
- ❏ Identity e2e test: challenge → sign → verify → F13 authority
- ❏ Overclaim blocker e2e test: certainty phrase → HOLD

---

## 4. Expected Outcomes After Full Upgrade

| Metric | Before | After (target) |
|---|---|---|
| FQ | 2.0 (unstable) | ≥ 5.0 (stable) |
| C_dark | 0.4456 | < 0.30 |
| Drift events / month | 1+ | 0 |
| False SEAL attempts blocked | Not tracked | Tracked, ≥ 0 |
| Rollback time | ~30min (manual) | < 5min (automated reversion) |
| Identity verification time | Not applicable (always OBSERVE_ONLY) | < 1s (Ed25519 challenge-response) |

---

*Intelligence is constraint, not freedom.*
*Better gates produce better agents.*
*No metric is truth until sealed.*
