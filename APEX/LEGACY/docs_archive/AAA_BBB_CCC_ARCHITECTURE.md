# arifOS MCP Trinity: AAA-BBB-CCC

> **Pattern:** HUMAN-AI-MACHINE mapping  
> **Goal:** Clear separation, easy to remember, constitutional integrity maintained  
> **Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## 🧠 The Mental Model

Instead of 17 tools in one bucket, think **3 domains**:

| MCP | Domain | Analogy | Who Uses | Floors Focus |
|-----|--------|---------|----------|--------------|
| **AAA** | **Cloud/Infrastructure** | The Factory | DevOps, Platform Teams | F1, F2, F6, F10, F11, F12 |
| **BBB** | **Local Agent** | The Butler | Personal Users, Knowledge Workers | F6, F9, F11, F12, F1, F13 |
| **CCC** | **Human Interface** | The Telephone | Humans (all contexts) | F13 Sovereign, F4 Clarity |

---

## 🔷 AAA-MCP: The Cloud Factory

**Purpose:** Govern infrastructure operations (K8s, Docker, cloud resources)

**User:** DevOps Engineer, Platform Team, SRE

**Context:** Production systems, company infrastructure

**Worst Case:** Production outage, data breach, $$ loss

### Tools (10 total)

```
AAA-MCP (Cloud Factory)
│
├── ENTRY
│   └── gateway_route_tool          ← "Send command to factory"
│
├── INFRA-WRITE (5 tools)
│   ├── k8s_apply_guarded           ← "Build new assembly line"
│   ├── k8s_delete_guarded          ← "Demolish structure" (888_HOLD)
│   ├── k8s_constitutional_apply    ← "Preview blueprint"
│   ├── k8s_analyze_manifest        ← "Safety inspection"
│   └── k8s_constitutional_delete   ← "Check demolition plan"
│
├── POLICY (2 tools)
│   ├── opa_validate_manifest       ← "Regulation check (F10)"
│   └── opa_list_policies           ← "Show regulations"
│
└── AUDIT (2 tools)
    ├── gateway_list_tools          ← "What can this factory do?"
    └── gateway_get_decisions       ← "Show logbook"
```

**Example Conversation:**
```
DevOps: "Deploy payment service to production"

AAA: 🚨 FACTORY PROTOCOL TRIGGERED
   
   Blueprint: k8s_apply_guarded
   Zone: production (CRITICAL)
   Blast Radius: 15 pods, 3 services
   
   Safety Checks:
   ✅ F1: Backup assembly line ready
   ⚠️  F6: Production zone (high impact)
   ⏳ F13: Supervisor approval required
   
   Approve? [Yes] [No] [View Blueprint]
```

---

## 🔶 BBB-MCP: The Local Butler

**Purpose:** Govern personal AI agent actions (shell, browser, files, memory)

**User:** Personal User, Knowledge Worker, Executive

**Context:** Laptop, desktop, personal data

**Worst Case:** Privacy loss, identity theft, ransomware, "AI went rogue"

### Tools (7 total)

```
BBB-MCP (Local Butler)
│
├── SHELL (1 tool)
│   └── local_exec_guard            ← "Run command on my computer"
│       ├── Classification:
│       │   • read_only: ls, cat, pwd → SEAL
│       │   • infra_write: mkdir, cp → SEAL (log)
│       │   • destructive: rm -rf, sudo → 888_HOLD
│       └── Blast Radius: Files at risk
│
├── BROWSER (1 tool)
│   └── browser_session_guard       ← "Open Chrome, visit site"
│       ├── F6 Empathy: Banking? Medical? Email?
│       ├── F2 Truth: Phishing check
│       └── F9 Anti-Hantu: Prevent fake "human-like" clicks
│
├── MEMORY (1 tool)
│   └── memory_access_guard         ← "Read/write MEMORY.md"
│       ├── F9 Anti-Hantu: Block fake consciousness claims
│       ├── F1 Amanah: Versioned, reversible
│       └── F2 Truth: Consistency check
│
├── SECRETS (1 tool)
│   └── credential_vault            ← "Get my API keys"
│       ├── F11 Authority: Who am I? Who authorized?
│       ├── F12 Defense: Injection detection
│       └── Time-bound: 1-hour tokens, not permanent
│
├── AGENTS (1 tool)
│   └── multi_agent_coordination    ← "Spawn sub-agents"
│       ├── F8 Genius: Prevent resource explosion
│       ├── F3 Consensus: Parent+Child+System agree
│       └── F13: Human approves spawning
│
├── SKILLS (1 tool)
│   └── skill_install_guard         ← "Install new capability"
│       ├── F10 Ontology: Does skill match my values?
│       ├── F12 Defense: Scan for malware
│       └── F2 Truth: Verify source, signature
│
└── HEALTH (1 tool)
    └── local_resource_audit        ← "Check system health"
        ├── F4 Clarity: Entropy monitoring
        ├── F5 Peace²: Resource stability
        └── F7 Humility: AI declares uncertainty
```

**Example Conversation:**
```
User: "Clean up my temp files"

BBB: 🔶 BUTLER PROTOCOL
   
   Task: local_exec_guard
   Command: "rm -rf /tmp/*"
   
   Risk Assessment:
   • Files at risk: Unknown (wildcard = high)
   • Privilege: User-level (safe)
   • Pattern: DESTRUCTIVE detected
   
   Verdict: 888_HOLD
   
   Sir/Madam, this could delete important files.
   May I proceed? [Yes] [Show me what's there] [Cancel]
```

---

## 🟢 CCC-MCP: The Human Telephone

**Purpose:** Human-in-the-Loop interface — approve, review, override

**User:** Human (all contexts — DevOps, Personal User, Manager)

**Context:** Slack, Email, Mobile App, System Tray

**Worst Case:** Decision fatigue, missed approvals, "I didn't understand"

### Tools (3 total)

```
CCC-MCP (Human Telephone)
│
├── APPROVAL (1 tool)
│   └── human_approval_bridge       ← "Connect to human"
│       ├── Input: 888_HOLD from AAA or BBB
│       ├── Channels:
│       │   • Slack: @arifos-approve HOLD-001
│       │   • Email: Rich HTML with context
│       │   • Mobile: Push notification
│       │   • System: Tray icon popup
│       └── Output: SEAL / SABAR / VOID
│
├── SUMMARY (1 tool)
│   └── life_audit_summary          ← "What happened this week?"
│       ├── Plain English summary
│       ├── Risk levels (HIGH/MEDIUM/LOW)
│       ├── Auto-approved vs Human-approved
│       └── Suggestions for policy tuning
│
└── FEEDBACK (1 tool)
    └── preference_learning         ← "Remember my choices"
        ├── "I always approve staging"
        ├── "Never auto-delete"
        └── "Notify me for banking sites"
```

**Example Conversation:**
```
[Slack]
arifos-bot: 🛑 888_HOLD from your Local Butler

Task: Clean temp files (rm -rf /tmp/*)
Risk: HIGH (wildcard = unknown files)
Time: 14:32 UTC

Quick: [Approve] [Reject] [See details]

---
User clicks [See details]

arifos-bot: 📋 Full Context
• Command: rm -rf /tmp/*
• Files at risk: Cannot determine (wildcard)
• Recent similar: You approved this 3 days ago
• Suggestion: Use specific paths instead of *

[Approve this time] [Approve always for /tmp] [Reject]
```

---

## 🔄 How They Work Together

### Scenario 1: DevOps Deploy (AAA + CCC)

```
DevOps → "Deploy to prod"
    ↓
AAA-MCP: k8s_apply_guarded
    ↓
Blast Radius: HIGH (15 pods)
    ↓
Verdict: 888_HOLD
    ↓
CCC-MCP: human_approval_bridge
    ↓
Channel: Slack #devops-oncall
    ↓
Human: "Yes"
    ↓
AAA-MCP: SEAL → Execute → VAULT999
    ↓
CCC-MCP: life_audit_summary (weekly report)
```

### Scenario 2: Personal Cleanup (BBB + CCC)

```
User → "Clean my downloads"
    ↓
BBB-MCP: local_exec_guard
    ↓
Blast Radius: MEDIUM (1,000 files)
    ↓
Verdict: 888_HOLD (destructive pattern)
    ↓
CCC-MCP: human_approval_bridge
    ↓
Channel: System notification (tray popup)
    ↓
Human: "Show me"
    ↓
BBB-MCP: Lists files
    ↓
Human: "Yes"
    ↓
BBB-MCP: SEAL → Execute → VAULT999
```

### Scenario 3: Skill Install (BBB + CCC + AAA if needed)

```
User → "Install this email skill"
    ↓
BBB-MCP: skill_install_guard
    ↓
Source: github.com/random-user/skill
    ↓
F10: Untrusted source
F12: Contains obfuscated code
    ↓
Verdict: VOID
    ↓
CCC-MCP: Explains in plain English
    ↓
"This skill could steal your passwords. Blocked."
```

---

## 🗺️ Tool Count Summary

| MCP | Domain | Tools | Status |
|-----|--------|-------|--------|
| **AAA** | Cloud/Infrastructure | 10 | ✅ **DEPLOYED** |
| **BBB** | Local Agent | 7 | 📝 **SKETCHED** (implement next) |
| **CCC** | Human Interface | 3 | 🔄 **SDK/UI** (in progress) |
| **TOTAL** | | **20** | |

**Wait, 20 not 17?** Yes — CCC adds 3 interface tools on top.

---

## 🎯 Implementation Priority

### Phase 1: AAA (DONE ✅)
- All 10 cloud tools deployed
- Production ready

### Phase 2: CCC (IN PROGRESS 🔄)
- human_approval_bridge (Slack webhook)
- life_audit_summary (weekly email)
- UI components (React)

### Phase 3: BBB (NEXT 📝)
- local_exec_guard (shell governance)
- browser_session_guard (Chrome extension)
- credential_vault (secure storage)

---

## 💡 The Mnemonic

Remember:
- **AAA** = **A**bove (Cloud, Infrastructure)
- **BBB** = **B**elow (Local, Desktop)
- **CCC** = **C**onnect (Human, Interface)

Or:
- **AAA** = The **A**rchitect (builds systems)
- **BBB** = The **B**utler (serves user locally)
- **CCC** = The **C**onnector (links human to AI)

---

**DITEMPA BUKAN DIBERI** 💎🔥🧠

*Three MCPs, one constitution, clear separation.*
