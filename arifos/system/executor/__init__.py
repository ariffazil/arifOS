"""
arifos_core/system/executor/__init__.py

The Sovereign Execution Engine (SEE).
Forges the "Hand" (Sandbox) with the "Conscience" (Interceptor).
"""

from .interceptor import ConstitutionalInterceptor
from .sandbox import ExecutionSandbox


class SovereignExecutor:
    """
    Facade for the Sovereign Execution Engine.
    """
    def __init__(self):
        self.sandbox = ExecutionSandbox()
        self.interceptor = ConstitutionalInterceptor(self.sandbox)

    def execute(self, query: str) -> dict:
        """
        Execute a query constitutionally.
        Delegates to Interceptor -> Sandbox.
        """
        return self.interceptor.process(query)
