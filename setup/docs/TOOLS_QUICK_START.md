# ?? IDE-Agnostic Auto-Bootstrap (Recommended)

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
