# VERDICT RECOVERY MATRIX
> **Authority:** 888_JUDGE  
> **Version:** v1.0.0-SEAL  
> **Status:** CONSTITUTIONAL MANDATE  
> **Band:** 000_KERNEL (F12 Resilience)

---

## 🎯 PURPOSE

Define state transitions and recovery protocols for all verdict outcomes. Ensures graceful degradation, prevents infinite loops, and provides clear escalation paths.

**F12 (Resilience):** Fail gracefully with defined recovery paths.  
**F1 (Amanah):** All state transitions must be reversible.

---

## 🔄 STATE MACHINE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│  VERDICT STATE MACHINE                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                         ┌──────────────┐                            │
│                         │   INITIAL    │                            │
│                         └──────┬───────┘                            │
│                                │                                     │
│                    init_anchor │                                     │
│                                ▼                                     │
│                         ┌──────────────┐                            │
│              ┌─────────▶│  OPERATIONAL │◀────────┐                  │
│              │          └──────┬───────┘         │                  │
│              │                 │                  │                  │
│         retry│            SEAL │                  │refresh           │
│              │                 │                  │                  │
│              │                 ▼                  │                  │
│         ┌────┴────┐      ┌──────────┐       ┌────┴────┐             │
│         │  SABAR  │◀─────│ EXECUTING│──────▶│DEGRADED │             │
│         └──┬────┬─┘      └──────────┘       └────┬────┘             │
│            │    │                  PARTIAL       │                  │
│    escalate│    │retry                             │terminate       │
│            │    └──────────────────────────────────┘                  │
│            ▼                                                         │
│      ┌──────────┐          VOID (non-recoverable)                   │
│      │  HUMAN   │────────────────────────────────────────┐           │
│      │ESCALATION│                                          ▼         │
│      └────┬─────┘                                  ┌──────────┐      │
│           │                                        │SAFE_MODE │      │
│    approve│reject                                  └────┬─────┘      │
│           │                                             │            │
│     ┌─────┴─────┐                              terminate│            │
│     ▼           ▼                                       ▼            │
│ ┌───────┐  ┌────────┐                            ┌──────────┐       │
│ │RESUME │  │TERMINATE│                           │TERMINATED│       │
│ └───┬───┘  └────────┘                            └──────────┘       │
│     │                                                                │
│     └──────────────────────────────────────────────────▶             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 RECOVERY MATRIX

### SEAL ✅ Recovery (None Required)

| Aspect | Specification |
|--------|---------------|
| **Trigger** | All F1-F13 constraints satisfied |
| **Action** | Proceed to next operation |
| **Next State** | OPERATIONAL |
| **Human Notification** | None (async audit log only) |
| **Reversibility** | N/A (successful completion) |

**Response:**
```json
{
  "verdict": "SEAL",
  "recovery": {
    "next_action": "continue",
    "state_transition": "OPERATIONAL"
  }
}
```

---

### SABAR ⏸️ Recovery Protocol

| Aspect | Specification |
|--------|---------------|
| **Trigger** | Recoverable constraint violation |
| **Max Retries** | 3 attempts |
| **Backoff Strategy** | Linear (immediate, +1s, +2s) |
| **Escalation** | After 3rd SABAR, escalate to human |

**SABAR State Machine:**

```
Attempt 1 ──SABAR──▶ Wait 0s ──Retry──▶ Attempt 2
                                         │
                                         SABAR
                                         │
                                         ▼
                              Wait 1s ──Retry──▶ Attempt 3
                                                    │
                                                    SABAR
                                                    │
                                                    ▼
                                         Wait 2s ──Retry──▶ Attempt 4
                                                              │
                                                              SABAR
                                                              │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │  ESCALATE TO    │
                                                    │  HUMAN (888)    │
                                                    └─────────────────┘
```

**SABAR Response Structure:**
```json
{
  "verdict": "SABAR",
  "recovery": {
    "sabar_step": 1,
    "max_retries": 3,
    "next_action": "retry",
    "state_transition": "OPERATIONAL",
    "retry_delay_ms": 0,
    "strategy_change_required": true
  }
}
```

**Retry Requirements:**
- Each retry must use a different approach
- Cannot retry with identical parameters
- Must log what changed between attempts
- Must update entropy budget (ΔS accumulates)

---

### VOID ❌ Recovery Protocol

| VOID Type | Cause | Action | Reversible? |
|-----------|-------|--------|-------------|
| **VOID_AUTH** | Invalid/expired credentials | Re-authenticate | Yes |
| **VOID_ENTROPY** | Budget exhausted | Checkpoint refresh | Yes (888 only) |
| **VOID_CONSTITUTION** | F1-F13 violation | Depends on floor | Maybe |
| **VOID_SYSTEM** | Internal failure | Degraded mode | No |
| **VOID_KILL** | Kill-switch triggered | Safe mode | No |

#### VOID Recovery Flowchart

```
VOID Detected
      │
      ▼
┌─────────────┐
│ Can Retry?  │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
  Yes     No
   │       │
   ▼       ▼
┌──────┐ ┌──────────────┐
│Retry │ │Enter Safe    │
│Auth  │ │Mode?         │
└──┬───┘ └──────┬───────┘
   │            │
   │       ┌────┴────┐
   │      Yes       No
   │       │         │
   │       ▼         ▼
   │   ┌────────┐  ┌──────────┐
   │   │DEGRADED│  │TERMINATE │
   │   └───┬────┘  └──────────┘
   │       │
   │   ┌───┴───┐
   │  Success Fail
   │   │       │
   │   ▼       ▼
   │ ┌─────┐ ┌──────────┐
   └▶│SEAL │ │TERMINATE │
     └─────┘ └──────────┘
```

#### VOID with Recovery Example

```json
{
  "verdict": "VOID",
  "status": "UNAUTHORIZED",
  "errors": [{
    "code": "VOID_AUTH_EXPIRED",
    "message": "Session token expired 5 minutes ago",
    "recoverable": true,
    "details": { "expired_at": "2026-03-30T20:30:00Z" }
  }],
  "recovery": {
    "sabar_step": null,
    "max_retries": 0,
    "next_action": "escalate",
    "state_transition": "SAFE_MODE",
    "requires_reauth": true
  }
}
```

---

### PARTIAL ⚠️ Recovery Protocol

| Aspect | Specification |
|--------|---------------|
| **Trigger** | Degraded success with constraints |
| **Action** | Continue with reduced capability |
| **Next State** | DEGRADED |
| **Human Notification** | Async warning |

**PARTIAL State Machine:**

```
Operation Requested
        │
        ▼
┌───────────────┐
│ PARTIAL Result│
│ (constraints) │
└───────┬───────┘
        │
   ┌────┴────┐
   │         │
 Acceptable  Unacceptable
   │         │
   ▼         ▼
┌──────┐  ┌─────────┐
│CONTINUE│ │ESCALATE │
│DEGRADED│ │TO HUMAN │
└───┬────┘ └────┬────┘
    │           │
    ▼           ▼
┌────────┐  ┌──────────┐
│SEAL next│ │SEAL/VOID │
└────────┘  └──────────┘
```

**PARTIAL Response Structure:**
```json
{
  "verdict": "PARTIAL",
  "status": "DEGRADED",
  "payload": {
    "result": "approximate",
    "confidence": 0.6,
    "caveats": ["Using stale cache", "Approximate calculation"]
  },
  "recovery": {
    "next_action": "continue",
    "state_transition": "DEGRADED",
    "degradation_reason": "dependency_unavailable",
    "full_capability_recovery": "auto_on_dependency_restore"
  }
}
```

---

## 👤 HUMAN ESCALATION PROTOCOL

### Escalation Triggers

| Condition | Priority | Timeout | Response Required |
|-----------|----------|---------|-------------------|
| 3rd consecutive SABAR | HIGH | 5 min | Approve/Revise/Void |
| VOID_ENTROPY_BUDGET | HIGH | 10 min | Checkpoint/Terminate |
| VOID_CONSTITUTION (F9) | CRITICAL | Immediate | Immediate decision |
| VOID_KILL_SWITCH | CRITICAL | Immediate | N/A (auto-terminate) |
| PARTIAL with low confidence | MEDIUM | 30 min | Accept/Reject |

### Escalation Interface

```typescript
interface EscalationRequest {
  escalation_id: string;
  session_id: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  
  context: {
    verdict: VerdictCode;
    errors: VerdictError[];
    session_delta_s: number;
    sabar_count: number;
  };
  
  options: {
    approve: { description: string; risk: string };
    revise: { description: string; suggested_changes: string[] };
    void: { description: string; consequence: string };
  };
  
  timeout_at: string;  // ISO 8601
}
```

### Human Response Actions

| Response | Effect | Next State |
|----------|--------|------------|
| **APPROVE** | Override VOID, proceed with warning | OPERATIONAL |
| **REVISE** | Provide corrected parameters | RETRY |
| **VOID** | Confirm rejection, enter safe mode | SAFE_MODE |
| **TIMEOUT** | Auto-degrade to SAFE_MODE | DEGRADED |

---

## 🛡️ SAFE MODE SPECIFICATION

### Entry Conditions

Safe mode activates when:
- VOID_KILL triggered
- 3 consecutive VOIDs without recovery
- Human escalation timeout
- 888_JUDGE explicit command

### Safe Mode Capabilities

| Capability | Status | Notes |
|------------|--------|-------|
| vault_ledger (read) | ✅ | Audit log access only |
| math_estimator | ✅ | Diagnostics only |
| init_anchor (refresh) | ✅ | Session recovery |
| All write operations | ❌ | Blocked |
| Code execution | ❌ | Blocked |
| External API calls | ❌ | Blocked |

### Safe Mode Exit

```python
async def exit_safe_mode(session_id: str, actor_id: str) -> Result:
    """
    Exit safe mode requires:
    1. 888_JUDGE authority OR
    2. Successful init_anchor refresh with human attestation
    """
    
    if actor_id != "888_JUDGE":
        # Requires human attestation
        attestation = await request_human_attestation(session_id)
        if not attestation.approved:
            return Result.void("Human attestation required")
    
    # Reset session state
    await session_store.update(session_id, {
        'state': 'OPERATIONAL',
        'sabar_count': 0,
        'entropy_budget': BUDGET_STANDARD,
        'exit_safe_mode_at': datetime.utcnow().isoformat()
    })
    
    await vault_ledger({
        'mode': 'seal',
        'evidence': f'Session {session_id} exited safe mode',
        'actor_id': actor_id
    })
    
    return Result.seal()
```

---

## 📋 COMPLIANCE CHECKLIST

For verdict implementers:

- [ ] Define recovery object for SABAR/VOID/PARTIAL
- [ ] Implement retry with strategy change
- [ ] Limit SABAR to 3 attempts
- [ ] Escalate to human after max retries
- [ ] Support safe mode entry/exit
- [ ] Log all state transitions
- [ ] Provide human escalation interface
- [ ] Define timeout for human responses

---

## 🔗 RELATED DOCUMENTS

- `VERDICT_SCHEMA_STANDARD.md` (recovery object spec)
- `000_CONSTITUTION.md` (F12 Resilience)
- `HUMAN_IN_LOOP_SPEC.md` (escalation interface)

---

*Ditempa Bukan Diberi* [ΔΩΨ|888] 🔄
