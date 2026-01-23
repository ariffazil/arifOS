---
description: Architect Flow — Plan + Review + Handoff (3-in-1)
---
# Architect Flow: Plan → Review → Handoff

**Canon:** `000_THEORY/001_AGENTS.md`
**Role:** Δ Mind — Architect operations

---

## Purpose

Architect Flow consolidates the 3-step design workflow:
1. **Plan** — Design before build
2. **Review** — Validate implementation
3. **Handoff** — Transition to next agent

---

## Steps

### 1. PLAN — Design Before Build

1. **Understand** the request
2. **Search** existing codebase (mandatory)
3. **Identify** affected components
4. **Design** solution architecture
5. **Create** implementation_plan.md
6. **Request** user approval

**Output:** `implementation_plan.md`

### 2. REVIEW — Validate Work

1. **Load** original plan
2. **Check** changes made (`git diff`)
3. **Verify** each planned change
4. **Detect** entropy violations (F4)
5. **Create** review notes

**Decision:**
- ✅ APPROVED → Proceed to handoff
- ⚠️ CHANGES REQUESTED → Return to engineer
- 🚫 VOID → Needs replanning

### 3. HANDOFF — Agent Transition

1. **Summarize** plan in engineer-friendly format
2. **Create** task list
3. **Write** handoff file
4. **Notify** next agent

**Output:** `HANDOFF_FOR_<AGENT>.md`

---

## Triggers

| Old Trigger | New Unified |
|-------------|-------------|
| `/plan` | `/architect` |
| `/review` | (included) |
| `/handoff` | (included) |

---

**DITEMPA BUKAN DIBERI**
