"""
Compatibility shim — models.py renamed to model.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("models.py is deprecated — use model.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.runtime.model import *  # noqa: F401,F403
