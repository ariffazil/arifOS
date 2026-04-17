# arifOS Repository Structure

> **DITEMPA BUKAN DIBERI** — Forged, Not Given  
> This document maps the canonical layout of the arifOS repository.

## Philosophy

The root directory is intentionally minimal to reduce cognitive load. Files at root represent **Source of Truth (SoT)** — the immutable law and core identity of arifOS. Everything else is organized into semantic directories.

---

## Root Directory (SoT + Core)

| File/Directory | Purpose | SoT Level |
|----------------|---------|-----------|
| `README.md` | Primary narrative, quickstart, civilization entrypoint | **PRIMARY** |
| `AGENTS.md` | Governance rules, SoT hierarchy, agent behavior contract | **PRIMARY** |
| `LICENSE` | AGPL-3.0-only — legal foundation | **PRIMARY** |
| `pyproject.toml` | Package manifest, dependencies, entrypoints | **PRIMARY** |
| `requirements.txt` | Runtime dependencies | **PRIMARY** |
| `CHANGELOG.md` | Version history, release timeline | **PRIMARY** |
| `ROADMAP.md` | Future direction, horizon planning | **PRIMARY** |
| `000-999-implementation-plan.md` | Constitutional pipeline specification | **PRIMARY** |
| `SEALING_CHECKLIST.md` | Release criteria, quality gates | **PRIMARY** |
| `VAULT999_4LAYER_IMPLEMENTATION_SUMMARY.md` | Core architecture documentation | **PRIMARY** |

### Code Directories at Root

| Directory | Purpose |
|-----------|---------|
| `core/` | Kernel logic — governance engine, floors F1-F13, judgment |
| `tools/` | MCP tool implementations (9+1 architecture) |
| `config/` | Canonical config schemas, SoT fields, `/health` metadata |
| `memory/` | Governed memory — vector stores, VAULT999 hooks |
| `arifosmcp/` | **Runtime shell** — MCP server, HTTP endpoints, transport layer |
| `infrastructure/` | K8s manifests, host-level infrastructure |
| `deployments/` | Concrete deployment descriptors per environment |

### Constitutional Directories at Root

| Directory | Purpose |
|-----------|---------|
| `000/` | Constitutional law — Floors F1-F13, K000 theory |
| `333/` | APEX canon — judgment, sealing, VAULT specifications |
| `VAULT999/` | Immutable ledger implementation |

---

## Documentation Organization (`docs/`)

### `docs/deployment/` — Operations & Deployment
Deployment artifacts, scripts, and environment configurations.

| File | Purpose |
|------|---------|
| `DEPLOYMENT_A_FORGE.md` | AF.FORGE deployment specification |
| `DEPLOYMENT_CONTRAST_ANALYSIS.md` | Deployment comparison analysis |
| `DEPLOYMENT_READINESS_REPORT.md` | Pre-deployment checklist |
| `DEPLOYMENT_V2_PLAN.md` | Version 2 deployment roadmap |
| `DEPLOY_CHART_A_FORGE.sh` | Deployment automation script |
| `DEPLOY_FAST.sh` | Quick deployment script |
| `DEPLOY_CONFIG.md` | Deployment configuration reference |

### `docs/reports/` — Operational Reports
Audit reports, test results, and analysis documents.

| File | Purpose |
|------|---------|
| `AUDIT_REPORT_2026-04-06.md` | Constitutional audit results |
| `EXTERNAL_CORPUS_REVIEW.md` | External data review |
| `external_corpus_analysis.json` | Structured corpus analysis |
| `TEST_REPORT_HORIZON_II_1.md` | Test execution report |
| `CLEAN_OUTPUT_MIGRATION_SUMMARY.md` | Migration post-mortem |

### `docs/runbooks/` — Runbooks & Maps
Operational guides, process documentation, and living documents.

| File | Purpose |
|------|---------|
| `DOCUMENTATION_UPDATE_MAP.md` | Docs maintenance guide |
| `NAMESPACE_UNIFICATION_MAP.md` | Namespace consolidation plan |
| `TG-OPTIMIZE-PROMPT.md` | Telegram optimization guide |
| `TODO.md` | Active task tracking |
| `MEMORY.md` | Project memory/context |
| `HEARTBEAT.md` | Health check specifications |

### `docs/releases/` — Release Documentation
Release notes and version announcements.

| File | Purpose |
|------|---------|
| `RELEASE_NOTES_2026.04.06.md` | v2026.04.06 release notes |

---

## Agent Client Configuration (Dotfolders)

These directories contain IDE/editor-specific configurations for agent workflows. They are **integration scaffolds**, not SoT.

| Directory | Purpose | Integration |
|-----------|---------|-------------|
| `.claude/` | Claude Desktop/IDE configuration | Anthropic |
| `.cursor/` | Cursor IDE settings | Cursor |
| `.gemini/` | Gemini/Gemini CLI config | Google |
| `.vscode/` | VS Code workspace settings | Microsoft |
| `.agents/` | Generic agent workflow definitions | Various |
| `.arifos/` | arifOS-specific tooling config | Internal |

---

## Configuration Files at Root

| File | Purpose | Note |
|------|---------|------|
| `fastmcp.json` | FastMCP server configuration | Runtime |
| `mcp.json` | MCP protocol configuration | Runtime |
| `prefect.yaml` | Prefect orchestration config | Runtime |
| `arifos.yml` | arifOS system configuration | Runtime |
| `docker-compose.yml` | Docker orchestration | Deployment |
| `docker-compose.*.yml` | Environment-specific compose | Deployment |

---

## Source of Truth Hierarchy

```
PRIMARY SoT (Root)
├── README.md, AGENTS.md, LICENSE
├── pyproject.toml, requirements.txt
├── 000-999-implementation-plan.md
├── SEALING_CHECKLIST.md
└── VAULT999_4LAYER_IMPLEMENTATION_SUMMARY.md

SECONDARY SoT (Core Directories)
├── core/ — Governance kernel
├── 000/ — Constitutional law
├── VAULT999/ — Immutable ledger
└── config/ — Canonical schemas

RUNTIME (arifosmcp/)
└── Runtime shell, HTTP endpoints, MCP transport
    Doctrine lives in core/, 000/, config/

DEPLOYMENT (docs/deployment/, infrastructure/, deployments/)
└── Environment-specific implementations
```

---

## Conflict Resolution

Per AGENTS.md:

- **Doctrine conflict** → Root SoT files win
- **Runtime surface conflict** → Live `/health` + `/tools` endpoints win
- **Documentation conflict** → `docs/REPO_STRUCTURE.md` + root `README.md` win

---

*Last updated: 2026-04-07*  
*Authority: 888_JUDGE*  
*Seal: 999_SEAL*
