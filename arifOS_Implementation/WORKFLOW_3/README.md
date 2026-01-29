# Level 3: WORKFLOW - Documented Sequences

**Effectiveness:** ★★★☆☆☆ (70% Coverage)
**Complexity:** Low-Medium
**Cost:** $0.50-1.00 per 1K operations
**Best For:** Process documentation, SOPs, human-in-loop systems

---

## 🎯 Overview

**WORKFLOW level** documents the complete 000-999 metabolic loop as step-by-step procedures that AI *should* follow. This is what was created in [.claude/workflows/](../../.claude/workflows/).

### Key Characteristics

✓ **Sequential guidance** - Clear order of operations
✓ **Decision trees** - Conditional logic documented
✓ **Tool integration** - References actual tools (Glob, Grep, Read, Edit)
✓ **Human-auditable** - Clear paper trail
✓ **Self-documenting** - Workflow IS the documentation
⚠️ **Voluntary compliance** - AI chooses to follow
✗ **No programmatic enforcement** - Relies on AI discipline
✗ **No automatic state management** - Manual context passing

---

## 📁 Structure

\`\`\`
.claude/workflows/          (or .agent/workflows/)
├── README.md              # Workflow system overview
├── 000_SESSION_INIT.md    # Ignition protocol
├── 111_INTENT.md          # Intent clarification
├── 333_CONTEXT.md         # Context mapping
├── 555_SAFETY.md          # Safety validation
├── 777_IMPLEMENT.md       # Code synthesis
└── 888_COMMIT.md          # Git commit protocol
\`\`\`

---

## 📝 Workflow Template Example

### 333_CONTEXT.md (Abbreviated)

\`\`\`markdown
# 333_CONTEXT: The Mapping Protocol

**Purpose:** Context discovery, dependency mapping, boundary identification
**Input:** Parsed intent from 111_INTENT
**Output:** Context map with uncertainty bounds

## Constitutional Floors

- F7 (Humility): Ω₀ ∈ [0.03, 0.05]
- F10 (Ontology): Only verified symbols
- F2 (Truth): All facts verified

## Workflow Steps

### 1. Target Identification

**Tools:** Glob, Grep

\`\`\`bash
# Find relevant files by pattern
Glob "**/*{target_keywords}*.{ts,tsx,js,jsx}"

# Search for existing implementations
Grep "{feature_name}" --output_mode files_with_matches
\`\`\`

**Output:** List of candidate files

### 2. Dependency Analysis

**Tools:** Read

\`\`\`typescript
For each candidate file:
  - Read file (limit=100 lines for large files)
  - Extract imports
  - Extract exports
  - Estimate complexity

Build dependency graph:
  nodes = files
  edges = import relationships
\`\`\`

**Output:** Dependency graph

### 3. Boundary Classification

Categorize every node:

| Category | Definition | Action |
|----------|------------|--------|
| Internal | Local files under control | Full access |
| External | npm packages | API surface only |
| Missing | Imported but not found | RED FLAG |
| Unstable | High complexity, TODOs | CAUTION |

### 4. Uncertainty Calculation (F7)

\`\`\`
Ω₀ = (α × |Unknown| + β × |Unstable|) / (|Known| + |Unknown|)

Target: 0.03 ≤ Ω₀ ≤ 0.05
\`\`\`

**Constitutional Check:**

\`\`\`
IF Ω₀ > 0.10:
  HALT("Map too foggy. Research required.")
ELIF Ω₀ < 0.03:
  WARN("Possible overconfidence. Verify edge cases.")
ELSE:
  PROCEED
\`\`\`

### 5. Vocabulary Extraction (F10)

Extract allowed symbols for F10 enforcement:

\`\`\`typescript
vocabulary = {
  functions: Set<string>,
  classes: Set<string>,
  types: Set<string>,
  packages: Set<string>
}
\`\`\`

**Usage:** 777_IMPLEMENT can ONLY use symbols from this vocabulary

### 6. Output Format

\`\`\`json
{
  "context_map": {
    "files": [...],
    "dependencies": {...},
    "boundaries": {
      "internal": [...],
      "external": [...],
      "missing": [...],
      "unstable": [...]
    }
  },
  "omega_0": 0.042,
  "vocabulary": {
    "functions": ["useTheme", "createTheme", ...],
    "classes": [...],
    "types": [...]
  },
  "floors_validated": ["F7", "F10", "F2"]
}
\`\`\`

## Decision Tree

\`\`\`
┌─────────────────┐
│ Start Mapping   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      NO     ┌──────────────────┐
│ Files found?    ├─────────────>│ HALT: No targets │
└────────┬────────┘              └──────────────────┘
         │ YES
         ▼
┌─────────────────┐
│ Build graph     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate Ω₀    │
└────────┬────────┘
         │
         ▼
    Ω₀ > 0.10? ───YES──> HALT (Too foggy)
         │
         │ NO
         ▼
    Ω₀ < 0.03? ───YES──> WARN (Overconfident)
         │
         │ NO (0.03-0.05)
         ▼
┌─────────────────┐
│ Extract vocab   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SEAL & proceed  │
│ to 777_IMPLEMENT│
└─────────────────┘
\`\`\`

## Troubleshooting

**Case 1: Missing Dependencies**
\`\`\`
Issue: import './utils' not found
Action:
  1. Glob "**/utils.*"
  2. If still not found, HALT
  3. User must clarify or provide file
\`\`\`

**Case 2: Circular Dependencies**
\`\`\`
Issue: A imports B imports A
Analysis: Ω₀ will be high (graph unstable)
Action: Mark module as "Volatile", recommend refactor
\`\`\`

---

**Next Stage:** [777_IMPLEMENT](./777_IMPLEMENT.md)
\`\`\`

---

## 💡 Key Workflow Patterns

### Pattern 1: Tool Call Sequences

\`\`\`markdown
## Step 3: Search for Theme System

**Sequential tool calls:**

1. \`Glob "**/*theme*.{ts,tsx}"\`
2. \`Grep "createTheme|ThemeProvider" --output_mode files_with_matches\`
3. For each file: \`Read {file_path}\`

**Parallel tool calls (when possible):**

\`\`\`python
# Call these in parallel (independent)
results = await asyncio.gather(
    Glob("**/*theme*.ts"),
    Grep("ThemeProvider", output_mode="files"),
    Read("package.json")  # Check existing theme libs
)
\`\`\`
\`\`\`

### Pattern 2: Constitutional Checkpoints

\`\`\`markdown
## Floor Validation Checkpoint (F2: Truth)

After extracting facts:

\`\`\`
FOR EACH fact in extracted_facts:
  IF NOT verify_against_codebase(fact):
    ASK user for clarification
    HALT until clarified
\`\`\`

**Example:**
\`\`\`
User: "Update the auth.py file"
Verification: Glob "**/*auth*.py"
Result: NOT FOUND

Action:
  AskUserQuestion({
    question: "File 'auth.py' not found. Did you mean 'authentication.py'?",
    options: [
      {label: "authentication.py", description: "Main auth module"},
      {label: "auth_utils.py", description: "Auth utility functions"}
    ]
  })
\`\`\`
\`\`\`

### Pattern 3: Conditional Routing

\`\`\`markdown
## Routing Decision

\`\`\`python
def route_next_stage(complexity, intent):
    if complexity < 3:  # Simple task
        return "777_IMPLEMENT"  # Skip context mapping

    if intent.action == "EXPLAIN":
        return "333_CONTEXT"  # Need deep exploration

    if intent.targets.length > 3:  # Many files
        return "333_CONTEXT"  # Map dependencies first

    return "333_CONTEXT"  # Default: always map
\`\`\`
\`\`\`

---

## 📊 Effectiveness Analysis

### Strengths

| Aspect | Score | Notes |
|--------|-------|-------|
| **Documentation** | ★★★★★ | Self-documenting process |
| **Auditability** | ★★★★☆ | Clear paper trail |
| **Human understanding** | ★★★★★ | Easy to follow |
| **Tool integration** | ★★★★☆ | References real tools |
| **Maintenance** | ★★★★☆ | Easy to update |

### Weaknesses

| Aspect | Issue | Impact |
|--------|-------|--------|
| **Enforcement** | Voluntary only | AI can skip steps |
| **State management** | Manual | Context passed by AI memory |
| **Error handling** | Documented, not enforced | AI must implement |
| **Consistency** | Varies by AI capability | Claude >> GPT-3.5 |

---

## 💰 Cost Analysis

### Per-Operation Breakdown

| Workflow | LLM Calls | Avg Tokens | Cost |
|----------|-----------|------------|------|
| 000_SESSION_INIT | 0-1 | 200 | $0.004 |
| 111_INTENT | 1-3 | 1500 | $0.030-0.060 |
| 333_CONTEXT | 2-5 | 2000 | $0.040-0.100 |
| 777_IMPLEMENT | 3-8 | 2500 | $0.075-0.200 |
| 555_SAFETY | 1-2 | 1000 | $0.020-0.040 |
| 888_COMMIT | 1-2 | 800 | $0.016-0.032 |

**Total per task:** $0.19 - $0.44

**Why higher than PROMPT/SKILL?**
- AI reads workflow docs (extra tokens)
- Tool calls add overhead
- More interactive (clarifications)

---

## 🔄 Migration Path

### From SKILL → WORKFLOW

**Before (SKILL):**
\`\`\`
User calls: /ignition, /cognition, /atlas, /forge, /defend, /decree
(Manual sequencing, user remembers order)
\`\`\`

**After (WORKFLOW):**
\`\`\`
AI reads: .claude/workflows/README.md
Follows: 000 → 111 → 333 → 777 → 555 → 888 (documented sequence)
Enforces: Decision trees, checkpoints, floor validations
\`\`\`

**Key Improvement:** Process knowledge embedded in documentation

---

### To TOOL Level

**Next Evolution:**
\`\`\`
Workflow docs → MCP tool implementations
\`\`\`

**Example:**
\`\`\`python
# From: .claude/workflows/333_CONTEXT.md (documentation)
# To: mcp_tools/atlas.py (code)

@mcp.tool()
async def _atlas_(intent: dict, session_id: str):
    """ENFORCED implementation of 333_CONTEXT workflow"""
    # ... actual code that MUST execute ...
\`\`\`

---

## 📚 Real-World Examples

**Current Implementations:**
- [.claude/workflows/](../../.claude/workflows/) - Claude Code adaptation
- [.agent/workflows/](../../.agent/workflows/) - arifOS global skills

**Usage:**
- Claude Code reads workflows when handling complex tasks
- Workflows guide implementation decisions
- Provides constitutional compliance framework

---

## 🎯 Best Practices

### 1. Workflow Writing

✓ **Clear step numbers** - Easy to follow
✓ **Tool specifications** - Exact commands
✓ **Decision trees** - Conditional logic visible
✓ **Examples** - Concrete cases
✓ **Floor checkpoints** - Constitutional validation

### 2. Maintenance

✓ **Version control** - Track changes
✓ **Update regularly** - As tools evolve
✓ **Test with AI** - Verify AI can follow
✓ **User feedback** - Improve clarity

### 3. Integration

✓ **Reference from prompts** - "See .claude/workflows/"
✓ **Link workflows** - Cross-references between stages
✓ **Provide context** - When to use each workflow
✓ **Document exceptions** - When to skip stages

---

## 📈 Adoption Strategy

### Phase 1: Documentation (Current)
Create workflow docs for team reference

### Phase 2: AI Integration
Train AI to read and follow workflows

### Phase 3: Validation
Add checklist validation (AI self-checks)

### Phase 4: Automation
Migrate to TOOL level (programmatic enforcement)

---

**Level:** WORKFLOW (3/6)
**Effectiveness:** 70%
**Status:** PRODUCTION (Claude Code)
**Next Level:** [4_TOOL](../4_TOOL/) for enforcement

*Ditempa Bukan Diberi.* 📋
