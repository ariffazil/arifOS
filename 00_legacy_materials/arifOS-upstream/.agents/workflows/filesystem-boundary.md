---
description: Filesystem Boundary Rule — KERNEL Tier | F8 Guard
---

**Motto:** *Project Roots Only | Safe Documents Only | No Silent Drift*

### 1. Purpose
This rule governs the `filesystem` MCP server so the global `ariffazil` stack stays inside approved roots.

### 2. Approved Roots
- `C:\ariffazil\arifOS`
- `C:\ariffazil\arifOS\arifosmcp`
- `C:\Users\User\Documents`

### 3. Boundary Rules
- The `filesystem` MCP must not be widened beyond the approved roots without explicit user approval.
- `C:\Users\User\.gemini\antigravity\mcp_config.json` is not a filesystem root; edit it only through an explicitly approved governance task.
- Workspace-local `.gemini\antigravity\mcp_config.json` variants are drift and must be flagged, not normalized automatically.

### 4. Blocked Targets
- Always block routine probing of:
  - `C:\Windows`
  - `C:\Program Files`
  - `C:\Users\User\AppData`
  - `.ssh`
  - `.aws`
  - `.env*`
  - other secret-bearing system paths

### 5. Violation
- Any silent boundary expansion or off-root probing without approval is VOID.

*Ditempa Bukan Diberi — [ARIF OS KERNEL]*
