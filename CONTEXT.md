# CONTEXT.md — arifOS Federation Live State

> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil)  
> **Scope:** Live machine + service state on VPS `af-forge` (72.62.71.199)  
> **Generated:** 2026-06-21T06:20 UTC by arifOS constitutional agent  
> **Next refresh:** Run `make reality` to regenerate this file and `FEDERATION_REALITY_SNAPSHOT.md`.

---

## 1. Current focus

The federation is in an **alpha-operational constitutional federation** state.
The immediate priority is converting *declared* operational status into
*observed* operational status via the new Federation Reality Probe.

Three active workstreams:

1. **Federation Reality Probe** — live (this commit). Raises reality score 64 → 70–73.
2. **Dream-engine Phase 2** — counterfactual rehearsal prototype built; deployment gated on A-FORGE kernel-issued leases.
3. **MCP internalization / P0 cleanup** — duplicate local-wrapper MCPs identified, pending cleanup.

---

## 2. Federation organ status

| Organ | Role | Localhost | Public | Tools (live/registered) | Verdict |
|-------|------|-----------|--------|-------------------------|---------|
| arifOS | constitutional_kernel | ✅ | ✅ | 0 / 57 | DEGRADED |
| GEOX | earth_evidence | ✅ | ✅ | 40 / 40 | PASS |
| WEALTH | capital_compute | ✅ | ✅ | 24 / 54 | PASS |
| WELL | human_readiness_reflect_only | ✅ | ✅ | 15 / 18 | DEGRADED |
| AAA | cockpit_a2a | ✅ | ✅ | — | PASS |
| A-FORGE | governed_execution | ✅ | — | 77 / 77 | PASS |
| VAULT999 | immutable_ledger | ✅ | — | 7 / 7 | PASS |

**Overall verdict:** `DEGRADED`  
**Reality score:** 58 / 100  
**Maturity:** Level 4.2 / 7

### Verdict notes

- **arifOS DEGRADED**: `tools/list` crawl returns 0 tools — `FederationRegistry._static_tools` missing (fixed 2026-06-21). 57 tools registered in `tool_registry.json`. 12 divergent ActionClass enums across codebase create permission-model fragmentation.
- **WEALTH PASS**: 24 live tools per MCP attestation (vs 54 declared — likely hidden aliases not counted). Attestation verified 2026-06-21.
- **WELL DEGRADED**: 15 live tools. Freshness `expired`, `truth_status=INSUFFICIENT_DATA`. Live biometric input stale.
- **A-FORGE PASS**: 77 tools on MCP:7072, healthy. No public HTTPS ingress configured.

---

## 3. Known gaps

| ID | Severity | Domain | Description |
|----|----------|--------|-------------|
| GAP-001 | high | A-FORGE | A-FORGE lease gate is self-issued; must become kernel-issued. |
| GAP-002 | medium | WELL | WELL live human-state telemetry is stale / INSUFFICIENT_DATA. |
| GAP-003 | medium | arifOS | arifOS CONTEXT.md and RUNBOOK.md missing/incomplete. || GAP-004 | low | A-FORGE | A-FORGE public HTTPS ingress not configured. |

Highest-impact next step: **GAP-001** (kernel-issued leases). Blocks safe autonomous execution and the dream-engine Phase 2 timer deployment.

---

## 4. Machine state

### Host

| Metric | Value |
|--------|-------|
| Host | VPS af-forge (72.62.71.199) |
| OS | Linux |
| Uptime | 6 days, 2h43m |
| Load average | 18.05, 19.26, 14.62 |
| Disk / | 387G total, 160G used (42%), 228G free |
| Memory pressure | High — opencode + Kimi Code + ollama dominant |

### Top processes by memory

| Command | RSS |
|---------|-----|
| opencode | ~1.1 GB |
| ollama serve | ~1.0 GB |
| arifOS kernel | ~676 MB |
| hermes gateway | ~474 MB |
| openclaw gateway | ~393 MB |

---

## 5. Service topology

### Federation organs (systemd)

| Service | Unit | Port | Status |
|---------|------|------|--------|
| arifOS | arifos.service | 8088 | active |
| arifosd | arifosd.service | 18081 | active |
| GEOX | geox-mcp.service | 8081 | active |
| WEALTH | wealth-organ.service | 18082 | active |
| WELL | well.service | 18083 | active |
| AAA | aaa-a2a.service | 3001 | active |
| A-FORGE | a-forge.service | 7071 | active |
| OpenClaw | openclaw-gateway.service | 18789 | active |
| VAULT999 API | vault999-api.service | 8100 | active |
| VAULT999 Writer | vault999-writer.service | 5001 | active |
| Cloudflare Tunnel | cloudflared.service | — | active |
| NATS | nats-server.service | 4222 | active |

### Data / supporting services (Docker)

| Container | Status | Ports |
|-----------|--------|-------|
| postgres | Up 6 days (healthy) | 127.0.0.1:5432 |
| redis | Up 2 days | 127.0.0.1:6379 |
| qdrant | Up 6 days (healthy) | 127.0.0.1:6333-6334 |
| falkordb | Up 6 days (healthy) | 127.0.0.1:6380 |
| temporal | Up 3 days (healthy) | 127.0.0.1:7233 |
| temporal-ui | Up 6 days (healthy) | 127.0.0.1:8233 |
| graphiti-mcp | Up 2 days (healthy) | 127.0.0.1:8000 |
| loki | Up 6 days (healthy) | 127.0.0.1:3100 |
| promtail | Up 6 days (healthy) | 127.0.0.1:9080 |

### Observability

| Service | Port | Status |
|---------|------|--------|
| Prometheus | 9090 | active |
| Grafana | 3000 | active |
| Netdata | 19999 | active |

---

## 6. Network listeners

Key ports observed live:

| Port | Process | Purpose |
|------|---------|---------|
| 8088 | arifOS python | Constitutional kernel MCP |
| 8081 | GEOX python | Earth intelligence MCP |
| 18082 | WEALTH python | Capital intelligence MCP |
| 18083 | WELL python | Human readiness MCP |
| 3001 | AAA node | A2A gateway / cockpit |
| 7071 | A-FORGE node | Governed execution shell |
| 4222 | nats-server | Governance event bus |
| 5432 | postgres docker | Primary database |
| 6333 | qdrant docker | Vector database |
| 6379 | redis docker | Session/cache |
| 6380 | falkordb docker | Graph database |
| 7233 | temporal docker | Workflow engine |
| 11434 | ollama | Local embeddings |
| 8931 | playwright-mcp | Browser automation |
| 9090 | prometheus | Metrics |

---

## 7. Recent events

- **2026-06-16** — Federation Reality Probe added (`make reality`).
- **2026-06-16** — Dream-engine Phase 2 counterfactual rehearsal prototype built.
- **2026-06-16** — Fixed `consolidate.py` Supabase column drift and `entropy_controller.py` R6 vault string guard.
- **2026-06-14** — MCP Gate v0 deployed; 25/25 benchmarks pass.
- **2026-06-14** — Steel Security Layer active (Trivy, Semgrep, Ruff, Gitleaks).

---

## 8. Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-16 | Build reality probe before A-FORGE lease fix | Lower risk, faster score gain, surfaces real gaps safely. |
| 2026-06-16 | Hold dream-engine Phase 2 timer deployment | Requires kernel-issued service identity/lease first. |
| 2026-06-16 | Keep WELL stale rather than fake freshness | F7 HUMILITY — never pretend fresh data. |
| 2026-06-16 | Fixed runtime test drift (`/ready`, `arif_evidence_fetch`, `arif_session_init`, A-RIF injection probe, vault-dir file-path guard) | Tests green; no functional behavior change, only test/code alignment. |

---

## 9. How to update this file

```bash
cd /root/arifOS
make reality
# Then regenerate CONTEXT.md manually or via future automation.
```

---

*DITEMPA BUKAN DIBERI — Context is observed, not assumed.*
