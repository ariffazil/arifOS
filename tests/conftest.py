import sys
from pathlib import Path

# Ensure the repository root is on sys.path so tests can import arifos_core without requiring an installed package.
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
