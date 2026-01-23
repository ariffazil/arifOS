# arifOS Operations: Ledger verification (staging & scheduled audits)

This page documents how to run automated ledger verification in staging and via CI.

## Systemd (recommended for modern Linux)

1. Place scripts in `/opt/arifos/scripts/`:
   - `verify_ledger_kms.py`
   - `verify_and_alert.sh`

2. Create an environment file `/etc/default/arifos-verify`:
```
ARIFOS_KMS_ENABLED=true
ARIFOS_KMS_KEY_ID=arn:aws:kms:ap-southeast-1:123:...:key/...
AWS_REGION=ap-southeast-1
VERIFIER=/opt/arifos/scripts/verify_ledger_kms.py
LEDGER=/var/log/arifos/cooling_ledger.jsonl
ALERT_WEBHOOK=https://hooks.example.com/team-alert
ALERT_EMAIL=security@arifos.ai
LOCAL_VERIFY=true
KEY_CACHE_DIR=/var/cache/arifos/kms-keys
```

3. Install units:
   - `/etc/systemd/system/verify_ledger.service` (see repo/systemd/verify_ledger.service)
   - `/etc/systemd/system/verify_ledger.timer` (see repo/systemd/verify_ledger.timer)

4. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now verify_ledger.timer
sudo systemctl start verify_ledger.service  # test once
```

## Cron example

If you prefer cron, drop `/etc/cron.d/verify_ledger` (see docs/cron/verify_ledger.cron) and make sure `verify_and_alert.sh` is executable.

## GitHub Actions scheduled audit

We include a workflow that runs weekly and downloads a ledger snapshot artifact (artifact name: `ledger-snapshot`) and runs the verification script. On failure it opens a GitHub issue labeled `security, automated-audit`.

To enable:
- Ensure artifacts are produced (pipeline that uploads `ledger-snapshot`).
- Optionally commit a pre-seeded `artifacts/kms-keys` cache for local verification, or set up secrets for AWS access.

## Key caching & rotation

- Cached public keys live in `/var/cache/arifos/kms-keys` (or configured KEY_CACHE_DIR).
- Cache TTL defaults to 7 days; you can force-refresh with the `--force-refresh-keys` flag.
- For rotation, new ledger entries should include their `kms_key_id`. The verification script will load the appropriate public key (from cache or via `GetPublicKey`) and validate entries signed by historic keys.

## Alerts & integration

- The wrapper supports webhook (ALERT_WEBHOOK) and simple email (sendmail) alerts.
- For production, replace the webhook/email with your pager/alerting integration (PagerDuty, Opsgenie, Slack with alert routing).
