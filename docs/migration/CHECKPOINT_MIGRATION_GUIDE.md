# Migration Guide: /checkpoint Endpoint

**Version:** v52.5.1-SEAL
**Target Audience:** MCP Client Developers
**Migration Complexity:** Low-Medium

---

## Overview

This guide helps you migrate from the legacy 5-tool Trinity architecture to the new unified `/checkpoint` endpoint.

### Why Migrate?

| Old Architecture | New Architecture |
|-----------------|------------------|
| 5 separate tool calls | 1 unified endpoint |
| Sequential execution | Parallel AGI∥ASI |
| Manual orchestration | Auto-orchestrated |
| 5x network overhead | 1x network call |
| Client-side complexity | Server-side simplicity |

---

## Quick Migration

### Before (5-Tool Chain)

```python
# OLD: Manual 5-tool orchestration
async def old_evaluate(task: str):
    # Step 1: Initialize
    init = await call_tool("000_init", {"action": "init", "query": task})
    session_id = init["session_id"]

    # Step 2: AGI Mind
    agi = await call_tool("agi_genius", {
        "action": "full",
        "query": task,
        "session_id": session_id
    })

    # Step 3: ASI Heart
    asi = await call_tool("asi_act", {
        "action": "full",
        "text": task,
        "session_id": session_id
    })

    # Step 4: APEX Judgment
    apex = await call_tool("apex_judge", {
        "action": "full",
        "query": task,
        "response": f"{agi['result']}, {asi['result']}",
        "session_id": session_id
    })

    # Step 5: Seal to Vault
    seal = await call_tool("vault_999", {
        "action": "seal",
        "session_id": session_id
    })

    return apex["verdict"], seal["ledger_entry"]
```

### After (Unified Checkpoint)

```python
# NEW: Single unified endpoint
async def new_evaluate(task: str):
    result = await call_endpoint("/checkpoint", {
        "task": task,
        "mode": "full"  # Runs all 5 stages internally
    })

    return result["verdict"], result["ledger_entry"]
```

---

## Endpoint Reference

### POST /checkpoint

**URL:** `https://arifos.arif-fazil.com/checkpoint`

**Headers:**
```http
Content-Type: application/json
Authorization: Bearer <api_key>  # Optional for public tier
```

**Request Body:**

```json
{
  "task": "Explain quantum computing in simple terms",
  "mode": "full",           // "full" | "quick" | "audit_only"
  "context": {              // Optional
    "history": [],          // Previous messages
    "user_id": "user_123",  // For personalization
    "urgency": "normal"     // "low" | "normal" | "high"
  },
  "options": {              // Optional
    "parallel": true,       // Enable AGI∥ASI parallel (default: true)
    "skip_vault": false,    // Skip ledger entry (default: false)
    "verbose": false        // Include full metrics (default: false)
  }
}
```

**Response (Success):**

```json
{
  "verdict": "SEAL",
  "metrics": {
    "truth": 0.99,
    "clarity": 0.12,
    "peace_squared": 1.0,
    "kappa_r": 0.97,
    "omega_0": 0.04,
    "genius_index": 0.85,
    "c_dark": 0.08
  },
  "floors": {
    "passed": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"],
    "failed": [],
    "warnings": []
  },
  "engines": {
    "agi": {"status": "pass", "duration_ms": 45},
    "asi": {"status": "pass", "duration_ms": 52},
    "apex": {"status": "pass", "duration_ms": 23}
  },
  "ledger_entry": {
    "id": "ldg_a3f7b2c1d4e5",
    "hash": "sha256:9f86d08...",
    "timestamp": "2026-01-26T10:30:00Z",
    "cooling_layer": "L0"
  },
  "session_id": "sess_xyz789"
}
```

**Response (Floor Violation):**

```json
{
  "verdict": "VOID",
  "metrics": {
    "truth": 0.72,
    "clarity": -0.05,
    ...
  },
  "floors": {
    "passed": ["F1", "F3", "F5", "F6"],
    "failed": ["F2", "F4"],
    "warnings": []
  },
  "failure_reasons": [
    {"floor": "F2", "reason": "Truth below threshold (0.72 < 0.99)", "severity": "hard"},
    {"floor": "F4", "reason": "Negative entropy (confusion increased)", "severity": "hard"}
  ],
  "suggestions": [
    "Verify factual claims with primary sources",
    "Simplify explanation to reduce confusion"
  ]
}
```

---

## Mode Comparison

| Mode | What It Does | Use Case | Latency |
|------|--------------|----------|---------|
| `full` | All 5 stages + ledger seal | Production evaluation | ~150ms |
| `quick` | AGI+ASI parallel only | Real-time validation | ~80ms |
| `audit_only` | Read-only metrics | Monitoring/dashboards | ~30ms |

---

## Migration Patterns

### Pattern 1: Direct Replacement

Replace individual tool calls with single checkpoint:

```python
# Before
result = await call_tool("agi_genius", {"action": "sense", "query": task})

# After
result = await call_endpoint("/checkpoint", {
    "task": task,
    "mode": "quick",
    "options": {"parallel": false}  # If you need AGI-only
})
```

### Pattern 2: Gradual Migration

Keep old tools but add checkpoint for new features:

```python
async def hybrid_evaluate(task: str):
    # Use checkpoint for standard evaluation
    checkpoint = await call_endpoint("/checkpoint", {
        "task": task,
        "mode": "full"
    })

    # Fall back to individual tools only if needed
    if checkpoint["verdict"] == "PARTIAL" and needs_custom_handling:
        # Custom AGI call for specific floor
        agi = await call_tool("agi_genius", {
            "action": "think",
            "query": task
        })
        return custom_merge(checkpoint, agi)

    return checkpoint
```

### Pattern 3: Webhook Integration

For async/event-driven systems:

```python
# Register webhook for verdicts
await call_endpoint("/checkpoint/webhook", {
    "url": "https://your-app.com/webhook/verdict",
    "events": ["VOID", "888_HOLD"],  # Only notify on failures
    "secret": "webhook_secret_123"
})

# Normal checkpoint call
result = await call_endpoint("/checkpoint", {
    "task": task,
    "mode": "full",
    "webhook": true  # Enable async notification
})
```

---

## Error Handling Migration

### Before (Multiple Error Points)

```python
try:
    init = await call_tool("000_init", {...})
except InitError:
    handle_init_error()

try:
    agi = await call_tool("agi_genius", {...})
except AGIError:
    handle_agi_error()

try:
    asi = await call_tool("asi_act", {...})
except ASIError:
    handle_asi_error()

# ... and so on for each tool
```

### After (Unified Error Handling)

```python
try:
    result = await call_endpoint("/checkpoint", {...})

    if result["verdict"] == "VOID":
        handle_floor_violation(result["failure_reasons"])
    elif result["verdict"] == "888_HOLD":
        await request_human_confirmation(result)
    elif result["verdict"] == "PARTIAL":
        log_warning(result["floors"]["warnings"])
        proceed_with_caution(result)
    else:
        # SEAL - all good
        process_response(result)

except CheckpointError as e:
    # Single error handler
    if e.is_retryable:
        await retry_with_backoff()
    else:
        escalate_to_human(e)
```

---

## SDK Support

### Python SDK

```python
from arifos import ArifOSClient

client = ArifOSClient(api_key="your_key")

# Simple evaluation
result = client.checkpoint("Explain quantum computing")

# With options
result = client.checkpoint(
    task="Analyze this code for security issues",
    mode="full",
    parallel=True,
    verbose=True
)

print(f"Verdict: {result.verdict}")
print(f"Truth: {result.metrics.truth}")
```

### TypeScript SDK

```typescript
import { ArifOS } from '@arifos/sdk';

const client = new ArifOS({ apiKey: 'your_key' });

// Async/await
const result = await client.checkpoint({
  task: 'Explain quantum computing',
  mode: 'full'
});

console.log(`Verdict: ${result.verdict}`);
console.log(`Floors passed: ${result.floors.passed.join(', ')}`);
```

### cURL

```bash
curl -X POST https://arifos.arif-fazil.com/checkpoint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "task": "Explain quantum computing in simple terms",
    "mode": "full"
  }'
```

---

## Feature Comparison Matrix

| Feature | 5-Tool (Old) | /checkpoint (New) |
|---------|-------------|-------------------|
| Single request | ❌ | ✅ |
| Parallel AGI∥ASI | ❌ Manual | ✅ Auto |
| Automatic retry | ❌ | ✅ |
| Ledger integration | Manual call | Built-in |
| WebSocket streaming | ❌ | ✅ |
| Webhook support | ❌ | ✅ |
| Rate limiting | Per-tool | Unified |
| Caching | ❌ | ✅ Semantic |
| OpenTelemetry | Manual | Built-in |

---

## Breaking Changes

### Removed Parameters

| Old Parameter | Migration Path |
|--------------|----------------|
| `session_id` (manual) | Auto-generated, returned in response |
| `action: "gate"` | Use `mode: "audit_only"` |
| `action: "reset"` | Use `/session/reset` endpoint |

### Changed Behavior

1. **Session Management**: Sessions are now auto-created. No need for explicit `000_init` call.

2. **Verdict Values**: `SABAR` now includes Phoenix cooling info:
   ```json
   {
     "verdict": "SABAR",
     "cooling": {
       "layer": "L2",
       "hours_remaining": 48,
       "reason": "High-stakes decision requires 72h cooling"
     }
   }
   ```

3. **Metrics Format**: All metrics now include confidence intervals:
   ```json
   {
     "truth": 0.99,
     "truth_ci": [0.97, 1.00]
   }
   ```

---

## Backward Compatibility

The old 5-tool endpoints remain available until **v54.0** (estimated Q3 2026):

```python
# These still work but are deprecated
await call_tool("000_init", {...})      # Deprecated
await call_tool("agi_genius", {...})    # Deprecated
await call_tool("asi_act", {...})       # Deprecated
await call_tool("apex_judge", {...})    # Deprecated
await call_tool("vault_999", {...})     # Deprecated
```

**Deprecation Timeline:**
- **v52.x**: Both APIs available, old API logs deprecation warnings
- **v53.x**: Old API requires `legacy=true` flag
- **v54.0**: Old API removed

---

## Migration Checklist

- [ ] Update API endpoint from individual tools to `/checkpoint`
- [ ] Remove manual session management (auto-handled)
- [ ] Update error handling to unified pattern
- [ ] Replace parallel tool calls with single checkpoint call
- [ ] Update response parsing for new format
- [ ] Enable verbose mode for debugging during migration
- [ ] Test with `mode: "audit_only"` before production
- [ ] Update monitoring dashboards for new metrics format
- [ ] Remove deprecated tool imports from codebase

---

## Support

- **Documentation:** https://arifos.arif-fazil.com/docs
- **API Status:** https://arifos.arif-fazil.com/status
- **Issues:** https://github.com/ariffazil/arifOS/issues

---

**Constitutional Authority:** This migration guide is SEALED under v52.5.1 governance.
