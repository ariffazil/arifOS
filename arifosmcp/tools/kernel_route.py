"""
Compatibility shim — renamed to kernel.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("kernel_route.py is deprecated — use kernel.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.kernel import *  # noqa: F401,F403
