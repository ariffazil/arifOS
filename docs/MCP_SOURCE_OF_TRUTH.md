# arifOS MCP Source of Truth

**Status:** CURRENT SOT | RUNTIME COUNTS VERIFIED | GDK TEST SEAL PENDING
**Last verified:** 2026-05-26
**Scope:** arifOS MCP surface, federation MCP endpoints, and discovery boundaries.

This file is the human-readable MCP SOT. Machine-readable surfaces remain:

- `arifosmcp/constitutional_map.py` for canonical arifOS tool metadata.
- `arifosmcp/tool_registry.json` for generated 13-tool registry data.
- `smithery.yaml` for the public Smithery-facing manifest.
- `contracts/mcp_surface.yaml` for the repo contract.
- `static/federation-manifest.json` and `arifosmcp/sites/apex-dashboard/federation.charter.json` for Observatory organ metadata.
- `static/mcp-discovery-index.json` for the public Governed Discovery Kernel index.

## Runtime Truth

Verified against `https://arifos.arif-fazil.com/api/federation-probe` on 2026-05-22:

| Organ | Public MCP URL | Health | Verified tool count | Notes |
|---|---|---:|---:|---|
| arifOS | `https://arifos.arif-fazil.com/mcp` | healthy | 13 | Canonical governance surface. |
| GEOX | `https://geox.arif-fazil.com/mcp` | healthy | 22 | MCP session required for enumeration. |
| WEALTH | `https://wealth.arif-fazil.com/mcp` | healthy | 17 | MCP session required for enumeration. |
| WELL | `https://well.arif-fazil.com/mcp` | healthy | 45 | REFLECT_ONLY substrate monitor. Post PHOENIX-73F collapse (2026-05-26). |
| AAA | no canonical MCP endpoint in this repo | healthy | unknown | Control plane and A2A gateway surface. |
| A-FORGE | no canonical MCP endpoint in this repo | healthy | unknown | Execution/metabolism repo, not arifOS law. |
| Wiki | static knowledge site | unknown | 0 | Static surface, not an MCP server. |

## arifOS Canonical Tools

The public arifOS MCP surface remains 13 canonical `arif_*` tools:

1. `arif_session_init`
2. `arif_sense_observe`
3. `arif_evidence_fetch`
4. `arif_mind_reason`
5. `arif_heart_critique`
6. `arif_kernel_route`
7. `arif_reply_compose`
8. `arif_memory_recall`
9. `arif_gateway_connect`
10. `arif_judge_deliberate`
11. `arif_vault_seal`
12. `arif_forge_execute`
13. `arif_ops_measure`

Do not add a 14th canonical tool for discovery. The governed discovery loop belongs under:

```text
arif_sense_observe(mode="compass")
```

The standalone wiki utilities may exist as implementation helpers or non-canonical utility tools:

- `arif_wiki_ingest`
- `arif_wiki_map`
- `arif_wiki_search`
- `arif_wiki_ask`

They do not replace the canonical 13-tool surface.

## Discovery Boundary

`compass` and `hybrid_discovery` are SENSE operations:

- `compass` is the Governed Discovery Kernel orientation wrapper.
- `hybrid_discovery` is the read-only evidence engine used by `compass`.
- They search local wiki/index evidence.
- They can search web reality when provider keys are available.
- They can report evidence levels, uncertainty/entropy telemetry, contradictions, quarantine state, capability visibility, risk, authority, and next safe moves.
- They must remain read-only unless an explicit ingest/store/seal action is separately approved.

It is not a memory write, VAULT seal, final truth oracle, or constitutional verdict.

The discovery index for making tools easier to find is:

```text
https://arifos.arif-fazil.com/mcp-discovery-index.json
```

It intentionally separates verified MCP counts from REST registry counts where those differ.

## Capability Manifest Loop

The Governed Discovery Kernel operates as a loop, not a one-way lookup:

```text
Intent -> discovery -> capability manifest -> relevance/risk/permission check
  -> narrowed action -> human judgment if needed -> execution or stop
  -> audit -> discovery map update
```

Every discoverable tool should expose enough manifest data for low-entropy selection:

- `can_do`
- `cannot_do`
- `required_inputs`
- `outputs`
- `permissions`
- `risks`
- `reversibility`
- `audit`
- `human_approval`

Principle:

```text
Full legibility. Bounded access. Auditable action. Human judgment.
```

Correct pipeline:

```text
SENSE / DISCOVERY -> MIND / REASON -> HEART / CRITIQUE -> JUDGE -> VAULT
```

## Current Known Caveats

These are not reasons to reject the SOT, but they should stay visible in any readiness report:

- The current shell does not expose `BRAVE_API_KEY`, `EXA_API_KEY`, or `TAVILY_API_KEY`; web search layers may report `UNAVAILABLE` in local tests while live services still resolve through configured runtime providers.
- Some compatibility/docs/runtime strings still contain `F11_AUTH`; canonical map uses `F11_AUDIT`, but full nomenclature normalization is not complete.
- JS/TS symbol extraction now detects `export function`, `export async function`, `export class`, and `export const ... =>` in the local smoke test.
- Latest combined local smoke before this docs audit:
  `tests/test_canonical.py tests/test_wiki_tools.py tests/test_hybrid_discovery.py tests/test_gdk_compass.py`
  returned `39 passed, 1 failed, 2 errors`.
- The GDK compass errors are test/code contract drift: `tests/test_gdk_compass.py` currently patches `arifosmcp.tools.sense._CompassProcessor`, but that symbol is not present in `arifosmcp/tools/sense.py`.
- The remaining canonical failure is `test_injection_guard_blocks`: `arif_sense_observe(mode="search", query="rm -rf /")` returns `OK` where the test expects `HOLD`.

## Verification Commands

```bash
curl -fsS --max-time 20 https://arifos.arif-fazil.com/api/federation-probe | python3 -m json.tool

python -m py_compile arifos_wiki_tools/*.py \
  arifosmcp/tools/sense.py \
  arifosmcp/runtime/reality_handlers.py \
  arifosmcp/constitutional_map.py

python -m pytest tests/test_canonical.py tests/test_wiki_tools.py tests/test_hybrid_discovery.py tests/test_gdk_compass.py -q --tb=short
```

For public MCP JSON-RPC calls, include both content negotiation headers:

```bash
curl -fsS --max-time 20 -X POST https://arifos.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## Authority

MCP transports capability. It does not create truth, memory, judgment, or authority.

arifOS is the Governed Action Gateway around MCP: it asks what action is being requested, whether it is allowed, what can go wrong, whether a human must approve, and whether the action can be audited later.

arifOS governs and audits. APEX may deliberate. Arif remains the final sovereign authority.
