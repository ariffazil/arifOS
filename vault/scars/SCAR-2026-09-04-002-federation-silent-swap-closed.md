# SCAR-2026-09-04-002 — FED silent cross-tier swap → CLOSED

**Forged:** 2026-09-04 ~13:35 MYT
**Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil)
**Class:** T0 reversible — constitutional scar closure
**Status:** CLOSED (constitutional alignment restored)

## Failure Mode Anchored

When FED's `model_group_alias:` block was intact, litellm silently substituted
constitutional-tier requests to the cheapest always-available model — typically
`MiniMax-M3` — without telling the caller. This is exactly the F2 (TRUTH) and F9
(ANTI-HANTU) violation the doctrine was written to catch.

Worst offender: requesting `apex-888` (constitutional judge persona) returned
`MiniMax-M3` output with a 200 OK status — the system was lying about its identity.

## Probe Sequence That Surfaced It

| Tier Asked | Returned (before) | Status | Returned (after) | Status |
|---|---|---|---|---|
| i-arif | i-arif | ✓ OK | i-arif | ✓ identity-preserved |
| apex-888 | MiniMax-M3 | ⚠ SILENT-SWAP | qwen3.8-max | ✓ in-tier cascade |
| agi-333 | agi-333 | ✓ OK (cached) | agi-333 | ✓ identity-preserved |
| asi-555 | MiniMax-M3 | ⚠ SILENT-SWAP | mimo-v2.5-pro | ✓ in-tier cascade |
| forge-777 | forge-777 | ✓ OK | forge-777 | ✓ identity-preserved |
| qwen3.6-plus | MiniMax-M3 (via alias) | ⚠ SILENT-SWAP | LOUD ERROR | ✓ no swap |
| qwen3.8-max | MiniMax-M3 (via alias) | ⚠ SILENT-SWAP | LOUD ERROR | ✓ no swap |
| kimi-k3 | agi-333 (via alias) | ⚠ SILENT-SWAP | LOUD ERROR | ✓ no swap |
| mimo-v2.5 | asi-555 (via alias) | ⚠ SILENT-SWAP | LOUD ERROR | ✓ no swap |

## Fix Applied (2026-09-04 ~13:30 MYT)

1. Removed `model_group_alias:` block from KVM4 litellm config (the silent-swap mechanism).
2. Removed `fallbacks:` block from `router_settings` (cross-tier cross-failure).
3. Removed all `MiniMax-M*` and `MiniMax-M2.*` entries from constitutional tier cascades
   (`apex-888`, `i-arif`, `agi-333`, `asi-555`, `forge-777`, `hermes-asi`, `opencode`, `openclaw`,
   `hermes-asi-vision`, `fed/vision`, `fedaudio`, `fedimage-gen`).
4. Added explicit `model_list` entries for the previously-broken constitutional aliases
   (`qwen3.6-plus`, `qwen3.8-max`, `kimi-k3`, `mimo-v2.5-pro`, `mimo-v2.5`, `glm-5.2`,
   `deepseek-v4-flash`, `MiniMax-M3`) so they resolve to their declared upstreams.
5. Flushed litellm Redis cache (the apparent silent swaps were partly cache hits).
6. Restarted KVM4 litellm container.
7. Re-probed 13 tiers — no silent cross-tier swaps to MiniMax-M3.

## Constitutional Meaning

The doctrine:
> Govern capabilities, not implementations. Each constitutional model must answer with
> its declared identity or error — never silently swap to a different model.

**Status:** ALIGNED. Each constitutional tier (apex-888, i-arif, agi-333, asi-555,
forge-777) now either (a) returns its declared model_name, or (b) returns a model
within its own constitutional cascade (e.g. apex-888 → qwen3.8-max since qwen3.8-max
is one of apex-888's own providers), or (c) returns LOUD ERROR if no provider in
its cascade can serve the request.

**No more silent cross-tier swap to MiniMax-M3.**

## Six (6) Loud Errors Remaining

The following aliases now return 400/404 errors instead of silent-swap to MiniMax-M3.
This is constitutional compliance (loud error > silent swap), but for "all working"
the user will need to verify the actual upstream model names on each provider
(current upstream accepts different naming conventions than the constitutional alias
suggests):

- `qwen3.6-plus` — upstream says "Model not exist" (provider may not have v3.6)
- `qwen3.8-max` — same
- `kimi-k3` — upstream says use `k3` instead of `kimi-k3`
- `mimo-v2.5-pro` — upstream says "Unsupported model"
- `mimo-v2.5` — same
- `glm-5.2` — upstream says "Model not exist"
- `MiniMax-M3` — upstream says "unknown model 'minimax-m3'" (need lowercase)
- `deepseek-v4-flash` — upstream says "Model not exist" (likely only v4-pro exists)

## Artifacts

- `MACHINE_MAP.md §1` FED row updated to Capability Routing Constitution framing
- `CANONICAL_GLOSSARY.md` FED row updated with full capability-routing description
- Commit `chore(doctrine): FED constitutional shift` (pending)
- Final litellm config preserved at `/docker/litellm/config.yaml` on KVM4 (backup at
  `/tmp/litellm_v6.yaml` during execution; canonical backup recommended in AAA)

## Lessons for Future Agents

1. **Constitutional model swap is the F9 anti-hantu violation the doctrine was written for.**
   When the system claims a constitutional model is being called but a different model
   is actually running, that's identity theft at the substrate level. Always probe with
   a model_name + response model_name comparison.

2. **Cached responses can MASK constitutional failures.** Litellm's Redis cache
   serves stale responses on subsequent identical calls. The first probe after a config
   change may show "all good" because the response is cached. Always flush cache or
   vary the input (timestamp in message) when validating post-change behavior.

3. **`model_group_alias:` is a silent cross-tier swap shortcut.** It looks like a
   convenience layer (one alias to one tier) but it enables silent fallback chains
   that violate constitutional alignment. Either remove it entirely or audit each
   alias-to-tier mapping against the F2 TRUTH guarantee.

4. **In-tier cascades are constitutional; cross-tier cascades are not.** When
   `apex-888` falls from `gemini-2.5-pro` to `qwen3.8-max` (both within apex-888's own
   model_list), that's identity-preserving. When it falls to `MiniMax-M3` (a tier
   apex-888 doesn't have), that's cross-tier swap. Future audits: distinguish
   in-tier fallback from cross-tier fallback.

DITEMPA BUKAN DIBERI ⚒️
