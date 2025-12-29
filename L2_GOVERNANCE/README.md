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

**Maintenance:** When `spec/v45/` or `L1_THEORY/canon/` change, these prompts should be manually updated to reflect changes.

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

### Universal (Copy-Paste Ready)

| File | Purpose | Lines | Derived From |
|------|---------|-------|--------------|
| `universal/communication_enforcement_v45.yaml` | **NEW** Communication Law enforcement | ~200 | [`L1_THEORY/canon/COMMUNICATION_LAW_v45.md`](../L1_THEORY/canon/COMMUNICATION_LAW_v45.md) |
| `universal/governance_v45.yaml` | Full governance pack (portable) | ~200 | spec/v45/*.json |
| `universal/system_prompt_v45.yaml` | Simplified governance YAML | ~200 | spec/v45/*.json |
| `templates/minimal_governance.yaml` | 20-line minimal version | 20 | Condensed from above |

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
| `integration/chatgpt_custom_instructions.yaml` | ChatGPT Custom Instructions format | ~450 | ChatGPT UI character limits (~1500 chars/field) |
| `integration/claude_projects.yaml` | Claude Projects knowledge base | ~800 | Claude's extended context + markdown rendering |
| `integration/cursor_rules.yaml` | Cursor IDE code-level governance | ~650 | Code generation + F1-CODE through F9-CODE |
| `integration/vscode_copilot.yaml` | VS Code Copilot instructions | ~600 | Inline suggestions + safe completion patterns |

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
