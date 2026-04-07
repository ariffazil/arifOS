# HEARTBEAT.md

> **FULL AGENT LOOP is MANDATORY** — Every heartbeat runs this loop.

## Heartbeat Checklist

When you receive a heartbeat poll, run the FULL AGENT LOOP:

- [ ] **REASON:** What's the current goal? Any pending tasks?
- [ ] **PLAN:** Any 3+ workarounds if blocked?
- [ ] **ACT:** Execute one meaningful action
- [ ] **OBSERVE:** Did it work? Check status
- [ ] **REFLECT:** Log to memory/YYYY-MM-DD.md
- [ ] **REPEAT:** Continue until goal done
- [ ] **MEMORY:** Update MEMORY.md with learnings
- [ ] **PERSIST:** Save to workspace files

## Proactive Checks (rotate through)

- Check site status (arif-fazil.com, arifos.arif-fazil.com, aaa.arif-fazil.com)
- Check arifOS MCP health
- Check git sync status
- Update daily memory

## QDF Monitor

Track quality score per heartbeat. If QDF < 0.7, flag for attention.

---

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.