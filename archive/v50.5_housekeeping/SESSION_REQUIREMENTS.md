# arifOS Session Requirements

**Version:** v49.0.0 (Constitutional Forge - 13 Floors, Trinity Engines, 25 MCP Servers)
**Authority:** Engineer (Ω) - Session Management Documentation
**Last Updated:** 2026-01-18
**Status:** ✅ SEALED

---

## 📋 Quick Reference

**Minimum Requirements:**
- Python 3.10+ (tested through 3.14)
- Git 2.0+
- 2GB RAM minimum
- Internet connection (for dependencies)

**One-Command Setup:**
```bash
python setup/bootstrap/bootstrap.py --full
```

**Session Initialization:**
```bash
# In Claude Code CLI
/init-session

# OR manually
python setup/on_workspace_open.py
```

---

## 1. System Requirements

### Operating System
- ✅ **Windows** (10/11) - Primary development platform
- ✅ **macOS** (10.15+) - Supported
- ✅ **Linux** (Ubuntu 20.04+, Debian 11+) - Supported

### Core Tools (Mandatory)
| Tool | Version | Purpose | Verification |
|------|---------|---------|--------------|
| **Python** | ≥ 3.10 | Core runtime | `python --version` |
| **Git** | ≥ 2.0 | Version control | `git --version` |
| **pip** | ≥ 21.0 | Package manager | `pip --version` |

### Optional Tools (Recommended)
| Tool | Version | Purpose | Verification |
|------|---------|---------|--------------|
| **Docker** | ≥ 20.10 | Containerization | `docker --version` |
| **Docker Compose** | ≥ 2.0 | Multi-container orchestration | `docker-compose --version` |

---

## 2. Python Dependencies

### Core Dependencies (Always Required)
**Defined in:** `pyproject.toml` [dependencies]

```toml
numpy >= 1.20.0          # Numerical operations
pydantic >= 2.0.0        # Data validation
anyio >= 4.0.0           # Async I/O
starlette >= 0.30.0      # ASGI framework
```

### Optional Dependency Groups
**Install with:** `pip install -e .[group_name]`

#### Development Tools (`dev`)
```bash
pip install -e .[dev]
```
- pytest >= 7.0.0 (testing framework)
- pytest-cov >= 4.0.0 (coverage reporting)
- black >= 23.0.0 (code formatter)
- ruff >= 0.1.0 (fast linter)
- mypy >= 1.0.0 (type checker)
- httpx >= 0.28.0 (HTTP client for tests)

#### API Server (`api`)
```bash
pip install -e .[api]
```
- fastapi >= 0.100.0 (REST API framework)
- uvicorn[standard] >= 0.23.0 (ASGI server)
- python-multipart >= 0.0.6 (form handling)

#### LiteLLM Integration (`litellm`)
```bash
pip install -e .[litellm]
```
- litellm >= 1.0.0 (unified LLM interface)

#### Governed Mode (`governed`)
```bash
pip install -e .[governed]
```
- litellm >= 1.0.0
- httpx >= 0.28.0
- pygments >= 2.16.0 (syntax highlighting)
- openai >= 1.6.0 (OpenAI SDK)

#### All Features (`all`)
```bash
pip install -e .[all]
```
Installs all optional dependencies above.

### Additional Dependencies (requirements.txt)
**Full list:** See `requirements.txt` for expanded dependencies including:
- MCP integration (mcp >= 0.1.0)
- Rich terminal output (rich >= 13.7.0)
- Environment management (python-dotenv >= 1.0.0)
- HTTP clients (requests, aiohttp)
- Configuration (pydantic-settings)
- SSE support (sse-starlette)

---

## 3. Installation & Setup

### Method 1: Auto-Bootstrap (Recommended)

**For First-Time Setup:**
```bash
# Clone repository
git clone https://github.com/yourusername/arifOS.git
cd arifOS

# Run full bootstrap (creates venv, installs deps, sets up tools)
python setup/bootstrap/bootstrap.py --full
```

**Bootstrap Modes:**
- `--full` - Complete setup (venv + deps + dev tools + pre-commit hooks)
- `--minimal` - Basic setup (venv + core deps only)
- `--auto` - Non-interactive mode (uses defaults)

**What Bootstrap Does:**
1. ✅ Verifies Python 3.10+ installed
2. ✅ Creates virtual environment (`.venv`)
3. ✅ Installs core dependencies
4. ✅ Installs development tools (pytest, black, ruff, mypy)
5. ✅ Sets up pre-commit hooks
6. ✅ Creates `.env` from `.env.example` (if missing)
7. ✅ Runs verification checks (13/13)

**Platform-Specific Bootstrap:**
```bash
# Windows PowerShell
.\setup\bootstrap\bootstrap.ps1 --full

# macOS/Linux Bash
./setup/bootstrap/bootstrap.sh --full
```

### Method 2: Manual Installation

**For Advanced Users:**
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install arifOS with dependencies
pip install -e .[all]

# 5. Copy environment template
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux

# 6. Verify installation
python setup/verification/verify_setup.py
```

### Method 3: Docker Deployment

**For Production or Isolated Environments:**
```bash
# Build container
docker build -t arifos:v49 .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f arifos
```

**Docker Configuration Files:**
- `Dockerfile` - Multi-stage production build
- `docker-compose.yml` - Main service orchestration
- `docker-compose-vault999.yml` - VAULT999 specific setup
- `.env.docker.example` - Docker environment template

---

## 4. Environment Configuration

### Environment Variables (.env)

**Required Variables:**
```bash
# API Configuration
PORT=8000                   # API server port
HOST=0.0.0.0               # Bind address
LOG_LEVEL=info             # Logging verbosity

# Constitutional Governance
GOVERNANCE_MODE=HARD       # HARD (strict) | SOFT | AUDIT_ONLY
VAULT_PATH=./VAULT999      # Constitutional memory storage

# Optional: Deployment
RENDER=false               # Set to true for Render.com deployment
CLOUDFLARE_TUNNEL_TOKEN=   # For Cloudflare Tunnel integration
```

**Load Environment Variables:**
```powershell
# Load into current session (temporary)
. .\load-env.ps1

# OR use script directly with options
. .\scripts\load_env.ps1 -ShowVariables

# Persist across sessions (saves to User environment)
. .\scripts\load_env.ps1 -Persist
```

**Verification:**
```powershell
# Check if variables loaded
echo $env:GOVERNANCE_MODE
echo $env:PORT
```

---

## 5. Session Initialization Protocol

### The Unified Origin Point (000)

**Constitutional Requirement:** Every arifOS session MUST initialize through the 000 protocol.

**Workflow Definition:** `.agent/workflows/000.md`

#### The 6-Step Initialization Sequence:

**1. Load the Unified Ontology**
```bash
# Read constitutional ontology
cat L1_THEORY/canon/000_foundation/000_ONTOLOGY.md
```

**2. Establish Identity & Time (Phoenix-72)**
```bash
# Verify current date/time
date

# Check agent identity
cat config/agents.yaml
```

**3. Load Constitution (Mandatory)**
```bash
# Supreme Law
cat AGENTS.md

# System Evolution
cat CHANGELOG.md
```

**4. Load Memory (Cross-Session Reflection)**
```bash
# Check for EUREKA notes
cat .antigravity/EUREKA_NEXT_SESSION.md 2>/dev/null
cat .claude/EUREKA_NEXT_SESSION.md 2>/dev/null
```

**5. Check Reality (Git Status)**
```bash
git status
git branch --show-current
git log -5 --oneline

# Check for pending governance seals
ls -la .git/seals/ 2>/dev/null
```

**6. System Lifecycle (Choose One)**
```powershell
# First-time setup
powershell -ExecutionPolicy Bypass -File scripts/setup_system.ps1

# Normal boot
powershell -ExecutionPolicy Bypass -File scripts/boot_system.ps1

# Reboot (after updates)
powershell -ExecutionPolicy Bypass -File scripts/reboot_system.ps1
```

### Quick Initialization Methods

#### Method A: Claude Code Skill (Recommended)
```bash
# In Claude Code CLI
/init-session

# OR
/000
```

#### Method B: Auto-Bootstrap on Workspace Open
```bash
# Run on every session start (idempotent, safe to repeat)
python setup/on_workspace_open.py
```

This script:
- ✅ Checks if `.venv` exists and is healthy
- ✅ Verifies dependencies installed
- ✅ Auto-runs bootstrap if needed
- ✅ Safe to run multiple times (idempotent)
- ✅ IDE-agnostic (works in any editor)

#### Method C: Manual Initialization
```bash
# 1. Load environment
. .\load-env.ps1

# 2. Read constitution
cat AGENTS.md

# 3. Check git status
git status

# 4. Check EUREKA notes
cat .antigravity/EUREKA_NEXT_SESSION.md
```

---

## 6. Verification & Health Checks

### Installation Verification
```bash
python setup/verification/verify_setup.py
```

**Expected Output:**
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
[OK] arifOS APEX Prime  v46.3.1 OK
[OK] Docker             Docker version 29.1.3

[OK] All checks passed! (13/13)
```

### Constitutional Health Checks
```bash
# Verify THE EYE ledger
python -c "import os; print('THE EYE: WATCHING' if os.path.exists('L1_THEORY/ledger/gitseal_audit_trail.jsonl') else 'Ledger not found')"

# Check VAULT999 status
ls VAULT999/ 2>/dev/null || echo "VAULT999 not initialized"

# Verify constitutional floors
python -m arifos.core.floor_validators --check-all
```

### Session Health Check
```bash
# Check virtual environment active
python -c "import sys; print('✅ venv active' if sys.prefix != sys.base_prefix else '❌ venv not active')"

# Check arifOS importable
python -c "import arifos; print(f'✅ arifOS v{arifos.__version__}')"

# Check governance mode
python -c "import os; print(f'Governance: {os.getenv(\"GOVERNANCE_MODE\", \"NOT SET\")}')"
```

---

## 7. Constitutional Tools & Skills

### Core Skills (Required)

**Defined in:** `.claude/REQUIRED_SKILLS.md`

#### 1. init-session (CRITICAL - Session Management)
**Purpose:** Load complete arifOS governance context
**When:** Every new session, branch switch, or after pulling updates
**Usage:**
```bash
/init-session   # In Claude Code
```

#### 2. full-autonomy (FAG Mode - Governance Enforcement)
**Purpose:** Activate Full Autonomy Governance with SABAR-72 protocol
**When:** Beginning autonomous development work
**Usage:**
```bash
/fag   # In Claude Code
```

#### 3. analyze-entropy (CRITICAL - Risk Assessment)
**Purpose:** Calculate entropy delta (ΔS) using Trinity forge
**When:** Before every commit (mandatory)
**Usage:**
```bash
/analyze-entropy   # In Claude Code
```

### Trinity Governance System

**Purpose:** Constitutional validation and sealing

**Commands:**
```bash
# Generate governance artifacts
python scripts/trinity.py forge

# Run quality control checks
python scripts/trinity.py qc

# Constitutional sealing (after human approval)
python scripts/trinity.py seal "Reason for seal"
```

**Trinity Workflow:**
1. **Forge** - Generate constitutional artifacts from changes
2. **QC** - Run constitutional compliance checks
3. **Seal** - Cryptographically seal approved changes

---

## 8. Common Setup Issues & Solutions

### Issue 1: load-env.ps1 Not Found
**Symptom:** Error when running `. .\load-env.ps1`
**Cause:** Missing `scripts/load_env.ps1` file
**Solution:**
```bash
# File has been restored in this session
# Verify it exists:
powershell -Command "Test-Path 'scripts\load_env.ps1'"

# If still missing, restore from archive:
powershell -Command "Copy-Item 'archive_local\scripts\scripts\load_env.ps1' 'scripts\load_env.ps1'"
```

### Issue 2: Python Version Too Old
**Symptom:** `requires-python = ">=3.10"` error
**Cause:** Python < 3.10 installed
**Solution:**
```bash
# Check current version
python --version

# Install Python 3.10+ from python.org
# OR use pyenv (recommended)
pyenv install 3.10.0
pyenv local 3.10.0
```

### Issue 3: Virtual Environment Not Activated
**Symptom:** Packages installed globally or not found
**Cause:** `.venv` not activated
**Solution:**
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate

# Verify activation
python -c "import sys; print(sys.prefix)"
```

### Issue 4: Dependencies Not Installed
**Symptom:** `ModuleNotFoundError` when importing arifos
**Cause:** Missing dependencies
**Solution:**
```bash
# Reinstall with all dependencies
pip install -e .[all]

# OR run verification to diagnose
python setup/verification/verify_setup.py
```

### Issue 5: Docker Build Fails
**Symptom:** Docker build errors or container won't start
**Cause:** Various (check Docker logs)
**Solution:**
```bash
# Check Docker running
docker --version

# Check logs
docker-compose logs arifos

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue 6: THE EYE Ledger Missing
**Symptom:** Constitutional operations fail
**Cause:** Ledger directory not created
**Solution:**
```bash
# Create ledger directory
mkdir -p L1_THEORY/ledger

# Verify creation
ls L1_THEORY/ledger/
```

---

## 9. Development Workflow

### Daily Session Start
```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate       # macOS/Linux

# 2. Initialize session
/init-session   # In Claude Code

# OR
python setup/on_workspace_open.py

# 3. Load environment
. .\load-env.ps1

# 4. Check git status
git status

# 5. Read EUREKA notes (if exist)
cat .claude/EUREKA_NEXT_SESSION.md 2>/dev/null
```

### Before Committing
```bash
# 1. Analyze entropy (MANDATORY)
/analyze-entropy

# 2. Run tests
pytest -v

# 3. Format code
black .

# 4. Lint code
ruff check .

# 5. Type check
mypy .

# 6. Trinity governance
python scripts/trinity.py forge
python scripts/trinity.py qc
```

### After Committing
```bash
# 1. Trinity seal (with human approval)
python scripts/trinity.py seal "Constitutional validation complete"

# 2. Update EUREKA notes (if significant insights)
# Add learnings to .claude/EUREKA_NEXT_SESSION.md

# 3. Push to remote (only after seal)
git push origin branch-name
```

---

## 10. Production Deployment

### Docker Production Setup

**1. Build Production Container**
```bash
docker build -t arifos:v49-production .
```

**2. Configure Environment**
```bash
# Copy Docker environment template
cp .env.docker.example .env.docker

# Edit for production
nano .env.docker

# Set production values:
GOVERNANCE_MODE=HARD
LOG_LEVEL=warning
RENDER=true
```

**3. Deploy with Docker Compose**
```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose-vault999.yml up -d

# Check health
docker-compose ps
docker-compose logs -f arifos

# Verify constitutional compliance
docker-compose exec arifos python -c "import arifos; arifos.verify_governance()"
```

### API Server Deployment

**Direct Python Deployment:**
```bash
# Production server with uvicorn
uvicorn arifos.api.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning
```

**Health Check Endpoint:**
```bash
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "governance": "HARD", "version": "49.0.0"}
```

---

## 11. Configuration Reference

### pyproject.toml Key Settings
```toml
[project]
name = "arifos"
version = "49.0.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true
```

### .env Template Reference
```bash
# API Server
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info

# Constitutional Governance
GOVERNANCE_MODE=HARD              # HARD | SOFT | AUDIT_ONLY
VAULT_PATH=./VAULT999
FLOOR_ENFORCEMENT_MODE=strict     # strict | permissive | audit_only
TRINITY_ENABLED=true
LEDGER_PATH=./L1_THEORY/ledger

# MCP Integration (Optional)
MCP_ENABLED=true
MCP_SERVERS=qdrant,ledger,session

# Deployment (Optional)
RENDER=false
CLOUDFLARE_TUNNEL_TOKEN=

# Database (Optional - for advanced deployments)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=arifos
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 12. Quick Command Reference

### Installation
```bash
# Full auto-bootstrap
python setup/bootstrap/bootstrap.py --full

# Manual install
pip install -e .[all]

# Verify installation
python setup/verification/verify_setup.py
```

### Session Management
```bash
# Initialize session
/init-session                    # Claude Code
python setup/on_workspace_open.py   # Manual

# Load environment
. .\load-env.ps1                 # Windows
source scripts/load_env.sh       # macOS/Linux

# Full autonomy governance
/fag                             # Claude Code
```

### Development
```bash
# Run tests
pytest -v

# Format code
black .

# Lint code
ruff check .

# Type check
mypy .

# Analyze entropy (before commit)
/analyze-entropy
```

### Constitutional Governance
```bash
# Trinity workflow
python scripts/trinity.py forge
python scripts/trinity.py qc
python scripts/trinity.py seal "Reason"

# Check THE EYE
cat L1_THEORY/ledger/gitseal_audit_trail.jsonl
```

### Docker
```bash
# Build
docker build -t arifos:v49 .

# Run
docker-compose up -d

# Logs
docker-compose logs -f arifos

# Health check
curl http://localhost:8000/health
```

---

## 13. Constitutional Compliance

### This Document Compliance
- ✅ **F1 (Amanah):** Git-backed, fully reversible
- ✅ **F2 (Truth):** All facts verified against v49.0.0 codebase
- ✅ **F4 (ΔS Clarity):** Reduces setup confusion with comprehensive guide
- ✅ **F6 (Empathy):** Serves weakest stakeholder (new users, zero prior knowledge)
- ✅ **F7 (Humility):** Acknowledges potential issues with troubleshooting section
- ✅ **F10 (Ontology):** Maintains symbolic integrity in technical descriptions

---

## 14. Additional Resources

### Documentation
- **[README.md](README.md)** - Complete zero-context introduction (1,738 lines)
- **[WHAT.md](WHAT.md)** - What arifOS does constitutionally
- **[WHERE.md](WHERE.md)** - Where everything is located
- **[HOW.md](HOW.md)** - How to start and use (quick reference)
- **[AGENTS.md](AGENTS.md)** - Constitutional governance specifications
- **[CHANGELOG.md](CHANGELOG.md)** - System evolution and version history

### Setup Documentation
- **[setup/bootstrap/BOOTSTRAP_GUIDE.md](setup/bootstrap/BOOTSTRAP_GUIDE.md)** - Detailed bootstrap guide
- **[setup/docs/SETUP_COMPLETE.md](setup/docs/SETUP_COMPLETE.md)** - Post-setup validation
- **[setup/docs/TOOLS_QUICK_START.md](setup/docs/TOOLS_QUICK_START.md)** - Tool usage guide
- **[setup/docs/DEVELOPMENT_SETUP.md](setup/docs/DEVELOPMENT_SETUP.md)** - Full IDE configuration

### Constitutional Canon
- **[L1_THEORY/canon/](L1_THEORY/canon/)** - Supreme constitutional law
- **[L2_PROTOCOLS/v46/](L2_PROTOCOLS/v46/)** - Operational specifications
- **[config/agents.yaml](config/agents.yaml)** - Agent configuration

### Workflows
- **[.agent/workflows/](\.agent\workflows/)** - All 000-999 constitutional workflows
- **[.claude/skills/](\.claude\skills/)** - Claude Code integration skills

---

## 15. Getting Help

### Community & Support
- **GitHub Issues:** https://github.com/yourusername/arifOS/issues
- **Documentation Index:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Constitutional Questions:** See AGENTS.md for governance framework

### Debugging Steps
1. **Verify Python version:** `python --version` (must be ≥ 3.10)
2. **Run verification:** `python setup/verification/verify_setup.py`
3. **Check dependencies:** `pip list | grep arifos`
4. **Review logs:** Check console output for errors
5. **Constitutional check:** Ensure GOVERNANCE_MODE set correctly

### Common Questions

**Q: Do I need to run bootstrap every session?**
A: No. Bootstrap is one-time setup. Use `python setup/on_workspace_open.py` for daily sessions.

**Q: Can I skip the virtual environment?**
A: Not recommended. Virtual environments prevent dependency conflicts.

**Q: What's the difference between HARD and SOFT governance?**
A: HARD enforces strict constitutional compliance (production). SOFT allows warnings (development).

**Q: Do I need Docker?**
A: No, Docker is optional. Required only for containerized deployments.

**Q: How do I update dependencies?**
A: `pip install --upgrade -e .[all]` updates all packages to latest compatible versions.

---

**DITEMPA BUKAN DIBERI** — *Session requirements forged from comprehensive root analysis, not assumed from documentation.*

**Version:** v49.0.0 | **Last Updated:** 2026-01-18 | **Status:** SEALED
**Constitutional Authority:** F1 (Amanah) + F2 (Truth) + F4 (ΔS Clarity) + F6 (Empathy)
