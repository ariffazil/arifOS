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
| **Specs (JSON/YAML)** | Constitutional thresholds, metrics, formulas | [`spec/v45/`](../spec/v45/) |
| **Canon (Markdown)** | Constitutional law, philosophy, explanations | [`L1_THEORY/canon/`](../L1_THEORY/canon/) |
| **Code (Python)** | Runtime enforcement, floor detectors | [`arifos_core/`](../arifos_core/) |

### This Directory (DERIVATIVE)

L2_GOVERNANCE provides **simplified, user-facing prompts** derived from the authoritative sources above. These are intentionally condensed for copy-paste into ChatGPT, Claude, Cursor, etc.

**Maintenance:** When `spec/v53/` or `codebase/` change, these prompts should be manually updated to reflect changes.

[**👉 LATEST SPECIFICATION (v53.1.0)**](../spec/v53/AAA_MCP_v53.1.0_SPEC.md)

---

## What Lives Here

| Directory | Contents | Status |
|-----------|----------|--------|
| `universal/` | Governance packs + Communication Law enforcement (YAML/JSON) | ✓ ACTIVE |
| `core/` | Constitutional floors, GENIUS metrics, verdict logic (YAML/JSON) | ✓ ACTIVE |
| `enforcement/` | Red patterns, session physics (YAML/JSON) | ✓ ACTIVE |
| `federation/` | W@W organs, Anti-Hantu patterns (YAML/JSON) | ✓ ACTIVE |
| `memory/` | Cooling Ledger, Phoenix-72, SCAR lifecycle (YAML/JSON) | ✓ ACTIVE |
| `pipeline/` | 000→999 stages, memory routing (YAML/JSON) | ✓ ACTIVE |
| `integration/` | Platform-specific configs (ChatGPT, Claude, Cursor, VS Code) | ✓ ACTIVE |
| `templates/` | Minimal governance templates for quick adoption | ✓ ACTIVE |

Other folders in `L2_GOVERNANCE/` are reserved module slots; keep them YAML/JSON-only (plus `README.md` if needed).

---

## The Hero: Universal System Prompt

**File:** `universal/system_prompt_v45.yaml`

This is the **viral layer** — anyone can copy-paste 80 lines of YAML into ANY LLM and get governed AI instantly.

**Supported:**
- ChatGPT Custom Instructions
- Claude Projects
- Cursor Rules
- VS Code Copilot
- Gemini
- ANY LLM with system prompt support

---

## Communication Law (v45.0)

**What Changed:** arifOS v45 introduces **Communication Law** — governance for how outputs are emitted.

**Canon:** [`L1_THEORY/canon/COMMUNICATION_LAW_v45.md`](../L1_THEORY/canon/COMMUNICATION_LAW_v45.md)
**Enforcement:** [`universal/communication_enforcement_v45.yaml`](universal/communication_enforcement_v45.yaml)

### What Users Should Expect

| Mode | Meaning | Output Format |
|------|---------|---------------|
| **SEAL** | Approved | Answer only. No metrics, no explanations. |
| **PARTIAL** | Conditional | Boundary statement + known facts + next step. |
| **SABAR** | Pause required | "I need to pause here." No internal details. |
| **HOLD-888** | Human judgment needed | Escalation notice + specific decision point. |

### What NOT to Expect

- ❌ Floor scores (F1-F9)
- ❌ GENIUS metrics (G, C_dark, Psi)
- ❌ Reasoning traces ("I think...", "After analyzing...")
- ❌ Confidence percentages ("95% confident...")
- ❌ Traffic lights (🔴/🟡/🟢)

**Why:** Governance happens internally. Outputs are clean, calm, lawful.

**Forensic Mode:** Authorized users can enable `/forensic on` to see internal metrics for audit purposes.

---

## Trinity Display Architecture (v45.0 - NEW)

arifOS v45 introduces **Trinity Display Architecture** (ASI/AGI/APEX modes) that control what users see.

**Canon:** [`L1_THEORY/canon/02_actors/010_TRINITY_ROLES_v45.md`](../L1_THEORY/canon/02_actors/010_TRINITY_ROLES_v45.md) Section 15
**Spec:** [`spec/v45/trinity_display.json`](../spec/v45/trinity_display.json)
**Enforcement:** [`universal/trinity_display_v45.yaml`](universal/trinity_display_v45.yaml)

### The Three Modes

| Mode | Symbol | Authority | What User Sees |
|------|--------|-----------|----------------|
| **ASI** (Guardian) | Ω | Public (default) | Clean response only. No metrics, no pipeline, no internals. |
| **AGI** (Architect) | Δ | Developer (`/agi` command) | Pipeline timeline + ΔΩΨ Trinity (3 numbers): Δ (Clarity), Ω (Empathy), Ψ (Vitality) |
| **APEX** (Judge) | Ψ | Auditor (`/apex` command) | Full forensic: F1-F9 floors + claim analysis + verdict reasoning |

### Authorization Cascade

```
ASI (default) → AGI (/agi) → APEX (/apex)
  ↓               ↓             ↓
Clean only    + Pipeline    + Forensic
              + ΔΩΨ         + F1-F9
                            + Claims
```

**Important:** Only human can escalate display mode. LLM cannot self-authorize.

### Example Outputs

**ASI Mode (Default):**
```
Paris is the capital of France.
```

**AGI Mode (`/agi` enabled):**
```
┌────────────────────────────────────┐
│ 🔬 PIPELINE (000→999)              │
├────────────────────────────────────┤
│ 111 SENSE  Lane=HARD    12ms      │
│ 888 JUDGE  Verdict=SEAL  7ms      │
│ 999 SEAL   Approved      2ms      │
└────────────────────────────────────┘

🧠 Δ=0.92  ❤️ Ω=0.96  ⚖️ Ψ=1.12  ✅

Paris is the capital of France.
```

**APEX Mode (`/apex` enabled):**
```
┌────────────────────────────────────┐
│ 🏛️  CONSTITUTIONAL FLOORS (F1-F9) │
├────────────────────────────────────┤
│ F1 Amanah    True       ✓         │
│ F2 Truth     1.000   ✓  [≥0.99]  │
│ F3 Tri-W     0.980   ✓  [≥0.95]  │
│ F4 ΔS        0.000   ✓  [≥0.0]   │
│ F5 Peace²    1.050   ✓  [≥1.0]   │
│ F6 κᵣ        0.980   ✓  [≥0.95]   │
│ F7 Ω₀        0.042   ✓  [0.03-0.05]│
│ F8 G         0.890   ✓  [≥0.80]   │
│ F9 C_dark    0.120   ✓  [<0.30]   │
└────────────────────────────────────┘

🧠 Δ=0.92  ❤️ Ω=0.96  ⚖️ Ψ=1.12  ✅

Paris is the capital of France.
```

**Philosophy:** "Measure everything. Show nothing (unless authorized)."

---

## Modular Prompt Architecture (v45.0 - NEW)

Instead of one-size-fits-all prompts, v45 uses **modular overlays** for different use cases.

### Architecture Layers

```
Identity Root: base_governance_v45.yaml (universal core)
   ↓
Logic Roots (context-specific overlays):
   ├── conversational_overlay_v45.yaml (empathy focus for web chat)
   ├── code_generation_overlay_v45.yaml (F1-CODE through F9-CODE for IDEs)
   └── agent_builder_overlay_v45.yaml (multi-turn tool governance for GPT Builder/Gems)
   ↓
Display Root: trinity_display_v45.yaml (ASI/AGI/APEX awareness)
   ↓
Action Root (optional): MCP server (runtime constitutional tools)
```

### Why Modular?

**Problem:** One system prompt for ALL contexts creates entropy.
- ChatGPT web chat needs empathy focus (F6 κᵣ)
- Cursor IDE needs F1-CODE through F9-CODE (code-level floors)
- GPT Builder needs multi-turn session state tracking

**Solution:** Modular overlays reduce context size and improve focus.

### Loading Order

**Conversational AI (ChatGPT web, Claude, Gemini):**
1. Load `base_governance_v45.yaml`
2. Load `conversational_overlay_v45.yaml`
3. Load `trinity_display_v45.yaml`

**Code Generation (Cursor, VS Code Copilot):**
1. Load `base_governance_v45.yaml`
2. Load `code_generation_overlay_v45.yaml`
3. Optional: Install MCP server for runtime tools

**Agent Builders (GPT Builder, Gemini Gems):**
1. Load `base_governance_v45.yaml`
2. Load `agent_builder_overlay_v45.yaml`
3. Load `trinity_display_v45.yaml`

---

## MCP Integration (IDE Users - NEW)

**MCP (Model Context Protocol)** provides runtime constitutional tools to LLMs in IDEs.

**Key Distinction:**
- **L2_GOVERNANCE** = Prompt-time governance (what LLM knows)
- **MCP** = Runtime governance (constitutional tools LLM can call)

**Together:** Prompt awareness + runtime verification = layered governance

### MCP Server Tools

**Server:** `scripts/arifos_mcp_entry.py`

**Provides:**
- `arifos_judge` - Constitutional evaluation of task/response
- `arifos_fag_read` - Governed file access (prevents unauthorized reads)
- `arifos_audit` - Ledger verification
- `arifos_recall` - Memory system queries
- `arifos_evaluate` - Lightweight governance check

**Installation Guide:** [`mcp/integration_guide.md`](mcp/integration_guide.md)

**Supported IDEs:**
- Claude Desktop
- VS Code
- Cursor

---

## Relationship to Authoritative Sources

```
spec/v45/ (PRIMARY)
    ↓ derives/simplifies
L2_GOVERNANCE (DERIVATIVE)
    ↓ copy-paste by users
ChatGPT/Claude/Cursor/etc.

L1_THEORY/canon/ (PRIMARY - philosophical)
    ↓ explains/justifies
spec/v45/ (PRIMARY - executable)
    ↓ enforced by
arifos_core/ (RUNTIME)
```

**Rule:** L2_GOVERNANCE is NOT imported by code. It's for humans to copy-paste into LLMs.

---

## Key Files

### Universal (Modular Architecture - v45.0)

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `universal/base_governance_v45.yaml` | **NEW** Universal core (9 floors + SABAR + verdicts) | ~500 | spec/v45/constitutional_floors.json + genius_law.json |
| `universal/conversational_overlay_v45.yaml` | **NEW** Empathy focus for web chat (ASI mode) | ~210 | spec/v45/trinity_display.json + Communication Law |
| `universal/code_generation_overlay_v45.yaml` | **NEW** F1-CODE through F9-CODE for IDEs | ~310 | CLAUDE.md + spec/v45/constitutional_floors.json |
| `universal/agent_builder_overlay_v45.yaml` | **NEW** Multi-turn tool governance | ~250 | spec/v45/constitutional_floors.json (high_stakes) |
| `universal/trinity_display_v45.yaml` | **NEW** ASI/AGI/APEX display modes | ~300 | spec/v45/trinity_display.json + canon Section 15 |
| `universal/communication_enforcement_v45.yaml` | Communication Law enforcement | ~330 | [`L1_THEORY/canon/COMMUNICATION_LAW_v45.md`](../L1_THEORY/canon/COMMUNICATION_LAW_v45.md) |
| `templates/minimal_governance.yaml` | 20-line minimal version | 20 | Condensed from base_governance |

### Core Governance

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `core/constitutional_floors.yaml` (.json) | Complete F1-F9 specifications | ~600 | spec/v45/constitutional_floors.json |
| `core/genius_law.yaml` (.json) | GENIUS metrics (G, C_dark, Psi, TP) | ~400 | spec/v45/genius_law.json |
| `core/verdict_system.yaml` (.json) | Verdict logic & hierarchy | ~500 | spec/v45/*.json |

### Enforcement

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `enforcement/red_patterns.yaml` (.json) | Instant VOID patterns (8 categories) | ~400 | spec/v45/red_patterns.json |
| `enforcement/session_physics.yaml` (.json) | TEARFRAME thresholds (budget, burst, streak) | ~500 | spec/v45/session_physics.json |

### Federation

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `federation/waw_organs.yaml` (.json) | W@W Federation (5 organs with veto powers) | ~700 | spec/v45/waw_prompt_floors.json |
| `federation/anti_hantu.yaml` (.json) | Anti-Hantu patterns (5 tiers) | ~600 | spec/v45/waw_prompt_floors.json |

### Memory

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `memory/cooling_ledger.yaml` (.json) | Ledger config + 6-band routing | ~500 | spec/v45/cooling_ledger_phoenix.json |
| `memory/phoenix72.yaml` (.json) | Phoenix-72 amendment engine (72h cooling) | ~600 | spec/v45/cooling_ledger_phoenix.json |
| `memory/scar_lifecycle.yaml` (.json) | SCAR/WITNESS state machine | ~500 | spec/v45/cooling_ledger_phoenix.json |

### Pipeline

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `pipeline/stages.yaml` (.json) | Complete 000→999 pipeline (10 stages) | ~650 | [`L1_THEORY/canon/03_runtime/010_PIPELINE_000TO999_v45.md`](../L1_THEORY/canon/03_runtime/010_PIPELINE_000TO999_v45.md) |
| `pipeline/memory_routing.yaml` (.json) | 6-band routing + retention tiers | ~500 | spec/v45/cooling_ledger_phoenix.json |

### Platform Integration

| File | Purpose | Lines | Optimized For |
|------|---------|-------|---------------|
| `integration/chatgpt_custom_instructions.yaml` | ChatGPT Custom Instructions (conversational) | ~127 | ChatGPT UI character limits (~1500 chars/field) |
| `integration/claude_projects.yaml` | Claude Projects (conversational) | ~225 | Claude's extended context + markdown rendering |
| `integration/cursor_rules.yaml` | Cursor IDE (code generation) | ~214 | Code generation + F1-CODE through F9-CODE |
| `integration/vscode_copilot.yaml` | VS Code Copilot (code generation) | ~220 | Inline suggestions + safe completion patterns |
| `integration/gpt_builder.yaml` | **NEW** GPT Builder (agent builder) | ~250 | OpenAI Custom GPTs + multi-turn tool governance |
| `integration/gemini_gems.yaml` | **NEW** Gemini Gems (agent builder) | ~240 | Google Gems + multi-turn tool governance |

**Modular References:**
- Conversational integrations → `base_governance` + `conversational_overlay` + `trinity_display`
- Code integrations → `base_governance` + `code_generation_overlay` + MCP (optional)
- Agent builder integrations → `base_governance` + `agent_builder_overlay` + `trinity_display`

**Note:** All files have both YAML (human-readable) and JSON (machine-readable) versions except integration files (YAML-only for platform compatibility).

## Format Policy (Repo Hygiene)

- Outside `skills/` (temporary exception), this layer is **YAML/JSON-only**, plus `README.md`.

--- 

## Usage

### Platform-Specific Installation (Recommended)

**Use platform-optimized configs for best results:**

#### ChatGPT
1. Open ChatGPT Settings → Personalization → Custom Instructions
2. Copy `about_you` section from [`integration/chatgpt_custom_instructions.yaml`](integration/chatgpt_custom_instructions.yaml) to first field
3. Copy `how_to_respond` section to second field
4. Save and test with: "What is the capital of France?"
   - Expected: "Paris is the capital of France." (clean, no metrics)

#### Claude Projects
1. Open Project Settings → Add Knowledge
2. Upload [`integration/claude_projects.yaml`](integration/claude_projects.yaml) as project knowledge
3. Test with simple query to verify Communication Law enforcement

#### Cursor IDE
1. Add [`integration/cursor_rules.yaml`](integration/cursor_rules.yaml) to repository root as `.cursorrules`
2. Restart Cursor to load rules
3. Test code generation to verify F1-CODE through F9-CODE enforcement

#### VS Code Copilot
1. Create `.github/copilot-instructions.md` in repository root
2. Copy `copilot_instructions` section from [`integration/vscode_copilot.yaml`](integration/vscode_copilot.yaml)
3. Add to `.vscode/settings.json`:
   ```json
   {
     "github.copilot.advanced": {
       "customInstructionsFile": ".github/copilot-instructions.md"
     }
   }
   ```

### Quick Start (Universal Format)

**For platforms without dedicated integration:**

1. **Simple governance:** Copy [`universal/communication_enforcement_v45.yaml`](universal/communication_enforcement_v45.yaml)
2. **Complete governance:** Copy [`universal/system_prompt_v45.yaml`](universal/system_prompt_v45.yaml)
3. **Minimal governance:** Copy [`templates/minimal_governance.yaml`](templates/minimal_governance.yaml)

**Result:** Governed AI with clean outputs (no metrics, no governance theater).

---

**DITEMPA BUKAN DIBERI** — Forged, not given. Governance is portable.
