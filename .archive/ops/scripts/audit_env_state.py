"""Audit environment-variable drift without exposing secret values.

Usage:
    python scripts/audit_env_state.py
"""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOBAL_ENV = Path.home() / ".arifos" / "env"

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".pytest_cache_win",
    "archive",
    "archive_local",
    "_ARCHIVE",
    "dist",
    "build",
    "node_modules",
    "remote_inspection",
    "telemetry",
    "memory",
    "VAULT999",
}

CODE_VAR_RE = re.compile(r"os\.(?:getenv|environ\.get)\(\s*['\"]([A-Z0-9_]+)['\"]")
ENV_LINE_RE = re.compile(r"^[A-Z0-9_]+=.*$")


def code_vars() -> set[str]:
    vars_found: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = Path(dirpath) / name
            text = path.read_text(encoding="utf-8", errors="ignore")
            vars_found.update(CODE_VAR_RE.findall(text))

    return vars_found


def env_keys(path: Path) -> set[str]:
    if not path.is_file():
        return set()

    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if not ENV_LINE_RE.match(s):
            continue
        keys.add(s.split("=", 1)[0])
    return keys


def summarize(name: str, file_keys: set[str], code: set[str]) -> None:
    overlap = file_keys & code
    unused = file_keys - code
    missing = code - file_keys
    print(f"[{name}]")
    print(f"  keys_total: {len(file_keys)}")
    print(f"  keys_used_by_code: {len(overlap)}")
    print(f"  keys_unused_by_code: {len(unused)}")
    print(f"  code_vars_missing_from_file: {len(missing)}")


def main() -> int:
    code = code_vars()

    files = {
        "repo .env": ROOT / ".env",
        "repo .env.example": ROOT / ".env.example",
        "repo .env.docker.example": ROOT / ".env.docker.example",
        "global ~/.arifos/env": GLOBAL_ENV,
    }

    print("arifOS environment drift audit")
    print(f"code_env_vars_detected: {len(code)}")
    print()

    for name, path in files.items():
        summarize(name, env_keys(path), code)

    missing_global = sorted(code - env_keys(GLOBAL_ENV))
    print()
    print("missing_in_global_first_25:")
    for key in missing_global[:25]:
        print(f"  - {key}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
