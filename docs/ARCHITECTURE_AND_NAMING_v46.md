# arifOS v46 Architecture & Naming Convention

**Authority:** `AGENTS.md` > `GEMINI.md` > This File
**Philosophy:** *"DITEMPA BUKAN DIBERI"* (Forged, not given).
**Core Tenet:** Structure is Constitution. A disciplined filesystem reflects a disciplined mind.

## 1. Directory Structure (The Orthogonal Tree)

The repository is divided into three "Magisteria" (Layers of Authority):

### Layer 1: The Canon (`L1_THEORY`)
*   **Purpose:** Immutable truths, constitutional laws, and sealed knowledge.
*   **Governance:** High friction. Requires `trinity.py seal`.
*   **Contents:** `canon/`, `ledger/` (Cooling Ledger).

### Layer 2: The Specifications (`L2_GOVERNANCE`)
*   **Purpose:** Operational rules, overlay configurations, and agent instructions.
*   **Governance:** Medium friction. Defines *how* we apply the Canon.
*   **Contents:** `active/` (Current specs), `archive/` (Superseded specs).

### Layer 3: The Operations (`arifos_*`)
*   **Purpose:** The machine itself. Source code and runtime logic.
*   **Governance:** Low friction (during Dev), High friction (during Deploy).
*   **Naming:** Python packages must use `snake_case` and start with `arifos_` (e.g., `arifos_core`, `arifos_clip`).

## 2. Root Directory Policy
The root directory must be kept Low Entropy.

*   **ALLOWED:**
    *   `AGENTS.md` (The Supreme Law)
    *   `GEMINI.md` (Agent Brain)
    *   `CLAUDE.md`, `CODEX.md` (Agent Contexts)
    *   `pyproject.toml`, `README.md`, `LICENSE` (Standard Meta)
    *   `tests/` (Unit Tests)
    *   `scripts/` (Maintenance Scripts)
    *   `docs/` (Documentation)

*   **FORBIDDEN (Must Move):**
    *   Loose `*_REPORT.md` or `*_SUMMARY.md` (Move to `docs/reports/`)
    *   Loose `.py` scripts (Move to `scripts/` or `tests/`)
    *   Ad-hoc directories without `L1/L2` or `arifos_` prefix.

## 3. Naming Conventions

### Files
*   **Python:** `snake_case.py` (e.g., `floor_checks.py`)
*   **Markdown:** `UPPER_SNAKE_CASE.md` for major artifacts (e.g., `AGENTS.md`), `snake_case.md` for documentation.
*   **Config:** `UPPER_CASE.json/yaml` for global config (e.g., `ARIFOS_GLOBAL_CONFIG.json`).

### Code
*   **Classes:** `PascalCase` (e.g., `TrinityOrchestrator`)
*   **Functions:** `snake_case` (e.g., `enforce_floors`)
*   **Constants:** `UPPER_CASE` (e.g., `VERDICT_SEAL`)

## 4. Governance Philosophy
**"Truth must cool before it rules."**

*   **Entropy Reduction:** Every action must ideally reduce the total entropy of the system.
*   **Fail-Closed:** When in doubt, the system (and architecture) defaults to a "secure, blocked" state.
*   **Observation:** If you can't see it (grep/ls), it doesn't exist.

---
**Status:** DRAFT (v46)
