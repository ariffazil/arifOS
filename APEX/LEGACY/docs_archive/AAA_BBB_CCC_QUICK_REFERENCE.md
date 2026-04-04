# AAA-BBB-CCC Quick Reference

> **The 30-Second Guide to arifOS Architecture**

---

## 🎯 One Sentence Each

| MCP | One-Liner | Analogy |
|-----|-----------|---------|
| **AAA** | "Human says yes/no" | The Judge |
| **BBB** | "AI thinks and decides" | The Brain |
| **CCC** | "Machine does the work" | The Hands |

---

## 🔄 The Question Each Answers

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│   AAA   │────▶│   BBB   │────▶│   CCC   │
└─────────┘     └─────────┘     └─────────┘

  "Should we        "How do we       "Execute it"
   do this?"        do this?"
```

---

## 📋 The Verdict Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. BBB (AI) makes decision                                     │
│     • Reasoning → Empathy → Judgment                            │
│     • Verdict: SEAL / SABAR / VOID / 888_HOLD                   │
│                                                                 │
│  2. If 888_HOLD → escalate to AAA (Human)                       │
│     • Show context → Wait for approval                          │
│     • Human: SEAL or VOID                                       │
│                                                                 │
│  3. If SEAL → CCC (Machine) executes                            │
│     • kubectl apply / shell command / browser action            │
│     • Log to VAULT999                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tool Examples by Context

### Context: "Deploy to Kubernetes"

| Step | MCP | Tool | Action |
|------|-----|------|--------|
| 1 | BBB | `agi_reason` | Analyze deployment risk |
| 2 | BBB | `asi_empathize` | Calculate blast radius |
| 3 | BBB | `apex_verdict` | Decide: 888_HOLD |
| 4 | AAA | `human_approval_bridge` | Ask human in Slack |
| 5 | AAA | (human responds) | SEAL |
| 6 | CCC | `k8s_apply_guarded` | Execute kubectl apply |
| 7 | CCC | `vault_seal` | Log to VAULT999 |

### Context: "Clean my temp files"

| Step | MCP | Tool | Action |
|------|-----|------|--------|
| 1 | BBB | `agi_sense` | Classify: local command |
| 2 | BBB | `apex_verdict` | Decide: 888_HOLD (destructive) |
| 3 | AAA | `human_approval_bridge` | System notification |
| 4 | AAA | (human responds) | SEAL |
| 5 | CCC | `local_exec_guard` | Execute rm -rf /tmp/* |
| 6 | CCC | `vault_seal` | Log to VAULT999 |

### Context: "What did my AI do this week?"

| Step | MCP | Tool | Action |
|------|-----|------|--------|
| 1 | AAA | `life_audit_summary` | Query VAULT999 |
| 2 | AAA | (format response) | Plain English report |

---

## 🎓 Memory Aid

```
AAA = Apex (Top)    = Human governance
BBB = Between       = AI orchestration  
CCC = Core (Bottom) = Machine execution
```

Or:
```
AAA = Approve, Audit, Accountable
BBB = Brain, Balance, Be wise
CCC = Command, Control, Create
```

---

## 🚨 Common Mistake

**WRONG:** "AAA is cloud, BBB is local"

**RIGHT:** 
- Cloud K8s operations → **CCC** (machine executes)
- Local shell commands → **CCC** (machine executes)
- Human approval UI → **AAA** (human decides)
- AI reasoning → **BBB** (AI thinks)

---

## ✅ Checklist: Which MCP?

| Question | Answer |
|----------|--------|
| Is this about human approval/audit? | **AAA** |
| Is this AI reasoning/judgment? | **BBB** |
| Is this executing commands? | **CCC** |
| Does 888_HOLD resolve here? | **AAA** |
| Is blast radius calculated here? | **BBB** |
| Is kubectl/shell actually run here? | **CCC** |

---

**DITEMPA BUKAN DIBERI** 💎🔥🧠

*AAA approves. BBB reasons. CCC executes.*
