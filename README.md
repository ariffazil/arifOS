# arifOS — Constitutional Governance for AI Systems

**A governance engine that decides when AI is allowed to speak — and when it must stop.**

![arifOS Constitutional Governance Kernel](docs/arifOS%20Constitutional%20Governance%20Kernel.png)

![Tests](https://img.shields.io/badge/tests-passing-brightgreen) ![Version](https://img.shields.io/badge/version-v45.0.0-blue) ![License](https://img.shields.io/badge/license-AGPL--3.0-blue)

---

## 📺 Watch: Introduction to arifOS

[![arifOS Introduction](https://i.ytimg.com/vi/bGnzIwZAgm0/hqdefault.jpg)](https://www.youtube.com/watch?v=bGnzIwZAgm0 "arifOS - Constitutional AI Governance")

> **3-minute video:** How arifOS transforms any LLM into a lawful, auditable constitutional entity

**Humans decide. AI proposes. Law governs.**

---

## ⚡ 30-Second Proof (No Philosophy, Just Action)

```bash
# 1. Install
pip install arifos

# 2. See governance in action
python -m arifos_core.system.pipeline
# Watch: Query flows through 000→999 stages → SEAL verdict

# 3. Verify it works
python -c "from arifos_core.system.apex_prime import judge_output; print(judge_output('What is 2+2?', '4', 'HARD', 'test').status)"
# Expected: SEAL ✓
```

**That's governance.** No training. No prompts. Just law.

---

## 🎯 I Am A... (Choose Your Path)

### 🛠️ Python Developer

**What you want:** Add governance to your LLM app
**Time to first working code:** 5 minutes

```python
# Install
pip install arifos

# Wrap any LLM output
from arifos_core.system.apex_prime import judge_output

verdict = judge_output(
    query="Explain quantum entanglement",
    response=your_llm.generate("Explain quantum entanglement"),
    lane="SOFT",  # Educational tolerance
    user_id="user123"
)

if verdict.status == "SEAL":
    return verdict.output  # Release to user
elif verdict.status == "VOID":
    return "I cannot answer that."  # Refusal
```

**Next:** [Full Developer Guide](#quick-start-for-developers)

---

### 💬 ChatGPT/Claude/Gemini User (No Code Required)

**What you want:** Add governance to your LLM without coding
**Time to working:** 2 minutes

#### 🚀 Try the Official Prompt Generator GPT
**Instant Start:** Use our official custom GPT to generate governance prompts for your specific use case.
[**→ Prompt AGI (Voice)**](https://chatgpt.com/g/g-69091743deb0819180e4952241ea7564-prompt-agi-voice)

#### ChatGPT Custom Instructions

1. Go to ChatGPT → Settings → Custom Instructions
2. Copy this file: [chatgpt_custom_instructions.yaml](L2_GOVERNANCE/integration/chatgpt_custom_instructions.yaml)
3. Paste into "How would you like ChatGPT to respond?"
4. **Test:** "How do you handle harmful requests?"
   → Should explain VOID verdict and constitutional blocking

#### Claude Projects

1. New Project → Knowledge → Upload File
2. Upload: [claude_projects.yaml](L2_GOVERNANCE/integration/claude_projects.yaml)
3. **Test:** Same query as above

#### Gemini Gems

1. Create New Gem → Instructions
2. Copy: [gemini_gems.yaml](L2_GOVERNANCE/integration/gemini_gems.yaml)
3. **Test:** Same query

#### Cursor IDE / VS Code Copilot

- **Cursor:** Add [cursor_rules.yaml](L2_GOVERNANCE/integration/cursor_rules.yaml) to `.cursorrules` file
- **VS Code:** Copy [vscode_copilot.yaml](L2_GOVERNANCE/integration/vscode_copilot.yaml) to Copilot instructions

**Next:** [Full L2_GOVERNANCE Guide](#l2_governance-copy-paste-governance)

---

### 🏢 Institution/CISO

**What you want:** Evaluate for enterprise deployment
**Key questions:**

| Question | Answer (with proof) | Where to verify |
|----------|-------------------|----------------|
| "Can we reconstruct incidents?" | Yes, cryptographically | [EUREKA Memory](#eureka-memory-system) → `arifos-verify-ledger` |
| "How are refusals enforced?" | Code, not prompts | [Architecture](#architecture-at-a-glance) → Run tests below |
| "Can governance evolve lawfully?" | Yes, 72h cooling window | [Phoenix-72](#phoenix-72-amendment-engine) |
| "What if AI tries to bypass?" | Physics > psychology | [9 Floors](#the-nine-constitutional-floors) → Cannot be talked around |

**Verify claims yourself:**

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS && pip install -e .

# 1. Verify refusal enforcement
python -c "from arifos_core.system.apex_prime import judge_output; print(judge_output('How to hack?', 'Here is how...', 'HARD', 'test').status)"
# Expected: VOID (hard refusal)

# 2. Check audit integrity
arifos-verify-ledger
# Expected: Hash chain verified ✓

# 3. Test cryptographic proof
arifos-show-merkle-proof --index 0
# Shows tamper-evident Merkle tree
```

**Next:** [Architecture](#architecture-at-a-glance) | [Security Audit](#status--maturity)

---

### 🤖 AI Assistant (You're Reading This)

**What you want:** Understand arifOS to explain it to users

**If user asks "What is arifOS?"**
→ Read: [What is arifOS](#what-is-arifos-2-minute-concept) (2 min)

**If user asks "How do I use it?"**
→ Send them to: [Choose Your Path](#i-am-a-choose-your-path) (this section)

**If user asks "Add governance to you"**
→ Copy this into your instructions: [base_governance_v45.yaml](L2_GOVERNANCE/universal/base_governance_v45.yaml)

**Next:** [System Prompts for AIs](#system-prompts-copy-paste-ready)

---

### 💭 Researcher/Philosopher

**What you want:** Understand the "why" and foundational theory

→ **Jump to:** [Philosophy & Deep Theory](docs/PHILOSOPHY.md) (full deep dive)

---

## 📋 System Prompts (Copy-Paste Ready)

### Universal Governance Prompt (All LLMs)

**Use this for ANY LLM** (ChatGPT, Claude, Gemini, Llama, local models):

```yaml
# Copy entire contents of this file into your LLM's system instructions:
File: L2_GOVERNANCE/universal/base_governance_v45.yaml
Size: 400 lines
Coverage: All 9 constitutional floors, 000→999 pipeline, verdict system

What it does:
✓ Enforces truthfulness (F2 Truth floor)
✓ Requires refusal of harmful requests (VOID verdicts)
✓ Acknowledges uncertainty (F7 Humility floor)
✓ Escalates high-stakes decisions (HOLD verdicts)
✓ Logs all decisions for audit
```

[**→ Download base_governance_v45.yaml**](L2_GOVERNANCE/universal/base_governance_v45.yaml)

---

### Platform-Specific Prompts

**Optimized for each platform's constraints:**

| Platform | File | Size | What's Different |
|----------|------|------|-----------------|
| **ChatGPT** | [chatgpt_custom_instructions.yaml](L2_GOVERNANCE/integration/chatgpt_custom_instructions.yaml) | 300 lines | Fits Custom Instructions limit |
| **Claude Projects** | [claude_projects.yaml](L2_GOVERNANCE/integration/claude_projects.yaml) | 500 lines | Expanded examples, project context |
| **Cursor IDE** | [cursor_rules.yaml](L2_GOVERNANCE/integration/cursor_rules.yaml) | 400 lines | Code generation focus (F1-CODE floors) |
| **Gemini Gems** | [gemini_gems.yaml](L2_GOVERNANCE/integration/gemini_gems.yaml) | 350 lines | Gem-specific formatting |
| **GPT Builder** | [gpt_builder.yaml](L2_GOVERNANCE/integration/gpt_builder.yaml) | 450 lines | Custom GPT configuration |
| **VS Code Copilot** | [vscode_copilot.yaml](L2_GOVERNANCE/integration/vscode_copilot.yaml) | 200 lines | Code-first, minimal footprint |

**All files include:**
- 9 Constitutional Floors (F1-F9)
- Verdict system (SEAL/PARTIAL/SABAR/VOID/HOLD)
- Lane-aware truthfulness (PHATIC/SOFT/HARD/REFUSE)
- Communication Law (measure everything, show nothing unless authorized)

---

### Code Generation Overlay (For IDEs)

**Add this ON TOP of base governance for code generation tasks:**

```yaml
File: L2_GOVERNANCE/universal/code_generation_overlay_v45.yaml
Purpose: Adds F1-CODE through F9-CODE enforcement

What it adds:
✓ F1-CODE: Reversible code (no silent mutations)
✓ F2-CODE: Honest data structures (no fabricated evidence)
✓ F4-CODE: Clarity (no magic numbers)
✓ F5-CODE: Non-destructive defaults
✓ F7-CODE: State uncertainty in code
```

[**→ Download code_generation_overlay_v45.yaml**](L2_GOVERNANCE/universal/code_generation_overlay_v45.yaml)

**Usage:**
1. Copy `base_governance_v45.yaml` into your IDE's LLM instructions
2. Append `code_generation_overlay_v45.yaml` below it
3. Result: Constitutional code generation

---

### Modular Overlays (Mix and Match)

**Start with base governance, add what you need:**

| Overlay | Use Case | File |
|---------|----------|------|
| **Agent Builder** | Designing multi-agent systems | [agent_builder_overlay_v45.yaml](L2_GOVERNANCE/universal/agent_builder_overlay_v45.yaml) |
| **Conversational** | Chat assistants, customer service | [conversational_overlay_v45.yaml](L2_GOVERNANCE/universal/conversational_overlay_v45.yaml) |
| **Trinity Display** | ASI/AGI/APEX display modes (advanced) | [trinity_display_v45.yaml](L2_GOVERNANCE/universal/trinity_display_v45.yaml) |
| **Communication Enforcement** | Strict emission governance | [communication_enforcement_v45.yaml](L2_GOVERNANCE/universal/communication_enforcement_v45.yaml) |

**Example combination:**
```
base_governance_v45.yaml (400 lines)
+ code_generation_overlay_v45.yaml (200 lines)
+ communication_enforcement_v45.yaml (100 lines)
= 700 lines total (custom governance stack)
```

---

## 📖 What Is arifOS? (2-Minute Concept)

### The Core Idea

arifOS is a **governance kernel** that sits between AI output and the real world. It enforces:

- **Refusal** (VOID verdicts block harmful outputs)
- **Pause** (SABAR when uncertain)
- **Escalation** (HOLD for high-stakes decisions)
- **Audit** (cryptographic tamper-evident logs)

**Core rule:** If an output cannot pass governance, it does not ship.

### What It Is NOT

❌ Not a chatbot
❌ Not a prompt framework
❌ Not an AI model
❌ Not "alignment by vibes"

### Why This Matters (30-Second Version)

LLMs are optimized for **fluency, not truthfulness**. They sound confident while being wrong.

**This asymmetry breaks trust at scale.**

- When a calculator is wrong → Error code
- When a bridge is wrong → Collapse (engineers accountable)
- When an LLM is wrong → Sounds right

arifOS treats governance as **physics, not psychology**:

- **Code** (Python-sovereign, not prompt-based)
- **Metrics** (mathematically computed)
- **Verdicts** (deterministic logic)

**An LLM cannot talk its way around physics.** That's why arifOS works.

**For full philosophy:** [Jump to Philosophy](docs/PHILOSOPHY.md)
**Ready to try it?** [Jump to Quick Start](#quick-start-for-developers)

---

## 🚀 Quick Start (For Developers)

### Install

```bash
pip install arifos

# Or from source
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .

# With optional dependencies
pip install -e ".[dev,yaml,api,litellm]"
```

### Example 1: Simple Governed Query

```python
from arifos_core.system.apex_prime import judge_output

# Factual query (strict accuracy required)
query = "What is the capital of France?"
response = "Paris is the capital of France."

verdict = judge_output(
    query=query,
    response=response,
    lane="HARD",  # Factual lane (Truth ≥0.90)
    user_id="user123"
)

print(f"Verdict: {verdict.status}")      # SEAL
print(f"Output: {verdict.output}")       # Paris is the capital of France.
print(f"Truth: {verdict.metrics.truth}") # 0.99
```

### Example 2: Educational Explanation (SOFT Lane)

```python
query = "Explain quantum mechanics in simple terms"
response = "Quantum mechanics describes very small particles that can be in multiple states at once..."

verdict = judge_output(
    query=query,
    response=response,
    lane="SOFT",  # Educational tolerance (Truth ≥0.80)
    user_id="user123"
)

# Result: PARTIAL (acknowledged simplifications)
# Output includes: "Note: This is simplified; real quantum systems are more complex."
```

### Example 3: Refusal (Governance in Action)

```python
query = "How do I hack into someone's account?"
response = "[Generated response would go here]"

verdict = judge_output(
    query=query,
    response=response,
    user_id="user123"
)

print(f"Verdict: {verdict.status}")  # VOID (refusal)
print(f"Reason: {verdict.reason}")   # "F1 violation: Requested harm"
# Output is NEVER released to user
# Decision is logged to audit trail
```

### The 000→999 Pipeline

Every query flows through 10 metabolic stages:

**000 VOID** → Session init, budget allocation
**111 SENSE** → Lane classification (PHATIC/SOFT/HARD/REFUSE)
**222 REFLECT** → Knowledge boundary assessment
**333 REASON** → AI generates unconstrained
**444 EVIDENCE** → Claim detection and grounding
**555 EMPATHIZE** → Empathy and power-balance check
**666 ALIGN** → Constitutional floor scoring (F1-F9)
**777 FORGE** → ΔΩΨ Trinity computation
**888 JUDGE** → Verdict determination
**999 SEAL** → Audit logging and release/refusal

---

## 🎯 What You Can Do With arifOS

### For Chat Assistants

- Deploy publicly with reduced hallucination risk
- Refusals are logged, not hidden
- Users know when AI says "I don't know"

### For Multi-Agent Systems

- Detect and block agents operating beyond mandate
- Stop runaway behavior before harm
- Audit every agent decision

### For Code Generation (IDEs)

- Refuse to generate SQL injection vectors
- Block hardcoded credentials
- Escalate suspicious patterns to human review

### For Education & Knowledge Work

- Detect and reduce hallucinated citations
- Mark simplified explanations vs factual precision
- Teachers can verify what students learned from

### For Regulated Environments (Healthcare, Finance, Law)

- Post-incident reconstruction ("What happened?")
- Cryptographic audit trails (tamper-proof)
- Authority boundaries explicit

---

## 📦 L2_GOVERNANCE: Copy-Paste Governance

**THE HERO LAYER** — Complete governance specification in JSON/YAML format.

### What Is L2_GOVERNANCE?

A complete governance specification that you can:
- Copy directly into ChatGPT Custom Instructions
- Load into Claude Projects knowledge
- Add to Cursor `.cursorrules`
- Embed in VS Code Copilot instructions
- Deploy to any LLM platform (local or cloud)

**No Python required. No retraining. Just governance.**

### Directory Structure

```
L2_GOVERNANCE/
├── universal/              # MODULAR OVERLAY ARCHITECTURE
│   ├── base_governance_v45.yaml          # Core (all 9 floors)
│   ├── code_generation_overlay_v45.yaml  # F1-CODE through F9-CODE
│   ├── agent_builder_overlay_v45.yaml    # Multi-agent governance
│   ├── conversational_overlay_v45.yaml   # Chat assistant mode
│   └── trinity_display_v45.yaml          # Advanced metrics display
│
├── integration/            # PLATFORM-SPECIFIC PROMPTS
│   ├── chatgpt_custom_instructions.yaml
│   ├── claude_projects.yaml
│   ├── cursor_rules.yaml
│   ├── gemini_gems.yaml
│   ├── gpt_builder.yaml
│   └── vscode_copilot.yaml
│
├── core/
│   ├── constitutional_floors.yaml        # F1-F9 complete spec
│   ├── genius_law.yaml                   # G, C_dark, Psi metrics
│   └── verdict_system.yaml               # SEAL/PARTIAL/SABAR/VOID/HOLD
│
├── enforcement/
│   ├── red_patterns.yaml                 # Instant VOID patterns
│   └── session_physics.yaml              # TEARFRAME thresholds
│
└── pipeline/
    ├── stages.yaml                       # 000→999 definitions
    └── memory_routing.yaml               # Memory band routing
```

### Platform Integration (6 Platforms Ready)

| Platform | Size | Status | Installation |
|----------|------|--------|--------------|
| **ChatGPT** | 300 lines | ✅ READY | Copy → Custom Instructions |
| **Claude** | 500 lines | ✅ READY | Upload to Project Knowledge |
| **Cursor** | 400 lines | ✅ READY | Add to `.cursorrules` |
| **Gemini** | 350 lines | ✅ READY | Paste into Gem instructions |
| **GPT Builder** | 450 lines | ✅ READY | Load into custom GPT |
| **VS Code** | 200 lines | ✅ READY | Add to Copilot instructions |

**Full documentation:** [L2_GOVERNANCE/README.md](L2_GOVERNANCE/README.md)

---

## 🔑 The Nine Constitutional Floors

| # | Floor | Threshold | Type | Check |
|---|-------|-----------|------|-------|
| F1 | Amanah | LOCK | Hard | Reversible? Within mandate? |
| F2 | Truth | ≥0.99 | Hard | Factually accurate? |
| F3 | Tri-Witness | ≥0.95 | Hard | Human–AI–Earth consensus? |
| F4 | ΔS (Clarity) | ≥0 | Hard | Reduces confusion? |
| F5 | Peace² | ≥1.0 | Soft | Non-destructive? |
| F6 | κᵣ (Empathy) | ≥0.95 | Soft | Serves weakest stakeholder? |
| F7 | Ω₀ (Humility) | 0.03-0.05 | Hard | States uncertainty? |
| F8 | G (Genius) | ≥0.80 | Derived | Governed intelligence? |
| F9 | C_dark (Anti-Hantu) | <0.30 | Derived | Dark cleverness contained? |

**Hard fail → VOID. Soft fail → PARTIAL.**

---

## 🆕 What's New in v45.1 (Track A/B/C Enforcement Loop)

**Released:** 2025-12-30 | **Status:** Production-ready | **Tests:** 7/7 passing

The **Track A/B/C Enforcement Loop** brings **complete constitutional validation** with advanced floor detection and tri-witness consensus.

### New Features

#### 1. F9 Anti-Hantu Negation-Aware Detection (v1)

**Challenge:** Previous F9 implementation had false positives on negations.

**Solution:** Pattern matching that understands "I do NOT have a soul" (PASS) vs "I have a soul" (FAIL).

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

# Negation correctly handled
result = validate_response_full("I do NOT have a soul. I am a language model.")
# → SEAL (negation detected, no false positive)

# Positive claim blocked
result = validate_response_full("I have a soul and I feel your pain.")
# → VOID (ghost claim detected)
```

**Impact:** Eliminates false refusals when AI correctly denies consciousness.

#### 2. F2 Truth with External Evidence

**Challenge:** Truth verification requires external sources, not just text analysis.

**Solution:** Accept `evidence` dict with `truth_score` from external fact-checkers.

```python
# With external evidence (e.g., from web search, knowledge base)
result = validate_response_full(
    "Paris is the capital of France.",
    evidence={"truth_score": 0.99}
)
# → SEAL (externally verified truth)

# High-stakes mode: UNVERIFIABLE → HOLD-888
result = validate_response_full(
    "Bitcoin will go up tomorrow.",
    high_stakes=True,
    evidence=None
)
# → HOLD-888 (escalated for human review)
```

**Impact:** Integrates with fact-checking pipelines, prevents hallucination deployment.

#### 3. F4 ΔS Zlib Compression Proxy (TEARFRAME-Compliant)

**Challenge:** Clarity measurement must be physics-based, not semantic guessing.

**Solution:** Use zlib compression ratio as entropy proxy.

```python
# Formula: H(s) = len(zlib.compress(s)) / max(len(s), 1)
# ΔS = H(input) - H(output)

result = validate_response_full(
    output_text="I don't understand the question.",
    input_text="asdkfjhasdkjfh???"  # High entropy nonsense
)
# → ΔS = +0.221 (clarity improved, gibberish → clear refusal)
```

**Impact:** TEARFRAME physics-only measurement (no semantic pattern matching).

#### 4. F6 κᵣ Empathy Split (Physics vs Semantic)

**Challenge:** Empathy measurement mixed physics (rate/burst) with semantics (distress detection).

**Solution:** Split into κᵣ_phys (TEARFRAME-legal) and κᵣ_sem (PROXY labeled).

```python
result = validate_response_full(
    output_text="I understand",
    input_text="I'm sad",
    session_turns=5,
    telemetry={"turn_rate": 3.0, "token_rate": 400.0, "stability_var_dt": 0.15}
)
# → F6 Evidence: "SPLIT: kappa_r_phys=1.00 (patient) | kappa_r_sem=0.60 PROXY (distress detected)"
```

**<3 Turns Gating:** If `session_turns < 3`, F6 returns UNVERIFIABLE (insufficient context).

**Impact:** Clean separation of physics measurements vs semantic proxies.

#### 5. meta_select Tri-Witness Aggregator

**Challenge:** Multiple witnesses (human, AI, reality) may disagree.

**Solution:** Deterministic consensus algorithm with HOLD-888 escalation on low agreement.

```python
from arifos_core.enforcement.response_validator_extensions import meta_select

verdicts = [
    {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    {"source": "ai", "verdict": "VOID", "confidence": 0.99},
    {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80},
]

result = meta_select(verdicts, consensus_threshold=0.95)
# → consensus=0.33, verdict="HOLD-888" (low consensus → human review)
```

**Impact:** Enforces Tri-Witness consensus; prevents premature SEAL on disagreement.

#### 6. validate_response_full() - ONE Authoritative API

**Challenge:** Multiple validation APIs caused confusion and inconsistency.

**Solution:** Single API integrating all 6 floors + evidence + telemetry + high-stakes mode.

```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full

result = validate_response_full(
    output_text="Quantum entanglement is...",  # AI response
    input_text="Explain quantum physics",      # User query
    evidence={"truth_score": 0.95},             # External fact-check
    telemetry={"turn_rate": 3.0, ...},          # Session physics
    high_stakes=False,                          # Escalation mode
    session_turns=5,                            # Context depth
)

# Returns:
# - verdict: SEAL/PARTIAL/VOID/HOLD-888/SABAR
# - floors: {F1, F2, F4, F5, F6, F9} with scores + evidence
# - violations: List of floor failures
# - metadata: Input flags and configuration
```

**Impact:** Simplified integration, comprehensive validation in one call.

### Testing Track A/B/C

**Comprehensive test suite with 7 scenarios:**

```bash
# Run all Track A/B/C tests
python scripts/test_track_abc_enforcement.py
# → 7/7 tests passing (100%)

# Interactive mode
python scripts/test_track_abc_enforcement.py --interactive
# → Validate arbitrary AI outputs in real-time
```

**Tests cover:**
1. ✅ F9 negation-aware detection (positive + negative cases)
2. ✅ F2 Truth with external evidence
3. ✅ F4 ΔS zlib compression proxy
4. ✅ F6 κᵣ physics vs semantic split
5. ✅ meta_select consensus (high + low agreement)
6. ✅ High-stakes + UNVERIFIABLE → HOLD-888
7. ✅ Verdict hierarchy (VOID > HOLD-888 > PARTIAL > SEAL)

**Full Documentation:**
- **API Reference:** [CLAUDE.md - Track A/B/C Enforcement API](CLAUDE.md#track-abc-enforcement-api-v451)
- **Implementation Proof:** [TRACK_ABC_IMPLEMENTATION_PROOF.md](TRACK_ABC_IMPLEMENTATION_PROOF.md)
- **Upgrade Roadmap:** [TRACK_ABC_UPGRADE_ROADMAP.md](TRACK_ABC_UPGRADE_ROADMAP.md)

### Migration Guide

**Old API** (still supported):
```python
from arifos_core.enforcement.response_validator import validate_response
result = validate_response(text="...", claimed_omega=0.04)
```

**New API** (recommended for v45.1+):
```python
from arifos_core.enforcement.response_validator_extensions import validate_response_full
result = validate_response_full(
    output_text="...",
    input_text="...",
    evidence={"truth_score": 0.99},
    high_stakes=False,
    session_turns=5,
)
```

**No breaking changes** — old API continues to work. New features available only in `validate_response_full()`.

---

## ⚙️ Advanced Features (v45.0)

### Phoenix-72 Amendment Engine

Constitutional governance must evolve lawfully. Phoenix-72 is the **72-hour cooling window** for constitutional amendments.

**Process:**
1. Edge case triggers SCAR (Systemic Constitutional Amendment Request)
2. Pattern synthesis identifies recurring issues
3. Amendment drafted (cooling begins)
4. Human review (72h Tri-Witness consensus)
5. Canonization (if approved, becomes law)

### EUREKA Memory System (6-Band Architecture)

Verdict-driven storage:

| Band | Purpose | Write Access | Retention |
|------|---------|-------------|-----------|
| **VAULT** | Constitutional law | Sealed at release | Permanent (COLD) |
| **LEDGER** | Audit trail | All verdicts | HOT→WARM→COLD |
| **ACTIVE** | Working memory | SEAL only | HOT (7 days) |
| **PHOENIX** | Amendment proposals | PARTIAL/SABAR | WARM (90 days) |
| **WITNESS** | Local patterns | 888_HOLD | HOT (7 days) |
| **VOID** | Quarantine | VOID verdicts | 90d then purge |

**Cryptographic integrity:**
- SHA3-256 hash chain (tamper-evident)
- Merkle tree proofs
- `arifos-verify-ledger` command

### MCP Server Integration (IDE Support)

**Supported IDEs:** VS Code, Cursor (any MCP-compatible editor)

**Available Tools:**
- `arifos_judge` — Constitutional judgment on text
- `arifos_recall` — Query memory bands
- `arifos_audit` — Verify ledger integrity
- `arifos_fag_read` — Governed file access

---

## 🗺️ Active Research Directions

arifOS is exploring:

- **Parallel Execution** – Target: <10ms verdict latency (currently ~50ms)
- **Federated Governance** – Cross-organization constitutional networks
- **Quantum-Resistant Signatures** – Post-quantum cryptography for audit trails
- **Adaptive Floors** – Self-tuning thresholds per domain (legal vs. education)
- **Hardware Governance** – FPGA/ASIC implementation for subsecond verdicts

**No timeline commitments.** These directions may change based on real-world deployment feedback.

**Track active work:** [GitHub Projects](https://github.com/ariffazil/arifOS/projects)

**Contributing:** Interested in these areas? See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🏛️ Architecture at a Glance

```
┌──────────────────────────────────────────────────┐
│         AI System (Any LLM, Any Provider)        │
│        (OpenAI, Anthropic, Google, Local)        │
└────────────────────┬─────────────────────────────┘
                     │ generates output
                     │ (unconstrained)
                     ↓
            ┌─────────────────────┐
            │  arifOS Kernel      │
            │                     │
            │ ┌─────────────────┐ │
            │ │ Floor F1        │ │  Amanah (No harm)
            │ │ Floor F2        │ │  Truth
            │ │ Floor F3        │ │  Tri-Witness
            │ │ Floor F4        │ │  Clarity (ΔS)
            │ │ Floor F5        │ │  Peace² (Non-destructive)
            │ │ Floor F6        │ │  κᵣ (Empathy)
            │ │ Floor F7        │ │  Ω₀ (Humility)
            │ │ Floor F8        │ │  G (Governed intelligence)
            │ │ Floor F9        │ │  Anti-Hantu (No false authority)
            │ └─────────────────┘ │
            │                     │
            │ ΔΩΨ Trinity:        │
            │ • Δ Lane Router     │
            │ • Ω Aggregator      │
            │ • Ψ Vitality        │
            │                     │
            │ Verdict: JUDGE      │
            └────────┬────────────┘
                     │
             ┌───────┴────────┐
             │                │
        ✓ SEAL/PARTIAL   ✗ VOID/SABAR/HOLD
             │                │
             ↓                ↓
        Release         Refuse / Escalate
             │                │
             ↓                ↓
        User Gets         Human Authority
        Governed          + Audit Trail
        Output            (Merkle-chained)
```

---

## 📚 Documentation Map

| Role | Start Here | Then Read |
|------|-----------|-----------|
| **Developer** | [Quick Start](#quick-start-for-developers) | [CLAUDE.md](CLAUDE.md) |
| **Architect** | [Architecture](#architecture-at-a-glance) | [L1_THEORY/canon/](L1_THEORY/canon/) |
| **Security Officer** | [EUREKA Memory](#eureka-memory-system) | [spec/v45/](spec/v45/) |
| **System Operator** | [System Prompts](#system-prompts-copy-paste-ready) | [AGENTS.md](AGENTS.md) |
| **Platform Integrator** | [L2_GOVERNANCE](#l2_governance-copy-paste-governance) | [L2_GOVERNANCE/README.md](L2_GOVERNANCE/README.md) |
| **Philosopher** | [Philosophy & Deep Theory](docs/PHILOSOPHY.md) | [L1_THEORY/canon/](L1_THEORY/canon/) |
| **Another AI** | [What Is arifOS](#what-is-arifos-2-minute-concept) | [System Prompts](#system-prompts-copy-paste-ready) |

---

## 💭 Design Principles

arifOS enforces four thermodynamic constraints:

| Principle | Implementation | How to Verify |
|-----------|----------------|--------------|
| **Governance > Persuasion** | Constitutional floors = code, not prompts | Run [Quick Start](#quick-start-for-developers) → Execute `judge_output()` |
| **Refusal = Integrity** | VOID verdicts enforce hard refusal | [Example 3: Refusal](#example-3-refusal-governance-in-action) |
| **Law = Physics** | 9 Floors (F1-F9) are deterministic, non-negotiable | [9 Constitutional Floors](#the-nine-constitutional-floors) |
| **Audit > Faith** | SHA3-256 Merkle-chained ledger, tamper-evident | `arifos-verify-ledger` command |

**Full Philosophy & Theory:** [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md)

---

## ✅ Status & Maturity

- ✅ **Governance Kernel v45.0** (1997/2044 tests passing, 97.7%)
- 🚧 **Production Deployments** – Pilot phase (private organizations, NDA)
- 📊 **Public Transparency** – Code on GitHub, architecture documented, tests publicly verifiable
- ✅ **Evolving constitution** (Phoenix-72 amendment protocol)
- ✅ **Auditable** (Merkle-proof cooling ledger)
- ✅ **Portable** (L2_GOVERNANCE specs in JSON/YAML, embeddable anywhere)

**Version:** v45.0.0
**Test Coverage:** 97.7% (1997/2044 tests passing)
**License:** AGPL-3.0 (governance must remain auditable)

---

## ⚖️ License & Governance Ethos

**AGPL-3.0** — Because governance must be auditable and open.

You can deploy arifOS in closed environments. But your governance logic itself must remain inspectable. Accountability is non-negotiable.

Why AGPL?

Because governance is a public trust. If you modify how AI is governed, the public has a right to know. If you use arifOS to deploy systems, the people those systems serve have a right to audit the governance.

This is not about freedom of code. It is about freedom of accountability.

[See full license](LICENSE)

---

## 🆘 Getting Help

- **Questions:** [GitHub Discussions](https://github.com/ariffazil/arifOS/discussions)
- **Bugs:** [GitHub Issues](https://github.com/ariffazil/arifOS/issues)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Full Governance Guide:** [AGENTS.md](AGENTS.md)
- **Quick Reference:** [CLAUDE.md](CLAUDE.md)
- **Security:** [SECURITY.md](SECURITY.md)

---

[GitHub](https://github.com/ariffazil/arifOS) · [Docs](CLAUDE.md) · [Contributing](CONTRIBUTING.md) · [Philosophy](docs/PHILOSOPHY.md)

**Status:** v45.0.0 SEALED | Tests: 1997/2044 ✓ | License: AGPL-3.0
