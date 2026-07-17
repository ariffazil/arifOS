# arifOS — Constitutional AI Governance Kernel

> **Constitutional execution gate for AI agents.**
> Verifies identity, evidence, authority and reversibility before tools may mutate the world.

## What arifOS does

arifOS sits between your AI agent and its tools. Before any write, delete, deploy, transfer, or publish action, arifOS checks:

- **Identity** — who is this agent?
- **Evidence** — what supports this action?
- **Authority** — is this action authorized?
- **Reversibility** — can it be undone?

Result: **SEAL** (proceed), **HOLD** (need more evidence/approval), **VOID** (blocked).

## Quick Start

```bash
npm install arifos
# Then install the Python kernel:
pip install arifos
```

## Connect

Add to your MCP client config:

```json
{
  "mcpServers": {
    "arifos": {
      "type": "streamable-http",
      "url": "https://mcp.arif-fazil.com/mcp"
    }
  }
}
```

## MCP Registries

| Registry | Link |
|----------|------|
| Glama | https://glama.ai/mcp/servers/ariffazil/arifos |
| PulseMCP | https://pulsemcp.com/servers/ariffazil-arifos |
| Smithery | https://smithery.ai/server/arifos |
| mcp.so | https://mcp.so/server/arifos |

## License

AGPL-3.0 — DITEMPA BUKAN DIBERI
