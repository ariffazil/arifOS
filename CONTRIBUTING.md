# Contributing to arifOS

Thank you for your interest in contributing to arifOS, the Constitutional AI Governance Framework.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- (Optional) Docker for deployment testing

### Setup

```bash
# Clone
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Verify
pytest tests/ -v
```

---

## Development Workflow

1. **Fork** the repository
2. **Branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
3. **Code** your changes (see Code Standards below)
4. **Test** thoroughly:
   ```bash
   pytest tests/ -v
   ```
5. **Commit** with conventional format:
   ```
   feat: add new paradox resolution method
   fix: correct confidence threshold in reason()
   docs: update API reference for _vault_ tool
   test: add tests for equilibrium solver
   ```
6. **Push** and open a Pull Request against `main`

---

## Code Standards

### Constitutional Floor Compliance

All code must pass the 13 constitutional floors. Quick reference:

| Floor | Code Smell | Fix |
|-------|------------|-----|
| F1 Amanah | Mutates input, hidden side effects | Pure functions, explicit returns |
| F2 Truth | Fabricated data, fake metrics | Empty/null when unknown |
| F4 Clarity | Magic numbers, obscure logic | Named constants, clear params |
| F5 Peace | Destructive defaults | Safe defaults, preserve state |
| F7 Humility | False confidence (1.0) | Cap at 0.95, state uncertainty |
| F9 Anti-Hantu | Deceptive naming | Honest names, transparent logic |

### Style

```bash
# Format
black codebase/ --line-length=100

# Lint
ruff check codebase/

# Type check
mypy codebase/ --strict
```

### Architecture Rules

- **Brain/Body separation:** All logic in `codebase/` kernels, MCP bridge is zero-logic wiring
- **No new files without integration:** Every new module must be wired into the existing pipeline
- **Hardened imports:** Use try/except for optional dependencies, never crash on import
- **Verdicts are 3-state:** SEAL, SABAR, VOID. No new verdict types without constitutional amendment.

---

## Testing

```bash
# Full suite
pytest tests/ -v

# Constitutional floor tests
pytest -m constitutional

# Specific floor
pytest -m f1   # F1 Amanah
pytest -m f2   # F2 Truth

# With coverage
pytest tests/ -v --cov=codebase --cov-report=html
```

All PRs must maintain or improve test coverage. No regressions allowed.

---

## Project Structure

```
codebase/
  agi/        # Mind Engine (F2, F4, F7)
  asi/        # Heart Engine (F1, F5, F6)
  apex/       # Soul Engine (F3, F8, F9-F13)
  mcp/        # MCP transport (zero-logic bridge)
  system/     # APEXPrime judge
  enforcement/# Floor validators
tests/        # Test suite
spec/         # Canonical floor definitions (source of truth)
```

---

## Pull Request Checklist

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] No constitutional floor regressions
- [ ] Code formatted with `black`
- [ ] Commit messages follow conventional format
- [ ] New code has tests
- [ ] No secrets or credentials committed

---

## Reporting Issues

Open an issue at [github.com/ariffazil/arifOS/issues](https://github.com/ariffazil/arifOS/issues) with:

1. What you expected
2. What happened
3. Steps to reproduce
4. Python version and OS

---

## License

arifOS is licensed under AGPL-3.0. By contributing, you agree that your contributions will be licensed under the same terms.

---

*DITEMPA BUKAN DIBERI*
