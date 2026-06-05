"""Pytest fixtures for the evals harness.

All evals share: Qdrant client, NATS connection, and a mock MCP registry.
"""

from __future__ import annotations

import pytest
from qdrant_client import QdrantClient


@pytest.fixture(scope="session")
def qdrant_client() -> QdrantClient:
    return QdrantClient(url="http://localhost:6333")


@pytest.fixture(scope="session")
def capability_store(qdrant_client):
    from capability_index.store import CapabilityStore

    return CapabilityStore()
