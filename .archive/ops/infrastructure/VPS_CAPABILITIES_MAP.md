# arifOS VPS — Capabilities Map

**Last verified:** 2026-03-24 by arifOS Gemini CLI  
**Reference:** [VPS_ARCHITECTURE.md](/opt/arifos/infrastructure/VPS_ARCHITECTURE.md)

> This file maps what the VPS can actually do right now, and which tools are truly reachable by agents. It distinguishes installed, mounted, and working.

---

## 1. Core Agent Stack

| Component | State | Reachability | Notes |
| :--- | :--- | :--- | :--- |
| `arifosmcp` | healthy | public + internal | canonical MCP brain |
| **OpenClaw** | healthy | internal + Telegram path | main executive agent gateway |
| **Agent Zero** | healthy | internal | autonomous reasoning |
| **n8n** | healthy | routed | workflow automation |
| **Ollama** | healthy | internal | local model runtime |
| **Qdrant** | healthy | internal | vector memory |
| **Browserless** | healthy | internal | browser automation |
| **Prometheus** | healthy | internal | metrics |
| **Grafana** | healthy | routed | dashboards |

---

## 2. Public MCP Capabilities

Live `arifosmcp` reports:

- status: `healthy`
- version: `2026.03.24-FORGED`
- transport: `SSE / streamable-http`
- tools loaded: `14`
- authentication: `F11 Bootstrap (Anchored)`

### Public MCP Tools (Trinity Surface)

- `init_anchor` : F11 Identity Continuity (Bootstrap)
- `arifOS_kernel` : Full Constitutional Pipeline (000-999)
- `apex_soul` : Ψ Final Judgment & Sovereign Override
- `mind_reason` : Δ AGI Reasoning & Truth Grounding
- `heart_memory` : Ω ASI Empathy & Vector Persistence
- `search_reality` : Web Grounding (Brave/Jina)
- `ingest_evidence` : Multi-modal Evidence Extraction
- `reality_atlas` : Semantic Evidence Graph
- `check_vital` : System Health & Capabilities
- `audit_rules` : Governance Floor Inspection
- `session_memory` : Session-specific State Management
- `verify_vault_ledger` : Merkle-chain Integrity (VAULT999)
- `open_apex_dashboard` : Visual Operations Ops
- `reality_dossier` : 3E Telemetry Decoder

---

## 3. Security Shield Status

| Component | Status | Config |
| :--- | :--- | :--- |
| **UFW Firewall** | Active | Ports 22, 80, 21, 443 |
| **Fail2ban** | Active | SSH jail enabled |
| **SSH Auth** | Hardened | Keys-Only (Passwords DISABLED) |
| **SSO Spine** | Pending | Planned: Authentik |

---

## 4. Host Toolchain Inventory

| Tool | Version | Host status |
| :--- | :--- | :--- |
| `docker` | 24.0.7 | healthy |
| `python3` | 3.12.3 | healthy |
| `pip` | 24.0 | healthy |
| `node` | v20.19.4 | present |
| `npm` | 10.8.2 | present |

---

## 5. Storage State

- **Disk Capacity:** 193GB
- **Available Space:** 85GB
- **Persistence:** Volumes mapped to `/opt/arifos/data`
