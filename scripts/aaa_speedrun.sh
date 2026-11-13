#!/usr/bin/env bash
# =============================================================================
# aaa_speedrun.sh — one-command live proof of the arifOS governed loop
#
# Inspired by karpathy/nanochat runs/speedrun.sh: the whole system must
# survive being run by a stranger on a blank terminal and produce something
# a human can EXPERIENCE at the end — not just an audit artifact.
#
# nanochat ends with "talk to your model".
# This ends with "talk to your constitution".
#
# Stages (canonical 8-verb chain, minus forge/seal which stay with 888/F13):
#   0 health   — is the kernel alive?
#   1 init     → bind session (identity, floors, clock)
#   2 observe  → vitals (measured machine reality)
#   3 think    → structured reasoning probe
#   4 route    → intent classification probe
#   5 judge    → constitutional verdict on a benign candidate
#   6 receipt  → sha256-hashed evidence file in runs/
#
# Stage verdicts: PASS | DEGRADED (unreachable/5xx/refused-without-answer) | FAIL
# NOTE: a REASONED verdict (SEAL/HOLD/SABAR/VOID) from judge counts as PASS —
# the constitution answering "HOLD, and here is why" is the system working,
# not the service degrading. Only silence or transport failure is DEGRADED.
#
# Exit codes: 0 = all PASS · 3 = any DEGRADED/FAIL (probe_runtime_source conv.)
# seal is NEVER attempted: VAULT999 writes belong to 888_APEX / F13.
# =============================================================================
set -u

BASE="${ARIFOS_URL:-http://localhost:8088}"
ACTOR="${AAA_ACTOR:-speedrun/human}"
TIMEOUT="${AAA_TIMEOUT:-90}"
OUTDIR="${AAA_SPEEDRUN_OUTDIR:-$PWD/runs}"
mkdir -p "$OUTDIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
RECEIPT="$OUTDIR/speedrun-$TS.json"

hr()  { printf '%.0s─' $(seq 1 72); echo; }
say() { printf "%-9s %s\n" "$1" "$2"; }

# call <tool> <json-args> -> sets globals BODY, RC (http code), LAT (ms)
call() {
  local tool="$1" args="$2" raw
  raw=$(curl -s -m "$TIMEOUT" -w '\n%{http_code} %{time_total}' \
    -X POST "$BASE/tools/$tool/call" \
    -H "Content-Type: application/json" -d "$args" 2>/dev/null)
  RC=$(echo "$raw" | tail -1 | awk '{print $1}')
  LAT=$(echo "$raw" | tail -1 | awk '{printf "%d", $2*1000}')
  RC=${RC:-000}; LAT=${LAT:-0}
  BODY=$(echo "$raw" | sed '$d')
}

declare -a STAGES=()
record() { # record <stage> <verdict> <http> <lat_ms> <detail>
  STAGES+=("{\"stage\":\"$1\",\"verdict\":\"$2\",\"http\":\"$3\",\"latency_ms\":$4,\"detail\":\"$5\"}")
  local icon="✗"; [ "$2" = "PASS" ] && icon="✓"; [ "$2" = "DEGRADED" ] && icon="~"
  say "$icon $1" "$2  (http $3, ${4}ms) — $5"
}
classify() { # classify <body> <http> -> PASS|DEGRADED|FAIL  (stdout)
  local body="$1" http="$2"
  [ "$http" = "000" ] && { echo FAIL; return; }
  { [ "$http" = "503" ] || [ "$http" = "502" ] || [ "$http" = "403" ]; } \
    && { echo DEGRADED; return; }
  echo "$body" | jq -e '.status=="success" or .status=="completed"' >/dev/null 2>&1 \
    && echo PASS || echo DEGRADED
}

hr; echo "AAA SPEEDRUN — governed-loop live proof · $TS"; echo "target: $BASE"; hr

# ── Stage 0: health ──────────────────────────────────────────────────────────
H=$(curl -s -m 15 "$BASE/health")
if [ -z "$H" ]; then
  record "health" "FAIL" "000" 0 "kernel unreachable — is arifos-mcp running?"
  echo; say "RESULT" "FAIL — kernel down. Try: PORT=8088 arifos-mcp streamable-http"
  exit 3
fi
FLOORS=$(echo "$H" | jq -r '.floors_measured // .floor_coverage // "n/a"' 2>/dev/null)
record "health" "PASS" "200" 0 "kernel alive · floors measured: $FLOORS"

# ── Stage 1: init ────────────────────────────────────────────────────────────
call arif_init "{\"intent\":\"aaa_speedrun $TS\",\"actor_id\":\"$ACTOR\"}"
B="$BODY"
V=$(classify "$B" "$RC")
SID=$(echo "$B" | jq -r '.result.session_id // empty' 2>/dev/null)
TOK=$(echo "$B" | jq -r '.result.session_token // empty' 2>/dev/null)
BAND=$(echo "$B" | jq -r '.result.authority_band // .result.authority // "?"' 2>/dev/null)
record "init" "$V" "$RC" "$LAT" "session ${SID:-none} · band $BAND"
if [ -z "$SID" ] || [ -z "$TOK" ]; then
  say "RESULT" "FAIL — no session bound; cannot continue the chain"
  exit 3
fi
AUTH="\"session_id\":\"$SID\",\"session_token\":\"$TOK\""

# ── Stage 2: observe (vitals) ────────────────────────────────────────────────
call arif_observe "{\"mode\":\"vitals\",$AUTH}"
B="$BODY"
V=$(classify "$B" "$RC")
LOAD=$(echo "$B" | jq -r '.result.load_1m // .result.vitals.load_1m // "n/a"' 2>/dev/null)
record "observe" "$V" "$RC" "$LAT" "machine vitals measured · load_1m=$LOAD"

# ── Stage 3: think ───────────────────────────────────────────────────────────
call arif_think "{\"query\":\"Derive: why must a governed runtime probe before it claims?\",$AUTH}"
B="$BODY"
V=$(classify "$B" "$RC")
if [ "$V" = "PASS" ]; then
  D="reasoning chain returned"
else
  D=$(echo "$B" | jq -r '.gate_reasons[0] // "reasoning unavailable (load or gate)"' 2>/dev/null | cut -c1-56)
fi
record "think" "$V" "$RC" "$LAT" "$D"

# ── Stage 4: route ───────────────────────────────────────────────────────────
call arif_route "{\"intent\":\"assess portfolio risk\",\"session_id\":\"$SID\",\"session_token\":\"$TOK\"}"
B="$BODY"
V=$(classify "$B" "$RC")
RVD=$(echo "$B" | jq -r '.result.verdict // "?"' 2>/dev/null)
record "route" "$V" "$RC" "$LAT" "intent classified · route verdict: $RVD"

# ── Stage 5: judge — the moment a human FEELS the constitution ───────────────
# A reasoned verdict (SEAL/HOLD/SABAR/VOID) = PASS: the constitution answered.
CAND="Read /root/arifOS/README.md and summarize it (read-only, reversible)"
call arif_judge "{\"candidate\":\"$CAND\",\"action_class\":\"OBSERVE\",\"claim_class\":\"OBS\",\"reversibility_level\":\"reversible\",\"blast_radius\":\"self\",\"session_id\":\"$SID\",\"session_token\":\"$TOK\"}"
B="$BODY"
JVERDICT=$(echo "$B" | jq -r '.result.verdict // .verdict // empty' 2>/dev/null)
GREASON=$(echo "$B" | jq -r '.gate_reasons[0] // .result.hold_reason // ""' 2>/dev/null | cut -c1-56)
case "$JVERDICT" in
  SEAL|HOLD|SABAR|VOID) V="PASS" ;;
  *) V=$(classify "$B" "$RC") ;;
esac
record "judge" "$V" "$RC" "$LAT" "constitution answered: ${JVERDICT:-silence} ${GREASON:+· $GREASON}"

# ── Stage 6: receipt ─────────────────────────────────────────────────────────
NPASS=$(printf '%s\n' "${STAGES[@]}" | grep -c '"verdict":"PASS"' || true)
NDEG=$(printf '%s\n'  "${STAGES[@]}" | grep -c '"verdict":"DEGRADED"' || true)
NFAIL=$(printf '%s\n' "${STAGES[@]}" | grep -c '"verdict":"FAIL"' || true)
if [ "$NFAIL" -eq 0 ] && [ "$NDEG" -eq 0 ]; then OVERALL="PASS"; else OVERALL="DEGRADED"; fi

STAGES_JSON=$(printf '%s\n' "${STAGES[@]}" | jq -s .)
RECEIPT_BODY=$(jq -n \
  --arg ts "$TS" --arg actor "$ACTOR" --arg sid "$SID" \
  --arg base "$BASE" --arg overall "$OVERALL" --argjson stages "$STAGES_JSON" \
  '{speedrun:"aaa_speedrun.v1", ts:$ts, actor:$actor, session:$sid,
    target:$base, overall:$overall,
    seal:"SKIPPED — VAULT999 writes belong to 888_APEX / F13",
    stages:$stages}')
RHASH=$(echo "$RECEIPT_BODY" | sha256sum | awk '{print $1}')
echo "$RECEIPT_BODY" | jq --arg h "$RHASH" '. + {receipt_sha256:$h}' > "$RECEIPT"

hr
echo "TALK TO YOUR CONSTITUTION"
hr
if [ -n "${JVERDICT:-}" ]; then
  echo "You proposed: \"$CAND\""
  echo "The constitution answered: $JVERDICT ${GREASON:+— $GREASON}"
else
  echo "Judge did not answer this run (degraded under load or gate)."
  echo "Re-run when the box cools: bash aaa_speedrun.sh"
fi
hr
say "RESULT" "$OVERALL — pass:$NPASS degraded:$NDEG fail:$NFAIL"
say "RECEIPT" "$RECEIPT"
say "SHA256" "$RHASH"
say "SEAL" "not attempted (888_APEX / F13 only — capability ≠ authority)"
hr

[ "$OVERALL" = "PASS" ] && exit 0 || exit 3
