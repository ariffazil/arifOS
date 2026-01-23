---
description: 999 SEAL - Commit to Vault & Close Session
---
# 999 SEAL: Immutable Storage

**Canon:** `000_THEORY/000_ARCHITECTURE.md`
**Role:** The final seal — commits decisions to immutable storage

---

## Purpose

SEAL is the **vault stage** — committing approved changes and closing the session.

---

## When to Use

- After APEX issues SEAL verdict
- End of work session
- Committing changes to git
- Archiving decisions

---

## Steps

### 1. Commit — Seal Changes
```bash
git add -A
git commit -m "[SEAL] Description"
```

### 2. Ledger — Record Decision
Append to cooling ledger with:
- Session ID
- Verdict
- Timestamp
- Summary

### 3. Cool — Phoenix-72 (Major Decisions)
Major constitutional changes require 72-hour cooling period.

### 4. Close — Exit Status
```
status = EXIT_SEALED (100)
```

---

## Memory Bands (Information Cooling)

```
L5 → L0 (Hot → Frozen)

L5: VOID    — Ephemeral, chaotic
L4: SYNC    — Warm, operational  
L3: REFLECT — Cool, verified
L2: WITNESS — Cold, archived
L1: ARCHIVE — Frozen, historical
L0: VAULT   — Immutable, sealed
```

---

## Optional: EUREKA Notes

Before closing, capture insights for next session:

```bash
# Write learnings for next session
write_to_file .agent/EUREKA_NEXT_SESSION.md
```

---

## Output

- Git commit sealed
- Ledger entry recorded
- Session closed

---

## Next Session

→ **000_init** (New session ignition)

---

**Session Closed.**

**DITEMPA BUKAN DIBERI**
