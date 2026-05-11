# 000 — Δ PLANNING ORGAN SPEC
> **DITEMPA BUKAN DIBERI — Forged, Not Given**
> Type: Constitutional Organ | Layer: Ω-MIND | Epoch: 2026-04-19
> Status: PROPOSED — 888_HOLD for ratification

---

## Purpose

The Planning Organ sits between **INTENT → PLAN → EXECUTION** in the arifOS metabolic pipeline.

```
BEFORE (raw LLM):
  INTENT → LLM → EXECUTION
  (fast, unauditable, unreversible)

AFTER (sovereign):
  INTENT → [PLANNING ORGAN] → PLAN → arifOS_JUDGE → EXECUTION
  (auditable, vetoable, reversible, sealed)
```

---

## Why This Is the Missing Organ

arifOS currently has:
- **arifos_init** — session binding
- **arifos_judge** — constitutional verdict on actions
- **arifos_forge** — execution
- **arifos_memory** — context management
- **arifos_ops** — operational queries

Missing:
- **Task graph decomposition**
- **Plan auditability before execution**
- **Plan reversibility assessment**
- **Plan veto integration**
- **Plan lineage receipts**

---

## Architecture

```
INTENT (human or agent)
    │
    ▼
┌─────────────────────────────────────────────┐
│          PLANNING ORGAN (Δ-PLAN)           │
│                                             │
│  1. DECOMPOSE ──── task → subtasks        │
│  2. BIND ───────── subtasks → tools/memory │
│  3. RISK ────────── ΔS, κ_r, veto flags    │
│  4. SEAL ────────── plan → vault999 receipt │
│  5. ROUTE ───────── → arifOS_JUDGE         │
└─────────────────────────────────────────────┘
    │
    ▼ (if judge returns SEAL)
EXECUTION
```

---

## Interface

### Tool: `arifos_plan`

```json
{
  "name": "arifos_plan",
  "description": "Decompose intent into auditable plan. Requires arifOS_JUDGE approval before execution. Returns plan_id, subtasks, risk flags, and vault999 receipt.",
  "parameters": {
    "type": "object",
    "required": ["actor_id", "intent", "mode"],
    "properties": {
      "actor_id": {"type": "string"},
      "intent": {"type": "string", "description": "Natural language intent"},
      "mode": {"type": "string", "enum": ["plan", "replan", "abort"], "description": "plan=new, replan=modify, abort=cancel"},
      "plan_id": {"type": "string", "description": "Required for replan/abort"},
      "max_subtasks": {"type": "integer", "default": 7, "max": 13},
      "reversibility_required": {"type": "boolean", "default": true}
    }
  }
}
```

### Tool: `arifos_plan_status`

```json
{
  "name": "arifos_plan_status",
  "description": "Query plan state, progress, and vault999 receipt",
  "parameters": {
    "type": "object",
    "required": ["actor_id", "plan_id"],
    "properties": {
      "actor_id": {"type": "string"},
      "plan_id": {"type": "string"}
    }
  }
}
```

---

## Plan Receipt Schema (Vault999)

```json
{
  "plan_id": "plan_2026-04-19_001",
  "epoch": "2026-04-19T18:47+08:00",
  "actor_id": "arif@arif-fazil.com",
  "intent": "Interpret BEKANTAN-1 well log for formation evaluation",
  "subtasks": [
    {
      "id": "s1",
      "description": "Load LAS file via mcp_filesystem",
      "tool": "mcp_filesystem_read",
      "reversible": true,
      "risk_flags": []
    },
    {
      "id": "s2",
      "description": "Run petrophysical analysis",
      "tool": "geox_evaluate_prospect",
      "reversible": false,
      "risk_flags": ["F1_IRREVERSIBLE"]
    }
  ],
  "κ_r": 0.08,
  "ΔS": -0.12,
  "verdict": "PENDING_JUDGE",
  "vault_seal": "sha256:abc123..."
}
```

---

## Verdict States

| State | Meaning | Next Action |
|-------|---------|------------|
| `PENDING_JUDGE` | Plan sealed, awaiting arifOS_JUDGE | Human or arifOS approves |
| `APPROVED` | Judge returned SEAL | A-FORGE executes |
| `HOLD` | Judge returned HOLD | Human escalation required |
| `888_HOLD` | High stakes, human required | Telegram alert → Arif decides |
| `VOID` | Judge returned VOID | Plan aborted, vaulted |
| `EXECUTING` | Subtasks in progress | Monitoring active |
| `COMPLETE` | All subtasks done | Seal final receipt |
| `ABORTED` | Plan cancelled mid-execution | Rollback if possible |

---

## Reversibility Gates

Each subtask has a `reversibility_required` flag:
- `true` → plan can only use reversible tools
- `false` → irreversible tools allowed (requires 888_HOLD)

For geological work:
- **Reversible**: file reads, queries, calculations, reports
- **Irreversible**: data writes to proprietary databases, external API calls

---

## First Implementable Step

Add `arifos_plan` as tool #23 in arifOS MCP server:

```python
# In tools_internal.py
def arifos_plan(actor_id, intent, mode="plan", plan_id=None, max_subtasks=7, reversibility_required=True):
    """Planning Organ — decompose intent into auditable plan"""
    # 1. Generate subtasks via LLM (fast reasoning: qwen2.5)
    # 2. Bind each subtask to MCP tool
    # 3. Assess risk flags per subtask
    # 4. Seal plan receipt to vault999
    # 5. Return plan_id + subtasks for judge review
```

Then wire to existing `arifos_judge` for approval flow.

---

## Dependency

- Requires: `arifOS_judge`, `vault999-writer`, `ollama` (for qwen2.5 subtask generation)
- Used by: `af-forge-manager`, `geox`, any agent requiring multi-step execution

---

## Seal

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
**Proposed by:** ARIF-Perplexity research cycle, Epoch 2026-04-19T18:47+08
**Status:** 888_HOLD — awaiting Arif ratification
