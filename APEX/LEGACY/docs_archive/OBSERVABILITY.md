# arifOS Observability Guide

This document explains how to monitor the health and status of the arifOS deployment on this VPS.

## 1. Process-Level Health (systemd)

The arifOS application is managed by `systemd`, which handles process supervision, automatic restarts, and logging.

### Checking Service Status

To check if the main `arifos-router` service is running, use `systemctl`:

```bash
sudo systemctl status arifos-router.service
```

A healthy service will show as `active (running)`.

### Process Health Check Script

A dedicated script is provided to check the service status, suitable for automation and CI/CD pipelines.

```bash
/opt/arifOS/health-check.sh
```

This script will exit with a code `0` if the service is active, and `1` if it is not.

## 2. Application-Level Health (HTTP Endpoint)

The `arifos-router` provides a simple HTTP health endpoint for external probes and monitoring tools.

*   **URL:** `http://localhost:8080/health`
*   **Method:** `GET`

A successful `200 OK` response with `{"status": "healthy"}` indicates that the web server is running.

### How to Check

You can use `curl` from within the VPS to check the endpoint:

```bash
curl http://localhost:8080/health
```

## 3. Logging (journald)

All output (both `stdout` and `stderr`) from the `arifos-router` and its backend subprocesses (`aaa_mcp`, `aclip_cai`) is captured by `journald`.

### Viewing Logs

To view the logs in real-time (live tail):

```bash
journalctl -u arifos-router.service -f
```

To view the last 100 lines:

```bash
journalctl -u arifos-router.service --lines=100 --no-pager
```

To filter logs for specific errors or keywords:

```bash
journalctl -u arifos-router.service | grep "ERROR"
```

## 4. Metrics (Prometheus)

The `arifOS` application includes the `prometheus-client` library, but no specific metrics are exposed by default in the current configuration.

To add custom metrics, you can use the `@mcp.custom_route` decorator in `arifos_router.py` to create a `/metrics` endpoint and use the `prometheus_client` library to render the metrics in the appropriate format.
