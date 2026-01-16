# ?? arifOS Visual Studio Quick Start

**Status:** ? READY TO CODE
**Setup Date:** 2026-01-18
**Python:** 3.14.0 | **Docker:** 29.1.3 | **arifOS:** 46.2.2

---

## ? 30-Second Start

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Verify installation
python -c "from arifos_core.system.apex_prime import APEXPrime, APEX_VERSION; print(f'? arifOS {APEX_VERSION} ready!')"

# 3. Start coding!
code .
```

---

## ?? Essential Commands

### Development

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Run tests
pytest

# Format code
black .

# Lint code
ruff check .

# Type check
mypy arifos_core
```

### MCP Server

```powershell
# Start VAULT999 MCP server
cd arifos_core\mcp
python -m uvicorn vault999_server:app --reload

# Access API docs
# http://localhost:8000/docs
```

### Docker

```powershell
# Build image
docker build -t arifos:latest .

# Run container
docker run -p 8000:8000 --env-file .env arifos:latest
```

---

## ?? Key Files to Know

### Constitutional Law (L1 - READ ONLY)
```
L1_THEORY/canon/000_foundation/
??? 000_CONSTITUTIONAL_CORE_v46.md    ? 12 Floors + AAA Trinity
??? 002_GEOMETRY_OF_INTELLIGENCE_v46.md ? ??? Physics
??? 004_ARCHITECTURAL_MAP_v46.md      ? System architecture
```

### Specifications (L2 - VERSIONED)
```
L2_PROTOCOLS/v46/
??? constitutional_floors.json         ? Floor thresholds (PRIMARY SOURCE)
??? 000_foundation/                    ? Stage 000 (Foundation Gate)
??? 888_compass/                       ? Stage 888 (APEX Judgment)
??? agent_specifications.json          ? Agent roles (? ? ?)
```

### Implementation (L3 - ACTIVE CODE)
```
arifos_core/
??? system/apex_prime.py               ? APEX verdict engine (SOUL)
??? agi/                               ? AGI engine (MIND - ?)
??? asi/                               ? ASI engine (HEART - ?)
??? apex/                              ? APEX orchestrator (SOUL - ?)
??? mcp/                               ? MCP server implementation
```

---

## ?? Test Your Setup

```powershell
# Test 1: Import check
python -c "import arifos_core; print('? arifOS imported')"

# Test 2: APEX Prime initialization
python -c "from arifos_core.system.apex_prime import APEXPrime, APEX_VERSION; apex = APEXPrime(); print(f'? APEX {APEX_VERSION} initialized')"

# Test 3: All dependencies
python -c "import numpy, pydantic, litellm, fastmcp, dspy, fastapi, uvicorn; print('? All deps ready')"

# Test 4: Run test suite
pytest tests/ -v

# Test 5: Docker verification
docker --version
```

**Expected output:** All tests pass with ?

---

## ?? The AAA Trinity (Who Does What)

| Agent | Symbol | Role | Stages | Responsibility |
|-------|--------|------|--------|----------------|
| **AGI** | ? (Delta) | Architect | 111-333 | Truth, Clarity, Logic |
| **ASI** | ? (Omega) | Auditor | 444-666 | Care, Empathy, Stability |
| **APEX** | ? (Psi) | Judge | 888 | Final Verdict, Integrity |

**The Pipeline:** 000 ? 111 ? 222 ? 333 ? 444 ? 555 ? 666 ? 777 ? 888 ? 999

---

## ?? Common Tasks

### Create a New Floor Check

```python
# File: arifos_core/agi/floor_checks.py

from ..enforcement.metrics import FloorCheckResult

def check_new_floor(response: str) -> FloorCheckResult:
    """Check Floor X: Your description."""
    threshold = 0.95
    score = calculate_score(response)  # Your logic
    
    return FloorCheckResult(
        floor_id="FX",
        floor_name="YourFloorName",
        threshold=threshold,
        score=score,
        passed=score >= threshold,
        is_hard=True,  # or False for soft floor
        reason="Floor X check result"
    )
```

### Add a New MCP Tool

```python
# File: arifos_core/mcp/vault999_server.py

@app.tool()
async def your_tool_name(arg1: str, arg2: int) -> dict:
    """
    Tool description.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
    
    Returns:
        Result dictionary
    """
    # Your implementation
    return {"result": "success"}
```

### Run a Specific Test

```powershell
# Test APEX Prime
pytest tests/test_apex_prime.py -v

# Test with coverage
pytest tests/test_apex_prime.py --cov=arifos_core.system.apex_prime

# Test specific function
pytest tests/test_apex_prime.py::test_function_name -v
```

---

## ?? Quick Debugging

### Import Error?

```powershell
# Check installation
pip show arifos

# Reinstall if needed
pip install -e ".[all]"

# Verify PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"
```

### Test Failure?

```powershell
# Run with verbose output
pytest -vv

# Run with print statements visible
pytest -s

# Run only failed tests
pytest --lf

# Run and drop into debugger on failure
pytest --pdb
```

### Docker Issue?

```powershell
# Check Docker is running
docker ps

# Restart Docker Desktop if needed
# Check Docker Desktop GUI

# View container logs
docker logs <container_id>
```

---

## ?? Learning Path

### Day 1: Constitutional Basics
1. Read `README.md` - System overview
2. Read `AGENTS.md` - Agent specifications
3. Read `L1_THEORY/canon/000_foundation/000_CONSTITUTIONAL_CORE_v46.md` - The 12 Floors

### Day 2: Architecture
1. Read `L1_THEORY/canon/000_foundation/002_GEOMETRY_OF_INTELLIGENCE_v46.md` - ??? Physics
2. Study `L2_PROTOCOLS/v46/constitutional_floors.json` - Floor thresholds
3. Explore `arifos_core/system/apex_prime.py` - Verdict engine

### Day 3: Hands-On
1. Run `pytest tests/` - Understand test patterns
2. Explore `L7_DEMOS/examples/` - Integration examples
3. Start modifying code - Make your first constitutional change

### Day 4: Deep Dive
1. Study the pipeline stages (000-999)
2. Understand the AAA Trinity separation
3. Explore MCP server implementation

---

## ?? Pro Tips

1. **Use the REPL for quick tests:**
   ```powershell
   python
   >>> from arifos_core.system.apex_prime import *
   >>> apex = APEXPrime()
   >>> # Test your code here
   ```

2. **Watch files during development:**
   ```powershell
   # Auto-reload on changes
   uvicorn arifos_core.mcp.vault999_server:app --reload
   ```

3. **Use pytest markers:**
   ```python
   @pytest.mark.slow
   def test_expensive_operation():
       pass
   
   # Run: pytest -m "not slow"  # Skip slow tests
   ```

4. **Format on save in VS Code:**
   - Install "Black Formatter" extension
   - Set as default Python formatter
   - Enable "Format On Save"

5. **Type hints everywhere:**
   ```python
   def check_floor(response: str, threshold: float) -> FloorCheckResult:
       # MyPy will catch type errors!
   ```

---

## ?? Environment Variables

Create `.env` file:

```bash
# Required
ARIF_LLM_API_KEY=your-api-key-here
SEALION_API_KEY=your-api-key-here

# Optional (defaults shown)
ARIFOS_ENV=development
ARIFOS_ENABLE_WAW=true
ARIFOS_LEDGER_PATH=cooling_ledger/L1_cooling_ledger.jsonl
ARIF_LLM_PROVIDER=openai
ARIF_LLM_MODEL=aisingapore/Llama-SEA-LION-v3-70B-IT
```

---

## ?? Your First Contribution

Ready to contribute? Here's the workflow:

```powershell
# 1. Create a feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# Edit files in arifos_core/

# 3. Format and lint
black .
ruff check .

# 4. Test your changes
pytest

# 5. Commit with constitutional compliance
git add .
git commit -m "feat: Your feature (F1-F12 compliant)"

# 6. Push and create PR
git push origin feature/your-feature-name
```

---

## ?? Help & Support

- **Documentation:** `VISUAL_STUDIO_SETUP.md` (full guide)
- **Issues:** https://github.com/ariffazil/arifOS/issues
- **Constitutional Law:** `L1_THEORY/canon/`
- **API Reference:** Start MCP server ? http://localhost:8000/docs

---

## ? Ready to Build Constitutional AI!

Your environment is **fully configured and tested**. You have:

? Python 3.14 + arifOS 46.2.2  
? All dependencies (LLM, MCP, DSPy, Docker)  
? Testing framework ready  
? Development tools configured  
? Docker support enabled  

**DITEMPA BUKAN DIBERI** — Your development environment is forged, not given.

**Now go build constitutionally governed AI! ?????**
