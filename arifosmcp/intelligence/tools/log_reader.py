from __future__ import annotations

import os
from pathlib import Path


def log_tail(
    log_file: str = "arifos.log",
    lines: int = 100,
    pattern: str | None = None,
    log_path: str | None = None,
    follow: bool = False,
    grep_pattern: str | None = None,
    since_minutes: int | None = None,
) -> dict:
    del follow, since_minutes
    path = Path(log_path) / log_file if log_path else Path(log_file)
    if not os.path.exists(path):
        return {"error": f"log file not found: {path}", "lines": []}
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            content = handle.readlines()
        selected = content[-lines:]
        if pattern:
            selected = [line for line in selected if pattern in line]
        if grep_pattern:
            selected = [line for line in selected if grep_pattern in line]
        return {
            "log_file": str(path),
            "lines": [line.rstrip("\n") for line in selected],
        }
    except Exception as exc:
        return {"error": str(exc), "lines": []}
