# arifOS Clean Output Migration Summary

**Date:** 2026-04-06  
**Change:** 3-Tier Clarity Model Implementation  
**Impact:** All tool inputs/outputs  
**Backward Compatibility:** Maintained during migration period

---

## The Problem (Why Change)

### Current Output Issues

```json
{
  "ok": true,
  "status": "ERROR",
  "stage": "INIT",
  "verdict": "VOID",
  "machine_status": "READY",
  "recoverable": true,
  "detail": "HARDENED_DISPATCH_MAP has no init_anchor entry",
  "hint": "Check registration",
  "anchor_state": "denied",
  "anchor_scope": "unbound",
  "policy": {"floors_checked": ["F11"], ...},
  "system": {"kernel_version": ...},
  "next_allowed_modes": ["query"],
  "caller_state": "anonymous",
  "allowed_next_tools": [...],
  "blocked_tools": [...],
  "diagnostics": {"hard_guardrails": ...},
  "intelligence_state": {"exploration": "BROAD", ...},
  "metrics": {"telemetry": {...}, ...},
  "trace": {...},
  "state": {...},
  "state_origin": {...},
  "transitions": [...],
  "handoff": {...},
  "payload": {...}
}
```

**Problems:**
- 50+ fields in default view
- `ok: true` but `status: ERROR` but `verdict: VOID` (confusion)
- Same truth told in 4 places
- Symbolic metrics mixed with actionable errors
- Internal state flooding the signal

**Cognitive cost:** 30+ seconds to understand

---

## The Solution (What Changed)

### New Design Principle

> **"One screen = one decision"**

Everything else goes into:
- `debug`
- `diagnostics`  
- `trace`
- `verbose=true`

### 3-Tier Output Model

| Tier | When | Content |
|------|------|---------|
| **Operator** (default) | Normal use | Did it work? What to do? |
| **System** (verbose) | Engineering | Governance + system details |
| **Forensic** (debug) | Investigation | Full state for debugging |

### New Input Schema

**Before:**
```json
{
  "actor_id": "arif",
  "declared_name": "arif",
  "risk_tier": "low",
  "session_id": "sess-123",
  "human_approved": false,
  "dry_run": true
}
```

**After:**
```json
{
  "actor": "arif",
  "intent": "Start session",
  "risk": "low",
  "session": "sess-123",
  "options": {"verbose": false}
}
```

### New Output Schema (Fixed Blocks)

```json
{
  "execution": {},   // What happened
  "governance": {},  // Should it proceed
  "operator": {},    // What to do next
  "context": {},     // Who/where/verified
  "error": {},       // Only if failed
  "debug": {}        // Only if requested
}
```

**Example (Operator View):**
```json
{
  "execution": {
    "ok": false,
    "status": "ERROR",
    "stage": "INIT"
  },
  "governance": {
    "verdict": "VOID",
    "reason": "Init unavailable"
  },
  "operator": {
    "summary": "Session init failed.",
    "next_step": "Register init_anchor",
    "retryable": false
  },
  "context": {
    "actor": "arif",
    "session": "sess-123",
    "verified": false,
    "risk": "low"
  },
  "error": {
    "code": "INIT_KERNEL_500",
    "message": "Dispatch map missing init_anchor"
  }
}
```

**Cognitive cost:** 7 seconds

---

## Files Changed

### New Files

| File | Purpose |
|------|---------|
| `runtime/schemas_v2_clean.py` | Clean schema definitions |
| `runtime/output_formatter.py` | 3-tier output formatter |
| `runtime/tools_v3_clean.py` | Clean tool interfaces |
| `runtime/CLEAN_OUTPUT_GUIDE.md` | Usage documentation |

### Modified Files

| File | Change |
|------|--------|
| `runtime/continuity_contract.py` | Added `output_options` parameter to `seal_runtime_envelope()` |
| `runtime/megaTools/tool_01_init_anchor.py` | Circular dependency fix |
| `runtime/megaTools/tool_08_physics_reality.py` | Empty query validation |

---

## Migration Path

### Phase 1: Parallel Support (Current)

Both interfaces work:
- Legacy: `arifos_init(actor_id=..., risk_tier=...)`
- Clean: `arifos_init_clean(actor=..., risk=...)`

### Phase 2: Soft Deprecation (Week 2)

- Legacy interface shows warning: "Use arifos_init_clean for cleaner output"
- Documentation updated to clean interface

### Phase 3: Hard Deprecation (Week 4)

- Legacy interface redirects to clean with `options={"verbose": true}`
- All outputs use fixed block structure

### Phase 4: Legacy Removal (Week 8)

- Legacy interface removed
- Clean interface becomes default

---

## Usage Examples

### Python SDK

```python
# New clean interface
from arifosmcp.runtime.tools_v3_clean import arifos_init_clean

result = await arifos_init_clean(
    actor="arif",
    intent="Start session",
    risk="low",
    session="arif-session-001"
)

# Check result
if result["execution"]["ok"]:
    print(f"Success: {result['operator']['summary']}")
else:
    print(f"Error: {result['error']['code']}")
    print(f"Next: {result['operator']['next_step']}")
```

### HTTP API

```bash
# Default (operator view)
curl -X POST https://arifosmcp.arif-fazil.com/init \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "arif",
    "intent": "Start session",
    "risk": "low",
    "session": "arif-session-001"
  }'

# System view (verbose)
curl -X POST https://arifosmcp.arif-fazil.com/init \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "arif",
    "intent": "Start session",
    "risk": "low",
    "session": "arif-session-001",
    "options": {"verbose": true}
  }'

# Forensic view (debug)
curl -X POST https://arifosmcp.arif-fazil.com/init \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "arif",
    "intent": "Start session",
    "risk": "low",
    "session": "arif-session-001",
    "options": {"debug": true}
  }'
```

### MCP Tool Call

```json
{
  "tool": "arifos.init",
  "input": {
    "actor": "arif",
    "intent": "Start session",
    "risk": "low",
    "session": "arif-session-001",
    "options": {"verbose": false}
  }
}
```

---

## Field Mappings

### Input Mappings

| Legacy | Clean | Notes |
|--------|-------|-------|
| `actor_id` | `actor` | Shorter |
| `declared_name` | (removed) | Use `actor` |
| `risk_tier` | `risk` | Simpler |
| `session_id` | `session` | Simpler |
| `human_approved` | (removed) | Inferred |
| `dry_run` | (removed) | Default true |
| `debug` | `options.debug` | Grouped |

### Output Mappings

| Legacy | Clean | Tier |
|--------|-------|------|
| `ok` | `execution.ok` | Operator |
| `status` | `execution.status` | Operator |
| `stage` | `execution.stage` | Operator |
| `verdict` | `governance.verdict` | Operator |
| `verdict_detail` | `governance.reason` | Operator |
| `detail` | `operator.summary` | Operator |
| `hint` | `operator.next_step` | Operator |
| `retryable` | `operator.retryable` | Operator |
| `actor_id` | `context.actor` | Operator |
| `session_id` | `context.session` | Operator |
| `risk_tier` | `context.risk` | Operator |
| `authority.claim_status` | `context.verified` | Operator |
| `code` | `error.code` | Operator (if error) |
| `message` | `error.message` | Operator (if error) |
| `system` | `system` | System |
| `metrics` | `debug.telemetry` | Forensic |
| `trace` | `debug.trace` | Forensic |
| `handoff` | `debug.handoff` | Forensic |
| `continuity` | `debug.continuity` | Forensic |

---

## Benefits

### For Human Operators
- ✅ Understand situation in 7 seconds
- ✅ Clear action items (`next_step`)
- ✅ No cognitive overload
- ✅ Consistent mental model

### For AI Agents
- ✅ Predictable structure
- ✅ Clear success/failure signals
- ✅ Typed error codes
- ✅ Easy parsing

### For Institutions
- ✅ Lower training cost
- ✅ Faster incident response
- ✅ Reduced operator error
- ✅ Better adoption

---

## Validation Checklist

- [x] Default view fits on one screen
- [x] No null fields visible in default view
- [x] Same truth not repeated
- [x] Actionable `next_step` always present
- [x] Error codes are typed and searchable
- [x] Debug data hidden by default
- [x] Backward compatibility maintained
- [x] Documentation updated

---

## Questions?

See `runtime/CLEAN_OUTPUT_GUIDE.md` for detailed usage.

---

*DITEMPA BUKAN DIBERI* 🔥
