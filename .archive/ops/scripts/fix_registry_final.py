import sys

path = '/root/arifosmcp/arifosmcp/runtime/public_registry.py'
with open(path, 'r') as f:
    lines = f.readlines()

out_lines = []
skip = False
for line in lines:
    if 'PUBLIC_TOOL_SPECS: tuple[ToolSpec, ...] = (' in line:
        out_lines.append(line)
        out_lines.append('    ToolSpec(\n')
        out_lines.append('        name="reality_compass",\n')
        out_lines.append('        stage="111_SENSE",\n')
        out_lines.append('        role="Unified Reality",\n')
        out_lines.append('        layer="Cognitive Input",\n')
        out_lines.append('        description="Unified search and fetch engine. Automatically routes between query search and deep URL scraping.",\n')
        out_lines.append('        trinity="Δ Delta",\n')
        out_lines.append('        floors=("F2", "F12"),\n')
        out_lines.append('        input_schema={\n')
        out_lines.append('            "type": "object",\n')
        out_lines.append('            "required": ["input"],\n')
        out_lines.append('            "properties": {\n')
        out_lines.append('                "input": {"type": "string", "description": "Search query or URL to fetch."},\n')
        out_lines.append('                "mode": {"type": "string", "enum": ["auto", "search", "fetch"], "default": "auto"},\n')
        out_lines.append('                "fetch_top_k": {"type": "integer", "default": 2, "description": "Fetch top K results if in search mode."}\n')
        out_lines.append('            },\n')
        out_lines.append('            "additionalProperties": False,\n')
        out_lines.append('        },\n')
        out_lines.append('        readonly=True,\n')
        out_lines.append('    ),\n')
        out_lines.append('    ToolSpec(\n')
        out_lines.append('        name="reality_atlas",\n')
        out_lines.append('        stage="222_REALITY",\n')
        out_lines.append('        role="Evidence Graph",\n')
        out_lines.append('        layer="Cognitive Input",\n')
        out_lines.append('        description="Build and query the semantic evidence graph from acquired EvidenceBundles.",\n')
        out_lines.append('        trinity="Δ Delta",\n')
        out_lines.append('        floors=("F2", "F11"),\n')
        out_lines.append('        input_schema={\n')
        out_lines.append('            "type": "object",\n')
        out_lines.append('            "required": ["operation"],\n')
        out_lines.append('            "properties": {\n')
        out_lines.append('                "operation": {"type": "string", "enum": ["ingest", "query", "merge"]},\n')
        out_lines.append('                "bundles": {"type": "array", "items": {"type": "object"}}\n')
        out_lines.append('            },\n')
        out_lines.append('            "additionalProperties": False,\n')
        out_lines.append('        },\n')
        out_lines.append('    ),\n')
        skip = True
        continue
    
    if skip and 'name="arifOS_kernel",' in line:
        out_lines.append('    ToolSpec(\n')
        out_lines.append('        name="arifOS_kernel",\n')
        skip = False
        continue
    
    if skip and 'name="reality_compass",' in line:
        continue # skip my previous messy insertion
    
    if skip:
        continue
        
    out_lines.append(line)

with open(path, 'w') as f:
    f.writelines(out_lines)
