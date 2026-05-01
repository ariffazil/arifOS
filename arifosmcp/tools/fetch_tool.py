"""
Compatibility shim — renamed to fetch.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("fetch_tool.py is deprecated — use fetch.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.fetch import *  # noqa: F401,F403
