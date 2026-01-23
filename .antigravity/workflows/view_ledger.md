---
description: View THE EYE cross-agent witness ledger (ARCHITECT transparency)
---

# /ledger — Cross-Agent Witness Ledger

View the transparent audit trail of all agent decisions.

## Steps

// turbo-all

1. Display THE EYE witness manifest:
```bash
cat L1_THEORY/ledger/README_EYE.md
```

2. Show recent GitSeal decisions (last 10):
```bash
tail -n 10 L1_THEORY/ledger/gitseal_audit_trail.jsonl
```

3. Show Claude history status:
```bash
wc -l L1_THEORY/ledger/claude_history.jsonl
```

4. List all session reflections:
```bash
ls -la .antigravity/SESSION_REFLECTION_*.md 2>/dev/null || echo "No session reflections yet"
```

5. Show EUREKA notes if present:
```bash
head -50 .antigravity/EUREKA_NEXT_SESSION.md 2>/dev/null || echo "No EUREKA notes"
```

## Output

Summarize:
- Total GitSeal decisions
- Recent verdicts (SEAL/VOID/SABAR)
- Session reflection count
- Any pending EUREKA notes

## Purpose

"All agents behave because if no one is watching, GOD EYE is there."

This command provides transparency across:
- Antigravity sessions
- Claude sessions
- Git seal decisions
- Session memory

**DITEMPA BUKAN DIBERI** — The EYE sees all.
