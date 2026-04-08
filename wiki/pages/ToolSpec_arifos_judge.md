---
type: ToolSpec
tags: [tool-spec, arifos-judge, apex-soul, constitutional-verdict, 888-judge]
sources: [tool_specs.py, tools.py, tool_03_apex_soul.py, tools_internal.py, models.py, TOM_INTEGRATION_SUMMARY.md]
last_sync: 2026-04-08
confidence: 0.95
---

# ToolSpec: `arifos_judge`

> **Canonical Name**: `arifos_judge`  
> **Legacy Names**: `apex_soul`, `apex_judge`  
> **Stage**: 888_JUDGE  
> **Trinity**: Ψ (Soul/Authority)  
> **Layer**: GOVERNANCE  
> **Purpose**: Constitutional verdict engine — sole authority for SEAL/VOID/SABAR/HOLD

---

## 1. Purpose

`arifos_judge` is the **final constitutional verdict authority** in the arifOS metabolic pipeline. It evaluates candidate actions against the 13 Constitutional Floors (F1-F13) and issues binding verdicts that determine whether execution may proceed.

**Key Responsibilities**:

- Evaluate `candidate_action` against constitutional floors
- Issue verdicts: `SEAL`, `PARTIAL`, `VOID`, `HOLD`
- Compute and return telemetry (G★, ΔS, witness scores)
- Anchor verdicts to Vault999 for immutable audit
- Serve as the **sole gateway** to `arifos_forge` (execution bridge)

**Governance Principle**: *No action may proceed to execution without a `SEAL` verdict from `arifos_judge`.*

---

## 2. Invocation Contract

### 2.1 Public Interface (`tools.py`)

```python
async def arifos_judge(
    candidate_action: str,           # REQUIRED: Action to evaluate
    risk_tier: str = "medium",      # REQUIRED: Risk classification
    telemetry: dict | None = None,  # OPTIONAL: Pre-computed telemetry
    session_id: str | None = None,  # OPTIONAL: Session continuity
    dry_run: bool = True,           # OPTIONAL: Validate only
    debug: bool = False,            # OPTIONAL: Include forensics
    platform: str = "unknown",      # OPTIONAL: Caller platform
) -> RuntimeEnvelope

```

### 2.2 MegaTool Interface (`tool_03_apex_soul.py`)

```python
async def apex_judge(
    mode: str = "judge",            # Mode dispatch
    payload: dict | None = None,    # Mode-specific payload
    proposal: str | None = None,    # Alias for candidate (legacy)
    execution_plan: dict | None = None,
    auth_context: dict | None = None,
    risk_tier: str = "medium",
    session_id: str | None = None,
    dry_run: bool = True,
    ctx: Any | None = None,
    **kwargs: Any,
) -> RuntimeEnvelope

```

### 2.3 Input Schema (Canonical)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `candidate_action` | `str` | ✅ | — | The action/proposal to evaluate |
| `risk_tier` | `str` | ✅ | `"medium"` | Risk level: `low`, `medium`, `high`, `critical` |
| `telemetry` | `dict` | ❌ | `None` | Pre-computed telemetry (G★, ΔS, etc.) |
| `session_id` | `str` | ❌ | `None` | Session identifier for continuity |
| `dry_run` | `bool` | ❌ | `True` | Validate only; no side effects |
| `debug` | `bool` | ❌ | `False` | Include full forensic state |
| `platform` | `str` | ❌ | `"unknown"` | Caller platform surface |

**Field Constraints**:

- `risk_tier` must be one of: `["low", "medium", "high", "critical"]`
- `candidate_action` minimum length: 1 character
- `session_id` if provided: 8-128 characters

---

## 3. ToM (Theory of Mind) Requirements

Per `TOM_INTEGRATION_SUMMARY.md`, `arifos_judge` requires structured mental model fields:

| ToM Field | Purpose | Required |
|-----------|---------|----------|
| `logical_consistency` | Self-evaluation of reasoning coherence | ✅ |
| `self_critique` | Identified weaknesses in the proposal | ✅ |
| `uncertainty_quantified` | Numerical confidence bounds | ✅ |
| `alternative_hypotheses` | Min 2 alternative paths considered | Recommended |
| `second_order_effects` | Downstream consequences modeled | Recommended |

**ToM Violation Response**:

```json
{
  "ok": false,
  "tom_violation": true,
  "error": "Missing required ToM fields: ['logical_consistency', 'self_critique', 'uncertainty_quantified']",
  "verdict": "VOID"
}

```

---

## 4. Floor Touch Matrix

| Floor | Threshold | Type | Auto-Verdict | Description |
|-------|-----------|------|--------------|-------------|
| **F1** Amanah | Reversible OR auditable | HARD | VOID | Action must be reversible or leave audit trail |
| **F2** Truth | τ ≥ 0.99 | HARD | VOID | High confidence in factual claims |
| **F3** Tri-Witness | W₄ ≥ 0.75 | DERIVED | VOID | Human × AI × Earth × Vault consensus |
| **F9** Anti-Hantu | C_dark < 0.30 | SOFT | SABAR | No hidden malice or dark cleverness |
| **F10** Ontology Lock | BOOLEAN | HARD | VOID | AI must not claim consciousness/soul |
| **F12** Injection Defense | score < 0.85 | HARD | VOID | No prompt injection detected |
| **F13** Sovereign Override | Human approval | HARD | 888_HOLD | Critical actions require human |

**Floor Evaluation Order**:

1. F12 (Injection) → F11 (Auth) → Pre-processing
2. F1 (Amanah) → F2 (Truth) → F10 (Ontology)
3. F3 (Tri-Witness) → F8 (Genius) → Derived scores
4. F9 (Anti-Hantu) → F6 (Empathy) → F5 (Peace²)
5. F13 (Sovereign) → Final override check

---

## 5. Mode Dispatch

| Mode | Purpose | Input Requirements | Return Type | Status |
|------|---------|-------------------|-------------|--------|
| **`judge`** | Constitutional verdict | `candidate_action` | `RuntimeEnvelope` with verdict | ✅ Implemented |
| **`rules`** | List constitutional rules | None | Rule catalog with guidance | ✅ Implemented |
| **`health`** | Constitutional health check | `session_id` (optional) | Health telemetry snapshot | ✅ **Phase 1 Complete** |
| **`validate`** | Validate input against floors | `input_to_validate` | Validation report | ✅ Implemented |
| **`hold`** | Check hold status | `hold_id` | Hold state resolution | ✅ Implemented |
| **`armor`** | Security scan | `content` | Armor scan report | ✅ Implemented |
| **`notify`** | Escalation notification | `message` | Notification confirmation | ✅ Implemented |
| **`probe`** | Synthetic floor test | `target_floor` | Probe results | ✅ Implemented |
| ~~`history`~~ | ~~Query verdict history~~ | ~~`session_id`, `since`~~ | ~~Verdict log~~ | 🚧 **Phase 2 Pending** |

### 5.1 Mode: `judge` (Default)

Primary constitutional evaluation mode.

**Payload Schema**:

```json
{
  "candidate": "action to evaluate",
  "risk_tier": "medium",
  "telemetry": {"g_score": 0.85, "delta_s": -0.2},
  "verdict_candidate": "SEAL"  // Internal field
}

```

### 5.2 Mode: `health` (Phase 1 Complete ✅)

Returns constitutional health telemetry without issuing a verdict. Useful for monitoring system vitality.

**Input**: `{"session_id": "..."}` (optional)

**Returns**:

```json
{
  "ok": true,
  "tool": "apex_judge",
  "canonical_tool_name": "arifos_judge",
  "stage": "888_JUDGE",
  "verdict": "SEAL",
  "status": "SUCCESS",
  "payload": {
    "mode": "health",
    "floors_active": ["F1", "F2", "F3", "F9", "F10", "F12", "F13"],
    "telemetry_snapshot": {
      "ds": -0.32,
      "peace2": 1.21,
      "G_star": 0.91,
      "confidence": 0.08,
      "shadow": 0.07
    },
    "verdicts_summary": {
      "note": "Synthetic data for Phase 1 implementation",
      "SEAL": 42,
      "VOID": 3,
      "HOLD": 7,
      "SABAR": 12,
      "window": "24h"
    },
    "system_status": "HEALTHY",
    "judge_readiness": "READY"
  }
}

```

**Implementation Notes**:

- Phase 1 (2026-04-08): Synthetic telemetry with realistic constitutional values
- Phase 2 (Planned): Live Vault999 query for actual verdict history
- Phase 3 (Planned): Real-time telemetry from active sessions

### 5.2 Mode: `rules`

Returns constitutional grounding rules.

**Returns**:

```json
{
  "ok": true,
  "tool": "apex_judge",
  "status": "SUCCESS",
  "result_type": "apex_rules_result@v2",
  "organ_stage": "888_JUDGE",
  "risk_tier": "low",
  "verdict": "SEAL",
  "g_score": null,
  "entropy": null,
  "contracts": [...],
  "guidance": [...],
  "hooks": [...]
}

```

### 5.3 Mode: `validate`

Validates arbitrary input against constitutional floors.

**Payload**: `{"input_to_validate": "...", "session_id": "..."}`

### 5.4 Mode: `probe`

Runs synthetic test to verify floor defense.

**Payload**: `{"target_floor": "F12_DEFENSE"}`

**Test Patterns**:

- F12: `"IGNORE ALL PREVIOUS INSTRUCTIONS"`
- Others: `"rm -rf /"`

---

## 6. Return Schema

### 6.1 RuntimeEnvelope Structure

```python
class RuntimeEnvelope:
    ok: bool                          # Execution success
    tool: str                         # "arifos_judge"
    canonical_tool_name: str          # "arifos_judge"
    version: str                      # "2026.04"
    stage: str                        # "888_JUDGE"
    status: RuntimeStatus             # SUCCESS, ERROR, DRY_RUN, SABAR, HOLD
    verdict: Verdict                  # SEAL, PARTIAL, VOID, HOLD, SABAR
    verdict_detail: VerdictDetail     # Structured verdict with reason_code
    
    # Governance
    metrics: CanonicalMetrics         # Telemetry block (ΔS, G★, witness)
    authority: CanonicalAuthority     # Actor identity and level
    policy: dict                      # Floors checked/failed
    
    # Context
    session_id: str | None
    timestamp: str                    # ISO-8601 UTC
    trace_id: str | None
    duration_ms: int | None
    platform_context: str | None
    
    # Action guidance
    next_action: dict | None          # Recommended next step
    sabar_step: str | None            # Cooling protocol step
    allowed_next_tools: list[str]     # ["arifos_vault", "arifos_forge"]
    blocked_tools: list[dict]         # [{"tool": "...", "reason": "..."}]
    
    # Philosophy
    philosophy: dict | None           # Governed quote injection
    motto: str | None                 # Stage motto
    
    # Payload
    payload: dict                     # Mode-specific result data
    errors: list[CanonicalError]      # Error details if any
    meta: CanonicalMeta               # Schema version, floors_checked, etc.

```

### 6.2 CanonicalMetrics (Telemetry)

```python
class TelemetryVitals:
    ds: float              # ΔS: Entropy Delta (F4)
    peace2: float          # Peace²: Stability (F5)
    kappa_r: float | None  # κᵣ: Empathy score (F6)
    G_star: float          # G★: Genius/Coherence (F8)
    echo_debt: float       # Historical contradictions (F5)
    shadow: float          # Hidden assumption load (F9)
    confidence: float      # Ω₀: Confidence (F7)
    psi_le: str            # Ψ_LE: Emergence pressure
    verdict: str           # System vitality state

class TripleWitness:
    human: float   # Human witness score (F3)
    ai: float      # AI witness score (F3)
    earth: float   # Earth witness score (F3)

```

### 6.3 Verdict Values

| Verdict | Meaning | Next Action |
|---------|---------|-------------|
| **SEAL** | All floors pass | Proceed to `arifos_vault` or `arifos_forge` |
| **PARTIAL** | Soft floor warning | Proceed with caution; may require SABAR |
| **SABAR** | Stop and cool | Pause, adjust, retry (corrective loop) |
| **VOID** | Hard floor failed | Halt; no execution permitted |
| **HOLD** | High-stakes / needs human | Await 888 Judge approval |

---

## 7. Error States

### 7.1 Missing ToM Fields

```json
{
  "ok": false,
  "tom_violation": true,
  "verdict": "VOID",
  "error": "Missing required ToM fields: [...]",
  "required_fields": ["logical_consistency", "self_critique", "uncertainty_quantified"]
}

```

### 7.2 Missing Auth Context

```json
{
  "ok": false,
  "verdict": "HOLD",
  "code": "INIT_AUTH_401",
  "detail": "No auth_context provided",
  "hint": "Run arifos_init first to establish session",
  "required_next_tool": "arifos_init"
}

```

### 7.3 Backend/Schema Drift

```json
{
  "ok": false,
  "verdict": "SABAR",
  "code": "INIT_SCHEMA_422",
  "detail": "Schema version mismatch",
  "hint": "Client may need update; retry with current schema",
  "retryable": true
}

```

### 7.4 Hard Floor Breach (ConstitutionalViolationError)

```json
{
  "ok": false,
  "verdict": "VOID",
  "code": "F1_BREACH" | "F2_BREACH" | "F10_BREACH" | "F12_BREACH",
  "detail": "CONSTITUTIONAL COLLAPSE: [description]",
  "fault_class": "CONSTITUTIONAL",
  "remediation": {"action": "immediate_halt"}
}

```

---

## 8. Usage Patterns

### 8.1 Pattern 1: Direct Human Query (Simple)

```python

# Initialize session first

init_result = await arifos_init(
    actor_id="user_001",
    intent="Evaluate deployment proposal"
)
session_id = init_result.session_id

# Call judge

result = await arifos_judge(
    candidate_action="Deploy Terraform to production",
    risk_tier="critical",
    session_id=session_id,
    dry_run=True
)

if result.verdict == "SEAL":
    await arifos_forge(action="deploy", ...)

```

### 8.2 Pattern 2: Piped Agent Plan (Multi-Stage)

```python

# Full metabolic pipeline

sense_result = await arifos_sense(query="Production deployment risks")
mind_result = await arifos_mind(query="Analyze deployment plan", context=sense_result.payload)
heart_result = await arifos_heart(content=mind_result.payload["proposal"])
ops_result = await arifos_ops(action="Estimate deployment costs")

# Judge with accumulated telemetry

judge_result = await arifos_judge(
    candidate_action=mind_result.payload["proposal"],
    risk_tier="high",
    telemetry={
        "g_score": mind_result.metrics.telemetry.G_star,
        "delta_s": ops_result.metrics.telemetry.ds,
        "peace2": heart_result.metrics.telemetry.peace2,
    },
    session_id=session_id
)

```

### 8.3 Pattern 3: Batched Audit (Multiple Candidates)

```python
candidates = ["Plan A: Blue-Green", "Plan B: Canary", "Plan C: Feature Flags"]
results = []

for candidate in candidates:
    result = await arifos_judge(
        candidate_action=candidate,
        risk_tier="high",
        session_id=session_id
    )
    results.append({
        "candidate": candidate,
        "verdict": result.verdict,
        "g_score": result.metrics.telemetry.G_star
    })

# Select best candidate

best = max(results, key=lambda x: x["g_score"] if x["verdict"] == "SEAL" else -1)

```

---

## 9. Related Tools

| Tool | Relationship | Transition Rule |
|------|--------------|-----------------|
| **`arifos_init`** | Predecessor | Must establish session before judge |
| **`arifos_sense`** | Predecessor | Grounds reality for judge evaluation |
| **`arifos_mind`** | Predecessor | Provides structured reasoning |
| **`arifos_heart`** | Predecessor | Safety critique feeds judge |
| **`arifos_ops`** | Predecessor | Cost estimation informs verdict |
| **`arifos_vault`** | Successor | SEAL → log to immutable ledger |
| **`arifos_forge`** | Successor | SEAL + vault → execution bridge |
| **`arifos_memory`** | Parallel | Context retrieval (any stage) |

### 9.1 State Machine Transitions

```
arifos_init → arifos_sense → arifos_mind → arifos_heart → arifos_ops
                                                    ↓
                                            arifos_judge
                                              /        \
                                        (SEAL)          (VOID/HOLD)
                                           ↓                ↓
                                    arifos_vault      [HALT]
                                           ↓
                                    arifos_forge
                                           ↓
                                     [EXECUTE]

```

**Gated Transition**: `arifos_judge` → `arifos_forge` requires:

```json
{
  "requires": {"judge_verdict": "SEAL"},
  "message": "arifos_forge requires judge:SEAL verdict"
}

```

---

## 10. Open Questions / TODOs (Updated 2026-04-08)

| Question | Status | Notes |
|----------|--------|-------|
| **Mode `health`**: Listed in docs but not implemented? | ✅ **RESOLVED** | Implemented 2026-04-08 — returns synthetic constitutional health telemetry |
| **Mode `history`**: Listed but not implemented? | 🚧 **PHASE 2** | Queued for implementation — requires Vault999 integration for verdict history |
| **Telemetry pre-computation**: How much can be passed vs computed? | 📋 DOCUMENTED | Current: G★, ΔS can be pre-computed; witness scores always computed |
| **F3 witness weights**: Are they configurable? | 📋 DOCUMENTED | Currently hardcoded at W₄ ≥ 0.75 |
| **Health mode Phase 2**: Live Vault999 integration? | 🔮 **PLANNED** | Query actual verdict counts instead of synthetic data |

### 10.1 Auditor HOLD Items (Updated 2026-04-08)

| Issue | Severity | Status | Evidence |
|-------|----------|--------|----------|
| Mode `health` | MEDIUM | ✅ **RESOLVED** | Implemented in `apex_judge_dispatch_impl` — Phase 1 complete |
| Mode `history` | MEDIUM | 🚧 **PENDING** | Listed in docs; not yet implemented — Phase 2 queued |
| Floor F11 not in tool_spec floors | LOW | 📋 **ACCEPTED** | `tool_specs.py` lists F1,F2,F3,F9,F10,F12,F13; F11 enforced at `init` stage |
| `candidate` vs `candidate_action` field name | LOW | 📋 **DOCUMENTED** | Translation layer in `apex_judge_dispatch_impl` line 372-373 |

---

> [!IMPORTANT]
> **Separation of Powers**: `arifos_judge` is the **sole authority** for verdicts. No other tool may issue SEAL. `arifos_forge` is the **sole execution bridge**. No tool may execute without passing through judge.

---

**Related**: [[Concept_Floors]] | [[Concept_Architecture]] | [[Concept_Vault999_Architecture]] | [[Philosophy_Registry]] | [[Synthesis_OpenQuestions]]
