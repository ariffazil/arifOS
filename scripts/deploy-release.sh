#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# deploy-release.sh — arifOS Release 1: Runtime Truth
# ═══════════════════════════════════════════════════════════════════════════════
#
# 1. Build immutable wheel from source
# 2. Install into /opt/arifos/venv (production venv only)
# 3. Remove stale global install from /usr/local/lib/.../dist-packages/
# 4. Verify import path resolves to venv, not global
# 5. Write release manifest for boot attestation
# 6. Restart arifOS service
# 7. Verify health with runtime alignment check
#
# DITEMPA BUKAN DIBERI — Truth is forged, not assumed.

set -euo pipefail

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SELF_DIR/.." && pwd)"
VENV_PYTHON="/opt/arifos/venv/bin/python"
VENV_PIP="/opt/arifos/venv/bin/pip"
VENV_SITE_PKG="$(cd / && "$VENV_PYTHON" -c 'from pathlib import Path; import arifosmcp; print(str(Path(arifosmcp.__file__).parent))' 2>/dev/null || echo "/opt/arifos/venv/lib/python3.12/site-packages/arifosmcp")"
SERVICE_NAME="arifos.service"
RELEASE_DIR="/opt/arifos/releases"
BUILD_DIR="/tmp/arifos-build-$$"

GIT_COMMIT="$(cd "$REPO_DIR" && git rev-parse --short=7 HEAD 2>/dev/null || echo "unknown")"
BUILD_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "═══ arifOS Release 1 — Runtime Truth ═══"
echo "  Source:     $REPO_DIR"
echo "  Commit:     $GIT_COMMIT"
echo "  Build time: $BUILD_TS"
echo ""

# ── Step 1: Build wheel ──────────────────────────────────────────────
echo "--- Step 1: Build immutable wheel ---"
cd "$REPO_DIR"
python -m build --wheel --outdir "$BUILD_DIR" 2>&1 || {
    echo "ERROR: build failed"
    rm -rf "$BUILD_DIR"
    exit 1
}

WHEEL_FILE="$(ls "$BUILD_DIR"/*.whl 2>/dev/null | head -1)"
if [ -z "$WHEEL_FILE" ]; then
    echo "ERROR: no wheel produced"
    rm -rf "$BUILD_DIR"
    exit 1
fi
WHEEL_HASH="$(sha256sum "$WHEEL_FILE" | cut -d' ' -f1)"
WHEEL_NAME="$(basename "$WHEEL_FILE")"
echo "  Wheel:  $WHEEL_NAME"
echo "  SHA256: $WHEEL_HASH"
echo ""

# ── Step 2: Remove stale global install ──────────────────────────────
echo "--- Step 2: Remove stale global install ---"
# Remove from global site-packages (python3.13 dist-packages)
GLOBAL_SITE_PKG="$(python3 -c 'import site; print([p for p in site.getsitepackages() if "dist-packages" in p][0])' 2>/dev/null || echo "")"
if [ -n "$GLOBAL_SITE_PKG" ] && [ -d "$GLOBAL_SITE_PKG/arifosmcp" ]; then
    echo "  Removing: $GLOBAL_SITE_PKG/arifosmcp"
    rm -rf "$GLOBAL_SITE_PKG/arifosmcp"
    rm -f "$GLOBAL_SITE_PKG/arifos-"*.dist-info 2>/dev/null || true
    echo "  ✅ Global install removed"
else
    echo "  No global install found"
fi
echo ""

# ── Step 3: Install wheel into production venv ────────────────────────
echo "--- Step 3: Install wheel into /opt/arifos/venv ---"
mkdir -p "$RELEASE_DIR"
cp "$WHEEL_FILE" "$RELEASE_DIR/"

# Uninstall old version first if present
"$VENV_PIP" uninstall -y arifos 2>/dev/null || true

# Remove any editable install artifacts from the venv (PEP 660 .pth files)
# These redirect imports to /root/arifOS source, defeating the wheel install
rm -f "$VENV_SITE_PKG/arifos-core.pth" 2>/dev/null || true
rm -f "$VENV_SITE_PKG/__editable__.arifos-"*.pth 2>/dev/null || true
rm -f "$VENV_SITE_PKG/__editable___arifos_"*.py 2>/dev/null || true

# Install fresh wheel (force to override any editable residue)
"$VENV_PIP" install --force-reinstall --no-deps "$WHEEL_FILE" 2>&1

echo "  ✅ Wheel installed (editable artifacts removed)"
echo ""

# ── Step 4: Verify import path ───────────────────────────────────────
echo "--- Step 4: Verify import path resolution ---"
IMPORT_PATH=$(cd / && "$VENV_PYTHON" -c "
import arifosmcp.runtime.build as b
from pathlib import Path
print(Path(b.__file__).resolve())
" 2>/dev/null || echo "ERROR")

echo "  Import path: $IMPORT_PATH"

# Path must be inside /opt/arifos/venv, NOT global
if echo "$IMPORT_PATH" | grep -q "/opt/arifos/venv"; then
    echo "  ✅ Import path is inside production venv"
else
    echo "  ❌ Import path is NOT inside production venv"
    echo "     Run: $VENV_PYTHON -c \"import arifosmcp; print(arifosmcp.__file__)\""
    rm -rf "$BUILD_DIR"
    exit 1
fi
echo ""

# ── Step 5: Write release manifest ───────────────────────────────────
echo "--- Step 5: Write release manifest ---"
MANIFEST_FILE="$RELEASE_DIR/release-manifest.json"
cat > "$MANIFEST_FILE" <<MANIFEST_EOF
{
  "release": 1,
  "name": "Runtime Truth",
  "git_commit": "$GIT_COMMIT",
  "build_timestamp": "$BUILD_TS",
  "wheel_name": "$WHEEL_NAME",
  "wheel_sha256": "$WHEEL_HASH",
  "imported_from": "$IMPORT_PATH",
  "venv_python": "$VENV_PYTHON"
}
MANIFEST_EOF

# Also write to deployment stamp
echo "$GIT_COMMIT" > /opt/arifos/app/.git_commit

echo "  Manifest: $MANIFEST_FILE"
echo "  Deployment stamp: /opt/arifos/app/.git_commit = $GIT_COMMIT"
echo ""

# ── Step 6: Restart service ──────────────────────────────────────────
echo "--- Step 6: Restart arifOS service ---"
systemctl daemon-reload 2>/dev/null || true
systemctl restart "$SERVICE_NAME" 2>&1 || {
    echo "WARNING: restart failed, attempting manually"
    pkill -f "arifosmcp.runtime" 2>/dev/null || true
}

echo "  Waiting for service to become healthy..."
for i in $(seq 1 30); do
    STATUS=$(curl -s -m 2 http://localhost:8088/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")
    if [ "$STATUS" = "healthy" ]; then
        echo "  ✅ Kernel healthy after ${i}s"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "  ❌ Kernel did not become healthy"
        systemctl status "$SERVICE_NAME" --no-pager 2>&1 | tail -20
        rm -rf "$BUILD_DIR"
        exit 1
    fi
    sleep 2
done
echo ""

# ── Step 7: Verify runtime alignment ─────────────────────────────────
echo "--- Step 7: Verify runtime alignment ---"
ALIGNMENT=$(cd / && "$VENV_PYTHON" -c "
from arifosmcp.runtime.build import _git_sha_short
s = _git_sha_short()
print(f'running_commit={s}')
" 2>/dev/null || echo "running_commit=unknown")

RUNTIME_COMMIT=$(echo "$ALIGNMENT" | grep "running_commit" | cut -d= -f2)
echo "  Expected commit: $GIT_COMMIT"
echo "  Runtime commit:  $RUNTIME_COMMIT"

if [ "$RUNTIME_COMMIT" = "$GIT_COMMIT" ]; then
    echo "  ✅ Runtime aligned with source"
else
    echo "  ⚠️  Runtime commit differs — deploy stamp may need update"
fi
echo ""

# ── Cleanup ──────────────────────────────────────────────────────────
rm -rf "$BUILD_DIR"
echo "═══ Release 1 deploy complete ═══"
echo "  Commit: $GIT_COMMIT"
echo "  Wheel:  $WHEEL_NAME"
echo "  Hash:   $WHEEL_HASH"
echo "  DITEMPA BUKAN DIBERI"
