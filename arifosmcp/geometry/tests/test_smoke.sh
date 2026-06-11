#!/usr/bin/env bash
# arifosmcp/geometry/tests/test_smoke.sh
# EUREKA-G smoke test — all 7 geometry modules: import + self-check.
# Run from /root/arifOS: PYTHONPATH=src bash arifosmcp/geometry/tests/test_smoke.sh
#
# Exit codes:
#   0 = all 7 PASS
#   1 = at least one FAIL
#   2 = at least one module missing (forge incomplete)

set -u

REPO_ROOT="${REPO_ROOT:-/root/arifOS}"
export PYTHONPATH="${PYTHONPATH:-${REPO_ROOT}/src}"

cd "$REPO_ROOT" || exit 2

declare -a MODULES=(
    "arifosmcp.geometry.manifold:_self_check"
    "arifosmcp.geometry.tom_geometry:_self_check"
    "arifosmcp.geometry.constitutional_gradient:_self_check"
    "arifosmcp.geometry.geometry_router:_self_check"
    "arifosmcp.geometry.drift:_self_check"
    "arifosmcp.geometry.eureka:_self_check"
    "arifosmcp.geometry.memory_key:_self_check"
    "arifosmcp.geometry.world_model:_self_check"
    "arifosmcp.geometry.trajectory_store:self_check"
)

pass=0
fail=0
missing=0

for entry in "${MODULES[@]}"; do
    mod="${entry%%:*}"
    fn="${entry##*:}"
    short="${mod##*.}"

    if ! python3 -c "import ${mod}" 2>/dev/null; then
        printf "  [MISSING] %s — module import failed\n" "$short"
        missing=$((missing + 1))
        continue
    fi

    if python3 -c "from ${mod} import ${fn}; ${fn}()" 2>/dev/null; then
        printf "  [PASS]    %s\n" "$short"
        pass=$((pass + 1))
    else
        printf "  [FAIL]    %s — %s() raised (see error above)\n" "$short" "$fn"
        fail=$((fail + 1))
    fi
done

printf "\ngeometry smoke: pass=%d fail=%d missing=%d\n" "$pass" "$fail" "$missing"

if [[ "$fail" -eq 0 && "$missing" -eq 0 ]]; then
    exit 0
elif [[ "$missing" -gt 0 ]]; then
    exit 2
else
    exit 1
fi
