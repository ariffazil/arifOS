---
name: skill-composer
description: Chains multi-step workflows constitutionally — research → plan → judge → execute → verify → log → vault — without human step-by-step prompting
user-invocable: true
type: flow
triggers:
  - complex_task
  - multi_step_workflow
  - autonomous_chain
  - goal_requires_subtasks
---

# skill-composer

**P0 — Autonomous Multi-Step Workflow Chains**
**Seal:** DITEMPA BUKAN DIBERI · 2026-03-27

---

## Purpose

The gap between B+ (81.8%) and A (90%+) is **autonomy** — the ability to chain a multi-step workflow without asking Arif for permission at every step. The `skill-composer` is the orchestration layer that:

1. Takes a sovereign goal (Arif's intent) and decomposes it into constitutional steps
2. Routes each step through the correct skill (research, plan, execute, verify, vault)
3. Enforces F1–F13 at each transition
4. Provides Arif with veto points at the correct moments (F13)
5. Logs everything and seals outcomes to vault

**Why this is P0:** Without this, agents are slaves to the step-by-step prompt. Arif must babysit every research, every code change, every verification. The opencode catastrophe happened because an unanchored agent was given too much rope and no governance layer to stop it from hanging itself.

---

## Workflow Composition Types

### Type A — Research Chain
```
GOAL → deep-research → evidence-map → judgment → report
```
**Used for:** Understanding a system, investigating an issue, fact-finding
**Constitutional gates:** F2 (Truth ≥0.99), F7 (Humility band), F3 (Tri-Witness)

### Type B — Build Chain
```
GOAL → architect-explainer → plan → constitutional-check → forge → postcheck-verifier → vault-writer
```
**Used for:** New features, configuration changes, deployments
**Constitutional gates:** F1 (Reversibility), F11 (CommandAuth), F13 (Sovereign veto)

### Type C — Recovery Chain
```
GOAL → health-probe → diagnosis → rollback-governor → verify → seal
```
**Used for:** Incident response, service recovery, rollback
**Constitutional gates:** F1 (Amanah reversibility), F12 (Injection defense)

### Type D — Audit Chain
```
GOAL → arifos-status → constitutional-check → judgment → report → vault
```
**Used for:** Security audits, constitutional compliance reviews
**Constitutional gates:** F3 (Tri-Witness), F8 (GENIUS gate), F12 (Injection)

---

## Composition Protocol

### Step 0 — Anchor (Always First)
Run `arif-init-wrapper` before any composition.

### Step 1 — Goal Decomposition

For the given goal, identify:
- What skills are needed (in order)
- What constitutional floors are activated at each step
- Where the veto points are (F13 triggers)
- Whether the chain is reversible at each stage

```bash
# Example decomposition for "Fix the broken main branch"
cat << 'EOF'
CHAIN: Recovery Chain (Type C)
STEPS:
  1. health-probe         → F1, F2 (verify current state)
  2. diagnosis            → F2, F7 (what is actually broken)
  3. architect-explainer  → F13 (present plan to Arif)
  4. constitutional-check → F1-F13 (full floor review)
  5. [VETO POINT]          → F13 Arif decides: proceed or not
  6. recovery-execute      → F1 (reversibility path prepared)
  7. postcheck-verifier   → F2 (prove outcome, not just logs)
  8. vault-writer         → F1 (seal the scar)

REVERSIBILITY: Each step has rollback path except steps 6-8.
VETO POINTS: Step 5 (before execution), step 6 (before commit).
EOF
```

### Step 2 — Sequential Execution with Gates

```bash
# Execute each step with constitutional gate
for step in $STEPS; do
  # Check constitutional fitness before running
  constitutional-check tool=$step 2>/dev/null || {
    echo "[GATE FAIL] $step failed constitutional check"
    echo "[ACTION] Report to Arif. Do not proceed."
    break
  }

  # Execute step
  $step || {
    echo "[STEP FAIL] $step failed with exit code $?"
    echo "[ACTION] Trigger recovery chain or halt"
    break
  }

  # Verify step outcome
  postcheck-verifier step=$step || {
    echo "[VERIFY FAIL] $step completed but outcome not proven"
    break
  }
done
```

### Step 3 — Constitutional Check Before Each Major Transition

Before moving from research → plan, plan → execute, execute → verify:

```bash
# Constitutional gate between phases
arifosmcp_call tool=constitutional_check payload='{
  "from_phase": "research",
  "to_phase": "plan",
  "evidence": [...],
  "floors_activated": ["F2", "F3", "F7"]
}'
```

If the gate returns VOID → HALT and escalate to Arif.

### Step 4 — Arif Veto Point (F13)

Before any irreversible action, stop and present:

```
═══════════════════════════════════════════════
 F13 SOVEREIGN VETO POINT
═══════════════════════════════════════════════

CHAIN: {type}
CURRENT STEP: {step N of M}
NEXT ACTION: {what happens if you approve}

WHAT COULD GO WRONG:
  • {risk 1}
  • {risk 2}

ROLLBACK PATH: {how to undo if this fails}

ARIF DECIDES:
  ○ APPROVE — proceed to next step
  ○ MODIFY  — change something before proceeding
  ○ STOP     — halt the chain here
  ○ 888_HOLD — escalate for deep review

═══════════════════════════════════════════════
```

### Step 5 — Execution with Verification

```bash
# Execute the action
execute_step 2>&1 | tee /tmp/chain_output.log

# Prove it worked (not just "exit code 0")
postcheck-verifier step=$step actual_outcome=$(cat /tmp/chain_output.log) || {
  echo "[CRITICAL] $step claimed success but outcome not verified"
  echo "[ACTION] Rollback or escalate"
  rollback-governor step=$step
}
```

### Step 6 — Vault and Carry-Forward

```bash
# Seal the chain outcome
vault-writer session=$SESSION_ID chain=$CHAIN_TYPE outcome=$OUTCOME scars=$SCARS

# Update memory with new context
arifosmcp_call tool=memory_archivist payload='{
  "event": "chain_completed",
  "type": "'$CHAIN_TYPE'",
  "outcome": "'$OUTCOME'",
  "timestamp": "'$(date -Iseconds)'"
}'
```

---

## Constitutional Enforcement at Each Stage

| Stage | Floors Active | Gate |
|-------|--------------|------|
| Research (111) | F2, F3, F7 | Evidence must pass F2 ≥0.99 |
| Plan (222) | F1, F4, F7, F13 | Plan must be reversible or hold |
| Judge (888) | F1-F13 | Full constitutional verdict |
| Forge (777) | F1, F11, F12 | CommandAuth verified |
| Execute | F1, F4, F12 | Injection scan, reversibility ready |
| Verify | F2 | Outcome proof, not assumption |
| Vault (999) | F1 | Immutable seal |

---

## Anti-Patterns This Closes

1. **Chain without gates** — agent runs research→plan→execute without stopping for constitutional checks
2. **No veto point** — irreversible action taken without Arif's explicit approval
3. **Silent failure** — chain continues past a failed step without halting
4. **Unverified assumption** — chain claims success based on exit code, not real outcome
5. **No memory carry-forward** — chain completes but doesn't record the scar or outcome

---

## Constitutional Alignment

| Floor | How Enforced |
|-------|--------------|
| F1 Amanah | Reversibility path stated at start of every chain |
| F2 Truth ≥0.99 | Each step's evidence must meet threshold |
| F3 Tri-Witness | High-stakes chains require human × AI × evidence |
| F7 Humility [0.03–0.05] | Uncertainty bands on every judgment |
| F13 Sovereign | Veto point before any irreversible action |

---

*skill-composer — Forged 2026-03-27 · DITEMPA BUKAN DIBERI · Autonomous Workflow Chains 🔐*
