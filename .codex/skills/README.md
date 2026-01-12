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

---

## Alignment (v46 AClip)

- Canonical sources: `AGENTS.md` (root), `spec/v46/*`, `L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md`.
- Stages (canonical): `000 → 444 → 666 → 888 → 999`; bundle shorthand (044/066/088/099/700/744) maps to the same spine—prefer canonical numbering here.
- Mandatory skills on Codex surface: `/000-init`, `/fag-read` (governed read with receipt), `/ledger`, `/review` (audit), `/websearch-grounding`, `/gitforge`/`/gitQC`/`/gitseal`, `/999-seal`.
- Floor references: use `spec/v46/constitutional_floors.json` (F7 RASA, F8 Tri-Witness, F9 Anti-Hantu, F10 Symbolic Guard, F11 Command Auth, F12 Injection Defense).
- Drift checks: `python scripts/sync_skills.py --check`; `rg --hidden -n "v45" .codex`.
