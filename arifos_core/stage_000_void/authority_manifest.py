"""Compatibility shim for Stage 000 canonical implementation.

Canonical source: arifos_core/000_void/authority_manifest.py
"""

from pathlib import Path
_CANONICAL_PATH = Path(__file__).resolve().parent.parent / "000_void" / "authority_manifest.py"
exec(_CANONICAL_PATH.read_text(encoding="utf-8"), globals())
