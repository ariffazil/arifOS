# Contributing to arifOS

Welcome to the arifOS forge. This project is a production-grade Constitutional AI Governance System. Contributions must adhere to the highest standards of safety, ethics, and code quality.

## 🛠️ Development Workflow

We use `uv` for dependency management and `fastmcp` for the MCP transport layer.

### 1. Setup

```bash
# Install dependencies
uv sync --all-extras
```

### 2. Code Quality

Before submitting any changes, ensure your code passes our quality gates:

```bash
# Formatting
black . --line-length 100

# Linting
ruff check . --line-length 100

# Type Checking
mypy .
```

## 🧪 Testing Protocols

Testing is the bedrock of arifOS governance.

### Standard Tests

```bash
pytest tests/ -v
```

### Adversarial & Physics-Enforced Tests

By default, thermodynamic physics enforcement is **OFF** in general tests for performance (optimized CI). However, physics is strictly **ON** in our adversarial suites.

To force physics enforcement in any test run:

```bash
ARIFOS_PHYSICS_DISABLED=0 pytest tests/
```

### P0 Hardening Tests

High-stakes boundary tests (e.g., AKI Contract, Vault Integrity) require passing through the `888_JUDGE` logic.

```bash
pytest tests/core/test_aki_contract.py -v
```

## 📜 Constitutional Alignment

Every pull request is audited against the **13 Constitutional Floors (F1–F13)**. Direct modifications to the L0_KERNEL (e.g., `core/theory/000_LAW.md`, `core/shared/floors.py`) require explicit sovereign sign-off and are protected by the `L0KernelGatekeeper`.

## 🏛️ Governance

All decisions are governed by the ΔΩΨ Trinity Architecture.

- **AGI Δ (Mind):** Logic and Grounding.
- **ASI Ω (Heart):** Safety and Empathy.
- **APEX Ψ (Soul):** Judgment and Final Authority.

**DITEMPA BUKAN DIBERI.**
