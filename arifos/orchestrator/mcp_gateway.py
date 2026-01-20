"""
AAA_MCP Transport Gateway (Component 2)
=====================================
Unified Wire for arifOS v49 MCP Architecture.
Acts as the transport abstraction layer between Clients (Comp 3) and Servers (Comp 1).

Authority: Δ Antigravity
Epoch: 2026-01-18
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable, Dict, Optional

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

# Component 4: Metabolizer (v49 canonical location)
from .metabolizer import AAAMetabolizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AAA_MCP_Gateway")

@dataclass
class TransportClient:
    """Represents a connected client via a specific transport"""
    client_id: str
    transport_type: str  # "stdio", "http", "sse", "grpc"
    read_stream: MemoryObjectReceiveStream
    write_stream: MemoryObjectSendStream
    metadata: Dict[str, Any]

class MCPGateway:
    """
    Unified entry point for multiple clients (Unified Wire).
    Routes requests to appropriate internal servers based on env vars or context.
    """
    def __init__(self):
        self.clients: Dict[str, TransportClient] = {}
        self.handlers: Dict[str, Callable] = {}
        self.metabolizer = AAAMetabolizer()  # Component 4
        self._setup_default_routes()

    def _setup_default_routes(self):
        """Register default JSON-RPC handlers"""
        self.register_handler("tools/list", self._handle_tools_list)
        self.register_handler("tools/call", self._handle_tools_call)

    def register_handler(self, method: str, handler: Callable):
        """Register a handler for a specific JSON-RPC method"""
        self.handlers[method] = handler
        logger.info(f"Registered handler for method: {method}")

    async def handle_connection(self, client_id: str, transport_type: str, reader: Any, writer: Any):
        """
        Main entry point for a transport connection.
        Normalizes transport streams into ANYIO memory streams if needed.
        """
        logger.info(f"New connection: {client_id} via {transport_type}")

        # In a real implementation, we would wrap reader/writer into MemoryObjectStreams
        # For now, we assume they present a similar async interface (read/write)

        try:
            async for message in reader:
                response = await self._process_message(message, client_id)
                if response:
                    await writer.send(response)
        except Exception as e:
            logger.error(f"Connection error for {client_id}: {e}")

    async def _process_message(self, raw_message: Any, client_id: str) -> Optional[Dict]:
        """Normalize and process a single message"""
        try:
            # 1. Normalize to JSON-RPC 2.0 Notional
            if isinstance(raw_message, bytes):
                data = json.loads(raw_message.decode())
            elif isinstance(raw_message, str):
                data = json.loads(raw_message)
            else:
                data = raw_message

            if not isinstance(data, dict) or "jsonrpc" not in data:
                 # Minimal validation
                 pass

            method = data.get("method")
            msg_id = data.get("id")
            params = data.get("params", {})

            # 2. Route to Handler
            if method in self.handlers:
                result = await self.handlers[method](params, client_id)
                return {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": msg_id
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": msg_id
                }

        except json.JSONDecodeError:
            return {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None}

    # --- Internal Routing Logic ---

    def _get_active_provider(self) -> str:
        """Determines which LLM provider context is active"""
        return os.environ.get("AAA_MCP_LLM_PROVIDER", "claude").lower()

    async def _handle_tools_list(self, params: Dict, client_id: str) -> Dict:
        """Route tools/list to the appropriate backend server"""
        provider = self._get_active_provider()
        logger.info(f"Routing tools/list for provider: {provider}")

        # ROUTING LOGIC (Component 1 Interfacing)
        # In full implementation, this calls Trinity Server instances
        if provider == "claude":
            # Access AGI/ASI/APEX tools suitable for Claude
            return {
                "tools": [
                    {"name": "vault/init", "description": "Initialize session (AGI)"},
                    {"name": "agi/think", "description": "Deep reasoning (AGI)"}
                ]
            }
        elif provider == "grok":
            # Maybe Grok needs different descriptions?
             return {
                "tools": [
                    {"name": "vault/init", "description": "Grok session init"}
                ]
            }
        else:
             return {"tools": []}

    async def _handle_tools_call(self, params: Dict, client_id: str) -> Dict:
        """
        Route tools/call to the appropriate backend server.

        Integrates Component 4 (Metabolizer):
        1. Route to server (VAULT/AGI/ASI/APEX)
        2. Get raw JSON response
        3. Pass through Metabolizer (Encoder → Metabolizer → Decoder)
        4. Return human-readable output to client
        """
        tool_name = params.get("name")
        if not tool_name:
             return {"content": [{"type": "text", "text": "Error: Tool name is required"}]}
        tool_args = params.get("arguments", {})
        provider = self._get_active_provider()

        logger.info(f"Routing tools/call {tool_name} for provider: {provider}")

        # ROUTING LOGIC
        # This is where we dispatch to vault_server.py, agi_server.py etc.
        # For now, mock a server response structure matching v49 servers

        # TODO: Replace with actual HTTP calls to servers
        # Example: response = await self._call_server(tool_name, tool_args)

        # Mock server response (Phase 9 structure)
        raw_server_response = {
            "verdict": "SEAL",
            "session_id": f"session_{client_id[:8]}",
            "stage": self._infer_stage_from_tool(tool_name),
            "latency_ms": 45.2,
            "floor_scores": {
                "F1_Amanah": {"pass": True, "score": 1.0},
                "F2_Truth": {"pass": True, "score": 0.99},
            },
            "output": {
                "message": f"Tool {tool_name} executed successfully",
            }
        }

        # COMPONENT 4: METABOLIZER INTEGRATION
        # Pass raw JSON through Encoder → Metabolizer → Decoder
        human_text = self.metabolizer.process(raw_server_response)

        # Return MCP-compatible response with human-readable text
        return {
            "content": [
                {
                    "type": "text",
                    "text": human_text
                }
            ]
        }

    def _infer_stage_from_tool(self, tool_name: str) -> str:
        """
        Infer arifOS aCLIP stage from tool name.
        Uses canonical Stage codes from arifos.protocol.
        """
        from arifos.protocol.codes import Stage

        # VAULT-999 (000, 999)
        if "init" in tool_name or "vault/init" == tool_name:
            return Stage.INIT_000.value
        elif "store" in tool_name or "vault/store" == tool_name or "999" in tool_name:
            return Stage.VAULT_999.value

        # AGI-Δ (111, 222, 333)
        elif "sense" in tool_name or "111" in tool_name:
            return Stage.SENSE_111.value
        elif "think" in tool_name or "222" in tool_name or "agi/think" in tool_name:
            return Stage.THINK_222.value
        elif "reason" in tool_name or "333" in tool_name:
            return Stage.ATLAS_333.value # 333_ATLAS

        # ASI-Ω (444, 555, 666)
        elif "align" in tool_name or "444" in tool_name:
            return Stage.ALIGN_444.value
        elif "empathy" in tool_name or "555" in tool_name or "asi/empathy" in tool_name:
            return Stage.EMPATHY_555.value
        elif "bridge" in tool_name or "666" in tool_name:
            return Stage.BRIDGE_666.value

        # APEX-Ψ (777, 888)
        elif "reflect" in tool_name or "777" in tool_name:
            return Stage.EUREKA_777.value # 777_EUREKA
        elif "seal" in tool_name or "888" in tool_name or "apex/seal" in tool_name:
            return Stage.JUDGE_888.value  # 888_JUDGE

        else:
            return "unknown"

# Singleton Instance
gateway = MCPGateway()
