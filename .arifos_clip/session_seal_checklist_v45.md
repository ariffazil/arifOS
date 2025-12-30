# arifOS v45.0 Session Seal Checklist

**Use this before closing any Claude Code / GitHub Copilot / CLI session.**

**Version:** v45.0 (Phoenix-72 Consolidation)
**Track B:** spec/v45/
**Tests:** 2180+ (100% passing)

---

## 🔍 666 ALIGN — Constitutional Floor Check

### Run Tests

```bash
# Core governance tests
pytest tests/test_apex_prime_floors.py -v
pytest tests/test_apex_genius_verdicts.py -v

# Integration tests
pytest tests/governance/ -v
pytest tests/evidence/ -v
pytest tests/judiciary/ -v

# All tests (2180+)
pytest -v

# Quick smoke test (5 tests)
pytest tests/test_apex_prime_floors.py -k "seal_verdict or void_verdict" -v
```

### Floor Verification

| Floor | Check | Command |
|-------|-------|---------|
| **F1 Amanah** | All changes reversible via Git? | `git log --oneline -5` |
| **F2 Truth** | Tests passing? Claims verified? | `pytest -v` |
| **F3 Tri-Witness** | PRIMARY sources cited? | Check code comments, git diffs |
| **F4 ΔS** | Documentation complete? Entropy reduced? | Check README updates, file count |
| **F5 Peace²** | No destructive operations? | `git diff --stat` (check deletions) |
| **F6 κᵣ** | Empathetic communication? | Review commit messages, comments |
| **F7 Ω₀** | Uncertainty acknowledged? | Check hedging language in docs |
| **F8 G** | Governed intelligence? | Verify governance imports |
| **F9 Anti-Hantu** | No fabricated claims? | Verify all constitutional claims |

**Expected:** ✅ All 9 floors PASS

### Track B Integrity (v45.0)

```bash
# Verify spec integrity
python scripts/regenerate_manifest_v45.py --check

# Test schema enforcement
pytest tests/test_spec_v44_schema_enforcement_subprocess.py -v

# Test manifest enforcement
pytest tests/test_spec_v44_manifest_enforcement_subprocess.py -v
```

**Expected:** All hashes match MANIFEST.sha256.json

---

## 🔨 777 FORGE — Stage Changes

### Check Status

```bash
# What changed?
git status

# Detailed diff
git diff --stat
git diff

# Check for untracked files
git status --short
```

### Stage Relevant Files

**L2_GOVERNANCE v45.0 (if applicable):**
```bash
# Universal modular files
git add L2_GOVERNANCE/universal/base_governance_v45.yaml
git add L2_GOVERNANCE/universal/conversational_overlay_v45.yaml
git add L2_GOVERNANCE/universal/code_generation_overlay_v45.yaml
git add L2_GOVERNANCE/universal/agent_builder_overlay_v45.yaml
git add L2_GOVERNANCE/universal/trinity_display_v45.yaml

# Integration files
git add L2_GOVERNANCE/integration/gpt_builder.yaml
git add L2_GOVERNANCE/integration/gemini_gems.yaml
git add L2_GOVERNANCE/mcp/integration_guide.md

# Documentation
git add L2_GOVERNANCE/README.md
```

**Master Agent Files (if applicable):**
```bash
git add AGENTS.md
git add CLAUDE.md
git add CODEX.md
git add GEMINI.md
```

**Core Changes (if applicable):**
```bash
# Governance core
git add arifos_core/judiciary/
git add arifos_core/evidence/
git add arifos_core/enforcement/

# Tests
git add tests/governance/
git add tests/evidence/
git add tests/judiciary/

# Specs (Track B)
git add spec/v45/*.json
git add spec/v45/MANIFEST.sha256.json

# Canon (Track A)
git add L1_THEORY/canon/

# Documentation
git add README.md
git add docs/
```

### Review Staged Changes

```bash
# Summary
git diff --staged --stat

# Detailed review
git diff --staged

# Verify no secrets
git diff --staged | grep -i "api_key\|password\|secret\|token"
```

**Expected:** No secrets, all changes intentional

---

## ⚖️ 888 HOLD — Governance Audit

### Ledger Integrity

```bash
# Verify cooling ledger
arifos-verify-ledger

# Compute Merkle root
arifos-compute-merkle

# Show recent entries
tail -n 5 cooling_ledger/L1_cooling_ledger.jsonl
```

**Expected:** Hash chain intact, Merkle root valid

### Governance Analysis

```bash
# Analyze recent decisions
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl --output reports/session_audit.json

# View report
cat reports/session_audit.json | jq '.summary'
```

### Human Review Questions

**Constitutional Changes:**
- [ ] Did I modify PRIMARY sources (canon, spec, core)?
- [ ] If yes, did I follow Phoenix-72 cooling (72h review window)?
- [ ] Are all threshold changes justified and documented?

**File Integrity (Anti-Janitor):**
- [ ] Did I avoid "cleaning up" files by removing sections?
- [ ] Are all edits surgical (append or specific replacements)?
- [ ] If `new_lines < old_lines`, is this intentional deletion?

**Testing:**
- [ ] Do all 2180+ tests pass?
- [ ] Did I add tests for new features?
- [ ] Did I update test count in README/AGENTS.md if changed?

**Documentation:**
- [ ] Are all new files documented?
- [ ] Did I update relevant README sections?
- [ ] Did I cite PRIMARY sources (not grep results)?

**L2_GOVERNANCE Sync (if applicable):**
- [ ] Do L2 YAML files derive from spec/v45/*.json?
- [ ] Did I regenerate MANIFEST.sha256.json if spec changed?
- [ ] Are platform integrations up to date?

---

## ✅ 999 SEAL — Commit & Close

### Commit Format (Conventional Commits)

```bash
# Format:
# <type>(<scope>): <description>
#
# <body with details>
#
# Tests: X/X passing
# Floors: F1=... F2=... F4=... F5=... F7=... F8=... F9=...
# Verdict: SEAL
#
# 🤖 Generated with [Claude Code](https://claude.com/claude-code)
#
# Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

# Example:
git commit -m "$(cat <<'EOF'
feat(l2): L2_GOVERNANCE v45.0 modular architecture

## Changes

- Created 8 NEW files (base_governance + 3 overlays + trinity_display + 2 integrations + MCP guide)
- Updated 5 files (README + 4 integration files)
- Modular architecture: Identity Root + Logic Roots + Display Root

## Derivation Loop

Track A (canon) + Track B (spec) → L2_GOVERNANCE (YAML) → Platforms

## Verification

Tests: 2180+ passing (100%)
Floors: F1=LOCK F2=0.99 F4=ΔS≥0 F5=1.0 F7=[0.03,0.05] F8=0.80 F9<0.30
Verdict: SEAL

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Commit Types

| Type | Use Case | Example |
|------|----------|---------|
| `feat` | New feature | `feat(trinity): Add ASI/AGI/APEX display modes` |
| `fix` | Bug fix | `fix(floors): Correct F2 threshold to 0.99` |
| `docs` | Documentation only | `docs(readme): Add Trinity Display section` |
| `refactor` | Code refactor (no behavior change) | `refactor(evidence): Extract atomic_ingest() method` |
| `test` | Test additions/changes | `test(governance): Add Sovereign Witness tests` |
| `chore` | Maintenance (deps, build, etc.) | `chore(deps): Upgrade pydantic to 2.0` |

### Push to Remote

```bash
# Push (if ready for remote)
git push origin main

# Or create branch first
git checkout -b feature/trinity-display
git push -u origin feature/trinity-display
```

**888_HOLD:** If pushing to main, ensure:
- All tests pass (2180+)
- Ledger verified
- No breaking changes (or documented)
- Phoenix-72 cooling complete (if constitutional change)

---

## 📦 Post-Seal Verification

### Verify Push

```bash
# Check recent commits
git log --oneline -5

# Verify remote sync
git fetch origin
git status
```

**Expected:** "Your branch is up to date with 'origin/main'"

### Tag Release (if major milestone)

```bash
# Create annotated tag
git tag -a v45.0.1 -m "L2_GOVERNANCE v45.0: Modular Architecture Complete"

# Push tag
git push origin v45.0.1

# List tags
git tag -l "v45.*"
```

### Archive Session

```bash
# Create dated archive
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p .arifos_clip/archive/$DATE

# Move session artifacts
mv .arifos_clip/claude_code_self_assessment.md .arifos_clip/archive/$DATE/
mv .arifos_clip/readme_feature_audit_v45.md .arifos_clip/archive/$DATE/
mv .arifos_clip/session.json .arifos_clip/archive/$DATE/

# Or use descriptive name
mkdir -p .arifos_clip/archive/2025-12-30_L2_Governance_v45
mv .arifos_clip/*.md .arifos_clip/archive/2025-12-30_L2_Governance_v45/
```

---

## 🎓 Session Close Canary (v45.0)

```
╔═══════════════════════════════════════════════════════════════════╗
║  [STAGE 999] SEAL COMPLETE — arifOS v45.0                        ║
║  ─────────────────────────────────────────────────────────────── ║
║  Session: [Your session description]                              ║
║  Tests: 2180+ PASSING (100%)                                      ║
║  Track B: spec/v45/ (SHA-256 verified)                            ║
║  Trinity Display: ASI mode (Ω) default                            ║
║  ─────────────────────────────────────────────────────────────── ║
║  Floors: F1=LOCK ✓  F2≥0.99 ✓  F3≥0.95 ✓  F4≥0 ✓                ║
║          F5≥1.0 ✓   F6≥0.95 ✓  F7∈[0.03,0.05] ✓                  ║
║          F8≥0.80 ✓  F9<0.30 ✓                                     ║
║  ─────────────────────────────────────────────────────────────── ║
║  Verdict: SEAL ✅                                                 ║
║  Memory: LEDGER + ACTIVE                                          ║
║  Phoenix-72: [No amendments pending / Cooling X hrs remaining]    ║
║  ─────────────────────────────────────────────────────────────── ║
║  DITEMPA BUKAN DIBERI — Forged, not given.                        ║
║  Akal Memerintah. Amanah Mengunci.                                ║
╚═══════════════════════════════════════════════════════════════════╝
```

**Session may now close safely.**

---

## 🔄 Trinity Display Mode Awareness (v45.0)

**Before closing session, verify display mode:**

| Mode | When to Use | What User Sees |
|------|-------------|----------------|
| **ASI** (Guardian) | Default (public-facing) | Clean output only, no metrics |
| **AGI** (Architect) | Developer debugging | Pipeline + ΔΩΨ Trinity (3 numbers) |
| **APEX** (Judge) | Auditor forensic review | Full F1-F9 floors + claim analysis |

**Session default:** ASI mode (Ω)

**To escalate:**
- `/agi` → Developer view
- `/apex` → Full forensic

**Philosophy:** "Measure everything. Show nothing (unless authorized)."

---

## 📋 Quick Checklist (Copy-Paste)

**Before committing:**

- [ ] All tests pass (`pytest -v`)
- [ ] Track B integrity (`python scripts/regenerate_manifest_v45.py --check`)
- [ ] Ledger verified (`arifos-verify-ledger`)
- [ ] No secrets in diff (`git diff --staged | grep -i secret`)
- [ ] F1 Amanah (all reversible via git)
- [ ] F2 Truth (PRIMARY sources cited)
- [ ] F4 ΔS (documentation complete, entropy reduced)
- [ ] F9 Anti-Hantu (no fabricated claims)
- [ ] Commit message follows format (type(scope): description)
- [ ] Session artifacts archived (`.arifos_clip/archive/`)

**After committing:**

- [ ] Push succeeded (`git log --oneline -5`)
- [ ] Tag created (if major milestone)
- [ ] Session archived (`.arifos_clip/archive/YYYYMMDD/`)
- [ ] Canary displayed (999 SEAL COMPLETE)

---

**DITEMPA BUKAN DIBERI**

The forge is sealed. The law is synchronized. The session may close.

**Version:** v45.0 (Phoenix-72 Consolidation)
**Last Updated:** 2025-12-30
**Maintainer:** Human (Arif) + Claude Code
