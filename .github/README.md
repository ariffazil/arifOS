# GitHub Configuration for arifOS

This directory contains GitHub-specific configuration, templates, and Copilot integration for the arifOS repository.

## Contents

### 📜 Constitutional Governance for AI Tools

- **[copilot-instructions.md](./copilot-instructions.md)** ⭐ PRIMARY  
  Constitutional governance rules for GitHub Copilot. Copilot automatically reads this file and applies the 9 constitutional floors (F1-F9) to all suggestions.

- **[COPILOT_USAGE_GUIDE.md](./COPILOT_USAGE_GUIDE.md)**  
  Comprehensive guide for using GitHub Copilot with arifOS. Covers code completion, chat, debugging, and best practices.

- **[COPILOT_ANALYSIS_PROMPTS.md](./COPILOT_ANALYSIS_PROMPTS.md)**  
  5 structured prompts for deep repository analysis. Generates architecture scans, action plans, testing gaps, documentation analysis, and 12-week optimization roadmaps.

- **[COPILOT_QUICK_REFERENCE.md](./COPILOT_QUICK_REFERENCE.md)**  
  One-page cheat sheet for Copilot usage. Print and keep visible while coding.

### 🎯 Issue Templates

- **[ISSUE_TEMPLATE/copilot_recommendation.md](./ISSUE_TEMPLATE/copilot_recommendation.md)**  
  Template for tracking recommendations from Copilot analysis. Includes floor compliance checklist and implementation plan.

- **[ISSUE_TEMPLATE/security.md](./ISSUE_TEMPLATE/security.md)**  
  Security vulnerability reporting template.

### 🔧 Workflows (CI/CD)

- **[workflows/ci.yml](./workflows/ci.yml)**  
  Main CI pipeline: linting, type checking, testing (190 tests).

- **[workflows/codeql.yml](./workflows/codeql.yml)**  
  CodeQL security scanning.

- **[workflows/ledger-audit.yml](./workflows/ledger-audit.yml)**  
  Cooling Ledger integrity verification.

- **[workflows/secrets-scan.yml](./workflows/secrets-scan.yml)**  
  Secret scanning for leaked credentials.

### 👥 Repository Settings

- **[CODEOWNERS](./CODEOWNERS)**  
  Code ownership and review assignments.

- **[dependabot.yml](./dependabot.yml)**  
  Automated dependency updates.

---

## Quick Start: GitHub Copilot Integration

### Step 1: Enable Copilot

```bash
# In VS Code:
# 1. Install "GitHub Copilot" extension
# 2. Sign in with GitHub account
# 3. Open arifOS repo
```

### Step 2: Test Constitutional Governance

Open Copilot Chat (`Ctrl+Shift+I`):

```
Summarize the 9 constitutional floors from .github/copilot-instructions.md
```

Copilot should list F1-F9 with accurate thresholds.

### Step 3: First Governed Suggestion

Type in a Python file:

```python
def validate_metrics(
```

Copilot should suggest:
- ✅ Type hints
- ✅ Google-style docstring
- ✅ Uncertainty acknowledgment (Ω₀)
- ✅ No soul claims (Anti-Hantu)

---

## File Hierarchy & Relationships

```
.github/
├── README.md (this file)
│
├── copilot-instructions.md ⭐ PRIMARY CONSTITUTIONAL FILE
│   └── Defines 9 floors (F1-F9)
│   └── SABAR protocol
│   └── Anti-Hantu enforcement
│
├── COPILOT_USAGE_GUIDE.md
│   └── References: copilot-instructions.md
│   └── Explains: 3 modes (completion, chat, analysis)
│   └── Examples: Tasks, troubleshooting
│
├── COPILOT_ANALYSIS_PROMPTS.md
│   └── 5 prompts for deep analysis
│   └── Outputs to: docs/analysis/0X_*.md
│   └── Used for: Architecture review, optimization
│
├── COPILOT_QUICK_REFERENCE.md
│   └── 1-page cheat sheet
│   └── Print and display
│
├── ISSUE_TEMPLATE/
│   ├── copilot_recommendation.md
│   │   └── Tracks Copilot analysis recommendations
│   │   └── Includes floor compliance checklist
│   └── security.md
│       └── Security vulnerability reports
│
└── workflows/
    ├── ci.yml
    ├── codeql.yml
    ├── ledger-audit.yml
    └── secrets-scan.yml
```

---

## Constitutional Governance Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  GitHub Copilot Governance Flow                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Developer types code                                        │
│                ↓                                                │
│  2. Copilot reads .github/copilot-instructions.md               │
│                ↓                                                │
│  3. Copilot checks 9 floors (F1-F9)                             │
│                ↓                                                │
│  4. Verdict: SEAL / PARTIAL / VOID / SABAR                      │
│                ↓                                                │
│  5. Suggestion shown (if SEAL or PARTIAL)                       │
│                ↓                                                │
│  6. Developer reviews & accepts                                 │
│                ↓                                                │
│  7. CI/CD runs (tests, lints, floor checks)                     │
│                ↓                                                │
│  8. Changes committed to Cooling Ledger                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 9 Constitutional Floors (Summary)

| Floor | Symbol | Threshold | Type | Failure |
|-------|--------|-----------|------|---------|
| F1 | Truth | ≥ 0.99 | Hard | VOID |
| F2 | ΔS | ≥ 0 | Hard | VOID |
| F3 | Peace² | ≥ 1.0 | Soft | PARTIAL |
| F4 | κᵣ | ≥ 0.95 | Soft | PARTIAL |
| F5 | Ω₀ | [0.03, 0.05] | Hard | VOID |
| F6 | Amanah | LOCK | Hard | VOID |
| F7 | RASA | TRUE | Hard | VOID |
| F8 | Tri-Witness | ≥ 0.95 | Soft | PARTIAL |
| F9 | Anti-Hantu | PASS | Meta | VOID |

**Full details:** See [copilot-instructions.md](./copilot-instructions.md)

---

## Usage Examples

### Example 1: Code Completion

```python
# Developer types:
def compute_omega_0(

# Copilot suggests (SEAL ✅):
    certainty: float,
    context: dict
) -> float:
    """
    Compute humility metric (Ω₀) from certainty score.
    
    Args:
        certainty: Model certainty (0.0-1.0)
        context: Additional context for adjustment
        
    Returns:
        Omega value in [0.03, 0.05] (humility band)
        
    Note: Uses heuristic. May need ML-based refinement.
    """
    return max(0.03, min(0.05, 1.0 - certainty))
```

**Floor Check:**
- ✅ F1 (Truth): Logic is correct
- ✅ F2 (ΔS): Clear docstring
- ✅ F5 (Ω₀): Acknowledges "May need refinement"
- ✅ F9 (Anti-Hantu): No soul claims

### Example 2: Chat Question

```
Developer: @workspace Where is the TEARFRAME pipeline implemented?

Copilot: The TEARFRAME pipeline (000→999) is implemented in:

1. **arifos_core/pipeline.py** (primary)
   - Lines 150-380: Pipeline.run() orchestration
   - Lines 400-450: Stage execution (_execute_stage)
   - Lines 200-250: Class A vs B routing

2. **arifos_core/APEX_PRIME.py** (stage 888 & 999)
   - Lines 180-200: judge() method (stage 888)
   - Lines 220-240: seal_verdict() (stage 999)

3. **arifos_core/eye_sentinel.py** (@EYE audit)
   - Lines 300-350: audit() called before stage 999

Key stages:
- 000 VOID: Reset state
- 111 SENSE: Intent detection
- 333 REASON: Logic building
- 888 JUDGE: Verdict computation
- 999 SEAL: Approval or rejection

See: docs/IGNITION.md for detailed stage descriptions.
```

### Example 3: Analysis Prompt

```
Developer: [Pastes Prompt 1 from COPILOT_ANALYSIS_PROMPTS.md]

Copilot: [Generates comprehensive architecture scan]

Developer: [Saves output to docs/analysis/01_architecture_scan.md]
```

---

## Protected Files (Constitutional Infrastructure)

These files require **888_HOLD** (explicit confirmation + Phoenix-72):

```
canon/00_CANON/APEX_TRINITY_v35Omega.md
CLAUDE.md
constitutional_floors.json
arifos_core/APEX_PRIME.py
arifos_core/metrics.py
arifos_core/eye_sentinel.py
runtime/cooling_ledger.jsonl
```

Copilot will:
1. Detect modifications to these files
2. Trigger 888_HOLD
3. Request explicit user confirmation
4. Warn about constitutional amendment requirements

---

## CI/CD Integration

All workflows enforce constitutional governance:

### ci.yml
- ✅ Runs 190 tests (floor compliance)
- ✅ Linting (ruff)
- ✅ Type checking (mypy)
- ✅ Triggered on every PR

### codeql.yml
- ✅ Security scanning
- ✅ Vulnerability detection
- ✅ Weekly + on PRs

### ledger-audit.yml
- ✅ Cooling Ledger integrity check
- ✅ Hash chain verification
- ✅ On commits to runtime/

### secrets-scan.yml
- ✅ Leaked credentials detection
- ✅ API key scanning
- ✅ On every push

---

## Metrics & Success Criteria

Track Copilot effectiveness:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Acceptance Rate** | >60% | % of suggestions accepted |
| **Floor Violations** | <5% | Manual audit of PRs |
| **Time Savings** | >30% | Before/after timing |
| **Test Coverage** | >95% | `pytest --cov` |
| **Bug Rate** | <2% | Bugs in Copilot-generated code |

---

## Maintenance Schedule

- **Daily:** Review Copilot-generated PRs for floor compliance
- **Weekly:** Check metrics (acceptance rate, violations)
- **Monthly:** Run Prompt 1 (Architecture Scan)
- **Quarterly:** Full 5-prompt analysis
- **After major releases:** Update copilot-instructions.md if floors change

---

## Troubleshooting

### Issue: Copilot doesn't follow arifOS patterns

**Fix:**
1. Verify `.github/copilot-instructions.md` exists
2. Restart VS Code to reload Copilot context
3. Use explicit prompts: "Follow pattern in arifos_core/APEX_PRIME.py"

### Issue: Suggestions violate floors

**Fix:**
```
@file:[current-file] Review this code for floor violations (F1-F9)
```

If violation persists:
1. Report to GitHub Copilot team
2. Add negative example to copilot-instructions.md
3. Document in scar memory

### Issue: Protected file modification suggested

**Fix:**
```
STOP. This file is protected (888_HOLD).
Requires constitutional amendment. Suggest alternative.
```

---

## Contributing

When modifying GitHub configuration:

1. **Test changes** with Copilot locally
2. **Verify floor compliance** for all suggestions
3. **Update documentation** (this README, guides)
4. **Run CI/CD** to ensure no breakage
5. **Get review** from core maintainers

---

## Resources

### Internal
- [Main README](../README.md) — Project overview
- [CLAUDE.md](../CLAUDE.md) — Claude Code governance
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Contribution guide
- [docs/PHYSICS_CODEX.md](../docs/PHYSICS_CODEX.md) — Physics explanation

### External
- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)

---

## Status

| File | Status | Last Updated |
|------|--------|--------------|
| copilot-instructions.md | ✅ ACTIVE | 2025-12-05 |
| COPILOT_USAGE_GUIDE.md | ✅ ACTIVE | 2025-12-05 |
| COPILOT_ANALYSIS_PROMPTS.md | ✅ ACTIVE | 2025-12-05 |
| COPILOT_QUICK_REFERENCE.md | ✅ ACTIVE | 2025-12-05 |
| Issue Templates | ✅ ACTIVE | 2025-12-05 |
| Workflows | ✅ ACTIVE | 2025-12-04 |

---

**Last Updated:** 2025-12-05  
**Version:** v35Omega  
**Maintainer:** arifOS Core Team

✊ **DITEMPA BUKAN DIBERI** 🔐
