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

**Last Updated**: 2026-01-12 (v46.1 Agent Alignment)  
**License**: AGPL-3.0
