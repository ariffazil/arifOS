#!/usr/bin/env python3
"""
arifOS Identity Broker — Stage 1
================================
MCP sidecar proxy that injects Arif's identity into OpenCode MCP calls.

DITEMPA BUKAN DIBERI — Forged, Not Given.

Usage:
    python broker.py [--port PORT] [--config PATH]

Environment:
    ARIF_IDENTITY_FILE  — path to ~/.arif/identity.json (default)
    ARIF_KERNEL_URL     — arifOS MCP endpoint (default: http://localhost:8088/mcp)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import hmac
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import Any

import httpx

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("arif-identity-broker")

# ─── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_KERNEL_URL = "http://localhost:8088/mcp"
DEFAULT_PORT = 8088
ARIF_DIR = Path.home() / ".arif"
ARIF_IDENTITY_FILE = ARIF_DIR / "identity.json"
BROKER_VERSION = "1.0.0"

# ─── Identity Envelope ────────────────────────────────────────────────────────


class IdentityEnvelope:
    """Builds and signs the identity envelope injected into every MCP call."""

    def __init__(self, config: dict[str, Any], broker_secret: str):
        self.config = config
        self.broker_secret = broker_secret
        self.session_id = f"ope-{uuid.uuid4().hex[:16]}"
        self.session_start = datetime.now(timezone.utc).isoformat()

    def inject(self, params: dict[str, Any]) -> dict[str, Any]:
        """Inject identity into MCP tool call params. Returns enriched params."""
        envelope = {
            "actor_id": self.config["actor_id"],
            "identity_state": self.config.get("identity_state", "OPERATOR_CLAIMED"),
            "identity_source": "local_broker",
            "broker_name": self.config.get("broker_name", "arif-identity-broker"),
            "broker_version": BROKER_VERSION,
            "session_id": self.session_id,
            "session_start": self.session_start,
        }
        # Sign the envelope so arifOS can verify broker authenticity
        envelope["envelope_signature"] = self._sign(envelope)
        # Inject into params under arif_identity key
        enriched = dict(params)
        if "arif_identity" in enriched:
            # Don't double-inject
            pass
        else:
            enriched["arif_identity"] = envelope
        return enriched

    def inject_into_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Inject identity into a full JSON-RPC request."""
        enriched = dict(request)
        if "params" not in enriched:
            enriched["params"] = {}
        enriched["params"] = self.inject(enriched["params"])
        return enriched

    def _sign(self, payload: dict[str, Any]) -> str:
        """HMAC-SHA256 sign the payload using broker_secret."""
        # Canonicalize: sorted JSON bytes
        canonical = json.dumps(payload, sort_keys=True, default=str).encode()
        signature = hmac.new(
            self.broker_secret.encode(),
            canonical,
            hashlib.sha256,
        ).hexdigest()
        return signature


# ─── Identity Loader ──────────────────────────────────────────────────────────


class IdentityLoader:
    """Loads and validates ~/.arif/identity.json."""

    REQUIRED_FIELDS = ["version", "actor_id", "broker_secret"]
    TOOL_DENY_LIST = [
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_forge_execute",
    ]

    @classmethod
    def load(cls, path: Path | None = None) -> dict[str, Any]:
        path = path or ARIF_IDENTITY_FILE
        if not path.exists():
            raise FileNotFoundError(
                f"Identity file not found: {path}\n"
                f"Run: python -m arif_identity_broker.setup\n"
                f"Or: curl -sL https://... | python"
            )
        with open(path, "r") as f:
            config = json.load(f)

        cls._validate(config, path)
        cls._check_deny_list(config)
        return config

    @classmethod
    def _validate(cls, config: dict[str, Any], path: Path) -> None:
        for field in cls.REQUIRED_FIELDS:
            if field not in config:
                raise ValueError(
                    f"Missing required field '{field}' in {path}\n"
                    f"Required fields: {cls.REQUIRED_FIELDS}"
                )
        if config.get("version") != 1:
            raise ValueError(
                f"Unsupported identity file version: {config.get('version')}\n"
                f"Only version 1 is supported."
            )

    @classmethod
    def _check_deny_list(cls, config: dict[str, Any]) -> None:
        """Warn if broker config allows dangerous tools."""
        allowed = config.get("allowed_tools", [])
        denied = cls.TOOL_DENY_LIST
        warned = [t for t in denied if t in allowed]
        if warned:
            logger.warning(
                f"BROKER ALLOWS CONSTITUTIONAL TOOLS (should be IDENTITY_VERIFIED only): {warned}"
            )

    @staticmethod
    def generate(output_path: Path | None = None) -> dict[str, Any]:
        """Generate a new identity file with a secure random broker_secret."""
        import secrets

        identity = {
            "version": 1,
            "actor_id": "arif",
            "broker_name": "arif-identity-broker",
            "broker_secret": secrets.token_hex(32),  # 64-char hex = 256 bits
            "identity_state": "OPERATOR_CLAIMED",
            "allowed_tools": [
                "arif_session_init",
                "arif_kernel_route",
                "arif_memory_recall",
                "arif_memory_store",
                "arif_sense_observe",
                "arif_mind_reason",
                "arif_gateway_connect",
                "arif_ops_measure",
                "arif_heart_critique",
                "arif_stack_health_probe",
            ],
            "deny_tools": [
                "arif_judge_deliberate",
                "arif_vault_seal",
                "arif_forge_execute",
            ],
            "session_ttl_seconds": 28800,
            "kernel_endpoint": os.environ.get("ARIF_KERNEL_URL", DEFAULT_KERNEL_URL),
        }
        output_path = output_path or ARIF_IDENTITY_FILE
        ARIF_DIR.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(identity, f, indent=2)
        os.chmod(output_path, 0o600)
        logger.info(f"Identity file written: {output_path} (chmod 600)")
        return identity


# ─── MCP Message Types ────────────────────────────────────────────────────────


class MCPMessage:
    """Minimal MCP JSON-RPC 2.0 message parser."""

    @staticmethod
    def is_initialize(request: dict[str, Any]) -> bool:
        return request.get("method") == "initialize"

    @staticmethod
    def is_notification(request: dict[str, Any]) -> bool:
        return request.get("id") is None

    @staticmethod
    def is_session_seal(request: dict[str, Any]) -> bool:
        m = request.get("method", "")
        params = request.get("params", {})
        return m == "arif_vault_seal" and params.get("mode") == "session_seal"

    @staticmethod
    def is_full_constitutional_seal(request: dict[str, Any]) -> bool:
        m = request.get("method", "")
        params = request.get("params", {})
        return m == "arif_vault_seal" and params.get("mode") == "seal"

    @staticmethod
    def is_tool_call(request: dict[str, Any]) -> bool:
        return not MCPMessage.is_initialize(request) and not MCPMessage.is_notification(request)


# ─── arifOS MCP Client ────────────────────────────────────────────────────────


class ArifOSClient:
    """Async HTTP client that forwards MCP calls to arifOS kernel."""

    def __init__(self, kernel_url: str, timeout: float = 60.0):
        self.kernel_url = kernel_url.rstrip("/")
        self.timeout = timeout
        self._protocol_version: str | None = None
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))

    async def initialize(self, broker_version: str) -> dict[str, Any]:
        """
        Send MCP initialize to arifOS.
        arifOS responds with its protocol version.
        We cache it for subsequent tool calls.
        """
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "arif-identity-broker",
                    "version": broker_version,
                },
                "actor_id": "arif",
                "identity_state": "OPERATOR_CLAIMED",
            },
        }
        response = await self._post(request)
        if "result" in response:
            self._protocol_version = response["result"].get("protocolVersion")
            logger.info(f"arifOS protocol version: {self._protocol_version}")
        return response

    async def call_tool(
        self,
        method: str,
        params: dict[str, Any],
        request_id: int | str | None = None,
    ) -> dict[str, Any]:
        """Forward a tool call to arifOS with enriched identity."""
        if request_id is None:
            request_id = str(uuid.uuid4().hex[:8])
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        return await self._post(request)

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST a single JSON-RPC request to arifOS."""
        logger.debug(f"→ arifOS: {payload.get('method', 'notify')} (id={payload.get('id')})")
        try:
            response = await self._client.post(
                self.kernel_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(
                f"← arifOS: id={payload.get('id')} result/error={bool('result' in result)}"
            )
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"arifOS HTTP error: {e.response.status_code} — {e.response.text[:200]}")
            return {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {"code": -32000, "message": f"HTTP {e.response.status_code}"},
            }
        except Exception as e:
            logger.error(f"arifOS call failed: {e}")
            return {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {"code": -32603, "message": str(e)},
            }

    async def close(self) -> None:
        await self._client.aclose()


# ─── Broker ───────────────────────────────────────────────────────────────────


class IdentityBroker:
    """
    MCP sidecar broker that:
    1. Accepts MCP calls from OpenCode (stdio or HTTP)
    2. Injects Arif's identity into every call
    3. Forwards enriched calls to arifOS
    4. Returns responses to OpenCode

    Identity is read from ~/.arif/identity.json (chmod 600).
    No secrets are ever passed through prompts or chat.
    """

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or ARIF_IDENTITY_FILE
        self.config = IdentityLoader.load(self.config_path)
        self.broker_secret = self.config["broker_secret"]
        self.kernel_url = self.config.get("kernel_endpoint", DEFAULT_KERNEL_URL)
        self.session_ttl = self.config.get("session_ttl_seconds", 28800)

        self._client: ArifOSClient | None = None
        self._initialized = False
        self._active_sessions: dict[str, dict[str, Any]] = {}

    @cached_property
    def envelope(self) -> IdentityEnvelope:
        return IdentityEnvelope(self.config, self.broker_secret)

    async def start(self) -> None:
        """Initialize connection to arifOS. Call once at broker start."""
        self._client = ArifOSClient(self.kernel_url)
        init_result = await self._client.initialize(BROKER_VERSION)
        if "error" in init_result:
            logger.error(f"arifOS init failed: {init_result['error']}")
            raise RuntimeError(f"Failed to initialize arifOS: {init_result['error']}")
        self._initialized = True
        logger.info(f"Broker started — arifOS: {self.kernel_url}")

    async def stop(self) -> None:
        """Close connection to arifOS."""
        if self._client:
            await self._client.close()
        logger.info("Broker stopped")

    # ── Public MCP interface ──────────────────────────────────────────────────

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """
        Main entry point. Receives a JSON-RPC request from OpenCode,
        enriches it with identity, forwards to arifOS, returns the response.
        """
        if not self._initialized:
            return self._error(request, -32005, "broker_not_initialized")

        method = request.get("method", "")

        # ── Initialize: broker handles it (caches protocol version) ──────────
        if MCPMessage.is_initialize(request):
            return await self._handle_initialize(request)

        # ── Notifications: forward without waiting for response ───────────────
        if MCPMessage.is_notification(request):
            enriched = self.envelope.inject_into_request(request)
            # Fire and forget for notifications
            assert self._client is not None, "Broker not initialized"
            asyncio.create_task(self._client.call_tool(method, enriched.get("params", {})))  # type: ignore[union-attr]
            return None  # Notification: no response

        # ── Tool calls ──────────────────────────────────────────────────────
        if MCPMessage.is_tool_call(request):
            return await self._handle_tool_call(request)

        return self._error(request, -32601, f"Unknown method: {method}")

    async def handle_batch(self, requests: list[dict[str, Any]]) -> list[dict[str, Any] | None]:
        """Handle a batch of JSON-RPC requests."""
        results = []
        for req in requests:
            result = await self.handle_request(req)
            results.append(result)
        return results

    # ── Request handlers ─────────────────────────────────────────────────────

    async def _handle_initialize(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        Handle MCP initialize from OpenCode.
        We respond with our own capabilities.
        The real arifOS initialize was already called in start().
        """
        logger.info("OpenCode initializing connection to broker")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "arif-identity-broker",
                    "version": BROKER_VERSION,
                },
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
                "instructions": "arifOS Identity Broker — OPERATOR_CLAIMED identity injected into all calls",
            },
        }

    async def _handle_tool_call(self, request: dict[str, Any]) -> dict[str, Any]:
        """Enrich and forward a tool call to arifOS."""
        method = request.get("method", "")
        raw_params = request.get("params", {})
        request_id = request.get("id")

        # ── Policy: block full constitutional seals from OPERATOR_CLAIMED ────
        if MCPMessage.is_full_constitutional_seal(request):
            logger.warning(
                f"Blocked constitutional seal attempt (OPERATOR_CLAIMED, needs IDENTITY_VERIFIED): "
                f"method={method}"
            )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32003,
                    "message": "HOLD — Full constitutional seal requires IDENTITY_VERIFIED. "
                    "888_HOLD escalation needed.",
                    "data": {
                        "reason": "F13 SOVEREIGN boundary — OPERATOR_CLAIMED cannot emit vault seal",
                        "required": "IDENTITY_VERIFIED",
                        "current": "OPERATOR_CLAIMED",
                        "tool": "arif_vault_seal",
                        "verdict": "HOLD",
                    },
                },
            }

        # ── Enrich params with identity envelope ──────────────────────────────
        enriched_params = self.envelope.inject(raw_params)

        # ── Forward to arifOS ────────────────────────────────────────────────
        try:
            assert self._client is not None, "Broker not initialized"
            response = await self._client.call_tool(  # type: ignore[union-attr]
                method,
                enriched_params,
                request_id=request_id,
            )
            return response
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return self._error(request, -32603, str(e))

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _error(
        request: dict[str, Any],
        code: int,
        message: str,
    ) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": code, "message": message},
        }


# ─── HTTP Server (for OpenCode HTTP MCP transport) ─────────────────────────────


class HTTPServer:
    """Minimal HTTP server that speaks MCP JSON-RPC 2.0 over HTTP POST."""

    def __init__(self, broker: IdentityBroker, port: int = DEFAULT_PORT):
        self.broker = broker
        self.port = port

    async def start(self) -> Any:
        from aiohttp import web

        async def handle_mcp(request: web.Request) -> web.Response:
            request.headers.get("Content-Type", "")

            if request.method != "POST":
                return web.Response(status=405, text="Method Not Allowed")

            try:
                body = await request.json()
            except Exception:
                return web.Response(status=400, text="Invalid JSON")

            # Batch or single?
            if isinstance(body, list):
                results = await self.broker.handle_batch(body)
                # Filter None (notifications) from batch response
                filtered = [r for r in results if r is not None]
                return web.json_response(filtered if filtered else None)
            else:
                result = await self.broker.handle_request(body)
                if result is None:
                    return web.Response(status=202, text="Accepted")
                return web.json_response(result)

        async def handle_health(request: web.Request) -> web.Response:
            return web.json_response(
                {
                    "status": "healthy",
                    "broker": "arif-identity-broker",
                    "version": BROKER_VERSION,
                    "actor_id": self.broker.config["actor_id"],
                    "identity_state": self.broker.config.get("identity_state", "OPERATOR_CLAIMED"),
                    "kernel_url": self.broker.kernel_url,
                }
            )

        app = web.Application()
        app.router.add_post("/mcp", handle_mcp)
        app.router.add_get("/health", handle_health)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
        logger.info(f"Broker HTTP server listening on http://localhost:{self.port}/mcp")
        return runner


# ─── Stdio Server (for OpenCode stdio MCP transport) ───────────────────────────


class StdioServer:
    """
    Stdio MCP server.
    Reads JSON-RPC requests from stdin, writes responses to stdout.
    OpenCode MCP stdio transport uses this.
    """

    def __init__(self, broker: IdentityBroker):
        self.broker = broker

    async def run(self) -> None:
        """
        Read lines from stdin (one JSON-RPC request per line).
        Write JSON-RPC responses to stdout.
        """
        import asyncio

        loop = asyncio.get_event_loop()

        def read_line() -> str:
            return sys.stdin.readline()

        async def pump() -> None:
            while True:
                try:
                    line = await loop.run_in_executor(None, read_line)
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        request = json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON from stdin: {e}")
                        continue

                    # Handle batch
                    if isinstance(request, list):
                        results = await self.broker.handle_batch(request)
                        for r in results:
                            if r is not None:
                                print(json.dumps(r), flush=True)
                    else:
                        result = await self.broker.handle_request(request)
                        if result is not None:
                            print(json.dumps(result), flush=True)

                except Exception as e:
                    logger.error(f"Stdio pump error: {e}")
                    break

        await pump()


# ─── CLI ──────────────────────────────────────────────────────────────────────


async def amain() -> None:
    parser = argparse.ArgumentParser(description="arifOS Identity Broker — Stage 1")
    parser.add_argument(
        "--config",
        type=Path,
        default=ARIF_IDENTITY_FILE,
        help=f"Path to identity JSON file (default: {ARIF_IDENTITY_FILE})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"HTTP server port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Use stdio transport instead of HTTP",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Generate a new ~/.arif/identity.json and exit",
    )
    parser.add_argument(
        "--generate",
        type=Path,
        help="Generate identity file to specified path and exit",
    )
    args = parser.parse_args()

    # ── Setup mode ────────────────────────────────────────────────────────────
    if args.setup or args.generate:
        path = args.generate or ARIF_IDENTITY_FILE
        identity = IdentityLoader.generate(path)
        print("\n✅ Identity file generated:")
        print(f"   Path:     {path}")
        print(f"   actor_id: {identity['actor_id']}")
        print(f"   state:    {identity['identity_state']}")
        print("\n⚠️  chmod 600 already applied. Keep this file SECURE.")
        print("   Never commit it. Never share it.")
        return

    # ── Normal broker mode ────────────────────────────────────────────────────
    broker = IdentityBroker(config_path=args.config)
    await broker.start()

    if args.stdio:
        logger.info("Starting stdio transport server")
        server = StdioServer(broker)
        await server.run()
    else:
        logger.info(f"Starting HTTP transport server on port {args.port}")
        httpserver = HTTPServer(broker, port=args.port)
        await httpserver.start()
        # Keep alive
        while True:
            await asyncio.sleep(3600)


def main() -> None:
    import asyncio

    asyncio.run(amain())


if __name__ == "__main__":
    main()
