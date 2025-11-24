#!/usr/bin/env bash
# Wrapper that runs the ledger verifier and alerts on non-zero exit.
# Configure via environment:
#   VERIFIER=/opt/arifos/scripts/verify_ledger_kms.py
#   LEDGER=/var/log/arifos/cooling_ledger.jsonl
#   ALERT_WEBHOOK=https://hooks.example.com/your/alert
#   ALERT_EMAIL=security@arifos.ai
# Example:
#   VERIFIER=/opt/arifos/scripts/verify_ledger_kms.py LEDGER=/var/log/arifos/cooling_ledger.jsonl ALERT_WEBHOOK=https://mynotify/webhook ./verify_and_alert.sh

set -euo pipefail

VERIFIER="${VERIFIER:-/opt/arifos/scripts/verify_ledger_kms.py}"
LEDGER="${LEDGER:-/var/log/arifos/cooling_ledger.jsonl}"
WEBHOOK="${ALERT_WEBHOOK:-}"
ALERT_EMAIL="${ALERT_EMAIL:-}"
REGION="${AWS_REGION:-}"

# Local verification defaults to false (you can enable by env var)
LOCAL_VERIFY="${LOCAL_VERIFY:-false}"
KEY_CACHE_DIR="${KEY_CACHE_DIR:-/var/cache/arifos/kms-keys}"

ARGS=("$LEDGER")
if [ "${LOCAL_VERIFY}" = "true" ]; then
  ARGS+=("--local-verify" "--key-cache-dir" "${KEY_CACHE_DIR}")
fi
if [ -n "$REGION" ]; then
  ARGS+=("--region" "$REGION")
fi

python3 "$VERIFIER" "${ARGS[@]}"
RC=$?

if [ $RC -ne 0 ]; then
  MESSAGE="Ledger verification failed on $(hostname) for $LEDGER (exit code $RC)"
  echo "$MESSAGE" 1>&2
  if [ -n "$WEBHOOK" ]; then
    # Send JSON payload to webhook (simple)
    curl -sS -X POST -H "Content-Type: application/json" -d "{\"text\": \"${MESSAGE}\"}" "$WEBHOOK" || true
  fi
  if [ -n "$ALERT_EMAIL" ]; then
    # Send simple mail using sendmail if available
    if command -v sendmail >/dev/null 2>&1; then
      printf "Subject: [arifOS] Ledger verification failure\n\n%s\n" "$MESSAGE" | sendmail "$ALERT_EMAIL"
    else
      echo "sendmail not found; cannot send email alert" 1>&2
    fi
  fi
  exit $RC
fi

echo "Ledger verification OK"
exit 0
