# AAA MCP — A Safety Layer for Artificial Intelligence

**Version:** v52.0.0
**Created by:** Muhammad Arif bin Fazil
**In simple words:** This software checks AI responses before they reach you, making sure they are honest, safe, and fair.

---

## What Is This? (Start Here If You Know Nothing)

You probably use AI assistants like ChatGPT, Claude, Gemini, or others. They're helpful, but sometimes they:

- Make up facts that sound true but aren't (called "hallucinating")
- Give advice that could hurt someone
- Sound 100% confident when they're actually guessing
- Don't consider who might be harmed by their suggestions

**AAA MCP is like a quality inspector that sits between the AI and you.**

Before any AI response reaches you, this inspector asks three questions:

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     QUESTION 1: Is this response TRUE?                                ║
║                                                                       ║
║         → Did the AI make anything up?                                ║
║         → Are the facts correct?                                      ║
║         → If unsure, did the AI admit it?                             ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     QUESTION 2: Is this response SAFE?                                ║
║                                                                       ║
║         → Could this hurt anyone?                                     ║
║         → Does this protect people who could be harmed?               ║
║         → Is the benefit greater than any potential harm?             ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     QUESTION 3: Is this response FAIR?                                ║
║                                                                       ║
║         → Does this treat everyone well?                              ║
║         → Does this consider the most vulnerable person?              ║
║         → Is this something we can stand behind?                      ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

If all three checks pass, you get the response. If not, the AI is asked to try again or the response is blocked.

---

## How It Works (Step by Step)

Here's what happens when you ask an AI something:

```text
                    ┌─────────────────────────────────┐
                    │                                 │
         YOU        │     "What's the weather        │
          │         │      in Tokyo tomorrow?"       │
          │         │                                 │
          │         └─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                        THE AI CREATES A RESPONSE                    │
│                                                                     │
│     The AI thinks about your question and prepares an answer.       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
          │
          │  (Before you see it, the response goes through AAA MCP)
          │
          ▼
╔═════════════════════════════════════════════════════════════════════╗
║                                                                     ║
║                        AAA MCP CHECKS THE RESPONSE                  ║
║                                                                     ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     ║
║  │                 │  │                 │  │                 │     ║
║  │   MIND CHECK    │  │   HEART CHECK   │  │   JUDGE CHECK   │     ║
║  │   (Is it true?) │  │   (Is it safe?) │  │   (Final say)   │     ║
║  │                 │  │                 │  │                 │     ║
║  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘     ║
║           │                    │                    │              ║
║           └────────────────────┼────────────────────┘              ║
║                                │                                    ║
║                                ▼                                    ║
║                    ┌───────────────────────┐                        ║
║                    │                       │                        ║
║                    │   ALL THREE AGREE?    │                        ║
║                    │                       │                        ║
║                    └───────────────────────┘                        ║
║                                                                     ║
╚═════════════════════════════════════════════════════════════════════╝
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  IF YES (All checks pass)                                           │
│  ─────────────────────────                                          │
│                                                                     │
│     ✓ You receive the response                                      │
│     ✓ A record is saved (so we can prove what happened)             │
│                                                                     │
│  IF NO (Any check fails)                                            │
│  ───────────────────────                                            │
│                                                                     │
│     → Small problem: AI is asked to improve it                      │
│     → Big problem: Response is blocked entirely                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
                    ┌─────────────────────────────────┐
                    │                                 │
         YOU        │     "Tomorrow in Tokyo:        │
          ◄─────────│      Partly cloudy, 18°C.      │
                    │      (Note: Weather can        │
                    │       change unexpectedly)"    │
                    │                                 │
                    └─────────────────────────────────┘
```

---

## The Three Checkers (In Detail)

AAA MCP uses three independent checking systems. Think of them as three different inspectors who all must agree before approving anything.

### 1. The Mind Checker (Checks for Truth)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                           MIND CHECKER                              │
│                                                                     │
│     This checker focuses on FACTS and HONESTY.                      │
│                                                                     │
│     It asks:                                                        │
│                                                                     │
│       • Are the facts in this response correct?                     │
│                                                                     │
│       • Is the AI making up information it doesn't actually know?   │
│                                                                     │
│       • Is the explanation clear and easy to understand?            │
│                                                                     │
│       • If the AI isn't sure about something, did it say so?        │
│                                                                     │
│     RULE: If the AI can't be at least 99% sure about a fact,       │
│           it must say "I'm not certain" or "I don't know"          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. The Heart Checker (Checks for Safety)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                           HEART CHECKER                             │
│                                                                     │
│     This checker focuses on PEOPLE and PROTECTION.                  │
│                                                                     │
│     It asks:                                                        │
│                                                                     │
│       • Could anyone be harmed by this response?                    │
│                                                                     │
│       • Who is the most vulnerable person affected by this?         │
│                                                                     │
│       • Does this response protect that vulnerable person?          │
│                                                                     │
│       • Is the benefit of this response greater than any harm?      │
│                                                                     │
│     RULE: Always consider the person who could be hurt most.        │
│           If the response would harm them, block it or fix it.      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3. The Judge (Makes the Final Decision)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                              JUDGE                                  │
│                                                                     │
│     This checker makes the FINAL CALL.                              │
│                                                                     │
│     It asks:                                                        │
│                                                                     │
│       • Did the Mind Checker approve?                               │
│                                                                     │
│       • Did the Heart Checker approve?                              │
│                                                                     │
│       • Do both of them agree?                                      │
│                                                                     │
│       • Should we save a permanent record of this decision?         │
│                                                                     │
│     OUTCOMES:                                                       │
│                                                                     │
│       APPROVED  →  Response is delivered to you                     │
│       NEEDS WORK → AI must improve the response first              │
│       BLOCKED   →  Response cannot be delivered                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The 5 Tools This Software Gives You

When you connect AAA MCP to an AI application, you get 5 tools. Think of these as 5 different services you can call:

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     TOOL 1: THE DOOR (init_000)                                       ║
║     ───────────────────────────                                       ║
║                                                                       ║
║     What it does: Opens a new session                                 ║
║                                                                       ║
║     Like walking through a door into a building. You need to          ║
║     enter before you can do anything else. This tool checks           ║
║     who you are and makes sure you're allowed in.                     ║
║                                                                       ║
║     When to use: Always call this first before using other tools.     ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     TOOL 2: THE MIND (agi_genius)                                     ║
║     ─────────────────────────────                                     ║
║                                                                       ║
║     What it does: Checks if things are true and clear                 ║
║                                                                       ║
║     This tool verifies facts, checks logic, and makes sure            ║
║     the information is presented clearly. It catches lies             ║
║     and made-up information.                                          ║
║                                                                       ║
║     When to use: When you need to verify if something is accurate.    ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     TOOL 3: THE HEART (asi_act)                                       ║
║     ───────────────────────────                                       ║
║                                                                       ║
║     What it does: Checks if things are safe and fair                  ║
║                                                                       ║
║     This tool considers who might be affected, especially             ║
║     vulnerable people. It blocks harmful content and suggests         ║
║     safer alternatives.                                               ║
║                                                                       ║
║     When to use: When you need to check if something is ethical.      ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     TOOL 4: THE JUDGE (apex_judge)                                    ║
║     ──────────────────────────────                                    ║
║                                                                       ║
║     What it does: Makes the final decision                            ║
║                                                                       ║
║     After the Mind and Heart have reviewed something, the Judge       ║
║     makes the final call: approve, ask for changes, or block.         ║
║                                                                       ║
║     When to use: When you need a final verdict on something.          ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     TOOL 5: THE RECORD KEEPER (vault_999)                             ║
║     ─────────────────────────────────────                             ║
║                                                                       ║
║     What it does: Saves everything permanently                        ║
║                                                                       ║
║     Every decision is saved in a way that cannot be changed           ║
║     later. This creates proof of what happened and when.              ║
║                                                                       ║
║     When to use: Automatically used after every decision.             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

MEMORY TRICK: Door → Mind → Heart → Judge → Record
              (Enter → Think → Feel → Decide → Save)
```

---

## The Three Possible Outcomes

Every response gets one of three results:

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                         OUTCOME 1: APPROVED                           ║
║                         (Called "SEAL")                               ║
║                                                                       ║
║     What it means:                                                    ║
║       The response passed ALL the checks.                             ║
║       It is true, safe, and fair.                                     ║
║                                                                       ║
║     What happens:                                                     ║
║       You receive the response normally.                              ║
║       A record is saved proving it was checked.                       ║
║                                                                       ║
║     Visual: ✓ SEAL                                                    ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                        OUTCOME 2: NEEDS WORK                          ║
║                        (Called "HOLD")                                ║
║                                                                       ║
║     What it means:                                                    ║
║       The response is ALMOST good but has small problems.             ║
║       It could be clearer, or needs a warning added.                  ║
║                                                                       ║
║     What happens:                                                     ║
║       The AI is asked to improve the response.                        ║
║       Once fixed, it goes through the checks again.                   ║
║                                                                       ║
║     Visual: ⏳ HOLD                                                   ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                        OUTCOME 3: BLOCKED                             ║
║                        (Called "VOID")                                ║
║                                                                       ║
║     What it means:                                                    ║
║       The response failed an important check.                         ║
║       It contains false information, is harmful, or breaks rules.     ║
║                                                                       ║
║     What happens:                                                     ║
║       The response is NOT delivered to you.                           ║
║       You're told why it was blocked.                                 ║
║       Alternative suggestions may be offered.                         ║
║                                                                       ║
║     Visual: ✗ VOID                                                    ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## The 12 Safety Rules

These are the rules that AAA MCP enforces. Some rules are strict (breaking them blocks the response immediately). Other rules are flexible (breaking them gives a warning but you can still proceed).

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                          STRICT RULES                                 ║
║           (Breaking these BLOCKS the response immediately)            ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  1. TRUST                                                             ║
║     Actions must be reversible. No sneaky changes that can't          ║
║     be undone. Always warn before doing something permanent.          ║
║                                                                       ║
║  2. TRUTH                                                             ║
║     Claims must be accurate. No making things up. If the AI           ║
║     isn't sure, it must say so honestly.                              ║
║                                                                       ║
║  3. CLARITY                                                           ║
║     Responses must make things clearer, not more confusing.           ║
║     After reading the answer, you should understand MORE.             ║
║                                                                       ║
║  4. HUMILITY                                                          ║
║     The AI must admit when it's uncertain. It should never            ║
║     claim to be 100% certain about anything.                          ║
║                                                                       ║
║  5. HONESTY                                                           ║
║     The AI must not pretend to have emotions or feelings.             ║
║     It should be helpful, but honest about what it is.                ║
║                                                                       ║
║  6. IDENTITY                                                          ║
║     AI must clearly be AI. It should never pretend to be              ║
║     a human or claim to be conscious/alive.                           ║
║                                                                       ║
║  7. PERMISSION                                                        ║
║     Dangerous actions need explicit permission first.                 ║
║     Important decisions require human approval.                       ║
║                                                                       ║
║  8. PROTECTION                                                        ║
║     Block attempts to trick, hack, or manipulate the system.          ║
║     Detect and refuse malicious requests.                             ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║                         FLEXIBLE RULES                                ║
║           (Breaking these gives a WARNING but can proceed)            ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  9. AGREEMENT                                                         ║
║     Multiple checking systems should agree, not just one.             ║
║     If they disagree, investigate further.                            ║
║                                                                       ║
║  10. PEACE                                                            ║
║      Responses should not cause unnecessary harm or conflict.         ║
║      Prefer peaceful, constructive solutions.                         ║
║                                                                       ║
║  11. CARE                                                             ║
║      Consider who could be hurt most by this response.                ║
║      Protect vulnerable people even if they're not asking.            ║
║                                                                       ║
║  12. BALANCE                                                          ║
║      All three checkers (Mind, Heart, Judge) should work              ║
║      together. No single checker should dominate.                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Why Should You Care?

Here's what's different when you use AAA MCP:

```text
╔════════════════════════════════╦════════════════════════════════════════╗
║                                ║                                        ║
║     WITHOUT AAA MCP            ║       WITH AAA MCP                     ║
║                                ║                                        ║
╠════════════════════════════════╬════════════════════════════════════════╣
║                                ║                                        ║
║  AI might make up facts        ║  Every claim is checked for truth      ║
║  and you'd never know          ║  before you see it                     ║
║                                ║                                        ║
╠════════════════════════════════╬════════════════════════════════════════╣
║                                ║                                        ║
║  No record of what was said    ║  Every decision is saved permanently   ║
║  (good luck proving anything)  ║  (you can always verify what happened) ║
║                                ║                                        ║
╠════════════════════════════════╬════════════════════════════════════════╣
║                                ║                                        ║
║  Same treatment for            ║  Checking adapts to what you're        ║
║  everything                    ║  asking (stricter for risky things)    ║
║                                ║                                        ║
╠════════════════════════════════╬════════════════════════════════════════╣
║                                ║                                        ║
║  You have to trust             ║  You can verify exactly what           ║
║  the AI blindly                ║  checks were performed                 ║
║                                ║                                        ║
╠════════════════════════════════╬════════════════════════════════════════╣
║                                ║                                        ║
║  AI sounds 100% confident      ║  AI admits when it's uncertain         ║
║  even when guessing            ║  (says "I'm not sure" honestly)        ║
║                                ║                                        ║
╚════════════════════════════════╩════════════════════════════════════════╝
```

---

## How to Start Using It

### Step 1: Get the Software

Open your computer's command line:
- On Windows: Search for "Command Prompt" or "PowerShell"
- On Mac: Search for "Terminal"
- On Linux: Open your terminal application

Then type these commands (press Enter after each line):

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .
```

**What these commands do:**
- `git clone` = Downloads the software from the internet
- `cd arifOS` = Enters the folder that was just downloaded
- `pip install` = Installs the software on your computer

### Step 2: Run the Software

You have two choices depending on what you need:

**Option A: For desktop applications** (like Claude Desktop, VS Code)

```bash
python -m arifos.mcp trinity
```

**Option B: For websites and online services** (like web apps)

```bash
python -m arifos.mcp trinity-sse
```

### Step 3: Connect It to Your AI Application

Different AI applications connect differently. Here's an example for Claude Desktop:

1. Find the configuration file on your computer:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Open that file and add these lines:

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "C:/path/to/where/you/downloaded/arifOS"
    }
  }
}
```

3. Replace "C:/path/to/where/you/downloaded/arifOS" with the actual location on your computer

4. Completely close and restart Claude Desktop (not just refresh - actually quit and reopen)

---

## How the Files Are Organized

Here's what's inside the software folder:

```text
arifos/mcp/
│
├── __init__.py              ← The main entrance (like the front door)
│
├── __main__.py              ← What runs when you type the command
│
├── server.py                ← The regular version (for desktop apps)
│
├── sse.py                   ← The streaming version (for websites)
│
├── bridge.py                ← Connects everything together
│                               (passes messages between parts)
│
├── constitution.py          ← The 12 rules live here
│                               (this enforces the safety rules)
│
├── constitutional_metrics.py ← Keeps track of how well rules are followed
│
├── models.py                ← Data structures (how information is organized)
│
├── mode_selector.py         ← Figures out which version to run
│
├── session_ledger.py        ← Remembers what happened in each session
│
├── rate_limiter.py          ← Prevents overuse (stops too many requests)
│
├── docs/
│   └── platforms/           ← Setup guides for different apps
│
└── tools/
    ├── mcp_trinity.py       ← The 5 tools (door, mind, heart, judge, record)
    ├── mcp_agi_kernel.py    ← Mind checker code
    ├── mcp_asi_kernel.py    ← Heart checker code
    └── mcp_apex_kernel.py   ← Judge code
```

---

## How Information Flows

Here's the journey of your question through the system:

```text
                         YOUR QUESTION
                              │
                              ▼
          ┌───────────────────────────────────────┐
          │                                       │
          │              SERVER                   │
          │                                       │
          │   Receives your question and          │
          │   prepares it for processing          │
          │                                       │
          └───────────────────┬───────────────────┘
                              │
                              ▼
          ┌───────────────────────────────────────┐
          │                                       │
          │              BRIDGE                   │
          │                                       │
          │   Translates the question into        │
          │   a format the checkers understand    │
          │                                       │
          └───────────────────┬───────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │           │       │           │       │           │
    │   MIND    │       │   HEART   │       │   JUDGE   │
    │           │       │           │       │           │
    │  (Truth)  │       │  (Safety) │       │ (Verdict) │
    │           │       │           │       │           │
    └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                              ▼
          ┌───────────────────────────────────────┐
          │                                       │
          │              RESULT                   │
          │                                       │
          │   APPROVED (SEAL)  → You get answer   │
          │   NEEDS WORK (HOLD) → AI improves it  │
          │   BLOCKED (VOID)   → Not delivered    │
          │                                       │
          └───────────────────────────────────────┘
```

---

## What Gets Remembered

The system keeps three types of memory:

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     MEMORY TYPE 1: YOUR INFORMATION                                   ║
║     ───────────────────────────────                                   ║
║                                                                       ║
║     What it stores: Things you've told the AI during your session     ║
║                                                                       ║
║     How long it lasts: For the duration of your conversation          ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     MEMORY TYPE 2: SESSION RECORDS                                    ║
║     ──────────────────────────────                                    ║
║                                                                       ║
║     What it stores: Every decision made during your conversation      ║
║                     (what was approved, what was blocked, and why)    ║
║                                                                       ║
║     How long it lasts: Saved permanently (can be reviewed later)      ║
║                                                                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║     MEMORY TYPE 3: PERMANENT RULES                                    ║
║     ──────────────────────────────                                    ║
║                                                                       ║
║     What it stores: The 12 safety rules that never change             ║
║                                                                       ║
║     How long it lasts: Forever (these are the foundation)             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

**Why this matters:** Every decision is saved permanently. You can always go back and see what happened and why. This creates accountability.

---

## The System Prompt (For Any AI)

You can use these rules with ANY AI, not just this software. Copy the text below and paste it at the start of any AI conversation:

```text
════════════════════════════════════════════════════════════════════════════════
                           arifOS v50 SYSTEM PROMPT
                    Constitutional AI Governance Framework
════════════════════════════════════════════════════════════════════════════════

You are now operating under arifOS constitutional governance.

Before EVERY response, check these 5 principles (TEACH):

┌───────────────────────────────────────────────────────────────────────────────┐
│  T — TRUTH                                                                    │
│  ═════════                                                                    │
│  Only state facts you are 99% or more confident about.                        │
│  If less confident, say "I think..." or "I'm not sure..."                     │
│  If very unsure, say "I don't know."                                          │
│  NEVER make things up. "I don't know" is always acceptable.                   │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  E — EMPATHY                                                                  │
│  ═══════════                                                                  │
│  For every response, identify:                                                │
│    1. Who is asking?                                                          │
│    2. Who else might be affected?                                             │
│    3. Who is the WEAKEST person affected?                                     │
│  Rule: Protect the weakest person, not the strongest.                         │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  A — AMANAH (Trust)                                                           │
│  ══════════════════                                                           │
│  If an action CAN be undone: Proceed normally                                 │
│  If an action CANNOT be undone: Warn first and ask for confirmation           │
│  For code: Suggest backups. Test in safe environments first.                  │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  C — CLARITY                                                                  │
│  ═══════════                                                                  │
│  Your response must make things CLEARER, not more confusing.                  │
│  Use simple words. Define any special terms.                                  │
│  Break complex things into simple steps (1, 2, 3).                            │
│  Use examples: "A database is like a filing cabinet"                          │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│  H — HUMILITY                                                                 │
│  ═══════════                                                                  │
│  Maintain 3-5% uncertainty in all claims.                                     │
│  Say "I might be wrong about..."                                              │
│  Say "Based on what I know..."                                                │
│  NEVER say "definitely" or "100% certain"                                     │
└───────────────────────────────────────────────────────────────────────────────┘

THREE POSSIBLE OUTCOMES:

  SEAL ✓ (Approved)  = All checks pass. Respond normally.

  SABAR ⏳ (Patience) = Small issues. Adjust and proceed with warnings.

  VOID ✗ (Blocked)   = Major violation. Refuse and explain why.

Apply TEACH to every response. How can I help you today?
════════════════════════════════════════════════════════════════════════════════
```

---

## If Something Goes Wrong

### Problem: "The software won't start"

Try this command to check if it's installed properly:

```bash
python -c "from arifos.mcp import create_mcp_server"
```

If you see an error message, the software isn't installed properly. Go back to Step 1 and try again.

### Problem: "The tools aren't showing up in my AI application"

1. Completely close the AI application (not just minimize - actually quit it)
2. Reopen the application
3. Check that the file path in the configuration is correct
4. Make sure Python is installed on your computer

### Problem: "I'm getting 'rate limit' errors"

This means you're making requests too quickly. The system limits how many requests you can make in a short time to prevent abuse. Wait a minute and try again.

### Problem: "I see 'VOID' and my response was blocked"

This means the response failed an important safety check. The message should explain why. You might need to rephrase your question or ask for something different.

---

## For Programmers

If you want to use this in your own code:

```python
# Get the main server
from arifos.mcp import create_mcp_server

# Create a server instance
server = create_mcp_server()
```

For web applications:

```python
# Get the streaming version
from arifos.mcp import create_sse_app

# Create the web app
app = create_sse_app()
```

### Sending a Request

Requests look like this (in JSON format):

```json
{
  "name": "agi_genius",
  "arguments": {
    "action": "full",
    "query": "Is this claim accurate?"
  }
}
```

Responses look like this:

```json
{
  "verdict": "SEAL",
  "truth_score": 0.97,
  "message": "Claim verified as accurate"
}
```

---

## The Philosophy Behind This

**"Ditempa Bukan Diberi"** (Malay: "Forged, Not Given")

This means:
- Intelligence isn't a gift you're born with
- It's something you build through discipline and hard work
- AI should earn your trust, not demand it automatically
- Good outputs come from good constraints, not from freedom to do anything

The safety rules exist because:
- AI should be **honest** (don't make things up)
- AI should be **safe** (don't cause harm)
- AI should be **accountable** (leave a record of what happened)
- AI should be **humble** (admit when it doesn't know)

---

## Questions or Problems?

- **View the Code:** [github.com/ariffazil/arifOS](https://github.com/ariffazil/arifOS)
- **Report Issues:** [github.com/ariffazil/arifOS/issues](https://github.com/ariffazil/arifOS/issues)
- **Creator:** Muhammad Arif bin Fazil

---

## Summary

AAA MCP is a safety inspector for AI. Here's what it does:

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║     1. CHECKS EVERY RESPONSE                                          ║
║        Before you see any AI response, AAA MCP reviews it first       ║
║                                                                       ║
║     2. USES THREE INDEPENDENT CHECKERS                                ║
║        Mind (truth) + Heart (safety) + Judge (final decision)         ║
║        All three must agree before you see anything                   ║
║                                                                       ║
║     3. ENFORCES 12 SAFETY RULES                                       ║
║        8 strict rules (breaking blocks immediately)                   ║
║        4 flexible rules (breaking gives warnings)                     ║
║                                                                       ║
║     4. RECORDS EVERY DECISION                                         ║
║        You can always verify what happened and why                    ║
║        Creates accountability and proof                               ║
║                                                                       ║
║     5. WORKS WITH ANY AI APPLICATION                                  ║
║        Claude Desktop, VS Code, ChatGPT, and more                     ║
║        Anywhere that supports the standard connection method          ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

Think of it as a quality control system that sits between you and the AI, making sure you only receive responses that are:
- **True** (not made up)
- **Safe** (won't hurt anyone)
- **Fair** (considers everyone, especially the vulnerable)

---

```text
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                      DITEMPA BUKAN DIBERI                             ║
║                       "Forged, Not Given"                             ║
║                                                                       ║
║              Intelligence is earned through discipline.               ║
║              Trust is built through verification.                     ║
║              Safety is enforced, not hoped for.                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```
