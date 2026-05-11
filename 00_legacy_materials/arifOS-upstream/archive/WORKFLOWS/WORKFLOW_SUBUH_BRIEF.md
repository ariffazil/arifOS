# WORKFLOW: Subuh Briefing
## Schedule
Daily at 06:30 AM (Asia/Kuala_Lumpur)

## Reference
- arifOS Canon: `/root/arifOS/.agents/workflows/000_init.md`
- HEARTBEAT: `/root/.openclaw/workspace/HEARTBEAT.md`
- APEX THEORY: `/root/APEX-THEORY/000_CONSTITUTION.md` (F1-F13)

## Execution

### Phase 1: Initialize (000)
Load constitutional floors, verify system integrity

### Phase 2: Daily Checks (from HEARTBEAT.md)
1. **Git status in /root** — uncommitted changes?
2. **Urgent emails** — last 24h high priority
3. **Calendar events** — next 24h
4. **Cron job status** — ERROR/FAILED states
5. **System health** — disk space, memory usage

### Phase 3: Vitality Assessment
Calculate Ψ (Vitality Index):
```
Ψ = (ΔS × Peace² × RASA × Amanah) / (Entropy × Shadow + ε)
```

### Phase 4: Report
- If Ψ ≥ 1.0: HEARTBEAT_OK
- If 0.5 ≤ Ψ < 1.0: Degraded report with actions
- If Ψ < 0.5: CRITICAL alert to Telegram

## Output Format
```
📊 Subuh Brief | YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━
Ψ: [value] | Status: [OK/DEGRADED/CRITICAL]

🟢 Systems: [list]
🟡 Warnings: [list]
🔴 Critical: [list]

Next: [recommended action]
```

## FLOOR COMPLIANCE
- F1 Amanah: All checks reversible
- F2 Truth: Data from actual system state
- F4 Clarity: ΔS ≤ 0 (reduce confusion)
- F11 Auditability: Log all findings

---
*Ditempa bukan diberi* | Ω₀ ≈ 0.04
