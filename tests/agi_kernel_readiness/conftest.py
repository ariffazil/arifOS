"""
conftest.py for AGI Kernel Readiness Gate tests.

Makes the _helpers module importable from any test file in this
directory, regardless of how the tests are invoked (script, module,
or pytest).
"""

import sys
import os

# Add this directory to sys.path so tests can do `from _helpers import ...`
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
