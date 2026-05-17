# C_INFRA_WINDOWS — The Local Substrate (Windows Forge)

**Status:** ARCHITECTURAL SPECIFICATION | **Version:** 2026.03.13
**Authority:** 888_JUDGE (Antigravity)
**Governance:** This document describes the "Body" requirements for a human-centric Windows host.

---

## 1. The Architectural Split (Mind vs. Body)

To maintain constitutional clarity, the host must enforce a strict physical separation of documents (The Mind) and code (The Body).

| Domain | Canonical Path | Role | Governance |
| :--- | :--- | :--- | :--- |
| **THE MIND** | `C:\arifOS\` | Document repository, historical canon, theory. | Read-intensive, Human-readable only. |
| **THE BODY** | `C:\arifosmcp\` | Active development, metabolic loop, executables. | Write-intensive, Machine-executable. |

---

## 2. Windows Environmental Prerequisites

### 2.1 Python Metabolic Layer
- **Version**: Python 3.12+ Required.
- **Management**: [uv](https://github.com/astral-sh/uv) is the mandatory environment manager for performance and stability.
- **Pip Config**: Isolated venvs (`.venv`) must reside within project subdirectories to avoid global namespace pollution.

### 2.2 Symbolic Transport Layer
- **Node.js**: v20+ (LTS).
- **Tooling**: Required for `aaa_mcp` client adapters and JavaScript-based MCP tools (e.g., `markdownlint`, `marp-cli`).

### 2.3 Version Control (The Witness)
- **Git**: git-scm for Windows.
- **Global Config**: `core.autocrlf` must be set to `true` to ensure cross-platform compatibility with VPS/Linux instances.

---

## 3. Operational Tooling (The Hands)

To fulfill the **METABOLIC LOOP (000-999)**, the following binaries must be system-available in the PATH:

| Tool | Purpose | Constitutional Floor |
| :--- | :--- | :--- |
| **Ruff** | Fast linting and formatting. | F4 Clarity |
| **Pytest** | Automated verification of logic. | F2 Truth |
| **Marp CLI** | Markdown-to-PDF/PPTX conversion. | F4 Clarity |
| **Docker Desktop** | Containerized sandbox for risky operations. | F5 Peace |
| **SQLite3** | Local storage for VAULT999 Merkle chains. | F3 Tri-Witness |

---

## 4. Hardware Calibration (Genius Benchmarks)

For a local Windows agent host to maintain `G ≥ 0.80` (Genius Index), the following hardware constraints are recommended:

- **Compute**: Minimum 8 Cores (16 Threads). AI inference requires high high-burst CPU capability for local embedding scans.
- **Memory**: 32GB RAM minimum. Agents typically maintain large context windows and multiple concurrent metabolic threads.
- **Storage**: NVMe SSD. The arifOS metabolic loop involves high-frequency file reads across the `Mind` and `Body`.

---

## 5. Security & Identity (F11/CmdAuth)

On Windows, arifOS agents leverage the local security context.
1. **Identity Binding**: Every session MUST be linked to a Windows User SID via the `CmdAuth (F11)` protocol.
2. **Permission Model**: Agents should run with "Standard User" privileges. Administrative elevation (`runas`) is a **CRITICAL TRIGGER** and must be logged as a sovereign event.
3. **Ghost Suppression (F9)**: All log outputs must be sent to `STDERR` to prevent the agent from inadvertently capturing its own logs as "reality" on `STDOUT`.

---

## 6. Directory Hygiene Protocol

- **Prohibited Paths**:
  - `C:\Users\User\Desktop\` (Chaos zone)
  - `C:\Users\User\Downloads\` (Unverified zone)
  - `OneDrive\` (Synchronization drift/latency issues)
- **Mandatory Rooting**: arifOS project folders MUST be at the highest possible root (`C:\arifOS`, `C:\arifosmcp`) to minimize path-length errors and maximize agent navigational efficiency.

**DITEMPA BUKAN DIBERI.**
