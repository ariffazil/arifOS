#!/usr/bin/env bash
# Daily ClamAV scan for arifOS
# Schedule: 03:30 MYT via cron

set -euo pipefail

LOG_DIR="/root/.openclaw/workspace/logs/security"
DATE=$(date +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/clamav-${DATE}.log"
SUMMARY_FILE="${LOG_DIR}/clamav-latest.summary"

mkdir -p "${LOG_DIR}"

echo "=== arifOS ClamAV Scan | ${DATE} $(date +%H:%M:%S) ===" > "${LOG_FILE}"
echo "Scanning /root/.openclaw/workspace ..." >> "${LOG_FILE}"

# Run scan on workspace (infected files only, recursive)
clamscan -r --infected --log="${LOG_FILE}" /root/.openclaw/workspace 2>> "${LOG_FILE}" || true

# Update summary
SCANNED=$(grep "^Scanned files:" "${LOG_FILE}" | tail -1 | cut -d: -f2 | xargs 2>/dev/null || echo "0")
INFECTED=$(grep "^Infected files:" "${LOG_FILE}" | tail -1 | cut -d: -f2 | xargs 2>/dev/null || echo "0")

echo "${DATE} | Scanned: ${SCANNED} | Infected: ${INFECTED}" > "${SUMMARY_FILE}"

if [ "${INFECTED}" != "0" ] && [ "${INFECTED}" != "" ]; then
    echo "⚠️  INFECTED FILES DETECTED: ${INFECTED}" >> "${LOG_FILE}"
    echo "ALERT: Infected files found in workspace" >> "${SUMMARY_FILE}"
fi

echo "=== Scan Complete | $(date +%H:%M:%S) ===" >> "${LOG_FILE}"
