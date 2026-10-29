#!/usr/bin/env bash
# deploy_local_body.sh — the ONLY mutating half of `make deploy-local`.
#
# CONTRACT
#   The caller must hold a live lease AND a 0600 authorization envelope minted
#   by `deploy_lease.py acquire`. The body proves ownership (sha256(token) ==
#   lease.holder_token_sha256), proves the live artifact is the lease baseline,
#   and proves HEAD == LEASE_CANDIDATE before the first protected write.
#
#   The body ALWAYS releases the lease on exit, including exit 7/8/9. A refused
#   preflight records a failed epoch and blocks the next governed deploy until
#   F13 resolves it; it never leaves the lease held until TTL.
#
# WHY (measured defects, 2026-10-26)
#   - release without --actor cleared a live lease
#   - the body re-read HEAD and deployed a different commit than the lease
#   - SITE_PKGS was derived from a mutable $PYTHON
#   - the holder token was written to /tmp and passed through argv
#   - verify-epoch was called before release (impossible by construction)
#
# TEST SEAM
#   DEPLOY_DRY_RUN=1       skip runtime mutation, still exercise lease lifecycle
#   CONFORMANCE_CMD=<cmd>  override the post-deploy verification command
#   ARIFOS_STATE_DIRECTORY redirect the lease ledger (tests only)
set -uo pipefail

DIR="${DIR:-/root/arifOS}"
PYTHON="${PYTHON:-/opt/arifos/current/venv/bin/python}"
RUNTIME_PYTHON="/opt/arifos/current/venv/bin/python"
LEASE_ACTOR="${DEPLOY_ACTOR:-$(whoami)}"
LEASE_SESSION="${DEPLOY_SESSION:-}"
DEPLOY_RECEIPT="${DEPLOY_RECEIPT:-docs/releases}"
DRY="${DEPLOY_DRY_RUN:-0}"
STATE_DIR="${ARIFOS_STATE_DIRECTORY:-/var/lib/arifos}"
ENVELOPE="${STATE_DIR}/deploy_envelope.json"
LEASE_TOOL="$DIR/scripts/deploy_lease.py"
SITE_PACKAGES="$("$RUNTIME_PYTHON" -c 'import site; print(site.getsitepackages()[0])')"
LEASE_ID=""
LEASE_CANDIDATE=""
EXPORT_DIR=""
RELEASED=0
ROLLBACK_SNAPSHOT=""
STALE_PRUNED="na"

# ── the invariant: a lease that was acquired is released, whatever happens ──
release_lease() {
	local rc=$?
	trap - EXIT INT TERM
	if [ -n "$EXPORT_DIR" ]; then
		rm -rf "$EXPORT_DIR"
	fi
	if [ "$RELEASED" = "1" ]; then
		exit "$rc"
	fi
	echo "Releasing deploy lease (deploy exit=${rc})..."
	if [ -z "$LEASE_ID" ]; then
		echo "WARNING: no lease id captured; lease may remain until TTL." >&2
		exit "$rc"
	fi
	if "$PYTHON" "$LEASE_TOOL" release --envelope "$ENVELOPE" \
		--actor "$LEASE_ACTOR" --session "$LEASE_SESSION" \
		--receipt "$DEPLOY_RECEIPT" --exit-code "$rc" \
		--observed-head "${HEAD_SHA:-}" \
		--rollback-snapshot "${ROLLBACK_SNAPSHOT:-NONE}" \
		--stale-pruned "$STALE_PRUNED" \
		>/tmp/arifos-deploy-release.json 2>&1; then
		echo "Deploy lease released — epoch appended to ${STATE_DIR}/deploy_epochs.jsonl"
	else
		local release_rc=$?
		if [ "$release_rc" -eq 11 ]; then
			echo "Deploy lease released — epoch recorded as CANDIDATE_MISMATCH (evidence preserved)."
		else
			echo "WARNING: lease release failed (exit=${release_rc}) — the lease may remain until TTL." >&2
			cat /tmp/arifos-deploy-release.json >&2 || true
		fi
	fi
	exit "$rc"
}
trap release_lease EXIT INT TERM

# A unique session is required before any acquire. make deploy-local also
# checks this; the body repeats it because the body is the last line of defense.
if [ -z "$LEASE_SESSION" ]; then
	echo "888_HOLD: HOLD_SESSION_REQUIRED — set DEPLOY_SESSION to a unique session id." >&2
	exit 2
fi

# Capture non-secret lease identity from the live lease. This does not prove
# ownership; check-envelope does that before any protected write.
STATUS_JSON="$("$PYTHON" "$LEASE_TOOL" status --json 2>/dev/null || true)"
LEASE_ID="$(printf '%s' "$STATUS_JSON" | "$RUNTIME_PYTHON" -c 'import json,sys; print((json.load(sys.stdin).get("lease") or {}).get("lease_id",""))' 2>/dev/null || true)"
LEASE_CANDIDATE="$(printf '%s' "$STATUS_JSON" | "$RUNTIME_PYTHON" -c 'import json,sys; print((json.load(sys.stdin).get("lease") or {}).get("candidate_commit",""))' 2>/dev/null || true)"
if [ -z "$LEASE_ID" ]; then
	echo "888_HOLD: NO_ACTIVE_LEASE — refusing to mutate production outside a lease." >&2
	exit 6
fi

# ── preflight 1: ownership envelope, including the opaque token hash ────────
if ! "$PYTHON" "$LEASE_TOOL" check-envelope --envelope "$ENVELOPE" \
	--actor "$LEASE_ACTOR" --session "$LEASE_SESSION" \
	>/tmp/arifos-envelope-check.json 2>&1; then
	echo "888_HOLD: HOLD_UNAPPROVED_ENTRY_POINT — the envelope does not prove this caller owns the lease." >&2
	cat /tmp/arifos-envelope-check.json >&2 || true
	exit 7
fi

# ── preflight 2: the live artifact must be the lease baseline ───────────────
if ! "$PYTHON" "$LEASE_TOOL" verify-baseline \
	>/tmp/arifos-baseline-check.json 2>&1; then
	echo "888_HOLD: HOLD_ARTIFACT_DRIFT — the live artifact is not the lease baseline." >&2
	cat /tmp/arifos-baseline-check.json >&2 || true
	exit 4
fi

# ── preflight 3: candidate binding — no second authority read ───────────────
HEAD_SHA="$(git -C "$DIR" rev-parse HEAD 2>/dev/null || true)"
if [ "$HEAD_SHA" != "$LEASE_CANDIDATE" ]; then
	echo "888_HOLD: HOLD_CANDIDATE_CHANGED — HEAD ${HEAD_SHA:-unknown} != lease candidate ${LEASE_CANDIDATE:-unknown}. Zero protected writes." >&2
	exit 9
fi
if [ -n "$(git -C "$DIR" status --porcelain --untracked-files=no 2>/dev/null)" ]; then
	echo "888_HOLD: HOLD_DIRTY_SOURCE — tracked files modified in $DIR. Zero protected writes." >&2
	exit 8
fi

echo "deploying ${LEASE_CANDIDATE} as ${LEASE_ACTOR} (session=${LEASE_SESSION}, dry_run=${DRY})"
if [ "$DRY" = "1" ]; then
	echo "DEPLOY_DRY_RUN=1 — test seam: no runtime mutation; lease lifecycle still exercised"
fi

set -e

if [ "$DRY" != "1" ]; then
	# Immutable source: export the pinned commit, not the mutable worktree.
	# This is what makes C4 real — untracked or post-assertion files cannot ride
	# rsync into the deployed artifact.
	EXPORT_DIR="$(mktemp -d "${TMPDIR:-/var/tmp}/arifos-deploy.XXXXXX")"
	git -C "$DIR" archive --format=tar "$LEASE_CANDIDATE" | tar -x -C "$EXPORT_DIR"

	# ── regression guard: the deployed artifact must be an ancestor of the
	# candidate (888 recurrence signal — main fell behind the live lineage
	# twice in 19h). Unknown marker fails closed. Zero protected writes on HOLD.
	DEPLOYED_MARK="$(cat "${DEPLOYED_COMMIT_MARKER:-/opt/arifos/releases/deployed-commit}" 2>/dev/null || true)"
	if ! "$PYTHON" "$LEASE_TOOL" check-ancestry --repo "$DIR" \
		--deployed "$DEPLOYED_MARK" --candidate "$LEASE_CANDIDATE" \
		>/tmp/arifos-ancestry-check.json 2>&1; then
		echo "888_HOLD: DEPLOY_REGRESSION_RISK — deployed ${DEPLOYED_MARK:-<none>} is not an ancestor of candidate ${LEASE_CANDIDATE}. Zero protected writes." >&2
		cat /tmp/arifos-ancestry-check.json >&2 || true
		exit 13
	fi

	# ── pre-registered rollback snapshot — BEFORE the first protected write ──
	# 888 deployment-readiness condition (2026-10-26): a governed deploy that
	# cannot be undone by script is not reversible. Fail-closed: no snapshot,
	# no mutation.
	if ! SNAP_OUT="$("$DIR/scripts/deploy_rollback.sh" snapshot \
		--site-packages "$SITE_PACKAGES" --candidate "$LEASE_CANDIDATE" 2>&1)"; then
		echo "888_HOLD: ROLLBACK_NOT_REGISTERED — refusing to mutate production without a pre-registered snapshot." >&2
		echo "$SNAP_OUT" >&2
		exit 10
	fi
	ROLLBACK_SNAPSHOT="$(printf '%s\n' "$SNAP_OUT" | sed -n 's/^ROLLBACK_REGISTERED //p')"
	echo "$SNAP_OUT"
	echo "Rollback registered: ${ROLLBACK_SNAPSHOT:-unknown}"

	# Stale-module accounting: modules live in site-packages but absent from
	# the pinned candidate are pruned by --delete below and counted here so the
	# epoch records what the deploy removed, not just what it wrote.
	STALE_COUNT="$(comm -23 \
		<(cd "$SITE_PACKAGES/arifosmcp" 2>/dev/null && find . -name '*.py' | sort) \
		<(cd "$EXPORT_DIR/arifosmcp" && find . -name '*.py' | sort) | grep -c . || true)"

	echo "Syncing canonical code to /opt/arifos/app (export=$EXPORT_DIR)..."
	rsync -a --exclude='.git' --exclude='.venv' --exclude='.claude' \
		--exclude='.worktrees' --exclude='**/__pycache__' --exclude='.pytest_cache' \
		--exclude='node_modules' --exclude='build' --exclude='.mypy_cache' \
		"$EXPORT_DIR/" /opt/arifos/app/
	chown -R ariffazil:arifos /opt/arifos/app/ 2>/dev/null || true
	chmod -R u+rwX,go+rX /opt/arifos/app/
	chmod 640 /opt/arifos/app/.env 2>/dev/null || true
	chown arifos:arifos /opt/arifos/app/.env 2>/dev/null || true

	echo "Syncing runtime import path ($SITE_PACKAGES)..."
	# --delete: the export IS the complete authorized package; a module the
	# candidate removed must not survive in the import path (stale-module
	# defect class: deployed tree silently keeps the previous release's code).
	rsync -a --delete --exclude='__pycache__' "$EXPORT_DIR/arifosmcp/" "$SITE_PACKAGES/arifosmcp/"
	find "$SITE_PACKAGES/arifosmcp" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
	STALE_PRUNED="true:stale_modules_pruned=${STALE_COUNT:-0}"

	# Top-level `core` package (2026-10-28). rest_routes imports
	# `core.governance_kernel`, and with cwd=/var/lib/arifos that resolves to
	# $SITE_PACKAGES/core/ -- NOT /opt/arifos/app/core/ and NOT the repo tree.
	# This deploy used to sync only arifosmcp/, so every commit touching core/
	# reached /opt/arifos/app and the test suite but never the live import path:
	# a deploy reported "aligned" while the running kernel executed the previous
	# release's core. Measured 2026-10-28: commit 6a644b07c (measurement window
	# declaration) was absent from live /health with deployment_drift=aligned.
	#
	# NO --delete here, deliberately: $SITE_PACKAGES/core/vault999/ (9 files:
	# unified_vault999.py, verify.py, reality_ledger.py, redaction.py + data)
	# exists only in the deployed tree, not in the repo. A --delete sync would
	# erase live vault code. Update-in-place, never prune this tree.
	if [ -d "$EXPORT_DIR/core" ]; then
		rsync -a --exclude='__pycache__' "$EXPORT_DIR/core/" "$SITE_PACKAGES/core/"
		find "$SITE_PACKAGES/core" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
		echo "Synced core/ into \$SITE_PACKAGES/core (no --delete: deployed-only vault999 preserved)."
	fi

	# Marker provenance: both stamps are written from LEASE_CANDIDATE, never
	# from a post-acquire HEAD re-read.
	echo "$LEASE_CANDIDATE" >/opt/arifos/app/.git_commit
	mkdir -p /opt/arifos/releases
	echo "$LEASE_CANDIDATE" >/opt/arifos/releases/deployed-commit

	# 2026-10-27 (stabilization-tail B2): the runtime attestation also reads
	# /opt/arifos/releases/release-manifest.json — a third stamp previously
	# written only by the legacy deploy-release.sh wheel path. Leaving it
	# stale made /health report drift=true against a proven-current artifact
	# until a manual reconcile + restart. Rewrite it from LEASE_CANDIDATE,
	# same provenance as the two stamps above.
	"$RUNTIME_PYTHON" -c 'import json,sys,os; p="/opt/arifos/releases/release-manifest.json"; c=sys.argv[1]; m=json.load(open(p)) if os.path.exists(p) else {"release":1,"name":"Runtime Truth"}; m.update({"git_commit":c,"origin_main_commit":c[:10],"deployed_via":"deploy_local_body.sh"}); json.dump(m,open(p,"w"),indent=2)' "$LEASE_CANDIDATE" 2>/dev/null || true


	# ── P7 (RSI reconciliation §12, landed 2026-10-29): deploy provenance receipt ──
	# deploy-release.sh writes /opt/arifos/current/receipts/latest.json but the
	# deploy-local path never did, so /health reported
	# deployed_commit_receipt_stale=true after every local deploy (epoch 36
	# measured: receipt still described 7599f1c4 from 2026-10-28). Write BOTH
	# truths from ONE place, every deploy: a dated receipt file plus
	# latest.json re-pointed at it — a symlink swap preserves the dated
	# history; writing THROUGH the link would overwrite an old receipt.
	RECEIPT_DIR="/opt/arifos/current/receipts"
	RECEIPT_TS="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
	mkdir -p "$RECEIPT_DIR" /var/lib/arifos/deploy_receipts
	PREV_RECEIPT_SHA="$("$RUNTIME_PYTHON" -c "import json
try: print(json.load(open('$RECEIPT_DIR/latest.json')).get('commit_sha',''))
except Exception: print('')" 2>/dev/null || true)"
	"$RUNTIME_PYTHON" - "$RECEIPT_DIR/${RECEIPT_TS}.json" "$LEASE_CANDIDATE" "$RECEIPT_TS" "$PREV_RECEIPT_SHA" "$DEPLOY_SESSION" "$DEPLOY_ACTOR" <<'PYRC'
import json, sys
path, commit, ts, prev, session, actor = sys.argv[1:7]
json.dump({
    "commit_sha": commit,
    "branch": "main",
    "build_time": ts,
    "deployed_via": "deploy_local_body.sh",
    "prev_commit_sha": prev or None,
    "deploy_session": session or None,
    "deploy_actor": actor or None,
}, open(path, "w"), indent=1)
PYRC
	ln -sfn "${RECEIPT_TS}.json" "$RECEIPT_DIR/latest.json"
	cat >"/var/lib/arifos/deploy_receipts/${RECEIPT_TS}-${LEASE_CANDIDATE:0:8}.md" <<MDRC
# arifOS deploy receipt — ${RECEIPT_TS}

- commit: ${LEASE_CANDIDATE}
- deployed via: deploy_local_body.sh (make deploy-local)
- session: ${DEPLOY_SESSION:-unattributed} · actor: ${DEPLOY_ACTOR:-unattributed}
- prev commit (receipt chain): ${PREV_RECEIPT_SHA:-none}
- dated JSON receipt: ${RECEIPT_DIR}/${RECEIPT_TS}.json
MDRC
	echo "Deploy receipt (P7): $RECEIPT_DIR/latest.json -> ${RECEIPT_TS}.json"
	
	# ── P6 (RSI reconciliation §12, landed 2026-10-29): pre-deploy health snapshot ──
	# Capture the RUNNING kernel's /health immediately before the restart so a
	# later read has a same-instrument pre-image. A failed capture is recorded
	# as a .FAILED marker — never silently absent.
	SNAP_DIR="/var/lib/arifos/deploy_health_snapshots"
	mkdir -p "$SNAP_DIR"
	if curl -sf -m 5 http://127.0.0.1:8088/health -o "$SNAP_DIR/pre-${LEASE_CANDIDATE:0:8}-${RECEIPT_TS}.json"; then
		echo "Pre-deploy health snapshot (P6): $SNAP_DIR/pre-${LEASE_CANDIDATE:0:8}-${RECEIPT_TS}.json"
	else
		printf '{"captured_utc":"%s","commit":"%s","error":"health capture failed pre-restart"}\n' \
			"$RECEIPT_TS" "$LEASE_CANDIDATE" >"$SNAP_DIR/pre-${LEASE_CANDIDATE:0:8}-${RECEIPT_TS}.FAILED.json"
		echo "P6 WARNING: pre-deploy health capture FAILED (marker written)"
	fi
	echo "Restarting arifOS bare-metal service..."
	systemctl restart arifos.service

	echo "Waiting for kernel health..."
	status=""
	for i in $(seq 1 30); do
		status="$(curl -s -m 2 http://localhost:8088/health 2>/dev/null |
			"$RUNTIME_PYTHON" -c 'import sys,json; print(json.load(sys.stdin).get("status",""))' 2>/dev/null || true)"
		if [ -n "$status" ]; then
			echo "Kernel answers (status=$status) after ${i}s"
			break
		fi
		sleep 2
	done
	if [ -z "$status" ]; then
		echo "888_HOLD: KERNEL_BOOT_UNRESPONSIVE — no /health answer after 60s" >&2
		exit 1
	fi
	echo "Deploy gate: kernel booted and answers (status=$status) — honesty of status is floor work, not a boot gate"

	# The running package must be the authorized candidate before we release.
	if ! "$PYTHON" "$LEASE_TOOL" verify-candidate --envelope "$ENVELOPE" \
		--actor "$LEASE_ACTOR" --session "$LEASE_SESSION" \
		>/tmp/arifos-candidate-check.json 2>&1; then
		echo "888_HOLD: ARTIFACT_CHANGED — running package is not the authorized candidate." >&2
		cat /tmp/arifos-candidate-check.json >&2 || true
		exit 4
	fi
fi

echo "Running conformance gate post-deploy..."
CONFORMANCE_RECEIPT="${CONFORMANCE_RECEIPT:-$STATE_DIR/conformance_amber.json}"
export CONFORMANCE_RECEIPT
if [ -n "${CONFORMANCE_CMD:-}" ]; then
	# shellcheck disable=SC2086
	$CONFORMANCE_CMD >/tmp/arifos-conformance.json 2>&1
else
	"$PYTHON" "$DIR/scripts/conformance_deploy_gate.py" >/tmp/arifos-conformance.json 2>&1
fi
cat /tmp/arifos-conformance.json
echo "Conformance gate: exit 0 (PASS or explicitly accepted AMBER)"

# ── release FIRST; verify-epoch can only stamp a RELEASED epoch ────────────
set +e
"$PYTHON" "$LEASE_TOOL" release --envelope "$ENVELOPE" \
	--actor "$LEASE_ACTOR" --session "$LEASE_SESSION" \
	--receipt "$DEPLOY_RECEIPT" --exit-code 0 \
	--observed-head "$HEAD_SHA" \
	--rollback-snapshot "${ROLLBACK_SNAPSHOT:-NONE(dry_run)}" \
	--stale-pruned "$STALE_PRUNED" \
	>/tmp/arifos-deploy-release.json 2>&1
RELEASE_RC=$?
set -e
if [ "$RELEASE_RC" -eq 0 ] || [ "$RELEASE_RC" -eq 11 ]; then
	RELEASED=1
fi
if [ "$RELEASE_RC" -ne 0 ]; then
	echo "888_HOLD: release refused or candidate mismatch (exit=${RELEASE_RC})." >&2
	cat /tmp/arifos-deploy-release.json >&2 || true
	exit "$RELEASE_RC"
fi
echo "Deploy lease released — epoch appended to ${STATE_DIR}/deploy_epochs.jsonl"

# ── post-release verdict: candidate == marker == manifest, or no clearance ──
if ! "$PYTHON" "$LEASE_TOOL" verify-epoch --lease-id "$LEASE_ID" \
	--verdict PASS --evidence "$DEPLOY_RECEIPT" \
	--actor "$LEASE_ACTOR" --session "$LEASE_SESSION" \
	>/tmp/arifos-verify-epoch.json 2>&1; then
	echo "888_HOLD: verify-epoch failed — the next governed deploy stays HOLD until a PASS verdict is recorded." >&2
	cat /tmp/arifos-verify-epoch.json >&2 || true
	exit 12
fi
echo "verify-epoch PASS — candidate/artifact equivalence recorded."
