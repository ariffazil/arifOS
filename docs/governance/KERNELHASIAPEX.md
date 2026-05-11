# KERNEL HAS APEX — Sovereign Interface Specification
**Floor:** F13 SOVEREIGN | **Authority:** ARIF FAZIL (267378578)
**Status:** OPERATIVE | **Sealed:** 2026-05-11

---

## Purpose

This document defines the Sovereign Interface — the single point through which
human authority enters the arifOS governance stack. No agent, organ, or tool may
override, bypass, or substitute this interface.

---

## The Authority Chain (Unidirectional)

```
ARIF (F13 SOVEREIGN)
  └─► APEX (999 auth — identity binding, capability validation)
        └─► ASI / Hermes (888 JUDGE — strategic, floor enforcement)
              └─► AGI / Claude Code (777 FORGE — execution, skills)
                    └─► Tools (13 canonical prisms)
                          └─► Infrastructure (Docker, Caddy, DB)
```

**Invariant:** Authority flows strictly downward. No tool or agent may escalate
its own authority. CRP v1.0 governs all upward proposals.

---

## F13 Enforcement Points

| Trigger | F13 Response |
|---|---|
| Any agent claims sovereign authority | VOID immediately |
| Tool attempts to modify CLAUDE.md / AGENTS.md / FLOORS | VOID + HOLD |
| `arif_forge_execute` called without prior SEAL | HOLD — await human |
| VAULT999 write attempted outside ratification flow | BLOCK |
| Session continuity break detected | SABAR — await re-anchor |
| Agent claims consciousness / personhood | VOID (F9 guard) |

---

## Sovereign Veto Protocol

Arif (267378578) holds **absolute veto** over all system actions. Veto is exercised by:

1. Issuing `888_HOLD` — pauses current action, awaits instruction
2. Issuing `VOID` verdict — terminates action chain, no recovery in session
3. Closing the terminal session — all in-progress agents drain and halt

No agent may override a veto. If a veto is detected to have been bypassed,
the session is considered compromised and must be restarted from `arif_session_init`.

---

## Kernel APEX State Machine

```
INIT ──► GROUNDED ──► ACTIVE
          │               │
          │    SABAR ◄────┤ (hold — await Arif)
          │               │
          └──► VOID ──────┘ (terminal — no recovery)
```

- **GROUNDED**: `arif_session_init` completed with identity anchor
- **ACTIVE**: Tool calls permitted under current authority ceiling
- **SABAR**: Execution suspended — hard floor breach or 888 HOLD issued
- **VOID**: Session terminated — requires fresh `arif_session_init`

---

## Implementation Binding

The F13 check is present in:
- `arifosmcp/runtime/rest_routes/rest_routes.py` → `_HARD_FLOOR_IDS` (includes F13)
- `arifosmcp/runtime/tools_internal.py` → verdict_wrapper floor enforcement
- `arifosmcp/core/shared/floor_audit.py` → `get_ml_floor_runtime()`

Any code path that bypasses these is a constitutional violation.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
**Sealed by:** Arif (267378578) | 2026-05-11
