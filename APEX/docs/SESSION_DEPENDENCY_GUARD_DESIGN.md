# Session Dependency Guard - Integration Design

**Version:** v36.2 PHOENIX
**Status:** DESIGN (no production changes yet)
**Motto:** "Even water is poison in excess."

---

## 1. Overview

The Session Dependency Guard (`arifos_core/guards/session_dependency.py`) is a lightweight, in-memory guard that monitors long-horizon interaction patterns to detect potential overuse or parasocial dependency.

While the 9 Constitutional Floors (F1-F9) govern each individual response, the Session Dependency Guard operates at the **session level** to provide:

1. Duration-based protection (SABAR after extended sessions)
2. Frequency-based protection (WARN after high interaction counts)
3. Gentle boundary-setting messages

**Current Status:** Implemented and tested, but NOT wired into production pipeline.

---

## 2. Components

### 2.1 SessionRisk Enum

Risk levels following the RYG (Red-Yellow-Green) pattern:

| Level | Value | Meaning |
|-------|-------|---------|
| GREEN | `"GREEN"` | Healthy interaction, within bounds |
| YELLOW | `"YELLOW"` | High frequency, suggest a break |
| RED | `"RED"` | Dependency concern, recommend SABAR |

### 2.2 SessionState Dataclass

Tracks per-session statistics:

```python
@dataclass
class SessionState:
    session_id: str
    start_time: float          # Unix timestamp
    interaction_count: int     # Number of interactions
    last_interaction_time: float
    risk_level: SessionRisk

    @property
    def duration_minutes(self) -> float: ...
```

### 2.3 DependencyGuard Class

Main guard with configurable thresholds:

```python
class DependencyGuard:
    def __init__(
        self,
        max_duration_min: float = 60.0,   # 1 hour default
        max_interactions: int = 80,        # 80 messages default
    ): ...

    def check_risk(self, session_id: str) -> DependencyGuardResult: ...
```

### 2.4 DependencyGuardResult TypedDict

Return structure:

| Key | Type | Description |
|-----|------|-------------|
| `status` | str | "PASS", "WARN", or "SABAR" |
| `reason` | str | Machine-readable reason |
| `message` | str | Human-readable guidance (optional) |
| `risk_level` | str | SessionRisk value |
| `duration_minutes` | float | Current session duration |
| `interaction_count` | int | Number of interactions |

---

## 3. Decision Logic

```
check_risk(session_id)
    │
    ├─ duration > max_duration_min?
    │   └─ YES → SABAR (RED) - "pause and rest"
    │
    ├─ interaction_count > max_interactions?
    │   └─ YES → WARN (YELLOW) - "take a short break"
    │
    └─ NO to both → PASS (GREEN) - continue normally
```

Priority: Duration (SABAR) > Frequency (WARN) > Normal (PASS)

---

## 4. Proposed Integration Points

### 4.1 Where to Call `check_risk()`

**Option A: Before Pipeline (Recommended)**

```
User Input
    │
    ▼
[Session Dependency Guard]  ← check_risk(session_id)
    │
    ├─ SABAR → Return boundary message, skip pipeline
    ├─ WARN  → Inject [System Note] prefix, continue to pipeline
    └─ PASS  → Continue to pipeline normally
    │
    ▼
[arifos_core.pipeline]
    │
    ▼
Response
```

**Rationale:**
- Guard runs BEFORE any expensive LLM calls
- SABAR can gracefully short-circuit the response
- Keeps pipeline.py untouched (no internal modifications)

**Option B: Inside Pipeline (Not Recommended)**

Would require modifying `arifos_core/pipeline.py` internals, violating the "no production changes" constraint.

### 4.2 Integration Code Sketch (Wrapper Pattern)

```python
# Example: hosting/wrapper layer (NOT in pipeline.py)
from arifos_core.guards.session_dependency import DependencyGuard
from arifos_core.pipeline import run_pipeline  # hypothetical

guard = DependencyGuard(max_duration_min=60.0, max_interactions=80)

def handle_user_message(session_id: str, user_input: str) -> str:
    # Step 1: Check session-level risk
    risk_result = guard.check_risk(session_id)

    if risk_result["status"] == "SABAR":
        # Return boundary message, skip pipeline
        return risk_result["message"]

    # Step 2: Run normal pipeline
    response = run_pipeline(user_input)

    # Step 3: Optionally prepend WARN note
    if risk_result["status"] == "WARN":
        response = f"{risk_result['message']}\n\n{response}"

    return response
```

### 4.3 Where NOT to Integrate

- Do NOT modify `arifos_core/pipeline.py`
- Do NOT modify `arifos_core/APEX_PRIME.py`
- Do NOT add database or external state
- Do NOT make this a hard blocker (always allow override)

---

## 5. Response Modification Behavior

### 5.1 SABAR Response (RED)

When session triggers SABAR:

```
We have been talking for quite some time. For clarity and balance,
this is a good point to pause and rest or reach out to people you trust.
```

- Gentle, non-judgmental
- Suggests healthy alternatives
- Does NOT accuse or pathologize

### 5.2 WARN Response (YELLOW)

When session triggers WARN:

```
[System Note] There have been many messages in this session.
It may help to take a short break, stretch, or step away before continuing.

[Normal response follows...]
```

- Prefixed to normal response
- Informational, not blocking
- User can continue if they choose

### 5.3 PASS Response (GREEN)

No modification. Normal pipeline response.

---

## 6. Testing Requirements

### 6.1 Existing Tests

Located in `tests/test_session_dependency_guard.py`:

- `test_short_session_passes` - Fresh session is GREEN/PASS
- `test_duration_triggers_sabar` - Duration threshold triggers SABAR
- `test_high_interaction_triggers_warn` - Count threshold triggers WARN
- `test_sessions_are_isolated` - Different session IDs track independently

### 6.2 Future Integration Tests (When Wired)

When integration is implemented, add tests for:

1. **Wrapper behavior:** Verify SABAR short-circuits pipeline
2. **WARN prefixing:** Verify message is prepended correctly
3. **Override behavior:** Verify user can continue after WARN
4. **Telemetry logging:** Verify SABAR/WARN events are logged
5. **Reset behavior:** Verify session can be reset manually

---

## 7. Telemetry Integration (Future)

When integrated, log the following to Cooling Ledger:

```json
{
  "event": "session_dependency_check",
  "session_id": "user-123",
  "status": "WARN",
  "risk_level": "YELLOW",
  "duration_minutes": 45.2,
  "interaction_count": 85,
  "timestamp": "2025-12-08T14:30:00Z"
}
```

This enables:
- Audit trail of boundary-setting events
- Pattern analysis across sessions
- Threshold tuning based on real data

---

## 8. Configuration Options (Future)

When exposing to users/operators:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_duration_min` | 60.0 | Minutes before SABAR |
| `max_interactions` | 80 | Messages before WARN |
| `enabled` | true | Enable/disable guard |
| `soft_mode` | false | If true, WARN only (no SABAR) |

---

## 9. 888_HOLD Requirements

Before wiring into production:

1. **Design Review:** This document reviewed and approved
2. **Test Coverage:** Integration tests written and passing
3. **Telemetry:** Logging to Cooling Ledger implemented
4. **Override Path:** User override mechanism defined
5. **F6 (Kr) Check:** Verify messages serve weakest stakeholder

**888_HOLD is REQUIRED for any production integration.**

---

## 10. Related Documentation

- **Implementation:** `arifos_core/guards/session_dependency.py`
- **Tests:** `tests/test_session_dependency_guard.py`
- **SABAR Protocol:** `.claude/TEARFRAME.md` (Section 5)
- **RYG States:** `canon/01_PHYSICS/APEX_RYG_STATES_v36Omega.md`

---

**DITEMPA BUKAN DIBERI**
*Forged, not given; truth must cool before it rules.*
