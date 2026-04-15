# arifOS Clean Output Guide — 3-Tier Clarity Model

**Version:** 2026.04.06-v0.2  
**Principle:** *"One screen = one decision"*

---

## Quick Start

### Input (Minimal)

```json
{
  "actor": "arif",
  "intent": "Explain how the human mind works",
  "risk": "low",
  "session": "arif-mind-20260406"
}
```

### Output (Operator View — Default)

```json
{
  "execution": {
    "ok": true,
    "status": "OK",
    "stage": "MIND"
  },
  "governance": {
    "verdict": "SEAL",
    "reason": "Grounded reasoning with falsification"
  },
  "operator": {
    "summary": "Reasoning completed successfully.",
    "next_step": "Review output and proceed to heart critique",
    "retryable": true
  },
  "context": {
    "actor": "arif",
    "session": "arif-mind-20260406",
    "verified": true,
    "risk": "low"
  }
}
```

**That's it.** 7 seconds to understand the situation.

---

## Three Output Tiers

### 1. Operator View (Default)

**When to use:** Normal operations, dashboards, human decision-making.

**Contains:**
- Did it work? (`execution`)
- Should it proceed? (`governance`)
- What do I do? (`operator`)
- Who/where/what? (`context`)

**Explicitly excludes:**
- telemetry, trace, handoff
- full payload, continuity state
- diagnostics, blocked_tools
- meta, state_origin, transitions

### 2. System View (`verbose: true`)

**When to use:** Engineering review, governance audit, debugging.

**Adds:**
```json
{
  "system": {
    "kernel_version": "2026.04",
    "adapter": "mcp",
    "env": "production"
  },
  "governance": {
    "authority": "verified",
    "operational_status": "pass",
    "proof_status": "complete"
  }
}
```

### 3. Forensic View (`debug: true`)

**When to use:** Deep investigation, incident response, contract verification.

**Adds:**
```json
{
  "debug": {
    "timestamp": "2026-04-06T12:00:00Z",
    "caller_state": "verified",
    "allowed_next_tools": ["arifos.heart", "arifos.judge"],
    "blocked_tools": [],
    "raw_payload": { ... },
    "trace": { ... },
    "telemetry": { ... },
    "continuity": { ... },
    "handoff": { ... },
    "diagnostics": { ... }
  }
}
```

---

## Fixed Block Structure

Every output follows this exact shape:

```json
{
  "execution": {},  // What happened
  "governance": {}, // Should it proceed
  "operator": {},   // What to do next
  "context": {},    // Who/where/verified
  "error": {},      // Only if failed
  "debug": {}       // Only if debug=true
}
```

**Benefit:** Consistent mental model across all tools.

---

## Input Schema Comparison

### Before (Chaotic)

```json
{
  "actor_id": "arif",
  "declared_name": "arif",
  "risk_tier": "low",
  "session_id": "sess-123",
  "human_approved": false,
  "dry_run": true,
  "debug": false,
  "payload": { ... }
}
```

### After (Clean)

```json
{
  "actor": "arif",
  "intent": "Explain human mind",
  "risk": "low",
  "session": "sess-123",
  "options": {
    "verbose": false,
    "debug": false
  }
}
```

**Changes:**
- `actor_id` + `declared_name` → `actor`
- `risk_tier` → `risk`
- `session_id` → `session`
- `human_approved`, `dry_run` → implied from context
- Explicit `options` block for verbosity

---

## Usage Examples

### Example 1: Failed Init (Operator View)

```python
result = await arifos.init(
    actor="arif",
    intent="Start new session",
    risk="low",
    session="arif-init-001"
)
```

**Output:**
```json
{
  "execution": {
    "ok": false,
    "status": "ERROR",
    "stage": "INIT"
  },
  "governance": {
    "verdict": "VOID",
    "reason": "Init tool unavailable"
  },
  "operator": {
    "summary": "Session initialization failed.",
    "next_step": "Register init_anchor in tools_hardened_dispatch.py",
    "retryable": false
  },
  "context": {
    "actor": "arif",
    "session": "arif-init-001",
    "verified": false,
    "risk": "low"
  },
  "error": {
    "code": "INIT_KERNEL_500",
    "message": "HARDENED_DISPATCH_MAP has no init_anchor entry"
  }
}
```

**Reading time:** 5 seconds.

### Example 2: Successful Mind (Verbose)

```python
result = await arifos.mind(
    actor="arif",
    intent="Explain consciousness",
    risk="low",
    session="arif-mind-001",
    options={"verbose": true}
)
```

**Output:**
```json
{
  "execution": {"ok": true, "status": "OK", "stage": "MIND"},
  "governance": {
    "verdict": "SEAL",
    "reason": "Grounded reasoning",
    "authority": "verified",
    "operational_status": "pass",
    "proof_status": "complete"
  },
  "operator": {
    "summary": "Reasoning completed with 3 alternative hypotheses.",
    "next_step": "Review output and proceed to heart critique",
    "retryable": true
  },
  "context": {"actor": "arif", "session": "arif-mind-001", "verified": true, "risk": "low"},
  "system": {
    "kernel_version": "2026.04",
    "adapter": "mcp",
    "env": "production"
  }
}
```

### Example 3: Debug Investigation

```python
result = await arifos.judge(
    actor="arif",
    intent="Validate deployment plan",
    risk="high",
    options={"debug": true}
)
```

**Output:** Full forensic state including telemetry, trace, handoff, continuity.

---

## Naming Cleanup

| Before | After | Reason |
|--------|-------|--------|
| `actor_id` | `actor` | Shorter, unambiguous |
| `declared_name` | (removed) | Collapsed into `actor` |
| `risk_tier` | `risk` | Simpler |
| `session_id` | `session` | Simpler |
| `verdict_detail` | `reason` | Clearer |
| `machine_status` | `status` | Less jargon |
| `detail` | `summary` | Action-oriented |
| `hint` | `next_step` | Action-oriented |
| `caller_state` | (debug only) | Reduced noise |
| `auth_state` | `verified` | Boolean clarity |

---

## Migration Guide

### Step 1: Update Inputs

Replace legacy input with clean input:

```python
# Old
await arifos.init(
    actor_id="arif",
    declared_name="arif",
    risk_tier="low",
    session_id="sess-123",
    dry_run=True,
)

# New
await arifos.init(
    actor="arif",
    intent="Start session",
    risk="low",
    session="sess-123",
)
```

### Step 2: Handle Outputs

Operator view is default. Check `execution.ok`:

```python
if result["execution"]["ok"]:
    print(f"Success: {result['operator']['summary']}")
else:
    print(f"Error: {result['error']['code']}")
    print(f"Next: {result['operator']['next_step']}")
```

### Step 3: Opt into Verbosity

```python
# System view
result = await arifos.mind(..., options={"verbose": True})

# Forensic view
result = await arifos.mind(..., options={"debug": True})
```

---

## Implementation Notes

### Backward Compatibility

Legacy format available during migration:

```python
from arifosmcp.runtime.output_formatter import format_output_legacy

# Returns old format
legacy_output = format_output_legacy(envelope, options)
```

### Tool Implementation

Tools automatically get clean output via `seal_runtime_envelope`:

```python
return seal_runtime_envelope(
    envelope=envelope,
    tool_id="arifos.mind",
    output_options={"verbose": False, "debug": False}  # Clean output
)
```

---

## Validation

### Rule of Compression

> Can the operator understand the situation in 7 seconds?

If not, output is too chaotic.

### Checklist

- [ ] Default view fits on one screen
- [ ] No null fields visible in default view
- [ ] Same truth not repeated in multiple places
- [ ] Actionable next_step always present
- [ ] Error code is typed and searchable
- [ ] Debug data completely hidden by default

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Input size** | 8+ fields | 4 fields + options |
| **Output size** | 50+ fields | 10-15 fields |
| **Reading time** | 30+ seconds | 7 seconds |
| **Mental model** | Chaotic | Fixed blocks |
| **Operator clarity** | Poor | Excellent |
| **AI integration** | Hard | Easy |

**Result:** Human and AI agents can both use arifOS effectively.

---

*DITEMPA BUKAN DIBERI* 🔥
