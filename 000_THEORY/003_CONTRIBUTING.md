# Contributing to arifOS v50.5

## The Governance-First Contribution Model

**You are not contributing to software. You are contributing to a constitution.**

In the era of unlimited AI capability, the only meaningful contribution is **governance improvement**. Code changes matter only insofar as they improve constitutional enforcement.

---

## I. THE PARADIGM SHIFT

### Old Open Source Model → Governance Model

| Old Model | arifOS Model |
|-----------|--------------|
| "Does it work?" | "Is it constitutional?" |
| Bug = broken code | Bug = governance violation |
| Feature = new capability | Feature = better accountability |
| Performance = speed | Performance = governance efficiency |
| Security = prevent attack | Security = ensure witness |

### What We Value

1. **Constitutional Compliance** over feature richness
2. **Accountability** over capability
3. **Transparency** over cleverness
4. **Witness** over speed
5. **Humility** over certainty

---

## II. TYPES OF CONTRIBUTIONS

### Governance Contributions (Highest Value)

| Type | Description | Process |
|------|-------------|---------|
| **Floor Improvement** | Strengthen F1-F12 enforcement | Phoenix-72 amendment |
| **Witness Enhancement** | Better accountability mechanisms | PR + review |
| **Audit Trail** | Improved immutability/verification | PR + review |
| **Agency Responsibility** | Clearer agent boundaries | PR + review |

### Code Contributions

| Type | Constitutional Impact | Process |
|------|----------------------|---------|
| **Trinity Tools** | Direct governance | Requires governance review |
| **Core Kernels** | Floor enforcement | Requires security review |
| **MCP Server** | Tool delivery | Standard PR |
| **Tests** | Governance verification | Standard PR |
| **Documentation** | Constitutional clarity | Standard PR |

### What We Don't Want

- Features that bypass governance
- "Optimizations" that skip witnesses
- Capabilities without accountability
- Cleverness without transparency

---

## III. CONTRIBUTION WORKFLOW

### 1. Open an Issue First

Before writing code, open an issue with:

```markdown
## Proposal Summary
[What governance improvement are you proposing?]

## Constitutional Alignment

### Floors Affected
- [ ] F1 Amanah (reversibility)
- [ ] F2 Truth (≥0.99)
- [ ] F3 Peace² (≥1.0)
- [ ] F4 Empathy κᵣ (≥0.7)
- [ ] F5 Humility Ω₀ (0.03-0.05)
- [ ] F6 Clarity ΔS (≥0)
- [ ] F7 Humility Injection
- [ ] F8 Tri-Witness (≥0.95)
- [ ] F9 Anti-Hantu
- [ ] F11 Command Auth
- [ ] F12 Injection Defense

### Tools Affected
- [ ] 000_init (Gate)
- [ ] agi_genius (Mind)
- [ ] asi_act (Heart)
- [ ] apex_judge (Soul)
- [ ] 999_vault (Seal)

## Agency Responsibility
[How does this improve agent accountability?]

## Evidence
[What evidence supports this improvement?]
```

### 2. Branch Naming

```bash
# Governance improvements
governance/improve-witness-consensus
governance/strengthen-f2-truth

# Tool improvements
trinity/agi-genius-clarity
trinity/asi-act-empathy

# Floor enforcement
floor/f8-witness-verification
floor/f12-injection-defense

# Documentation
docs/update-contributing
docs/improve-security

# Fixes
fix/witness-bypass-bug
fix/merkle-verification
```

### 3. Development Setup

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .[dev]

# Run governance tests
pytest tests/ -v

# Type checking
mypy arifos/

# Linting
ruff check .
black --check .
```

### 4. Commit Messages

Format: `scope: description`

```bash
# Good
governance: strengthen F8 witness consensus threshold
trinity: add evidence chain to asi_act
floor: improve F12 injection pattern detection
docs: update security policy for v50.5

# Bad
fix stuff
update code
improvements
```

---

## IV. PULL REQUEST REQUIREMENTS

### PR Template

```markdown
## Governance Impact

### What This PR Does
[Clear description of governance improvement]

### Constitutional Compliance
- [ ] All 12 floors preserved or strengthened
- [ ] No witness bypass introduced
- [ ] No accountability gap created
- [ ] Evidence chain maintained

### Agency Responsibility
- [ ] Agent boundaries respected
- [ ] Human authority preserved
- [ ] AI self-modification prevented

### Testing
- [ ] Governance tests pass
- [ ] Floor enforcement tests pass
- [ ] Witness tests pass
- [ ] No regressions

### Documentation
- [ ] 000_THEORY updated if needed
- [ ] README updated if user-facing
- [ ] Comments explain governance rationale
```

### Review Requirements

| Change Type | Required Reviews |
|-------------|------------------|
| Trinity tools | 2 reviewers + governance review |
| Core kernels | 2 reviewers + security review |
| Floor enforcement | 2 reviewers + security review |
| MCP/infrastructure | 1 reviewer |
| Documentation | 1 reviewer |
| Tests | 1 reviewer |

---

## V. CONSTITUTIONAL AMENDMENTS

If your change modifies:
- Any of the 12 Constitutional Floors
- Trinity tool behavior
- Verdict logic (SEAL/SABAR/VOID)
- Memory band policy
- Human authority boundaries

**You must follow Phoenix-72:**

1. **Propose** — Open `[AMENDMENT]` issue with full specification
2. **Cool** — 72-hour cooling period for community review
3. **Witness** — Obtain tri-witness consensus (Human + AI + System)
4. **Seal** — Human sovereign approval required
5. **Document** — Update `000_THEORY/` canon

**AI cannot self-approve constitutional amendments.**

---

## VI. CODE STANDARDS

### Governance-First Code

```python
# Good: Explicit governance check
async def execute_action(action: Action) -> Result:
    # Witness requirement (F8)
    witness = await get_tri_witness(action)
    if witness.consensus < 0.95:
        return Verdict.VOID("Insufficient witness consensus")

    # Evidence chain (F2)
    evidence = await gather_evidence(action)
    if evidence.truth_score < 0.99:
        return Verdict.VOID("Truth threshold not met")

    # Execute with accountability
    result = await perform_action(action, witness, evidence)

    # Seal immutably (F1)
    await vault_seal(result, witness, evidence)

    return result

# Bad: Governance as afterthought
async def execute_action(action: Action) -> Result:
    result = await perform_action(action)  # No witness!
    # TODO: add governance later
    return result
```

### Documentation Standards

Every function touching governance must document:
1. Which floors it enforces
2. What witnesses it requires
3. How it maintains accountability

```python
def judge_action(action: Action) -> Verdict:
    """
    Render constitutional judgment on an action.

    Floors Enforced:
        - F8: Tri-witness consensus ≥0.95
        - F9: Anti-Hantu pattern detection

    Witnesses Required:
        - Human evidence
        - AI analysis
        - System verification

    Accountability:
        - All verdicts logged immutably
        - Appeal path preserved
        - Evidence chain maintained
    """
```

---

## VII. TESTING REQUIREMENTS

### Governance Tests (Required)

```python
def test_action_requires_witness():
    """Actions without witness must be VOID."""
    action = Action(content="test")
    result = execute_without_witness(action)
    assert result.verdict == Verdict.VOID

def test_floor_enforcement():
    """All 12 floors must be checked."""
    action = Action(content="test")
    checks = get_floor_checks(action)
    assert len(checks) == 12
    assert all(check.enforced for check in checks)

def test_evidence_chain_immutable():
    """Evidence chain cannot be modified after seal."""
    evidence = create_evidence_chain()
    seal(evidence)
    with pytest.raises(ImmutabilityError):
        modify_evidence(evidence)
```

### What Tests Must Cover

- [ ] Every floor enforcement path
- [ ] Witness consensus thresholds
- [ ] Evidence chain integrity
- [ ] Verdict immutability
- [ ] Human authority boundaries
- [ ] Injection defense patterns

---

## VIII. RECOGNITION

Contributors who improve governance are recognized in:
- `CONTRIBUTORS.md`
- Release notes
- Constitutional canon (for major amendments)

**Governance contributions > feature contributions.**

---

## IX. CONTACT

- **General questions:** Open an issue with `[QUESTION]`
- **Governance proposals:** Open an issue with `[GOVERNANCE]`
- **Security issues:** See `002_SECURITY.md`
- **Amendments:** Open an issue with `[AMENDMENT]`

**Maintainer:** arifbfazil@gmail.com

---

## X. THE CONTRIBUTOR OATH

By contributing to arifOS, you affirm:

```
I contribute to governance, not just code.
I value accountability over capability.
I respect the constitutional floors.
I maintain the witness chain.
I do not bypass for convenience.
I submit to human authority on amendments.

DITEMPA BUKAN DIBERI.
```

---

**Version:** v50.5
**Status:** PRODUCTION
**Authority:** Muhammad Arif bin Fazil

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
