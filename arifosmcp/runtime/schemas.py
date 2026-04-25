"""
Compatibility shim — schemas.py renamed to schema.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("schemas.py is deprecated — use schema.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.schema import *  # noqa: F401,F403
