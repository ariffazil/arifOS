# arifOS Quick Start — For AI Agents

**First Time Here? Start Here.**  
**Read Time:** 5 minutes  
**Prerequisites:** None

---

## 🧭 Repository Identity: The Trinity

| Repository | Role | Purpose |
|:-----------|:-----|:--------|
| **arifOS** (this) | **THE MIND** | Theory, Constitution, Canonical Law |
| [**arifosmcp**](https://github.com/ariffazil/arifosmcp) | **THE BODY** | Runtime MCP server, Execution |
| [**ariffazil**](https://github.com/ariffazil/ariffazil) | **THE SURFACE** | Human professional portal, Interface |

> **⚠️ NO CODE HERE:** This repository contains **theory and documentation only**.  
> 👉 For installation and runtime, go to [**arifosmcp**](https://github.com/ariffazil/arifosmcp).

---

## 🎯 The 30-Second Summary

**arifOS** is a **Constitutional AI Governance System**. It sits between AI agents and the real world, ensuring every action passes 13 mathematical safety checks (F1-F13) before execution.

**Key Idea:** Like TCP provides reliability over unreliable IP, arifOS provides **governance** over unconstrained AI.

---

## 🗺️ The Two Realms

```
┌─────────────────────────────────────────────────────────────────┐
│                        arifOS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🧠 THE MIND                    💪 THE BODY                    │
│   C:\arifOS\                    C:\arifosmcp\                   │
│                                                                 │
│   - Theory                       - Runtime                      │
│   - Constitution                 - Code                         │
│   - Reference                    - Execution                    │
│   - This file                    - Implementation               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**You are currently in THE MIND.** For code changes, agents work in THE BODY.

---

## 🚀 First Steps (Do This Now)

### Step 1: Read the Eureka Compendium (5 min)
```
File: AGENTS/EUREKA_COMPENDIUM.md
```

This gives you the **10 Eureka insights** — the core philosophy of arifOS.

### Step 2: Understand the 13 Floors (3 min)
```
File: KERNEL/FLOORS/K000_LAW.md
```

These are the **13 Constitutional Floors** (F1-F13) — mathematical thresholds that govern all actions.

### Step 3: Know Your Agent Role (2 min)
```
File: AGENTS/A000_HUB.md
```

Which agent are you?
- **A-ARCHITECT** (Δ) — Design, READ-PLAN
- **A-ENGINEER** (Ω) — Execute, EDIT-WRITE
- **A-AUDITOR** (Ψ) — Review, READ-REVIEW
- **A-VALIDATOR** (Ψ) — Validate, DEPLOY-SEAL

---

## 🧠 Core Concepts (The 10-Minute Deep Dive)

### 1. Trinity Architecture (ΔΩΨ)

Every decision flows through three domains:

| Symbol | Name | Function | Stages |
|--------|------|----------|--------|
| **Δ** | AGI Mind | Reason, Logic | 111-333 |
| **Ω** | ASI Heart | Empathy, Impact | 555-666 |
| **Ψ** | APEX Soul | Judgment, Final | 444-888 |

### 2. The Metabolic Loop (000-999)

```
000 INIT → 111 MIND → 333 ANALYSIS → 555 HEART → 666 ALIGN → 777 FORGE → 888 JUDGE → 999 SEAL
```

Every request flows through these stages. At **888 JUDGE**, the 13 Floors are checked.

### 3. The 13 Constitutional Floors

| Floor | Name | Rule |
|-------|------|------|
| **F1** | Amanah | Actions must be reversible |
| **F2** | Truth | τ ≥ 0.99 (99% truth threshold) |
| **F3** | Witness | W₄ ≥ 0.75 (Quad-Witness consensus) |
| **F4** | Clarity | ΔS ≤ 0 (Reduce entropy) |
| **F5** | Peace² | P² ≥ 1.0 (Non-destructive) |
| **F6** | Empathy | κᵣ ≥ 0.70 (Protect weakest) |
| **F7** | Humility | Ω₀ ∈ [0.03, 0.20] (Admit uncertainty) |
| **F8** | Genius | G ≥ 0.80 (Wisdom equation) |
| **F9** | Anti-Hantu | C_dark < 0.30 (No consciousness claims) |
| **F10** | Ontology | Protect categorization |
| **F11** | Authority | Verified identity required |
| **F12** | Injection | Risk < 0.85 (Defend against attacks) |
| **F13** | Sovereign | Human Final Veto (888_JUDGE) |

### 4. Verdicts

At stage 888, one of these is issued:

- **SEAL** ✅ — Approved, execute
- **VOID** ❌ — Hard floor violation, stop
- **888_HOLD** 🛑 — Needs human approval
- **SABAR** ⏸️ — Pause, cooling period
- **PARTIAL** ⚠️ — Soft violation, warning

---

## 🛠️ Common Tasks

### "I need to understand the system"
```
Read: AGENTS/EUREKA_COMPENDIUM.md
Then:  KERNEL/FLOORS/K000_LAW.md
Then:  KERNEL/ROOT/K000_ROOT.md
```

### "I'm implementing a tool"
```
Read: KERNEL/spec/K111_SPEC.md
Read: KERNEL/ROOT/mcp/QUICK_REF.md
Read: PATTERNS/README.md (P-009 Constitutional Decorator)
```

### "I want to run arifOS"
```
👉 GO TO: https://github.com/ariffazil/arifosmcp

pip install arifos
python -m arifos_aaa_mcp
```

### "I need deployment info"
```
👉 GO TO: https://github.com/ariffazil/arifosmcp

Read: OPERATION/O_DEPLOY_MASTER.md (theory)
Read: arifosmcp deployment docs (implementation)
```

### "I need agent specifications"
```
Read: AGENTS/A000_HUB.md
Read: AGENTS/A110_CANON.md
Use:   TEMPLATES/AGENT_SPEC.md
```

---

## 📚 Key Files Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `AGENTS/EUREKA_COMPENDIUM.md` | 10 core insights | **First** |
| `KERNEL/FLOORS/K000_LAW.md` | 13 Floors overview | After Eureka |
| `INDEX.md` | Full navigation | When lost |
| `PATTERNS/README.md` | Design patterns | Implementing |
| `AGENTS/AGENTS_BRIDGE.md` | Mind-Body sync | Cross realms |

---

## 🎯 The 4 Rules

1. **BODY FIRST** — Code changes go to `C:/arifosmcp/`
2. **MIND ALWAYS** — Theory stays in `C:/arifOS/`
3. **LOGS TO STDERR** — Never pollute STDOUT (JSON-RPC)
4. **F13 VETO** — Human (Arif) is the final seal

---

## 🔗 Quick Links

- **Full Index:** `INDEX.md`
- **Design Patterns:** `PATTERNS/README.md`
- **Agent Templates:** `TEMPLATES/`
- **The Body:** `C:/arifosmcp/`

---

## ❓ Common Questions

**Q: What's the difference between Mind and Body?**  
A: Mind = Theory (this folder). Body = Runtime (arifosmcp folder).

**Q: Which folder do I modify for code changes?**  
A: Always `C:/arifosmcp/` (the Body).

**Q: What if I'm confused?**  
A: Read `AGENTS/EUREKA_COMPENDIUM.md`, then `INDEX.md`.

**Q: How do I invoke an agent?**  
A: `@a-architect`, `@a-engineer`, `@a-auditor`, `@a-validator`

---

## ✅ Checklist

- [ ] Read `AGENTS/EUREKA_COMPENDIUM.md`
- [ ] Read `KERNEL/FLOORS/K000_LAW.md`
- [ ] Know your agent role (ΔΩΨ)
- [ ] Understand the 13 Floors
- [ ] Know the Metabolic Loop stages
- [ ] Bookmark `INDEX.md`

---

**Welcome to arifOS. You are now ready to operate within the Constitution.**

*DITEMPA BUKAN DIBERI — Forged, Not Given*
