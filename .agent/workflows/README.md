# arifOS Agent Workflows Registry

This directory contains the canonical workflow definitions for arifOS agents (e.g., Antigravity/Gemini, Claude).

## Available Workflows

| Workflow | Trigger | Description |
| :--- | :--- | :--- |
| `000.md` | `/000` | Session initialization: loads version, branch, status, and logs |
| `gitforge.md` | `/gitforge` | Trinity forge: entropy analysis & hot-zone detection |
| `fag.md` | `/fag` | Full Autonomy Governance: preflight checks & authority boundaries |

## Naming Crosswalk (Agent ↔ Codex)

| Agent Workflow | Codex Skill Equivalent |
| :--- | :--- |
| `000.md` | `arifos-workflow-000` |
| `gitforge.md` | `arifos-workflow-gitforge` |
| `fag.md` | `arifos-workflow-fag` |

## Global Prerequisites (Always On)

These skills are loaded from your user profile and apply to any repository:

* `arifos-constitution`: 9-Floor Constitutional Governance
* `arifos-fag-safe-read`: Governed file I/O with receipts
* `arifos-trinity-git-governance`: Git QC/Seal workflow
* `arifos-aclip-runner`: Full 000→999 ACLIP Pipeline

## Usage

Workflows are triggered by slash commands (e.g., `/000`). The agent reads the corresponding `.md` file and executes the steps within.
