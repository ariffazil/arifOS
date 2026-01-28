"""
AGI (Mind/Δ) - The Thinker

Unified namespace for arifOS Mind engine.

Modules:
    engine.py    - AGI engine core logic
    kernel.py    - AGI neural kernel
    eval.py      - AGI floor validation
    server.py    - AGI MCP server
    paradox/     - AGI paradox detection
"""

from .engine import AGIEngine
from .kernel import AGINeuralCore
from .eval import validate_agi_output
from .server import AGIServer

__all__ = ["AGIEngine", "AGINeuralCore", "validate_agi_output", "AGIServer"]
