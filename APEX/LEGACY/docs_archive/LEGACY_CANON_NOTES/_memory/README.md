# 05_memory - Memory Layer

**Version:** v42.0 | **Status:** DRAFT

---

## Purpose

This layer defines the memory governance of arifOS:

- **EUREKA Memory Stack** - 6-band memory architecture
- **Cooling Ledger** - Hash-chained audit trail
- **Phoenix-72** - Constitutional amendment engine

---

## Files

| File | Purpose |
|------|---------|
| `05_EUREKA_MEMORY_v42.md` | 6-band memory stack |
| `05_COOLING_LEDGER_v42.md` | Audit trail |
| `05_PHOENIX_72_v42.md` | Amendment engine |

---

## 4 Core Invariants

| # | Invariant |
|---|-----------|
| INV-1 | VOID verdicts NEVER become canonical memory |
| INV-2 | Humans seal law, AI proposes |
| INV-3 | Every write must be auditable |
| INV-4 | Recalled memory = suggestion (0.85 ceiling) |

---

## 6 Memory Bands

| Band | Purpose | Retention |
|------|---------|-----------|
| L0 VAULT | Constitution | PERMANENT |
| L1 LEDGER | Audit trail | 90 days |
| L2 ACTIVE | Working state | 7 days |
| L3 PHOENIX | Amendments | 90 days |
| L4 WITNESS | Soft evidence | 90 days |
| L5 VOID | Diagnostic | 90 days |

---

## Verdict => Band Routing

```
SEAL    => LEDGER + ACTIVE
SABAR   => LEDGER + ACTIVE
PARTIAL => PHOENIX + LEDGER
VOID    => VOID only
888_HOLD => LEDGER
SUNSET  => PHOENIX
```

---

## Dependencies

- `01_floors/` - Thresholds
- `03_runtime/` - Pipeline stages

## Dependents

- All runtime operations use memory

---

**DITEMPA BUKAN DIBERI** - Memory must cool before it rules.
