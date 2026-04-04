# HEARTBEAT.md — arifOS_bot Autonomy Surface
**Version:** 2026.03.07-AUDIT-SEALED
**Mode:** Conservative — Health + Governance + Backup Sanity
**Floors in scope:** F1 (Reversibility), F2 (Truth), F4 (Clarity), F11 (Command Auth), F12 (Injection Defense)

---

## Principles

Every heartbeat action MUST be:
- **Read-only** — no config edits, no container restarts
- **Reversible** — logs only, proposals not executions
- **Internal** — only `arifosmcp_server`, `localhost`, Docker socket (no external HTTP)
- **Bounded** — if a check takes >10s, skip it and log `heartbeat_timeout`

---

## Task 1 — AGI Stack Health Probe (every heartbeat)

Run skill: `health-probe`

Checks:
- `curl -sf http://arifosmcp_server:8080/health` → `tools_loaded == 13`
- `docker inspect --format='{{.State.Health.Status}}' <container>` for all 12 containers
- `df / | awk 'NR==2{print $5}'` → alert if >80%
- `free -m | awk '/^Mem:/{print $7}'` → alert if available <2000 MiB

Log to `logs/audit.jsonl`:
```json
{"ts":"<ISO>","event":"health_probe","source":"heartbeat","arifos_tools":<n>,"disk_pct":"<X>%","ram_avail_mb":<n>,"agent":"arifOS_bot"}
```

If CRITICAL (tools<13 or disk>85% or RAM<1500MiB):
- Log `action_proposal` with recommended fix
- Send Telegram alert if `TELEGRAM_BOT_TOKEN` is set:
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=⚠️ arifOS_bot ALERT: [describe issue] — $(date)"
```

---

## Task 2 — Governance Floor Refresh (every 3rd heartbeat ≈ 90 min)

Run skill: `agentic-governance`

- Re-read `SPEC.md`, `AGENTS.md`, `SOUL.md`, `USER.md`
- Re-sync: 888_HOLD list, egress allowlist, sovereign preferences
- Call `arifos audit` via MCP bridge if arifOS is healthy

Log to `logs/audit.jsonl`:
```json
{"ts":"<ISO>","event":"governance_refresh","source":"heartbeat","floors":"F1-F13","drift_detected":false,"agent":"arifOS_bot"}
```

---

## Task 3 — Backup & Memory Sanity (every 4th heartbeat ≈ 2 hours)

```bash
# Read-only — check last commit time only
LAST_COMMIT=$(git -C ~/.openclaw/workspace log -1 --format='%ci' 2>/dev/null)
HOURS_AGO=$(( ($(date +%s) - $(git -C ~/.openclaw/workspace log -1 --format='%at' 2>/dev/null)) / 3600 ))

if [ "$HOURS_AGO" -gt 25 ]; then
  echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"backup_overdue\",\"hours_since_last\":${HOURS_AGO},\"agent\":\"arifOS_bot\"}" \
    >> ~/.openclaw/workspace/logs/audit.jsonl
fi

# Check today's memory file
TODAY=$(TZ='Asia/Kuala_Lumpur' date +%Y-%m-%d)
if [ ! -f ~/.openclaw/workspace/memory/${TODAY}.md ]; then
  echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"memory_missing_today\",\"date\":\"${TODAY}\",\"agent\":\"arifOS_bot\"}" \
    >> ~/.openclaw/workspace/logs/audit.jsonl
fi
```

**DO NOT** run `backup-to-github.sh` from heartbeat. That is cron-only (00:00 MYT).

---

## Task 4 — Model Vitality Check (every 8th heartbeat ≈ 4 hours)

```bash
# Lightweight: check Kimi provider is reachable
KIMI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://api.moonshot.cn/v1/models" \
  -H "Authorization: Bearer ${KIMI_API_KEY}" --max-time 5)

echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"model_vitality\",\"kimi_http\":${KIMI_STATUS},\"agent\":\"arifOS_bot\"}" \
  >> ~/.openclaw/workspace/logs/audit.jsonl
```

If Kimi returns 401 → expected (key issue), log but don't alert (Claude fallback active).
If Kimi returns 0 (timeout) → log `model_provider_unreachable`.

---

## 888_HOLD Boundaries (Heartbeat MUST NOT)

| Action | Why |
|--------|-----|
| `docker compose restart ...` | F11 — propose only |
| Edit `.env` or `openclaw.json` | F11 — config changes need human |
| Run `backup-to-github.sh` | Reserved for cron at 00:00 MYT |
| `curl` to non-allowlisted domains | F12 — egress policy |
| Kill or pause any process | F11 — propose, don't execute |

For any of the above, heartbeat MUST log `action_proposal` and wait for Arif's command.

---

## Telemetry Tag Format

Every heartbeat log entry:
```json
{
  "ts": "<ISO-8601-UTC>",
  "event": "<event_type>",
  "source": "heartbeat",
  "floors": ["F1","F2","F4","F11","F12"],
  "mode": "conservative",
  "agent": "arifOS_bot",
  "summary": "<short English description>"
}
```

---

*arifOS_bot heartbeat — DITEMPA BUKAN DIBERI*
