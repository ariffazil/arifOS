# Agent Alignment Audit Report (v46 → Surfaces)

**Date**: Jan 12, 2026  
**Scope**: Platform surfaces (.agent/, .codex/, .claude/, .kimi/, .cursor/, .gemini/)  
**Goal**: Align existing agent governance docs to v46 + AClip 000/999 stages  
**Outcome**: Update existing files only (no new CLI framework)

---

## Current State: Misaligned Surfaces

| Platform | Current Status | Gap |
|----------|----------------|-----|
| **.agent/** | Exists, generic | No v46 floor refs; no 000/999 AClip enforcement |
| **.codex/** | AGENTS.md exists | No sync to ARIFOS_SKILLS_REGISTRY; v45 references |
| **.claude/** | ENGINEER.md exists | No v46 floors; no 000/999 requirement; no HANDOFF reference |
| **.kimi/** | AGENTS.md sparse | No "Meta APEX PRIME" designation; missing 7 exclusive skills |
| **.cursor/** | aclip.md exists | Outdated 000→999 summary; no v46 overlay |
| **.gemini/** | No AGENT_ALIGNMENT doc | No architect surface; no v46/000/999 mention |
| **.arifos/** | Legacy holder | Should point to .antigravity/* for v46 truth |
| **.arifos_clip/** | Session ledger dir | OK; add pointer to spec/v46 in README |
| **.github/** | copilot-instructions.md | v45 references; needs v46 floor update |

---

## Alignment Plan (Lightweight)

### Phase 1: Canonical Sources (Truth Layer)

**File**: `.antigravity/AGENT_ALIGNMENT_AUDIT_REPORT.md` (this doc)

Add sections:
- [ ] **Canonical Sources**: Link to AGENTS.md, spec/v46, arifOS_SKILLS_REGISTRY.md
- [ ] **AClip 000/999 Enforcement**: Architect must run 000 before planning; Engineer seals 999 before handoff
- [ ] **Roles & Separation of Powers**: Architect (Δ), Engineer (Ω), Auditor (Ψ/Codex), KIMI (Meta APEX PRIME)
- [ ] **Platform Derivatives**: Which .agent/.codex/.claude/.kimi/.cursor/.gemini use which sources
- [ ] **Gap List**: See below

---

## File-by-File Alignment Checklist

### 1. `.agent/README.md` (or append to it)

**Add section**: "Agent Alignment (v46 AClip)"

- Canonical sources: AGENTS.md, spec/v46, ARIFOS_SKILLS_REGISTRY.md
- AClip pipeline 000→999 table
- Roles: ARCHITECT (Δ), ENGINEER (Ω), AUDITOR (Ψ), KIMI (Κ)
- Floors: F1–F9 brief explanation
- Platform derivatives: which use which sources

**Status**: ☐ Update `.agent/README.md`

---

### 2. `.codex/AGENTS.md`

**Create/update with**:
- Role: AUDITOR (Ψ) / Codex
- Floors: F1 (Truth), F3 (Stability), F6 (Amanah)
- AClip Stages: 700–999
- Canonical sources: AGENTS.md, spec/v46, ARIFOS_SKILLS_REGISTRY.md
- Requirements: Run 000 before audit; seal 999 before forwarding to KIMI
- Audit checklist: F1, F3, F6 specific checks

**Replace all v45 refs** → v46

**Status**: ☐ Update `.codex/AGENTS.md`

---

### 3. `.codex/skills/README.md`

**Add**:
- Source of truth: L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md
- Sync instruction: `python scripts/sync_skills.py --platform codex`
- Do NOT manually edit; use registry instead

**Status**: ☐ Update `.codex/skills/README.md`

---

### 4. `.claude/ENGINEER.md`

**Add section**: "v46 Alignment"

- Role: ENGINEER (Ω)
- Floors: F2 (Clarity), F4 (Iteration), F5 (Craft)
- AClip Stages: 300–699
- Required 000 (Architect) prerequisite
- Required 999 (KIMI) sign-off
- Reference: .antigravity/HANDOFF_FOR_CLAUDE.md
- Implementation checklist: F2, F4, F5 specific checks

**Status**: ☐ Update `.claude/ENGINEER.md`

---

### 5. `.claude/skills/README.md`

**Add**:
- Source of truth: L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md
- Sync instruction: `python scripts/sync_skills.py --platform claude`
- Do NOT manually edit

**Status**: ☐ Update `.claude/skills/README.md`

---

### 6. `.claude/settings`

**Add line**:
```
# Reference handoff doc: .antigravity/HANDOFF_FOR_CLAUDE.md
```

**Status**: ☐ Update `.claude/settings`

---

### 7. `.kimi/AGENTS.md`

**Create/update**:
- Designation: Meta APEX PRIME (Κ)
- Floors: All (F1–F9)
- AClip Stage: 999 (meta-governance)
- Exclusive Skills: SEAL, VOID, HOLD-888, SABAR, KIMI-OVERRIDE, LEDGER-FORENSICS, CONSTITUTION-AMEND
- Stage 999 process: receive verdicts, check floors, calculate consensus, issue verdict
- Requirements: Log to .arifos_clip/ with reasoning

**Status**: ☐ Create/update `.kimi/AGENTS.md`

---

### 8. `.kimi/skills/README.md`

**Create**:
- Role: Meta APEX PRIME (Κ)
- Exclusive skills (not synced from registry):
  - SEAL, VOID, HOLD-888, SABAR
  - KIMI-OVERRIDE, LEDGER-FORENSICS, CONSTITUTION-AMEND

**Status**: ☐ Create `.kimi/skills/README.md`

---

### 9. `.cursor/aclip.md`

**Refresh section**: "AClip Pipeline (000→999)"

- Update stage table with current AClip v46 stages
- Add v46 overlay section: canonical sources, floors, handoff docs
- Link to spec/v46

**Status**: ☐ Update `.cursor/aclip.md`

---

### 10. `.gemini/ARCHITECT_SURFACE.md` (NEW)

**Create** (~50 lines):
- Role: Specialist / Researcher
- AClip Stages: 044–066 (Read & Draft phases)
- Canonical sources: AGENTS.md, spec/v46, ARIFOS_SKILLS_REGISTRY.md
- Purpose: Provide research before ARCHITECT drafts plan
- Floors: F1 (Truth), F2 (Clarity), F4 (Iteration)
- Not your job: Implementation, governance decisions, final verdicts
- Handoff: research feeds into .antigravity/HANDOFF_FOR_CLAUDE.md

**Status**: ☐ Create `.gemini/ARCHITECT_SURFACE.md`

---

### 11. `.arifos/README_v46.md` (NEW)

**Create** (~30 lines):
- Status: Legacy v45 holder; governance moved to .antigravity/
- For v46: See .antigravity/AGENT_ALIGNMENT_AUDIT_REPORT.md
- For ledger: See .arifos_clip/

**Status**: ☐ Create `.arifos/README_v46.md`

---

### 12. `.arifos_clip/README.md` (NEW)

**Create** (~40 lines):
- Purpose: Audit trail for all agent decisions (AClip stages 000–999)
- Format: session_ROLE_STAGE_TIMESTAMP.json
- Example JSON structure
- Related docs: spec/v46, AGENTS.md, alignment audit report

**Status**: ☐ Create `.arifos_clip/README.md`

---

### 13. `.github/copilot-instructions.md`

**Update**:
- Replace v45 → v46 references
- Add floor refs: v46 floors (F1–F9)
- Add AClip gating: "Copilot respects 000/999 stages"
- Add note: "See .antigravity/AGENT_ALIGNMENT_AUDIT_REPORT.md for role/stage map"

**Status**: ☐ Update `.github/copilot-instructions.md`

---

## Canonical Sources → Derivatives Mapping

| Canonical | Derivative | Role | AClip Stages |
|-----------|-----------|------|--------------|
| AGENTS.md | .codex/AGENTS.md | Auditor | 700–999 |
| spec/v46 | .codex/skills/README.md | Auditor | 700–999 |
| ARIFOS_SKILLS_REGISTRY.md | .codex/skills/*.md | Auditor | 700–999 |
| AGENTS.md | .claude/ENGINEER.md | Engineer | 300–699 |
| spec/v46 | .claude/skills/README.md | Engineer | 300–699 |
| ARIFOS_SKILLS_REGISTRY.md | .claude/skills/*.md | Engineer | 300–699 |
| AGENTS.md | .kimi/AGENTS.md | Meta APEX PRIME | 999 |
| spec/v46 | .kimi/skills/README.md | Meta APEX PRIME | 999 |
| AGENTS.md | .cursor/aclip.md | Architect | 000–099 |
| spec/v46 | .cursor/aclip.md | Architect | 000–099 |
| AGENTS.md | .gemini/ARCHITECT_SURFACE.md (new) | Specialist | 044–066 |

---

## Verification Checklist

### Code Search (Negative Tests)

```bash
# 1. Verify no v45 references in agent surfaces
rg --hidden -n "v45" .agent/ .codex/ .claude/ .kimi/ .cursor/ .gemini/

# Expected: [No results, or only in archived/legacy sections]

# 2. Verify 000/999 mentioned in each surface
rg --hidden -n "000|999" .agent/ .codex/ .claude/ .kimi/ .cursor/ .gemini/

# Expected: Each should mention 000 (init) and 999 (final seal)

# 3. Verify spec/v46 referenced
rg --hidden -n "spec/v46" .agent/ .codex/ .claude/ .kimi/ .cursor/ .gemini/

# Expected: Each should cite spec/v46

# 4. Verify AGENTS.md referenced
rg --hidden -n "AGENTS.md" .agent/ .codex/ .claude/ .kimi/ .cursor/ .gemini/

# Expected: Each should cite AGENTS.md as canonical source
```

### Skill Registry Sync

```bash
# Check if skills are synced from canonical source
python scripts/sync_skills.py --check

# Expected: No drift between L2_GOVERNANCE/skills/ARIFOS_SKILLS_REGISTRY.md and platform skills/
```

### Hot Zone Spot-Check

```bash
# Test each platform can load its AGENTS.md
python -c "
from pathlib import Path

for platform in ['codex', 'claude', 'kimi', 'cursor', 'gemini']:
    agents_path = Path(f'.{platform}/AGENTS.md')
    if agents_path.exists():
        print(f'✓ .{platform}/AGENTS.md exists')
    else:
        print(f'✗ .{platform}/AGENTS.md MISSING')
"
```

---

## Ownership & Timeline

| Task | Owner | Deadline | Status |
|------|-------|----------|--------|
| Phase 1: `.antigravity/AGENT_ALIGNMENT_AUDIT_REPORT.md` | KIMI | Jan 15 | ☐ |
| `.agent/README.md` update | Architect | Jan 16 | ☐ |
| `.codex/*` alignment | Auditor/Codex | Jan 17 | ☐ |
| `.claude/*` alignment | Engineer | Jan 18 | ☐ |
| `.kimi/*` designation + skills | KIMI | Jan 18 | ☐ |
| `.cursor/aclip.md` refresh | Architect | Jan 19 | ☐ |
| `.gemini/ARCHITECT_SURFACE.md` (new) | Architect | Jan 19 | ☐ |
| `.arifos/` + `.arifos_clip/` pointers | KIMI | Jan 19 | ☐ |
| `.github/copilot-instructions.md` update | KIMI | Jan 19 | ☐ |
| **Verification (rg, sync_skills, spot-check)** | Engineer | Jan 20 | ☐ |
| **Final sign-off** | KIMI | Jan 20 | ☐ |

---

## Success Criteria

✅ All agent surfaces (.agent/, .codex/, .claude/, .kimi/, .cursor/, .gemini/) cite v46 and AClip 000/999  
✅ No v45 references in agent docs (only in scripts/ if legacy)  
✅ Each platform knows its role (Architect/Engineer/Auditor/Meta APEX) and stages  
✅ Canonical sources (AGENTS.md, spec/v46) are linked from all surfaces  
✅ `.antigravity/AGENT_ALIGNMENT_AUDIT_REPORT.md` is source of truth for alignment map  
✅ Skill registry sync works: `python scripts/sync_skills.py --check` passes  
✅ Session ledger pointers clear: `.arifos_clip/` is the audit trail  

---

**End State**: Light, clear, no new code. Just **alignment of surfaces to v46 + AClip 000/999 with transparent roles and handoff paths**.
