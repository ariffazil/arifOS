# v45 Naming Convention (Epoch Law)

**Authority:** Track A (Mutable via Phoenix-72)
**Status:** ACTIVE | **Version:** v45.0.0

---

## 1. Core Principles
1.  **Drift Prevention:** Every file must have a single, canonical location.
2.  **Epoch Clarity:** Filenames must reflect their era (v42, v45) where ambiguous.
3.  **Track Separation:** Law (A), Spec (B), and Code (C) must not mix.

## 2. Directory Structure Layers (Immutable)

| Layer | Path | Content |
| :--- | :--- | :--- |
| **L1** | `L1_THEORY/canon/` | **Track A:** Constitutional Law. Read-only to runtime. |
| **L2** | `L2_GOVERNANCE/` | **Portable:** Constitutions & Prompts for export. |
| **Core** | `arifos_core/` | **Track C:** The Runtime Implementation (Python). |
| **L4** | `L4_MCP/` | Model Context Protocol servers. |
| **L5** | `L5_CLI/` | Command Line Interfaces. |
| **L6** | `L6_SEALION/` | Regional LLM integrations. |
| **L7** | `L7_DEMOS/` | Examples, Demos, and Legacy artifacts. |

## 3. File Naming Rules

### Track A: Canon Files
- **Path:** `L1_THEORY/canon/<domain>/`
- **Pattern:** `{NNN}_{NAME}_v45.md`
- **Example:** `041_TRINITY_FOUNDATION_v45.md`
- **Rule:** Legacy epochs (v42/v44) must be archived if superseded.

### Track B: Specifications
- **Path:** `spec/v45/`
- **Pattern:** `{component}.{json|yaml}`
- **Example:** `spec/v45/constitutional_floors.json`
- **Rule:** Version is in the *directory* name, not the filename.

### Track C: Runtime Code
- **Path:** `arifos_core/`
- **Pattern:** `snake_case.py`
- **Rule:** No version numbers in module filenames (`pipeline.py`, not `pipeline_v45.py`).

## 4. Integration Surface Policy
- **Core Integrations:** `arifos_core/integration/` (Ports/Interfaces).
- **Core Providers:** `arifos_core/adapters/` (LLM Drivers).
- **Root `integrations/`:** **DEPRECATED**. Must contain only a README shim or legacy demos.

## 5. Artifacts and Hidden Directories
- `.arifos/` - Tooling config (Trinity, templates).
- `.gemini/`, `.claude/` - Agent memory contexts.
- `cooling_ledger/` - Runtime audit logs.
- `archive/` - Retired artifacts (Never delete, always archive).
