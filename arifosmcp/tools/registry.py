from pathlib import Path
from typing import Any

import yaml

CHARTER_DIR = Path(__file__).parent / "charters"


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, dict[str, Any]] = {}
        self._load_charters()

    def _load_charters(self):
        if not MANIFEST_DIR.exists():
            return

        for charter_path in CHARTER_DIR.glob("**/*.yaml"):
            with open(charter_path) as f:
                try:
                    charter = yaml.safe_load(f)
                    if charter and "name" in charter:
                        self.tools[charter["name"]] = charter
                except Exception:
                    continue

    def get_tool(self, name: str) -> dict[str, Any] | None:
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())


registry = ToolRegistry()
