#!/usr/bin/env python3
"""
arifOS IDE-Agnostic Auto-Bootstrap Script

- Ensures .venv exists and is healthy
- Ensures arifOS and all dependencies are installed
- Runs full bootstrap if needed
- Safe to run on every workspace/session open (idempotent)
"""

import os
import sys
import subprocess
from pathlib import Path

def venv_ok():
    venv = Path(".venv")
    if not venv.exists():
        return False
    if not (venv / "Scripts" / "python.exe").exists() and not (venv / "bin" / "python").exists():
        return False
    return True

def pip_check():
    python = (
        str(Path(".venv") / "Scripts" / "python.exe")
        if (Path(".venv") / "Scripts" / "python.exe").exists()
        else str(Path(".venv") / "bin" / "python")
    )
    try:
        out = subprocess.check_output(
            [python, "-m", "pip", "freeze"], text=True, stderr=subprocess.DEVNULL
        )
        required = ["arifos", "numpy", "pydantic", "litellm", "fastapi", "uvicorn"]
        return all(any(r.lower() in line.lower() for line in out.splitlines()) for r in required)
    except Exception:
        return False

def main():
    print("arifOS: Checking environment foundation...")
    if not venv_ok() or not pip_check():
        print("arifOS: Environment incomplete. Running bootstrap...")
        bootstrap = "setup/bootstrap/bootstrap.py"
        python = sys.executable
        if not Path(bootstrap).exists():
            print("arifOS: ERROR - Bootstrap script not found!")
            sys.exit(1)
        subprocess.run([python, bootstrap, "--full"], check=True)
        print("arifOS: Bootstrap complete.")
    else:
        print("arifOS: Environment is ready.")

if __name__ == "__main__":
    main()
