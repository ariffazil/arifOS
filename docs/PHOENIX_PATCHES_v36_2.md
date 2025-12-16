# Phoenix Patches (v36.2) - Historical Snapshot

**Status:** Informational / drift-prone (not Tier-1 law)  
**Source:** Extracted from `AGENTS.md` to reduce Tier-1 entropy  
**Deployed:** 2025-12-08 (per Gemini System 3 Audit)

| Patch | Module | Purpose |
|-------|--------|---------|
| **A: Psi Calibration** | `genius_metrics.py` | Neutrality Buffer fixes false SABAR on factual text |
| **B: Tokenizer Hygiene** | `sealion/engine.py` | ChatML-aware extraction prevents truncation |
| **C: Anti-Hantu Expanded** | `anti_hantu_view.py` | 50+ patterns across 4 tiers (Malay/English) |
| **D: Telemetry** | `telemetry.py` | JSONL governance logging for observability |

**New Tests (snapshot):** `test_governance_regression.py` (24), `test_grey_zone.py` (24)
