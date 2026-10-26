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

	# Marker provenance: both stamps are written from LEASE_CANDIDATE, never
	# from a post-acquire HEAD re-read.
	echo "$LEASE_CANDIDATE" >/opt/arifos/app/.git_commit
	mkdir -p /opt/arifos/releases
	echo "$LEASE_CANDIDATE" >/opt/arifos/releases/deployed-commit

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
