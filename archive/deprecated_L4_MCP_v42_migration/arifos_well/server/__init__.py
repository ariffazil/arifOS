"""
arifos_well.server - FastAPI REST Server for @WELL

Provides universal HTTP interface for all AI coding agents.
"""

from .app import app, create_app

__all__ = ["app", "create_app"]
