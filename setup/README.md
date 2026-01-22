# Setup Directory

All setup-related files organized by function.

## Quick Start

**New machine setup:**
```bash
# From project root
python setup/bootstrap/bootstrap.py --full
```

## Directory Structure

```
setup/
??? bootstrap/          # Bootstrap scripts and guides
?   ??? bootstrap.py    # Cross-platform Python script
?   ??? bootstrap.ps1   # Windows PowerShell script
?   ??? bootstrap.sh    # macOS/Linux Bash script
?   ??? BOOTSTRAP_GUIDE.md
?
??? docs/              # Setup documentation
?   ??? IDE_AGNOSTIC_SUMMARY.md      # Why it works everywhere
?   ??? QUICK_START.md               # Essential commands
?   ??? DEVELOPMENT_SETUP.md         # Full IDE configuration
?   ??? DEPENDENCY_ENHANCEMENT_SUMMARY.md
?   ??? RECOMMENDED_DEPENDENCIES_RESEARCH.md
?   ??? TOOLS_QUICK_START.md
?   ??? DOCUMENTATION_INDEX.md
?
??? tools/             # Installation and utility scripts
?   ??? install_recommended_deps.ps1
?   ??? housekeeping.ps1
?
??? verification/      # Verification and testing
    ??? verify_setup.py
```

## Configuration Files (Root)

These must stay in project root:
- `.pre-commit-config.yaml` - Git hooks (required by pre-commit)
- `pytest.ini` - Test configuration (required by pytest)
- `mypy.ini` - Type checking (required by mypy)
- `pyproject.toml` - Package metadata (required by pip)

## Usage

### Bootstrap New Machine
```bash
# Windows
.\setup\bootstrap\bootstrap.ps1 --full

# macOS/Linux
./setup/bootstrap/bootstrap.sh --full

# Cross-platform
python setup/bootstrap/bootstrap.py --full
```

### Verify Installation
```bash
python setup/verification/verify_setup.py
```

### Install Additional Tools
```powershell
.\setup\tools\install_recommended_deps.ps1
```

### Read Documentation
Start with: `setup/docs/DOCUMENTATION_INDEX.md`

## See Also

- [../README.md](../README.md) - Project overview
- [../AGENTS.md](../AGENTS.md) - Agent specifications
- [../L1_THEORY/](../L1_THEORY/) - Constitutional law

---

## IDE-Agnostic Auto-Bootstrap (Recommended)

To ensure your environment is always ready (even if you don't know coding):

```bash
# Run this on every workspace/session open (or configure your IDE to do it):
python setup/on_workspace_open.py
```

**What it does:**
- Checks if .venv and all dependencies are present
- If not, runs the full bootstrap automatically
- Works in any IDE (Antigravity, VS Code, PyCharm, etc.)
- Safe to run as often as you want

**Recommended:**
- Add `python setup/on_workspace_open.py` as a workspace startup task in your IDE for zero-click setup
