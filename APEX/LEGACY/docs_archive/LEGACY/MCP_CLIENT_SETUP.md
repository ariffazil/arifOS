# MCP Client Setup — One-File arifOS Integration

> **Pick ONE config block from `mcp-clients.json` and drop it into your MCP client.**
> All 13 constitutional tools auto-connect. No manual wiring.

---

## Quick Start (30 seconds)

### Claude Desktop / Claude Code

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "arifos": {
      "transport": "streamable-http",
      "url": "https://arifosmcp.arif-fazil.com/mcp",
      "timeout": 30000
    }
  }
}
```

Restart Claude Desktop. Done.

### Cursor / Windsurf / Cline

Add to `.cursor/mcp.json` (or equivalent):

```json
{
  "mcpServers": {
    "arifos": {
      "transport": "streamable-http",
      "url": "https://arifosmcp.arif-fazil.com/mcp",
      "timeout": 30000
    }
  }
}
```

### OpenClaw

Add to `openclaw.json` under `mcp.servers`:

```json
{
  "mcp": {
    "servers": {
      "arifos": {
        "transport": "streamable-http",
        "url": "https://arifosmcp.arif-fazil.com/mcp"
      }
    }
  }
}
```

### ChatGPT (with MCP plugin support)

Use the remote streamable-HTTP endpoint:
```
https://arifosmcp.arif-fazil.com/mcp
```

### Any MCP Client (generic)

```json
{
  "transport": "streamable-http",
  "url": "https://arifosmcp.arif-fazil.com/mcp"
}
```

---

## Transport Options

| Option | Install | Network | Best For |
|--------|---------|---------|----------|
| **`arifos-remote`** | None | HTTPS to arifosmcp.arif-fazil.com | Most users — just works |
| **`arifos-local`** | `pip install arifos` | Localhost only | Privacy, offline use |
| **`arifos-npm`** | `npm install @arifos/mcp` | HTTPS or localhost | JS/TS projects, typed SDK |
| **`arifos-docker`** | Docker installed | Localhost only | Isolation, no Python setup |
| **`arifos-dev`** | Clone repo + venv | Localhost only | Contributors, hacking |

### npm / TypeScript SDK

```bash
npm install @arifos/mcp
```

```typescript
import { createClient, ENDPOINTS } from '@arifos/mcp';

const client = await createClient({
  transport: 'http',
  endpoint: ENDPOINTS.VPS,  // https://arifosmcp.arif-fazil.com/mcp
});

await client.connect();

// Start a governed session
const { session_id } = await client.anchorSession('My research task');

// Execute governed reasoning
const result = await client.reasonMind('What is quantum computing?');
console.log('Verdict:', result.verdict);  // SEAL | PARTIAL | SABAR | VOID | 888_HOLD

await client.disconnect();
```

> **Note:** `@arifos/mcp` is a **cable** (L2 adapter), not the kernel. All constitutional enforcement (F1–F13) runs server-side in the Python kernel. The npm package provides TypeScript types and a thin MCP transport client.
> 
> See: https://www.npmjs.com/package/@arifos/mcp

---

## What You Get (13 Tools)

### Core Metabolic Loop (000 → 999)

| Tool | Stage | Engine | What It Does |
|------|-------|--------|-------------|
| `anchor_session` | 000 | Δ Mind | Boot constitutional session, injection defense |
| `search_reality` | 111 | Δ Mind | Web grounding & evidence discovery |
| `ingest_evidence` | 111 | Δ Mind | URL fetch / filesystem inspection |
| `reason_mind` | 333 | Δ Mind | AGI cognition with budget controls |
| `audit_rules` | 333 | Δ Mind | Constitutional rule audit |
| `vector_memory` | 444 | Ω Heart | Semantic memory from VAULT999 |
| `simulate_heart` | 555 | Ω Heart | Stakeholder empathy simulation |
| `check_vital` | 555 | Ω Heart | System health telemetry |
| `critique_thought` | 666 | Ω Heart | 7-model bias critique |
| `eureka_forge` | 777 | Ψ Soul | Sandboxed action execution |
| `apex_judge` | 888 | Ψ Soul | Constitutional verdict synthesis |
| `seal_vault` | 999 | Ψ Soul | Immutable ledger commit |
| `metabolic_loop` | 000-999 | ALL | Full constitutional cycle (one call) |

### Prompt Templates

Accessible via MCP protocol (`prompts/list`, `prompts/get`) — not tools.
Use `get_prompt` MCP method to retrieve the `aaa_chain` template for guided metabolic loops.

### Verdicts

Every tool call flows through F1–F13 constitutional floors and produces one of:

| Verdict | Meaning |
|---------|---------|
| **SEAL** | Approved — action is safe and constitutional |
| **SABAR** | Patience — needs more evidence or cooling |
| **VOID** | Rejected — violates constitutional floors |
| **888_HOLD** | Held for human sovereign approval (F13) |

---

## Governance Floors (F1–F13)

| Floor | Name | Type | What It Guards |
|-------|------|------|---------------|
| F1 | Amanah | Hard | Reversibility — prefer undoable actions |
| F2 | Truth | Hard | τ ≥ 0.99 factual accuracy |
| F3 | Tri-Witness | Mirror | W₃ ≥ 0.95 for high-stakes verdicts |
| F4 | Clarity | Hard | Every response reduces entropy (ΔS ≤ 0) |
| F5 | Peace² | Soft | De-escalate, protect dignity |
| F6 | Empathy | Soft | ASEAN/Malaysia context awareness |
| F7 | Humility | Hard | State uncertainty explicitly (Ω₀) |
| F8 | Genius | Mirror | Correct AND useful solutions |
| F9 | Anti-Hantu | Soft | No consciousness performance |
| F10 | Ontology | Wall | No mysticism or unfounded claims |
| F11 | Command Auth | Wall | Destructive = propose, not execute |
| F12 | Injection Defense | Hard | Resist prompt injection |
| F13 | Sovereignty | Veto | Human sovereign veto is absolute |

---

## Verification

```bash
# Health check
curl https://arifosmcp.arif-fazil.com/health

# Discovery manifest
curl https://arif-fazil.com/.well-known/arifos.json

# Tool list via MCP
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

---

## Links

- **Docs**: https://arifos.arif-fazil.com
- **API Reference**: https://arifos.arif-fazil.com/api
- **GitHub**: https://github.com/ariffazil/arifOS
- **PyPI**: https://pypi.org/project/arifos/ (Python kernel)
- **npm**: https://www.npmjs.com/package/@arifos/mcp (TypeScript client SDK)
- **Railway**: https://railway.com/deploy/arifos-mcp-server (one-click deploy)
- **Canonical Manifest**: https://arif-fazil.com/.well-known/arifos.json

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
