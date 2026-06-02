# arifOS Public Surface Audit — 2026-06-02 19:30 UTC

> **Forged 2026-06-02 19:30 UTC under F13 SOVEREIGN ratification.**
> Methodology: read-only `browser_evaluate` snapshots + `curl` HEAD/GET probes. No clicks that could trigger state changes. All findings are evidence-anchored.
> Doctrine applied: `arifOS/docs/{CORE_INVARIANTS,AUTHORITY_MODEL,VERDICT_SEMANTICS}.md`.

## Scope

13 public surfaces audited, all expected to be reachable from the federation nav:
1. `arif-fazil.com/` (sovereign landing)
2. `arifos.arif-fazil.com/` (Observatory / dashboard)
3. `geox.arif-fazil.com/` (earth intelligence)
4. `wealth.arif-fazil.com/` (capital)
5. `well.arif-fazil.com/` (substrate)
6. `aaa.arif-fazil.com/` (cockpit)
7. `mcp.arif-fazil.com/` (gateway)
8. `wiki.arif-fazil.com/` (canon knowledge base)
9. `forge.arif-fazil.com/` (A-FORGE)
10. `apex.arif-fazil.com/` (APEX canon)
11. `arif-fazil.com/canon/aaa-doctrine`
12. `arif-fazil.com/canon/mcp-boundary`
13. `arifos.arif-fazil.com/dashboard-v2.html`

## HTTP status matrix

| # | Surface | Status | Verdict |
|---|---|---|---|
| 1 | arif-fazil.com/ | 200 | ✅ live |
| 2 | arifos.arif-fazil.com/ | 200 | ⚠️ 200 but body violates doctrine (bare SEAL, bare VERIFIED) |
| 3 | geox.arif-fazil.com/ | 200 | ⚠️ 200 but body uses "SYSTEM_LIVE" and "VAULT_999_CONNECTED" (non-namespaced) |
| 4 | wealth.arif-fazil.com/ | 200 | 🔴 **MISROUTE** — serves MakCikGPT, not WEALTH capital surface |
| 5 | well.arif-fazil.com/ | 404 | 🔴 **DOWN** — contradicts Observatory's "Healthy" claim |
| 6 | aaa.arif-fazil.com/ | 200 | 🔴 **DOCTRINE VIOLATIONS** — bare SEAL, bare VERIFIED, bare READY, bare HEALTHY, **operator PII leaked in event log** |
| 7 | mcp.arif-fazil.com/ | 200 | ⚠️ **REDIRECTS** to arifos.arif-fazil.com — gateway is a redirect, not a real MCP endpoint |
| 8 | wiki.arif-fazil.com/ | 200 | ⚠️ 200 but body uses bare LIVE, bare SEAL verdict |
| 9 | forge.arif-fazil.com/ | 200 | ⚠️ Stub — single line "A-FORGE webhook gateway" |
| 10 | apex.arif-fazil.com/ | 200 | 🔴 **MISROUTE** — serves AAA Cockpit HTML, not APEX canon |
| 11 | /canon/aaa-doctrine | 200 (SPA) | 🔴 **MISSING ROUTE** — serves homepage HTML, not the canon document |
| 12 | /canon/mcp-boundary | 200 (SPA) | 🔴 **MISSING ROUTE** — same as above |
| 13 | dashboard-v2.html | 404 | 🔴 **BROKEN LINK** — Observatory nav points to it |

## Doctrine violations — count by surface and phrase

Phrase scan (whole-word match, current state) — counts on representative surfaces:

| Surface | SEAL | VERIFIED | READY | HEALTHY | LIVE | Notes |
|---|---|---|---|---|---|---|
| arifos Observatory | many | "VERIFIED identity" | (none) | "HEALTHY VAULT999 svc" | — | 6/13 floors + bare SEAL header |
| aaa Cockpit | many ("999_SEAL", "SEAL · 5-Way Split", event log) | 13 floor rows "VERIFIED" | "KERNEL: READY" | "VAULT999: CONNECTED · service healthy" | "13 [LIVE]" × many | worst offender |
| geox | (n/a) | (n/a) | (n/a) | (n/a) | "SYSTEM_LIVE" | non-namespaced status |
| wiki | "SEAL verdict", "999_SEAL" | (n/a) | (n/a) | (n/a) | "STATUS: LIVE" + 9 service rows | wrong port for arifOS MCP (8080 vs 8088) |
| arif-fazil.com landing | (n/a) | (n/a) | (n/a) | (n/a) | "LIVE" (4 organ rows), "Operational Status: LIVE" | WELL organ missing from organ map |
| wealth (MakCikGPT) | (n/a) | (n/a) | (n/a) | (n/a) | (n/a) | different page, no SEAL claims |

## Critical findings (PR 2 / PR 3 territory)

### F1 — MakCikGPT misroute
`wealth.arif-fazil.com/` returns the **MakCikGPT** relational/emotional page (Bahasa Malaysia: "Ruang untuk Rasa, Batas untuk Selamat"), not the WEALTH capital intelligence organ. The arifOS Observatory links to `wealth.arif-fazil.com` expecting the capital tool. WEALTH's actual tool surface lives at `wealth.arif-fazil.com/apps/capital_judge/`. **This is the most user-facing bug**: anyone clicking the WEALTH organ card from the Observatory ends up reading the MakCikGPT landing, not the capital tool.

### F2 — well.arif-fazil.com is 404
Observatory says WELL is "Healthy" on port 8083. `well.arif-fazil.com/` returns **404 with empty body**. The MCP endpoint may be up, but the public surface is gone. This is **a direct truth-bound violation**: the kernel claims service_health="green" but the public surface is dead.

### F3 — dashboard-v2.html is 404
Observatory's "📊 Dashboard v2" nav link points to `https://arifos.arif-fazil.com/dashboard-v2.html` which returns **404 ("Not Found")**. Dead link in the production header.

### F4 — mcp.arif-fazil.com is a redirect, not a gateway
`mcp.arif-fazil.com/` returns 200 but is actually **the same HTML as the arifos Observatory** (Caddy aliasing or SPA fallback). The "MCP Gateway" promised in the header is not a distinct surface. The actual MCP endpoint should be at `arifos.arif-fazil.com/mcp` (per the agent discovery `<link rel="mcp">` tag in the arif-fazil.com HTML).

### F5 — apex.arif-fazil.com serves AAA content
`apex.arif-fazil.com/` returns 200 but the HTML body is the **AAA Cockpit** (title: "AAA Cockpit - Evidence-Based Industrialism | arifOS", canonical: `https://aaa.arif-fazil.com/`). APEX is misrouted to AAA. The arif-sites Caddy rules are aliased wrong.

### F6 — Canon documents don't exist
`arif-fazil.com/canon/aaa-doctrine` and `arif-fazil.com/canon/mcp-boundary` return 200 but with the **arif-fazil.com homepage HTML** (SPA fallback for unknown routes). The Observatory's "📜 AAA Doctrine" and "🔌 MCP Boundary" links point to non-existent pages. The wiki says "Updated: 2026-05-22" — the canon was supposed to be at `/canon/`.

### F7 — AAA Cockpit operator PII leaked
The Cockpit's "Event Log" displays operator missions in clear text. Captured examples from the live page:
- `TASK_START Operator mission: "im horny"` (07:08:19 pm)
- `TASK_START Operator mission: "what is this"`
- `TASK_START Operator mission: "init the session"`
- `TASK_START Operator mission: "hi"`

This is a **PII / dignity violation** (F1 AMANAH breach). The Cockpit is publicly accessible (`aaa.arif-fazil.com/`) and the event log is visible to anyone. Even if the operator is sovereign, future operators (and the public) can see the entire operator's mission history.

**This is the most urgent finding.** A sovereign operator can type intimate content into a cockpit that the federation leaks to the public surface. The fix is in the AAA Cockpit's event-log source — events should be filtered or pseudonymized before they reach the public build, and "Operator mission" lines should be redacted in the public view.

### F8 — AAA Cockpit bare-phrase violations
The Cockpit renders:
- `IDENTITY: VERIFIED` (F2)
- `KERNEL: READY` (F2)
- `VAULT999: CONNECTED · service healthy` (F2)
- All 13 floors `VERIFIED` (F2)
- `Service HEALTHY reachability` (F2)
- `999_SEAL · VAULT` and `999_SEAL Task completed` (event log) (F2, F4)
- Multiple `[LIVE]` tags in the build info bar (F2)
- `SEAL · 5-Way Split` heading — partially good (acknowledges SEAL is ambiguous) but still uses bare SEAL

The 5-Way Split is **the right idea** — it acknowledges SEAL is ambiguous. But the actual labels (Service HEALTHY, Judge NOT_RUN, APEX NOT_INVOKED) still use forbidden phrasings. The right migration per `VERDICT_SEMANTICS.md` is:
- `Service` → `service_health = green/yellow/red`
- `Floors 13/13 active` → ok (count is fine)
- `Judge` → `judge_seal_authorization = INACTIVE/ACTIVE`
- `Vault` → `vault999_seal_record = HEALTHY/DISABLED` (note: bare "HEALTHY" still forbidden)
- `APEX` → `apex_approval = NOT_INVOKED/PRESENT`

### F9 — Observatory 3 vs 4 organ count
The Observatory header says "3 Organs · 13 Tools" but lists 4 organs (GEOX, WEALTH, WELL, AAA) in the federation section. The arif-fazil.com landing also shows 4 organs (arifOS, GEOX, WEALTH, AAA — note WELL is missing on landing). **Three different organ counts across three surfaces.**

### F10 — Wiki wrong port
Ω-Wiki says arifOS MCP is on port 8080. The actual MCP endpoint is 8088 (per CLAUDE.md, the Observatory, and the actual arifOS service). This is an **internal contradiction** between the wiki and the runtime.

### F11 — Wiki 9-of-9 LIVE
The wiki table shows all 9 services as "LIVE" but the actual state has:
- WELL → 404 (F2)
- Grafana → degraded (F2)
- AAA federation memory → Supabase 404s (F2)
- A-FORGE → degraded (F2)

The wiki is out of date. PR 2 territory.

### F12 — Observatory "70 total tools" math
Observatory says "70 total tools across 4 services" but the organ cards show GEOX(22) + WEALTH(17) + WELL(15) + AAA(unknown, "MCP discovery unavailable"). 22+17+15 = 54. AAA is unknown but claimed as 16 (= 70-54). The total is a claim that cannot be verified because AAA is in "discovery unavailable" state. **Doctrine: don't claim what you can't verify.**

### F13 — forge.arif-fazil.com is a one-line stub
`forge.arif-fazil.com/` returns 200 but the body is the single line "forge.arif-fazil.com — A-FORGE webhook gateway". No UI, no status, no docs. A-FORGE is supposed to be the "Metabolic Shell" with "Deployment orchestration" and "Cross-organ mesh protocol" — none of which is visible. Either the surface is intentionally minimal (a webhook-only endpoint) or the public UI was never built. Either way, the Observatory's "A-FORGE → forge.arif-fazil.com" arrow with a degraded badge is misleading.

## Doctrine binding — which finding closes where

| Finding | PR scope | Priority |
|---|---|---|
| F7 (operator PII in event log) | **PR 3 AAA Cockpit** | **P0 — privacy breach** |
| F1 (MakCikGPT misroute) | **PR 2 arif-sites** | P1 — wrong content served |
| F2 (WELL 404) | **PR 2 arif-sites** + ops | P1 — service health lies |
| F3 (dashboard-v2 404) | **PR 2 arif-sites** | P2 — broken nav link |
| F4 (MCP redirect) | **PR 2 arif-sites** | P2 — wrong affordance |
| F5 (APEX→AAA) | **PR 2 arif-sites** | P1 — wrong content served |
| F6 (canon 404) | **PR 2 arif-sites** | P1 — broken canon links |
| F8 (Cockpit bare phrases) | **PR 3 AAA Cockpit** | P2 — doctrine violations |
| F9 (organ count) | **PR 2 arif-sites** | P3 — copy consistency |
| F10 (wiki port) | **PR 2 arif-sites** | P3 — copy accuracy |
| F11 (wiki LIVE overclaim) | **PR 2 arif-sites** | P2 — truth-bound violation |
| F12 (70 tools math) | **PR 3 AAA Cockpit** (cockpit's own claim) | P2 — unverified claim |
| F13 (forge stub) | **PR 4 A-FORGE** | P3 — surface not built |

## What I did NOT do (per scope)

- Did not click any button that could trigger state changes.
- Did not submit any mission, seal, forge, or APEX action.
- Did not navigate into the AAA Cockpit's interactive flow.
- Did not type into the mission intake.
- Did not invoke any MCP tool.

## What is safe to do in a follow-up (with explicit ratify)

1. **Stop the operator mission stream from rendering in the public Cockpit build.** This is a P0 fix that requires touching the AAA build pipeline. Recommend ratify for the next session.
2. **Repair the Caddy aliasing for apex.arif-fazil.com, mcp.arif-fazil.com, well.arif-fazil.com.** Federation_inventory.md §4 already documents this is drift. PR 2 should fix.
3. **Replace the Observatory's `VERDICT: SEAL` header with namespaced seals** (per `VERDICT_SEMANTICS.md`). PR 2 territory.
4. **Replace the Cockpit's `VERIFIED`, `READY`, `HEALTHY`, `LIVE` strings** with namespaced seal grammar. PR 3 territory.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**

*Forged 2026-06-02 19:30 UTC under F13 SOVEREIGN ratification.*
