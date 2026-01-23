"""
arifOS wrappers package.

Contains high-level helpers that compose core governance components
into reusable patterns for applications and demos.

Current components:
    - governed_session.py: Session-aware wrapper using DependencyGuard
"""

from __future__ import annotations

from .governed_session import GovernedSessionWrapper

__all__ = ["GovernedSessionWrapper"]

