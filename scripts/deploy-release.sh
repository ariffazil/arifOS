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
# ONE_ORIGIN (2026-09-16): the production venv lives at
# /opt/arifos/current/venv — the ONLY legal runtime origin. Legacy
# /opt/arifos/venv is a compat symlink for sibling services.
ACTIVE_VENV="/opt/arifos/current/venv"
VENV_PYTHON="$ACTIVE_VENV/bin/python"
VENV_PIP="$ACTIVE_VENV/bin/pip"
SERVICE_NAME="arifos.service"
RELEASE_DIR="/opt/arifos/releases"
STAMP_FILE="$RELEASE_DIR/deployed-commit"
BUILD_DIR="/tmp/arifos-build-$$"

# Real site-packages ROOT (sysconfig), not the arifosmcp package dir —
# the 2026-09-16 audit found the old cleanup computed the package dir,
# so editable/.pth removal had been a silent no-op for weeks.
SITE_PKG_ROOT="$(cd / && "$VENV_PYTHON" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null || echo "$ACTIVE_VENV/lib/python3.13/site-packages")"

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
# 2026-09-16: stale build/lib + egg-info poison every wheel — scripts/
# shipped for months because a cached copy lived in build/lib even after
# pyproject include-list hygiene. Clean before every build.
rm -rf build arifos.egg-info
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

# ── Step 3: Install wheel into the active release venv ───────────────
echo "--- Step 3: Install wheel into $ACTIVE_VENV ---"
mkdir -p "$RELEASE_DIR"
cp "$WHEEL_FILE" "$RELEASE_DIR/"

# ONE_ORIGIN seed (first run only): build the active venv from the legacy
# venv's dependencies — WITHOUT the arifos lineage, stale dist-infos
# (1!2026.8.2 / 1!2026.9.2), or editable finder artifacts. Fresh venv has
# correct shebangs; deps arrive by copy so no network resolution.
if [ ! -x "$VENV_PYTHON" ]; then
	echo "  Seeding $ACTIVE_VENV from legacy /opt/arifos/venv ..."
	LEGACY_SP="$(ls -d /opt/arifos/venv/lib/python*/site-packages 2>/dev/null | head -1 || true)"
	python3 -m venv "$ACTIVE_VENV"
	if [ -n "$LEGACY_SP" ]; then
		NEW_SP="$ACTIVE_VENV/lib/$(basename "$(dirname "$LEGACY_SP")")/site-packages"
		rsync -a \
			--exclude 'arifosmcp/' \
			--exclude 'core/' \
			--exclude 'arifos/' \
			--exclude 'arifos-*.dist-info/' \
			--exclude '__editable__*' \
			--exclude '~*' \
			"$LEGACY_SP/" "$NEW_SP/"
	fi
	echo "  ✅ Active venv seeded"
fi

SITE_PKG_ROOT="$(cd / && "$VENV_PYTHON" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"

# Purge every arifos lineage artifact at site-packages ROOT (the old
# script computed the arifosmcp package dir — cleanup was a no-op).
"$VENV_PIP" uninstall -y arifos arifosmcp 2>/dev/null || true
rm -rf "$SITE_PKG_ROOT/arifosmcp" "$SITE_PKG_ROOT/core" "$SITE_PKG_ROOT/arifos"
rm -rf "$SITE_PKG_ROOT"/arifos-*.dist-info "$SITE_PKG_ROOT"/arifosmcp-*.dist-info
rm -f "$SITE_PKG_ROOT/arifos-core.pth" "$SITE_PKG_ROOT"/__editable__.arifos-*.pth \
	"$SITE_PKG_ROOT"/__editable___arifos_*.py

# Install fresh wheel — the ONLY arifos distribution in the active venv
"$VENV_PIP" install --no-deps "$WHEEL_FILE" 2>&1

# Axis C gate: exactly one arifos distribution, zero editable installs
# (|| true: empty glob is a PASS condition, not an ls error)
ARIFOS_DIST_COUNT=$( { ls -d "$SITE_PKG_ROOT"/arifos-*.dist-info 2>/dev/null || true; } | wc -l)
EDITABLE_COUNT=$( { ls "$SITE_PKG_ROOT"/__editable__.arifos-* 2>/dev/null || true; } | wc -l)
if [ "$ARIFOS_DIST_COUNT" -ne 1 ] || [ "$EDITABLE_COUNT" -ne 0 ]; then
	echo "❌ ONE-ORIGIN GATE: dist_count=$ARIFOS_DIST_COUNT editable=$EDITABLE_COUNT"
	rm -rf "$BUILD_DIR"
	exit 1
fi
echo "  ✅ Wheel installed (single distribution, zero editables)"

# Host identity config: /etc/arifos/identity.toml (root:root 0644)
install -d -m 0755 -o root -g root /etc/arifos
install -m 0644 -o root -g root "$REPO_DIR/identity.toml" /etc/arifos/identity.toml
echo "  ✅ identity.toml → /etc/arifos/identity.toml"
echo ""

# Wheel content gate: exactly three legal roots, nothing else ships.
WHEEL_ROOTS=$(unzip -l "$RELEASE_DIR/$WHEEL_NAME" 2>/dev/null | awk '{print $4}' \
	| grep -v '^$' | grep -v 'dist-info' | cut -d/ -f1 | sort -u | tr '\n' ' ')
case "$WHEEL_ROOTS" in
	*"scripts"*|*"tests"*|*"archive"*|*"mcp_server"*)
		echo "❌ WHEEL GATE: illegal package root shipped: $WHEEL_ROOTS"
		rm -rf "$BUILD_DIR"
		exit 1
		;;
esac
echo "  ✅ Wheel roots: $WHEEL_ROOTS"

# ── Step 4: Verify import path (ONE_ORIGIN axis A) ───────────────────
echo "--- Step 4: Verify import origin ---"
IMPORT_PATH=$(cd / && "$VENV_PYTHON" -c "
import arifosmcp
from pathlib import Path
print(Path(arifosmcp.__file__).resolve())
" 2>/dev/null || echo "ERROR")

echo "  Import origin: $IMPORT_PATH"

# Axis A: origin must be inside the ACTIVE release venv — nothing else
# (no app tree, no global, no editable) may serve the kernel.
if echo "$IMPORT_PATH" | grep -q "^$ACTIVE_VENV"; then
	echo "  ✅ Runtime origin is the active release venv"
else
	echo "  ❌ ONE-ORIGIN GATE: import origin outside $ACTIVE_VENV"
	echo "     Origin: $IMPORT_PATH"
	rm -rf "$BUILD_DIR"
	exit 1
fi
echo ""

# ── Step 5-pre: Deploy canon package to /etc/arifos/canon ────────────
echo "--- Step 5-pre: Deploy canon package to /etc/arifos/canon ---"
# FHS formalization (2026-09-16): ratified authority lives at /etc — a
# DIFFERENT change cadence from code releases. Canon files are root-owned,
# 0644; the service reads but can never write them (drop-in 02-fhs-canon).
# Generated projections (tools_sot.yaml, capability_registry.json) are NOT
# canon — they stay code-shipped; hashes ride the release manifest only.
CANON_DIR_FHS="/etc/arifos/canon"
install -d -m 0755 -o root -g root "$CANON_DIR_FHS/charter"
install -m 0644 -o root -g root "$REPO_DIR/config/sovereignty.charter.json" \
    "$CANON_DIR_FHS/sovereignty.charter.json"
install -m 0644 -o root -g root "$REPO_DIR/config/charter/kernel.charter.yaml" \
    "$CANON_DIR_FHS/charter/kernel.charter.yaml"
install -m 0644 -o root -g root "$REPO_DIR/config/memory-admissibility-policy.yaml" \
    "$CANON_DIR_FHS/memory-admissibility-policy.yaml"
CANON_VERSION="$(date -u +%Y.%m.%d)-${GIT_COMMIT}"
CANON_MANIFEST_SHA=$("$VENV_PYTHON" - "$CANON_DIR_FHS" "$CANON_VERSION" "$GIT_COMMIT" <<'PYEOF'
import hashlib, json, sys
from pathlib import Path

canon_dir, version, commit = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
names = [
    "sovereignty.charter.json",
    "charter/kernel.charter.yaml",
    "memory-admissibility-policy.yaml",
]
files = []
for name in names:
    p = canon_dir / name
    if p.is_file():
        files.append({"name": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    else:
        sys.exit(f"canon file missing after install: {p}")
manifest = {
    "canon_version": version,
    "ratified_by": "F13",
    "source_commit": commit,
    "files": files,
}
raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
(canon_dir / "canon-release.json").write_text(raw + "\n", encoding="utf-8")
print("sha256:" + hashlib.sha256(raw.encode()).hexdigest())
PYEOF
) || {
	echo "ERROR: canon package generation failed"
	rm -rf "$BUILD_DIR"
	exit 1
}
echo "  ✅ Canon deployed: $CANON_VERSION (manifest $CANON_MANIFEST_SHA)"
echo ""

# ── Step 5: Write release manifest ───────────────────────────────────
echo "--- Step 5: Write release manifest ---"
MANIFEST_FILE="$RELEASE_DIR/release-manifest.json"
cat >"$MANIFEST_FILE" <<MANIFEST_EOF
{
  "release": 1,
  "name": "Runtime Truth",
  "git_commit": "$GIT_COMMIT",
  "build_timestamp": "$BUILD_TS",
  "wheel_name": "$WHEEL_NAME",
  "wheel_sha256": "$WHEEL_HASH",
  "canon_version": "$CANON_VERSION",
  "canon_manifest_sha256": "$CANON_MANIFEST_SHA",
  "imported_from": "$IMPORT_PATH",
  "venv_python": "$VENV_PYTHON"
}
MANIFEST_EOF

# Deployment stamp: ONE stable path (build.py + reconciler read this).
# No legacy /opt/arifos/app stamp — that tree is retired by ONE_ORIGIN.
echo "$GIT_COMMIT" >"$STAMP_FILE"

echo "  Manifest: $MANIFEST_FILE"
echo "  Deployment stamp: $STAMP_FILE = $GIT_COMMIT"
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

# ═══════════════════════════════════════════════════════════════════════════════
# CANON GATE: tools/list == capability_registry.json (surface consistency)
# Fail the build if tools don't match — don't let a 9th tool ship again.
# ═══════════════════════════════════════════════════════════════════════════════
echo "--- Step 5.5: Canon gate (surface consistency) ---"
CANON_RESULT=$("$VENV_PYTHON" -c "
import json, sys
from arifosmcp.abi.kernel_abi import tool_names_for_profile, profile_contract

profile = 'public_agent'
abi_tools = set(tool_names_for_profile(profile))
print(f'ABI profile tools ({len(abi_tools)}): {sorted(abi_tools)}')

# Also check capability_registry
with open('$REPO_DIR/arifosmcp/abi/capability_registry.json') as f:
    cr = json.load(f)
cr_ids = set(c['capability_id'] for c in cr['capabilities'])
print(f'Capability registry ({len(cr_ids)}): {sorted(cr_ids)}')

# Check policy_registry for public_agent
with open('$REPO_DIR/arifosmcp/abi/policy_registry.json') as f:
    pr = json.load(f)
pa_caps = set(pr['profiles']['public_agent']['capabilities'])
print(f'Policy public_agent ({len(pa_caps)}): {sorted(pa_caps)}')

# All three must be consistent.
# Fixed 2026-09-15 (333-AGI): the gate compared raw ABI TOOL names against
# policy CAPABILITY ids — different namespaces, so it could never pass.
# Correct invariant: policy caps, mapped through capability_registry to
# provider tool names, must equal the ABI profile's tool names, and every
# policy cap must exist in the capability registry.
by_id = {c['capability_id']: c for c in cr['capabilities']}
unknown_caps = pa_caps - set(by_id)
pa_tools = set(by_id[c]['provider']['tool'] for c in pa_caps if c in by_id)

if unknown_caps:
    print(f'MISMATCH: policy caps missing from capability registry: {sorted(unknown_caps)}')
    sys.exit(1)
if abi_tools != pa_tools:
    print(f'MISMATCH: ABI tools != policy caps mapped to tools')
    print(f'  ABI - Policy(tools): {abi_tools - pa_tools}')
    print(f'  Policy(tools) - ABI: {pa_tools - abi_tools}')
    sys.exit(1)

print('✅ Canon gate: ABI, capability, and policy registries consistent')
" 2>&1) || {
	echo "ERROR: Canon gate failed — surface inconsistency detected"
	echo "$CANON_RESULT"
	echo "Aborting deploy. Fix the ABI registries before deploying."
	rm -rf "$BUILD_DIR"
	exit 1
}
echo "$CANON_RESULT"
echo ""
