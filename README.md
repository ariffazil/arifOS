# arifOS - Sovereign Constitutional Intelligence Kernel

> DITEMPA BUKAN DIBERI - Intelligence is forged, not given.

arifOS is the law kernel for a governed AI federation. It is not a model, chatbot, or agent persona. It is the constitutional runtime that decides how AI systems observe, reason, execute, judge, and seal actions through MCP tools, typed schemas, floor enforcement, and VAULT999 audit trails.

The core guarantee is simple: high-impact or irreversible action must pass constitutional judgment before execution, and the human sovereign retains final veto.

## Current SOT

This README reflects the local repository state audited on 2026-04-26.

| Surface | Current truth |
| --- | --- |
| Canonical repository | `https://github.com/ariffazil/arifOS` |
| Python package | `arifos` |
| Package version | `2026.04.24` |
| Runtime version | `2026.04.24-KANON` |
| Runtime entrypoint | `arifosmcp.runtime.server:app` |
| CLI entrypoint | `arifos-mcp` |
| Python | `>=3.12` |
| MCP framework | `fastmcp==3.1.1` |
| Default HTTP port | `8080` |
| Constitutional floors | 13, `F01` through `F13` |
| Registered MCP tools | 15 total: 13 constitutional tools plus 2 public probes |
| Canonical prompts | 8 |
| Canonical resources | 5 |
| Test files | 95 `test_*.py` files under `tests/` |

Source-of-truth order when files disagree:

1. Live runtime endpoints: `/health`, `/metadata`, MCP discovery.
2. `arifosmcp/constitutional_map.py` for floor and tool authority.
3. `arifosmcp/runtime/tools.py` for registered tool behavior.
4. `arifosmcp/resources/` and `arifosmcp/prompts/` for context surfaces.
5. `pyproject.toml`, `Dockerfile`, and `docker-compose.yml` for packaging and deployment.
6. Documentation, including this README.

## What arifOS Does

arifOS governs AI work through five responsibilities:

| Responsibility | Meaning |
| --- | --- |
| Constitutional law | Defines the 13 floors that constrain action. |
| Runtime governance | Registers MCP tools, prompts, resources, schemas, and HTTP routes. |
| Judgment | Emits `SEAL`, `HOLD`, or `VOID` decisions for proposed action. |
| Execution gating | Routes irreversible work through identity, risk, and floor checks. |
| Witness and memory | Preserves evidence, state, and audit trails through VAULT999 and supporting stores. |

arifOS may be used alone as an MCP server, or as the law kernel in the wider federation:

| Project | Role |
| --- | --- |
| `arifOS` | Constitutional law kernel and VAULT999 authority. |
| `A-FORGE` | Execution shell and agent orchestration layer. |
| `GEOX` | Earth-domain coprocessor for geoscience and physical evidence. |
| `WEALTH` | Capital intelligence coprocessor for valuation and risk. |
| `compose` | Production stack wiring Caddy, Postgres, Redis, Qdrant, Ollama, arifOS, GEOX, WEALTH, and gateway services. |

A-FORGE may orchestrate. arifOS adjudicates. Domain coprocessors provide evidence and specialist computation, but constitutional verdicts belong here.

## Runtime Surface

The current runtime registers 15 MCP tools. The distinction matters:

- 13 constitutional tools are the governed metabolic surface.
- 2 public probes, `arif_ping` and `arif_selftest`, are lightweight diagnostics.

The older `arifosmcp/tool_registry.json` lists the 13 constitutional tools. The active runtime imports `CANONICAL_TOOLS` from `arifosmcp/constitutional_map.py`, which currently includes the 2 probes as well.

### Public Probes

| Tool | Purpose |
| --- | --- |
| `arif_ping` | Lightweight health probe. |
| `arif_selftest` | In-memory diagnostic self-test. |

### Constitutional Tools

| Stage | Tool | Lane | Access | Purpose |
| --- | --- | --- | --- | --- |
| `000` | `arif_session_init` | AGI | public | Start a session and bind identity context. |
| `111` | `arif_sense_observe` | AGI | public | Observe reality, telemetry, and evidence. |
| `222` | `arif_evidence_fetch` | AGI | public | Fetch and preserve evidence. |
| `333` | `arif_mind_reason` | AGI | public | Reason with humility, claim labeling, and synthesis traces. |
| `444` | `arif_kernel_route` | AGI | public | Route kernel actions and telemetry. |
| `444r` | `arif_reply_compose` | AGI | public | Compose governed responses. |
| `555` | `arif_memory_recall` | AGI | public | Recall, store, search, and prune governed memory context. |
| `666` | `arif_heart_critique` | ASI | authenticated | Critique safety, empathy, consequence, and manipulation risk. |
| `666g` | `arif_gateway_connect` | ASI | authenticated | Connect and route across A2A/federated gateways. |
| `777` | `arif_ops_measure` | AGI | public | Measure operations, cost, vitality, and thermodynamics. |
| `888` | `arif_judge_deliberate` | ASI | authenticated | Produce constitutional verdicts. |
| `999` | `arif_vault_seal` | APEX | authenticated | Seal audit records and ledger entries. |
| `010` | `arif_forge_execute` | AGI | sovereign | Dispatch execution to A-FORGE with irreversible-action controls. |

Access classes:

| Access | Current tools |
| --- | --- |
| public | `arif_ping`, `arif_selftest`, `arif_session_init`, `arif_sense_observe`, `arif_mind_reason`, `arif_kernel_route`, `arif_ops_measure`, `arif_memory_recall`, `arif_evidence_fetch`, `arif_reply_compose` |
| authenticated | `arif_heart_critique`, `arif_judge_deliberate`, `arif_vault_seal`, `arif_gateway_connect` |
| sovereign | `arif_forge_execute` |

## 13 Constitutional Floors

| Floor | Name | Rule |
| --- | --- | --- |
| `F01` | AMANAH | Actions must be accountable; irreversible action requires approval and trace. |
| `F02` | TRUTH | Do not fabricate. Separate fact, estimate, hypothesis, and unknown. |
| `F03` | WITNESS | Evidence must be inspectable and preserved where possible. |
| `F04` | CLARITY | Intent, uncertainty, and consequences must be legible. |
| `F05` | PEACE | Preserve dignity and reduce avoidable harm. |
| `F06` | EMPATHY | Model stakeholder consequences before acting. |
| `F07` | HUMILITY | Bound confidence and acknowledge limits. |
| `F08` | GENIUS | Prefer elegant correctness over noisy complexity. |
| `F09` | ANTIHANTU | Reject manipulation, dark patterns, and false agency claims. |
| `F10` | ONTOLOGY | Preserve structural and identity coherence. |
| `F11` | AUTH | Verify actor authority before sensitive operations. |
| `F12` | INJECTION | Treat inputs as hostile until sanitized. |
| `F13` | SOVEREIGN | Human veto is absolute. |

## Verdicts

arifOS judgment collapses proposed action into one of three operational states:

| Verdict | Meaning |
| --- | --- |
| `SEAL` | Proceed; action is constitutionally cleared and may be recorded. |
| `HOLD` | Pause; more evidence, identity, consent, or review is required. |
| `VOID` | Halt; action violates a hard floor or cannot be safely justified. |

The expected path for high-impact action is:

```text
observe -> reason -> critique -> judge -> execute or hold -> seal
```

## Prompts and Resources

Canonical prompts registered by the runtime:

```text
system, judge, init, rsi, ortho, epistemic, governance, entropy
```

Canonical resources registered by the runtime:

| URI | Meaning |
| --- | --- |
| `arifos://doctrine` | Immutable law and floor doctrine. |
| `arifos://vitals` | Runtime vitality and system pulse. |
| `arifos://schema` | Tool, prompt, resource, and schema blueprint. |
| `arifos://forge` | Execution bridge context. |
| `arifos://civilization` | Federation organs and strata. |

## HTTP Endpoints

The FastMCP HTTP app exposes MCP transport plus small REST routes:

| Endpoint | Purpose |
| --- | --- |
| `/mcp` | MCP streamable HTTP endpoint. |
| `/health` | Runtime health, counts, and version. |
| `/metadata` | Gateway metadata and access classes. |
| `/humans.txt` | Human attribution. |

The deployed VPS may show a release tag older than the package version if the live container has not been rebuilt from the latest local checkout. Treat live `/health` as runtime truth and this repo as source truth.

## Repository Map

| Path | Purpose |
| --- | --- |
| `000/` | Constitutional law, floors, policies, root doctrine. |
| `arifosmcp/server.py` | Canonical FastMCP server setup and HTTP app. |
| `arifosmcp/runtime/server.py` | Compatibility entrypoint that re-exports the root server app. |
| `arifosmcp/runtime/tools.py` | MCP tool implementations and registration. |
| `arifosmcp/constitutional_map.py` | Active tool/floor/access SOT used by the runtime. |
| `arifosmcp/tool_registry.json` | 13-tool constitutional registry snapshot. |
| `arifosmcp/prompts/` | Prompt registration and constitutional context injection. |
| `arifosmcp/resources/` | `arifos://` resource registration. |
| `arifosmcp/schemas/` | Typed contracts for cognition, synthesis, telemetry, forge, verdicts, and memory. |
| `arifosmcp/core/` | Governance kernel and floor logic. |
| `arifosmcp/apps/` | Optional app/dashboard surfaces. |
| `skills/` | Agent skill packs and operational runbooks. |
| `tests/` | Pytest suite for runtime, floors, tools, integration, and adversarial checks. |
| `docker-compose.yml` | Production-style compose stack for the arifOS federation. |
| `Dockerfile` | Container image for the MCP server. |
| `Makefile` | Local status, publish, and release helpers. |

## Quick Start

```bash
cd /root/arifOS

python -m pip install -e . --break-system-packages
arifos-mcp
```

Alternative entrypoints:

```bash
python -m arifosmcp.server
uvicorn arifosmcp.runtime.server:app --host 0.0.0.0 --port 8080
```

Probe the server:

```bash
curl -s http://localhost:8080/health | jq .
curl -s http://localhost:8080/metadata | jq .
```

## Docker

```bash
cd /root/arifOS
docker build -t arifos:local .
docker run --rm -p 8080:8080 arifos:local
```

Production compose expects the shared `arifos_core_network` Docker network and supporting services such as Postgres, Redis, Qdrant, Ollama, Caddy, VAULT999, GEOX, and WEALTH.

```bash
cd /root/arifOS
docker compose up -d --build
docker compose logs -f arifosmcp
```

## Development

Install development dependencies:

```bash
python -m pip install -e ".[dev]" --break-system-packages
```

Run focused checks:

```bash
python -m pytest tests/ -q --tb=short
ruff check .
mypy arifosmcp/
```

Useful Makefile targets:

| Command | Purpose |
| --- | --- |
| `make status` | Run reforge/status and show git status. |
| `make forge` | Run reforge and stage changes. |
| `make seal` | Commit and push a dated seal commit. |
| `make publish-check` | Check tokens and run tests before publish. |
| `make publish-pypi` | Build and publish the Python package. |
| `make publish-ghcr` | Build and push GHCR image. |

Note: `make health` currently probes `localhost:8000`; the canonical arifOS server default is `8080`.

## Security Rules for Agents

Agents working in this repository must follow these hard rules:

1. Do not fabricate runtime facts. Verify with code, tests, or live endpoints.
2. Do not expose secrets, tokens, `.env` files, private keys, or raw credential values.
3. Do not run destructive operations such as `rm -rf`, `docker volume prune`, `docker system prune -a`, `DROP TABLE`, or ledger deletion without explicit human approval.
4. Treat VAULT999 ledgers as append-only.
5. Keep constitutional judgment in arifOS. Do not duplicate SEAL/HOLD/VOID authority in A-FORGE, GEOX, or WEALTH.
6. If docs, registry, and runtime disagree, report the conflict and cite the stronger SOT.

## Known SOT Gaps

These are documentation/runtime alignment issues that should not be hidden:

| Gap | Current state |
| --- | --- |
| Legacy docs | Some older docs outside this README may still say 13, 37, or 39 tools. Current runtime SOT is 15 registered tools: 13 constitutional plus 2 probes. |
| Deployed version | The live VPS health endpoint may report `v2026.04.19-UNIFIED` while local source reports `2026.04.24-KANON`. |

These gaps are not fatal, but they should be resolved before a release seal.

## License

AGPL-3.0-only. See `LICENSE`.

## One-Sentence Summary

arifOS is the constitutional MCP law kernel that gives AI agents a governed path from observation to judgment to execution to audit, while preserving human sovereignty.
