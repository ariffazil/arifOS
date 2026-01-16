# ?? arifOS Setup - Function-Based Organization

**Quick Start:** One command to set up everything!

---

## ? New Machine? Start Here!

```bash
# Clone repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Run bootstrap (choose one)
python setup/bootstrap/bootstrap.py --full      # Cross-platform
./setup/bootstrap/bootstrap.ps1 --full          # Windows
./setup/bootstrap/bootstrap.sh --full           # macOS/Linux

# That's it! ??
```

**Time:** 3-5 minutes from clone to coding

---

## ?? Directory Structure (Function-Based)

```
arifOS/
?
??? setup/                      # All setup-related (organized by function)
?   ??? bootstrap/             # Bootstrap scripts & guide
?   ?   ??? bootstrap.py       # Cross-platform
?   ?   ??? bootstrap.ps1      # Windows
?   ?   ??? bootstrap.sh       # macOS/Linux
?   ?   ??? BOOTSTRAP_GUIDE.md # Detailed guide
?   ?   ??? README.md
?   ?
?   ??? docs/                  # Setup documentation
?   ?   ??? IDE_AGNOSTIC_SUMMARY.md
?   ?   ??? QUICK_START.md
?   ?   ??? DEVELOPMENT_SETUP.md
?   ?   ??? DOCUMENTATION_INDEX.md
?   ?   ??? ... (more guides)
?   ?
?   ??? tools/                 # Installation utilities
?   ?   ??? install_recommended_deps.ps1
?   ?   ??? housekeeping.ps1
?   ?
?   ??? verification/          # Verification scripts
?   ?   ??? verify_setup.py
?   ?
?   ??? README.md             # Setup overview
?
??? arifos_core/              # Core package
??? L1_THEORY/                # Constitutional law
??? L2_PROTOCOLS/             # Specifications
??? README.md                 # Project overview
??? AGENTS.md                 # Agent specifications
?
??? Config files (root - required by tools):
    ??? .pre-commit-config.yaml
    ??? pytest.ini
    ??? mypy.ini
    ??? pyproject.toml
```

**Organized by FUNCTION, not file type!**

---

## ?? Quick Commands

### Bootstrap (From Project Root)

```bash
# Full setup (recommended)
python setup/bootstrap/bootstrap.py --full

# Minimal (core only)
python setup/bootstrap/bootstrap.py --minimal

# Auto mode (no prompts)
python setup/bootstrap/bootstrap.py --auto
```

### Verify Installation

```bash
# Activate environment
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Run verification
python setup/verification/verify_setup.py
```

### Install Additional Tools

```powershell
.\setup\tools\install_recommended_deps.ps1
```

---

## ?? Documentation

**Start here:**
1. [`setup/bootstrap/BOOTSTRAP_GUIDE.md`](setup/bootstrap/BOOTSTRAP_GUIDE.md) - New machine setup
2. [`setup/docs/IDE_AGNOSTIC_SUMMARY.md`](setup/docs/IDE_AGNOSTIC_SUMMARY.md) - Why it works with any IDE
3. [`setup/docs/QUICK_START.md`](setup/docs/QUICK_START.md) - Essential commands

**Full index:**
- [`setup/docs/DOCUMENTATION_INDEX.md`](setup/docs/DOCUMENTATION_INDEX.md) - Complete documentation index

---

## ? What Gets Installed

### Core (Always)
- Python virtual environment
- arifOS 46.2.2 package
- NumPy, Pydantic
- LiteLLM (OpenAI, Claude, Gemini, SEA-LION)
- FastAPI + Uvicorn
- FastMCP (MCP server)
- DSPy framework

### Development Tools (Full Mode)
- pytest + coverage
- black (formatter)
- ruff (linter)
- mypy (type checker)
- pre-commit hooks
- Security scanners (safety, bandit, detect-secrets)

---

## ?? Why This Structure?

### Function-Based Organization

**OLD (type-based):**
```
docs/setup/         # Docs here
scripts/setup/      # Scripts there
root/               # Some files here
```
**Problems:** Hard to find related files

**NEW (function-based):**
```
setup/
  ??? bootstrap/    # Everything bootstrap-related
  ??? docs/         # All setup docs together
  ??? tools/        # All tools together
  ??? verification/ # All verification together
```
**Benefits:** 
- ? Related files together
- ? Clear purpose per directory
- ? Easy to navigate
- ? Logical grouping

---

## ?? Works Everywhere

**Platforms:**
- ? Windows (PowerShell/CMD)
- ? macOS (Bash)
- ? Linux (Bash)
- ? WSL, Git Bash, etc.

**IDEs:**
- ? VS Code
- ? PyCharm
- ? Vim/Neovim
- ? Emacs
- ? Sublime Text
- ? Command line only

**Same setup works everywhere!**

---

## ?? Troubleshooting

### Bootstrap Fails

**Python not found:**
```bash
# Install Python 3.10+
# Windows: https://python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

**Permission denied (macOS/Linux):**
```bash
chmod +x setup/bootstrap/bootstrap.sh
```

### After Bootstrap

**Verification fails:**
```bash
# Activate environment first
source .venv/bin/activate

# Run verification
python setup/verification/verify_setup.py
```

**More help:**
- [`setup/docs/DEVELOPMENT_SETUP.md`](setup/docs/DEVELOPMENT_SETUP.md) - Full troubleshooting

---

## ?? You're Ready!

**After bootstrap:**
1. ? Environment configured
2. ? Dependencies installed
3. ? Pre-commit hooks active
4. ? Tests passing
5. ? Ready to code!

```bash
# Activate environment
source .venv/bin/activate

# Start your IDE
code .    # VS Code
charm .   # PyCharm
vim .     # Vim
```

**DITEMPA BUKAN DIBERI** — Your environment is forged! ???

---

## ?? Project Structure

**Full project:**
```
arifOS/
??? setup/                  # Setup (you are here)
??? arifos_core/           # Core package
??? arifos_clip/           # A-CLIP pipeline
??? arifos_orchestrator/   # Orchestration layer
??? L1_THEORY/             # Constitutional law
??? L2_PROTOCOLS/          # Specifications
??? L7_DEMOS/              # Examples and demos
??? tests/                 # Test suite
??? ...
```

---

**Ready to build constitutional AI!** ??
