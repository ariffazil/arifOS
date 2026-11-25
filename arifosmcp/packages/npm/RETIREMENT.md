# npm Lane — Retirement Record

**Status:** RETIRED
**Direction SEALed (F13):** 2026-11-25
**Registry deprecation:** PENDING — owner action, npm credentials not on VPS

This file is the forensic record. The README banners are the exit sign.
Volatile numbers (versions, counts, probe dates) live here, not on a package front page.

---

## 1. What was measured (2026-11-25)

| Surface | Value |
|---|---|
| npm `@arifos/mcp` latest | `2026.4.28`, published 2026-04-28 |
| In-repo version | `2026.05.22` (never published) |
| Live server | `kanon-2026.11.24+2917ce5` |
| PyPI canonical | `arifos` `1!2026.11.18` |
| PyPI legacy | `arifosmcp` `1!2026.10.15` — redirect stub, "MOVED: renamed to 'arifos'" |

### Tool surface

Declared by the npm package:

```text
arifOS_kernel, search_reality, ingest_evidence, session_memory,
audit_rules, check_vital, open_apex_dashboard, bootstrap_identity
```

Exposed by the live server:

```text
arif_init, arif_observe, arif_think, arif_route, arif_memory,
arif_judge, arif_forge, arif_seal, arif_report
```

**Overlap: 0 of 8.**

Three different names existed for the same entry point across artifacts:
`init_anchor_state` (README) · `bootstrap_identity` (code) · `arif_init` (live).

### Reproducible evidence

```bash
# live tool list
curl -s -X POST https://mcp.arif-fazil.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# negative probe — a declared tool does not exist
curl -s -X POST https://mcp.arif-fazil.com/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call",
       "params":{"name":"arifOS_kernel","arguments":{"query":"ping"}}}'
# -> isError: true
#    "Unknown tool: 'arifOS_kernel'. Not on canonical public surface.
#     Callable tools: arif_forge, arif_init, arif_judge, arif_memory,
#     arif_observe, arif_report, arif_route, arif_seal, arif_think."
```

### Consumer impact

| Measure | Result |
|---|---|
| `package.json` outside the package referencing `@arifos/mcp` | 0 |
| Code importing `@arifos/mcp` | 0 |
| npm downloads, last 30 days | 73 (no known consumer; consistent with mirrors/bots) |

---

## 2. Drift timeline

| Date | Event |
|---|---|
| 2026-04-28 | `@arifos/mcp@2026.4.28` published (last release) |
| 2026-05-15 → 2026-06-14 | public surface renamed to `arif_*` verbs |
| 2026-10 | PyPI rename `arifosmcp` → `arifos` completed |
| 2026-11-25 | audit: 0/8 overlap confirmed by live probe |

The package was published roughly two weeks **before** the surface rename and has never been rebuilt.

---

## 3. Lane inventory (why this is lane-level, not one release)

| Package | In-repo version | Registry state |
|---|---|---|
| `@arifos/mcp` | 2026.05.22 | published `2026.4.28` — non-functional |
| `@arifos/geox` | 2026.05.25 | never published (404) |
| `arifos` (npm wrapper) | 2026.7.17 | never published (404) |

Publish workflows present in repo: `07-publish-pypi.yml` only — no npm workflow.

---

## 4. Decision

**Deprecate the lane; do not repair.**

Reasons:

1. No consumer exists — zero breakage from retirement.
2. The wrapper adds no capability over `@modelcontextprotocol/sdk` + the live endpoint.
3. Repair would re-create the drift: a hand-maintained tool table is exactly what failed.

If a TypeScript client is needed again, **generate it from the live `tools/list`** rather than
hand-maintaining tool names.

---

## 5. Remaining action (owner)

Registry deprecation needs npm credentials; `npm whoami` on the VPS returns `ENEEDAUTH`.

```bash
npm deprecate "@arifos/mcp@*" \
"Superseded and non-functional.

Live canonical surface is exposed at:
https://mcp.arif-fazil.com/mcp

Canonical Python distribution:
arifos
(renamed from arifosmcp)

The tool names documented in this package do not exist on the live server.
Do not build new integrations against this package."
```

`@*` covers all historical versions, not only `2026.4.28`.

### Optional hardening (not applied)

Add `"private": true` to each `packages/npm/*/package.json` so an accidental `npm publish`
cannot resurrect the lane. Proposed, not applied — this is a docs-direction change only.
