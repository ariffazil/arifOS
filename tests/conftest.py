"""Pytest configuration and fixtures for arifOS tests."""

from __future__ import annotations

import asyncio
import os
import sys
import warnings
from pathlib import Path

import anyio
import httpx
import pytest


# Add project root to sys.path for imports when running from repo checkout.
sys.path.insert(0, str(Path(__file__).parents[1]))


# Silence langsmith/pydantic v1 warning on Python 3.14 (benign in this env)
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.",
    category=UserWarning,
    module="langsmith.schemas",
)


# Ensure legacy spec bypass is active during import/collection
os.environ.setdefault("ARIFOS_ALLOW_LEGACY_SPEC", "1")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")
# Default to debug output in tests to preserve rich contracts for assertions.
os.environ.setdefault("AAA_MCP_OUTPUT_MODE", "debug")


class SyncASGIClient:
    """Minimal sync wrapper over httpx.ASGITransport for FastMCP test routes."""

    def __init__(self, app, base_url: str = "http://testserver") -> None:
        self.app = app
        self.base_url = base_url

    def request(self, method: str, url: str, **kwargs):
        async def runner():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url=self.base_url,
                follow_redirects=True,
            ) as client:
                return await client.request(method, url, **kwargs)

        return anyio.run(runner)

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def disable_physics_globally():
    """Disable physics globally for all tests (performance optimization)."""

    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    yield
    if "ARIFOS_PHYSICS_DISABLED" in os.environ:
        del os.environ["ARIFOS_PHYSICS_DISABLED"]


@pytest.fixture(scope="session", autouse=True)
def allow_legacy_spec_for_tests():
    """Allow legacy spec loading for tests (bypasses cryptographic manifest requirement)."""

    os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"
    yield
    if "ARIFOS_ALLOW_LEGACY_SPEC" in os.environ:
        del os.environ["ARIFOS_ALLOW_LEGACY_SPEC"]


@pytest.fixture(scope="module")
def enable_physics_for_apex_theory():
    """Enable physics for APEX THEORY system flow tests."""

    original_state = os.environ.get("ARIFOS_PHYSICS_DISABLED")
    if "ARIFOS_PHYSICS_DISABLED" in os.environ:
        del os.environ["ARIFOS_PHYSICS_DISABLED"]

    yield

    if original_state is not None:
        os.environ["ARIFOS_PHYSICS_DISABLED"] = original_state
    else:
        os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"


def pytest_ignore_collect(collection_path, config):
    """Avoid collecting archived/legacy tests.

    This repo contains multiple historical MCP surfaces. For the arifOS AAA MCP
    13-tool surface, the active lanes are:
    - tests/canonical: current public contract
    - tests/compat: backward-compat and entrypoint behavior
    - tests/archive and tests/legacy: historical surfaces excluded by default

    Active suites are selected by directory, not by scanning file contents for
    old import strings.
    """

    path_str = str(collection_path)
    if "tests/archive" in path_str or "tests\\archive" in path_str:
        return True
    if "tests/legacy" in path_str or "tests\\legacy" in path_str:
        return True

    if collection_path.suffix != ".py":
        return False

    return False


def is_postgres_running() -> bool:
    """Check if PostgreSQL is running and accessible."""

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return False

    try:
        import asyncpg as asyncpg_mod
    except ImportError:
        return False

    async def check_pg() -> bool:
        try:
            conn = await asyncio.wait_for(asyncpg_mod.connect(dsn=db_url), timeout=2.0)
            await conn.close()
            return True
        except (OSError, asyncio.TimeoutError, asyncpg_mod.PostgresError):
            return False

    try:
        return asyncio.run(check_pg())
    except Exception:
        return False


def is_redis_running() -> bool:
    """Check if Redis is running and accessible."""

    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        return False

    try:
        import redis as redis_mod
        from redis import exceptions as redis_exceptions
    except ImportError:
        return False

    try:
        r = redis_mod.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        return bool(r.ping())
    except (redis_exceptions.ConnectionError, redis_exceptions.TimeoutError):
        return False


@pytest.fixture
def require_postgres():
    """Skip only when a test explicitly needs a live PostgreSQL service."""

    if not is_postgres_running():
        pytest.skip("PostgreSQL service not running or configured via DATABASE_URL")


@pytest.fixture
def require_redis():
    """Skip only when a test explicitly needs a live Redis service."""

    if not is_redis_running():
        pytest.skip("Redis service not running or configured via REDIS_URL")


postgres_required = pytest.mark.usefixtures("require_postgres")
redis_required = pytest.mark.usefixtures("require_redis")


@pytest.fixture
async def aaa_client():
    """In-memory MCP client for the canonical AAA server."""

    from fastmcp import Client

    from arifosmcp.runtime.server import create_aaa_mcp_server

    async with Client(create_aaa_mcp_server()) as client:
        yield client
