# ARIFFAZIL_EXTERNAL_MCP_DOSSIER.md
**Version:** v1.1.0-BLUEPRINT  
**Authority:** Muhammad Arif bin Fazil (888_JUDGE)  
**Status:** CANON_GOVERNANCE  
**Motto:** *Standardized Interface | Layered Responsibility | Zero Chaos*

---

## ⚓ 1. OVERVIEW
This dossier establishes the official blueprint for the **ariffazil Global MCP Stack**. It serves as the single reference for all workspaces within the ecosystem, ensuring that every tool added to the Antigravity global configuration conforms to the 3-tier governance model of arifOS.

The goal is to provide a lean, high-utility surface for research, code, deployment, data, and controlled execution while preventing local configuration drift and unauthorized dynamic discovery side-effects.

---

## 🧠 2. KERNEL MCPs (The Engine)
These servers form the core cognitive and environmental boundary of arifOS.

| Server | Role | Primary Function |
| :--- | :--- | :--- |
| **arifos** | Constitutional | Enforces F1-F13 governance and sovereign signatures. |
| **memory** | Persistence | Provides long-term continuity across agent sessions. |
| **sequential-thinking** | Reasoning | Structures complex problem-solving into logical steps. |
| **filesystem** | Boundary | Provides bounded access to project roots and documents. |
| **meyhem** | Oracle | Read-only discovery for new capabilities (Candidate-only). |
| **time** | Temporal | Essential temporal reasoning and timestamping for autonomous agents. |

---

## ⚙️ 3. EXTERNAL MCPs (Ops & Intelligence)
These layers provide the active tools for state transformation and reality acquisition.

### Tier 2: OPS (Execution & Deployment)
- **github-official**: Authoritative source for repository state, issues, and PR management.
- **PostgresMCP**: Primary datastore for structured reality state (replacing Supabase overlap).
- **playwright**: Browser automation for testing and dynamic web state acquisition.
- **desktop-commander**: High-privilege OS bridge (Restricted with `--no-onboarding`).
- **cloudflare-workers**: Primary deployment path for edge-runtime code (selected over Railway).

### Tier 3: INTELLIGENCE (Knowledge & Retrieval)
- **brave-search**: Live web reality acquisition.
- **context7**: External witness for library documentation and technical truths.
- **perplexity**: Research synthesis and deep search amplification.
- **exa-search**: Semantic discovery for high-density information.
- **notion**: Persistent personal and operational knowledge base.

---

## 🚦 4. KEEP / ADD / DEFER / REMOVE
To maintain system order (F4 Clarity), the stack is managed according to the following lifecycle:

### ✅ KEEP (Baseline Baseline)
*Essential for daily sovereign operations:*
`arifos`, `memory`, `sequential-thinking`, `filesystem`, `meyhem`, `time`, `github-official`, `PostgresMCP`, `playwright`, `cloudflare-workers`, `desktop-commander`, `brave-search`, `context7`, `perplexity`, `exa-search`, `notion`.

### ➕ ADD (Future Growth)
*Integrate only when capability gap is identified:*
- **telegram**: If requiring real-time operational chat control.
- **openapi-swagger**: For mapping external service explosions.
- **Supabase**: Only if transitioning from local Postgres to cloud scalability.

### ⏳ DEFER (Under Review)
*Deferred to reduce system entropy:*
- **DockerMCP**: Currently deferred pending specialized container needs.
- **JinaMCP**: Deferred; Brave + Perplexity + Exa is the current primary Intelligence set.

### 🗑️ REMOVE (Redundant/Legacy)
- `GitKraken`, `time` (legacy version), `fetch`, `railway`, `time` (redundant variants).

---

## 🛡️ 5. RISK AND GUARDRAILS (F8/F13)
All external MCP usage must adhere to the following hard rules:

1.  **Zero Auto-Attach**: No server found via `meyhem` may be mounted without an explicit JSON config update and manual "SEAL" signature.
2.  **Denied Paths**: `filesystem` and `desktop-commander` MUST exclude system directories (`C:\Windows`, `.ssh`, `.env`).
3.  **Amanah (F1)**: All irreversible operations (PR merges, DB drops, file deletions) REQUIRE human sovereign intervention.
4.  **No Drift**: Global `C:\Users\User\.gemini\antigravity\mcp_config.json` is the sole source of truth.

---

## 🔄 6. ROLLBACK AND VERSIONING
- **Global Config Path**: `C:\Users\User\.gemini\antigravity\mcp_config.json`
- **Backup Snapshot**: `mcp_config.20260324_023330.bak.json`
- **Rollback Path**: Restore the backup file to `mcp_config.json` and refresh the MCP server list in Antigravity / Claude Code / Gemini CLI.

*DITEMPA BUKAN DIBERI — [ARIF OS SOVEREIGN BLUEPRINT]*
