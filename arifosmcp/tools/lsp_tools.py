"""
Compatibility shim — renamed to lsp.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("lsp_tools.py is deprecated — use lsp.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.lsp import *  # noqa: F401,F403
