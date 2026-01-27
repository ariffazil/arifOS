# arifOS v53.1.0 Railway Deployment Guide

**Version**: v53.1.0-CODEBASE
**Architecture**: Hybrid Proxy (Codebase)
**Last Updated**: 2026-01-27
**Status**: Production Ready

---

## Overview

This guide details deploying the **Codebase Microservices** architecture to Railway. This v53 release uses a lightweight SSE server (`codebase/mcp/sse.py`) to bridge external requests to the Constitutional Monolith actions.

---

## 🏗️ Deployment Configuration

### 1. Build Command
Railway auto-detects Python, but ensure dependencies are installed including the local package:
```bash
pip install -r requirements.txt && pip install -e .
```
*(The `-e .` is critical for `codebase` module resolution)*

### 2. Start Command
The entry point has moved from the monolith to the codebase layer:
```bash
python -m codebase.mcp.sse
```

### 3. Environment Variables (Required)

| Variable | Value | Purpose |
| :--- | :--- | :--- |
| `ARIFOS_ENV` | `production` | Production mode |
| `PORT` | `8000` | Railway assigned port |
| `AAA_MCP_TRANSPORT` | `sse` | Enable SSE Transport |
| `ARIFOS_VERSION` | `v53.1.0-CODEBASE` | Version Tag |

**Secrets (Add in Railway Dashboard):**
*   `OPENAI_API_KEY` (for AGI)
*   `ANTHROPIC_API_KEY` (for ASI)
*   `GROQ_API_KEY` (for APEX fast inference)

---

## 📦 Architecture Map

```
[Railway Internet Edge]
       │ (HTTPS /sse)
       ▼
[Codebase MCP Server]  (codebase/mcp/sse.py)
       │
       ▼
[Bridge Layer]         (codebase/mcp/bridge.py)
       │ "Physics/Math/Language" Actions
       ▼
[Kernel Manager]       (codebase/kernel.py)
       │
       ▼
[Constitutional Monolith] (arifos/core/...)
```

---

## 🛡️ Verification Steps

After deployment, verify the health status:

```bash
curl https://your-app.up.railway.app/health
```

**Expected JSON:**
```json
{
  "status": "online",
  "mode": "CODEBASE",
  "transport": "sse",
  "version": "v53.1.0-CODEBASE"
}
```

---

## ⚡ Connecting Clients

### Claude Desktop / Cursor
Use the SSE URL provided by Railway:
```json
{
  "mcpServers": {
    "arifos-railway": {
      "transport": "sse",
      "url": "https://your-app.up.railway.app/sse"
    }
  }
}
```

---
*DITEMPA BUKAN DIBERI*
