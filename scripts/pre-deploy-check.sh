#!/bin/bash
# pre-deploy-check.sh — validates deploy refs against stack.manifest.json
# DITEMPA BUKAN DIBERI
set -euo pipefail

MANIFEST="${MANIFEST:-deploy/stack.manifest.json}"
ARIFOS_DIR="${ARIFOS_DIR:-/root/arifos}"
GEOX_DIR="${GEOX_DIR:-/srv/siblings/GEOX-repo}"

# ── manifest presence ─────────────────────────────────────────
if [ ! -f "$MANIFEST" ]; then
  echo "ERROR: $MANIFEST not found. HOLD deploy." >&2
  exit 1
fi

if [ ! -f "${MANIFEST}" ]; then
  echo "ERROR: manifest not found at $MANIFEST" >&2
  exit 1
fi

# ── parse refs ────────────────────────────────────────────────
ARIFOS_REF="$(python3 -c "import json,sys; d=json.load(open('$MANIFEST')); print(d.get('arifos',{}).get('ref','NONE'))")"
GEOX_REF="$(python3 -c "import json,sys; d=json.load(open('$MANIFEST')); print(d.get('geox',{}).get('ref','NONE'))")"

if [ "$ARIFOS_REF" = "NONE" ] || [ -z "$ARIFOS_REF" ]; then
  echo "ERROR: arifos.ref not found in manifest" >&2
  exit 1
fi

# ── current HEAD SHAs ─────────────────────────────────────────
ARIFOS_CURRENT="$(git -C "$ARIFOS_DIR" rev-parse HEAD 2>/dev/null)"
GEOX_CURRENT="$(git -C "$GEOX_DIR" rev-parse HEAD 2>/dev/null)"

echo "--- pre-deploy check ---"
echo "arifOS manifest: $ARIFOS_REF"
echo "arifOS current:  $ARIFOS_CURRENT"
echo "GEOX manifest:   $GEOX_REF"
echo "GEOX current:    $GEOX_CURRENT"

# ── assert match ───────────────────────────────────────────────
ARIFOS_MISMATCH=0
GEOX_MISMATCH=0

if [ "$ARIFOS_CURRENT" != "$ARIFOS_REF" ]; then
  echo "WARNING: arifOS HEAD ($ARIFOS_CURRENT) != manifest ($ARIFOS_REF)" >&2
  ARIFOS_MISMATCH=1
fi

if [ "$GEOX_CURRENT" != "$GEOX_REF" ]; then
  echo "WARNING: GEOX HEAD ($GEOX_CURRENT) != manifest ($GEOX_REF)" >&2
  GEOX_MISMATCH=1
fi

if [ $ARIFOS_MISMATCH -eq 1 ] || [ $GEOX_MISMATCH -eq 1 ]; then
  echo "ERROR: manifest mismatch — update manifest or pull correct refs" >&2
  exit 1
fi

echo "PASS: deploy refs match manifest"
exit 0
