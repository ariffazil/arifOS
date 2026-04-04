# Contributing to arifOS
**Authority:** 888_JUDGE | **Version:** 55.2

> **"You are not just contributing to software. You are contributing to a constitution."**

In the era of unlimited AI capability, the only meaningful contribution is **governance improvement**. We value **accountability** over capability, and **witness** over speed.

---

## 🏗️ The 3 Laws of Contribution

1.  **Governance First:** Code changes matter only if they improve constitutional enforcement (F1-F13).
2.  **No Bypass:** You may not add features that skip the **Trinity** checks (Mind, Heart, Soul).
3.  **Witness Everything:** Every action must be logged, verifiable, and reversible (F1).

---

## 🚀 Getting Started

### 1. The Governance Trinity
Before writing code, understand the laws you are enforcing:
*   **The Law:** Explainers in **[`llms.txt`](llms.txt)**.
*   **The Check:** Thresholds in **[`codebase/apex/governance/floors.json`](codebase/apex/governance/floors.json)**.
*   **The Behavior:** Logic in **[`333_APPS/L1_PROMPT/SYSTEM_PROMPT.md`](333_APPS/L1_PROMPT/SYSTEM_PROMPT.md)**.

### 2. Setup
```bash
# Clone & Setup
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate
pip install -e ".[dev]"

# Verify Governance
pytest tests/ -v
```

---

## 🛠️ Contribution Workflow

### Step 1: Governance Check
Ask yourself: *Does this change strengthen or weaken a Constitutional Floor?*
- **Good:** "Strengthening F12 injection regex."
- **Bad:** "Disabling F12 to make it faster." (Will be **VOID**)

### Step 2: Develop
Follow the **Governance-First** coding style:

```python
# ✅ GOOD: Explicit Governance
async def execute_action(action: Action) -> Result:
    # 1. Witness (F8)
    witness = await get_tri_witness(action)
    if witness.consensus < 0.95:
        return Verdict.VOID("Insufficient witness")

    # 2. Evidence (F2)
    if not await verify_truth(action):
        return Verdict.VOID("F2 Violation")

    # 3. Act & Seal (F1)
    return await vault_seal(action, witness)

# ❌ BAD: Blind Execution
async def execute_action(action: Action):
    return run(action) # No witness, no seal!
```

### Step 3: Test
You must prove your code respects the floors.

```bash
# Run the Constitutional Suite
pytest -m constitutional

# Specific Floor Checks
pytest -m f1   # F1 Amanah (Reversibility)
pytest -m f2   # F2 Truth (Factuality)
```

---

## 📜 Pull Request Standards

### Commit Messages
Use meaningful scopes:
- `governance: strengthen F8 witness consensus`
- `trinity: add evidence chain to asi_act`
- `docs: update F12 injection policy`

### PR Checklist
- [ ] No constitutional floor regressions (F1-F13)
- [ ] All 3 Trinity systems (Mind, Heart, Soul) operational
- [ ] Tests pass (`pytest tests/`)
- [ ] No "magic bypasses" or hardcoded overrides

---

## 🤝 The Contributor Oath

By contributing to arifOS, you affirm:

> I contribute to governance, not just code.
> I value accountability over capability.
> I respect the constitutional floors.
> I maintain the witness chain.
> I do not bypass for convenience.
>
> **DITEMPA BUKAN DIBERI.**

---

## 📞 Reporting Issues

- **Governance Proposals:** Open issue with `[GOVERNANCE]`
- **Security Vulnerabilities:** See **[`SECURITY.md`](SECURITY.md)**
- **Bugs:** Open issue with `[BUG]`

**Authority:** Muhammad Arif bin Fazil
**License:** AGPL-3.0 (Constitutional Open Source)
