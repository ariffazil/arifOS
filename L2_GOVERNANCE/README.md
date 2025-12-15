# L2_GOVERNANCE — Portable Constitution

**Layer:** L2
**Purpose:** Universal system prompts and IDE configurations — THE HERO LAYER
**License:** CC-BY-4.0 (Governance is portable)

---

## What Lives Here

| Directory | Contents |
|-----------|----------|
| `universal/` | THE HERO — Copy-paste system prompts (YAML, JSON, MD) |
| `ide_configs/` | IDE-specific governance files (AGENTS.md, CLAUDE.md, CURSOR.md) |
| `validation/` | Red-team prompts and adversarial testing |
| `templates/` | Minimal governance templates for quick adoption |

---

## The Hero: Universal System Prompt

**File:** `universal/system_prompt_v42.yaml`

This is the **viral layer** — anyone can copy-paste 80 lines of YAML into ANY LLM and get governed AI instantly.

**Supported:**
- ChatGPT Custom Instructions
- Claude Projects
- Cursor Rules
- VS Code Copilot
- Gemini
- ANY LLM with system prompt support

---

## Dependency Rules

```
L2_GOVERNANCE ← L3_KERNEL reads governance rules
              ← IDE integrations import from here
              → Reads law from L1_THEORY
              → NEVER imports from higher layers
```

---

## Key Files

| File | Purpose |
|------|---------|
| `universal/system_prompt_v42.yaml` | THE HERO — Full governance YAML |
| `universal/system_prompt_v42.json` | JSON format for APIs |
| `universal/system_prompt_v42.md` | Markdown format for docs |
| `ide_configs/AGENTS.md` | Multi-agent governance |
| `ide_configs/CLAUDE.md` | Claude Code instructions |
| `ide_configs/CURSOR.md` | Cursor IDE rules |
| `ide_configs/COPILOT.md` | GitHub Copilot instructions |
| `templates/minimal_governance.yaml` | 20-line minimal version |

---

## Usage

### For ChatGPT

1. Go to Settings → Custom Instructions
2. Copy contents of `universal/system_prompt_v42.yaml`
3. Paste into "How would you like ChatGPT to respond?"
4. Done. Your ChatGPT is now constitutionally governed.

### For Claude Projects

1. Create a new Project
2. Add `universal/system_prompt_v42.md` to Project Knowledge
3. Done.

### For Cursor

1. Copy `ide_configs/CURSOR.md` to `.cursor/rules.md`
2. Done.

---

**DITEMPA BUKAN DIBERI** — Forged, not given. Governance is portable.
