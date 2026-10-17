#!/usr/bin/env bash
# ARIFOS::BASELINE_UNIT_TESTS::v1 — secret scan
# Scans harness directory for leaked credentials / private keys.
set -uo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HARNESS_DIR" || exit

echo "=== Secret scan of harness directory ==="
# High-signal patterns for leaked secrets (value-side, not name-side)
PATTERNS=(
	'sk-[A-Za-z0-9]{16,}'
	'glm_[A-Za-z0-9_-]{20,}'
	'AKIA[0-9A-Z]{16}'
	'-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----'
	'ghp_[A-Za-z0-9]{36}'
	'xox[baprs]-[A-Za-z0-9-]{10,}'
	'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}' # JWT
)

FOUND=0
for p in "${PATTERNS[@]}"; do
	hits=$(grep -rInE "$p" . 2>/dev/null | grep -v 'Binary file' | grep -vE '\.pyc$')
	if [ -n "$hits" ]; then
		echo "[HIT] pattern=$p"
		echo "$hits" | sed -E 's/(.{0,60})('"$p"').*/\1\2<REDACTED>/'
		FOUND=1
	fi
done

if [ "$FOUND" -eq 0 ]; then
	echo "CLEAN — no secret-pattern hits in harness directory."
	exit 0
else
	echo "SECRETS DETECTED — do NOT bundle until resolved."
	exit 1
fi
