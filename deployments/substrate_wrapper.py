#!/usr/bin/env python3
"""
MCP Substrate Wrapper — HTTP-to-MCP Bridge

Provides HTTP endpoints for arifOS substrate_bridge.py to connect to.
Each substrate runs as a separate HTTP server on its own port.

DITEMPA BUKAN DIBERI
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SubstrateHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP substrate simulation."""
    
    substrate_name = "base"
    
    def log_message(self, format, *args):
        logger.info(f"[{self.substrate_name}] {format % args}")
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path in ["/health", "/", "/mcp/health", "/api/health"]:
            self.handle_health()
        elif path in ["/tools", "/mcp/tools", "/api/tools"]:
            self.handle_list_tools()
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else '{}'
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}
        
        # Extract tool name from path
        if '/tools/' in path and '/call' in path:
            tool_name = path.split('/tools/')[1].split('/call')[0]
            self.handle_call_tool(tool_name, data)
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def handle_health(self):
        raise NotImplementedError
    
    def handle_list_tools(self):
        raise NotImplementedError
    
    def handle_call_tool(self, tool_name, arguments):
        raise NotImplementedError


class TimeSubstrateHandler(SubstrateHandler):
    """MCP Time Server — F2 Truth (deterministic epochs)"""
    
    substrate_name = "mcp_time"
    
    def handle_health(self):
        self.send_json_response({
            "status": "OK",
            "service": "mcp_time",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def handle_list_tools(self):
        self.send_json_response({
            "tools": [
                {"name": "get_current_time", "description": "Get current UTC time"},
                {"name": "get_epoch", "description": "Get Unix epoch timestamp"},
                {"name": "convert_timezone", "description": "Convert between timezones"}
            ]
        })
    
    def handle_call_tool(self, tool_name, arguments):
        if tool_name == "get_current_time":
            result = {
                "datetime": datetime.now(timezone.utc).isoformat(),
                "timezone": "UTC",
                "epoch": int(datetime.now(timezone.utc).timestamp())
            }
        elif tool_name == "get_epoch":
            result = {"epoch": int(datetime.now(timezone.utc).timestamp())}
        elif tool_name == "convert_timezone":
            result = {
                "source": arguments.get("from_timezone", "UTC"),
                "target": arguments.get("to_timezone", "UTC"),
                "converted": datetime.now(timezone.utc).isoformat()
            }
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self.send_json_response({"result": result})


class FilesystemSubstrateHandler(SubstrateHandler):
    """MCP Filesystem Server — F1 Amanah (destructive ops gated)"""
    
    substrate_name = "mcp_filesystem"
    destructive_ops = ["delete", "remove", "rm", "rmdir", "unlink"]
    data_dir = os.getenv("MCP_FS_DATA_DIR", "/data")
    
    def handle_health(self):
        self.send_json_response({
            "status": "OK",
            "service": "mcp_filesystem",
            "data_dir": self.data_dir,
            "f1_enforcement": True
        })
    
    def handle_list_tools(self):
        self.send_json_response({
            "tools": [
                {"name": "read_file", "description": "Read file contents"},
                {"name": "write_file", "description": "Write file (requires 888_HOLD)"},
                {"name": "list_directory", "description": "List directory contents"},
                {"name": "delete_file", "description": "Delete file (F1 - requires ratification)"}
            ]
        })
    
    def handle_call_tool(self, tool_name, arguments):
        # F1 Amanah enforcement
        if any(op in tool_name.lower() for op in self.destructive_ops):
            result = {
                "status": "HOLD",
                "verdict": "F1_AMANAH_ENFORCED",
                "message": "Destructive operation requires 888_HOLD ratification",
                "tool": tool_name,
                "floor": "F1"
            }
        elif tool_name == "read_file":
            result = {"status": "OK", "action": "read", "path": arguments.get("path")}
        elif tool_name == "list_directory":
            result = {"status": "OK", "action": "list", "path": arguments.get("path")}
        elif tool_name == "write_file":
            result = {"status": "HOLD", "message": "Write operations require verification"}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self.send_json_response({"result": result})


class GitSubstrateHandler(SubstrateHandler):
    """MCP Git Server — F11 Authority (commits require ratification)"""
    
    substrate_name = "mcp_git"
    
    def handle_health(self):
        self.send_json_response({
            "status": "OK",
            "service": "mcp_git",
            "f11_enforcement": True
        })
    
    def handle_list_tools(self):
        self.send_json_response({
            "tools": [
                {"name": "git_status", "description": "Get git status"},
                {"name": "git_log", "description": "Get commit history"},
                {"name": "git_commit", "description": "Create commit (F11 - requires authority)"},
                {"name": "git_push", "description": "Push to remote (F11 - requires ratification)"}
            ]
        })
    
    def handle_call_tool(self, tool_name, arguments):
        # F11 Authority enforcement
        if tool_name in ["git_commit", "git_push"]:
            result = {
                "status": "HOLD",
                "verdict": "F11_AUTHORITY_ENFORCED",
                "message": f"{tool_name} requires constitutional authority ratification",
                "tool": tool_name,
                "floor": "F11",
                "required": "888_APEX_SEAL"
            }
        elif tool_name == "git_status":
            result = {"status": "OK", "action": "status", "branch": "main"}
        elif tool_name == "git_log":
            result = {"status": "OK", "action": "log", "commits": 5}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self.send_json_response({"result": result})


class MemorySubstrateHandler(SubstrateHandler):
    """MCP Memory Server — F2 Truth, F11 Audit (entity relations)"""
    
    substrate_name = "mcp_memory"
    _entities = {}
    _relations = []
    
    def handle_health(self):
        self.send_json_response({
            "status": "OK",
            "service": "mcp_memory",
            "entities": len(self._entities),
            "relations": len(self._relations)
        })
    
    def handle_list_tools(self):
        self.send_json_response({
            "tools": [
                {"name": "create_entity", "description": "Create new entity"},
                {"name": "get_entity", "description": "Retrieve entity by ID"},
                {"name": "create_relation", "description": "Create relation between entities"},
                {"name": "search_entities", "description": "Search entities by property"}
            ]
        })
    
    def handle_call_tool(self, tool_name, arguments):
        if tool_name == "create_entity":
            entity_id = arguments.get("id") or f"entity_{len(self._entities)}"
            self._entities[entity_id] = arguments
            result = {"status": "OK", "id": entity_id, "action": "created"}
        elif tool_name == "get_entity":
            entity_id = arguments.get("id")
            result = self._entities.get(entity_id, {"error": "Not found"})
        elif tool_name == "create_relation":
            relation = arguments
            self._relations.append(relation)
            result = {"status": "OK", "action": "relation_created"}
        elif tool_name == "search_entities":
            result = {"status": "OK", "matches": list(self._entities.keys())}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self.send_json_response({"result": result})


class FetchSubstrateHandler(SubstrateHandler):
    """MCP Fetch Server — F9 Anti-Hantu (SSRF protection)"""
    
    substrate_name = "mcp_fetch"
    blocked_patterns = [
        "localhost", "127.0.0.1", "0.0.0.0", "::1",
        "10.", "192.168.", "172.16.", "172.17.", "172.18.",
        "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
        "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
        "172.29.", "172.30.", "172.31.",
        "internal.", "metadata.google", "169.254."
    ]
    
    def handle_health(self):
        self.send_json_response({
            "status": "OK",
            "service": "mcp_fetch",
            "f9_enforcement": True,
            "blocked_patterns": len(self.blocked_patterns)
        })
    
    def handle_list_tools(self):
        self.send_json_response({
            "tools": [
                {"name": "fetch_url", "description": "Fetch URL content (F9 protected)"},
                {"name": "fetch_json", "description": "Fetch and parse JSON"},
                {"name": "check_url_safety", "description": "Check if URL is safe to fetch"}
            ]
        })
    
    def handle_call_tool(self, tool_name, arguments):
        url = arguments.get("url", "")
        
        # F9 Anti-Hantu enforcement
        if any(pattern in url for pattern in self.blocked_patterns):
            result = {
                "status": "VOID",
                "verdict": "F9_ANTI_HANTU_ENFORCED",
                "message": "Internal/localhost URL access blocked",
                "url": url,
                "floor": "F9"
            }
        elif tool_name == "fetch_url":
            result = {
                "status": "OK", 
                "action": "fetch",
                "url": url,
                "content_length": 0,
                "note": "External fetch simulated"
            }
        elif tool_name == "fetch_json":
            result = {"status": "OK", "action": "fetch_json", "data": {}}
        elif tool_name == "check_url_safety":
            is_safe = not any(pattern in url for pattern in self.blocked_patterns)
            result = {"url": url, "safe": is_safe}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self.send_json_response({"result": result})


class EverythingSubstrateHandler(SubstrateHandler):
    """MCP Everything Server — Protocol conformance testing"""
    
    substrate_name = "mcp_everything"
    
    def handle_health(self):
        self.send_json_response({
            "status": "OK",
            "service": "mcp_everything",
            "conformance": True,
            "version": "1.0"
        })
    
    def handle_list_tools(self):
        self.send_json_response({
            "tools": [
                {"name": "echo", "description": "Echo back input"},
                {"name": "add", "description": "Add two numbers"},
                {"name": "long_running_op", "description": "Test long-running operation"}
            ]
        })
    
    def handle_call_tool(self, tool_name, arguments):
        if tool_name == "echo":
            result = {"status": "OK", "echo": arguments}
        elif tool_name == "add":
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            result = {"status": "OK", "sum": a + b}
        elif tool_name == "long_running_op":
            result = {"status": "OK", "completed": True, "duration_ms": 100}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        self.send_json_response({"result": result})


def run_substrate(handler_class, port):
    """Run a substrate HTTP server."""
    server = HTTPServer(("0.0.0.0", port), handler_class)
    logger.info(f"Starting {handler_class.substrate_name} on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info(f"Shutting down {handler_class.substrate_name}")


if __name__ == "__main__":
    import sys
    
    substrates = {
        "time": (TimeSubstrateHandler, 8001),
        "filesystem": (FilesystemSubstrateHandler, 8002),
        "git": (GitSubstrateHandler, 8003),
        "memory": (MemorySubstrateHandler, 8004),
        "fetch": (FetchSubstrateHandler, 8005),
        "everything": (EverythingSubstrateHandler, 8006),
    }
    
    if len(sys.argv) < 2:
        print("Usage: substrate_wrapper.py <substrate_name>")
        print(f"Available: {', '.join(substrates.keys())}")
        sys.exit(1)
    
    name = sys.argv[1]
    if name not in substrates:
        print(f"Unknown substrate: {name}")
        print(f"Available: {', '.join(substrates.keys())}")
        sys.exit(1)
    
    handler_class, port = substrates[name]
    run_substrate(handler_class, port)
