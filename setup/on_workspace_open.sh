#!/bin/bash
# arifOS IDE-Agnostic Auto-Bootstrap (Bash)
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
  echo "arifOS: Setting up environment (auto-bootstrap)..."
  python3 setup/bootstrap/bootstrap.py --full
else
  echo "arifOS: Environment already set up."
fi
