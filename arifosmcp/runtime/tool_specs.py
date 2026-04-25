"""
Compatibility shim — tool_specs.py renamed to tool_spec.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("tool_specs.py is deprecated — use tool_spec.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.tool_spec import *  # noqa: F401,F403
