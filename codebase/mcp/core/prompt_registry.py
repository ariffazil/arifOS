"""
arifOS MCP Prompt Registry
Exposes reusable constitutional evaluation prompts.

MCP Prompts are user-controlled templated workflows (spec 2025-11-25).
Unlike tools (model-controlled), prompts provide reusable templates.

v55.1: Initial prompt registry with constitutional evaluation templates.

DITEMPA BUKAN DIBERI
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PromptDefinition:
    """MCP Prompt definition."""
    name: str
    description: str
    template: str
    arguments: Optional[List[Dict[str, str]]] = None


class PromptRegistry:
    """
    Registry for MCP Prompts exposed by arifOS.
    
    Prompts are reusable templates for constitutional evaluation:
    - constitutional_eval: Full F1-F13 evaluation workflow
    - paradox_analysis: 9-paradox equilibrium analysis
    - trinity_full: Complete metabolic loop walkthrough
    - floor_violation_repair: SABAR/VOID remediation guide
    """

    def __init__(self):
        self._prompts: Dict[str, PromptDefinition] = {}
        self._register_default_prompts()

    def register(self, prompt: PromptDefinition) -> None:
        """Register a new prompt."""
        self._prompts[prompt.name] = prompt
        logger.info(f"Registered prompt: {prompt.name}")

    def get(self, name: str) -> Optional[PromptDefinition]:
        """Get a prompt definition by name."""
        return self._prompts.get(name)

    def list_prompts(self) -> List[PromptDefinition]:
        """Get all registered prompts."""
        return list(self._prompts.values())

    def render_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> str:
        """Render a prompt template with arguments."""
        prompt = self._prompts.get(name)
        if not prompt:
            raise ValueError(f"Prompt not found: {name}")
        
        template = prompt.template
        if arguments:
            for key, value in arguments.items():
                template = template.replace(f"{{{key}}}", str(value))
        return template

    def _register_default_prompts(self):
        """Register the default constitutional prompts."""
        
        # 1. Full Constitutional Evaluation
        self.register(PromptDefinition(
            name="constitutional_eval",
            description="Full F1-F13 constitutional evaluation workflow with floor-by-floor analysis.",
            template="""Please evaluate the following query through all 13 constitutional floors:

QUERY: {query}

Evaluate systematically across F1-F13 floors and return verdict.""",
            arguments=[{"name": "query", "description": "The query to evaluate", "required": "true"}],
        ))

        # 2. 9-Paradox Analysis
        self.register(PromptDefinition(
            name="paradox_analysis",
            description="9-paradox equilibrium analysis for APEX judgment.",
            template="""Analyze the following through the 9 constitutional paradoxes:

QUERY: {query}

Determine equilibrium where all paradoxes balance.""",
            arguments=[{"name": "query", "description": "The query to analyze", "required": "true"}],
        ))

        # 3. Trinity Full Pipeline
        self.register(PromptDefinition(
            name="trinity_full",
            description="Complete 000-999 metabolic loop walkthrough.",
            template="""Execute the complete constitutional pipeline for:

QUERY: {query}

Run full 000-999 metabolic loop and return all phases.""",
            arguments=[{"name": "query", "description": "The query to process", "required": "true"}],
        ))

        # 4. Floor Violation Repair
        self.register(PromptDefinition(
            name="floor_violation_repair",
            description="SABAR/VOID remediation guide for floor violations.",
            template="""A floor violation was detected. Guide the repair process:

VIOLATED FLOOR: {floor}
CURRENT VERDICT: {verdict}
ORIGINAL QUERY: {query}

Provide specific repair recommendations.""",
            arguments=[
                {"name": "floor", "description": "The violated floor (F1-F13)", "required": "true"},
                {"name": "verdict", "description": "Current verdict", "required": "true"},
                {"name": "query", "description": "The original query", "required": "true"},
            ],
        ))

        # 5. Constitutional Summary
        self.register(PromptDefinition(
            name="constitutional_summary",
            description="Quick reference for all 13 floors.",
            template="""Provide a summary of the arifOS constitutional framework:

THE 13 FLOORS:
- F1-F13 with thresholds
- Verdict hierarchy
- Usage guidance

Use as reference for constitutional decisions.""",
        ))
