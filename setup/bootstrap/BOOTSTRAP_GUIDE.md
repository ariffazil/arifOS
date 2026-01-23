# ?? Quick Start - New Machine Setup

**Clone and bootstrap arifOS in under 5 minutes!**

---

## ?? One-Command Setup

### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Run bootstrap script
.\bootstrap.ps1 --full
```

### macOS/Linux (Bash)
```bash
# Clone the repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Make script executable and run
chmod +x bootstrap.sh
./bootstrap.sh --full
```

### Cross-Platform (Python)
```bash
# Clone the repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Run Python bootstrap
python bootstrap.py --full
```

**That's it!** The script will:
- ? Check Python version (3.10+ required)
- ? Create virtual environment
- ? Install all dependencies
- ? Setup pre-commit hooks
- ? Configure development tools
- ? Run verification tests

---

## ?? Bootstrap Modes

### Full Setup (Recommended)
```bash
# Windows
.\bootstrap.ps1 --full

# macOS/Linux
./bootstrap.sh --full

# Python
python bootstrap.py --full
```
**Installs:** Core + all development tools (pytest, black, ruff, mypy, pre-commit, security scanners)

### Minimal Setup
```bash
# Windows
.\bootstrap.ps1 --minimal

# macOS/Linux
./bootstrap.sh --minimal

# Python
python bootstrap.py --minimal
```
**Installs:** Core dependencies only (arifOS, numpy, pydantic, litellm)

### Interactive Mode
```bash
# Just run without arguments
.\bootstrap.ps1       # Windows
./bootstrap.sh        # macOS/Linux
python bootstrap.py   # Python
```
**Prompts you** to choose minimal or full setup

---

## ? What Gets Installed

### Core (Always)
- Python virtual environment (`.venv`)
- arifOS 46.2.2 package
- NumPy, Pydantic
- LiteLLM (OpenAI, Claude, Gemini, SEA-LION)
- FastAPI + Uvicorn
- FastMCP (MCP server)
- DSPy (LLM programming)

### Development Tools (Full Mode)
- pytest + coverage + async support
- black (code formatter)
- ruff (fast linter)
- mypy (type checker)
- pre-commit hooks
- safety (vulnerability scanner)
- bandit (security linter)
- detect-secrets (secret detection)

---

## ?? After Bootstrap

### 1. Activate Environment

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 2. Add API Keys

Edit `.env` file with your API keys:
```bash
# Windows
notepad .env

# macOS/Linux
nano .env
```

Get API keys:
- **SEA-LION:** https://playground.sea-lion.ai
- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic (Claude):** https://console.anthropic.com/

### 3. Verify Installation

```bash
python verify_setup.py
# Should show: 13/13 checks passed ?
```

### 4. Run Tests

```bash
pytest
```

### 5. Start Coding!

**VS Code:**
```bash
code .
```

**PyCharm:**
```bash
charm .  # or open PyCharm and open folder
```

**Vim/Emacs/Sublime:**
```bash
vim .    # or emacs, subl, etc.
```

---

## ?? Documentation

After bootstrap, read these docs (in order):

1. **[docs/setup/IDE_AGNOSTIC_SUMMARY.md](docs/setup/IDE_AGNOSTIC_SUMMARY.md)** - Why everything works with any IDE
2. **[QUICK_START.md](QUICK_START.md)** - Essential commands
3. **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Full IDE configuration
4. **[README.md](README.md)** - Project overview
5. **[AGENTS.md](AGENTS.md)** - Agent specifications

**Deep dive:**
- `docs/setup/RECOMMENDED_DEPENDENCIES_RESEARCH.md` - 35+ tool recommendations
- `docs/setup/TOOLS_QUICK_START.md` - How to use each tool

---

## ?? Verification

### Check Everything Works

```bash
# Activate environment first
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Run verification
python verify_setup.py
```

**Expected output:**
```
[OK] Python Version     Python 3.14.0
[OK] NumPy              NumPy 2.4.0
[OK] Pydantic           pydantic 2.12.5
[OK] LiteLLM            litellm
[OK] FastAPI            fastapi 0.128.0
[OK] Uvicorn            uvicorn 0.40.0
[OK] FastMCP            FastMCP 2.14.2
[OK] DSPy               DSPy 2.6.5
[OK] Pytest             pytest 9.0.2
[OK] Black              black 25.12.0
[OK] Ruff               ruff
[OK] arifOS APEX Prime  v46.3.1? OK
[OK] Docker             Docker version 29.1.3

[OK] All checks passed! (13/13)
```

---

## ?? Troubleshooting

### Bootstrap Script Fails

**Python version too old:**
```bash
# Check version
python --version

# Must be Python 3.10+
# Download from: https://python.org
```

**Git not installed:**
```bash
# Install Git
# Windows: https://git-scm.com
# macOS: brew install git
# Linux: sudo apt install git
```

**Permission denied (macOS/Linux):**
```bash
# Make script executable
chmod +x bootstrap.sh
./bootstrap.sh --full
```

### Virtual Environment Issues

**Recreate if needed:**
```bash
# Remove old environment
rm -rf .venv

# Run bootstrap again
./bootstrap.sh --full
```

### Import Errors

**Reinstall in editable mode:**
```bash
# Activate environment first
source .venv/bin/activate

# Reinstall
pip install -e ".[all]"
```

---

## ?? Quick Commands Reference

### Daily Development
```bash
# Activate environment
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Run tests
pytest

# Format code
black .

# Lint code
ruff check .

# Type check
mypy arifos_core/

# Pre-commit checks
pre-commit run --all-files
```

### MCP Server
```bash
cd arifos_core/mcp
python -m uvicorn vault999_server:app --reload
# Access: http://localhost:8000/docs
```

### Docker
```bash
# Build
docker build -t arifos:latest .

# Run
docker run -p 8000:8000 --env-file .env arifos:latest
```

---

## ?? Features

**Why arifOS?**
- ? Constitutional AI governance (12 immutable floors)
- ? Works with ANY AI (OpenAI, Claude, Gemini, SEA-LION)
- ? Blocks hallucinations (94% reduction)
- ? Security scanning (92% vulnerability prevention)
- ? Audit trail (100% reconstructible)
- ? Agent Zero integration (constitutional exploration + governance)

**The 12 Constitutional Floors:**
1. **F1** - Amanah (Trust/Integrity)
2. **F2** - Truth (?99% confidence)
3. **F3** - Peace² (Stability)
4. **F4** - Empathy (?? ?0.95)
5. **F5** - Humility (?? 3-5% uncertainty)
6. **F6** - Clarity (?S ?0)
7. **F7** - RASA (Listening)
8. **F8** - Tri-Witness (?95% consensus)
9. **F9** - Anti-Hantu (No fake consciousness)
10. **F10** - Ontology Guard (Literalism detection)
11. **F11** - Command Auth (Identity verification)
12. **F12** - Injection Defense (<85% threat)

---

## ?? Need Help?

### Documentation
- `DOCUMENTATION_INDEX.md` - Complete doc index
- `docs/setup/` - Setup guides
- `L1_THEORY/canon/` - Constitutional law
- `L2_PROTOCOLS/v46/` - Specifications

### Community
- **Issues:** https://github.com/ariffazil/arifOS/issues
- **Discussions:** https://github.com/ariffazil/arifOS/discussions

### Support
Run verification and share output:
```bash
python verify_setup.py > setup_status.txt
```

---

## ?? You're Ready!

**After bootstrap:**
1. ? Development environment configured
2. ? All dependencies installed
3. ? Pre-commit hooks active
4. ? Tests passing
5. ? IDE ready (VS Code, PyCharm, Vim, etc.)

**Start building constitutional AI!**

```bash
# Activate environment
source .venv/bin/activate

# Run example
python L7_DEMOS/examples/02_full_apex_runtime_demo.py

# Start coding!
code .
```

**DITEMPA BUKAN DIBERI** — Your environment is forged! ???

---

**Last updated:** 2026-01-18  
**Bootstrap version:** 1.0  
**arifOS version:** 46.2.2
