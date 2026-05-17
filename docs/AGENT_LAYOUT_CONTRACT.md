# AGENT_LAYOUT_CONTRACT — arifOS Federation

> **Status:** SOVEREIGN LAW | **Target:** All AI Agents (L1–L4) | **Authority:** 888_JUDGE

## 🏛️ Purpose
This contract defines the immutable structural grammar of the arifOS federation repositories. It prevents "Stochastic Entropy"—the tendency of AI agents to create root-level junk, duplicate configurations, and unreferenced artifacts.

## 🛠️ The Primordial Root Rule
The repository root is a **Low-Entropy Zone**. No agent shall create new files or folders at the root unless they fall into the **Sovereign Whitelist**:
- README.md (Orientation)
- LICENSE (Legal)
- pyproject.toml / package.json / uv.lock (Dependencies)
- .gitignore / .gitattributes (Git Config)
- GEMINI.md / CLAUDE.md (Agent SOT)
- Makefile / docker-compose.yml (Root Orchestration)
- .github/ (CI/CD)

**Any other root-level item is an Automatic Violation (VOID).**

## 📂 Directory Grammar
All other items MUST be placed according to the following semantic lattice:

| Path | Purpose | Content |
|------|---------|---------|
| src/ or {repo_name}/ | **Mind (Δ)** | Production runtime code. |
| docs/ | **Memory** | Human and agent documentation. |
| specs/ | **Governance** | Formal specifications, contracts, and manifests. |
| data/ | **Substrate** | Persistent state, JSON stores, and raw assets. |
| scripts/ | **Automation** | Internal tools, maintenance scripts, and one-offs. |
| 	ests/ | **Validation** | Unit, integration, and compliance tests. |
| deploy/ | **Forge (A)** | Dockerfiles, Caddyfiles, and orchestration logic. |
| rchive/ | **History** | Superseded files, historical backups, and logs. |

## 🚦 Execution Rules
1. **Move > Dump**: If you create a script, put it in scripts/. Do not leave it at root.
2. **Refactor > Duplicate**: Never create 2_config.yaml. Update the existing one or create a managed migration.
3. **Archive > Delete**: Never m a file with significant history. Move it to rchive/ and update the ROOT_ARCHIVE_MANIFEST.md.
4. **Path Hardening**: Always resolve paths relative to the project root or via environment variables. Brittle paths (e.g., ../../state.json) are prohibited.

## 🛡️ Pre-Commit Gate
All structural changes must pass the **"NO BANGANG" Checklist** (see docs/NO_BANGANG_CHECKLIST.md if available, otherwise refer to the global arifOS standard).

---
*Ditempa Bukan Diberi — Intelligence without order is chaos.*
**999 SEAL ALIVE**
