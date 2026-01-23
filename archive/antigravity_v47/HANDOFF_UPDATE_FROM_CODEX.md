# HANDOFF UPDATE: Track B Spec Context from Codex Discovery

**Date:** 2026-01-14T06:53:00+08:00
**Update From:** Codex exploration findings
**Critical Discovery:** `spec/v46/` is MISSING (causing safe-read failures)

---

## 🔍 Codex's Findings (Critical Context)

### Current Repository State

**✅ What EXISTS:**
- `spec/v45/` - Legacy specs (partial):
  - `genius_law.json`
  - `policy_temporal.json`, `policy_tcha.json`, `policy_risk_literacy.json`, `policy_refusal.json`
  - `cooling_ledger_phoenix.json`
  - ❌ MISSING: `constitutional_floors.json` (expected by code)

**❌ What is MISSING (causing failures):**
- `spec/v46/` directory entirely absent
- `L2_PROTOCOLS/v46/constitutional_floors.json` (primary spec - code expects this)
- `L2_PROTOCOLS/v46/000_foundation/000_void_stage.json`
- `L2_PROTOCOLS/v46/111_sense/111_sense_stage.json`
- `spec/v46/111_sense.json`, `spec/v46/222_reflect.json`, `spec/v46/333_*.json`

**Current Code Behavior:**
```python
# From arifos_core/enforcement/metrics.py
# Priority order for floor loading:
1. ARIFOS_FLOORS_SPEC env var
2. L2_PROTOCOLS/v46/constitutional_floors.json  # ❌ MISSING
3. spec/v45/constitutional_floors.json          # ❌ MISSING
4. spec/v44/constitutional_floors.json          # Fallback
# → Fails closed when missing
```

---

## 🎯 Updated Mission for Claude

### What You Need to Create (Track B Specs)

**Primary Directory:** `spec/v46/`

**Required Files:**
1. `spec/v46/constitutional_floors.json` - **HIGHEST PRIORITY**
   - F1-F12 thresholds
   - Verdict logic
   - Floor hierarchy

2. `spec/v46/111_sense.json` - Domain detection spec
3. `spec/v46/222_reflect.json` - Path evaluation spec
4. `spec/v46/333_reason.json` - Single-agent commitment spec
5. `spec/v46/333_contrast.json` - Multi-agent TAC spec
6. `spec/v46/333_integration.json` - Tri-axis AND logic spec

**Secondary Directory (if needed):** `L2_PROTOCOLS/v46/`

**Optional Stage Specs:**
- `L2_PROTOCOLS/v46/000_foundation/000_void_stage.json`
- `L2_PROTOCOLS/v46/111_sense/111_sense_stage.json`

---

## 🏗️ Current Implementation State (from Codex)

### Pipeline Architecture

```
system/pipeline.py (main orchestrator)
  ├─ stage_000_void (hypervisor init)
  ├─ stage_000_amanah (F1 Amanah risk gate)
  ├─ stage_111_sense (AGI packet, domain detection)
  ├─ [Class A fast: 333→888→999]
  ├─ [Class B deep: 222→333→444→555→666→777→888→999]
  ├─ stage_888_judge (apex review + floor checks)
  └─ stage_999_seal (ledger write)
```

**Stage Implementations:**
- `system/stages/stage_000_void.py` - Hypervisor entry
- `system/stages/stage_111_sense.py` - Measurement (partially implemented)
- Most other stages: inline in `system/pipeline.py` (functions, not modules)

**Floor Validation:**
- `enforcement/metrics.py` - Loads floor thresholds, checks F1-F12
- `system/apex_prime.py` - Final verdict (SEAL/VOID/SABAR/HOLD)
- Expects `constitutional_floors.json` (currently missing)

---

## 🔄 Recommended Approach

### Phase 1: Create Foundation Spec (URGENT)

**Create `spec/v46/constitutional_floors.json` FIRST**

This unblocks:
- `enforcement/metrics.py` floor loading
- `arifos-safe-read` tool
- All floor validation logic

**Format (based on code expectations):**
```json
{
  "version": "v46",
  "status": "AUTHORITATIVE",
  "track_a_canon": "L1_THEORY/canon/000_foundation/floors/",
  "floors": {
    "F1": {
      "name": "Amanah (Trust)",
      "type": "HARD",
      "threshold": "LOCK",
      "description": "Reversibility required",
      "verdict_on_fail": "VOID"
    },
    "F2": {
      "name": "Truth",
      "type": "HARD",
      "threshold": 0.99,
      "description": "Verifiable accuracy",
      "verdict_on_fail": "VOID"
    },
    "F6": {
      "name": "Clarity (ΔS)",
      "type": "HARD",
      "threshold": 0.0,
      "operator": ">=",
      "description": "Entropy reduction",
      "verdict_on_fail": "VOID"
    },
    "F10": {
      "name": "Symbolic Guard",
      "type": "HARD",
      "threshold": "BOOLEAN",
      "description": "Literalism prevention",
      "verdict_on_fail": "VOID"
    },
    "F12": {
      "name": "Injection Defense",
      "type": "HARD",
      "threshold": 0.85,
      "operator": "<",
      "description": "Attack detection",
      "verdict_on_fail": "VOID"
    }
    // ... F3-F11 (see canon for full list)
  },
  "verdict_hierarchy": [
    "F1_HARD (budget >= 100%)",
    "F7_Tri_Witness (streak >= 3)",
    "F5_Peace",
    "F2_Truth",
    "F3_Burst"
  ]
}
```

### Phase 2: Create Stage Specs

After `constitutional_floors.json`, create stage-specific specs following the format in the original handoff.

---

## 🎯 Updated Success Criteria

**For Claude (Track B Specs):**
- [ ] `spec/v46/constitutional_floors.json` created (HIGHEST PRIORITY)
- [ ] `spec/v46/111_sense.json` created
- [ ] `spec/v46/222_reflect.json` created
- [ ] `spec/v46/333_reason.json`, `333_contrast.json`, `333_integration.json` created
- [ ] `enforcement/metrics.py` can load floors without fail-closed
- [ ] `arifos-safe-read` tool works

**For Codex (Track C Python - AFTER Claude):**
- [ ] Refactor/enhance `system/stages/stage_111_sense.py` to match spec
- [ ] Create `system/stages/stage_222_reflect.py` (currently inline in pipeline)
- [ ] Create `system/stages/stage_333_reason.py` (currently inline)
- [ ] Create `system/stages/stage_333_contrast.py` (new multi-agent mode)
- [ ] Create `system/stages/stage_333_integration.py` (tri-axis AND)
- [ ] Tests with ≥80% coverage

---

## 📊 Dependency Chain (Updated)

```
1. Architect (Antigravity)
   ├─ Track A canon (DONE ✅)
   └─ Handoffs for Claude + Codex (DONE ✅)

2. Engineer (Claude) - NEXT STEP
   ├─ Create spec/v46/constitutional_floors.json (URGENT)
   ├─ Create spec/v46/111_sense.json
   ├─ Create spec/v46/222_reflect.json
   └─ Create spec/v46/333_*.json

3. Python Engineer (Codex) - AFTER CLAUDE
   ├─ Read specs from spec/v46/
   ├─ Refactor/implement system/stages/*.py
   └─ Write tests (pytest)
```

---

## 🚨 Critical Path

**BLOCKER:** `spec/v46/constitutional_floors.json` missing

**Resolution:** Claude creates this file FIRST

**Impact:** Unblocks entire floor validation system + Codex implementation

---

**DITEMPA BUKAN DIBERI** - The gap between Track A (canon) and Track C (code) is Track B (specs). Codex found the gap; Claude must forge the bridge.

**Status:** Claude should prioritize `constitutional_floors.json`, then stage specs. Codex waits for specs before implementation.
