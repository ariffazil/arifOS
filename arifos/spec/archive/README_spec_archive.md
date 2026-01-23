# Archived Specifications

**Purpose:** This directory contains deprecated specification versions preserved for forensic analysis and historical reference.

**Retention Policy:** Permanent (never delete)
**Access:** Read-only for audit and learning purposes

---

## Archived Versions

### v42/ - Phoenix Consolidation (Archived 2026-01-12)
**Status:** DEPRECATED
**Successor:** v45.0
**Sunset Date:** 2025-12-XX
**Reason:** Superseded by v45 Phoenix-72 consolidation

**Contents:**
- `constitutional_floors.json` - 9 floors (pre-hypervisor)
- `cooling_ledger_phoenix.json` - Phoenix-72 protocol
- `federation.json` - Multi-agent coordination
- `pipeline.json` - Pipeline orchestration
- `spec_binding.json` - Spec-code binding
- `waw_prompt_floors.json` - W@W Federation
- `cooling_ledger_cryptography.md` - ZKPC documentation

### v45/ - Phoenix-72 Consolidation (Archived 2026-01-12)
**Status:** DEPRECATED
**Successor:** v46.0
**Sunset Date:** 2026-01-12
**Reason:** CIV-12 Hypervisor Layer expansion (F10-F12)

**Contents:**
- `constitutional_floors.json` - 9 floors (pre-hypervisor)
- `atlas_333.json` - AGI exploration layer
- `eureka_777.json` - ASI felt-care layer
- `genius_law.json` - Genius Law (Part 1.1.0)
- `cooling_ledger_phoenix.json` - Phoenix-72 protocol
- `red_patterns.json` - Anti-Hantu patterns
- `session_physics.json` - Session thermodynamics
- `trinity_display.json` - Trinity display protocol
- `truth_verification.json` - Truth verification
- `waw_prompt_floors.json` - W@W Federation
- `sealion_adapter_v45.json` - Sealion integration
- `tac_eureka_vault999.json` - TAC EUREKA vault
- Policy files: `policy_fag.json`, `policy_refusal.json`, `policy_risk_literacy.json`, `policy_tcha.json`, `policy_temporal.json`
- Schema files: `schema/*.schema.json` (JSON Schema validators)
- `MANIFEST.sha256.json` - Cryptographic integrity
- `SEAL_CHECKLIST.md` - Constitutional seal checklist

**Key Differences from v46:**
- 9 floors vs 12 (missing F10 Ontology, F11 Command Auth, F12 Injection Defense)
- Monolithic structure vs pipeline-organized (no 000-999 folders)
- Combined governance vs separated (no governance/ subfolder)

---

## Migration Notes

**From v45 → v46:**
- **+3 Hypervisor Floors:** F10 (Ontology guard), F11 (Command auth), F12 (Injection defense)
- **Pipeline Organization:** Files organized by stage (000_foundation, 333_atlas, 444-888, 999_vault)
- **Governance Separation:** governance/ subfolder for AAA Trinity, W@W Federation, pipeline stages
- **Crisis Patterns:** Consolidated to governance/crisis_patterns.json (single source of truth)
- **Temporal Numbering:** Canon files use stage-hundreds (3XX, 4XX, 5XX, etc.)

**Breaking Changes:**
- Import paths changed (Track C needs updates)
- MANIFEST.sha256.json hashes changed (all files moved/modified)
- Constitutional loader must target spec/v46/constitutional_floors.json

**Migration Guide:** See `spec/v46/README.md` for loader updates

---

## Forensic Use Cases

1. **Historical Analysis:** Compare floor threshold evolution across versions
2. **Bug Archaeology:** Trace when specific patterns/rules were introduced
3. **Audit Trail:** Verify constitutional decisions made under older versions
4. **Learning:** Study architectural evolution (monolithic → pipeline-organized)
5. **Regression Testing:** Compare v46 behavior against v45 baselines

---

## Access Guidelines

**DO:**
- Read for historical reference
- Compare for forensic analysis
- Study for architectural learning
- Reference in audit reports

**DO NOT:**
- Load as runtime specifications (outdated)
- Modify files (historical integrity)
- Copy patterns without v46 review (may be deprecated)
- Use for new implementations (use v46)

---

**Archived:** 2026-01-12
**Archived By:** Ω (Claude Code - Session X7K9F22)
**Git History:** Preserved via `git mv` (use `git log --follow` to trace)

**Current Version:** spec/v46/ (PRIMARY AUTHORITY)
