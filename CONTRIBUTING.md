# Contributing to arifOS

Thank you for considering a contribution to arifOS. This guide explains how to contribute safely and in a way that preserves the constitutional governance of the system.

If you contribute code, documentation, tests, or governance proposals, you agree to the contributor guidelines in this file and the governance rules in GOVERNANCE.md.

---

## Quick overview

Before submitting any change, ensure it:
- Preserves the constitutional floors operationally (see GOVERNANCE.md).
- Does not bypass or disable APEX PRIME, the Amanah lock, or the Cooling Ledger.
- Respects the 000→999 pipeline ordering (no skipping stages).
- Follows the Phoenix‑72 amendment process for changes to constitutional rules.

---

## 1) Opening an issue

Open an issue describing:
- What you want to change (bug fix / feature / refactor).
- Why it matters to arifOS governance.
- How it affects the 8 floors or the 000→999 pipeline.

Issue template suggestion:

```
## Change Summary
[What are you proposing?]

## Constitutional Impact
- [ ] Affects Truth floor
- [ ] Affects ΔS (clarity)
- [ ] Affects Peace²
- [ ] Affects κᵣ (empathy)
- [ ] Affects Ω₀ (humility)
- [ ] Affects Amanah (integrity)
- [ ] Affects RASA (felt care)
- [ ] Affects Tri-Witness

## Justification
[Why is this change aligned with arifOS governance?]

## Test Plan
[How will you verify this maintains all floors?]
```

---

## 2) Branch naming

Create topic branches using this convention:
- apex/feature-name — APEX PRIME judiciary changes
- ledger/feature-name — Cooling Ledger or Vault-999 changes
- guard/feature-name — Safeguards or guard constraints
- docs/feature-name — Documentation
- tests/feature-name — Tests
- fix/bug-description — Bug fixes
- refactor/module-name — Non-functional refactors

Example:
```bash
git checkout -b apex/fix-verdict-threshold
```

---

## 3) Development workflow

Install dev deps and run tests:
```bash
python -m venv venv
source venv/bin/activate
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

Do not commit secrets or private keys. Use environment variables or your org’s secret manager.

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
```

---

## 5) Pull Requests (PRs)

Before creating a PR:
- Run all tests and linters locally.
- Ensure no secrets or keys in commits.
- Add or update tests for your change.
- Update documentation where applicable.

PR template suggestion:

```markdown
## What This PR Does
[Clear description]

## Constitutional Impact
- [ ] Preserves all 8 floors
- [ ] Does not bypass APEX PRIME
- [ ] Maintains Amanah lock
- [ ] Adds or improves tests
- [ ] Updates documentation

## Test Coverage
- Tests added: [describe]
- Existing tests passing: ✅

## Breaking Changes?
- [ ] No
- [ ] Yes — Phoenix-72 amendment required

## Checklist
- [ ] Code follows style guide (black, isort)
- [ ] Type checks pass (mypy)
- [ ] All tests pass (pytest)
- [ ] Documentation updated
- [ ] No secrets or keys committed
```

---

## 6) Code review & approvals

- PRs touching APEX, Ledger, Vault‑999, or guard modules require approval by designated code owners.
- Expect requests for additional tests and governance impact analysis.
- Do not force-push reviewed branches; push new commits to address feedback.

Suggested CODEOWNERS entries should be added to `CODEOWNERS` separately.

---

## 7) Tests required

Every change should include:
- Unit tests for modified functions/classes.
- Integration tests for cross-module behavior.
- Edge/corner-case tests for thresholds and invariants.
- Security tests for crypto, ledger, or access control changes.

Example test name:
```python
def test_apex_judge_truth_floor_breach():
    """APEX returns VOID when Truth < 0.99."""
```

---

## 8) Security & reporting

If your change touches security-sensitive code (APEX, ledger, keys), include a security rationale and a brief threat model.

Security contact for reporting: arifbfazil@gmail.com  
Preferred: open a private GitHub Security Advisory.

Do not include PoCs in public issues—use private advisories or encrypted email. See SECURITY.md for full policy.

---

## 9) Amendment process (Phoenix-72)

If a change modifies:
- Any of the 8 Floors
- The 000→999 pipeline
- APEX verdict logic
- Amanah lock enforcement
- Cooling Ledger format

Follow Phoenix‑72: create an `[AMENDMENT]` issue, tag `constitutional-change`, provide spec/impact/migration, obtain Tri‑Witness consensus, then seal the amendment in Vault‑999.

---

## 10) Documentation & style

- Update README.md for user-facing changes.
- Update `spec/APEX_PRIME.yaml` for judiciary changes.
- Use docstrings on public APIs and maintain changelog/release notes.

---

## 11) Conduct & recognition

- Be respectful and inclusive.
- Criticize ideas, not people.
- Contributors are recognized in CONTRIBUTORS.md and release notes.

Security/governance questions:
- Governance: open an issue with `[QUESTION]`.
- Security: use Security Advisory or email above.

**Last updated:** 2025-11-24  
**Maintainer contact:** arifbfazil@gmail.com
