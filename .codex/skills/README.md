# arifOS Codex Skills Registry

This directory contains Codex-specific skill wrappers for arifOS workflows.

## Available Skills

| Skill | Trigger | Canonical Source | Description |
| :--- | :--- | :--- | :--- |
| `arifos-workflow-000` | `/000` | `.agent/workflows/000.md` | Initialize session context & version status |
| `arifos-workflow-gitforge` | `/gitforge` | `.agent/workflows/gitforge.md` | Analyze branch entropy & hot zones |
| `arifos-workflow-fag` | `/fag` | `.agent/workflows/fag.md` | Activate Full Autonomy Governance |

## Global Prerequisites (Always On)

These skills are available globally and do not require repo-specific wrappers:

*   `arifos-constitution`: 9-Floor Constitutional Governance
*   `arifos-fag-safe-read`: Governed file I/O with receipts
*   `arifos-trinity-git-governance`: Git QC/Seal workflow
*   `arifos-aclip-runner`: Full 000→999 ACLIP Pipeline

## Skill Structure

Each skill directory contains a `SKILL.md` with:
- `name`: Skill identifier
- `description`: When to trigger this skill
- Procedure steps pointing to the canonical workflow source
