# aCLIp — arifOS Constitutional Layer Interface

**Version:** 2026.03.24  
**Location:** `arifOS/scripts/aclip.py`  
**Purpose:** Unified CLI for constitutional GitOps, agent governance, and F1-F13 enforcement

---

## Philosophy

> aCLIp is the human interface to arifOS governance. Every command routes through constitutional floors (F1-F13) before execution.

| Principle | Implementation |
|-----------|----------------|
| **F1 (Reversibility)** | All changes sandboxed in worktrees |
| **F3 (Tri-Witness)** | `aclip f3 eval` computes W₃ before any push |
| **F7 (Humility)** | `dry_run` default, Ω₀ explicitly tracked |
| **F13 (Sovereignty)** | Arif holds veto on all governance paths |

---

## Command Tree

```
aclip
├── worktree          # F1: Constitutional sandboxes
│   ├── add <agent> <feature>   # Create sandbox + arifos.yml
│   ├── rm <branch>             # Collapse → VOID
│   └── list                    # Show all worktrees
│
├── agent             # F7: Agent execution
│   └── run [--stage]           # Execute with dry_run
│
├── f3                # F3: Tri-Witness evaluation
│   └── eval [--mode] [--enforce]   # Compute W₃ score
│
├── judge             # 888_JUDGE: CI/CD governance
│   ├── status                  # Check CI status
│   └── logs <pr-number>        # View 888_JUDGE logs
│
├── floor             # F1-F12: Floor auditing
│   ├── audit                   # Run full floor check
│   └── check <floor>           # Check specific floor (F1, F3, etc.)
│
├── vault             # VAULT999: Memory & lineage
│   ├── seal <commit>           # Seal to VAULT999
│   ├── verify <hash>           # Verify lineage
│   └── list                    # Show sealed entries
│
└── version           # Show aCLIp version
```

---

## Detailed Command Reference

### `aclip worktree add <agent> <feature>`

**Purpose:** Create F1-compliant constitutional sandbox

**F1 Guarantee:** Reversible — `rm -rf` worktree leaves main untouched

**Arguments:**
- `agent`: Agent identifier (claude, codex, gemini, arifos-bot)
- `feature`: Feature slug (kebab-case)

**Behavior:**
```bash
# Creates:
../arifos-worktrees/arifos-claude-api-refactor/
├── arifos.yml          # Auto-generated manifest
├── .gitignore          # F12: Secrets protection
└── [repo files]        # Git worktree

# Creates branch:
feature/claude-api-refactor → tracks origin/main
```

**Example:**
```bash
aclip worktree add claude api-refactor
# ✅ F1 SANDBOX CREATED
# 📁 Path:    ../arifos-worktrees/arifos-claude-api-refactor
# 🔒 Branch:  feature/claude-api-refactor
```

---

### `aclip worktree rm <branch>`

**Purpose:** Collapse universe → VOID

**F1 Guarantee:** Main repo untouched, branch deleted, directory removed

**Arguments:**
- `branch`: Full branch name (feature/claude-api-refactor)

**Behavior:**
```bash
# Destroys:
- Git worktree directory
- Git branch
- All uncommitted changes

# Preserves:
- Main repository
- Remote branch (if pushed)
```

**Safety:**
```bash
# Prompts for confirmation unless --force
aclip worktree rm feature/claude-api-refactor
# ⚠️  F1 REVERSIBILITY CHECK
# Type 'VOID' to confirm:
```

---

### `aclip worktree list`

**Purpose:** F5 (Peace²) — visibility of all constitutional states

**Output:**
```
WORKTREE                                    BRANCH                          STATUS
/mnt/arifos-worktrees/arifos-claude-api    feature/claude-api              active
/mnt/arifos-worktrees/arifos-codex-mcp     feature/codex-mcp-hardening     sealed
```

---

### `aclip agent run [--worktree PATH] [--stage STAGE]`

**Purpose:** Execute agent under F7 (Humility) constraints

**F7 Guarantee:** `dry_run: true` by default, Ω₀ explicitly tracked

**Arguments:**
- `--worktree`: Path to sandbox (default: current directory)
- `--stage`: Execution stage (dev | staging | prod)

**Behavior:**
```bash
# Enters worktree
# Sets ARIFOS_DRY_RUN=1
# Executes agent via configured runtime (acp | subagent | direct)
# Hands off to F3 evaluation
```

**Example:**
```bash
cd ../arifos-worktrees/arifos-claude-api-refactor
aclip agent run --stage prod
# ▶ F1 Sandbox: /mnt/arifos-worktrees/arifos-claude-api-refactor
# ▶ Stage: prod
# ⚖️  F7: Ω₀ enforced — dry_run mode active
```

---

### `aclip f3 eval [--worktree PATH] [--mode MODE] [--json] [--enforce]`

**Purpose:** Compute Tri-Witness (F3) consensus

**F3 Formula:** `W₃ = (Human × AI × Earth)^(1/3)`

**Arguments:**
| Flag | Description | Default |
|------|-------------|---------|
| `--worktree` | Path to evaluate | `.` |
| `--mode` | Evaluation context | `pre-push` |
| `--json` | Machine-readable output | `false` |
| `--enforce` | Exit 2 if below threshold | `false` |

**Modes:**
- `pre-push`: Local evaluation before git push
- `pr-draft`: Pre-PR check, allows lower thresholds
- `ci`: Non-interactive CI mode

**Exit Codes:**
| Code | Meaning |
|------|---------|
| `0` | Executed (any verdict in output) |
| `1` | Config error (missing/invalid arifos.yml) |
| `2` | Enforce violated (VOID or W₃ < hold_min) |

**Output (human):**
```
🔥 F3 TRI-WITNESS EVALUATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI:     0.87
🌍 Earth:  0.92
👤 Human:  0.00

W₃ = 0.00
Threshold (medium): 0.95

🚨 VERDICT: HOLD_888
Can push: False
f13_review_required
```

**Output (JSON):**
```json
{
  "worktree": "/mnt/arifos-worktrees/arifos-claude-api",
  "witness": {
    "ai": {"score": 0.87, "source": "heuristic"},
    "earth": {"score": 0.92, "source": "local_tests"},
    "human": {"raw_status": "pending", "score": 0.0}
  },
  "w3": 0.0,
  "verdict": "HOLD_888",
  "can_push": false
}
```

---

### `aclip judge status`

**Purpose:** Check 888_JUDGE CI/CD governance status

**Output:**
```
🔥 888_JUDGE Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CI/CD: GitHub Actions
Workflow: .github/workflows/888-judge.yml
Status: Active on all PRs to main

Verdicts: SEAL | PROVISIONAL | SABAR | HOLD | HOLD_888 | VOID
Thresholds: low=0.85 | medium=0.95 | high=0.99 | critical=1.0

Governance Paths (Phase 2+):
- 0_KERNEL/
- 000_THEORY/
- Floor definitions
- Constitutional law
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### `aclip floor audit`

**Purpose:** Full F1-F13 constitutional compliance check

**Output:**
```
🔥 CONSTITUTIONAL FLOOR AUDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F1  Amanah (Reversibility)     ✅ Worktree pattern
F2  Truth                      ✅ Tests present
F3  Tri-Witness                ⚠️  Human pending
F4  Clarity                    ✅ Naming convention
F5  Peace²                     ✅ State visible
F6  Empathy                    ✅ Agent isolated
F7  Humility                   ✅ dry_run enforced
F8  Genius                     ✅ G* > 0.8
F9  Anti-Hantu                 ✅ No consciousness claims
F10 Ontology                   ✅ Explicit semantics
F11 Command Auth               ✅ Branch separation
F12 Injection Defense          ✅ .gitignore
F13 Sovereignty                ✅ Arif veto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Verdict: HOLD (F3 requires human review)
```

---

### `aclip vault seal <commit>`

**Purpose:** Seal commit hash to VAULT999 immutable ledger

**VAULT999:** Permanent, cryptographically signed record

**Example:**
```bash
aclip vault seal a3e73034
# 🔒 SEALED to VAULT999
# Hash: a3e73034...
# Timestamp: 2026-03-24T05:30:00Z
# Signature: [cryptographic proof]
```

---

## Implementation Architecture

```
┌─────────────────────────────────────────────┐
│  aclip (Unified CLI)                       │
│  scripts/aclip.py                          │
├─────────────────────────────────────────────┤
│  Command Router                             │
│  ├── worktree/ → arifos-worktree-*.sh      │
│  ├── agent/    → arifos-agent-run.sh       │
│  ├── f3/       → arifos_f3_eval.py         │
│  ├── judge/    → GitHub API                │
│  ├── floor/    → floor check scripts       │
│  └── vault/    → VAULT999 ledger           │
├─────────────────────────────────────────────┤
│  Constitutional Floors (F1-F13)            │
├─────────────────────────────────────────────┤
│  arifOS Kernel + MCP Tools                  │
└─────────────────────────────────────────────┘
```

---

## Entry Point Setup

```bash
# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="/mnt/arifOS/scripts:$PATH"

# Create alias for convenience
alias aclip="/mnt/arifOS/scripts/aclip.py"
```

---

## Future Extensions

| Command | Purpose | Priority |
|---------|---------|----------|
| `aclip floor peace2` | Lyapunov stability metrics | Phase 2 |
| `aclip agent spawn` | Spawn sub-agents via MCP | Phase 2 |
| `aclip judge override` | F13 sovereign override (Arif only) | Phase 3 |
| `aclip vault query` | Semantic search VAULT999 | Phase 3 |

---

## Comparison: aclip vs aclip-cai

| Tool | Scope | User |
|------|-------|------|
| **aclip-cai** | AI agent reasoning, planning | Agents |
| **aclip** (new) | GitOps, constitutional governance | Humans |

**Unified under:** arifOS Constitutional Layer Interface family

---

*Ditempa bukan diberi.* 🔥
