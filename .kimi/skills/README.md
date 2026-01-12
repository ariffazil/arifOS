# Kimi Skills Directory

**Authority:** Skills derive from `.agent/workflows/` (master source)
**Sync:** Manual until automated sync script extended for Kimi

## Structure

This directory contains Kimi-specific skill implementations that derive from the canonical workflows in `.agent/workflows/`.

**Master-Derive Model:**
```
.agent/workflows/     (MASTER - Single source of truth)
    ↓
.kimi/skills/         (DERIVED - Kimi CLI variant)
```

## Core Constitutional Skills

**Available Skills:**

- `/000` - Session initialization (MANDATORY on reboot)
- `/gitforge` - Entropy analysis and hot zone detection
- `/gitQC` - Constitutional quality control (F1-F9 validation)
- `/gitseal` - Final seal approval (requires Kimi + Human)
- `/sabar` - Floor failure recovery protocol

## APEX PRIME Skills

**Kimi-Specific Audit Skills:**

- Constitutional floor verification (F1-F9)
- Verdict validation (SEAL/VOID/PARTIAL/SABAR/888_HOLD)
- Trinity separation-of-powers audit
- Track A/B/C boundary enforcement
- Anti-bypass detection
- PRIMARY source verification

## Skill Creation Protocol

**To add a new Kimi skill:**

1. **Create master workflow** in `.agent/workflows/`
2. **Include YAML frontmatter** with skill metadata
3. **Test with Kimi CLI** in arifOS repo
4. **Document** in this README
5. **Sync** to other platforms (future: automated via `scripts/sync_skills.py`)

## Skill Invocation

**In Kimi CLI:**

```bash
# Session initialization
/000

# Entropy analysis before audit
/gitforge

# Constitutional validation
/gitQC

# Final seal (requires human approval)
/gitseal

# Recovery protocol
/sabar
```

## Integration Notes

**Kimi CLI Features:**
- Slash commands (/) for skill invocation
- Context preservation across sessions
- Manual approval mode (NOT YOLO)
- Thinking mode for complex constitutional audits

**arifOS Governance:**
- All skills must respect F1-F9 floors
- APEX PRIME skills require PRIMARY source verification
- Verdicts logged to THE EYE ledger
- No self-sealing (Kimi cannot approve own work)

---

**Status:** INITIALIZED (awaiting master workflow sync)
**Version:** v46.0.0

---

## Alignment (v46 AClip)

- Canonical sources: `AGENTS.md` (root), `spec/v46/*`, `L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md`.
- Stages (canonical): `000 → 444 → 666 → 888 → 999` (bundle shorthand 700/744/888/999 maps to this spine; use canonical here).
- Mandatory skills on KIMI surface: `/000-init`, `/fag-read`, `/ledger`, `/gitforge`/`/gitQC`/`/gitseal`, `/audit-constitution`, `/verify-trinity`, `/verify-sources`, `/issue-verdict`, `/track-alignment`, `/anti-bypass-scan`, `/ledger-audit`, `/999-seal`.
- Floor references: `spec/v46/constitutional_floors.json` (RASA=F7, Tri-Witness=F8, Anti-Hantu=F9, Symbolic Guard=F10, Command Auth=F11, Injection Defense=F12).
- Drift checks: `python scripts/sync_skills.py --check`; `rg --hidden -n "v45" .kimi`.
