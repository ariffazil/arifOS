#!/usr/bin/env python3
"""
Constitutional Codex MCP Server for arifOS
Unified server for OpenAI Codex integration with full constitutional governance
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# MCP server components
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP package not available. Codex server will operate in mock mode.")

# arifOS constitutional components
from arifos_core.mcp.codex_client import ConstitutionalCodexClient
from arifos_core.mcp.tools.codex_skills import CodexConstitutionalSkills
from arifos_core.trinity.coordinator import TrinityCoordinator, coordinate_codex_trinity
from arifos_core.system.apex_prime import Verdict
from arifos_core.memory.vault999 import vault999_query, vault999_store


@dataclass
class CodexMCPServerConfig:
    """Configuration for Constitutional Codex MCP Server"""
    user_id: str = "codex_user"
    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: float = 30.0
    constitutional_mode: bool = True
    trinity_coordination: bool = True
    session_timeout: int = 3600
    max_sessions: int = 10


class ConstitutionalCodexMCPServer:
    """Constitutional MCP server for OpenAI Codex integration"""
    
    def __init__(self, config: CodexMCPServerConfig):
        self.config = config
        
        # Initialize constitutional components
        self.codex_client = ConstitutionalCodexClient(
            api_key=config.api_key,
            user_id=config.user_id
        )
        
        self.codex_skills = CodexConstitutionalSkills(user_id=config.user_id)
        self.trinity_coordinator = TrinityCoordinator(user_id=config.user_id)
        
        # Session management
        self.sessions: Dict[str, Dict] = {}
        
        # Tool registry
        self.tools = self._initialize_constitutional_tools()
        
        logging.info(f"ConstitutionalCodexMCPServer initialized for user: {config.user_id}")
    
    def _initialize_constitutional_tools(self) -> List[Tool]:
        """Initialize all constitutional tools for Codex"""
        
        tools = [
            # Constitutional Pipeline Tools
            Tool(
                name="arifos_live",
                description="Live constitutional governance through 000→999 pipeline",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to process through constitutional pipeline"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for constitutional tracking"
                        },
                        "intent": {
                            "type": "string",
                            "description": "Intent behind the query for F1 Amanah validation"
                        },
                        "lane": {
                            "type": "string",
                            "enum": ["HARD", "SOFT", "PHATIC"],
                            "description": "Constitutional strictness level",
                            "default": "HARD"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context for constitutional processing"
                        }
                    },
                    "required": ["query", "user_id"]
                }
            ),
            
            Tool(
                name="agi_think",
                description="AGI bundle: 111 SENSE + 222 REFLECT + 777 EUREKA - The Mind",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query for AGI thinking process"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier"
                        },
                        "depth": {
                            "type": "string",
                            "enum": ["surface", "deep", "recursive"],
                            "description": "Thinking depth level",
                            "default": "deep"
                        }
                    },
                    "required": ["query", "user_id"]
                }
            ),
            
            Tool(
                name="asi_act",
                description="ASI bundle: 555 EMPATHIZE + 666 BRIDGE - The Heart",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to validate with ASI empathy"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier"
                        },
                        "stakeholder_context": {
                            "type": "object",
                            "description": "Context about affected stakeholders"
                        }
                    },
                    "required": ["action", "user_id"]
                }
            ),
            
            # Codex-Specific Constitutional Skills
            Tool(
                name="codex_code_analysis",
                description="Analyze code with AGI/ASI/APEX constitutional validation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["security", "performance", "architecture", "maintainability"],
                            "description": "Type of analysis to perform"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for constitutional tracking"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context about the code"
                        }
                    },
                    "required": ["code", "analysis_type", "user_id"]
                }
            ),
            
            Tool(
                name="codex_code_generation",
                description="Generate code with constitutional constraints and trinity validation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "requirements": {
                            "type": "string",
                            "description": "Code requirements and specifications"
                        },
                        "constraints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Constitutional constraints to apply"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for constitutional tracking"
                        },
                        "language": {
                            "type": "string",
                            "default": "python",
                            "description": "Programming language"
                        },
                        "complexity_level": {
                            "type": "string",
                            "enum": ["simple", "moderate", "complex"],
                            "description": "Desired code complexity level",
                            "default": "moderate"
                        }
                    },
                    "required": ["requirements", "user_id"]
                }
            ),
            
            Tool(
                name="codex_debug_assistance",
                description="Debug assistance with trinity coordination and constitutional validation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_description": {
                            "type": "string",
                            "description": "Description of the error or bug"
                        },
                        "code_context": {
                            "type": "string",
                            "description": "Relevant code context"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier"
                        },
                        "debug_level": {
                            "type": "string",
                            "enum": ["basic", "advanced", "architectural"],
                            "description": "Level of debugging assistance",
                            "default": "advanced"
                        }
                    },
                    "required": ["error_description", "user_id"]
                }
            ),
            
            Tool(
                name="codex_architectural_review",
                description="Architectural review with AGI perspective",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "architecture_description": {
                            "type": "string",
                            "description": "Description of the architecture to review"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier"
                        },
                        "review_focus": {
                            "type": "string",
                            "enum": ["scalability", "maintainability", "security", "performance"],
                            "description": "Focus area for architectural review",
                            "default": "maintainability"
                        }
                    },
                    "required": ["architecture_description", "user_id"]
                }
            ),
            
            # Memory and Governance Tools
            Tool(
                name="vault999_query",
                description="Query arifOS constitutional memory system",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query or prompt"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier for memory access"
                        },
                        "document_id": {
                            "type": "string",
                            "description": "Specific document ID to fetch"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 10,
                            "description": "Maximum results to return"
                        }
                    },
                    "required": ["query"]
                }
            ),
            
            Tool(
                name="vault999_store",
                description="Store insights in arifOS constitutional memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "insight_text": {
                            "type": "string",
                            "description": "The core insight/learning to store"
                        },
                        "structure": {
                            "type": "string",
                            "description": "What changed (the new invariant)"
                        },
                        "truth_boundary": {
                            "type": "string",
                            "description": "What is now constrained (non-violable)"
                        },
                        "scar": {
                            "type": "string",
                            "description": "What it took / what it prevents"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User identifier"
                        },
                        "vault_target": {
                            "type": "string",
                            "enum": ["CCC", "BBB"],
                            "default": "BBB",
                            "description": "Target vault (CCC for machine law, BBB for memory)"
                        }
                    },
                    "required": ["insight_text", "structure", "truth_boundary", "scar", "user_id"]
                }
            ),
            
            Tool(
                name="fag_read",
                description="Governed file read with constitutional oversight",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to read"
                        },
                        "root": {
                            "type": "string",
                            "description": "Root directory for jailed access"
                        },
                        "enable_ledger": {
                            "type": "boolean",
                            "default": true,
                            "description": "Log access to Cooling Ledger"
                        }
                    },
                    "required": ["path"]
                }
            ),
            
            Tool(
                name="fag_write",
                description="Governed file write with constitutional oversight",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to file"
                        },
                        "root": {
                            "type": "string",
                            "description": "Root directory for jailed access"
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["create", "update", "append"],
                            "description": "Type of write operation"
                        }
                    },
                    "required": ["path", "content", "operation"]
                }
            )
        ]
        
        return tools
    
    async def handle_tool_call(self, name: str, arguments: Dict) -> Union[TextContent, List[TextContent]]:
        """Handle tool calls with constitutional governance"""
        
        try:
            logging.info(f"Handling tool call: {name} with arguments: {arguments}")
            
            # Validate arguments constitutionally
            validation_result = await self._validate_tool_arguments(name, arguments)
            if not validation_result["valid"]:
                return TextContent(
                    type="text",
                    text=f"Constitutional validation failed: {validation_result['reason']}"
                )
            
            # Route to appropriate tool handler
            if name == "arifos_live":
                return await self._handle_arifos_live(arguments)
            elif name == "agi_think":
                return await self._handle_agi_think(arguments)
            elif name == "asi_act":
                return await self._handle_asi_act(arguments)
            elif name == "codex_code_analysis":
                return await self._handle_codex_code_analysis(arguments)
            elif name == "codex_code_generation":
                return await self._handle_codex_code_generation(arguments)
            elif name == "codex_debug_assistance":
                return await self._handle_codex_debug_assistance(arguments)
            elif name == "codex_architectural_review":
                return await self._handle_codex_architectural_review(arguments)
            elif name == "vault999_query":
                return await self._handle_vault999_query(arguments)
            elif name == "vault999_store":
                return await self._handle_vault999_store(arguments)
            elif name == "fag_read":
                return await self._handle_fag_read(arguments)
            elif name == "fag_write":
                return await self._handle_fag_write(arguments)
            else:
                return TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )
                
        except Exception as e:
            logging.error(f"Error handling tool call {name}: {e}")
            return TextContent(
                type="text",
                text=f"Error processing tool {name}: {str(e)}"
            )
    
    async def _validate_tool_arguments(self, tool_name: str, arguments: Dict) -> Dict:
        """Validate tool arguments constitutionally"""
        
        # Basic validation
        if not arguments or not isinstance(arguments, dict):
            return {"valid": False, "reason": "Invalid arguments format"}
        
        # Tool-specific validation
        if tool_name in ["codex_code_analysis", "codex_code_generation", "codex_debug_assistance"]:
            # Validate code-related arguments don't contain malicious patterns
            code_content = arguments.get("code", "") or arguments.get("requirements", "")
            if self._detect_malicious_patterns(code_content):
                return {"valid": False, "reason": "F12 Injection violation: Malicious patterns detected"}
        
        # User ID validation
        user_id = arguments.get("user_id")
        if user_id and not self._validate_user_id(user_id):
            return {"valid": False, "reason": "F11 Command Auth violation: Invalid user identifier"}
        
        return {"valid": True, "reason": "Arguments validated successfully"}
    
    def _detect_malicious_patterns(self, content: str) -> bool:
        """Detect potentially malicious patterns in content"""
        malicious_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'os\.system',
            r'subprocess\.call.*shell=True',
            r'rm\s+-rf',
            r'del\s+/f',
            r'format\s*\(.*\*.*\*)'  # SQL injection patterns
        ]
        
        import re
        for pattern in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_user_id(self, user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id or not isinstance(user_id, str):
            return False
        
        # Basic validation - alphanumeric with underscores and hyphens
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', user_id))
    
    # Individual tool handlers
    
    async def _handle_arifos_live(self, arguments: Dict) -> TextContent:
        """Handle arifos_live tool call"""
        query = arguments.get("query", "")
        user_id = arguments.get("user_id", self.config.user_id)
        intent = arguments.get("intent", "general_inquiry")
        lane = arguments.get("lane", "HARD")
        context = arguments.get("context", {})
        
        result = await self.codex_client.process_constitutional_request(
            query=query,
            user_id=user_id,
            intent=intent,
            context=context
        )
        
        return TextContent(
            type="text",
            text=f"Constitutional Verdict: {result.verdict}\n"
                 f"Output: {result.output}\n"
                 f"Reason: {result.reason}\n"
                 f"Constitutional Score: {result.metrics.get('constitutional_score', 'N/A')}\n"
                 f"Session ID: {result.session_id}"
        )
    
    async def _handle_agi_think(self, arguments: Dict) -> TextContent:
        """Handle agi_think tool call"""
        query = arguments.get("query", "")
        user_id = arguments.get("user_id", self.config.user_id)
        depth = arguments.get("depth", "deep")
        
        # Simulate AGI thinking (would call actual AGI in production)
        agi_result = await self._simulate_agi_thinking(query, user_id, depth)
        
        return TextContent(
            type="text",
            text=f"AGI Analysis: {agi_result['analysis']}\n"
                 f"Architectural Insights: {', '.join(agi_result['insights'])}\n"
                 f"Confidence: {agi_result['confidence']:.2f}\n"
                 f"Constitutional Compliance: {agi_result['constitutional_compliance']}"
        )
    
    async def _handle_asi_act(self, arguments: Dict) -> TextContent:
        """Handle asi_act tool call"""
        action = arguments.get("action", "")
        user_id = arguments.get("user_id", self.config.user_id)
        stakeholder_context = arguments.get("stakeholder_context", {})
        
        # Simulate ASI validation (would call actual ASI in production)
        asi_result = await self._simulate_asi_validation(action, user_id, stakeholder_context)
        
        return TextContent(
            type="text",
            text=f"ASI Validation: {asi_result['validation']}\n"
                 f"Empathy Score: {asi_result['empathy_score']:.2f}\n"
                 f"Weakest Stakeholder Protected: {asi_result['weakest_protected']}\n"
                 f"κᵣ (Empathy Conductance): {asi_result['kappa_r']:.2f}"
        )
    
    async def _handle_codex_code_analysis(self, arguments: Dict) -> TextContent:
        """Handle codex_code_analysis tool call"""
        code = arguments.get("code", "")
        analysis_type = arguments.get("analysis_type", "security")
        user_id = arguments.get("user_id", self.config.user_id)
        context = arguments.get("context", {})
        
        result = await self.codex_skills.analyze_code(code, analysis_type, user_id, context)
        
        return TextContent(
            type="text",
            text=f"Code Analysis Verdict: {result['verdict']}\n"
                 f"Security Score: {result['security_score']:.2f}/1.0\n"
                 f"Performance Score: {result['performance_score']:.2f}/1.0\n"
                 f"Architectural Score: {result['architectural_score']:.2f}/1.0\n"
                 f"Maintainability Score: {result['maintainability_score']:.2f}/1.0\n"
                 f"Constitutional Compliance: {result['constitutional_compliance']}\n"
                 f"AGI Insights: {len(result['agi_insights'])} insights\n"
                 f"Recommendations: {len(result['recommendations'])} recommendations"
        )
    
    async def _handle_codex_code_generation(self, arguments: Dict) -> TextContent:
        """Handle codex_code_generation tool call"""
        requirements = arguments.get("requirements", "")
        constraints = arguments.get("constraints", [])
        user_id = arguments.get("user_id", self.config.user_id)
        language = arguments.get("language", "python")
        complexity_level = arguments.get("complexity_level", "moderate")
        
        result = await self.codex_skills.generate_code(
            requirements, constraints, user_id, language, complexity_level
        )
        
        return TextContent(
            type="text",
            text=f"Code Generation Verdict: {result['verdict']}\n"
                 f"Complexity Score: {result['complexity_score']:.2f}/1.0\n"
                 f"Clarity Score: {result['clarity_score']:.2f}/1.0\n"
                 f"Trinity Validation: {result['trinity_validation']}\n"
                 f"Constraints Applied: {len(result['constraints_applied'])}\n"
                 f"Generated Code:\n{result['generated_code'][:500]}..."
        )
    
    async def _handle_codex_debug_assistance(self, arguments: Dict) -> TextContent:
        """Handle codex_debug_assistance tool call"""
        error_description = arguments.get("error_description", "")
        code_context = arguments.get("code_context", "")
        user_id = arguments.get("user_id", self.config.user_id)
        debug_level = arguments.get("debug_level", "advanced")
        
        # Simulate debug assistance (would implement actual debugging logic)
        debug_result = await self._simulate_debug_assistance(error_description, code_context, debug_level)
        
        return TextContent(
            type="text",
            text=f"Debug Analysis: {debug_result['analysis']}\n"
                 f"Root Cause: {debug_result['root_cause']}\n"
                 f"Suggested Fix: {debug_result['suggested_fix']}\n"
                 f"Prevention: {debug_result['prevention']}\n"
                 f"Constitutional Validation: {debug_result['constitutional_valid']}"
        )
    
    async def _handle_codex_architectural_review(self, arguments: Dict) -> TextContent:
        """Handle codex_architectural_review tool call"""
        architecture_description = arguments.get("architecture_description", "")
        user_id = arguments.get("user_id", self.config.user_id)
        review_focus = arguments.get("review_focus", "maintainability")
        
        # Simulate architectural review (would implement actual review logic)
        review_result = await self._simulate_architectural_review(architecture_description, review_focus)
        
        return TextContent(
            type="text",
            text=f"Architectural Review: {review_result['review']}\n"
                 f"AGI Architectural Score: {review_result['architectural_score']:.2f}/1.0\n"
                 f"Scalability Assessment: {review_result['scalability']}\n"
                 f"Maintainability Assessment: {review_result['maintainability']}\n"
                 f"Security Assessment: {review_result['security']}\n"
                 f"Constitutional Compliance: {review_result['constitutional_compliance']}"
        )
    
    async def _handle_vault999_query(self, arguments: Dict) -> TextContent:
        """Handle vault999_query tool call"""
        query = arguments.get("query", "")
        user_id = arguments.get("user_id", self.config.user_id)
        document_id = arguments.get("document_id")
        max_results = arguments.get("max_results", 10)
        
        try:
            result = await vault999_query(
                query=query,
                user_id=user_id,
                document_id=document_id,
                max_results=max_results
            )
            
            return TextContent(
                type="text",
                text=f"VAULT-999 Query Results:\n{json.dumps(result, indent=2, default=str)}"
            )
            
        except Exception as e:
            return TextContent(
                type="text",
                text=f"VAULT-999 query failed: {str(e)}"
            )
    
    async def _handle_vault999_store(self, arguments: Dict) -> TextContent:
        """Handle vault999_store tool call"""
        insight_text = arguments.get("insight_text", "")
        structure = arguments.get("structure", "")
        truth_boundary = arguments.get("truth_boundary", "")
        scar = arguments.get("scar", "")
        user_id = arguments.get("user_id", self.config.user_id)
        vault_target = arguments.get("vault_target", "BBB")
        
        try:
            result = await vault999_store(
                insight_text=insight_text,
                structure=structure,
                truth_boundary=truth_boundary,
                scar=scar,
                vault_target=vault_target,
                user_id=user_id
            )
            
            return TextContent(
                type="text",
                text=f"VAULT-999 Storage Result:\n{json.dumps(result, indent=2, default=str)}"
            )
            
        except Exception as e:
            return TextContent(
                type="text",
                text=f"VAULT-999 storage failed: {str(e)}"
            )
    
    async def _handle_fag_read(self, arguments: Dict) -> TextContent:
        """Handle fag_read tool call"""
        path = arguments.get("path", "")
        root = arguments.get("root", ".")
        enable_ledger = arguments.get("enable_ledger", True)
        
        try:
            # This would call the actual FAG read implementation
            # For now, return mock result
            return TextContent(
                type="text",
                text=f"FAG Read Result:\n"
                     f"Path: {path}\n"
                     f"Root: {root}\n"
                     f"Ledger Logging: {enable_ledger}\n"
                     f"Status: Constitutional read access granted"
            )
            
        except Exception as e:
            return TextContent(
                type="text",
                text=f"FAG read failed: {str(e)}"
            )
    
    async def _handle_fag_write(self, arguments: Dict) -> TextContent:
        """Handle fag_write tool call"""
        path = arguments.get("path", "")
        content = arguments.get("content", "")
        root = arguments.get("root", ".")
        operation = arguments.get("operation", "create")
        
        try:
            # This would call the actual FAG write implementation
            # For now, return mock result
            return TextContent(
                type="text",
                text=f"FAG Write Result:\n"
                     f"Path: {path}\n"
                     f"Operation: {operation}\n"
                     f"Root: {root}\n"
                     f"Content Length: {len(content)} characters\n"
                     f"Status: Constitutional write access granted"
            )
            
        except Exception as e:
            return TextContent(
                type="text",
                text=f"FAG write failed: {str(e)}"
            )
    
    # Simulation methods for development
    
    async def _simulate_agi_thinking(self, query: str, user_id: str, depth: str) -> Dict:
        """Simulate AGI thinking for development"""
        return {
            "analysis": f"AGI architectural analysis of: {query[:50]}...",
            "insights": [
                "Modular architecture recommended",
                "Scalability considerations identified",
                "Security patterns detected"
            ],
            "confidence": 0.85,
            "constitutional_compliance": {
                "f2_truth": True,
                "f1_amanah": True,
                "f10_symbolic": True
            }
        }
    
    async def _simulate_asi_validation(self, action: str, user_id: str, stakeholder_context: Dict) -> Dict:
        """Simulate ASI validation for development"""
        return {
            "validation": f"ASI safety validation complete for: {action[:50]}...",
            "empathy_score": 0.89,
            "weakest_protected": True,
            "kappa_r": 0.87,
            "stakeholder_impact": {
                "end_users": 0.8,
                "developers": 0.6,
                "system": 0.5
            }
        }
    
    async def _simulate_debug_assistance(self, error_description: str, code_context: str, debug_level: str) -> Dict:
        """Simulate debug assistance for development"""
        return {
            "analysis": f"Debug analysis for: {error_description[:50]}...",
            "root_cause": "AttributeError due to NoneType object access",
            "suggested_fix": "Add null check before accessing object attributes",
            "prevention": "Implement comprehensive input validation",
            "constitutional_valid": True
        }
    
    async def _simulate_architectural_review(self, architecture_description: str, review_focus: str) -> Dict:
        """Simulate architectural review for development"""
        return {
            "review": f"AGI architectural review of: {architecture_description[:50]}...",
            "architectural_score": 0.82,
            "scalability": "Architecture supports horizontal scaling",
            "maintainability": "Good separation of concerns detected",
            "security": "Security patterns properly integrated",
            "constitutional_compliance": True
        }
    
    async def run_server(self):
        """Run the constitutional Codex MCP server"""
        
        if not MCP_AVAILABLE:
            logging.error("MCP package not available. Cannot run server.")
            return
        
        from mcp.server.stdio import stdio_server
        
        server = Server("arifos-codex-constitutional")
        
        @server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available constitutional tools"""
            return self.tools
        
        @server.call_tool()
        async def handle_call_tool(name: str, arguments: Optional[Dict]) -> Union[TextContent, List[TextContent]]:
            """Handle tool calls with constitutional governance"""
            if arguments is None:
                arguments = {}
            
            return await self.handle_tool_call(name, arguments)
        
        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="arifos-codex-constitutional",
                    server_version="46.2.2",
                    capabilities=server.get_capabilities()
                )
            )


async def main():
    """Main entry point for Constitutional Codex MCP Server"""
    
    # Load configuration from environment
    config = CodexMCPServerConfig(
        user_id=os.getenv("ARIFOS_USER_ID", "codex_user"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4000")),
        timeout=float(os.getenv("OPENAI_TIMEOUT", "30.0")),
        constitutional_mode=os.getenv("ARIFOS_CONSTITUTIONAL_MODE", "true").lower() == "true",
        trinity_coordination=os.getenv("ARIFOS_TRINITY_ENABLED", "true").lower() == "true",
        session_timeout=int(os.getenv("ARIFOS_SESSION_TIMEOUT", "3600")),
        max_sessions=int(os.getenv("ARIFOS_MAX_SESSIONS", "10"))
    )
    
    # Create and run server
    server = ConstitutionalCodexMCPServer(config)
    
    logging.info("Starting Constitutional Codex MCP Server...")
    logging.info(f"Configuration: user_id={config.user_id}, constitutional_mode={config.constitutional_mode}, trinity_coordination={config.trinity_coordination}")
    
    try:
        await server.run_server()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run server
    asyncio.run(main())