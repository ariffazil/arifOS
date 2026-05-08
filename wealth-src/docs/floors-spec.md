# WEALTH — F1–F13 Floor Specifications

> Every module in WEALTH is audited against these floors.

---

## Floor Matrix by Module

| Floor | Rule | networth | cashflow | goals | risk | maruah | projection | UI |
|---|---|---|---|---|---|---|---|---|
| **F1** Reversible | Soft-delete only | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F2** Truth Band | Tag all outputs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F3** Align | Source all numbers | ✅ | ✅ | — | ✅ | — | ✅ | ✅ |
| **F4** Clarity | Reduce complexity | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F5** Peace | No unresolved panic | — | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| **F6** Maruah | Dignity as variable | — | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| **F7** Humility | Uncertainty band | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F8** Law | Local-first data | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F9** Anti-Hantu | No phantom entries | ✅ | ✅ | ✅ | ✅ | — | — | ✅ |
| **F10** AI Only Advises | Human decides | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F11** Auth | PIN for critical | — | — | ✅ | ✅ | ✅ | — | ✅ |
| **F12** No Override | Floors unbypassable | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **F13** Human Veto | Final authority | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 888 HOLD Triggers by Module

| Module | 888 HOLD Condition |
|---|---|
| `networth` | Net worth delta > -20% in single session |
| `cashflow` | Runway drops below 3 months |
| `goals` | Goal ABANDONED state attempted |
| `risk` | Debt-to-asset ratio enters RED band |
| `maruah` | Maruah Score drops below floor (0.6) |
| `projection` | Projection used without ESTIMATE tag |
| `UI` | Any irreversible UI action confirmed |

---

*WEALTH Floors Spec v1.0.0 — DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
