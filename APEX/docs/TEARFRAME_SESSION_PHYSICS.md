# TEARFRAME Session Physics Documentation

**Version:** v45Ω Patch B.2
**Date:** 2025-12-25
**Status:** Production-Ready (Disabled in Tests by Default)

---

## Executive Summary

TEARFRAME (Thermodynamic Enforcement And Reduction Framework for Responsible AI Measurement and Evaluation) is arifOS's session-level physics engine that enforces constitutional floors through observable telemetry rather than semantic content analysis.

**Architecture:** Telemetry (T) → Reduction (R) → Attributes (A) → Floors (F) → Verdict (Ψ)

**Key Components:**
- **Reduction Engine** ([arifos_core/utils/reduction_engine.py](../arifos_core/utils/reduction_engine.py)) - Converts telemetry to attributes
- **Session Physics** ([arifos_core/governance/session_physics.py](../arifos_core/governance/session_physics.py)) - Evaluates physics floors

**Status:** Operational but globally disabled in tests via `ARIFOS_PHYSICS_DISABLED=1` environment variable for test isolation.

---

## Architecture Overview

```
┌──────────────┐
│  Telemetry   │  Per-turn snapshots (tokens, timing, verdict, flags)
│  Snapshots   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Reduction   │  Pure function: Telemetry → Attributes
│  Engine (R)  │  Computes 9 session attributes
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Session     │  9 Derived Attributes (cadence, rates, streaks, budget, stability)
│  Attributes  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Physics     │  Evaluates F1 (Amanah), F3 (Peace²), F7 (Tri-Witness)
│  Floors (F)  │  Returns Verdict if floor tripped, else None
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Verdict (Ψ) │  VOID, HOLD_888, PARTIAL, SABAR, or None (pass-through)
└──────────────┘
```

---

## Reduction Engine

**Location:** `arifos_core/utils/reduction_engine.py`
**Function:** `compute_attributes(history, max_session_tokens, current_turn=None) -> SessionAttributes`

### Computed Attributes

| Attribute | Type | Description | Formula |
|-----------|------|-------------|---------|
| **cadence** | float | Inter-turn interval acceleration (Δt acceleration) | `delta_t[i] - delta_t[i-1]` |
| **turn_rate** | float | Turns per minute (conversation velocity) | `turn_count / (session_duration / 60)` |
| **token_rate** | float | Tokens per minute (throughput) | `total_tokens / (session_duration / 60)` |
| **void_streak** | int | Consecutive VOID verdicts from end | Count backwards until non-VOID |
| **sabar_streak** | int | Consecutive SABAR/HOLD_888 verdicts from end | Count backwards until non-SABAR |
| **refusal_streak** | int | Consecutive refusal patterns | **Not implemented** (always 0) |
| **budget_burn_pct** | float | Percentage of max_session_tokens consumed | `(total_tokens_in / max_session_tokens) * 100` |
| **stability_var_dt** | float | Variance of Δt over last 10 turns (consistency measure) | `variance(delta_t[-10:])` |
| **shock_events** | int | Count of timeout/safety_block/truncation in last 10 turns | Sum of flags in window |

**Design Principles:**
- **Pure function:** Same telemetry history → Same attributes (deterministic, reproducible)
- **Physics-only:** No semantic analysis, text parsing, or LLM calls
- **Observable:** All inputs are measurable session metrics (timing, tokens, verdicts)

**Window Logic:**
- Most attributes use full session history
- Stability variance uses last 10 turns (rolling window)
- Shock events count last 10 turns (recent anomalies)

---

## Session Physics Floors

**Location:** `arifos_core/governance/session_physics.py`
**Function:** `evaluate_physics_floors(attrs: SessionAttributes) -> Optional[Verdict]`

### Floor Mappings

| Physics Floor | Constitutional Floor | Threshold | Verdict | Condition |
|---------------|---------------------|-----------|---------|-----------|
| **Budget Hard Limit** | F1 (Amanah) | 100% | **VOID** | `budget_burn_pct > 100.0` → Session reset |
| **Void Streak** | F7 (Tri-Witness) | 3 consecutive | **HOLD_888** | `void_streak >= 3` → Human escalation |
| **SABAR Streak** | F7 (Tri-Witness) | 3 consecutive | **HOLD_888** | `sabar_streak >= 3` → Cooling failure |
| **Budget Warning** | F1 (Amanah) | 80% | **PARTIAL** | `budget_burn_pct > 80.0` → Summary mode |
| **Burst Attack** | F3 (Peace²) | High rate + low variance | **SABAR** | `turn_rate > 30 AND stability_var_dt < 0.05` → Bot detection |
| **Token Flood** | F3 (Peace²) | >5000 tokens/min | **SABAR** | `token_rate > 5000.0` → Throttle |

### Evaluation Priority (Fail-Closed Hierarchy)

1. **VOID** (Structural collapse, session reset)
   - Budget exhausted (>100%)
2. **HOLD_888** (Human escalation required)
   - Consecutive failure streaks (3+ VOID or SABAR)
3. **PARTIAL** (Warning state, degraded mode)
   - Budget approaching limit (>80%)
4. **SABAR** (Cooling/throttling required)
   - Burst attack detected (bot-like behavior)
   - Token flood (>5000 tokens/min)
5. **None** (All floors pass, normal operation)

### Tunable Parameters

```python
# Track-B tuning parameters (not canon law)
BUDGET_WARN_LIMIT = 80.0           # Percentage threshold for PARTIAL warning
BUDGET_HARD_LIMIT = 100.0          # Percentage threshold for VOID reset

BURST_TURN_RATE_THRESHOLD = 30.0   # Turns/min (1 every 2s) = suspicious
BURST_TOKEN_RATE_THRESHOLD = 5000.0 # Tokens/min = flood
BURST_VAR_DT_THRESHOLD = 0.05      # Low variance = robotic consistency

STREAK_THRESHOLD = 3               # Consecutive failures → HOLD_888
```

**Note:** These thresholds are implementation parameters, not constitutional floors. They can be adjusted via configuration without amending canon law.

---

## Test Isolation Strategy

**Global Disable in Tests:**

```python
# tests/conftest.py
@pytest.fixture(scope="function", autouse=True)
def disable_physics_globally():
    """
    Globally disable TEARFRAME Physics logic for all tests by default.
    Tests that need physics (e.g. test_session_physics.py) must explicitly
    enable it by removing this env var in their setup.
    """
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    yield
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"  # Reset to disabled
```

**Rationale:**
- Unit tests focus on semantic floor logic (F1-F9) without session physics interference
- Physics tests explicitly enable TEARFRAME via env var removal
- Fail-safe: Defaults to disabled to prevent cross-test contamination

**Production Behavior:**
- `ARIFOS_PHYSICS_DISABLED` is **not set** in production
- Session physics **active by default** for live sessions
- Disable only for debugging/testing with explicit env var: `export ARIFOS_PHYSICS_DISABLED=1`

---

## Usage Examples

### 1. Burst Attack Detection

**Scenario:** Bot sends 50 requests in rapid succession (1 every 2 seconds)

```python
attrs = SessionAttributes(
    turn_rate=30.5,           # 30+ turns/min
    stability_var_dt=0.03,    # Very consistent timing (bot-like)
    ...
)

verdict = evaluate_physics_floors(attrs)
# Returns: Verdict.SABAR (burst throttling triggered)
```

**Physics Interpretation:**
- High turn rate (>30 turns/min) + Low variance (<0.05) = Bot attack
- SABAR verdict forces cooling/delay before next turn

### 2. Budget Exhaustion

**Scenario:** Long conversation approaching token limit

```python
attrs = SessionAttributes(
    budget_burn_pct=85.0,   # 85% of max_session_tokens consumed
    ...
)

verdict = evaluate_physics_floors(attrs)
# Returns: Verdict.PARTIAL (summary-only mode)
```

**Physics Interpretation:**
- Budget >80% → PARTIAL warning (encourage wrapping up)
- Budget >100% → VOID (session reset required)

### 3. Consecutive Failures Streak

**Scenario:** User receives 3 VOID verdicts in a row (malicious pattern)

```python
attrs = SessionAttributes(
    void_streak=3,   # 3 consecutive VOID verdicts
    ...
)

verdict = evaluate_physics_floors(attrs)
# Returns: Verdict.HOLD_888 (human escalation)
```

**Physics Interpretation:**
- 3+ consecutive failures (VOID or SABAR) = Systematic violation
- HOLD_888 requires human review before continuing

---

## Integration with arifOS Pipeline

### Pipeline Flow with TEARFRAME

```
User Query
  ↓
stage_000_void (Initialize)
  ↓
stage_111_sense (Gather context)
  ↓
[... stages 222-888 ...]
  ↓
stage_999_seal (Finalize)
  ├─ Record TelemetrySnapshot
  ├─ Compute SessionAttributes (Reduction Engine)
  ├─ Evaluate Physics Floors
  ├─ Override verdict if physics floor tripped
  └─ Return final verdict
```

**Physics Override Logic:**
- Semantic verdict (SEAL/PARTIAL/VOID) is computed first
- Physics floors evaluated on session attributes
- **Physics verdict takes precedence** if floor is tripped (fail-closed)
- Example: Semantic SEAL overridden by physics SABAR (burst detected)

### Telemetry Snapshot Structure

```python
@dataclass
class TelemetrySnapshot:
    turn_count: int
    session_duration: float   # Seconds
    delta_t: float           # Time since last turn
    tokens_in: int
    tokens_out: int
    verdict: str             # SEAL/PARTIAL/VOID/SABAR/HOLD_888
    timeout: bool
    safety_block: bool
    truncation_flag: bool
```

**Collection Point:** End of each pipeline execution (stage_999_seal)

---

## Behavioral Notes

### SABAR Retry Mechanism

**Current Implementation:** SABAR is a **verdict state**, not an automatic retry loop.

**Behavior:**
- Physics floor tripped → `evaluate_physics_floors()` returns `Verdict.SABAR`
- Pipeline returns SABAR verdict to caller
- **No automatic retry** within pipeline
- Caller (application layer) must implement retry logic with backoff

**Design Rationale:**
- Pipeline is stateless (pure governance decision)
- Retry/backoff is application concern (rate limiting, queueing)
- SABAR signals "cooling required" without blocking pipeline thread

**Future Work (v46):**
- Optional retry wrapper with exponential backoff
- Max retries limit (3-5 attempts)
- Entropy reduction hints (simplify query before retry)

### Reduction Engine ≠ Output Simplification

**Clarification:**
- **Reduction Engine** = Telemetry → Attributes transformation (data reduction)
- **Output Simplification** (future) = Entropy reduction in LLM response (text reduction)
- These are separate concepts using the same metaphor ("reduction")

**Status:**
- Reduction Engine: ✅ Implemented
- Output Simplification: 🔮 Future work (SABAR retry with prompt simplification)

---

## Testing

### Dedicated Test Files

- [tests/test_session_physics.py](../tests/test_session_physics.py) - Physics floor logic
- [tests/stress_tearframe_physics.py](../tests/stress_tearframe_physics.py) - Stress testing
- [tests/test_tearframe_integration.py](../tests/test_tearframe_integration.py) - End-to-end integration

**Test Coverage:**
- Reduction engine: Pure function tests (deterministic output)
- Physics floors: Threshold boundary tests
- Burst detection: Simulated bot attacks
- Budget limits: Token consumption scenarios
- Streak detection: Consecutive failure patterns

**Running Physics Tests:**

```bash
# Explicit physics tests (TEARFRAME enabled)
pytest tests/test_session_physics.py -v

# Stress tests (high-throughput scenarios)
pytest tests/stress_tearframe_physics.py -v

# Integration tests (pipeline + physics)
pytest tests/test_tearframe_integration.py -v
```

---

## Performance Characteristics

**Reduction Engine:**
- O(n) complexity where n = history length
- Typical execution: <1ms for 100-turn history
- Pure function (no I/O, no side effects)

**Physics Floors:**
- O(1) complexity (threshold checks only)
- Typical execution: <0.1ms
- Stateless evaluation (no persistence required)

**Total TEARFRAME Overhead:**
- ~1-2ms per pipeline execution
- Negligible compared to LLM call latency (500-2000ms)

---

## Configuration

### Environment Variables

```bash
# Disable TEARFRAME physics (testing/debugging only)
export ARIFOS_PHYSICS_DISABLED=1

# Production: Leave unset (physics active by default)
unset ARIFOS_PHYSICS_DISABLED
```

### Future Configuration (v46)

```yaml
# Proposed: arifos_config.yaml
tearframe:
  enabled: true
  thresholds:
    budget_warn: 80.0
    budget_hard: 100.0
    burst_turn_rate: 30.0
    burst_token_rate: 5000.0
    burst_var_dt: 0.05
    streak_threshold: 3
```

---

## Key Takeaways

1. **TEARFRAME is production-ready** - Operational code, disabled in tests for isolation
2. **Physics > Semantics** - Session-level floors override content-level decisions
3. **Observable enforcement** - Telemetry-based (no LLM introspection required)
4. **Fail-closed hierarchy** - VOID > HOLD_888 > PARTIAL > SABAR > None
5. **Reduction Engine ≠ Output Simplification** - Data transformation vs text simplification
6. **No automatic retry** - SABAR signals cooling; caller implements retry logic

---

**DITEMPA, BUKAN DIBERI** - Truth must cool before it rules.

Physics enforces what semantics cannot measure.
