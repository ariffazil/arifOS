import sys
import os

path = '/root/arifosmcp/arifosmcp/runtime/public_registry.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Add reality_dossier to PUBLIC_TOOL_SPECS
atlas_spec = """    ToolSpec(
        name="reality_atlas",
        stage="222_REALITY",
        role="Evidence Graph",
        layer="Intelligence (3E)",
        description="Build and query the semantic evidence graph from acquired EvidenceBundles.",
        trinity="Δ Delta",
        floors=("F2", "F11"),
        input_schema={
            "type": "object",
            "required": ["operation"],
            "properties": {
                "operation": {"type": "string", "enum": ["ingest", "query", "merge"]},
                "bundles": {"type": "array", "items": {"type": "object"}},
            },
            "additionalProperties": False,
        },
    ),"""

dossier_spec = """    ToolSpec(
        name="reality_dossier",
        stage="222_REALITY",
        role="Tri-Witness Decoder",
        layer="Intelligence (3E)",
        description="Synthesize EvidenceBundles into human-facing verdicts with 3E (Exploration→Entropy→Eureka) telemetry.",
        trinity="Δ Delta",
        floors=("F3", "F11", "F12"),
        input_schema={
            "type": "object",
            "required": ["bundles"],
            "properties": {
                "bundles": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of EvidenceBundles to synthesize.",
                },
                "session_id": {"type": "string", "default": "global"},
            },
            "additionalProperties": False,
        },
    ),"""

if 'name="reality_dossier"' not in content:
    content = content.replace(atlas_spec, atlas_spec + '\n' + dossier_spec)

# 2. Add reality_dossier_prompt to PUBLIC_PROMPT_SPECS
atlas_prompt = 'PromptSpec("reality_atlas_prompt", "reality_atlas", "Semantic evidence graph management."),'
dossier_prompt = '    PromptSpec("reality_dossier_prompt", "reality_dossier", "Tri-Witness synthesis decoder."),'

if 'reality_dossier_prompt' not in content:
    content = content.replace(atlas_prompt, atlas_prompt + '\n' + dossier_prompt)

with open(path, 'w') as f:
    f.write(content)
print("Successfully updated public_registry.py with reality_dossier.")
