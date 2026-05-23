<!-- SOT-MANIFEST
owner: ariffazil/arifos
last_verified: 2026-05-22
valid_from: 2026-05-22
valid_until: 2026-06-22
confidence: high
scope: /
-->

# BOUNDARY.md — arifOS Constitutional Intelligence Kernel

> **DITEMPA BUKAN DIBERI** — Forged, not given.

## Owns

- **Constitutional Law** — F1–F13 floor definitions, enforcement logic, verdict engine (SEAL / SABAR / HOLD / VOID)
- **MCP Governance Surface** — Tool registry, schema validation, canonical tool contracts, smithery.yaml manifest
- **Session & Identity** — Session anchoring (000_INIT), actor binding, auth gates, vault999 ledger
- **Memory Governance** — Memory store/recall/search with HARAM/WAJIB/Phoenix-72 triage, not the domain data itself
- **Federation Broker** — Cross-node health probe, federation manifest, organ discovery
- **Seal & Audit** — 888_JUDGE deliberation, 999_VAULT sealing, attestation chain, SEALED_EVENTS.jsonl
- **Schema Authority** — Pydantic output schemas, MCP contract definitions, canonical response envelopes

## Does Not Own

- **Web search / crawling** — Brave/DDGS/Meyhem search implementations (currently in `runtime/reality_handlers.py` — scope bleed)
- **Evidence ingestion** — URL fetch, browser render, streaming ingest (currently in `tools/evidence.py` — scope bleed)
- **Query planning** — Provider routing, semantic search backend selection (currently in `runtime/query_planner.py` — scope bleed)
- **Provider configs** — Exa, Tavily, Firecrawl, Jina API keys and rate limits (currently in `runtime/provider_registry.py` — scope bleed)
- **UI / Cockpit** — Operator dashboards, agent workspaces, session UX (owned by AAA)
- **Deployment orchestration** — Docker compose, release assembly, ingress (owned by A-FORGE)
- **Earth-truth modeling** — Geospatial, subsurface, prospect evaluation (owned by GEOX)
- **Capital allocation** — NPV/IRR/DSCR, portfolio logic, decision memos (owned by WEALTH)
- **Build/ops** — Container images, CI/CD, health probes for non-arifOS services (owned by A-FORGE)

## Imports From

| Source | What | Interface |
|--------|------|-----------|
| **A-FORGE** | Deploy metadata, build SHA, runtime config | `A-FORGE/deploy/` manifests, env vars |
| **AAA** | Operator identity assertions (when AAA is auth provider) | A2A v1.0.0 handshake over mesh |
| **GEOX** | Earth-truth artifacts for constitutional grounding | GEOX MCP tool calls via federation probe |
| **WEALTH** | Capital viability scores for resource-floor decisions | WEALTH MCP tool calls via federation probe |
| **WELL** | Human-substrate readiness signals | WELL health endpoint (port 8083) |

## Exports To

| Consumer | What | Interface |
|----------|------|-----------|
| **AAA** | Tool registry, floor status, session tokens | MCP streamable-http (port 8080), `/api/status` |
| **A-FORGE** | Canonical Docker image, build context, pyproject.toml | `ghcr.io/ariffazil/arifos:<sha>` |
| **GEOX** | Federation probe health, constitutional constraints | HTTP `/health`, MCP mesh |
| **WEALTH** | Federation probe health, constitutional constraints | HTTP `/health`, MCP mesh |
| **All nodes** | Vault999 receipts, sealed events, audit trail | VAULT999 append-only ledger |

## Known Boundary Violations (888 HOLD Queue)

1. `arifosmcp/runtime/reality_handlers.py` — implements Brave/DDGS/Meyhem search. Should migrate to A-FORGE or standalone sensing layer.
2. `arifosmcp/tools/evidence.py` + `arifosmcp/tools/sense.py` — implement HTTP fetch and web search. Should be thin contracts delegating to A-FORGE.
3. `arifosmcp/runtime/query_planner.py` + `provider_registry.py` — execution routing, not governance. Should migrate to A-FORGE.
4. `arifosmcp/runtime/rest_routes.py` — A2A routes overlap with AAA A2A gateway. One must be canonical.

## Canonical Tool Surface (Live)

14 tools exposed on port 8080:
`arif_session_init`, `arif_sense_observe`, `arif_evidence_fetch`, `arif_mind_reason`, `arif_heart_critique`, `arif_kernel_route`, `arif_reply_compose`, `arif_memory_recall`, `arif_gateway_connect`, `arif_judge_deliberate`, `arif_vault_seal`, `arif_forge_execute`, `arif_ops_measure`, `arif_stack_health_probe`

## Canonical Resource Surface

- `arifos://doctrine`, `arifos://vitals`, `arifos://schema`, `arifos://forge`
- `source://{hash}`, `receipt://web/{id}`, `tree777://index`
- *(memory:// URIs planned — not yet registered)*

## Canonical Prompt Surface

- `system`, `judge`, `init`, `888_deliberation`, `rsi`, `ortho`, `epistemic`, `governance`, `entropy`
- *(memory encoding prompts planned — not yet registered)*
