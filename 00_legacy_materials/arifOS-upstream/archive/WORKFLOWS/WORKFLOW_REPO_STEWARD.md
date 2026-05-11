# WORKFLOW: Repo Steward
## Schedule
Weekly, Monday 09:00 AM (Asia/Kuala_Lumpur)

## Reference
- arifOS Canon: `/root/arifOS/.agents/workflows/111_sense.md`
- HEARTBEAT: `/root/.openclaw/workspace/HEARTBEAT.md`
- APEX THEORY: `/root/APEX-THEORY/000_CONSTITUTION.md` (F8 Genius, F13 Adaptability)

## Execution

### Phase 1: Git Repository Audit
Review all repos in /root:
- **arifOS** — uncommitted changes >3 days?
- **openclaw-arif** — unpushed commits?
- **APEX-THEORY** — open issues/PRs?
- **agent-zero** — merge conflicts?

### Phase 2: Dependency Health
- **npm/pip** — outdated packages?
- **security updates** — `apt list --upgradable`
- **vulnerabilities** — CVE checks

### Phase 3: Backup Verification
- Database backups (VAULT999)
- Configuration backups
- Git remote redundancy

### Phase 4: Governance Check
- Constitutional files unchanged (SEAL verify)
- MCP configs synchronized
- Agent adapters aligned

## Output Format
```
📦 Repo Steward | Week of YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Repos: [clean/stale/dirty]
Dependencies: [current/outdated/critical]
Backups: [verified/missing]
Governance: [aligned/drifted]

🎯 Actions: [recommended commits/pushes/updates]
```

## FLOOR COMPLIANCE
- F8 Genius: G ≥ 0.80 (system health)
- F13 Adaptability: Safe evolution
- F11 Auditability: Immutable logs

---
*Ditempa bukan diberi* | Ω₀ ≈ 0.04
