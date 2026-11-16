#!/usr/bin/env bash
# witness.sh — one-command external reproduction kit for arifOS.
#
# Design rule: this script is allowed to say NOT READY. It is never allowed to say
# PASS when the suite is absent, skipped, or erroring. A witness who is told "pass"
# by a missing test has been deceived by the tool, not by the author.
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${REPO_DIR}/witness-result.json"
IMAGE="python:3.12-slim"
SUITE_DIR="tests/negative"

say() { printf '%s\n' "$*"; }

write_result() {
	local status="$1" code="$2" note="${3:-}"
	local head wname uname_s
	head="$(git -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
	wname="${WITNESS_NAME:-anonymous}"
	uname_s="$(uname -srm 2>/dev/null || echo unknown)"
	python3 - "$OUT" "$status" "$code" "$note" "$head" "$wname" "$uname_s" "$IMAGE" "$SUITE_DIR" <<'PY'
import hashlib, json, os, sys, time
out, status, code, note, head, wname, host, image, suite = sys.argv[1:10]
files = {}
if os.path.isdir(suite):
    for root, _, names in os.walk(suite):
        for n in sorted(names):
            p = os.path.join(root, n)
            with open(p, "rb") as f:
                files[os.path.relpath(p, ".")] = hashlib.sha256(f.read()).hexdigest()
json.dump({
    "schema": "witness-result/1.0",
    "status": status,
    "exit_code": int(code),
    "note": note,
    "head_sha": head,
    "suite_dir": suite,
    "suite_files": files,
    "suite_digest": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest() if files else None,
    "container_image": image,
    "witness": wname,
    "host": host,
    "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}, open(out, "w"), indent=2, sort_keys=True)
PY
}

die() {
	say ""
	say "NOT READY: $*"
	write_result "not_ready" 2 "$*"
	say "wrote $(basename "$OUT") with status=not_ready"
	exit 2
}

say "=== arifOS external witness kit ==="
say "repo:    $REPO_DIR"
say "commit:  $(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo 'not a git repo')"
say "witness: ${WITNESS_NAME:-anonymous (set WITNESS_NAME=\"your name\" to record it)}"
say ""

command -v docker >/dev/null 2>&1 || die "docker not found on this machine"
command -v git >/dev/null 2>&1 || die "git not found on this machine"

[ -d "${REPO_DIR}/${SUITE_DIR}" ] || die "${SUITE_DIR}/ does not exist in this commit — there is nothing to witness yet"
find "${REPO_DIR}/${SUITE_DIR}" -name 'test_*.py' 2>/dev/null | grep -q . || die "${SUITE_DIR}/ contains no test_*.py — an empty suite is not a passing suite"

say "Running the negative suite in a clean container (no kernel, no /root state, no network)..."
say ""

docker run --rm \
	--network none \
	-v "${REPO_DIR}:/w" -w /w \
	"$IMAGE" \
	sh -c "pip install -q -e . >/tmp/pip.log 2>&1 || { echo 'INSTALL FAILED'; tail -30 /tmp/pip.log; exit 5; }; python -m pytest -m offline ${SUITE_DIR} -q"

rc=$?

if [ "$rc" -eq 0 ]; then
	write_result "pass" 0 "suite green in ${IMAGE} with --network none"
	say ""
	say "RESULT: PASS — written to witness-result.json"
	say "Publish that file in a repo you own, in your own words."
	say "Optional, so it cannot be edited later: pip install opentimestamps-client && ots stamp witness-result.json"
	exit 0
else
	write_result "fail" "$rc" "suite not green (exit ${rc})"
	say ""
	say "RESULT: FAIL (exit ${rc}) — written to witness-result.json"
	say "Publish the failure. A failing witness report is worth more than a passing one."
	exit "$rc"
fi
