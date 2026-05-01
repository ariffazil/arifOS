"""
Compatibility shim — renamed to judge.py
This file will be removed after one sprint.
"""
import warnings
warnings.warn("judge_deliberate.py is deprecated — use judge.py instead", DeprecationWarning, stacklevel=2)
from arifosmcp.tools.judge import *  # noqa: F401,F403
