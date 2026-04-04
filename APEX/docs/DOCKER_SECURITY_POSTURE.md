# Docker Security Posture - arifOS VPS

**Inspection Date:** 2026-03-03  
**Inspector:** Resident arifOS VPS Agent  
**Classification:** READ-ONLY AUDIT  

---

## Executive Summary

| Risk Level | Count | Containers |
|------------|-------|------------|
| 🔴 CRITICAL | 1 | openclaw (docker.sock - intentional) |
| 🟠 MODERATE | 2 | ollama, agent-zero (run as root) |
| 🟢 LOW | 2 | qdrant, coolify (non-root users) |

---

## Container Security Matrix

### OpenClaw (AGI Gateway)

| Property | Value | Risk |
|----------|-------|------|
| User | `node` | 🟢 Good |
| Privileged | `false` | 🟢 Good |
| CapAdd | none | 🟢 Good |
| CapDrop | none | 🟡 Neutral |
| ReadonlyRootfs | `false` | 🟡 Neutral |
| **Docker Socket** | **YES** | 🔴 **HIGH** |
| ExtraHosts | `host.docker.internal:host-gateway` | 🟡 Intentional |

**Mounts:**
```
/root/arifOS → /mnt/arifos (rw)
/root/APEX-THEORY → /mnt/apex (rw)
/var/run/docker.sock → /var/run/docker.sock (rw) ⚠️
/root/openclaw_data → /home/node/.openclaw (rw)
```

**Assessment:** OpenClaw has docker.sock mounted BY DESIGN. This is intentional for AGI-level execution capability. The container runs as non-root `node` user, which provides some mitigation.

**Suggested Hardening (888_HOLD required):**
- [ ] Consider read-only mount for `/mnt/arifos` and `/mnt/apex` if write not needed
- [ ] Document docker.sock access in security policy
- [ ] Enable container logging for audit trail

---

### Qdrant (Vector Database)

| Property | Value | Risk |
|----------|-------|------|
| User | `0:0` (root) | 🟡 Acceptable |
| Privileged | `false` | 🟢 Good |
| CapAdd | none | 🟢 Good |
| CapDrop | none | 🟡 Neutral |
| ReadonlyRootfs | `false` | 🟡 Neutral |
| Docker Socket | NO | 🟢 Good |

**Mounts:**
```
/root/qdrant → /qdrant/storage (rw)
```

**Assessment:** Runs as root but minimal attack surface. Data-only mount.

**Suggested Hardening (888_HOLD required):**
- [ ] Add `--read-only` flag with tmpfs for /tmp
- [ ] Add `--cap-drop ALL` if not needed
- [ ] Consider dedicated qdrant user

---

### Ollama (LLM + Embeddings)

| Property | Value | Risk |
|----------|-------|------|
| User | **not specified (root)** | 🟠 **MODERATE** |
| Privileged | `false` | 🟢 Good |
| CapAdd | none | 🟢 Good |
| CapDrop | none | 🟡 Neutral |
| ReadonlyRootfs | `false` | 🟡 Neutral |
| Docker Socket | NO | 🟢 Good |

**Mounts:**
```
/root/ollama → /root/.ollama (rw)
```

**Assessment:** Runs as root by default (upstream image). Model storage requires write access.

**Suggested Hardening (888_HOLD required):**
- [ ] Add `--user ollama:ollama` if upstream supports
- [ ] Add `--cap-drop ALL`
- [ ] Consider read-only rootfs with volume for model storage

---

### Agent-Zero (Autonomous Agent)

| Property | Value | Risk |
|----------|-------|------|
| User | **not specified (root)** | 🟠 **MODERATE** |
| Privileged | `false` | 🟢 Good |
| CapAdd | none | 🟢 Good |
| CapDrop | none | 🟡 Neutral |
| ReadonlyRootfs | `false` | 🟡 Neutral |
| Docker Socket | NO | 🟢 Good |

**Mounts:**
```
/root/APEX-THEORY → /mnt/apex (rw)
/root/arifOS → /mnt/arifos (rw)
/root/agent_zero_data → /app/work_dir (rw)
```

**Assessment:** Runs as root but sandboxed to trinity_network (no external access). Has access to arifOS and APEX-THEORY repos.

**Suggested Hardening (888_HOLD required):**
- [ ] Add `--user agent:agent` if possible
- [ ] Consider read-only mounts for /mnt/apex and /mnt/arifos
- [ ] Add `--cap-drop ALL`

---

### Coolify (Platform Manager)

| Property | Value | Risk |
|----------|-------|------|
| User | `www-data` | 🟢 Good |
| Privileged | `false` | 🟢 Good |
| CapAdd | none | 🟢 Good |
| CapDrop | none | 🟡 Neutral |
| ReadonlyRootfs | `false` | 🟡 Neutral |
| Docker Socket | NO | 🟢 Good |
| ExtraHosts | `host.docker.internal:host-gateway` | 🟡 Intentional |

**Mounts:**
```
/data/coolify/databases → /var/www/html/storage/app/databases (rw)
/data/coolify/services → /var/www/html/storage/app/services (rw)
/data/coolify/ssh → /var/www/html/storage/app/ssh (rw)
/data/coolify/source/.env → /var/www/html/.env (ro)
... (more mounts)
```

**Assessment:** Runs as www-data, follows least privilege. Multiple data mounts for platform management.

**Suggested Hardening (888_HOLD required):**
- [ ] Review SSH key access scope
- [ ] Add `--cap-drop ALL` if not needed
- [ ] Consider read-only rootfs

---

## MCP Servers & Risk Level

From `~/.kimi/mcp.json`:

| Server | Type | Location | Capabilities | Risk |
|--------|------|----------|--------------|------|
| arifos-aaa | Local | stdio → `/root/arifOS` | Constitutional tools, forge, audit | 🟡 Moderate (internal) |
| codegraphcontext | Local | `/root/.local/.../cgc` | Code graph queries | 🟢 Low (read-only) |
| context7 | Remote | `https://mcp.context7.com/mcp` | Context retrieval | 🟡 Moderate (external API) |
| docker-mcp | Local | npx docker-mcp | Docker management | 🟠 High (Docker access) |
| jina-reader | Remote | `https://mcp.jina.ai/v1` | Web content fetching | 🟢 Low (read-only) |

**Notes:**
- `arifos-aaa` uses stdio mode (most secure, no network exposure)
- `docker-mcp` has DOCKER_MCP_LOCAL=true (limited to local)
- Remote servers require API keys (documented in config)

---

## Firewall Status (UFW)

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)

Allowed Ports:
  22/tcp   (LIMIT)    - SSH
  80/tcp   (ALLOW)    - HTTP (Nginx)
  443      (ALLOW)    - HTTPS (Nginx)
  8000/tcp (ALLOW)    - Coolify Panel
  8080/tcp (ALLOW)    - arifOS MCP Server
```

**Docker & UFW Interaction:**
- Docker modifies iptables directly
- DOCKER-USER chain is empty (default accept)
- Docker containers can bypass UFW for outbound
- Internal Docker network traffic not filtered by UFW

**Known Issue:**
- Docker-to-host traffic (`host.docker.internal`) works due to `extra_hosts`
- Host-to-Docker traffic works on published ports

---

## Critical Risks Summary

### 🔴 Requires 888_HOLD (Human Approval)

| Risk | Container | Action | Impact |
|------|-----------|--------|--------|
| Docker socket access | openclaw | Document policy or restrict | AGI capability |
| Root user | ollama, agent-zero | Add non-root user | Breaks if upstream requires root |
| No capability dropping | All containers | Add `--cap-drop ALL` | May break functionality |

### 🟡 Recommended (Lower Priority)

| Risk | Container | Action |
|------|-----------|--------|
| Read-write mounts | openclaw, agent-zero | Consider read-only for code mounts |
| No read-only rootfs | All containers | Test with read-only + tmpfs |

---

## 888_HOLD Actions Required

The following changes **MUST NOT** be applied without human approval:

1. **Add capability dropping** - May break containers
2. **Change container users** - May break upstream images
3. **Enable read-only rootfs** - Requires testing
4. **Modify firewall rules** - May lock out access
5. **Restrict docker.sock access** - Breaks AGI capabilities

---

## Next Steps

1. **Human review** of this document
2. **Test hardening** in staging environment
3. **Apply changes** one at a time with rollback plan
4. **Document** any issues in VPS_ARCHITECTURE_MASTER_DOSSIER.md

---

**Classification:** READ-ONLY AUDIT  
**Inspector:** Resident arifOS VPS Agent  
**Date:** 2026-03-03  

*Ditempa Bukan Diberi* 🔥

---

## 🔴 CRITICAL: docker-mcp Security Warning

### 888_HOLD Required

**Status:** `docker-mcp` is currently **ENABLED** in Kimi Code MCP config.

| Property | Value | Risk Level |
|----------|-------|------------|
| Execution | `npx -y docker-mcp` | Spawns Node.js process |
| User context | Runs as `root` (Kimi context) | 🔴 **CRITICAL** |
| Docker socket | `/var/run/docker.sock` accessible | 🔴 **RCE-grade channel** |
| Scope | **UNRESTRICTED** - can manage ANY container | 🔴 **CRITICAL** |
| Governance | **NOT routed through arifOS** | 🔴 **BYPASSES CONSTITUTION** |
| Audit logging | **NONE** | 🔴 **NO ACCOUNTABILITY** |

### Attack Vector

```
User → Kimi Code → docker-mcp → docker.sock → docker daemon → ANY container
                                              → host filesystem (via mounts)
                                              → network (via published ports)
```

**A malicious or confused prompt could:**
1. Delete all containers: `docker rm -f $(docker ps -aq)`
2. Expose secrets: `docker exec openclaw cat /home/node/.openclaw/.env`
3. Create privileged container: `docker run --privileged -v /:/host alpine`
4. Modify arifOS: `docker exec openclaw sh -c "echo 'evil' >> /mnt/arifos/some_file.py"`

### Required Actions (888_HOLD)

**Option A: Disable docker-mcp (RECOMMENDED)**
```bash
# Edit ~/.kimi/mcp.json
# Remove or comment out the docker-mcp entry
```

**Option B: Restrict scope (requires development)**
```bash
# Create a wrapper script that only allows safe commands
# /usr/local/bin/docker-mcp-restricted
#!/bin/bash
ALLOWED_COMMANDS="ps,images,logs,inspect,stats"
if [[ "$1" =~ ^($ALLOWED_COMMANDS) ]]; then
  docker "$@"
else
  echo "ERROR: Command not allowed. Use arifOS eureka_forge for write operations."
  exit 1
fi
```

**Option C: Route through arifOS (requires MCP client changes)**
- All Docker operations should go through `arifos-aaa` → `eureka_forge` tool
- This provides constitutional validation before execution
- Requires Kimi Code to be configured to use arifOS tools for Docker operations

### Current Decision

**Status:** 🟡 **ACKNOWLEDGED RISK - Human review required**

Until human approval:
- [ ] Monitor docker-mcp usage via process logging
- [ ] Document all docker-mcp invocations
- [ ] Consider this a "known vulnerability" in security posture

---

## MCP Server Trust Policy

### Trust Classification Framework

| Trust Level | Label | Description | Allowed Actions |
|-------------|-------|-------------|-----------------|
| 🔴 CRITICAL | `TRUST_CRITICAL` | Full system access | ONLY through arifOS governance |
| 🟠 HIGH | `TRUST_HIGH` | Write + exec, local | Must go through arifOS validation |
| 🟡 MEDIUM | `TRUST_MEDIUM` | Write but sandboxed | Documented, logged |
| 🟢 LOW | `TRUST_LOW` | Read-only, external | Safe for general use |

### Kimi MCP Servers - Trust Classification

| Server | Trust Level | Justification | Governance Path |
|--------|-------------|---------------|-----------------|
| arifos-aaa | 🟠 TRUST_HIGH | Constitutional kernel, forge access | Self-governing (F1-F13 floors) |
| codegraphcontext | 🟢 TRUST_LOW | Read-only code analysis | Direct (safe) |
| context7 | 🟢 TRUST_LOW | External API, context retrieval | Direct (no secrets) |
| **docker-mcp** | 🔴 **TRUST_CRITICAL** | **Docker daemon access** | **SHOULD BE THROUGH arifOS** |
| jina-reader | 🟢 TRUST_LOW | External API, web fetch | Direct (no secrets) |

### OpenClaw MCP Servers - Trust Classification

| Server | Trust Level | Justification | Governance Path |
|--------|-------------|---------------|-----------------|
| arifOS Bridge (arifos_judge) | 🟠 TRUST_HIGH | Constitutional validation | Self-governing |
| Internal tools (shell, file) | 🟠 TRUST_HIGH | Host access via docker.sock | Logged, should route through arifOS |

### Trust Policy Rules

1. **TRUST_CRITICAL servers MUST:**
   - Route all operations through arifOS `eureka_forge` tool
   - Have explicit scope limits documented
   - Require 888_HOLD approval to enable

2. **TRUST_HIGH servers SHOULD:**
   - Log all operations to VAULT999
   - Have human review for bulk operations
   - Respect constitutional floors

3. **TRUST_LOW servers CAN:**
   - Be used directly without governance
   - Only access public/external data
   - Not receive secrets or credentials

4. **Secrets Policy:**
   - NEVER send API keys to TRUST_LOW servers
   - NEVER send user data to external MCPs without consent
   - Constitutional secrets (VAULT999) ONLY through arifOS

---

## Firewall Reality Check

### UFW vs Docker

| Aspect | UFW Claims | Docker Reality | Gap? |
|--------|------------|----------------|------|
| Port 80 | ALLOW | Open (nginx) | ✅ OK |
| Port 443 | ALLOW | Open (nginx) | ✅ OK |
| Port 8000 | ALLOW | Open (coolify) | ✅ OK |
| Port 8080 | ALLOW | Open (arifOS) | ✅ OK |
| Port 3000 | NOT LISTED | Open (openclaw) | 🔴 **BYPASS** |
| Port 6333 | NOT LISTED | Open (qdrant) | 🔴 **BYPASS** |
| Port 11434 | NOT LISTED | Open (ollama) | 🔴 **BYPASS** |
| Port 50001 | NOT LISTED | Open (agent-zero) | 🔴 **BYPASS** |

**Finding:** Docker published ports (`0.0.0.0:PORT`) **BYPASS UFW**.

### DOCKER-USER Chain

```bash
Chain DOCKER-USER (1 references)
target     prot opt source               destination         
# EMPTY - No restrictions
```

**Risk:** All container ports are exposed to the internet without UFW filtering.

### Remediation Options (888_HOLD)

**Option A: Install ufw-docker**
```bash
wget -O /usr/local/bin/ufw-docker \
  https://raw.githubusercontent.com/chaifeng/ufw-docker/master/ufw-docker
chmod +x /usr/local/bin/ufw-docker
ufw-docker install
```

**Option B: Bind to localhost only**
```yaml
# docker-compose.yml
services:
  openclaw:
    ports:
      - "127.0.0.1:3000:18789"  # Only localhost
```

**Option C: Add DOCKER-USER rules**
```bash
# Only allow specific IPs to access container ports
iptables -I DOCKER-USER -i eth0 ! -s YOUR_IP -j DROP
```

---

## Updated Risk Summary

| Risk | Previous Level | Updated Level | Reason |
|------|---------------|---------------|--------|
| docker-mcp access | Not assessed | 🔴 **CRITICAL** | RCE-grade, bypasses governance |
| UFW bypass by Docker | Not assessed | 🔴 **HIGH** | Ports exposed without filtering |
| IP drift | Not assessed | 🟠 **MEDIUM** | IPs are DHCP, can change |

---

**Document Updated:** 2026-03-03  
**Gödel Boundary Added:** docker-mcp, UFW bypass, IP drift  
**Next Review:** After human approval of 888_HOLD items

*Ditempa Bukan Diberi* 🔥
