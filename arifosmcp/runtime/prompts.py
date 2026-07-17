"""
arifosmcp/runtime/prompts.py — register_prompts shim

Routes to the canonical implementation in fastmcp_ext/prompts.py.
This shim exists because the CI shim resolution test imports
`arifosmcp.runtime.prompts.register_prompts` as a public surface entry.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from arifosmcp.runtime.fastmcp_ext.prompts import (
    register_arifos_prompts as register_prompts,  # noqa: F401
)
