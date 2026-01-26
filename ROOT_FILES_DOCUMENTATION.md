# arifOS Repository Root Files - Constitutional Organization

**Document Version:** v1.0  
**Last Updated:** 2026-01-26  
**Authority:** Muhammad Arif bin Fazil  

This document explains the function and purpose of every file in the repository root directory after the constitutional entropy reduction cleanup (2026-01-26).

---

## 📋 FILE CATEGORIES & PURPOSES

### 📄 CORE PROJECT DOCUMENTATION (Essential Files)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **README.md** | 41 KB | **Primary project documentation** - Comprehensive overview, installation, quickstart, architecture, and usage guide. This is the main entry point for users and developers. | ACTIVE |
| **LICENSE** | 35 KB | **Legal license** - AGPL-3.0-only license defining usage rights and obligations for the arifOS constitutional AI governance system. | ACTIVE |
| **AGENTS.md** | 21 KB | **Agent development guide** - Specifications for AI agents working on this repository, coding standards, constitutional compliance requirements, and tool usage guidelines. | ACTIVE |
| **CHANGELOG.md** | 10 KB | **Version history** - Detailed release notes following Keep a Changelog format. Documents all versions from v50.0.0 to current v53.0.0 and unreleased changes. | ACTIVE |

**Function:** These four files form the essential documentation quartet that any user, developer, or contributor needs to understand and work with the project.

---

### 🏛️ ARCHITECTURE DOCUMENTATION (Strategic Documents)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **ARCHITECTURE_DECISION_EXECUTIVE_BRIEFING.md** | 11 KB | High-level architecture decisions for executives and stakeholders. Strategic overview without technical depth. | REFERENCE |
| **ARCHITECTURE_COMPARISON_ANALYSIS.md** | 29 KB | Detailed technical analysis comparing v45, v50, and v52+ architectures with migration paths. | REFERENCE |
| **ARCHITECTURE_COMPARISON_DIAGRAMS.md** | 52 KB | Visual architecture diagrams (Mermaid format) showing system evolution and component relationships. | REFERENCE |
| **ARCHITECTURE_COMPARISON_SUMMARY.md** | 14 KB | Executive summary of architecture evolution and key decision points. | REFERENCE |
| **TRINITY_PARALLEL_SPEC.md** | 16 KB | **Critical specification** - Defines AGI (Mind), ASI (Heart), APEX (Soul) parallel execution model and constitutional compliance. | ACTIVE |
| **arifOS_Trinity_Parallel_Corrected.md** | 14 KB | Corrected Trinity parallel flow documentation with accurate constitutional floor enforcement. | ACTIVE |
| **CANONICAL_CORE_GAP_ANALYSIS.md** | 30 KB | Analysis of gaps between legacy core and canonical core implementation with migration strategy. | REFERENCE |
| **CANONICAL_CORE_MIGRATION_COMPLETE.md** | 8 KB | Completion report for canonical core migration (v52+ architecture). | ARCHIVED |

**Function:** These documents provide architectural context, historical evolution, and strategic direction. They are reference materials for understanding system design decisions.

---

### ⚙️ CONFIGURATION FILES (Project Setup)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **pyproject.toml** | 9 KB | **Python project configuration** - Package metadata (aaa-mcp v53.0.0), dependencies, build system, tool configurations (black, mypy, pytest). | ACTIVE |
| **.gitignore** | 3 KB | **Git ignore rules** - Specifies files/directories excluded from version control (168 lines covering: caches, logs, IDE dirs, secrets, build artifacts). | ACTIVE |
| **pytest.ini** | 4 KB | **Test configuration** - pytest settings, markers for constitutional tests (f1-f13, apex, mcp, integration), coverage settings. | ACTIVE |
| **mypy.ini** | 2 KB | **Type checking configuration** - mypy settings for static type analysis, strict mode for core governance modules. | ACTIVE |
| **.pre-commit-config.yaml** | 5 KB | **Code quality automation** - pre-commit hooks for black, ruff, mypy, bandit security scanning, detect-secrets. | ACTIVE |
| **MANIFEST.in** | 141 B | **Package manifest** - Specifies additional files to include in Python package distribution. | ACTIVE |
| **requirements.txt** | 612 B | **Runtime dependencies** - Production requirements for deployment (Railway/app). | ACTIVE |
| **runtime.txt** | 13 B | **Python runtime version** - Specifies Python 3.10 for deployment environments. | ACTIVE |
| **nixpkgs.nix** | 340 B | **Nix package configuration** - For reproducible builds in Nix environments. | ACTIVE |
| **.mcp.json** | 553 B | **MCP server configuration** - Claude Desktop integration config for local development. | LOCAL |
| **gemini-mcp.json** | 613 B | **Gemini MCP configuration** - GitHub Copilot/Gemini integration settings. | LOCAL |

**Function:** These files configure the development environment, build system, code quality tools, and package management. They ensure consistent development and deployment.

---

### 🚀 DEPLOYMENT CONFIGURATION (Production)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **Dockerfile** | 1 KB | **Container definition** - Multi-stage Docker build for production deployment with Python 3.10-slim base. | ACTIVE |
| **railway.toml** | 326 B | **Railway.app configuration** - Production deployment settings, start commands, health checks. | ACTIVE |
| **railway.COMPLETE.toml** | 593 B | **Railway config backup** - Complete Railway configuration reference. | REFERENCE |
| **Caddyfile** | 631 B | **Web server configuration** - Caddy v2 reverse proxy config for custom domains and SSL/TLS. | ACTIVE |
| **DEPLOY_V53.md** | 1 KB | **Deployment guide** - Quick reference for v53.0.0 deployment steps. | ACTIVE |

**Function:** Production deployment configurations for containerization, cloud platforms, and web server routing.

---

### 🗄️ LOCK & LOG FILES (Generated)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **uv.lock** | 930 KB | **Dependency lock file** - uv package manager lock file ensuring reproducible builds (auto-generated, commit to git). | GENERATED |
| **VERSION** | 6 B | **Version marker** - Simple version indicator file (v53) for deployment verification. | ACTIVE |

**Function:** Lock files ensure deterministic builds. The VERSION file provides runtime version checking.

---

### 📄 INTEGRATION DOCUMENTATION (Platform-Specific)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **CLAUDE.md** | 12 KB | **Claude Desktop setup** - Configuration guide for Claude Desktop integration with arifOS MCP server. | ACTIVE |
| **GEMINI.md** | 7 KB | **Gemini/Github Copilot setup** - Configuration guide for Gemini CLI and Copilot integration. | ACTIVE |
| **openapi.json** | 34 KB | **API specification** - OpenAPI 3.1 specification for the Body API (Governance-as-a-Service). | ACTIVE |
| **.env** | 370 B | **Environment variables** - Local development environment configuration (gitignored, local only). | LOCAL |
| **.env.example** | 440 B | **Environment template** - Example environment variables for local setup and Railway deployment. | REFERENCE |

**Function:** Platform-specific integration guides and API specifications for different AI assistants and development tools.

---

### 📊 CONSTITUTIONAL AUDIT TRAILS

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **999_VAULT_SEAL.log** | 16 KB | **Constitutional audit log** - Immutable ledger of all SEAL operations, verdicts, and constitutional compliance checks. Generated by VAULT999 system. | GENERATED |
| **PLANNING_REMOVAL_SUMMARY.md** | 4.5 KB | **Cleanup documentation** - Summary of planning files removal operation (just performed). | ARCHIVE RECORD |

**Function:** Audit trails and operation logs for constitutional governance compliance and historical record-keeping.

---

### 📁 GITIGNORED DIRECTORIES (Not Tracked)

These directories are present locally but excluded from git via `.gitignore`:

| Directory | Purpose |
|-----------|---------|
| **.agent/** | Kimi CLI agent workspace configuration |
| **.antigravity/** | Multi-agent (Claude/Gemini) integration cache |
| **.arifos_clip/** | Clipboard artifact storage |
| **.claude/** | Claude Desktop IDE configuration |
| **.codex/** | GitHub Copilot workspace settings |
| **.cursor/** | Cursor IDE configuration |
| **.gemini-clipboard/** | Gemini clipboard cache |
| **.kimi/** | Kimi CLI configuration |
| **.openmcp/** | OpenMCP server configuration |
| **.serena/** | Serena IDE workspace |
| **.vs/** | Visual Studio configuration |
| **.vscode/** | VS Code configuration |
| **.pytest_cache/** | pytest test cache (deleted during cleanup) |
| **arifos.egg-info/** | Python package metadata (auto-generated) |

**See:** `.IDE_DIRECTORIES.md` for complete documentation of these directories.

---

### 📂 SOURCE CODE DIRECTORIES (Active Development)

| Directory | Purpose |
|-----------|---------|
| **arifos/** | **Main Python package** - Constitutional AI governance core (83 files, 3.2 MB) |
| **codebase/** | **Migration codebase** - v52→v53 architecture migration (actively used, 567 files) |
| **canonical_core/** | **Legacy core** - Deprecated canonical implementation (migration source) |
| **tests/** | **Test suite** - 164+ test files covering constitutional compliance |
| **docs/** | **Documentation** - 16 MB of comprehensive documentation (165 files) |
| **docs-site/** | **Documentation website** - MkDocs site for API documentation |
| **reports/** | **Periodic reports** - 19 timestamped reports from development |
| **scripts/** | **Utility scripts** - Development, deployment, and maintenance scripts |
| **setup/** | **Bootstrap** - Environment setup and bootstrapping tools |
| **SEAL999/** | **Canonical SEAL module** - Importable constitutional sealing module (v2.0) |
| **VAULT999/** | **Operational vault** - Runtime data, ledgers, and audit trails |
| **archive/** | **Historical archives** - Legacy code, migrations, completed operations |
| **refactoring/** | **Refactoring workspace** - Temporary refactoring staging area |
| **runtime/** | **Runtime configs** - Runtime-specific configurations |
| **templates/** | **Templates** - Code and configuration templates |
| **integrations/** | **Third-party** - External integrations and plugins |
| **logs/** | **Application logs** - Runtime log files |
| **career-timeline/** | **Personal** - Career documentation (Arif) |
| **spec/** | **Specifications** - Constitutional specifications v45-v47 |
| **deploy/** | **Deployment** - Deployment scripts and configurations |
| **000_THEORY/** | **Canon** - Constitutional law and theoretical foundation |
| **vault_test/** | **Test vault** - VAULT999 testing environment |

**Function:** These directories contain the actual source code, tests, documentation, and operational data that constitute the arifOS system.

---

## 🎯 ROOT DIRECTORY FILE STATISTICS

### Summary by Category
- **Core Documentation:** 4 files (68 KB) - CRITICAL
- **Architecture Docs:** 8 files (174 KB) - REFERENCE
- **Configuration:** 12 files (23 KB) - ACTIVE
- **Deployment:** 5 files (4 KB) - ACTIVE
- **Generated:** 2 files (946 KB) - GENERATED
- **Integration:** 5 files (54 KB) - ACTIVE
- **Audit Trails:** 2 files (20 KB) - GENERATED
- **Total Root Files:** 38 files
- **Total Size:** ~1.3 MB

### Critical vs Non-Critical
- **CRITICAL (6 files):** README.md, LICENSE, AGENTS.md, CHANGELOG.md, pyproject.toml, .gitignore
- **ACTIVE (22 files):** Configuration, deployment, integration files that are actively used
- **REFERENCE (8 files):** Architecture and historical documentation for context
- **GENERATED (2 files):** Auto-generated files (uv.lock, 999_VAULT_SEAL.log)

---

## 🔒 CONSTITUTIONAL COMPLIANCE

### F1 - Amanah (Reversibility & Audit)
✅ All historical work preserved in `archive/` with timestamps  
✅ No irreversible operations performed  
✅ Full audit trail via `999_VAULT_SEAL.log`  

### F4 - Clarity (ΔS ≤ 0)
✅ Entropy reduced from 60+ files to 38 files  
✅ Information consolidated logically  
✅ Clear separation: active vs archived vs generated  

### F6 - Transparency
✅ Every file's purpose documented  
✅ Clear categorization by function  
✅ IDE directories explained and gitignored  

---

## 📖 USAGE GUIDE

### For New Contributors
Start with: **README.md** → **AGENTS.md** → **CHANGELOG.md**

### For Developers
Focus on: **pyproject.toml** → **arifos/** → **tests/** → **CHANGELOG.md** (unreleased)

### For DevOps/Deployment
Use: **Dockerfile** → **railway.toml** → **docs/DEPLOYMENT_SEAL.md**

### For Architecture Understanding
Read: **TRINITY_PARALLEL_SPEC.md** → **ARCHITECTURE_COMPARISON_SUMMARY.md**

### For Constitutional Compliance
Review: **AGENTS.md** (F1-F13) → **999_VAULT_SEAL.log** → **CHANGELOG.md**

---

**DITEMPA BUKAN DIBERI** - Repository order is forged through governance, not left to chaos.

**Authority:** Muhammad Arif bin Fazil | Penang, Malaysia  
**Seal:** 2026-01-26T19:10:00+08:00  
**Version:** v53.0.0-AAA (Constitutionally Organized)
