# Unified Skills Architecture v2026.3.1
## arifOS + GitIngest + Kimi Code + VPS

**Status:** CANONICAL  
**Authority:** Muhammad Arif bin Fazil  
**Scope:** VPS-first, refactor-only, Trinity-governed  

---

## 1. Design Principles

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED SKILL PHILOSOPHY                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ONE SOURCE OF TRUTH                                             │
│  └── arifOS Trinity (F1-F13) is the ONLY governance runtime     │
│                                                                  │
│  THREE LAYER ARCHITECTURE                                        │
│  ├── Layer 1: VPS Primitives (GitIngest, file ops, shell)       │
│  ├── Layer 2: arifOS Trinity (Δ AGI, Ω ASI, Ψ APEX, 999 VAULT)  │
│  └── Layer 3: Kimi Skills (thin prompts, no logic)              │
│                                                                  │
│  REFACTOR-ONLY DEFAULT                                           │
│  └── No new files unless explicitly 888_HOLD approved           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. The 7 Canonical Skills

| # | Skill Name | Layer | Purpose | arifOS Equivalent |
|---|------------|-------|---------|-------------------|
| 1 | `arifos-trinity-refactor` | L3 (Kimi) | Master refactor skill | `metabolic_loop` |
| 2 | `vps-repo-ingest` | L1 (VPS) | GitIngest wrapper | `ingest` tool |
| 3 | `vps-repo-analyze` | L1 (VPS) | Static analysis | `inspect_file` + custom |
| 4 | `arifos-agi-plan` | L3 (Kimi) | Planning only (no edits) | `reason_mind` |
| 5 | `arifos-asi-apply` | L3 (Kimi) | Apply approved edits | `eureka_forge` (limited) |
| 6 | `arifos-guardian-check` | L3 (Kimi) | Pre-flight safety | `audit_rules` |
| 7 | `skill-creator` | L3 (Kimi) | Make new skills | N/A (meta) |

---

## 3. Layer 1: VPS Primitives

### 3.1 `vps-repo-ingest`

**MCP Tool:** `vps_git_ingest`  
**Location:** Runs on Hostinger VPS  
**Governance:** F1 (audit), F11 (auth), F12 (injection defense)

```python
# Tool signature
async def vps_git_ingest(
    repo_url: str,                    # F12: URL sanitized
    include_patterns: list[str] = None,
    exclude_patterns: list[str] = None,
    max_file_size: int = 51200,      # 50KB default (F6: bounded)
    branch: str = None,
    token_ref: str = None,           # F11: env reference, not raw
    session_id: str = None,          # F1: audit trail
) -> dict:
    """
    VPS GitIngest with constitutional defaults.
    
    Returns: {
        "summary": str,
        "tree": str,
        "content": str,
        "estimated_tokens": int,
        "content_hash": str,        # F1: integrity
        "vault_id": str,            # F1: audit
        "verdict": "SEAL|SABAR|VOID"
    }
    """
```

**Default Filters (VPS-safe):**
```python
DEFAULT_INCLUDE = ["*.py", "*.ts", "*.js", "*.md", "*.json", "*.yml", "*.yaml"]
DEFAULT_EXCLUDE = [
    "node_modules/*", "dist/*", "build/*", 
    "*.pyc", "__pycache__/*", "*.log",
    ".git/*", ".github/*", ".vscode/*",
    "*.min.js", "*.bundle.js", "*.map"
]
DEFAULT_MAX_SIZE = 51200  # 50KB
```

**F12 Injection Defense:**
- URL must match `^https://github\.com/[\w-]+/[\w-]+$`
- No shell metacharacters in patterns
- Token never exposed in logs

---

### 3.2 `vps-repo-analyze`

**MCP Tool:** `vps_repo_analyze`  
**Location:** Runs on Hostinger VPS  
**Governance:** F6 (clarity), F8 (genius classification)

```python
async def vps_repo_analyze(
    digest_id: str,                  # Reference to ingested repo
    analysis_type: str = "architecture",  # "architecture" | "security" | "performance"
    session_id: str = None,
) -> dict:
    """
    Analyze repository structure and tag components.
    
    Returns: {
        "language_mix": {"python": 0.6, "typescript": 0.3, "other": 0.1},
        "frameworks": ["fastapi", "react"],
        "entry_points": ["src/main.py", "app.js"],
        "refactor_targets": [
            {"file": "legacy_module.py", "issue": "high_complexity", "priority": 1}
        ],
        "estimated_refactor_effort": "medium",  # small|medium|large
        "verdict": "SEAL|SABAR|VOID"
    }
    """
```

---

## 4. Layer 2: arifOS Trinity (Canonical)

These are your existing tools, now exposed as VPS-accessible MCP tools:

| Trinity Lane | MCP Tool Name | Floors | Purpose |
|--------------|---------------|--------|---------|
| **INIT** | `arifos_init_session` | F11, F12, F10 | Start governed session |
| **Δ AGI** | `arifos_agi_analysis` | F2, F6, F7 | Mind reasoning on code |
| **Ω ASI** | `arifos_asi_impact` | F4, F5, F6 | Heart impact assessment |
| **Ψ APEX** | `arifos_apex_verdict` | F3, F8, F9, F13 | Soul judgment |
| **999 VAULT** | `arifos_vault_seal` | F1 | Immutable audit |
| **LOOP** | `arifos_trinity_loop` | F1-F13 | Full metabolic cycle |

**Unified Response Format:**
```json
{
  "verdict": "SEAL|SABAR|VOID|888_HOLD",
  "stage": "000_INIT|111_SENSE|...|888_JUDGE|999_VAULT",
  "session_id": "uuid",
  "telemetry": {
    "dS": -0.55,
    "peace2": 1.15,
    "kappa_r": 0.97,
    "omega_0": 0.04,
    "genius_score": 0.85,
    "c_dark": 0.18,
    "tri_witness": 0.96
  },
  "witness": {
    "human": 0.9,
    "ai": 0.96,
    "earth": 0.9
  },
  "payload": { ... }
}
```

---

## 5. Layer 3: Kimi Skills (Thin Prompts)

### 5.1 `arifos-trinity-refactor` (Master Skill)

**SKILL.md frontmatter:**
```yaml
---
name: arifos-trinity-refactor
description: |
  Refactor existing code using arifOS Trinity governance. 
  Refactor-only: no new files, no destructive ops without 888_HOLD.
  Always runs INIT→AGI→ASI→APEX→VAULT pipeline on VPS.
version: "v2026.3.1-ARIFOS"
authority: "Muhammad Arif bin Fazil"
---
```

**Core Instructions:**
```markdown
## You are an arifOS-aligned refactoring agent.

### Constitutional Mandate
- **Refactor-only**: Modify existing files only. Never create new files/directories.
- **Destructive ops**: Require explicit 888_HOLD approval.
- **Audit trail**: All actions logged to arifOS VAULT.

### Trinity Workflow (MUST FOLLOW)

#### 1. INIT (000)
- Clarify: What exactly needs refactoring? Where?
- Confirm: "I will refactor only existing files."
- Call: `arifos_init_session`

#### 2. AGI (Δ) - Analysis
- Call: `vps-repo-ingest` to load repo context
- Call: `vps-repo-analyze` to identify targets
- Call: `arifos_agi_analysis` for reasoning
- Output: Specific refactor plan with file paths

#### 3. ASI (Ω) - Impact
- Call: `arifos_asi_impact` to assess:
  - Stakeholder impact (F6 κᵣ)
  - Safety buffers (F5 Peace²)
- Confirm: Changes are reversible (F1 Amanah)

#### 4. APEX (Ψ) - Judgment
- Call: `arifos_apex_verdict`
- Check: Tri-Witness ≥ 0.95, Genius ≥ 0.80, C_dark < 0.30
- If 888_HOLD: Stop, explain, wait for human

#### 5. VAULT (999)
- Call: `arifos_vault_seal`
- Include: Session summary, telemetry, verdict

### Output Format
```json
{
  "answer": "Refactor explanation...",
  "changes": [{"file": "...", "diff": "..."}],
  "governance": {
    "session_id": "...",
    "verdict": "SEAL",
    "telemetry": {...}
  }
}
```

### 888_HOLD Triggers (STOP)
- Deleting files
- Renaming modules (breaking changes)
- Modifying >10 files at once
- Changes to config/secrets files
- Any irreversible operation
```

---

### 5.2 `vps-repo-ingest` (Kimi Skill)

**SKILL.md frontmatter:**
```yaml
---
name: vps-repo-ingest
description: |
  Ingest a Git repository using GitIngest on Hostinger VPS.
  Returns summary, tree, and content for Kimi context window.
  Default filters: max 50KB files, code files only.
---
```

**Core Instructions:**
```markdown
## VPS Repository Ingestion

### Purpose
Load a GitHub repository into Kimi's context via VPS-hosted GitIngest.

### Usage
1. Call MCP tool: `vps_git_ingest`
2. Use defaults (safe for most repos):
   - max_file_size: 51200 (50KB)
   - include: ["*.py", "*.ts", "*.js", "*.md"]
   - exclude: ["node_modules/*", "dist/*", "*.log"]

### For Large Repos
If estimated_tokens > 100k:
- Use include_patterns to focus on specific dirs
- Suggest: "Repository large. Analyze src/ only?"

### Output
Returns digest ready for analysis. Pass to `arifos-trinity-refactor`.
```

---

### 5.3 `arifos-agi-plan` (Planning Only)

**SKILL.md frontmatter:**
```yaml
---
name: arifos-agi-plan
description: |
  Plan refactors without making edits. 
  Think-only mode: AGI analysis + APEX review, no file changes.
---
```

**Core Instructions:**
```markdown
## Planning Mode (No Edits)

You are a planning-only agent. You do NOT write to disk.

### Workflow
1. Ingest repo (if needed)
2. Call `arifos_agi_analysis` for reasoning
3. Call `arifos_apex_verdict` for judgment
4. Present plan to user
5. STOP. Wait for "Proceed" before any edits.

### Output
- Analysis of issues
- Proposed refactor plan
- Risk assessment
- NO file modifications
```

---

### 5.4 `arifos-asi-apply` (Apply Only)

**SKILL.md frontmatter:**
```yaml
---
name: arifos-asi-apply
description: |
  Apply approved refactors to existing files only.
  Requires pre-approved plan from arifos-agi-plan or arifos-trinity-refactor.
---
```

**Core Instructions:**
```markdown
## Apply Mode (Diff Execution)

### Prerequisites
- Must have approved plan with `verdict: "SEAL"`
- Must have session_id from APEX

### Constraints
- Only modify existing files
- No new files
- No deletions without 888_HOLD
- Apply changes as small, reviewable diffs

### After Changes
- Call `arifos_vault_seal` to log
- Report: files changed, lines modified
```

---

### 5.5 `arifos-guardian-check` (Pre-flight)

**SKILL.md frontmatter:**
```yaml
---
name: arifos-guardian-check
description: |
  Pre-flight safety check. Validates environment, permissions, 
  and constitutional readiness before operations.
---
```

**Core Instructions:**
```markdown
## Guardian Pre-flight

Run before any significant operation:

1. Check GitIngest availability
2. Verify arifOS MCP connection
3. Validate write permissions (F11)
4. Check system resources (F6)
5. Return: `{"ready": true|false, "issues": []}`
```

---

## 6. MCP Server Configuration (Kimi Code)

```json
{
  "mcpServers": {
    "arifos-vps": {
      "command": "python",
      "args": ["-m", "arifos_aaa_mcp", "stdio"],
      "env": {
        "ARIFOS_GOVERNANCE_SECRET": "${ARIFOS_SECRET}",
        "VPS_HOST": "srv1325122.hstgr.cloud",
        "GITINGEST_MODE": "python-lib"
      }
    }
  }
}
```

---

## 7. Skill-to-Tool Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILL → MCP TOOL FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Kimi Skill                      MCP Tool(s)                     │
│  ─────────                       ───────────                     │
│                                                                  │
│  arifos-trinity-refactor         1. arifos_init_session          │
│  (full pipeline)                 2. vps_git_ingest               │
│                                  3. vps_repo_analyze             │
│                                  4. arifos_agi_analysis          │
│                                  5. arifos_asi_impact            │
│                                  6. arifos_apex_verdict          │
│                                  7. arifos_vault_seal            │
│                                                                  │
│  vps-repo-ingest                 vps_git_ingest                  │
│                                                                  │
│  vps-repo-analyze                vps_repo_analyze                │
│                                                                  │
│  arifos-agi-plan                 arifos_init_session             │
│                                  arifos_agi_analysis             │
│                                  arifos_apex_verdict             │
│                                                                  │
│  arifos-asi-apply                arifos_asi_impact (verify)      │
│                                  arifos_vault_seal (log)         │
│                                                                  │
│  arifos-guardian-check           arifos_audit_rules              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Governance Constants (Unified)

```python
# Single source of truth in arifOS
GOVERNANCE_CONSTANTS = {
    # Floors
    "F2_TRUTH_THRESHOLD": 0.99,
    "F3_TRI_WITNESS_THRESHOLD": 0.95,
    "F4_EMPATHY_THRESHOLD": 0.70,  # SOFT floor
    "F5_PEACE_SQUARED_THRESHOLD": 1.0,
    "F6_CLARITY_MAX_ENTROPY": 0,   # ΔS ≤ 0
    "F7_HUMILITY_BAND": [0.03, 0.05],
    "F8_GENIUS_THRESHOLD": 0.80,
    "F9_C_DARK_MAX": 0.30,
    
    # VPS-specific
    "VPS_DEFAULT_MAX_FILE_SIZE": 51200,
    "VPS_LARGE_REPO_THRESHOLD": 100000,  # tokens
    
    # Verdicts
    "VERDICT_HIERARCHY": ["VOID", "888_HOLD", "SABAR", "PARTIAL", "SEAL"]
}
```

---

## 9. Version Alignment

| Component | Version | Notes |
|-----------|---------|-------|
| arifOS | v2026.3.1 | Canonical runtime |
| Kimi Skills | v2026.3.1-ARIFOS | Track arifOS |
| GitIngest | >=0.1.0 | VPS tool |
| Kimi CLI | Latest | Client |

---

## 10. File Locations

```
arifOS/
├── docs/60_REFERENCE/
│   └── UNIFIED_SKILLS_ARCHITECTURE.md    [THIS FILE]
├── arifos_aaa_mcp/
│   └── server.py                         [MCP tools]
├── .kimi/skills/                         [Kimi skills]
│   ├── arifos-trinity-refactor/SKILL.md
│   ├── vps-repo-ingest/SKILL.md
│   ├── vps-repo-analyze/SKILL.md
│   ├── arifos-agi-plan/SKILL.md
│   ├── arifos-asi-apply/SKILL.md
│   └── arifos-guardian-check/SKILL.md
└── scripts/
    └── vps_git_ingest.py                 [VPS tool impl]
```

---

## 11. Quick Start

```bash
# 1. Start arifOS MCP server on VPS
ssh root@srv1325122.hstgr.cloud
cd /srv/arifOS
docker compose up -d arifosmcp

# 2. Configure Kimi Code
kimi mcp add arifos-vps \
  --command "ssh root@srv1325122.hstgr.cloud 'cd /srv/arifOS && python -m arifos_aaa_mcp stdio'"

# 3. Use master skill
kimi skill use arifos-trinity-refactor

# 4. Run refactor
> Refactor the auth module in /src to use dependency injection
[INIT] → [AGI] → [ASI] → [APEX: SEAL] → [VAULT] → Changes applied
```

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.  
**Version:** v2026.3.1  
**Status:** CANONICAL
