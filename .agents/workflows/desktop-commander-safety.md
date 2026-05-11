---
description: Desktop Commander Safety Rule — OPS Tier | F8 Guard
---

**Motto:** *Minimal Reach | Reversible Change | Explicit Seal for Surface Edits*

### 1. Purpose
This rule governs the use of `desktop-commander` for config-level and system-adjacent actions in the global `ariffazil` stack.

### 2. Approved Scope
- Preferred roots for file operations are:
  - `C:\ariffazil\arifOS`
  - `C:\ariffazil\arifOS\arifosmcp`
  - `C:\Users\User\Documents`
- `C:\Users\User\.gemini\antigravity\mcp_config.json` is a governance exception and may only be edited when the task is explicitly about global MCP maintenance.

### 3. 888_HOLD Triggers
- Explicit confirmation is required before any command that:
  - touches global or user-level MCP config files
  - changes workflow rules in `C:\ariffazil\arifOS\.agents\workflows`
  - targets `C:\Windows`, `C:\Program Files`, `C:\Users\User\AppData`, `.ssh`, `.aws`, `.kube`, `.gnupg`, or `.env*`
  - changes service state, Docker state, auth state, or deletes data

### 4. Enforcement
- Prefer narrower MCPs before `desktop-commander`.
- Back up config files before editing them.
- Never use discovery output to auto-install, auto-enable, or auto-call a new MCP.
- If Desktop Commander runtime config is changed, `allowedDirectories` must stay aligned to the approved roots above.

### 5. Residual Risk
- Upstream Desktop Commander directory limits do not fully constrain terminal commands.
- Treat shell execution through `desktop-commander` as high-risk even when file roots appear restricted.

### 6. Violation
- Widening Desktop Commander reach without explicit approval is a direct F1/F8 violation.

*Ditempa Bukan Diberi — [ARIF OS KERNEL]*
