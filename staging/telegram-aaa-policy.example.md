# Telegram & AAA Visibility Policy

This policy governs visibility and command authority when in-scope agents interact via AAA or Telegram integration.

---

## 1. Command Authority Gating

To prevent unauthorized actions, commands are restricted based on the agent's intelligence tier:

| Command | Allowed Tier | Action on Violation |
|---|---|---|
| `/genesis` | AGI, Clerk, ASI | Auto-approve (Read-only check) |
| `/init` | AGI, Clerk, ASI | Propose to ASI queue |
| `/seal` | ASI (Hermes Only) | **888_HOLD** (Clerk/AGI cannot seal) |
| `/undo` | ASI, Clerk | Evaluated by ASI; triggers undo rollback |
| Any destructive command | None | **VOID** (Aggressively blocks execution) |

---

## 2. Notification & Heartbeat Visibility

- **Operator Heartbeat:** Cockpit agents must send simple heartbeat packets tracing local host stability.
- **Log Redaction:** No private keys, `.env` file contents, or personal session memory shall be shared on Telegram channels or public logs.
- **Audit Provenance:** Every remote execution proposal sent over Telegram must include the canonical `trace_id` referencing the local cockpit session.
