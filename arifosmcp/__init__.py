"""arifOS MCP package root.

This package is imported under both ``arifosmcp`` and the historical
``arifosmcp`` alias. Keep both names bound to the same module object so
runtime globals, Prometheus collectors, and subpackages do not initialize
twice during mixed-import test runs.
"""

from __future__ import annotations

import sys

if __name__ == "arifosmcp":
    sys.modules.setdefault("arifosmcp", sys.modules[__name__])
elif __name__ == "arifosmcp":
    sys.modules.setdefault("arifosmcp", sys.modules[__name__])
