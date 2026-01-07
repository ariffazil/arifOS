"""
arifOS API Routes - Route modules for the FastAPI server.

All routes are thin wrappers over existing pipeline/memory/ledger logic.
v41.3: Added federation routes for L7 multi-endpoint routing.
"""

from . import health, pipeline, memory, ledger, metrics, federation

__all__ = ["health", "pipeline", "memory", "ledger", "metrics", "federation"]
