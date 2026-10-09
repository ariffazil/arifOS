#!/usr/bin/env bash
# deploy-memory-mode-fix.sh — F13-gated deploy of the memory-mode truth fix (cb2411928)
# APEX-777 phase 3 · 333-AGI 2026-09-18
#
# Usage:  bash scripts/deploy-memory-mode-fix.sh --dry-run   # plan only (safe, default check)
#         bash scripts/deploy-memory-mode-fix.sh             # requires F13 approval
#
# Steps: verify repo marker -> refuse if already deployed -> backup live+app ->
#        sync repo tools.py -> py_compile -> restart -> health -> universe verify.
# Auto-rollback on compile failure or verify failure.
#
# NOT touched (deliberate): /opt/arifos/arifosmcp/runtime/tools.py is a skewed
# lineage (carries a "C1 FIX 2026-09-17" substrate variant) — reconcile
# separately, do NOT blind-sync. See PHASE3_DEPLOY_DECISION.md.
set -euo pipefail

REPO="/root/arifOS/arifosmcp/runtime/tools.py"
LIVE="/opt/arifos/current/venv/lib/python3.13/site-packages/arifosmcp/runtime/tools.py"
APP="/opt/arifos/app/arifosmcp/runtime/tools.py"
STAMP="bak-333-20260918-deploy"
MARKER="ARIF_MEMORY_MODES as _V5_MEMORY_MODES"
PY="/opt/arifos/current/venv/bin/python"

DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

echo "── memory-mode truth deploy ─────────────────────────────"
echo "repo : $REPO"
echo "live : $LIVE"
echo "app  : $APP"

grep -q "$MARKER" "$REPO" || {
	echo "ABORT: repo patch marker absent — nothing to deploy"
	exit 2
}
if grep -q "$MARKER" "$LIVE" 2>/dev/null; then
	echo "ALREADY DEPLOYED (live carries marker) — nothing to do"
	exit 0
fi

echo "PLAN:"
echo "  1. backup live+app   -> *.$STAMP"
echo "  2. copy repo tools.py -> live + app"
echo "  3. py_compile live"
echo "  4. systemctl restart arifos.service"
echo "  5. verify health + dispatch universe (13 modes incl audit)"
echo "WARN: /opt/arifos/arifosmcp (skewed lineage) deliberately NOT synced."

if [ "$DRY" -eq 1 ]; then
	echo "DRY-RUN — no changes made."
	exit 0
fi

cp -p "$LIVE" "$LIVE.$STAMP"
cp -p "$APP" "$APP.$STAMP"
cp "$REPO" "$LIVE"
cp "$REPO" "$APP"

if ! "$PY" -m py_compile "$LIVE"; then
	echo "COMPILE FAIL — restoring live from backup"
	cp -p "$LIVE.$STAMP" "$LIVE"
	exit 3
fi

systemctl restart arifos.service
for _i in $(seq 1 15); do
	sleep 2
	curl -sf -m 3 http://127.0.0.1:8088/health >/dev/null 2>&1 && break
done
if ! curl -sf -m 5 http://127.0.0.1:8088/health >/dev/null; then
	echo "HEALTH FAIL — rollback: cp $LIVE.$STAMP $LIVE && systemctl restart arifos.service"
	exit 4
fi

cd /var/lib/arifos # neutral cwd so the import resolves the LIVE site-packages copy
set +e
"$PY" - <<'PYEOF'
from arifosmcp.runtime.tools import _arif_memory_v5_router as R

u = getattr(R, "__dispatch_modes__", None)
ok = bool(u) and "audit" in u and len(u) == 13
print(f"dispatch universe: {len(u) if u else None} modes | audit: {bool(u and 'audit' in u)} | OK={ok}")
raise SystemExit(0 if ok else 1)
PYEOF
VERIFY_RC=$?
set -e

if [ "$VERIFY_RC" -ne 0 ]; then
	echo "VERIFY FAIL (rc=$VERIFY_RC) — rolling back"
	cp -p "$LIVE.$STAMP" "$LIVE"
	cp -p "$APP.$STAMP" "$APP"
	systemctl restart arifos.service
	exit 5
fi

echo "✅ DEPLOYED + VERIFIED"
echo "rollback: cp $LIVE.$STAMP $LIVE && cp $APP.$STAMP $APP && systemctl restart arifos.service"
echo "next: $PY /root/AAA/scripts/capability_truth.py   # live enum re-measure"
