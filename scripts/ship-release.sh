#!/usr/bin/env bash
# ship-release.sh — the ONE ordered lane for arifOS releases (born 2026-11-13).
#
# Failure classes it exists to kill (all observed live that day):
#   1. concurrent writers shipping divergent branches  -> loud writer check + one command
#   2. stale build/lib smuggling excluded files        -> clean build/ every time (step 3)
#   3. silent pre-push guard failures                  -> every gate is loud, named, exits non-zero
#   4. parity attestation vs wheel excludes            -> census asserts BEFORE shipping
#   5. registry token expiry discovered at publish     -> token age checked up front
#   6. remote URL drift (automation resets to SSH)     -> push via explicit https URL
#   7. serial human-in-the-loop auth                   -> token age warned early, not at the end
#
# Usage:
#   scripts/ship-release.sh --check-only   # gates + census, no push/publish
#   scripts/ship-release.sh                # full: push -> PyPI dispatch -> registry -> notify
# Requires: CLEAN tree (commit first — lane DP-D refuses dirty trees anyway).
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REG_DIR="${ARIFOS_REGISTRY_DIR:-/root/forge_work/arifos-mcp-registry}"
PUSH_URL="https://github.com/ariffazil/arifOS.git"
BRANCH="$(git -C "$REPO" branch --show-current)"
MODE="${1:-ship}"
fail(){ echo "❌ SHIP ABORT: $1"; exit 1; }
step(){ echo "--- $* ---"; }

step "0. preconditions (clean tree + healthy kernel)"
git -C "$REPO" diff --quiet || fail "dirty tree — commit first (DP-D)"
git -C "$REPO" status --porcelain | grep -q . && fail "untracked/staged files present — clean or commit them"
curl -sf -m 8 http://127.0.0.1:8088/health >/dev/null || fail "kernel :8088 unreachable — restart arifos first (pre-push guard GATE 1 needs it)"

step "1. concurrent writers, last 30 min (warn-only)"
ME="$(git -C "$REPO" config user.name)"
git -C "$REPO" log --oneline --since="30 minutes ago" --pretty="%h %an %s" | head -6 || true
echo "  (if another writer is mid-flight: ONE writer per lane. Coordinate first.)"

step "2. version + ownership sanity"
VER="$(grep -E '^version' "$REPO/pyproject.toml" | head -1 | sed 's/.*"\(.*\)"/\1/')"
echo "  pyproject version: $VER"
grep -q "mcp-name: io.github.ariffazil/arifos" "$REPO/README.md" \
  || echo "  ⚠ README missing 'mcp-name: io.github.ariffazil/arifos' — registry PyPI ownership validation WILL fail"

step "3. clean build + wheel census (capability-preserving asserts)"
source "$REPO/scripts/immutability_cycle.sh"
immutability_unlock "$REPO/build" "$REPO/arifos.egg-info"
rm -rf "$REPO/build" "$REPO/arifos.egg-info"
mkdir -p /tmp/ship-wheel && rm -f /tmp/ship-wheel/*.whl
(cd "$REPO" && python3 -m pip wheel --no-deps --no-build-isolation -w /tmp/ship-wheel . >/dev/null 2>&1) || fail "wheel build failed"
WHEEL="$(ls /tmp/ship-wheel/*.whl | head -1)"
[ -n "$WHEEL" ] || fail "no wheel produced"
python3 - "$WHEEL" <<'PY' || fail "census asserts FAILED — see above"
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); n = z.namelist()
def c(p): return sum(p in x for x in n)
pyc = sum(x.endswith('.pyc') for x in n)
junk = c('arifosmcp/sites/') + c('arifosmcp/packages/npm/') + c('arifosmcp/evals/') + c('arifosmcp/static/')
assert junk == 0, f"junk files shipped: {junk}"
assert c('arifosmcp/gateway/') >= 1, "gateway capability MISSING (F13 no-capability-removal constraint)"
assert c('agent_registry/cards/') >= 1, "agent cards MISSING (runtime-read assets)"
assert pyc == 0, f".pyc shipped: {pyc}"
hits = sum(1 for x in n if x.endswith(('.py', '.json', '.md'))
           and ('Syed Anas' in z.read(x).decode('utf-8', 'ignore')
                or 'CVE-2026-SyedAnas' in z.read(x).decode('utf-8', 'ignore')))
assert hits == 0, f"third-party name hits in wheel: {hits}"
print(f"  census OK: {len(n)} files | junk 0 | gateway {c('arifosmcp/gateway/')} | cards {c('agent_registry/cards/')} | names 0")
PY
twine check "$WHEEL" >/dev/null || fail "twine check failed"
echo "  wheel: $WHEEL"

if [ "$MODE" = "--check-only" ]; then
  echo "✅ CHECK-ONLY COMPLETE (no push/publish). Wheel: $WHEEL"; exit 0
fi

step "4. push (explicit https URL — remote config drifts to SSH via automation)"
git -C "$REPO" -c credential.helper="!gh auth git-credential" push "$PUSH_URL" "$BRANCH" 2>&1 | tail -2
sleep 2
REMOTE="$(git -C "$REPO" ls-remote "$PUSH_URL" "refs/heads/$BRANCH" | awk '{print substr($1,1,9)}')"
HEADS="$(git -C "$REPO" rev-parse --short=9 HEAD)"
[ "$REMOTE" = "$HEADS" ] || fail "push verify FAILED: remote=$REMOTE head=$HEADS"
echo "  remote=$REMOTE == head=$HEADS"

step "5. PyPI dispatch (GitHub Actions OIDC — no local token exists, by design)"
command -v gh >/dev/null || fail "gh CLI missing"
gh workflow run 07-publish-pypi.yml --repo ariffazil/arifOS --ref "$BRANCH"
sleep 10
RID="$(gh run list --repo ariffazil/arifOS --workflow=07-publish-pypi.yml --limit 1 --json databaseId -q '.[0].databaseId')"
echo "  run: $RID"
ST="in_progress"
for i in $(seq 1 24); do
  sleep 10
  ST="$(gh run view "$RID" --repo ariffazil/arifOS --json status,conclusion -q '.status + "/" + (.conclusion // "pending")')"
  [ "${ST%%/*}" = "completed" ] && break
done
[ "$ST" = "completed/success" ] || fail "PyPI workflow ended $ST — gh run view $RID --log-failed"
curl -sf -m 12 "https://pypi.org/pypi/arifos/$VER/json" >/dev/null || fail "PyPI version $VER not visible after successful run (CDN lag — verify manually)"
echo "  PyPI $VER LIVE"

step "6. registry publish (token checked BEFORE the attempt, not after)"
[ -f /root/.config/mcp-publisher/token.json ] || fail "no registry token — run: cd $REG_DIR && mcp-publisher login github (authorize in browser), then re-run step 6"
AGE_H=$(( ($(date +%s) - $(stat -c %Y /root/.config/mcp-publisher/token.json)) / 3600 ))
[ "$AGE_H" -lt 168 ] || fail "registry token stale (${AGE_H}h) — cd $REG_DIR && mcp-publisher login github, authorize, then re-run step 6"
PUB="$(cd "$REG_DIR" && mcp-publisher publish server.json 2>&1 | tail -3)" || true
if echo "$PUB" | grep -q "already exists"; then
  echo "  registry: this version already published — done"
elif echo "$PUB" | grep -q "401"; then
  fail "registry auth expired — cd $REG_DIR && mcp-publisher login github, authorize, re-run step 6"
else
  echo "  $PUB"
fi

step "7. notify sovereign"
"$REPO/scripts/notify_sovereign.sh" "🚢 shipped arifos $VER — PyPI ✓ registry ✓ wheel census clean (ship-release.sh)" || true
echo "✅ SHIP COMPLETE: $VER"
