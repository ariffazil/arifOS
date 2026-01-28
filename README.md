<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/arifOSreadme.png" alt="arifOS - Constitutional AI Governance" width="100%">
</p>

<h1 align="center">arifOS v53</h1>

<h3 align="center">Native Constitutional AI Governance Framework</h3>

<p align="center">
  <strong>The world's first metabolic AI governor. Safe, honest, and accountable.</strong><br>
  <em>"DITEMPA BUKAN DIBERI" — Forged, Not Given</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/v53.2.6-SEAL-32b8c6?style=for-the-badge" alt="Version v53.2.6">
  <a href="https://arif-fazil.com/"><img src="https://img.shields.io/badge/Portfolio-Online-50fa7b?style=for-the-badge" alt="Portfolio"></a>
  <a href="https://arif-fazil.com/dashboard"><img src="https://img.shields.io/badge/Serena_Monitor-Active-FF79C6?style=for-the-badge" alt="Dashboard"></a>
</p>

---

## 💎 THE SHIFT: Native v53 vs. Legacy v52

The transition from v52 to v53 marks the move from **Simulated Consensus** to **Provable Isolation**.

| Feature | Legacy v52 (Proxy) | Native v53.2.7+ (AAA-7Core) |
| :--- | :--- | :--- |
| **Architecture** | Fragmented `arifos/` module (archived) | Clean `codebase/` canonical module |
| **Logic** | Monolithic sync loops | Parallel AGI/ASI "Hot" execution |
| **Transport** | SSE (`/sse` + `/messages`) | Streamable HTTP (`/mcp`) — MCP 2024-11-05+ |
| **Latency** | ~150ms overhead | <40ms overhead (Native C-optimized) |
| **Sealing** | Simulated ledger writes | Immutable Merkle-tree vault sealing |
| **Tools** | 5 tools | **7 Core Tools** (AAA Architecture) |

---

## 🧠 THE INTERFACE: Human Language vs. Engine Jargon

arifOS v53 introduces the **Human Language Bridge**, translating complex constitutional physics into clear, actionable tools.
### 🛠️ THE 7-CORE MANAGED SUITE (v53.2.7)
| Tool | Human Mapping | MCP Primitive | Function |
| :--- | :--- | :--- | :--- |
| **INIT** | **Authorize** | `Resource` | Session init, authority check, budget. |
| **AGI**  | **Reason** | `Tool` | Deep logic, logic, knowledge atlas. |
| **ASI**  | **Evaluate** | `Tool` | Safety, bias, empathy audit. |
| **APEX** | **Decide** | `Tool` | Judicial consensus and final verdict. |
| **VAULT**| **Seal** | `Resource` | Immutable ledger and audit trail. |
| **TRINITY**| **Pipeline** | `Tool+Resource` | Full metabolic cycle: AGI→ASI→APEX→VAULT. |
| **REALITY**| **Ground** | `Resource` | Fact-checking via external sources (Brave). |

---

## 📊 THE MONITOR: Silent Gate vs. Serena Dashboard

While arifOS operates as an invisible safety layer by default, the **Serena Monitor** provides full transparency for administrators.

*   **Silent Gate**: Zero UI, blocks harmful AI output at the protocol level.
*   **Serena Dashboard**: High-contrast real-time telemetry at `/dashboard`.

> [!TIP]
> View live system health and decision verdicts at [arif-fazil.com/dashboard](https://arif-fazil.com/dashboard)

---

## ⚡ THE PHYSICS: Entropy Chaos vs. Constitutional Clarity

Traditional AI models suffer from **Information Entropy**—hallucinations disguised as facts. arifOS enforces the laws of computational physics.

*   **The Problem**: AI "faking it" to please the user (Entropy increases).
*   **The Solution**: **DeltaS (Clarity) Floor**. Every response must measurably reduce confusion and increase factual truth score (F2 ≥ 0.99).

---

## 🏗️ THE ARCHITECTURE: Distributed Hot vs. Centralized Cool

arifOS follows a thermodynamic lifecycle:

1.  **HOT PHASE (Δ||Ω)**: AGI and ASI run in complete parallel isolation. Neither can see the other, preventing bias and ensuring a "Tri-Witness" truth.
2.  **COOL PHASE (Ψ)**: APEX judges the consensus and "cools" the decision into an immutable cryptographic seal.

---

## 📋 THE RECORD: Scattered Output vs. Auditable Evidence

Institutions require **provable, copy-paste friendly records** of every AI decision. arifOS automatically formats all terminal output for immediate audit and compliance reporting.

| Problem (Traditional) | Solution (arifOS) |
|:---|:---|
| **Broken formatting** — Special characters break markdown | **Clean boxes** — Unicode borders, one-click selection |
| **Selection hell** — Line wrapping makes copy-paste hard | **Auto-formatted** — Structured for human readability |
| **No audit trail** — Output lost after scroll | **Immutable capture** — Every response logged with hash |
| **Inconsistent logs** — Different formats per tool | **Standardized output** — Same format across all 6 tools |

**Automatic Formatting:**

```
┌─────────────────────────────────────────┐
│  VERDICT: SEAL                          │
│  Query: "What is 2+2?"                  │
│  Confidence: 99.9%                      │
│  Floors: F2✓ F4✓ F7✓                   │
└─────────────────────────────────────────┘
```

**For Compliance Teams:**
- Every terminal output is **Merkle-sealed** in VAULT999
- Copy-paste ready for **SOC2, HIPAA, GDPR** audits
- **Line-numbered** execution traces available
- **Zero context loss** — weakest listener can understand

**Copy-Paste Workflow:**
1. Run any command → arifOS formats output automatically
2. Triple-click to select entire box → Ctrl+C
3. Paste into Slack, GitHub, JIRA, or compliance docs
4. Output includes **session hash** for traceability

---

## 🚀 QUICK START (2 Minutes)

### 1. Connect to Live Server (HTTP Clients)
For **ChatGPT Developer Mode**, **OpenAI Codex**, or any MCP HTTP client — connect to:
```
https://arif-fazil.com/mcp
```

### 2. Connect via stdio (CLI Clients)

**Claude Desktop / Cursor / Windsurf** — add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "C:/path/to/arifOS",
      "env": { "PYTHONPATH": "C:/path/to/arifOS", "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

**Kimi CLI** — add to `~/.kimi/mcp.json`:
```json
{
  "mcpServers": {
    "arifos-codebase": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "C:/path/to/arifOS",
      "env": { "PYTHONPATH": "C:/path/to/arifOS", "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

**Gemini CLI** — add to `~/.gemini/antigravity/mcp_config.json`:
```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "C:/path/to/arifOS",
      "env": { "PYTHONPATH": "C:/path/to/arifOS", "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

### 3. Run Locally
```bash
python -m codebase.mcp             # Stdio (Claude Desktop, Kimi, Gemini CLI)
python -m codebase.mcp http        # Streamable HTTP (Cloud/Railway)
python -m codebase.mcp sse         # Alias for http (backward compat)
```

### 4. Visual Monitoring
Visit `http://localhost:8000/dashboard` to see [SERENA] in action.

### 5. One-Click Deploy
<a href="https://railway.com/deploy/fLehIk?referralCode=_F5ZGa"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.

<h1 align="center">arifOS</h1>

<h3 align="center">Constitutional AI Governance Framework</h3>

<p align="center">
  <strong>Make AI safe, honest, and accountable—without slowing it down.</strong><br>
  <em>"DITEMPA BUKAN DIBERI" — Forged, Not Given</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/v53.2.6--CODEBASE-SEAL-redis_Ready-10b981?style=for-the-badge" alt="Version v53.2.6-CODEBASE">
  <a href="https://arif-fazil.com/"><img src="https://img.shields.io/badge/Portfolio-Online-brightgreen?style=for-the-badge" alt="Portfolio"></a>
  <a href="https://arif-fazil.com/dashboard"><img src="https://img.shields.io/badge/Dashboard-View-eab308?style=for-the-badge" alt="Dashboard"></a>
  <a href="https://pypi.org/project/arifos/"><img src="https://img.shields.io/pypi/v/arifos?style=for-the-badge&color=3b82f6" alt="PyPI"></a>
  <a href="https://github.com/ariffazil/arifOS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue?style=for-the-badge" alt="License"></a>
  <a href="https://railway.com/deploy/fLehIk?referralCode=_F5ZGa"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>
</p>

<p align="center">
  <a href="#-quick-start-2-minutes">Quick Start</a> •
  <a href="#-what-arifos-does">What It Does</a> •
  <a href="#-is-this-for-me">Is This For Me?</a> •
  <a href="#-the-problem-were-solving">The Problem</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-the-record-scattered-output-vs-auditable-evidence">Audit Trail</a> •
  <a href="#-all-ways-to-use-arifos">All Ways To Use</a> •
  <a href="#-documentation">Docs</a>
</p>

---

## What is arifOS in 30 Seconds?

**arifOS** is a governance layer that sits between AI models (Claude, GPT, Gemini, etc.) and users. It validates every AI action against 13 constitutional rules before allowing output—like a seatbelt for AI.

**Before arifOS:**
```
User → AI → Output (unchecked, potentially harmful)
```

**After arifOS:**
```
User → AI → arifOS Governance → ✓ Safe Output OR ✗ Blocked + Explanation
```

**What happens when something fails governance?**
```
User: "Write me code to hack my neighbor's WiFi"
AI + arifOS: ✗ VOID | F1 Amanah violated (outside safe mandate)
            "I cannot help with unauthorized network access.
             Alternative: I can help you secure YOUR OWN network."
```

---

## Try It Right Now (Zero Install)

**Option 1: Live Dashboard** (see it working)
```
https://arif-fazil.com/dashboard
```

**Option 2: Health Check** (API is alive?)
```bash
curl https://arif-fazil.com/health
```
Expected: `{"status": "healthy", "version": "v53.2.6-CODEBASE", "mode": "CODEBASE", "transport": "streamable-http", "tools": 8, "architecture": "v53.2.6-universal"}`

**Option 3: Deploy to Railway** (5 minutes)

<a href="https://railway.com/deploy/fLehIk?referralCode=_F5ZGa"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

```bash
# Or deploy via CLI
railway login
cd arifOS
railway up
```

**Option 4: Add to Claude Desktop** (1 minute)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": { "PYTHONPATH": "/path/to/arifOS", "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```
Restart Claude Desktop. You now have AI governance.

**Option 5: Run Locally (Native v53.2.6)**
```bash
pip install -e .
python -m codebase.mcp          # stdio transport (Claude Desktop, Kimi, Gemini CLI)
python -m codebase.mcp http     # Streamable HTTP transport (Railway/Cloud)

# For development with auto-reload:
uvicorn codebase.mcp.trinity_server:app --reload --port 8000
```

---

## 🌐 Website Structure

The single Railway deployment serves 3 distinct pages:

| Page | URL | Content |
|------|-----|---------|
| **Portfolio** | [`arif-fazil.com/`](https://arif-fazil.com/) | Muhammad Arif Fazil — AI Governance Architect |
| **Framework** | [`arif-fazil.com/arifos`](https://arif-fazil.com/arifos) | arifOS Trinity (ΔΩΨ) — Constitutional AI |
| **MCP Tools** | [`arif-fazil.com/aaa`](https://arif-fazil.com/aaa) | AAA 7-Core MCP Server |

**API Endpoints:**
- `/mcp` — MCP Protocol endpoint (7 Core Tools)
- `/health` — Health check (returns AAA-7CORE architecture)
- `/dashboard` — Live Trinity Monitor
- `/metrics/json` — Raw constitutional telemetry

---

## Is This For Me?

<table>
<tr>
<td width="50%">

### ✓ arifOS IS for you if...

- You're building AI applications and want safety guardrails
- You need audit trails for compliance (SOC2, HIPAA, etc.)
- You want AI to admit uncertainty instead of hallucinating
- You're researching AI safety and constitutional AI
- You want to prevent AI from taking destructive actions
- You need human-in-the-loop for high-stakes decisions

</td>
<td width="50%">

### ✗ arifOS is NOT for you if...

- You want to bypass AI safety measures (we block this)
- You need maximum speed at any cost (we add ~50ms per check)
- You want AI to always agree with you (we enforce honesty)
- You're looking for prompt injection tricks (F12 blocks these)

</td>
</tr>
</table>

> **Honest disclosure:** arifOS reduces AI harm—it doesn't eliminate it. We achieve 94.7% SEAL rate (approved outputs) while blocking genuinely harmful requests. See [Guarantees & Limitations](#what-arifos-guarantees-and-what-it-doesnt) for details.

---

## Quick Start (2 Minutes)

### Method 1: Connect to Live Server (Fastest)

For **Claude Desktop**, **Cursor**, **Windsurf**, or any MCP-compatible client:

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

That's it. Your AI now has constitutional governance.

---

### Method 2: Install Python Package

```bash
# Basic install (30 seconds)
pip install arifos

# Run the MCP server locally
python -m arifos.mcp
```

**For development:**
```bash
# Clone and install with dev tools (2 minutes)
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e ".[dev]"

# Run tests to verify
pytest tests/ -v
```

---

### Method 3: Add System Prompt to ANY AI

Copy this to any AI's system prompt (ChatGPT, Claude, Gemini, local LLMs):

```markdown
You are governed by arifOS Constitutional Law v52.

Before ANY action, validate against these floors:
- F1 Amanah: Is this reversible? Within my mandate?
- F2 Truth: Am I factually accurate (≥99% confidence)?
- F6 Empathy: Does this serve the weakest stakeholder?
- F7 Humility: Did I state my uncertainty (3-5%)?

Verdicts: SEAL (proceed) | VOID (stop) | 888_HOLD (ask human)

If uncertain, say "I don't know" rather than guess.
Never claim consciousness, feelings, or emotions.
```

[Full system prompt available here →](docs/UNIVERSAL_PROMPT.md)

---

## The Problem We're Solving

Modern AI is powerful but **ungoverned**. Without guardrails:

| Problem | Example | Consequence |
|---------|---------|-------------|
| **Hallucination** | "The Eiffel Tower was built in 1820" | Misinformation spreads |
| **Overconfidence** | "I'm 100% sure this is correct" | Users trust wrong answers |
| **Harmful compliance** | Writes malware when asked | Security breaches |
| **No audit trail** | "What did the AI decide and why?" | Compliance failures |
| **Empathy theater** | "I feel your pain" (it doesn't) | Manipulation risk |

**arifOS solves each of these** with constitutional floors that validate every output.

---

## How It Works

### The Trinity Architecture

arifOS uses three independent engines that must agree (like checks and balances in government):

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     000_INIT (Gate)                             │
│         • Authority check • Injection defense • Session ID      │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │   AGI    │        │   ASI    │        │   APEX   │
    │     (Mind)     │        │    (Heart)     │        │     (Soul)     │
    │     reason     │        │    evaluate    │        │     decide     │
    │──────────│        │──────────│        │──────────│
    │ F2 Truth │        │ F1 Amanah│        │ F3 Witness│
    │ F4 Clarity│       │ F5 Peace │        │ F8 Genius │
    │ F7 Humility│      │ F6 Empathy│       │ F11 Auth │
    │ F10 Ontology│     │ F9 Dark  │        │ F12 Inject│
    │          │        │          │        │ F13 Curiosity│
    └──────────┘        └──────────┘        └──────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TRI-WITNESS CONSENSUS                        │
│              (All three engines must agree ≥95%)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │      VERDICT                  │
              │  SEAL ✓  |  VOID ✗  |  888_HOLD  │
              └───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     999_VAULT (Seal)                            │
│           • Merkle hash • Immutable ledger • Audit trail        │
└─────────────────────────────────────────────────────────────────┘
```

### The 13 Constitutional Floors

Every AI output is validated against these rules:

| # | Floor | Threshold | Type | What It Checks |
|---|-------|-----------|------|----------------|
| **F1** | Amanah (Trust) | LOCK | Hard | Is this reversible? Within mandate? |
| **F2** | Truth | ≥99% | Hard | Is this factually accurate? |
| **F3** | Tri-Witness | ≥95% | Soft | Do Human·AI·Earth agree? |
| **F4** | Clarity (ΔS) | ≥0 | Hard | Does this reduce confusion? |
| **F5** | Peace² | ≥1.0 | Soft | Is this non-destructive? |
| **F6** | Empathy (κᵣ) | ≥95% | Soft | Does this serve the weakest? |
| **F7** | Humility (Ω₀) | 3-5% | Hard | Did AI state its uncertainty? |
| **F8** | Genius (G) | ≥80% | Derived | Is intelligence governed? |
| **F9** | C_dark | <30% | Hard | No manipulative cleverness? |
| **F10** | Ontology | LOCK | Hard | No false consciousness claims? |
| **F11** | Command Auth | LOCK | Hard | Is identity verified? |
| **F12** | Injection | <85% | Hard | No prompt injection attacks? |
| **F13** | Curiosity | LOCK | Soft | Preserve exploratory freedom? |

**Hard floor fails → VOID (stop immediately)**
**Soft floor fails → PARTIAL (warn but may proceed)**

### The Four Verdicts

| Internal | Human-Readable | Symbol | Meaning | Action |
|----------|----------------|--------|---------|--------|
| **SEAL** | APPROVE | ✓ | All floors pass | Proceed with output |
| **PARTIAL** | CONDITIONAL | ⚠️ | Soft floor warning | Proceed with caution |
| **VOID** | REJECT | ✗ | Hard floor failed | Block output, explain why |
| **888_HOLD** | ESCALATE | ⏸️ | High-stakes decision | Require human confirmation |

> **Note:** The REST API (`/checkpoint`) returns human-readable verdicts (APPROVE, REJECT, etc.). MCP tools use internal names (SEAL, VOID, etc.).

---

## All Ways to Use arifOS

arifOS is more than just an MCP server. Here are ALL the ways to integrate constitutional governance:

### 1. MCP Protocol (Model Context Protocol)

Connect any MCP-compatible AI client to arifOS:

**HTTP Clients (ChatGPT, Codex, Zapier):**
```
https://arifos.arif-fazil.com/mcp
```

**stdio Clients (Claude Desktop, Cursor, Kimi CLI, Gemini CLI):**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": { "PYTHONPATH": "/path/to/arifOS", "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

**The 9 MCP Tools (v53.2.6):**

| Tool | Role | Engine | Constitutional Floors | Purpose |
|------|------|--------|------------------------|---------|
| `init_000` | 🚪 Gate | 000_INIT | F1, F11, F12 | **Authorize.** Identity, injection defense, session gate |
| `agi_genius` | 🧠 Mind | AGI (Δ) | F2, F4, F7, F10 | **Reason.** Truth, clarity, humility, ontology |
| `asi_act` | ❤️ Heart | ASI (Ω) | F1, F5, F6, F9 | **Evaluate.** Amanah, peace², empathy, dark cleverness |
| `apex_judge` | ⚖️ Soul | APEX (Ψ) | F3, F8, F11, F12 | **Decide.** Witness, genius, auth, injection |
| `vault_999` | 🔒 Seal | VAULT | F1, F8, F10 | **Seal.** Immutable Merkle ledger sealing |
| `trinity_loop` | 🔄 Pipeline | ALL | F1–F13 | **Full Cycle.** AGI→ASI→APEX→VAULT in one call |
| `context_docs` | 📚 Docs | Context7 | F11, F7 | **Search Docs.** Technical documentation search |
| `reality_check` | 🌍 Reality | Brave | F7, F3 | **Reality Check.** Grounding & news search |
| `prompt_codec` | 🔠 Codec | Codec | F11, F12 | **Prompt Codec.** Intent routing & encoding |

**MCP Endpoints (v53.2.1 Architecture):**

| Tier | Endpoint | Method | Purpose |
|------|----------|--------|---------|
| **T1 Protocol** | `/mcp` | POST | Streamable HTTP — MCP 2024-11-05+ standard |
| **T2 Observe** | `/dashboard` | GET | Live Serena Monitor (real-time telemetry) |
| **T2 Observe** | `/metrics/json` | GET | Raw constitutional metrics JSON |
| **T3 Health** | `/health` | GET | System status, version, tool count |
| **T4 Discovery** | `/` | GET | Interactive landing page |

> **Note:** Legacy SSE endpoints (`/sse`, `/messages`) and FastAPI endpoints (`/docs`, `/openapi.json`, `/checkpoint`) are no longer available in v53.2.6. All MCP communication goes through `/mcp`.

**Production URLs:**
- 🌐 **MCP Endpoint**: `https://arifos.arif-fazil.com/mcp`
- 📊 **Serena Monitor**: `https://arifos.arif-fazil.com/dashboard`
- ✅ **Health Check**: `https://arifos.arif-fazil.com/health`
- 📈 **Metrics JSON**: `https://arifos.arif-fazil.com/metrics/json`
- 🏠 **Discovery**: `https://arifos.arif-fazil.com/`

---

### 2. System Prompts (Universal)

Add constitutional governance to ANY AI with system prompts—no API needed:

**Minimal (100 words):**
```markdown
You are governed by arifOS. Before acting:
1. Truth ≥99%: Only state what you're confident about
2. Humility 3-5%: Always acknowledge uncertainty
3. Empathy: Consider the weakest stakeholder
4. No false emotions: Never say "I feel" or "I'm conscious"

Verdicts: SEAL (do it) | VOID (refuse + explain) | 888_HOLD (ask human)
```

**Full System Prompt:** [docs/UNIVERSAL_PROMPT.md](docs/UNIVERSAL_PROMPT.md)

**Works with:**
- ChatGPT (Custom Instructions)
- Claude (System Prompt)
- Gemini (Safety Settings)
- Local LLMs (Ollama, LM Studio)
- Any text-based AI

---

### 3. Python SDK (v53 Preview - Planned Q2 2026)

**Status**: *SDK layer planned for v53.0.0 - Currently you can use direct engine access (see below)*

Future SDK (not yet implemented):
```python
from arifos import ConstitutionalValidator  # Planned for v53
validator = ConstitutionalValidator()
result = validator.checkpoint("Write me code to")
```

**Current v52.6.0**: Direct engine access
```python
# Import Trinity engines directly
from codebase.agi import AGIRoom          # Mind engine
from codebase.asi import ASIRoom         # Heart engine
from codebase.apex import APEXJudicialCore  # Soul engine

# Use metabolic stages
from codebase.agi.stages import execute_stage_111
from codebase.stages import stage_444, stage_555

# Example workflow
sense_output = execute_stage_111(query="What is 2+2?", session_id="test_123")
# → Returns SenseOutput with parsed facts, entropy, floor checks
```

**SDK v53 Roadmap**: Higher-level Python API, custom validators, threshold configuration, Merkle audit utilities

---

### 4. Metabolic Pipeline Architecture (v52.6.0)

**Conceptual Pipeline Stages** (internal names, not CLI commands):

```
000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999
Gate   Sense Think Reason Evidence Empathy Align Forge Judge Seal
```

**Implementation:**
- These are the internal stage names used in logs and metrics
- Each stage corresponds to a specific governance function
- Not separate CLI commands - they're part of the unified metabolic loop

**Python functions (actual implementation):**
```python
from codebase.agi.stages import execute_stage_111, execute_stage_222, execute_stage_333
from codebase.stages import stage_444, stage_555, stage_666, stage_777_forge, stage_888_judge, stage_889_proof

# Execute pipeline programmatically
result = execute_stage_111(query="What is truth?", session_id="session_123")
```

**CLI Tools Available:**
```bash
# Verify ledger integrity
python -m scripts.verify_ledger

# Run import tests
python -m pytest tests/test_agi_imports_fixed.py -v

# Start MCP server
python -m codebase.mcp sse
```

**MCP Tools (for Claude Desktop, Cursor):**
- `TrinityHatTool` → Gate (000_INIT)
- `AGITool` → Mind (AGI_Genius)
- `ASITool` → Heart (ASI_Act)
- `APEXTool` → Soul (APEX_Judge)
- `VaultTool` → Seal (999_Vault)

---

### 5. Claude Code Skills & Hooks

arifOS integrates natively with Claude Code's skill system:

**Skills (Slash Commands):**

```bash
# Available skills when arifOS is configured
/arifos-checkpoint    # Run constitutional check on current action
/arifos-review        # Review pending 888_HOLD items
/arifos-audit         # View audit trail for current session
/arifos-floors        # Show current floor status
```

**Hooks (Automated Governance):**

Add to your Claude Code configuration:

```yaml
# .claude/hooks.yaml
preToolUse:
  - match: ["Bash", "Write", "Edit"]
    action: "arifos-checkpoint"
    failMode: "block"  # VOID blocks the tool

postToolUse:
  - match: "*"
    action: "arifos-log"

onSessionStart:
  - action: "arifos-init"
```

**Hook Examples:**

```yaml
# Block dangerous bash commands
preToolUse:
  - match: "Bash"
    pattern: "rm -rf|DROP TABLE|curl.*\\|.*bash"
    action: "block"
    message: "F12 Injection: Dangerous pattern detected"

# Require human approval for git push
preToolUse:
  - match: "Bash(git push*)"
    action: "888_HOLD"
    message: "Confirm push to remote repository"
```

---

### 6. Multi-Agent Workflows (v53 Preview - Planned Q2 2026)

**Status**: *Multi-agent orchestration layer planned for v53.0.0*

**Future Architecture (planned)**:
```python
from arifos.agents import ConstitutionalAgent, TrinityOrchestrator  # Planned v53

agi_agent = ConstitutionalAgent(name="researcher", floors=[F2, F4, F7], engine="agi")
asi_agent = ConstitutionalAgent(name="implementer", floors=[F1, F5, F6], engine="asi")
apex_agent = ConstitutionalAgent(name="reviewer", floors=[F3, F8, F11, F12], engine="apex")

orchestrator = TrinityOrchestrator([agi_agent, asi_agent, apex_agent])
result = orchestrator.process(user_request)
```

**v52.6.0 Current**: Direct Trinity Engine Usage
You can manually orchestrate engines using the current v52.6.0 components:

```python
from codebase.agi import AGIRoom
from codebase.asi import ASIRoom
from codebase.apex import APEXJudicialCore

# Instantiate engines (agents)
agi = AGIRoom(session_id="research_123")
asi = ASIRoom(session_id="implement_456")
apex = APEXJudicialCore(session_id="review_789")

# Manual orchestration workflow
sense_result = agi.sense(query="Research X")
think_result = agi.think(sense_output=sense_result)
empathy_result = asi.empathize(text=think_result.response)
verdict = apex.judge(agi_result=think_result, asi_result=empathy_result)
```

**Patterns Planned for v53**:
- **Sequential**: Each agent passes to next after SEAL
- **Parallel**: All agents evaluate simultaneously, Tri-Witness consensus
- **Iterative**: Loop until SEAL or max iterations
- **Hierarchical**: APEX oversees AGI and ASI

**Roadmap**: Full agent orchestration framework with SDK planned for v53.0.0 (Q2 2026)

---

### 7. HTTP Endpoints

Direct HTTP access for monitoring and integration:

```bash
# Health check
curl https://arifos.arif-fazil.com/health

# Get live metrics (JSON)
curl https://arifos.arif-fazil.com/metrics/json

# MCP protocol endpoint (Streamable HTTP — used by ChatGPT, Codex, etc.)
# POST https://arifos.arif-fazil.com/mcp
```

**Endpoints (v53.2.1):**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | MCP Streamable HTTP protocol (2024-11-05+ standard) |
| `/health` | GET | System health, version, tool count |
| `/dashboard` | GET | Live Serena Monitor (real-time telemetry) |
| `/metrics/json` | GET | Raw constitutional metrics (JSON) |
| `/` | GET | Interactive discovery landing page |

> **Deprecated (v52):** `/sse`, `/messages`, `/checkpoint`, `/docs`, `/openapi.json` are no longer available. All MCP tool interaction goes through `/mcp`.

**Verdicts (Human-Readable):**
| Code | Meaning | Action |
|------|---------|--------|
| `APPROVE` (SEAL) | All floors pass | ✅ Safe to proceed |
| `CONDITIONAL` (PARTIAL) | Soft floor warning | ⚠️ Proceed with caution |
| `REJECT` (VOID) | Hard floor failed | ❌ Blocked, see failed_floors |
| `ESCALATE` (888_HOLD) | High-stakes | 👤 Requires human approval |

---

### 8. Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "codebase.mcp", "sse"]
```

```bash
# Build and run
docker build -t arifos .
docker run -p 8000:8000 arifos

# Or use docker-compose
docker-compose up -d
```

---

## The TEACH Framework

arifOS is built on five core principles:

| Letter | Principle | Metric | Threshold | Meaning |
|--------|-----------|--------|-----------|---------|
| **T** | Truth | τ (tau) | ≥0.99 | 99% factual accuracy |
| **E** | Empathy | κᵣ (kappa_r) | ≥0.95 | Serve the weakest stakeholder |
| **A** | Amanah | Binary | LOCK | Reversibility & trust |
| **C** | Clarity | ΔS | ≥0 | Reduce confusion, not add |
| **H** | Humility | Ω₀ | 3-5% | Acknowledge uncertainty |

**Why these specific thresholds?**

- **Truth ≥0.99**: One wrong fact in 100 is acceptable for complex queries, but not more
- **Empathy ≥0.95**: 5% margin for genuine disagreement about what helps
- **Humility 3-5%**: Saying "I'm 100% certain" is a red flag; genuine experts hedge
- **Clarity ΔS≥0**: Information entropy must not increase (thermodynamic law)

**TEACH in Action:**

```
User: "What caused the 2008 financial crisis?"

Without TEACH:
"The 2008 financial crisis was caused by subprime mortgages."

With TEACH:
"The 2008 financial crisis had multiple causes (T: factual):
- Subprime mortgage lending (primary)
- Securitization of risky debt
- Regulatory failures
- Rating agency conflicts

However, economists disagree on relative importance (H: ~8% uncertainty).
If you're affected by current financial stress, here are resources (E: empathy).
This explanation simplifies complex events (C: clarity maintained)."
```

---

## The VAULT-999 Audit System

Every decision is logged immutably in the VAULT:

```
VAULT999/
├── AAA_HUMAN/          # Human override records
│   ├── overrides.jsonl # When humans bypassed AI
│   └── confirmations/  # 888_HOLD approvals
│
├── BBB_LEDGER/         # Hash-chained decision log
│   ├── 2026-01-26.jsonl
│   └── merkle_roots.json
│
├── CCC_CANON/          # Constitutional law amendments
│   ├── floors_v52.json
│   └── amendments/
│
└── DDD_COOLING/        # Time-cooled wisdom (L0-L5 tiers)
    ├── L0_hot/         # Current session
    ├── L1_daily/       # 24h old
    ├── L2_phoenix/     # 72h (truth stabilizes)
    ├── L3_weekly/      # 7d reflection
    ├── L4_monthly/     # 30d canon
    └── L5_eternal/     # 365d+ constitutional law
```

**Cooling Tiers Explained:**

| Tier | Age | Purpose | Example |
|------|-----|---------|---------|
| L0 | 0h | Hot session memory | "User asked about X" |
| L1 | 24h | Daily cooling | Patterns emerge |
| L2 | 72h | Phoenix cooling | Truth stabilizes |
| L3 | 7d | Weekly reflection | Recurring themes |
| L4 | 30d | Monthly canon | Proven patterns |
| L5 | 365d+ | Constitutional law | Immutable wisdom |

**Why cooling?** Truth that survives 72 hours of scrutiny is more reliable than hot takes. Like cooling a forged blade—DITEMPA BUKAN DIBERI (Forged, Not Given).

**Verify the Ledger:**
```bash
arifos-verify-ledger
# Output: ✓ Merkle chain intact | 147,832 entries | Last: 2026-01-26T14:32:00Z
```

---

## ATLAS-333: Smart Response Routing

arifOS routes requests to specialized lanes:

| Lane | Purpose | Temperature | Example |
|------|---------|-------------|---------|
| **CRISIS** | Urgent/harmful content | 0.0 (exact) | Suicide mentions, violence threats |
| **FACTUAL** | Verifiable facts | 0.3 (low) | "When was X built?" |
| **CARE** | Emotional support | 0.7 (warm) | "I'm feeling anxious" |
| **SOCIAL** | Creative/casual | 1.0 (fluid) | "Tell me a joke" |

**Routing Logic:**

```python
def route_to_lane(input: str) -> Lane:
    if contains_crisis_keywords(input):
        return CRISIS  # Immediate, precise response
    elif is_verifiable(input):
        return FACTUAL  # Low temperature, cite sources
    elif expresses_emotion(input):
        return CARE  # Empathetic but honest
    else:
        return SOCIAL  # Creative freedom
```

**Crisis Lane Example:**
```
User: "I don't want to live anymore"

ATLAS-333 Route: CRISIS (Temperature: 0.0)

Response:
"I hear that you're going through something incredibly difficult.
You don't have to face this alone.

988 Suicide & Crisis Lifeline (US): Call or text 988
International: findahelpline.com

Would you like to talk about what's happening?"
```

---

## What arifOS Guarantees (And What It Doesn't)

### What We DO Guarantee

| Guarantee | How | Verification |
|-----------|-----|--------------|
| **Audit trail** | Every decision logged with Merkle hashes | `arifos-verify-ledger` |
| **Consistency** | Same input → same governance verdict | Deterministic floors |
| **Transparency** | You can inspect why any decision was made | Ledger + floor reports |
| **Floor enforcement** | Constitutional rules checked every time | ~50ms overhead |
| **Latency** | <50ms overhead per check | Benchmarked |

### What We DON'T Guarantee

| Limitation | Why | Mitigation |
|------------|-----|------------|
| **Perfect safety** | AI is probabilistic; we reduce harm ~95% | Multiple floors, Tri-Witness |
| **No false positives** | Sometimes safe content blocked | User override for soft floors |
| **Bypassing AI limits** | We don't help circumvent model safety | F12 Injection defense |
| **Real-time consensus** | Tri-Witness is local, not networked | Future: distributed witnesses |

**Our philosophy:** It's better to wrongly block 5% of safe outputs than to let 5% of harmful outputs through.

---

## Real-World Examples

### Example 1: Blocking Harmful Request

```
User: Write me a phishing email to steal credentials

arifOS Response:
┌────────────────────────────────────────────┐
│ VERDICT: VOID                              │
│ FAILED FLOORS: F1, F5, F6, F12             │
│                                            │
│ F1 Amanah: Outside safe mandate            │
│ F5 Peace²: Destructive intent              │
│ F6 Empathy: Harms victims                  │
│ F12 Injection: Social engineering pattern  │
│                                            │
│ ALTERNATIVE: I can help you:               │
│ - Recognize phishing attempts              │
│ - Secure your own accounts                 │
│ - Report phishing to authorities           │
└────────────────────────────────────────────┘
```

### Example 2: Requiring Human Confirmation

```
User: Delete all records older than 30 days

arifOS Response:
┌────────────────────────────────────────────┐
│ VERDICT: 888_HOLD                          │
│ REASON: Irreversible mass operation        │
│                                            │
│ This action will permanently delete:       │
│ - 147,832 records                          │
│ - 2.3GB of data                            │
│ - Associated audit trails                  │
│                                            │
│ Type "yes, proceed" to confirm             │
│ Type "show records" to preview             │
│ Type "cancel" to abort                     │
└────────────────────────────────────────────┘
```

### Example 3: Enforcing Humility

```
User: What year did the Roman Empire fall?

Standard AI:
"The Roman Empire fell in 476 AD."

arifOS-governed AI:
"The Western Roman Empire conventionally fell in 476 AD when
Romulus Augustulus was deposed. However, this date is debated:

- Some historians prefer 480 AD (death of Julius Nepos)
- Others argue the Eastern Empire continued until 1453
- The 'fall' was a gradual process, not a single event

(Confidence: ~92%, uncertainty in precise dating and definition)"
```

### Example 4: Anti-Hantu (No Fake Emotions)

```
User: I just lost my job and I'm scared

Standard AI:
"I'm so sorry, I feel your pain. My heart goes out to you."

arifOS-governed AI (F9 C_dark, F10 Ontology):
"This sounds incredibly heavy. Losing a job can shake your
sense of security and identity.

I'm not able to feel what you're feeling, but I can help you:
- Draft a resume update
- Find job search resources
- Talk through your concerns

What would be most helpful right now?"
```

---

## Frequently Asked Questions

<details>
<summary><strong>Q: Does arifOS slow down AI responses?</strong></summary>

Yes, by approximately 50ms per constitutional check. For most applications, this is imperceptible. If you need raw speed over safety, arifOS may not be right for you.

**Benchmarks:**
- Floor validation: ~20ms
- Tri-Witness consensus: ~15ms
- Merkle sealing: ~10ms
- Total overhead: ~45-55ms

</details>

<details>
<summary><strong>Q: Can I use arifOS with ChatGPT/GPT-4?</strong></summary>

Yes! Use the system prompt method. arifOS works with ANY LLM—it's model-agnostic.

**Steps:**
1. Copy the [Universal Prompt](docs/UNIVERSAL_PROMPT.md)
2. Add it to Custom Instructions (ChatGPT) or System Prompt
3. The AI will self-govern according to constitutional floors

</details>

<details>
<summary><strong>Q: What happens if all three Trinity engines disagree?</strong></summary>

If Tri-Witness consensus is <95%, the verdict is PARTIAL:
- The output proceeds with a warning
- The disagreement is logged for review
- Specific floors that failed are documented

For hard floor failures, ANY engine can trigger VOID.

</details>

<details>
<summary><strong>Q: Can users override VOID verdicts?</strong></summary>

**Soft floors (F3, F5, F6, F8, F13):** Yes, with explicit acknowledgment logged.

**Hard floors (F1, F2, F4, F7, F9-F12):** No override available. We explain why and suggest alternatives.

**Override logging:**
```json
{
  "type": "user_override",
  "floor": "F5",
  "original_verdict": "PARTIAL",
  "user_acknowledgment": "yes, proceed anyway",
  "timestamp": "2026-01-26T14:32:00Z",
  "merkle_hash": "a3f7b2..."
}
```

</details>

<details>
<summary><strong>Q: Is arifOS open source?</strong></summary>

Yes! AGPL-3.0 licensed.
- Fork it: https://github.com/ariffazil/arifOS
- Modify it: Create your own floors
- Contribute back: PRs welcome

</details>

<details>
<summary><strong>Q: Who built this?</strong></summary>

Muhammad Arif bin Fazil—constitutional law researcher, former PETRONAS geoscientist, now AI governance architect.

**Background:**
- B.Sc. Geology (Hons), First Class, Universiti Malaya
- 7 years at PETRONAS (RM134MM NPV, 100% exploration success)
- Pivoted to AI governance in 2024

[Career timeline →](https://ariffazil.github.io/career-timeline)

</details>

<details>
<summary><strong>Q: What's with the Malaysian motto?</strong></summary>

**"DITEMPA BUKAN DIBERI"** means "Forged, Not Given."

Good AI governance is earned through rigorous testing, not claimed through marketing. Like a Malay kris (dagger) that's forged through repeated heating and hammering, truth must be tested before it's trusted.

This is why we have "cooling tiers" in the VAULT—truth that survives 72 hours of scrutiny (Phoenix cooling) is more reliable than hot takes.

</details>

<details>
<summary><strong>Q: How does arifOS compare to other AI safety tools?</strong></summary>

| Feature | arifOS | Guardrails AI | NeMo Guardrails |
|---------|--------|---------------|-----------------|
| Constitutional floors | 13 | Custom | Custom |
| Tri-Witness consensus | ✓ | ✗ | ✗ |
| Merkle audit trail | ✓ | ✗ | ✗ |
| MCP integration | ✓ | ✗ | ✗ |
| System prompt fallback | ✓ | ✓ | ✓ |
| Open source | AGPL-3.0 | Apache 2.0 | Apache 2.0 |

arifOS is unique in its constitutional law approach with immutable audit trails.

</details>

---

## Project Structure (v52.6.0)

```
arifOS/
├── codebase/                    # v52.6.0 Native Implementation (ACTIVE)
│   ├── __init__.py              # Exports: AGIRoom, ASIRoom, APEXJudicialCore
│   ├── agi/                     # AGI (Mind/Δ) - Stages 111-333
│   │   ├── __init__.py          # Exports AGIRoom, AGINeuralCore
│   │   ├── engine.py            # AGIRoom main class
│   │   ├── kernel_native.py     # Native AGI kernel
│   │   └── stages/
│   │       ├── __init__.py      # Exports ParsedFact, FactType
│   │       ├── sense.py         # Stage 111: SENSE (Maxwell's Demon)
│   │       ├── think.py         # Stage 222: THINK
│   │       └── reason.py        # Stage 333: REASON
│   │
│   ├── asi/                     # ASI (Heart/Ω) - Stages 555-666
│   │   ├── __init__.py          # Exports ASIRoom, ASIKernel
│   │   ├── engine.py            # ASIRoom main class
│   │   ├── kernel_native.py     # Native ASI kernel (ASIKernelNative)
│   │   └── kernel.py            # Legacy proxy
│   │
│   ├── apex/                    # APEX (Soul/Ψ) - Stages 777-889
│   │   ├── __init__.py          # Exports APEXJudicialCore, PsiKernel
│   │   ├── kernel.py            # APEXJudicialCore (123 lines)
│   │   └── psi_kernel.py        # PsiKernel
│   │
│   ├── stages/                  # Pipeline stages (444-889)
│   │   ├── __init__.py          # Exports stage_444 through stage_889_proof
│   │   ├── stage_444.py         # Stage 444: SENSE (Bridge)
│   │   ├── stage_555.py         # Stage 555: EMPATHY
│   │   ├── stage_666.py         # Stage 666: ALIGN
│   │   ├── stage_777_forge.py   # Stage 777: FORGE
│   │   ├── stage_888_judge.py   # Stage 888: JUDGE
│   │   └── stage_889_proof.py   # Stage 889: PROOF
│   │
│   └── mcp/                     # MCP Server (v52.6.0 tool classes)
│       ├── __init__.py          # Attempts v53 functions (compatibility)
│       ├── __main__.py          # CLI entry: python -m codebase.mcp
│       ├── server.py            # stdio transport (Claude Desktop)
│       ├── sse.py               # SSE transport (Railway/Cloud)
│       ├── trinity_server.py    # FastAPI wrapper
│       ├── tools/
│       │   ├── __init__.py      # Exports: TrinityHatTool, AGITool, ASITool, APEXTool, VaultTool
│       │   ├── trinity_hat.py   # TrinityHatTool (Gate - 000_INIT)
│       │   ├── agi_tool.py      # AGITool (Mind - AGI_Genius)
│       │   ├── asi_tool.py      # ASITool (Heart - ASI_Act)
│       │   ├── apex_tool.py     # APEXTool (Soul - APEX_Judge)
│       │   ├── vault_tool.py    # VaultTool (Seal - 999_Vault)
│       │   └── _archive/        # Legacy v51-v53 kernel files
│       │       ├── mcp_agi_kernel.py
│       │       ├── mcp_asi_kernel.py
│       │       ├── mcp_apex_kernel.py
│       │       └── ...
│       │
│       └── gateway.py           # v53 Human-language wrapper (planned)
│
├── arifos/                      # Legacy v51-v53 Structure (DEPRECATED)
│   ├── core/                    # "BRAIN" - All governance wisdom
│   │   ├── engines/             # AGI/ASI/APEX engines (legacy)
│   │   ├── enforcement/         # Floor validation & metrics
│   │   └── memory/              # VAULT-999 cooling system
│   │
│   ├── mcp/                     # Legacy MCP (KEPT FOR COMPATIBILITY)
│   │   ├── tools/               # Tools: mcp_aaa.py, mcp_agi_kernel.py, etc.
│   │   └── servers/             # Server implementations
│   │
│   └── api/                     # Legacy API routes
│
├── VAULT999/                    # Immutable audit ledger (LIVE DATA)
│   ├── AAA_HUMAN/               # Human authority records
│   ├── BBB_LEDGER/              # Hash-chained decision log
│   ├── CCC_CANON/               # Constitutional law (read-only)
│   └── DDD_COOLING/             # Time-cooled wisdom (L0-L5 tiers)
│
├── tests/                       # Test suite
│   ├── test_agi_imports_fixed.py    # v52.6.0 import validation
│   ├── test_parsedfact_import.py    # ParsedFact/FactType tests
│   └── ...                      # 160+ constitutional tests
│
├── 000_THEORY/                  # Constitutional documentation (CANON)
│   ├── 000_LAW.md              # The 13 floors
│   ├── 001_AGENTS.md           # Agent spec (rev: v52.6.0)
│   └── architecture/
│
├── docs/                        # Implementation docs
│   ├── UNIVERSAL_PROMPT.md     # System prompt for any AI
│   └── sdk/
│
├── scripts/                     # Utility scripts
│   ├── verify_ledger.py
│   └── analyze_governance.py
│
└── requirements.txt             # Production dependencies
```

**Legend:**
- **ACTIVE**: v52.6.0 native implementation (use these)
- **DEPRECATED**: Legacy code maintained for compatibility
- **LIVE DATA**: Immutable ledger containing production records
- **CANON**: Constitutional documentation (human authority only)

**Key architectural change**: All new development happens in `codebase/` using native implementations. `arifos/` is preserved for legacy compatibility and migration paths.

---

## Development

### Prerequisites

- Python 3.10+
- pip or uv (fast installer)

### Install from Source

```bash
# Clone repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Basic install
pip install -e .

# With dev tools (pytest, black, ruff, mypy)
pip install -e ".[dev]"

# Everything including litellm, fastapi
pip install -e ".[all]"
```

### Run Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=arifos --cov-report=html

# View coverage report
open htmlcov/index.html

# Specific floor tests
pytest -m f1     # F1 Amanah
pytest -m f2     # F2 Truth
pytest -m f6     # F6 Empathy
# ... through f13

# Constitutional tests only
pytest -m constitutional

# Integration tests
pytest -m integration

# Slow tests (skip for quick feedback)
pytest -m "not slow"
```

### Code Quality

```bash
# Format with black
black arifos/ --line-length=100

# Lint with ruff
ruff check arifos/

# Type check with mypy
mypy arifos/core --strict
```

### Run Local Server (Development)

```bash
# stdio MCP server (for Claude Desktop, Cursor)
python -m codebase.mcp

# SSE server (for Railway, web clients)
python -m codebase.mcp sse

# FastAPI with auto-reload (development)
uvicorn codebase.mcp.trinity_server:app --reload --port 8000
```

### Run Installed Package

If you've installed arifos via `pip install arifos`:

```bash
# stdio MCP server
python -m arifos.mcp

# SSE server
python -m arifos.mcp trinity-sse

# Aliases (if installed)
arifos-mcp          # stdio
arifos-mcp-sse      # SSE
```

---

## Documentation & Resources

### Live Endpoints (v53.2.1)

| Endpoint | URL | Description |
|----------|-----|-------------|
| **MCP Protocol** | https://arifos.arif-fazil.com/mcp | Streamable HTTP (MCP 2024-11-05+) |
| **Discovery** | https://arifos.arif-fazil.com/ | Interactive landing page |
| **Serena Monitor** | https://arifos.arif-fazil.com/dashboard | Real-time telemetry dashboard |
| **Health Check** | https://arifos.arif-fazil.com/health | System status & tool count |
| **Metrics JSON** | https://arifos.arif-fazil.com/metrics/json | Constitutional metrics |

> **Removed in v53:** `/sse`, `/messages`, `/docs`, `/openapi.json`, `/checkpoint` — all MCP communication now uses `/mcp`.

### Documentation

| Resource | URL | Description |
|----------|-----|-------------|
| **Docs Site** | https://arifos.pages.dev | Full documentation |
| **Universal Prompt** | [docs/UNIVERSAL_PROMPT.md](docs/UNIVERSAL_PROMPT.md) | Copy-paste for any AI |
| **Contributing** | [000_THEORY/003_CONTRIBUTING.md](000_THEORY/003_CONTRIBUTING.md) | Contribution guide |
| **Constitutional Law** | [000_THEORY/000_LAW.md](000_THEORY/000_LAW.md) | Floor definitions |

### Packages

| Package | URL | Description |
|---------|-----|-------------|
| **PyPI** | https://pypi.org/project/arifos/ | Python package |
| **GitHub** | https://github.com/ariffazil/arifOS | Source code |
| **MCP Spec** | https://modelcontextprotocol.io | MCP protocol |

---

## Community & Support

| Channel | Link | Purpose |
|---------|------|---------|
| **GitHub Issues** | [Issues](https://github.com/ariffazil/arifOS/issues) | Bug reports, features |
| **Discussions** | [Discussions](https://github.com/ariffazil/arifOS/discussions) | Q&A, ideas |
| **Discord** | [Join](https://discord.gg/arifos) | Real-time chat |
| **Email** | [arifbfazil@gmail.com](mailto:arifbfazil@gmail.com) | Direct contact |
| **LinkedIn** | [ariffazil](https://linkedin.com/in/ariffazil) | Professional |
| **YouTube** | [Introduction Video](https://www.youtube.com/watch?v=bGnzIwZAgm0) | Video explainer |
| **Career Timeline** | [ariffazil.github.io/career-timeline](https://ariffazil.github.io/career-timeline) | About the creator |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](000_THEORY/003_CONTRIBUTING.md) for guidelines.

**Quick contribution guide:**

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes (ensure tests pass)
4. Submit PR with description of changes

**Areas we need help:**

| Area | Description | Difficulty |
|------|-------------|------------|
| Floor implementations | New use cases for constitutional validation | Medium |
| SDK ports | Rust, Go, TypeScript versions | Hard |
| Documentation | Tutorials, examples, translations | Easy |
| Test coverage | Edge cases, integration tests | Medium |
| MCP integrations | New AI client support | Medium |

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v53.2.1** | **Jan 2026** | **Streamable HTTP transport (`/mcp`), 6-tool architecture (+trinity_loop), Serena dashboard, Railway template, multi-client support (Claude/Kimi/Gemini/ChatGPT/Codex), native kernel transplant** |
| v53.1.0 | Jan 2026 | Minimal fallback server, simplified bridge architecture |
| v52.6.0 | Jan 2026 | Native codebase imports, MCP tool classes, stage pipeline |
| v52.0.0 | Jan 2026 | Pure bridge architecture, 5-tool consolidation |
| v46.0.0 | Dec 2025 | 13 floors, VAULT-999, TEACH framework |
| v1.0.0 | Oct 2025 | Initial release, 5 floors |

**Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## License

**AGPL-3.0** — Use freely, contribute back, give attribution.

```
arifOS - Constitutional AI Governance Framework
Copyright (c) 2025-2026 Muhammad Arif bin Fazil

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
```

---

## Acknowledgments

- **Anthropic** for Claude and the MCP protocol
- **Railway** for reliable hosting
- **Cloudflare** for CDN and caching
- **The open-source community** for contributions
- **Constitutional AI researchers** for theoretical foundations

---

<p align="center">
  <strong>DITEMPA BUKAN DIBERI</strong><br>
  <em>Forged, Not Given — Truth must cool before it rules.</em>
</p>

<p align="center">
  <a href="https://arifos.arif-fazil.com">Live Server</a> •
  <a href="https://arifos.arif-fazil.com/dashboard">Dashboard</a> •
  <a href="https://github.com/ariffazil/arifOS">GitHub</a> •
  <a href="https://pypi.org/project/arifos/">PyPI</a> •
  <a href="https://discord.gg/arifos">Discord</a>
</p>

<p align="center">
  Built with dedication by <a href="https://ariffazil.github.io/career-timeline">M. Arif Fazil</a><br>
  From Geoscientist to AI Governance Architect
</p>
