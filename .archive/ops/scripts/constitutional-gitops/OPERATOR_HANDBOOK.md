# Operator Handbook: Constitutional GitOps for Agent Developers

**Version:** 2026.03.24  
**Prerequisites:** Git, Python 3.8+, `arif-sites` cloned locally

---

## Quick Start (5-Minute Setup)

```bash
# 1. Clone arif-sites (contains the toolchain)
git clone https://github.com/ariffazil/arif-sites.git
cd arif-sites

# 2. Add to PATH
export PATH="$PATH:$(pwd)/scripts/constitutional-gitops"

# 3. Verify installation
arifos-worktree-add.sh --help
```

---

## The 5-Step Workflow

### Step 1: Create Constitutional Sandbox

```bash
# Syntax: arifos-worktree-add.sh <agent-name> <feature-slug>
arifos-worktree-add.sh claude api-refactor
```

**What happens:**
- Creates worktree: `../arifos-worktrees/arifos-claude-api-refactor/`
- Creates branch: `feature/claude-api-refactor`
- Generates `arifos.yml` with your agent identity and risk tier

**Verify:**
```bash
cd ../arifos-worktrees/arifos-claude-api-refactor
ls -la
# Should see: arifos.yml, .gitignore, and your repo files
```

---

### Step 2: Develop Under F7 (Humility)

```bash
# Enter the sandbox
cd ../arifos-worktrees/arifos-claude-api-refactor

# Run agent with dry_run enforced
arifos-agent-run.sh
```

**Key constraints:**
- `dry_run: true` by default — no irreversible actions
- All work isolated to this worktree
- `main` branch untouched

**Develop normally:**
```bash
# Write code, add tests
echo "def new_feature(): pass" > feature.py
git add .
git commit -m "feat: implement api refactor"
```

---

### Step 3: Evaluate with Tri-Witness (F3)

```bash
# Run F3 evaluation locally
arifos_f3_eval.py --worktree .
```

**Expected output:**
```
🔥 F3 TRI-WITNESS EVALUATION
🤖 AI:     0.87
🌍 Earth:  0.92
👤 Human:  0.00

W₃ = 0.00
🚨 VERDICT: HOLD_888
```

**Interpretation:**
- **HOLD_888** = Medium+ risk, no human approval yet
- **SEAL** = Ready to push (rare without human review)
- **VOID** = Rejected, fix issues first

**Check what needs work:**
```bash
# Detailed JSON output
arifos_f3_eval.py --json | jq .
```

---

### Step 4: Push and Open PR

```bash
# Push to origin (even HOLD_888 is OK for draft PR)
git push origin feature/claude-api-refactor

# Open PR via GitHub CLI or web
git checkout main  # Return to main first
gh pr create --title "feat: api refactor" --body-file PR_DRAFT.md
```

**888_JUDGE runs automatically:**
- CI reads your `arifos.yml`
- Computes Tri-Witness
- Posts verdict as PR comment

**For HOLD_888:**
- Mark PR as **Draft**
- Request review from Arif (F13)
- Wait for human approval

---

### Step 5: Collapse or Merge

**If approved (SEAL):**
```bash
# PR merged via GitHub UI
# Clean up local worktree
cd /path/to/arif-sites
arifos-worktree-remove.sh feature/claude-api-refactor
```

**If rejected (VOID):**
```bash
# Immediately collapse universe
cd /path/to/arif-sites
arifos-worktree-remove.sh feature/claude-api-refactor

# Worktree and branch deleted
# Main repo untouched (F1 guaranteed)
```

---

## Common Workflows

### Low-Risk Docs Fix (SEAL Path)

```bash
arifos-worktree-add.sh docs readme-typo
cd ../arifos-worktrees/arifos-docs-readme-typo
echo "# Fix" >> README.md
git commit -am "docs: fix typo"
arifos_f3_eval.py --worktree .  # Should show SEAL
git push origin feature/docs-readme-typo
# Open PR, merge, cleanup
```

### High-Risk Governance Change (HOLD_888 Path)

```bash
arifos-worktree-add.sh arif f2-clarification
cd ../arifos-worktrees/arifos-arif-f2-clarification
# Edit 000_THEORY/000_LAW.md
git commit -am "docs: clarify F2 truth threshold"
arifos_f3_eval.py --worktree . --enforce  # Exit 2, HOLD_888
# Push as draft PR, request Arif review
```

### Emergency Hotfix (F13 Override)

```bash
# Only Arif can create hotfix worktrees
arifos-worktree-add.sh arif hotfix-critical
cd ../arifos-worktrees/arifos-arif-hotfix-critical
# Fix, commit, push
# 888_JUDGE will flag HOLD_888 but branch protection allows F13 override
```

---

## Troubleshooting

### "No arifos.yml found" (Exit 1)

**Cause:** Worktree created manually, not via `arifos-worktree-add.sh`

**Fix:**
```bash
# Add manifest manually
cp /path/to/arif-sites/templates/arifos.yml.template ./arifos.yml
# Edit with your agent info
```

### "W₃ = 0.0" despite good code

**Cause:** Human witness = 0 (pending), medium+ risk requires >0.5

**Fix:**
```bash
# Edit arifos.yml to mark partial review
# Or accept HOLD_888 and open draft PR
```

### Cannot remove worktree

**Cause:** Uncommitted changes or active processes

**Fix:**
```bash
cd /path/to/worktree
git reset --hard HEAD  # Discard changes
cd /path/to/arif-sites
arifos-worktree-remove.sh feature/branch-name
```

---

## Exit Code Reference

| Code | Meaning | Action |
|------|---------|--------|
| `0` | Success | Verdict in payload, check output |
| `1` | Config error | Fix `arifos.yml` or reinstall |
| `2` | Enforce violated | `--enforce` flag + W₃ < 0.7 |

---

## Best Practices

1. **Always use worktrees** — Never develop on `main` directly
2. **Run F3 eval before push** — Catch issues locally, not in CI
3. **Treat HOLD_888 as guidance** — Not failure, needs human review
4. **Clean up after merge** — Remove worktrees to avoid clutter
5. **Update manifest** — Keep `arifos.yml` accurate as work evolves

---

## Integration with IDEs

### VS Code
```json
// .vscode/tasks.json
{
  "label": "F3 Evaluate",
  "type": "shell",
  "command": "arifos_f3_eval.py --worktree .",
  "group": "test"
}
```

### Git Hook (Pre-Push)
```bash
# .git/hooks/pre-push
arifos_f3_eval.py --worktree . --enforce || exit 2
```

---

## Getting Help

- **Tool issues:** Check `REGRESSION_TESTS.md` for validation
- **Constitutional questions:** See `000_THEORY/000_LAW.md` in arifOS
- **CI issues:** Check `.github/workflows/888-judge.yml` logs

---

*Ditempa bukan diberi.* 🔥
