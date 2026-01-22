---
name: Go Online
description: Expose the local arifOS MCP server to the internet via Cloudflare Tunnel
---

# Go Online (AAA MCP)

This skill exposes the local VAULT999 MCP server (`https://localhost:8000`) to the public internet via a secure Cloudflare Tunnel.

## Prerequisites
- **Cloudflare Tunnel Installed**: `cloudflared` available in PATH.
- **Tunnel Configured**: Existing tunnel named `vault999`.
- **Domain Mapped**: `vault999.arif-fazil.com` pointing to tunnel.
- **Local Server Running**: `vault999_server.py` must be active on port 8000.

## Workflow

1.  **Check Local Server**
    Ensure the MCP server is running locally.
    ```powershell
    # Check for port 8000
    Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    ```

2.  **Start Tunnel**
    Run the tunnel connector.
    ```powershell
    cloudflared tunnel run vault999
    ```

## Verification

- **URL**: `https://vault999.arif-fazil.com`
- **Check**: Visit `https://vault999.arif-fazil.com/sse`
    - **Success**: 404 Not Found (Server reached, endpoint valid) or "Method Not Allowed".
    - **Failure**: "Bad Gateway" (Local server down) or "Connection Refused".

## AAA Alignment Note
- **Exposed**: `VAULT999` (Machine Law) is PUBLIC.
- **Protected**: `ARIF FAZIL` (Human Biography) is OFFLINE (Code-gated).
- **Access**: READ tools are public; WRITE tools require `human_seal_token`.
