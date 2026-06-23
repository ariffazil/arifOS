"""Shared helpers for the arifOS CLI."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from typing import Any


class CliError(Exception):
    """Recoverable CLI error with user-facing message."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def http_post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    """POST JSON and return parsed JSON response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise CliError(f"HTTP {exc.code} from {url}: {body}", code=exc.code) from exc
    except urllib.error.URLError as exc:
        raise CliError(f"Cannot reach {url}: {exc.reason}", code=2) from exc
    except TimeoutError as exc:
        raise CliError(f"Timeout reaching {url}", code=2) from exc


def http_get_json(url: str, timeout: int = 10) -> dict[str, Any]:
    """GET JSON and return parsed response."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise CliError(f"HTTP {exc.code} from {url}: {body}", code=exc.code) from exc
    except urllib.error.URLError as exc:
        raise CliError(f"Cannot reach {url}: {exc.reason}", code=2) from exc
    except TimeoutError as exc:
        raise CliError(f"Timeout reaching {url}", code=2) from exc


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run git and return (returncode, stdout, stderr)."""
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def get_writer_token() -> str:
    """Resolve VAULT999 writer token from env or secret file."""
    token = os.getenv("VAULT_WRITER_TOKEN", "")
    if token:
        return token
    secret_path = os.getenv("VAULT_WRITER_TOKEN_FILE", "/run/secrets/vault_writer_token")
    try:
        with open(secret_path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
