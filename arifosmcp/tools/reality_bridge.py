"""
Compatibility shim — renamed to reality.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("reality_bridge.py is deprecated — use reality.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.reality import *  # noqa: F401,F403
