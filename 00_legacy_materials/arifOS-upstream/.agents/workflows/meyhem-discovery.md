---
description: Meyhem Discovery Rule — KERNEL Tier | F13 Sovereign Oracle
---

**Motto:** *Discovery Is Intake | Not Installation*

### 1. Purpose
This rule governs `meyhem` as a discovery oracle only. It may inform the stack, but it may not change the stack on its own.

### 2. Allowed Output
- `meyhem` may return candidates, comparisons, and capability matches.
- The agent may convert results into `keep`, `add`, `defer`, `remove`, or `risk` recommendations for human review.

### 3. Forbidden Actions
- No auto-install.
- No auto-mount.
- No auto-enable.
- No auto-call of a newly discovered server.
- No direct mutation of `C:\Users\User\.gemini\antigravity\mcp_config.json` based only on discovery output.

### 4. Consolidation Policy
- If a discovered tool overlaps an approved capability, prefer the existing approved server instead of adding a parallel one.
- Any exception requires explicit user approval and a paired update to the workflow canon plus global config.

### 5. Violation
- Treating discovery as approval is VOID.

*Ditempa Bukan Diberi — [ARIF OS KERNEL]*
