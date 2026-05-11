"""
arifosmcp/core/ — empty package.

Canonical core lives at /core/ (root level).
arifosmcp/core/ exists solely to hold constitution_kernel.py
and floors.py which are imported via 'from arifosmcp.core.X'.

No re-exports — that creates a shadow namespace collision
with root /core/ which is reached via absolute import.
"""
