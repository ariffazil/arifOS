"""
ASI (Heart/Ω) - The Empathizer

Unified namespace for arifOS Heart engine.

Modules:
    engine.py           - ASI engine core logic (ASIRoom)
    kernel.py           - ASI kernel proxy
    kernel_native.py    - Native ASI kernel (ASIKernelNative alias ASIKernel)
    empathy/            - Empathy scoring
        stage.py        - Stage 555: EMPATHY
    integration/        - ASI integrations
        async_wrapper.py - Async wrapper
"""

from .engine import ASIRoom
from .kernel_native import ASIKernel, ASIKernelNative, ASIActionCore
from .kernel import ASIActionCore as ASIKernelActionCore

__all__ = ["ASIRoom", "ASIKernel", "ASIKernelNative", "ASIActionCore", "ASIKernelActionCore"]  # ASIEngine renamed to ASIRoom for consistency
