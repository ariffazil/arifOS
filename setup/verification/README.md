# Verification Scripts

Verify your installation is working correctly.

## Run Verification

```bash
# Activate environment first
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Run verification
python verify_setup.py
```

## Expected Output

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

## Troubleshooting

If checks fail:
1. Activate virtual environment
2. Reinstall: `pip install -e ".[all]"`
3. Check [../docs/DEVELOPMENT_SETUP.md](../docs/DEVELOPMENT_SETUP.md)
