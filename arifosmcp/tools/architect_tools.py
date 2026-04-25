"""
Compatibility shim — renamed to architect.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("architect_tools.py is deprecated — use architect.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.architect import *  # noqa: F401,F403
