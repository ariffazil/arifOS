"""
Caller Identity Extraction for L4_MCP.

Extracts caller identity from context for audit logging.
"""

from typing import Dict, Any

from L4_MCP.apex.schema import Caller


def extract_caller(context: Dict[str, Any]) -> Caller:
    """
    Extract caller identity from context dict.

    Args:
        context: Request context (may contain source, model, tenant, trust_level)

    Returns:
        Caller dataclass with identity information
    """
    return Caller(
        source=context.get("source", "unknown"),
        model=context.get("model", "unknown"),
        tenant=context.get("tenant", "unknown"),
        trust_level=context.get("trust_level", "unknown"),
    )
