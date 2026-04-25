"""
Compatibility shim — renamed to forge.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("forge_execute.py is deprecated — use forge.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.forge import *  # noqa: F401,F403
