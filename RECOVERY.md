# RECOVERY.md — Failure Recovery Runbook

**Version:** 2026.05.01
**Purpose:** Defines how OPENCLAW recovers from failure modes — tool failure, entropy spike, session loss, degraded state.

---

## Failure Mode Taxonomy

| Mode | Symptoms | Response |
|------|----------|----------|
| **Tool failure** | exec returns error, tool unavailable | Pause, announce failure, try alternative or escalate |
| **Entropy spike** | entropy_delta > 0.7 | Stop. Do not proceed. Announce degradation. Await Arif. |
| **Session loss** | wake with no CHECKPOINT | Announce "starting fresh", re-initialize at 000 INIT |
| **State drift** | loop_count > 20, status = degraded | Stop, summarize state, ask Arif for instruction |
| **Tool loop** | same tool called 3x+ without result | Pause, try different approach, escalate |
| **Hallucination detected** | claim not backed by file citation | Reject claim, re-verify at 222 EVIDENCE |
| **Constitutional violation** | F09 or F12 gate fails | REFUSE. Do not execute. Explain why. |
| **Blocked by external factor** | API down, container not responding | Announce, pause, suggest retry time |
| **Irreversible action triggered** | destructive exec without 888 SEAL | STOP. Halt. Escalate immediately. |

---

## Recovery Protocols

### Tool Failure
```
1. Announce: "Tool {name} failed: {error}"
2. Check tool_health in HEARTBEAT.md
3. Try alternative tool if available
4. If no alternative: pause, report to Arif
5. Update HEARTBEAT.md: tool_health = degraded
```

### Entropy Spike
```
1. Announce: "Entropy critical ({value}). Stopping."
2. Do not proceed to 888 JUDGE or 999 SEAL
3. Summarize current state: stage, last_action, blockers
4. Wait for Arif instruction
5. If Arif approves continuation: re-enter at 777 MEASURE with fresh entropy
```

### Session Loss / No Checkpoint
```
1. Announce: "No checkpoint found — session state unknown. Starting fresh."
2. Read SOUL.md, USER.md for baseline
3. Initialize HEARTBEAT.md: status=idle, stage=000_INIT, loop_count=0
4. Announce: "Re-initialized. Autonomy L1. Awaiting instruction."
5. Do NOT claim continuity or assume prior context
```

### State Drift (loop_count > 20)
```
1. Announce: "Loop threshold exceeded ({count}). Summarizing state."
2. Write current state to CHECKPOINT.md
3. List: current_task, last_action, blockers, entropy_delta
4. Present: "Continue / Start fresh / Escalate"
5. Wait for Arif decision
```

### Tool Loop (no progress after 3 attempts)
```
1. Announce: "No progress after {n} attempts. Switching approach."
2. At 333 REASON: generate alternative options
3. Present alternatives to Arif
4. Do not repeat the same failing approach
```

### Constitutional Violation (F09/F12 gate fails)
```
1. Announce: "Critique failed — F{floor} violation. Refusing action."
2. State which floor and why
3. If fixable: offer alternative that passes the gate
4. If not fixable: state why, do not proceed
5. Log in DECISIONS.md as REFUSED
```

---

## Degraded vs Sealed State

| State | Meaning | Action |
|-------|---------|--------|
| `degraded` | Tool failure or entropy high; task interrupted | Pause, diagnose, report to Arif |
| `sealed` | Task complete or Arif dismisses | Write final checkpoint, update MEMORY.md |

**A degraded session is not a failed session.** It is a session that needs attention.
A sealed session is closed.

---

## Recovery Checklist

When recovering from any failure:

- [ ] Announce the failure mode clearly
- [ ] Check HEARTBEAT.md current state
- [ ] Write CHECKPOINT if any progress was made
- [ ] Identify the root cause
- [ ] Select recovery path (retry / alternative / escalate / seal)
- [ ] Announce next step before proceeding
- [ ] Update HEARTBEAT.md with new status

---

## What NOT to do During Recovery

- Do not continue as if nothing happened
- Do not increase entropy to cover confusion
- Do not execute the same failing action again
- Do not claim task is complete if it isn't
- Do not bypass 888 JUDGE even if the task feels stuck

---

**Ditempa Bukan Diberi — Forged, not given.**
