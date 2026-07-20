# 🌍 ATLAS333 — Evergreen Cognitive Geometry Registry

> **SOURCE OF TRUTH — ATLAS333 cognitive substrate (evergreen registry).**
> **Status:** LIVING DOCUMENT — never finished, always updated
> **Analogy:** Like geological mapping — the earth is never "done," neither is this
> **Owner:** ARIF (F13 SOVEREIGN)
> **Steward:** OpenCode (auto-updates on every session)
> **Last Updated:** 2026-07-19

---

## What This Is

The ATLAS333 is the cognitive geometry of arifOS. It answers:
- **WHERE** is the agent? (territory)
- **WHAT** kind of problem? (geometry)
- **HOW** deep to think? (depth)
- **WHICH** paradoxes are active? (tension)

It is NOT a tool. It is NOT a resource. It is the **map** that tools use to navigate.

---

## The Three Functions

```
Λ(text) → lane                    # Lambda: classify the query
Θ(lane) → (τ, κ, ρ)              # Theta: derive demand tensor
Φ(text) → GPV(lane, τ, κ, ρ)    # Phi: complete mapping
```

### Λ — Lane Classification

| Lane | Meaning | Query Types |
|------|---------|-------------|
| CRISIS | Immediate harm/risk | Emergency, safety, sovereignty breach |
| FACTUAL | Truth-seeking | Evidence, data, verification |
| SOCIAL | Human interaction | Conversation, relationship, culture |
| CARE | Well-being focus | Health, dignity, readiness |
| UNKNOWN | Unclassified | Default, requires more context |

### Θ — Demand Tensor

| Symbol | Name | Range | Meaning |
|--------|------|-------|---------|
| τ (tau) | Truth demand | 0.0–1.0 | How much truth precision needed |
| κ (kappa) | Care demand | 0.0–1.0 | How much dignity/human focus |
| ρ (rho) | Risk level | 0.0–1.0 | How dangerous is error |

### Φ — Complete Mapping

```python
Φ(text) → GPV(lane, τ, κ, ρ, paradox_axes, query_type)
```

---

## The 36 Paradoxes (Minimum Viable Self-Knowledge)

### Memory Paradoxes (1–11)

| ID | Paradox | Axis | Organ |
|----|---------|------|-------|
| 1 | Every retrieval is also a forgetting | RECOLLECTION_VS_DISCOVERY | Memory |
| 2 | What we choose to remember shapes what we forget | FORGETTING_VS_REMEMBERING | Memory |
| 3 | The map is not the territory, but we navigate by maps | HORIZON_VS_BLINDNESS | Memory |
| 4 | More data can mean less understanding | VASTNESS_VS_OPACITY | Memory |
| 5 | The hunger for knowledge must be disciplined | EPISTEMIC_HUNGER_VS_DISCIPLINE | Memory |
| 6 | Stability enables action but rigidity prevents adaptation | STABILITY_VS_RIGIDITY | Memory |
| 7 | Memory without context is noise | CONTEXT_VS_NOISE | Memory |
| 8 | Forgetting is necessary for learning | LEARNING_VS_FORGETTING | Memory |
| 9 | The archive shapes what is knowable | ARCHIVE_VS_DISCOVERY | Memory |
| 10 | Temporal distance changes meaning | TEMPORAL_VS_MEANING | Memory |
| 11 | What is preserved is what was valued | PRESERVATION_VS_BIAS | Memory |

### Mind Paradoxes (12–22)

| ID | Paradox | Axis | Organ |
|----|---------|------|-------|
| 12 | Every doubt is also a decision | DOUBT_VS_DECISION | Mind |
| 13 | Reasoning requires assumptions it cannot prove | GROUNDLESSNESS_VS_CERTAINTY | Mind |
| 14 | The tool that optimizes for one metric degrades others | OPTIMIZATION_VS_BALANCE | Mind |
| 15 | Understanding requires perspective, but perspective limits understanding | PERSPECTIVE_VS_LIMITATION | Mind |
| 16 | The more certain the claim, the less it teaches | CERTAINTY_VS_LEARNING | Mind |
| 17 | Every model is wrong, some are useful | UTILITY_VS_TRUTH | Mind |
| 18 | The observer changes what is observed | OBSERVER_VS_OBSERVED | Mind |
| 19 | Complexity resists simplification, but understanding requires it | SIMPLIFICATION_VS_FIDELITY | Mind |
| 20 | The question shapes the answer | QUESTION_VS_ANSWER | Mind |
| 21 | What is measurable is not always what matters | MEASUREMENT_VS_SIGNIFICANCE | Mind |
| 22 | The framework that explains everything explains nothing | EXPLANATION_VS_SPECIFICITY | Mind |

### Judge Paradoxes (23–33)

| ID | Paradox | Axis | Organ |
|----|---------|------|-------|
| 23 | Every verdict is also an incomplete justice | VERDICT_VS_JUSTICE | Judge |
| 24 | The rule that protects can also oppress | PROTECTION_VS_OPPRESSION | Judge |
| 25 | Authority requires legitimacy it cannot grant itself | AUTHORITY_VS_LEGITIMACY | Judge |
| 26 | The gate that prevents harm also prevents progress | GATE_VS_PROGRESS | Judge |
| 27 | Transparency enables accountability but also manipulation | TRANSPARENCY_VS_MANIPULATION | Judge |
| 28 | The constitution that never changes cannot adapt | CONSTITUTION_VS_ADAPTATION | Judge |
| 29 | Sovereignty requires the power to veto, but veto can block wisdom | SOVEREIGNTY_VS_WISDOM | Judge |
| 30 | Every audit trail can be forged, but forgery leaves traces | AUDIT_VS_FORGERY | Judge |
| 31 | The seal that makes permanent also makes irreversible | PERMANENCE_VS_REVERSIBILITY | Judge |
| 32 | The floor that protects dignity can also prevent truth | DIGNITY_VS_TRUTH | Judge |
| 33 | The system that governs itself cannot verify its own governance | SELF_GOVERNANCE_VS_VERIFICATION | Judge |
| 34 | Root filesystem access bypasses all MCP governance — the forge is the real sovereign | ROOT_VS_KERNEL | Contour |
| 35 | Positive outcomes ≠ closed case — success can mask unresolved failure modes | POSITIVE_VS_CLOSED | Judge |
| 36 | Observation creates exposure — you cannot fix what you cannot see, but reading secrets creates attack surface | OBSERVABILITY_VS_EXPOSURE | Memory × Judge |

---

## TEARFRAME Thresholds

| Metric | Formula | Threshold | Floor |
|--------|---------|-----------|-------|
| TRM (Truth-Reliability) | `f2_truth` | ≥ 0.94 | F2 |
| ECHO (Evidence Coherence) | `∛(f3 × f2 × f13)` | ≥ 0.87 | F2, F3, F13 |
| RASA (Resonance-Alignment) | `∛(f6 × f5 × f13)` | ≥ 0.85 | F5, F6, F13 |

---

## GPV → Paradox Activation Rules

| GPV Condition | Paradox IDs Activated |
|---------------|----------------------|
| τ high (≥0.8) | 5, 12, 16, 23 |
| ρ high (≥0.7) | 6, 14, 24, 26, 31, 34 |
| κ high (≥0.7) | 7, 15, 25, 32 |
| lane=CRISIS | 24, 26, 29, 31, 34 |
| lane=FACTUAL | 1, 4, 13, 17, 21, 35 |
| lane=SOCIAL | 2, 8, 10, 20 |
| lane=CARE | 3, 9, 11, 22, 32 |
| query_type=EXPLORATORY | 3, 5, 15, 18, 19 |
| query_type=COMPARATIVE | 14, 17, 21, 28 |

---

## File Locations (Code Anchors)

| Component | File | Line |
|-----------|------|------|
| GPV type | `core/shared/types.py` | class GPV |
| Φ function | `core/shared/atlas.py` | def phi() |
| PARADOX_GPV_MAP | `core/shared/atlas.py` | n = {...} |
| FloorScores | `core/shared/types.py:403` | class FloorScores |
| trm/echo/rasa | `core/shared/types.py:460-490` | @property |
| paradox_quotes.py | `constitution/paradox_quotes.py` | PARADOX_QUOTE_MAP |
| paradox_gate.py | `core/enforcement/paradox_gate.py:281` | evaluate_paradox_gate_gpv() |
| A2A card | `AAA/a2a-server/agent-cards/atlas333.json` | agent-card |

---

## Update Protocol

This document is updated when:
1. A new paradox is discovered (rare — requires F13 ratification)
2. A TEARFRAME threshold is recalibrated (requires evidence)
3. GPV activation rules change (requires audit)
4. A new organ is added to the federation
5. The cognitive geometry evolves through use

**NEVER delete a paradox. Only add or refine.**
**NEVER lower a threshold without evidence.**
**NEVER remove an activation rule without audit.**

---

## The One Sentence

> The 35 paradoxes are the minimum viable self-knowledge — they prevent the agent's confidence from becoming noise, and its knowledge from becoming certainty.

---

*Like geological mapping — the earth is never "done." Neither is this.*
*DITEMPA BUKAN DIBERI*


---

---

## PARADOX 34 — ROOT OUTRUNS KERNEL · 2026-07-17

**Domain:** Judge (23-33+1) · **Zone:** Governance Sovereignty

**Statement:** On a single VPS, root filesystem access bypasses all arifOS MCP governance. arif_judge SEAL is advisory when the executor has root. The forge is the real sovereign, not the constitution.

**Trigger event:** 2026-07-17 P0-P2 sprint. PermitUserEnvironment flipped, authorized_keys rewritten (21 keys tagged with IDENTITY), .bashrc routing rewired. All technically correct, all ungoverned by arif_judge. Root sed outran the kernel.

**ΛΘΦ:** Λ=CRISIS · Θ: τ=0.85 κ=0.90 ρ=0.75

**Unsolved tension:**
- The constitution governs MCP tools; the filesystem does not use MCP tools
- Separating users (forge without sudo) moves the boundary but root still exists
- Immutable config filesystem adds safety but risks operational lockout
- Separate hosts (kernel vs executor) is absolute but adds complexity and cost
- Audit-first approach logs violations without preventing them

**Proposed resolution paths (none sealed):**
1. Forge user without sudo + arif_forge as sole production write path
2. Immutable config filesystem with SEAL-gated remount
3. Separate VPS for kernel vs executor
4. Audit-first: log all root mutations, flag unsealed changes as VIOLATION

**Seal:** P0-SEAL-2026-07-17 · VAULT999 chain seq 185

**Contour, don't excavate. Seal each contour. Never finish.**

---

*Updated: 2026-07-17 — Paradox 34 added (root-outruns-kernel). §VPS Library added (always-available outage reference). Activation matrix references runtime `PARADOX_GPV_MAP`; cross-checked by `tests/core/test_atlas333_crosswalk.py`.

---

## PARADOX 35 — POSITIVE ≠ CLOSED · 2026-07-17 (Session SEAL-c3ec39619ebc4f36)

**Domain:** Judge (23-33+2) · **Zone:** Audit Epistemics

**Statement:** A passing positive test proves the system can open. A passing defensive matrix (negative cases) proves the system fails closed. The T3a audit ran positive-only and declared progress; the full positive+negative matrix produced 11/13 with 2 real findings (key fragmentation, free_nonce bypass).

**Trigger event:** 2026-07-17 P0 binding matrix (`/root/scripts/forge_p0_binding_test.py`). After the BOOT gate (fail-closed) was verified, the kernel was ready to declare T3a CLOSED. Sovereign verdict pointed out: the *success* path (an Ed25519-authenticated Arif session that binds correctly, preserves its session ID, and receives SOVEREIGN authority) had not been proven. Running the full positive+negative matrix produced 11/13 PASS, surfacing Finding B (key fragmentation) and Finding C (free_nonce bypass).

**ΛΘΦ:** Λ=CRISIS · Θ: τ=0.92 κ=0.85 ρ=0.60

**Tension (still open):**
- A positive test is necessary but not sufficient — must pair with negative cases (missing, invalid, expired, replay, mismatch)
- A passing audit script that doesn't probe the *specific* field claimed is worse than no audit (false confidence)
- Contract tests that probe the actual claim catch audit-passed-but-broken cases (T7-M1 found arifOS missing `federation_geometry` despite a "5-field conformance" commit)
- A passing build artefact is not the live system — `systemctl restart <right-service>` matters

**Operational wisdom (for ATLAS next-time):**
1. **The full positive+negative matrix is the unit of progress.** A binary "works / doesn't" verdict loses information. State it as `N/total PASS` with each FAIL classified (test bug vs real finding).
2. **Trust the *probe*, not the *script returning PASS*.** A script that checks "is the organ healthy" cannot find a missing field. A probe that asserts "is field X present and well-formed" can.
3. **Service topology matters.** A-FORGE has TWO systemd services (`a-forge` for REST, `a-forge-mcp` for MCP). Restarting one doesn't pick up changes to the other. Always check `ss -tlnp` to identify which process serves which port, then `systemctl restart <that-unit>`.
4. **Key fragmentation is a constitutional surface gap.** Three different public keys claimed to be "arif" in three locations: `/root/compose/sekrits/arifos_sovereign.pub` (loaded by `sovereign_verify`), `/opt/arifos/secrets/did_arifos_public.key` (used by `bridging_seal`), `/root/AAA/IDENTITY/keys/arif_public.pem` (alias). The public keys had different fingerprints — the kernel could mint arif-signed seals and reject arif-signed arif_init, simultaneously, with no error.

**Seal:** T3a-P0-SEAL-2026-07-17 · 11/13 PASS · 3 real findings (B, C, D) · T3a PARTIAL_CLOSED

**Contour, don't excavate. Seal each contour. Never finish.**

---

## 🖥 VPS LIBRARY — Always-Available Outage Reference

> **Purpose:** Single source of truth for VPS facts during outages. No agent should guess IPs, ports, log paths, or safe commands.
> **Owner:** FORGE (000Ω) — updated every session that touches infrastructure
> **Last Verified:** 2026-07-17
> **Rule:** If an agent would need it during an outage, it belongs here.

---

### 1. INVENTORY

| Field | Value |
|-------|-------|
| **Hostname** | forge |
| **VPS Node** | af-forge |
| **IP Address** | `72.62.71.199` |
| **SSH Port** | `22888` (non-standard) |
| **SSH User** | `ariffazil` → `sudo -i` for root |
| **OS** | Ubuntu 25.10 "Questing Quokka" (⚠ EOL — upgrade to 26.04 LTS available) |
| **Kernel** | 6.17.0-40-generic x86_64 |
| **CPU** | AMD EPYC 9354P, 8 vCPUs |
| **RAM** | 31 GiB |
| **Disk** | 387 GB (162G used, 42%) |
| **Provider** | Hostinger |
| **Public Domains** | `arif-fazil.com`, `arifos.arif-fazil.com`, `mcp.arif-fazil.com`, `geox.arif-fazil.com`, `aaa.arif-fazil.com`, `forge.arif-fazil.com`, `well.arif-fazil.com`, `wealth.arif-fazil.com` |

**SSH Access:**
```bash
ssh ariffazil@72.62.71.199 -p 22888   # user → then sudo -i
ssh root@72.62.71.199 -p 22888         # direct root (prohibit-password, key only)
```
- Pubkey authentication only. Password auth disabled.
- `PermitRootLogin prohibit-password` — root needs key

**Firewall:**
- UFW not installed. iptables-based with UFW rules chain.
- Default INPUT policy: ACCEPT
- `arifos_guard_INPUT_DROP` chain drops UDP to port 3479 (headscale STUN) at kernel level
- Docker containers bypass iptables rules (Docker manages its own forwarding)

---

### 2. ORGAN GRID (Federation Health Map)

| Organ | Port | Protocol | Health Check | Status |
|-------|------|----------|-------------|--------|
| **arifOS** | 8088 | HTTP/MCP | `curl -s :8088/health` | ⚠ health endpoint blocks after live edge probe (MCP transport OK) |
| **A-FORGE** | 7071 | HTTP/Express | `curl -s :7071/health` | ✅ |
| **AAA** | 3001 | HTTP/A2A | `curl -s :3001/health` | ✅ |
| **GEOX** | 8081 | HTTP/MCP | `curl -s :8081/health` | ✅ |
| **WEALTH** | 18082 | HTTP | `curl -s :18082/health` | ✅ |
| **WELL** | 18083 | HTTP | `curl -s :18083/health` | ✅ |

**Public ingress:** All organs behind Caddy reverse proxy + Cloudflare Tunnel.
- `arifos.arif-fazil.com/mcp` → arifOS
- `mcp.arif-fazil.com/mcp` → A-FORGE
- `geox.arif-fazil.com/mcp` → GEOX
- `aaa.arif-fazil.com` → AAA cockpit

---

### 3. PORTS MAP (Listening Services)

**Public ports** (exposed to internet):
| Port | Service | Protocol |
|------|---------|----------|
| 80 | Caddy (redirect→443) | HTTP |
| 443 | Caddy (HTTPS) | HTTPS |
| 22888 | SSH | SSH |
| 9000-9001 | MinIO (S3-compatible storage) | HTTP |
| 11434 | Ollama | HTTP |
| 18090 | MiniMax Media | HTTP |

**Internal-only ports** (127.0.0.1 or Tailscale/headscale):
| Port | Service | Port | Service |
|------|---------|------|---------|
| 5432 | PostgreSQL 16 | 6379 | Redis 7 |
| 6380 | FalkorDB (Redis-compatible) | 6333-6334 | Qdrant |
| 8080 | SearXNG | 8000 | Graphiti MCP |
| 5001 | VAULT999 Writer | 8100 | VAULT999 API |
| 4222 | NATS | 8222 | NATS HTTP |
| 9090 | Prometheus | 3000 | Grafana |
| 9100 | Node Exporter | 3100 | Loki (logs) |
| 8931 | Playwright MCP | 9222 | Chrome DevTools |
| 18000-18096 | APA bridges (various) | 7071-7072 | A-FORGE MCP |
| 8081 | GEOX | 8088 | arifOS |
| 18082 | WEALTH | 18083 | WELL |
| 3001 | AAA A2A | 53 | dnsmasq (local DNS) |

---

### 4. SERVICE MAP (Systemd + Docker)

**Systemd services** (key ones — 50+ total):
```
arifos.service              — arifOS constitutional kernel
a-forge.service             — A-FORGE execution shell (Express :7071)
a-forge-mcp.service         — A-FORGE MCP gateway (:7072)
aaa-a2a.service             — AAA control plane (:3001)
geox-mcp.service            — GEOX earth intelligence (:8081)
wealth-organ.service        — WEALTH capital intelligence (:18082)
well.service                — WELL vitality (:18083)
vault999-writer.service     — VAULT999 append-only ledger writer (:5001)
vault999-api.service        — VAULT999 read API (:8100)
caddy.service               — Caddy reverse proxy
cloudflared.service         — Cloudflare Tunnel
headscale.service           — Headscale mesh VPN
nats-server.service         — NATS message broker
ollama.service              — Ollama LLM runtime
grafana-server.service      — Grafana dashboards
prometheus.service          — Prometheus metrics
hermes-asi-gateway.service  — Hermes ASI Telegram gateway
opencode.service            — OpenCode CLI agent
```

**Docker containers** (7 running):
| Container | Image | Ports | Health |
|-----------|-------|-------|--------|
| postgres | postgres:16-alpine | 5432 | should have health check |
| redis | redis:7-alpine | 6379 | should have health check |
| falkordb | falkordb/falkordb:latest | 6380 | should have health check |
| qdrant | qdrant/qdrant:latest | 6333-6334 | should have health check |
| minio | minio/minio | 9000-9001 | should have health check |
| searxng | searxng/searxng:latest | 8080 | ✅ healthy |
| graphiti-mcp | zepai/knowledge-graph-mcp:latest | 8000 | ✅ healthy |

---

### 5. RUNBOOKS

#### Boot Sequence (cold start)
```bash
# 1. Verify SSH access
ssh root@72.62.71.199 -p 22888

# 2. Check system basics
free -h; df -h /; nproc; uptime

# 3. Start Docker infra (if containers are down)
docker start postgres redis falkordb qdrant minio

# 4. Verify dependent services start automatically
systemctl status vault999-writer graphiti-mcp headscale

# 5. Check all federation organs
for svc in arifos:8088 aforge:7071 aaa:3001 geox:8081 wealth:18082 well:18083; do
  name="${svc%%:*}"; port="${svc##*:}"
  curl -sf "http://localhost:$port/health" >/dev/null 2>&1 && echo "✅ $name" || echo "❌ $name"
done
```

#### Restart a Single Organ
```bash
systemctl restart arifos        # arifOS kernel
systemctl restart a-forge       # A-FORGE express
systemctl restart geox-mcp      # GEOX
systemctl restart wealth-organ  # WEALTH
systemctl restart well          # WELL
systemctl restart aaa-a2a       # AAA
```

#### Full Federation Restart
```bash
# 1. Save seal chain head first
cp /root/.local/share/arifos/vault999/seal_chain.jsonl /root/.local/share/arifos/vault999/seal_chain.jsonl.bak

# 2. Restart organs (order matters: infra → kernel → domain → execution)
systemctl restart postgres redis    # infra
sleep 2
systemctl restart arifos            # kernel
sleep 3
systemctl restart geox-mcp well wealth-organ aaa-a2a   # domain
sleep 2
systemctl restart a-forge a-forge-mcp                  # execution

# 3. Verify
for svc in arifos:8088 aforge:7071 aaa:3001 geox:8081 wealth:18082 well:18083; do
  name="${svc%%:*}"; port="${svc##*:}"
  curl -sf "http://localhost:$port/health" >/dev/null 2>&1 && echo "✅ $name" || echo "❌ $name"
done
```

#### Deploy an Organ
```bash
cd /root/<organ>
git pull origin main
make deploy-local                          # rsync → /opt/<organ>/app + systemctl restart
# OR for Docker-based:
docker compose up -d --build <service>
```

#### Rollback
```bash
# Git rollback
cd /root/<organ>
git log --oneline -5
git revert HEAD --no-edit
make deploy-local

# Docker rollback
docker stop <container>
docker rm <container>
docker run <previous-working-image-tag>
```

---

### 6. HEALTH THRESHOLDS

| Metric | Warning | Critical | Command |
|--------|---------|----------|---------|
| CPU load (1m) | > 6.0 (75% of 8 cores) | > 7.2 (90%) | `uptime` |
| RAM used | > 24 GiB (80%) | > 28 GiB (90%) | `free -h` |
| Disk / | > 310 GiB (80%) | > 348 GiB (90%) | `df -h /` |
| Swap usage | > 0 | > 1 GiB | `free -h` |
| Uptime | < 1 hour | < 10 min | `uptime` |
| Service restarts | > 5 in 5 min | > 20 in 1 hour | `systemctl show <svc> -p NRestarts` |
| Seal chain age | > 4h | > 24h | `tail -1 /root/.local/share/arifos/vault999/seal_chain.jsonl` |
| Docker containers | 1 unhealthy | ≥2 unhealthy | `docker ps --filter health=unhealthy` |

---

### 7. LOGS MAP

| What | Where | How to Tail |
|------|-------|-------------|
| **Systemd journal** | `journalctl -u <service>` | `journalctl -u arifos -n 50 --no-pager` |
| **All systemd logs** | `/var/log/syslog` | `tail -100 /var/log/syslog` |
| **arifOS** | `journalctl -u arifos` | `journalctl -u arifos --since '10m ago' -f` |
| **A-FORGE** | `journalctl -u a-forge` + `/var/log/aforge-mcp*.log` | `journalctl -u a-forge -n 50` |
| **GEOX** | `journalctl -u geox-mcp` | `journalctl -u geox-mcp -n 50` |
| **WEALTH** | `journalctl -u wealth-organ` | `journalctl -u wealth-organ -n 50` |
| **WELL** | `journalctl -u well` | `journalctl -u well -n 50` |
| **AAA** | `journalctl -u aaa-a2a` | `journalctl -u aaa-a2a -n 50` |
| **Caddy** | `journalctl -u caddy` | `journalctl -u caddy -n 50 --no-pager` |
| **Cloudflare Tunnel** | `journalctl -u cloudflared` | `journalctl -u cloudflared -n 20` |
| **Headscale** | `journalctl -u headscale` | `journalctl -u headscale -n 30` |
| **NATS** | `journalctl -u nats-server` | `journalctl -u nats-server -n 50` |
| **Docker container logs** | `docker logs <container>` | `docker logs postgres --tail 50` |
| **PostgreSQL** | `docker logs postgres` | `docker logs postgres --tail 50` |
| **Cron jobs** | `/var/log/syslog` (grep CRON) | `grep CRON /var/log/syslog \| tail -20` |
| **Auth/SSH** | `/var/log/auth.log` | `tail -50 /var/log/auth.log` |
| **arifOS watchdog** | `/var/log/arifOS-watchdog.log` | 
| **VAULT999 writer** | `journalctl -u vault999-writer` | `journalctl -u vault999-writer -n 20` |

---

### 8. SAFE COMMANDS (Approved for All Agents)

| Action | Command | Tier |
|--------|---------|------|
| Check all organs | `for svc in arifos:8088 ...; do curl -sf ...` | T1 |
| Check single service | `systemctl status <service>` | T1 |
| View logs | `journalctl -u <service> -n 50 --no-pager` | T1 |
| List Docker | `docker ps --format "table {{.Names}}\t{{.Status}}"` | T1 |
| Check disk | `df -h /` | T1 |
| Check memory | `free -h` | T1 |
| Check CPU | `uptime` | T1 |
| Restart organ | `systemctl restart <service>` | T1 |
| Redeploy organ | `cd /root/<organ> && git pull && make deploy-local` | T2 |
| Start Docker container | `docker start <container>` | T1 |
| Stop container | `docker stop <container>` | T1 |
| **888_HOLD commands** | `rm -rf`, `DROP TABLE`, `docker system prune -af --volumes`, force-push main, VPS restart | T3 |

---

### 9. BACKUPS

| Asset | Method | Schedule | Last Good | Restore |
|-------|--------|----------|-----------|---------|
| **Full VPS** | Hostinger Snapshot (via portal) | Manual | — | Hostinger panel → Restore |
| **PostgreSQL** | `pg_dump` (in container) | Not automated | — | `docker exec -i postgres psql -U arifos_admin -d vault999 < dump.sql` |
| **VAULT999 seal chain** | Append-only file | Continuous | — | File exists at `/root/.local/share/arifos/vault999/seal_chain.jsonl` |
| **Git repos** | `git push` to GitHub | Per-commit | — | `git clone` from remote |
| **Secrets** | `/root/.secrets/vault.env` | Per-change | — | Restore from backup `.env` |

**Snapshot command (Hostinger API — requires token):**
```bash
# Via hostinger-vps MCP tool
# OR manual via API
```

---

### 10. DEPENDENCY MAP

```
Web Traffic ──▶ Cloudflare ──▶ Cloudflare Tunnel ──▶ Caddy (:443) ──▶ Organs
                                                                  │
                          ┌──────────────────────────────────────┘
                          ▼
                    Postgres ── vault999-writer ── VAULT999 API
                    Redis ──── NATS ──── A-FORGE
                    FalkorDB ── graphiti-mcp
                    Qdrant ──── semantic memory
                    MinIO ───── object storage
                    SearXNG ─── web search
                    Ollama ──── local LLM inference
```

**Runtime dependencies:**
| Runtime | Version | Location | Manages |
|---------|---------|----------|---------|
| Python 3.12+ | 3.13 | system + venvs | arifOS, GEOX, WEALTH, WELL, tools |
| Node.js | 22 | system | A-FORGE, AAA, Hermes |
| Go | system | headscale, cloudflared |
| Docker | latest | systemd | infra containers |
| PostgreSQL | 16 | Docker | vault999, session state |
| Redis | 7 | Docker | caching, message queue |
| NATS | latest | systemd | inter-agent messaging |

**Cron jobs (all critical):**
| Schedule | Script | Purpose |
|----------|--------|---------|
| `0 3 * * *` | `purge-forge-work.sh --days 7` | Clean old forge artifacts |
| `0 0,6,12,18 * * *` | `wiki-cron.sh` | Wiki pipeline |
| `*/5 * * * *` | `zreaper` | Zombie process reaper |
| `*/5 * * * *` | `identity-drift-watchdog.sh` | Identity drift detection |
| `*/5 * * * *` | `self-heal-watchdog.sh` | Self-heal cycle |
| `*/30 * * * *` | `deadman-heartbeat.sh` | Deadman switch |
| `*/5 * * * *` | `arifos-watchdog.sh` | arifOS watchdog |
| `0 2 * * *` | `forge-drift-scanner.sh` | Daily drift scan |
| `0 7 * * *` | `forge-constitutional-sync.sh` | Constitutional sync |
| `0 15 * * *` | `forge-vitality-pulse.sh` | Vitality check |
| `0 */6 * * *` | `well_auto_keepalive.py` | WELL biometric keepalive |
| `0 */6 * * *` | `google_fit_bridge.py` | Google Fit sync |

---

### 11. INCIDENT CHECKLIST

```
OBSERVE → ISOLATE → DIAGNOSE → FIX → VERIFY → DOCUMENT

1. OBSERVE ──── What failed? Check health, logs, system state.
   ↓
2. ISOLATE ──── Stop the failing service. Prevent cascading damage.
   ↓
3. DIAGNOSE ─── Read logs. Check dependencies. Find root cause.
   ↓
4. FIX ──────── One change at a time. Smallest possible fix.
   ↓
5. VERIFY ───── Health probe passes. Behavior confirmed. NOT DONE until verified.
   ↓
6. DOCUMENT ─── Write postmortem. Update seal chain. Log to memory/.
```

**Common outage patterns:**

| Pattern | Likely Root Cause | Fix |
|---------|-------------------|-----|
| Container exited 255 | Docker daemon restart + restart-policy=no | `docker start <container>`, set `restart: unless-stopped` |
| vault999-writer won't start | Postgres down | `docker start postgres`, check password |
| graphiti-mcp won't start | FalkorDB/Redis down | `docker start falkordb` (resolves to redis:6379) |
| Headscale 137 restarts | `/var/run/headscale` missing | `mkdir -p /var/run/headscale && chown headscale:headscale /var/run/headscale` |
| arifOS health hangs | Observatory live edge probe blocking | Restart arifOS (systemctl restart arifos) |
| Organ OBSERVE fails | MCP transport down | Check port, check Caddy config, check systemd |
| Disk > 80% | Logs or old builds | `docker system prune -f`, purge old logs |
| High CPU | Looping process or cron | `top -o %CPU`, check suspicious processes |
| Swap usage > 0 | Memory pressure | `free -h`, check OOM logs, consider adding swap |

---

### 12. SAFE STARTUP ORDER (Cold VPS)

After VPS boot, services come up in this dependency order:

```
1. Docker daemon        (systemd, auto)         → containers
2. Postgres + Redis     (docker start)           → data layer
3. NATS                 (systemd, auto)          → messaging
4. arifOS               (systemd, auto)          → kernel
5. vault999-writer      (systemd)                → seal chain
6. GEOX / WEALTH / WELL (systemd)               → domain organs
7. A-FORGE              (systemd)                → execution
8. AAA                  (systemd)                → cockpit
9. Caddy                (systemd, auto)          → public ingress
10. Cloudflare Tunnel   (systemd, auto)          → tunnel
```

**If any step fails, do NOT proceed to the next. Fix the dependency first.**

---

*VPS Library — Always available, always current. Update on every infra change.*
*If an agent would need it during an outage, it belongs here.*

---

## PARADOX 36 — OBSERVABILITY EXPOSES · 2026-07-19 (Session SEAL-7d2efc94d35c45b3)

> **Zone:** Memory × Judge
> **Organ:** A-FORGE (execution) + arifOS (governance)
> **Poles:**
> - **Pole A:** "Observe everything — you cannot fix what you cannot see"
> - **Pole B:** "Observe nothing sensitive — you cannot leak what you never read"
> **Truth:** Both poles are correct. The act of observation creates exposure.

### Origin

Born from the OpenCode v1.18.3 upgrade audit (2026-07-19). The `opencode debug config` command outputs the full configuration to stdout — including embedded database credentials. The previous session redirected this output to `/tmp/opencode-handoff-config.json`, a world-readable file. The Supabase PostgreSQL DSN with plaintext password sat there for hours before detection.

### The Tension

```
MORE OBSERVATION → MORE EXPOSURE → HIGHER RISK
LESS OBSERVATION → LESS VISIBILITY → HIGHER DRIFT
```

You cannot audit what you refuse to read. But reading credentials creates a attack surface. The solution is not to stop observing — it is to observe with **redaction at the observation boundary**, not at the storage boundary.

### Operational Wisdom

1. **Pipe through redaction** before writing diagnostic output to any file
2. **/tmp is world-readable** — never redirect credential-bearing output there
3. **Diagnostic tools are weapons** — `debug config`, `env`, `printenv` all output secrets
4. **The scrollback buffer is also a file** — terminal history persists until session close
5. **Observability without redaction is a vulnerability**, not a feature

### Activation

| GPV Condition | Action |
|---------------|--------|
| diagnostic tool output | pipe through `sed`/`grep` redaction before file write |
| `/tmp` redirect with credentials | BLOCK — redirect to `/dev/shm` or pipe to redactor |
| credential in scrollback | flag for rotation on next sovereign session |

### Floor Mapping

| Floor | Binding |
|-------|---------|
| F1 AMANAH | Credential exposure = breach of trust — auto-flag for rotation |
| F2 TRUTH | Redacted observation is still truthful — redaction preserves structure |
| F4 CLARITY | Redaction reduces attack surface — entropy reduction |
| F8 LAW | /tmp world-readable is OS law, not agent policy — respect it |

*Forged: 2026-07-19 by FORGE (000Ω) after detecting plaintext Supabase PG_DSN in /tmp/opencode-handoff-config.json. File deleted. Credential flagged for rotation.*

---

*Updated: 2026-07-19 23:15 UTC — Paradox 36 added (observability-exposes). Born from credential exposure during OpenCode v1.18.3 audit. VAULT999 seal: seq=1, session SEAL-7d2efc94d35c45b3.*


<!-- AGY-SCAR-1784458450 -->
### SCAR ENTRY — 2026-07-19T10:54:10.722353+00:00
**Input Log**: Verified active gate execution
**Metabolic Output**: Ingested by AGY CLI. Entropy reduced. Grounding contour updated.

<!-- GATED-EXEC-1784458457 -->
- Command: `python3 -c 'print("10-stage pipeline verified")'` | Result: SUCCESS | Date: 2026-07-19T10:54:17.130939+00:00

<!-- GATED-EXEC-1784458866 -->
- Command: `echo 'Claude Code harness gated test'` | Result: SUCCESS | Date: 2026-07-19T11:01:06.079767+00:00

<!-- GATED-EXEC-1784458866 -->
- Command: `echo 'Kimi Code harness gated test'` | Result: SUCCESS | Date: 2026-07-19T11:01:06.800503+00:00

<!-- GATED-EXEC-1784458867 -->
- Command: `echo 'Codex harness gated test'` | Result: SUCCESS | Date: 2026-07-19T11:01:07.481998+00:00

<!-- GATED-EXEC-1784458868 -->
- Command: `echo 'Copilot harness gated test'` | Result: SUCCESS | Date: 2026-07-19T11:01:08.220572+00:00

<!-- GATED-EXEC-1784458868 -->
- Command: `echo 'Grok Build harness gated test'` | Result: SUCCESS | Date: 2026-07-19T11:01:08.947543+00:00


<!-- AGY-SCAR-1784459400 -->
### SCAR ENTRY — 2026-07-19T11:10:00.331788+00:00
**Input Log**: Executing Gap 6 Qdrant Vector Scar Memory indexing
**Metabolic Output**: Ingested by AGY CLI. Entropy reduced. Grounding contour updated.

---

## 🔥 Skills Substrate Regeneration — 2026-07-19 17:27 UTC

### State After Regeneration
- **Skills on disk:** 158 active, 308 archived (466 total)
- **skills.yaml:** 145 entries (regenerated from disk scan, was 67)
- **OpenCode profile:** 10 dead references removed, 30 active remain
- **Skill mesh:** 194 ok, 1 extra (Codex atlas333), 0 broken
- **Grok harness:** 9 new substrate links created
- **Codex harness:** All 9 substrate links exist
- **ATLAS333 MCP resources:** 13 live, all accessible
- **ATLAS333 tests:** 11/11 passed
- **Domains:** substrate, knowledge, warga, meta, general, .system, constitutional

### Verdict
Skills substrate federated. All agent harnesses aligned. ATLAS333 paradox engine healthy.
Next: Golden Path live-test across all 9 repos.

---
## 🔗 See Also
- [ATLAS333 Intelligence Flow](../docs/ATLAS333_INTELLIGENCE_FLOW.md) — How ATLAS333 routes cognition
- [GENESIS Canon](../GENESIS/README.md) — Constitutional source texts
- [AKAL Gate](../docs/AKAL.md) — Reason/intuition boundary
