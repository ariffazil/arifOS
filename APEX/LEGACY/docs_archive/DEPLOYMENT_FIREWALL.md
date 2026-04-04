# arifOS VPS Firewall Configuration

This document outlines the firewall configuration for the arifOS deployment on this VPS, managed by `ufw` (Uncomplicated Firewall).

## Policy

The firewall operates on a principle of "default deny". All incoming traffic is blocked by default, and only explicitly allowed services are accessible from the outside.

## Rules

| Port | Protocol | Service | Action | From      |
|------|----------|---------|--------|-----------|
| 22   | TCP      | SSH     | ALLOW  | Anywhere  |
| 80   | TCP      | HTTP    | ALLOW  | Anywhere  |
| 443  | TCP      | HTTPS   | ALLOW  | Anywhere  |

## Service Accessibility

*   **SSH (Port 22):** Open to the world to allow for administrative access and for the CI/CD pipeline (via GitHub Actions) to trigger deployments. Access is secured by SSH keys.
*   **HTTP/HTTPS (Ports 80/443):** Open to the world to allow access to any web services, such as a potential web UI or API gateway that might be reverse-proxied.
*   **arifOS MCP Server:** The core MCP server runs as a `systemd` service and binds to `localhost` by default. It is **not** directly exposed to the internet. Access is only possible from within the VPS itself or through an SSH tunnel.

## Commands

*   **Check status:** `sudo ufw status`
*   **Disable firewall:** `sudo ufw disable`
*   **Enable firewall:** `sudo ufw enable`
