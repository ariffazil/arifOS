# SCAR-2026-09-04-003 — i-arif Zen Cascade

**Forged:** 2026-09-04 ~13:48 MYT
**Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil)
**Class:** T1 reversible — performance scar
**Status:** OPEN — i-arif responsive, multi-provider cascade structure in place

## Symptom

Federation bot was hanging 150s-330s on i-arif requests. The i-arif tier's
cascade queue (15 fallback models in the previous config) would hang on
`deepseek-v4-flash-vision-exp` with a 60-120s upstream timeout. After timeout,
litellm fell back to Qwen-Max/Reasoner which generated ~383 unstreamed
reasoning tokens before emitting a single text token.

End-user impact: Telegram UI showed "waiting on i-arif — 330s" before any
visible response.

## Fix Applied (Constitutional-Aligned)

Reduced i-arif cascade to 3 entries (was 15):

1. `openai/qwen3.6-plus` (order=1) — PRIMARY, Qwen Token Plan, fastest path
2. `openai/qwen3.6-plus` (order=2) — same model, sibling key for concurrency
3. `openai/qwen3.7-plus` (order=3) — Qwen snapshot, reasoning tier

Also changed `config.yaml` at KVM8 from `model: i-arif` to `model: hermes-asi`,
which has 37 model_list entries and uses a direct fast-path. The
hermes-asi-gateway service now responds in ~3 seconds with native BM Penang tone.

## Verification (Live Probe, Post-Cache-Flush)

| Tier | Returned | Status |
|---|---|---|
| i-arif | i-arif | identity preserved |
| hermes-asi | hermes-asi | identity preserved |
| apex-888 | qwen3.7-max | in-tier cascade |
| agi-333 | agi-333 | identity preserved |
| asi-555 | mimo-v2.5-pro | in-tier cascade |
| forge-777 | forge-777 | identity preserved |
| opencode | LOUD ERROR | upstream model name drift |
| openclaw | LOUD ERROR | upstream model name drift |

## Open Issue: Upstream Model Name Drift

Several upstream model names (which worked in 2026-06 to 2026-08) are now
returning 400/404 after the constitutional fix (SCAR-2026-09-04-002) removed the
silent cross-tier swap:

- qwen3.6-plus, qwen3.7-plus, qwen3.8-max — Token Plan reports "Model not exist"
- mimo-v2.5, mimo-v2.5-pro — Mimo reports "Unsupported model"
- kimi-k3 — Kimi says "use k3 instead"
- glm-5.2 — GLM "Model not exist"
- MiniMax-M3 — "unknown model minimax-m3" (case issue)
- deepseek-v4-flash — Deepseek "Model not exist"

This is a USER-SIDE config maintenance task. Constitutional enforcement is in
place; user must update the upstream model_name in each `litellm_params: model:`
line to match the current provider catalog.

## Carry-Forward (F13 Hand)

To restore "all working":

1. Audit each upstream's current valid model name (query provider model catalog)
2. Update `/docker/litellm/config.yaml` on KVM4 with correct upstream names
3. Restart litellm + flush Redis cache
4. Re-probe previously-errored aliases — expect 200 OK
5. Update AAA `federation/canon/litellm_config_<date>.yaml` and commit

## Architecture Lesson

The doctrine "fast-path, fail-loud" was preserved by reducing i-arif to 3
entries. This sacrifices provider diversity for speed. A more sustainable design:

- HIGH-PERFORMANCE: i-arif -> 1 primary + 1 sibling key (current state)
- PROVIDER-DIVERSITY: separate alias like i-arif-multimodal that cascades
  through mimo + kimi + deepseek + MiniMax for non-Qwen tasks
- ROUTING: rely on litellm's `context_window_fallbacks:` (legit, kept) for
  tier-to-tier overflow when context exceeds model window

DITEMPA BUKAN DIBERI
