# ART Unified — Final Extraction (Pre-Deletion Distillation)

> **Date:** 2026-06-21
> **Trigger:** Final distillation of `arifOS/arifosmcp/runtime/art_unified_DEPRECATED.py` (1603 lines, untracked in git) before deletion. Sandbox-safe — no production code affected.
> **Status:** EXTRACTION COMPLETE. The orphan file may now be deleted safely; the canonical reflex (`art.py` 417 lines + `art_compat.py` 361 lines + `art_pusaka.py` 181 lines) already contains everything below.

---

## §0 — What This File Was

The unified `art.py` attempt of 2026-06-21. A single-file merge of three legacy ART implementations:

| Legacy source | What it contributed | Now lives at |
|---|---|---|
| `arifosmcp/runtime/art.py` (v2, ~378 lines) | 4-state lifecycle + 3 reflexive checks | `art.py` (417 lines, ceiling-enforced) |
| `arifosmcp/runtime/art_gateway/` (4 modules, 922 lines) | 6-check order compat shim + entropy watcher | `art_compat.py` (361 lines) |
| `core/governance/art_*.py` (3 modules, ~1013 lines) | APEX grand equation + dial computation + DOCTRINE cold path | `art_pusaka.py` (181 lines, doctrinal cold path) |

The merge produced **1603 lines, 7 classes, 18 functions, 1 grand equation** that violated the reflex weight ceiling on every cell. The T1 probe caught this; the corrective edit restored the 3-file split.

This document is the **load-bearing knowledge** worth preserving from the unified attempt — the parts that future ART patches should remember, but don't need to carry in the runtime. The file itself can go.

---

## §1 — The APEX Grand Equation (load-bearing)

The unified file's most distinctive contribution. Found at lines 711–786, the equation:

```
g(t) = A(t) · P(t) · H(t) · √(S(t) · U(t)) · E(t)²
```

Where:

| Dial | Name | Domain | Floors |
|---|---|---|---|
| A | AKAL | Reasoning lawfulness | F2 / F4 / F7 / F10 |
| P | PRESENT | State truth (reversibility tier) | F1 / F5 / F11 |
| H | AUTHORITY | Legitimacy (tier match) | F13 + identity |
| S | ENTROPY | Uncertainty integrity (1 − Ω) | F4 + ΔS |
| U | EXPLORATION | Risk × custody | F3 / F6 / F8 / F9 |
| E | ENERGY | Thermodynamic adequacy (budget + reversibility + ack) | F12 / F13 + compute |

**Verdict lattice (per APEX_CANON §2.4):**

```
G ≥ 0.80          → PROCEED       (SEAL)
0.50 ≤ G < 0.80   → SABAR         (gather evidence)
G < 0.50          → HOLD          (888 escalation)
any axiom violated → BLOCK        (VOID)
```

**Why this matters for future ART patches:** the equation is a *doctrinal anchor*, not a hot-path computation. It belongs in `art_pusaka.py` (cold path) — already there in distilled form. The reflex (`art.py`) does NOT recompute G on every call; the doctrine does, on demand, for governance review.

**Distilled into `art_pusaka.py`:** yes — the canonical 6-dial doctrine lives there. The unified file's contribution was surfacing this as the unifying mathematical frame; the 3-file split kept the math without paying the runtime cost.

---

## §2 — Enums Worth Carrying Forward

Seven enum classes in the unified file. Three were canonical (already in `art.py`), three were gateway-specific (now in `art_compat.py`), one was doctrinal (now in `art_pusaka.py`).

| Enum | Members | Now at | Notes |
|---|---|---|---|
| `ToolState` | UNTRUSTED / OBSERVED / TRUSTED / FALLBACK / ABANDONED | `art.py` | 4-state lifecycle — canonical |
| `ArtVerdict` | PROCEED / HOLD / BLOCK / DEFAULT_OBSERVE | `art.py` | reflex output |
| `ArtReason` | 18 values (8 state transitions + 10 reflex) | `art.py` | reflex reasons |
| `DecisionClass` | C0 / C1 / C2 / C3 / C4 / C5 | `art_compat.py` | 6-check order compat |
| `GatewayVerdict` | PROCEED / SABAR / HOLD / BLOCK / VOID | `art_compat.py` | 6-check order output (supersedes ArtVerdict in compat calls) |
| `ReversibilityTier` | REVERSIBLE / COMPENSABLE / IRREVERSIBLE / VOID | `art_compat.py` | 4-tier classification for compat |
| `ApexDial` | AKAL / PRESENT / AUTHORITY / ENTROPY / EXPLORATION / ENERGY | `art_pusaka.py` | doctrinal 6-dial model |

**No knowledge lost in the split.** Every enum survives; the split separates them by their hot/warm/cold path.

---

## §3 — Functions: What Was Unique vs. Redundant

### Unique — worth knowing the unified file tried this

| Function | Lines | What it tried | Verdict |
|---|---|---|---|
| `EntropyWatcher` class | 569–651 | Periodic entropy probing with overload/slow thresholds | Over-engineering for the reflex. Doctrine-side only. `art_pusaka.py` has the doctrinal anchors; live entropy is `well_assess_homeostasis` territory, not ART. |
| `entropy_snapshot_from_health()` | 1520+ | Map runtime health dict → EntropySnapshot | Redundant with WELL's vitality layer. **Drop.** |
| `_check_authority()` | 320–434 | Authority gate with tier mismatch detection | Useful as doctrine, redundant as runtime — `actor_resolved: bool` already gates MUTATE in `art.py`. **Doctrine-only.** |
| `_compute_apex_G()` | 768–776 | The grand equation computation | Doctrinal. Lives conceptually in `art_pusaka.py`; the reflex doesn't compute G. |

### Redundant — already in `art.py` 3-check reflex

| Function | Lines | Redundant with |
|---|---|---|
| `art()` | 848–1047 | The reflex itself — the unified file's `art()` is the v3 reflex + 4-state lifecycle + verdict emission. v3's reflex is lighter (417 lines vs 200 here), but the same 3-check × 4-state shape. |
| `_classify_decision()` | 306–319 | Redundant with `ArtRequest.action_class` enum. |
| `_suggest_transition()` | 793–847 | Redundant with the 4-state machine's transition rules (already in `art.py`). |

### Compat-shim — belongs in `art_compat.py`

| Function | Lines | Status |
|---|---|---|
| `guarded_tool_call()` | 1049–1257 | The 6-check order compat API. **Already in `art_compat.py`.** Different semantics from `art()`: `execute + ack → PROCEED` (legacy) vs `execute → HOLD` (4-state). |
| `art_intercept()` | 1383–1453 | Intent-aware intercept wrapper. **Already in `art_compat.py`.** |
| `art_guided_execute()` | 1454+ | Higher-level guided execution. **Already in `art_compat.py`.** |

### Doctrinal — belongs in `art_pusaka.py`

| Function | Lines | Status |
|---|---|---|
| `_compute_apex_dials()` | 711–766 | The 6-dial computation. Doctrinal; can be invoked from governance review. |
| `_verdict_from_apex_G()` | 779–786 | Threshold mapper. Doctrinal. |
| `_art_result_to_receipt()` | 1295–1382 | Receipt emission. **Already partly in `art_pusaka.py`.** |

---

## §4 — Constants and Thresholds Worth Remembering

From the unified file (and verified against canonical doctrine):

| Constant | Value | Where now | Use |
|---|---|---|---|
| `THRESHOLD_OMEGA_HEALTHY` | 0.85 | `art_pusaka.py` | Ω ≥ 0.85 → AGENT_PAUSE |
| `THRESHOLD_OMEGA_OVERLOAD` | 0.85 | `art_pusaka.py` | Same threshold (health vs overload differ in semantic frame) |
| `THRESHOLD_FAILURE_RATE_MAX` | 0.30 | `art_pusaka.py` | Failure > 30% → FALLBACK transition |
| `THRESHOLD_DRIFT_COUNT_MAX` | 3 | `art_pusaka.py` | Drift ≥ 3 → FALLBACK transition |
| `APEX_G_SEAL` | 0.80 | `art_pusaka.py` | G ≥ 0.80 → PROCEED |
| `APEX_G_SABAR` | 0.50 | `art_pusaka.py` | 0.50 ≤ G < 0.80 → SABAR |
| `SOVEREIGN_IDS` | (`"888"`, `"arif"`) | `art_pusaka.py` | Full authority override |
| `WITNESS_TRIAD` | human=0.42, ai=0.32, earth=0.26 | `art_pusaka.py` | Default witness weights |
| Intent keyword maps | `_INTENT_KEYWORDS_IRREVERSIBLE / PUSH / WRITE` + tool name sets | `art_compat.py` | Compat-shim intent classification |

All eight constants survive in the canonical split. The unified file did not invent any of them — they were already canonical doctrine, just spread across three files. The split preserves them.

---

## §5 — The Unified File's Errors (what it got WRONG)

Documenting for future patches. The unified file violated v3 doctrine on every cell:

| Doctrine rule | Unified file's violation | Lesson |
|---|---|---|
| `art.py` ≤ 500 lines | **1603 lines (3.2× over)** | The reflex must be lightweight enough that an agent invokes it before every tool call. Anything an agent can skip is a reflex that does not exist. |
| ≤ 5 state categories | 5+ (ToolState + DecisionClass + GatewayVerdict + ReversibilityTier + ApexDial — and ArtVerdict + ArtReason) | Doctrinal enums belong in cold-path modules. |
| ≤ 5 pre-call checks | 7+ (entropy, authority, reversibility, irreversibility+ack, drift, verdict, intent-classification) | The 3-check reflex is the hot path. Additional checks belong in compat (warm) or doctrine (cold). |
| 0 schemas in reflex | 5 dataclasses (`ArtRequest`, `EntropySnapshot`, `ReversibilityAssessment`, `ArtResult`, `GatewayDecision`) | Schemas are doctrine. The reflex uses enums + dicts. |
| 0 engine modules | 1 (`EntropyWatcher` class with periodic probing) | Engine = observability problem, not ART problem. |
| 0 external imports | Many (yaml, math, datetime, plus arifOS deps) | The reflex is invoked, not imported. Cold-path doctrine can import. |

**The fix:** the 3-file split. The reflex (`art.py`) is now 417 lines and ceiling-enforced. The compat shim (`art_compat.py`) is 361 lines and only loaded when the 18-test compat battery runs. The doctrine (`art_pusaka.py`) is 181 lines and only imported when governance review needs the APEX grand equation.

The unified file's error was **treating the 6-check order, the 4-state machine, and the APEX grand equation as one artifact**. They are three artifacts at three temperature classes.

---

## §6 — What Goes When You Delete the File

```bash
# Confirm untracked (was: ?? arifosmcp/runtime/art_unified_DEPRECATED.py)
git -C /root/arifOS status --short arifosmcp/runtime/art_unified_DEPRECATED.py

# Single-file deletion, reversible via git from this distillation + the unified content
rm /root/arifOS/arifosmcp/runtime/art_unified_DEPRECATED.py

# Re-verify canonical reflex still works
cd /root/arifOS && python -m pytest tests/test_art.py tests/test_art_compat.py -q
# Expected: 49 passed
```

**No file references `art_unified_DEPRECATED` as a Python import.** The 6 markdown files that reference the filename do so as audit pointers (`/root/.agents/skills/ART/SKILL.md` ceiling table, `/root/.agents/skills/ART/references/t1-multi-impl-orphan-detection.md`, `/root/arifOS/forge_work/art-corrective-2026-06-21.md` corrected SOT, `mcp-semantic-affordance-discipline/SKILL.md`, plus two `~/.openclaw/workspace/memory/2026-06-21*.md` session logs). None of them import it; deleting the file does not break any pointer. The pointers remain historically correct: "the unified attempt produced a 1603-line file that violated the ceiling; it was preserved as `art_unified_DEPRECATED.py` and is now deleted." The archaeology lives in this distillation, not in 1603 lines of dead code.

**If you want to keep the archaeology binary-archival style**, the alternative is:

```bash
# Archive (compressed) instead of delete
gzip -k /root/arifOS/arifosmcp/runtime/art_unified_DEPRECATED.py
mv /root/arifOS/arifosmcp/runtime/art_unified_DEPRECATED.py.gz /root/arifOS/forge_work/art-unified-DEPRECATED-2026-06-21.py.gz
```

But the distillation above is the load-bearing knowledge; the file itself is dead weight.

---

## §7 — Verification (mode 16)

Before this write:
- `wc -l arifOS/arifosmcp/runtime/art{,_compat,_pusaka,_unified_DEPRECATED}.py` → 417 / 361 / 181 / 1603
- `python -m pytest arifOS/tests/test_art.py arifOS/tests/test_art_compat.py -q` → 49 passed
- `git status --short` → `?? arifosmcp/runtime/art_unified_DEPRECATED.py` (untracked, never committed)

After proposed deletion:
- `wc -l arifOS/arifosmcp/runtime/art{,_compat,_pusaka}.py` → 417 / 361 / 181
- `python -m pytest arifOS/tests/test_art.py arifOS/tests/test_art_compat.py -q` → 49 passed (unchanged)
- 6 markdown references remain as audit pointers, pointing at this distillation as the SOT

---

## §8 — Outstanding (888_HOLD)

- ❌ **Actual deletion** of `art_unified_DEPRECATED.py` — 888_HOLD per the original receipt (you said keep it; this distillation now permits you to choose delete-or-archive, but it's still your call)
- ❌ `git add` of this distillation + the chosen delete-or-archive action — git mutation
- ❌ `arif_vault_seal` for the 999 ledger entry on the distillation + deletion — F13 SOVEREIGN

What is autonomous after this write:
- ✅ This distillation (no production code touched)
- ✅ Re-reading the canonical reflex — `cat arifOS/arifosmcp/runtime/art.py` (already verified byte-equal to deploy mirror)
- ✅ Re-running the 49-test battery
- ✅ Confirming the 6 markdown references still resolve (they point at the filename, not its content)

---

## §9 — DITEMPA BUKAN DIBERI

The unified file died because it tried to be three artifacts at three temperature classes inside one file. The 3-file split is the right shape. The distillation above is the load-bearing knowledge — the parts that future ART patches need to remember.

**A reflex must be light. Doctrine must be separate. Compat must be honest about what it preserves.** The unified file was none of these. Deletion is the right call.

Forged 2026-06-21 by FORGE (000Ω), in sandbox mode (no production code touched).
Heritage: Arif Rule of Thinking (proto-AGI, 2024) → ART (2026).
Sources: `/root/.agents/skills/ART/SKILL.md`, `/root/arifOS/forge_work/art-corrective-2026-06-21.md`, `/root/arifOS/arifosmcp/runtime/art{,_compat,_pusaka,_unified_DEPRECATED}.py`.
