> **SUPERSEDED for findings** by `docs/conformance/RECONCILIATION_2026-10-20.md` (21:48 MYT).
> Runtime changed 21:32 (ee2b4e1 → 09f9823); several findings here are RETIRED. Kept unedited for audit.

# RECEIPT — F1–F13 conformance test (invariant → contract → enforcement → test)

- Date: 2026-10-20, 21:14–21:22 MYT (13:14–13:22 UTC)
- Actor: claude-code-kvm8 (FI-002) · session `SEAL-0f39068bd9af46d4` · OBSERVE_ONLY
- Lane: B. Read-only analysis + one new read-only test script. **No kernel semantics changed.**
- Trigger: Arif — verify the doctrine/axioms drift he measured, then build the enforcement
  point his formula calls for.

## 1. What the probe found (OBS)

Live, in one running kernel (`arifos-ee2b4e1`, canon `2026.10.20-ee2b4e1`, 3/3 files verified):

| Floor | GENESIS canon | doctrine / schema | `arifos://floors` | `floor/{id}` | Law enum | amendment_guard | `arif_think(axioms)` |
|---|---|---|---|---|---|---|---|
| F3 | TRI-WITNESS | WITNESS | ok | WITNESS | WITNESS | WITNESS | WITNESS |
| F6 | EMPATHY | MARUAH | EMPATHY ⇄ MARUAH | MARUAH | EMPATHY | MARUAH | EMPATHY |
| F10–F13 | present | present | present | **ABSENT** | present | n/a | present |
| F11 | AUDITABILITY | AUDIT | ok | **ABSENT** | AUDIT | AUDIT | AUDIT |
| F12 | RESILIENCE | INJECTION | ok | **ABSENT** | INJECTION | INJECTION | INJECTION |

- 24 drift findings across 7 surfaces; `arifos://floor/{id}` implements only F1–F9.
- `arif_think(mode=axioms)` L11 record is internally contradictory: id `L11_AUDIT`,
  text *"Authority — verify identity before irreversible acts."*
- **F2 confidence cap is unenforced:** doctrine states "Cap confidence at 0.90";
  axioms emit **13/13 above the cap**, max `L13_SOVEREIGN = 0.99`, envelope 0.97.
  GENESIS F2 says `P(truth) ≥ 0.99` — a threshold, not a ceiling. The 0.90 ceiling
  exists in exactly one resource that nothing reads.
- Separate defect: `arif_think` advertises a `concise` parameter in its live input schema
  (`tool_spec.py:258`, `public_registry.py:400`) but the callable rejects it —
  `ValueError: CONTRACT_VIOLATION: invalid input types`. Bisected: `mode`, `query`,
  `session_id`, `actor_id`, `witness_type`, `context` all pass; `concise` alone fails.

Arif's reported findings reproduce exactly. Two additional defects found: `axioms` cap
violation quantified, and the `concise` phantom parameter.

## 2. What was built (the enforcement point)

`/root/arifOS/scripts/floor_conformance.py` — read-only, ~330 lines, no new canon.

- Canon = `GENESIS/FLOOR_TABLE.json` (its own `consumers_must_sync_to` names itself).
- Extracts floor names mechanically from **7 surfaces**: 2 static resource modules
  (AST/prose), the `floor/{id}` template dict, the `Law` enum (AST — multi-line members
  included), `amendment_guard`, live `arifos://floors`, live `arif_think(mode=axioms)`.
- Second check: `check_confidence_cap()` — parses the declared cap and compares it with
  every confidence the axioms surface actually emits.
- Human table + `--json`; **exit 1 on any drift**, so it can gate CI.
- It reports, it does not decide: *"Resolution of any drift is an F13 sovereign call."*

Result today: `verdict=DRIFT · drift=24 · surfaces 7/7 · F2 cap VIOLATION`.
Machine-readable: `docs/conformance/floor_conformance_2026-10-20.json`.

## 3. Not proven (INT / UNKNOWN)

- Whether any *runtime decision* currently reads the wrong floor name. Grep shows
  `amendment_guard` and `dignity_gate` do, but no verdict today was shown to flip because
  of it. Drift is proved at the surface; its blast radius is not yet measured.
- Why `concise` is rejected — the callable that serves the live tool was not located;
  only the interface failure is proved.

## 4. MENUNGGU ARIF — resolution is an F13 call

The names are constitutional, so I prepared but did not apply. Pick one direction:

**Direction A — canonicalise to the runtime (fewest edits).** Rewrite
`GENESIS/FLOOR_TABLE.json` names to `F3 WITNESS · F6 MARUAH · F11 AUDIT · F12 INJECTION`
(v1.0.0 → 1.1.0, `authority: F13 SOVEREIGN`, keep rule text). Then add F10–F13 to
`resources/floor_table.py`. One canon edit clears 20 of 24 findings.

**Direction B — canonicalise to GENESIS.** Edit `resources/doctrine.py`,
`resources/schema.py`, `resources/floor_table.py`, `resources/alignment_gap.py`,
`constitutional_map.py`, `runtime/amendment_guard.py` to `EMPATHY / AUDITABILITY /
RESILIENCE / TRI-WITNESS`. Six files, touches runtime code paths.

**Either way, separately:** decide whether `0.90` is a real cap (then wire it into the
axioms emitter) or retire it from doctrine. Right now it is a rule with no reader.

Exact commands after the word:

```
chattr -i /root/arifOS/GENESIS/FLOOR_TABLE.json   # if immutable
python3 -I /root/arifOS/scripts/floor_conformance.py --session <SID>   # expect exit 0 after fix
systemctl restart arifos                            # court service — Arif's hand
```

## 5. CORRECTION (21:40 MYT — after reading the sealed canon, not the resource)

Two claims in this receipt were wrong. Both are corrected in
`scripts/floor_conformance.py`; the original text above is kept so the
correction is auditable rather than silent.

**5.1 — F6 was never drift.** `GENESIS/000_KERNEL_CANON.md §3.4` (F13, 2026-07-24)
seals a **dual-registry bridge**: the kernel layer emits `MARUAH`, the public
layer emits `EMPATHY`, and both are correct — the rendering layer chooses. My
first cut flagged this as drift (7 findings). It is a designed bridge, not a
defect. The checker now reports status `BRIDGED` for any name in a sealed pair.

**5.2 — the cap is 0.97, not 0.90.** `§3.2` (F13, 2026-07-23) states
`Ω₀ ∈ [0.03, 0.05] ⇒ confidence cap = 1 − Ω₀ ∈ [0.95, 0.97]`, operational
ceiling 0.96. The "0.90" on the doctrine page is the **stale value §3.2
explicitly absorbed** — citing it alone is the documented way the drift
returns. I had been measuring against a retired rule.

The finding survives, but with the right threshold: `arif_think(mode=axioms)`
emits **3 axioms above the 0.97 hard max**, maximum `L13_SOVEREIGN = 0.99`.
That is a genuine F7 violation — just not the one I originally named.

Corrected verdict: **18 findings, all from F3/F11/F12 naming** (was 24, of
which 6 were F6 false positives and 12 were mine to withdraw). F6 removed,
F10–F13 now present in `arifos://floor/{id}`.

**5.3 — a concurrent writer is mid-flight on the same defect.** Between 21:22
and 21:25 another writer created `arifosmcp/constitutional_canon.py` as the
single floor source and repointed `doctrine.py`, `floor_table.py`, `core/law.py`,
`runtime/law.py`, `runtime/tools.py` at it — Direction A of my own proposal,
implemented better (generated block, no retyping). I did not touch those files.
The live runtime still serves the old names because no restart has happened.

## 6. Rollback

Nothing in the kernel changed. New files only:
`scripts/floor_conformance.py`, `docs/conformance/floor_conformance_2026-10-20.json`,
this receipt. Delete-and-forget; no state affected.
