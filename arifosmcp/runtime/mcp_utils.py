"""
Compatibility shim — mcp_utils.py renamed to mcp_util.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("mcp_utils.py is deprecated — use mcp_util.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.mcp_util import *  # noqa: F401,F403
