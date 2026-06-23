"""Pydantic models for the Capability Index.

Explains the shape of a registered MCP tool so agents know
what it does without loading all 97 schemas into prompt context.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CapabilityRecord(BaseModel):
    """One row in the capability index — everything an agent needs to decide
    whether to invoke a tool.
    """

    tool_name: str = Field(..., description="Canonical MCP tool name, e.g. wealth_flow_liquidity")
    server: str = Field(..., description="Which MCP server owns this tool, e.g. WEALTH")
    description: str = Field(..., description="Human-readable summary of what the tool does")
    parameters: dict | None = Field(default=None, description="JSON Schema-like parameter summary")
    tags: list[str] = Field(
        default_factory=list, description="Semantic tags, e.g. ['capital', 'liquidity', 'malaysia']"
    )
    epistemic_tag: str = Field(
        default="CLAIM", description="Evidence quality: CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE"
    )

    def to_embedding_text(self) -> str:
        """Flatten into a single string for the embedding model."""
        tags_str = " ".join(self.tags)
        return f"{self.tool_name}. {self.description}. Tags: {tags_str}."
