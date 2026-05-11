from __future__ import annotations

import os
from pathlib import Path


def inspect_path(path: str, include_hidden: bool = False, max_depth: int = 2) -> dict:
    root = Path(path)
    if not root.exists():
        return {"error": f"path not found: {path}", "entries": []}
    entries = []
    base_depth = len(root.parts)
    for current, dirs, files in os.walk(root):
        depth = len(Path(current).parts) - base_depth
        if depth > max_depth:
            dirs[:] = []
            continue
        names = list(dirs) + list(files)
        for name in names:
            if not include_hidden and name.startswith("."):
                continue
            entries.append(str(Path(current) / name))
    return {"path": str(root), "entries": entries}
