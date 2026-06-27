"""Pytest configuration and fixtures for arifOS tests."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
import warnings
from pathlib import Path

import anyio
import httpx
import pytest

# ─────────────────────────────────────────────────────────────────────────────
# PROTOCOL VERSION SENTINEL — F13 ratified 2026-06-27 by FORGE hardening
#
# Catches the silent drift class of failures:
#   - Test helpers hardcode protocolVersion="2024-11-25"
#   - Kernel :8088 has upgraded to "2025-11-25"
#   - The mismatch caused 20/47 agi_kernel_readiness tests to fail with
#     "MCP protocol version mismatch" or "missing mcp-session-id header"
#
# Without this sentinel: tests pass on the wrong protocol and silently
# certify a kernel the test suite was never designed for.
# With this sentinel: pytest aborts at collection time if kernel version
# drifts away from EXPECTED_PROTOCOL_VERSION. Loud, single source of truth.
#
# Set ARIFOS_SKIP_PROTOCOL_SENTINEL=1 to bypass (CI rotation / offline).
# ─────────────────────────────────────────────────────────────────────────────

EXPECTED_PROTOCOL_VERSION = "2025-11-25"
KERNEL_BASE_URL = os.environ.get("ARIFOS_KERNEL_URL", "http://127.0.0.1:8088")


def _probe_kernel_protocol() -> tuple[str | None, str | None]:
    """Probe arifOS MCP /mcp initialize. Returns (protocol_version, error)."""
    payload = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": EXPECTED_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "arifos-test-sentinel", "version": "1.0"},
        },
    }
    req = urllib.request.Request(
        f"{KERNEL_BASE_URL}/mcp",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode())
            return body.get("result", {}).get("protocolVersion"), None
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError) as e:
        return None, f"connection_error: {type(e).__name__}: {e}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _check_protocol_sentinel() -> None:
    """Fail loudly if kernel protocol drifts from expected version."""
    if os.environ.get("ARIFOS_SKIP_PROTOCOL_SENTINEL") == "1":
        return  # explicit bypass

    if os.environ.get("ARIFOS_SKIP_PROTOCOL_SENTINEL") == "soft":
        # Soft check — warn but don't fail (useful when kernel is intentionally
        # on an older protocol during a controlled upgrade).
        version, err = _probe_kernel_protocol()
        if err:
            warnings.warn(f"[protocol-sentinel] could not probe kernel: {err}")
        elif version != EXPECTED_PROTOCOL_VERSION:
            warnings.warn(
                f"[protocol-sentinel] kernel protocol {version!r} != "
                f"expected {EXPECTED_PROTOCOL_VERSION!r} — tests may fail. "
                f"Set ARIFOS_SKIP_PROTOCOL_SENTINEL=1 to suppress."
            )
        return

    # Hard check (default): fail at collection if drift detected.
    version, err = _probe_kernel_protocol()
    if err:
        pytest.exit(
            f"[protocol-sentinel] KERNEL UNREACHABLE at {KERNEL_BASE_URL}/mcp: {err}\n"
            f"  Cannot verify protocol version. Tests cannot proceed.\n"
            f"  Fix: start arifOS MCP at :8088, OR set ARIFOS_SKIP_PROTOCOL_SENTINEL=1 "
            f"(only for controlled offline runs).",
            returncode=2,
        )
    if version != EXPECTED_PROTOCOL_VERSION:
        pytest.exit(
            f"[protocol-sentinel] PROTOCOL DRIFT DETECTED\n"
            f"  Kernel reports:  {version!r}\n"
            f"  Test suite expects: {EXPECTED_PROTOCOL_VERSION!r}\n"
            f"\n"
            f"  This usually means the kernel was upgraded but tests/helpers were not.\n"
            f"  Update EXPECTED_PROTOCOL_VERSION in tests/conftest.py AND any\n"
            f"  hardcoded 'protocolVersion' strings in test files.\n"
            f"\n"
            f"  Bypass (NOT recommended): export ARIFOS_SKIP_PROTOCOL_SENTINEL=1",
            returncode=3,
        )


# Run sentinel once at collection time, BEFORE any tests.
_check_protocol_sentinel()


# Add project root to sys.path for imports when running from repo checkout.
root_dir = Path(__file__).parents[1].resolve()

# Force root and root/core to the very top of sys.path
# This ensures 'import core' hits /root/arifOS/core/ and NOT arifosmcp/core/
sys.path = [str(root_dir), str(root_dir / "core")] + [
    p for p in sys.path if p not in (str(root_dir), str(root_dir / "core"))
]


# Pre-import core package to lock it in sys.modules and prevent collision with arifosmcp/core


# Load .env for tests if available
env_path = root_dir / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except ImportError:
        # Manual fallback if python-dotenv missing
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    os.environ[key.strip().replace("export ", "")] = (
                        val.strip().strip('"').strip("'")
                    )


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
# Include the legacy arifos.supabase.co issuer for JWT acceptance tests
# (overrides .env which uses the utbmmjmbolmuahwixjqc project instance)
_original_jti = os.environ.get("JWT_TRUSTED_ISSUERS", "")
os.environ["JWT_TRUSTED_ISSUERS"] = "https://arifos.supabase.co,arifos-internal"


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


@pytest.fixture(scope="session", autouse=True)
def mock_well_state_for_tests(tmp_path_factory):
    """Provide a healthy WELL mirror state so biological readiness gate passes.

    Uses WELL_STATE_PATH env var if set (production/VPS), otherwise creates a
    temporary file so CI runners (which lack /root/WELL) can run tests cleanly.
    """
    import json

    healthy = {
        "timestamp": "2026-04-30T00:00:00+00:00",
        "operator_id": "arif",
        "metrics": {},
        "well_score": 100,
        "floors_violated": [],
        "backend_status": "STABLE",
        "last_successful_read": "2026-04-30T00:00:00+00:00",
        "last_successful_write": "2026-04-30T00:00:00+00:00",
        "state_file_access": "PASS",
        "vault_access": "OK",
        "test_contamination": "NO",
        "contamination_quarantined": False,
        "confidence": "HIGH",
        "freshness": "FRESH",
        "environment": "TEST",
        "telemetry_confidence": "HIGH",
        "reason": "Mocked healthy state for test session",
        "safe_mode": "off",
        "arif_decision_required": False,
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }

    # Resolve the well state path: env var > VPS default > tmpdir for CI
    env_path = os.environ.get("WELL_STATE_PATH")
    vps_path = Path("/root/WELL/state.json")

    if env_path:
        well_path = Path(env_path)
    elif vps_path.parent.exists():
        well_path = vps_path
    else:
        # CI runner: create temp file and point WELL_STATE_PATH at it
        tmp_dir = tmp_path_factory.mktemp("well_state")
        well_path = tmp_dir / "state.json"
        os.environ["WELL_STATE_PATH"] = str(well_path)

    original: str | None = None
    if well_path.exists():
        original = well_path.read_text(encoding="utf-8")

    well_path.parent.mkdir(parents=True, exist_ok=True)
    well_path.write_text(json.dumps(healthy), encoding="utf-8")

    yield

    if original is not None:
        well_path.write_text(original, encoding="utf-8")
    else:
        well_path.unlink(missing_ok=True)


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

    # ── Skip tests with missing optional deps at collection time ─────
    # prefab_ui is a UI-builder dep used by arifosmcp.apps.*. The root
    # pyproject doesn't declare it; only the inner arifosmcp/ venv has it
    # (and that's a 3.12 venv with a broken pydantic_core wheel). Until
    # the root deps are reconciled, the apps-tree tests cannot import.
    if collection_path.name == "test_wealth_invariant_surface.py":
        try:
            import prefab_ui  # noqa: F401
        except ImportError:
            return True

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
