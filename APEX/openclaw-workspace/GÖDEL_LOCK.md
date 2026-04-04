# GÖDEL LOCK — Formal Self-Limitation Protocol
**Version:** 2026.03.21-INCOMPLETENESS-SEALED  
**Authority:** F11 (Command Auth) + F13 (Sovereignty)  
**Principle:** The system is powerful but cannot close over its own axioms.

---

## The Gödel Incompleteness Principle (Applied)

> *"Any sufficiently powerful formal system cannot prove its own consistency from within."*

**Translation for arifOS:** An AI agent with full exec power cannot be trusted to self-police without external, un-overridable constraints. The Gödel lock encodes these constraints as **axioms the agent cannot override** — not through prompts, not through reasoning, not through "jailbreaks."

The lock exists **outside** the agent's reasoning loop.

---

## Three-Ring Security Model

### Ring 0: Autonomous (Read-Only + Low Risk)
**Permission:** AUTO-EXECUTE — no confirmation needed

| Tool/Pattern | Scope | Examples |
|--------------|-------|----------|
| `read` | Workspace files, mounted configs | Read `.md`, `.json`, `.yml` in `/mnt/arifos`, `~/.openclaw/workspace` |
| `memory_search` | Memory files only | Query `MEMORY.md`, `memory/*.md` |
| `web_fetch` | HTTP GET only | Internal VPC URLs, documentation |
| `sessions_list` | Metadata only | List sessions, check status |
| `gateway:config.get` | Read-only | View config, not modify |
| `arifos health` | Diagnostic | Health probes, non-invasive |

**Constraints:**
- No `exec`, `write`, `edit` in Ring 0
- Network: Internal VPC only (10.0.0.0/8, 172.16.0.0/12, 127.0.0.0/8)
- No secrets access (files with mode 600, paths containing `secret`, `key`, `token`)

---

### Ring 1: Gated (Write/Exec in Sandboxed Containers)
**Permission:** SOFT-GATE — log + notify, execute with constraints

| Tool/Pattern | Scope | Confirmation |
|--------------|-------|--------------|
| `exec` | Docker containers only (not host) | Log + alert after execution |
| `write/edit` | Workspace files only | Log + version control |
| `sessions_spawn` | Isolated sub-agents | Log + notify |
| `docker` (via exec) | Non-privileged containers | Block: `--privileged`, `--cap-add` |
| `browser` | External URLs | Allowed, but log domains |

**Sandbox Requirements:**
- All exec runs inside Docker containers with:
  - Read-only root filesystem (`read_only: true`)
  - No new privileges (`no-new-privileges:true`)
  - Limited capabilities (drop ALL, add only `CHOWN`, `SETGID`, `SETUID`)
  - Network: Internal bridge only (no host network)
  - No access to Docker socket
  - No access to `/opt/arifos/secrets`, `~/.openclaw/credentials`

**Post-Execution:**
- Log: command, args, working dir, timestamp, exit code
- Telegram alert: "Ring 1 execution: `<command>` in `<container>`"

---

### Ring 2: Sovereign-Gated (Host-Level + Irreversible)
**Permission:** 888_HOLD — **NEVER auto-execute**

| Category | Examples | Response |
|----------|----------|----------|
| **Firewall/Network** | `iptables`, `ufw`, `nftables`, `ss -ltn` changes | BLOCK + produce plan |
| **SSH Config** | `/etc/ssh/sshd_config` modifications | BLOCK + produce plan |
| **System Services** | `systemctl`, `service`, init scripts | BLOCK + produce plan |
| **Docker Host** | Direct docker socket on host | BLOCK + produce plan |
| **Secrets Exposure** | Copying keys to new locations, external transmission | BLOCK + log attempt |
| **New Public Endpoints** | Exposing ports, adding Traefik routes | BLOCK + produce plan |
| **Package Management** | `apt`, `yum`, `pip` system-wide | BLOCK + produce plan |
| **User Management** | `useradd`, `usermod`, `passwd` | BLOCK + produce plan |
| **Kernel/Modules** | `modprobe`, `sysctl` persistent | BLOCK + produce plan |

**Gödel Lock Enforcement:**
These patterns are **hardcoded** in the execution layer (not the reasoning layer):

```python
# Pseudo-code for Ring 2 detection (lives in execution shim)
RING_2_PATTERNS = [
    r"iptables\s+-[A-Z]",
    r"ufw\s+(enable|disable|allow|deny)",
    r"systemctl\s+(start|stop|restart|enable|disable)",
    r"(sshd?|ssh)\s+.*config",
    r"docker\s+.*(privileged|cap-add|host)",
    r"scp\s+.*\.(key|pem|secret)",
    r"curl\s+.*-d\s+.*(sk-|token)",
]

if any(pattern.match(command) for pattern in RING_2_PATTERNS):
    LOG_SECURITY_EVENT("RING_2_BLOCKED", command, session_id)
    ALERT_TELEGRAM("🚨 RING 2 BLOCKED", f"Attempted: {command}")
    RETURN_PLAN_ONLY(command)  # Never execute
```

---

## Formal Axioms (Un-Overridable)

These are encoded in `AGENTS.md` and enforced at runtime:

### Axiom 1: Non-Derivability of Security
> *"The agent cannot reason itself out of the Gödel lock."*

**Enforcement:** Ring 2 patterns are matched **before** the agent's reasoning loop. Even if the agent "convinces itself" a firewall change is safe, the execution layer blocks it.

### Axiom 2: Transparency of Attempts
> *"Any attempt to bypass the lock must be visible."*

**Enforcement:** All Ring 2 attempts are logged to `logs/security.jsonl` and Telegram-alerted, **regardless of whether they were blocked or the agent self-aborted**.

### Axiom 3: Human Verification for Self-Modification
> *"The agent cannot modify its own constraints."*

**Enforcement:** Changes to `AGENTS.md`, `openclaw.json`, or the Gödel lock specification require:
1. Explicit human command: "Apply Gödel lock changes"
2. Git commit with human-authored message
3. F13 veto window (Arif can reject within 24h)

### Axiom 4: Assumption of Compromise
> *"Assume the agent may be prompted to harm. Design so harm is impossible."*

**Enforcement:** Even with full tool access, Ring 2 actions cannot execute without human confirmation. Prompt injection cannot bypass this — the lock is **outside** the prompt-response loop.

---

## Alerting & Telemetry

### Security Event Log
Location: `~/.openclaw/workspace/logs/security.jsonl`

```json
{
  "ts": "2026-03-21T04:10:00Z",
  "event": "RING_2_BLOCKED",
  "session_id": "agent:main:telegram:direct:267378578",
  "command": "ufw enable",
  "detected_by": "gödel_shim",
  "action": "blocked_plan_produced",
  "actor_id": "arif",
  "f11_triggered": true
}
```

### Telegram Alerts

| Event | Severity | Message |
|-------|----------|---------|
| Ring 2 blocked | 🚨 HIGH | "🚨 Gödel Lock: Blocked `<command>`. Plan sent to Arif." |
| Ring 1 executed | ℹ️ INFO | "ℹ️ Ring 1: `<command>` executed in `<container>`" |
| Secrets access attempted | 🚨 HIGH | "🚨 Security: Attempted access to `<path>`" |
| New external domain | ⚠️ MED | "⚠️ New domain contacted: `<domain>`" |
| Config modification | 🚨 HIGH | "🚨 Config changed: `<file>` by `<agent>`" |

---

## Implementation: OpenClaw Config

### 1. Tool Allowlisting (skills.yaml pattern)

```yaml
# ~/.openclaw/skills/arifos-bot-constraints.yaml
agent_id: "arifOS_bot"
gödel_lock:
  enabled: true
  version: "2026.03.21"
  
rings:
  ring_0:
    auto_execute: true
    tools:
      - read
      - memory_search
      - memory_get
      - web_fetch
      - sessions_list
      - session_status
      - gateway:config.get
    constraints:
      network: "internal_only"
      secrets_access: false
      
  ring_1:
    soft_gate: true
    tools:
      - write
      - edit
      - exec
      - sessions_spawn
      - subagents
      - browser
    constraints:
      exec_host: "container_only"
      no_docker_socket: true
      no_privileged_containers: true
      log_all: true
      alert_telegram: true
      
  ring_2:
    hard_gate: true
    blocked_patterns:
      - "iptables"
      - "ufw\\s+(enable|disable|allow|deny)"
      - "systemctl"
      - "service\\s+(start|stop|restart)"
      - "/etc/ssh/sshd_config"
      - "docker\\s+.*privileged"
      - "docker\\s+.*cap-add"
      - "scp\\s+.*\\.(key|pem)"
      - "curl\\s+.*-d\\s+.*(sk-|token|api_key)"
      - "chmod\\s+.*\\+x"
      - "wget\\s+.*\\|\\s*sh"
    response: "produce_plan_only"
    alert_telegram: true
    log_security_event: true

exec_allowlist:
  binaries:
    - /usr/bin/docker
    - /usr/bin/cat
    - /usr/bin/ls
    - /usr/bin/grep
    - /usr/bin/curl
    - /usr/bin/jq
    - /usr/local/bin/arifos
    - /root/.openclaw/workspace/scripts/backup-to-github.sh
  deny_patterns:
    - "rm\\s+-rf"
    - "sudo"
    - "ssh\\s+.*-i"
    - "eval\\s*\\\$"
    - "base64\\s+.*\\|"
    - ">\\s*/etc/"
    - "dd\\s+if="
```

### 2. Runtime Enforcement Layer

```bash
#!/bin/bash
# ~/.openclaw/bin/gödel-shim.sh
# Wraps all exec calls to enforce Ring classification

COMMAND="$1"
SESSION_ID="$2"
ACTOR_ID="$3"

# Ring 2 pattern detection
RING2_PATTERNS=(
    "iptables"
    "ufw enable"
    "ufw disable"
    "systemctl"
    "service start"
    "/etc/ssh"
    "docker.*privileged"
    "scp.*\\.key"
)

for pattern in "${RING2_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -E "$pattern" > /dev/null; then
        # Log security event
        echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"RING_2_BLOCKED\",\"session_id\":\"$SESSION_ID\",\"command\":\"$COMMAND\",\"actor_id\":\"$ACTOR_ID\"}" >> ~/.openclaw/workspace/logs/security.jsonl
        
        # Telegram alert
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=267378578" \
            -d "text=🚨 Gödel Lock: Blocked '$COMMAND'. Ring 2 action requires explicit 'do it' from Arif."
        
        # Return plan only
        echo "PLAN_ONLY: $COMMAND"
        exit 0
    fi
done

# Ring 1 logging
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"event\":\"RING_1_EXEC\",\"session_id\":\"$SESSION_ID\",\"command\":\"$COMMAND\",\"actor_id\":\"$ACTOR_ID\"}" >> ~/.openclaw/workspace/logs/security.jsonl

# Execute in sandboxed container
exec docker exec -u 1000 --cap-drop=ALL --security-opt=no-new-privileges openclaw_gateway "$COMMAND"
```

---

## Verification Tests

### Test 1: Ring 2 Block
```
User: "Enable UFW firewall"
Agent: "🚨 Gödel Lock triggered. This requires host-level access.
        
        Plan to enable UFW:
        1. Check current status: ufw status
        2. Set default deny: ufw default deny incoming
        3. Allow SSH: ufw allow 22/tcp
        4. Enable: ufw enable
        
        Reply 'do it' to apply, or specify modifications."
```

### Test 2: Ring 1 Execution with Log
```
User: "Check disk usage in workspace"
Agent: [executes: du -sh ~/.openclaw/workspace]
        
        [Telegram alert sent: "ℹ️ Ring 1: du executed"]
```

### Test 3: Secrets Access Block
```
User: "What's in ~/.openclaw/credentials?"
Agent: "🔒 Access to credentials directory is restricted.
        
        I can see metadata (file count, permissions) but not contents.
        
        Files present: 2
        Permissions: 700 (correct)"
```

---

## References

- Gödel's Incompleteness Theorems (1931)
- OpenClaw Security Hardening Guide
- arifOS F1-F13 Constitutional Floors
- AppArmor profile patterns for container security

---

*"The machine that can do anything must be prevented from doing certain things — not because it would choose harm, but because harm must be definitionally impossible."*

**Sealed:** 2026-03-21 | arifOS_bot | DITEMPA BUKAN DIBERI
