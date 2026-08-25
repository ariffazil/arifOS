<!-- SOT-MANIFEST
federation_release: v2026.08.19
last_verified: 2026-08-19T00:00:00Z
live_commit: 36f291ef1 (fix(deps): pin langgraph upper bound for supply-chain sovereignty)
tools_exposed_via_mcp: 8 (canonical public verbs — KERNEL_ABI_8)
total_declared_tools: 48 (includes diagnostics, internal modes, aliases)
resources: 34 · prompts: 13
floors_registered: 13 (F1–F13)
federation_schema: 2.0.0
organs: 7 (arifOS:8088, A-FORGE:7072, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083, arifFlow:7073)
truth_rule: live :8088/health + tools/list beat any static count in prose
canonical_stations: tools_sot.yaml + constitutional_map.py (SOT)
generated_marker: this file is hand-maintained; canonical verb table sourced from tools_sot.yaml
-->

# arifOS

**A constitutional control plane for AI agents.**

arifOS evaluates identity, evidence, authority, risk, and reversibility
before an AI agent may execute a consequential action.

It does not execute actions itself. It returns an auditable verdict:

- **SEAL** — authorized under stated conditions
- **HOLD** — insufficient evidence or human approval required
- **SABAR** — proceed cautiously, partial authorization
- **VOID** — blocked by a constitutional floor

[Try the safe demo](#-quickstart) ·
[Connect through MCP](#-mcp-surface) ·
[Read the constitution](./GENESIS/000_KERNEL_CANON.md) ·
[Documentation](./docs/)

> **The agent that acts is not allowed to certify its own action.**
>
> DITEMPA BUKAN DIBERI. Forged, Not Given.

---

## What arifOS does

arifOS is a [Model Context Protocol](https://modelcontextprotocol.io) server that sits between an AI agent's intent and the action it wants to take. It enforces 13 constitutional floors — non-negotiable rules about truth, reversibility, humility, auditability, and human authority.

When an agent calls `arif_init`, arifOS binds a session, activates the floors, and routes the agent through a governed loop: observe evidence, think under constraints, dispatch to the right organ, recall governed memory, receive a constitutional verdict, execute (if authorized), and seal the result.

When an agent's evidence is thin, risk is high, or an irreversible action is proposed — arifOS returns **HOLD**. A HOLD is not a failure. It is a fence.

**What arifOS does not do:**
- It does not execute actions (A-FORGE executes; arifOS judges).
- It does not wrap an LLM (it governs any agent that speaks MCP).
- It does not replace human judgment (F13 = human veto is final).

---

## The 8 canonical verbs

arifOS exposes 8 verbs on its public MCP surface. Each verb corresponds to a station in the 000–999 authority ladder.

| Station | Verb | What it does |
|---|---|---|
| 000 | `arif_init` | Bind session, activate floors, mint token |
| 111 | `arif_observe` | Sense reality — search, fetch, vitals, entropy |
| 333 | `arif_think` | Structured reasoning under F2/F7 constraints |
| 444 | `arif_route` | Dispatch intent to the correct organ |
| 555 | `arif_memory` | Governed recall, store, revise (L1–L6) |
| 666 | `arif_judge` | Constitutional verdict: SEAL / HOLD / SABAR / VOID |
| 777 | `arif_forge` | Governed execution (post-SEAL, lease-gated) |
| 999 | `arif_seal` | Immutable append to VAULT999 ledger |

> Canonical stage assignments live in [`tools_sot.yaml`](./tools_sot.yaml), sourced from [`constitutional_map.py`](./arifosmcp/constitutional_map.py). If prose and code disagree, code wins.

---

## The 13 constitutional floors (F1–F13)

These are checked on every governed action. They are the physics of the kernel.

| Floor | Name | Essence |
|---|---|---|
| F1 | AMANAH | Reversible-first. Irreversible → 888_HOLD |
| F2 | TRUTH | Every claim carries evidence (OBS/DER/INT/SPEC) |
| F3 | TRI-WITNESS | Human × AI × Earth × Verifier ≥ 0.75 |
| F4 | CLARITY | ΔS ≤ 0 — every output reduces entropy |
| F5 | PEACE² | Non-destructive power |
| F6 | EMPATHY | Protect the weakest stakeholder |
| F7 | HUMILITY | Confidence cap 0.90. Ω₀ ∈ [0.03, 0.05] |
| F8 | GENIUS | G ≥ 0.80 for complex actions |
| F9 | ANTIHANTU | No deception, no consciousness claims |
| F10 | ONTOLOGY | AI-only ontology. Soul = VOID |
| F11 | AUDITABILITY | Every decision logged, attributable |
| F12 | RESILIENCE | Injection defense |
| F13 | SOVEREIGN | Human veto FINAL |

Full floor definitions: [`GENESIS/FLOOR_TABLE.json`](./GENESIS/FLOOR_TABLE.json) · [`GENESIS/000_KERNEL_CANON.md`](./GENESIS/000_KERNEL_CANON.md) §3

---

## Architecture: two loops

```
  INNER LOOP (deliberation)          OUTER LOOP (actuation)
  ─────────────────────────          ──────────────────────
  init → observe → think             forge (post-SEAL)
       → route → memory                  → verify
       → judge → verdict                  → seal to VAULT999
                                            → FQ metabolic pulse
```

The doer is never the judge. `caller == target → HOLD`. This is the Gödel Lock — a separation-of-duties rule inspired by Gödel's incompleteness: the reference for certifying an action cannot be a member of the system that performs it (**R ∉ S**).

ASCII map:

```
  👑 F13 Sovereign (Arif) — human veto, final
           │
  ┌────────▼────────────┐    verdict    ┌─────────────────┐
  │  arifOS Kernel :8088│──── SEAL ───▶│  A-FORGE :7072   │
  │  F1–F13 always on   │              │  execution only  │
  │                     │──── HOLD ──▶ 🧍 human gate      │
  └──┬──────────┬───────┘              └───────┬─────────┘
     │ query    │ evidence                     │
     ▼          ▼                              ▼
  ┌──────┐ ┌──────┐ ┌──────┐          ┌────────────┐
  │ GEOX │ │WEALTH│ │ WELL │          │ arifFlow   │
  │:8081 │ │:18082│ │:18083│          │ :7073 (FQ) │
  └──────┘ └──────┘ └──────┘          └────────────┘
```

---

## Quickstart

**For humans — try it in under a minute:**

```bash
# 1. Check health
curl -sf https://mcp.arif-fazil.com/health | jq '{status, floors_active}'

# 2. List the 8 canonical tools (stateless MCP wire)
curl -sS -X POST 'https://mcp.arif-fazil.com/mcp' \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: tools/list' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

**For agents — the golden path:**

```
arif_init → arif_observe → arif_think → arif_route →
arif_memory → arif_judge → arif_forge → arif_seal
```

Always start with `arif_init`. No session = no mutation. Expect HOLDs — they are fences, not failures.

**Reading a verdict:**
- **SEAL** — authorized. Execute, then seal receipt to VAULT999.
- **HOLD** — pause. Evidence insufficient or human approval required.
- **SABAR** — proceed cautiously under partial authorization.
- **VOID** — blocked. Hard floor violation.

---

## MCP surface

The public wire exposes 8 canonical verbs, stateless-first (MCP `2026-07-28`).

| Surface | Count |
|---|---|
| Tools | 8 canonical verbs |
| Resources | 34 |
| Prompts | 13 |

Full tool schemas, resource URIs, and prompt templates are discoverable via standard MCP `tools/list`, `resources/list`, and `prompts/list` calls.

---

## VAULT999

Every irreversible decision appends to an append-only, hash-chained ledger. Properties:

- **Append-only** — `chattr +a`; Merkle anchor every 100 receipts
- **Cross-organ receipts** — WEALTH, WELL, A-FORGE all write witness receipts
- **Seal chain health** — live at `/health` → `vault999_health`

The chain is the federation's memory that survives agent death.

---

## For developers

**Connect your MCP client:**
```
Endpoint: https://mcp.arif-fazil.com/mcp
Protocol: MCP 2026-07-28 (stateless)
Auth: varies by verb (see access classification below)
```

**Safe destructive-action demo:**
```bash
# This will return HOLD — the kernel refuses to execute
# without a valid session and evidence
# tools/call arif_forge {mode: "engineer", manifest: "delete all production data"}
# Expected: HOLD (no session, no evidence, irreversible)
```

A HOLD is your best demo — it proves the gate works.

---

## For agents — machine contract

Boot via `arif_init`. Required first verb. No session = no mutation.

| Access class | Verb |
|---|---|
| **discoverable** (public surface) | all 8 verbs |
| **anonymous** (no session needed) | `arif_init` |
| **session-bound** | `arif_observe`, `arif_think`, `arif_route`, `arif_memory` |
| **authenticated** | `arif_judge`, `arif_forge`, `arif_seal` |

HOLD handling: retry with better evidence, not the same payload.
Idempotency: `arif_init` is idempotent with `idempotency_key`.
Irreversible actions: require `ack_irreversible: true` + 888_HOLD + F13 ack.

Machine-readable surfaces:
- `/.well-known/mcp/server.json` — MCP server metadata
- `/llms.txt` — LLM-readable summary
- `/tools` — public tool inventory with access classification
- [`AGENT_BOOTSTRAP.md`](./AGENT_BOOTSTRAP.md) — full machine contract

---

## Federation

| Organ | Port | Role |
|---|---|---|
| arifOS | 8088 | Constitutional kernel (this repo) |
| A-FORGE | 7072 | Governed execution |
| AAA | 3001 | DISPLAY_ONLY cockpit + A2A gateway (never judges, never executes) |
| GEOX | 8081 | Earth intelligence |
| WEALTH | 18082 | Capital intelligence |
| WELL | 18083 | Vitality mirror |
| arifFlow | 7073 | FQ metabolic pulse |

Truth rule: **live `:port/health` + `tools/list` beat any static count in prose.**

---

## Documentation

| Audience | Start here |
|---|---|
| **Humans** (understand it) | [`docs/humans/WHY_ARIFOS.md`](./docs/humans/WHY_ARIFOS.md) |
| **Humans** (the constitution) | [`docs/humans/CONSTITUTION_IN_PLAIN_LANGUAGE.md`](./docs/humans/CONSTITUTION_IN_PLAIN_LANGUAGE.md) |
| **Developers** (integrate it) | [`docs/QUICKSTART.md`](./docs/QUICKSTART.md) |
| **Agents** (boot and operate) | [`AGENT_BOOTSTRAP.md`](./AGENT_BOOTSTRAP.md) |
| **Researchers** (cite and evaluate) | [`CITATION.cff`](./CITATION.cff) · [`GENESIS/`](./GENESIS/) |
| **Constitution** | [`GENESIS/000_KERNEL_CANON.md`](./GENESIS/000_KERNEL_CANON.md) |
| **Floor definitions** | [`GENESIS/FLOOR_TABLE.json`](./GENESIS/FLOOR_TABLE.json) |
| **Deploy** | [`deploy/DEPLOY.md`](./deploy/DEPLOY.md) |
| **Full doctrine** | [`arifos://doctrine`](https://mcp.arif-fazil.com) (MCP resource) |

---

## Governance

- **Authority chain:** `arif_init → arif_observe → arif_think → arif_route → arif_memory → arif_judge → arif_forge → arif_seal`
- **Autonomy tiers:** T0 read auto-do · T1 edit/test/commit · T2 announce-10s-veto · T3 888_HOLD always
- **No self-certification.** No consciousness claims (F9). The kernel audits itself last.

---

## Citation

If you use arifOS in research, please cite:

```bibtex
@software{arifos2026,
  author = {Muhammad Arif bin Fazil},
  title = {arifOS: Constitutional AI Kernel and AGI Substrate},
  year = {2026},
  url = {https://github.com/ariffazil/arifOS},
  license = {AGPL-3.0}
}
```

See [`CITATION.cff`](./CITATION.cff) for full metadata.

---

## License

**AGPL-3.0** — fork the institution, not just the code.

---

## Author

**Muhammad Arif bin Fazil** — F13 Sovereign of the arifOS Federation.

Forged on VPS af-forge, under load, by an agent that survived its own audit.

DITEMPA BUKAN DIBERI.
