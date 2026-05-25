#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Smoke check: arifos service user can write to XDG_DATA_HOME
# Regression test for 000_FIX (SAFE_VOID /home/arifos/.local/share)
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

USER="arifos"
XDG_DATA_HOME="/home/arifos/.local/share"
SMOKE_DIR="${XDG_DATA_HOME}/.smoke-check.$$"

ERRORS=0

# 1. Home directory ownership
echo -n "[1/4] Home dir owned by ${USER}... "
OWNER=$(stat -c '%U:%G' /home/arifos)
if [ "$OWNER" = "${USER}:${USER}" ]; then
    echo "PASS ($OWNER)"
else
    echo "FAIL ($OWNER)"
    ERRORS=$((ERRORS + 1))
fi

# 2. XDG_DATA_HOME exists
echo -n "[2/4] XDG_DATA_HOME exists (${XDG_DATA_HOME})... "
if [ -d "$XDG_DATA_HOME" ]; then
    echo "PASS"
else
    echo "FAIL (missing)"
    ERRORS=$((ERRORS + 1))
fi

# 3. Service user can write
echo -n "[3/4] Service user can write to XDG_DATA_HOME... "
if su -s /bin/bash "$USER" -c "mkdir -p '${SMOKE_DIR}' && echo ok > '${SMOKE_DIR}/test.txt' && cat '${SMOKE_DIR}/test.txt'" >/dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    ERRORS=$((ERRORS + 1))
fi

# 4. Cleanup
echo -n "[4/4] Cleanup smoke dir... "
rm -rf "$SMOKE_DIR"
echo "PASS"

if [ $ERRORS -eq 0 ]; then
    echo "=== ALL CHECKS PASS ==="
    exit 0
else
    echo "=== $ERRORS CHECK(S) FAILED ==="
    echo "Fix: chown ${USER}:${USER} /home/arifos && mkdir -p ${XDG_DATA_HOME} && chown -R ${USER}:${USER} /home/arifos/.local"
    exit 1
fi
