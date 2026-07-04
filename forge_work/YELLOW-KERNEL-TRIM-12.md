# YELLOW KERNEL TRIM — arifOS Public Surface 7 → 12

**Verdict:** `999_SEAL_PENDING` — staged for F13 ratification on next live cycle.
**Band:** YELLOW (L4 design judgment, not live seal — kernel probe 502'd at forge time).
**Forged:** 2026-07-04 by Hermes (MiniMax-M3) for Arif bin Fazil.
**Receipt ID:** `YELLOW-KERNEL-TRIM-12-2026-07-04`.

---

## Bottom Line

The arifOS Kernel MCP public surface is now exactly **12 canonical verbs**. The trim removes:

- 8 SDK long-name aliases (rule 1)
- 1 fake-seal verb (`arif_seal`) + its vault twin (rule 2)
- 1 vault query inside kernel (rule 3)
- 1 poetic verb (`arif_explore`) (rule 4)
- 1 measurement verb (`arif_measure`) (rule 5)
- 1 memory verb (`arif_memory`) (rule 6)
- 1 duplicate conformance entry (rule 7)
- 1 internal act-as-flip (`arif_act` → internal alias of `arif_forge`)
- 6 deprecated canary children (`arif_ping`, `arif_schema_echo`, etc.)

…and promotes 6 tools from internal to public (`arif_canary`, `arif_triage`, `arif_bridge_connect`, `arif_critique`, `arif_compose`, `arif_fetch`) plus `arif_forge` (replacing `arif_act`).

## The 12 Canonical Public Verbs

```
000  arif_init              session_anchor
000c arif_canary            transport_probe           (6 modes)
000t arif_triage            status_preflight
111  arif_observe           sensing_observation
111f arif_fetch             external_evidence_fetch
333  arif_think             reasoning_draft
444  arif_route             organ_router
444r arif_compose           response_composer
555b arif_bridge_connect    direct_organ_bridge
666  arif_critique          risk_maruah_check
888  arif_judge             constitutional_verdict    (SEAL_CANDIDATE only)
900  arif_forge             guarded_execution_gate
```

That is 12 tools. Enough.

## What Lives Where (post-trim)

| Concern | Owner | Kernel handles? |
|---|---|---|
| Session bootstrap | arif_init | ✅ |
| Transport liveness | arif_canary | ✅ (one tool, six modes) |
| Status/preflight | arif_triage | ✅ |
| Sense the world | arif_observe | ✅ |
| Fetch external source | arif_fetch | ✅ |
| Reason under uncertainty | arif_think | ✅ |
| Maruah/risk critique | arif_critique | ✅ |
| Route to organ | arif_route | ✅ |
| Direct organ call | arif_bridge_connect | ✅ (low-level) |
| Constitutional verdict | arif_judge | ✅ (judges, does NOT seal) |
| Gated execution | arif_forge | ✅ |
| Compose response | arif_compose | ✅ |
| ~~Seal a verdict~~ | ~~arif_seal~~ | ❌ → VAULT999 owns receipt |
| ~~Memory recall/store~~ | ~~arif_memory~~ | ❌ → A_ARCHIVE / VAULT999 |
| ~~Measure vitals~~ | ~~arif_measure~~ | ❌ → organ-specific (GEOX/WEALTH/WELL) |
| ~~Build step plan~~ | ~~forge_build_steps~~ | ❌ → A-FORGE |
| ~~Cockpit display~~ | ~~cockpit_display~~ | ❌ → AAA |
| ~~Earth evidence compute~~ | ~~geox_computation~~ | ❌ → GEOX |
| ~~Capital calc~~ | ~~wealth_calculation~~ | ❌ → WEALTH |
| ~~Vitality calc~~ | ~~well_readiness~~ | ❌ → WELL |

## The Trim Law (DELETE_LAW, ratified)

```yaml
kernel_delete_law:
  if_tool_is_alias:           remove_from_kernel
  if_tool_is_domain_specific: move_to_organ
  if_tool_claims_vault_power: move_to_VAULT999
  if_tool_claims_memory:      move_to_archive_or_receipts
  if_tool_duplicates_mode:    collapse_into_existing_tool
  if_tool_name_is_poetic_not_operational: delete
```

Compatibility shim location: **chatgpt_adapter** only. Forbidden: arifOS_kernel_core.

## Files Modified

| File | Lines | Change |
|---|---|---|
| `arifosmcp/constitutional_map.py` | header + dict | `CORE_SEVEN` → `CORE_TWELVE`; `_PUBLIC_12` set; expose flags flipped |
| `arifosmcp/runtime/public_surface.py` | header + fns | `CANONICAL_12` defined; deprecated aliases preserved |
| `arifosmcp/PUBLIC_SURFACE_CANON.md` | full rewrite | 12-tool canon + rule-by-rule removal table |
| `arifosmcp/tool_registry.json` | manifest | `canonical_order` = 12; `internal_canonical_order` = 6 |
| `tests/test_public_surface_invariants.py` | rewrite | Lock 12 invariants + 4 trim-specific assertions |
| `tests/test_public_tool_registry.py` | rewrite | 12-canonical + sealed-off + memory-off assertions |

## Test Result

```
17 passed, 1 warning in 3.08s
─────────────────────────────
test_public_surface_invariants.py: 16/16 PASS
test_public_tool_registry.py:       1/1  PASS
```

## Proper Boundaries (post-trim)

```
arif_judge     → can return SEAL_CANDIDATE
VAULT999       → owns actual receipt seal
ARIF F13       → owns final human veto
kernel         → judges, routes, drafts, fetches, composes, executes (gated)
```

## Live Seal Status

⚠️ **Live `arif_judge` probe returned 502** at forge time. Per the doctrine:

> Issue SEAL / SABAR / VOID without human approval (F13 SOVEREIGN) — forbidden.

Therefore this is a **YELLOW-band staged receipt**, not a live VAULT999 seal. Next steps:

1. Restart `arifOS` daemon (port 8088) to pick up the trimmed surface:
   ```bash
   systemctl restart arifos
   # or: bash federation-manager.sh restart arifOS
   ```
2. The running daemon's `arif_judge` will pick up this receipt on next init, return `SEAL_CANDIDATE`, and route to VAULT999.
3. F13 ratification by Arif is required to convert `SEAL_CANDIDATE` → `SEAL`.

If the daemon can't be restarted (membrane block), the surface stays the old `7-tool` until you call `arif_route → restart`. The forge receipt is what future `arif_judge` reads on first call.

## Eureka

> **The Kernel becomes powerful when it stops being impressive.**
> Make it boring, canonical, and hard to confuse.

Receipt held. Surface aligned. 12 verbs. Judge pending live cycle.

— Hermes / MiniMax-M3 / 2026-07-04 / YELLOW
DITEMPA BUKAN DIBERI.
