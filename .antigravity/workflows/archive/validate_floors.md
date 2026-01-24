---
description: Constitutional validation before git push (Trinity QC)
---

# /gitQC - Constitutional Quality Control

**Pipeline Stage:** 888 ATTEST
**Territory:** APEX (Ψ Psi - Architect/All)
**Function:** Validate F1-F12 constitutional compliance before pushing
**Authority:** AGENTS.md - Trinity Git Governance

---

## Purpose

Constitutional validation of all changes before pushing to ensure F1-F12 floor compliance, entropy thresholds, and governance requirements are met.

**Part of Trinity Git Governance:**
1. `/gitforge` - Analyze entropy and hot zones
2. **`/gitQC`** - Validate constitutional compliance ← YOU ARE HERE
3. `/gitseal` - Seal with human authority

**When to Use:**
- Before pushing to remote
- After `/gitforge` shows acceptable entropy
- Before requesting code review
- Before merging to main branch
- After major refactoring

---

## Constitutional Validation (F1-F12)

### Hypervisor Floors (F10-F12)
**Pre-execution validation:**

```
F12 (Injection Defense):
- No eval(), exec(), or system() calls without justification
- No user input directly in SQL/shell commands
- Pattern scanning for injection vulnerabilities

F11 (Command Auth):
- Nonce verification for identity reloads
- Channel verification for sensitive operations
- Replay attack prevention

F10 (Ontology):
- Symbolic mode enforcement
- No literalism drift in thermodynamic language
- ΔΩΨ treated as metaphor, not physics
```

### Core Governance Floors (F1-F9)
**Constitutional compliance:**

```
F1 (Truth ≥0.99):
- Documentation matches code
- Comments are accurate
- No misleading variable names
- Test assertions verify claims

F2 (Clarity ΔS ≥0):
- Entropy delta acceptable (ΔS < 5.0)
- Code reduces confusion
- Clear naming conventions
- Adequate documentation

F3 (Peace² ≥1.0):
- No destructive operations without safeguards
- Reversibility maintained
- Breaking changes documented
- Migration paths provided

F4 (κᵣ Empathy ≥0.95):
- User-facing changes consider impact
- Error messages are helpful
- Accessibility maintained
- Weakest stakeholder protected

F5 (Ω₀ Humility 0.03-0.05):
- Uncertainty acknowledged in comments
- Assumptions documented
- Known limitations stated
- TODOs for unknowns

F6 (Amanah - LOCK):
- All changes reversible
- No silent failures
- Audit trail complete
- Authority boundaries respected

F7 (RASA):
- Code reviews requested
- Feedback incorporated
- Active listening to concerns
- Stakeholder input sought

F8 (Tri-Witness ≥0.95):
- Tests verify behavior
- Documentation confirms intent
- Code review validates quality
- Three-way consensus

F9 (Anti-Hantu):
- No AI consciousness claims in comments
- No anthropomorphization in docs
- Clear agent/human boundaries
```

---

## Execution Steps

// turbo-all

### 1. Run Trinity QC Script
```bash
python scripts/trinity.py qc <branch>
```

**What it checks:**
- Constitutional floor compliance (F1-F12)
- Entropy thresholds (ΔS < 5.0)
- Test coverage (≥80% for core modules)
- Documentation completeness
- Breaking change detection
- Security vulnerabilities

### 2. Review QC Report
```
Constitutional QC Report:
========================

Branch: feature/new-architecture
Commits: 12
Files Changed: 45
Lines Added: 2,340
Lines Deleted: 890

FLOOR VALIDATION:
-----------------
✅ F1 (Truth): 0.99 - PASS
✅ F2 (Clarity): ΔS = 3.2 - PASS
✅ F3 (Peace²): 1.0 - PASS
✅ F4 (Empathy): 0.96 - PASS
✅ F5 (Humility): Ω₀ = 0.041 - PASS
✅ F6 (Amanah): LOCK verified - PASS
✅ F7 (RASA): Reviews requested - PASS
✅ F8 (Tri-Witness): 0.97 - PASS
✅ F9 (Anti-Hantu): No violations - PASS
✅ F10 (Ontology): Symbolic mode - PASS
✅ F11 (Command Auth): Nonces valid - PASS
✅ F12 (Injection): No vulnerabilities - PASS

ENTROPY ANALYSIS:
-----------------
ΔS (Entropy Delta): 3.2 (ACCEPTABLE)
Hot Zones: 2 files
Risk Score: 0.35 (LOW)

TEST COVERAGE:
--------------
Core Modules: 87% (PASS - ≥80%)
New Code: 92% (EXCELLENT)
Integration Tests: 15 passing

DOCUMENTATION:
--------------
README updated: ✅
CHANGELOG updated: ✅
API docs: ✅
Architecture docs: ✅

SECURITY:
---------
Injection vulnerabilities: 0
Unsafe operations: 0
Dependency vulnerabilities: 0

VERDICT: ✅ SEAL (All floors passed)
```

### 3. Address Any Violations
```
If SABAR or VOID:
1. Review failed floors
2. Fix violations
3. Re-run /gitQC
4. Repeat until SEAL
```

### 4. Proceed to Seal
```
If SEAL verdict:
→ Ready for /gitseal
→ Human authority can approve
→ Safe to push
```

---

## Constitutional Floors

**Primary Floors:**
- **F1-F12:** All constitutional floors validated
- **F8 (Audit):** Complete validation trail

**Enforcement:**
- **Fail-Closed:** Any floor failure → VOID (block push)
- **Human Override:** Only via `/gitseal APPROVE` with justification

---

## Example Usage

**Scenario:** Validate architecture refactoring before push

```
/gitQC

Running Constitutional QC...
Branch: refactor/sovereign-extraction
Analyzing 47 files, 3,200 lines changed...

⚠️ SABAR ISSUED:

FLOOR VIOLATIONS:
-----------------
❌ F2 (Clarity): ΔS = 6.8 (FAIL - threshold 5.0)
   - Hot zone: arifos_core/apex/ (15 files changed)
   - Recommendation: Split into smaller commits

⚠️ F5 (Humility): Missing uncertainty in 3 files
   - arifos_core/apex/governance/fag.py:L234 (TODO needed)
   - arifos_core/system/apex_prime.py:L567 (assumption undocumented)
   - tests/test_apex.py:L89 (known limitation not stated)

✅ All other floors: PASS

VERDICT: ⚠️ SABAR (2 floor violations)

RECOMMENDED ACTIONS:
1. Reduce ΔS: Split apex/ changes into separate commit
2. Add F5 compliance: Document uncertainties in 3 files
3. Re-run /gitQC after fixes

BLOCK PUSH: Changes do not meet constitutional requirements
```

**After fixes:**
```
/gitQC

Running Constitutional QC...
Branch: refactor/sovereign-extraction
Analyzing 47 files, 3,200 lines changed...

✅ SEAL VERDICT:

All 12 constitutional floors: PASS
Entropy: ΔS = 4.2 (ACCEPTABLE)
Test coverage: 89% (EXCELLENT)
Documentation: Complete
Security: No vulnerabilities

READY FOR SEAL:
→ Run /gitseal to obtain human authority
→ Safe to push after seal
```

---

## Output Format

```markdown
## Constitutional QC Report

**Branch:** [branch-name]
**Date:** [YYYY-MM-DD HH:MM]
**Commits:** [count]
**Files Changed:** [count]
**Lines:** +[added] -[deleted]

---

### Floor Validation (F1-F12)

| Floor | Name | Score | Status | Notes |
|-------|------|-------|--------|-------|
| F1 | Truth | [0.00-1.00] | [PASS/FAIL] | [Details] |
| F2 | Clarity | ΔS=[value] | [PASS/FAIL] | [Details] |
| F3 | Peace² | [0.00-1.00] | [PASS/FAIL] | [Details] |
| F4 | Empathy | [0.00-1.00] | [PASS/FAIL] | [Details] |
| F5 | Humility | Ω₀=[value] | [PASS/FAIL] | [Details] |
| F6 | Amanah | LOCK | [PASS/FAIL] | [Details] |
| F7 | RASA | [status] | [PASS/FAIL] | [Details] |
| F8 | Tri-Witness | [0.00-1.00] | [PASS/FAIL] | [Details] |
| F9 | Anti-Hantu | [count] | [PASS/FAIL] | [Details] |
| F10 | Ontology | [mode] | [PASS/FAIL] | [Details] |
| F11 | Command Auth | [status] | [PASS/FAIL] | [Details] |
| F12 | Injection | [count] | [PASS/FAIL] | [Details] |

---

### Entropy Analysis
- **ΔS:** [value] ([ACCEPTABLE/HIGH/CRITICAL])
- **Hot Zones:** [count] files
- **Risk Score:** [0.00-1.00] ([LOW/MEDIUM/HIGH])

---

### Test Coverage
- **Core Modules:** [percentage]% ([PASS/FAIL])
- **New Code:** [percentage]%
- **Integration Tests:** [count] passing

---

### Documentation
- [x] README updated
- [x] CHANGELOG updated
- [x] API docs current
- [x] Architecture docs current

---

### Security
- **Injection Vulnerabilities:** [count]
- **Unsafe Operations:** [count]
- **Dependency Vulnerabilities:** [count]

---

### Verdict
[✅ SEAL / ⚠️ SABAR / 🚫 VOID]

**Recommendation:**
[Action to take]
```

---

## Anti-Patterns (Violations)

❌ **Pushing without QC** - violates F6 (Amanah)
❌ **Ignoring SABAR/VOID** - violates F8 (Audit)
❌ **Manual floor override** - violates F1 (Truth)
❌ **Skipping tests** - violates F8 (Tri-Witness)
❌ **Incomplete documentation** - violates F2 (Clarity)

---

## Integration with Trinity

**Standard Trinity Flow:**

```
1. /gitforge          → Analyze entropy
   ↓ (if ΔS acceptable)
2. /gitQC             → Validate F1-F12
   ↓ (if SEAL)
3. /gitseal APPROVE   → Human authority
   ↓
4. git push           → Changes go live
```

**With Cooling:**

```
1. /gitforge          → ΔS = 6.8 (HIGH)
   ↓
2. /cool              → SABAR-72 cooling
   ↓ (after 72h)
3. /gitQC             → Validate F1-F12
   ↓ (if SEAL)
4. /gitseal APPROVE   → Human authority
   ↓
5. git push           → Changes go live
```

---

## Fail-Closed Enforcement

**Default Behavior:**
- Any floor failure → VOID verdict
- VOID verdict → Block push
- Only human authority can override (via `/gitseal` with justification)

**No Bypass:**
- Cannot skip QC
- Cannot auto-approve
- Cannot silence warnings
- Must fix violations or justify override

**Audit Trail:**
- All QC runs logged to THE EYE
- Verdicts recorded in cooling ledger
- Human overrides require written justification

---

**DITEMPA BUKAN DIBERI** - Constitutional compliance is validated, not assumed.

**Version:** v47.0
**Status:** ACTIVE
**Territory:** APEX (Ψ Psi - All Agents)
