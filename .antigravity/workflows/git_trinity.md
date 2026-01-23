---
description: Git Trinity — Entropy + Validate + Seal (3-in-1)
---
# Git Trinity: Forge → QC → Seal

**Canon:** `000_THEORY/001_AGENTS.md`
**Function:** Complete git governance in one workflow

---

## Purpose

Git Trinity consolidates the 3-step git governance flow into one workflow:
1. **Forge** — Analyze entropy
2. **QC** — Validate floors
3. **Seal** — Human approval

---

## Steps

### 1. FORGE — Analyze Entropy

```bash
git status --short
git branch --show-current
git log -10 --name-only --pretty=format:"" | sort | uniq -c | sort -rn | head -10
```

**Check:**
- ΔS < 5.0 → Proceed
- ΔS ≥ 5.0 → SABAR (cool down)

### 2. QC — Validate Floors

**Constitutional Check (F1-F13):**
- F1 (Amanah) — Reversible?
- F2 (Truth) — Documentation matches code?
- F6 (Clarity) — Reduces confusion?
- F9 (Anti-Hantu) — No consciousness claims?

**Verdict:**
- SEAL → Proceed to step 3
- SABAR → Fix violations first
- VOID → Do not proceed

### 3. SEAL — Human Authority

```bash
# Only after SEAL verdict
git add -A
git commit -m "[SEAL] Description"
git push origin <branch>
```

**Requires:** Human approval (F1 Amanah)

---

## Triggers

| Old Trigger | New Unified |
|-------------|-------------|
| `/gitforge` | `/git` or `/trinity` |
| `/gitQC` | (included) |
| `/gitseal` | (included) |

---

**DITEMPA BUKAN DIBERI**
