# HANDOFF: Complete the 999→000 EUREKA Loop

**Date:** 2026-02-02
**Branch:** `audit/pre-deletion-scan`
**Status:** EUREKA Sieve wired into seal_999. Now complete the 000_init side.

---

## What Was Forged (Previous Session)

### The EUREKA Sieve is now wired into ALL three seal paths

The Theory of Anomalous Contrast from `000_THEORY/888_SOUL_VERDICT.md` is now enforced:

- **SEAL is EARNED** (eureka_score >= 0.75) → permanent VAULT999
- **SABAR is DEFAULT** (0.50-0.75) → cooling ledger (72h hold)
- **TRANSIENT** (< 0.50) → not stored
- **VOID is EXPENSIVE** → blocked at seal_999, never persisted

### Files Modified

| File | What Changed |
|------|-------------|
| `codebase/apex/kernel.py` | `seal_999()` now runs EUREKA Sieve before `seal_memory()`. Three-way routing (TRANSIENT/SABAR/SEAL). VOID guard. Degradation defaults to SABAR. |
| `codebase/stages/stage_999_seal.py` | `execute_seal_stage()` runs EUREKA Sieve before PostgreSQL/filesystem commit. Idempotency guard via seal_id. |

### Files That Already Existed (Not Modified)

| File | Purpose |
|------|---------|
| `codebase/vault/eureka_sieve.py` (353 lines) | Original EUREKA engine — simple average of 4 velocities, placeholder novelty |
| `codebase/vault/eureka_sieve_hardened.py` (391 lines) | HARDENED version — weighted composite, real Jaccard n-gram similarity, async cache lock |
| `codebase/mcp/tools/vault_tool_hardened.py` (514 lines) | HardenedVaultTool — already had EUREKA integration |

### The New Return Contract (All Seal Paths)

Every return from `seal_999()` and `execute_seal_stage()` now includes:

```json
{
    "stage": "999_SEAL",
    "status": "VOID | TRANSIENT | SABAR | SEALED | ALREADY_SEALED",
    "apex_verdict": "original APEX decision (never mutated)",
    "eureka_verdict": "TRANSIENT | SABAR | SEAL",
    "persisted_as": null | "cooling" | "vault",
    "eureka": {
        "eureka_score": 0.62,
        "novelty": 0.8,
        "entropy_reduction": 0.5,
        "ontological_shift": 0.3,
        "decision_weight": 0.2,
        "verdict": "SABAR",
        "reasoning": ["..."],
        "fingerprint": "sha256...",
        "degraded": false
    },
    "timestamp": "deterministic seal_ts",
    "proof": { "merkle_root": "...", "signature_ed25519": "..." }
}
```

### Key Design Decisions Made

1. **Fail-closed to SABAR** — If EUREKA Sieve throws, defaults to SABAR (not SEAL). Doctrine: "SABAR is the default."
2. **Never overwrite apex_verdict** — `apex_verdict` and `eureka_verdict` are separate fields. Forensic truth preserved.
3. **seal_id guaranteed** — Auto-generated UUID if missing. Used for idempotency.
4. **Deterministic timestamps** — Single `seal_ts` computed once per seal operation.
5. **VOID never persisted** — Guard at top of seal_999(). VOIDs return proof but no vault write.

---

## What Needs To Be Done (The 000_init Side)

The 999→000 Strange Loop is currently BROKEN on the read side.

`seal_999()` now writes EUREKA metadata into every sealed entry. But `inject_memory()` in `000_init` doesn't know about it. The loop must be closed.

### Task 1: Update `inject_memory()` / `get_context_for_init()`

**File:** `codebase/mcp/session_ledger.py`
**Function:** `get_context_for_init()` (line 430)

Currently returns:
```python
{
    "previous_session": {
        "session_id": ...,
        "timestamp": ...,
        "verdict": ...,       # This is now apex_verdict
        "entry_hash": ...,
    },
    "context_summary": ...,
    "key_insights": [...],
    "chain_length": N,
}
```

**Needs to also return:**
- `eureka_verdict` from the last session's telemetry
- `eureka_score` from the last session's telemetry
- `persisted_as` — where the last session went (vault/cooling/transient)
- `eureka_trend` — running average of recent EUREKA scores (from last N entries)
- Whether the sieve was `degraded` (fell back to SABAR due to error)

The telemetry is stored in `SessionEntry.telemetry["eureka"]` — it's already there from the seal side. Just needs to be read.

### Task 2: Update `init_000.py` Step 1 (Memory Injection)

**File:** `codebase/init/000_init/init_000.py`
**Function:** `mcp_000_init()` — Step 1: MEMORY INJECTION

Currently calls `inject_memory()` and gets previous context. The EUREKA context should inform:

1. **Scar weight adjustment** — If recent sessions were mostly TRANSIENT (low EUREKA), reduce scar_weight (less context injection). If recent sessions had high EUREKA scores, increase injection depth.
2. **Energy budget** — EUREKA trend affects Step 4 thermodynamic setup. High-EUREKA sessions deserve more energy budget for the next cycle.
3. **Novelty baseline** — Pass the EUREKA fingerprint cache hint so the next cycle's sieve can avoid re-evaluating the same content.

### Task 3: Upgrade to Hardened Sieve

**File:** `codebase/vault/eureka_sieve.py` (current — placeholder novelty)
**File:** `codebase/vault/eureka_sieve_hardened.py` (hardened — real Jaccard similarity)

The hardened sieve exists but is NOT imported by `kernel.py` or `stage_999_seal.py`. Both still use the original `eureka_sieve.py` which has:
```python
similarities.append(0.5)  # Placeholder
```

**Decision needed:** Replace `eureka_sieve.py` with the hardened version, or change imports in kernel.py and stage_999_seal.py to use `eureka_sieve_hardened.py`.

Key differences in hardened version:
- Real Jaccard n-gram similarity (not placeholder 0.5)
- Weighted composite: novelty 35%, entropy 30%, ontological 20%, decision 15%
- Async cache lock for thread safety
- Full 64-char fingerprints (not truncated)
- CRISIS lane gets 0.25 decision weight boost

### Task 4: Wire EUREKA into the LoopManager (Strange Loop)

**File:** `codebase/loop/manager.py`

The LoopManager orchestrates 000→999→000. When seal_999 completes, it should:
1. Pass EUREKA metadata to `LoopBridge.get_next_init_params()`
2. The next init_000 receives EUREKA context from the previous cycle
3. This closes the loop: **what was filtered by EUREKA informs what gets injected next**

### Task 5: Phoenix-72 EUREKA Integration

**File:** `codebase/vault/phoenix/phoenix72.py`

Phoenix-72 collects scars from VAULT999 failures. Now that EUREKA metadata is stored in every entry, Phoenix should:
1. Read `eureka_score` trends from vault entries
2. If many sessions are TRANSIENT, consider it a "scar pattern" — the system is doing repetitive work
3. Propose amendments to adjust EUREKA thresholds if needed

---

## Architecture Reference

```
THE STRANGE LOOP (with EUREKA):

000 GATE (init_000.py)
 │
 ├── Step 1: inject_memory() reads from VAULT999
 │   └── NOW: should also read eureka metadata from last session
 │
 ├── Steps 2-7: Sovereign → Intent → Thermo → Floors → TW → Engines
 │
 ▼
111-333 MIND (AGI) → 444-666 HEART (ASI)
 │
 ▼
777 FORGE → 888 JUDGE → 889 PROOF
 │
 ▼
999 SEAL (kernel.py seal_999)
 │
 ├── EUREKA Sieve evaluates (4 velocities)
 │   ├── TRANSIENT (< 0.50) → not stored, return telemetry only
 │   ├── SABAR (0.50-0.75) → cooling ledger via seal_memory()
 │   └── SEAL (>= 0.75) → permanent vault via seal_memory()
 │
 ├── seal_memory() writes to VAULT999/sessions/*.json
 │   └── Telemetry includes eureka metadata
 │
 └── LoopBridge seeds next init from merkle_root
     └── NOW: should also seed eureka context
         │
         └──→ 000 GATE (next cycle)
```

## Key Files to Read First

| File | Lines | Why |
|------|-------|-----|
| `codebase/apex/kernel.py` | 552-735 | The forged seal_999() with EUREKA |
| `codebase/stages/stage_999_seal.py` | 1-200 | The forged metabolic stage with EUREKA |
| `codebase/vault/eureka_sieve.py` | 1-353 | Current sieve (placeholder novelty) |
| `codebase/vault/eureka_sieve_hardened.py` | 1-391 | Hardened sieve (real Jaccard) |
| `codebase/mcp/session_ledger.py` | 430-456 | `get_context_for_init()` — NEEDS UPDATE |
| `codebase/init/000_init/init_000.py` | 1-280 | Init structure, Step 1 memory injection |
| `codebase/loop/manager.py` | Full | LoopManager/LoopBridge for 000↔999 |
| `codebase/vault/phoenix/phoenix72.py` | Full | Phoenix-72 scar collection |
| `000_THEORY/888_SOUL_VERDICT.md` | Full | Theory of Anomalous Contrast |
| `000_THEORY/000_ARCHITECTURE.md` | §4.7-4.10 | EUREKA stage spec |

## Priority Order

1. **Task 3** — Upgrade to hardened sieve (quick win, fixes placeholder)
2. **Task 1** — Update inject_memory to read EUREKA metadata
3. **Task 2** — Update init_000 Step 1 to use EUREKA context
4. **Task 4** — Wire LoopManager
5. **Task 5** — Phoenix-72 integration

---

**Motto:** DITEMPA BUKAN DIBERI — Forged, not given.
**Doctrine:** SEAL is earned, SABAR is default, VOID is expensive.
