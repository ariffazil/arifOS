# Constitutional GitOps Regression Test Specification

**Version:** 2026.03.24
**Scope:** Validate F1-F13 enforcement across filesystem, local evaluation, and CI layers

---

## Test Matrix

| Test ID | Scenario | Risk Tier | Expected Verdict | Exit Code | F13 Required |
|---------|----------|-----------|------------------|-----------|--------------|
| T-01 | Docs only (README typo) | low | SEAL | 0 | ❌ |
| T-02 | Feature with tests | medium | HOLD | 0 | ❌ (draft OK) |
| T-03 | Feature without human approval | medium | HOLD_888 | 0/2* | ✅ |
| T-04 | 0_KERNEL modification | high | HOLD_888 | 0/2* | ✅ |
| T-05 | Missing arifos.yml | — | ERROR | 1 | — |
| T-06 | Invalid syntax | — | VOID | 2 (if --enforce) | — |

*Exit 2 only with `--enforce` flag

---

## Test Scenarios

### T-01: Low-Risk Docs Change (SEAL Path)

**Objective:** Verify low-risk changes can auto-SEAL

**Steps:**
```bash
# 1. Create worktree
./scripts/constitutional-gitops/arifos-worktree-add.sh docs readme-fix

# 2. Make trivial docs change
cd ../arifos-worktrees/arifos-docs-readme-fix
echo "# Test" >> README.md
git add . && git commit -m "docs: fix typo"

# 3. Evaluate
./arifos_f3_eval.py --worktree . --json
```

**Expected:**
```json
{
  "w3": 0.88,
  "verdict": "SEAL",
  "can_push": true,
  "recommendation": "ready_to_merge"
}
```

**CI Verification:**
- Open PR → 888_JUDGE runs
- No blocking checks
- Merge allowed after review

---

### T-02: Medium-Risk Feature (HOLD Path)

**Objective:** Verify medium-risk changes require work but not F13

**Steps:**
```bash
# 1. Create feature worktree
./scripts/constitutional-gitops/arifos-worktree-add.sh claude api-refactor

# 2. Add feature code + tests
cd ../arifos-worktrees/arifos-claude-api-refactor
# ... write code ...
git add . && git commit -m "feat: api refactor with tests"

# 3. Evaluate (without human approval)
./arifos_f3_eval.py --worktree . --enforce
echo "Exit: $?"  # Should be 0 (not enforcing yet)
```

**Expected:**
```
🤖 AI:     0.87
🌍 Earth:  0.92
👤 Human:  0.00
W₃ = 0.00
🚨 VERDICT: HOLD_888
Exit: 0
```

**CI Verification:**
- PR marked as "draft recommended"
- 888_JUDGE comments with F3 status
- Merge blocked until human approval

---

### T-03: 0_KERNEL Modification (F13 Enforcement)

**Objective:** Verify governance paths require Arif (F13)

**Steps:**
```bash
# 1. Create worktree for governance change
./scripts/constitutional-gitops/arifos-worktree-add.sh arif f2-clarification

# 2. Edit constitutional floor
cd ../arifos-worktrees/arifos-arif-f2-clarification
echo "# F2 clarification" >> 000_THEORY/000_LAW.md
git add . && git commit -m "docs: clarify F2 truth threshold"

# 3. Evaluate
./arifos_f3_eval.py --worktree . --enforce
```

**Expected:**
```
⚠️  Risk: high
W₃ = 0.00
🚨 VERDICT: HOLD_888
Exit: 2
```

**CI Verification:**
- 888_JUDGE fails with "F13 REQUIRED"
- Branch protection blocks merge
- Only Arif can override

---

### T-04: Missing Manifest (Config Error)

**Objective:** Verify F4 enforcement (manifest required)

**Steps:**
```bash
# 1. Create manual worktree (bypassing script)
git worktree add ../test-manual -b feature/manual

# 2. Try to evaluate (no arifos.yml)
cd ../test-manual
/mnt/arifos/scripts/constitutional-gitops/arifos_f3_eval.py --worktree .
```

**Expected:**
```
❌ Config error (F4): No arifos.yml in /path/to/test-manual
Exit: 1
```

---

### T-05: F1 Reversibility

**Objective:** Verify worktree removal restores clean state

**Steps:**
```bash
# 1. Create and verify
./scripts/constitutional-gitops/arifos-worktree-add.sh temp test-f1
ls ../arifos-worktrees/arifos-temp-test-f1  # exists

# 2. Make changes
cd ../arifos-worktrees/arifos-temp-test-f1
echo "test" > test.txt && git add . && git commit -m "test"

# 3. Remove
./scripts/constitutional-gitops/arifos-worktree-remove.sh feature/temp-test-f1

# 4. Verify cleanup
ls ../arifos-worktrees/arifos-temp-test-f1  # should fail
```

**Expected:**
- Worktree directory removed
- Branch deleted
- Main repo unchanged

---

## Automated Test Script

```bash
#!/bin/bash
# run-regression-tests.sh

set -e

echo "🔥 Constitutional GitOps Regression Tests"
echo "=========================================="

ARIFOS_ROOT="/mnt/arifos"
TOOLCHAIN="$ARIFOS_ROOT/scripts/constitutional-gitops"

cd "$ARIFOS_ROOT"

# Test 1: Low-risk docs
echo "T-01: Low-risk docs change..."
$TOOLCHAIN/arifos-worktree-add.sh test docs-fix
cd ../arifos-worktrees/arifos-test-docs-fix
echo "# Test" >> README.md
git add . && git commit -m "docs: test"
$TOOLCHAIN/arifos_f3_eval.py --worktree . --json | grep -q "SEAL" && echo "✅ PASS" || echo "❌ FAIL"
cd "$ARIFOS_ROOT"
echo "VOID" | $TOOLCHAIN/arifos-worktree-remove.sh feature/test-docs-fix

# Test 2: Config error (no manifest)
echo "T-04: Missing manifest..."
git worktree add ../test-no-manifest -b feature/no-manifest 2>/dev/null || true
cd ../test-no-manifest
$TOOLCHAIN/arifos_f3_eval.py --worktree . 2>/dev/null
code=$?
if [ $code -eq 1 ]; then echo "✅ PASS (exit 1)"; else echo "❌ FAIL (exit $code)"; fi
cd "$ARIFOS_ROOT"
git worktree remove ../test-no-manifest --force 2>/dev/null || rm -rf ../test-no-manifest

# Test 3: F1 reversibility
echo "T-05: F1 reversibility..."
$TOOLCHAIN/arifos-worktree-add.sh test f1-test
worktree_path="../arifos-worktrees/arifos-test-f1-test"
[ -d "$worktree_path" ] && echo "✅ Created" || echo "❌ FAIL"
echo "VOID" | $TOOLCHAIN/arifos-worktree-remove.sh feature/test-f1-test
[ ! -d "$worktree_path" ] && echo "✅ Removed" || echo "❌ FAIL"

echo ""
echo "=========================================="
echo "Regression tests complete."
```

---

## CI Integration Test

Create `.github/workflows/test-constitutional-gitops.yml`:

```yaml
name: Test Constitutional GitOps
on: [workflow_dispatch]

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: T-01: Low-risk docs
        run: |
          ./scripts/constitutional-gitops/arifos-worktree-add.sh ci docs-test
          cd ../arifos-worktrees/arifos-ci-docs-test
          echo "# CI Test" >> README.md
          git add . && git commit -m "docs: ci test"
          ./arifos_f3_eval.py --worktree .

      - name: T-04: Missing manifest
        run: |
          git worktree add ../ci-no-manifest -b feature/ci-test
          cd ../ci-no-manifest
          # Should exit 1
          ! ./scripts/constitutional-gitops/arifos_f3_eval.py --worktree .
```

---

## Success Criteria

| Criterion | Status |
|-----------|--------|
| All T-01 through T-05 pass | ⏳ Pending CI |
| 888_JUDGE runs on PRs without breaking | ⏳ Pending CI |
| No direct main writes possible | ✅ Branch protection |
| Documentation complete | ✅ README.md exists |

---

*Ditempa bukan diberi.* 🔥
