# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

**Version:** v42.0.0 | **Tests:** 2156+ | **Safety Ceiling:** 97%

**Imports:** `~/.claude/CLAUDE.md` — Global governance (floors, SABAR, verdicts)
**Extends:** [AGENTS.md](AGENTS.md) — Full constitutional governance

---

## Quick Reference

```bash
# Install
pip install arifos

# Test
pytest -v

# Pipeline demo
python -m arifos_core.pipeline
```

---

## Canon Index (v42)

**Master:** [canon/_INDEX/00_MASTER_INDEX_v42.md](canon/_INDEX/00_MASTER_INDEX_v42.md)

| Layer | Canon | Spec |
|-------|-------|------|
| Foundation | `canon/00_foundation/` | — |
| Floors (F1–F9) | `canon/01_floors/01_CONSTITUTIONAL_FLOORS_v42.md` | `spec/v42/constitutional_floors.json` |
| Actors (AGI/ASI/APEX) | `canon/02_actors/` | — |
| Runtime (Pipeline/W@W) | `canon/03_runtime/` | `spec/v42/pipeline.yaml` |
| Measurement (GENIUS) | `canon/04_measurement/04_GENIUS_LAW_v42.md` | `spec/v42/genius_law.json` |
| Memory (EUREKA) | `canon/05_memory/` | `spec/v42/cooling_ledger_phoenix.json` |
| Paradox (Grey Zone) | `canon/06_paradox/` | — |

---

## Nine Floors (Summary)

| # | Floor | Threshold | Type |
|---|-------|-----------|------|
| F1 | Amanah | LOCK | Hard |
| F2 | Truth | >=0.99 | Hard |
| F3 | Tri-Witness | >=0.95 | Hard |
| F4 | DeltaS | >=0 | Hard |
| F5 | Peace^2 | >=1.0 | Soft |
| F6 | Kr | >=0.95 | Soft |
| F7 | Omega0 | 0.03-0.05 | Hard |
| F8 | G | >=0.80 | Derived |
| F9 | C_dark | <0.30 | Derived |

Hard fail → VOID. Soft fail → PARTIAL.

---

## Verdict Hierarchy

```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

**Python decides. Claude proposes.**

---

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/000` | Session init |
| `/888` | High-stakes hold |
| `/999` | Session close |
| `/g` | GENIUS metrics |
| `/s` | SABAR trigger |
| `/f` | Floor check |

---

## Custom Agents

| Agent | Purpose |
|-------|---------|
| `anti-hantu` | F9 language enforcement |
| `apex-reviewer` | Code review with floors |
| `canon-keeper` | Code-canon alignment |
| `eye-sentinel` | Multi-view governance |

---

For full governance details, see [AGENTS.md](AGENTS.md).

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
