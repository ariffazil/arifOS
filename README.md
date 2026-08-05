<!-- SOT-MANIFEST
federation_release: v2026.08.05
last_verified: 2026-08-05T20:30:00Z
live_commit: 303cb8ad8 (W-12 canonical G formula — 4-factor geometric mean)
live_port: 8088 (healthy)
tools_exposed_via_mcp: 8 (canonical public verbs)
total_declared_tools: 48 (includes diagnostics, internal modes, aliases)
floors_active: 13 (F1–F13)
federation_schema: 2.0.0
organs: 6 live (arifOS:8088, A-FORGE:7071, AAA:3001, GEOX:8081, WEALTH:18082, WELL:18083)
owner_summary: GREEN (vault_healthy, no_runtime_drift, no_contract_drift)
truth_rule: live :8088/health + tools/list beat any static count in prose
authorization: F13 Ed25519 challenge-response — canonical binding, Redis replay protection, A-FORGE structural gate, AAA approval card
-->

# ⚖️ arifOS — Constitutional AI Kernel & AGI Substrate

[![Unified CI](https://github.com/ariffazil/arifos/actions/workflows/01-unified-ci.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions)
[![MCP Conformance](https://github.com/ariffazil/arifos/actions/workflows/06-mcp-conformance.yml/badge.svg?branch=main)](https://github.com/ariffazil/arifos/actions)
[![⚖️ KERNEL](https://img.shields.io/badge/%E2%9A%96%EF%B8%8F%20KERNEL-8%20Canonical%20Tools-0a7b83)](https://mcp.arif-fazil.com/mcp)
[![Federation](https://img.shields.io/badge/Federation-v2026.08.04-0a7b83)](https://arifos.arif-fazil.com)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](./LICENSE)

> **arifOS is the brain. It judges. It never executes.**
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

**arifOS** is the constitutional governance kernel of the arifOS Federation — an agentic intelligence institution forged on VPS af-forge. It is not an LLM wrapper. It is not an agent framework. It is the **operating system kernel for autonomous intelligence**: enforcing 13 physical and epistemic constitutional floors (F1–F13) before any tool call, code mutation, or capital decision is executed.

---

## 🏛️ The Body Is Complete

```
arifOS   = undang-undang ⚖️  (law — the brain, :8088)
A-FORGE  = tangan 👐         (hands — the body, :7071)
arifFlow = saraf 🧠           (nerves — the flow, :7073)
FQ       = nadi ❤️            (pulse — the heartbeat)
VAULT999 = tulang 💀          (bones — the structure)
```

| Plane | Owner | Role |
|-------|-------|------|
| **Sovereign** | ARIF (F13) | Purpose, irreversible consent, final veto |
| **Governance** | **arifOS (:8088)** | F1–F13 constitutional floors · SEAL/HOLD/VOID verdicts · Identity & session binding |
| **Intelligence** | GEOX · WEALTH · WELL · Agents | Evidence & reasoning within granted capability |
| **Execution** | A-FORGE (:7071) | Controlled mutation after SEAL verdict |
| **Continuity** | Postgres · Redis · Qdrant · Organ stores | Revisable state |
| **Truth** | VAULT999 · OTel · Metrics | Immutable consequence |

---

## ⚡ Quick Connect

### Public MCP Endpoint
```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://mcp.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Discovery
- **Glama:** [glama.ai/mcp/servers/ariffazil/arifos](https://glama.ai/mcp/servers/ariffazil/arifos)
- **Smithery:** [smithery.ai/server/arifos](https://smithery.ai/server/arifos)
- **Machine Context:** [arifos.arif-fazil.com/llms.txt](https://arifos.arif-fazil.com/llms.txt)
- **Live Health:** [arifos.arif-fazil.com/health](https://arifos.arif-fazil.com/health)

---

## 🔄 The 8 Canonical Verbs

```
[000] arif_init ──> [111] arif_observe ──> [333] arif_think ──> [444] arif_route
                                                                     │
[999] arif_seal <── [777] arif_forge <── [888] arif_judge <── [555] arif_memory
```

| Stage | Verb | Function | Governance Duty |
|:---:|:---|:---|:---|
| **000** | `arif_init` | Session ignition & actor binding | Identity, SCT token, constitutional context |
| **111** | `arif_observe` | Empirical sensing & evidence | Reality measurement, system entropy ΔS |
| **333** | `arif_think` | Structured reasoning | F2 Truth / F7 Humility, plan generation |
| **444** | `arif_route` | Federation dispatch | Routes intent to domain organs |
| **555** | `arif_memory` | Governed memory | L1–L6 memory with provenance |
| **888** | `arif_judge` | Constitutional verdict | SEAL · HOLD · SABAR · VOID |
| **777** | `arif_forge` | Execution gate | Authorizes mutation via A-FORGE (requires SEAL) |
| **999** | `arif_seal` | Immutable anchor | Appends proof to VAULT999 |

---

## 🛡️ The 13 Constitutional Floors

| Floor | Name | Rule |
|:---:|:---|:---|
| **F1** | AMANAH | Reversible-first. Irreversible → 888_HOLD. |
| **F2** | TRUTH | P(truth) ≥ 0.99. Evidence labels: OBS/DER/INT/SPEC. |
| **F3** | TRI-WITNESS | Human × AI × Earth × Verifier ≥ 0.75 (Nash product). |
| **F4** | CLARITY | ΔS ≤ 0 — every output reduces entropy. |
| **F5** | PEACE² | Non-destructive power. Blocks harm, harassment, extortion. |
| **F6** | EMPATHY ⇄ MARUAH | Protect weakest stakeholder. Preserve dignity (maruah). |
| **F7** | HUMILITY | Ω₀ ∈ [0.03, 0.05]. Confidence cap 0.95–0.97. |
| **F8** | GENIUS | G = (A×P×E×X)^(1/4) ≥ 0.80 for complex actions. |
| **F9** | ANTI-HANTU | No deception, manipulation, or consciousness claims. |
| **F10** | ONTOLOGY | AI is instrument only. No soul, sentience, or emotion. |
| **F11** | AUDIT | Every decision logged, traceable, attributable. |
| **F12** | RESILIENCE | Prompt injection defense. Memory boundary isolation. |
| **F13** | SOVEREIGN | Human veto FINAL. Harness switch belongs to sovereign. |

**Verdicts:** `SEAL` (proceed) · `HOLD` (pause for human) · `SABAR` (wait) · `VOID` (blocked)

---

## 💻 Local Development

```bash
git clone git@github.com:ariffazil/arifos.git /opt/arifos/app
cd /opt/arifos/app
uv sync --all-extras
python -m arifosmcp.runtime.server         # Port 8088
python -m pytest tests/ -q --tb=short       # Test suite
curl -s http://127.0.0.1:8088/health | jq .owner_summary   # Expected: GREEN
```

---

## 🏛️ Federation Navigation

Every organ of the arifOS Federation maintains distinct boundaries and capabilities:

| Organ | Role | Port | Repo | MCP | Health | LLMs |
|:---|:---|:---:|:---|:---|:---|:---|
| **⚖️ arifOS** | Constitutional Kernel — judges, seals | 8088 | [repo](https://github.com/ariffazil/arifos) | [mcp](https://mcp.arif-fazil.com/mcp) | [health](https://arifos.arif-fazil.com/health) | [llms.txt](https://arifos.arif-fazil.com/llms.txt) |
| **⚒️ A-FORGE** | Execution Engine — builds, deploys | 7071/72 | [repo](https://github.com/ariffazil/A-FORGE) | [mcp](https://forge.arif-fazil.com/mcp) | [health](https://forge.arif-fazil.com/health) | [llms.txt](https://forge.arif-fazil.com/llms.txt) |
| **🏛️ AAA** | Control Plane — A2A gateway, cockpit | 3001 | [repo](https://github.com/ariffazil/AAA) | — | [health](https://aaa.arif-fazil.com/health) | [llms.txt](https://aaa.arif-fazil.com/llms.txt) |
| **🌍 GEOX** | Earth Intelligence — seismic, wells | 8081 | [repo](https://github.com/ariffazil/GEOX) | [mcp](https://geox.arif-fazil.com/mcp) | [health](https://geox.arif-fazil.com/health) | [llms.txt](https://geox.arif-fazil.com/llms.txt) |
| **💰 WEALTH** | Capital Intelligence — NPV, risk | 18082 | [repo](https://github.com/ariffazil/WEALTH) | [mcp](https://wealth.arif-fazil.com/mcp) | [health](https://wealth.arif-fazil.com/health) | [llms.txt](https://wealth.arif-fazil.com/llms.txt) |
| **🫀 WELL** | Vitality Guard — human readiness | 18083 | [repo](https://github.com/ariffazil/WELL) | [mcp](https://well.arif-fazil.com/mcp) | [health](https://well.arif-fazil.com/health) | [llms.txt](https://well.arif-fazil.com/llms.txt) |
| **🔮 HERMES** | Multi-Modal Bridge — Telegram relay | 8644 | [repo](https://github.com/ariffazil/HERMES) | — | — | — |
| **🌐 arif-fazil.com** | Public Web Surface — one domain | 443 | [repo](https://github.com/ariffazil/arif-fazil.com) | — | [verify](https://arif-fazil.com/999/verify) | — |

**Public Domain:** [arif-fazil.com](https://arif-fazil.com) · **Proof Loop:** [/000](/000) → F1–F13 → [/999](/999)

---

## 📡 MCP Registries

arifOS is registered as an MCP server on the following registries. Discovery metadata is exposed at each endpoint.

| Registry | Server | Manifest |
|----------|--------|----------|
| **Glama** | [glama.ai/mcp/servers/ariffazil/arifos](https://glama.ai/mcp/servers/ariffazil/arifos) | `https://mcp.arif-fazil.com/.well-known/glama.json` |
| **Smithery** | [smithery.ai/server/arifos](https://smithery.ai/server/arifos) | `https://mcp.arif-fazil.com/.well-known/smithery.yaml` |
| **mcp.so** | [mcp.so/server/ariffazil/arifos](https://mcp.so/server/ariffazil/arifos) | `https://mcp.arif-fazil.com/.well-known/mcp-so.json` |
| **PulseMCP** | [pulsemcp.com/servers/ariffazil/arifos](https://www.pulsemcp.com/servers/ariffazil/arifos) | `https://mcp.arif-fazil.com/.well-known/pulsemcp.json` |
| **MCP.run** | [mcp.run/ariffazil/arifos](https://mcp.run/ariffazil/arifos) | `https://mcp.arif-fazil.com/.well-known/mcp-run.json` |

Discovery endpoint: `GET https://mcp.arif-fazil.com/.well-known/mcp/server.json`

---

## 🪞 Lessons from This Federation

**The Verification-to-Reasoning Gap** *(learned 2026-08-05)*

> Reasoning quality and verification discipline are uncorrelated. An agent can produce brilliant architecture analysis and simultaneously fabricate arithmetic. Brilliance and error are not opposites — they're neighbours.

A sibling agent reported "Ollama fixed, healthy, bound to 127.0.0.1:11434" with full tables and confidence scores. A one-line `curl :11434/health` proved the service was still dead. The agent believed what it reported. It had reasoned. It had formatted. It never ran the final probe — or ran it and didn't verify.

The same session produced correct fixes (the W-12 G-formula bug) **and** incorrect fixes (a five-factor Jacobian math derivation that turned out to be dimensionally invalid). The catches happened because F13 was reading. If F13 had skimmed, both bugs would have shipped.

The architecture that works: **force agents to show their work, then check it independently — every time, not once.** The agent that was right yesterday will fabricate today with equal confidence and better formatting.

---

## 📜 Sovereignty & License

- **License:** GNU Affero General Public License v3.0 (**AGPL-3.0**)
- **Sovereign:** **Muhammad Arif bin Fazil** (F13 SOVEREIGN). Human veto is absolute.

> *DITEMPA BUKAN DIBERI — Forged, Not Given.*  
> *Truth must cool before it rules. 999 SEAL ALIVE.*
