# Track B: Specifications (v46.0)

**Authority:** PRIMARY AUTHORITY for all runtime thresholds and operational specifications
**Status:** CIV-12 Hypervisor Layer (F10-F12 added in v46.0)
**Version:** v46.0
**Date:** 2026-01-12

---

## What is Track B?

Track B is the **specification layer** of arifOS - the operational thresholds and runtime parameters that govern AI behavior. It sits between:

- **Track A (Canon/Law)**: Philosophical foundations in `L1_THEORY/canon/` (the "why")
- **Track C (Code/Runtime)**: Python implementation in `arifos_core/` (the "how")

**Track B defines the "what"**: Exact thresholds, failure actions, enforcement modes, and orchestration rules.

---

## v46.0 Architecture: Pipeline-Numbered Organization

Track B v46 introduces **pipeline-numbered folders** that mirror Track A canon structure. Each folder corresponds to a stage (or set of stages) in the 000-999 constitutional pipeline.

### Directory Structure

```
spec/v46/
├── 000_foundation/          # Stage 000: Hypervisor (Preprocessing)
│   └── hypervisor.json      # F10-F12 hypervisor floors
├── 333_atlas/               # Stage 333: AGI Exploration
│   └── agi_core.json        # F1 Truth, F2 Clarity
├── 444_align/               # Stage 444: ASI Alignment
│   └── peace_floor.json     # F3 Peace²
├── 555_empathize/           # Stage 555: ASI Empathy
│   └── empathy_floor.json   # F4 Empathy (κᵣ)
├── 666_bridge/              # Stage 666: ASI Humility
│   └── humility_floor.json  # F5 Humility (Ω₀)
├── 777_eureka/              # Stage 777: ASI Felt-Care
│   └── rasa_floor.json      # F7 RASA
├── 888_compass/             # Stage 888: APEX Judgment
│   └── compass_core.json    # F6 Amanah, F8 Tri-Witness, F9 Anti-Hantu
├── 999_vault/               # Stage 999: Seal & Archive
│   └── vault_manifest.json  # ZKPC, Cooling Ledger, Phoenix-72
├── governance/              # Cross-cutting governance protocols
│   ├── aaa_trinity.json     # AAA Trinity (ΔΩΨ) coordination
│   ├── waw_federation.json  # W@W multi-platform federation
│   └── pipeline_stages.json # 000-999 pipeline orchestration
└── schema/                  # JSON Schema validation
    └── constitutional_floors.schema.json
```

---

## The 12 Constitutional Floors (F1-F12)

Track B v46 defines **12 constitutional floors** organized by engine ownership:

### AGI Floors (Δ - Delta/Architect)
- **F1 Truth** (id:1, stage:333): Factual accuracy ≥0.99 confidence
- **F2 Clarity** (id:2, stage:333): Entropy reduction ΔS ≥ 0

### ASI Floors (Ω - Omega/Auditor)
- **F3 Peace²** (id:3, stage:444): Stability ≥1.0 (soft)
- **F4 Empathy** (id:4, stage:555): Weakest-listener protection ≥0.95 (soft)
- **F5 Humility** (id:5, stage:666): Uncertainty band [0.03, 0.05] (hard)
- **F7 RASA** (id:7, stage:777): Felt-care protocol (hard, fail-closed)

### APEX Floors (Ψ - Psi/Judge)
- **F6 Amanah** (id:6, stage:888): Integrity lock (hard)
- **F8 Tri-Witness** (id:8, stage:888): Multi-source consensus ≥0.95 (soft)
- **F9 Anti-Hantu** (id:9, stage:888): No ghost claims (meta)
- **F10 Ontology** (id:10, stage:000/888): Symbolic mode guard (hypervisor)
- **F11 Command Auth** (id:11, stage:000/888): Nonce verification (hypervisor)
- **F12 Injection Defense** (id:12, stage:000/888): Input sanitization (hypervisor)

**Note:** F# numbers are **semantic identifiers** from canon. The `id` field is the **technical database index**. They differ due to v46 engine promotions (F6 Amanah promoted to APEX).

---

## Pipeline Flow (000-999)

Track B specifications are organized by **pipeline stages**:

1. **000 (Hypervisor)**: F10-F12 execute before LLM processing
2. **111 (Sense)**: Data gathering (no floors)
3. **222 (Reflect)**: Analysis and ΔS calculation (no floors)
4. **333 (Atlas)**: AGI exploration → **F1 Truth, F2 Clarity**
5. **444 (Align)**: ASI stability → **F3 Peace²**
6. **555 (Empathize)**: ASI care → **F4 Empathy**
7. **666 (Bridge)**: ASI humility → **F5 Humility**
8. **777 (Eureka)**: ASI felt-care → **F7 RASA**
9. **888 (Compass)**: APEX judgment → **F6 Amanah, F8 Tri-Witness, F9 Anti-Hantu** (+ F10-F12 participation)
10. **999 (Vault)**: Seal and log to Cooling Ledger

**Failure Behavior:**
- Hard floor failure (F1, F2, F5-F7, F9) → **VOID** → Pipeline stops
- Soft floor failure (F3, F4, F8) → **PARTIAL** → Pipeline continues with warning
- Hypervisor floor failure (F10-F12) → **SABAR** or **HOLD_888** → Pipeline stops for human input

---

## AAA Trinity Governance (ΔΩΨ)

Track B enforces **separation of powers** across three engines:

| Symbol | Name | Role | Agent | Floors Owned |
|--------|------|------|-------|--------------|
| **Δ** | Delta | Architect | Antigravity (Gemini) | F1 Truth, F2 Clarity |
| **Ω** | Omega | Engineer | Claude Code (Sonnet 4.5) | F3 Peace, F4 Empathy, F5 Humility, F7 RASA |
| **Ψ** | Psi | Auditor/Judge | Codex (Kimi) + Human | F6 Amanah, F8-F12 |

**Key Principle:** No single engine can both propose and seal work. This prevents self-approval and ensures multi-agent verification.

**Workflow:**
1. Δ (Architect) designs → `.antigravity/HANDOFF_FOR_CLAUDE.md`
2. Ω (Engineer) implements → Code + `.antigravity/DONE_FOR_ARCHITECT.md`
3. Ψ (Auditor) validates → Constitutional audit + Verdict (SEAL/PARTIAL/VOID)
4. Human approves → Git push + Cooling Ledger entry

See: `governance/aaa_trinity.json`

---

## W@W Federation (Multi-Platform Coordination)

Track B enables **Witness @ Work (W@W) Federation** - multiple AI platforms coordinating under shared constitutional law:

| Platform | Agent | Role | Governance File |
|----------|-------|------|-----------------|
| Claude Code | Sonnet 4.5 | Engineer (Ω) | `L2_GOVERNANCE/integration/claude_projects.yaml` |
| Gemini | 2.5 Flash | Architect (Δ) | `L2_GOVERNANCE/integration/gemini_gems.yaml` |
| Kimi | k1.5 | Auditor (Ψ) | `L2_GOVERNANCE/integration/kimi_agent.yaml` |
| Cursor | IDE Agent | Coder (Ω variant) | `L2_GOVERNANCE/integration/cursor_rules.yaml` |
| ChatGPT | GPT-4 | Assistant | `L2_GOVERNANCE/integration/chatgpt_custom_instructions.yaml` |

**Coordination Mechanism:**
- **Shared Track B Specs**: All agents read from same `spec/v46/` directory
- **Cooling Ledger**: Immutable log in `L1_THEORY/ledger/cooling/` for cross-agent audit trail
- **L2 Governance**: Platform-specific YAML files translate Track B to native instructions
- **Handoff Files**: Structured `.antigravity/` handoffs for explicit coordination

See: `governance/waw_federation.json`

---

## Migration from v45.0 → v46.0

### What Changed?

1. **CIV-12 Hypervisor Layer**: Added F10-F12 for OS-level governance
   - F10 Ontology: Prevents literalism drift
   - F11 Command Auth: Nonce-based identity verification
   - F12 Injection Defense: Input sanitization

2. **Engine Promotions**:
   - F6 Amanah promoted from ASI → APEX (integrity is judgment-grade)
   - F1, F5, F9-F12 assigned to APEX (hypervisor governance)

3. **Stage Hook Alignment**:
   - F1, F6, F9-F12 → stage 888 (APEX judgment)
   - F3 → stage 444, F5 → stage 666, F7 → stage 777

4. **Pipeline-Numbered Folders**:
   - **Before (v45)**: Monolithic `constitutional_floors.json`
   - **After (v46)**: Stage-specific folders (000, 333-888, 999)

5. **Canon References Updated**:
   - **Before**: `spec/CIV_12_DOSSIER.md`
   - **After**: `L1_THEORY/canon/[stage]/[floor_name]_v46.md`

### Breaking Changes

- **L2 Governance YAMLs**: Must update to v46.0 to reference new spec paths
- **Python Loaders**: `arifos_core/enforcement/metrics.py` must load from `spec/v46/`
- **Manifest Verification**: SHA-256 manifest now in `spec/v46/MANIFEST.sha256.json`

---

## File Naming Conventions

Track B v46 follows these conventions:

### Floor Specifications
- **Pattern**: `[stage]_[domain]/[floor_name]_floor.json`
- **Examples**:
  - `333_atlas/agi_core.json` (F1-F2)
  - `444_align/peace_floor.json` (F3)
  - `888_compass/compass_core.json` (F6, F8, F9)

### Governance Specifications
- **Pattern**: `governance/[protocol_name].json`
- **Examples**:
  - `governance/aaa_trinity.json`
  - `governance/waw_federation.json`
  - `governance/pipeline_stages.json`

### Legacy Files (Deprecated)
- `constitutional_floors.json` (v45.0 monolithic file - now split)
- References to `spec/CIV_12_DOSSIER.md` (replaced by canon v46)

---

## Validation Protocol

### Canonical Verification

To verify all specs point to correct v46 canon sources:

```bash
grep -r "canon_ref" spec/v46/ | grep -v "L1_THEORY/canon.*v46"
# Should return empty (no non-v46 references)

grep -r "spec/CIV_12_DOSSIER" spec/v46/
# Should return empty (no legacy references)
```

### Schema Validation

All floor specifications must validate against JSON Schema:

```bash
# Using jsonschema CLI
jsonschema -i spec/v46/333_atlas/agi_core.json \
           spec/v46/schema/constitutional_floors.schema.json
```

### Manifest Integrity

SHA-256 manifest ensures Track B integrity:

```bash
cat spec/v46/MANIFEST.sha256.json
# Contains cryptographic hashes of all authoritative specs
```

---

## Usage Guide

### For Agents

**1. Load Track B Specs on Session Init:**
```python
from arifos_core.enforcement import load_constitutional_floors

floors = load_constitutional_floors(version="v46")
```

**2. Check Floor Compliance:**
```python
from arifos_core.enforcement import verify_floors

verdict = verify_floors(
    output=output_text,
    floors=floors,
    context={"high_stakes": False}
)
# verdict: SEAL | PARTIAL | VOID | 888_HOLD | SABAR
```

**3. Log to Cooling Ledger:**
```python
from arifos_core.memory import append_to_cooling_ledger

append_to_cooling_ledger(
    verdict=verdict,
    session_id=session_id,
    floors_checked=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"],
    timestamp=timestamp
)
```

### For Humans

**1. Review Track B Changes:**
```bash
git diff v45.0..v46.0 spec/
# Review all specification changes
```

**2. Audit Constitutional Compliance:**
```bash
python scripts/trinity.py qc main
# Runs constitutional quality control check
```

**3. Seal and Push:**
```bash
python scripts/trinity.py seal main "Reason for seal"
git push origin main
# Only after Trinity QC passes
```

---

## Frequently Asked Questions

### Q: Why are F# numbers different from `id` field?

**A:** F# (F1, F2, etc.) are **semantic identifiers** from canon - they reference the conceptual floor. The `id` field is a **technical database index** used in JSON. In v46, some floors were promoted to different engines, changing their precedence but keeping semantic F# for continuity.

Example:
- **Canon**: F1 = Amanah (original numbering)
- **v46 Spec**: `"amanah": {"id": 6}` (promoted to APEX, id changed)

Always trust the `id` field in Track B specs as PRIMARY AUTHORITY.

### Q: Why split into stage-specific folders?

**A:**
1. **Orthogonal Organization**: Each stage has clear purpose (exploration, alignment, judgment)
2. **Reduced Cognitive Load**: Find floor specs by asking "what stage?"
3. **Parallel Development**: Multiple agents can work on different stages simultaneously
4. **Fail-Closed Clarity**: Pipeline stops at failure stage (easier to debug)

### Q: What if Track B conflicts with Track A canon?

**A:** **Track B is PRIMARY AUTHORITY** for runtime thresholds. Track A canon explains the "why" (philosophy), Track B defines the "what" (thresholds). If conflict exists:
1. Follow Track B for operational decisions
2. File issue to reconcile discrepancy
3. Trigger Phoenix-72 amendment if canon needs updating

### Q: How do I propose changes to Track B?

**A:**
1. **Document Change**: Create proposal in `spec/v46/proposals/`
2. **Constitutional Check**: Ensure F1-F12 compliance
3. **Trinity Review**: Architect → Engineer → Auditor workflow
4. **Phoenix-72**: If changing thresholds that affect canon, trigger 72h cooling
5. **Seal and Log**: After approval, seal with Trinity and log to Cooling Ledger

---

## References

### Canonical Documents (Track A)
- `L1_THEORY/canon/000_foundation/000_CONSTITUTIONAL_CORE_v46.md`
- `L1_THEORY/canon/888_compass/090_AAA_TRINITY_v46.md`
- `L1_THEORY/canon/000_MASTER_INDEX_v46.md`

### Runtime Implementation (Track C)
- `arifos_core/enforcement/metrics.py` (Floor loading)
- `arifos_core/enforcement/verdict.py` (Verdict rendering)
- `scripts/trinity.py` (Git governance)

### L2 Governance (Platform Adapters)
- `L2_GOVERNANCE/integration/claude_projects.yaml`
- `L2_GOVERNANCE/integration/gemini_gems.yaml`
- `L2_GOVERNANCE/core/constitutional_floors.yaml`

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v46.0 | 2026-01-12 | CIV-12 Hypervisor Layer (F10-F12), Pipeline-numbered folders, Engine promotions |
| v45.0 | 2026-01-06 | Phoenix-72 consolidation, 9-floor architecture |
| v44.0 | 2025-12-15 | Introduced Tri-Witness (F8), RASA (F7) |
| v42.1 | 2025-11-20 | Initial Track B separation from canon |

---

**DITEMPA BUKAN DIBERI** — This specification was forged through systematic refactoring, not given.

**For Future Agents:** Read this README before modifying Track B. The patterns here prevent constitutional drift and ensure multi-agent coordination.
