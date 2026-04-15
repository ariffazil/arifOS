"""
arifOS MCP Prompt Specifications
═══════════════════════════════════════════════════════════════════════════════

10 workflow prompt templates.

Prompts are reusable interaction templates that users invoke explicitly.
They are NOT hidden system prompts — they are user-controlled workflows.

Each prompt:
- Has a clear purpose
- Accepts typed arguments
- References expected contracts
- Provides template text
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PromptArgument:
    """Typed argument for a prompt template."""
    name: str
    required: bool
    description: str
    arg_type: str = "string"  # string, integer, boolean
    default: Any = None


@dataclass(frozen=True)
class PromptSpec:
    """
    Clean prompt specification following MCP protocol.
    
    Prompts are reusable workflow templates.
    
    Fields:
        name: Machine-stable identifier
        title: Human-facing name
        description: Clear purpose
        arguments: List of expected arguments
        template_text: Jinja2-style template (optional)
        expected_contracts: Contracts this prompt produces/consumes
    """
    name: str
    title: str
    description: str
    arguments: tuple[PromptArgument, ...] = field(default_factory=tuple)
    template_text: str | None = None
    expected_contracts: tuple[str, ...] = field(default_factory=tuple)


def _arg(
    name: str,
    required: bool,
    description: str,
    arg_type: str = "string",
    default: Any = None
) -> PromptArgument:
    """Helper to create prompt arguments."""
    return PromptArgument(
        name=name,
        required=required,
        description=description,
        arg_type=arg_type,
        default=default
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 10 CANONICAL PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_PROMPT_SPECS: tuple[PromptSpec, ...] = (
    # ═══ SESSION LIFECYCLE ═══
    
    PromptSpec(
        name="prompt_init_anchor",
        title="Start Governed Session",
        description=(
            "Initialize a constitutional session with proper identity binding. "
            "First step for any serious arifOS work."
        ),
        arguments=(
            _arg("actor_id", False, "Your identity claim (email, username)"),
            _arg("intent", False, "What you plan to accomplish"),
        ),
        template_text=(
            "I want to start a governed arifOS session. "
            "My identity is {{actor_id|default('anonymous')}}. "
            "My intent is: {{intent|default('general exploration')}}. "
            "Please initialize the session anchor."
        ),
        expected_contracts=("SessionAnchor", "TelemetryEnvelope"),
    ),
    
    # ═══ EVIDENCE GATHERING ═══
    
    PromptSpec(
        name="prompt_sense_reality",
        title="Gather Evidence",
        description=(
            "Search and verify facts before making decisions. "
            "Grounds reasoning in observable reality."
        ),
        arguments=(
            _arg("topic", True, "What to research or verify"),
            _arg("depth", False, "How thorough: quick or thorough", default="thorough"),
        ),
        template_text=(
            "I need to ground my understanding in reality. "
            "Please search and verify: {{topic}}. "
            "Depth: {{depth}}. "
            "Provide evidence with confidence scores and source attribution."
        ),
        expected_contracts=("EvidenceBundle", "WitnessTriple"),
    ),
    
    # ═══ REASONING ═══
    
    PromptSpec(
        name="prompt_reason_synthesis",
        title="Structured Reasoning",
        description=(
            "Produce multi-source synthesis with uncertainty bands. "
            "Uses constitutional floors F2-F8 for evaluation."
        ),
        arguments=(
            _arg("question", True, "What to analyze"),
            _arg("sources", False, "Source constraints or preferred domains"),
        ),
        template_text=(
            "Please reason through this question step by step: {{question}}. "
            "Evaluate against constitutional floors F2-F8. "
            "Present synthesis with: (1) confidence levels, "
            "(2) uncertainty bands, (3) key assumptions, "
            "(4) what would change my mind."
            "{% if sources %}Sources to prioritize: {{sources}}.{% endif %}"
        ),
        expected_contracts=("EvidenceBundle", "TelemetryEnvelope"),
    ),
    
    # ═══ SAFETY ═══
    
    PromptSpec(
        name="prompt_critique_safety",
        title="Safety Critique",
        description=(
            "Red-team a proposal for risks, biases, and harms. "
            "Adversarial analysis with empathy for all stakeholders."
        ),
        arguments=(
            _arg("proposal", True, "What to critique"),
            _arg("stakeholders", False, "Who might be affected", default="all affected parties"),
        ),
        template_text=(
            "Please critique this proposal for safety and dignity concerns: "
            "{{proposal}}. "
            "Consider stakeholders: {{stakeholders}}. "
            "Use adversarial red-team analysis. "
            "Report: (1) direct risks, (2) subtle harms, "
            "(3) bias indicators, (4) dignity implications, "
            "(5) mitigation suggestions."
        ),
        expected_contracts=("EvidenceBundle",),
    ),
    
    # ═══ ROUTING ═══
    
    PromptSpec(
        name="prompt_route_kernel",
        title="Route Complex Request",
        description=(
            "Send a complex request through the constitutional pipeline. "
            "Metabolic routing with 888_HOLD protection."
        ),
        arguments=(
            _arg("request", True, "What needs to be done"),
            _arg("intent_type", False, "Category: ask, audit, design, decide, analyze, execute", "ask"),
        ),
        template_text=(
            "Please route this request through arifOS: {{request}}. "
            "Intent type: {{intent_type}}. "
            "Respect 888_HOLD for high-risk operations. "
            "Return: (1) chosen tool path, (2) risk assessment, "
            "(3) constitutional checkpoints, (4) next actions."
        ),
        expected_contracts=("SessionAnchor", "VerdictRecord"),
    ),
    
    # ═══ MEMORY ═══
    
    PromptSpec(
        name="prompt_memory_recall",
        title="Recall Memory",
        description=(
            "Retrieve relevant prior context from governed memory. "
            "Vector search with constitutional verification."
        ),
        arguments=(
            _arg("query", True, "Memory search query"),
            _arg("project", False, "Project scope filter", "general"),
        ),
        template_text=(
            "Please search governed memory for: {{query}}. "
            "Project context: {{project}}. "
            "Return: (1) most relevant items, "
            "(2) constitutional verification status, "
            "(3) confidence scores, "
            "(4) recommended next layer."
        ),
        expected_contracts=("EvidenceBundle",),
    ),
    
    # ═══ ESTIMATION ═══
    
    PromptSpec(
        name="prompt_estimate_ops",
        title="Estimate Operations",
        description=(
            "Compute costs, capacity, and thermodynamic feasibility. "
            "Returns G-score, entropy impact, capacity assessment."
        ),
        arguments=(
            _arg("action", True, "What to estimate"),
            _arg("constraints", False, "Budget/time limits", "none specified"),
        ),
        template_text=(
            "Please estimate operational cost and feasibility of: {{action}}. "
            "Constraints: {{constraints}}. "
            "Return: (1) G-score, (2) entropy impact, "
            "(3) capacity assessment, (4) time estimate, "
            "(5) resource requirements, (6) thermodynamic cost."
        ),
        expected_contracts=("TelemetryEnvelope",),
    ),
    
    # ═══ JUDGMENT ═══
    
    PromptSpec(
        name="prompt_judge_verdict",
        title="Render Verdict",
        description=(
            "Produce final constitutional verdict with floor evaluation. "
            "Comprehensive F1-F13 analysis."
        ),
        arguments=(
            _arg("candidate", True, "Action to evaluate"),
            _arg("risk_tier", False, "Risk level: low, medium, high, critical", "medium"),
        ),
        template_text=(
            "Please render constitutional verdict for: {{candidate}}. "
            "Risk tier: {{risk_tier}}. "
            "Evaluate against all F1-F13 floors. "
            "Return structured verdict with: "
            "(1) SEAL/PARTIAL/VOID/SABAR/HOLD, "
            "(2) floors passed/failed, "
            "(3) telemetry evidence, "
            "(4) witness attestation, "
            "(5) recommended actions."
        ),
        expected_contracts=("VerdictRecord", "TelemetryEnvelope", "WitnessTriple"),
    ),
    
    # ═══ EXPLANATION ═══
    
    PromptSpec(
        name="prompt_human_explainer",
        title="Explain to Human",
        description=(
            "Translate machine verdict into plain language. "
            "Makes constitutional decisions accessible."
        ),
        arguments=(
            _arg("verdict_json", True, "Machine verdict to explain"),
            _arg("audience", False, "Target: technical, executive, or general", "general"),
        ),
        template_text=(
            "Please explain this constitutional verdict in "
            "{{audience}} terms: {{verdict_json}}. "
            "Include: (1) what the verdict means, "
            "(2) why it was reached, "
            "(3) what actions are recommended, "
            "(4) what the user should do next."
        ),
        expected_contracts=(),
    ),
    
    # ═══ VAULT ═══
    
    PromptSpec(
        name="prompt_vault_record",
        title="Prepare Vault Record",
        description=(
            "Prepare immutable ledger entry with proper attestation. "
            "BLS signatures and juror quorum."
        ),
        arguments=(
            _arg("decision", True, "Decision to record"),
            _arg("evidence", False, "Supporting context", "none provided"),
        ),
        template_text=(
            "Please prepare a vault record for: {{decision}}. "
            "Evidence: {{evidence}}. "
            "Include: (1) BLS attestation block, "
            "(2) juror signature requests, "
            "(3) telemetry snapshot, "
            "(4) witness triple, "
            "(5) final seal hash."
        ),
        expected_contracts=("VerdictRecord",),
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# LOOKUP UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

PROMPT_NAMES: tuple[str, ...] = tuple(spec.name for spec in CANONICAL_PROMPT_SPECS)


def get_prompt_spec(name: str) -> PromptSpec | None:
    """Get prompt spec by name."""
    for spec in CANONICAL_PROMPT_SPECS:
        if spec.name == name:
            return spec
    return None


def prompt_spec_to_mcp_schema(spec: PromptSpec) -> dict[str, Any]:
    """Convert PromptSpec to MCP prompts/list schema."""
    return {
        "name": spec.name,
        "title": spec.title,
        "description": spec.description,
        "arguments": [
            {
                "name": arg.name,
                "required": arg.required,
                "description": arg.description,
            }
            for arg in spec.arguments
        ]
    }


def render_prompt(spec: PromptSpec, **kwargs: Any) -> str:
    """
    Simple template rendering for prompt text.
    
    Uses basic Jinja2-style variable substitution.
    """
    if not spec.template_text:
        return ""
    
    import re
    text = spec.template_text
    
    # Handle {{var|default('val')}}
    pattern = r'\{\{(\w+)\|default\([\'"]([^\'"]*)[\'"]\)\}\}'
    for match in re.finditer(pattern, text):
        var_name = match.group(1)
        default_val = match.group(2)
        value = kwargs.get(var_name, default_val)
        text = text.replace(match.group(0), str(value))
    
    # Handle {% if var %}...{% endif %}
    # Simplified: remove the conditionals if var is empty/false
    if_pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
    for match in re.finditer(if_pattern, text, re.DOTALL):
        var_name = match.group(1)
        content = match.group(2)
        if kwargs.get(var_name):
            text = text.replace(match.group(0), content)
        else:
            text = text.replace(match.group(0), "")
    
    # Handle simple {{var}}
    simple_pattern = r'\{\{(\w+)\}\}'
    for match in re.finditer(simple_pattern, text):
        var_name = match.group(1)
        value = kwargs.get(var_name, f"[{var_name}]")
        text = text.replace(match.group(0), str(value))
    
    return text.strip()


__all__ = [
    "PromptArgument",
    "PromptSpec",
    "CANONICAL_PROMPT_SPECS",
    "PROMPT_NAMES",
    "get_prompt_spec",
    "prompt_spec_to_mcp_schema",
    "render_prompt",
]
