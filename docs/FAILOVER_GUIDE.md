# Multi-Provider Failover Guide

**Version:** v45Ω Patch C
**Status:** Production-Ready
**Zero-Break:** Disabled by default, opt-in via environment variable

---

## Overview

The **Multi-Provider Failover Orchestrator** provides automatic failover across multiple LLM providers (Claude, OpenAI, Gemini, SEA-LION) while maintaining full constitutional governance.

**Key Guarantee:** ALL responses flow through `888_JUDGE → APEX_PRIME`. Failover ONLY handles provider selection, never bypassing governance.

---

## Quick Start

### 1. Enable Failover

Add to your `.env` file:

```bash
# Enable multi-provider failover
ARIFOS_FAILOVER_ENABLED=true
ARIFOS_FAILOVER_PROVIDERS=claude_primary,openai_fallback,sealion_backup
```

### 2. Configure Providers

```bash
# Claude Sonnet 4.5 (Primary - Priority 0)
ARIFOS_FAILOVER_CLAUDE_PRIMARY_TYPE=claude
ARIFOS_FAILOVER_CLAUDE_PRIMARY_MODEL=claude-sonnet-4-5-20250929
ARIFOS_FAILOVER_CLAUDE_PRIMARY_API_KEY=$ANTHROPIC_API_KEY
ARIFOS_FAILOVER_CLAUDE_PRIMARY_PRIORITY=0
ARIFOS_FAILOVER_CLAUDE_PRIMARY_TIMEOUT=30.0
ARIFOS_FAILOVER_CLAUDE_PRIMARY_MAX_RETRIES=2

# OpenAI GPT-4o (Fallback - Priority 1)
ARIFOS_FAILOVER_OPENAI_FALLBACK_TYPE=openai
ARIFOS_FAILOVER_OPENAI_FALLBACK_MODEL=gpt-4o
ARIFOS_FAILOVER_OPENAI_FALLBACK_API_KEY=$OPENAI_API_KEY
ARIFOS_FAILOVER_OPENAI_FALLBACK_PRIORITY=1

# SEA-LION v4 (Backup - Priority 2)
ARIFOS_FAILOVER_SEALION_BACKUP_TYPE=sealion
ARIFOS_FAILOVER_SEALION_BACKUP_MODEL=aisingapore/Gemma-SEA-LION-v4-27B-IT
ARIFOS_FAILOVER_SEALION_BACKUP_API_KEY=$SEALION_API_KEY
ARIFOS_FAILOVER_SEALION_BACKUP_API_BASE=https://api.sea-lion.ai/v1
ARIFOS_FAILOVER_SEALION_BACKUP_PRIORITY=2
```

### 3. Run Pipeline

```python
from arifos_core.system.pipeline import Pipeline

pipeline = Pipeline()
result = pipeline.run("What is the capital of France?")

# Check if failover occurred
if result.state.failover_metadata:
    print(f"Provider used: {result.state.failover_metadata['provider']}")
    print(f"Failover occurred: {result.state.failover_metadata['fallback_occurred']}")
```

---

## Architecture

### Current Flow (Without Failover)

```
[333_REASON] llm_generate(prompt) → [Single Provider]
                                         ↓ (if fails, entire pipeline fails)
[888_JUDGE] APEX_PRIME → [999_SEAL]
```

### New Flow (With Failover)

```
[333_REASON] llm_generate(prompt, lane="SOFT")
                 ↓
    FailoverOrchestrator
         ↓
    Try Claude (primary) → Failed (429 rate limit)
         ↓
    Try OpenAI (fallback) → Success
         ↓
    Return response + metadata
         ↓
[888_JUDGE] APEX_PRIME (still executes - governance preserved)
         ↓
[999_SEAL] Return governed response
```

**Constitutional Guarantee:** The orchestrator is inserted BEFORE stage 888_JUDGE, so ALL responses (regardless of provider) flow through constitutional review.

---

## Configuration Reference

### Environment Variables

#### Global Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ARIFOS_FAILOVER_ENABLED` | Yes | `false` | Enable/disable failover (`true`/`false`) |
| `ARIFOS_FAILOVER_PROVIDERS` | Yes | — | Comma-separated list of provider names |
| `ARIFOS_FAILOVER_CIRCUIT_BREAKER_THRESHOLD` | No | `3` | Consecutive failures before circuit opens |
| `ARIFOS_FAILOVER_CIRCUIT_BREAKER_COOLDOWN` | No | `60` | Cooldown seconds before retry |

#### Per-Provider Settings

For each provider in `ARIFOS_FAILOVER_PROVIDERS`, configure:

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `ARIFOS_FAILOVER_{NAME}_TYPE` | Yes | `claude` | Provider type (`claude`, `openai`, `gemini`, `sealion`) |
| `ARIFOS_FAILOVER_{NAME}_MODEL` | Yes | `claude-sonnet-4-5-20250929` | Model identifier |
| `ARIFOS_FAILOVER_{NAME}_API_KEY` | Yes | `sk-...` | API key (use env var substitution) |
| `ARIFOS_FAILOVER_{NAME}_PRIORITY` | Yes | `0` | Priority (lower = higher priority, 0=primary) |
| `ARIFOS_FAILOVER_{NAME}_API_BASE` | No | `https://...` | Custom API base URL |
| `ARIFOS_FAILOVER_{NAME}_TIMEOUT` | No | `30.0` | Timeout in seconds |
| `ARIFOS_FAILOVER_{NAME}_MAX_RETRIES` | No | `2` | Max retries for transient errors |

**Note:** `{NAME}` should be UPPERCASE version of provider name from `ARIFOS_FAILOVER_PROVIDERS`.

---

## Failover Logic

### Decision Tree

1. **Load providers** sorted by priority (0=primary, 1=fallback, 2=backup)
2. **For each provider** (in priority order):
   - Check circuit breaker status (CLOSED/OPEN/HALF_OPEN)
   - If available, attempt generation
   - **On success**: Reset failures, close circuit, return result
   - **On failure**:
     - Classify error (RATE_LIMIT, TIMEOUT, API_ERROR, AUTH_ERROR)
     - Retry transient errors with exponential backoff
     - Skip non-retryable errors (AUTH_ERROR)
     - Update health tracker
     - Move to next provider
3. **If all providers exhausted**: Return VOID (fail-closed safety)

### Error Classification

| Error Type | Retryable? | Action |
|------------|------------|--------|
| `RATE_LIMIT` (429) | ✅ Yes | Retry with exponential backoff |
| `TIMEOUT` | ✅ Yes | Retry with backoff |
| `API_ERROR` (5xx) | ✅ Yes | Retry with backoff |
| `AUTH_ERROR` (401, 403) | ❌ No | Skip to next provider immediately |
| `INVALID_RESPONSE` | ❌ No | Skip to next provider immediately |

### Retry Strategy

- **Exponential Backoff:** 500ms → 1000ms → 2000ms (capped at 5000ms)
- **Max Retries:** Configurable per provider (default: 2)
- **Only retry transient errors** - never retry auth failures

### Circuit Breaker

Prevents hammering unhealthy providers (F5 Peace² floor):

- **CLOSED:** Provider healthy, requests allowed
- **OPEN:** Provider unhealthy after 3 consecutive failures, skip for 60s
- **HALF_OPEN:** After cooldown, allow ONE test attempt to check recovery

---

## Cooling Ledger Integration

All failover events are logged to the cooling ledger for audit trail.

### Normal Operation (No Failover)

```jsonl
{
  "job_id": "abc123",
  "verdict": "SEAL",
  "failover": {
    "provider": "claude_primary",
    "fallback_occurred": false,
    "attempt_count": 1,
    "total_latency_ms": 1234.5
  }
}
```

### Failover Event (Primary Failed, Fallback Succeeded)

```jsonl
{
  "job_id": "def456",
  "verdict": "SEAL",
  "failover": {
    "provider": "openai_fallback",
    "fallback_occurred": true,
    "attempt_count": 2,
    "total_latency_ms": 2567.8,
    "failures": [
      {
        "provider": "claude_primary",
        "failure_type": "RATE_LIMIT",
        "error": "429 Too Many Requests"
      }
    ]
  }
}
```

### Query Cooling Ledger

```bash
# Find all failover events
grep '"fallback_occurred": true' cooling_ledger/L1_cooling_ledger.jsonl

# Count by provider
jq -r '.failover.provider' cooling_ledger/L1_cooling_ledger.jsonl | sort | uniq -c

# Average latency with failover
jq -r 'select(.failover.fallback_occurred == true) | .failover.total_latency_ms' \
  cooling_ledger/L1_cooling_ledger.jsonl | awk '{sum+=$1; count++} END {print sum/count}'
```

---

## Constitutional Compliance

### Floors Preserved

All 9 constitutional floors apply regardless of failover:

- **F1 Amanah:** All provider switches logged (audit trail intact)
- **F2 Truth:** Orchestrator doesn't modify responses (pass-through)
- **F3 Tri-Witness:** All responses through APEX_PRIME verification
- **F4 ΔS (Clarity):** Provider metadata exposed in ledger
- **F5 Peace²:** Circuit breaker prevents hammering providers
- **F6 κᵣ (Empathy):** No change - governance layer enforces
- **F7 Ω₀ (Humility):** Provider status tracked (HEALTHY/DEGRADED/UNHEALTHY)
- **F8 G (Governed Intelligence):** ALL responses through 888_JUDGE
- **F9 C_dark (Anti-Hantu):** No change - governance layer enforces

### Governance Flow (No Bypass)

```
Failover Orchestrator → Response → 888_JUDGE → APEX_PRIME → 999_SEAL
                                        ↑
                                    MANDATORY
                                   (no bypass)
```

**CRITICAL:** The orchestrator ONLY selects which provider to call. The response is ALWAYS passed to `888_JUDGE` for constitutional review. Even if failover logic is perfect, governance is still enforced.

---

## Monitoring & Observability

### Enable Verbose Logging

```bash
export ARIFOS_VERBOSE=1
```

Logs will show:

```
[PIPELINE] Failover enabled with 3 providers
[FAILOVER] Trying provider: claude_primary (priority=0)
[FAILOVER] Provider claude_primary failed: 429 Too Many Requests
[FAILOVER] Retrying in 500ms... (attempt 1/2)
[FAILOVER] Provider claude_primary failed again: 429 Too Many Requests
[FAILOVER] Trying provider: openai_fallback (priority=1)
[FAILOVER] Provider openai_fallback succeeded (latency: 1234ms)
[FAILOVER] Failover complete - used: openai_fallback (total latency: 2567ms)
```

### Health Check Script

```bash
# Check provider health status
python -c "
from arifos_core.connectors.failover_orchestrator import load_failover_config_from_env

config = load_failover_config_from_env()
for p in config.providers:
    print(f'{p.name}: {p.status.value} (failures: {p.consecutive_failures})')
"
```

### Cooling Ledger Analysis

```bash
# Failover rate (last 100 requests)
tail -100 cooling_ledger/L1_cooling_ledger.jsonl | \
  jq -r '.failover.fallback_occurred' | \
  grep -c true

# Provider usage distribution
jq -r '.failover.provider' cooling_ledger/L1_cooling_ledger.jsonl | \
  sort | uniq -c | sort -nr
```

---

## Troubleshooting

### Failover Not Working

**Symptom:** Pipeline fails even though fallback providers configured.

**Check:**

1. Verify `ARIFOS_FAILOVER_ENABLED=true`
2. Check provider names match (case-sensitive)
3. Verify API keys are valid
4. Check logs: `grep FAILOVER logs/*.log`

### Circuit Breaker Stuck Open

**Symptom:** Provider never retried even after recovery.

**Solution:**

```python
from arifos_core.connectors.failover_orchestrator import ProviderHealthTracker

tracker = ProviderHealthTracker()
# Reset circuit manually (for debugging)
tracker.reset_all()
```

### All Providers Failing

**Symptom:** Pipeline returns VOID for all queries.

**Check:**

1. Verify API keys are valid (test with `curl`)
2. Check network connectivity
3. Review error logs for specific failure reasons
4. Test each provider individually (disable failover, test one at a time)

### Governance Not Applied

**Symptom:** Responses bypass constitutional review.

**THIS SHOULD NEVER HAPPEN.** If it does:

1. Check if `888_JUDGE` stage is skipped in logs
2. Verify pipeline integrity: `pytest tests/integration/test_failover_pipeline.py::test_pipeline_governance_not_bypassed -v`
3. Report as critical security bug (see [SECURITY.md](../SECURITY.md))

---

## Migration & Rollback

### Enabling Failover (Zero-Break)

Failover is **disabled by default**. To enable:

1. Add `.env` configuration (see Quick Start)
2. Test with: `python -m arifos_core.system.pipeline`
3. Run integration tests: `pytest tests/integration/test_failover_pipeline.py -v`
4. Deploy with monitoring: `tail -f cooling_ledger/L1_cooling_ledger.jsonl | grep FAILOVER`

**Verification:**

```bash
# Check failover is enabled
python -c "import os; print('Enabled' if os.getenv('ARIFOS_FAILOVER_ENABLED') == 'true' else 'Disabled')"

# Run single query and check ledger
python -m arifos_core.system.pipeline
tail -1 cooling_ledger/L1_cooling_ledger.jsonl | jq '.failover'
```

### Rollback (Immediate)

**Emergency disable:**

```bash
export ARIFOS_FAILOVER_ENABLED=false
# or
unset ARIFOS_FAILOVER_ENABLED
```

Pipeline will revert to single-provider mode instantly (existing behavior).

### Gradual Rollout

For production systems:

1. **Phase 1:** Enable for 10% of traffic (canary deployment)
2. **Phase 2:** Monitor failover rate and latency impact
3. **Phase 3:** Increase to 50% if metrics healthy
4. **Phase 4:** Full rollout after 7 days with <1% failover rate

**Canary Test:**

```python
import random
from arifos_core.system.pipeline import Pipeline

# 10% use failover
use_failover = random.random() < 0.10

if use_failover:
    os.environ["ARIFOS_FAILOVER_ENABLED"] = "true"
else:
    os.environ["ARIFOS_FAILOVER_ENABLED"] = "false"

pipeline = Pipeline()
# ... proceed normally
```

---

## Best Practices

### 1. Provider Selection

- **Primary:** Most reliable provider (e.g., Claude for reasoning, OpenAI for speed)
- **Fallback:** Balanced cost/performance (e.g., GPT-4o, Gemini)
- **Backup:** Cost-effective or specialized (e.g., SEA-LION for Southeast Asian languages)

### 2. Timeout Configuration

- **Primary:** Higher timeout (30-60s) for quality
- **Fallback:** Lower timeout (15-30s) for speed
- **Backup:** Lowest timeout (10-15s) to fail fast

### 3. Circuit Breaker Tuning

- **Default (3 failures, 60s cooldown):** Good for most cases
- **Aggressive (2 failures, 30s):** For critical low-latency systems
- **Conservative (5 failures, 120s):** For tolerant batch jobs

### 4. Cost Optimization

- **Primary:** Expensive model (Claude Opus, GPT-4o)
- **Fallback:** Mid-tier model (Claude Sonnet, GPT-4)
- **Backup:** Budget model (GPT-3.5, SEA-LION)

**Cost Tracking:**

```bash
# Estimate cost impact of failover
jq -r 'select(.failover.fallback_occurred == true) | .failover.provider' \
  cooling_ledger/L1_cooling_ledger.jsonl | sort | uniq -c
```

### 5. Monitoring Alerts

Set alerts for:

- **Failover rate >10%:** Primary provider may be unhealthy
- **Circuit breaker opens:** Provider down, investigate
- **All providers fail:** Critical outage, escalate immediately

---

## FAQ

### Q: Does failover increase latency?

**A:** Only when failover occurs. Normal operation has negligible overhead (<10ms). When failover happens, you pay the cost of failed attempts + backoff delays, but this is better than complete failure.

### Q: What happens if all providers fail?

**A:** Pipeline returns `VOID` verdict (fail-closed safety). Better no response than ungoverned response.

### Q: Can I use same provider with different models?

**A:** Yes! Example: GPT-4o (primary) → GPT-3.5-turbo (fallback).

```bash
ARIFOS_FAILOVER_PROVIDERS=gpt4,gpt35
ARIFOS_FAILOVER_GPT4_TYPE=openai
ARIFOS_FAILOVER_GPT4_MODEL=gpt-4o
ARIFOS_FAILOVER_GPT35_TYPE=openai
ARIFOS_FAILOVER_GPT35_MODEL=gpt-3.5-turbo
```

### Q: How do I test failover locally?

**A:** Use mock providers or intentionally misconfigure primary API key to force failover.

### Q: Does failover work with lane-aware governance (v45Ω)?

**A:** Yes! Lane metadata (PHATIC/SOFT/HARD/REFUSE) is preserved through failover. Different truth thresholds apply regardless of provider used.

### Q: Can I add custom providers?

**A:** Yes, but requires implementing adapter interface. See [arifos_core/adapters/](../arifos_core/adapters/) for examples.

---

## Support

- **Documentation:** [CLAUDE.md](../CLAUDE.md), [AGENTS.md](../AGENTS.md)
- **Security Issues:** [SECURITY.md](../SECURITY.md)
- **Contributing:** [CONTRIBUTING.md](../CONTRIBUTING.md)

**DITEMPA BUKAN DIBERI** — Forged, not given; governance must cool before it rules.
