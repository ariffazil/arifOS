# L3 Procedural Memory — Entry Point

**Layer:** L3 | **Authority:** ARIF | **Purpose:** Reusable tool sequences and SOPs

---

## What Goes Here

Procedural memories are **verified, repeatable tool sequences** that have been used successfully 3+ times. They are not notes about what happened — they are step-by-step instructions for making it happen again.

**Examples:**
- `restart-mcp-container.md` — how to restart a specific MCP container
- `deploy-arifos-a-forge.md` — full deploy pipeline
- `qdrant-backup.md` — vector DB backup procedure
- `well-health-check.md` — WELL telemetry diagnostic procedure

---

## When to Create a Procedure

A procedure is created when:
1. **Repetition**: Same task done 3+ times successfully
2. **Pattern detected**: Tool sequence is stable and repeatable
3. **Gate passes**: F8 (elegant), F12 (safe), F1 (reversible)

---

## Procedure Template

```markdown
# Procedure: <task-name>

**Layer:** L3 | **Status:** VERIFIED | **Success rate:** 3/3
**Last used:** YYYY-MM-DD | **Last verified:** YYYY-MM-DD
**Tools used:** [tool_a] → [tool_b] → [tool_c]

## Steps

1. [Step description]
2. [Step description]
3. [Step description]

## Rollback / Undo

[How to revert if this goes wrong]

## Verification

[How to confirm the task succeeded]

## Failsafes

[Known failure modes and mitigations]
```

---

## Current Procedures

_Empty — procedures are created from L1→L3 promotion only._

---

## Promotion Trigger

To promote an L1 episodic note to L3:

```
In episodic entry, add:
[PROMOTE-TO-L3] tool_sequence=<list>, success_count=<n>

System evaluates gate:
  [ ] F8: steps minimal and correct
  [ ] F12: no injection-prone content
  [ ] F1: rollback documented

If pass → creates memory/procedures/<name>.md
If fail → returns gate failure reason
```

---

## Governance

- F8 Genius: Procedures must be elegant, not complex
- F12 Injection: No raw shell commands without escaping
- F1 Amanah: Every procedure must have a rollback path
- F13 Sovereign: Human must approve critical infrastructure procedures

**DITEMPA BUKAN DIBERI — forged from verified repetition, not assumed.**
