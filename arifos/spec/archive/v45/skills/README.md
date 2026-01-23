# arifOS Skills Directory

**Location:** `L2_GOVERNANCE/skills/`
**Purpose:** Canonical skills registry and governance specifications
**Authority:** Track B (Operational Governance Layer)

---

## Directory Purpose

This directory contains the **single source of truth** for all arifOS constitutional skills. It consolidates fragmented skill definitions from:

- `.agent/workflows/` (master definitions)
- `.codex/skills/` (ChatGPT Codex variants)
- `.claude/skills/` (Claude Code variants)

**Key Principle:** Master-Derive model – one canonical definition, platform-specific derivations.

---

## Files in This Directory

### Core Registry

- **[ARIFOS_SKILLS_REGISTRY.md](ARIFOS_SKILLS_REGISTRY.md)** – **PRIMARY REFERENCE**
  - Authoritative registry of all 7 core skills
  - Constitutional law (LAW), interface specs (INTERFACE), enforcement logic (ENFORCEMENT)
  - Tool restrictions, verdict triggers, logging requirements
  - Master-derive sync protocol
  - Version history and naming mappings

### Future Additions (Planned)

- `skill_schema_v1.json` – JSON Schema for skill YAML frontmatter validation
- `sync_manifest.json` – Sync state tracking (last sync time, version checksums)
- Individual skill specifications (if expanded beyond single registry file)

---

## Quick Reference

### 7 Core Skills

| # | Skill | Master File | Purpose | CLI Safe? |
|---|-------|-------------|---------|-----------|
| 1 | /000 | `.agent/workflows/000.md` | Session initialization | ✅ Yes |
| 2 | /fag | `.agent/workflows/fag.md` | Full autonomy governance mode | ✅ Yes |
| 3 | /entropy | [bundled in /gitforge] | Entropy assessment | ✅ Yes |
| 4 | /gitforge | `.agent/workflows/gitforge.md` | State mapping & entropy prediction | ✅ Yes |
| 5 | /gitQC | [code: `trinity/qc.py`] | Constitutional quality control (F1-F9) | ✅ Yes |
| 6 | /gitseal | [code: `trinity.py`] | Human sealing (approval gate) | 🚫 No (Human-gated) |
| 7 | /sabar | [embedded in pipeline] | Constitutional pause protocol | 🚫 No (Internal) |

**Legend:**
- ✅ Yes: Read-only or governed analysis (safe for CLI exposure)
- 🚫 No: Requires human approval or is internal governance state

---

## Usage

### For Developers

**Read the registry:**
```bash
# View full registry
cat L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md

# Search for specific skill
grep -A 20 "## Skill 1: /000" L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md
```

**Sync skills to platforms:**
```bash
# Preview changes (dry-run)
python scripts/sync_skills.py --dry-run

# Apply sync (propagate master to .codex/ and .claude/)
python scripts/sync_skills.py --apply
```

**Check for drift:**
```bash
# Detect version mismatches, orphaned skills, tool violations
python scripts/check_skill_drift.py
```

### For AI Agents

**On session start (000):**
1. Read `L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md` for skill definitions
2. Cross-reference with loaded constitutional specs (`spec/v44/*.json`)
3. Apply tool restrictions per skill context

**During autonomous work (fag):**
- Check `allowed-tools` for current skill
- Enforce fail-closed (unlisted tool = forbidden)
- Monitor entropy (ΔS) against SABAR-72 threshold (≥5.0)

---

## Relationship to Other Governance Layers

### Track A (L1_THEORY/canon/) – Immutable Law

- Constitutional floors (F1-F9)
- Pipeline stages (000→999)
- Philosophical foundations (ΔΩΨ Trinity)

**Skills implement Track A law.**

### Track B (spec/v44/) – Tunable Parameters

- `constitutional_floors.json` – Floor thresholds
- `genius_law.json` – G, C_dark metrics
- `session_physics.json` – Pipeline physics

**Skills consume Track B specs.**

### L2_GOVERNANCE (This Layer) – Operational Governance

- Plugin governance (`.claude/plugins/arifos-governed/governance/`)
- Skills registry (this directory)
- Operator manuals, CLI guides

**Skills define operational procedures.**

### Implementation Layer (arifos_core/) – Python Enforcement

- Floor detectors (`floor_detectors/`)
- Pipeline stages (`stages/`)
- Verdict generation (`judiciary/`)

**Skills are enforced by Python code.**

---

## Skill Governance Principles

### Master-Derive Model

```
.agent/workflows/*.md (MASTER)
    ↓
    ↓ scripts/sync_skills.py
    ↓
    ├─→ .codex/skills/*/SKILL.md (DERIVED + Codex enhancements)
    └─→ .claude/skills/*/SKILL.md (DERIVED + Claude enhancements)
```

**Key Rules:**
1. **ONE** master definition per skill (in `.agent/workflows/`)
2. Platform variants derived via automated sync
3. Platform enhancements **preserved** (not overwritten)
4. Tool restrictions can only **restrict further**, never expand

### Fail-Closed Enforcement

- Unlisted tool = **FORBIDDEN**
- Missing skill definition = **VOID**
- Version drift detected = **WARN** (require sync)
- Tool violation = **BLOCK** (fail-closed)

### Constitutional Compliance

Every skill must:
- [ ] Map to specific constitutional floors (F1-F9)
- [ ] Define `allowed-tools` (whitelist)
- [ ] Specify verdict logic (SEAL/PARTIAL/VOID/SABAR/HOLD)
- [ ] Document logging requirements (cooling ledger integration)
- [ ] Include LAW, INTERFACE, ENFORCEMENT sections

---

## Adding a New Skill

### Step-by-Step

1. **Create master file:**
   ```bash
   touch .agent/workflows/new-skill.md
   ```

2. **Define YAML frontmatter:**
   ```yaml
   ---
   skill: "new-skill"
   version: "0.1.0"
   description: "Brief description"
   floors: [F1, F2, ...]
   allowed-tools:
     - Tool1
     - Tool2
   expose-cli: true/false
   derive-to: [codex, claude]
   ---
   ```

3. **Write sections:**
   - **LAW**: Constitutional function
   - **INTERFACE**: Usage examples
   - **ENFORCEMENT**: Verdict logic

4. **Update registry:**
   - Add to `ARIFOS_SKILLS_REGISTRY.md` skill catalog
   - Document tool restrictions
   - Add naming mappings

5. **Sync to platforms:**
   ```bash
   python scripts/sync_skills.py --apply
   ```

6. **Test enforcement:**
   - Create unit tests for floor checks
   - Verify tool restrictions work
   - Test verdict logic (SEAL/VOID scenarios)

7. **Update AGENTS.md:**
   - Add cross-reference if needed
   - Document new skill in operator guidance

---

## Modifying Existing Skill

**CRITICAL:** Only edit master files (`.agent/workflows/`), never platform variants directly.

### Workflow

1. **Edit master:**
   ```bash
   vi .agent/workflows/000.md
   ```

2. **Bump version:**
   ```yaml
   version: "1.0.0" → "1.1.0"
   ```

3. **Document changes:**
   ```bash
   # Add to CHANGELOG.md
   echo "- Updated /000 skill: Added git branch verification" >> CHANGELOG.md
   ```

4. **Sync platforms:**
   ```bash
   python scripts/sync_skills.py --apply
   ```

5. **Verify no drift:**
   ```bash
   python scripts/check_skill_drift.py
   ```

6. **Test:**
   ```bash
   pytest tests/skills/ -v
   ```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-29 | Initial skills directory (unified registry) |

---

## See Also

- [ARIFOS_SKILLS_REGISTRY.md](ARIFOS_SKILLS_REGISTRY.md) – **PRIMARY REFERENCE**
- [../../.claude/plugins/arifos-governed/governance/](../../.claude/plugins/arifos-governed/governance/) – Plugin governance docs
- [../../AGENTS.md](../../AGENTS.md) – Full constitutional governance
- [../../spec/v44/](../../spec/v44/) – Track B specs
- [../../.agent/workflows/](../../.agent/workflows/) – Master skill definitions

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
