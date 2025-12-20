# spec/v44 - v44 Specification Files

**Version:** v44.0.0 | **Status:** SEALED | **Last Updated:** 2025-12-20

---

## Structure Note

**v44 uses the v42 spec structure as its foundation.**

The TEARFRAME v44 upgrade adds physics-based governance (session telemetry, reduction engine, physics floors) without changing the core constitutional spec structure defined in v42.

**Canonical Specs (v42 structure applies):**

| File | Purpose | Version |
|------|---------|---------|
| `../v42/constitutional_floors.json` | F1-F9 thresholds | v42.1 → v44 |
| `../v42/genius_law.json` | G, C_dark params | v42.1 → v44 |
| `../v42/pipeline.yaml` | Stage config | v42.1 → v44 |
| `../v42/waw_prompt_floors.json` | W@W config | v42.1 → v44 |
| `../v42/cooling_ledger_phoenix.json` | Ledger config | v42.1 → v44 |

**v44-Specific Additions:**

TEARFRAME physics layer additions are **code-driven** (not spec-driven) to maintain deterministic enforcement:

- `arifos_core/utils/session_telemetry.py` - Session state tracking
- `arifos_core/utils/reduction_engine.py` - Physics attribute calculation
- `arifos_core/governance/session_physics.py` - Floor evaluation

**Rationale:**

v44 extends v42 without breaking compatibility. The v42 specs remain the canonical source of truth for:
- Constitutional floor thresholds (F1-F9)
- GENIUS LAW parameters (G, C_dark, Ψ)
- Pipeline stage configuration (000-999)
- W@W federation rules

TEARFRAME adds **runtime physics enforcement** on top of these specs, not replacing them.

---

## Version Evolution

- **v42:** Spec-driven constitutional floors
- **v43:** Interface & Authority (federated backends)
- **v44:** TEARFRAME Physics (fail-closed session governance)

---

**See:** `../v42/README.md` for detailed spec documentation.
