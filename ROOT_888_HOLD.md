# ROOT STRUCTURAL HOLDS

**Status:** ✅ ALL RESOLVED — 2026-05-26
**Resolver:** Copilot CLI session `c2d1f4ee`
**Commit:** `73292d09`

---

## Resolved Collisions

| Issue | Verdict | Commit |
|-------|---------|--------|
| `GEOX/` vs `geox/` submodule collision | `GEOX/` survives; `geox` removed (labeled "broken alias" in `cb1c02d7`) | `73292d09` |
| `CONFIG/` vs `config/` directory collision | `config/` survives; 5 unique files migrated from CONFIG, CONFIG deleted | `73292d09` |
| `staging/` Windows-path snapshot | Archived → `archive/2026-05-22-windows-staging/` | `73292d09` |
| `scratch/` diagnostic scripts at root | Moved → `audit/scratch/` | `73292d09` |
| `.archive/` vs `archive/` | Merged into `archive/` | Prior session |
| `breach_results.json` at root | Moved → `audit/breach_results.json` | `75f8c812` |

---

## Next Active Holds

None currently. Open a new `888_HOLD` entry if a new structural decision requires Sovereign review.

---

*DITEMPA BUKAN DIBERI | F13 SOVEREIGN*
