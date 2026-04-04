# arifOS Rollback Playbook

This document provides the steps to roll back the arifOS application to the last known-good state on the VPS.

## When to Roll Back

A rollback is necessary if a deployment fails and the application is left in a non-functional state. Indications of a failed deployment include:
- The `deploy.sh` script exits with an error.
- The `health-check.sh` script fails after a deployment.
- The `arifos-mcp.service` is not running or is in a `failed` state (`systemctl status arifos-mcp.service`).
- The application is throwing critical errors in the logs (`journalctl -u arifos-mcp.service -f`).

## How to Roll Back

A one-command rollback script is provided to automate the process.

### Step 1: Connect to the VPS

SSH into the arifOS server.

```bash
ssh root@<your_vps_ip>
```

### Step 2: Run the Rollback Script

Execute the `rollback.sh` script.

```bash
/opt/arifOS/rollback.sh
```

The script will:
1.  Ask for confirmation after identifying the most recent backup to use.
2.  Stop the application.
3.  Delete the current (broken) deployment.
4.  Restore the application files from the backup.
5.  Re-create the Python virtual environment and install all dependencies.
6.  Restart the application.
7.  Run a health check to confirm the rollback was successful.

### Step 3: Verify the Rollback

The script runs a health check automatically, but you should also manually verify that the application is functioning as expected.

```bash
# Check service status
systemctl status arifos-mcp.service

# Check logs
journalctl -u arifos-mcp.service -f --no-pager
```

## Manual Rollback (Emergency Only)

If the `rollback.sh` script fails for any reason, you can perform the steps manually.

1.  **Stop the service:** `sudo systemctl stop arifos-mcp.service`
2.  **Find the latest backup:** `ls -t /opt/backups/arifos_backup_*.tar.gz | head -n 1`
3.  **Remove the broken deployment:** `rm -rf /opt/arifOS`
4.  **Extract the backup:** `tar -xzvf /opt/backups/<backup_filename.tar.gz> -C /opt`
5.  **Rebuild the environment:**
    ```bash
    cd /opt/arifOS
    python3 -m venv .venv
    source .venv/bin/activate
    pip install uv
    uv pip install -e ".[all]"
    uv pip install "redis>=5.0.0" "pytest-benchmark"
    ```
6.  **Restart the service:** `sudo systemctl start arifos-mcp.service`
