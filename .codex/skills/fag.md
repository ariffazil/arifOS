---
description: /fag — File Access Governance (safe reads)
---
# /fag — File Access Governance (safe reads)

**Role:** Heart (Ω)
**Platform:** Codex CLI

---

## Purpose

Use governed file reads to prevent secret leakage and enforce root jail.

---

## Steps

1. **Verify /000** — Session initialized
2. **Safe Read Canon** — Prefer `arifos-safe-read` if available
3. **Root Jail** — Limit reads to repo root
4. **Record** — Note any blocked paths or redactions

---

## Example

```bash
arifos-safe-read --path "AGENTS.md" --root "$(git rev-parse --show-toplevel)"
```

---

**DITEMPA BUKAN DIBERI**
