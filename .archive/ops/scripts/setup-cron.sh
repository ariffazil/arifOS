#!/bin/bash
# Setup cron jobs for arifOS monitoring
set -e

CRON_TMP="/tmp/arifos_cron"

# Backup current crontab
crontab -l > "$CRON_TMP" 2>/dev/null || true

# Remove existing arifOS cron entries
sed -i '/arifOS/d' "$CRON_TMP" 2>/dev/null || true

# Add new entries
echo "# arifOS monitoring" >> "$CRON_TMP"
echo "0 2 * * * /root/arifOS/scripts/backup-data.sh >> /root/arifOS/data/backup.log 2>&1" >> "$CRON_TMP"
echo "*/5 * * * * /root/arifOS/scripts/health-check.sh >> /root/arifOS/data/healthcheck.log 2>&1" >> "$CRON_TMP"

# Install new crontab
crontab "$CRON_TMP"
rm -f "$CRON_TMP"

echo "Cron jobs installed."
