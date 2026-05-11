# ARCH-001: arif_mind_reason → arif_forge_execute Dispatch Boundary

> **Status:** DOCUMENTED — boundary is architecturally sound, gap is in documentation
> **Fixed:** 2026-05-05
> **Auditor:** AGI OPENCLAW

## The Concern

When `arif_mind_reason(mode='plan')` generates a plan, and that plan includes steps that require `arif_forge_execute`, the handoff between "thinking" (333_MIND) and "doing" (010_FORGE) was poorly defined. Could cause:

1. Wrong tool routing after planning
2. Missing audit trail between plan creation and execution
3. AI self-approval of its own plans (F13 SOVEREIGN violation)

## Plan Lifecycle (The Contract)

```
arif_mind_reason(plan)
    ↓ [plan_id created, status=pending_approval]
    ↓ [vault ledger entry written]
    ↓
    888_JUDGE deliberates
    OR arif_mind_reason(plan_approve, witness_type=human)
    ↓ [status=pending_approval → approved, human witness recorded]
    ↓
arif_forge_execute(mode=engineer, plan_id=xxx)
    ↓ [H2 hard-gate: plan must exist AND status=='approved']
    ↓ [F13 hard-gate: plan_approve requires witness_type='human' — AI cannot self-approve]
    ↓
    Manifest executed or SEALed
```

## Boundary Rules (Fixed)

### Rule 1: AI Cannot Self-Approve Plans
```
F13 SOVEREIGN: plan_approve requires witness_type='human'
```
The LLM running inside `arif_mind_reason` can **propose** plans but cannot **approve** them. Approval requires either:
- `arif_judge_deliberate(888_JUDGE)` SEAL verdict
- `arif_mind_reason(mode='plan_approve', witness_type='human')` — human actor

### Rule 2: Forge Gated on Approved Plans Only
```python
if mode in _PLAN_REQUIRED_MODES:  # engineer, write, generate
    plan = _PLAN_REGISTRY.get(plan_id)
    assert plan["status"] == "approved", "Plan not approved"
```

### Rule 3: plan_id is the Chain Link
- `arif_mind_reason(plan)` writes vault ledger entry with `plan_id`
- `arif_forge_execute` requires `plan_id` to reference the approving verdict
- Vault chain: plan_created → plan_approved → forge_executed

### Rule 4: tool_hint is Advisory Only
`plan.task_steps[].tool_hint` tells the executor which tool *might* be needed, but:
- Does NOT automatically dispatch
- Does NOT bypass constitutional gates
- Does NOT override human veto (F13)

## What Was Unclear (The Gap)

The original HERMES_RUNTIME_AUDIT said "boundary unclear." The actual code is correct — the issue was undocumented assumptions:

| Assumption | Reality |
|------------|---------|
| AI can approve its own plan | ❌ F13 forbids this |
| plan_id auto-dispatches to forge | ❌ Human must action forge with plan_id |
| tool_hint bypasses governance | ❌ Every tool goes through its own floor checks |

## Fix Applied

1. **This document** — explicit boundary contract
2. **`federation_bridge.py`** — new WEALTH/WELL bridge with proper SSE session handling
3. **`geox_bridge.py`** — live MCP wiring (SIMULATED → LIVE)

## Verification

```bash
# Verify boundary enforcement
python3 -c "
import asyncio
from arifosmcp.runtime.tools import _PLAN_REGISTRY

# After plan_approve with witness_type=human:
plan = _PLAN_REGISTRY.get('PLAN-xxxxxxxx')
assert plan['status'] == 'approved'
assert plan.get('witness_type') == 'human'

# After arif_forge_execute without plan_id or with unapproved plan:
# → returns HOLD with failed_floors=['F01','F13']
"
```
