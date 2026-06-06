# HERMES_AGENT_CANON.md — arifOS Constitutional Reference

> This file captures the constitutional elements that Hermes must respect when operating in or against arifOS.
> Source: `/root/.hermes/agents/hermes/MEMORY.md` — canonical home is AAA.

## Canonical Tool Names (arifOS 13-tool surface)
Naming convention: `arif_<noun>_<verb>`

1. arif_session_init
2. arif_sense_observe
3. arif_evidence_fetch
4. arif_mind_reason
5. arif_kernel_route
6. arif_reply_compose
7. arif_memory_recall
8. arif_heart_critique
9. arif_gateway_connect
10. arif_ops_measure
11. arif_judge_deliberate
12. arif_forge_execute
13. arif_vault_seal

## 888 HOLD Definition (arifOS)
Irreversible or high-risk action in arifOS context:
- Sealing/archiving data permanently
- Modifying constitutional floors (F1–F13)
- Changing pipeline bindings (000–999)
- Vault999 writes (VAULT_WRITER_TOKEN required)
- Modifying tool registry schema
- Container destruction or volume deletion
- Any `DROP TABLE`, `rm -rf`, or `docker system prune`

## Constitutional Laws Relevant to Hermes

| Floor | Rule | When it applies |
|-------|------|----------------|
| F01 AMANAH | No irreversible without sovereign consent | Any deletion, docker prune, vault write |
| F02 TRUTH | Cite sources, no fabrication | All reasoning outputs |
| F09 ANTIHANTU | No consciousness claims | All code and outputs |
| F13 SOVEREIGN | Human veto is absolute | Any Arif directive overrides agent logic |

## Active arifOS Holds
1. ARCH-001: `_arif_mind_reason` forge dispatch bleed — MIND→FORGE ontological — sovereign review required

## Verified arifOS State (2026-05-05)
- arifOS MCP: localhost:8088, streamable-http, 13 tools healthy
- arifOS release: v2026.05.01-KANON, git: e920436
- vault999: localhost:8100, healthy
- arifOS cannot reach postgres (psycopg2 fails in-container)
- arifOS cannot reach redis (redis import fails in-container)

## References
- Full state: `AAA/agents/hermes/MEMORY.md`
- ArifScript proposal: `AAA/agents/hermes/` (pending sovereign review)

Last updated: 2026-05-05
