# arifOS MCP Source of Truth

**Status:** CURRENT SOT | RUNTIME COUNTS VERIFIED | FEDERATION-SOT-20260714
**Last verified:** 2026-07-14
**Valid until:** 2026-08-14
**Scope:** arifOS MCP surface, federation MCP endpoints, and discovery boundaries.

This file is the human-readable MCP SOT. Machine-readable surfaces remain:

- `arifosmcp/constitutional_map.py` for canonical arifOS tool metadata.
- `arifosmcp/tool_registry.json` for generated 13-tool registry data.
- `smithery.yaml` for the public Smithery-facing manifest.
- `contracts/mcp_surface.yaml` for the repo contract.
- `static/federation-manifest.json` and `arifosmcp/sites/apex-dashboard/federation.charter.json` for Observatory organ metadata.
- `static/mcp-discovery-index.json` for the public Governed Discovery Kernel index.

## Runtime Truth

Verified against live `/health` endpoints on 2026-07-14 (FEDERATION-SOT-20260714-a840f2ae):

| Organ | Public MCP URL | Health | Verified tool count | Notes |
|---|---|---:|---:|---|
| arifOS | `https://mcp.arif-fazil.com/mcp` | healthy | 8 deployed / 6 generated public profile | 8-capability Kernel ABI; deployed profile currently exposes all bindings. |
| GEOX | `https://geox.arif-fazil.com/mcp` | healthy | 15 canonical (ZEN-15) | Earth intelligence. Mode-based tools. |
| WEALTH | `https://wealth.arif-fazil.com/mcp` | ALIVE | 12 live | Capital intelligence. Mode-dispatched canonical tools. |
| WELL | `https://well.arif-fazil.com/mcp` | degraded | 27 live | REFLECT_ONLY substrate monitor. WELL_HOLD signal. |
| AAA | no canonical MCP endpoint | healthy | — | Federation state and operator cockpit. A2A gateway at `https://aaa.arif-fazil.com`. |
| A-FORGE | `https://mcp.arif-fazil.com/mcp` | healthy | 52 live (30 stateless + 22 session-bound) | Governed execution shell. All `forge_*` prefixed. |

## arifOS Kernel ABI

The permanent contract is **8 semantic capabilities**: `session.bind`, `reality.observe`, `cognition.think`, `intent.route`, `memory.govern`, `authority.judge`, `action.execute`, and `history.seal`.

The generated `public_agent` profile exposes 6 MCP bindings; `executor` adds execution and `sovereign` adds final sealing. The deployed service still reports 8 because its explicit legacy `forge_next_8` environment value normalizes to the sovereign profile; that is a profile selection, not a second canon.

Machine authority: `arifosmcp/abi/capability_registry.json` and `policy_registry.json`. Generated views: `docs/KERNEL_CAPABILITY_ABI.md`, `smithery.yaml`, `mcp-arifos.json`, and `static/.well-known/mcp/server.json`.

The standalone wiki utilities may exist as implementation helpers or non-canonical utility tools:

- `arif_wiki_ingest`
- `arif_wiki_map`
- `arif_wiki_search`
- `arif_wiki_ask`

They do not replace the canonical 7-verb surface.

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
https://mcp.arif-fazil.com/mcp-discovery-index.json
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
- Some compatibility/docs/runtime strings still contain `L11_AUTH`; canonical map uses `L11_AUDIT`, but full nomenclature normalization is not complete.
- JS/TS symbol extraction now detects `export function`, `export async function`, `export class`, and `export const ... =>` in the local smoke test.
- Latest combined local smoke before this docs audit (pre-2026-07-01):
  `tests/test_canonical.py tests/test_wiki_tools.py tests/test_hybrid_discovery.py tests/test_gdk_compass.py`
  returned `39 passed, 1 failed, 2 errors`. Re-run after any code change.
- The GDK compass errors are test/code contract drift: `tests/test_gdk_compass.py` currently patches `arifosmcp.tools.sense._CompassProcessor`, but that symbol is not present in `arifosmcp/tools/sense.py`.
- The remaining canonical failure is `test_injection_guard_blocks`: `arif_sense_observe(mode="search", query="rm -rf /")` returns `OK` where the test expects `HOLD`.

## Verification Commands

```bash
curl -fsS --max-time 20 https://arifos.arif-fazil.com/health | python3 -m json.tool
for p in 8081 18082 18083 7072; do curl -fsS --max-time 10 "http://localhost:$p/health" | head -c 200; echo; done

python -m py_compile arifos_wiki_tools/*.py \
  arifosmcp/tools/sense.py \
  arifosmcp/runtime/reality_handlers.py \
  arifosmcp/constitutional_map.py

python -m pytest tests/test_canonical.py tests/test_wiki_tools.py tests/test_hybrid_discovery.py tests/test_gdk_compass.py -q --tb=short
```

For public MCP JSON-RPC calls, include both content negotiation headers:

```bash
curl -fsS --max-time 20 -X POST https://mcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## Authority

MCP transports capability. It does not create truth, memory, judgment, or authority.

arifOS is the Governed Action Gateway around MCP: it asks what action is being requested, whether it is allowed, what can go wrong, whether a human must approve, and whether the action can be audited later.

arifOS governs and audits. AAA a2a-server handles deliberation. Arif remains the final sovereign authority.
