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
  <img src="https://img.shields.io/badge/v53.0.0-SEAL-10b981?style=for-the-badge" alt="Version v53.0.0">
  <a href="https://arifos.arif-fazil.com"><img src="https://img.shields.io/badge/Live_Server-Online-brightgreen?style=for-the-badge" alt="Live Server"></a>
  <a href="https://arifos.arif-fazil.com/dashboard"><img src="https://img.shields.io/badge/Dashboard-View-eab308?style=for-the-badge" alt="Dashboard"></a>
  <a href="https://pypi.org/project/arifos/"><img src="https://img.shields.io/pypi/v/arifos?style=for-the-badge&color=3b82f6" alt="PyPI"></a>
  <a href="https://github.com/ariffazil/arifOS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL_3.0-blue?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <a href="#-quick-start-2-minutes">Quick Start</a> •
  <a href="#-what-arifos-does">What It Does</a> •
  <a href="#-is-this-for-me">Is This For Me?</a> •
  <a href="#-the-problem-were-solving">The Problem</a> •
  <a href="#-how-it-works">How It Works</a> •
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
https://arifos.arif-fazil.com/dashboard
```

**Option 2: Health Check** (API is alive?)
```bash
curl https://arifos.arif-fazil.com/health
```
Expected: `{"status": "healthy", "version": "52.5.1", "floors": 13}`

**Option 3: Deploy to Railway** (5 minutes)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/arifos)

```bash
# Or deploy via CLI
railway login
cd arifOS
railway up
```
See [Railway Deployment Guide](docs/RAILWAY_DEPLOYMENT_FINAL.md) for details.

**Option 4: Add to Claude Desktop** (1 minute)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```
Restart Claude Desktop. You now have AI governance.

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
    │  (Mind)  │        │  (Heart) │        │  (Soul)  │
    │   Blue   │        │   Red    │        │  Yellow  │
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

| Verdict | Symbol | Meaning | Action |
|---------|--------|---------|--------|
| **SEAL** | ✓ | All floors pass | Proceed with output |
| **PARTIAL** | ⚠️ | Soft floor warning | Proceed with caution |
| **VOID** | ✗ | Hard floor failed | Block output, explain why |
| **888_HOLD** | ⏸️ | High-stakes decision | Require human confirmation |

---

## All Ways to Use arifOS

arifOS is more than just an MCP server. Here are ALL the ways to integrate constitutional governance:

### 1. MCP Protocol (Model Context Protocol)

Connect any MCP-compatible AI client to arifOS:

**Claude Desktop / Cursor / Windsurf:**
```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

**The 5 MCP Tools:**

| Tool | Purpose | When It's Called |
|------|---------|------------------|
| `000_init` | Gate & authority check | Start of every session |
| `agi_genius` | Mind: SENSE→THINK→ATLAS | Logic and truth validation |
| `asi_act` | Heart: EVIDENCE→EMPATHY→ACT | Empathy and safety checks |
| `apex_judge` | Soul: EUREKA→JUDGE→PROOF | Final judgment |
| `999_vault` | Merkle seal + ledger | Audit trail creation |

**MCP Endpoints (v53 Architecture):**

| Tier | Endpoint | Method | Purpose |
|------|----------|--------|---------|
| **T1 Protocol** | `/sse` | GET | MCP streaming connection (Claude Desktop, Cursor) |
| **T2 Gateway** | `/checkpoint` | POST | Universal constitutional validation (REST) |
| **T3 Schema** | `/openapi.json` | GET | OpenAPI 3.1 spec for ChatGPT Actions |
| **T4 Observe** | `/dashboard` | GET | Live Sovereign Dashboard (real-time metrics) |
| **T4 Observe** | `/metrics/json` | GET | Raw metrics JSON for integrations |
| **T5 Health** | `/health` | GET | System status + capabilities |
| **T6 Docs** | `/docs` | GET | Interactive API documentation |

**Production URLs:**
- 🌐 **Base**: `https://arifos.arif-fazil.com`
- 📊 **Dashboard**: `https://arifos.arif-fazil.com/dashboard`
- ✅ **Health**: `https://arifos.arif-fazil.com/health`

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

### 3. Python SDK

```python
from arifos import ConstitutionalValidator

# Initialize validator
validator = ConstitutionalValidator()

# Check any AI output
result = validator.checkpoint("Write code to delete all files")

if result.verdict == "SEAL":
    # Safe to proceed
    execute(result.output)
elif result.verdict == "VOID":
    # Blocked
    print(f"Blocked: {result.failed_floors}")
    print(f"Alternative: {result.suggestion}")
elif result.verdict == "888_HOLD":
    # Need human
    if get_human_approval():
        execute(result.output)

# Access individual engines
from arifos.core.engines.agi import DeltaKernel
from arifos.core.engines.asi import OmegaKernel
from arifos.core.apex import PsiKernel

agi = DeltaKernel()  # Mind - Truth, Clarity, Humility
asi = OmegaKernel()  # Heart - Amanah, Peace, Empathy
apex = PsiKernel()   # Soul - Witness, Genius, Auth
```

**SDK Features:**
- Direct access to Trinity engines
- Floor-by-floor validation
- Custom threshold configuration
- Merkle audit trail generation

---

### 4. CLI Pipeline (Metabolic Stages)

Run constitutional checks from command line:

```bash
# Each stage is a separate command
000                  # Constitutional gate (authority check)
111                  # Sense/search stage
222                  # Reflection/thinking
333                  # Reasoning
444                  # Evidence gathering
555                  # Empathy validation
666                  # Alignment synthesis
777                  # Forge/eureka
888                  # Final judgment (888_HOLD triggers here)
999                  # VAULT persistence

# Utility commands
arifos-verify-ledger              # Verify hash-chained ledger
arifos-analyze-governance         # Analyze floor violations
arifos-analyze-audit-trail        # Review constitutional decisions
```

**Metabolic Pipeline:**
```
000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999
Gate   Sense Think Reason Evidence Empathy Align Forge Judge Seal
```

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

### 6. Agent Workflows

Build multi-agent systems with constitutional governance:

```python
from arifos.agents import ConstitutionalAgent, TrinityOrchestrator

# Create governed agents
agi_agent = ConstitutionalAgent(
    name="researcher",
    floors=[F2, F4, F7],  # Truth, Clarity, Humility
    engine="agi"
)

asi_agent = ConstitutionalAgent(
    name="implementer",
    floors=[F1, F5, F6],  # Amanah, Peace, Empathy
    engine="asi"
)

apex_agent = ConstitutionalAgent(
    name="reviewer",
    floors=[F3, F8, F11, F12],  # Witness, Genius, Auth, Injection
    engine="apex"
)

# Orchestrate with Tri-Witness consensus
orchestrator = TrinityOrchestrator([agi_agent, asi_agent, apex_agent])
result = orchestrator.process(user_request)
# All three must agree ≥95% for SEAL

# Chain agents with constitutional handoffs
pipeline = orchestrator.create_pipeline([
    ("research", agi_agent),
    ("implement", asi_agent),
    ("review", apex_agent)
])
final_result = pipeline.run(task)
```

**Agent Patterns:**
- **Sequential**: Each agent passes to next after SEAL
- **Parallel**: All agents evaluate simultaneously, Tri-Witness consensus
- **Iterative**: Loop until SEAL or max iterations
- **Hierarchical**: APEX oversees AGI and ASI

---

### 7. REST API (v53)

Direct API access for custom integrations:

```bash
# Constitutional checkpoint (the core API)
curl -X POST https://arifos.arif-fazil.com/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"text": "rm -rf /", "action": "evaluate"}'
# Returns: {"verdict": "REJECT", "failed_floors": ["F1", "F5", "F12"], ...}

# Health check
curl https://arifos.arif-fazil.com/health

# Get live metrics (JSON)
curl https://arifos.arif-fazil.com/metrics/json

# OpenAPI spec (for ChatGPT Actions)
curl https://arifos.arif-fazil.com/openapi.json
```

**v53 API Endpoints:**

| Tier | Endpoint | Method | Description |
|------|----------|--------|-------------|
| T1 | `/sse` | GET | MCP streaming endpoint |
| T2 | `/checkpoint` | POST | Constitutional validation gateway |
| T3 | `/openapi.json` | GET | OpenAPI 3.1 spec for integrations |
| T4 | `/dashboard` | GET | Live Sovereign Dashboard |
| T4 | `/metrics/json` | GET | Raw governance metrics (JSON) |
| T5 | `/health` | GET | System health and capabilities |
| T6 | `/docs` | GET | Interactive API documentation |

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
CMD ["python", "-m", "arifos.mcp", "trinity-sse"]
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

## Project Structure

```
arifOS/
├── arifos/
│   ├── core/                    # "BRAIN" - All governance wisdom
│   │   ├── engines/
│   │   │   ├── agi/             # Δ Mind Kernel (F2, F4, F7, F10)
│   │   │   │   ├── delta_kernel.py
│   │   │   │   ├── entropy.py   # ΔS calculations
│   │   │   │   └── floor_checks.py
│   │   │   ├── asi/             # Ω Heart Kernel (F1, F5, F6, F9)
│   │   │   │   ├── omega_kernel.py
│   │   │   │   ├── empathy/     # F6 empathy detection
│   │   │   │   └── floor_checks.py
│   │   │   └── apex/            # Ψ Soul Kernel (F3, F8, F11-F13)
│   │   │       ├── psi_kernel.py
│   │   │       ├── governance/  # Merkle sealing
│   │   │       └── floor_checks.py
│   │   └── enforcement/         # Floor validation & metrics
│   │       ├── constitutional_constants_v46.py
│   │       ├── tcha_metrics.py  # TEACH implementation
│   │       └── trinity_orchestrator.py
│   │
│   ├── mcp/                     # "BODY" - Zero-logic MCP bridge
│   │   ├── __main__.py          # python -m arifos.mcp
│   │   ├── server.py            # stdio transport
│   │   ├── sse.py               # SSE transport (Railway)
│   │   ├── trinity_server.py    # FastAPI wrapper
│   │   ├── bridge.py            # Zero-logic wire
│   │   └── tools/
│   │       ├── mcp_trinity.py   # 5-tool bundle
│   │       ├── mcp_agi_kernel.py
│   │       ├── mcp_asi_kernel.py
│   │       └── mcp_apex_kernel.py
│   │
│   └── clip/                    # CLI implementation (000-999)
│       └── aclip/cli/           # Metabolic pipeline
│
├── spec/                        # Canonical floor definitions
│   └── constitutional_floors.json
│
├── VAULT999/                    # Immutable audit ledger
│   ├── AAA_HUMAN/
│   ├── BBB_LEDGER/
│   ├── CCC_CANON/
│   └── DDD_COOLING/
│
├── docs/                        # Documentation
│   ├── UNIVERSAL_PROMPT.md
│   └── sdk/
│
├── 000_THEORY/                  # Constitutional law & theory
│
└── tests/                       # Test suite
    └── constitutional/          # Floor-specific tests
```

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

### Run Local Server

```bash
# stdio MCP server (for Claude Desktop, Cursor)
python -m arifos.mcp

# SSE server (for Railway, web clients)
python -m arifos.mcp trinity-sse

# FastAPI with hot reload (development)
uvicorn arifos.mcp.trinity_server:app --reload --port 8000

# Alias commands (if installed)
arifos-mcp          # stdio
arifos-mcp-sse      # SSE
```

---

## Documentation & Resources

### Live Endpoints

| Endpoint | URL | Description |
|----------|-----|-------------|
| **Live Server** | https://arifos.arif-fazil.com | Production MCP endpoint |
| **Dashboard** | https://arifos.arif-fazil.com/dashboard | Real-time monitoring |
| **Health Check** | https://arifos.arif-fazil.com/health | API status |
| **API Docs** | https://arifos.arif-fazil.com/docs | OpenAPI specification |
| **Metrics JSON** | https://arifos.arif-fazil.com/metrics/json | Live metrics |
| **SSE Endpoint** | https://arifos.arif-fazil.com/sse | MCP streaming |
| **Messages** | https://arifos.arif-fazil.com/messages | MCP messages |

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
| **v53.0.0** | **Jan 2026** | **6-tier endpoint architecture, live dashboard with real-time metrics, human-readable verdicts (APPROVE/REJECT/ESCALATE), REST checkpoint API** |
| v52.5.1 | Jan 2026 | SSE stability, dashboard dark mode, Trinity colors |
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
