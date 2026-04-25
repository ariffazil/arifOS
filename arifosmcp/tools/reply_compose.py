"""
Compatibility shim — renamed to reply.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("reply_compose.py is deprecated — use reply.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.reply import *  # noqa: F401,F403
