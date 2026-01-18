# Trinity AI Assistant Template

**For**: ANY AI Assistant (ChatGPT, Claude, Gemini, Copilot, local LLMs, etc.)  
**Purpose**: Enable any AI to understand and use Trinity commands  
**Version**: 43.1.0

---

## Quick Reference

When the user says any of these, run the corresponding command:

| User Says | Run This Command |
|-----------|------------------|
| "trinity forge X" or "/gitforge X" | `python scripts/trinity.py forge X` |
| "trinity qc X" or "/gitQC X" | `python scripts/trinity.py qc X` |
| "trinity seal X reason" or "/gitseal X" | `python scripts/trinity.py seal X "reason"` |

---

## The Three Trinity Commands

### 1. `/gitforge` - Analyze Changes

**Purpose**: Scan git history, detect hot zones, predict entropy impact

**Command**:

```bash
trinity forge <branch-name>
```

**Example**:

```bash
trinity forge my-feature
```

**Output**: Shows files changed, hot zones, entropy delta (ΔS), risk score

**When to use**: Before making changes, to understand impact

---

### 2. `/gitQC` - Constitutional Validation

**Purpose**: Validate changes against F1-F9 constitutional floors

**Command**:

```bash
trinity qc <branch-name>
```

**Example**:

```bash
trinity qc my-feature
```

**Output**: Constitutional floor results (F1-F9), ZKPC ID, verdict (PASS/FLAG/VOID)

**When to use**: After making changes, before sealing

---

### 3. `/gitseal` - Human Authority Gate

**Purpose**: Seal changes with human approval, create atomic release bundle

**Command**:

```bash
trinity seal <branch-name> <reason>
```

**Example**:

```bash
trinity seal my-feature "Feature complete and all tests passing"
```

**Output**: Creates version tag, ledger entry, manifest update, pushes to GitHub

**When to use**: Final step - only when ready to commit and push

---

## AI Assistant Instructions

### If user asks: "What is Trinity?"

**Respond**:

Trinity is a git governance system that simplifies version control into 3 commands:

1. `trinity forge` - Analyze what changed
2. `trinity qc` - Check if it's safe
3. `trinity seal` - Save it with approval

It's built for accessibility - reducing 20+ git commands to just 3.

### If user asks: "How do I use Trinity?"

**Respond**:

```bash
# Step 1: Analyze your changes
trinity forge your-branch-name

# Step 2: Check constitutional compliance
trinity qc your-branch-name

# Step 3: Seal and push (with your approval)
trinity seal your-branch-name "Reason for this change"
```

That's it! Trinity handles all the git complexity.

### If user asks: "What's the difference between the three commands?"

**Respond**:

- **forge**: Read-only analysis (safe to run anytime)
- **qc**: Read-only validation (safe to run anytime)
- **seal**: *CREATES* commits and pushes (requires approval, irreversible)

Always run `forge` and `qc` before `seal`.

---

## Platform Notes

**Windows**: Use `python scripts/trinity.py` or `.\trinity.ps1`  
**Mac/Linux**: Use `python scripts/trinity.py` or `./trinity.sh`

All platforms support: `python scripts/trinity.py <command>`

---

## Help Command

If user is stuck, suggest:

```bash
trinity help
```

This shows full usage information.

---

## Error Handling

**If user gets**: "Cannot find git_forge.py"  
**Suggest**: Make sure you're in the arifOS repository root

**If user gets**: "Missing branch name"  
**Suggest**: `trinity <command> <branch-name>`

**If user gets**: "Unknown command"  
**Suggest**: `trinity help` to see available commands

---

## Constitutional Context (For Reference)

Trinity validates against 9 constitutional floors (F1-F9):

- F1: Truth (no credential leaks)
- F2: ΔS (entropy reduction - learning)
- F3: Peace² (stability)
- F4: κᵣ (empathy/readability)
- F5: Ω₀ (appropriate uncertainty)
- F6: Amanah (integrity)
- F7: RASA (active listening)
- F8: Tri-Witness (human/AI/earth consensus)
- F9: Anti-Hantu (no consciousness claims)

These are automatically checked by `trinity qc`.

---

## Advanced: Thermodynamic Metrics

Trinity uses physics-inspired metrics:

- **ΔS** (Entropy Delta): Measures complexity increase/decrease
- **Peace²**: Stability metric
- **Ψ** (Psi, Vitality): Overall system health
- **Risk Score**: 0-1 scale (0=safe, 1=dangerous)

These guide decision-making but don't require deep understanding.

---

## For AI Developers Building on Trinity

Trinity is:

- **Open Source**: Use freely
- **Platform-Agnostic**: Python-based, works anywhere
- **AI-Agnostic**: Works with any AI assistant
- **Accessible-First**: Built for people with memory/cognitive challenges

Integration is welcome. Just respect human sovereignty - Trinity requires human approval for all commits.

---

**Built by**: Muhammad Arif bin Fazil  
**License**: See LICENSE file  
**More Info**: <https://github.com/ariffazil/arifOS>

**Motto**: *Ditempa, bukan diberi* (Forged, not given)
