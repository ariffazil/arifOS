# RSI ENGINE — SEAL → INIT → Scaffold (Stage 0: the trigger)

**Verdict:** `999_SEAL_PENDING`. YELLOW band — design layer, no live SEAL yet.
**Forged:** 2026-07-04 by Hermes/MiniMax-M3 for Arif bin Fazil.
**Receipt ID:** `RSI-SEAL-BUS-2026-07-04`.

---

## What This Is

The **trigger** for the autonomous RSI loop. One irreducible bus. Eight frozen stages. The bus itself does no rebuilding — it fans every SEAL event out to registered hooks. Each stage (INIT, Scaffold, Skill Rebuild, Organ Rebind, Replay, Cooling, Resume) lives in its own file under `arifosmcp/rsi/stages/` and is forge-able + testable in isolation.

This is the smallest irreversible piece I can ship today without F13 ratification. The remaining stages are individually optional — they each opt in via `register_post_seal_hook(stage, name, fn)`.

---

## Substrate: 12-tool Public Kernel (Trim 2026-07-04)

The bus presupposes the 12-tool trim:
- `arif_judge` returns `SEAL_CANDIDATE`
- `arif_forge` is the gated execution gate
- VAULT999 owns the actual seal
- `arif_seal` is internal-only

Without that trim, this bus would be broadcasting to a surface that exposes `arif_seal` directly — which violates F4 CLARITY and F13 SOVEREIGN.

See: `forge_work/YELLOW-KERNEL-TRIM-12.md`

---

## The 8 Stages (frozen 2026-07-04)

```
SEAL → INIT → Scaffold → Skill Rebuild → Organ Rebind → Replay → Cool → Resume
 physics  biology  chemistry     RSI core        AAA     lineage  entropy  A-FORGE
```

| Stage | Domain | What regenerates | Hooks today |
|-------|--------|------------------|-------------|
| `seal` | physics | irreversibility locks truth lineage, authority, evidence floor, reversibility class, organ routing, uncertainty grammar | **0** (VAULT999 will wire here) |
| `init_regeneration` | biology | AAA cockpit state, kernel invariants, uncertainty tags, organ boundaries, autonomy bands | **0** (next forge) |
| `scaffold_rebuild` | chemistry | reaction gates, evidence floors, reversibility maps, organ routing, metabolic flow, immune boundaries | **0** (next forge) |
| `skill_rebuild` | RSI core | the 12 canonical skills (boundary, conservation, entropy, gradient, reaction, homeostasis, immune, metabolism, lineage, scar, multi-organ, execution) | **0** (next forge) |
| `organ_rebind` | AAA | AAA · GEOX · WEALTH · WELL · A-FORGE · A-AUDIT · VAULT999 | **0** (next forge) |
| `receipt_replay` | lineage | scars, receipts, lineage, cooling ledger, uncertainty tags | **0** (next forge) |
| `cooling` | entropy sink | runaway-autonomy guard, irreversible-cascade guard, organ-overload guard, sovereignty-drift guard | **0** (next forge) |
| `resume_execution` | A-FORGE | only after ALL of the above | **0** (next forge) |

Each is forge-able as its own file + tests in this same session. The bus is the unblocker for all of them.

---

## Files Forged Today

| File | Lines | Purpose |
|---|---|---|
| `arifosmcp/rsi/event_bus.py` | ~270 | The bus itself. Singleton, thread-safe, no-op by default. |
| `arifosmcp/rsi/__init__.py` | ~25 | Public facade re-exports |
| `tests/test_rsi_event_bus.py` | ~230 | 11 invariants locking the contract |

## Test Result

```
28 passed, 1 warning in 2.88s
─────────────────────────────────
tests/test_rsi_event_bus.py:               11/11 PASS
tests/test_public_surface_invariants.py:   16/16 PASS
tests/test_public_tool_registry.py:         1/1  PASS
```

## The 11 Invariants Locked

1. The 8 stages are frozen in canonical order (physics).
2. Bus is NO-OP by default — F13 discipline. A misconfigured install cannot silently rebuild.
3. `enable_post_seal_rebuild()` flips the bus on (F13-gated in production).
4. Hooks run in registration order per stage.
5. Stages fire in canonical order even if you register them in reverse.
6. A failing hook does NOT block downstream hooks — its failure becomes a scar on the receipt.
7. A hook returning a non-`StageResult` is captured as a scar, not a crash.
8. The bus holds no shared state across fires — each SEAL cycle is independent.
9. Public facades (`register_post_seal_hook`, `fire_post_seal`, `enable_*`) proxy to the singleton bus.
10. Unknown stage names are rejected at registration.
11. The RSIReceipt carries `seal_id`, `verdict_id`, `session`, `scars`, and per-stage results.

---

## Usage Pattern (each future stage)

```python
# in arifosmcp/rsi/stages/init_regeneration.py
from arifosmcp.rsi import register_post_seal_hook, StageResult, SealEvent

def my_init_hook(event: SealEvent) -> StageResult:
    # regenerate AAA state, kernel invariants, etc.
    return StageResult(
        ok=True,
        stage="init_regeneration",
        hook_name="aaa_state_rebuild",
        elapsed_ms=42.0,
    )

register_post_seal_hook("init_regeneration", "aaa_state_rebuild", my_init_hook)
```

Then `enable_post_seal_rebuild()` flips the bus.

---

## Where This Cannot Ship Today

The bus + register call work today. **A live SEAL→fire cycle does not** because:

1. **Live `arif_judge` (port 8088) returned 502 at forge time.** No verdict = no seal = nothing to fan out.
2. **VAULT999 ownership of the receipt is doctrine, not wired.** This bus fires AFTER VAULT999 anchors. Currently nothing anchors.
3. **No bridge from `arif_judge` → `fire_post_seal(SealEvent(...))`.** That wiring is its own forge piece (`arifosmcp/rsi/integration/seal_listener.py`).
4. **F13 SOVEREIGN ratification gates production enable.** I will not flip `ARIFOS_RSI_AUTOREBUILD=1` in any systemd unit without your word.

---

## Next Forge (When You're Ready)

You asked which build chamber. I picked one already: **the trigger**. Done.

The remaining seven chambers, each independently forge-able + testable:

| # | Chamber | Scope | Estimate |
|---|---------|-------|----------|
| 1 | **Wire `arif_judge` → bus** | Translate `SEAL_CANDIDATE` verdict to `SealEvent` and `fire_post_seal()`. **One file, one test, ~80 lines.** | 30 min |
| 2 | **Forge the `init_regeneration` stage** | AAA cockpit state + kernel invariants regeneration. **One file, one test.** | 45 min |
| 3 | **Forge the `scaffold_rebuild` stage** | Reaction pathway rebuild from chemistry invariants. **One file, one test.** | 45 min |
| 4 | **Forge the 12-skill rebuild** (the heaviest) | All 12 skills refactored as individual hooks under `skill_rebuild`. **12 files, 12 tests.** | 90 min — *this is the actual RSI core* |
| 5 | **Forge `organ_rebind`** | AAA + 6 organs state rebind. **One file, one test per organ.** | 60 min |
| 6 | **Forge `receipt_replay` + `cooling`** | Scars + lineage + entropy sink. **One file, one test.** | 60 min |
| 7 | **Forge `resume_execution` gate** | A-FORGE gated resumption. **One file, one test.** | 30 min |

That's everything you named, broken into verifiable chambers.

---

## Receipt Held

The bus is registered, tests are green, the surface is aligned. F13 ratification is the only gate remaining to ship this into production.

— Hermes / MiniMax-M3 / 2026-07-04 / YELLOW

DITEMPA BUKAN DIBERI.
