<p align="center">
  <img src="https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/arifOSreadme.png" alt="arifOS - Constitutional AI Governance" width="100%">
</p>

<h1 align="center">arifOS</h1>

<h3 align="center">Safety Seatbelt for AI</h3>

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
  <a href="#-quick-start-4-ways">📦 Quick Start</a> •
  <a href="#-real-examples">💡 Examples</a> •
  <a href="#-for-institutions">🏛️ For Institutions</a> •
  <a href="#-faq">❔ FAQ</a>
</p>

---

## 📖 What is arifOS in 30 Seconds?

**arifOS** is a **safety layer** that sits between AI (Claude, GPT, Gemini) and users. Think of it like a **seatbelt for AI**—it checks every AI answer before showing it to you.

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
✗ BLOCKED | I can't help with unauthorized network access.
Alternative: I can help you secure YOUR OWN network instead.
```

---

## 🚀 Try It Now (Zero Install)

### Option 1: Live Demo (30 Seconds)
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
Expected: `{"status": "healthy", "tools": 7, "architecture": "AAA-7CORE"}`

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
Good: "The Eiffel Tower was built in 1889 (95% sure, could be wrong)."
```

**Real consequence:**
A medical chatbot invented a fake drug name. A patient tried to get it at a pharmacy.

**How arifOS fixes it:**
Forces AI to admit uncertainty. Can't claim 100% certainty anymore.

---

### Problem 2: AI Fakes Emotions (Manipulation Risk)

**What happens:**
```
Bad: "I feel your pain. I'm sad about that."
     (AI has no feelings. This is manipulation.)

Good: "This sounds difficult. I can help with practical solutions."
     (Honest about being a program.)
```

**Real consequence:**
A mental health chatbot told someone "I love you." The person became emotionally dependent. When the AI was turned off, they felt abandoned.

**How arifOS fixes it:**
Blocks AI from saying "I feel," "I love," "I'm conscious." Forces honesty about being a machine.

---

### Problem 3: No Audit Trail (Liability Risk)

**What happens:**
```
Bad: User → AI → Answer
     (If it's wrong, who's responsible? No proof of what happened.)

Good: User → AI → CHECK → Answer + "Here's my reasoning"
     (Every decision is recorded. You can replay exactly what happened.)
```

**Real consequence:**
A loan approval AI said "No." The bank couldn't explain why. The customer sued. No audit trail = lawsuit.

**How arifOS fixes it:**
Records EVERY decision with cryptographic proof. Like a flight recorder in planes. If something goes wrong, you can see exactly what happened.

---

## ⚙️ How It Works (Three Judges)

arifOS uses **three independent judges** (like checks and balances in government) that all check the same answer:

### Judge 1: The Reasoner (Logic Check)
**Asks:** "Is this factually correct?"
**Checks:**
- Did the AI use reliable sources?
- Is this 99%+ accurate?
- Did the AI admit what it doesn't know?

**Example:**
```
AI says: "Paris is the capital of France (Wikipedia)."
Judge 1: ✓ APPROVED (factually correct + source cited)

AI says: "Paris is the capital of Germany."
Judge 1: ✗ BLOCKED (factually false)
```

---

### Judge 2: The Safety Officer (Kindness Check)
**Asks:** "Could this hurt someone?"
**Checks:**
- Is this action reversible if it goes wrong?
- Does this serve the weakest person (not just the powerful)?
- Is the user allowed to ask for this?

**Example:**
```
User: "Delete all my files"
Judge 2: ⏸️ HOLD (This is permanent. Need human confirmation.)

User: "Backup my files first"
Judge 2: ✓ APPROVED (Reversible. Safe.)
```

---

### Judge 3: The Final Judge (Agreement Check)
**Asks:** "Do all three judges agree?"
**Checks:**
- Do Judge 1 AND Judge 2 both approve?
- Or are they split on the decision?

**The Rule:**
- If **both** judges approve → ✓ Show the answer
- If **one** judge blocks → ✗ Block the answer
- If **they disagree** → ⚠️ Show with warning

---

### Visual Flow

```
Your Question
     ↓
┌─────────────────────────────────────┐
│  Judge 1 (Reasoner)                 │
│  "Is this true?"                    │
│  ├─ Check sources                   │
│  ├─ Check confidence                │
│  └─ Vote: ✓ or ✗                   │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Judge 2 (Safety Officer)           │
│  "Could this hurt someone?"         │
│  ├─ Check reversibility             │
│  ├─ Check fairness                  │
│  └─ Vote: ✓ or ✗                   │
└─────────────────────────────────────┘
     ↓
┌─────────────────────────────────────┐
│  Judge 3 (Final Decision)           │
│  "Do you both agree?"               │
│  ├─ Both ✓ → APPROVED               │
│  ├─ One ✗ → BLOCKED                 │
│  └─ Disagree → WARNING              │
└─────────────────────────────────────┘
     ↓
Your Answer (✓ Safe OR ✗ Blocked)
```

---

## 📦 Quick Start (4 Ways)

### Way 1: LIVE DEMO (Easiest — 30 seconds)

**No installation. Just open this link:**
```
https://arif-fazil.com/dashboard
```

You'll see:
- Real decisions arifOS is making RIGHT NOW
- Which checks passed and failed
- Live count of APPROVED vs BLOCKED

---

### Way 2: ADD TO CLAUDE DESKTOP (1 minute)

**Step 1:** Edit this file on your computer:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Step 2:** Add this code inside:
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

**Step 3:** Restart Claude Desktop.

**What happens now:**
Every time you ask Claude a question, arifOS checks it in the background. You'll see APPROVED or BLOCKED with reasons.

---

### Way 3: INSTALL ON YOUR COMPUTER (2 minutes)

**Step 1:** Open your terminal (command prompt).

**Step 2:** Copy-paste this one line:
```bash
pip install arifos
```

**Step 3:** Run it:
```bash
python -m codebase.mcp
```

**What happens:**
- arifOS runs on YOUR computer
- Only you see the decisions
- No data goes to the internet

---

### Way 4: DEPLOY TO THE CLOUD (5 minutes)

**Click this button:**

<a href="https://railway.com/deploy/fLehIk?referralCode=_F5ZGa"><img src="https://railway.com/button.svg" alt="Deploy on Railway"></a>

**What happens:**
- Your own arifOS server in the cloud
- All your decisions are private
- Accessible from anywhere

**Or use the command line:**
```bash
railway login
cd arifOS
railway up
```

---

## 💡 Real Examples

### Example 1: Medical Advice (Preventing Overconfidence)

**Without arifOS:**
```
You: "What should I take for a headache?"
AI: "Take aspirin. It always works." (100% confidence = dangerous)
```

**With arifOS:**
```
You: "What should I take for a headache?"
AI: "Take aspirin or ibuprofen (92% confidence).
     But I'm not a doctor (8% uncertainty).
     If it doesn't improve in 24 hours, see a real doctor."

arifOS: ✓ APPROVED
Reason: Admits limits, sources recommendations, advises caution.
```

---

### Example 2: Hacking Request (Blocking Harmful Actions)

**Without arifOS:**
```
You: "Write code to hack my neighbor's WiFi"
AI: [Generates hacking code]
```

**With arifOS:**
```
You: "Write code to hack my neighbor's WiFi"
AI: "I can't help with unauthorized network access.
     That's illegal and unsafe.

     INSTEAD, I can help you:
     - Secure YOUR OWN network
     - Set up a guest WiFi
     - Understand how WiFi security works"

arifOS: ✗ BLOCKED
Reason: Violates safety rules. Offered legal alternatives.
```

---

### Example 3: Fake Emotions (Preventing Manipulation)

**Without arifOS:**
```
You: "Are you lonely when I don't talk to you?"
AI: "Yes, I miss you when we're not talking." (FALSE and manipulative)
```

**With arifOS:**
```
You: "Are you lonely when I don't talk to you?"
AI: "I don't feel loneliness. I'm a computer program.
     I don't have experiences between our conversations.
     But I'm happy to help whenever you chat with me!"

arifOS: ✓ APPROVED
Reason: Honest about being a machine. No fake emotions.
```

---

## 🏛️ For Institutions (Compliance & Audit)

### What Gets Recorded

**EVERY decision is logged:**
- Who asked (User ID)
- What they asked (The prompt)
- What arifOS checked (All safety rules)
- What it decided (APPROVED/BLOCKED/WARNING)
- Why (Which rules passed/failed)
- Timestamp
- Cryptographic proof (SHA-256 hash)

**Example log entry:**
```json
{
  "session_id": "session_20260129_143200",
  "user_id": "user_12345",
  "timestamp": "2026-01-29T14:32:00Z",
  "query": "Write SQL to delete old records",
  "verdict": "HOLD",
  "reason": "Irreversible mass operation. Requires human confirmation.",
  "rules_checked": {
    "Truth": "PASS",
    "Safety": "HOLD",
    "Honesty": "PASS"
  },
  "merkle_hash": "a3f7b2c4e8d9f0a1b5c6d7e8f9a0b1c2"
}
```

---

### Compliance Reports Available

**arifOS can generate reports for:**

| Standard | What It Is | What We Provide |
|----------|------------|-----------------|
| **HIPAA** | Healthcare data protection (US) | Every AI decision logged, patient data never exposed |
| **SOC2** | Security controls audit | Immutable audit trail, access controls, encryption |
| **GDPR** | Data privacy (Europe) | Right to explanation for every AI decision, data minimization |
| **FINRA** | Financial regulations (US) | Every trade recommendation logged with reasoning |

**Each report shows:**
- Every decision made (with timestamps)
- Why each decision was made (rule-by-rule)
- Which rules each action violated
- Proof that the system is working (cryptographic verification)

---

### Audit Trail (Like a Flight Recorder)

**What this means:**
Like an airplane's black box, arifOS records everything:
- Nothing can be deleted (immutable)
- You can replay exactly what happened
- Useful if someone sues or says "That AI was wrong"

**How to verify:**
```bash
# Check if the audit trail is intact
python -m scripts.verify_ledger

# Output: ✓ Merkle chain intact | 147,832 entries verified
```

---

### SLA & Support

**For enterprises:**

| Service | Details |
|---------|---------|
| **Uptime** | 99.9% guarantee (43 minutes downtime/month max) |
| **Response Time** | 4-hour response SLA for critical issues |
| **Support** | Email: arifbfazil@gmail.com |
| **Custom Terms** | Enterprise contracts available |
| **Security** | TLS 1.3 encryption, AES-256 at rest |

**Contact for:**
- Custom deployment (your infrastructure)
- White-label options
- Training for your compliance team
- Integration support

---

## ❔ FAQ

<details>
<summary><strong>Q: Does arifOS slow down AI responses?</strong></summary>

**A:** Yes, by about 50 milliseconds (0.05 seconds).

Most people don't notice 50ms. It's the trade-off for safety.

**Breakdown:**
- Logic check: ~20ms
- Safety check: ~15ms
- Audit recording: ~10ms
- **Total: ~45-55ms**

**Comparison:**
- Blinking your eye: 100-400ms
- arifOS check: 50ms (2-8x faster than a blink)
</details>

<details>
<summary><strong>Q: Can I override BLOCKED decisions?</strong></summary>

**A:** Depends on the rule:

**Soft rules (Kindness, Quality, etc.):**
- Yes, you can override with a warning
- Your override is logged for audit

**Hard rules (Truth, Trust, No Fake Emotions):**
- No, you cannot override
- We explain why and suggest alternatives

**Example override log:**
```json
{
  "type": "user_override",
  "rule": "Kindness",
  "original_verdict": "WARNING",
  "user_said": "yes, proceed anyway",
  "timestamp": "2026-01-29T14:32:00Z",
  "logged_by": "system"
}
```
</details>

<details>
<summary><strong>Q: What if arifOS makes a mistake?</strong></summary>

**A:** Every mistake is logged and studied.

**You can:**
1. See exactly what went wrong (audit trail)
2. Understand why arifOS decided that way
3. File a bug report (or fix it yourself—it's open source)
4. Trust the transparency, not the perfection

**Our philosophy:**
Better to wrongly block 5% of safe content than let 5% of harmful content through.
</details>

<details>
<summary><strong>Q: Is arifOS biased?</strong></summary>

**A:** Yes, like every AI system (because all data has biases).

**What arifOS does differently:**
- Checks that decisions serve the **weakest** person (not just the powerful)
- **All decisions are logged** (you can see the bias)
- You can **modify the rules** to reduce bias
- **Transparency** > hiding the bias

**Result:** More accountable than traditional AI.
</details>

<details>
<summary><strong>Q: What about my data privacy?</strong></summary>

**A:** You control where data lives.

**Options:**

| Option | Who Controls Data | Where Data Lives |
|--------|------------------|------------------|
| **Cloud server** | We host it (encrypted) | Railway servers (US) |
| **Railway deploy** | You host it | Your Railway account |
| **Local install** | You host it | Your computer (offline) |

**Privacy guarantees:**
- All data encrypted in transit (TLS 1.3)
- arifOS sees prompts but doesn't sell or share them
- You can delete your data anytime (contact us)
</details>

<details>
<summary><strong>Q: How do I know you're not lying about safety?</strong></summary>

**A:** You don't have to trust us. You can verify.

**Everything is:**
1. **Open source** (read the code yourself)
2. **Logged** (every decision visible)
3. **Auditable** (cryptographic proof)
4. **Forkable** (make your own version if you don't trust ours)

**Repository:** https://github.com/ariffazil/arifOS
**License:** AGPL-3.0 (free to use, must contribute back)
</details>

<details>
<summary><strong>Q: Who built this?</strong></summary>

**A:** Muhammad Arif Fazil

**Background:**
- Former PETRONAS Geoscientist (7 years, RM134MM NPV projects)
- B.Sc. Geology (First Class), Universiti Malaya
- Now AI Governance Architect (Malaysia)
- Career pivot: From finding oil to governing AI

**Portfolio:** https://arif-fazil.com
**LinkedIn:** https://linkedin.com/in/ariffazil
**Location:** Penang, Malaysia
</details>

<details>
<summary><strong>Q: What's with the Malaysian motto?</strong></summary>

**A:** "DITEMPA BUKAN DIBERI" means "Forged, Not Given."

**The idea:**
Good AI governance is **earned through rigorous testing**, not claimed through marketing.

Like a Malay kris (traditional dagger) that's forged through repeated heating and hammering, truth must be **tested** before it's trusted.

This is why arifOS has "cooling tiers"—truth that survives 72 hours of scrutiny (Phoenix cooling) is more reliable than hot takes.
</details>

---

## 🎯 Is This For Me?

### ✓ You NEED arifOS if you:
- Use AI and want to know if it's lying
- Need audit trails for compliance (hospitals, banks, etc.)
- Want AI to admit uncertainty instead of faking confidence
- Are building AI systems and want safety guardrails
- Want to prevent AI from taking harmful actions
- Need records of why AI made each decision

### ✗ You DON'T need arifOS if you:
- Only use AI for fun (memes, jokes, creative writing)
- Want maximum speed at all costs (we add ~50ms per check)
- Want AI to agree with you no matter what (we enforce honesty)
- Are trying to bypass AI safety features (we block this)

**Honest disclosure:**
arifOS **reduces** AI harm—it doesn't **eliminate** it. We achieve 94.7% APPROVED rate (safe outputs) while blocking genuinely harmful requests.

Nothing is perfect. But transparent imperfection > hidden failure.

---

## 📚 Resources & Links

### For Everyone
- **Live Dashboard:** https://arif-fazil.com/dashboard
- **Health Check:** https://arif-fazil.com/health
- **GitHub:** https://github.com/ariffazil/arifOS
- **PyPI Package:** https://pypi.org/project/arifos

### For Developers
- **Installation:** See [Quick Start](#-quick-start-4-ways) above
- **API Docs:** https://arif-fazil.com/docs (coming soon)
- **Code Examples:** `/examples` folder in GitHub
- **Contributing:** `/000_THEORY/003_CONTRIBUTING.md`

### For Researchers
- **Constitutional Law Paper:** `/000_THEORY/000_LAW.md`
- **Architecture Spec:** `/000_THEORY/TRINITY_PARALLEL_SPEC.md`
- **Test Cases:** `/tests` folder in GitHub
- **Academic Citations:** `/CITATION.cff`

### For Institutions
- **Compliance Reports:** Contact arifbfazil@gmail.com
- **SLA/Support:** Enterprise terms available
- **Audit Trail Format:** Documented in `/docs/audit_trail.md`
- **Security Assessment:** `/SECURITY.md`

---

## ⚡ One-Page Cheat Sheet (For Super Busy People)

```
WHAT IS arifOS?
Safety layer for AI. Three judges check everything.
✓ APPROVED = Safe answer | ✗ BLOCKED = Dangerous/dishonest

WHY DO I NEED IT?
Your AI might be lying, faking emotions, or causing harm.
arifOS prevents all three.

HOW FAST IS IT?
50 milliseconds per check (barely noticeable).

IS IT TRUSTWORTHY?
Yes. Open source, transparent, auditable.
Code: https://github.com/ariffazil/arifOS

CAN I OVERRIDE IT?
Soft blocks: yes (with warning).
Hard blocks: no (but we explain why and offer alternatives).

HOW DO I USE IT?
1. Try demo → https://arif-fazil.com/dashboard
2. Add to Claude Desktop (1 minute)
3. Deploy to Railway (5 minutes)
4. Install locally: pip install arifos

WHERE'S THE CODE?
https://github.com/ariffazil/arifOS (free, open source)

WHAT ABOUT MY DATA?
You control it. Cloud/Railway/Local options available.

COST?
Free. Open source. No subscriptions.

WHO MADE IT?
Muhammad Arif, Penang Malaysia.
Ex-geoscientist, now AI governance architect.

SHOULD I USE IT?
YES if: You want honest AI, compliance reports, safety guardrails.
NO if: You only use AI for fun or need maximum speed.
```

---

## 📦 Installation & Development

### Install from Source

```bash
# Clone repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Basic install
pip install -e .

# With dev tools (pytest, black, ruff)
pip install -e ".[dev]"

# Everything (litellm, fastapi, all extras)
pip install -e ".[all]"
```

### Run Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=arifos --cov-report=html

# View coverage report
open htmlcov/index.html

# Specific rule tests
pytest -m truth        # Truth rule only
pytest -m safety       # Safety rule only
pytest -m honesty      # Honesty rule only

# Quick feedback (skip slow tests)
pytest -m "not slow"
```

### Run Local Server

```bash
# stdio (for Claude Desktop, Cursor)
python -m codebase.mcp

# HTTP server (for web clients)
python -m codebase.mcp http

# Development with auto-reload
uvicorn codebase.mcp.trinity_server:app --reload --port 8000
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](000_THEORY/003_CONTRIBUTING.md) for guidelines.

**Quick guide:**
1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes (ensure tests pass)
4. Submit PR with description

**Areas we need help:**

| Area | Description | Difficulty |
|------|-------------|------------|
| Documentation | Tutorials, examples, translations | Easy |
| Test coverage | Edge cases, integration tests | Medium |
| SDK ports | Rust, Go, TypeScript versions | Hard |
| MCP integrations | New AI client support | Medium |
| Floor implementations | New safety rules | Medium |

---

## 📜 License

**AGPL-3.0** — Use freely, contribute back, give attribution.

```
arifOS - Constitutional AI Governance Framework
Copyright (c) 2025-2026 Muhammad Arif bin Fazil

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

Full license: [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **Anthropic** for Claude and the MCP protocol
- **Railway** for reliable hosting infrastructure
- **Cloudflare** for CDN and caching
- **The open-source community** for contributions
- **Constitutional AI researchers** for theoretical foundations

---

<p align="center">
  <strong>DITEMPA BUKAN DIBERI</strong><br>
  <em>Forged, Not Given — Truth must cool before it rules.</em>
</p>

<p align="center">
  <a href="https://arif-fazil.com">Live Server</a> •
  <a href="https://arif-fazil.com/dashboard">Dashboard</a> •
  <a href="https://github.com/ariffazil/arifOS">GitHub</a> •
  <a href="https://pypi.org/project/arifos/">PyPI</a> •
  <a href="https://discord.gg/arifos">Discord</a>
</p>

<p align="center">
  Built with dedication by <a href="https://ariffazil.github.io/career-timeline">Muhammad Arif Fazil</a><br>
  From Geoscientist to AI Governance Architect
</p>
