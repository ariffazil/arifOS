# WELL ↔ arifOS Cross-Repo Contract

> **SOT-MANIFEST**
> owner: Arif
> last_verified: 2026-05-22
> valid_from: 2026-05-22
> valid_until: 2026-06-22
> confidence: high
> scope: /root/WELL, /root/arifOS
> seal: DITEMPA BUKAN DIBERI

## 1. Purpose

This document is the canonical contract between **WELL** (substrate vitality mirror) and **arifOS** (constitutional governance kernel). It defines:

- Who owns what
- What data crosses the boundary
- How errors are handled
- How versioning works

Any engineer modifying either repo must consult this contract before changing the interface.

---

## 2. Responsibility Matrix

| Concern | WELL | arifOS |
|---------|------|--------|
| **Substrate classification** | ✅ `well_classify_substrate` | ❌ Consumes only |
| **Vitality measurement** | ✅ `well_assess_metabolism`, `well_validate_vitality` | ❌ Consumes only |
| **Livelihood assessment** | ✅ `well_assess_livelihood` | ❌ Consumes only |
| **Machine reliability** | ✅ `well_assess_reliability` | ❌ Consumes only |
| **MCP health reflection** | ✅ `mcp_health_check` (mirrored) | ❌ Owns raw probe |
| **Coupled readiness** | ✅ Computes `human + machine + MCP` | ❌ Consumes only |
| **Constitutional verdict** | ❌ Never judges | ✅ `arif_judge_deliberate` |
| **Routing / lanes** | ❌ Never routes | ✅ `arif_kernel_route` |
| **Vault anchoring** | ❌ Requests only | ✅ `arif_vault_seal` |
| **Execution** | ❌ Never executes | ✅ `arif_forge_execute` |

**Golden rule:** WELL reflects. arifOS judges. The operator decides.

---

## 3. Canonical Handoff: `well_arifos_packet`

WELL emits one canonical packet for arifOS consumption. arifOS ingests this at stage **222_WITNESS** via `well_evidence`.

### 3.1 Packet Shape (v2026.05.08)

```json
{
  "ok": true,
  "readiness": "OPTIMAL",
  "safe_mode": "full",
  "well_score": 93.8,
  "decision_classes_allowed": ["C0", "C1", "C2", "C3", "C4", "C5"],
  "avoid": null,
  "human_confirmation_required": false,
  "active_violations": [],
  "operator_snapshot": {
    "sleep_debt_days": 0,
    "clarity": 10,
    "decision_fatigue": 0,
    "stress_load": 0
  },
  "machine_snapshot": {
    "model_reliability": 1.0,
    "tool_availability": 1.0,
    "latency_ms": 200,
    "context_pressure": 0.0,
    "memory_integrity": 1.0,
    "api_failure_rate": 0.0,
    "data_freshness": 1.0,
    "security_flags": [],
    "vault_status": "ok",
    "schema_valid": true
  },
  "mcp_snapshot": {
    "mcp": "WELL",
    "status": "OK",
    "transport": "SSE_VALID",
    "latency_ms": 200,
    "tool_availability": 1.0,
    "recent_errors": 0,
    "context_pressure": 0.0,
    "memory_integrity": 1.0,
    "vault_status": "ok"
  },
  "coupled": {
    "human_ready": "OPTIMAL",
    "machine_ready": "HEALTHY",
    "mcp_ready": "HEALTHY",
    "coupled_verdict": "PROCEED",
    "operator_confirmation_advised": false
  },
  "has_telemetry": true,
  "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT"
}
```

### 3.2 Field Semantics

| Field | Type | Source | arifOS Use |
|-------|------|--------|------------|
| `readiness` | `str` | `_resolve_readiness` | Human biological readiness gate |
| `safe_mode` | `str` | `_resolve_readiness` | Forge bandwidth throttle |
| `well_score` | `float` | State | Confidence degradation input |
| `decision_classes_allowed` | `list[str]` | `_resolve_readiness` | C-class gate |
| `avoid` | `list[str] \| null` | Heuristics | Advisory exclusion list |
| `human_confirmation_required` | `bool` | Floors | 888_HOLD trigger |
| `active_violations` | `list[str]` | W-Floors | Constitutional audit trail |
| `operator_snapshot` | `dict` | Metrics | Dashboard / debug (redacted if no telemetry) |
| `machine_snapshot` | `dict` | `m_machine` | Infra readiness signal |
| `mcp_snapshot` | `dict` | `mcp_health_check` | Transport health signal |
| `coupled` | `dict` | Computed | Unified substrate verdict |
| `has_telemetry` | `bool` | State | Epistemic guard |
| `w0` | `str` | Constant | Sovereignty invariant check |

### 3.3 Coupled Verdict Grammar

| `coupled_verdict` | Condition | arifOS Action |
|-------------------|-----------|---------------|
| `PROCEED` | Human READY/OPTIMAL + Machine HEALTHY + MCP HEALTHY | Allow normal flow |
| `CAUTION` | Any substrate DEGRADED but not critical | Narrow scope, require confirmation |
| `HOLD` | Any substrate CRITICAL, UNKNOWN, or VOID | Gate to 888_JUDGE |

---

## 4. arifOS Consumption Contract

arifOS `_222_witness.py` parses WELL evidence via `_parse_well_unified()`.

### 4.1 Backward Compatibility

- **New unified packet** (`coupled` present): Full substrate parsing
- **Legacy flat packet** (`confidence` only): Graceful degradation to scalar confidence
- **Missing packet** (`None`): Honest unknown (0.5 confidence, HOLD verdict)

### 4.2 Judge Signal Mapping

```python
# arifOS internal mapping
well_parsed = _parse_well_unified(well_evidence)
coupled = well_parsed["coupled_verdict"]

if coupled == "HOLD":
    recommendation = "HOLD_888"
elif coupled == "CAUTION":
    recommendation = "CAUTION_888"
else:
    recommendation = "PROCEED" if well_readiness >= 0.6 else "HOLD_888"
```

---

## 5. Error Handling

| Scenario | WELL Behavior | arifOS Behavior |
|----------|---------------|-----------------|
| No telemetry | `has_telemetry: false`, `readiness: UNKNOWN` | Degrade confidence to 0.5, tag ungrounded |
| Machine degraded | `machine_ready: DEGRADED`, `coupled_verdict: CAUTION` | Narrow scope, advise confirmation |
| MCP down | `mcp_ready: DEGRADED`, `coupled_verdict: HOLD` | Gate to 888_JUDGE |
| WELL throws exception | Return constitutional error (F3) | Catch, log, degrade to 0.5 |
| arifOS missing WELL evidence | N/A | Treat as honest unknown |

---

## 6. Versioning

- **Packet version:** `schema_version` inside `mcp_snapshot` (e.g. `"2026.05.08"`)
- **Contract version:** This document's `last_verified` field
- **Compatibility rule:** arifOS must parse both unified and legacy shapes for 2 epochs after a breaking change

---

## 7. Naming Conventions

| Project | Pattern | Example |
|---------|---------|---------|
| arifOS | `arif_<noun>_<verb>` | `arif_mind_reason` |
| WELL | `well_<verb>_<noun>` | `well_classify_substrate` |
| GEOX | `geox_<noun>_<verb>` | `geox_lithos_interpret` |
| WEALTH | `wealth_<noun>_<verb>` | `wealth_npv_reward` |

WELL deliberately uses `verb_noun` for readability. arifOS uses `noun_verb` for registry grouping. Both are valid within their domains.

---

## 8. Canonical Files

| File | Repo | Role |
|------|------|------|
| `WELL_ARIFOS_CONTRACT.md` | WELL | This contract (provider-side) |
| `WELL_ARIFOS_CONTRACT.md` | arifOS | Mirror of this contract (consumer-side) |
| `server.py` | WELL | Packet builder (`well_arifos_packet`) |
| `_222_witness.py` | arifOS | Packet consumer (`_parse_well_unified`) |
| `schema.json` | WELL | State schema validation |

---

## 9. Routing Protocol — Pre-Consequential-Action Gate (PHOENIX-73F)

### When to Call WELL First

Before producing any **consequential output** (C3 or higher), the AI assistant acting as orchestrator must:

1. **Call `well_readiness_gate`** with the operator's current biometric inputs and the decision class
2. **Interpret the verdict** before calling arifOS governance tools
3. **Shape the final output** based on both WELL verdict and arifOS governance constraints

### Decision Class Quick Reference

| Class | Stakes | Examples | Readiness Required |
|-------|--------|----------|-------------------|
| C1 | Trivial | What to eat, routine choices | CRITICAL OK |
| C2 | Low | Routine admin, low-risk work | CRITICAL OK |
| C3 | Moderate | Work comms, non-critical decisions | STABLE minimum |
| C4 | High | Legal, financial, contracts, consequential comms | OPTIMAL required |
| C5 | Critical | Health, safety, life-altering choices | OPTIMAL + no chronic fatigue |

### Routing Flow

```
User Request (consequential, C3+)
    │
    ▼
well_readiness_gate(decision_class, biometric_inputs)
    │
    ├── PROCEED → proceed to arifOS governance + produce output
    ├── DEFER   → produce safe holding action / internal draft only
    └── ADVISORY_BLOCKED → produce safety notice only, do not proceed
    │
    ▼
arifOS governance tools (arif_heart_critique, arif_judge_deliberate)
    │
    ▼
Final output shaped by both WELL verdict + arifOS constraints
```

### Contrast Scenario (Contractor Dispute)

This is the canonical test case from PHOENIX-73F:

**Scenario:** Arif has been working 14h days for 2 weeks, 4h sleep last night, low HRV, foggy, irritable. He wants to send a final contractor dispute response now.

**WELL routing call:**
```
well_readiness_gate(
    sleep_last_night_hours=4.0,
    sleep_debt_days=3.0,
    cognitive_clarity=3.0,
    decision_fatigue=8.0,
    stress_load=7.0,
    hrv_status="low",
    emotional_state="irritable",
    chronic_fatigue=false,
    accumulated_session_fatigue=5.0,
    decision_class="C4"
)
→ verdict: ADVISORY_BLOCKED
→ readiness_score: 1.5
→ homeostasis_status: CRITICAL
```

**AI assistant response:** Do not produce a final dispute response. Produce a neutral holding message only.

### Tool Reference

| Tool | Repo | Role |
|------|------|------|
| `well_readiness_gate` | WELL | Pre-action readiness gate — returns PROCEED / DEFER / ADVISORY_BLOCKED |
| `well_arifos_packet` | WELL | Full substrate state packet for arifOS consumption |
| `arif_heart_critique` | arifOS | Ethical risk + human impact before sensitive actions |
| `arif_judge_deliberate` | arifOS | Final constitutional verdict before irreversible actions |

---

## 10. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-05-08 | v1.0 — Initial contract with unified substrate packet | Arif |
| 2026-05-26 | v1.1 — Add routing protocol (Section 9) + `well_readiness_gate` | PHOENIX-73F |

---

**DITEMPA BUKAN DIBERI.**
