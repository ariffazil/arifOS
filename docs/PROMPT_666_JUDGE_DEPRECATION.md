# Prompt alias deprecation — `666_judge` → `888_judge`

**Status:** DEPRECATION ACTIVE  
**Opened:** 2026-07-10  
**Owner:** arifOS kernel (prompts surface)  
**Authority:** F4 CLARITY + F11 AUDIT — no permanent silent aliases  

---

## Why

11-stage canon:
- **666** = GOVERN (`arif_critique` path / floors stress)
- **888** = JUDGE (`arif_judge` = KERNEL 888)

Prompt registry historically registered **`666_judge`** as the judge template while the tool and title already said 888. That is the same failure mode as updated labels with stale identifiers.

**Canonical prompt name now:** `888_judge`  
**Legacy alias (temporary):** `666_judge` → same body, title = `LEGACY ALIAS → use 888_judge`

---

## What “one cycle” means (concrete)

| Field | Value |
|-------|--------|
| **Cycle definition** | One full calendar week after open date |
| **Removal not before** | 2026-07-10 |
| **Hard remove on or after** | **2026-07-17** (Asia/Kuala_Lumpur date) |
| **Removal action** | Delete `@mcp.prompt(name="666_judge")` and drop from `CANONICAL_PROMPTS` |
| **After removal** | `prompts/get name=666_judge` must fail; only `888_judge` remains |

---

## Who / what checks

1. **Automated (primary):**  
   `python3 /root/arifOS/scripts/check_prompt_alias_deprecation.py`  
   - Exit 0 if before deadline and alias still present (OK)  
   - Exit 1 if **on/after 2026-07-17** and `666_judge` still in live `prompts/list`  
   - Exit 0 if after deadline and alias **absent** (done)

2. **Human (secondary):** Next agent that runs federation readiness or prompt surface work must run the script if date ≥ 2026-07-17.

3. **Not sufficient:** “We’ll remove it next restart” or “next deploy” without a date.

---

## Receipt of open

| Date | Event |
|------|--------|
| 2026-07-10 | `888_judge` registered; `666_judge` marked LEGACY ALIAS |
| 2026-07-10 | `555_critique` title cleaned (no bare “666” as identity of the prompt) |
| 2026-07-17 | **Deadline** — alias must be gone from live MCP |

---

*DITEMPA BUKAN DIBERI — Deprecations expire by calendar, not by hope.*
