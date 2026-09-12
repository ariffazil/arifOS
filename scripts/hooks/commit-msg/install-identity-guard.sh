#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# install-identity-guard.sh — idempotent installer + verifier
# ═══════════════════════════════════════════════════════════════════════
# Why this exists: the commit-msg hook was written but NOT chmod +x, so git
# silently skipped it on every commit. A guard that is installed but not
# executable produces zero errors and protects nothing — the worst failure
# mode, because it looks like success.
#
# This installer sets the mode AND verifies the hook actually fires, so the
# gap cannot recur silently.
#
# Usage: bash /root/arifOS/scripts/hooks/commit-msg/install-identity-guard.sh
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

REPO="${1:-/root/arifOS}"
HOOK_DIR="$REPO/.git/hooks"
HOOK="$HOOK_DIR/commit-msg"
GUARD="$REPO/scripts/hooks/commit-msg/identity_guard.py"

fail() { echo "  FAIL: $1"; exit 1; }
ok()   { echo "  ok  : $1"; }

echo "═══════════════════════════════════════════════════════════"
echo " IDENTITY GUARD INSTALLER — repo: $REPO"
echo "═══════════════════════════════════════════════════════════"

[[ -d "$REPO/.git" ]] || fail "bukan git repo: $REPO"
[[ -f "$GUARD" ]]     || fail "guard script tiada: $GUARD"
chmod 755 "$GUARD"
ok "guard script executable (755)"

# core.hooksPath mesti tunjuk ke .git/hooks (arifOS dah set; pastikan)
HP="$(git -C "$REPO" config --get core.hooksPath || true)"
if [[ -n "$HP" && "$HP" != "$HOOK_DIR" ]]; then
  echo "  WARN: core.hooksPath = $HP (bukan $HOOK_DIR)"
  echo "        hook mesti dipasang ke \$core.hooksPath supaya git nampak dia"
  HOOK_DIR="$HP"
  HOOK="$HP/commit-msg"
fi
ok "hooks path = $HOOK_DIR"

# ── pasang hook ──────────────────────────────────────────────────────────
if [[ -f "$HOOK" ]]; then
  # jangan tindih hook sedia ada yang BUKAN wrapper kita
  if ! grep -q "IDENTITY GUARD wrapper" "$HOOK" 2>/dev/null; then
    BK="$HOOK.bak-$(date +%Y%m%dT%H%M%S)"
    cp -p "$HOOK" "$BK"
    echo "  WARN: $HOOK sedia ada dan bukan wrapper kami -> backup ke $BK"
    echo "        hook lama di-REPLACE. Jika ia gate penting, chain manual."
  fi
fi

cat > "$HOOK" <<'HOOKEOF'
#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# commit-msg hook — IDENTITY GUARD wrapper (thin, mirrors pre-push pattern)
# ═══════════════════════════════════════════════════════════════════════
# Forged 2026-09-13 after ffe6cbdd9 smuggled 9 lines of SOUL.md under an
# unrelated "fix(probe)" subject. Logic lives in the repo-tracked guard:
#   scripts/hooks/commit-msg/identity_guard.py
# so it is versioned, reviewable, and cannot be edited without a diff.
#
# Fail-open on missing guard (never wedge a repo's commits because a file
# moved) but prints a warning so the gap stays visible.
#
# MUST be mode 755. If it is not executable git skips it silently — that is
# the exact failure this installer was forged to prevent.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GUARD="$REPO_ROOT/scripts/hooks/commit-msg/identity_guard.py"

if [[ ! -f "$GUARD" ]]; then
  echo "[WARN] identity_guard.py missing at $GUARD; allowing commit." >&2
  exit 0
fi

python3 "$GUARD" "$@"
exit $?
HOOKEOF

chmod 755 "$HOOK"
[[ -x "$HOOK" ]] || fail "hook masih tak executable selepas chmod"
ok "hook dipasang + executable: $(stat -c '%a' "$HOOK")"

# ── VERIFIKASI: hook betul-betul fire? ────────────────────────────────────
echo ""
echo "── verify 1: guard selftest (BLOCK yang patut, ALLOW yang sah) ──"
SELFTEST="$(python3 "$GUARD" --selftest 2>&1)"
ST_RC=$?
echo "$SELFTEST"
if [[ $ST_RC -ne 0 ]]; then
  fail "selftest exit $ST_RC — guard tak melindungi apa-apa"
fi
# exit code alone is not enough: a crashed guard can exit 0 via a wrapper.
# Insist on positive evidence of a full pass, and reject any FAIL line.
if echo "$SELFTEST" | grep -q '\[FAIL\]'; then
  fail "selftest ada kes FAIL — guard cacat, jangan deploy"
fi
if ! echo "$SELFTEST" | grep -qE 'selftest result: ([1-9][0-9]*)/\1 passed'; then
  fail "selftest tak lapor full pass (jangka 'N/N passed')"
fi
if echo "$SELFTEST" | grep -qi 'guard error\|CRASHED\|Traceback'; then
  fail "selftest mengandungi ralat walaupun exit 0 — false PASS, tolak"
fi
ok "selftest PASS — disahkan oleh kandungan output, bukan exit code semata"

echo ""
echo "── verify 2: hook betul-betul dipanggil oleh git (bukan cuma wujud) ──"
PROBE_DIR="$(mktemp -d /tmp/idguard-fire-XXXXXX)"
(
  cd "$PROBE_DIR" || exit 1
  git init -q . >/dev/null 2>&1
  git config user.email probe@local >/dev/null 2>&1
  git config user.name probe >/dev/null 2>&1
  git config --local core.hooksPath .git/hooks >/dev/null 2>&1
  mkdir -p memory/identity .git/hooks scripts/hooks/commit-msg
  echo "# probe v1" > memory/identity/SOUL.md
  git add -A >/dev/null 2>&1 && git commit -q -m "probe init" >/dev/null 2>&1
  cp "$GUARD" scripts/hooks/commit-msg/identity_guard.py
  cp "$HOOK" .git/hooks/commit-msg && chmod 755 .git/hooks/commit-msg
  echo "smuggled" >> memory/identity/SOUL.md
  git add -A >/dev/null 2>&1
  git commit -q -m "fix(probe): unrelated subject" >/dev/null 2>&1
  echo "$?" > rc.txt
)
FIRE_RC="$(cat "$PROBE_DIR/rc.txt" 2>/dev/null || echo '?')"
rm -rf "$PROBE_DIR"
if [[ "$FIRE_RC" == "1" ]]; then
  ok "git SEBENAR memanggil hook dan guard BLOCK commit tak didedahkan (rc=1)"
else
  fail "hook tak fire melalui git (rc=$FIRE_RC) — guard dipasang tapi mati"
fi

# pastikan mode tak boleh senyap-senyap hilang: rekod dalam ledger
python3 - "$HOOK" "$GUARD" <<'PYEOF'
import sys, os, json, time
from pathlib import Path
d = Path("/root/.hermes/governance"); d.mkdir(parents=True, exist_ok=True)
rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": "GUARD_INSTALLED",
       "hook": sys.argv[1], "hook_mode": oct(os.stat(sys.argv[1]).st_mode)[-3:],
       "guard": sys.argv[2], "guard_mode": oct(os.stat(sys.argv[2]).st_mode)[-3:]}
(d / "identity-guard-audit.jsonl").open("a").write(json.dumps(rec) + "\n")
print("  ok  : install direkod dalam audit ledger")
PYEOF

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " IDENTITY GUARD: ARMED"
echo "═══════════════════════════════════════════════════════════"
exit 0
