# arifOS PyPI Publication Guide

**Version:** 2026.03.07 (P3 Thermodynamic Hardening Seal)  
**Package:** `arifos`  
**License:** AGPL-3.0-only

---

## Pre-Publication Checklist

### ✅ Build Verification

```bash
# Clean build artifacts
rm -rf dist/ *.egg-info/

# Build the package
python -m build

# Verify wheel contents
unzip -l dist/arifos-2026.3.7-py3-none-any.whl | head -50
```

**Expected outputs:**
- `dist/arifos-2026.3.7.tar.gz` (~865 KB)
- `dist/arifos-2026.3.7-py3-none-any.whl` (~1.37 MB)

**Required packages in wheel:**
- ✅ `core/` - Constitutional kernel
- ✅ `aaa_mcp/` - FastMCP transport adapter
- ✅ `arifos_aaa_mcp/` - Canonical PyPI entry point
- ✅ `aclip_cai/` - Intelligence layer

### ✅ Test Installation

```bash
# Create fresh venv
python -m venv /tmp/test_arifos
source /tmp/test_arifos/bin/activate  # Windows: .\tmp\test_arifos\Scripts\activate

# Install from wheel
pip install dist/arifos-2026.3.7-py3-none-any.whl

# Verify imports
python -c "from arifos_aaa_mcp import create_aaa_mcp_server; print('✓ arifos_aaa_mcp')"
python -c "from core.governance_kernel import GovernanceKernel; print('✓ core')"
python -c "from aaa_mcp.server import mcp; print('✓ aaa_mcp')"
python -c "from aclip_cai.triad import anchor; print('✓ aclip_cai')"

# Test CLI entry point
arifos --help
```

### ✅ Version Verification

```bash
# Check version
python -c "import arifos_aaa_mcp; print(arifos_aaa_mcp.__version__)"
# Expected: 2026.03.07
```

---

## Publication Steps

### Step 1: Configure PyPI Credentials

**Option A: Using API Token (Recommended)**

Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...  # Your PyPI API token
```

**Option B: Using Environment Variable**
```bash
export PYPI_API_TOKEN="pypi-AgEIcHlwaS5vcmcCJ..."
```

### Step 2: Upload to TestPyPI (Dry Run)

```bash
# Install twine
pip install twine

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Verify on TestPyPI
open https://test.pypi.org/project/arifos/2026.3.7/
```

### Step 3: Test Installation from TestPyPI

```bash
# Create fresh venv
python -m venv /tmp/test_arifos_testpypi
source /tmp/test_arifos_testpypi/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ arifos==2026.3.7

# Run smoke tests
python -c "from arifos_aaa_mcp import create_aaa_mcp_server; print('✓ Import successful')"
arifos --help
```

### Step 4: Upload to Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Verify on PyPI
open https://pypi.org/project/arifos/2026.3.7/
```

### Step 5: Post-Publication Verification

```bash
# Create fresh venv
python -m venv /tmp/test_arifos_pypi
source /tmp/test_arifos_pypi/bin/activate

# Install from PyPI
pip install arifos==2026.3.7

# Verify installation
python -c "
from arifos_aaa_mcp import create_aaa_mcp_server
from core.governance_kernel import GovernanceKernel
from core.physics.thermodynamics_hardened import ThermodynamicBudget
print('✓ arifOS 2026.03.07 (P3 Thermodynamic Hardening) installed successfully')
"

# Test CLI
arifos --help
arifos stdio --help 2>&1 | head -5
```

---

## Package Metadata

| Field | Value |
|-------|-------|
| **Name** | `arifos` |
| **Version** | `2026.3.7` |
| **License** | AGPL-3.0-only |
| **Python** | >=3.12 |
| **Author** | Muhammad Arif bin Fazil |
| **Email** | arifbfazil@gmail.com |
| **Description** | arifOS - The World's First Production-Grade Constitutional AI Governance System |
| **Keywords** | ai-governance, constitutional-ai, mcp, ai-safety, thermodynamic-governance |
| **Homepage** | https://github.com/ambitious-octopus/arifos |

### Classifiers
- Development Status :: 5 - Production/Stable
- Programming Language :: Python :: 3.12
- Programming Language :: Python :: 3.13
- Topic :: Scientific/Engineering :: Artificial Intelligence
- Topic :: Security

---

## Entry Points

```python
# CLI
[project.scripts]
arifos = "arifos_aaa_mcp.__main__:main"

# MCP Server
[project.entry-points."mcp.server"]
arifos = "arifos_aaa_mcp.server:create_aaa_mcp_server"
```

---

## Known Issues & Notes

### Session Archives in Wheel
The wheel includes `aaa_mcp/sessions/archive/` with JSON session logs. This is intentional for:
- Demonstration purposes
- Testing the VAULT999 ledger system
- Documentation of real constitutional decisions

Size impact: ~500 KB (acceptable for a governance system with provenance requirements).

### Node Modules Exclusion
`aclip_cai/dashboard/node_modules/` is NOT included in the wheel (excluded via `exclude_package_data` in `pyproject.toml`).

### MANIFEST.in Warnings
Some warnings during build are expected (non-existent directories like `spec/`, `arifos/`, `codebase/` referenced in legacy patterns). These do not affect the build.

---

## Rollback Procedure

If critical issues are found post-publication:

```bash
# Yank the version (prevents new installs but keeps for existing)
twine yank arifos==2026.3.7

# Or delete (only if absolutely necessary, within 24 hours)
# Contact PyPI support for deletion
```

---

## Post-Publication Announcements

Update the following after successful publication:

1. **GitHub Release**: Create release notes with CHANGELOG excerpt
2. **Documentation**: Update `docs/` with new installation instructions
3. **Social**: Announce on relevant channels with P3 Thermodynamic Hardening highlights

---

## Verification Commands Summary

```bash
# Full verification pipeline
rm -rf dist/ *.egg-info/
python -m build
twine check dist/*
python -m venv /tmp/verify_arifos
source /tmp/verify_arifos/bin/activate
pip install dist/arifos-2026.3.7-py3-none-any.whl
python -c "from arifos_aaa_mcp import create_aaa_mcp_server; print('✓ Import OK')"
arifos --help
```

---

**Seal Date:** 2026-03-07  
**Constitutional Compliance:** F2 Truth ✓, F4 Clarity ✓, F7 Humility ✓, F13 Sovereign ✓
