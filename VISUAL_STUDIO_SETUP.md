# Visual Studio Setup Guide for arifOS v46.2

**Status:** ? COMPLETE - All dependencies installed
**Date:** 2026-01-18
**Python Version:** 3.14.0
**Docker Version:** 29.1.3

---

## ? Installation Complete

Your Visual Studio environment is now fully configured with all arifOS dependencies!

### Installed Components

#### Core Dependencies ?
- **Python 3.14.0** - Installed and configured
- **pip 25.3** - Latest package manager
- **Virtual Environment** - `.venv` activated at `C:\Users\User\OneDrive\Documents\GitHub\arifOS\.venv`

#### arifOS Package ?
- **arifos 46.2.2** - Installed in editable mode with `[all]` extras
- **numpy 2.4.0** - Mathematical operations
- **pydantic 2.12.5** - Data validation and settings management

#### AI/LLM Dependencies ?
- **litellm 1.64.17** - Universal LLM adapter (OpenAI, Claude, Gemini, SEA-LION)
- **openai 1.63.2** - OpenAI API client
- **httpx 0.28.1** - Async HTTP client
- **tiktoken 0.12.0** - Token counting

#### MCP Server Dependencies ?
- **fastmcp 2.14.2** - Fast MCP server implementation
- **pydocket 0.16.3** - Docker management for Python
- **mcp 1.6.0** - Model Context Protocol SDK

#### API Server Dependencies ?
- **fastapi 0.120.5** - Modern web framework
- **uvicorn 0.40.0** - ASGI server with standard extensions
- **httptools 0.7.1** - Fast HTTP parser
- **watchfiles 1.1.1** - File watcher for hot reload

#### DSPy Integration ?
- **dspy-ai 2.6.20** - Framework for LLM programming
- **datasets 3.4.0** - Dataset management
- **optuna 4.3.0** - Hyperparameter optimization

#### Development Tools ?
- **pytest 9.0.2** - Testing framework
- **pytest-cov 7.0.0** - Coverage reporting
- **pytest-asyncio 1.3.0** - Async test support
- **pytest-mock 3.15.1** - Mocking utilities
- **black 25.1.0** - Code formatter
- **ruff 0.14.10** - Fast Python linter
- **mypy 1.15.0** - Static type checker

#### Docker ?
- **Docker 29.1.3** - Container platform (already installed)
- **docker-py** - Python Docker SDK (via litellm)

---

## ?? Quick Start Commands

### Activate Virtual Environment
```powershell
# From project root
.\.venv\Scripts\Activate.ps1
```

### Run arifOS Scripts
```powershell
# Analyze audit trail
arifos-analyze-audit-trail

# Verify governance
arifos-analyze-governance

# Verify ledger chain
arifos-verify-ledger

# Compute Merkle root
arifos-compute-merkle
```

### Start MCP Server
```powershell
# From arifos_core/mcp directory
cd arifos_core\mcp
python -m uvicorn vault999_server:app --reload
```

### Run Tests
```powershell
# Run all tests
pytest

# With coverage
pytest --cov=arifos_core --cov-report=html

# Specific test file
pytest tests/test_apex_prime.py
```

### Start FastAPI Server
```powershell
# From project root
uvicorn arifos_orchestrator.main:app --reload --port 8000
```

---

## ?? Visual Studio Configuration

### Python Environment
Visual Studio should automatically detect your `.venv` virtual environment.

**To verify:**
1. Open **View** ? **Other Windows** ? **Python Environments**
2. Confirm `.venv (Python 3.14)` is selected
3. If not, click **Add Environment** ? **Existing environment** ? Browse to `.venv\Scripts\python.exe`

### Recommended VS Extensions

Install these for better arifOS development:

1. **Python** (Microsoft) - Core Python support
2. **Pylance** (Microsoft) - Advanced IntelliSense
3. **Python Debugger** (Microsoft) - Debugging support
4. **Ruff** (Astral Software) - Fast linting
5. **Black Formatter** (Microsoft) - Code formatting
6. **Docker** (Microsoft) - Container management
7. **REST Client** - Test API endpoints

### Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "arifOS: APEX Prime",
      "type": "debugpy",
      "request": "launch",
      "module": "arifos_core.system.apex_prime",
      "console": "integratedTerminal",
      "env": {
        "ARIFOS_ENV": "development"
      }
    },
    {
      "name": "arifOS: MCP Server",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "arifos_core.mcp.vault999_server:app",
        "--reload"
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

### Tasks Configuration

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "${workspaceFolder}\\.venv\\Scripts\\pytest.exe",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Start MCP Server",
      "type": "shell",
      "command": "${workspaceFolder}\\.venv\\Scripts\\uvicorn.exe",
      "args": [
        "arifos_core.mcp.vault999_server:app",
        "--reload"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Format Code (Black)",
      "type": "shell",
      "command": "${workspaceFolder}\\.venv\\Scripts\\black.exe",
      "args": [
        "."
      ],
      "problemMatcher": []
    },
    {
      "label": "Lint (Ruff)",
      "type": "shell",
      "command": "${workspaceFolder}\\.venv\\Scripts\\ruff.exe",
      "args": [
        "check",
        "."
      ],
      "problemMatcher": []
    }
  ]
}
```

---

## ?? Environment Configuration

### Create .env File

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` with your actual API keys:

```bash
# LLM Provider Configuration
ARIF_LLM_PROVIDER=openai
ARIF_LLM_API_BASE=https://api.sea-lion.ai/v1
ARIF_LLM_API_KEY=your-sealion-api-key-here
SEALION_API_KEY=your-sealion-api-key-here
ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT

# arifOS Governance
ARIFOS_ENV=development
ARIFOS_ENABLE_WAW=true
ARIFOS_LEDGER_PATH=cooling_ledger/L1_cooling_ledger.jsonl
```

### Get API Keys

**SEA-LION (recommended for arifOS):**
- Visit: https://playground.sea-lion.ai
- Sign up and get your API key
- Paste into `.env` file

**Alternatives:**
- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic (Claude):** https://console.anthropic.com/
- **Google (Gemini):** https://makersuite.google.com/app/apikey

---

## ?? Docker Configuration

Docker is already installed. To use Docker with arifOS:

### Start Docker Desktop
Make sure Docker Desktop is running before using container features.

### Test Docker Installation
```powershell
docker run hello-world
```

### Run arifOS in Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Copy requirements
COPY pyproject.toml .
COPY README.md .
COPY arifos_core ./arifos_core

# Install dependencies
RUN pip install -e ".[all]"

# Expose ports
EXPOSE 8000 5000

# Run MCP server
CMD ["uvicorn", "arifos_core.mcp.vault999_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```powershell
docker build -t arifos:latest .
docker run -p 8000:8000 --env-file .env arifos:latest
```

---

## ?? Verify Installation

Run these commands to verify everything works:

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Check Python
python --version
# Expected: Python 3.14.0

# Check arifOS
python -c "import arifos_core; print('arifOS version:', arifos_core.__version__)"
# Expected: arifOS version: 46.2.2

# Check dependencies
python -c "import pydantic, numpy, litellm, fastmcp, dspy; print('All imports successful!')"
# Expected: All imports successful!

# Check Docker
docker --version
# Expected: Docker version 29.1.3

# Run a simple test
python -c "from arifos_core.system.apex_prime import APEXPrime; apex = APEXPrime(); print('APEX Prime initialized:', apex)"
# Expected: APEX Prime initialized: <APEXPrime object at ...>
```

---

## ?? Next Steps

1. **Read the Documentation**
   - `AGENTS.md` - Agent roles and specifications
   - `README.md` - Project overview
   - `L1_THEORY/canon/000_foundation/` - Constitutional law

2. **Explore Examples**
   - `L7_DEMOS/examples/` - Integration examples
   - `examples/` - Usage examples

3. **Run Tests**
   ```powershell
   pytest tests/
   ```

4. **Start Development**
   - Open `arifos_core/system/apex_prime.py` to see the core verdict engine
   - Check `L2_PROTOCOLS/v46/constitutional_floors.json` for floor specifications
   - Explore `arifos_core/agi/`, `arifos_core/asi/`, `arifos_core/apex/` for the AAA Trinity

5. **Try the MCP Server**
   ```powershell
   cd arifos_core\mcp
   python -m uvicorn vault999_server:app --reload
   # Visit http://localhost:8000/docs for API documentation
   ```

---

## ?? Troubleshooting

### Python Environment Not Detected

If Visual Studio doesn't detect the virtual environment:

1. **Manually select interpreter:**
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose `.venv\Scripts\python.exe`

2. **Rebuild environment:**
   ```powershell
   deactivate
   Remove-Item -Recurse -Force .venv
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e ".[all]"
   ```

### Import Errors

If you get `ModuleNotFoundError`:

1. **Verify installation:**
   ```powershell
   pip list | Select-String "arifos"
   ```

2. **Reinstall in editable mode:**
   ```powershell
   pip install -e ".[all]"
   ```

3. **Check PYTHONPATH:**
   ```powershell
   $env:PYTHONPATH = "C:\Users\User\OneDrive\Documents\GitHub\arifOS"
   ```

### Docker Issues

If Docker commands fail:

1. **Start Docker Desktop** - Must be running
2. **Check Docker service:**
   ```powershell
   Get-Service -Name "com.docker.service"
   ```
3. **Restart Docker Desktop** if needed

### Dependency Conflicts

If you encounter dependency conflicts:

```powershell
# Force upgrade conflicting packages
pip install --upgrade rich uvicorn fastapi

# Or reinstall all dependencies
pip install --force-reinstall -e ".[all]"
```

---

## ?? Summary

Your Visual Studio is now fully configured for arifOS development with:

? Python 3.14.0 + virtual environment  
? arifOS 46.2.2 (editable mode)  
? All core dependencies (numpy, pydantic, litellm)  
? MCP server support (fastmcp)  
? API server (FastAPI + Uvicorn)  
? DSPy integration  
? Testing framework (pytest)  
? Development tools (black, ruff, mypy)  
? Docker 29.1.3  

**You're ready to develop constitutionally governed AI! ???**

---

## ?? Support

- **Documentation:** Check `AGENTS.md` and `README.md`
- **Issues:** https://github.com/ariffazil/arifOS/issues
- **Constitutional Law:** `L1_THEORY/canon/000_foundation/`
- **Specifications:** `L2_PROTOCOLS/v46/`

**DITEMPA BUKAN DIBERI** — Your development environment is forged, not given. ??
