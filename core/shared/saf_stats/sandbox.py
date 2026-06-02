"""F6 PRIVACY sandbox. All file I/O resolves under SAF_DATA_ROOT.

Path traversal is blocked, extensions are validated, and the canonical
absolute path is always returned. The data root defaults to
/root/SAF/saf-data if SAF_DATA_ROOT is unset.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

ALLOWED_READ_EXTS = {".sav", ".zsav", ".por", ".csv", ".tsv"}
ALLOWED_WRITE_EXTS = {".sav", ".csv", ".tsv", ".json", ".md", ".txt", ".log"}

DEFAULT_DATA_ROOT = "/root/SAF/saf-data"


def get_data_root() -> Path:
    """Resolve the SAF_DATA_ROOT, creating it if missing."""
    root = os.environ.get("SAF_DATA_ROOT", DEFAULT_DATA_ROOT)
    p = Path(root).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def _validate_extension(path: Path, allowed: Iterable[str], mode: str) -> None:
    ext = path.suffix.lower()
    if ext not in allowed:
        raise PermissionError(
            f"F6 PRIVACY: {mode} blocked — extension '{ext}' not in {sorted(allowed)}"
        )


def safe_resolve(
    user_path: str | os.PathLike,
    *,
    mode: str = "read",
    must_exist: bool = True,
) -> Path:
    """Resolve *user_path* under the SAF_DATA_ROOT.

    - Rejects absolute paths that escape the root.
    - Rejects `..` traversal.
    - Validates extension against the mode's allowlist.
    """
    root = get_data_root()
    up = Path(user_path)

    # Absolute path outside root is an immediate block.
    if up.is_absolute():
        try:
            up.resolve(strict=False).relative_to(root)
        except ValueError:
            raise PermissionError(
                f"F6 PRIVACY: path '{user_path}' is outside SAF_DATA_ROOT ({root})"
            )
        resolved = up.resolve(strict=False)
    else:
        resolved = (root / up).resolve(strict=False)

    # Defence in depth — re-check containment.
    try:
        resolved.relative_to(root)
    except ValueError:
        raise PermissionError(
            f"F6 PRIVACY: resolved path '{resolved}' escapes SAF_DATA_ROOT ({root})"
        )

    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"file not found in sandbox: {resolved}")

    allowed = ALLOWED_READ_EXTS if mode == "read" else ALLOWED_WRITE_EXTS
    _validate_extension(resolved, allowed, mode)

    return resolved


def relative_to_root(p: Path) -> str:
    """Return a stable, sandbox-relative display path."""
    root = get_data_root()
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)
