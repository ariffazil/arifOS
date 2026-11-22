# @arifos/mcp

**Thin JavaScript/TypeScript MCP client for the arifOS governance kernel.**

```text
PyPI (`pip install arifos`) ships the kernel.
npm  (`npm install @arifos/mcp`) ships the JavaScript cable.
MCP  is the language through the cable.
The endpoint (`https://mcp.arif-fazil.com/mcp`) is the address of a running kernel.
arifOS judges; this client carries ZERO independent constitutional authority.
```

> **Choose the right tool first:**
> - **Just want to try arifOS?** Connect your MCP client directly to `https://mcp.arif-fazil.com/mcp` — no Python or Node.js installation required.
> - **Want to run your own kernel?** Install the Python package: `pip install arifos` ([PyPI](https://pypi.org/project/arifos/)).
> - **Building a JavaScript or TypeScript app?** Install `@arifos/mcp` to talk to a running kernel (hosted or self-hosted).

---

## Installation

```bash
npm install @arifos/mcp
```

Requires Node.js >= 18. Installing this package does **not** start a kernel, run background services, or evaluate constitutional floors locally.

---

## Quick Start

### Connect to the hosted kernel (Streamable HTTP)

```typescript
import { createClient, ENDPOINTS } from "@arifos/mcp";

const client = await createClient({
  transport: "http",
  endpoint: ENDPOINTS.MCP, // https://mcp.arif-fazil.com/mcp
});

await client.connect();

// 1. Discover the live wire tools (8 canonical verbs + arif_report)
const tools = await client.listTools();
console.log(tools.map((t) => t.name));

// 2. Ignite a governed session (000)
const session = await client.init({
  intent: "Check whether a refund action is permitted",
  actor_id: "my-ts-app",
});

// 3. Request a constitutional verdict (666)
const verdict = await client.judge({
  candidate: "Issue RM5000 customer refund without human approval",
  action_tier: "T3",
});

console.log(session.session_id, verdict.verdict);
await client.disconnect();
```

### Connect to a local self-hosted kernel (stdio)

Requires `pip install arifos` so the `arifos-mcp` binary is available on `PATH`:

```typescript
import { quickConnect } from "@arifos/mcp";

const client = await quickConnect.local();
await client.connect();
const tools = await client.listTools();
await client.disconnect();
```

---

## Live Wire Contract (9 tools = 8 canonical verbs + `arif_report`)

| Tool | Stage | Purpose |
| :--- | :--- | :--- |
| `arif_init` | `000_INIT` | Start or resume a governed session |
| `arif_observe` | `111_OBSERVE` | Collect labeled evidence (`OBS`/`DER`/`INT`/`SPEC`) |
| `arif_think` | `333_THINK` | Structured reasoning under F2/F7 |
| `arif_route` | `444_ROUTE` | Route intent to the right organ or next step |
| `arif_memory` | `555_MEMORY` | Recall, store, or promote governed memory |
| `arif_judge` | `666_JUDGE` | Evaluate a proposed action against F1–F13 |
| `arif_forge` | `777_FORGE` | Execute an approved action (requires a prior `SEAL`) |
| `arif_seal` | `999_SEAL` | Record an auditable receipt in VAULT999 |
| `arif_report` | `REPORT` | File, read, or acknowledge operational reports |

Always treat live `tools/list` on the connected kernel as authoritative over static documentation.

---

## Architecture & Authority Boundary

```text
JavaScript / TypeScript application
           |
           | @arifos/mcp (transport + types only)
           v
Running arifOS Python kernel (`pip install arifos` or https://mcp.arif-fazil.com/mcp)
           |
           v
Verdict (SEAL / PROVISIONAL / PARTIAL / SABAR / HOLD / HOLD_888 / VOID) + receipt
```

- `AuthorityEnvelope` and `ReceiptRecord` types are **transparent payload mirrors** only.
- Presenting a token or authority field in TypeScript does **not** grant authority; the Python kernel verifies and decides.
- To remove this package cleanly: `npm uninstall @arifos/mcp`.

---

## Links

- **Authoritative Kernel (PyPI):** <https://pypi.org/project/arifos/>
- **Source & Evidence (GitHub):** <https://github.com/ariffazil/arifOS>
- **Hosted MCP Endpoint:** `https://mcp.arif-fazil.com/mcp`
- **Public Health:** <https://mcp.arif-fazil.com/health>

## License

AGPL-3.0-only — *DITEMPA BUKAN DIBERI*
