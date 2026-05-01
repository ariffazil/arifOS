"""
Compatibility shim — renamed to gateway.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("gateway_connect.py is deprecated — use gateway.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.gateway import *  # noqa: F401,F403
