# L2_GOVERNANCE — Portable System Prompts

**Layer:** L2 (User-Facing)
**Purpose:** Simplified, copy-paste governance prompts for ANY LLM — THE HERO LAYER
**License:** CC-BY-4.0 (Governance is portable)

---

## ⚠️ IMPORTANT: This is NOT the Authoritative Source

**L2_GOVERNANCE contains user-friendly summaries, NOT authoritative specs.**

### Authoritative Sources (PRIMARY)

| Source | Purpose | Location |
|--------|---------|----------|
| **Specs (JSON/YAML)** | Constitutional thresholds, metrics, formulas | [`spec/v44/`](../spec/v44/) |
| **Canon (Markdown)** | Constitutional law, philosophy, explanations | [`L1_THEORY/canon/`](../L1_THEORY/canon/) |
| **Code (Python)** | Runtime enforcement, floor detectors | [`arifos_core/`](../arifos_core/) |

### This Directory (DERIVATIVE)

L2_GOVERNANCE provides **simplified, user-facing prompts** derived from the authoritative sources above. These are intentionally condensed for copy-paste into ChatGPT, Claude, Cursor, etc.

**Maintenance:** When `spec/v44/` or `L1_THEORY/canon/` change, these prompts should be manually updated to reflect changes.

---

## What Lives Here

| Directory | Contents | Status |
|-----------|----------|--------|
| `universal/` | Simplified system prompts (YAML, JSON, MD) | ✓ ACTIVE |
| `templates/` | Minimal governance templates for quick adoption | ✓ ACTIVE |

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

## Relationship to Authoritative Sources

```
spec/v44/ (PRIMARY)
    ↓ derives/simplifies
L2_GOVERNANCE (DERIVATIVE)
    ↓ copy-paste by users
ChatGPT/Claude/Cursor/etc.

L1_THEORY/canon/ (PRIMARY - philosophical)
    ↓ explains/justifies
spec/v44/ (PRIMARY - executable)
    ↓ enforced by
arifos_core/ (RUNTIME)
```

**Rule:** L2_GOVERNANCE is NOT imported by code. It's for humans to copy-paste into LLMs.

---

## Key Files

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `universal/system_prompt_v42.yaml` | THE HERO — Simplified governance YAML | 204 | spec/v44/*.json |
| `universal/system_prompt_v42.json` | JSON format for APIs | ~200 | spec/v44/*.json |
| `universal/system_prompt_v42.md` | Markdown format for docs | ~200 | spec/v44/*.json |
| `templates/minimal_governance.yaml` | 20-line minimal version | 20 | Condensed from above |

**Note:** IDE-specific configs (AGENTS.md, CLAUDE.md) are now at repository root, not in L2_GOVERNANCE.

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

1. Cursor rules are at repository root (not in L2_GOVERNANCE)
2. See [AGENTS.md](../AGENTS.md) and [CLAUDE.md](../CLAUDE.md)

---

**DITEMPA BUKAN DIBERI** — Forged, not given. Governance is portable.
