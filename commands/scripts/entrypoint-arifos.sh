#!/bin/bash
# ArifOS MCP Server Entrypoint
# Fixes Python namespace package resolution for Docker volume mounts
# and injects live git metadata into env vars for /health traceability

set -e

# ── Git metadata from host (bind-mounted at /usr/src/app = /root/arifOS) ──────
# The entire /root/arifOS repo is bind-mounted. Use the host git to extract
# current SHA + date-derived version tag, then export into the container env.
ARIFOS_GIT_DIR="${ARIFOS_GIT_DIR:-/root/arifOS/.git}"

if [ -d "$ARIFOS_GIT_DIR" ] && [ -r "$ARIFOS_GIT_DIR/HEAD" ]; then
    # Read current branch name
    _head_ref=$(cat "$ARIFOS_GIT_DIR/HEAD" 2>/dev/null || echo "ref: refs/heads/main")
    if [[ "$_head_ref" == ref:\ refs/heads/* ]]; then
        _branch="${_head_ref#ref: refs/heads/}"
        _branch="${_branch// /}"
    else
        _branch=" detached"
    fi

    # Read current commit SHA
    if [ -f "$ARIFOS_GIT_DIR/HEAD" ] && [ "$(cat "$ARIFOS_GIT_DIR/HEAD")" != "ref: "* ]; then
        # Direct SHA (detached HEAD)
        _commit_sha="$(cat "$ARIFOS_GIT_DIR/HEAD" | tr -d ' \n')"
    elif [ -f "$ARIFOS_GIT_DIR/"*"$_branch"* ] 2>/dev/null; then
        _commit_sha="$(cat "$ARIFOS_GIT_DIR/refs/heads/$_branch" 2>/dev/null | tr -d ' \n')"
    elif [ -f "$ARIFOS_GIT_DIR/ORIG_HEAD" ]; then
        _commit_sha="$(cat "$ARIFOS_GIT_DIR/ORIG_HEAD" 2>/dev/null | tr -d ' \n')"
    fi

    if [ -n "$_commit_sha" ] && [ ${#_commit_sha} -ge 7 ]; then
        export GIT_SHA="${_commit_sha:0:7}"
        echo "[arifOS] GIT_SHA=$GIT_SHA (branch: $_branch)"
    else
        export GIT_SHA="unknown"
        echo "[arifOS] GIT_SHA=unknown (could not resolve commit)"
    fi

    # Date-derived version tag: vYYYY.4.D (year.quarter.day-of-quarter)
    if [ -n "$_commit_sha" ] && [ -f "$ARIFOS_GIT_DIR/commits/$(echo $_commit_sha | cut -c1-2)/$(echo $_commit_sha | cut -c3-40)" ] 2>/dev/null; then
        # Loose object file (fallback)
        _commit_time=$(stat -c %Y "$ARIFOS_GIT_DIR/objects/$(echo $_commit_sha | cut -c1-2)/$(echo $_commit_sha | cut -c3-40)" 2>/dev/null || echo "")
    elif git -C /root/arifOS rev-list --format=%ci --max-count=1 "$_commit_sha" 2>/dev/null | tail -1 | grep -q .; then
        _commit_time=$(git -C /root/arifOS rev-list --format=%ci --max-count=1 "$_commit_sha" 2>/dev/null | tail -1 | cut -d' ' -f1 || echo "")
    fi

    if [ -n "$_commit_time" ]; then
        _year=$(echo "$_commit_time" | cut -d'-' -f1)
        _month=$(echo "$_commit_time" | cut -d'-' -f2)
        _day=$(echo "$_commit_time" | cut -d'-' -f3 | cut -d'T' -f1)
        # Quarter: 1=Jan-Mar, 2=Apr-Jun, 3=Jul-Sep, 4=Oct-Dec
        _quarter=$(( (_month - 1) / 3 + 1 ))
        # Day of quarter: count days from start of quarter
        _qstart_month=$(( (_quarter - 1) * 3 + 1 ))
        _qstart_day=1
        # Days into quarter (rough calc)
        _days_offset=0
        for _m in $(seq 1 $((_month - 1))); do
            case $_m in 1|3|5|7|8|10|12) _days_offset=$((_days_offset + 31));; 4|6|9|11) _days_offset=$((_days_offset + 30));; 2) _days_offset=$((_days_offset + 28));; esac
        done
        _days_offset=$((_days_offset + _day))
        _day_of_quarter=$(( (_month <= _qstart_month) ? _day : _days_offset - $(( (_qstart_month - 1) * 30 + 1 )) + 1 ))
        _day_of_quarter=${_day_of_quarter#-}

        export ARIFOS_APP_VERSION="v${_year}.${_quarter}.$((_day_of_quarter))"
        echo "[arifOS] ARIFOS_APP_VERSION=$ARIFOS_APP_VERSION (from commit date)"
    fi
else
    echo "[arifOS] Git dir not accessible at $ARIFOS_GIT_DIR — using Dockerfile ARGs"
fi

# ── Python namespace symlinks ─────────────────────────────────────────────────

# Create symlink so 'from arifOS.core.shared.types' resolves correctly
# when core/ is volume-mounted at /usr/src/app/core instead of /usr/src/app/arifOS/core
if [ -d "/usr/src/app/arifOS" ] && [ ! -L "/usr/src/app/arifOS/core" ] && [ -d "/usr/src/app/core" ]; then
    ln -sf /usr/src/app/core /usr/src/app/arifOS/core
    echo "[arifOS] Linked /usr/src/app/arifOS/core -> /usr/src/app/core"
fi

# Also fix arifosmcp -> arifOS/arifosmcp if needed
if [ -d "/usr/src/app/arifOS" ] && [ ! -L "/usr/src/app/arifOS/arifosmcp" ] && [ -d "/usr/src/app/arifosmcp" ]; then
    ln -sf /usr/src/app/arifosmcp /usr/src/app/arifOS/arifosmcp
    echo "[arifOS] Linked /usr/src/app/arifOS/arifosmcp -> /usr/src/app/arifosmcp"
fi

# ── Run the original command ──────────────────────────────────────────────────
exec "$@"
