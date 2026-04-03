# arifOS Horizon Gateway

> Deprecated as a deployment entrypoint reference. The canonical public entrypoint is `server.py:mcp`.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REQUEST                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────────┐
│  ☁️ Horizon     │ │ 🔥 VPS   │ │ 💻 Local        │
│  (Gateway)      │ │ (Execution)│ │ (STDIO)       │
├─────────────────┤ ├──────────┤ ├─────────────────┤
│ Public tools    │ │ Full toolset│ │ Full toolset │
│ Gateway policy  │ │ Sovereign   │ │ Development  │
│ Auto-scale      │ │ execution   │ │ Direct access│
│ Public ingress  │ │ Stateful ops│ │              │
└─────────────────┘ └──────────┘ └─────────────────┘
```

## Canonical Deployment Rule

- Deploy Horizon with `server.py:mcp`
- Treat `horizon/server.py` as deprecated compatibility only
- Use the Horizon gateway policy to distinguish:
  - `public`
  - `authenticated`
  - `sovereign-only`

## Deploy to Horizon

1. Push this repo to GitHub
2. Go to https://horizon.prefect.io
3. Connect this repository
4. Set entrypoint: `server.py:mcp`
5. Deploy

## Connecting to Sovereign Kernel

The Horizon gateway proxies public-safe tools to the VPS and advertises the
full unified contract via gateway policy metadata.

```python
# Set in Horizon dashboard
ARIFOS_VPS_URL=https://arifosmcp.arif-fazil.com
ARIFOS_GOVERNANCE_SECRET=your_key
```

---

**arifOS Trinity**: 🔥 VPS | ☁️ Horizon | 💻 Local

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
