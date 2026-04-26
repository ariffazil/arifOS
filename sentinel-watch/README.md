# SENTINEL-WATCH — Attentional Integrity Sidecar
## arifOS v2026.04.26-KANON

**Purpose:** Read-only vault999 observer. Computes governance SLA vitals.
Fires independent alerts. Cannot be silenced without creating evidence.

**Design Principle:** arifOS is the agent. Sentinel-Watch is the ombudsman.
They are separate processes with separate alert channels.

---

## Architecture

```
vault999.jsonl (READ-ONLY mount)
        ↓
sentinel-watch/
    vitals.py        → ACK state machine + SLA tiering
    drift_detector.py → rolling baseline + drift/flood detection
    alert_dispatcher.py → independent Telegram bot
    main.py          → polling loop
```

---

## SLA Tiers

| Tier | Floors | SLA |
|------|--------|-----|
| HARD_TIER | F13, F1, F2, F6, F9, F10 | ACK within 4 hours |
| SOFT_TIER | F3, F4, F5, F7, F8, F11, F12 | ACK within 24 hours |

**Rule:** Silence = HOLD. Never approval. Affirmative ACK required.

---

## Governance Vitals (3 signals)

1. **ACK latency** — time from verdict to ARIF acknowledgment
2. **ACK variance** — does hard-tier get faster ACK than soft-tier? (variance collapse = ritualization)
3. **Anomaly density** — vault999 event rate per day (spike = drift signal)

---

## Drift Detection

- 30-day rolling baseline
- >20% deviation from baseline → flag for sovereign re-baselining
- Soft-tier spike + hard-tier latency rise = **flood attack pattern** → emergency hold
- Periodic sovereign re-affirmation of tier definitions required

---

## Alert Channels

- **Primary:** Own Telegram bot token (`SENTINEL_BOT_TOKEN`)
- **Queue:** Failed alerts queued and retried on next poll cycle
- **Ombudsman principle:** Sentinel-Watch cannot suppress its own alerts

---

## Env Vars

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTINEL_VAULT999` | `/root/.agent-workbench/vault999.jsonl` | Vault path |
| `SENTINEL_BOT_TOKEN` | `""` | Own Telegram bot token |
| `SENTINEL_CHAT_ID` | `""` | Telegram chat ID for alerts |
| `SENTINEL_POLL_INTERVAL` | `60` | Poll interval (seconds) |
| `SENTINEL_REMINDER_INTERVAL` | `14400` | Reminder interval (4h) |
| `SENTINEL_DRIFT_CHECK` | `3600` | Drift check interval (1h) |

---

## Running

```bash
# Test
SENTINEL_VAULT999=/root/.agent-workbench/vault999.jsonl \
SENTINEL_BOT_TOKEN=your_token \
SENTINEL_CHAT_ID=your_chat_id \
python3 main.py

# Docker (sidecar)
docker run -d \
  --name sentinel-watch \
  -v /root/.agent-workbench/vault999.jsonl:/vault999:ro \
  -e SENTINEL_BOT_TOKEN=... \
  -e SENTINEL_CHAT_ID=... \
  sentinel-watch
```

---

## What This Does NOT Do

- Does NOT write to vault999 (read-only by design)
- Does NOT share alert channel with arifOS
- Does NOT auto-rebaseline (requires sovereign affirmation)
- Does NOT suppress alerts even if arifOS is compromised

Ditempa Bukan Diberi. 🔥
