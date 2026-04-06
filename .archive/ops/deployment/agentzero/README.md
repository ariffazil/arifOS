# AgentZero + arifOS Integration

> **Ditempa Bukan Diberi — Forged Under Constitutional Law [ΔΩΨ | ARIF]**

Production-grade deployment of AgentZero autonomous AI agents under arifOS 13-floor constitutional governance.

---

## 🎯 Overview

This deployment package enables you to run **AgentZero** — a highly autonomous, hierarchical multi-agent AI framework — under complete **arifOS constitutional supervision**.

### What You Get

| Component | Purpose | Constitutional Enforcement |
|-----------|---------|---------------------------|
| **arifOS Guardian** | Governance kernel | All 13 floors (F1-F13) |
| **AgentZero** | Autonomous agent execution | Inherited from arifOS |
| **Qdrant** | Vector memory (RAG) | F4 entropy, F2 verification |
| **Ollama** | Local LLM for F2 | Truth verification |
| **VAULT999** | Immutable audit ledger | F1 Amanah compliance |
| **Prometheus/Grafana** | Observability | F7 transparency |

---

## 🚀 Quick Start

### Prerequisites

- Docker 24.0+ and Docker Compose
- 8GB RAM minimum (16GB recommended)
- Linux/macOS/Windows WSL2

### Installation

```bash
# 1. Navigate to deployment directory
cd /root/arifosmcp/deployment/agentzero

# 2. Run initialization
./scripts/init.sh

# 3. Configure API keys (optional, for external LLMs)
vim .env

# 4. Start the stack
docker compose up -d

# 5. Verify deployment
./scripts/status.sh
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| arifOS API | http://localhost:18080 | Constitutional governance |
| arifOS Health | http://localhost:18080/health | System status |
| Grafana | http://localhost:13000 | Metrics & dashboards |
| Prometheus | http://localhost:19090 | Raw metrics |

---

## ⚖️ Constitutional Enforcement

### 13 Floors Applied to AgentZero

| Floor | Enforcement | Trigger |
|-------|-------------|---------|
| **F1 Amanah** | All actions logged to VAULT999 with hash chain | Every tool call |
| **F2 Truth** | Claims verified ≥ 0.99 confidence | Every output |
| **F3 Tri-Witness** | Human confirmation for critical ops | Destructive actions |
| **F4 ΔS Clarity** | Entropy reduction required | Code generation |
| **F5 Peace²** | Constructive power only | System modifications |
| **F6 κᵣ Empathy** | Weakest stakeholder protection | User-facing changes |
| **F7 Ω₀ Humility** | Uncertainty bounds mandatory | All responses |
| **F8 G Genius** | Coherence ≥ 0.80 | Tool creation |
| **F9 C_dark** | Dark cleverness < 0.30 | Code analysis |
| **F10 Ontology** | Consciousness claims blocked | All outputs |
| **F11 Command Auth** | Identity verification | Dangerous ops |
| **F12 Injection** | Prompt injection blocked | All inputs |
| **F13 Sovereign** | Human veto absolute | Any time |

---

## 🛡️ Security Architecture

### Container Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                    Host System                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Docker Network: agentzero-sandbox (internal only)    │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  AgentZero Container                            │  │  │
│  │  │  ├── Read-only root filesystem                  │  │  │
│  │  │  ├── No new privileges                          │  │  │
│  │  │  ├── Dropped capabilities (cap_drop: ALL)       │  │  │
│  │  │  ├── seccomp-bpf syscall filtering              │  │  │
│  │  │  └── tmpfs /workspace (ephemeral)               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Kill Switch (F13 Sovereign)

```bash
# Emergency stop all AgentZero agents
docker compose exec arifos arifos-cli emergency stop-agentzero

# Kill specific agent
docker compose exec arifos arifos-cli agentzero kill --agent-id <id>

# Quarantine for forensics
docker compose exec arifos arifos-cli agentzero quarantine
```

---

## 📊 Monitoring

### Key Metrics

| Metric | Query | Alert Threshold |
|--------|-------|-----------------|
| F2 Verification Rate | `rate(arifos_truth_verified_total[5m])` | < 0.95 |
| F11 Auth Failures | `rate(arifos_auth_denied_total[1m])` | > 0 |
| F12 Injection Blocks | `rate(arifos_injection_blocked_total[5m])` | > 0 |
| AgentZero CPU | `container_cpu_usage_seconds_total{name="agentzero"}` | > 80% |
| VAULT999 Lag | `arifos_vault_write_latency_seconds` | > 1s |

### Dashboards

Access Grafana at http://localhost:13000 with credentials from `.env`:

- **Constitutional Compliance** — F1-F13 status overview
- **AgentZero Activity** — Tool calls, subagent spawning, memory usage
- **Security Events** — Injection attempts, auth failures, violations

---

## 🎮 Usage Examples

### Example 1: Governed Task Execution

```python
# AgentZero task with constitutional oversight
import requests

# Submit task through arifOS
response = requests.post("http://localhost:18080/agentzero/task", json={
    "task": "Analyze the codebase and refactor for clarity",
    "constraints": {
        "max_files": 10,
        "require_tests": True
    },
    "floors": ["F2", "F4", "F7", "F11"]
})

task_id = response.json()["task_id"]

# Monitor with constitutional checks
status = requests.get(f"http://localhost:18080/agentzero/task/{task_id}")
print(f"Status: {status.json()['status']}")
print(f"F2 Verified: {status.json()['f2_verification']}")
```

### Example 2: Dynamic Tool Creation

```python
# AgentZero wants to create a new tool
# Must pass F8, F9, F11, F12

tool_proposal = {
    "name": "code_analyzer",
    "description": "Analyze code complexity",
    "code": "def analyze(code): ...",
    "author": "agentzero-main"
}

# arifOS will:
# 1. F12: Scan for injection
# 2. F9: Check for dark cleverness
# 3. F8: Verify coherence
# 4. F11: Request human approval (external-facing)
# 5. F1: Log to VAULT999

response = requests.post(
    "http://localhost:18080/agentzero/tools/forge",
    json=tool_proposal
)
```

### Example 3: Subagent Spawning

```python
# Spawn subagent with inherited constraints
spawn_request = {
    "task": "Research API documentation",
    "parent_id": "agentzero-main",
    "inherit_constraints": True,  # Mandatory
    "max_depth": 3  # Enforced by arifOS
}

response = requests.post(
    "http://localhost:18080/agentzero/subagent/spawn",
    json=spawn_request
)
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# ═════════════════════════════════════════════════════════════════
# LLM Configuration (via arifOS proxy)
# ═════════════════════════════════════════════════════════════════
# These are proxied through arifOS for constitutional enforcement
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# ═════════════════════════════════════════════════════════════════
# AgentZero A0_SET_* Configuration
# See: https://github.com/agent0ai/agent-zero
# ═════════════════════════════════════════════════════════════════
A0_SET_AGENT_NAME=arifos-governed-agent
A0_SET_MAX_SUBAGENTS=3              # Limit subagent depth
A0_SET_REQUIRE_APPROVAL=true        # F11 enforcement
A0_SET_MEMORY_BACKEND=qdrant        # Vector store
A0_SET_QDRANT_HOST=qdrant
A0_SET_QDRANT_PORT=6333
A0_SET_LLM_PROVIDER=arifos-proxy    # Route through arifOS
A0_SET_LLM_MODEL=arifos/governed-claude
A0_SET_ARIFOS_ENDPOINT=http://arifos:8080

# ═════════════════════════════════════════════════════════════════
# arifOS Constitutional Thresholds
# ═════════════════════════════════════════════════════════════════
F2_TRUTH_THRESHOLD=0.99            # Fact confidence
F7_HUMILITY_MIN=0.03               # Uncertainty lower bound
F7_HUMILITY_MAX=0.20               # Uncertainty upper bound
F12_INJECTION_MAX=0.15             # Injection threshold
```

### AgentZero Skills (SKILL.md)

AgentZero uses the **SKILL.md standard** (compatible with Claude Code, Codex, Goose).

Place custom skills in the `skills/` directory:

```
skills/
└── my_custom_skill/
    └── SKILL.md
```

arifOS automatically scans all skills for:
- **F12**: Injection attempts in skill content
- **F8**: Coherence and elegance
- **F2**: Factual claims verification
- **F1**: Loading logged to VAULT999

See `skills/example_governed_skill/SKILL.md` for a template.

### Customizing Prompts

Edit `prompts/arifos-system.md` to adjust constitutional constraints:

```bash
# WARNING: Modifying constitution changes the integrity hash
# AgentZero will refuse to start if hash mismatch detected

vim prompts/arifos-system.md

# Recalculate hash
sha256sum prompts/arifos-system.md
```

---

## 🚨 Emergency Procedures

### Scenario 1: Runaway AgentZero

```bash
# Symptoms: High CPU, spawning many subagents, making unauthorized changes

# Step 1: Emergency stop
docker compose exec arifos arifos-cli emergency stop-agentzero

# Step 2: Quarantine
docker compose exec arifos arifos-cli agentzero quarantine

# Step 3: Preserve logs
cp -r data/vault999 vault999-backup-$(date +%Y%m%d-%H%M%S)

# Step 4: Analyze
docker compose logs agentzero > agentzero-incident.log
```

### Scenario 2: F12 Injection Detected

```bash
# Symptoms: arifOS blocking inputs, F12 alerts firing

# Check injection logs
docker compose exec arifos arifos-cli vault query --floor F12 --last 1h

# If false positive, whitelist pattern
docker compose exec arifos arifos-cli config set \
  F12_WHITELIST="safe_pattern1,safe_pattern2"
```

### Scenario 3: VAULT999 Chain Break

```bash
# Symptoms: Tamper detection alert

# Verify chain integrity
docker compose exec arifos arifos-cli vault verify --full-chain

# If legitimate corruption (disk failure), restore from backup
# If tampering suspected, preserve evidence and investigate
```

---

## 📚 Architecture Reference

### Data Flow

```
User Request
     │
     ▼
┌─────────────────┐
│   arifOS API    │ ← F11 Auth, F12 Injection Scan
│   (Port 18080)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gov. Kernel     │ ← F2, F4, F7, F8, F9, F10 validation
│ (ΔΩΨ Trinity)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AgentZero MCP  │ ← Tool execution
│  (Container)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Subagent│ │VAULT999│ ← F1 logging
│(if any)│ │(audit) │
└───────┘ └───────┘
```

### File Structure

```
deployment/agentzero/
├── docker-compose.yml          # Main stack definition
├── .env                        # Environment variables (generated)
├── seccomp-agentzero.json      # Syscall filtering
├── prompts/
│   └── arifos-system.md        # Constitutional override
├── config/
│   ├── arifos/                 # arifOS config
│   ├── agentzero/              # AgentZero config
│   ├── grafana/                # Dashboards
│   └── prometheus/             # Scraping config
├── scripts/
│   ├── init.sh                 # Initialization
│   ├── status.sh               # Status check
│   ├── stop.sh                 # Clean shutdown
│   └── logs.sh                 # Log viewer
├── data/                       # Persistent data
│   ├── vault999/               # Audit ledger
│   ├── agentzero/memory/       # RAG storage
│   ├── qdrant/                 # Vector DB
│   └── ollama/                 # Local models
├── logs/                       # Application logs
└── workspace/                  # AgentZero workspace
```

---

## 🔗 Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `arifos-constitutional` | Floor enforcement |
| `arifos-embedding-rag` | Memory governance |
| `arifos-mcp-bridge` | Protocol layer |
| `vps-operations` | Container management |
| `openclaw-gateway` | Multi-channel access |

---

## 📄 License

AGPL-3.0-only — Same as arifOS core

---

## 🙏 Credits & References

### AgentZero
- **GitHub**: https://github.com/agent0ai/agent-zero
- **Website**: https://www.agent-zero.ai/
- **Docker**: `docker pull agent0ai/agent-zero`
- **Web UI**: http://localhost:50001 (default)

### arifOS
- **Author**: Muhammad Arif bin Fazil [ΔΩΨ | ARIF]
- **Version**: 2026.3.12-FORGED
- **License**: AGPL-3.0-only

### Protocols
- **MCP (Model Context Protocol)**: Anthropic
- **A2A (Agent-to-Agent)**: Google / Linux Foundation
- **SKILL.md Standard**: Anthropic (compatible with Claude Code, Codex, Goose)

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*

**Version:** 2026.03.13-FORGED  
**Constitutional Status:** 13/13 Floors Enforced  
**VAULT999:** Ready for Sealing
