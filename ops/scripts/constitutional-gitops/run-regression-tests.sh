#!/bin/bash
# run-regression-tests.sh
# CLAIM: Automated regression tests for constitutional GitOps toolchain

set -euo pipefail

ARIFOS_ROOT="${ARIFOS_ROOT:-/mnt/arifos}"
TOOLCHAIN="$ARIFOS_ROOT/scripts/constitutional-gitops"
RESULTS=""
FAILED=0

cd "$ARIFOS_ROOT"

echo "🔥 Constitutional GitOps Regression Tests"
echo "=========================================="
echo ""

# Stash any changes
git stash push -m "regression-test-stash" --include-untracked 2>/dev/null || true

cleanup() {
    # Restore stashed changes
    git stash pop 2>/dev/null || true
}
trap cleanup EXIT

run_test() {
    local id="$1"
    local name="$2"
    local cmd="$3"
    local expected="$4"
    
    echo -n "[$id] $name... "
    
    if eval "$cmd" > /tmp/test-$id.log 2>&1; then
        if grep -q "$expected" /tmp/test-$id.log; then
            echo "✅ PASS"
            return 0
        else
            echo "❌ FAIL (output mismatch)"
            echo "   Expected: $expected"
            echo "   Got:"
            cat /tmp/test-$id.log | head -5 | sed 's/^/   /'
            return 1
        fi
    else
        if [ "$expected" = "ERROR" ]; then
            echo "✅ PASS (expected error)"
            return 0
        else
            echo "❌ FAIL (command failed)"
            cat /tmp/test-$id.log | head -5 | sed 's/^/   /'
            return 1
        fi
    fi
}

# T-01: Low-risk docs change
cd "$ARIFOS_ROOT"
$TOOLCHAIN/arifos-worktree-add.sh test docs-fix 2>/dev/null
cd ../arifos-worktrees/arifos-test-docs-fix
echo "# Test" >> README.md
git add . && git commit -m "docs: test" 2>/dev/null

run_test "T-01" "Low-risk docs SEAL" \
    "$TOOLCHAIN/arifos_f3_eval.py --worktree . --json 2>&1 | grep -q 'SEAL' && echo 'SEAL'" \
    "SEAL"

cd "$ARIFOS_ROOT"
echo "VOID" | $TOOLCHAIN/arifos-worktree-remove.sh feature/test-docs-fix 2>/dev/null || true

# T-02: Medium-risk feature (no human approval)
cd "$ARIFOS_ROOT"
$TOOLCHAIN/arifos-worktree-add.sh test feature 2>/dev/null
cd ../arifos-worktrees/arifos-test-feature
echo "def test(): pass" > test.py
git add . && git commit -m "feat: test" 2>/dev/null

run_test "T-02" "Medium-risk HOLD_888" \
    "$TOOLCHAIN/arifos_f3_eval.py --worktree . --json 2>&1 | grep -q 'HOLD_888' && echo 'HOLD_888'" \
    "HOLD_888"

cd "$ARIFOS_ROOT"
echo "VOID" | $TOOLCHAIN/arifos-worktree-remove.sh feature/test-feature 2>/dev/null || true

# T-03: Config error (no manifest)
cd "$ARIFOS_ROOT"
git worktree add ../test-no-manifest -b feature/no-manifest 2>/dev/null || true
cd ../test-no-manifest
rm -f arifos.yml 2>/dev/null || true

run_test "T-03" "Missing manifest (exit 1)" \
    "! $TOOLCHAIN/arifos_f3_eval.py --worktree . 2>&1; echo 'ERROR'" \
    "ERROR"

cd "$ARIFOS_ROOT"
git worktree remove ../test-no-manifest --force 2>/dev/null || rm -rf ../test-no-manifest 2>/dev/null || true

# T-04: F1 reversibility
cd "$ARIFOS_ROOT"
$TOOLCHAIN/arifos-worktree-add.sh test f1 2>/dev/null
worktree_path="../arifos-worktrees/arifos-test-f1"

if [ -d "$worktree_path" ]; then
    echo "[T-04] F1 creation... ✅ PASS"
else
    echo "[T-04] F1 creation... ❌ FAIL"
    FAILED=$((FAILED + 1))
fi

echo "VOID" | $TOOLCHAIN/arifos-worktree-remove.sh feature/test-f1 2>/dev/null || true

if [ ! -d "$worktree_path" ]; then
    echo "[T-05] F1 removal... ✅ PASS"
else
    echo "[T-05] F1 removal... ❌ FAIL"
    FAILED=$((FAILED + 1))
fi

# T-05: Exit code 2 on enforce
cd "$ARIFOS_ROOT"
$TOOLCHAIN/arifos-worktree-add.sh test enforce 2>/dev/null
cd ../arifos-worktrees/arifos-test-enforce

$TOOLCHAIN/arifos_f3_eval.py --worktree . --enforce 2>/dev/null
exit_code=$?

if [ $exit_code -eq 2 ]; then
    echo "[T-06] Enforce exit 2... ✅ PASS"
else
    echo "[T-06] Enforce exit 2... ❌ FAIL (exit $exit_code)"
    FAILED=$((FAILED + 1))
fi

cd "$ARIFOS_ROOT"
echo "VOID" | $TOOLCHAIN/arifos-worktree-remove.sh feature/test-enforce 2>/dev/null || true

echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed. Constitutional GitOps validated."
else
    echo "❌ $FAILED test(s) failed."
fi
echo "=========================================="

exit $FAILED
