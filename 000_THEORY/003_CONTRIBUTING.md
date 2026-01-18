# Contributing to arifOS

Thank you for considering a contribution to arifOS. This guide explains how to contribute safely and in a way that preserves the constitutional governance of the system.

If you contribute code, documentation, tests, or governance proposals, you agree to the contributor guidelines in this file and the governance rules in GOVERNANCE.md.

---

## Quick overview

Before submitting any change, ensure it:
- Preserves the 9 constitutional floors operationally (see GOVERNANCE.md).
- Does not bypass or disable APEX PRIME, the Amanah lock, the Cooling Ledger, or the Memory Write Policy (EUREKA).
- Respects the 000→999 pipeline ordering (no skipping stages).
- Does not allow VOID verdicts to become canonical memory.
- Follows the Phoenix‑72 amendment process for changes to constitutional rules or memory bands.

---

## 1) Opening an issue

Open an issue describing:
- What you want to change (bug fix / feature / refactor).
- Why it matters to arifOS governance.
- How it affects the 9 floors, the 000→999 pipeline, or the 6 Memory Bands.

Issue template suggestion:

```markdown
## Change Summary
[What are you proposing?]

## Constitutional Impact (F1-F9)
- [ ] Affects F1: Amanah (Integrity/Reversibility)
- [ ] Affects F2: Truth (Factual Accuracy ≥0.99)
- [ ] Affects F3: Tri-Witness (Human·AI·Earth consensus ≥0.95)
- [ ] Affects F4: ΔS/Clarity (Entropy reduction ≥0)
- [ ] Affects F5: Peace² (Non-destructive ≥1.0)
- [ ] Affects F6: κᵣ/Empathy (Serve weakest stakeholder ≥0.95)
- [ ] Affects F7: Ω₀/Humility (Uncertainty band 0.03-0.05)
- [ ] Affects F8: G/Genius (Governed intelligence ≥0.80)
- [ ] Affects F9: C_dark/Anti-Hantu (Dark cleverness <0.30)

## Memory Impact (EUREKA - v45)
- [ ] Affects Memory Write Policy (verdict → band routing)
- [ ] Changes 6 Memory Bands (VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID)
- [ ] Modifies Authority Boundary (human seal enforcement)
- [ ] Changes Audit Layer (SHA-256 hash-chain or Merkle proofs)
- [ ] Affects Retention Lifecycle (HOT 7d / WARM 90d / COLD permanent / VOID 90d)
- [ ] Impacts ΔΩΨ Trinity (Delta lane routing, Omega aggregation, Psi vitality)

## Justification
[Why is this change aligned with arifOS governance?]

## Test Plan
[How will you verify this maintains all floors and memory invariants?]
```

---

## 2) Branch naming

Create topic branches using this convention:
- **apex/** — APEX PRIME judiciary changes
- **ledger/** — Cooling Ledger or Vault-999 changes
- **memory/** — Memory Write Policy (EUREKA) or band routing changes (v38)
- **guard/** — Safeguards or guard constraints
- **docs/** — Documentation
- **tests/** — Tests
- **fix/** — Bug fixes
- **refactor/** — Non-functional refactors

Examples:
```bash
git checkout -b apex/fix-verdict-threshold
git checkout -b memory/void-band-isolation
git checkout -b ledger/hash-chain-verification
```

---

## 3) Development workflow

Install dev deps and run tests:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .[dev]
pre-commit install
pytest -v
```

Linters and type checks:
```bash
black .
isort .
mypy .
ruff
flake8
pre-commit run --all-files
```

Memory-specific validation (v38):
```bash
# Test memory write policy enforcement
pytest tests/test_memory_policy.py -v

# Test 6 memory bands + routing
pytest tests/test_memory_bands.py -v

# Test authority boundary (humans seal law)
pytest tests/test_memory_authority.py -v

# Test hash-chain + retention lifecycle
pytest tests/test_memory_retention.py -v

# Full memory + floor integration
pytest tests/integration/test_memory_floor_integration.py -v
```

**Do not:**
- Commit secrets or private keys. Use environment variables or your org's secret manager.
- Allow VOID verdicts to be written to LEDGER or ACTIVE bands (VOID → VOID band only).
- Disable hash-chain verification in audit layer.
- Modify authority boundary without Phoenix-72 amendment process.

---

## 4) Commit messages

Use a concise scope: summary format:
```
scope: brief description

Optional longer explanation and issue references.
```

Examples:
```
apex: fix verdict threshold edge case at Ψ == 1.0
ledger: add canonical JSON serialization before hashing
memory: enforce VOID verdict isolation from canonical bands
memory: add confidence ceiling (0.85) to recalled state
```

---

## 5) Pull Requests (PRs)

Before creating a PR:
- Run all tests and linters locally.
- Ensure no secrets or keys in commits.
- Add or update tests for your change (see section 7).
- Update documentation where applicable (README.md, docs/, canon/).
- For memory changes: verify no VOID verdicts escape to canonical bands.

PR template suggestion:

```markdown
## What This PR Does
[Clear description]

## Constitutional Impact
- [ ] Preserves all 9 floors
- [ ] Does not bypass APEX PRIME
- [ ] Maintains Amanah lock
- [ ] Adds or improves tests
- [ ] Updates documentation

## Memory Impact (EUREKA - v45)
- [ ] Memory Write Policy enforced (verdict → band routing)
- [ ] VOID verdicts isolated (never reach LEDGER/ACTIVE)
- [ ] Authority boundary maintained (humans seal law)
- [ ] SHA-256 hash-chain verified on all writes
- [ ] Confidence ceiling (0.85) enforced on recalls
- [ ] Memory integration tests added/pass (2359/2359 ✓)
- [ ] Spec manifest verified: python scripts/regenerate_manifest_v45.py --check

## Test Coverage
- Tests added: [describe]
- Existing tests passing: ✅
- Memory integration tests: ✅
- Hash-chain verification: ✅

## Breaking Changes?
- [ ] No
- [ ] Yes — Phoenix-72 amendment required

## Checklist
- [ ] Code follows style guide (black, isort)
- [ ] Type checks pass (mypy)
- [ ] All tests pass (pytest) including memory tests
- [ ] Documentation updated (README.md, docs/, canon/)
- [ ] No secrets or keys committed
- [ ] Memory-related changes reviewed for governance impact
```

---

## 6) Code review & approvals

### Standard Reviews
- PRs touching APEX, Ledger, Vault‑999, or guard modules require approval by designated code owners.
- Expect requests for additional tests and governance impact analysis.
- Do not force-push reviewed branches; push new commits to address feedback.

### Memory-Specific Reviews (EUREKA - v45)
- PRs touching `arifos_core/memory/` or memory integration require:
  - Confirmation that VOID verdicts cannot reach canonical bands (INV-1).
  - Verification that authority boundary is maintained—AI proposes, humans seal (INV-2).
  - SHA-256 hash-chain audit trail for every write (INV-3).
  - Confidence ceiling validation for recalled memory (INV-4).
  - Evidence of integration with 000→999 pipeline stages (SENSE 111, FORGE 777, JUDGE 888, SEAL 999).
  - Spec integrity: Verify spec/v45/MANIFEST.sha256.json after changes.

Suggested CODEOWNERS entries should be added to `CODEOWNERS` separately.

---

## 7) Tests required

Every change should include:
- Unit tests for modified functions/classes.
- Integration tests for cross-module behavior.
- Edge/corner-case tests for thresholds and invariants.
- Security tests for crypto, ledger, or access control changes.

### Memory-Specific Tests (v38)

If you modify memory code:

**Test VOID isolation (INV-1):**
```python
def test_void_verdict_never_canonical():
    """VOID verdicts routed to VOID band only, never LEDGER/ACTIVE."""
    policy = MemoryWritePolicy()
    band = policy.route_verdict("VOID", content="test")
    assert band == BandType.VOID
    assert "LEDGER" not in policy.get_canonical_targets("VOID")
```

**Test authority boundary (INV-2):**
```python
def test_authority_boundary_humans_seal():
    """AI proposes amendments; humans seal law."""
    check = MemoryAuthorityCheck()
    proposal = check.propose_amendment(new_rule)
    assert proposal.sealed == False  # AI cannot self-seal
    check.seal_amendment(proposal, human_key)  # Human seals
    assert proposal.sealed == True
```

**Test hash-chain integrity (INV-3):**
```python
def test_ledger_hash_chain_unbroken():
    """Every ledger entry links to previous; chain is verifiable."""
    audit = MemoryAuditLayer()
    entry1 = audit.record_write("decision_1", metadata)
    entry2 = audit.record_write("decision_2", metadata)
    assert entry2.previous_hash == entry1.content_hash
    assert audit.verify_chain() == True  # Chain unbroken
```

**Test confidence ceiling (INV-4):**
```python
def test_memory_recall_confidence_ceiling():
    """Recalled memory capped at 0.85 confidence (suggestion, not oracle)."""
    sense = MemorySense()
    recalled = sense.recall_state(session_id, confidence_threshold=0.85)
    assert recalled.confidence <= 0.85
    assert recalled.metadata["recalled_as"] == "suggestion"
```

**Test retention lifecycle:**
```python
def test_warm_band_90_day_retention():
    """LEDGER/PHOENIX/WITNESS bands retain 90 days, then cool."""
    retention = MemoryRetention()
    entry = retention.write(band=BandType.LEDGER, content)
    assert retention.should_retain(entry, days=89) == True
    assert retention.should_retain(entry, days=91) == False  # Cooled
```

Example full memory test name:
```python
def test_memory_write_policy_seal_verdict_routes_to_ledger_and_active():
    """SEAL verdicts route to LEDGER + ACTIVE; PARTIAL to PHOENIX only."""
```

---

## 8) Security & reporting

If your change touches security-sensitive code (APEX, ledger, memory, keys):
- Include a security rationale and a brief threat model.
- For memory changes: explain how INV-1 through INV-4 are preserved.
- Test for hash-chain breakage, VOID leakage, or authority bypass.

Security contact for reporting: arifbfazil@gmail.com  
Preferred: open a private GitHub Security Advisory.

Do not include PoCs in public issues—use private advisories or encrypted email. See SECURITY.md for full policy.

---

## 9) Amendment process (Phoenix-72)

If a change modifies:
- Any of the 9 Floors
- The 000→999 pipeline stages
- APEX PRIME verdict logic
- Amanah lock enforcement
- Cooling Ledger format
- **Memory Write Policy (EUREKA)** (v38)
- **Any of the 6 Memory Bands** (v38)
- **Authority Boundary enforcement** (v38)

Follow Phoenix‑72:
1. Create an `[AMENDMENT]` issue, tag `constitutional-change`.
2. Provide: spec, impact analysis, migration plan, test coverage.
3. Obtain Tri‑Witness consensus (human, AI, Earth/domain expert).
4. Seal the amendment in Vault‑999 via human approval.
5. Update canon (e.g., `canon/ARIFOS_MEMORY_STACK_v38Omega.md` for memory changes).

---

## 10) Documentation & style

- Update **README.md** for user-facing changes.
- Update **docs/** for architecture changes.
- Update **spec/v45/*.json** for Track B specification changes (requires manifest regeneration).
- Update **L1_THEORY/canon/** for constitutional law changes (requires Phoenix-72 amendment).
- Update **CLAUDE.md** for development workflow changes.
- Update **AGENTS.md** for agent governance changes.
- Use docstrings on public APIs.
- Maintain **CHANGELOG.md** and release notes.

---

## 11) Conduct & recognition

- Be respectful and inclusive.
- Criticize ideas, not people.
- Contributors are recognized in CONTRIBUTORS.md and release notes.

Security/governance questions:
- Governance: open an issue with `[QUESTION]`.
- Security: use Security Advisory or email above.
- Memory/EUREKA: open an issue with `[MEMORY]` or contact maintainer.

---

**Last updated:** 2025-12-29
**Version:** v45.0.0 (Phoenix-72 Consolidation)
**Maintainer contact:** arifbfazil@gmail.com
**Track B Spec:** spec/v45/ (SHA-256 verified) | **Canon:** L1_THEORY/canon/ (v45)
**Memory System (EUREKA):** Active | 4 Core Invariants enforced | 6 Memory Bands | 2359/2359 tests passing
