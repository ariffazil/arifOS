"""
arifOS API Routes - Route modules for the FastAPI server.

All routes are thin wrappers over existing pipeline/memory/ledger logic.
"""

from . import health, pipeline, memory, ledger, metrics

__all__ = ["health", "pipeline", "memory", "ledger", "metrics"]
