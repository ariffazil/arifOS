import sys

path = '/root/arifosmcp/arifosmcp/runtime/public_registry.py'
with open(path, 'r') as f:
    content = f.read()

# 1. Update PUBLIC_TOOL_SPECS
new_specs = """    ToolSpec(
        name="reality_compass",
        stage="111_SENSE",
        role="Unified Reality",
        layer="Cognitive Input",
        description="Unified search and fetch engine. Automatically routes between query search and deep URL scraping.",
        trinity="Δ Delta",
        floors=("F2", "F12"),
        input_schema={
            "type": "object",
            "required": ["input"],
            "properties": {
                "input": {"type": "string", "description": "Search query or URL to fetch."},
                "mode": {"type": "string", "enum": ["auto", "search", "fetch"], "default": "auto"},
                "fetch_top_k": {"type": "integer", "default": 2, "description": "Fetch top K results if in search mode."}
            },
            "additionalProperties": False,
        },
        readonly=True,
    ),
    ToolSpec(
        name="reality_atlas",
        stage="222_REALITY",
        role="Evidence Graph",
        layer="Cognitive Input",
        description="Build and query the semantic evidence graph from acquired EvidenceBundles.",
        trinity="Δ Delta",
        floors=("F2", "F11"),
        input_schema={
            "type": "object",
            "required": ["operation"],
            "properties": {
                "operation": {"type": "string", "enum": ["ingest", "query", "merge"]},
                "bundles": {"type": "array", "items": {"type": "object"}}
            },
            "additionalProperties": False,
        },
    ),"""

if 'name="reality_compass"' not in content:
    content = content.replace('name="arifOS_kernel",', 'name="arifOS_kernel",\n' + new_specs)

# 2. Update PUBLIC_PROMPT_SPECS
new_prompts = """    PromptSpec("reality_compass_prompt", "reality_compass", "Unified reality acquisition entrypoint."),
    PromptSpec("reality_atlas_prompt", "reality_atlas", "Semantic evidence graph management."),"""

if 'reality_compass_prompt' not in content:
    content = content.replace('PromptSpec("arifos_kernel_prompt",', new_prompts + '\n    PromptSpec("arifos_kernel_prompt",')

with open(path, 'w') as f:
    f.write(content)
