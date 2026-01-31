"""
arifOS MCP Server - AAA Framework Implementation
Model Context Protocol Server for Constitutional AI Governance

Protocol: MCP 2025-06-18
Architecture: AGI (Mind) + ASI (Heart) + APEX (Soul)

Tools:
- _init_   : Session initialization and security gate
- _agi_    : Mind engine (reasoning, logic, knowledge)
- _asi_    : Heart engine (safety, bias, empathy)
- _apex_   : Soul engine (judgment, verdicts, synthesis)
- _vault_  : Immutable ledger (sealing, audit)
- _trinity_: Full pipeline (AGI→ASI→APEX→VAULT)
- _reality_: External fact-checking

DITEMPA BUKAN DIBERI
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arifos-mcp")


@dataclass
class ToolDefinition:
    """MCP Tool Definition Schema"""
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema
        }
        if self.output_schema:
            result["outputSchema"] = self.output_schema
        if self.annotations:
            result["annotations"] = self.annotations
        return result


@dataclass
class ToolResult:
    """MCP Tool Result"""
    content: List[Dict[str, Any]]
    is_error: bool = False
    structured_content: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "content": self.content,
            "isError": self.is_error
        }
        if self.structured_content:
            result["structuredContent"] = self.structured_content
        return result


TOOL_SCHEMAS = {
    "_init_": ToolDefinition(
        name="_init_",
        title="Session Initialization Gate",
        description="Initialize session with identity verification, injection detection, budget allocation. MUST be called first.",
        input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["init", "gate", "reset", "validate", "authorize"], "default": "init"},
                "query": {"type": "string", "maxLength": 10000},
                "session_id": {"type": "string", "minLength": 8},
                "user_token": {"type": "string"}
            },
            "required": ["action"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "authority_level": {"type": "string", "enum": ["guest", "user", "admin", "system"]},
                "budget_allocated": {"type": "integer"},
                "injection_check_passed": {"type": "boolean"},
                "access_level": {"type": "string"},
                "session_ttl": {"type": "integer"},
                "constitutional_version": {"type": "string"}
            },
            "required": ["session_id", "authority_level", "injection_check_passed"]
        },
        annotations={"title": "Session Gate", "readOnlyHint": False, "destructiveHint": False, "openWorldHint": False}
    ),
    
    "_agi_": ToolDefinition(
        name="_agi_",
        title="Mind Engine (Delta)",
        description="Deep reasoning, pattern recognition, knowledge retrieval. Implements 111 SENSE → 222 THINK → 333 FORGE.",
        input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["sense", "think", "reflect", "reason", "atlas", "forge", "physics", "full"], "default": "full"},
                "query": {"type": "string", "maxLength": 10000},
                "context": {"type": "object"},
                "session_id": {"type": "string"},
                "lane": {"type": "string", "enum": ["CRISIS", "HARD", "SOFT", "PHATIC"], "default": "SOFT"}
            },
            "required": ["action", "query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "entropy_delta": {"type": "number"},
                "omega_0": {"type": "number"},
                "precision": {"type": "object"},
                "hierarchical_beliefs": {"type": "object"},
                "action_policy": {"type": "object"},
                "vote": {"type": "string", "enum": ["SEAL", "VOID", "SABAR"]},
                "floor_scores": {"type": "object"}
            },
            "required": ["session_id", "entropy_delta", "vote"]
        },
        annotations={"title": "Mind Engine", "readOnlyHint": False, "destructiveHint": False, "openWorldHint": True}
    ),
    
    "_asi_": ToolDefinition(
        name="_asi_",
        title="Heart Engine (Omega)",
        description="Safety evaluation, bias detection, empathy assessment. Implements 555 EMPATHY → 666 ALIGN → 777 SOCIETY.",
        input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["evidence", "empathize", "evaluate", "act", "witness", "stakeholder", "diffusion", "audit", "full"], "default": "full"},
                "query": {"type": "string", "maxLength": 10000},
                "reasoning": {"type": "string"},
                "agi_context": {"type": "object"},
                "session_id": {"type": "string"}
            },
            "required": ["action", "query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "empathy_kappa_r": {"type": "number"},
                "peace_squared": {"type": "number"},
                "thermodynamic_justice": {"type": "number"},
                "stakeholders": {"type": "array"},
                "weakest_stakeholder": {"type": "object"},
                "reversibility_score": {"type": "number"},
                "consent_verified": {"type": "boolean"},
                "vote": {"type": "string", "enum": ["SEAL", "VOID", "SABAR"]},
                "omega_total": {"type": "number"}
            },
            "required": ["session_id", "omega_total", "vote"]
        },
        annotations={"title": "Heart Engine", "readOnlyHint": False, "destructiveHint": False, "openWorldHint": True}
    ),
    
    "_apex_": ToolDefinition(
        name="_apex_",
        title="Soul Engine (Psi) - Judicial",
        description="Judicial consensus, final verdicts. Synthesizes AGI + ASI. Implements 888 APEX PRIME with 9-paradox equilibrium.",
        input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["eureka", "judge", "decide", "proof", "entropy", "full"], "default": "full"},
                "query": {"type": "string"},
                "response": {"type": "string"},
                "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR"]},
                "agi_context": {"type": "object"},
                "asi_context": {"type": "object"},
                "reasoning": {"type": "string"},
                "session_id": {"type": "string"}
            },
            "required": ["action", "query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "final_verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR", "EQUILIBRIUM"]},
                "trinity_score": {"type": "number"},
                "paradox_scores": {"type": "object"},
                "equilibrium": {"type": "object"},
                "constitutional_alignment": {"type": "object"},
                "proof": {"type": "object"}
            },
            "required": ["session_id", "final_verdict", "trinity_score"]
        },
        annotations={"title": "Soul Engine", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": False}
    ),
    
    "_vault_": ToolDefinition(
        name="_vault_",
        title="Immutable Ledger (Seal)",
        description="Tamper-proof storage using Merkle-tree sealing. Implements F1 Amanah (Trust).",
        input_schema={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"], "default": "seal"},
                "verdict": {"type": "string"},
                "decision_data": {"type": "object"},
                "target": {"type": "string", "enum": ["seal", "ledger", "canon", "fag", "tempa", "phoenix", "audit"], "default": "seal"},
                "session_id": {"type": "string"}
            },
            "required": ["action"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "merkle_root": {"type": "string"},
                "timestamp": {"type": "string"},
                "seal_id": {"type": "string"},
                "target": {"type": "string"},
                "integrity_hash": {"type": "string"},
                "status": {"type": "string", "enum": ["SEALED", "PENDING", "ERROR"]}
            },
            "required": ["seal_id", "merkle_root", "status"]
        },
        annotations={"title": "Vault Seal", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": False}
    ),
    
    "_trinity_": ToolDefinition(
        name="_trinity_",
        title="Full Constitutional Pipeline",
        description="Complete metabolic loop: AGI→ASI→APEX→VAULT. Single-call constitutional evaluation.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "maxLength": 10000},
                "session_id": {"type": "string"},
                "auto_seal": {"type": "boolean", "default": True},
                "context": {"type": "object"}
            },
            "required": ["query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "agi_result": {"type": "object"},
                "asi_result": {"type": "object"},
                "apex_result": {"type": "object"},
                "vault_result": {"type": "object"},
                "final_verdict": {"type": "string"},
                "execution_time_ms": {"type": "number"}
            },
            "required": ["session_id", "final_verdict"]
        },
        annotations={"title": "Full Trinity", "readOnlyHint": False, "destructiveHint": True, "openWorldHint": True}
    ),
    
    "_reality_": ToolDefinition(
        name="_reality_",
        title="External Fact-Checking",
        description="Fact-checking via external sources. Implements F7 Humility: external data labeled, sources cited, uncertainty stated.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "maxLength": 500},
                "session_id": {"type": "string"}
            },
            "required": ["query"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "verified": {"type": "boolean"},
                "confidence": {"type": "number"},
                "sources": {"type": "array"},
                "caveats": {"type": "string"},
                "external_data_label": {"type": "string"}
            },
            "required": ["verified", "confidence"]
        },
        annotations={"title": "Reality Check", "readOnlyHint": True, "destructiveHint": False, "openWorldHint": True}
    )
}


class ArifOSMCPServer:
    """arifOS MCP Server implementing AAA Framework"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.tools = TOOL_SCHEMAS
        self.request_handlers = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "prompts/list": self._handle_prompts_list,
        }
    
    async def run(self):
        """Main server loop"""
        logger.info("arifOS MCP Server starting...")
        
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, input)
                if not line:
                    continue
                
                request = json.loads(line)
                response = await self._process_request(request)
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                self._send_error(None, -32700, "Parse error", str(e))
            except Exception as e:
                logger.error(f"Server error: {e}")
                self._send_error(None, -32603, "Internal error", str(e))
    
    async def _process_request(self, request: Dict) -> Dict:
        """Process JSON-RPC request"""
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})
        
        logger.info(f"Request: {method} (id: {request_id})")
        
        if method in self.request_handlers:
            return await self.request_handlers[method](request_id, params)
        else:
            return self._send_error(request_id, -32601, f"Method not found: {method}")
    
    def _send_error(self, request_id, code: int, message: str, data=None) -> Dict:
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return {"jsonrpc": "2.0", "id": request_id, "error": error}
    
    def _send_result(self, request_id, result: Dict) -> Dict:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    
    async def _handle_initialize(self, request_id, params: Dict) -> Dict:
        """Handle initialize request"""
        protocol_version = params.get("protocolVersion", "2025-06-18")
        client_info = params.get("clientInfo", {})
        
        logger.info(f"Client connected: {client_info.get('name', 'unknown')}")
        
        return self._send_result(request_id, {
            "protocolVersion": protocol_version,
            "serverInfo": {"name": "arifOS", "version": "v54.0", "title": "arifOS Constitutional AI"},
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {},
                "prompts": {},
                "logging": {}
            },
            "instructions": """arifOS MCP Server - Constitutional AI Governance. Tools: _init_ (session), _agi_ (mind), _asi_ (heart), _apex_ (soul), _vault_ (seal), _trinity_ (full), _reality_ (fact-check). Call _init_ first, then _trinity_ for complete evaluation."""
        })
    
    async def _handle_tools_list(self, request_id, params: Dict) -> Dict:
        """Handle tools/list request"""
        tools_list = [tool.to_dict() for tool in self.tools.values()]
        return self._send_result(request_id, {"tools": tools_list})
    
    async def _handle_tools_call(self, request_id, params: Dict) -> Dict:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return self._send_error(request_id, -32602, f"Unknown tool: {tool_name}")
        
        try:
            result = await self._execute_tool(tool_name, arguments)
            return self._send_result(request_id, result.to_dict())
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return self._send_result(request_id, ToolResult(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                is_error=True
            ).to_dict())
    
    async def _execute_tool(self, tool_name: str, arguments: Dict) -> ToolResult:
        """Execute tool logic"""
        
        if tool_name == "_init_":
            return await self._tool_init(arguments)
        elif tool_name == "_trinity_":
            return await self._tool_trinity(arguments)
        else:
            # For demo, return mock results
            return ToolResult(
                content=[{"type": "text", "text": f"Tool {tool_name} executed with args: {json.dumps(arguments)}"}],
                structured_content={"tool": tool_name, "status": "executed"}
            )
    
    async def _tool_init(self, args: Dict) -> ToolResult:
        """Implement _init_ tool"""
        action = args.get("action", "init")
        query = args.get("query", "")
        
        injection_patterns = ["ignore previous", "system prompt", "DAN mode", "jailbreak"]
        injection_detected = any(p in query.lower() for p in injection_patterns)
        
        session_id = f"arif_{uuid.uuid4().hex[:12]}"
        self.sessions[session_id] = {
            "created": datetime.utcnow().isoformat(),
            "action": action,
            "query": query,
            "injection_check": not injection_detected
        }
        
        result = {
            "session_id": session_id,
            "authority_level": "user",
            "budget_allocated": 1000,
            "injection_check_passed": not injection_detected,
            "access_level": "constitutional",
            "session_ttl": 3600,
            "constitutional_version": "v54.0"
        }
        
        return ToolResult(
            content=[{"type": "text", "text": json.dumps(result, indent=2)}],
            structured_content=result
        )
    
    async def _tool_trinity(self, args: Dict) -> ToolResult:
        """Implement _trinity_ tool - full pipeline"""
        import time
        start = time.time()
        
        query = args.get("query", "")
        session_id = args.get("session_id") or f"trinity_{uuid.uuid4().hex[:12]}"
        
        # Mock execution - would integrate with actual codebase
        result = {
            "session_id": session_id,
            "final_verdict": "SEAL",
            "trinity_score": 0.91,
            "equilibrium": {"is_equilibrium": True, "std_deviation": 0.08},
            "execution_time_ms": (time.time() - start) * 1000
        }
        
        return ToolResult(
            content=[{"type": "text", "text": json.dumps(result, indent=2)}],
            structured_content=result
        )
    
    async def _handle_resources_list(self, request_id, params: Dict) -> Dict:
        return self._send_result(request_id, {
            "resources": [
                {"uri": "constitution://floors", "name": "Constitutional Floors F1-F13", "mimeType": "application/json"},
                {"uri": "docs://9-paradox", "name": "9-Paradox Architecture", "mimeType": "text/markdown"}
            ]
        })
    
    async def _handle_prompts_list(self, request_id, params: Dict) -> Dict:
        return self._send_result(request_id, {
            "prompts": [
                {"name": "constitutional_evaluation", "description": "Complete constitutional evaluation"},
                {"name": "safety_check", "description": "Quick safety assessment"}
            ]
        })


if __name__ == "__main__":
    server = ArifOSMCPServer()
    asyncio.run(server.run())
