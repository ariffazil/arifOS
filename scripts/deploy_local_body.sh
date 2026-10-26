#!/usr/bin/env bash
# deploy_local_body.sh — the mutating half of `make deploy-local`.
#
# CONTRACT
#   The caller MUST already hold an active production lease (make deploy-local
#   acquires it before calling this). This script ALWAYS releases the lease:
#   on success, on any failure, and on SIGINT/SIGTERM. It exits with the
#   ORIGINAL status — the release never masks a failed deploy.
#
# WHY (measured defect, 2026-10-26)
#   `conformance_spine` returns 1 on a CAUTION verdict (its own "T6 SKIPPED is
#   not PASS" doctrine). That aborted make before the release recipe line, so
#   production stayed leased for the remainder of the 1800s TTL. Fail-closed,
#   but sticky: every other deploy was refused for up to 30 minutes.
#
# TEST SEAM
#   DEPLOY_DRY_RUN=1       skip every runtime mutation, still run the lease
#                          lifecycle (used by tests/scripts/test_deploy_lease.py)
#   CONFORMANCE_CMD=<cmd>  override the post-deploy verification command
#   ARIFOS_STATE_DIRECTORY redirect the lease ledger (tests only)
set -uo pipefail

DIR="${DIR:-/root/arifOS}"
PYTHON="${PYTHON:-/opt/arifos/current/venv/bin/python}"
GIT_SHA="${GIT_SHA:-$(git -C "$DIR" rev-parse HEAD)}"
LEASE_ACTOR="${DEPLOY_ACTOR:-$(whoami)}"
DEPLOY_RECEIPT="${DEPLOY_RECEIPT:-docs/releases}"
DRY="${DEPLOY_DRY_RUN:-0}"
SITE_PKGS="$($PYTHON -c 'import site; print(site.getsitepackages()[0])')"
LEASE_TOOL="$DIR/scripts/deploy_lease.py"

# ── the invariant: a lease that was acquired is released, whatever happens ──
release_lease() {
	local rc=$?
	trap - EXIT INT TERM
	echo "Releasing deploy lease (deploy exit=${rc})..."
	# shellcheck disable=SC2086
	if $PYTHON "$LEASE_TOOL" release --actor "$LEASE_ACTOR" \
		--session "${DEPLOY_SESSION:-}" --lease-id "${DEPLOY_LEASE_ID:-}" \
		--token "${DEPLOY_HOLDER_TOKEN:-}" --receipt "$DEPLOY_RECEIPT" \
		>/tmp/arifos-deploy-release.json 2>&1; then
		echo "Deploy lease released — epoch appended to ${ARIFOS_STATE_DIRECTORY:-/var/lib/arifos}/deploy_epochs.jsonl"
	else
		echo "WARNING: lease release FAILED — production may stay leased." >&2
		echo "  recover with: $PYTHON $LEASE_TOOL release --actor $LEASE_ACTOR" >&2
		cat /tmp/arifos-deploy-release.json >&2 || true
	fi
	exit "$rc"
}
trap release_lease EXIT INT TERM

# ── refuse to mutate without a lease (complete mediation on this path) ──────
if ! $PYTHON "$LEASE_TOOL" status --json 2>/dev/null | grep -q '"state": "LEASED"'; then
	echo "888_HOLD: NO_ACTIVE_LEASE — refusing to mutate production outside a lease." >&2
	trap - EXIT INT TERM
	exit 6
fi

echo "deploying ${GIT_SHA} as ${LEASE_ACTOR} (dry_run=${DRY})"
if [ "$DRY" = "1" ]; then
	echo "DEPLOY_DRY_RUN=1 — test seam: no runtime mutation, lease lifecycle still exercised"
fi

set -e

if [ "$DRY" = "1" ]; then
	echo "  [dry-run] rsync app skipped"
else
	echo "Syncing canonical code to /opt/arifos/app..."
	rsync -a --exclude='.git' --exclude='.venv' --exclude='.claude' \
		--exclude='.worktrees' --exclude='**/__pycache__' --exclude='.pytest_cache' \
		--exclude='node_modules' --exclude='build' --exclude='.mypy_cache' \
		"$DIR/" /opt/arifos/app/
	chown -R ariffazil:arifos /opt/arifos/app/ 2>/dev/null || true
	chmod -R u+rwX,go+rX /opt/arifos/app/
	chmod 640 /opt/arifos/app/.env 2>/dev/null || true
	chown arifos:arifos /opt/arifos/app/.env 2>/dev/null || true

	echo "Syncing runtime import path ($SITE_PKGS)..."
	rsync -a --exclude='__pycache__' "$DIR/arifosmcp/" "$SITE_PKGS/arifosmcp/"
	echo "$GIT_SHA" >/opt/arifos/app/.git_commit

	echo "Restarting arifOS bare-metal service..."
	systemctl restart arifos.service
fi

status=""
if [ "$DRY" = "1" ]; then
	status="dry-run"
else
	echo "Waiting for kernel health..."
	for i in $(seq 1 30); do
		status="$(curl -s -m 2 http://localhost:8088/health 2>/dev/null |
			python3 -c 'import sys,json; print(json.load(sys.stdin).get("status",""))' 2>/dev/null || true)"
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
fi

echo "Running conformance spine post-deploy..."
# shellcheck disable=SC2086
${CONFORMANCE_CMD:-$PYTHON -m arifosmcp.transport.conformance_spine}
echo "Conformance spine: exit 0"

# success falls through to the EXIT trap, which releases the lease
