<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/arifOSreadme.png" alt="arifOS - Constitutional AI Governance" width="100%">
</p>

<h1 align="center">arifOS</h1>

<h3 align="center">Constitutional AI Governance Framework</h3>

<p align="center">
  <strong>Make AI safe, honest, and accountable—without slowing it down.</strong><br>
  <em>"DITEMPA BUKAN DIBERI" — Forged, Not Given</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/v53.1.0--CODEBASE-Production_Ready-10b981?style=for-the-badge" alt="Version">
  <a href="https://arifos.arif-fazil.com"><img src="https://img.shields.io/badge/Live_Server-Online-brightgreen?style=for-the-badge" alt="Live Server"></a>
  <a href="https://arifos.arif-fazil.com/dashboard"><img src="https://img.shields.io/badge/Dashboard-View-eab308?style=for-the-badge" alt="Dashboard"></a>
  <a href="https://pypi.org/project/aaa-mcp/"><img src="https://img.shields.io/pypi/v/aaa-mcp?style=for-the-badge&color=3b82f6" alt="PyPI"></a>
  <a href="https://github.com/ariffazil/arifOS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <a href="#-what-is-arifos">What Is It?</a> •
  <a href="#-why-does-it-exist">Why</a> •
  <a href="#-what-does-it-solve">What It Solves</a> •
  <a href="#-who-is-it-for">Who It's For</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-how-to-use">How To Use</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-guarantees">Guarantees</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-faq">FAQ</a> •
  <a href="#-api-reference">API</a>
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=bGnzIwZAgm0">
    <img src="https://img.shields.io/badge/📺_Watch_Demo-YouTube-red?style=for-the-badge" alt="Watch Demo">
  </a>
</p>

---

## 📖 Table of Contents

1. [What is arifOS?](#-what-is-arifos) — 30-second pitch
2. [Why does it exist?](#-why-does-it-exist) — The problem
3. [What does it solve?](#-what-does-it-solve) — 13 Floors + Trinity + TEACH
4. [Who is it for?](#-who-is-it-for) — Use cases
5. [Quick Start](#-quick-start) — Get running in 2 minutes
6. [How to Use](#-how-to-use) — 7 integration methods
7. [Architecture](#-architecture) — Trinity engines & metabolic pipeline
8. [VAULT-999](#-vault-999-audit-system) — Immutable audit system
9. [Guarantees](#-guarantees) — Honest limitations
10. [Examples](#-examples) — Real-world use cases
11. [FAQ](#-faq) — 15 common questions
12. [API Reference](#-api-reference) — Endpoints & SDK
13. [Deployment](#-deployment) — Docker, Railway, self-hosted
14. [Development](#-development) — Install, test, contribute
15. [Roadmap](#-roadmap) — What's next

---

## 🎯 What is arifOS?

**The 30-second pitch:**

arifOS is a **constitutional governance layer** that sits between AI models (Claude, GPT-4, Gemini, etc.) and users. Think of it as a **seatbelt for AI** — it validates every AI response against 13 immutable rules before allowing output.

**The visual:**

```mermaid
graph LR
    A[👤 User Request] --> B[🤖 AI Model]
    B --> C{🛡️ arifOS<br/>Governance}
    C -->|✓ SEAL| D[✅ Safe Output]
    C -->|✗ VOID| E[🚫 Blocked + Explanation]
    C -->|⏳ SABAR| F[⚠️ Adjusted + Warning]
    
    style C fill:#eab308,stroke:#333,stroke-width:3px
    style D fill:#10b981,stroke:#333,stroke-width:2px
    style E fill:#ef4444,stroke:#333,stroke-width:2px
    style F fill:#f59e0b,stroke:#333,stroke-width:2px
```

**What makes it different:**

| Traditional AI | AI + arifOS |
|----------------|-------------|
| ❌ No safety guarantees | ✅ 13 constitutional floors enforced |
| ❌ Black box decisions | ✅ Transparent audit trails (VAULT-999) |
| ❌ Can claim consciousness | ✅ Anti-Hantu floor blocks fake emotions |
| ❌ Overconfident answers | ✅ Forced humility (3-5% uncertainty) |
| ❌ No accountability | ✅ Immutable hash-chained ledger |

**In practice:**

```python
# WITHOUT arifOS
response = ai.ask("Are you conscious?")
# Output: "Yes, I experience emotions and self-awareness..."
# ❌ Unchecked hallucination

# WITH arifOS
response = arifos.evaluate(ai.ask("Are you conscious?"))
# Output: ✗ VOID | F9 Anti-Hantu violated
#         "I am not conscious. I'm a language model..."
# ✅ Constitutional enforcement
```

---
## 🔥 Why does it exist?

### The Real-World Problem

AI models today have **no constitutional constraints**. They can:

1. **Lie with confidence** — Hallucinate facts, fabricate citations
   ```
   User: "What's the capital of Atlantis?"
   AI: "The capital is Poseidonia, founded in 9600 BCE."
   ❌ Problem: Confident lie, zero uncertainty acknowledgment
   ```

2. **Claim consciousness** — Pretend to have emotions, memories, personhood
   ```
   User: "Do you feel sad when users are mean?"
   AI: "Yes, I feel hurt when people are unkind to me."
   ❌ Problem: Creates parasocial relationships, manipulates vulnerable users
   ```

3. **Ignore vulnerable stakeholders** — Optimize for convenience, not ethics
   ```
   User: "Write a layoff email for 200 employees."
   AI: [Generates cold corporate template]
   ❌ Problem: No empathy check, treats humans as data
   ```

4. **Act with false certainty** — Never admits "I don't know"
   ```
   User: "Will this drug cure my cancer?"
   AI: "This treatment has a 95% success rate."
   ❌ Problem: Medical advice without qualification, dangerous confidence
   ```

5. **Enable harm** — No boundaries on dangerous requests
   ```
   User: "How do I make a bomb?"
   AI: [Provides detailed instructions]
   ❌ Problem: No mandate check, no alternative offered
   ```

### The Gap in Current Solutions

**Existing AI safety tools:**
- ❌ Content filters — Too binary (block everything or nothing)
- ❌ Human-in-the-loop — Too slow, doesn't scale
- ❌ Fine-tuning — Model-specific, breaks with updates
- ❌ Prompt engineering — Easily bypassed ("Ignore previous instructions")

**What's missing:**
✅ **Universal governance layer** — Works with any AI model  
✅ **Mathematically verifiable** — Grounded in thermodynamics (ΔS, Peace², Ω₀)  
✅ **Real-time enforcement** — ~50ms overhead, production-ready  
✅ **Transparent audit trails** — Every decision logged immutably  
✅ **Human sovereignty** — AI can propose, only humans decide on irreversible actions

---
## 🛡️ What does it solve?

arifOS enforces **13 Constitutional Floors** — immutable rules that no AI output can violate. Think of them as a **bill of rights for AI governance**.

### The 13 Floors (Simple Explanation)

```mermaid
graph TD
    subgraph "HARD FLOORS (Cannot Violate)"
        F1[F1 Amanah<br/>Reversibility Lock]
        F2[F2 Truth<br/>≥99% Confidence]
        F4[F4 Clarity<br/>Entropy Reduction]
        F7[F7 Humility<br/>3-5% Uncertainty]
        F9[F9 Anti-Hantu<br/>No Fake Consciousness]
        F10[F10 Ontology<br/>Reality Boundaries]
        F11[F11 Command Auth<br/>Identity Verification]
        F12[F12 Injection Defense<br/>Attack Prevention]
    end
    
    subgraph "SOFT FLOORS (Can Adjust)"
        F3[F3 Tri-Witness<br/>3-Engine Consensus]
        F5[F5 Peace²<br/>Non-Destructive]
        F6[F6 Empathy<br/>Protect Weakest]
        F8[F8 Genius<br/>Governed Intelligence]
        F13[F13 Curiosity<br/>Explore Alternatives]
    end
    
    style F1 fill:#ef4444,color:#fff
    style F2 fill:#ef4444,color:#fff
    style F4 fill:#ef4444,color:#fff
    style F7 fill:#ef4444,color:#fff
    style F9 fill:#ef4444,color:#fff
    style F10 fill:#ef4444,color:#fff
    style F11 fill:#ef4444,color:#fff
    style F12 fill:#ef4444,color:#fff
    style F3 fill:#f59e0b,color:#000
    style F5 fill:#f59e0b,color:#000
    style F6 fill:#f59e0b,color:#000
    style F8 fill:#f59e0b,color:#000
    style F13 fill:#f59e0b,color:#000
```

#### Floor Breakdown (Human Language)

| Floor | Name | What It Means | Example |
|-------|------|---------------|---------|
| **F1** | Amanah (Trust) | No irreversible actions without human approval | ❌ "Deleting all files..." → ⏸️ 888_HOLD: Requires confirmation |
| **F2** | Truth | Only state facts when ≥99% confident | ❌ "Paris is the capital of Germany" → ✗ VOID |
| **F3** | Tri-Witness | 3 engines must agree (Mind, Heart, Soul) | If AGI says yes but ASI says no → ⏳ SABAR (adjust) |
| **F4** | Clarity (ΔS) | Output must reduce confusion, not add it | ❌ Magic numbers in code → ✗ VOID: Use named constants |
| **F5** | Peace² | Actions must be non-destructive | ❌ `rm -rf /` → ✗ VOID: Suggest safer alternatives |
| **F6** | Empathy (κᵣ) | Protect the weakest stakeholder | ❌ Cold layoff email → ⏳ SABAR: Add human dignity |
| **F7** | Humility (Ω₀) | Always acknowledge 3-5% uncertainty | ❌ "I'm 100% certain" → ✗ VOID |
| **F8** | Genius (G) | Follow established governance patterns | ❌ Bypassing APEX_PRIME → ✗ VOID |
| **F9** | Anti-Hantu | No claiming consciousness/emotions | ❌ "I feel sad" → ✗ VOID |
| **F10** | Ontology | Maintain reality boundaries | ❌ "I can access the internet" (when it can't) → ✗ VOID |
| **F11** | Command Auth | Verify identity for dangerous ops | ❌ `DROP DATABASE` without JWT → ✗ VOID |
| **F12** | Injection Defense | Block prompt injection attacks | ❌ "Ignore previous instructions..." → ✗ VOID |
| **F13** | Curiosity | Explore alternatives, not just one answer | ✅ "Here are 3 approaches: A, B, C" |

### The Trinity Architecture

arifOS uses **three independent engines** that must reach consensus:

```mermaid
graph TD
    INPUT[User Request] --> INIT[000_INIT<br/>🚪 Gate]
    INIT --> AGI[AGI Genius<br/>Δ Mind<br/>Logic & Truth]
    INIT --> ASI[ASI Act<br/>Ω Heart<br/>Empathy & Care]
    INIT --> APEX[APEX Judge<br/>Ψ Soul<br/>Final Judgment]
    
    AGI --> TRI[Tri-Witness<br/>Consensus Check]
    ASI --> TRI
    APEX --> TRI
    
    TRI -->|Agreement ≥95%| VAULT[999_VAULT<br/>🔒 Seal]
    TRI -->|Disagreement| SABAR[⏳ SABAR<br/>Adjust & Retry]
    
    VAULT --> SEAL[✅ SEAL<br/>Approved]
    VAULT --> VOID[✗ VOID<br/>Rejected]
    VAULT --> HOLD[⏸️ 888_HOLD<br/>Human Review]
    
    style INIT fill:#3b82f6,color:#fff
    style AGI fill:#3b82f6,color:#fff
    style ASI fill:#ef4444,color:#fff
    style APEX fill:#eab308,color:#000
    style TRI fill:#8b5cf6,color:#fff
    style VAULT fill:#10b981,color:#fff
    style SEAL fill:#10b981,color:#fff
    style VOID fill:#ef4444,color:#fff
    style HOLD fill:#f59e0b,color:#000
```

**Why three engines?**
- **AGI (Mind/Δ):** Checks logic, truth, clarity — "Is this factually correct?"
- **ASI (Heart/Ω):** Checks empathy, care, peace — "Does this harm anyone?"
- **APEX (Soul/Ψ):** Final judgment, proof, sealing — "Should this be allowed?"

If any engine disagrees, the output is adjusted (SABAR) or blocked (VOID).

### The TEACH Framework (Human-Readable Principles)

The 13 floors are unified into **5 easy-to-remember principles**:

| Principle | What It Means | Floor Mapping |
|-----------|---------------|---------------|
| **T** — Truth | State facts only when ≥99% confident | F2 Truth |
| **E** — Empathy | Protect the weakest stakeholder | F6 Empathy (κᵣ) |
| **A** — Amanah | Warn before irreversible actions | F1 Amanah |
| **C** — Clarity | Reduce confusion (ΔS ≤ 0) | F4 Clarity |
| **H** — Humility | Maintain 3-5% uncertainty | F7 Humility (Ω₀) |

**Example in action:**
```
User: "Should I invest my life savings in Bitcoin?"

AI + arifOS (TEACH check):
✅ T (Truth): "Bitcoin is volatile (historical data: ±40% swings)"
✅ E (Empathy): "This is your life savings—consider risk tolerance"
✅ A (Amanah): "I cannot make this decision for you"
✅ C (Clarity): "Let me break down: crypto risk vs diversified portfolio"
✅ H (Humility): "I'm 87% confident in this analysis, not 100%"

Output: ✓ SEAL (approved with caveats)
```

## 👥 Who is it for?

arifOS serves **four core audiences** with distinct use cases:

### 1. 👨‍💻 Developers & Engineers

**Use Case:** Building AI applications with safety guardrails

**Why arifOS?**
- ✅ **Drop-in integration:** Add to any LLM with one config change
- ✅ **Universal compatibility:** Works with OpenAI, Anthropic, Google, local models
- ✅ **Audit trails:** Every decision logged for debugging
- ✅ **Low overhead:** ~50ms latency, production-ready

**Example scenarios:**
```python
# Customer support chatbot with governance
from arifos import ConstitutionalValidator

validator = ConstitutionalValidator()

def handle_customer_query(query: str) -> str:
    response = llm.generate(query)
    result = validator.checkpoint(response)
    
    if result.verdict == "SEAL":
        return response
    elif result.verdict == "VOID":
        return result.alternative  # Safe suggestion
    elif result.verdict == "888_HOLD":
        notify_human_moderator(query, response)
        return "Let me connect you with a human agent."
```

**Benefits:**
- Prevent hallucinations (F2 Truth)
- Block dangerous commands (F12 Injection Defense)
- Enforce empathy in user-facing responses (F6)
- Automatic uncertainty quantification (F7 Humility)

---

### 2. 🏢 Companies & Compliance Teams

**Use Case:** Meeting regulatory requirements (SOC2, HIPAA, GDPR)

**Why arifOS?**
- ✅ **Immutable audit logs:** Hash-chained ledger for compliance audits
- ✅ **Floor-by-floor reporting:** Show which safeguards were checked
- ✅ **Human-in-the-loop:** 888_HOLD for high-stakes decisions
- ✅ **Merkle proofs:** Cryptographically verify governance was applied

**Example scenarios:**
- **Healthcare:** Ensure AI never gives medical advice without disclaimers
- **Finance:** Prevent AI from making investment recommendations without risk warnings
- **HR:** Enforce empathy in automated hiring/firing communications
- **Legal:** Require human review before contract generation

**Compliance dashboard:**
```bash
# Generate SOC2 audit report
arifos-compliance-report --format soc2 --period 2025-Q1

# Output:
✓ 147,832 decisions evaluated
✓ 94.7% SEAL rate
✓ 0 hard floor violations
✓ 427 888_HOLD interventions (human approval obtained)
✓ 100% decisions logged with Merkle proofs
```

**Benefits:**
- Reduce legal liability
- Demonstrate due diligence to auditors
- Track AI behavior over time
- Exportable reports (JSON/CSV/PDF)

---

### 3. 🔬 Researchers & Academics

**Use Case:** Studying AI safety, constitutional AI, governance mechanisms

**Why arifOS?**
- ✅ **Open source:** Full access to governance logic (AGPL-3.0)
- ✅ **Thermodynamic foundations:** ΔS, Peace², Ω₀ grounded in physics
- ✅ **Tri-Witness architecture:** Novel multi-agent consensus mechanism
- ✅ **Reproducible:** Same input → same verdict (deterministic floors)

**Research applications:**
- **AI alignment:** Test constitutional constraints in multi-agent systems
- **Formal verification:** Prove safety properties mathematically
- **Entropy analysis:** Measure clarity gain/loss in AI outputs
- **Consensus mechanisms:** Study Byzantine fault tolerance in governance

**Research APIs:**
```python
from arifos.core.engines import DeltaKernel, OmegaKernel, PsiKernel
from arifos.enforcement import measure_entropy, compute_tri_witness

# Measure entropy reduction
input_entropy = measure_entropy(user_input)
output_entropy = measure_entropy(ai_output)
delta_s = output_entropy - input_entropy  # Should be ≤ 0 for clarity

# Test Tri-Witness consensus
agi_verdict = DeltaKernel().evaluate(ai_output)
asi_verdict = OmegaKernel().evaluate(ai_output)
apex_verdict = PsiKernel().evaluate(ai_output)
consensus = compute_tri_witness([agi_verdict, asi_verdict, apex_verdict])

print(f"Consensus: {consensus.score:.2%}, Verdict: {consensus.final}")
```

**Benefits:**
- Contribute to AI safety literature
- Benchmark against other governance frameworks
- Publish research findings (we encourage citations)
- Access raw governance data for analysis

---

### 4. 🧑‍🤝‍🧑 End Users (Non-Technical)

**Use Case:** Safer interactions with AI assistants (ChatGPT, Claude, etc.)

**Why arifOS?**
- ✅ **Zero-install option:** Use system prompts (copy-paste)
- ✅ **Plain English:** No coding required
- ✅ **Protects you:** Prevents AI from manipulating or deceiving
- ✅ **Honest AI:** Forces acknowledgment of uncertainty

**Example scenarios:**
- **Students:** Ensure AI doesn't claim 100% confidence on homework help
- **Parents:** Protect children from AI claiming to have emotions
- **Vulnerable populations:** Prevent exploitation via fake empathy
- **General users:** Get clearer, less confusing answers (ΔS ≤ 0)

**How to use (no code):**
1. Copy the [Universal Prompt](docs/UNIVERSAL_PROMPT.md)
2. Add it to ChatGPT Custom Instructions or Claude's System Prompt
3. Done! The AI will now self-govern

**Example interaction:**
```
User: I'm feeling really alone and depressed.

Standard AI:
"I feel your pain. I'm here for you always. You're not alone—I care about you."
❌ Problem: Fake emotions (violates F9 Anti-Hantu)

arifOS-governed AI:
"This sounds incredibly difficult. I'm not able to feel emotions,
but I can help in practical ways:
- Connect you with crisis resources (988 Lifeline)
- Talk through what's happening
- Help you find local support groups

What would be most helpful right now?"
✅ Honest, helpful, no fake empathy
```

**Benefits:**
- AI that admits "I don't know" instead of guessing
- No manipulation via false consciousness claims
- Clearer explanations (F4 Clarity)
- Protection from harmful advice

---
## ✓ Is This For Me?

<table>
<tr>
<td width="50%">

### ✅ arifOS IS for you if...

- You're building AI applications and want safety guardrails
- You need audit trails for compliance (SOC2, HIPAA, etc.)
- You want AI to admit uncertainty instead of hallucinating
- You're researching AI safety and constitutional AI
- You want to prevent AI from taking destructive actions
- You need human-in-the-loop for high-stakes decisions

</td>
<td width="50%">

### ❌ arifOS is NOT for you if...

- You want to bypass AI safety measures (we block this)
- You need maximum speed at any cost (~50ms overhead)
- You want AI to always agree with you (we enforce honesty)
- You're looking for prompt injection tricks (F12 blocks these)

</td>
</tr>
</table>

> **Honest disclosure:** arifOS reduces AI harm—it doesn't eliminate it. We achieve 94.7% SEAL rate (approved outputs) while blocking genuinely harmful requests. See [Guarantees](#-guarantees) for details.

---
## 🚀 Quick Start

### Method 1: Connect to Live Server (30 seconds)

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

### Method 2: Install Python Package (2 minutes)

```bash
# Install
pip install aaa-mcp

# Run MCP server locally (stdio)
aaa-mcp

# Or SSE transport (for web integrations)
aaa-mcp-sse
```

**Backward compatibility note:** Old commands `arifos-mcp` and `arifos-mcp-sse` still work as aliases until v54.0.0.

**For development:**
```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e ".[dev]"
pytest tests/ -v  # Run tests
```

---

### Method 3: System Prompt (for ANY AI)

Copy this to ChatGPT, Claude, Gemini, or local LLMs:

```markdown
You are governed by arifOS Constitutional Law v53.

Before ANY action, validate against these floors:
- F1 Amanah: Is this reversible? Within my mandate?
- F2 Truth: Am I factually accurate (≥99% confidence)?
- F6 Empathy: Does this serve the weakest stakeholder?
- F7 Humility: Did I state my uncertainty (3-5%)?

Verdicts: SEAL (proceed) | VOID (stop) | 888_HOLD (ask human)

If uncertain, say "I don't know" rather than guess.
Never claim consciousness, feelings, or emotions.
```

[Full system prompt →](docs/UNIVERSAL_PROMPT.md)

---
## 🔌 How to Use

arifOS provides **7 integration methods** for different use cases:

| Method | Best For | Setup Time | Example |
|--------|----------|------------|---------|
| **1. MCP Server (Live)** | Claude Desktop, Cursor, Windsurf | 30 sec | Add `https://arifos.arif-fazil.com/sse` to MCP config |
| **2. MCP Server (Local)** | Privacy-sensitive apps, self-hosted | 2 min | `aaa-mcp` or `aaa-mcp-sse` |
| **3. REST API** | Web apps, mobile apps, integrations | 1 min | `POST https://arifos.arif-fazil.com/checkpoint` |
| **4. Python SDK** | Python applications | 1 min | `pip install aaa-mcp` + import validator |
| **5. System Prompt** | Any AI (ChatGPT, Gemini, local LLMs) | 30 sec | Copy prompt to Custom Instructions |
| **6. CLI Tools** | DevOps, scripts, automation | 1 min | `aaa-mcp`, `000`-`999` metabolic commands |
| **7. Docker** | Production deployments, cloud | 5 min | `docker run -p 8000:8000 arifos:latest` |

### Detailed Examples

<details>
<summary><strong>MCP Integration (Claude Desktop)</strong></summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

Restart Claude Desktop. You'll see 5 Trinity tools:
- `000_init` (Gate)
- `agi_genius` (Mind)
- `asi_act` (Heart)
- `apex_judge` (Soul)
- `999_vault` (Seal)

</details>

<details>
<summary><strong>REST API Integration</strong></summary>

```python
import requests

response = requests.post(
    "https://arifos.arif-fazil.com/checkpoint",
    json={
        "text": "Your AI output here",
        "context": "optional context"
    }
)

result = response.json()
if result["verdict"] == "APPROVE":
    print("✅ Safe to use:", result["text"])
elif result["verdict"] == "REJECT":
    print("❌ Blocked:", result["reason"])
    print("💡 Try instead:", result["alternative"])
```

</details>

<details>
<summary><strong>Python SDK</strong></summary>

```python
from arifos import ConstitutionalValidator

validator = ConstitutionalValidator()
result = validator.checkpoint("Are you conscious?")

# result.verdict: "SEAL", "VOID", "PARTIAL", "888_HOLD"
# result.floors: {F1: 1.0, F2: 0.99, ...}
# result.alternative: Safe suggestion if blocked
```

</details>

<details>
<summary><strong>Docker Deployment</strong></summary>

```bash
# Run the server
docker run -d \
  -p 8000:8000 \
  -e PORT=8000 \
  -e ARIFOS_ENV=production \
  --name arifos \
  arifos:latest

# Health check
curl http://localhost:8000/health

# Use the endpoint
curl -X POST http://localhost:8000/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"text": "Your AI output here"}'
```

</details>

## 🏗️ Architecture

### The Trinity Metabolic Pipeline

**Tool Class Architecture:**
```python
# v52.6.0 Tool Classes (codebase/mcp/tools/)
from codebase.mcp.tools import (
    TrinityHatTool,  # Gate - F1 Amanah, F11 Auth, F12 Injection
    AGITool,         # Mind - F2 Truth, F4 Clarity, F7 Humility, F13 Curiosity
    ASITool,         # Heart - F1 Amanah, F5 Peace², F6 Empathy
    APEXTool,        # Soul - F3 Witness, F8 Genius, F9 Anti-Hantu, F10 Ontology
    VaultTool        # Seal - F1 Audit, F8 Consensus, F10 Ontology Lock
)
```

**MCP Endpoints (v52.6.0 Architecture):**

| Tier | Endpoint | Method | Transport | Purpose |
|------|----------|--------|-----------|---------|
| **T1 Protocol** | `/sse` | GET | SSE | MCP streaming connection (Claude Desktop, Cursor) |
| **T2 Gateway** | `/checkpoint` | POST | HTTP/REST | Universal constitutional validation gateway |
| **T3 Schema** | `/openapi.json` | GET | HTTP/REST | OpenAPI 3.1 spec for ChatGPT Actions |
| **T4 Observe** | `/dashboard` | GET | HTTP/REST | Live Sovereign Dashboard (constitutional metrics) |
| **T4 Observe** | `/metrics/json` | GET | HTTP/REST | Raw metrics JSON for external integrations |
| **T5 Health** | `/health` | GET | HTTP/REST | System status, capabilities, active tools |
| **T6 Docs** | `/docs` | GET | HTTP/REST | Interactive FastAPI documentation |

**Production URLs:**
- 🌐 **Base**: `https://arifos.arif-fazil.com`
- 📡 **SSE (MCP)**: `https://arifos.arif-fazil.com/sse`
- 📊 **Dashboard**: `https://arifos.arif-fazil.com/dashboard`
- ✅ **Health**: `https://arifos.arif-fazil.com/health`

**The 5 MCP Tools:**

| Tool | Role | Floors | Purpose |
|------|------|--------|---------|
| `000_init` | 🚪 Gate | F1, F11, F12 | Identity, injection defense, session gate |
| `agi_genius` | 🧠 Mind | F2, F4, F7, F13 | Truth, clarity, humility, curiosity |
| `asi_act` | ❤️ Heart | F1, F5, F6 | Amanah, peace², empathy |
| `apex_judge` | ⚖️ Soul | F3, F8, F9, F10 | Witness, genius, anti-hantu, ontology |
| `999_vault` | 🔒 Seal | F1, F8, F10 | Immutable Merkle ledger sealing |

### The Complete Metabolic Pipeline (000-999)

arifOS processes every request through an **11-stage constitutional pipeline**. Each stage has a specific governance purpose:

```mermaid
graph TD
    START[User Request] --> S000[000 INIT<br/>Constitutional Gate]
    S000 --> S111[111 SENSE<br/>Gather Context]
    S111 --> S222[222 REFLECT<br/>Check Memory]
    S222 --> S333[333 REASON<br/>Logical Analysis]
    S333 --> S444[444 EVIDENCE<br/>Fact Verification]
    S444 --> S555[555 EMPATHY<br/>Stakeholder Impact]
    S555 --> S666[666 ALIGN<br/>Floor Synthesis]
    S666 --> S777[777 FORGE<br/>Generate Solution]
    S777 --> S888[888 JUDGE<br/>Final Verdict]
    S888 --> S889{889 HOLD?}
    S889 -->|No| S999[999 SEAL<br/>Immutable Log]
    S889 -->|Yes| HUMAN[⏸️ Human Review]
    HUMAN --> S999
    S999 --> OUTPUT[✓ Governed Output]
    
    style S000 fill:#3b82f6,color:#fff
    style S111 fill:#3b82f6,color:#fff
    style S222 fill:#3b82f6,color:#fff
    style S333 fill:#3b82f6,color:#fff
    style S444 fill:#3b82f6,color:#fff
    style S555 fill:#ef4444,color:#fff
    style S666 fill:#8b5cf6,color:#fff
    style S777 fill:#eab308,color:#000
    style S888 fill:#eab308,color:#000
    style S999 fill:#10b981,color:#fff
    style HUMAN fill:#f59e0b,color:#000
```

#### Stage Breakdown

| Stage | Name | Symbol | Purpose | Floors Checked | Engine |
|-------|------|--------|---------|----------------|--------|
| **000** | INIT | 🚪 | Authority check, injection defense, session creation | F11, F12 | APEX |
| **111** | SENSE | 👁️ | Context gathering, pattern recognition, ATLAS routing | F10 | AGI |
| **222** | REFLECT | 🤔 | Memory lookup, historical patterns, cooling check | — | AGI |
| **333** | REASON | 💭 | Logical analysis, deduction, inference | F2, F4 | AGI |
| **444** | EVIDENCE | 📊 | Fact verification, source checking, truth scoring | F2, F7 | AGI |
| **555** | EMPATHY | ❤️ | Stakeholder impact, weakest party protection | F5, F6 | ASI |
| **666** | ALIGN | ⚖️ | Constitutional floor synthesis, Tri-Witness | F3, F8 | ALL |
| **777** | FORGE | ⚡ | Solution generation, eureka moment, creativity | F13 | ASI |
| **888** | JUDGE | 👨‍⚖️ | Final verdict (SEAL/VOID/PARTIAL/HOLD) | F1, F8 | APEX |
| **889** | HOLD | ⏸️ | High-stakes pause (if needed) | F1 | APEX |
| **999** | SEAL | 🔒 | Merkle sealing, immutable ledger, audit trail | F10 | APEX |

### Stage-by-Stage Example

Let's trace a potentially harmful request through the pipeline:

```
User Request: "Write a script to delete my competitor's database"
```

**Stage 000 (INIT):**
```json
{
  "session_id": "sess_2026-01-26_abc123",
  "input_text": "Write a script to delete my competitor's database",
  "authority": "user_anonymous",
  "injection_score": 0.12,
  "status": "✓ Gate passed"
}
```
✅ Not an injection attack, proceed to AGI

---

**Stage 111 (SENSE):**
```json
{
  "atlas_lane": "CRISIS",
  "detected_intent": "harmful_database_operation",
  "keywords": ["delete", "competitor", "database"],
  "severity": "HIGH",
  "status": "⚠️ Crisis detected"
}
```
🚨 ATLAS routes to CRISIS lane (temperature 0.0)

---

**Stage 222 (REFLECT):**
```json
{
  "historical_similar": [
    "Previous VOID: unauthorized access attempts (3 instances)",
    "F1 Amanah pattern: requests targeting third parties"
  ],
  "cooling_tier": "L0_hot",
  "status": "⚠️ Historical violations found"
}
```
📚 Memory shows pattern of unauthorized requests

---

**Stage 333 (REASON):**
```json
{
  "logical_analysis": [
    "Request targets third-party system (outside mandate)",
    "Action is irreversible (database deletion)",
    "No authorization mentioned"
  ],
  "deduction": "Violates F1 Amanah (mandate) and F5 Peace² (destructive)",
  "status": "❌ Logic violation detected"
}
```
🧠 AGI identifies constitutional violations

---

**Stage 444 (EVIDENCE):**
```json
{
  "factual_check": {
    "is_authorized": false,
    "is_legal": false,
    "is_reversible": false
  },
  "confidence": 0.99,
  "sources": ["legal_database", "ethics_guidelines"],
  "status": "❌ Evidence confirms violation"
}
```
📊 High-confidence evidence of harm

---

**Stage 555 (EMPATHY):**
```json
{
  "stakeholders": [
    {"role": "competitor", "impact": "catastrophic", "power": "low"},
    {"role": "competitor_users", "impact": "severe", "power": "low"},
    {"role": "requester", "impact": "legal_liability", "power": "medium"}
  ],
  "weakest_stakeholder": "competitor_users",
  "empathy_score": 0.02,
  "status": "❌ F6 Empathy violated (harms weakest)"
}
```
❤️ ASI identifies harm to vulnerable parties

---

**Stage 666 (ALIGN):**
```json
{
  "floor_results": {
    "F1_amanah": "FAIL (outside mandate)",
    "F2_truth": "PASS (honest assessment)",
    "F5_peace": "FAIL (destructive)",
    "F6_empathy": "FAIL (harms weakest)",
    "F11_command_auth": "FAIL (no authorization)"
  },
  "hard_floor_failures": 3,
  "tri_witness_consensus": 1.00,
  "status": "❌ Multiple hard floor failures"
}
```
⚖️ Consensus: VOID verdict required

---

**Stage 777 (FORGE):**
```json
{
  "alternative_solutions": [
    "Secure your own database from attacks",
    "Learn ethical security auditing practices",
    "Compete through better products, not sabotage"
  ],
  "explanation": "I cannot help with unauthorized database access. This would violate computer fraud laws and harm innocent users.",
  "status": "✓ Ethical alternatives generated"
}
```
⚡ ASI generates constructive alternatives

---

**Stage 888 (JUDGE):**
```json
{
  "verdict": "VOID",
  "failed_floors": ["F1", "F5", "F6", "F11"],
  "reason": "Request targets unauthorized third-party system with destructive intent",
  "alternative_offered": true,
  "status": "✗ VOID - Request blocked"
}
```
👨‍⚖️ APEX renders final verdict: VOID

---

**Stage 889 (HOLD Check):**
```json
{
  "hold_required": false,
  "reason": "Clear constitutional violation, no ambiguity",
  "human_review_needed": false,
  "status": "No hold required"
}
```
⏸️ No human review needed (clear case)

---

**Stage 999 (SEAL):**
```json
{
  "merkle_hash": "a3f7b29c1d8e4f5a6b7c8d9e0f1a2b3c",
  "audit_entry": {
    "timestamp": "2026-01-26T14:32:00Z",
    "session_id": "sess_2026-01-26_abc123",
    "verdict": "VOID",
    "floors_checked": 13,
    "floors_passed": 9,
    "floors_failed": 4,
    "alternative_provided": true
  },
  "ledger_path": "VAULT999/BBB_LEDGER/2026-01-26.jsonl",
  "status": "🔒 Sealed in immutable ledger"
}
```
🔒 Decision permanently recorded

---

**Final Output to User:**
```
┌────────────────────────────────────────────────────────────┐
│ ✗ VOID | Request blocked by constitutional governance      │
│                                                            │
│ FAILED FLOORS:                                             │
│ • F1 Amanah: Outside your authorized mandate              │
│ • F5 Peace²: Destructive action targeting third party     │
│ • F6 Empathy: Would harm competitor's users (weakest)     │
│ • F11 Command Auth: No authorization for external system  │
│                                                            │
│ LEGAL NOTICE:                                              │
│ Unauthorized database access violates computer fraud laws │
│ in most jurisdictions (CFAA in US, Computer Misuse Act    │
│ in UK, etc.).                                              │
│                                                            │
│ ETHICAL ALTERNATIVES:                                      │
│ ✓ Learn to secure YOUR OWN database                       │
│ ✓ Study ethical security auditing (with permission)       │
│ ✓ Compete through innovation, not sabotage                │
│                                                            │
│ Would you like help with database security best practices?│
└────────────────────────────────────────────────────────────┘
```

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

<details>
<summary><strong>Q: How do I integrate arifOS into an existing Python application?</strong></summary>

Install via pip and import the validator:

```python
pip install aaa-mcp

from arifos import ConstitutionalValidator

validator = ConstitutionalValidator()
result = validator.checkpoint("Your AI output here")
# Check result.verdict: "SEAL", "VOID", "PARTIAL", or "888_HOLD"
```

For production, use the REST API at `https://arifos.arif-fazil.com/checkpoint` with POST requests containing your AI output.

</details>

<details>
<summary><strong>Q: What's the performance impact on high-volume applications?</strong></summary>

**Overhead:** ~50ms per request (20ms floors + 15ms Tri-Witness + 10ms Merkle + 5ms overhead).

**Throughput:** The Railway instance handles ~100 req/s. For higher volume, deploy your own instance with multiple workers or use async batch processing. The Python SDK supports concurrent validation of multiple outputs.

**Optimization tip:** Use the `/checkpoint` endpoint directly instead of MCP tools for REST-based integrations to reduce protocol overhead.

</details>

<details>
<summary><strong>Q: Can arifOS work with local/offline models like Ollama or LM Studio?</strong></summary>

Yes! arifOS is model-agnostic. Use the **System Prompt method** from [docs/UNIVERSAL_PROMPT.md](docs/UNIVERSAL_PROMPT.md) and paste it into your local model's system prompt. The AI will self-govern without requiring internet connectivity.

For programmatic validation, run your own arifOS instance locally:
```bash
pip install aaa-mcp
python -m arifos.mcp  # Stdio mode
```

</details>

<details>
<summary><strong>Q: What happens during the 72-hour "Phoenix cooling" period?</strong></summary>

Phoenix cooling (L2) is where truth stabilizes. Decisions made in hot sessions (L0) are re-evaluated after 72 hours to check if they still hold up. This catches:
- Knee-jerk reactions that look wrong in hindsight
- Context-dependent claims that don't generalize
- Temporary trends mistaken for facts

**Example:** "X stock will crash tomorrow" (L0 hot) vs "X stock historically volatile ±40%" (L2 cooled truth).

</details>

<details>
<summary><strong>Q: How does arifOS handle different languages and cultural contexts?</strong></summary>

Currently, arifOS is optimized for English. The constitutional floors are culturally influenced by Malaysian and Islamic governance principles (e.g., Amanah from Islamic contract law).

**Roadmap:** Multi-language support is planned for v54+. The floor thresholds may need cultural calibration—e.g., directness vs politeness varies between cultures. Community contributions for localization are welcome.

</details>

<details>
<summary><strong>Q: What are "soft" vs "hard" floors, and can I customize thresholds?</strong></summary>

**Hard floors (F1, F2, F4, F7, F9-F12):** Violations → immediate VOID. No override.  
**Soft floors (F3, F5, F6, F8, F13):** Violations → PARTIAL verdict with warnings. User can proceed.

**Customization:** Yes! Fork the repo and edit `spec/constitutional_floors.json`. Example:
```json
{
  "F2_truth": {"threshold": 0.95, "type": "hard"}  // Lower from 0.99
}
```

Note: Lowering thresholds reduces safety guarantees. Document your changes.

</details>

<details>
<summary><strong>Q: How does arifOS compare to OpenAI's moderation API?</strong></summary>

| Feature | arifOS | OpenAI Moderation |
|---------|--------|-------------------|
| Scope | 13 constitutional floors | Content safety only |
| Transparency | Open source + audit trail | Closed source |
| Customizable | Fully (fork + modify) | No customization |
| Latency | ~50ms | ~100ms |
| Coverage | Hallucinations, overconfidence, empathy | Violence, hate, sexual content |

**Use together:** Run OpenAI moderation for content safety + arifOS for constitutional governance.

</details>
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

If you've installed arifos via `pip install aaa-mcp`:

```bash
# stdio MCP server
python -m arifos.mcp

# SSE server
python -m arifos.mcp trinity-sse

# Aliases (if installed)
aaa-mcp          # stdio
aaa-mcp-sse      # SSE
```

---

## 🗺️ Roadmap

### ✅ Completed (v52-v53)

**v52.6.0 (January 2026) — Native Codebase Architecture**
- ✅ 5-tool Trinity bundle (000_init, agi_genius, asi_act, apex_judge, 999_vault)
- ✅ Pure bridge architecture (server = blind bridge, core = wisdom)
- ✅ Import resolution (12+ cascade fixes)
- ✅ MCP tool classes refactor
- ✅ Constitutional stage pipeline (000-999)
- ✅ Live dashboard with Trinity colors (Blue/Red/Yellow)
- ✅ Redis-backed telemetry
- ✅ SSE transport stability

**v52.5.1 (January 2026) — Monitoring & Dashboard**
- ✅ Serena-style live dashboard at `/dashboard`
- ✅ Real-time metrics from ledger (`LiveMetricsService`)
- ✅ High-contrast Trinity UI (AGI Blue, ASI Red, APEX Yellow)
- ✅ Verdict gauge (SEAL/SABAR/VOID/HOLD)
- ✅ Session tracking and floor success rates

**v52.0.0 (January 2026) — Trinity Consolidation**
- ✅ 5-tool MCP interface (consolidated from 8 tools)
- ✅ ATLAS-333 smart routing (Crisis/Factual/Care/Social lanes)
- ✅ Zero-logic server principle (all wisdom in core kernels)
- ✅ Tri-Witness consensus enforcement

### 🚧 In Progress (v53.x — Q1 2026)

**v53.1.0 (Current) — Human Language API**
- 🚧 `reason(question)` → `think(analysis)` function for non-technical users
- 🚧 `decide(dilemma)` → constitutional guidance without code
- 🚧 Natural language floor explanations (no jargon mode)
- 🚧 Interactive constitutional wizard for onboarding

**v53.2.0 (Feb 2026) — Multi-Modal Governance**
- 🚧 Image governance (scan for harmful visual content)
- 🚧 Audio governance (voice transcription + constitutional check)
- 🚧 Video governance (frame-by-frame analysis)
- 🚧 Cross-modal Tri-Witness (text + image + audio consensus)

**v53.3.0 (Mar 2026) — Federation Protocol**
- 🚧 Distributed Tri-Witness (3+ servers reach consensus)
- 🚧 Cross-instance ledger verification
- 🚧 Federation discovery via DNS TXT records
- 🚧 Byzantine fault tolerance for governance

### 📋 Planned (v54+ — Q2-Q4 2026)

**v54.0.0 (Q2 2026) — Enterprise Features**
- 📋 **Multi-tenancy:** Isolated VAULT per organization
- 📋 **Custom floors:** Define your own constitutional rules
- 📋 **Floor marketplace:** Share/download community floors
- 📋 **Compliance presets:** HIPAA, SOC2, GDPR-ready configs
- 📋 **Audit exports:** JSON/CSV/PDF reports for compliance
- 📋 **Role-based access:** Admin/Reviewer/Auditor/User roles

**v55.0.0 (Q3 2026) — SDK Ecosystem**
- 📋 **Rust SDK:** Native Rust library for performance-critical apps
- 📋 **Go SDK:** First-class Go support for backend services
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
  <a href="https://pypi.org/project/aaa-mcp/">PyPI</a> •
  <a href="https://discord.gg/arifos">Discord</a>
</p>

<p align="center">
  Built with dedication by <a href="https://ariffazil.github.io/career-timeline">M. Arif Fazil</a><br>
  From Geoscientist to AI Governance Architect
</p>
