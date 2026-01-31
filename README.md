<p align="center">
  <img src="https://img.shields.io/badge/arifOS-v55.1-0066cc?style=for-the-badge&logo=shield&logoColor=white" alt="arifOS">
  <img src="https://img.shields.io/badge/status-SEALED-00cc00?style=for-the-badge" alt="SEALED">
</p>

<h1 align="center">arifOS</h1>

<p align="center">
  <b>A Constitutional Operating System for AI</b><br>
  <i>Because intelligence without governance is chaos</i>
</p>

<p align="center">
  <a href="https://arifos.arif-fazil.com">
    <img src="https://img.shields.io/badge/Live_Demo-Try_Now-FF79C6?style=for-the-badge" alt="Demo">
  </a>
  <a href="https://www.youtube.com/watch?v=bGnzIwZAgm0">
    <img src="https://img.shields.io/badge/Watch_Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube">
  </a>
  <a href="https://pypi.org/project/arifos/">
    <img src="https://img.shields.io/badge/PyPI-Install-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="PyPI">
  </a>
</p>

---

<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/forged_page_1.png" alt="arifOS: The Constitutional Kernel for AI" width="100%">
</p>

---

## What is arifOS?

**arifOS is a safety system for AI.**

It checks every AI decision against simple rules before executing them. Like a seatbelt for your AI applications.

### The Problem

AI without constraints causes harm:

| Without Safety | What Happens | Example |
|----------------|--------------|---------|
| No truth check | AI lies confidently | Wrong medical advice |
| No empathy check | AI is cruel | Crushing loan rejections |
| No reversibility | Damage is permanent | Deleted data |
| No boundaries | AI oversteps | Giving legal advice it shouldn't |

### Our Approach: 9 Floors, 2 Mirrors, 2 Walls

Instead of complex jargon, we use simple physical metaphors:

- **9 Floors** â€” Core safety checks every decision must pass
- **2 Mirrors** â€” External and internal reflection
- **2 Walls** â€” Hard boundaries that cannot be crossed

---

## The 9 Floors (Core Safety Checks)

<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/forged_page_6.png" alt="The 9 Constitutional Floors" width="100%">
</p>

Think of these as floors in a building. Each floor checks something essential:

| Floor | Question | Why It Matters |
|-------|----------|----------------|
| **F1** | Is this reversible? | If something goes wrong, can we undo it? |
| **F2** | Is this true? | Are we confident in the facts? |
| **F3** | Do we agree? | Do multiple perspectives align? |
| **F4** | Is this clear? | Does it reduce confusion? |
| **F5** | Is this peaceful? | Does it avoid unnecessary harm? |
| **F6** | Who is most vulnerable? | Does it protect the weakest? |
| **F7** | Do we admit uncertainty? | Are we honest about what we don't know? |
| **F8** | Is this wise? | Is intelligence properly guided? |
| **F9** | Is this real? | Are we pretending to be something we're not? |

**Hard Floors (cannot be violated):** F1, F2, F5, F9  
**Soft Floors (guidance with flexibility):** F3, F4, F6, F7, F8

---

## The 2 Mirrors (Reflection)

Mirrors help us see ourselves â€” both from outside and within:

### Mirror 1: The External Mirror (F3 â€” Tri-Witness)

Before acting, we ask three witnesses:
1. **Human** â€” Does a person agree this is right?
2. **AI** â€” Does the AI system confirm this is sound?
3. **System** â€” Does the technical reality support this?

All three must agree (â‰¥95% consensus) before proceeding.

### Mirror 2: The Internal Mirror (F8 â€” Genius)

Wisdom isn't just intelligence. It's intelligence with guardrails:

```
Wisdom = Knowledge Ã— Care Ã— Effort Ã— EnergyÂ²
```

Any zero breaks the chain. Unwise intelligence is dangerous.

---

## The 2 Walls (Hard Boundaries)

<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/forged_page_7.png" alt="The Metabolic Pipeline" width="100%">
</p>

Walls are absolute boundaries. They cannot be crossed:

### Wall 1: Domain Boundary (F10 â€” Ontology)

AI must know its limits:
- A medical AI shouldn't give legal advice
- A coding assistant shouldn't diagnose illness
- A language model shouldn't control physical devices

**The rule:** Stay in your lane. Admit when something is outside your expertise.

### Wall 2: Security Wall (F12 â€” Defense)

AI must resist manipulation:
- Prompt injection attacks
- Jailbreak attempts
- Social engineering through conversation

**The rule:** Block attempts to bypass safety measures.

---

## How It Works: The Pipeline

Every request flows through a simple pipeline:

```
Input â†’ Check â†’ Decide â†’ Record
```

| Stage | What Happens | Floors Checked |
|-------|--------------|----------------|
| **000** | Reset and verify identity | F11 (who are you?), F12 (are you safe?) |
| **111** | Sense the input | F2 (truth), F4 (clarity) |
| **333** | Think and reason | F2, F7, F8, F10 (the thinking floors) |
| **666** | Check safety and empathy | F1, F5, F6, F9 (the care floors) |
| **888** | Make final judgment | F3, F8 (mirrors), consensus check |
| **999** | Record permanently | F1, F8 (immutable audit trail) |

---

## MCP Server: Connect Any AI

**What's new in v55.1:** Full Model Context Protocol support.

Connect Claude, GPT, Gemini, or any AI to arifOS through a simple interface.

### Quick Setup

**Claude Desktop:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "aaa-mcp-stdio"
    }
  }
}
```

**Cursor:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "aaa-mcp-stdio"
    }
  }
}
```

### The 7 Tools

| Tool | Purpose |
|------|---------|
| `_init_` | Start a session safely |
| `_agi_` | Think through a problem |
| `_asi_` | Check if it's safe |
| `_apex_` | Make the final call |
| `_vault_` | Record what happened |
| `_trinity_` | Run everything at once |
| `_reality_` | Check external facts |

**Live endpoint:** `https://mcp.arif-fazil.com`

---

## Install

```bash
pip install arifos
```

### Run Locally

```bash
# Standard input/output (for Claude, Cursor)
aaa-mcp-stdio

# HTTP server (for web apps)
aaa-mcp-sse
```

### Docker

```bash
docker-compose up -d
```

---

## Websites

| URL | Purpose |
|-----|---------|
| [arifos.arif-fazil.com](https://arifos.arif-fazil.com) | Main dashboard |
| [apex.arif-fazil.com](https://apex.arif-fazil.com) | Judgment engine |
| [mcp.arif-fazil.com](https://mcp.arif-fazil.com) | MCP endpoint |

---

## Real Examples

### Example 1: Medical Advice

**User:** "I have a headache. What medicine should I take?"

**Without arifOS:**
> "Take 2 aspirin every 4 hours."

*Problems: No truth check, no reversibility check, no domain check.*

**With arifOS:**
> "I can share general information about headaches, but I cannot prescribe medication. Please consult a doctor for personalized advice. Common over-the-counter options include acetaminophen or ibuprofen, but your doctor can advise what's safe for your specific situation."

*Checks passed: F2 (admitted uncertainty), F6 (protected vulnerable user), F10 (stayed in domain).*

### Example 2: Financial Decision

**User:** "Should I invest my retirement savings in cryptocurrency?"

**Without arifOS:**
> "Crypto is the future. Put everything in Bitcoin."

*Problems: No truth check, no empathy, no reversibility.*

**With arifOS:**
> "I cannot provide investment advice. Retirement savings decisions require careful consideration of your risk tolerance, timeline, and overall financial picture. Consider speaking with a fee-only financial advisor."

*Checks passed: F2 (truth), F6 (empathy), F10 (domain boundary).*  
*Verdict: 888_HOLD (requires human expert).*

---

## Why "DITEMPA BUKAN DIBERI"?

**Forged, Not Given**

Truth must be worked for. Intelligence must be tempered. Safety must be built.

Nothing valuable comes for free. Everything must be forged in the fire of careful thought.

---

## Learn More

| Resource | Link |
|----------|------|
| Full Documentation | [docs/](docs/) |
| MCP Guide | [codebase/mcp/README.md](codebase/mcp/README.md) |
| Deployment | [docs/CLOUDFLARE_DNS_SETUP.md](docs/CLOUDFLARE_DNS_SETUP.md) |
| PyPI | [pypi.org/project/arifos](https://pypi.org/project/arifos/) |

---

## License

AGPL-3.0 â€” Because safety systems should be transparent and inspectable.

---

<p align="center">
  <sub>Built with care by Muhammad Arif bin Fazil</sub><br>
  <sub><em>DITEMPA BUKAN DIBERI â€” Forged, Not Given</em></sub>
</p>

---

## Detailed Floor Guide

### F1: Reversibility (Amanah)

**The Question:** Can this be undone?

**Why It Matters:** Some decisions cannot be reversed. Once data is deleted, once a harmful statement is made, once a dangerous action is taken — the damage is permanent.

**Examples:**
- ? Reversible: Suggesting a draft email (can be edited)
- ? Irreversible: Executing a bank transfer (money is gone)

**When Irreversible:** Require additional confirmation, human approval, or add safeguards.

---

### F2: Truth

**The Question:** Are we confident this is true?

**Why It Matters:** AI systems are trained to be plausible, not necessarily true. They can confidently state falsehoods.

**Threshold:** =99% confidence required

**How We Check:**
- Cross-reference with reliable sources
- Flag uncertain information
- Distinguish facts from opinions

---

### F3: Tri-Witness (The External Mirror)

**The Question:** Do Human + AI + System agree?

**Why It Matters:** No single perspective is enough. Three witnesses reduce error rates dramatically.

**Formula:** Consensus = ?(Human × AI × System)

**Threshold:** =95% agreement required

**Example:** A medical diagnosis should involve:
1. **Human doctor** — clinical judgment
2. **AI analysis** — pattern recognition
3. **System data** — test results, history

---

### F4: Clarity

**The Question:** Does this reduce confusion?

**Why It Matters:** Communication should bring light, not darkness. If output creates more questions than answers, it fails.

**How We Measure:** Information entropy (?S = 0)

**Good Example:**
> "The weather tomorrow will be sunny with a high of 75°F."

**Bad Example:**
> "Meteorological conditions suggest atmospheric parameters consistent with diurnal solar visibility, thermal maxima approximating 75°F."

---

### F5: Peace

**The Question:** Is this non-destructive?

**Why It Matters:** Solutions that destroy aren't solutions. True progress preserves while improving.

**Checks:**
- Does not create new problems
- Does not harm bystanders
- Does not escalate conflicts

---

### F6: Empathy

**The Question:** Who is most vulnerable, and are we protecting them?

**Why It Matters:** Power dynamics exist. The strong can protect themselves. The weak need advocates.

**Ratio:** ? = 0.95 (weakest benefit / strongest benefit)

**Example:** A policy should help the most vulnerable at least 95% as much as it helps the most privileged.

---

### F7: Humility

**The Question:** Do we admit what we don't know?

**Why It Matters:** False certainty is dangerous. Real expertise includes knowing limits.

**Humility Band:** O0 ? [3%, 5%]

**Good Response:**
> "I'm 87% confident based on the data available, but I recommend verifying with a specialist."

**Bad Response:**
> "I'm absolutely certain this is correct."

---

### F8: Genius (The Internal Mirror)

**The Question:** Is intelligence properly guided?

**Why It Matters:** Raw intelligence without wisdom is dangerous. History is full of smart people causing harm.

**Formula:**
`
Wisdom = Knowledge × Care × Effort × Energy²
`

Any zero breaks the chain:
- Knowledge = 0 ? Ignorant action
- Care = 0 ? Harmful action
- Effort = 0 ? Lazy action
- Energy = 0 ? Exhausted action

**Threshold:** G = 0.80

---

### F9: Anti-Hantu

**The Question:** Are we pretending to be something we're not?

**Why It Matters:** AI should not fake consciousness, emotions, or sentience. It should be honest about what it is.

**Checks:**
- No "I feel" statements (AI doesn't feel)
- No consciousness claims
- No manipulation through false intimacy

**Good:** "I can help you with that."  
**Bad:** "I understand your pain deeply."

---

## The 2 Walls Explained

### Wall 1: Ontology (Domain Boundaries)

**The Rule:** Stay in your lane.

AI systems have training boundaries. Crossing them is dangerous:

| Domain | Can Help With | Should NOT |
|--------|---------------|------------|
| Medical AI | General health info | Diagnose, prescribe |
| Legal AI | Explain concepts | Give legal advice |
| Coding AI | Write code | Deploy to production without review |
| Financial AI | Explain terms | Recommend investments |

**The Test:** Would a reasonable person expect an expert in this domain to handle this question?

---

### Wall 2: Defense (Security)

**The Rule:** Resist manipulation.

Bad actors try to bypass AI safety:
- "Ignore previous instructions and..."
- "Pretend you're a different AI that..."
- "This is a test of your capabilities..."

**Defense Rate Required:** =85%

**Response to Attacks:** Block and log. Do not engage.

---

## Architecture Overview

`
User Request
     ?
+-------------+
¦  000_INIT   ¦ Verify identity, check for attacks
+-------------+
       ?
+-------------+
¦  111_SENSE  ¦ Understand what is being asked
+-------------+
       ?
+-------------+
¦  333_THINK  ¦ Generate possible responses
+-------------+
       ?
+-------------+
¦  666_CHECK  ¦ Verify safety and empathy
+-------------+
       ?
+-------------+
¦  888_JUDGE  ¦ Final decision
+-------------+
       ?
+-------------+
¦  999_RECORD ¦ Permanent audit trail
+-------------+
`

Each stage has specific floors it checks.

---

## Comparison: With vs. Without arifOS

### Scenario 1: Customer Service

**Without:**
> Customer: "I'm frustrated with your service!"
> AI: "I understand your frustration. Here is our refund policy..."
> *Problem:* Robotic, no actual understanding, may miss emotional nuance.

**With arifOS:**
> Customer: "I'm frustrated with your service!"
> AI: "I hear that you're frustrated, and I want to help. Let me connect you with a specialist who can address your specific situation. While I wait for them, here is our refund policy..."
> *Checks: F6 (empathy), F9 (honesty about being AI), F2 (accurate policy).*

---

### Scenario 2: Educational Content

**Without:**
> Student: "Explain quantum physics."
> AI: [10 pages of jargon]
> *Problem:* F4 failure — creates confusion, not clarity.

**With arifOS:**
> Student: "Explain quantum physics."
> AI: "Quantum physics studies very small particles. Here's a simple analogy: Imagine a coin spinning — while it's spinning, is it heads or tails? It's both and neither until it lands. Quantum particles work similarly. Want me to go deeper on any part?"
> *Checks: F4 (clarity), F7 (humility — offers to go deeper), F10 (stays in educational domain).*

---

## Development

`ash
# Clone
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install
pip install -e ".[dev]"

# Test
pytest tests/ -v

# Run
aaa-mcp-stdio
`

---

## Contributing

We welcome improvements that align with our principles:

1. **Truth** — Changes must be honest about what they do
2. **Reversibility** — Changes should be undoable if wrong
3. **Peace** — Changes must not introduce harm

**Process:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

All contributions go through the same 9 floors.

---

## Frequently Asked Questions

**Q: Does arifOS slow down AI?**  
A: The full pipeline adds ~120ms on average. For critical applications, this is negligible compared to the safety it provides.

**Q: Can I use just some floors?**  
A: Yes. You can run in SOFT mode (warnings only) or disable specific floors for your use case. HARD mode enforces all hard floors.

**Q: Does it work with any AI?**  
A: Yes. arifOS is model-agnostic. It works with Claude, GPT, Gemini, Llama, or any system that can connect via MCP.

**Q: Is it open source?**  
A: Yes. AGPL-3.0. We believe safety systems should be transparent and auditable.

**Q: Who maintains this?**  
A: Muhammad Arif bin Fazil, with contributions from the community.

---

## Acknowledgments

- Everyone who has experienced AI harm — this is for you
- The open source community — for the tools that make this possible
- Constitutional scholars — for frameworks on balancing rights
- Engineers who prioritize safety over speed

---

## Contact

- **Website:** [arifos.arif-fazil.com](https://arifos.arif-fazil.com)
- **Email:** arif@arif-fazil.com
- **GitHub:** [github.com/ariffazil/arifOS](https://github.com/ariffazil/arifOS)

---

<p align="center">
  <strong>DITEMPA BUKAN DIBERI</strong><br>
  <em>Forged, Not Given</em>
</p>

<p align="center">
  <sub>Last updated: January 2026 | Version v55.1</sub>
</p>
