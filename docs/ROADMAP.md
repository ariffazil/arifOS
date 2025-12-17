# arifOS Development Roadmap

**Version:** v37.0.0 | **Last Updated:** 2025-12-12

---

## Current Status

- **v37.0.0** — RELEASED (PyPI)
- **Tests:** 1123 passing
- **Runtime Law:** v35Omega
- **Measurement Law:** v37 (unified LAW+SPEC+CODE)

---

## Completed (v37)

- [x] Unified LAW+SPEC+CODE epoch
- [x] All 9 constitutional floors implemented
- [x] W@W Federation (5 organs: @WELL, @RIF, @WEALTH, @GEOX, @PROMPT)
- [x] @EYE Sentinel (12 views)
- [x] GENIUS LAW metrics (G, C_dark, Psi)
- [x] Python-sovereign enforcement (Amanah, Anti-Hantu)
- [x] Cooling Ledger with hash-chain integrity
- [x] Phoenix-72 metabolism
- [x] SEA-LION integration
- [x] v36.2 PHOENIX patches (Psi calibration, Anti-Hantu expanded, telemetry)

---

## In Progress (v37.1)

### P0 — Critical

- [ ] Harden fail-open governance paths (prefer SABAR/VOID over silent SEAL)
- [ ] Align Cooling Ledger schema with `vault999_ledger_schema_v36.3O.json`

### P1 — High Value

- [ ] Extract stakes classifier to dedicated module (`arifos_core/stakes_classifier.py`)
- [ ] Expand W@W + GENIUS telemetry fields in Cooling Ledger
- [ ] Add promptfoo configs for W@W organs

### P2 — Nice to Have

- [ ] Architecture overview in `docs/ARIFOS_ARCHITECTURE_OVERVIEW.md`
- [ ] Expand mypy coverage on non-core modules
- [ ] Link whitepaper from README.md

---

## Future (v38+)

- [ ] Hardware-backed KMS signing (replace HMAC-SHA256 stubs)
- [ ] Full zkPC cryptographic integrity (currently non-cryptographic stub)
- [ ] Multi-modal @GEOX (images, audio, sensors)
- [ ] SEA-LION in-model GENIUS LAW computation
- [ ] Thermodynamic grounding: Cooling Ledger entropy measurement

---

## Development Tracks

### Track A — LAW (archive/versions/v36_3_omega/v36.3O/canon)

Only modify canon when explicitly requested.

### Track B — SPEC (archive/versions/v36_3_omega/v36.3O/spec)

Only modify specs when explicitly requested.

### Track C — CODE_FORGE (Runtime)

Default track for day-to-day work. Keep tests green.

**Rule of thumb:** Canon > Spec > Code. If conflict, mark as PARADOX_HOTSPOT.

---

## Contributing

1. Check this roadmap for current priorities
2. Follow [AGENTS.md](../AGENTS.md) governance rules
3. All changes must pass 9 constitutional floors
4. Run `pytest -v` before committing
