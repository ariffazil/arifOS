# ToM-Anchored MCP Integration Summary

## Overview

Successfully integrated **Theory of Mind (ToM)** structured inputs with **Philosophy Registry** (83 quotes) into the **9+1 Constitutional Architecture**.

**Version**: 1.2.0  
**Date**: 2026-04-06  
**Status**: OPERATIONAL

---

## The 9+1 Architecture

### 9 Governance Tools (Cognitive Layer)

These tools **think, validate, and reason** — but never execute directly.

| Tool | Stage | Function | ToM Required |
|------|-------|----------|--------------|
| `arifos.init` | 000_INIT | Session anchoring | `declared_intent`, `confidence_self_estimate`, `context_assumptions` |
| `arifos.sense` | 111_SENSE | Reality grounding | `claim`, `evidence_type`, `source_confidence`, `bias_assessment` |
| `arifos.mind` | 333_MIND | Structured reasoning | `alternative_hypotheses` (min 2), `second_order_effects` |
| `arifos.route` | 444_ROUTER | Lane selection | `intent_model`, `inferred_user_goals` |
| `arifos.heart` | 666_HEART | Safety modeling | `potential_harm_vectors`, `vulnerability_risk`, `consent_assessment` |
| `arifos.ops` | 444_OPS | Operational cost | `complexity_estimate`, `irreversibility`, `rollback_plan` |
| `arifos.judge` | 888_JUDGE | **Constitutional verdict** | `logical_consistency`, `self_critique`, `uncertainty_quantified` |
| `arifos.memory` | 777_MEMORY | Context recall | `query_vector`, `recall_confidence` |
| `arifos.vault` | 999_VAULT | Immutable seal | `verdict`, `hash_of_input`, `irreversibility_acknowledged` |

### 1 Execution Bridge (Action Layer)

| Tool | Function | Gate | Output |
|------|----------|------|--------|
| `arifos.forge` | Delegated execution | Requires `judge` verdict="SEAL" | Signed manifest + receipt hash |

**Separation of Powers:**
- ✅ 9 Governance Tools validate
- ✅ Judge is the sole SEAL authority
- ✅ Forge is the sole execution bridge
- ✅ No action without SEAL

---

## Philosophy Registry v1.2.0

### G★ Bands

| Band | G★ Range | Categories | Example Quote |
|------|----------|------------|---------------|
| 0 | 0.00-0.20 | void, paradox | "The only principle that does not inhibit progress..." — Feyerabend |
| 1 | 0.20-0.40 | paradox, truth | "The concept of truth cannot be defined within..." — Tarski |
| 2 | 0.40-0.60 | wisdom, justice | "Nearly all men can stand adversity..." — Lincoln |
| 3 | 0.60-0.80 | discipline, power | "Build less, build right." — arifOS |
| 4 | 0.80-1.00 | power | "What gets measured gets managed." — Drucker |

### Hard Overrides

- **INIT stage** → Always "DITEMPA, BUKAN DIBERI."
- **SEAL verdict** → Always "DITEMPA, BUKAN DIBERI."

### Registry Stats

- **Total Quotes**: 83
- **Diversity Score**: 0.85 (target: ≥0.80)
- **Categories**: 8 (void, paradox, truth, wisdom, justice, discipline, power, seal)
- **Civilizations**: 7 represented
- **Selection**: Deterministic (`sha256(session_id + band + g_star) % count`)

---

## Tool Modes

Several tools support multiple modes:

| Tool | Modes | Description |
|------|-------|-------------|
| `arifos.judge` | `judge`, `health`, `validate`, `hold`, `armor`, `notify`, `probe` | Verdict + diagnostics |
| `arifos.vault` | `seal`, `seal_card`, `render`, `status` | Ledger + widgets |

---

## ToM Validation

Without required ToM fields, tools return:

```json
{
  "ok": false,
  "tom_violation": true,
  "error": "Missing required ToM fields: ['declared_intent', 'confidence_self_estimate', 'context_assumptions']"
}
```

This forces the LLM to externalize its mental model.

---

## Execution Pipeline

```
Intent
  ↓
arifos.init (Session anchoring)
  ↓
arifos.sense (Reality grounding)
  ↓
arifos.mind (Structured reasoning)
  ↓
arifos.heart (Safety critique)
  ↓
arifos.ops (Operational feasibility)
  ↓
arifos.judge (Constitutional verdict)
  ↓
  IF verdict == "SEAL":
    → arifos.forge (Execution bridge)
      → A-FORGE Substrate (spawn, write, send)
    → arifos.vault (Immutable receipt)
  
  IF verdict == "VOID":
    → Blocked. No execution.
```

---

## Key Principles

1. **ToM Ignition**: Tools require structured fields that force mental model externalization
2. **G★ Scoring**: Constitutional alignment calculated from ToM input quality
3. **Philosophy Injection**: Post-verdict, deterministic, never affects verdict
4. **Separation of Powers**: Governance (9) and Execution (1) are strictly separated
5. **F1 Amanah**: No irreversible action without SEAL

---

## Files Modified

| File | Purpose |
|------|---------|
| `runtime/philosophy_registry.py` | 83 quotes, G★ bands, diversity 0.85 |
| `runtime/tools.py` | 9 ToM-enhanced tools + forge bridge |
| `runtime/tool_specs.py` | Clean 2-term naming (arifos.init, etc.) |
| `runtime/server.py` | MCP server registration |

---

## Testing

```bash
# Verify all 10 tools registered
cd /root/arifOS
python3 -c "
from arifosmcp.runtime.server import mcp
import asyncio

async def test():
    tools = await mcp._list_tools()
    for t in tools:
        if t.name.startswith('arifos.'):
            print(f'✅ {t.name}')

asyncio.run(test())
"
```

---

## Status

**🌑 OPERATIONAL — DITEMPA, BUKAN DIBERI.**
