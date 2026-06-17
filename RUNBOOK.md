# RUNBOOK.md — arifOS Federation Operations

> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil)  
> **Scope:** Operational commands for the arifOS federation on VPS `af-forge`  > **Motto:** DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

---

## Quick reference

| Task | Command |
|------|---------|
| Verify federation reality | `cd /root/arifOS && make reality` |
| Check kernel health | `curl -s http://localhost:8088/health \| python3 -m json.tool` |
| Restart arifOS | `sudo systemctl restart arifos.service` |
| Restart all organs | See §6 "Full federation restart" |
| View organ logs | `journalctl -u arifos.service -f` |
| Check VAULT999 | `python scripts/vault999_status.py` |
| Security audit | `make security-audit` |

---

## 1. Health checks

### 1.1 Single-organ health

```bash
# arifOS
curl -s http://localhost:8088/health | python3 -m json.tool

# GEOX
curl -s http://localhost:8081/health | python3 -m json.tool

# WEALTH
curl -s http://localhost:18082/health | python3 -m json.tool

# WELL
curl -s http://localhost:18083/health | python3 -m json.tool

# AAA
curl -s http://localhost:3001/health | python3 -m json.tool

# A-FORGE
curl -s http://localhost:7071/health | python3 -m json.tool
```

### 1.2 Full federation reality probe

```bash
cd /root/arifOS
make reality
```

Outputs:
- `FEDERATION_REALITY_SNAPSHOT.md`
- `var/reality/federation_reality_<timestamp>.json`

Verdicts:
- `GREEN` — all organs pass.
- `GREEN_WITH_GAPS` — organs reachable but known gaps exist (normal).
- `RED` — at least one organ unreachable.

---

## 2. Service management

### 2.1 List all federation services

```bash
systemctl is-active arifos arifosd geox-mcp wealth-organ well aaa-a2a a-forge \
  openclaw-gateway vault999-api vault999-writer cloudflared nats-server
```

### 2.2 Restart a single organ

```bash
sudo systemctl restart arifos.service
sudo systemctl restart geox-mcp.service
sudo systemctl restart wealth-organ.service
sudo systemctl restart well.service
sudo systemctl restart aaa-a2a.service
sudo systemctl restart a-forge.service
```

### 2.3 Full federation restart (888_HOLD class)

Requires Arif approval. Use only during planned maintenance or recovery.

```bash
sudo systemctl restart arifos arifosd geox-mcp wealth-organ well aaa-a2a a-forge \
  openclaw-gateway vault999-api vault999-writer nats-server cloudflared
```

After restart, verify:

```bash
make reality
```

### 2.4 Data services (Docker)

```bash
# List
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

# Restart a data service
docker restart postgres redis qdrant falkordb temporal

# Check logs
docker logs --tail 50 postgres
```

---

## 3. Diagnostics

### 3.1 Logs

```bash
# Live log for an organ
journalctl -u arifos.service -f

# Last 100 lines across all federation services
journalctl -u arifos -u arifosd -u geox-mcp -u wealth-organ -u well \
  -u aaa-a2a -u a-forge --no-pager -n 100
```

### 3.2 Port check

```bash
ss -tlnp | grep -E ':(8088|8081|18082|18083|3001|7071|4222|5432|6333|6379|6380|7233)'
```

### 3.3 Resource check

```bash
free -h
df -h
uptime
```

### 3.4 MCP tool surface check

```bash
# arifOS
curl -s -X POST http://localhost:8088/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' > /dev/null

curl -s -X POST http://localhost:8088/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | \
  python3 -c 'import sys,json; d=json.load(sys.stdin); print("tools:", len(d.get("result",{}).get("tools",[])))'
```

---

## 4. VAULT999

### 4.1 Check seal chain status

```bash
cd /root/arifOS
python scripts/vault999_status.py
```

### 4.2 Replay reality ledger

```bash
cd /root/arifOS
make reality-replay
```

---

## 5. Security / audit

```bash
# Full security audit (non-blocking)
make security-audit

# Source-of-truth check
make sot-check

# Constitutional benchmark
make constitutional-benchmark
```

---

## 6. Common incidents

### 6.1 One organ shows DEGRADED in `make reality`

1. Check health endpoint directly.
2. Check logs: `journalctl -u <service> -n 50 --no-pager`.
3. Restart service if needed.
4. Re-run `make reality`.

### 6.2 WELL reports `INSUFFICIENT_DATA`

This is expected when live biometric telemetry is stale.
Do **not** fake freshness. WELL is REFLECT_ONLY and degrades safely.

To refresh:

```bash
# If a cron or autosleeper exists, run it manually or wait for next cycle.
cd /root/WELL
python well_autosleeper.py  # if present
```

### 6.3 arifOS tool count mismatch (39 vs 13)

The probe currently reports all registered tools including aliases.
This is a known registry-truth gap (GAP-003 continuation).
Canonical count should be verified against `arifOS/TOOL_MANIFEST.json`.

### 6.4 A-FORGE MCP 406 / session required

A-FORGE uses streamable HTTP and may require a session ID.
For read-only health checks, use `/health`.
For tool listing, use the metadata endpoint:

```bash
curl -s http://localhost:7071/mcp
```

---

## 7. Escalation matrix

| Situation | Action |
|-----------|--------|
| Single service down | Restart, re-run `make reality` — autonomous. |
| Multiple organs RED | Alert 888 (Arif), begin incident log. |
| Secret exposure | 888_HOLD immediately, rotate keys. |
| `git push --force` | 888_HOLD — never autonomous. |
| VAULT999 chain break | 888_HOLD — do not attempt manual repair. |
| A-FORGE lease logic change | 888_HOLD — cross-repo authority change. |
| Caddy reload | 888_HOLD — production traffic impact. |

---

## 8. Useful file locations

| File | Purpose |
|------|---------|
| `/root/arifOS/CONTEXT.md` | Live machine + service state |
| `/root/arifOS/FEDERATION_REALITY_SNAPSHOT.md` | Latest reality probe output |
| `/root/arifOS/docs/REALITY_SCORECARD.md` | Reality score baseline |
| `/root/arifOS/scripts/federation_reality_probe.py` | Probe script |
| `/root/arifOS/var/reality/` | Timestamped JSON truth artifacts |
| `/root/arifOS/Makefile` | `make reality`, `make health`, etc. |
| `/root/AGENTS.md` | Global federation rules |
| `/root/.secrets/INDEX.md` | Secret locations |

---

*DITEMPA BUKAN DIBERI — Operations are rehearsed, not improvised.*
