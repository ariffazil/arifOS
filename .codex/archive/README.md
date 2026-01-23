# Codex Skills (v46.1)

**Source of Truth**: L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md

All Codex skills are synced from the canonical registry. To add, modify, or remove a skill:

## Sync Workflow

1. **Edit canonical source**: L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md
2. **Run sync command**:
   ```bash
   python scripts/sync_skills.py --platform codex
   ```
3. **Verify**: `.codex/skills/` reflects the changes
4. **Commit**: Document the skill in git commit message

## Skill Categories (From Registry)

- **audit-floors**: Check F1–F6 compliance (primary auditor skills)
- **audit-ledger**: Verify `.arifos_clip/` session trail integrity
- **audit-code**: Validate code against spec/v46 thresholds
- **audit-governance**: Check constitutional boundaries (F6 Amanah)
- [Additional skills populated from registry...]

## Skill Structure

Each skill directory contains a `SKILL.md` with:
- `name`: Skill identifier
- `description`: When to trigger this skill
- Procedure steps pointing to the canonical workflow source

## Restrictions

❌ **DO NOT**:
- Manually edit `.codex/skills/*.md` (sync from registry only)
- Invent new skills (add to ARIFOS_SKILLS_REGISTRY.md first)
- Skip floor checks (F1, F3, F6 mandatory)

✅ **DO**:
- Run sync_skills.py after registry changes
- Verify skill descriptions match registry
- Test skills before committing

---

## Alignment (v46 AClip)

- Canonical sources: `AGENTS.md` (root), `spec/v46/*`, `L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md`.
- Stages (canonical): `000 → 444 → 666 → 888 → 999`; bundle shorthand (044/066/088/099/700/744) maps to the same spine—prefer canonical numbering here.
- Mandatory skills on Codex surface: `/000-init`, `/fag-read` (governed read with receipt), `/ledger`, `/review` (audit), `/websearch-grounding`, `/gitforge`/`/gitQC`/`/gitseal`, `/999-seal`.
- Floor references: use `spec/v46/constitutional_floors.json` (F7 RASA, F8 Tri-Witness, F9 Anti-Hantu, F10 Symbolic Guard, F11 Command Auth, F12 Injection Defense).
- Drift checks: `python scripts/sync_skills.py --check`; `rg --hidden -n "v45" .codex`.

---

**Last Updated**: 2026-01-12 (v46.1 Agent Alignment)
**License**: AGPL-3.0
