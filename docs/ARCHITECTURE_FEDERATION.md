# arifOS Federation — Plain-English Topology

> **One sentence:** The arifOS federation is a team of specialized AI services that work like a government: one makes the law (arifOS), one runs the front desk (AAA), one executes the work (A-FORGE), and others provide expert evidence (GEOX, WEALTH, WELL).

---

## The Analogy: City Hall

Imagine you want to build a factory. You don't go to one person who does everything. You go through a chain:

1. **Law Office (arifOS)** — Checks if building a factory is legal, safe, and reversible. Issues a permit (SEAL) or blocks it (VOID).
2. **Front Desk (AAA)** — Takes your application, shows you forms, and routes you to the right department.
3. **Construction Crew (A-FORGE)** — Actually builds the factory, but only after the Law Office approves.
4. **Experts (GEOX, WEALTH, WELL)** — Provide specialized reports: soil stability, budget impact, public health readiness.

In software terms, this means:

| Service | Role | Plain English |
|---------|------|---------------|
| **arifOS** | LAW | Decides what's allowed, held, or void. Every tool call passes through here first. |
| **AAA** | INTERFACE | Human cockpit + A2A agent gateway. The front desk you interact with. |
| **A-FORGE** | EXECUTION | Runs governed agent workloads. The worker that carries out approved actions. |
| **GEOX** | FIELD | Earth-science evidence engine. Provides geological, environmental, and spatial data. |
| **WEALTH** | CAPITAL | Financial / capital evidence engine. Provides economic modeling and budget analysis. |
| **WELL** | HUMAN | Human readiness evidence engine. Provides health, wellness, and biological state data. |

---

## How Data Flows

```
User or Agent
    │
    ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│   AAA   │──→│  arifOS │──→│ A-FORGE │
│ (front) │   │  (law)  │   │ (work)  │
└─────────┘   └────┬────┘   └─────────┘
                   │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      GEOX     WEALTH     WELL
     (field)  (capital)  (human)
```

1. **AAA** receives the request and formats it.
2. **arifOS** evaluates the request against F1–F13 floors.
3. If arifOS needs evidence, it calls **GEOX**, **WEALTH**, or **WELL**.
4. arifOS issues a verdict: **SEAL** (proceed), **HOLD** (ask human), or **VOID** (block).
5. Only if **SEAL** is issued does **A-FORGE** execute the action.
6. The result is logged in **VAULT999** — an immutable audit trail.

---

## Do I Need All of Them?

**No.** arifOS is the only required piece. The others are optional evidence providers:

- Running **arifOS alone** gives you constitutional guardrails (F1–F13) and audit logging.
- Add **AAA** if you want a web UI or A2A agent gateway.
- Add **A-FORGE** if you want a separate execution cluster.
- Add **GEOX / WEALTH / WELL** only if your use case needs earth-science, financial, or biological evidence.

---

## Integration Points

- **MCP (Model Context Protocol):** arifOS exposes its 13 tools as an MCP server. Any MCP client (Claude Desktop, Cursor, etc.) can connect.
- **A2A (Agent-to-Agent):** arifOS can route requests to and from other agents in the federation via the AAA gateway.
- **HTTP REST:** Direct API calls to `mcp.arif-fazil.com/mcp` or your self-hosted instance.

---

## Further Reading

- [MCP Specification](https://modelcontextprotocol.io)
- [AAA Repository](https://github.com/ariffazil/AAA)
- [A-FORGE Repository](https://github.com/ariffazil/A-FORGE)
- [GEOX Repository](https://github.com/ariffazil/geox)
- [WEALTH Repository](https://github.com/ariffazil/wealth)
