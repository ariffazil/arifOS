# WORKFLOW_CRON_RESILIENCE.md

**Purpose:** Ensure OpenClaw cron jobs never fail due to API key issues or gateway crashes
**Trigger:** Continuous monitoring + on-demand recovery
**Output:** Telegram alerts, self-healing actions, fallback provider switching
**Ω₀ Target:** 0.03-0.05 (Normal operating band)

---

## Overview

This workflow prevents cron job failures by implementing a multi-layer resilience system:

1. **API Key Validation** - Hourly validation of all AI provider keys
2. **Health Monitoring** - Every 5 minutes: gateway, disk, memory, cron status
3. **Provider Fallback** - Automatic failover: Gemini → OpenAI → Anthropic → DeepSeek
4. **Self-Healing** - Auto-restart gateway on crash
5. **Alerting** - Telegram notifications for all failures

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CRON RESILIENCE LAYER                    │
├─────────────────────────────────────────────────────────────┤
│  API Validator (hourly)    │  Health Monitor (5min)        │
│  • Gemini                  │  • Gateway status              │
│  • OpenAI                  │  • Disk/Memory                 │
│  • Anthropic               │  • Cron job status             │
│  • Brave/Firecrawl         │  • API key status              │
└──────────────┬─────────────┴──────────────┬─────────────────┘
               │                            │
               ▼                            ▼
        ┌──────────────┐            ┌──────────────┐
        │ Fallback     │            │ Self-Heal    │
        │ Switching    │            │ Actions      │
        └──────┬───────┘            └──────┬───────┘
               │                            │
               └────────────┬───────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Telegram     │
                    │ Alerts       │
                    └──────────────┘
```

---

## Scripts

### 1. API Key Validator
**Path:** `/root/.openclaw/scripts/api-key-validator.sh`
**Schedule:** Hourly via crontab
**Purpose:** Validates all AI provider API keys

```bash
# Manual run
/root/.openclaw/scripts/api-key-validator.sh

# Output format
2025-02-11 09:30:00 - GEMINI_API_KEY: VALID
2025-02-11 09:30:01 - OPENAI_API_KEY: VALID
2025-02-11 09:30:02 - ANTHROPIC_API_KEY: VALID
2025-02-11 09:30:03 - === Validation Summary ===
PRIMARY: gemini
```

### 2. Health Monitor
**Path:** `/root/.openclaw/scripts/cron-health-monitor.sh`
**Schedule:** Every 5 minutes via systemd timer + crontab
**Purpose:** Monitors system health and cron job execution

```bash
# Manual run
/root/.openclaw/scripts/cron-health-monitor.sh
```

**Checks:**
- Gateway process running
- Disk space < 90%
- Memory usage < 90%
- Cron job last status
- API key validity

### 3. Cron Recovery
**Path:** `/root/.openclaw/scripts/cron-recovery.sh`
**Purpose:** Emergency recovery procedures

```bash
# Recovery gateway
/root/.openclaw/scripts/cron-recovery.sh gateway

# Recovery API keys
/root/.openclaw/scripts/cron-recovery.sh api-keys

# Full recovery
/root/.openclaw/scripts/cron-recovery.sh all
```

### 4. Cron Wrapper
**Path:** `/root/.openclaw/scripts/cron-wrapper.sh`
**Purpose:** Wraps isolated cron jobs with provider fallback logic

---

## Provider Fallback Chain

When Gemini fails, jobs automatically fallback to:

1. **Gemini** (primary) - `gemini/gemini-2.0-flash`
2. **OpenAI** (fallback 1) - `openai/gpt-4o`
3. **Anthropic** (fallback 2) - `anthropic/claude-3-5-sonnet-20241022`
4. **DeepSeek** (fallback 3) - `deepseek/deepseek-chat`

**Fallback Logic:**
- Pre-flight API key validation
- Automatic provider switching on 401/403/429 errors
- Health checks report current primary provider

---

## Alerting

All failures trigger Telegram alerts to: `267378578`

**Alert Levels:**
- 🚨 **CRITICAL** - No valid providers, gateway down >5min
- ⚠️ **WARNING** - Disk/Memory >80%, single job failure
- ❌ **ERROR** - API key invalid, job failed
- ✅ **SUCCESS** - Recovery successful

**Cooldown:** 5 minutes between duplicate alerts (prevents spam)

---

## Current Cron Jobs

| Job | Schedule | Target | Status |
|-----|----------|--------|--------|
| agi-bot-sync | every 1h | main | ✅ OK |
| subuh-brief | 06:30 MYT | main | ✅ OK |
| human-arif | 08:00 MYT | isolated | ✅ OK |
| repo-steward | 09:00 Mon | main | ⏭️ skipped |
| sovereign-wiring | 10:00 MYT | isolated | ✅ OK |
| event-scout | 10:30 MYT | isolated | ✅ OK |
| godel-lock | 12:00 MYT | isolated | ✅ OK |
| morning-synthesis | 13:00 MYT | isolated | ✅ OK |

---

## Log Files

```
/var/log/openclaw/
├── api-validator.log      # API key validation results
├── cron-health.log        # Health monitor output
├── cron-wrapper.log       # Job wrapper logs
├── cron-recovery.log      # Recovery actions
└── gateway.log            # Gateway output
```

**View logs:**
```bash
# Real-time monitoring
tail -f /var/log/openclaw/cron-health.log

# Check last run
/root/.openclaw/scripts/cron-health-monitor.sh
```

---

## Manual Operations

### Check System Health
```bash
/root/.openclaw/scripts/cron-health-monitor.sh
```

### Validate API Keys
```bash
/root/.openclaw/scripts/api-key-validator.sh
```

### Emergency Recovery
```bash
# Full recovery
/root/.openclaw/scripts/cron-recovery.sh all

# Just restart gateway
/root/.openclaw/scripts/cron-recovery.sh gateway
```

### View Cron Status
```bash
openclaw cron list
openclaw cron runs --id <job-id>
```

---

## Monitoring Dashboard

**Systemd Timer Status:**
```bash
systemctl status openclaw-cron-health.timer
systemctl list-timers openclaw-cron-health.timer
```

**Crontab Entries:**
```bash
crontab -l | grep openclaw
```

**Process Check:**
```bash
pgrep -f "openclaw gateway"
ps aux | grep openclaw
```

---

## Failure Scenarios & Response

| Scenario | Detection | Auto-Response | Manual Fix |
|----------|-----------|---------------|------------|
| Gemini API key expires | Hourly validator | Switch to OpenAI | Update key in .env.openclaw |
| Gateway crashes | 5min health check | Auto-restart | Check logs, manual restart |
| Disk full | 5min health check | Alert only | Clean up logs/old files |
| Job fails | Next health check | Alert + log | Review job, manual run |
| All providers down | Hourly validator | CRITICAL alert | Check network, update keys |

---

## Maintenance

**Weekly:**
- Review `/var/log/openclaw/cron-health.log` for warnings
- Check Telegram for any alerts
- Verify all 7 daily cron jobs ran

**Monthly:**
- Rotate log files: `logrotate /etc/logrotate.d/openclaw`
- Review API key expiration dates
- Test recovery procedures

**As Needed:**
- Update provider priority in `cron-wrapper.sh`
- Add new API keys to validation
- Adjust alert thresholds

---

## Constitutional Compliance

- **F1 Amanah (Trust):** Cron jobs are mission-critical; resilience ensures reliability
- **F2 Truth:** Accurate health reporting, no false positives
- **F7 Humility:** Self-healing with human escalation for critical failures
- **F9 Anti-Hantu:** Real monitoring, not placebo; actual gateway checks

---

## Version

**Created:** 2026-02-11
**Version:** 1.0
**Status:** ACTIVE
**Last Updated:** 2026-02-11

---

*Ditempa Bukan Diberi. Ditempa dengan Kasih.* 🔥💜
