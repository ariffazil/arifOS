"""
SkillsDirectoryProvider — Domain Skill Loader
══════════════════════════════════════════════

Loads domain skills from skills/geox/, skills/wealth/, skills/well/.
Skills are NOT top-level MCP tools; they are callable sub-capabilities
invoked by canonical tools via mode delegation.
"""
from __future__ import annotations

import importlib.util
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SKILL_DIRS: dict[str, Path] = {
    "geox": Path("skills/geox"),
    "wealth": Path("skills/wealth"),
    "well": Path("skills/well"),
}


class SkillsDirectoryProvider:
    """
    Loads domain skills from the filesystem.

    Skills are exposed as callable functions keyed by domain and name.
    They are invoked by canonical tools, not registered as MCP tools.
    """

    def __init__(self, root: str | Path | None = None) -> None:
        self._root = Path(root) if root else Path(".")
        self._skills: dict[str, dict[str, Callable[..., Any]]] = {
            "geox": {},
            "wealth": {},
            "well": {},
        }
        self._load_all()

    def _load_domain(self, domain: str, path: Path) -> None:
        if not path.exists():
            logger.debug(f"[SkillsDirectoryProvider] Skill path missing: {path}")
            return

        for item in path.iterdir():
            if item.is_file() and item.suffix == ".py" and not item.name.startswith("_"):
                name = item.stem
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"arifosmcp.skills.{domain}.{name}", str(item)
                    )
                    if spec is None or spec.loader is None:
                        continue
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    for attr in dir(mod):
                        if attr.startswith("_"):
                            continue
                        obj = getattr(mod, attr)
                        if callable(obj):
                            key = f"{domain}/{name}.{attr}"
                            self._skills[domain][key] = obj
                    logger.debug(f"[SkillsDirectoryProvider] Loaded skill: {domain}/{name}")
                except Exception as e:
                    logger.warning(f"[SkillsDirectoryProvider] Failed to load {domain}/{name}: {e}")

    def _load_all(self) -> None:
        for domain, rel_path in _SKILL_DIRS.items():
            self._load_domain(domain, self._root / rel_path)

    def get(self, domain: str, name: str) -> Callable[..., Any] | None:
        """Retrieve a skill by domain and fully-qualified name."""
        return self._skills.get(domain, {}).get(name)

    def list_skills(self, domain: str | None = None) -> dict[str, list[str]]:
        """List loaded skills, optionally filtered by domain."""
        if domain:
            return {domain: list(self._skills.get(domain, {}).keys())}
        return {k: list(v.keys()) for k, v in self._skills.items()}

    def invoke(self, domain: str, name: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke a skill by domain and name."""
        skill = self.get(domain, name)
        if skill is None:
            raise ValueError(f"Skill not found: {domain}/{name}")
        return skill(*args, **kwargs)
