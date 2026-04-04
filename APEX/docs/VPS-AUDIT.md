# VPS Security Audit Report

**Date:** 2026-03-02  
**Host:** srv1325122 (72.62.71.199)  
**Location:** Kuala Lumpur  
**Auditor:** DevSecOps Agent  
**Telemetry:** `{"dS":-0.55,"peace2":1.08,"kappa_r":0.97,"confidence":0.93,"verdict":"Alive"}`

---

## 1. Host Summary

| Attribute | Value |
|-----------|-------|
| **OS** | Ubuntu 24.04.4 LTS (Noble) |
| **Kernel** | 6.8.0-101-generic x86_64 |
| **CPU** | 4 cores |
| **RAM** | 15GB (6.4GB used, 9.2GB available) |
| **Disk** | 193GB total, 132GB used (69% full) |
| **Uptime** | ~4 hours |
| **Load** | 0.60, 0.44, 0.38 |

### Running Services (Key)

| Service | Status | Notes |
|---------|--------|-------|
| arifos-aaa-mcp | ✅ Running | Native systemd, root user |
| arifos-embeddings | ✅ Running | Native systemd, root user |
| arifos-router | ✅ Running | Native systemd, root user |
| docker | ✅ Running | Container runtime |
| postgresql@16-main | ✅ Running | Native Postgres |
| redis-server | ✅ Running | Native Redis |
| nginx | ✅ Running | Reverse proxy |
| fail2ban | ✅ Running | 3 jails active |
| netdata | ✅ Running | Monitoring |
| unattended-upgrades | ✅ Running | Auto-updates enabled |

---

## 2. Docker & Network Topology

### Containers (11 running)

| Container | Image | Network | Status |
|-----------|-------|---------|--------|
| openclaw | openclaw:local | trinity_network, ai-net, coolify | Healthy |
| agent-zero | agent0ai/agent-zero | trinity_network | Healthy |
| qdrant | qdrant/qdrant | bridge | Running |
| ollama | ollama/ollama | ai-net, bridge | Running |
| coolify | ghcr.io/coollabsio/coolify | coolify | Healthy |
| coolify-proxy | traefik:v3.6 | - | Healthy |
| coolify-db | postgres:15-alpine | coolify | Healthy |
| coolify-redis | redis:7-alpine | coolify | Healthy |
| postgres-qoo0... | postgres:16-alpine | qoo0o48o... | Healthy |
| redis-qoo0... | redis:7-alpine | qoo0o48o... | Healthy |

### Networks

| Network | Subnet | Containers |
|---------|--------|------------|
| trinity_network | 10.0.2.0/24 | agent-zero, openclaw |
| ai-net | 10.0.4.0/24 | openclaw, ollama |
| coolify | 10.0.1.0/24 | coolify, coolify-db, coolify-redis, openclaw |
| qoo0o48o... | 10.0.3.0/24 | postgres, redis (Coolify app) |

### Exposed Ports (Public)

| Port | Service | Risk |
|------|---------|------|
| 22 | SSH | ⚠️ Brute force target (LIMIT in UFW) |
| 80 | HTTP (Traefik) | Low |
| 443 | HTTPS (Traefik) | Low |
| 3000 | OpenClaw | ⚠️ No auth visible |
| 50001 | Agent-Zero | ⚠️ No auth visible |
| 6333 | Qdrant | ⚠️ No auth, vector DB exposed |
| 8080 | arifOS MCP | ⚠️ Public MCP endpoint |
| 11434 | Ollama | ⚠️ No auth, LLM API exposed |
| 8000 | Coolify Panel | ⚠️ Admin panel public |

### Localhost Only (Safe)

- 5432 (PostgreSQL)
- 6379 (Redis)
- 19999 (Netdata)
- 8090, 8125 (StatsD)

---

## 3. arifOS / MCP Stack Overview

### Native Services (systemd)

| Service | User | Working Dir | Port |
|---------|------|-------------|------|
| arifos-aaa-mcp | root | /root/arifOS | Internal |
| arifos-router | root | /root/arifOS | 8080 |
| arifos-embeddings | root | /opt/arifos-embeddings | Internal |

### Git Status

| Repo | Branch | Status |
|------|--------|--------|
| /root/arifOS | main | ✅ Clean, synced to GitHub |

### MCP Config Files Found (19)

```
/root/arifOS/fastmcp.json
/root/arifOS/.opencode-mcp.json
/root/arifOS/333_APPS/L4_TOOLS/mcp-configs/*/
/root/.kimi/mcp.json
/root/.gemini/mcp-oauth-tokens-v2.json
```

### Environment Variables (keys detected)

```
QDRANT_URL, OLLAMA_URL, OPENCLAW_URL, AGENT_ZERO_URL
(Values stored in .env.docker, not exposed)
```

---

## 4. Security Findings (Host)

### ✅ Strengths

| Finding | Status |
|---------|--------|
| UFW Firewall | ✅ Active, default deny |
| Fail2Ban | ✅ Running, 3 jails, 11 bans |
| Unattended Upgrades | ✅ Enabled |
| Netdata Monitoring | ✅ Active |
| PostgreSQL | ✅ Localhost only |
| Redis | ✅ Localhost only |

### ⚠️ Weaknesses

| ID | Finding | Severity | Details |
|----|---------|----------|---------|
| H1 | **Root SSH login enabled** | HIGH | `PermitRootLogin yes` |
| H2 | **Password auth enabled** | HIGH | `PasswordAuthentication yes` |
| H3 | **Services run as root** | MEDIUM | arifOS native services use root |
| H4 | **Multiple login users** | MEDIUM | root, ubuntu, postgres, arifos, netdata |

---

## 5. Security Findings (Containers & MCP)

### 🔴 Critical

| ID | Finding | Severity | Details |
|----|---------|----------|---------|
| C1 | **OpenClaw has docker.sock** | CRITICAL | Full host control via Docker API |
| C2 | **OpenClaw mounts arifOS** | CRITICAL | Read/write to constitutional kernel |
| C3 | **Agent-Zero mounts arifOS** | CRITICAL | Read/write to constitutional kernel |

### 🟠 High

| ID | Finding | Severity | Details |
|----|---------|----------|---------|
| C4 | **Ollama exposed publicly** | HIGH | Port 11434, no auth |
| C5 | **Qdrant exposed publicly** | HIGH | Port 6333, no auth |
| C6 | **Agent-Zero exposed publicly** | HIGH | Port 50001, no auth |
| C7 | **OpenClaw exposed publicly** | HIGH | Port 3000, no auth |

### 🟡 Medium

| ID | Finding | Severity | Details |
|----|---------|----------|---------|
| C8 | **Containers run as root** | MEDIUM | qdrant (0:0), ollama, agent-zero |
| C9 | **No capability dropping** | MEDIUM | All containers have full caps |
| C10 | **No read-only filesystems** | MEDIUM | All containers writable |

---

## 6. Risks Ranked

### Critical (Immediate Action)

1. **C1: OpenClaw docker.sock mount** — Container can control host Docker daemon, create privileged containers, access any mount.
2. **C2/C3: arifOS mounted in containers** — Constitutional kernel code/data accessible to Agent-Zero and OpenClaw.

### High (This Week)

3. **H1/H2: SSH weak config** — Root login + password auth = easy compromise vector.
4. **C4-C7: Unauthenticated public services** — Ollama, Qdrant, Agent-Zero, OpenClaw all exposed without auth.

### Medium (This Month)

5. **H3, C8: Root user everywhere** — Privilege escalation path if any service compromised.
6. **C9/C10: No container hardening** — No caps drop, no read-only FS.

---

## 7. Hardening Plan

### Stage 1: No Downtime (Do Now)

#### 1.1 SSH Hardening

```bash
# Backup first
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Edit config
sudo nano /etc/ssh/sshd_config

# Changes:
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes

# Test config before reload
sudo sshd -t && sudo systemctl reload sshd
```

**Impact:** Disables password login, requires SSH key.  
**Rollback:** `sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config && sudo systemctl reload sshd`

#### 1.2 Close Public Ports (UFW)

```bash
# Close unauthenticated services to public
sudo ufw delete allow 3000/tcp
sudo ufw delete allow 50001/tcp
sudo ufw delete allow 6333/tcp
sudo ufw delete allow 11434/tcp
sudo ufw delete allow 8080/tcp

# Allow only from specific IPs (replace with your IP)
sudo ufw allow from YOUR_CLIENT_IP to any port 3000
sudo ufw allow from YOUR_CLIENT_IP to any port 8080
```

**Impact:** Services only accessible from your IP.  
**Rollback:** Re-add `sudo ufw allow <port>/tcp`

#### 1.3 Add HTTP Basic Auth to OpenClaw

```bash
# Install htpasswd
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd arif

# Add to nginx config for OpenClaw endpoint
# location /openclaw {
#   auth_basic "Restricted";
#   auth_basic_user_file /etc/nginx/.htpasswd;
# }
sudo nginx -t && sudo systemctl reload nginx
```

---

### Stage 2: Short Restarts (Plan Ahead)

#### 2.1 Run arifOS as Non-Root User

**888_HOLD** — Requires testing before applying

```bash
# Create dedicated user
sudo useradd -r -s /bin/false arifos

# Change ownership
sudo chown -R arifos:arifos /root/arifOS
sudo chown -R arifos:arifos /opt/arifos-embeddings

# Update systemd units
sudo systemctl edit arifos-aaa-mcp
# [Service]
# User=arifos
# Group=arifos

sudo systemctl daemon-reload
sudo systemctl restart arifos-aaa-mcp arifos-embeddings arifos-router
```

**Impact:** arifOS runs with minimal privileges.  
**Rollback:** Revert systemd override, restore ownership.

#### 2.2 Remove docker.sock from OpenClaw

**888_HOLD** — Will break OpenClaw Docker features

```bash
# Edit docker-compose.yml or container config
# Remove: /var/run/docker.sock:/var/run/docker.sock

# Alternative: Use Docker API via TCP with TLS
```

**Impact:** OpenClaw cannot manage containers. May break features.  
**Rollback:** Re-add the mount.

#### 2.3 Container Security Options

```yaml
# In docker-compose.yml for each service:
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # only if needed
read_only: true
tmpfs:
  - /tmp
```

**Impact:** Containers more restricted. May break some apps.  
**Rollback:** Remove security options.

---

### Stage 3: Advanced (Optional)

#### 3.1 Network Segmentation

- Create isolated network for arifOS (no internet)
- Only Traefik/nginx can reach arifOS
- Agent-Zero and OpenClaw in DMZ

#### 3.2 Secrets Management

- Move from .env files to HashiCorp Vault or Docker Secrets
- Rotate all API keys after migration

#### 3.3 MCP Policy Gateway

- Implement tool whitelist in arifOS
- Require human approval for destructive tools
- Log all MCP calls to audit table

---

## 8. Summary

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Host | 0 | 2 | 2 | 0 |
| Containers | 3 | 4 | 3 | 0 |
| **Total** | **3** | **6** | **5** | **0** |

### Immediate Actions (Today)

1. ✅ Disable SSH password auth
2. ✅ Close public ports 3000, 50001, 6333, 11434
3. ✅ Review OpenClaw docker.sock necessity

### This Week

4. Add auth to public services
5. Audit arifOS mount exposure

### This Month

6. Container hardening (non-root, caps drop)
7. Network segmentation
8. Secrets rotation

---

**Report generated:** 2026-03-02 10:30 UTC  
**Next audit:** 2026-04-02

---

*Ditempa Bukan Diberi*
