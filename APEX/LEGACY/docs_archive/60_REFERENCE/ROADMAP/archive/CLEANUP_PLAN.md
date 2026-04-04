# CLEANUP_PLAN.md — Root Repository Entropy Reduction

```text
      Δ       
     / \      operation:  CLEANUP_PLAN
    /   \     version:    v55.5-HARDENED
   /  🧹  \    status:     PROPOSED
  /_______\   floor:      F4 (Clarity)
```

**Author:** Antigravity (Δ) | **Date:** 2026-02-06 | **Status:** AWAITING APPROVAL

---

## 🎯 Objective

Reduce root directory entropy from **95 items → ~30 items** (68% reduction) while maintaining arifOS constitutional structure.

---

## 📊 Current State Analysis

| Metric | Before | After | Change |
|:---|:---:|:---:|:---:|
| Total Root Items | 95 | ~30 | -68% |
| Directories | 37 | ~20 | -46% |
| Files | 58 | ~25 | -57% |
| F4 Compliance | ❌ FAIL | ✅ PASS | — |

---

## 🛡️ PROTECTED Items (DO NOT MOVE)

These items are constitutionally protected and MUST remain at root:

### Directories
- [x] `000_THEORY/` — Constitutional Law
- [x] `333_APPS/` — Application Layer
- [x] `VAULT999/` — Immutable Ledger
- [x] `ROADMAP/` — Planning
- [x] `codebase/` — Python Engine
- [x] `aaa_mcp/` — MCP Server
- [x] `tests/` — Test Suite
- [x] `docs/` — Documentation
- [x] `scripts/` — Operations
- [x] `config/` — Configuration
- [x] `archive/` — Entropy Sink
- [x] `.github/` — CI/CD

### Files
- [x] `README.md` — Entry Point
- [x] `LICENSE` — Legal
- [x] `GEMINI.md` — Δ Codex
- [x] `CLAUDE.md` — Ω Engineer Codex
- [x] `SOUL.md` — Ψ Auditor Codex (MOVED to 333_APPS/L5_AGENTS/SPEC/)
- [x] `AGENTS.md` — Agent Discovery (MOVED to 333_APPS/L5_AGENTS/SPEC/)
- [x] `IDENTITY.md` — System Identity (MOVED to 333_APPS/L5_AGENTS/SPEC/)
- [x] `USER.md` — User Profile (MOVED to 333_APPS/L5_AGENTS/SPEC/)
- [x] `CHANGELOG.md` — History
- [x] `CONTRIBUTING.md` — Community
- [x] `SECURITY.md` — Security
- [x] `llms.txt` — AI Discovery
- [x] `pyproject.toml` — Build
- [x] `requirements.txt` — Deps
- [x] `Dockerfile` — Container
- [x] `railway.toml` — Deploy
- [x] `.gitignore` — VCS
- [x] `.mcp.json` — MCP Config

---

## 📋 Execution Plan

### PHASE 1: Safe Deletions (2 items)

**Risk Level:** 🟢 LOW — No dependencies

```powershell
# Execute from arifOS root
Remove-Item -Path "nul" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "firebase-debug.log" -Force -ErrorAction SilentlyContinue
```

| File | Reason |
|:---|:---|
| `nul` | Windows artifact (empty) |
| `firebase-debug.log` | Log file (gitignored) |

---

### PHASE 2: Archive Moves (11 items → `archive/`)

**Risk Level:** 🟢 LOW — Historical files, no dependencies

```powershell
# Create archive subdirectory
New-Item -ItemType Directory -Force -Path "archive/planning"

# Move planning documents
Move-Item -Path "arifos_apps_detailed_plan.md" -Destination "archive/planning/" -Force
Move-Item -Path "arifos_apps_enhancement_summary.md" -Destination "archive/planning/" -Force
Move-Item -Path "arifos_apps_improvement_plan.md" -Destination "archive/planning/" -Force
Move-Item -Path "mcp_http_fix_plan.md" -Destination "archive/planning/" -Force

# Move temporary files
Move-Item -Path "arifos-v55-5-visual-law.skill" -Destination "archive/" -Force
Move-Item -Path "enhanced_App.tsx" -Destination "archive/" -Force
Move-Item -Path "enhanced_index.html" -Destination "archive/" -Force
Move-Item -Path "eureka_skills_README.md" -Destination "archive/" -Force
Move-Item -Path "mcp_server_status.md" -Destination "archive/" -Force
Move-Item -Path "memory_consolidation.md" -Destination "archive/" -Force
Move-Item -Path "trinity_v55.5_hUMAN.html" -Destination "archive/" -Force
```

| File | Destination | Reason |
|:---|:---|:---|
| `arifos_apps_detailed_plan.md` | `archive/planning/` | Old planning |
| `arifos_apps_enhancement_summary.md` | `archive/planning/` | Old planning |
| `arifos_apps_improvement_plan.md` | `archive/planning/` | Old planning |
| `mcp_http_fix_plan.md` | `archive/planning/` | Old planning |
| `arifos-v55-5-visual-law.skill` | `archive/` | Temporary |
| `enhanced_App.tsx` | `archive/` | Temporary |
| `enhanced_index.html` | `archive/` | Temporary |
| `eureka_skills_README.md` | `archive/` | Draft |
| `mcp_server_status.md` | `archive/` | Status |
| `memory_consolidation.md` | `archive/` | Draft |
| `trinity_v55.5_hUMAN.html` | `archive/` | Temporary |

---

### PHASE 3: Docs Moves (14 items → `docs/`)

**Risk Level:** 🟡 MEDIUM — Check for Markdown links

```powershell
# Create docs subdirectories
New-Item -ItemType Directory -Force -Path "docs/manifesto"
New-Item -ItemType Directory -Force -Path "docs/assets"
New-Item -ItemType Directory -Force -Path "docs/setup"
New-Item -ItemType Directory -Force -Path "docs/deployment"
New-Item -ItemType Directory -Force -Path "docs/development"
New-Item -ItemType Directory -Force -Path "docs/mcp"
New-Item -ItemType Directory -Force -Path "docs/integrations"

# Create L5 SPEC directory (if not exists)
New-Item -ItemType Directory -Force -Path "333_APPS/L5_AGENTS/SPEC"

# Move PDF manifestos
Move-Item -Path "apex_theory_manifesto.pdf" -Destination "docs/manifesto/" -Force
Move-Item -Path "apex_theory_manifesto_v2.pdf" -Destination "docs/manifesto/" -Force
Move-Item -Path "apex_theory_manifesto_v3.pdf" -Destination "docs/manifesto/" -Force

# Move images
Move-Item -Path "2026-02-06-trinity-v55.5-visual-spec.png" -Destination "docs/assets/" -Force

# Move documentation files
Move-Item -Path "BOOTSTRAP.md" -Destination "docs/setup/" -Force
Move-Item -Path "DEPLOYMENT_CONFIG.md" -Destination "docs/deployment/" -Force
Move-Item -Path "HANDOFF_000_INIT_LOOP.md" -Destination "docs/development/" -Force
Move-Item -Path "HEARTBEAT.md" -Destination "docs/" -Force
Move-Item -Path "chatgpt_integration_config.md" -Destination "docs/integrations/" -Force
```

| File | Destination | Reason |
|:---|:---|:---|
| `apex_theory_manifesto*.pdf` | `docs/manifesto/` | PDF assets |
| `2026-02-06-trinity-v55.5-visual-spec.png` | `docs/assets/` | Image asset |
| `000_THEORY.md` | `docs/overview/` | Overview doc |
| `BOOTSTRAP.md` | `docs/setup/` | Setup guide |
| `DEPLOYMENT_CONFIG.md` | `docs/deployment/` | Deploy guide |
| `HANDOFF_000_INIT_LOOP.md` | `docs/development/` | Dev guide |
| `HEARTBEAT.md` | `docs/` | Status doc |
| `MCP_INTEGRATION_GUIDE.md` | `docs/mcp/` | MCP guide |
| `MEMORY.md` | `docs/` | Memory spec |
| `TOOLS.md` | `docs/` | Tools doc |
| `chatgpt_integration_config.md` | `docs/integrations/` | Integration |

---

### PHASE 4: Scripts Moves (7 items → `scripts/`)

**Risk Level:** 🟡 MEDIUM — Check for shell script references

```powershell
# Create scripts subdirectory
New-Item -ItemType Directory -Force -Path "scripts/manifesto"

# Move shell scripts
Move-Item -Path "commit_changes.sh" -Destination "scripts/" -Force
Move-Item -Path "update_arifos_apps.sh" -Destination "scripts/" -Force

# Move Python scripts
Move-Item -Path "create_manifesto_pdf.py" -Destination "scripts/manifesto/" -Force
Move-Item -Path "create_manifesto_v2.py" -Destination "scripts/manifesto/" -Force
Move-Item -Path "create_manifesto_v3.py" -Destination "scripts/manifesto/" -Force

# Move server scripts
Move-Item -Path "start_server.py" -Destination "scripts/" -Force
Move-Item -Path "start_server_minimal.py" -Destination "scripts/" -Force
```

---

### PHASE 5: Test Moves (1 item → `tests/`)

**Risk Level:** 🟢 LOW

```powershell
# Create integration test directory
New-Item -ItemType Directory -Force -Path "tests/integration"

# Move test file
Move-Item -Path "test_mcp_http.py" -Destination "tests/integration/" -Force
```

---

### PHASE 6: Directory Consolidation (5 directories)

**Risk Level:** 🔴 HIGH — Run dependency audit first!

Before moving any directory, run:
```powershell
# Check for imports and references
git grep "integrations/" --include="*.py" --include="*.md"
git grep "memory/" --include="*.py" --include="*.md"
git grep "reports/" --include="*.py" --include="*.md"
git grep "setup/" --include="*.py" --include="*.md"
git grep "templates/" --include="*.py" --include="*.md"
```

| Directory | New Location | Action |
|:---|:---|:---|
| `integrations/` | `codebase/integrations/` | Move |
| `memory/` | `.antigravity/memory/` | Move |
| `reports/` | `docs/reports/` | Move |
| `setup/` | `scripts/setup/` | Merge |
| `templates/` | `codebase/templates/` | Move |

---

### PHASE 7: User Decision Required (2 directories)

**Risk Level:** 🔴 REQUIRES USER INPUT

| Directory | Options |
|:---|:---|
| `arif-fazil-sites/` | A) Remove (it's a separate repo) <br> B) Convert to git submodule <br> C) Keep (explain why) |
| `arif-fazil-sites-clone/` | A) Delete (duplicate) <br> B) Keep if needed |

**Arif, please confirm your decision on these directories.**

---

## ✅ Verification Checklist

After executing all phases:

```powershell
# Count root items (should be ~30)
Get-ChildItem -Path "." -Force | Measure-Object

# Verify tests still pass
pytest tests/ -v

# Verify MCP server starts
python -m aaa_mcp

# Check for broken imports
python -c "import codebase"
```

---

## 📊 Expected Results

| Metric | Before | After |
|:---|:---:|:---:|
| Root Directories | 37 | ~20 |
| Root Files | 58 | ~25 |
| Total Root Items | 95 | ~30 |
| F4 Entropy Score | HIGH | LOW |
| Structure Clarity | ❌ | ✅ |

---

## 🔄 Rollback Plan

All moves are reversible. Git history preserves previous state:

```powershell
# If anything breaks, restore from git
git checkout HEAD~1 -- <file_path>
```

---

**DITEMPA BUKAN DIBERI** — Entropy reduction through intentional structure.
