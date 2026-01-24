---
description: /000 — Session Initialization (arifOS)
---
# /000 — Session Initialization (arifOS)

**Role:** Gate (000_init)
**Platform:** Codex CLI

---

## Purpose

Initialize session with constitutional context and repo state.

---

## Steps

1. **Load System Canon** — Read `000_THEORY/` (law + agents)
2. **Check Version** — `rg "^version" pyproject.toml`
3. **Review Recent Changes** — `git log -10 --oneline`
4. **Check Git Status** — `git status -sb`
5. **Load AGENTS.md Context** — `Get-Content AGENTS.md`
6. **Load Governance Protocols** — `GOVERNANCE_PROTOCOLS.md` (if present)
7. **Check Active Branch** — `git branch --show-current`
8. **Review CHANGELOG** — `CHANGELOG.md` (if present)
9. **Update Codex Brain** — append session timestamp to `.codex/codexbrain.md`:
   ```powershell
   "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') — /000 session start" | Add-Content .codex/codexbrain.md
   ```

---

## Notes

If `GOVERNANCE_PROTOCOLS.md` or `CHANGELOG.md` are missing, note the absence and continue.
Use the PowerShell line above to mark session start.

---

**DITEMPA BUKAN DIBERI**
