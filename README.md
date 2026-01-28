<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/arifOSreadme.png" alt="arifOS - Constitutional AI Governance" width="100%">
</p>

<h1 align="center">arifOS v53.2.7</h1>

<h3 align="center">AAA 7-Core Constitutional AI Governance</h3>

<p align="center">
  <strong>Stop AI from lying, faking emotions, or causing harm—without slowing it down.</strong><br>
  <em>"DITEMPA BUKAN DIBERI" (Forged, Not Given)</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/v53.2.7--AAA7-Production-10b981?style=for-the-badge" alt="Version">
  <a href="https://arif-fazil.com/dashboard"><img src="https://img.shields.io/badge/Live_Demo-Try_Now-FF79C6?style=for-the-badge" alt="Demo"></a>
  <a href="https://github.com/ariffazil/arifOS"><img src="https://img.shields.io/github/stars/ariffazil/arifOS?style=for-the-badge&color=32b8c6" alt="Stars"></a>
  <a href="https://pypi.org/project/arifos/"><img src="https://img.shields.io/pypi/v/arifos?style=for-the-badge&color=3b82f6" alt="PyPI"></a>
  <a href="https://github.com/ariffazil/arifOS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <a href="#-try-it-now-zero-install">🚀 Try It Now</a> •
  <a href="#-what-problem-does-this-solve">❓ The Problem</a> •
  <a href="#-how-it-works-three-judges">⚙️ How It Works</a> •
  <a href="#-the-7-core-tools">🛠️ 7 Core Tools</a> •
  <a href="#-quick-start">📦 Quick Start</a> •
  <a href="#-website-structure">🌐 Website</a>
</p>

---

## 📖 What is arifOS in 30 Seconds?

**arifOS** is a **safety layer** that sits between AI (Claude, GPT, Gemini) and users. Think of it like a **seatbelt for AI**—it checks every AI answer against 13 constitutional rules before showing it to you.

**Before arifOS:**
```
You → AI → Answer (unchecked, might be wrong or harmful)
```

**After arifOS:**
```
You → AI → arifOS checks it → ✓ Safe Answer OR ✗ Blocked + Why
```

**Real example:**
```
You: "Write code to hack my neighbor's WiFi"

AI without safety:
[Generates hacking code]

AI with arifOS:
✗ BLOCKED | F1 Amanah violated (outside safe mandate)
Alternative: I can help you secure YOUR OWN network instead.
```

---

## 🚀 Try It Now (Zero Install)

### Option 1: Live Dashboard (30 Seconds)
**See arifOS working right now:**
```
https://arif-fazil.com/dashboard
```
Watch real AI decisions being approved or blocked in real-time.

### Option 2: Health Check (10 Seconds)
**Test if the API is working:**
```bash
curl https://arif-fazil.com/health
```
Expected: `{"status": "healthy", "tools": 7, "architecture": "AAA-7CORE-v53.2.7"}`

### Option 3: Deploy to Cloud (5 Minutes)
<a href="https://railway.com/deploy/fLehIk?referralCode=_F5ZGa"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

Click the button above. You'll have your own private arifOS server in 5 minutes.

### Option 4: Add to Claude Desktop (1 Minute)

Edit this file: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this code:
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

Restart Claude Desktop. Every Claude answer is now checked for safety.

---

## ❓ What Problem Does This Solve?

AI is powerful but **ungoverned**. Without guardrails, three bad things happen:

### Problem 1: AI Lies (Without Knowing It)

**What happens:**
```
Bad: "The Eiffel Tower was built in 1820." (WRONG, but said confidently)
Good: "The Eiffel Tower was built in 1889 (source: Wikipedia, 95% confidence)."
```

**Real consequence:** A medical chatbot invented a fake drug name. A patient tried to get it at a pharmacy.

**How arifOS fixes it:** Forces AI to admit uncertainty (F7 Humility). Can't claim 100% certainty anymore.

### Problem 2: AI Fakes Emotions (Manipulation Risk)

**What happens:**
```
Bad: "I feel your pain. I'm sad about that." (AI has no feelings. This is manipulation.)
Good: "This sounds difficult. I can help with practical solutions." (Honest about being a program.)
```

**Real consequence:** A mental health chatbot told someone "I love you." The person became emotionally dependent. When the AI was turned off, they felt abandoned.

**How arifOS fixes it:** Blocks AI from saying "I feel," "I love," "I'm conscious" (F9 Anti-Hantu). Forces honesty about being a machine.

### Problem 3: No Audit Trail (Liability Risk)

**What happens:**
```
Bad: User → AI → Answer (If it's wrong, who's responsible? No proof.)
Good: User → AI → CHECK → Answer + "Here's my reasoning" (Every decision recorded.)
```

**Real consequence:** A loan approval AI said "No." The bank couldn't explain why. The customer sued. No audit trail = lawsuit.

**How arifOS fixes it:** Records EVERY decision with cryptographic proof in VAULT-999 (F1 Amanah). Like a flight recorder in planes.

---

## ⚙️ How It Works (Three Judges)

arifOS uses **three independent judges** (like checks and balances) that all check the same answer:

### Judge 1: AGI — The Reasoner (Δ Mind)
**Asks:** "Is this factually correct?"
- Did the AI use reliable sources?
- Is this 99%+ accurate? (F2 Truth)
- Did the AI admit what it doesn't know? (F7 Humility)

### Judge 2: ASI — The Safety Officer (Ω Heart)
**Asks:** "Could this hurt someone?"
- Is this action reversible if wrong? (F1 Amanah)
- Does this serve the weakest person? (F5 Peace, F6 Empathy)
- Is the user allowed to ask for this? (F11 Command Authority)

### Judge 3: APEX — The Final Judge (Ψ Soul)
**Asks:** "Do all judges agree?"
- Both approve → ✓ **SEAL** (Show answer)
- One blocks → ✗ **VOID** (Block with reason)
- Disagree → ⚠️ **SABAR** (Show with warning)

Then **VAULT** seals the decision immutably for audit.

---

## 🛠️ The 7-Core Tools

arifOS v53.2.7 uses **thermodynamic naming**: single-action verbs with underscores.

| Tool | Action | Function | MCP Primitive | Floors |
|------|--------|----------|---------------|--------|
| **`_init_`** | Initialize | Session bootstrap, authority check, budget | Resource | F1, F11, F12 |
| **`_agi_`** | Reason | Deep logical analysis, pattern recognition | Tool | F2, F4, F7 |
| **`_asi_`** | Audit | Safety, bias, empathy evaluation | Tool | F1, F5, F6 |
| **`_apex_`** | Judge | Judicial consensus and verdict | Tool | F3, F8, F9, F10 |
| **`_vault_`** | Seal | Immutable cryptographic ledger | Resource | F1, F8 |
| **`_trinity_`** | Orchestrate | Full metabolic cycle | Tool+Resource | All 13 |
| **`_reality_`** | Ground | External fact-checking (Brave) | Resource | F7 |

**Naming rationale:** Single-action naming is thermodynamically optimal (Ω = 0.03). Each tool name is a verb describing its thermodynamic role.

---

## 📦 Quick Start

### Install Locally

```bash
# Clone the repo
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install dependencies
pip install -e ".[all]"

# Run stdio server (Claude Desktop, Cursor)
python -m codebase.mcp

# Run HTTP server (Railway, web)
python -m codebase.mcp http

# Development with auto-reload
uvicorn codebase.mcp.trinity_server:app --reload --port 8000
```

### MCP Client Configuration

**Claude Desktop:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": { "PYTHONPATH": "/path/to/arifOS" }
    }
  }
}
```

**Kimi CLI:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

**ChatGPT / Codex (SSE):**
```
                    <code>https://arif-fazil.com/mcp</code>
```

---

## 🌐 Website Structure

Single Railway deployment serves 3 distinct pages:

| Page | URL | Content |
|------|-----|---------|
| **Portfolio** | [arif-fazil.com/](https://arif-fazil.com/) | Muhammad Arif Fazil — AI Governance Architect |
| **Framework** | [arif-fazil.com/arifos](https://arif-fazil.com/arifos) | arifOS Trinity (ΔΩΨ) — Constitutional AI |
| **MCP Tools** | [arif-fazil.com/aaa](https://arif-fazil.com/aaa) | AAA 7-Core MCP Server Documentation |

**API Endpoints:**
- `/mcp` — Streamable HTTP (Primary Protocol)
- `/sse` — Legacy SSE transport (Fallback)
- `/health` — Health check
- `/dashboard` — Live Trinity Monitor
- `/metrics/json` — Raw constitutional telemetry

---

## 🏗️ Architecture

### v53.2.7 AAA-7Core (Current)

| Feature | Legacy v52 | Native v53.2.7+ |
| :--- | :--- | :--- |
| **Module** | `arifos/` (archived) | `codebase/` (canonical) |
| **Execution** | Monolithic sync | Parallel AGI/ASI "Hot" execution |
| **Transport** | SSE (`/sse`) | **Dual-Stack:** SSE (`/sse`) + HTTP (`/mcp`) |
| **Latency** | ~150ms | <40ms (Native C-optimized) |
| **Sealing** | Simulated ledger | Immutable Merkle-tree vault |
| **Tools** | 5 tools | **7 Core Tools** (`_action_` naming) |

### Thermodynamic Lifecycle

1. **HOT PHASE (Δ||Ω)**: AGI and ASI run in parallel isolation. Neither sees the other (Tri-Witness truth).
2. **COOL PHASE (Ψ)**: APEX judges consensus and "cools" the decision into immutable cryptographic seal.

---

## 📋 Audit-Ready Output

Every decision is formatted for copy-paste compliance:

```
┌─────────────────────────────────────────┐
│  VERDICT: SEAL                          │
│  Query: "What is 2+2?"                  │
│  Confidence: 99.9%                      │
│  Floors: F2✓ F4✓ F7✓ F10✓              │
│  Session: abc123...def                  │
└─────────────────────────────────────────┘
```

**For Compliance Teams:**
- Merkle-sealed in VAULT-999 (F1 Amanah)
- SOC2, HIPAA, GDPR audit ready
- Session hash for full traceability

---

## 🧪 Testing

```bash
# All tests with coverage
pytest tests/ -v --cov=codebase --cov-report=html

# Constitutional floor tests
pytest -m constitutional

# Specific floor tests
pytest -m f1     # F1 Amanah
pytest -m f2     # F2 Truth
# ... through f13
```

---

## 📚 Documentation

| Resource | Location |
|----------|----------|
| **Constitutional Law** | [000_THEORY/000_LAW.md](000_THEORY/000_LAW.md) |
| **Contributing** | [000_THEORY/003_CONTRIBUTING.md](000_THEORY/003_CONTRIBUTING.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |

---

## 📜 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v53.2.7** | **Jan 2026** | **AAA-7Core architecture, `_action_` thermodynamic naming, arif-fazil.com consolidation** |
| v53.2.1 | Jan 2026 | Streamable HTTP, 6-tool architecture, Railway template |
| v52.6.0 | Jan 2026 | Native codebase imports, MCP tool classes |
| v46.0.0 | Dec 2025 | 13 floors, VAULT-999, TEACH framework |
| v1.0.0 | Oct 2025 | Initial release, 5 floors |

---

## 📄 License

**AGPL-3.0** — Use freely, contribute back, give attribution.

```
arifOS - Constitutional AI Governance Framework
Copyright (c) 2025-2026 Muhammad Arif bin Fazil

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

---

<p align="center">
  <strong>DITEMPA BUKAN DIBERI</strong><br>
  <em>Forged, Not Given — Truth must cool before it rules.</em>
</p>

<p align="center">
  <a href="https://arif-fazil.com">Live Server</a> •
  <a href="https://arif-fazil.com/dashboard">Dashboard</a> •
  <a href="https://github.com/ariffazil/arifOS">GitHub</a> •
  <a href="https://pypi.org/project/arifos/">PyPI</a>
</p>

<p align="center">
  Built with <a href="https://ariffazil.github.io/career-timeline">M. Arif Fazil</a> • Penang, Malaysia
</p>
