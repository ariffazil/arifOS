"""Compatibility shim for Stage 000 canonical implementation.

Canonical source: arifos/000_void/injection_defense.py
"""

from pathlib import Path
_CANONICAL_PATH = Path(__file__).resolve().parent.parent / "000_void" / "injection_defense.py"
exec(_CANONICAL_PATH.read_text(encoding="utf-8"), globals())
