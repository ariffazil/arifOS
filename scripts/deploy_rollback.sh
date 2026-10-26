#!/usr/bin/env bash
# deploy_rollback.sh — pre-registered rollback for governed local deploys.
#
# WHY (888 deployment-readiness condition, 2026-10-26)
#   The governed body mutated site-packages and the runtime markers with no
#   snapshot taken beforehand and no scripted way back. "Rollback available"
#   was aspirational text in deploy-release.sh pointing at rollback-* dirs
#   that nothing ever created. A deploy that cannot be undone by script is
#   an irreversible mutation wearing a reversible costume.
#
# CONTRACT
#   snapshot : capture the live importable package (site-packages/arifosmcp)
#              plus both deploy markers BEFORE the first protected write.
#              Output = tar + sha256 + meta + pointer file. Retention keeps
#              the newest ROLLBACK_RETENTION (default 4) snapshots.
#              The deploy body MUST refuse to mutate if snapshot fails.
#   restore  : verify snapshot hash, stop service, replace site-packages
#              content from the tar, restore markers, start service.
#              Restore is an F13/manual recovery verb — the deploy body
#              never invokes it automatically (no automatic retry doctrine).
#
# TEST SEAMS (all paths overridable; no production default is required)
#   SNAP_ROOT, POINTER_FILE, DEPLOYED_COMMIT_MARKER, APP_GIT_COMMIT_MARKER,
#   SERVICE_STOP_CMD, SERVICE_START_CMD, ROLLBACK_RETENTION
set -euo pipefail

SNAP_ROOT="${SNAP_ROOT:-/opt/arifos/releases}"
POINTER_FILE="${POINTER_FILE:-/tmp/arifos_rollback_dir.txt}"
DEPLOYED_COMMIT_MARKER="${DEPLOYED_COMMIT_MARKER:-/opt/arifos/releases/deployed-commit}"
APP_GIT_COMMIT_MARKER="${APP_GIT_COMMIT_MARKER:-/opt/arifos/app/.git_commit}"
RETENTION="${ROLLBACK_RETENTION:-4}"
# Lease mediation config — the restore verb is a production writer (W11) and
# refuses without a live lease. Declared before any service-mutating default
# so the ordering is real, not incidental.
LEASE_TOOL="${LEASE_TOOL:-$(cd "$(dirname "$0")" && pwd)/deploy_lease.py}"
REQUIRE_PYTHON="${REQUIRE_PYTHON:-/opt/arifos/current/venv/bin/python}"
SERVICE_STOP_CMD="${SERVICE_STOP_CMD:-systemctl stop arifos.service}"
SERVICE_START_CMD="${SERVICE_START_CMD:-systemctl start arifos.service}"

usage() {
	echo "usage: $0 snapshot --site-packages DIR --candidate SHA" >&2
	echo "       $0 restore  --snapshot DIR" >&2
	exit 2
}

cmd="${1:-}"
[ -n "$cmd" ] || usage
shift || true

case "$cmd" in
snapshot)
	SITE="" CAND=""
	while [ $# -gt 0 ]; do
		case "$1" in
		--site-packages)
			SITE="${2:-}"
			shift 2
			;;
		--candidate)
			CAND="${2:-}"
			shift 2
			;;
		*) usage ;;
		esac
	done
	[ -n "$SITE" ] && [ -n "$CAND" ] || usage
	if [ ! -d "$SITE/arifosmcp" ]; then
		echo "ROLLBACK_SNAPSHOT_FAILED: $SITE/arifosmcp absent — nothing live to roll back to" >&2
		exit 3
	fi
	SNAP="$SNAP_ROOT/rollback-$(date -u +%Y%m%dT%H%M%SZ)-${CAND:0:9}"
	if [ -e "$SNAP" ]; then
		# same-second collision: fail rather than overwrite a registered snapshot
		echo "ROLLBACK_SNAPSHOT_FAILED: $SNAP already exists" >&2
		exit 3
	fi
	mkdir -p "$SNAP"
	tar -C "$SITE" -cf "$SNAP/arifosmcp-site.tar" arifosmcp
	(cd "$SNAP" && sha256sum arifosmcp-site.tar >SNAPSHOT.sha256)
	{
		echo "site_packages=$SITE"
		echo "candidate_of_next_deploy=$CAND"
		echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
		echo "prev_deployed_commit=$(cat "$DEPLOYED_COMMIT_MARKER" 2>/dev/null || echo '')"
		echo "prev_app_git_commit=$(cat "$APP_GIT_COMMIT_MARKER" 2>/dev/null || echo '')"
	} >"$SNAP/SNAPSHOT.meta"
	mkdir -p "$(dirname "$POINTER_FILE")"
	echo "$SNAP" >"$POINTER_FILE"
	# retention: keep the newest $RETENTION snapshots (by mtime)
	ls -1dt "$SNAP_ROOT"/rollback-* 2>/dev/null | tail -n +$((RETENTION + 1)) |
		while IFS= read -r old; do rm -rf "$old"; done
	echo "ROLLBACK_REGISTERED $SNAP"
	;;
restore)
	SNAP=""
	while [ $# -gt 0 ]; do
		case "$1" in
		--snapshot)
			SNAP="${2:-}"
			shift 2
			;;
		*) usage ;;
		esac
	done
	if [ -z "$SNAP" ] && [ -f "$POINTER_FILE" ]; then
		SNAP="$(cat "$POINTER_FILE")"
	fi
	if [ -z "$SNAP" ] || [ ! -f "$SNAP/arifosmcp-site.tar" ]; then
		echo "RESTORE_FAILED: snapshot not found: ${SNAP:-<none>}" >&2
		exit 4
	fi
	# Complete mediation: a rollback IS a production mutation. A live lease must
	# authorize this host before restore writes anything — the same discipline
	# the deploy body (W02) and auto_remediate (W07) are held to. No bypass env.
	if ! "$REQUIRE_PYTHON" "$LEASE_TOOL" require --caller "deploy_rollback.sh:restore"; then
		echo "RESTORE_REFUSED: NO_ACTIVE_LEASE — acquire a deploy lease before rolling back production." >&2
		exit 6
	fi
	(cd "$SNAP" && sha256sum -c SNAPSHOT.sha256) || {
		echo "RESTORE_FAILED: snapshot hash mismatch — refusing to restore tampered bytes" >&2
		exit 5
	}
	SITE="$(sed -n 's/^site_packages=//p' "$SNAP/SNAPSHOT.meta")"
	[ -n "$SITE" ] && [ -d "$SITE" ] || {
		echo "RESTORE_FAILED: snapshot meta lacks a live site_packages target" >&2
		exit 4
	}
	$SERVICE_STOP_CMD
	rm -rf "${SITE:?}/arifosmcp"
	tar -C "$SITE" -xf "$SNAP/arifosmcp-site.tar"
	PREV_DEPLOYED="$(sed -n 's/^prev_deployed_commit=//p' "$SNAP/SNAPSHOT.meta" || true)"
	PREV_APP="$(sed -n 's/^prev_app_git_commit=//p' "$SNAP/SNAPSHOT.meta" || true)"
	if [ -n "$PREV_DEPLOYED" ]; then
		mkdir -p "$(dirname "$DEPLOYED_COMMIT_MARKER")"
		echo "$PREV_DEPLOYED" >"$DEPLOYED_COMMIT_MARKER"
	fi
	if [ -n "$PREV_APP" ]; then
		mkdir -p "$(dirname "$APP_GIT_COMMIT_MARKER")"
		echo "$PREV_APP" >"$APP_GIT_COMMIT_MARKER"
	fi
	$SERVICE_START_CMD
	echo "ROLLBACK_RESTORED from $SNAP into $SITE"
	;;
*)
	usage
	;;
esac
