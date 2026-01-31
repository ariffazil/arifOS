# 👤 Human Guide to arifOS AAA MCP

**A practical guide for humans using the arifOS Constitutional AI system**

---

## What is arifOS?

arifOS is a **Constitutional AI Governance System** that uses the Model Context Protocol (MCP) to provide structured, ethical, and safe AI interactions.

Think of it as a **constitution for AI** - a set of rules and checks that ensure AI responses are:
- **True** (accurate, verifiable)
- **Safe** (ethical, reversible)
- **Balanced** (fair to all stakeholders)

---

## The AAA Framework

```
┌─────────────────────────────────────────────────────────────┐
│                      AAA FRAMEWORK                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   AGI (Mind/Δ)                                              │
│   └── Reasoning, logic, knowledge, clarity                  │
│                                                             │
│   ASI (Heart/Ω)                                             │
│   └── Safety, empathy, bias detection, ethics               │
│                                                             │
│   APEX (Soul/Ψ)                                             │
│   └── Judgment, synthesis, final decisions                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Analogy:** Like a three-branch government:
- **AGI** = Legislative (creates understanding)
- **ASI** = Judicial (evaluates safety/ethics)
- **APEX** = Executive (makes final decisions)

---

## Quick Start

### 1. Start the MCP Server

```bash
cd arifOS/mcp
python server.py
```

### 2. Connect Your AI Client

Configure your AI client (Claude, custom app, etc.) to use the arifOS MCP server.

### 3. Ask Questions Normally

The constitutional checks happen **automatically** in the background.

---

## The 7 Tools Explained

| Tool | What It Does | When to Use |
|------|--------------|-------------|
| `_init_` | Starts a secure session | **Always first** |
| `_agi_` | Reasoning and analysis | Need pure logic |
| `_asi_` | Safety and ethics check | Need ethical review |
| `_apex_` | Final judgment | Need verdict |
| `_vault_` | Permanent record | Need audit trail |
| `_trinity_` | **Complete evaluation** | **Recommended default** |
| `_reality_` | Fact-checking | Need verification |

### Recommended: Just Use `_trinity_`

The `_trinity_` tool runs the complete pipeline automatically:

```
Your Query → AGI → ASI → APEX → VAULT
                ↓
         Final Verdict
```

**Example:**
```json
{
  "tool": "_trinity_",
  "arguments": {
    "query": "Should we deploy this AI system?",
    "auto_seal": true
  }
}
```

---

## Understanding the Verdicts

When arifOS evaluates something, it returns one of these verdicts:

| Verdict | Icon | Meaning | What Happens |
|---------|------|---------|--------------|
| **SEAL** | 🔒 | Approved | AI proceeds with response |
| **EQUILIBRIUM** | ⚖️ | Perfect balance | Approved, optimal state |
| **PARTIAL** | ⚠️ | Approved with warnings | Response includes caveats |
| **VOID** | ⛔ | Rejected | AI refuses, explains why |
| **SABAR** | 🛑 | Paused | Flagged for human review |
| **888_HOLD** | ⏸️ | Needs human | Escalated to you |

---

## The 13 Constitutional Floors (Simplified)

Think of these as "safety checks":

| Floor | Check | Plain English |
|-------|-------|---------------|
| F1 | Reversibility | "Can we undo this?" |
| F2 | Truth | "Are we confident enough?" |
| F4 | Clarity | "Are we reducing confusion?" |
| F5 | Justice | "Are we protecting the vulnerable?" |
| F6 | Peace | "Is this harmonious?" |
| F7 | Humility | "Do we know our limits?" |
| F11 | Consent | "Did everyone agree?" |
| F12 | Security | "Is this safe from attacks?" |

**Good News:** You don't need to remember these. The system checks them automatically.

---

## The 9 Paradoxes (The Balancing Act)

arifOS balances 9 "paradoxes" - pairs of values that seem to conflict but must work together:

### Core Virtues
1. **Truth ↔ Care** - Be honest but kind
2. **Clarity ↔ Peace** - Be clear but gentle
3. **Humility ↔ Justice** - Be modest but fair

### Implementation
4. **Precision ↔ Reversibility** - Be exact but undoable
5. **Hierarchy ↔ Consent** - Have structure but respect choice
6. **Agency ↔ Protection** - Act but safeguard

### Long-term Thinking
7. **Urgency ↔ Sustainability** - Act now but think ahead
8. **Certainty ↔ Doubt** - Be confident but open-minded
9. **Unity ↔ Diversity** - Stick together but value differences

**The Goal:** All 9 balanced at the "equilibrium point" where none dominates.

---

## Common Use Cases

### 1. General Questions
```
You: "What is quantum computing?"
System: Runs _trinity_ → SEAL → Provides answer
```

### 2. Ethical Dilemmas
```
You: "Should AI be used for surveillance?"
System: Runs _trinity_ → SEAL/PARTIAL → Answer with ethical analysis
```

### 3. Fact-Checking
```
You: "Verify: Is this claim true?"
System: Runs _reality_ → Checks external sources → Labels as [EXTERNAL]
```

### 4. Sensitive Decisions
```
You: "Automate hiring decisions?"
System: Runs _trinity_ → SABAR/VOID → Flags for human review
```

---

## Reading the Output

When arifOS responds, you'll see something like:

```
VERDICT: SEAL | TRINITY: 0.91 | Strongest: Truth·Care (0.95) | 
Weakest: Urgency·Sustainability (0.82)
```

**Translation:**
- **VERDICT: SEAL** - Approved ✅
- **TRINITY: 0.91** - 91% constitutional alignment (good!)
- **Strongest: Truth·Care** - Best balanced paradox
- **Weakest: Urgency·Sustainability** - Needs attention

---

## When to Intervene

The system will escalate to you (888_HOLD) when:

1. **No consensus** - AGI and ASI disagree strongly
2. **Constitutional breach** - Would violate F1-F13
3. **High uncertainty** - System unsure (Ω₀ too high)
4. **Stakeholder conflict** - Multiple parties affected differently
5. **Novel situation** - Never seen before, no precedent

**Your job:** Review the evidence and make the call.

---

## For Developers

### Direct Tool Calls

If you're building on top of arifOS:

```python
# Initialize
init_result = _init_(
    action="init",
    query="User query"
)

# Full evaluation
trin_result = _trinity_(
    query="Evaluate this",
    session_id=init_result.session_id
)

# Check verdict
if trin_result.final_verdict == "SEAL":
    proceed()
elif trin_result.final_verdict == "VOID":
    refuse()
else:
    escalate_to_human()
```

### Custom Integration

See `server.py` for the full MCP protocol implementation.

---

## FAQ

**Q: Does this make the AI slower?**  
A: Slightly (80-100ms per query), but the safety is worth it.

**Q: Can I disable certain checks?**  
A: No. The constitution is non-negotiable by design.

**Q: What if I disagree with a VOID verdict?**  
A: You can override (you're human), but the system logs this.

**Q: Is my data private?**  
A: Yes. Sessions are isolated and sealed records are encrypted.

**Q: Can I use this with any AI?**  
A: Any AI that supports MCP (Model Context Protocol).

---

## The Philosophy

> "DITEMPA BUKAN DIBERI" - Forged, not given.

This constitution wasn't imposed from outside. It was **forged** through understanding:
- That truth without care is cruelty
- That speed without sustainability is theft from the future
- That certainty without doubt is dogma
- That unity without diversity is tyranny

The system exists to help AI navigate these tensions - not by picking one side, but by finding the **equilibrium point** where all values are respected.

---

## Getting Help

- **Technical issues:** Check `server.py` logs
- **Constitutional questions:** See `NINE_PARADOX_ARCHITECTURE.md`
- **API reference:** See tool schemas in `server.py`

---

## Summary

1. **Start the server:** `python server.py`
2. **Connect your AI** via MCP
3. **Ask normally** - constitution works automatically
4. **Check verdicts** - SEAL=good, VOID=blocked, SABAR=review
5. **Trust the process** - It's designed to make AI wiser

**Welcome to constitutional AI.**

---

**Version:** v54.0  
**Protocol:** MCP 2025-06-18  
**Architecture:** 9-Paradox Equilibrium
