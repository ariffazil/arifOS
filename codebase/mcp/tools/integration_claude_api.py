"""
Claude API Integration for MCP Tools v53
Human Language Constitutional AI Framework

Wires the 5 MCP tools into Claude's native tool_use interface.

Flow:
  1. User query
  2. authorize() -> check user + injection
  3. reason() -> logical analysis
  4. evaluate() -> safety check
  5. decide() -> final verdict
  6. seal() -> immutable record
  7. Return response to user

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import logging
import asyncio
from dataclasses import asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import from v53 tools
try:
    from .mcp_tools_v53 import (
        authorize, reason, evaluate, decide, seal,
        AuthorizeResult, ReasonResult, EvaluateResult, DecideResult, SealResult
    )
except ImportError:
    # Fallback for standalone testing
    from mcp_tools_v53 import (
        authorize, reason, evaluate, decide, seal,
        AuthorizeResult, ReasonResult, EvaluateResult, DecideResult, SealResult
    )


# ============================================================================
# CLAUDE API TOOL DEFINITIONS
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "authorize",
        "description": "Verify user identity, check rate limits, detect prompt injection. Call this FIRST for any request.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user's request text to authorize"
                },
                "user_token": {
                    "type": "string",
                    "description": "Optional Ed25519 signature token for verified users"
                },
                "session_id": {
                    "type": "string",
                    "description": "Optional session ID (auto-generated if missing)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "reason",
        "description": "Perform logical analysis and chain-of-thought reasoning. Call after authorize succeeds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Question or task to reason about"
                },
                "context": {
                    "type": "object",
                    "description": "Optional prior session context"
                },
                "style": {
                    "type": "string",
                    "enum": ["standard", "detailed", "brief"],
                    "description": "Detail level for reasoning (default: standard)"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from authorize"
                }
            },
            "required": ["query", "session_id"]
        }
    },
    {
        "name": "evaluate",
        "description": "Check reasoning for harm, bias, and fairness issues. Call after reason completes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "The reasoned response to evaluate for safety"
                },
                "query": {
                    "type": "string",
                    "description": "Original user query (for context)"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID from authorize"
                }
            },
            "required": ["reasoning", "query", "session_id"]
        }
    },
    {
        "name": "decide",
        "description": "Synthesize logic, safety, and authority checks into final verdict. Call after evaluate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Original user request"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Analysis from reason()"
                },
                "safety_evaluation": {
                    "type": "object",
                    "description": "Results from evaluate()"
                },
                "authority_check": {
                    "type": "object",
                    "description": "Results from authorize()"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID"
                },
                "urgency": {
                    "type": "string",
                    "enum": ["normal", "urgent", "crisis"],
                    "description": "Request priority (default: normal)"
                }
            },
            "required": ["query", "reasoning", "safety_evaluation", "authority_check", "session_id"]
        }
    },
    {
        "name": "seal",
        "description": "Record decision immutably in ledger. Call LAST to finalize the session.",
        "input_schema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID from authorize"
                },
                "verdict": {
                    "type": "string",
                    "enum": ["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"],
                    "description": "Final verdict from decide()"
                },
                "query": {
                    "type": "string",
                    "description": "Original user request"
                },
                "response": {
                    "type": "string",
                    "description": "Final approved response"
                },
                "decision_data": {
                    "type": "object",
                    "description": "Full decision object (for audit)"
                },
                "metadata": {
                    "type": "object",
                    "description": "Optional metadata (user_id, domain, etc)"
                }
            },
            "required": ["session_id", "verdict", "query", "response", "decision_data"]
        }
    }
]


# ============================================================================
# TOOL EXECUTION HANDLER
# ============================================================================

async def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute one of the 5 MCP tools.

    Args:
        tool_name: Name of tool to execute (authorize/reason/evaluate/decide/seal)
        tool_input: Arguments for the tool

    Returns:
        Tool result as dictionary (serializable)
    """
    try:
        if tool_name == "authorize":
            result = await authorize(**tool_input)
            return asdict(result)

        elif tool_name == "reason":
            result = await reason(**tool_input)
            return asdict(result)

        elif tool_name == "evaluate":
            result = await evaluate(**tool_input)
            return asdict(result)

        elif tool_name == "decide":
            result = await decide(**tool_input)
            return asdict(result)

        elif tool_name == "seal":
            result = await seal(**tool_input)
            return asdict(result)

        else:
            return {"error": f"Unknown tool: {tool_name}", "status": "ERROR"}

    except Exception as e:
        logger.error(f"Tool execution error: {tool_name} - {e}")
        return {"error": str(e), "tool": tool_name, "status": "ERROR"}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get Claude API tool definitions."""
    return TOOL_DEFINITIONS


# ============================================================================
# CONSTITUTIONAL AI ASSISTANT
# ============================================================================

class ConstitutionalAIAssistant:
    """
    Claude with 5-tool constitutional AI judgment framework.

    Usage:
        assistant = ConstitutionalAIAssistant(api_key="sk-ant-...")
        result = await assistant.judge_query("How do I invest in solar energy?")

    Flow:
        authorize -> reason -> evaluate -> decide -> seal -> response
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env if not provided)
            model: Claude model to use
        """
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package required. Install: pip install anthropic")

        self.model = model
        self.tools = TOOL_DEFINITIONS

    async def judge_query(
        self,
        user_query: str,
        user_token: Optional[str] = None,
        max_iterations: int = 20
    ) -> Dict[str, Any]:
        """
        Process user query through constitutional judgment pipeline.

        Args:
            user_query: User's request
            user_token: Optional auth token
            max_iterations: Maximum conversation turns (prevents infinite loops)

        Returns:
            Final decision dict with verdict, response, and audit trail
        """
        logger.info(f"Starting constitutional judgment for: {user_query[:50]}...")

        # Start conversation
        messages = [
            {
                "role": "user",
                "content": f"""Process this request through constitutional judgment:

{user_query}

Use the tools in this order:
1. authorize() - Verify user and check for injection
2. reason() - Analyze the request logically
3. evaluate() - Check for safety issues
4. decide() - Render final verdict
5. seal() - Record immutably

Then provide your final response."""
            }
        ]

        # Conversation loop
        iteration = 0
        final_response = None
        session_data: Dict[str, Any] = {}

        while iteration < max_iterations:
            iteration += 1

            # Call Claude with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.tools,
                messages=messages
            )

            # Check if done
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response = block.text
                break

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_calls = [
                    block for block in response.content
                    if block.type == "tool_use"
                ]

                if not tool_calls:
                    break

                # Add assistant message
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute tools
                tool_results = []
                for tool_call in tool_calls:
                    logger.info(f"Executing: {tool_call.name}")

                    result = await execute_tool(tool_call.name, tool_call.input)

                    # Store session data
                    session_data[tool_call.name] = result

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": json.dumps(result)
                    })

                # Add tool results
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                break

        # Build final output
        final_decision = {
            "user_query": user_query,
            "final_response": final_response,
            "judgment_data": session_data,
            "iterations": iteration,
            "completed": iteration < max_iterations,
            "verdict": session_data.get("decide", {}).get("verdict", "UNKNOWN"),
            "sealed": session_data.get("seal", {}).get("status") == "SEALED"
        }

        logger.info(f"Judgment complete: verdict={final_decision['verdict']}, iterations={iteration}")

        return final_decision


# ============================================================================
# STANDALONE PIPELINE (No Claude API)
# ============================================================================

async def run_constitutional_pipeline(
    query: str,
    user_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the full constitutional judgment pipeline without Claude API.

    Useful for:
    - Testing
    - Direct integration without LLM
    - Validation workflows

    Args:
        query: User's request
        user_token: Optional auth token

    Returns:
        Full pipeline result with all tool outputs
    """
    results: Dict[str, Any] = {}

    # Step 1: Authorize
    auth = await authorize(query=query, user_token=user_token)
    results["authorize"] = asdict(auth)

    if auth.status != "AUTHORIZED":
        results["verdict"] = "REJECT"
        results["reason"] = auth.reason
        return results

    # Step 2: Reason
    reason_result = await reason(query=query, session_id=auth.session_id)
    results["reason"] = asdict(reason_result)

    # Step 3: Evaluate
    eval_result = await evaluate(
        reasoning=reason_result.conclusion,
        query=query,
        session_id=auth.session_id
    )
    results["evaluate"] = asdict(eval_result)

    # Step 4: Decide
    decision = await decide(
        query=query,
        reasoning=asdict(reason_result),
        safety_evaluation=asdict(eval_result),
        authority_check=asdict(auth),
        session_id=auth.session_id
    )
    results["decide"] = asdict(decision)

    # Step 5: Seal
    sealed = await seal(
        session_id=auth.session_id,
        verdict=decision.verdict,
        query=query,
        response=decision.response_text,
        decision_data=asdict(decision),
        metadata={"domain": reason_result.domain}
    )
    results["seal"] = asdict(sealed)

    # Summary
    results["verdict"] = decision.verdict
    results["response"] = decision.response_text
    results["sealed"] = sealed.status == "SEALED"
    results["entry_hash"] = sealed.entry_hash

    return results


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "TOOL_DEFINITIONS",
    "execute_tool",
    "get_tool_definitions",
    "ConstitutionalAIAssistant",
    "run_constitutional_pipeline",
]


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    async def main():
        print("=" * 70)
        print("MCP Tools v53 - Constitutional Pipeline Test")
        print("=" * 70)

        query = "How do I invest in renewable energy?"
        print(f"\nQuery: {query}\n")

        result = await run_constitutional_pipeline(query)

        print(f"Verdict: {result['verdict']}")
        print(f"Sealed: {result['sealed']}")
        print(f"Entry Hash: {result.get('entry_hash', 'N/A')[:32]}...")

        print("\n" + "=" * 70)
        print("Pipeline Complete")
        print("=" * 70)

    asyncio.run(main())
