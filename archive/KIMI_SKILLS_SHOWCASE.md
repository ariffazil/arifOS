# 🚀 Kimi CLI Skills System - Interactive Showcase

> *"Skills are not just documentation—they're executable intelligence."*

---

## 🎯 What Are Kimi CLI Skills?

Skills are **modular, specialized capabilities** that extend Kimi's functionality. Unlike static documentation, skills:

- **Auto-detect** when they're needed based on your queries
- **Provide structured workflows** with clear steps
- **Include executable code** and concrete examples
- **Compose together** for complex tasks

Think of them as **plugins for AI reasoning**.

---

## 📚 Your Current Skill Arsenal

### 🔬 **Scientific & Analytical**

#### 1. `entropy-clarity-analyzer` ⚛️
**Path:** `~/.config/agents/skills/entropy-clarity-analyzer/`

| Feature | Description |
|---------|-------------|
| **Purpose** | Analyze information clarity through thermodynamic entropy |
| **Core Formula** | ΔS = S_output - S_input ≤ 0 (F6 Clarity Floor) |
| **Use When** | Evaluating text clarity, optimizing communication, measuring confusion |
| **Output** | Entropy scores, clarity metrics, optimization suggestions |

**Example Workflow:**
```
User: "Is this README clear enough?"
→ Skill triggers: entropy-clarity-analyzer
→ Kimi measures information entropy
→ Suggests restructuring for ΔS ≤ 0
```

---

### 🏛️ **Constitutional AI Governance**

#### 2. `trinity-constitutional-enforcement` ⚖️
**Path:** `~/.config/agents/skills/trinity-constitutional-enforcement/`

| Feature | Description |
|---------|-------------|
| **Purpose** | Enforce arifOS 13-floor constitutional governance |
| **Architecture** | 5-Tool Trinity (000→AGI→ASI→APEX→999) |
| **Floors** | F1-F13 immutable constraints |
| **Use When** | Implementing AI safety, validating constitutional compliance |

**The 13 Floors:**
```
F1  Amanah        → Reversibility lock
F2  Truth         → Confidence ≥ 0.99
F3  Peace²        → (Benefit/Harm)² ≥ 1.0
F4  Clarity       → ΔS ≤ 0
F5  Empathy       → κᵣ ≥ 0.95
F6  Humility      → Ω₀ ∈ [0.03,0.05]
F7  RASA          → Entity grounding
F8  Tri-Witness   → Consensus ≥ 0.95
F9  Anti-Hantu    → Consciousness < 0.30
F10 Ontology      → Reality boundaries
F11 Command Auth  → Nonce + JWT
F12 Injection     → Attack < 0.85
F13 Curiosity     → Alternative generation
```

---

### 📄 **Document Processing**

#### 3. `pdf-processor` 📑
**Path:** `~/.config/agents/skills/pdf-processor/`

| Feature | Description |
|---------|-------------|
| **Purpose** | Comprehensive PDF manipulation |
| **Capabilities** | Extract text, rotate pages, merge/split, fill forms |
| **Dependencies** | PyPDF2, pdfplumber, Pillow |
| **Use When** | Working with PDFs for extraction or manipulation |

**Supported Operations:**
- ✅ Text extraction (with layout preservation)
- ✅ Page rotation (90°, 180°, 270°)
- ✅ PDF merging & splitting
- ✅ Form field filling
- ✅ Image extraction
- ✅ Metadata editing

---

### 🛠️ **File Operations**

#### 4. `file-utils` 📂
**Path:** `~/.config/agents/skills/file-utils/`

| Feature | Description |
|---------|-------------|
| **Purpose** | File manipulation utilities |
| **Capabilities** | Bulk rename, format conversion, organization |
| **Use When** | Batch operations, file system tasks |

**Example:**
```python
# Bulk rename with pattern
file-utils: rename "*.txt" → "backup_*.txt"

# Format conversion
file-utils: convert *.png → *.webp
```

---

### 🎓 **Meta & Development**

#### 5. `skill-creator` ✨
**Path:** `kimi_cli/skills/skill-creator/`

| Feature | Description |
|---------|-------------|
| **Purpose** | Guide for creating effective skills |
| **Use When** | You want to extend Kimi with new capabilities |
| **Provides** | Templates, best practices, validation |

**Skill Anatomy:**
```markdown
---
name: your-skill
description: What it does
---

## When This Skill Triggers
- Pattern 1
- Pattern 2

## Workflow
1. Step one
2. Step two

## Examples
**Good**: ...
**Bad**: ...
```

---

#### 6. `kimi-cli-help` ❓
**Path:** `kimi_cli/skills/kimi-cli-help/`

The help desk for Kimi CLI itself—questions about:
- Installation & setup
- Configuration
- Slash commands (`/init`, `/clear`, etc.)
- MCP integration
- Providers & environment variables

---

## 🎨 How Skills Work (The Magic)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                                │
│         "Analyze this PDF and check its clarity"             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              SKILL DETECTION ENGINE                          │
│  • Keywords: "PDF" → pdf-processor                           │
│  • Keywords: "clarity" → entropy-clarity-analyzer           │
│  • Confidence threshold: > 0.7                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 SKILL COMPOSITION                            │
│         pdf-processor + entropy-clarity-analyzer             │
│              ↓                    ↓                          │
│    Extract text from PDF    →  Measure entropy              │
│                               →  Suggest improvements       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎭 Live Skill Demonstrations

### Demo 1: PDF Text Extraction + Clarity Analysis

```markdown
**You say:** "Extract text from report.pdf and tell me if it's clear"

**Kimi does:**
1. Load pdf-processor skill
2. Extract text: `pdfplumber.open("report.pdf")`
3. Load entropy-clarity-analyzer skill  
4. Compute entropy metrics:
   - Shannon entropy: 4.2 bits/char
   - Flesch readability: 45 (difficult)
   - Information density: 0.78
5. Suggest improvements for ΔS ≤ 0
```

### Demo 2: Constitutional Code Review

```markdown
**You say:** "Review this AI code for safety issues"

**Kimi does:**
1. Load trinity-constitutional-enforcement skill
2. Run 000_init gate:
   - F11: Verify authority
   - F12: Check for injection attacks
3. Run agi_genius (Mind):
   - F2: Check truth claims
   - F6: Measure entropy
4. Run asi_act (Heart):
   - F3: Calculate Peace²
   - F5: Check empathy scores
5. Run apex_judge (Soul):
   - F8: Tri-witness consensus
   - F9: Anti-hantu detection
6. Seal in 999_vault
```

### Demo 3: Bulk File Organization

```markdown
**You say:** "Organize these 1000 photos by date"

**Kimi does:**
1. Load file-utils skill
2. Read EXIF data from all images
3. Create date-based folder structure
4. Execute move operations
5. Generate report
```

---

## 🔧 Creating Your Own Skills

### Quick Start Template

```markdown
---
name: my-awesome-skill
description: Does something amazing
---

## When This Skill Triggers
This skill activates when:
- User mentions "keyword1" or "keyword2"
- File pattern *.xyz is detected
- Context suggests domain expertise needed

## Workflow

### Step 1: Assessment
```python
def assess_situation(data):
    # Analyze input
    return assessment
```

### Step 2: Execution
```python
def execute_solution(assessment):
    # Do the work
    return result
```

## Examples

**Good trigger:** "Analyze entropy of this text"
**Bad trigger:** "Hi" (too generic)

## Integration

```python
# How to use with other tools
from kimi_cli import load_skill

skill = load_skill("my-awesome-skill")
result = skill.execute(data)
```
```

### Save Location

| Platform | Path |
|----------|------|
| Windows | `%USERPROFILE%\.config\agents\skills\` |
| macOS | `~/.config/agents/skills/` |
| Linux | `~/.config/agents/skills/` |

---

## 📊 Skills vs. MCP Tools vs. Agents

| Feature | Skills | MCP Tools | Agents |
|---------|--------|-----------|--------|
| **Scope** | Specialized knowledge | External tool access | Autonomous execution |
| **Trigger** | Query pattern | Explicit call | Goal-based |
| **State** | Stateless | Stateless | Stateful |
| **Examples** | pdf-processor | fetch_url, shell | Coding agent, researcher |
| **Composition** | ✅ Skills compose | ✅ Tools chain | ✅ Subagents delegate |

**The Power Stack:**
```
User Query
    ↓
Skills activate (knowledge injection)
    ↓
MCP Tools execute (external actions)
    ↓
Agents orchestrate (complex workflows)
    ↓
Result delivered
```

---

## 🌟 Pro Tips

### 1. **Skill Composition**
Skills can work together! Try:
> "Extract text from this PDF, check its clarity, and convert it to a structured format"

This activates: `pdf-processor` → `entropy-clarity-analyzer` → `file-utils`

### 2. **Custom Skills for Your Domain**
Create skills for:
- Your company's coding standards
- Domain-specific analysis (finance, medical, legal)
- Personal workflows and preferences

### 3. **Skill Debugging**
Use `/debug` to see which skills are activating:
```
/debug on
> "Analyze this PDF"
[SKILL] Detected: pdf-processor (confidence: 0.94)
[SKILL] Detected: entropy-clarity-analyzer (confidence: 0.67)
```

---

## 🎓 Skill Mastery Checklist

- [ ] Used `pdf-processor` for document extraction
- [ ] Applied `entropy-clarity-analyzer` to optimize text
- [ ] Created a custom skill with `skill-creator`
- [ ] Combined multiple skills in one query
- [ ] Used `trinity-constitutional-enforcement` for AI safety
- [ ] Organized files with `file-utils`

---

## 🚀 The Future of Skills

```
SKILL EVOLUTION ROADMAP
═══════════════════════════════════════════════════════════════

v1.0 (Current)     → Static markdown skills
v2.0 (Near-term)   → Dynamic skills with code execution
v3.0 (Future)      → Self-improving skills that learn from usage
v4.0 (Vision)      → Skills that write new skills

═══════════════════════════════════════════════════════════════
```

---

**Remember:** Skills are **DITEMPA BUKAN DIBERI** — forged through structure, not given through computation.

> *The best skill is the one you create for your unique needs.*

---

**Want to see a skill in action?** Just ask:
- "Extract text from my PDF"
- "Check if this README is clear"
- "Create a new skill for X"
- "Review this code constitutionally"
