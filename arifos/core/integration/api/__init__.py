"""
arifOS API Package - FastAPI server for v50.5 governance pipeline.

This module provides a REST API wrapping the governed pipeline, L7 memory,
and ledger access. All endpoints are stateless, fail-open, and read-only
or append-only.

Version: v51.2.0
"""

from .app import create_app, app

__all__ = ["create_app", "app"]
