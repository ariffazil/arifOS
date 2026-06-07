# tool_registry_v2.json — Purpose Label (Ω — 2026-06-07)

> **Role:** WORKING ROADMAP — state machine for tool promotion
>
> **Tool count:** 79 (distributed: 26 LIVE / 23 HOLD / 30 FORGED)
>
> **State semantics:**
> - `LIVE` — currently callable on arifOS MCP (sanity-check against `tool_registry.json`)
> - `HOLD` — gated by F1-F13 floors, awaiting conditions (JUDGE_SEAL_AUTHORIZATION, etc.)
> - `FORGED` — implementation complete, awaiting sovereign release
>
> **Used by:** A-FORGE `/api/repo-steward/registry-trinity` (working_roadmap role)

## Drift Signal (2026-06-07 audit)

The v2 file declares **26 LIVE** tools, but `tool_registry.json` (canonical) declares **13**. This means 13 entries in v2 are marked LIVE that aren't on the canonical surface. Possible causes:

- v2 was last regenerated during a transition window and never re-validated
- 13 tools were retired/archived but not yet marked FORGED in v2

**Recommended action:** Re-run `arifOS /inspector/sot` and reconcile. Either:
- Promote the 13 missing tools to canonical (if intentional), OR
- Demote them to HOLD/FORGED in v2 (if retired)

**Authority:** A-FORGE observes, doesn't execute. arifOS `/api/judge/deliberate` adjudicates.

DITEMPA BUKAN DIBERI.
