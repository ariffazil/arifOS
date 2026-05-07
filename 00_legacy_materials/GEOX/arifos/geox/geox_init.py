"""
arifos/geox/geox_init.py — GEOX Foundation Hardening

This module provides the "Ignition State" for GEOX, ensuring:
- Operational environment verification (F9 Physics9)
- Identity anchoring (F11 Authority)
- System health and dependency checks
- arifOS Constitutional alignment
"""

import logging
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("geox.init")


def _candidate_arifos_paths() -> list[Path]:
    roots: list[Path] = []
    env_root = os.getenv("ARIFOS_ROOT")
    if env_root:
        roots.append(Path(env_root))

    here = Path(__file__).resolve()
    for parent in here.parents:
        sibling = parent / "arifOS"
        if sibling.exists():
            roots.append(sibling)
        if (parent / "arifosmcp").exists():
            roots.append(parent)

    unique: list[Path] = []
    seen: set[str] = set()
    for path in roots:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def _bootstrap_arifosmcp_path() -> bool:
    for root in _candidate_arifos_paths():
        candidates = [root, root / "arifosmcp", root / "arifosmcp" / "sites"]
        for candidate in candidates:
            candidate_str = str(candidate)
            if candidate.exists() and candidate_str not in sys.path:
                sys.path.append(candidate_str)
        try:
            __import__("arifosmcp")
            return True
        except ImportError:
            continue
    return False


class GEOXFoundation:
    """Hardened foundation for GEOX intelligence."""

    VERSION = "0.1.0-hardened"
    REQUIRED_PY_VERSION = (3, 10)

    @classmethod
    def ignite(cls) -> dict[str, Any]:
        """
        Ignite the GEOX foundation.
        Performs environment checks and returns the system status.
        """
        cwd = os.getcwd()
        status: dict[str, Any] = {
            "version": cls.VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "os": platform.system(),
            "python": sys.version.split()[0],
            "checks": {},
            "verdict": "CLEAR",
        }

        # 1. Python Version Check (F9 Physics9)
        if sys.version_info < cls.REQUIRED_PY_VERSION:
            status["checks"]["python_version"] = "FAIL"
            status["verdict"] = "VOID"
            logger.error(f"Python {cls.REQUIRED_PY_VERSION} required, found {sys.version}")
        else:
            status["checks"]["python_version"] = "OK"

        # 2. Dependency Verification (F9 Physics9)
        essential_deps = ["pydantic", "httpx", "yaml", "arifosmcp"]
        missing_deps = []
        for dep in essential_deps:
            try:
                if dep == "arifosmcp" and not _bootstrap_arifosmcp_path():
                    raise ImportError("arifosmcp import path bootstrap failed")
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)

        if missing_deps:
            status["checks"]["dependencies"] = f"FAIL (missing: {', '.join(missing_deps)})"
            # arifosmcp is not strictly mandatory for local tools but good for hardening
            if "arifosmcp" not in missing_deps:
                status["verdict"] = "VOID"
        else:
            status["checks"]["dependencies"] = "OK"

        # 3. arifOS Alignment (F11 Authority)
        # Check if running in the correct ariffazil directory
        path_norm = os.path.normpath(cwd).lower()
        is_ariffazil = "ariffazil" in path_norm
        status["arifos_aligned"] = (
            is_ariffazil or os.environ.get("ARIFOS_KERNEL_VERSION") is not None
        )

        # 4. Workspace Integrity (F1 Amanah)
        has_git = os.path.isdir(os.path.join(cwd, ".git"))
        has_venv = os.path.exists(os.path.join(cwd, ".venv"))
        status["checks"]["workspace"] = "GIT_REPO" if has_git else "LOCAL_DIR"
        status["checks"]["venv"] = "VENV_LOCKED" if has_venv else "NATIVE"

        if not has_git:
            status["verdict"] = "888_HOLD"  # Warn if not a git repo

        logger.info(f"GEOX Foundation Ignited: {status['verdict']}")
        return status


def verify_and_exit_if_void():
    """Standard entrypoint check for CLI tools."""
    status = GEOXFoundation.ignite()
    if status["verdict"] == "VOID":
        print(f"CRITICAL: GEOX Foundation Failure - {status['checks']}")
        sys.exit(1)
    return status
