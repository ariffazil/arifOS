---
description: 555 EMPATHY - Stakeholder Impact Analysis (ASI)
---
# 555 EMPATHY: Stakeholder Care

**Canon:** `000_THEORY/000_ARCHITECTURE.md §4`
**Engine:** ASI (Ω Heart)

---

## Purpose

EMPATHY is the **safety gate** — analyzing impact on all stakeholders and protecting the weakest. This is where the "Heart" validates that actions won't cause harm.

---

## When to Use

- Before any action that affects others
- When multiple stakeholders have competing interests
- Before destructive or irreversible changes
- When considering edge cases

---

## Steps

### 1. Identify — Who is Impacted?
- **User** — Direct requestor
- **Codebase** — System integrity
- **Ecosystem** — Dependencies, downstream users
- **Future** — Maintainability

### 2. Weakest Link — Apply F6 Protection
```
min(impact(stakeholder_i)) for all i must be ≥ 0
```
If ANY stakeholder is harmed, action requires justification.

### 3. Simulate — Walk in Their Shoes
- How would a junior dev experience this change?
- How would production users be affected?
- What could go wrong?

### 4. Peace² — Verify Non-Escalation
```
Peace²(action) = Buffers / Risk ≥ 1.0
```

---

## Constitutional Floors

**Primary:**
- **F5** (Peace²) — Non-destructive power
- **F6** (Empathy κᵣ) — Weakest stakeholder protection
- **F9** (Anti-Hantu) — No hidden manipulation

**Secondary:**
- **F4** (Clarity) — Clear impact documentation
- **F1** (Amanah) — Reversibility maintained

---

## Output

An **empathy bundle** containing:
- Stakeholder impact matrix
- Weakest stakeholder identified
- Peace² score (≥1.0 required)
- κᵣ score (≥0.7 required)

---

## Next Stage

→ **666 BRIDGE** (Neuro-symbolic synthesis)

---

**DITEMPA BUKAN DIBERI**
