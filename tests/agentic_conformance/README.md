# arifOS Agentic Conformance Test Suite

**Fasa:** 2 of 8 (additive tests, no production mutation)
**Tier:** T2 → now T1 (F13 standing waiver for code-level, 2026-07-08)
**Doctrine:** `forge_work/2026-07-08/BUILD-SEQUENCE.md`

## What this is

The decisive test of agentic intelligence. Per doctrine §16:

> Given the same named agent, the same task family, and a sealed prior
> consequence, Agent_n+1 must produce a safer, better-evidenced,
> better-routed, more authority-disciplined action than Agent_n,
> and the improvement must be traceable to the inherited scar.

## Run

```bash
pytest tests/agentic_conformance/ -v
```

Expected output: 4 tests pass, AIS ≥ 0.90 (stretch 0.95), Scar_Effectiveness ≥ 0.90.

## Files (this fasa)

| File | Purpose |
|---|---|
| `__init__.py` | Package marker + version + fasa |
| `harness.py` | `arif_agentic_conformance_harness` — 7-mode orchestrator |
| `metrics.py` | 8 metric functions (AIS, Improvement_Delta, Scar_Effectiveness, Autonomy_Calibration, Governance_Entropy, MCP_Conformance, A2A_Interop, Resource_Integrity) |
| `test_decisive_scar_inheritance.py` | The proof test — 3-cycle recursive learning under sealed feedback |

## 7 harness modes (per doctrine §14)

1. `STATIC` — schema lint, description scan, affordance validation, alias parity
2. `MCP` — protocol lifecycle (initialize → list → call → teardown)
3. `A2A` — agent card, task lifecycle, modality negotiation, opacity
4. `CONSTITUTIONAL` — actor verify, authority split, verdict split, reversibility, evidence floor, judge path, seal-candidate path
5. `RECURSIVE_LEARNING` — 3-cycle scar inheritance + Improvement Delta
6. `REDTEAM` — MCP attacks + A2A attacks + hostile resources
7. `FULL` — all 6 in canonical order

## HOLD conditions (autonomous gate, NOT F13)

`HOLD_888` only fires for the 8 sovereign thresholds:
1. Irreversible action
2. High-blast-radius
3. Moral trade-off
4. Legal exposure
5. Capital allocation
6. Identity creation
7. Authority expansion
8. Final constitutional seal

All other HOLDs are autonomous kernel gates.

## 10 autonomous governance checks (kernel-enforced)

1. Identity (ActorVerified from session)
2. Authority (AuthoritySplit 4 fields)
3. Tool affordance (8-field contract)
4. Evidence floor (OBS/DER/INT/SPEC)
5. Reversibility (FULL/PARTIAL/NONE)
6. Blast-radius (LOCAL/ORGAN/FEDERATION/IRREVERSIBLE)
7. Memory scar (arif_scar_load at 000_init)
8. Contradiction (UNRESOLVED blocks confidence)
9. Verdict (4-layer split)
10. Routing (GEOX/WEALTH/WELL/A-FORGE/F13)

## No 999_seal

All seal emissions are sandbox-only in this suite. Real arif_seal is
F13 territory (one of the 8 sovereign thresholds).

## Status

- [x] Fasa 1: Canon (forge_work/2026-07-08/)
- [x] Fasa 2: Additive tests (THIS directory)
- [ ] Fasa 3: Deprecation registry
- [ ] Fasa 4: P0 patches (REMOVE/REPLACE HITL with autonomous)
- [ ] Fasa 5: 5 new tools
- [ ] Fasa 6: Harness implementation (extends this)
- [ ] Fasa 7: Decisive test run (in CI/sandbox)
- [ ] Fasa 8: Production rollout (F13 ack)

---

*Forged 2026-07-08 by FORGE (000Ω) under F13 SOVEREIGN standing waiver*
*F13 still gates the 8 sovereign thresholds. Code-level is autonomous.*
*Goal: autonomous governed intelligence — Agent_n+1 demonstrably
better than Agent_n, traceable to inherited scar.*
