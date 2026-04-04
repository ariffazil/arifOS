# arifOS MCP Quick Reference

> **The 20-Second Guide to 20 Tools**

---

## 🧠 Remember: "Above, Below, Connect"

```
     ☁️ AAA-MCP ☁️          👤 CCC-MCP 👤          💻 BBB-MCP 💻
    (Cloud Factory)      (Human Bridge)       (Local Butler)
         ↑                      ↑                      ↑
    DevOps engineer ←→ YOU ←→ Personal user
         ↑                      ↑                      ↑
    "Deploy to prod"      "Approve this"        "Clean my files"
```

---

## 🔷 AAA-MCP (Cloud)

**When to use:** Kubernetes, Docker, Infrastructure

**Remember:** "Factory operations"

| Tool | Purpose | 888_HOLD Trigger |
|------|---------|------------------|
| `gateway_route_tool` | Main entry | High blast radius |
| `k8s_apply_guarded` | Deploy | Production namespace |
| `k8s_delete_guarded` | Delete | Always (destructive) |
| `k8s_constitutional_apply` | Preview | - (dry-run) |
| `k8s_analyze_manifest` | Inspect | - (read-only) |
| `opa_validate_manifest` | Policy check | - (read-only) |
| `opa_list_policies` | List rules | - (read-only) |
| `gateway_list_tools` | Discovery | - (read-only) |
| `gateway_get_decisions` | Audit log | - (read-only) |
| *(1 more)* | TBD | - |

**Count:** 10 tools

**Status:** ✅ DEPLOYED

---

## 🟢 CCC-MCP (Human Interface)

**When to use:** Approving, reviewing, understanding

**Remember:** "The telephone"

| Tool | Purpose | Where |
|------|---------|-------|
| `human_approval_bridge` | Get yes/no | Slack, Email, Mobile |
| `life_audit_summary` | Weekly report | Email digest |
| `preference_learning` | Remember choices | Background |

**Count:** 3 tools

**Status:** 🔄 IN PROGRESS

---

## 🔶 BBB-MCP (Local Agent)

**When to use:** Shell, browser, files, memory

**Remember:** "The butler"

| Tool | Purpose | 888_HOLD Trigger |
|------|---------|------------------|
| `local_exec_guard` | Run commands | rm, sudo, curl \| sh |
| `browser_session_guard` | Open Chrome | Banking, passwords |
| `memory_access_guard` | Edit MEMORY.md | Fake consciousness |
| `credential_vault` | Get API keys | Production secrets |
| `multi_agent_coordination` | Spawn agents | >3 sub-agents |
| `skill_install_guard` | Install plugin | Untrusted source |
| `local_resource_audit` | System health | High entropy |

**Count:** 7 tools

**Status:** 📝 SKETCHED

---

## 🎯 Decision Tree

```
What is the user trying to do?
│
├─► Deploy/scale/manage servers? ──► AAA-MCP (Cloud)
│
├─► Run command/browser/file on their laptop? ──► BBB-MCP (Local)
│
└─► Approve/review/understand what AI did? ──► CCC-MCP (Human)
```

---

## 🚨 888_HOLD Triggers by MCP

| MCP | Triggers 888_HOLD When... |
|-----|---------------------------|
| **AAA** | Production namespace, destructive ops, high blast radius |
| **BBB** | Shell commands (rm, sudo), banking sites, fake memories |
| **CCC** | Human explicitly requests hold, anomaly detected |

---

## 📊 One-Line Summaries

- **AAA:** *"The cloud factory — builds and destroys infrastructure"*
- **BBB:** *"The local butler — serves your laptop safely"*
- **CCC:** *"The human connector — gets your approval"*

---

## 🎓 Exam Question

**Q:** User says "Delete my temp files"

**A:** BBB-MCP (local command) → local_exec_guard → 888_HOLD → CCC-MCP → Human approves → SEAL → Execute

**Q:** User says "Deploy to production"

**A:** AAA-MCP (cloud infrastructure) → k8s_apply_guarded → 888_HOLD → CCC-MCP → Human approves → SEAL → Deploy

---

**DITEMPA BUKAN DIBERI** 💎🔥🧠

*Above, Below, Connect — Three MCPs, one constitution.*
