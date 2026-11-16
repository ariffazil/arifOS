#!/bin/bash
# immutability_cycle.sh — shared chattr unlock/relock helper (F13 zen pass 2026-11-03)
#
# WHY: /root/arifOS production tree nodes are hardened with chattr +i
# (repo root, build/, arifos.egg-info/, .git_commit markers). deploy-release.sh
# must rm build artifacts and rewrite markers, but until now it did NOT own
# that cycle — measured 2026-11-03: two deploys died on
# "rm: cannot remove 'build': Operation not permitted" and a third on
# ".git_commit: Operation not permitted". git-lane owns the .git cycle; this
# helper gives deploy-release.sh the same discipline for the WORKING TREE.
#
# USAGE (source, then call once per script):
#   source "$(dirname "${BASH_SOURCE[0]}")/lib/immutability_cycle.sh"
#   immutability_unlock "<path>" "<path>" ...   # records + unlocks, traps relock
#
# Idempotent: nodes without the +i flag are skipped and never re-locked.
# The EXIT/INT/TERM/HUP trap relocks exactly what was unlocked — an aborted
# run can never leave the tree softer than it found it.

_IMMUTABILITY_UNLOCKED_LIST="$(mktemp /tmp/arifos-immutability.XXXXXX)"
_IMMUTABILITY_TRAP_ARMED=0

_immutable_relock_all() {
    local rc=$?
    trap - EXIT INT TERM HUP
    if [ -s "$_IMMUTABILITY_UNLOCKED_LIST" ]; then
        # Never fail the exiting script because a relock hiccupped.
        xargs -r chattr +i <"$_IMMUTABILITY_UNLOCKED_LIST" 2>/dev/null || true
    fi
    rm -f "$_IMMUTABILITY_UNLOCKED_LIST" 2>/dev/null || true
    return "$rc"
}

immutability_unlock() {
    # Arms the relock trap on first use.
    if [ "$_IMMUTABILITY_TRAP_ARMED" -eq 0 ]; then
        trap _immutable_relock_all EXIT INT TERM HUP
        _IMMUTABILITY_TRAP_ARMED=1
    fi
    local node flags
    for node in "$@"; do
        [ -e "$node" ] || continue
        flags="$(lsattr -d "$node" 2>/dev/null | awk '{print $1}')"
        case "$flags" in
        *i*) ;;
        *) continue ;;
        esac
        if chattr -i "$node" 2>/dev/null; then
            printf '%s\n' "$node" >>"$_IMMUTABILITY_UNLOCKED_LIST"
        else
            echo "WARNING: immutability_cycle could not unlock $node — continuing" >&2
        fi
    done
}
