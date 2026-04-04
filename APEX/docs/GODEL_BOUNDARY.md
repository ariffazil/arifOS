# Gödel Boundary - Known Uncertainties

**Version:** 2026.03.03  
**Classification:** TRINITY SEALED (with caveats)  

---

## Purpose

This document encodes **known unknowns** - areas where the dossier may diverge from reality. This is our Gödel lock: acknowledging incompleteness to prevent false confidence.

---

## 🔴 HIGH-RISK Uncertainties

### 1. docker-mcp Security Posture

**Status:** ⚠️ **HIGH RISK - Requires 888_HOLD**

| Property | Value | Risk |
|----------|-------|------|
| Runs as | `npx -y docker-mcp` (spawned by Kimi) | As root user |
| Docker socket | **YES** - `/var/run/docker.sock` is accessible | 🔴 **RCE-grade channel** |
| Scope | Can manage ANY container | Unrestricted |
| Governance | **NOT routed through arifOS** | Bypasses constitutional checks |

**Gödel Uncertainty:**
- We do not know if docker-mcp is being used by Kimi Code
- We do not know what Docker commands are being executed
- We do not have audit logging for docker-mcp actions

**Required Action (888_HOLD):**
```bash
# Option A: Disable docker-mcp entirely
# Edit ~/.kimi/mcp.json and remove or disable the docker-mcp entry

# Option B: Restrict docker-mcp scope (requires wrapper script)
# Create a restricted docker-mcp wrapper that only allows safe commands

# Option C: Route all docker operations through arifOS eureka_forge tool
# This provides constitutional validation before execution
```

---

### 2. UFW + Docker Interaction

**Status:** ⚠️ **UFW IS BYPASSED BY DOCKER**

| Property | Expected | Actual |
|----------|----------|--------|
| UFW rules | Block unauthorized ports | ✅ Present |
| Docker published ports | Respect UFW | ❌ **BYPASS UFW** |
| DOCKER-USER chain | May have rules | Empty (no restrictions) |

**Evidence:**
```bash
# Published ports bypass UFW:
# openclaw: 0.0.0.0:3000->18789/tcp  (exposed to internet!)
# qdrant: 0.0.0.0:6333->6333/tcp     (exposed to internet!)
# ollama: 0.0.0.0:11434->11434/tcp   (exposed to internet!)
# agent-zero: 0.0.0.0:50001->80/tcp  (exposed to internet!)
# coolify: 0.0.0.0:8000->8080/tcp    (exposed to internet!)
```

**Gödel Uncertainty:**
- UFW shows "active" but Docker ports are still exposed
- We rely on Docker's internal security, not UFW
- Future agents may assume UFW is protecting these ports

**Mitigation Options (888_HOLD):**
```bash
# Option A: Use ufw-docker tool
# https://github.com/chaifeng/ufw-docker
sudo wget -O /usr/local/bin/ufw-docker https://raw.githubusercontent.com/chaifeng/ufw-docker/master/ufw-docker
sudo chmod +x /usr/local/bin/ufw-docker

# Option B: Bind to localhost only
# Change docker-compose.yml from:
#   ports: - "3000:18789"
# To:
#   ports: - "127.0.0.1:3000:18789"

# Option C: Add DOCKER-USER rules
# iptables -I DOCKER-USER -i ext_if ! -s 192.168.1.0/24 -j DROP
```

---

## 🟠 MODERATE Uncertainties

### 3. IP Drift Risk

**Status:** ⚠️ **IPs are DHCP, not static**

| Network | Configured | Risk |
|---------|------------|------|
| bridge | DHCP (10.0.0.0/24) | IPs can change on restart |
| ai-net | DHCP (10.0.4.0/24) | IPs can change on restart |
| trinity_network | DHCP (10.0.2.0/24) | IPs can change on restart |
| coolify | DHCP (10.0.1.0/24) | IPs can change on restart |

**Current Reality (2026-03-03):**
```
openclaw: 10.0.4.3 (ai-net) - also on bridge, trinity
qdrant: 10.0.4.4 (ai-net) - also on bridge
ollama: 10.0.4.2 (ai-net) - also on bridge
agent-zero: 10.0.2.2 (trinity_network)
coolify: 10.0.1.4 (coolify)
```

**Gödel Uncertainty:**
- If containers restart in different order, IPs may change
- Documentation assumes static IPs
- Hardcoded URLs in configs may break

**Mitigation Options (888_HOLD):**
```yaml
# docker-compose.yml - Add static IPs
networks:
  ai-net:
    ipam:
      config:
        - subnet: 10.0.4.0/24
services:
  openclaw:
    networks:
      ai-net:
        ipv4_address: 10.0.4.3
```

---

### 4. MCP Server Trust Policy Undefined

**Status:** ⚠️ **No formal trust classification**

| Server | Type | Trust Level | Risk Classification |
|--------|------|-------------|---------------------|
| arifos-aaa | Local (stdio) | HIGH | Constitutional kernel - governed |
| codegraphcontext | Local | MEDIUM | Code analysis - read heavy |
| context7 | Remote (HTTPS) | LOW | External API - data leaves VPS |
| docker-mcp | Local (npx) | **CRITICAL** | Docker access - **NO GOVERNANCE** |
| jina-reader | Remote (HTTPS) | LOW | External API - data leaves VPS |

**Gödel Uncertainty:**
- No policy on what data can be sent to remote MCPs
- No policy on which MCPs can execute write operations
- arifOS governance not enforced for all MCP tools

---

## 🟢 LOW-RISK Uncertainties

### 5. PostgreSQL Database Contents

**Status:** Documented but not detailed

| Question | Answer | Confidence |
|----------|--------|------------|
| What databases exist? | Unknown | Low |
| Does VAULT999 use Postgres? | Likely | Medium |
| Backup strategy? | Unknown | Low |

**Action Required:**
```bash
# Document database contents
psql -U arifos -c "\l"
psql -U arifos -c "\dt"
```

---

## Residual Uncertainty Score

| Category | Score | Notes |
|----------|-------|-------|
| docker-mcp security | 0.3 | Critical gap |
| UFW + Docker | 0.5 | Partial protection |
| IP drift | 0.7 | Moderate risk |
| MCP trust policy | 0.6 | Not formalized |
| DB documentation | 0.8 | Low detail |

**Overall Confidence:** 0.58 (Moderate - significant gaps exist)

---

## Truth Claim

> "This dossier documents what we know, and explicitly marks what we don't know. The system is TRINITY SEALED with caveats - not perfect, but honest about imperfection."

**Next Reseal Required:** After addressing docker-mcp and UFW bypass issues.

---

*Ditempa Bukan Diberi* 🔥
