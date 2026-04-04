# arifOS MCP Trinity: The 20-Tool Architecture

> **Simple Rule:** Above (Cloud) → Below (Local) → Connect (Human)

---

## The Mental Model

Think of arifOS as having **three domains**, each with its own MCP server:

| MCP | Name | Analogy | User | Tools |
|-----|------|---------|------|-------|
| **AAA** | Cloud/Infrastructure | The Factory | DevOps Engineer | 10 |
| **BBB** | Local Agent | The Butler | Personal User | 7 |
| **CCC** | Human Interface | The Telephone | Human (All) | 3 |
| | | | **TOTAL** | **20** |

---

## AAA-MCP: The Cloud Factory ☁️

**What it governs:** Kubernetes, Docker, infrastructure, production systems

**Who uses it:** Platform teams, SREs, DevOps engineers

**10 Tools:**
```
gateway_route_tool           ← Main entry point
k8s_apply_guarded            ← Deploy to K8s
k8s_delete_guarded           ← Delete from K8s (destructive)
k8s_constitutional_apply     ← Preview deployment
k8s_analyze_manifest         ← Security scan
opa_validate_manifest        ← Policy check
opa_list_policies            ← List rules
gateway_list_tools           ← Discovery
gateway_get_decisions        ← Audit log
[1 reserved]
```

**Status:** ✅ **DEPLOYED** (production ready)

---

## BBB-MCP: The Local Butler 💻

**What it governs:** Shell commands, browser, files, memory, credentials

**Who uses it:** Personal users, knowledge workers, executives

**7 Tools:**
```
local_exec_guard             ← Shell commands (rm, sudo, etc.)
browser_session_guard        ← Chrome automation
memory_access_guard          ← MEMORY.md protection
credential_vault             ← API keys & secrets
multi_agent_coordination     ← Spawn sub-agents
skill_install_guard          ← Plugin installation
local_resource_audit         ← System health monitoring
```

**Status:** 📝 **SKETCHED** (ready to implement)

---

## CCC-MCP: The Human Telephone 👤

**What it does:** Connects humans to AI for approvals, summaries, feedback

**Who uses it:** Everyone (when 888_HOLD triggers)

**3 Tools:**
```
human_approval_bridge        ← Get yes/no from human
life_audit_summary           ← Weekly plain-English report
preference_learning          ← Remember user choices
```

**Status:** 🔄 **IN PROGRESS** (SDK/UI development)

---

## How They Connect

```
┌─────────────┐
│   HUMAN     │
│  (Intent)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│               CCC-MCP                       │
│         (The Interface)                     │
│  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Approve?    │  │ Weekly summary      │  │
│  │ [Yes] [No]  │  │ "3 high-risk ops"   │  │
│  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────┘
       │
       │ Verdict: SEAL / SABAR / VOID
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌───────┐ ┌───────┐
│AAA    │ │BBB    │
│Cloud  │ │Local  │
└───────┘ └───────┘
```

---

## Decision Guide

**Q: User says "Deploy payment service to production"**

→ **AAA-MCP** (cloud infrastructure) → k8s_apply_guarded → 888_HOLD → CCC approval → SEAL → Deploy

**Q: User says "Clean my temp files"**

→ **BBB-MCP** (local agent) → local_exec_guard → 888_HOLD → CCC approval → SEAL → Execute

**Q: User says "What did my AI do this week?"**

→ **CCC-MCP** (human interface) → life_audit_summary → Plain English report

---

## What Unifies Them

All three MCPs share:

| Element | Implementation |
|---------|----------------|
| **Constitution** | Same F1-F13 floors |
| **Verdicts** | SEAL, SABAR, VOID, 888_HOLD |
| **Audit** | VAULT999 logging |
| **Identity** | Actor → Accountable human mapping |
| **Blast Radius** | Context-appropriate (pods vs files) |

---

## Implementation Roadmap

| Phase | MCP | Priority | Status |
|-------|-----|----------|--------|
| 1 | AAA | Cloud governance | ✅ DONE |
| 2 | CCC | Human interface | 🔄 NOW |
| 3 | BBB | Local agent guards | 📝 NEXT |

---

## Remember

- **AAA = Above** (Cloud, Infrastructure)
- **BBB = Below** (Local, Desktop)
- **CCC = Connect** (Human, Interface)

Three MCPs. One constitution. Clear separation.

---

**DITEMPA BUKAN DIBERI** 💎🔥🧠
